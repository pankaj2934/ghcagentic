# 60-minute run sheet: "Hello, Agent!"

## Before the talk (15 min, the day before)

- [ ] VS Code + Copilot Chat signed in; custom agents show up in the agent dropdown
- [ ] `git config user.name` prints your name (step 05 depends on it)
- [ ] `python --version` (or `py --version` on Windows) shows Python 3.9 or newer, for step 06/07. Use the same command name in `.vscode/mcp.json` and `.github/hooks/audit.json`
- [ ] Run every demo prompt once, so you know the approval prompts and how long each takes
- [ ] Settings → search "agent skills" and "hooks" → enabled (if those settings exist in your version)
- [ ] Open `steps/06-mcp-local/.vscode/mcp.json` → **Start**. If it fails, MCP is blocked by policy: use the fallback (below)
- [ ] `python evals/test_tools.py` is green in `steps/08-evals`. Optionally record a `baseline` run the day before, so `/judge baseline` has data
- [ ] Open `visualizer/index.html` in a browser tab (Guided mode needs no setup). For Live mode, check that `python ../../visualizer/serve.py` works from `steps/08-evals`
- [ ] Zoom the editor (`Ctrl +`) and chat font; turn off notifications
- [ ] Optional: one VS Code window per step, already open, so switching is instant

## Timeline

| Time | Section | Step | What to show | Key message |
|------|---------|------|--------------|-------------|
| 0:00–0:05 | Intro | – | Title, agenda, "by the end you'll know what every file in `.github/` does" | |
| 0:05–0:12 | **What is an agent?** | – | [`concepts.md`](concepts.md) loop diagram, then the **visualizer**: step through *01 Hello World* | Model + loop + tools, inside a **harness** |
| 0:12–0:17 | Hello, World | 01 | `hello.agent.md`, pick **Hello**, ask anything | An agent is one Markdown file. `tools: []` means it can only talk |
| 0:17–0:22 | Instructions | 02 | `copilot-instructions.md`, sign-off appears even in built-in Agent; show References | Context the harness adds for you |
| 0:22–0:27 | Prompt files | 03 | `/greet Priya` | Reusable task vs. persona |
| 0:27–0:37 | **Skills** | 04 | `Say hello to Priya in Hindi`, expand tool calls: SKILL.md → languages.md; then Swahili | Loaded on demand (progressive disclosure), open format |
| 0:37–0:45 | **Tools** | 05 | `Say hello to me`, **approval prompt**, the JSON output; remove `execute` and retry | The model asks, the harness acts. `tools:` is the allow-list |
| 0:45–0:52 | **MCP (local)** | 06 | `python mcp/demo_client.py`, `mcp.json`, `Say hello to Priya` / `Bob` | Your own typed tools; a standard protocol |
| 0:52–0:56 | Hooks & handoffs | 07 | *Make a greeting card* button → `cards/carlos.md`; `audit.log`; blocked `rm` | Advice vs. enforcement |
| (bonus) | **Multi-agent** | 09 | Guided *09 Multi-agent*, then live: `Welcome Priya to the team` with the visualizer in Live mode | Orchestrator + subagents: output of one is the input of the next; a fresh context each |
| 0:56–1:03 | **Evals** | 08 | `test_tools.py`; `grade.py example` (the "guessed without the tool" failure); `/judge` | Test properties and the trace, across several runs |
| 1:03–1:05 | Wrap-up + Q&A | – | Final file tree (root README), "which one should I use?" table | |

That's 65 minutes. To fit 60: run step 03 and step 07 as file walk-throughs
(no live demo), and in step 08 show `grade.py example` instead of recording a
live run. Running late on the day? Do the same, and skip `/judge`.

## Using the visualizer during the talk

* **Before each live demo**, step through the matching scenario in the visualizer (arrow keys) so people know what to look for, then run it for real in VS Code.
* For **04 Skill**, stop on step 2 and point at the context panel: only the skill's *description* is there. Then press → and watch SKILL.md arrive.
* For **05/06**, point at the *model calls* counter: one greeting takes 3 model calls.
* **Live mode** for step 07/08: put Simple Browser next to the chat and let the audience watch the tool calls appear as you type.

## Lines that land

* "Every step changes **one** file or adds **one** file. Watch the folder tree."
* (step 01) "This isn't really an agent yet. It has no tools, so it's a chatbot with a name."
* (step 04) "The model only sees the skill's *description* until it needs the skill. That's how you can have 50 skills without filling the context."
* (step 05) "Who ran that script? Not the model. The model *asked*, VS Code asked **you**, then VS Code ran it."
* (step 06) "MCP is just JSON lines over stdin/stdout. `initialize`, `tools/list`, `tools/call`."
* (step 07) "Markdown is advice. Hooks and the tool allow-list are enforcement."
* (step 09) "Host has exactly one tool: start another agent. It can't do the work, so it has to delegate. And it only ever sees one line back from each helper."
* (step 08) "The reply looked perfect, but the trace shows it never called the tool. It guessed. That's why you test the trajectory as well as the answer."

## Fallbacks

| Problem | Do this |
|---------|---------|
| Agent not in the dropdown | Check you opened the **step folder** (not the repo root). Reload Window. |
| Skill isn't used | Say "use the greeting-etiquette skill", or type `/greeting-etiquette`. Check the skills setting. |
| Script approval is slow or blocked | Run `bash …/whoami.sh` / `…whoami.ps1` in the terminal yourself and paste the output. |
| MCP blocked by policy | `python mcp/demo_client.py` to show the protocol, then use step 05 (script tool) for the live agent demo. |
| MCP server won't start | Usually the Python command name: try `py` (Windows) or `python3` (Mac/Linux) in `.vscode/mcp.json`. Check **Output → MCP: hello-mcp** for the error. |
| Hooks don't fire | Preview feature: show `audit.json` + `audit.py`, and run the script by hand (see the step 07 README for the command) |
| The model words its reply differently | That's expected, LLMs vary. Point out the parts that matched the skill (greeting word, emoji, name). |

## Audience Q&A crib

* **Do these files work outside VS Code?** Skills and `AGENTS.md`/instructions are read by Copilot CLI and the Copilot cloud agent too. Skills use an open format that other agents (e.g. Claude Code) also read.
* **Where do personal (not repo) agents/skills go?** In your user profile. Use **Chat: New Custom Agent / New Skill** in the Command Palette and choose *User*.
* **Can I pin a model per agent?** Yes, `model:` in the agent front matter.
* **Is MCP safe?** Local stdio servers run with your permissions, like any script. Review them. Organizations can block MCP, or allow-list servers, by policy.
* **Skill vs. MCP?** A skill is know-how (plus maybe scripts). MCP gives you typed, reusable tools that any MCP client can use. They work well together: the skill says *when and how* to use the tool.
