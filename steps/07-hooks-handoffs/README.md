# Step 07: Hooks and handoffs (control the harness, chain agents)

Two new concepts:

* **Hooks:** your own commands that the **harness** runs at fixed points in
  the agent loop (before a tool runs, after it runs, …). The model can't skip
  them. Use them for things that must *always* happen: audit logs, policy
  checks, formatting.
* **Handoffs:** buttons under an agent's reply that pass the conversation on
  to **another agent** that has a different job and different tools.

```
07-hooks-handoffs/
├── .vscode/mcp.json
├── mcp/…
├── cards/                         ← NEW: Card Writer saves cards here
└── .github/
    ├── copilot-instructions.md
    ├── agents/
    │   ├── hello.agent.md         ← changed: adds a handoff to Card Writer
    │   └── card-writer.agent.md   ← NEW: second agent, tools: read + edit only
    ├── hooks/
    │   ├── audit.json             ← NEW: PreToolUse / PostToolUse → audit.py
    │   └── scripts/audit.py       ← NEW: writes the log, blocks "rm"/"del"
    ├── prompts/greet.prompt.md
    └── skills/…
```

## Demo: handoff

1. Open `steps/07-hooks-handoffs`, start the MCP server (as in step 06).
2. Select **Hello**: `Say hello to Carlos`
3. A **Make a greeting card** button appears under the reply. Click it, then
   press Enter: the **Card Writer** agent takes over and creates `cards/carlos.md`.
4. Point out that the two agents have **different tool allow-lists**. Hello
   can run commands but can't edit files. Card Writer can edit files but can't
   run commands. Least privilege, one agent per job.

## Demo: hooks

1. After the steps above, open `.github/hooks/logs/audit.log`. Every tool call
   (skill reads, the MCP calls, the file edit) has a `PreToolUse` and a
   `PostToolUse` line. **No prompt asked for this. The harness did it.**
2. Switch to the built-in **Agent** and ask: `delete the cards folder using the terminal`.
   The hook sees `rm`/`del`/`Remove-Item` in the command and **denies** it,
   even if you'd have clicked *Allow*.

> **Preview feature.** Agent hooks are in preview in VS Code and the exact
> event names and JSON fields have changed between releases. If nothing
> appears in the log:
> * check that hooks are enabled (Settings → search **"hooks"**),
> * look at **Output → GitHub Copilot Chat** for hook errors,
> * compare `audit.json` with the hooks page in the VS Code docs for your version.
>
> The hook runs `python .github/hooks/scripts/audit.py` from the workspace root.
> On Windows, if `python` opens the Microsoft Store, change `python` to `py` in `audit.json`.
>
> To show the hook working without the agent, run it yourself (this works in PowerShell and bash):
> ```
> '{"hook_event_name":"PreToolUse","tool_name":"run_in_terminal","tool_input":{"command":"rm -rf cards"}}' | python .github/hooks/scripts/audit.py
> ```

## Watch it live

The hook also writes `.github/hooks/logs/audit.jsonl`. Run
`python ../../visualizer/serve.py` and open `http://localhost:8765/#live` in
**Simple Browser** to see each tool call animate as it happens (see
[`visualizer/README.md`](../../visualizer/README.md)).

## Talking point: where each piece lives in the loop

| Piece | Decided by | Can the model skip it? |
|-------|-----------|------------------------|
| Instructions, skills, prompts | text the model reads | yes, it's advice |
| `tools:` allow-list | the harness | no |
| Approval prompts | the harness + you | no |
| Hooks | the harness runs your code | **no** |
