# Bundle verification map — everything linked, everything proven

`v2026-11-08.20 · bundle = source of truth; `~/.claude/CLAUDE.md` is a backup-synced copy`

## How to verify everything in one command

```bash
cd <bundle> && python3 tools/bundle-verify.py   # → BUNDLE VERDICT: GREEN (26/26 checks)
```
Read-only; exits 1 on any failure; covers syntax, lint, enforcement fixtures, and the demo.

## The whole bundle, one table

| File | Role | Verified by | Links to |
|---|---|---|---|
| `CLAUDE.md` | master contract, 8,799-word resident | `CONTRACT_MD=./CLAUDE.md contract-lint.py` → PASS (109 headings, 29 parts, F 100/100) | every shard; §0.6; §43.7 |
| `contract-lint.py` | structure audit (counts as WARN for machine rot) | py_compile + runs in bundle-verify | CLAUDE.md, rules/*.md |
| `rules/swarm.md` | T3/T4 dispatch, Trinity (T3+ default) | heading scan (resolves §16.*) | human-output, testing, recipes, token-econ, manifest |
| `rules/testing.md` | pyramid, TDD, edge matrix | heading scan | swarm, recipes, human-output, master §26 |
| `rules/design.md` | tokens, a11y, 3-widths law | heading scan | human-output, reference, game-web, recipes, master §25 |
| `rules/human-output.md` | ship-human doctrine (2,144w) | §27 line 4 now demands taste-inspect or `NOT:` for user-facing output | design, swarm, testing, reference, master §0.5/§27/§34 |
| `rules/token-econ.md` | budgets, 5-session heuristic (labeled heuristic) | token figure synced (~11k) | swarm, recipes, design, master §30 |
| `rules/recipes.md` | §38 copy-paste templates (Trinity now T3+) | Trinity alignment with §1 rule 13 | swarm, testing, design, token-econ, manifest |
| `rules/manifest.md` | F001–F100 capability map | F-range coverage enforced by lint | recipes, swarm, master §44 |
| `rules/reference.md` | §29/§39/§40/§41, migrated to shrink resident | shard heading resolution | human-output, recipes, manifest, master stubs |
| `rules/game-web.md` | WebGL/canvas/socket laws | shard resolution | design, swarm, human-output, master §25G |
| `tools/session-audit.py` | report↔journal verifier | 3 fixtures (pass/fail paths) in bundle-verify | master §43.6/§43.7 |
| `tools/stop-audit-hook.py` | Stop hook; blocks edit-without-AUDIT | 3 synthetic transcripts in bundle-verify | master §43.7; needs live approval |
| `tools/weekly-audit.py` | external-eye weekly sweep → audits/AUDIT-*.md | ran on this machine: red=0 hollow=0 | master §43.7; `claude.weekly-audit.plist` |
| `tools/weekly-review-brief.md` | reviewer prompt for a fresh pair of eyes | human-run; never the author | weekly-audit output |
| `tools/claude.weekly-audit.plist` | launchd schedule (Mon 09:00) | static; install needs approval | weekly-audit |
| `tools/bundle-verify.py` | one command, whole bundle | runs itself in its own check suite | everything above |
| `audits/AUDIT-*.md` | real weekly-audit artifacts | generated, readable, latest is CLEAN | weekly-audit |
| `demo/` | reference implementation (Unconstrained vs Contract) | 10/10 tests + verify_contract.py DONE | README/verify harness |
| `backups/` (live `~/.claude/`) | rollback copies | naming `bak-<date>-pre<ver>` | restore any version |

## Live-install checklist (needs your explicit yes)

1. `cp CLAUDE.md ~/.claude/CLAUDE.md.bak-2026-11-08-pre817 && cp CLAUDE.md ~/.claude/CLAUDE.md`
2. `cp rules/*.md ~/.claude/rules/ && cp contract-lint.py ~/.claude/bin/contract-lint.py`
3. `cp tools/session-audit.py tools/weekly-audit.py ~/.claude/bin/ && cp tools/stop-audit-hook.py ~/.claude/hooks/stop-audit.py`
4. Append Stop hook to `~/.claude/settings.json` `hooks.Stop` (backup first) — §43.7 snippet
5. `launchctl load ~/Library/LaunchAgents/claude.weekly-audit.plist` (after `cp tools/claude.weekly-audit.plist ~/Library/LaunchAgents/`)
6. `mkdir -p ~/.claude/audits && launchctl start com.claude.contract-weekly-audit` → confirm a new audit file appears

## Honest limits — where 100/100 is off the table, by design

- 9 of 10 rules of this contract are honor-system at execution time; §43.7 converts exactly one — edits without AUDIT — into mechanical friction. No text file makes an agent honest; make dishonesty expensive, not imagination illegal.
- "Godly-good" output quality is taste, unmeasurable by any regex; §27 line 4 narrows it to quoted taste-inspect output only for user-facing work.
- Enforcement runs on *your* machine, *your* Claude Code, *your* settings — the moment the harness changes, every machine-fact claim here expires (§37 says as much).
- Scores vs. 100 are a judgment, not a benchmark.
