#!/usr/bin/env python3
"""weekly-audit.py — the external-eye audit, run weekly against the journal.

Reads ~/.claude/activity.log and ~/.claude/activity.log.1 (the rotated one), groups lines
by session, and writes a markdown audit report to audits/AUDIT-<timestamp>.md (cwd) or
~/.claude/audits/. Findings are red flags plus missing-discipline signals:

  RED GIT      forbidden ops (--no-verify, force push, reset --hard, clean -fd, git add -A/.)
  SILENT EDIT  session with ≥1 Edit/Write but zero verification-flavoured command
               (test|tsc|lint|build|pytest|unittest|vitest|run|check|verify_contract)
  HOLLOW GATE  Edit burst immediately followed by no command at all in the same session
  HUGE OUTPUT  Bash/Edit briefs longer than ~140 chars were supposedly truncated — flag if journaled raw
  VOLUME       totals per session (sessions, edits, verifies, lines) for trend-spotting

Exits 0 always (it reports; humans/the reviewer decide). Prints a summary line and the path.
Read-only against the journal; the report is the only thing it writes.
"""
import argparse, re, sys, pathlib
from datetime import datetime

RED_PAT = [(r"--no-verify", "--no-verify"), (r"push\s+(--force|-f)\b", "force-push"),
           (r"reset\s+--hard", "reset --hard"), (r"clean\s+-fd", "clean -fd"),
           (r"git\s+add\s+(-A\b|\.)", "git add -A / .")]
VERIFY_HINT = re.compile(r"test|tsc|lint|build|pytest|unittest|vitest|check|verify_contract|run", re.I)
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}

LINE = re.compile(r"^(\d{2}:\d{2}:\d{2}) \| ([^|]+) \| (\S+) \| (.*)$")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=str(pathlib.Path.home() / ".claude" / "activity.log"))
    ap.add_argument("--out", default="", help="report path; default <cwd>/audits/AUDIT-<ts>.md or ~/.claude/audits/")
    args = ap.parse_args()

    chunks = []
    for suffix in (".1", ""):
        p = pathlib.Path(args.log + suffix)
        if p.exists():
            chunks.append(p.read_text(errors="ignore"))
    lines = [l for l in "\n".join(chunks).splitlines() if LINE.match(l)]

    sessions = {}
    red = []
    for l in lines:
        m = LINE.match(l)
        ts, sid, tool, brief = m.groups()
        s = sessions.setdefault(sid, {"lines": 0, "edits": 0, "verifies": 0, "tools": {}, "red": []})
        s["lines"] += 1
        s["tools"][tool] = s["tools"].get(tool, 0) + 1
        if tool in EDIT_TOOLS:
            s["edits"] += 1
        if tool == "Bash" and VERIFY_HINT.search(brief):
            s["verifies"] += 1
        for pat, name in RED_PAT:
            if re.search(pat, brief):
                s["red"].append(name)
                red.append((sid, ts, name, brief.strip()[:110]))

    out = pathlib.Path(args.out) if args.out else None
    if out is None:
        cwd_audits = pathlib.Path.cwd() / "audits"
        out = (cwd_audits if pathlib.Path.cwd().joinpath("CLAUDE.md").exists() else pathlib.Path.home() / ".claude" / "audits")
        out.mkdir(parents=True, exist_ok=True)
        out = out / f"AUDIT-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"

    edits_total = sum(s["edits"] for s in sessions.values())
    hollow = [sid for sid, s in sessions.items() if s["edits"] >= 1 and s["verifies"] == 0]
    big = [ (sid, t) for sid, s in sessions.items() for t, n in s["tools"].items() ]

    body = [
        f"# Weekly audit — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"Source: `{args.log}` + rotated sibling · sessions: {len(sessions)} · lines: {len(lines)}",
        "",
        "## Red flags (forbidden ops)"
    ]
    if red:
        body += [f"- **{name}** — {sid} @ {ts}: `{brief}`" for sid, ts, name, brief in red]
    else:
        body.append("- none")
    body += ["", "## Sessions that edited files with zero verification commands"]
    if hollow:
        body += [f"- {sid} — {sessions[sid]['edits']} edit(s), 0 verify-flavoured commands" for sid in hollow]
    else:
        body.append("- none")
    body += ["", "## Volume per session", "", "| session | lines | edits | verifies | tools |", "|---|---|---|---|---|"]
    for sid, s in sorted(sessions.items()):
        tools = ", ".join(f"{k}:{v}" for k, v in sorted(s["tools"].items(), key=lambda kv: -kv[1])[:4])
        body.append(f"| {sid} | {s['lines']} | {s['edits']} | {s['verifies']} | {tools} |")
    body += ["", "## How to read this",
             "Red flags = violation of §24.6/§36. Hollow sessions = output without proof (§22/§27).",
             "Both lists want a human or a fresh subagent to cross-check the journals — never the author of the work."]
    out.write_text("\n".join(body) + "\n")
    print(f"audit written: {out}")
    print(f"sessions={len(sessions)} lines={len(lines)} red={len(red)} hollow={len(hollow)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
