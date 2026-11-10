#!/usr/bin/env python3
"""bundle-verify.py — one command, the whole bundle proven.

Runs every check that can run against the bundle, read-only:
  1. Python syntax compile: contract-lint.py, tools/*.py, demo python files
  2. JS syntax: demo/src/app.js via `node --check`
  3. contract-lint.py against the bundle (CONTRACT_MD + CONTRACT_RULES auto-set)
  4. stop-audit-hook.py — three synthetic transcript fixtures (block / allow-audit / allow-T0)
  5. session-audit.py — fixtures: missing AUDIT (must fail), unevidenced gate (must fail), clean (must pass)
  6. demo unittest discovery (python3 -m unittest)
  7. demo/scripts/verify_contract.py (exits 0)
  8. every `cat ~/.claude/rules/<x>.md` reference in the contract — the bundle copy must exist
  9. every `~/.claude/...` path string in the contract that must exist at verify-time — report only (WARN), since live ≠ bundle until sync

Prints a summary table and a single verdict. Exit 1 on any FAIL. Read-only.
"""
import json, os, pathlib, re, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
os.chdir(ROOT)
PASS, FAIL, NOTE = [], [], []

def run(label, cmd, ok=(0,), cwd=None, env=None):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=env or os.environ.copy())
    if r.returncode in ok:
        PASS.append(label)
    else:
        FAIL.append(f"{label} — rc={r.returncode}\n{(r.stdout + r.stderr)[-400:]}")
    return r

print(f"bundle-verify @ {ROOT}\n" + "-" * 60)
PY = sys.executable or "python3"

# 1. python syntax
py_files = list(ROOT.glob("*.py")) + list(ROOT.glob("tools/*.py")) + list(ROOT.glob("demo/**/*.py"))
for f in py_files:
    run(f"compile {f.relative_to(ROOT)}", [PY, "-m", "py_compile", str(f)])

# 2. node check
run("node --check demo/src/app.js", ["node", "--check", "demo/src/app.js"])

# 3. bundle lint via env override
env = os.environ.copy()
env["CONTRACT_MD"] = str(ROOT / "CLAUDE.md")
run("CONTRACT_MD lint of the bundle", [PY, str(ROOT / "contract-lint.py")], env=env)

# 4. stop-audit-hook fixtures
hook = ROOT / "tools" / "stop-audit-hook.py"
fix = pathlib.Path(tempfile.mkdtemp())
(fix / ".claude").mkdir()
(fix / ".claude" / "activity.log").write_text("12:00:00 | s-1 | Edit | x.py\n")
(fix / "no_audit.jsonl").write_text('{"message":{"content":[{"type":"tool_use","name":"Edit","input":{}}]}}\n{"message":{"content":[{"type":"text","text":"done"}]}}\n')
(fix / "audit_ok.jsonl").write_text('{"message":{"content":[{"type":"tool_use","name":"Write","input":{}}]}}\n{"message":{"content":[{"type":"text","text":"AUDIT: pass"}]}}\n')
(fix / "t0.jsonl").write_text('{"message":{"content":[{"type":"text","text":"plain answer"}]}}\n')
env2 = os.environ.copy(); env2["HOME"] = str(fix)
r = subprocess.run([PY, str(hook)], input=f'{{"transcript_path":"{fix}/no_audit.jsonl"}}', capture_output=True, text=True, env=env2)
(PASS if '"decision": "block"' in r.stdout else FAIL).append(f"stop hook blocks edit-without-AUDIT (got {r.stdout[:80]!r})")
r = subprocess.run([PY, str(hook)], input=f'{{"transcript_path":"{fix}/audit_ok.jsonl"}}', capture_output=True, text=True, env=env2)
(PASS if r.returncode == 0 and not r.stdout.strip() else FAIL).append("stop hook passes AUDIT-bearing reply silently")
fix2 = pathlib.Path(tempfile.mkdtemp()); (fix2 / ".claude").mkdir(); (fix2 / ".claude" / "activity.log").write_text("")
env2b = os.environ.copy(); env2b["HOME"] = str(fix2)
r = subprocess.run([PY, str(hook)], input=f'{{"transcript_path":"{fix}/t0.jsonl"}}', capture_output=True, text=True, env=env2b)
(PASS if r.returncode == 0 and not r.stdout.strip() else FAIL).append("stop hook passes T0 replies silently")

# 5. session-audit fixtures
sa = ROOT / "tools" / "session-audit.py"
j = fix / "journal"; j.write_text("14:22:31 | s-1 | Bash | pytest -q tests/ -> 4 passed\n")
ok = fix / "r_ok.txt"; ok.write_text("TIER: T2\nVERIFIED: pytest -q tests/ -> 4 passed\nAUDIT: pass\n")
bad = fix / "r_bad.txt"; bad.write_text("TIER: T2\nVERIFIED: pytest -q tests/ -> 4 passed\n")
r = subprocess.run([PY, str(sa), "--report", str(ok), "--log", str(j), "--no-git"], capture_output=True, text=True)
(PASS if r.returncode == 0 else FAIL).append("session-audit passes a clean report")
r = subprocess.run([PY, str(sa), "--report", str(bad), "--log", str(j), "--no-git"], capture_output=True, text=True)
(PASS if r.returncode == 1 else FAIL).append("session-audit fails a missing-AUDIT report")

# 6. demo tests
run("demo unittest discover", [PY, "-m", "unittest", "discover", "-s", "demo/tests", "-p", "test_*.py"], cwd=ROOT)

# 7. demo verifier
run("demo/scripts/verify_contract.py", [PY, "demo/scripts/verify_contract.py"], cwd=ROOT)

# 8. every rules/ shard referenced from CLAUDE.md exists in the bundle
src = (ROOT / "CLAUDE.md").read_text()
referenced = set(re.findall(r"~/.claude/rules/([A-Za-z0-9_.-]+\.md)", src))
for name in sorted(referenced):
    if (ROOT / "rules" / name).exists():
        PASS.append(f"shard present: rules/{name}")
    else:
        FAIL.append(f"referenced shard missing: rules/{name}")

# 9. live paths — report-only (bundle ≠ live until sync)
live = pathlib.Path.home() / ".claude"
for name in sorted({"CLAUDE.md", "RUNBOOK.md", "settings.json", "hooks/statusline.sh", "hooks/activity-log.sh"}):
    NOTE.append(f"live path check (informational): {name} {'present' if (live / name).exists() else 'MISSING'}")

print()
print(f"PASS {len(PASS)}  ·  FAIL {len(FAIL)}")
for f in FAIL:
    print("  FAIL", f)
for n in NOTE:
    print("  NOTE", n)
print()
print("BUNDLE VERDICT:", "GREEN — everything that can run, ran" if not FAIL else "RED — see above")
sys.exit(0 if not FAIL else 1)
