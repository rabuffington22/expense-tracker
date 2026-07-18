#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const root = process.cwd();
const commandCenterRoot = path.join(root, "command-center");
const statePath = path.join(commandCenterRoot, "state.json");
const dashboardPath = path.join(commandCenterRoot, "index.html");
const roadmapPath = path.join(commandCenterRoot, "roadmap.md");
const queueRoot = path.join(commandCenterRoot, "agent-router", "queue");

function countQueue(folder) {
  const dir = path.join(queueRoot, folder);
  if (!fs.existsSync(dir)) return 0;
  return fs.readdirSync(dir).filter((name) => name.endsWith(".md")).length;
}

function validateState(state) {
  for (const key of ["project", "phase", "currentTask", "phases", "phaseTasks", "agents", "artifacts"]) {
    if (!(key in state)) throw new Error(`state.json missing required key: ${key}`);
  }
  const active = state.phases.filter((phase) => phase.status === "active");
  if (active.length !== 1) {
    throw new Error(`state.json must include exactly one active phase; found ${active.length}`);
  }
  const activeTasks = state.phaseTasks.filter((task) => task.phaseId === active[0].id && task.status === "current");
  if (activeTasks.length !== 1) {
    throw new Error(`active phase must include exactly one current phase task; found ${activeTasks.length}`);
  }
  if (state.currentTask.title !== activeTasks[0].title) {
    throw new Error("currentTask.title must match the active phase current task title");
  }
  validateParkedCards(state);
  validateNextMilestone(state);
  validateRoadmapTaskInventory(state, active[0]);
}

function normalizedStatus(value) {
  return String(value || "").trim().toLowerCase();
}

function isUsefulString(value) {
  if (typeof value !== "string") return false;
  const trimmed = value.trim();
  return trimmed.length > 0 && !/^(tbd|todo|none|n\/a|not started)$/i.test(trimmed);
}

function normalizeText(value) {
  return String(value || "").trim().toLowerCase().replace(/\s+/g, " ");
}

function normalizeParkedCard(item) {
  if (typeof item === "string") {
    const textValue = item.trim();
    return { title: textValue, summary: textValue };
  }
  if (!item || typeof item !== "object") {
    return { title: "", summary: "" };
  }
  return {
    title: item.title || item.name || item.summary || "",
    summary: item.summary || item.description || item.title || item.name || ""
  };
}

function validateParkedCards(state) {
  const failures = [];
  for (const key of ["ideas", "issues"]) {
    for (const [index, rawItem] of (state[key] || []).entries()) {
      const item = normalizeParkedCard(rawItem);
      if (!isUsefulString(item.title) || !isUsefulString(item.summary)) {
        failures.push(`${key}[${index}] needs visible title and summary content`);
      }
    }
  }
  if (failures.length > 0) {
    throw new Error(`Parked idea/issue cards are incomplete: ${failures.join("; ")}`);
  }
}

function validateNextMilestone(state) {
  const milestoneName = state.nextMilestone && state.nextMilestone.name;
  if (!isUsefulString(milestoneName)) return;

  const normalizedMilestone = normalizeText(milestoneName);
  const staleStatuses = new Set(["done", "closed", "superseded"]);
  const staleMatches = [];

  for (const block of state.phaseWorkBlocks || []) {
    if (!staleStatuses.has(normalizedStatus(block.status))) continue;
    const candidates = [
      block.name,
      block.label && block.name ? `${block.label} ${block.name}` : "",
      block.label
    ].filter(isUsefulString).map(normalizeText);
    if (candidates.some((candidate) => normalizedMilestone === candidate || normalizedMilestone.startsWith(`${candidate} `))) {
      staleMatches.push(`completed work block ${block.label || block.id || block.name}`);
    }
  }

  for (const task of state.phaseTasks || []) {
    if (!staleStatuses.has(normalizedStatus(task.status))) continue;
    if (normalizedMilestone === normalizeText(task.title)) {
      staleMatches.push(`completed task ${task.taskId || task.title}`);
    }
  }

  if (staleMatches.length > 0) {
    throw new Error(`nextMilestone appears stale: "${milestoneName}" points at ${staleMatches.join(", ")}`);
  }
}

