# Step 06: A local MCP server (your own tools)

**New concept:** *MCP* (Model Context Protocol) is a standard way to plug
**your own tools** into any agent. A server lists its tools (name,
description, input schema). The agent picks one, and the harness calls it.

This server is **local**: VS Code starts it as a child process and talks to
it over stdin/stdout. It's a single file with no dependencies. No
extension, no `npm install`, no network, no registry.

```
06-mcp-local/
├── .vscode/
│   └── mcp.json                 ← NEW: tells VS Code how to start the server
├── mcp/
│   ├── hello_mcp_server.py      ← NEW: the server (Python standard library only, ~120 lines)
│   ├── hello-mcp-server.js      ← NEW: the same server in Node (optional)
│   ├── team.json                ← NEW: the "database" behind lookup_teammate
│   └── demo_client.py           ← NEW: prints the raw MCP conversation
└── .github/
    ├── copilot-instructions.md
    ├── agents/hello.agent.md    ← changed: tools adds 'hello-mcp/*'
    ├── prompts/greet.prompt.md
    └── skills/
        ├── greeting-etiquette/  ← changed: uses lookup_teammate for colleagues
        └── identify-user/       ← changed: prefers get_current_user, script is the fallback
```

## Tools the server exposes

| Tool | Input | Returns |
|------|-------|---------|
| `get_current_user` | nothing | your git name, username, local time, part of day |
| `lookup_teammate` | `name` | role, city, language, *their* local time |

## Demo

1. **Show the protocol first** (works even if MCP is blocked):
   ```bash
   python mcp/demo_client.py
   ```
   Point out the `initialize` → `tools/list` → `tools/call` sequence. That's
   all of MCP that you need to know for this talk.
2. Open `.vscode/mcp.json`. Click the **Start** link that VS Code shows above
   `"hello-mcp"` (or run **MCP: List Servers** → hello-mcp → Start).
   If VS Code asks whether to trust the server, say yes.
   *Won't start?* On Windows, if `python` opens the Microsoft Store, change
   `"command"` to `"py"` in `mcp.json`. On macOS/Linux you may need `"python3"`.
3. Select **Hello** in chat. Open the 🔧 tool picker: `hello-mcp` and its two
   tools now appear.
4. Type: `Say hello to Priya`

> Namaste, Priya! 🙏 Good morning. Hope Bengaluru is treating you well!
> — sent by the Copilot Demo Team

   The agent read the skill, called `lookup_teammate`, and used Priya's
   language and her time zone.
5. `Say hello to Kenji`, `Say hello to Bob` (not found), `Say hello to me`
   (now uses `get_current_user` instead of the terminal script).
6. Open **Output → MCP: hello-mcp** to watch the server log each call.

## If MCP is blocked in your organization

MCP can be switched off by an organization policy, **local servers
included**. If the server won't start or its tools don't appear, the policy is
probably the reason. Don't try to get around it. Instead:

* run `python mcp/demo_client.py` to show what MCP looks like on the wire, and
* go back to **step 05**: a script shipped in a skill plus the built-in
  `execute` tool gives the agent the same ability, and the skill in this step
  already falls back to it.

## Talking point: built-in tool vs. script vs. MCP

| | Built-in tool | Script in a skill | MCP server |
|---|---|---|---|
| Who defines the inputs | VS Code | the SKILL.md text | a JSON schema (`inputSchema`) |
| How it's called | directly | via `execute` (a terminal command) | directly, as a typed tool call |
| Approval prompt | depends on the tool | yes, for each command | yes, for each tool (can be pre-approved) |
| Reusable outside VS Code | no | any agent that runs skills | any MCP client (CLI, other IDEs, other AI apps) |
