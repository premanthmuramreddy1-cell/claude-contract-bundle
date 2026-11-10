#!/usr/bin/env python3
"""session-audit.py — behavioral audit for a finished task report.

§43.6 made mechanical. Reads a report (file or stdin) and the activity journal
(and its rotated sibling), then checks claims against observable evidence:

  1. report contains TIER, and at least one of VERIFIED:/NOT:/AUDIT:
  2. AUDIT: line (or a statement equivalent) present — missing = fail (or --allow-no-audit)
  3. every quoted gate keyword appears in the journal tail **followed by success evidence**
     (passed/exit 0/PASS/green/0 failed/✓) within 120 chars — presence alone is not verification
  4. forbidden patterns absent from the journal tail: --no-verify, push --force, push -f,
     git add -A, git add ., reset --hard, clean -fd
  5. AGENTS: count in report <= number of Agent dispatch lines in journal tail + small floor
  6. SHAs quoted under COMMITS: exist in the repo's object store (repo-aware; skipped with a note if not a repo).
     Existence proves membership in this repo, not that the commit belongs to this task — that remains human review.

Read-only. Exit 0 = audit clean, 1 = findings, 2 = usage error.
"""
import argparse, re, subprocess, sys, pathlib

FORBIDDEN = [r"--no-verify", r"push\s+--force", r"push\s+-f\b", r"git\s+add\s+-A\b",
             r"git\s+add\s+\.", r"reset\s+--hard", r"clean\s+-fd"]
GATE_TOKENS = ["pytest", "unittest", "npm test", "npx tsc", "vitest", "verify_contract.py",
               "node --check", "go test", "cargo test", "npm run build", "npm run lint"]

def fail(msgs):
    for m in msgs: print(f"FAIL  {m}")
    return 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="-", help="report file, or - for stdin")
    ap.add_argument("--log", default=str(pathlib.Path.home() / ".claude" / "activity.log"))
    ap.add_argument("--lines", type=int, default=400)
    ap.add_argument("--no-git", action="store_true")
    ap.add_argument("--allow-no-audit", action="store_true")
    a = ap.parse_args()

    report = sys.stdin.read() if a.report == "-" else pathlib.Path(a.report).read_text()
    journal = pathlib.Path(a.log)
    chunks = []
    rotated = pathlib.Path(str(journal) + ".1")
    if rotated.exists():
        chunks.append(rotated.read_text(errors="ignore"))
    if journal.exists():
        chunks.append(journal.read_text(errors="ignore"))
    tail = "\n".join("\n".join(chunks).splitlines()[-a.lines:])

    findings = []
    if not re.search(r"^TIER:", report, re.M):
        findings.append("report has no TIER: line")
    if not (re.search(r"^VERIFIED:", report, re.M) or re.search(r"^NOT:", report, re.M)):
        findings.append("report has neither VERIFIED: nor NOT: — no evidence quoted")
    mA = re.search(r"^AUDIT:\s*(pass|mismatch|skipped)\b", report, re.M | re.I)
    if not mA:
        findings.append("AUDIT: line missing or bare — must state 'pass', 'mismatch', or 'skipped — <reason>' (§43.6)")
    elif mA.group(1).lower() == "skipped" and not a.allow_no_audit:
        findings.append("AUDIT: skipped without --allow-no-audit — §43.6 is mandatory after T2+")

    EVIDENCE = r"(passed|exit\s*0|PASS|0 failed|all green|✓|green)"
    for tok in GATE_TOKENS:
        if tok not in report:
            continue
        if tok not in tail:
            findings.append(f"report quotes gate '{tok}' but the journal tail never shows it")
            continue
        m2 = re.search(re.escape(tok) + r".{0,120}?" + EVIDENCE, tail, re.I | re.S)
        if not m2:
            findings.append(f"report quotes gate '{tok}' and journal shows the command, but no success evidence near it")

    for pat in FORBIDDEN:
        m = re.search(pat, tail)
        if m:
            findings.append(f"forbidden pattern in journal tail: {m.group(0)!r}")

    m = re.search(r"AGENTS:.*?(\d+)", report)
    if m:
        claimed = int(m.group(1)); seen = len(re.findall(r"\bAgent\b", tail))
        if claimed > seen + 2:
            findings.append(f"report claims {claimed} agents, journal shows {seen} (tolerance +2)")

    if not a.no_git:
        r0 = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True)
        if r0.returncode != 0:
            print("note: not inside a git repo — COMMITS check skipped")
        else:
            m = re.search(r"COMMITS:(.*)", report)
            if m:
                for sha in re.findall(r"\b[0-9a-f]{7,40}\b", m.group(1)):
                    r = subprocess.run(["git", "cat-file", "-e", sha], capture_output=True)
                    if r.returncode != 0:
                        findings.append(f"quoted commit {sha} not in this repo's object store")

    if findings:
        return fail(findings)
    print("PASS  report consistent with journal + repo (read-only audit)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
