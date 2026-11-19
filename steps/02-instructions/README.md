# Step 02: Always-on instructions

**New concept:** *instructions* are context that the harness adds to every
request automatically. The agent file says **who the agent is**. The
instructions file says **what's true for this whole repo**.

```
02-instructions/
└── .github/
    ├── copilot-instructions.md   ← NEW: applies to every chat in this workspace
    └── agents/
        └── hello.agent.md        ← changed: now uses a name if it knows one
```

## Demo

1. Open `steps/02-instructions` as the workspace folder.
2. Select the **Hello** agent and type: `Hi, I'm Pankaj`

Expected:

> Hello, Pankaj! 👋
> — sent by the Copilot Demo Team

3. Switch to the built-in **Ask** or **Agent** and ask anything. The sign-off is
   still there, because instructions apply to *all* agents.
4. Expand the **References** / *Used n references* section in the reply to show
   that `copilot-instructions.md` was attached by the harness. You didn't attach it.

## Related files you can mention

| File | Scope |
|------|-------|
| `.github/copilot-instructions.md` | Whole workspace, always |
| `.github/instructions/*.instructions.md` with `applyTo: "**/*.py"` | Only when matching files are involved |
| `AGENTS.md` at repo root | Same idea, an open convention several AI tools read |

## Talking point

The agent can only greet you by name because **you typed it**. It has no way
to find out who you are. Hold that thought for step 05.
