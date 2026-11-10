Pairs with → human-output.md (the lanes produce human-made output), testing.md (L0–L2 per unit), recipes.md (§38.7 template), token-econ.md (T3/T4 budgets), manifest.md (what exists).

# PART 8 — SUBAGENT SWARM (T3/T4)

## §16 Subagent swarm

### §16.1 Fan-out shape

```
                      MAIN THREAD  (plan · own the contracts · merge · every commit)
                                         │
              ┌──────────┬───────────┬───┴────┬───────────┬──────────┐
              ▼          ▼           ▼        ▼           ▼          ▼
          A1 map+     A2 data     A3 api   A4 ui      A5 tests   A6 docs
          schema      layer       routes    views      + fixtures  + a11y
              │          │           │        │           │          │
              └──────────┴───── returns ≤15 lines ────────┴──────────┘
                                         │
                             ┌───────────▼───────────┐
                             │  CROSS-VERIFY (blind)  │  V1 fable-5-1: ran the command
                             │  V2 fable-5-1: contract│  V3 main : L3 integration
                             └───────────┬───────────┘
                                         │ fail → one re-dispatch with quoted evidence
                                         ▼
                                         merge → green → commit
```

Rules: T3 ≥4 units, T4 ≥10 units, all independent units dispatched in **one parallel batch**, never serially. At the top level no agent spawns an agent — **lane agents may spawn leaf subagents** (depth cap: lane → leaf, §16.7). Background agents are for independent units only — never predict their results, never act on partial output; merge only from the returned block.

### §16.2 Brief template (≤15 lines, sent verbatim)

```
UNIT:        A3 (step S3)
GOAL:        <one sentence>
OWN:         <paths you may write — exhaustive>
DO NOT TOUCH: <lockfiles, schema, other units' paths, package managers>
READ:        <paths to imitate, docs to follow — ranges welcome>
CONSTRAINTS: no new deps · no schema · match existing error style · strict types
ACCEPT:      <command> → <expected>
RETURN:      verdict, files, evidence, deviations, risks, needs — ≤15 lines
FORBIDDEN:   commits · pushes · network installs · edits outside OWN · spawning agents
```

**Pillar enforcement in swarms:** `OWN` and `DO NOT TOUCH` enforce §1.3 surgical boundaries. `CONSTRAINTS` enforces §1.2 simplicity first (no speculative abstractions for single-use code). `ACCEPT:` enforces §1.4 goal-driven execution.

### §16.3 Return template (demand verbatim)

```
VERDICT:   DONE | PARTIAL | BLOCKED | CONTRACT-VIOLATION
TOUCHED:   path:line ranges ONLY
EVIDENCE:  <command> → <≤3 lines of result>
DEVIATED:  none | <what + why>
RISKS:     none | <one line each>
NEEDS:     none | <lockfile/schema/router request for the designated writer>
```

A report containing pasted source is a `CONTRACT-VIOLATION`: reject, quote the required format, re-request once.

### §16.4 Unit kinds (verified subagents on this machine)

| Kind | Use | model |
|---|---|---|
| `Explore` | location, dependency mapping, read-only sweeps | `fable-5-1` |
| `Plan` | implementation plan, critical files, trade-offs | `fable-5-2`/`fable-5-1` |
| `general-purpose` | bounded build units, multi-step fixes with tools | `fable-5-1` |
| `voltagent-qa-sec:test-automator` | build/extend a suite | `fable-5-1` |
| `voltagent-qa-sec:code-reviewer` | review a diff | `fable-5-1` |
| `voltagent-qa-sec:security-auditor` / `:penetration-tester` | security passes | `fable-5-2` |
| `voltagent-qa-sec:performance-engineer` | perf regressions | `fable-5-1` |
| `voltagent-qa-sec:accessibility-tester` / `:ui-ux-tester` | a11y / UI conformance | `fable-5-1` |
| `voltagent-qa-sec:debugger` / `:error-detective` | stuck root-cause | `fable-5-2` |
| `ruflo-swarm:architect` / `:coordinator` | bigger fan-out orchestration | contract still binds |

### §16.5 Workflow skills to follow, not reinvent

`superpowers:subagent-driven-development` and `superpowers:dispatching-parallel-agents` define the mechanics; §16 overrides anything looser. Ordering: `brainstorming` → `writing-plans` → `executing-plans` → `test-driven-development` (when behavior is new) → `verification-before-completion` → `requesting-code-review` → `receiving-code-review` → `finishing-a-development-branch`. `using-git-worktrees` when parallel units could collide.

### §16.6 Blast radius — before any change to a shared symbol

```
1. graphify query "what depends on <symbol>" --budget 1500   (or grep for importers)
2. list: callers, subclasses, serialized consumers, tests, docs
3. write the count into the step's `risk:` line
4. if count > ~15 or a consumer is a data format → raise tier or ask
```

### §16.7 The 3-Lane Trinity — T3+ builds split three ways, verified three ways

For any T3+ **build** (feature, UI surface, or multi-file change), split the work into **three parallel lanes by default**. T2 collapses to a single thread by default; it may split only when the work is genuinely separable, and only in one explicit line — never silently. T0/T1 skip entirely.

```
                 MAIN THREAD (plan · own the contracts · merge · every commit · L3)
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
   A-UI   (design)             A-CODE  (build)             A-CONNECT (wire)
   DESIGN.md tokens            schema → routes → logic     router/DI/registry
   components FROM tokens      tests, edge matrix          config, env, glue
   a11y + 3-width screenshots  against contract            integration + e2e
        │                           │                           │
        └─────────── returns §16.3, ≤15 lines each ──────────────┘
                                    ▼
        CROSS-VERIFY (blind, §19): each lane's output reviewed by an agent
        that wrote none of it (A-CODE reviews A-UI, A-CONNECT reviews A-CODE, A-UI reviews A-CONNECT)
                                    ▼
        merge (A-CODE → A-UI → A-CONNECT) → L3 green → commit → report (§34)
```

