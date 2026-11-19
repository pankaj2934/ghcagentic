# Step 04: Skill

**New concept:** a *skill* is a folder of know-how (instructions plus optional
reference files and scripts) that the agent loads **only when it's relevant**.

```
04-skill/
└── .github/
    ├── copilot-instructions.md
    ├── agents/
    │   └── hello.agent.md          ← changed: tools: ['read']
    ├── prompts/
    │   └── greet.prompt.md
    └── skills/
        └── greeting-etiquette/     ← NEW: the skill's folder
            ├── SKILL.md            ← name + description + steps
            └── references/
                └── languages.md    ← only read if the skill needs it
```

## How a skill gets loaded (progressive disclosure)

1. **Always in context:** only the `name` and `description` from the front matter (a few words).
2. **When the request matches the description:** the agent reads `SKILL.md`.
3. **Only if needed:** the agent follows links in `SKILL.md` to read `references/languages.md`.

That's why the agent now needs the `read` tool: loading a skill means reading files.

## Demo

1. Open `steps/04-skill`.
2. Select **Hello**, type: `Say hello to Priya in Hindi`

Expected:

> Namaste, Priya! 🙏
> — sent by the Copilot Demo Team

3. Expand the tool calls in the reply. You'll see the agent read `SKILL.md`,
   then `languages.md`.
4. Try `Say hello to Priya in Klingon`. Klingon is in the table, so the model
   doesn't have to make anything up.
5. Try `Say hello to Priya in Swahili`. Swahili isn't in the table, so the
   skill tells the agent to say so.
6. You can also run the skill directly by typing `/greeting-etiquette` in chat.

> **Skills not showing up?** In older VS Code versions agent skills had to be
> switched on. Open Settings and search for **"agent skills"** (`chat.useAgentSkills`).

## Talking point: skill vs. instructions

| | `copilot-instructions.md` | Skill |
|---|---|---|
| Loaded | every request | only when relevant |
| Cost | always uses tokens | almost nothing until used |
| Can include | text | text, reference files, **scripts** (next step) |
| Portable | Copilot only | open format: the same `SKILL.md` folder works in Copilot (VS Code, CLI, cloud agent), Claude Code and others |
