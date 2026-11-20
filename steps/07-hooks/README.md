# Step 07: Hooks (code the harness always runs)

**New concept:** a *hook* is your own command that the **harness** runs at
fixed points in the agent loop: when a prompt arrives, before a tool runs,
after it runs, when the agent finishes. The model can't skip a hook or talk
its way around it. Use hooks for things that must happen *every* time:
audit logs, policy checks, formatting.

```
07-hooks/
├── .vscode/mcp.json
├── mcp/…
├── cards/                         ← something for the demo to (try to) delete
└── .github/
    ├── copilot-instructions.md
    ├── agents/hello.agent.md      (same as step 06)
    ├── hooks/
    │   ├── audit.json             ← NEW: which events run which command
    │   └── scripts/audit.py       ← NEW: writes the audit log, blocks "rm"/"del"
    ├── prompts/greet.prompt.md
    └── skills/…
```

## What `audit.json` says

| Event | When the harness runs `audit.py` |
|-------|----------------------------------|
| `UserPromptSubmit` | you send a message |
| `PreToolUse` | **before** every tool call. The hook can *deny* it |
| `PostToolUse` | after every tool call |
| `Stop` | the agent has finished its reply |

`audit.py` gets a JSON description of the event on stdin. It appends a line
to `.github/hooks/logs/audit.log` (and to `audit.jsonl` for the visualizer).
Before a tool runs, it prints `permissionDecision: deny` if the command
deletes files.

## Demo

1. Open `steps/07-hooks`, start the MCP server (as in step 06).
2. Select **Hello**: `Say hello to Carlos`
3. Open `.github/hooks/logs/audit.log`. There's a line for your prompt,
   a `PreToolUse` and a `PostToolUse` line for every tool call (skill reads,
   `lookup_teammate`), and a `Stop` line. **No prompt asked for this. The harness did it.**
4. Switch to the built-in **Agent** and ask: `delete the cards folder using the terminal`.
   The hook sees `rm`/`del`/`Remove-Item` in the command and **denies** it,
   even if you'd have clicked *Allow*.
5. Optional: run the [visualizer](../../visualizer) in Live mode
   (`python ../../visualizer/serve.py`, then Simple Browser →
   `http://localhost:8765/#live`) and watch each event as it happens.

To show the hook working without the agent, run it yourself (this works in
PowerShell and bash):

```
'{"hook_event_name":"PreToolUse","tool_name":"run_in_terminal","tool_input":{"command":"rm -rf cards"}}' | python .github/hooks/scripts/audit.py
```

> **Preview feature.** Agent hooks are in preview in VS Code and the exact
> event names and JSON fields have changed between releases. If nothing
> appears in the log:
> * check that hooks are enabled (Settings → search **"hooks"**),
> * look at **Output → GitHub Copilot Chat** for hook errors,
> * compare `audit.json` with the hooks page in the VS Code docs for your version.
>
> The hook runs `python .github/hooks/scripts/audit.py` from the workspace root.
> On Windows, if `python` opens the Microsoft Store, change `python` to `py` in `audit.json`.

## Talking point: advice vs. enforcement

| Piece | Decided by | Can the model skip it? |
|-------|-----------|------------------------|
| Instructions, skills, prompts | text the model reads | yes, it's advice |
| `tools:` allow-list | the harness | no |
| Approval prompts | the harness + you | no |
| Hooks | the harness runs your code | **no** |
