# Steps: one folder per concept

Each folder is a complete VS Code workspace. Open the folder itself
(**File → Open Folder…**), not the repo root, and read its README for the
demo prompt and the talking points. Each step adds one thing to the one
before it.

| Folder | Concept | What it adds |
|--------|---------|--------------|
| [`01-hello-agent`](01-hello-agent) | Custom agent | `.github/agents/hello.agent.md` with `tools: []` |
| [`02-instructions`](02-instructions) | Instructions | `.github/copilot-instructions.md`, applied to every chat |
| [`03-prompt-file`](03-prompt-file) | Prompt file | `.github/prompts/greet.prompt.md` → `/greet` |
| [`04-skill`](04-skill) | Skill | `.github/skills/greeting-etiquette/` loaded on demand |
| [`05-tool-script`](05-tool-script) | Tools | built-in `execute` + a script bundled in a skill |
| [`06-mcp-local`](06-mcp-local) | MCP | a local, dependency-free MCP server + `.vscode/mcp.json` |
| [`07-hooks`](07-hooks) | Hooks | `.github/hooks/audit.json`: audit log + a guard that blocks deletes |
| [`08-handoffs`](08-handoffs) | Handoffs | a button that passes the chat to the Card Writer agent |
| [`09-evals`](09-evals) | Evals | tool tests, reply + trace checks, LLM-as-judge |
| [`10-multi-agent`](10-multi-agent) | Multi-agent | an orchestrator that runs Hello, then passes its output to Card Writer |