function extractRoadmapPhaseSection(roadmap, activePhase) {
  const phaseNumber = String(activePhase.id || "").match(/phase-(\d+)/)?.[1];
  const names = [activePhase.name, activePhase.label, phaseNumber ? `Phase ${phaseNumber}` : ""].filter(isUsefulString);

  for (const name of names) {
    const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const match = roadmap.match(new RegExp(`(^##\\s+${escaped}[^\\n]*\\n[\\s\\S]*?)(?=^##\\s+Phase\\s+\\d+|(?![\\s\\S]))`, "im"));
    if (match) return match[1];
  }
  return "";
}

function validateRoadmapTaskInventory(state, activePhase) {
  if (!fs.existsSync(roadmapPath)) return;

  const section = extractRoadmapPhaseSection(fs.readFileSync(roadmapPath, "utf8"), activePhase);
  if (!section) return;

  const roadmapTaskNumbers = new Set();
  const taskLinePattern = /^\s*(?:[-*]\s*)?(?:\*\*)?Task\s+(\d+)\s*[:.-]/gim;
  let match;
  while ((match = taskLinePattern.exec(section))) {
    roadmapTaskNumbers.add(match[1]);
  }
  if (roadmapTaskNumbers.size === 0) return;

  const stateTaskNumbers = new Set(
    (state.phaseTasks || [])
      .filter((task) => task.phaseId === activePhase.id)
      .map((task) => String(task.title || "").match(/Task\s+(\d+)\s*:/i)?.[1])
      .filter(Boolean)
  );
  const missing = [...roadmapTaskNumbers].filter((taskNumber) => !stateTaskNumbers.has(taskNumber));
  if (missing.length > 0) {
    throw new Error(`roadmap.md lists active-phase task numbers missing from state.json: ${missing.map((n) => `Task ${n}`).join(", ")}`);
  }
}

function formatCentralTimestamp(date = new Date()) {
  const parts = Object.fromEntries(
    new Intl.DateTimeFormat("en-US", {
      timeZone: "America/Chicago",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "numeric",
      minute: "2-digit",
      hour12: true
    }).formatToParts(date).map((part) => [part.type, part.value])
  );
  return `${parts.year}-${parts.month}-${parts.day} ${parts.hour}:${parts.minute} ${parts.dayPeriod} CST`;
}

function replaceDashboardState(html, state) {
  const serialized = JSON.stringify(state, null, 2)
    .replace(/</g, "\\u003c")
    .replace(/>/g, "\\u003e")
    .replace(/&/g, "\\u0026");
  let replaced = false;
  const next = html.replace(
    /<script id="dashboard-state" type="application\/json">[\s\S]*?<\/script>/,
    () => {
      replaced = true;
      return `<script id="dashboard-state" type="application/json">\n${serialized}\n</script>`;
    }
  );
  if (!replaced) throw new Error("Could not find dashboard-state script tag in index.html");
  return next.replace(/<title>[\s\S]*?<\/title>/, `<title>${state.project.name} Command Center</title>`);
}

const state = JSON.parse(fs.readFileSync(statePath, "utf8"));
state.project.lastUpdated = formatCentralTimestamp();
const isScratchProfile = state.project?.scaffold?.profile === "scratch";
state.routerHealth = {
  ...(state.routerHealth || {}),
  status: "healthy",
  summary: isScratchProfile
    ? "Scratch-project queue is clear; command-center state is local to this project."
    : "Protected retrofit queue is clear; external worker runners are intentionally not installed.",
  lastChecked: formatCentralTimestamp().slice(0, 10),
  command: "node command-center/agent-router/scripts/queue-summary.js",
  healthCommand: "node command-center/scripts/health-check.js",
  counts: {
    todo: 0,
    working: 0,
    review: 0,
    done: countQueue("done"),
    needsHuman: 0,
    failed: countQueue("failed")
  },
  taskCounts: {
    done: countQueue("done"),
    failed: countQueue("failed")
  },
  activeTasks: [],
  failedDetails: [],
  backlogDisposition: isScratchProfile
    ? "Derived from scratch-project queue folders during dashboard refresh."
    : "Derived from protected retrofit queue folders during dashboard refresh."
};
state.verification = {
  ...(state.verification || {}),
  dashboardRefresh: "pass"
};
validateState(state);
fs.writeFileSync(statePath, `${JSON.stringify(state, null, 2)}\n`);
fs.writeFileSync(dashboardPath, replaceDashboardState(fs.readFileSync(dashboardPath, "utf8"), state));
console.log(`Refreshed ${path.relative(root, dashboardPath)} from ${path.relative(root, statePath)}`);
