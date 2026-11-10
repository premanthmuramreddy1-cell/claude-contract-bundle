# PROGRESS.md — Contract Comparison Demo Ledger

## PLAN (§12.1)
```
GOAL        Build a runnable side-by-side Release Gate & Edge-Case Sandbox Website comparing Unconstrained Agent output vs CLAUDE.md Contract-Driven output
TIER        T3 (7 files across UI, Engine, Tests, and Verification Harness)
BASELINE    local bundle /Users/premanthmuramreddy/Downloads/claude-contract-bundle/demo
MAP         grep (greenfield demo subdir inside connected bundle)
STEPS
  S1  Write DESIGN.md token specification & PROGRESS.md ledger        owner: A-UI      model: sonnet
      files:   demo/DESIGN.md, demo/PROGRESS.md
      accept:  test -f demo/DESIGN.md → exit 0
      deps:    none
      parallel: S2
      risk:    low — new directory
  S2  Build A-CODE comparison engine + TDD edge-matrix test suite     owner: A-CODE    model: sonnet
      files:   demo/src/engine.py, demo/tests/test_engine.py
      accept:  /usr/bin/python3 -m unittest discover -s demo/tests -p "test_*.py" -v → 10 passed, 0 failed
      deps:    none
      parallel: S1, S3
      risk:    unicode/CJK NFC normalization + tenant isolation edge cases
  S3  Build A-UI token stylesheet + side-by-side interactive website  owner: A-UI      model: sonnet
      files:   demo/src/tokens.css, demo/src/styles.css, demo/src/app.js, demo/index.html
      accept:  /usr/bin/python3 demo/scripts/verify_contract.py → 0 design-debt violations, all gates green
      deps:    S1
      parallel: S2
      risk:    ensuring zero raw hex/px in styles.css while isolating the "Bad AI Slop" preview
  S4  Wire A-CONNECT contract auditor & L3 verification gate          owner: A-CONNECT model: sonnet
      files:   demo/scripts/verify_contract.py
      accept:  /usr/bin/python3 demo/scripts/verify_contract.py → VERDICT: DONE
      deps:    S2, S3
      parallel: none
      risk:    parity between Python engine.py and browser app.js edge-matrix cases
RISKIEST    S2/S3 parity — disprove-by: /usr/bin/python3 demo/scripts/verify_contract.py
BUDGET      agents ≤ 3 (Trinity lanes) · rounds ≤ 2 · ceiling T3
CONTRACT    A-UI owns DESIGN.md/HTML/CSS/app.js | A-CODE owns src/engine.py + tests/ | A-CONNECT owns scripts/verify_contract.py
MERGE       order A-CODE (S2) → A-UI (S3) → A-CONNECT (S4)
DEFINITION OF DONE  10/10 unit+edge tests pass · 0 design-debt hex/px leaks in contract CSS · interactive HTML website verified
```

## UNIT RETURNS (§16.3)

```
UNIT:      A-CODE (S2)
VERDICT:   DONE
TOUCHED:   demo/src/engine.py:1-196 · demo/tests/test_engine.py:1-118
EVIDENCE:  /usr/bin/python3 -m unittest discover -s demo/tests -p "test_*.py" -v → Ran 10 tests in 0.001s · OK
DEVIATED:  Used /usr/bin/python3 unittest (Node not in default /bin/sh PATH)
RISKS:     none
NEEDS:     none
```

```
UNIT:      A-UI (S1, S3)
VERDICT:   DONE
TOUCHED:   demo/DESIGN.md:1-58 · demo/src/tokens.css:1-66 · demo/src/styles.css:1-278 · demo/src/app.js:1-462 · demo/index.html:1-226
EVIDENCE:  verify_contract.py Gate 1 & Gate 2 → PASS (0 raw hex, 0 raw px in styles.css; 1 <h1>, all landmarks & <label for> present)
DEVIATED:  none
RISKS:     Browser screenshot diff not run in headless shell — reported in NOT: line per §22
NEEDS:     none
```

```
UNIT:      A-CONNECT (S4)
VERDICT:   DONE
TOUCHED:   demo/scripts/verify_contract.py:1-125
EVIDENCE:  /usr/bin/python3 demo/scripts/verify_contract.py → VERDICT: DONE — All L1/L2/L3 contract gates green
DEVIATED:  none
RISKS:     none
NEEDS:     none
```
