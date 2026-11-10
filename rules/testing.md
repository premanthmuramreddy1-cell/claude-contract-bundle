Pairs with → swarm.md (unit returns carry evidence), recipes.md (§38.2/§38.3), human-output.md (tests are prose the machine reads), master §26.

# PART 13 — TESTING

## §26 Testing

### §26.1 Pyramid and cost

```
            ▲  E2E (few, slow, expensive)          ≤5%  real flows, 1–3 per feature
           ███  Integration (moderate)             ~20% boundaries, DB, APIs
        ████████  Unit (many, fast, cheap)         ~75% pure logic, parsers, rules
```

Dispatch: unit-test authoring → `fable-5-1`; boundary and flake triage → `fable-5-1`; concurrency/property tests → `fable-5-2`. `superpowers:test-driven-development` when behavior is new.

### §26.2 TDD order

```
RED    write the failing test   → run it → SEE the failure message you expect (§1.4 goal-driven execution)
GREEN  smallest change that passes → rerun (§1.2 simplicity first — no speculative code)
REFACTOR with green tests → name the extraction, run tests again (§1.3 surgical changes — no collateral churn)
COMMIT code + test together (§24.2, §1.4)
```

A test you never watched fail is not proof. If you cannot articulate the failure you expected, the test is asserting nothing.

### §26.3 What deserves a test

| Change | Test |
|---|---|
| new pure logic, parsing, calculation | unit, always |
| bug fix | regression test reproducing the exact report, before the fix |
| API/route handler | contract test incl. error status + validation |
| DB migration | forward + rollback or documented rollback plan + data check |
| UI interaction | component test for behavior, screenshot check for layout |
| auth/authz | deny-path test (not just the happy login) |
| config change | one test asserting the effective behavior, or state it is untested |

**Simplicity discipline (§1.2):** Write tests for requested behaviors and realistic boundary edges (§26.6). Never construct speculative test suites for impossible scenarios.

### §26.4 Test style

```
name: <unit> <behavior> <condition>          # "notes writer rejects empty title"
AAA: arrange / act / assert — one act, real assertions (no expect(true))
no sleeps — wait on the condition; no network in unit tests; factories over fixtures sprawl
each test fails for exactly one reason; no assertion soup
never weaken or delete an assertion to get green — fix the code or prove the test wrong
```

### §26.5 Test-plan template

```
UNIT          <n> new · commands: npx vitest run <path>
INTEGRATION   <n> new · command: ...
E2E           <n> flows · tool/command + which route
EDGE MATRIX   empty · null · unicode · CJK · large input · concurrent · retry · offline · corrupt
PERF          <metric> budget: <number>
NOT TESTABLE  <what + why>
```

### §26.6 Edge matrix — apply to every new behavior

```
empty/zero · null/undefined · max-int/negative · unicode (combining marks, emoji, CJK, RTL)
whitespace-only · 10× expected size · duplicate/concurrent writes · partial failure mid-operation
retry after success · clock skew · dependency unavailable · malformed input · unauthorized + wrong-tenant
```

### §26.7 Flake handling

```
reproduce 3× consecutively ──► if intermittent: name the trigger (timing, ordering, shared state,
     network, randomness, time) before touching code
     seed/timeouts/shared globals are the usual suspects; a sleep added to "fix" it is not a fix
     cannot reproduce ──► record it, add the deterministic guard the symptom implies, do not delete the test
```

### §26.8 Gates (detect from the repo, never guess)

| Stack | Detect | Run |
|---|---|---|
| JS/TS | `package.json` | `npm/pnpm run build`, `npx tsc --noEmit`, `npm test`, `npm run lint`, `npm audit --omit=dev` |
| Python | `pyproject.toml` | `pytest -q`, `mypy` (if configured), `ruff`/`flake8`, `pip-audit` |
| Go | `go.mod` | `go vet ./...`, `go test ./...`, `golangci-lint run`, `govulncheck ./...` |
| Rust | `Cargo.toml` | `cargo build`, `cargo test`, `cargo clippy -- -D warnings`, `cargo audit` |
| Roblox/Luau | game place | `execute_luau`, `screen_capture`, `start_stop_play`, `get_console_output` |

