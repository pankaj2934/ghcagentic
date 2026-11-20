# Step 09: Evals (how do you know your agent works?)

**New concept:** an *eval* is a test for an agent. LLM replies vary from run
to run, so you don't check for one exact answer. You check **properties**:
did it use the right name, call the right tool, avoid making things up?

This step adds three layers of evals. They're all plain Python with nothing
to install, and none of them needs an API key.

```
09-evals/
├── evals/
│   ├── test_tools.py        ← NEW  layer 1: unit tests for the TOOLS (MCP server, hook, script)
│   ├── cases.json           ← NEW  layer 2: test prompts + checks on the reply and the trace
│   ├── record.py            ← NEW           saves a reply (from the clipboard) + its tool trace
│   ├── grade.py             ← NEW           grades a run, writes report.md, exit code 1 on failure
│   ├── rubric.md            ← NEW  layer 3: what the LLM judge scores
│   └── runs/example/        ← NEW           hand-written sample run (one failure on purpose)
└── .github/
    ├── agents/judge.agent.md    ← NEW: the Judge agent (LLM-as-judge)
    ├── prompts/judge.prompt.md  ← NEW: /judge <run>
    └── hooks/…                  ← from step 07: its audit log becomes the TRACE
```

## The three layers

| Layer | What it checks | How it runs | Same result every time? |
|-------|----------------|-------------|-------------------------|
| **1. Tool evals** | The tools do what their descriptions say | `python evals/test_tools.py`, also in CI | yes |
| **2. Output + trace evals** | The *agent's* reply contains/avoids certain text, and it called the right tools | you run the prompts, `record.py` saves them, `grade.py` grades them | the grader is; the agent isn't |
| **3. LLM-as-judge** | Things rules can't check: grounded? right tone? | `/judge <run>` in chat (the Judge agent) | no, the judge is a model too |

The **trace** is the trick that makes layer 2 work without any API: the
step 07 audit hook logs every tool call, and `record.py` saves the lines
logged since the previous recording next to each reply. So you can check
*how* the agent got an answer, as well as the answer itself ("did it really
call `lookup_teammate`, or did it guess?").

## Demo

**1. Tool evals (30 seconds)**

```bash
python evals/test_tools.py
```

Ten tests, all green, in under a second. These run in CI on every push
(`.github/workflows/tool-evals.yml` at the repo root).

**2. Show the grader on the sample run (1 minute)**

```bash
python evals/grade.py example
```

Point out `mcp-teammate ⚠️ 1/2`: in attempt 2 the agent **skipped the tool
and guessed** ("Hello, Kenji!"). The reply looks fine, but the trace shows no
`lookup_teammate` call. Testing only the final answer would miss that.

**3. Record a live run (3–4 minutes)**

```bash
python evals/record.py start baseline
python evals/record.py list
```

For two or three cases: select **Hello** in chat, type the prompt, click the
reply's **Copy** button, then:

```bash
python evals/record.py skill-language
```

(It reads the clipboard. If that doesn't work, add `--paste` and paste the
reply into the terminal.) Then:

```bash
python evals/grade.py baseline
```

**4. Catch a regression (2 minutes)**

Delete the `Hindi` row from `.github/skills/greeting-etiquette/references/languages.md`, then:

```bash
python evals/record.py start no-hindi
```

Run `Say hello to Priya in Hindi` again, record it, and grade `no-hindi`. The
`skill-language` case fails, because the skill now says Hindi "isn't listed".
**That's why evals exist: you changed one file and a test caught the
side-effect.** Put the row back afterwards.

**5. LLM-as-judge (2 minutes)**

In chat: `/judge baseline`. The **Judge** agent reads the rubric, the replies
and the traces, and writes `evals/runs/baseline/judge.md` with scores and
reasons.

## Talking points

* **Record each case several times.** Run `record.py <case>` 3–5 times. The
  report shows `3/5`, not just pass/fail. Consistency is part of quality.
* **Test properties, not exact strings.** `contains: ["Namaste"]`, not "the
  reply must equal `Namaste, Priya! 🙏 Good morning.`".
* **Test the trajectory, not just the answer.** `trace_contains` checks which
  tools ran.
* **Rules first, judge second.** Rule checks are cheap and give the same
  result every time. Use an LLM judge only for what rules can't check, and
  spot-check the judge, because it's a model too.
* **Evals pin down behaviour before you change things.** Record a
  `baseline`, change a prompt/skill/model, record again, compare the reports.

## Notes

* `{git_name}` in `cases.json` is replaced with the first word of your
  `git config user.name`.
* Traces are only as good as the hook. If hooks don't fire in your VS Code
  (preview), the `trace_contains` checks fail. Remove them from
  `cases.json` and grade the reply text only.
* `evals/runs/` is git-ignored except for `example/`.
