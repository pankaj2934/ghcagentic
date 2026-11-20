#!/usr/bin/env python3
"""Record the Hello agent's replies so grade.py can check them.

There's no API to drive Copilot Chat from a script, so a person runs the
prompt and this script saves the result:

    python evals/record.py start baseline     # begin a run called "baseline"
    python evals/record.py list               # show the prompts to type

    # In Copilot Chat: pick the agent, type the case's prompt, click the
    # reply's Copy button. Then:
    python evals/record.py skill-language     # saves the clipboard as the reply

Each recording saves two files in evals/runs/<run>/:
    <case>.<n>.txt          the reply (n = attempt 1, 2, 3, …)
    <case>.<n>.trace.log    the tool calls the audit hook logged meanwhile

Record a case several times to measure how consistent the agent is.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
RUNS = ROOT / "runs"
CURRENT = RUNS / ".current"
AUDIT_LOG = ROOT.parent / ".github" / "hooks" / "logs" / "audit.log"


def load_cases():
    return {c["id"]: c for c in json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))["cases"]}


def audit_size():
    return AUDIT_LOG.stat().st_size if AUDIT_LOG.exists() else 0


def read_clipboard():
    """Read text from the clipboard with tkinter (ships with Python on Windows/macOS)."""
    try:
        import tkinter
        root = tkinter.Tk()
        root.withdraw()
        text = root.clipboard_get()
        root.destroy()
        return text
    except Exception:
        return None


def read_pasted():
    end_key = "Ctrl+Z then Enter" if sys.platform == "win32" else "Ctrl+D"
    print(f"Paste the agent's reply, then press {end_key}:")
    return sys.stdin.read()


def start(run):
    run_dir = RUNS / run
    run_dir.mkdir(parents=True, exist_ok=True)
    CURRENT.write_text(json.dumps({"run": run, "audit_offset": audit_size()}), encoding="utf-8")
    print(f"Started run '{run}' in {run_dir}")
    print("Next: python evals/record.py list")


def record(case_id, paste=False):
    cases = load_cases()
    if case_id not in cases:
        sys.exit(f"Unknown case '{case_id}'. Known cases: {', '.join(cases)}")
    if not CURRENT.exists():
        sys.exit("No run started. First run: python evals/record.py start <run-name>")
    state = json.loads(CURRENT.read_text(encoding="utf-8"))
    run_dir = RUNS / state["run"]

    reply = None if paste else read_clipboard()
    if reply:
        print("Read the reply from the clipboard:\n" + "-" * 60 + f"\n{reply.strip()}\n" + "-" * 60)
    else:
        reply = read_pasted()
    if not reply.strip():
        sys.exit("Nothing to record.")

    # The trace: audit-log lines written since the previous recording
    trace = ""
    if AUDIT_LOG.exists():
        with open(AUDIT_LOG, "rb") as log:
            log.seek(state["audit_offset"])
            trace = log.read().decode("utf-8", errors="replace")

    attempt = len(list(run_dir.glob(f"{case_id}.*.txt"))) + 1
    (run_dir / f"{case_id}.{attempt}.txt").write_text(reply.strip() + "\n", encoding="utf-8")
    (run_dir / f"{case_id}.{attempt}.trace.log").write_text(trace, encoding="utf-8")
    state["audit_offset"] = audit_size()
    CURRENT.write_text(json.dumps(state), encoding="utf-8")
    print(f"Saved {case_id} attempt {attempt} ({len(trace.splitlines())} tool events) in run '{state['run']}'")


def list_cases():
    for case in load_cases().values():
        print(f"{case['id']:<18} [{case['agent']}]  {case['prompt']}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
    elif args[0] == "start" and len(args) == 2:
        start(args[1])
    elif args[0] == "list":
        list_cases()
    else:
        record(args[0], paste="--paste" in args)
