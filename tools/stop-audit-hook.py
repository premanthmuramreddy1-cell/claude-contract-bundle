#!/usr/bin/env python3
"""stop-audit-hook.py — Claude Code Stop hook: fail the turn if files changed and no AUDIT: line exists.

Reads the hook payload (JSON on stdin), finds the session transcript, and checks
whether the session ended its reply with an AUDIT: line from §34. Behaviour:

  - T0/T1 (no Edit/Write/NotebookEdit happened)     → allow stop, silently
  - edits happened, transcript has AUDIT:            → allow stop
  - edits connected, transcript unparseable / absent → allow stop but write a loud stderr note
    (failing closed on every parse error would brick the user's session; log loudly instead)
  - edits happened, AUDIT: absent                    → {"decision":"block","reason": …} on stdout
    (Claude Code re-opens the turn with the reason; the agent must run §43.6 / session-audit.py
     and quote its result, or write an honest NOT:/skipped line)

Read-only. Never blocks T0/T1. Never edits anything.
"""
import json, sys, pathlib, re

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
AUDIT_RE = re.compile(r"AUDIT:\s*(pass|mismatch|skipped)", re.I)

def allow(reason=""):
    if reason:
        print(reason, file=sys.stderr)
    sys.exit(0)

def block(reason: str):
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)

def main() -> int:
    raw = sys.stdin.read().strip()
    if not raw:
        allow("stop-audit-hook: empty payload; nothing to audit")
    try:
        payload = json.loads(raw)
    except Exception as e:
        allow(f"stop-audit-hook: unparseable payload ({e}); not blocking")

    journal = pathlib.Path.home() / ".claude" / "activity.log"
    if journal.exists():
        lines = journal.read_text(errors="ignore").splitlines()
        recent = lines[-400:]
        sid = None
        for ln in reversed(recent):
            m = re.match(r"^\d{2}:\d{2}:\d{2} \| (\S+) \|", ln)
            if m:
                sid = m.group(1)
                break
        rec = recent
        if sid:
            rec = [l for l in recent if f"| {sid} |" in l]
        edited = any(l.split("|")[2].strip().split()[0] in EDIT_TOOLS for l in rec if l.count("|") >= 2)
        if not edited:
            allow()
    else:
        edited = True  # no journal → rely on transcript edit scan below

    tp = payload.get("transcript_path") or payload.get("transcriptPath")
    if not tp or not pathlib.Path(tp).exists():
        allow("stop-audit-hook: no transcript_path; cannot verify AUDIT — NOT verified")

    final_text = ""
    edit_count = 0
    try:
        with open(tp, errors="ignore") as fh:
            for line in fh:
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                msg = obj.get("message", {})
                content = msg.get("content")
                if isinstance(content, str):
                    final_text += "\n" + content
                elif isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict):
                            if part.get("type") == "text":
                                final_text += "\n" + part.get("text", "")
                            elif part.get("type") == "tool_use" and part.get("name", "") in EDIT_TOOLS:
                                edit_count += 1
    except Exception as e:
        allow(f"stop-audit-hook: transcript unreadable ({e}); not blocking")

    if edit_count == 0 and not edited:
        allow()

    if AUDIT_RE.search(final_text):
        allow()
    block(
        "Files were changed this turn but the final message carries no §34 AUDIT: line "
        "('AUDIT: pass', 'AUDIT: mismatch — …', or 'AUDIT: skipped — <reason>'). "
        "Run: python3 ~/.claude/bin/session-audit.py --report - and quote its result, "
        "or state AUDIT: skipped — <reason> in one honest line (§22)."
    )

if __name__ == "__main__":
    sys.exit(main())
