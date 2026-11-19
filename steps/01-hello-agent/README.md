# Step 01: Hello World agent

**New concept:** a custom agent is a Markdown file in `.github/agents/`.

```
01-hello-agent/
└── .github/
    └── agents/
        └── hello.agent.md   ← the whole agent
```

## What's in the file

| Part | What it does |
|------|--------------|
| YAML front matter (`name`, `description`) | Shows up in the agent picker in Copilot Chat |
| `tools: []` | The agent gets **no tools**: it can only write text |
| Markdown body | The agent's **system prompt** (its instructions) |

## Demo

1. Open this folder as its own window: **File → Open Folder… → `steps/01-hello-agent`**
2. Open Copilot Chat (`Ctrl+Alt+I` / `⌃⌘I`).
3. In the agent picker (bottom of the chat box) choose **Hello**.
4. Type anything, e.g. `What's the weather?`

Expected reply:

> Hello, World! 👋

## Talking point

The agent is just **a model + a prompt + a list of tools**. Here the tool list
is empty, so it isn't really an "agent" yet. It can't act on anything, it can
only answer. The next steps add pieces one at a time.
