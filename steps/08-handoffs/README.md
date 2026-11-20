# Step 08: Handoffs (pass the conversation to another agent)

**New concept:** a *handoff* is a button under an agent's reply that passes
the conversation to **another agent**, one with a different job and
different tools. A person stays in the loop: nothing happens until you click.

```
08-handoffs/
├── cards/                         ← Card Writer saves cards here
└── .github/
    ├── agents/
    │   ├── hello.agent.md         ← changed: adds a handoff to Card Writer
    │   └── card-writer.agent.md   ← NEW: second agent, tools: read + edit only
    ├── hooks/…                    (from step 07: logs every tool call)
    └── …                          (skills, prompts, MCP as before)
```

## What changed in `hello.agent.md`

```yaml
handoffs:
  - label: Make a greeting card     # the button text
    agent: Card Writer              # which agent takes over
    prompt: Turn the greeting above into a greeting card file.
    send: false                     # put the prompt in the box; you press Enter
```

## Demo

1. Open `steps/08-handoffs`, start the MCP server (as in step 06).
2. Select **Hello**: `Say hello to Carlos`
3. A **Make a greeting card** button appears under the reply. Click it, then
   press Enter: the **Card Writer** agent takes over and creates `cards/carlos.md`.
4. Point out that the two agents have **different tool allow-lists**. Hello
   can call MCP and run commands but can't edit files. Card Writer can edit
   files but can't run commands. Least privilege, one agent per job.
5. Open `.github/hooks/logs/audit.log`: the step 07 hook logged Card
   Writer's `create_file` call like any other tool call.
6. In the [visualizer](../../visualizer), step through **08 Handoff**. The
   context panel shows Hello's system prompt being *replaced* by Card Writer's.

## Talking point

A handoff is the simplest multi-agent pattern: **a person decides when the
next agent starts**. Good for checkpoints like *plan → you review → build*.
In step 10 an orchestrator agent starts the next agent by itself (subagents).
