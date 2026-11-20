# Copilot Agent Flow (visualizer)

A one-page UI that shows **what travels between you, the harness, the model,
skills, tools, MCP and hooks** while an agent works. It's one HTML file plus a
tiny Python server (standard library only). Nothing to install.

## Guided mode: step through each demo

Open `visualizer/index.html` in any browser by double-clicking it, or in VS Code:
right-click the file → **Open with Live Preview**, or use **Simple Browser**
(see below).

* Pick a scenario: **01 Hello World, 02 Instructions, 04 Skill, 05 Tool (script), 06 MCP tool, 07 Hook blocks a tool, 07 Handoff, 09 Multi-agent**
* **→ / ←** step forward and back, **Space** plays it on its own
* Each step animates the message along the wire and explains it
* The **Context window** panel shows what the model sees on its next call.
  Watch skills arrive as a one-line description (*always*), then the full
  SKILL.md only when it's needed (*on demand*), then tool results.
* The counters show **model calls** and **tool runs**, which makes the loop visible.
* In **09 Multi-agent** the context panel follows the agent whose loop is
  running (dashed outline in the Agents lane): Host, then Hello with a fresh
  context, then Card Writer with a fresh context, then back to Host.

## Live mode: watch your real agent

Live mode animates the hook events from steps 07, 08 and 09 as they happen.

1. Open `steps/09-multi-agent` (or `07-hooks-handoffs` / `08-evals`) in VS Code.
2. In the terminal:
   ```bash
   python ../../visualizer/serve.py
   ```
3. In VS Code: **Command Palette → Simple Browser: Show →** `http://localhost:8765/#live`
   and drag it next to the chat panel.
4. Chat with the **Hello** agent, or with **Welcome Host** in step 09. Every prompt, tool call,
   tool result, subagent start/stop and finish appears on the diagram. While a
   subagent is working, its box in the Agents lane gets a dashed outline.

How it works: the audit hook (`.github/hooks/scripts/audit.py`) also writes
`.github/hooks/logs/audit.jsonl`. `serve.py` serves this page and returns new
lines from that file at `/api/events`, and the page polls it every second.
The server listens on localhost only.

No hooks in your VS Code version, or no time to set up? Click **Play sample:
one agent** or **Play sample: multi-agent** in Live mode.

## What it can and can't see

* Live mode sees only what the hooks report: prompts, tool calls and
  results, and when the agent finished. It doesn't see what's inside the
  model call, so the context-window panel appears in Guided mode only.
* Tool names differ between VS Code versions. The page sorts them into
  built-in, terminal or MCP from the name and input, so an unknown tool
  shows up as a built-in tool.
