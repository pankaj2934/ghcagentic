# Step 05: Tools (built-in tools plus a script shipped in a skill)

**New concept:** *tools* are how an agent **acts**: it reads files, runs
commands, edits code. Up to now the agent could only talk. Now it can find
out **your** name by itself.

No extension and no MCP needed: we use VS Code's **built-in** `execute` tool
(run in terminal) to run a script that comes with the skill.

```
05-tool-script/
└── .github/
    ├── copilot-instructions.md
    ├── agents/
    │   └── hello.agent.md            ← changed: tools: ['read', 'execute']
    ├── prompts/
    │   └── greet.prompt.md
    └── skills/
        ├── greeting-etiquette/
        │   ├── SKILL.md              ← changed: adds time of day, uses identify-user
        │   └── references/languages.md
        └── identify-user/            ← NEW skill that bundles scripts
            ├── SKILL.md
            └── scripts/
                ├── whoami.sh         ← macOS / Linux
                └── whoami.ps1        ← Windows
```

The script reads `git config user.name` and the local clock, and prints JSON.
Before the demo, check that `git config user.name` returns your name.

## Demo

1. Open `steps/05-tool-script`.
2. Select **Hello**, type: `Say hello to me`
3. The agent will:
   1. match the request to **greeting-etiquette**, then **identify-user** (reads both `SKILL.md` files)
   2. ask to **run `whoami.ps1` / `whoami.sh`** in the terminal. **This is the harness asking you for permission.** Click *Allow*.
   3. read the JSON output and greet you:

> Hello, Pankaj! 👋 Good afternoon.
> — sent by the Copilot Demo Team

4. Try `Say hello to me in Tamil`. That uses both skills and the reference table.
5. Show the tool picker (the 🔧 icon in the chat box). The `tools:` list in
   the agent file decides which of these the agent is allowed to use.

## Talking points

* **The model never ran anything.** It *asked* to run a command. The harness
  (VS Code) showed you the approval, ran the command, and gave the output back
  to the model. That loop is what makes it an agent.
* `tools:` in the agent file is the **allow-list**. Remove `execute`, reload,
  and ask again: the agent can't run the script and falls back to "Hello, World!".
* A skill that bundles scripts is the simplest way to give an agent a custom
  tool when extensions and MCP aren't allowed.

### Built-in tool sets you can list in `tools:`

| Tool set | Lets the agent… |
|----------|-----------------|
| `read`    | read files, see problems/diagnostics |
| `search`  | search the workspace (text, file names, symbols) |
| `edit`    | create and edit files |
| `execute` | run terminal commands / tasks |
| `web`     | fetch web pages |
| `agent`   | start subagents |
| `todo`    | keep a task list |

You can also name one tool, e.g. `execute/runInTerminal` or `read/readFile`.
In chat, type `#` to see every tool available in your VS Code.
