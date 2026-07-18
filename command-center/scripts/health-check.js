#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = process.cwd();
const commandCenter = path.join(root, "command-center");
const watchedSourceFiles = [
  "command-center/roadmap.md",
  "command-center/now.md",
  "command-center/decisions.md",
  "command-center/ideas.md",
  "command-center/issues.md",
  "command-center/operating-rules.md"
];
const stateStaleMessage =
  "Dashboard state may be stale; update state.json from command-center source files, then run node command-center/scripts/refresh-dashboard.js";
const dashboardStaleMessage =
  "Generated dashboard is stale; run node command-center/scripts/refresh-dashboard.js";
const required = [
  "README.md",
  ".gitignore",
  "PROJECT_STRUCTURE.md",
  "command-center/state.json",
  "command-center/now.md",
  "command-center/roadmap.md",
  "command-center/decisions.md",
  "command-center/ideas.md",
  "command-center/issues.md",
  "command-center/operating-rules.md",
  "command-center/agent-selection.md",
  "command-center/architecture.md",
  "command-center/index.html",
  "command-center/scripts/refresh-dashboard.js",
  "command-center/scripts/health-check.js",
  "command-center/scripts/new-claude-handoff.js",
  "command-center/logs/README.md",
  "command-center/handoffs/README.md",
  "command-center/templates/claude-handoff.md",
  "command-center/templates/second-opinion.md",
  "command-center/templates/closeout-report.md",
  "command-center/templates/project-intake-wizard.md",
  "command-center/templates/agent-output-intake.md",
  "command-center/agent-router/README.md",
  "command-center/agent-router/agents.json",
  "command-center/agent-router/routing-policy.json",
  "command-center/agent-router/scripts/queue-summary.js",
  "command-center/skills/claude-handoff/SKILL.md",
  "command-center/skills/dashboard-refresh/SKILL.md",
  "command-center/skills/project-manager/SKILL.md",
  "command-center/skills/second-opinion/SKILL.md"
];

function canonicalize(value) {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, canonicalize(value[key])]));
  }
  return value;
}

function sameJson(left, right) {
  return JSON.stringify(canonicalize(left)) === JSON.stringify(canonicalize(right));
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
  for (const key of ["ideas", "issues"]) {
    for (const [index, rawItem] of (state[key] || []).entries()) {
      const item = normalizeParkedCard(rawItem);
      if (!isUsefulString(item.title) || !isUsefulString(item.summary)) {
        console.error(`state.json ${key}[${index}] needs visible title and summary content`);
        failed = true;
      }
    }
  }
}

