#!/usr/bin/env python3
"""Grade a recorded run against the checks in cases.json.

    python evals/grade.py baseline

Prints a table, writes evals/runs/<run>/report.md, and exits with code 1 if
any check failed, so it can run in CI.

Check types (all optional, per case):
    contains        every string must appear in the reply
    any_of          at least one of these strings must appear
    not_contains    none of these strings may appear
    regex           every regular expression must match the reply
    trace_contains  every string must appear in the tool-call trace (from the audit hook)

Matching ignores upper/lower case, except for regex.
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent


def git_first_name():
    try:
        name = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True).stdout.strip()
        return name.split()[0] if name else ""
    except Exception:
        return ""


def fill(value, variables):
    for key, val in variables.items():
        value = value.replace("{" + key + "}", val)
    return value


def run_checks(checks, reply, trace, variables):
    """Return a list of failure messages (empty list = pass)."""
    failures = []
    low_reply, low_trace = reply.lower(), trace.lower()
    for s in checks.get("contains", []):
        s = fill(s, variables)
        if s.lower() not in low_reply:
            failures.append(f"missing '{s}'")
    any_of = [fill(s, variables) for s in checks.get("any_of", [])]
    if any_of and not any(s.lower() in low_reply for s in any_of):
        failures.append(f"none of {any_of}")
    for s in checks.get("not_contains", []):
        s = fill(s, variables)
        if s.lower() in low_reply:
            failures.append(f"should not contain '{s}'")
    for pattern in checks.get("regex", []):
        if not re.search(fill(pattern, variables), reply, re.MULTILINE):
            failures.append(f"no match for /{pattern}/")
    for s in checks.get("trace_contains", []):
        s = fill(s, variables)
        if s.lower() not in low_trace:
            failures.append(f"tool trace missing '{s}'")
    return failures


def grade(run):
    run_dir = ROOT / "runs" / run
    if not run_dir.is_dir():
        sys.exit(f"No run called '{run}' in {ROOT / 'runs'}")
    cases = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))["cases"]
    variables = {"git_name": git_first_name()}

    rows, total, passed = [], 0, 0
    for case in cases:
        attempts = sorted(run_dir.glob(f"{case['id']}.*.txt"), key=lambda p: int(p.name.split(".")[-2]))
        if not attempts:
            rows.append((case["id"], "–", "not recorded"))
            continue
        ok, problems = 0, []
        for reply_file in attempts:
            trace_file = reply_file.with_name(reply_file.name[:-4] + ".trace.log")
            trace = trace_file.read_text(encoding="utf-8") if trace_file.exists() else ""
            failures = run_checks(case["checks"], reply_file.read_text(encoding="utf-8"), trace, variables)
            if failures:
                problems.append(f"#{reply_file.name.split('.')[-2]}: " + "; ".join(failures))
            else:
                ok += 1
        total += len(attempts)
        passed += ok
        status = "✅" if ok == len(attempts) else ("⚠️" if ok else "❌")
        rows.append((case["id"], f"{status} {ok}/{len(attempts)}", " | ".join(problems) or "all checks passed"))

    width = max(len(r[0]) for r in rows)
    print(f"\nRun: {run}\n")
    for case_id, score, detail in rows:
        print(f"{case_id:<{width}}  {score:<8}  {detail}")
    summary = f"{passed}/{total} attempts passed" if total else "nothing recorded yet"
    print(f"\n{summary}\n")

    report = [f"# Eval report: {run}", "", "| Case | Passed | Details |", "|---|---|---|"]
    report += [f"| {c} | {s} | {d} |" for c, s, d in rows]
    report += ["", f"**{summary}**", ""]
    (run_dir / "report.md").write_text("\n".join(report), encoding="utf-8")
    print(f"Report written to {run_dir / 'report.md'}")
    return 0 if total and passed == total else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(grade(sys.argv[1]))
