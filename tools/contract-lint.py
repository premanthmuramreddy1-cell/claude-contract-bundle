#!/usr/bin/env python3
"""contract-lint.py — verify ~/.claude/CLAUDE.md and ~/.claude/RUNBOOK.md stay honest.

Checks (exit 1 on any failure, prints the list):
  1. every §N[.M] reference resolves to a defined section/subsection
  2. §44 covers F001–F100 as ten complete ranges
  3. §0.3 has a row for every # PART heading (29 parts), and §42 points at §0.3 + RUNBOOK
  4. forbidden stale strings are absent
  5. no duplicate section sub-headings (identical §N[.M]), RUNBOOK.md exists
  6. machine↔contract sync (WARN-tier, non-fatal): 15 settings claims — drift is reported, never fatal; machine facts rot
  7. existence of 8 core tools + 12 named plugins/skills
  8. the inline measured-words figure in §30 matches wc -w (±1%)
  9. no self-certifying claims; all v2026-11-08.N strings (master + shards) match the header version; reference shards exist

Read-only. Run after any edit to the contract:
  python3 ~/.claude/bin/contract-lint.py
"""
import re, sys, os, pathlib

HOME = pathlib.Path(os.path.expanduser("~"))
import os as _os
C = pathlib.Path(_os.environ.get("CONTRACT_MD", str(HOME / ".claude" / "CLAUDE.md")))
R = HOME / ".claude" / "RUNBOOK.md"
errors = []
warns = []

src = C.read_text()
lines = src.splitlines()

# ---- 1. headings + reference resolution
headings = set()
for ln in lines:
    m = re.match(r'^(#{2,4})\s+§(\d+)(?:\.(\d+))?', ln)
    if m:
        base, sub = m.group(2), m.group(3)
        headings.add(f"§{base}")
        if sub:
            headings.add(f"§{base}.{sub}")

import os as _os2
RULES = pathlib.Path(_os2.environ.get("CONTRACT_RULES", str((pathlib.Path(_os2.environ.get("CONTRACT_MD", "")).parent / "rules") if _os2.environ.get("CONTRACT_MD") else HOME / ".claude" / "rules")))
if RULES.exists():
    for rfile in RULES.glob("*.md"):
        for ln in rfile.read_text().splitlines():
            m = re.match(r'^(#{2,4})\s+§(\d+)(?:\.(\d+))?', ln)
            if m:
                base, sub = m.group(2), m.group(3)
                headings.add(f"§{base}")
                if sub:
                    headings.add(f"§{base}.{sub}")

for i, ln in enumerate(lines, 1):
    for m in re.finditer(r'§(\d+)(?:\.(\d+))?', ln):
        ref = f"§{m.group(1)}" + (f".{m.group(2)}" if m.group(2) else "")
        if ref not in headings:
            errors.append(f"line {i}: unresolved reference {ref}")

# ---- 2. F-range coverage (ten contiguous ranges of ten)
covered = set()
for m in re.finditer(r'F(\d{3})–F(\d{3})', src):
    covered.update(range(int(m.group(1)), int(m.group(2)) + 1))
missing_f = [f for f in range(1, 101) if f not in covered]
if missing_f:
    errors.append(f"§44 coverage gap: F{missing_f[0]:03d}..F{missing_f[-1]:03d} not covered")

# ---- 3. navigation maps agree with the document
parts = [ln for ln in lines if ln.startswith("# PART ")]
if len(parts) != 29:
    errors.append(f"expected 29 # PART headings, found {len(parts)}")
quick_index = next((l for l in lines if l.startswith("## §0.3")), None)
if quick_index is None:
    errors.append("missing §0.3 quick index")
else:
    qi_start = lines.index(quick_index)
    qi_block = "\n".join(lines[qi_start:qi_start + 40])
    for p in parts:
        # e.g. "# PART 17 — ..." -> expect "PART 17" row in the quick index
        m = re.match(r'# (PART \d+)', p)
        if m and m.group(1) not in qi_block:
            errors.append(f"quick index §0.3 has no row for {m.group(1)} ({p[:40]})")
idx42 = next((l for l in lines if l.startswith("## §42")), None)
if idx42 is None:
    errors.append("missing §42 index")
else:
    i42 = lines.index(idx42)
    block = "\n".join(lines[i42:i42 + 12])
    for needle in ("§0.3", "RUNBOOK.md"):
        if needle not in block:
            errors.append(f"§42 index does not reference {needle}")

# ---- 4. forbidden stale strings
for bad in ["~22k", "~16k", "Four state layers", "168-line", "exalxs"]:
    if bad in src:
        errors.append(f"stale string present: {bad!r}")
for line in (lines + R.read_text().splitlines()):
    if "NO plain" in line:          # explicit negation, fine
        continue
    for m in re.finditer(r'settings\.json\.bak-2026-11-08(?![-{])', line):
        errors.append(f"plain 'settings.json.bak-2026-11-08' claimed on line: {line.strip()[:60]}")

# ---- 5. duplicate ## SUBSECTION (identical full §N[.M] heading) + RUNBOOK exists
from collections import Counter
subs = Counter(re.match(r'^(##|###)\s+§(\d+(?:\.\d+)?)', ln).group(2)
               for ln in lines if re.match(r'^(##|###)\s+§(\d+(?:\.\d+)?)', ln))
for b, n in subs.items():
    if n > 1:
        errors.append(f"duplicate ^## section §{b} ({n}×)")
if not R.exists():
    errors.append("~/.claude/RUNBOOK.md missing")

ver = re.search(r'\*\*Version\*\*\s+(\d{4}-\d{2}-\d{2}\.\d+)', src)

