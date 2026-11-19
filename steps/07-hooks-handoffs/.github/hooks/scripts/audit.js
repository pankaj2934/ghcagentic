#!/usr/bin/env node
// Agent hook: runs before and after every tool call (see ../audit.json).
//
// 1. AUDIT: appends one line per event to .github/hooks/logs/audit.log
// 2. GUARD: before a tool runs, denies terminal commands that delete files
//
// The harness sends a JSON description of the event on stdin. Field names
// differ a little between Copilot surfaces and versions, so we accept both
// spellings (tool_name / toolName, tool_input / toolArgs).
const fs = require("fs");
const path = require("path");

let raw = "";
process.stdin.on("data", (c) => (raw += c));
process.stdin.on("end", () => {
  let event = {};
  try { event = JSON.parse(raw || "{}"); } catch {}

  const hook = event.hook_event_name || event.hookEventName || "unknown";
  const tool = event.tool_name || event.toolName || "?";
  const input = event.tool_input || event.toolArgs || {};
  const inputText = typeof input === "string" ? input : JSON.stringify(input);

  // ---- 1. audit log -------------------------------------------------------
  const logDir = path.join(".github", "hooks", "logs");
  fs.mkdirSync(logDir, { recursive: true });
  fs.appendFileSync(
    path.join(logDir, "audit.log"),
    `${new Date().toISOString()}  ${hook.padEnd(12)}  ${tool}  ${inputText.slice(0, 200)}\n`
  );

  // ---- 2. guard: no deleting files from the terminal ----------------------
  const isPre = /pre.?tool.?use/i.test(hook);
  if (isPre && /\b(rm|del|rmdir|Remove-Item)\b/i.test(inputText)) {
    process.stdout.write(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "Demo guard hook: deleting files is not allowed in this workspace.",
      },
    }));
  }
  process.exit(0); // exit 0 and no output = carry on as normal
});
