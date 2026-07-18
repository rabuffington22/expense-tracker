#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const routerRoot = path.resolve(__dirname, "..");
const repoRoot = path.resolve(routerRoot, "..", "..");
const queueRoot = path.join(routerRoot, "queue");

const QUEUE_FOLDERS = ["todo", "working", "review", "done", "needs-human", "failed"];
const DEFAULT_STALE_HOURS = 24;

function parseArgs(argv) {
  const args = { json: false, staleHours: DEFAULT_STALE_HOURS };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--json") {
      args.json = true;
    } else if (arg === "--help") {
      args.help = true;
    } else if (arg === "--stale-hours") {
      const value = argv[i + 1];
      if (!value || value.startsWith("--")) {
        throw new Error("Missing value for --stale-hours");
      }
      args.staleHours = Number(value);
      i += 1;
    } else if (arg.startsWith("--stale-hours=")) {
      args.staleHours = Number(arg.split("=", 2)[1]);
    } else {
      throw new Error(`Unexpected argument: ${arg}`);
    }
  }

  if (!Number.isFinite(args.staleHours) || args.staleHours < 0) {
    throw new Error("--stale-hours must be a non-negative number");
  }

  return args;
}

function printHelp() {
  console.log(`Usage:
  node command-center/agent-router/scripts/queue-summary.js [--json] [--stale-hours 24]

Reports agent-router queue counts, task ids by folder, return-file pairing,
and stale working/review items. Folder location remains canonical task state.
`);
}

function rel(target) {
  return path.relative(repoRoot, target);
}

function parseFrontmatter(content) {
  if (!content.startsWith("---\n")) {
    return {};
  }

  const end = content.indexOf("\n---\n", 4);
  if (end === -1) {
    return {};
  }

  const data = {};
  for (const line of content.slice(4, end).split("\n")) {
    const match = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!match) {
      continue;
    }

    const key = match[1];
    const rawValue = match[2].trim();
    if (!rawValue) {
      data[key] = "";
      continue;
    }

    try {
      data[key] = JSON.parse(rawValue);
    } catch (_error) {
      if (rawValue === "true") {
        data[key] = true;
      } else if (rawValue === "false") {
        data[key] = false;
      } else {
        data[key] = rawValue;
      }
    }
  }

  return data;
}

function readEntries(folder) {
  const dir = path.join(queueRoot, folder);
  if (!fs.existsSync(dir)) {
    return { folder, exists: false, tasks: [], returns: [] };
  }

  const names = fs.readdirSync(dir).filter((name) => name.endsWith(".md")).sort();
  const entries = names.map((name) => {
    const filePath = path.join(dir, name);
    const content = fs.readFileSync(filePath, "utf8");
    const stat = fs.statSync(filePath);
    const isReturn = name.endsWith("-return.md");
    const id = isReturn ? name.replace(/-return\.md$/, "") : name.replace(/\.md$/, "");
    const frontmatter = isReturn ? {} : parseFrontmatter(content);
    return {
      id: frontmatter.id || id,
      name,
      path: rel(filePath),
      isReturn,
      assignedTo: frontmatter.assigned_to || "",
      type: frontmatter.type || "",
      risk: frontmatter.risk || "",
      routingStatus: frontmatter.routing_status || "",
      created: frontmatter.created || "",
      modified: stat.mtime.toISOString()
    };
  });

  return {
    folder,
    exists: true,
    tasks: entries.filter((entry) => !entry.isReturn),
    returns: entries.filter((entry) => entry.isReturn)
  };
}

function summarizeQueue(staleHours) {
  const folders = Object.fromEntries(QUEUE_FOLDERS.map((folder) => [folder, readEntries(folder)]));
  const cutoffMs = Date.now() - staleHours * 60 * 60 * 1000;
  const staleFolders = new Set(["working", "review", "needs-human"]);
  const stale = [];

  for (const folder of QUEUE_FOLDERS) {
    const summary = folders[folder];
    for (const task of [...summary.tasks, ...summary.returns]) {
      const modifiedMs = Date.parse(task.modified);
      if (staleFolders.has(folder) && Number.isFinite(modifiedMs) && modifiedMs < cutoffMs) {
        stale.push({
          folder,
          id: task.id,
          path: task.path,
          modified: task.modified
        });
      }
    }
  }

  const counts = {};
  for (const folder of QUEUE_FOLDERS) {
    const summary = folders[folder];
    counts[folder] = summary.exists ? summary.tasks.length + summary.returns.length : null;
  }

  const unpaired = [];
  for (const folder of QUEUE_FOLDERS) {
    const summary = folders[folder];
    const tasks = new Set(summary.tasks.map((entry) => entry.id));
    const returns = new Set(summary.returns.map((entry) => entry.id));
    for (const id of tasks) {
      if (!returns.has(id) && ["review", "done"].includes(folder)) {
        unpaired.push({ folder, id, missing: "return" });
      }
    }
    for (const id of returns) {
      if (!tasks.has(id)) {
        unpaired.push({ folder, id, missing: "task" });
      }
    }
  }

  return {
    ok: counts.todo === 0 && counts.working === 0 && counts.review === 0 && stale.length === 0 && unpaired.length === 0,
    counts,
    folders,
    staleHours,
    stale,
    unpaired
  };
}

function formatIds(items) {
  if (items.length === 0) {
    return "none";
  }
  return items.map((item) => item.id).join(", ");
}

function printSummary(summary) {
  console.log("Agent router queue summary\n");

  for (const folder of QUEUE_FOLDERS) {
    const data = summary.folders[folder];
    const count = summary.counts[folder];
    console.log(`${folder.padEnd(12)} ${count === null ? "missing" : count}`);
    if (data.exists) {
      console.log(`  tasks:   ${formatIds(data.tasks)}`);
      console.log(`  returns: ${formatIds(data.returns)}`);
    }
  }

  console.log("\nReview backlog: " + summary.counts.review);
  console.log("Working backlog: " + summary.counts.working);
  console.log("Stale threshold: " + summary.staleHours + "h");

  if (summary.stale.length > 0) {
    console.log("\nStale items:");
    for (const item of summary.stale) {
      console.log(`  ${item.folder}: ${item.id} (${item.modified})`);
    }
  }

  if (summary.unpaired.length > 0) {
    console.log("\nUnpaired task/return files:");
    for (const item of summary.unpaired) {
      console.log(`  ${item.folder}: ${item.id} missing ${item.missing}`);
    }
  }

  console.log(`\n${summary.ok ? "OK" : "ATTENTION"}: queue ${summary.ok ? "has no active backlog" : "needs review"}`);
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    printHelp();
    return 0;
  }

  const summary = summarizeQueue(args.staleHours);
  if (args.json) {
    console.log(JSON.stringify(summary, null, 2));
  } else {
    printSummary(summary);
  }
  return summary.ok ? 0 : 1;
}

try {
  process.exit(main());
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