# ---- 6. machine ↔ contract sync (the §37/§43 claims, enforced not asserted)
import json as _json
try:
    cfg = _json.loads((HOME / ".claude" / "settings.json").read_text())
except Exception as e:
    cfg = {}
    warns.append(f"settings.json unreadable/absent ({e}) — §37/§43 claims unverified, not fatal")
must = [
    ("hooks stops", "Stop" in cfg.get("hooks", {})),
    ("hooks PostToolUse wired", any(
        any("activity-log.sh" in h.get("command", "") for h in grp.get("hooks", []))
        for grp in cfg.get("hooks", {}).get("PostToolUse", []))),
    ("statusLine wired", "statusline.sh" in _json.dumps(cfg.get("statusLine", {}))),
    ("18 allow rules", len(cfg.get("permissions", {}).get("allow", [])) == 18),
    ("8 deny rules", len(cfg.get("permissions", {}).get("deny", [])) == 8),
    ("defaultMode auto", cfg.get("permissions", {}).get("defaultMode") == "auto"),
    ("MCP cap 8000", cfg.get("env", {}).get("MAX_MCP_OUTPUT_TOKENS") == "8000"),
    ("bash cap 4000", cfg.get("env", {}).get("BASH_MAX_OUTPUT_LENGTH") == "4000"),
    ("outputStyle Proactive", cfg.get("outputStyle") == "Proactive"),
    ("model fable-5-2", cfg.get("model") in ("fable-5-2", "fable-5.2", "fable 5.2")),
    ("subagents fable-5-1", cfg.get("env", {}).get("CLAUDE_CODE_SUBAGENT_MODEL") in ("fable-5-1", "fable-5.1", "fable 5.1")),
    ("autoCompact on", bool(cfg.get("autoCompact"))),
    ("enabledPlugins 52/13", sum(1 for v in cfg.get("enabledPlugins", {}).values() if v is True) == 52
                          and sum(1 for v in cfg.get("enabledPlugins", {}).values() if v is False) == 13),
    ("fable-5-2 effort high", cfg.get("modelSettings", {}).get("fable-5-2", {}).get("effortLevel") == "high" or cfg.get("modelSettings", {}).get("fable-5.2", {}).get("effortLevel") == "high"),
    ("fable-5-1 effort low", cfg.get("modelSettings", {}).get("fable-5-1", {}).get("effortLevel") == "low" or cfg.get("modelSettings", {}).get("fable-5.1", {}).get("effortLevel") == "low"),
]
for name, ok in must:
    if not ok:
        warns.append(f"settings drift: {name} no longer true — §37/§43 are stale")

# ---- 7. named tools & plugins exist (the §5/§44 roster, enforced)
import shutil as _shutil, glob as _glob
for tool in ["jq", "git", "node", "npm", "npx", "python3", "graphify", "claude"]:
    if not (_shutil.which(tool) or _glob.glob(str(HOME / ".local/bin" / tool))):
        warns.append(f"named tool missing: {tool}")
for plug in ["voltagent-qa-sec", "superpowers", "ruflo-swarm", "taste-skill",
             "claude-security", "design-review", "ponytail", "frontend-design",
             "remember", "feature-dev", "pr-review-toolkit", "deep-research"]:
    found = any(_glob.glob(str(HOME / root / "**" / f"*{plug}*"), recursive=True)
                for root in (".claude/plugins/cache", ".claude/skills", ".agents/skills"))
    if not found:
        warns.append(f"named plugin/skill missing: {plug}")
# ---- 9. forbidden self-congratulation + version consistency (no external truth from inside the file)
FORBIDDEN_SELF = ["currently passes (v", "self-verifies green", "proves itself correct"]
for bad in FORBIDDEN_SELF:
    if bad in src:
        errors.append(f"forbidden self-certification claim: {bad!r} — never assert your own verification, point at the command")
if ver:
    hv = ver.group(1)
    for i, ln in enumerate(lines, 1):
        for m in re.finditer(r'v(\d{4}-\d{2}-\d{2}\.\d+)', ln):
            if m.group(1) != hv:
                errors.append(f"line {i}: stale version v{m.group(1)} (header says {hv})")

for required in ["reference.md", "human-output.md"]:
    if not (RULES / required).exists():
        errors.append(f"shard missing: ~/.claude/rules/{required} (referenced by stubs/triggers)")
for rf in RULES.glob("*.md"):
    for ln in rf.read_text().splitlines():
        for m in re.finditer(r'v(\d{4}-\d{2}-\d{2}\.\d+)', ln):
            if ver and m.group(1) != ver.group(1):
                errors.append(f"{rf.name}: stale version v{m.group(1)} (master {ver.group(1)})")

held = sum(1 for _, ok in must if ok)
print(f"settings claims (WARN-tier): {held}/{len(must)} hold — drift is non-fatal; re-verify via RUNBOOK")
print(f"machine checks drifted: {len(warns)} — WARNs below (non-fatal; they change under you)")
for w in warns:
    print("  WARN", w)

words = len(src.split())
m = re.search(r'([\d,]+) words measured — lint-verified', src)
if m:
    inline = int(m.group(1).replace(",", ""))
    if abs(inline - words) > words * 0.01:
        errors.append(f"§30.1 claims {inline:,} words but file measures {words:,} — update the inline figure")
else:
    errors.append("§30.1 inline measured-words figure missing or reworded — keep it lint-checkable")
print(f"file: {C} · {len(lines)} lines · {words} words (~{round(words * 1.3 / 1000)}k tokens) · version {ver.group(1) if ver else 'MISSING'}")
print(f"headings: {len(headings)} · parts: {len(parts)} · F coverage: {'100/100' if not missing_f else 'GAP'}")
if errors:
    print("FAIL")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("PASS — structure consistent (not behavioral verification; §43.6 audits sessions)")
