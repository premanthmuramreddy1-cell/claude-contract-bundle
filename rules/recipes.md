Pairs with → swarm.md (dispatch templates), testing.md (verify recipes), design.md (UI builds), token-econ.md (when to spend), manifest.md (full capability map).

# PART 22 — COPY-PASTE RECIPES

## §38 Copy-paste recipes (proven shapes, fill the angle brackets)

### §38.1 Resume a compacted or abandoned session cold

```
1. read PROGRESS.md          → PLAN block, unit table, open questions
2. git log --oneline -8      → which steps are already paid for
3. git status --porcelain    → is there half-finished work? whose is it?
4. graphify query "what depends on <the next file I will touch>" --budget 1500
5. run the fast gate once    → is the baseline actually green?
6. re-emit TIER/REASON/DELEGATION (§2) and continue at the first unfinished step
never: restart the plan from scratch, or trust memory of the previous session's state
```

### §38.2 One-file bug fix (T1) — the whole procedure

```
reproduce:   <exact command or click path> → quote the error (§1.4 goal-driven execution)
locate:      grep the symbol; read ±40 lines around it (§1.1 think before coding)
hypothesise: one sentence, testable (surface assumptions, don't guess)
prove it:    the smallest check — a log line, an assertion, a 5-line script
fix:         minimal edit inside the same function boundary (§1.2 simplicity + §1.3 surgical changes)
orphans:     remove imports/variables made unused by the fix (§1.3 clean own mess)
regress:     write the test that fails without your fix, watch it fail, then pass (§1.4)
commit:      <area>: bugfix <symptom> — <root cause>
budget:    0 agents · ≤3 file reads · report in 4 lines
```

### §38.3 T3 feature with a 5-agent batch

```
PLAN:    §12 block; 6 steps; RISKIEST named; disprove-by run first
CONTRACT: A1 schema+migration | A2 data layer | A3 api | A4 ui | A5 tests+a11y
BRIEF:   §16.2 ×5, sent in ONE parallel message, model per §16.4
RETURN:  §16.3 ×5 → appended to PROGRESS.md (the blackboard)
VERIFY:  L1 fable-5-1 ran-it check ×5 → L2 fable-5-1 blind contract review ×5
NEEDS:   collect all lockfile/schema requests → one designated-writer batch
MERGE:   S1→S5, commit each, cheap gate every 2 merges
GATE:    §27 all seven lines green
END:     /graphify . --update (background) · lessons · §34 report
```

### §38.4 UI build with design proof

```
direction: one line from §25.1, chosen, not polled
DESIGN.md: §25.2 tokens written BEFORE the first component
build:     components reference tokens only; no raw hex, no raw px outside the scale
matrix:    §25.7 a11y minimums + §25.8 three widths
proof:     §25.9 screenshots at 375/768/1440 + console clean
audit:     design-review:design-debt-review → 0 hard-coded values, or list the debts
report:    VERIFIED line names the command; NOT line names anything you could not run
```

### §38.5 Repo-wide audit (T4, parallelizable by construction)

```
1. map: graphify query "list modules with most incoming deps" --budget 2000
2. shard: one unit per module/route group — 10+ units, each with its own accept:
     example: "every route handler in /api/accounts has an authz check" → grep+assert count
3. dispatch: one batch, fable-5-1 for enumeration, fable-5-1 for judgement, fable-5-2 for findings
4. verify: L2 blind reviewer re-checks 20% of PASS verdicts (audits lie quietly)
5. output: one table (severity · path:line · exploit/failure scenario · fix cost · owner)
6. do NOT fix anything in the audit pass — findings first, remediation as its own tier
```

### §38.6 Migration or schema change

```
read: model/schema file, row counts, foreign keys, index list
plan: forward + backward or an explicit "no rollback, here is the restore" line
test: nullability · uniqueness · default values · index rebuild · 10× row estimate
gate: run against a copy first; EXPLAIN the changed queries before and after
commit: <area>: S<n> migration <name> — reversible: yes|no
never: bundle a schema change with a behavior change in one step; one `accept:` each
```

### §38.7 The 3-Lane Trinity dispatch (T3+ builds, the default shape)

```
PLAN:    §12 block; 6 steps; 3 lanes (A-UI · A-CODE · A-CONNECT); RISKIEST named (usually A-CONNECT seam or A-CODE migration); disprove-by run first
CONTRACT: A-UI (DESIGN.md → tokens → views, 3-width proof) | A-CODE (schema → routes → logic → tests) | A-CONNECT (router → DI → config → e2e)
BRIEF:   §16.2 ×3, sent in ONE parallel message, model=fable-5-1 each; swap-verify map declared (CODE reviews UI, CONNECT reviews CODE, UI reviews CONNECT); each lane's OWN list exhaustive
RETURN:  §16.3 ×3 → appended to PROGRESS.md (the blackboard)
VERIFY:  L1 fable-5-1 ran-it ×3 → L2 fable-5-1 swap-review ×3 (§16.7) → one REVISE round max per lane
NEEDS:   all lockfile/schema/router requests → designated writer in ONE batch (§8)
MERGE:   A-CODE → A-UI → A-CONNECT, each its own commit + green check (§16.7)
GATE:    §27 seven lines green · real user command · screenshots at 375/768/1440
END:     /graphify . --update (background) · lessons · §34 report
RECURSION: a lane with ≥3 independent pieces dispatches leaves (one parallel batch, depth cap 1, leaves never spawn)
```

### §38.8 Real-Time Game & Interactive Canvas Feature (WebGL + Sockets)

```
PRE-FLIGHT: port sweep: `lsof -ti :3000,5173,8080 | xargs kill -15 2>/dev/null || true`
SHARDS:     cat ~/.claude/rules/game-web.md · cat ~/.claude/rules/design.md
PLAN:       §12 block; 4 steps:
  S1 Canvas/Scene Lifecycle   (A-UI): setup scene, camera, renderer, resize, RAF loop, .dispose() on unmount
  S2 Delta Sync & Protocol    (A-CODE): socket event schemas, message sequencer, ping-pong heartbeat, room state
  S3 Interactive Loop / Input (A-CODE/UI): input buffer, fixed physics step (16.6ms), prediction & interpolation
  S4 End-to-end Wiring        (A-CONNECT): wire server room to client canvas, handle reconnect + graceful drop
GATE:       npx tsc --noEmit · test suite green · canvas memory disposal verified · frame render <16.6ms · socket reconnect tested
```

### §38.9 T4 Worktree Swarm Dispatch

```
SETUP:   git worktree add -b feat/t4-swarm .worktrees/t4-swarm HEAD
         ln -s "$(git rev-parse --show-toplevel)/node_modules" .worktrees/t4-swarm/node_modules
         cd .worktrees/t4-swarm
PLAN:    T4 master plan; ≥10 units; designated writers named for schema/lockfiles/router
BATCH:   dispatch units in parallel (pace in batches of 3–4 if TPM rate pressure exists)
VERIFY:  blind cross-verify per unit; sequential merge order; L3 integration pass inside worktree
CLEANUP: cd ../.. && (git merge --ff-only feat/t4-swarm || git merge feat/t4-swarm)
         git worktree remove .worktrees/t4-swarm && git branch -d feat/t4-swarm
REPORT:  §34 report with SHA and verification evidence
```


