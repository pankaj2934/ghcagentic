#!/usr/bin/env python3
"""Agent hook: runs when a prompt arrives, before and after every tool call,
when a subagent starts/stops (step 10), and when the agent finishes
(see ../audit.json).

1. AUDIT: appends one line per event to .github/hooks/logs/audit.log
   (and audit.jsonl, which visualizer/serve.py animates live)
2. GUARD: before a tool runs, denies terminal commands that delete files

The harness sends a JSON description of the event on stdin. Field names
differ a little between Copilot surfaces and versions, so we accept both
spellings (tool_name / toolName, tool_input / toolArgs).
"""
import datetime
import json
import pathlib
import re
import sys

sys.stdin.reconfigure(encoding="utf-8")
try:
    event = json.loads(sys.stdin.read() or "{}")
except json.JSONDecodeError:
    event = {}

hook = event.get("hook_event_name") or event.get("hookEventName") or "unknown"
tool = event.get("tool_name") or event.get("toolName") or "?"
tool_input = event.get("tool_input") or event.get("toolArgs") or event.get("prompt")
if tool_input is None:
    # Other events (e.g. SubagentStart/SubagentStop): keep the interesting
    # fields, such as which agent started, and drop the bookkeeping ones.
    skip = {"hook_event_name", "hookEventName", "session_id", "sessionId", "transcript_path", "cwd", "timestamp"}
    tool_input = {k: v for k, v in event.items() if k not in skip}
input_text = tool_input if isinstance(tool_input, str) else json.dumps(tool_input, ensure_ascii=False)
if tool == "?" and not re.search(r"tool", hook, re.IGNORECASE):
    tool = "-"  # UserPromptSubmit / Stop events aren't about a tool

# ---- 1. audit log -----------------------------------------------------------
log_dir = pathlib.Path(".github") / "hooks" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
stamp = datetime.datetime.now().isoformat(timespec="seconds")
with open(log_dir / "audit.log", "a", encoding="utf-8") as log:  # for people
    log.write(f"{stamp}  {hook:<12}  {tool}  {input_text[:200]}\n")
with open(log_dir / "audit.jsonl", "a", encoding="utf-8") as log:  # for the flow visualizer
    log.write(json.dumps({"time": stamp, "hook": hook, "tool": tool, "input": input_text[:500]}, ensure_ascii=False) + "\n")

# ---- 2. guard: no deleting files from the terminal --------------------------
is_pre = re.search(r"pre.?tool.?use", hook, re.IGNORECASE)
if is_pre and re.search(r"\b(rm|del|rmdir|Remove-Item)\b", input_text, re.IGNORECASE):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Demo guard hook: deleting files is not allowed in this workspace.",
        }
    }))

sys.exit(0)  # exit 0 and no output = carry on as normal