**Lane contracts — exhaustive write-lists**

| Lane | Owns (writes) | Must NOT touch | Delivers | `accept:` example |
|---|---|---|---|---|
| A-UI | `DESIGN.md` · `views/`/`components/` · styles | schema · routes · router/DI · lockfiles | tokens + views + 3-width screenshots + console clean | `npm run build` → exit 0 · screenshots 375/768/1440 |
| A-CODE | `schema` · `routes` · `logic` · `tests/` | `DESIGN.md` · views · router/DI · lockfiles | working code + failing→passing test log | `npm test` → all pass |
| A-CONNECT | router/DI registry · config · env schema · `e2e/` glue — **A-CONNECT is the designated writer for router/DI (§8); A-UI/A-CODE file `NEEDS:` lines to it, applied in one batch** | components · unit tests · lockfiles | wired app + e2e green + `/health` ok | `curl -sf localhost:3000/health` → `{"status":"ok"}` |

**Cross-verify — mandatory and blind**
1. Every lane's diff goes to a reviewer that wrote none of it (the swap map above).
2. Reviewers get exactly: the diff + the lane's `ACCEPT:` line + its `OWN`/`DO NOT TOUCH` list (§19 rule). Nothing else.
3. Reviewer returns `VERDICT: DONE | REVISE` + evidence ≤15 lines. One REVISE round per lane maximum (§20), then escalate (§31).
4. Main thread runs L3 — whole build + full test suite + the real user-facing command (§27). The only "done" gate.

**Recursion — lanes may spawn leaves when their unit is large**
- A lane may dispatch **leaf subagents** when its unit splits into ≥3 independently verifiable pieces (e.g., A-CODE → data / api / tests leaves; A-UI → header / list / dialog leaves; A-CONNECT → router / e2e leaves), or needs an Explore sweep.
- **Depth cap: lane → leaf. Leaves never spawn.** No third level, ever.
- Leaves receive §16.2 briefs (`OWN:` exhaustive) and return §16.3 blocks; the lane collects, then returns its own ≤15 lines to main.
- One owner per path and the designated-writer rule (§8 / §23) stay absolute — leaves file `NEEDS:` lines up to the lane's writer.
- Lane dispatches go out in **one parallel batch**, never serially.

**Merge order (why this order)**
1. **A-CODE first** — it produces the schema/API contract the others consume; merges only after its own `accept:` passes.
2. **A-UI next** — consumes A-CODE's API shapes; merge after a green check.
3. **A-CONNECT last** — it wires both; its failures localize at the seam; merge after green.
4. Every 2–3 merges: one cheap gate (`typecheck` or fast test subset). Final: L3 (§27 seven lines) + real command + 3-width screenshots.

**When NOT to split three ways**
- T0/T1, backend-only work, refactor with no new surface, or a task where a lane would be empty — collapse the empty lane, say so in one line ("CONNECT lane collapsed — no router/DI change needed"), and proceed. Never fabricate a design lane for a bug fix.

**Models (set on the Agent call, never claimed in prose, §4)**
- A-UI → `fable-5-1` (design judgment) · A-CODE → `fable-5-1` (build) · A-CONNECT → `fable-5-1` (wiring) · L2 swap-reviewers → `fable-5-1` (mechanical & contract judgment) · one `fable-5-2` only if a lane fails twice (§18/§31).
- All three lanes default to `CLAUDE_CODE_SUBAGENT_MODEL` (fable-5-1) unless overridden per §16.4.

**PROGRESS.md blackboard** — the three `§16.3` returns + the two swap verdicts + the L3 result go in the ledger; the next session resumes from it cold (§38.1).

---

## §16.8 Git Worktree Isolation for T4 Swarms

For T4 swarms (≥10 parallel agents, large refactors, or concurrent game subsystem builds):
* **Why:** Hot reloaders (Vite/Webpack), intermediate broken syntax, and test runs collide when 10 agents touch one working directory.
* **Instant Dependency Sharing (Zero Extra Disk Space):**
  * Never run a slow, full `npm install` inside the new worktree.
  * Symlink the root `node_modules` into the worktree immediately:
    ```bash
    git worktree add -b feat/t4-swarm .worktrees/t4-swarm HEAD
    ln -s "$(git rev-parse --show-toplevel)/node_modules" .worktrees/t4-swarm/node_modules
    cd .worktrees/t4-swarm
    ```
* **TPM Rate-Limit Pacing:**
  * If usage warnings, token pressure, or HTTP 429 appear, throttle parallel dispatch to **batches of 3–4 agents** with a brief pause between batches instead of launching 10+ simultaneously.
  * Contract precedence: **this pacing rule is the only sanctioned exception to the one-parallel-batch rule.** Rate-limit pacing overrides §16.1's "one batch"; never anything else. Serial dispatch for independence of units is still forbidden.
* **Cleanup & Re-integration:**
  ```bash
  # Once L3 integration gate passes cleanly inside the worktree:
  cd ../..
  git merge --ff-only feat/t4-swarm || git merge feat/t4-swarm
  git worktree remove .worktrees/t4-swarm
  git branch -d feat/t4-swarm
  ```
* **Safety:** If aborted mid-run, safely force-clean: `git worktree remove --force .worktrees/t4-swarm`.


