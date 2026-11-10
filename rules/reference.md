Pairs with → human-output.md (all user-facing output), recipes.md (§38.6 migration), manifest.md (F-ranges), master §29/§39/§40/§41 stubs. Load on-demand only.

# §0.1/§0.2 + §29/§39/§40/§41 — reference mirror (load on demand)

> Migrated from CLAUDE.md v2026-11-08.20 to cut resident tokens (~1,000w). Referenced sections stay numbered identically; lint headings resolve from here too.

## §29 Building AI features into a product

Distinct from agents writing code: this is code you ship that calls a model.

```
RULE 1  one narrow job per call. never a generalist prompt doing auth + summarize + route
RULE 2  structured output with a schema; validate it; on invalid → one repair call, then fail loudly
RULE 3  cache + dedupe. identical inputs should cost once. cache keys include the model version
RULE 4  budget per call: cap max tokens, state it in code, test the truncation path
RULE 5  evals before shipping: a fixed set of inputs with expected properties, run in CI, not vibes
RULE 6  provider failures are normal: timeout, retry-with-backup ×1, then a real fallback path
RULE 7  never put secrets, PII, or credentials in prompts, logs, traces, or eval fixtures
RULE 8  prompt text lives in one module with a version, so an eval can be attributed to a change
RULE 9  state what is NOT verified: model output quality without an eval run is "not verified"
RULE 10 the UI must render a graceful failure for every model error you handle
```

```
eval gate template
  SET      <n> cases: happy · adversarial · empty · long · unicode · out-of-domain
  ASSERT   schema valid · contains/doesn't-contain · latency ≤ x · tokens ≤ y · refusal correct
  RUN      command → pass rate vs baseline (regression > threshold blocks shipping)
  BUDGET   cost per run stated; runs are opt-in outside CI, capped at 1 per change in CI
```

When you (the agent) are told to use a model tier: set it in parameters (`model=` on an Agent call, `--effort` for a session) — never claim it in prose.

## §39 Repo-specific onboarding template

Use this when starting work in a new repo that lacks its own `CLAUDE.md`.

```
# <repo-name> CLAUDE.md

## Mission
<one line: what this repo builds and for whom>

## Commands
build:     <command>
test:      <command>
lint:      <command>
format:    <command>
dev:       <command>

## Stack
language:    <e.g. TypeScript 5.x, Python 3.11, Go 1.22>
framework:   <e.g. Next.js, FastAPI, Gin>
test runner: <e.g. vitest, pytest>
CI:          <e.g. GitHub Actions .github/workflows/ci.yml>

## Conventions
- <convention 1>
- <convention 2>

## Gotchas
- <gotcha 1>
- <gotcha 2>

## Graph
graphify-out/ exists: yes|no
```

## §40 Incident response & on-call

```
SEV1 (production down, data loss, security breach)
  1. contain: stop the bleeding — revert, feature-flag off, drain traffic
  2. communicate: page on-call, write incident thread, state impact + ETA
  3. diagnose: reproduce in a safe copy, capture exact error + stack
  4. fix: minimal revert-or-patch, tested against the reproduction
  5. verify: run the failing path + adjacent tests
  6. commit: <area>: incident fix <symptom> — <root cause>
  7. postmortem: 5-why root cause, action items with owners + due dates

SEV2 (degraded, non-critical path)
  1. reproduce + capture evidence
  2. fix + test
  3. commit + monitor
  4. track in PROGRESS.md or incident backlog

Never: push to production without explicit request · rewrite history on main · deploy on a Friday without a rollback plan
```

## §41 Cross-repo standards

These apply to every repo you touch unless that repo's `CLAUDE.md` overrides them.

| Standard | Rule |
|---|---|
| Commit messages | `<area>: S<n> <outcome>` · imperative · ≤72 chars first line |
| Branch names | `<area>/<short-description>` |
| Stash messages | `pre-task <date>` · restore with `apply`, never `pop` |
| Screenshots | `.claude/screenshots/<step>-<w>.png` · never commit |
| PROGRESS.md | one per repo · ledger, not scratchpad |
| remember/claude-mem | one-line facts only · no secrets |
| graphify | `--update` after verified tasks · never commit graphify-out/ |
| Tests | code + test in the same commit |
| Secrets | never in code, logs, fixtures · env at startup only |
| AI features | structured output + schema · evals before shipping |
| Design | DESIGN.md tokens before components · no hard-coded hex/px |
| Game/Canvas | 16.6ms frame budget; full scene GPU disposal on unmount |
| Port hygiene | Pre-flight check & sweep (3000/5173/8080/WS); kill orphaned listeners |
| T4 Swarm isolation | Run in `.worktrees/<name>` until L3 integration pass is green |
| Verification | quote the command output · never claim "tests pass" without proof |

