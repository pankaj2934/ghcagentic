# Step 03: Prompt file (a reusable slash command)

**New concept:** a *prompt file* is a saved prompt you run with `/name`. It
can choose which agent runs it and ask the user for input.

```
03-prompt-file/
└── .github/
    ├── copilot-instructions.md
    ├── agents/
    │   └── hello.agent.md
    └── prompts/
        └── greet.prompt.md    ← NEW: becomes /greet
```

## What's in the file

| Part | What it does |
|------|--------------|
| `agent: Hello` | Runs the prompt with the Hello agent, whichever agent is currently selected |
| `${input:name:...}` | VS Code asks for a value (or takes it from what you type after `/greet`) |
| `argument-hint` | Hint text shown in the chat box after you type `/greet` |

## Demo

1. Open `steps/03-prompt-file`.
2. In chat type `/greet Priya` and press Enter.

Expected:

> Hello, Priya! 👋
> — sent by the Copilot Demo Team

## Talking point: agent vs. prompt

| | Agent (`.agent.md`) | Prompt file (`.prompt.md`) |
|---|---|---|
| Is a… | persona that stays selected | one task you trigger |
| Started by | the agent picker | typing `/name` |
| Typical content | role, rules, allowed tools | "do X with ${input}" |
