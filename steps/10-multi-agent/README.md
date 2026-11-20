# Step 10: Multi-agent (one agent's output is another agent's input)

**New concept:** an *orchestrator* agent that does no work itself. It runs
other agents as **subagents** and passes the output of one into the input
of the next.

```
 You ──► Welcome Host (orchestrator, tools: agent)
            │
            ├─1─► Hello (subagent)        "Greet Priya. Greeting line only."
            │        └─ lookup_teammate (MCP) ─► "Namaste, Priya! 🙏 Good morning."
            │                                              │
            │◄──────────────── greeting ───────────────────┘
            │
            ├─2─► Card Writer (subagent)  "Make a card for Priya with: Namaste, Priya! 🙏 …"
            │        └─ create_file ─► cards/priya.md
            │◄──────────────── "Created cards/priya.md." ─┘
            │
            └──► You: "Greeting: Namaste, Priya! 🙏 Good morning. · Card: cards/priya.md"
```

```
10-multi-agent/
└── .github/
    ├── agents/
    │   ├── welcome-host.agent.md  ← NEW: orchestrator, tools: ['agent'], agents: [Hello, Card Writer]
    │   ├── hello.agent.md         ← changed: "as a subagent, do exactly the task"
    │   └── card-writer.agent.md   ← changed: takes the greeting from its task
    ├── prompts/
    │   └── welcome.prompt.md      ← NEW: /welcome Priya
    └── hooks/audit.json           ← changed: also logs SubagentStart / SubagentStop
```

Everything else (skills, MCP server, evals) is carried over from step 09.

## Handoff (step 08) vs. subagents (this step)

| | Handoff | Subagent |
|---|---|---|
| Who starts the next agent | **you**, by clicking a button | **the orchestrator's model**, by calling the `agent` tool |
| Context | the same conversation continues | each subagent gets a **fresh, separate** context: its own agent file plus the task |
| What comes back | nothing; you're now talking to the new agent | only the subagent's **final reply**, as a tool result |
| Good for | human checkpoints (plan → *you review* → build) | automatic pipelines, keeping the main context small |

## Demo

1. Open `steps/10-multi-agent`, start the MCP server (as in step 06).
2. Optional, to watch it live (recommended), in the terminal:
   ```bash
   python ../../visualizer/serve.py
   ```
   Then **Simple Browser: Show** → `http://localhost:8765/#live`, next to the chat.
3. Select **Welcome Host** in the agent picker, type: `Welcome Priya to the team`
   (or run `/welcome Priya`).
4. Watch:
   * In chat: Host calls the subagent tool twice. Expand each call to see the
     task Host wrote and the reply that came back.
   * In the visualizer: **Hello** lights up (its loop calls `lookup_teammate`),
     then **Card Writer** (its loop creates `cards/priya.md`), then Host answers.
5. Open `cards/priya.md`: the greeting Hello wrote, saved by a different agent.
6. Before or after the live run, step through the **09 Multi-agent** scenario in
   Guided mode. The context panel switches between agents, so you can see that
   Hello's and Card Writer's contexts start empty and Host only ever gets the
   two short results.

Eval it: `python evals/record.py start multi`, run the prompt, record
`multi-agent-welcome`, then `python evals/grade.py multi`. The case checks the
final reply *and* that the trace shows both subagents and the MCP call.

## Talking points

* **The orchestrator has one tool: `agent`.** It can't greet or write
  files, so it *has* to delegate. Small tool lists keep each agent honest.
* **Fresh context per subagent.** Hello reads skills and calls MCP. None
  of that fills Host's context. Host sees one line back.
* **The task text is the interface.** What Host writes into the task is
  everything the next agent knows. Write it like a function's inputs.
* **Same harness, same rules.** Subagent tool calls still go through
  approvals and hooks. The audit log shows every one.

> **Version note.** Running custom agents as subagents, the `agents:` field,
> and the `SubagentStart`/`SubagentStop` hook events are newer VS Code
> features, and they may be named differently in your version. If Host can't
> start Hello, check that the `agent` tool is enabled in the tool picker, and
> look at the subagents section of the VS Code docs. You can still show the
> same pipeline with the step 08 handoff (a person clicks instead) and with
> **Play sample: multi-agent** in the visualizer.
