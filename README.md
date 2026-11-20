# Hello, Agent! Building agents in GitHub Copilot, one file at a time

A step-by-step **Hello World** for building agents in **GitHub Copilot in VS
Code**. Each step adds **one new concept** to the one before it, so you can
see exactly which file does what.

* No extensions to install
* No MCP servers from outside your machine (step 06 uses a local, single-file MCP server, and it's optional)
* Works on Windows, macOS and Linux

| Step | Folder | New concept | Try this in chat | Reply looks like |
|------|--------|-------------|------------------|------------------|
| 01 | [`steps/01-hello-agent`](steps/01-hello-agent) | **Custom agent** (`.agent.md`) | `anything` | Hello, World! 👋 |
| 02 | [`steps/02-instructions`](steps/02-instructions) | **Instructions** (always on) | `Hi, I'm Pankaj` | Hello, Pankaj! 👋 — sent by… |
| 03 | [`steps/03-prompt-file`](steps/03-prompt-file) | **Prompt file** (`/greet`) | `/greet Priya` | Hello, Priya! 👋 |
| 04 | [`steps/04-skill`](steps/04-skill) | **Skill** (`SKILL.md` + reference) | `Say hello to Priya in Hindi` | Namaste, Priya! 🙏 |
| 05 | [`steps/05-tool-script`](steps/05-tool-script) | **Tools** (built-in `execute` + a script in a skill) | `Say hello to me` | Hello, Pankaj! 👋 Good afternoon. |
| 06 | [`steps/06-mcp-local`](steps/06-mcp-local) | **MCP** (your own tools, local) | `Say hello to Priya` | Namaste, Priya! 🙏 Good morning. Hope Bengaluru… |
| 07 | [`steps/07-hooks-handoffs`](steps/07-hooks-handoffs) | **Hooks** and **handoffs** | `Say hello to Carlos` → *Make a greeting card* | `cards/carlos.md` + audit log |
| 08 | [`steps/08-evals`](steps/08-evals) | **Evals**: tool tests, output + trace checks, LLM-as-judge | `python evals/grade.py example`, `/judge baseline` | a pass/fail report per case |
| 09 | [`steps/09-multi-agent`](steps/09-multi-agent) | **Multi-agent**: an orchestrator runs Hello, then passes its output to Card Writer | `Welcome Priya to the team` (Welcome Host agent) | greeting + `cards/priya.md`, made by two subagents |

## How to use this repo

Copilot looks for `.github/agents`, `.github/skills` and the rest **at the root
of the folder you open**. Each step is a complete, separate workspace, so:

> **File → Open Folder… → `steps/0N-…`** (or `code steps/04-skill`)

Then open Copilot Chat (`Ctrl+Alt+I` on Windows/Linux, `⌃⌘I` on Mac), pick the
**Hello** agent from the agent dropdown, and use the prompt from the table.

**See what changed between steps:** select two files in the Explorer →
right-click → **Compare Selected**, or:

```bash
code --diff steps/04-skill/.github/agents/hello.agent.md steps/05-tool-script/.github/agents/hello.agent.md
```

## The final file layout

```
your-repo/
├── .github/
│   ├── copilot-instructions.md        INSTRUCTIONS  always-on rules for this repo
│   ├── agents/
│   │   ├── hello.agent.md             AGENT         persona + tool allow-list + handoffs
│   │   ├── card-writer.agent.md       AGENT         a second agent with other tools
│   │   ├── welcome-host.agent.md      AGENT         orchestrator: runs Hello → Card Writer as subagents
│   │   └── judge.agent.md             AGENT         grades the others (LLM-as-judge)
│   ├── prompts/
│   │   ├── greet.prompt.md            PROMPT        reusable /greet command
│   │   └── judge.prompt.md            PROMPT        /judge <run>
│   ├── skills/
│   │   ├── greeting-etiquette/        SKILL         know-how, loaded on demand
│   │   │   ├── SKILL.md
│   │   │   └── references/languages.md
│   │   └── identify-user/             SKILL         know-how + a bundled script
│   │       ├── SKILL.md
│   │       └── scripts/whoami.sh|.ps1
│   └── hooks/
│       ├── audit.json                 HOOK          harness runs this on every tool call
│       └── scripts/audit.py
├── .vscode/
│   └── mcp.json                       TOOLS (MCP)   how to start your local tool server
├── mcp/
│   └── hello_mcp_server.py            TOOLS (MCP)   the tool server itself
└── evals/
    ├── test_tools.py                  EVALS         deterministic tests for the tools
    ├── cases.json                     EVALS         prompts + checks on reply and trace
    ├── record.py / grade.py           EVALS         save replies, grade them
    └── rubric.md                      EVALS         what the Judge agent scores
```

## Learn the concepts

* [`visualizer/`](visualizer): **Copilot Agent Flow**, an animated diagram of what travels between you, the harness, the model, skills, tools, MCP and hooks for each step. Guided mode opens straight from disk. Live mode animates your real agent's hook events, subagents included (`python ../../visualizer/serve.py` from step 07, 08 or 09)

* [`docs/concepts.md`](docs/concepts.md): what an agent, the harness, tools, skills, MCP and hooks are, with a diagram of the agent loop
* [`docs/presentation-guide.md`](docs/presentation-guide.md): a 60-minute run sheet with timings, demo prompts and fallbacks

## Requirements

* VS Code with GitHub Copilot Chat (a recent version; custom agents, skills and hooks are newer features)
* `git` (step 05 reads `git config user.name`)
* Step 06–09 only: Python 3.9+ on the PATH (`python`, or `py` on Windows). Nothing to `pip install`. A Node version of the MCP server is included too, in case you'd rather use Node.
* Agent hooks (step 07) are a **preview** feature. Check that they're enabled in your VS Code.
