# Concepts: what all these files actually are

## The one-sentence version

> An **agent** is a **model** running in a **loop** inside a **harness**. The
> harness gives it **context** (instructions, skills) and **tools**, and runs
> the tools on the model's behalf.

## The agent loop (what the harness does)

```
             ┌──────────────────────────── HARNESS (VS Code + Copilot Chat) ───────────────────────────┐
             │                                                                                          │
  you ──►    │  1. Build the context                                                                    │
  prompt     │     • agent file body (.agent.md)          ← who am I                                    │
             │     • copilot-instructions.md              ← rules for this repo                         │
             │     • skill names + descriptions           ← what know-how is available                  │
             │     • tool list (from `tools:`)            ← what I'm allowed to do                      │
             │     • your message (+ prompt file)                                                       │
             │                         │                                                                │
             │                         ▼                                                                │
             │  2. Call the MODEL ──► it answers with text ...................................► reply   │
             │                         │   ... or with "please call tool X with args Y"                 │
             │                         ▼                                                                │
             │  3. HOOK: PreToolUse    (your code; can block)                                           │
             │  4. Ask you to approve  (if needed)                                                      │
             │  5. Run the tool  ──►  built-in (read/edit/execute…)  or  MCP server  or  script         │
             │  6. HOOK: PostToolUse   (your code; e.g. audit log)                                      │
             │  7. Add the tool result to the context, go back to 2                                     │
             └──────────────────────────────────────────────────────────────────────────────────────────┘
```

The model **never runs anything itself**. It can only ask. Everything in the
box is the harness.

## Glossary

| Term | In VS Code | What it is | Step |
|------|-----------|------------|------|
| **Model** | model picker in chat | The LLM. It reads text and writes text, including "call this tool" requests. | all |
| **Harness** | Copilot Chat in VS Code | The program around the model: builds the context, runs the loop, runs tools, asks for approval, runs hooks. The same `.github` files also work in other harnesses (Copilot CLI, Copilot cloud agent). | all |
| **Agent** | `.github/agents/*.agent.md` | A named setup: system prompt + tool allow-list (+ model, handoffs). The built-in *Agent*, *Ask* and *Plan* are agents too. | 01 |
| **Instructions** | `.github/copilot-instructions.md`, `*.instructions.md`, `AGENTS.md` | Context added **automatically** to every request (or every request about matching files). | 02 |
| **Prompt file** | `.github/prompts/*.prompt.md` | A saved task you run with `/name`. Can choose the agent and ask for inputs. | 03 |
| **Skill** | `.github/skills/<name>/SKILL.md` | A folder of know-how (steps, reference files, scripts) loaded **only when relevant**. Open format, so it's portable across agents. | 04, 05 |
| **Tool** | `tools:` in the agent file, 🔧 picker in chat | Something the agent can *do*: read a file, edit, run a command, fetch a URL, call MCP. | 05 |
| **MCP server** | `.vscode/mcp.json` | A process that offers tools in a standard format. Local (stdio) or remote (HTTP). | 06 |
| **Hook** | `.github/hooks/*.json` | Your command, run by the harness at lifecycle events. Deterministic: the model can't skip it. | 07 |
| **Handoff** | `handoffs:` in the agent file | A button that passes the conversation to another agent. | 07 |
| **Eval** | `evals/` (step 08) | A test for agent behaviour: checks properties of the reply and of the tool trace, across several runs. Can be rules or an LLM judge. | 08 |
| **Trace** | audit-hook log (step 07/08) | The record of which tools the agent called, with which inputs. Lets you test *how* it answered. | 07, 08 |
| **Subagent** | `agent` tool, `agents:` in the agent file | An agent started by another agent's model, with a fresh, separate context. Only its final reply goes back. | 09 |
| **Orchestrator** | e.g. `welcome-host.agent.md` | An agent whose job is to delegate: it runs subagents in order and passes one's output into the next one's task. | 09 |

## Which one should I use?

| I want… | Use |
|---------|-----|
| a rule that always applies in this repo | **instructions** |
| a one-click, repeatable task | **prompt file** |
| a persona with its own tools and limits | **custom agent** |
| know-how that's only needed sometimes (maybe with scripts) | **skill** |
| the agent to reach a system (API, DB, ticket tool) | **tool**: an MCP server, or a script in a skill |
| something that must happen every time, whatever the model decides | **hook** |
| a workflow across roles (plan → build → review) | **handoffs** / **subagents** |
| to know whether a change made the agent better or worse | **evals**: tool tests, output + trace checks, an LLM judge |

## Advice vs. enforcement

```
 advice (the model reads it, and usually follows it)     enforcement (the harness does it)
 ──────────────────────────────────────────────────     ──────────────────────────────────
 instructions · agent body · skills · prompt files      tools: allow-list · approvals · hooks
```

If something **must** happen, don't only write it in a Markdown file. Put
it in a hook or leave the tool out of the allow-list.