function validateNextMilestone(state) {
  const milestoneName = state.nextMilestone && state.nextMilestone.name;
  if (!isUsefulString(milestoneName)) return;

  const normalizedMilestone = normalizeText(milestoneName);
  const staleStatuses = new Set(["done", "closed", "superseded"]);

  for (const block of state.phaseWorkBlocks || []) {
    if (!staleStatuses.has(normalizedStatus(block.status))) continue;
    const candidates = [
      block.name,
      block.label && block.name ? `${block.label} ${block.name}` : "",
      block.label
    ].filter(isUsefulString).map(normalizeText);
    if (candidates.some((candidate) => normalizedMilestone === candidate || normalizedMilestone.startsWith(`${candidate} `))) {
      console.error(`state.json nextMilestone appears stale: "${milestoneName}" points at completed work block ${block.label || block.id || block.name}`);
      failed = true;
    }
  }

  for (const task of state.phaseTasks || []) {
    if (!staleStatuses.has(normalizedStatus(task.status))) continue;
    if (normalizedMilestone === normalizeText(task.title)) {
      console.error(`state.json nextMilestone appears stale: "${milestoneName}" points at completed task ${task.taskId || task.title}`);
      failed = true;
    }
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

function validateRoadmapTaskInventory(state) {
  const active = (state.phases || []).filter((phase) => normalizedStatus(phase.status) === "active");
  if (active.length !== 1) return;

  const roadmapPath = path.join(commandCenter, "roadmap.md");
  if (!fs.existsSync(roadmapPath)) return;

  const section = extractRoadmapPhaseSection(fs.readFileSync(roadmapPath, "utf8"), active[0]);
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
      .filter((task) => task.phaseId === active[0].id)
      .map((task) => String(task.title || "").match(/Task\s+(\d+)\s*:/i)?.[1])
      .filter(Boolean)
  );
  for (const taskNumber of roadmapTaskNumbers) {
    if (!stateTaskNumbers.has(taskNumber)) {
      console.error(`roadmap.md lists active-phase Task ${taskNumber}, but state.json is missing that task number`);
      failed = true;
    }
  }
}

function validateDashboardFreshness() {
  const stateStat = fs.statSync(statePath);
  const newerSources = [];

  for (const rel of watchedSourceFiles) {
    const sourcePath = path.join(root, rel);
    if (fs.statSync(sourcePath).mtimeMs > stateStat.mtimeMs) {
      newerSources.push(rel);
    }
  }

  if (newerSources.length > 0) {
    console.error(`${stateStaleMessage}. Newer sources: ${newerSources.join(", ")}`);
    failed = true;
  }

  if (stateStat.mtimeMs > fs.statSync(indexPath).mtimeMs) {
    console.error(dashboardStaleMessage);
    failed = true;
  }
}

let failed = false;
for (const rel of required) {
  if (!fs.existsSync(path.join(root, rel))) {
    console.error(`Missing required file: ${rel}`);
    failed = true;
  }
}

if (!fs.existsSync(path.join(root, ".git"))) {
  console.error("Missing local git repo metadata: .git");
  failed = true;
}

for (const rel of [
  "command-center/scripts/refresh-dashboard.js",
  "command-center/scripts/health-check.js",
  "command-center/scripts/new-claude-handoff.js",
  "command-center/agent-router/scripts/queue-summary.js"
]) {
  try {
    new vm.Script(fs.readFileSync(path.join(root, rel), "utf8"), { filename: rel });
  } catch (error) {
    console.error(`Syntax error in ${rel}: ${error.message}`);
    failed = true;
  }
}

const statePath = path.join(commandCenter, "state.json");
const indexPath = path.join(commandCenter, "index.html");
const state = JSON.parse(fs.readFileSync(statePath, "utf8"));
validateDashboardFreshness();
const scaffold = state.project?.scaffold || {};
const requiredScaffold = {
  product: "Runway OS",
  contractVersion: "0.1.2",
  installer: "scratch-project-command-center",
  installerVersion: "0.1.2",
  parentChangeLog: "Projects Project/command-center/template-productization/scaffold-change-log.md"
};
const allowedProfiles = new Set(["scratch", "retrofit", "sensitive-retrofit"]);
for (const [key, expected] of Object.entries(requiredScaffold)) {
  if (scaffold[key] !== expected) {
    console.error(`state.json project.scaffold.${key} must be ${expected}`);
    failed = true;
  }
}
if (!allowedProfiles.has(scaffold.profile)) {
  console.error("state.json project.scaffold.profile must be scratch, retrofit, or sensitive-retrofit");
  failed = true;
}
for (const key of ["installedAt", "lastUpdatedAt"]) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(scaffold[key] || "")) {
    console.error(`state.json project.scaffold.${key} must be a YYYY-MM-DD date`);
    failed = true;
  }
}
if (state.project?.helperBundle && state.project.helperBundle !== scaffold.profile) {
  console.error("state.json project.helperBundle must match project.scaffold.profile while compatibility field remains present");
  failed = true;
}

if (scaffold.profile === "scratch" && !fs.existsSync(path.join(root, "command-center/skills/agent-router/SKILL.md"))) {
  console.error("Scratch profile must include command-center/skills/agent-router/SKILL.md");
  failed = true;
}

if (scaffold.profile === "scratch") {
  for (const rel of ["app/README.md", "scratch/README.md"]) {
    if (!fs.existsSync(path.join(root, rel))) {
      console.error(`Scratch profile is missing required file: ${rel}`);
      failed = true;
    }
  }
}

if (scaffold.profile !== "scratch") {
  const existingProductRoots = ["web", "core", "scripts"].filter((rel) =>
    fs.existsSync(path.join(root, rel))
  );
  if (existingProductRoots.length === 0) {
    console.error("Retrofit profile must preserve at least one existing product root");
    failed = true;
  }
}

if (!state.childRepo || state.childRepo.localGit !== "required" || state.childRepo.parentTracking !== "pointer-only") {
  console.error("state.json must record childRepo localGit and pointer-only parent tracking defaults");
  failed = true;
}

if (!Array.isArray(state.phaseWorkBlocks)) {
  console.error("state.json must include phaseWorkBlocks, even when empty");
  failed = true;
}

validateParkedCards(state);
validateNextMilestone(state);
validateRoadmapTaskInventory(state);

const active = (state.phases || []).filter((phase) => phase.status === "active");
if (active.length !== 1) {
  console.error(`state.json must contain exactly one active phase; found ${active.length}`);
  failed = true;
}

const html = fs.readFileSync(indexPath, "utf8");
const match = html.match(/<script id="dashboard-state" type="application\/json">([\s\S]*?)<\/script>/);
if (!match) {
  console.error("Dashboard is missing embedded dashboard-state JSON");
  failed = true;
} else {
  const embedded = JSON.parse(match[1]);
  if (!sameJson(embedded, state)) {
    console.error("Dashboard embedded state is stale; run node command-center/scripts/refresh-dashboard.js");
    failed = true;
  }
}

if (failed) process.exit(1);
console.log("Command center health check passed");
