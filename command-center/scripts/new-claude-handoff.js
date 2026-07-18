#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const repoRoot = path.resolve(root, "..");
const statePath = path.join(root, "state.json");
const outDir = path.join(root, "handoffs", "claude");

const DEFAULT_CONSTRAINTS = [
  "Keep changes scoped.",
  "Preserve existing project conventions.",
  "Do not make unrelated refactors.",
  "Ask before changing product direction.",
  "Keep the repo as the source of truth."
];

const DEFAULT_RETURN_FORMAT = [
  "Summary",
  "Files changed",
  "Tests/checks run",
  "Decisions or assumptions",
  "Risks/follow-ups"
];

function parseArgs(argv) {
  const args = {};

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];

    if (!arg.startsWith("--")) {
      throw new Error(`Unexpected positional argument: ${arg}`);
    }

    const [rawKey, inlineValue] = arg.slice(2).split(/=(.*)/s);
    const key = rawKey.trim();

    if (["help", "dry-run", "force"].includes(key)) {
      args[key] = true;
      continue;
    }

    const value = inlineValue !== undefined ? inlineValue : argv[i + 1];
    if (!value || value.startsWith("--")) {
      throw new Error(`Missing value for --${key}`);
    }

    args[key] = value;
    if (inlineValue === undefined) {
      i += 1;
    }
  }

  return args;
}

function printHelp() {
  console.log(`Usage:
  node command-center/scripts/new-claude-handoff.js --task "Task summary" [options]

Options:
  --slug <short-name>       File slug. Defaults to a slug from --task.
  --date <YYYY-MM-DD>       Date prefix. Defaults to today's local date.
  --outcome <text>          Desired end state.
  --files <a,b,c>           Relevant files, comma or newline separated.
  --constraints <a;b;c>     Extra constraints, separated by semicolon or newline.
  --checks <a;b;c>          Acceptance checks, separated by semicolon or newline.
  --return-format <a;b;c>   Override the default Claude return sections.
  --force                   Overwrite an existing handoff file.
  --dry-run                 Print the generated handoff instead of writing it.
  --help                    Show this help.
`);
}

function list(value) {
  if (!value) {
    return [];
  }

  return value
    .split(/[\n,;]+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function todayLocal() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function slugify(value) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80);
}

function bulletList(items, fallback) {
  const source = items.length > 0 ? items : fallback;
  return source.map((item) => `- ${item}`).join("\n");
}

function numberedList(items) {
  return items.map((item, index) => `${index + 1}. ${item}`).join("\n");
}

function renderHandoff({ state, args, slug }) {
  const task = args.task || state.currentTask?.nextAction || state.currentTask?.title;
  const relevantFiles = list(args.files);
  const constraints = [...DEFAULT_CONSTRAINTS, ...list(args.constraints)];
  const checks = list(args.checks);
  const returnFormat = list(args["return-format"]);
  const outcome = args.outcome || "Complete the task described above and return a concise implementation summary for Codex intake.";

  return `# Claude Handoff: ${titleCase(slug)}

## Task

${task}

## Repo Context

- Project: ${state.project?.name || "Unknown project"}
- Source of truth: ${state.project?.sourceOfTruth || "Repo"}
- Current phase: ${state.phase?.name || "Unknown"} (${state.phase?.status || "unknown"})
- Current task: ${state.currentTask?.title || "Unknown"}
- Current owner: ${state.currentTask?.owner || "Unknown"}
- Supporting agent: ${state.currentTask?.supportingAgent || "Not specified"}
- Blocker: ${state.currentTask?.blocker || "None"}

## Relevant Files

${bulletList(relevantFiles, [
  "command-center/state.json",
  "command-center/now.md",
  "command-center/roadmap.md"
])}

## Desired Outcome

${outcome}

## Constraints

${bulletList(constraints, [])}

## Acceptance Checks

${bulletList(checks, [
  "Files changed are listed.",
  "Tests or manual checks are listed.",
  "Known risks are listed.",
  "Follow-up questions are listed."
])}

## Return Format

Return:

${numberedList(returnFormat.length > 0 ? returnFormat : DEFAULT_RETURN_FORMAT)}

## Codex Intake Reminder

After Claude returns work, Codex should review the diff, record the result in a dated intake log, update repo state if the status changed, and run \`node command-center/scripts/refresh-dashboard.js\`.
`;
}

function titleCase(slug) {
  return slug
    .split("-")
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.help) {
    printHelp();
    return;
  }

  const state = JSON.parse(fs.readFileSync(statePath, "utf8"));
  const task = args.task || state.currentTask?.nextAction || state.currentTask?.title;
  if (!task) {
    throw new Error("Provide --task, or make sure state.json has currentTask.title/nextAction.");
  }

  const date = args.date || todayLocal();
  const slug = slugify(args.slug || task);
  if (!slug) {
    throw new Error("Could not create a usable slug. Provide --slug.");
  }

  const filename = `${date}-${slug}.md`;
  const outPath = path.join(outDir, filename);
  const content = renderHandoff({ state, args: { ...args, task }, slug });

  if (args["dry-run"]) {
    console.log(content);
    return;
  }

  if (fs.existsSync(outPath) && !args.force) {
    throw new Error(`Refusing to overwrite existing handoff: ${path.relative(repoRoot, outPath)}. Use --force to overwrite.`);
  }

  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(outPath, content);
  console.log(`Created ${path.relative(repoRoot, outPath)}`);
}

try {
  main();
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
