Pairs with → recipes.md (how to use a capability), swarm.md (dispatch shape), master §44. Reference/audit only — do not load for building.

# PART 28 — 100-FEATURE MANIFEST (WHAT THIS SETUP GIVES YOU)

## §44 The 100-feature manifest — compact map

Every feature is real: wired in `settings.json`/hooks or defined as a rule in this file. Group order matches §0.3 and §42. Detail lives in the referenced section, not here.

| Range | Capabilities (where they live) |
|---|---|
| F001–F010 Visibility | statusline w/ dirty ★, ctx % + k-readout (amber ≥70 / red ≥85), cost·minutes, PostToolUse journal (wired 2026-11-08, 2MB rotation), MCP cap 8000, bash cap 4000, graph report after each `--update`, ended-task changed/verified/NOT report — §43, §33, §34 |
| F011–F020 Guardrails | 8 deny rules · 18 pre-approved verify commands · auto mode + deny floor · §1.1–§1.4 four core pillars · L0–L3 author-never-signs-off · 2-round cap · stash-first · hook-fix-never-skip · secrets scan before staging · explicit-confirm destructive ops — §43.4, §17, §19, §22, §24 |
| F021–F030 Token economy | 5-session 15/40/30/10/5% protocol · T0–T4 ladder with agents/brief/read caps · §1.2 simplicity discipline · ≤15-line briefs & returns · fable-5-1 subagents (fable-5-1 low / fable-5-2 high effort) · compact at step boundaries · `graphify --update` only · limit-approach protocol — §2, §9, §16, §30, §33 |
| F031–F040 Dispatch & swarm | Explore routing · one parallel batch · **3-Lane Trinity default for builds: UI + CODE + CONNECT lanes, swap-verified (§16.7)** · designated-writer exclusivity · PLAN block · `accept:` contracts (§1.4) · background agents never predicted · T4 worktree isolation — §5, §12, §13, §16, §23 |
| F041–F050 Verification & quality | L0–L3 ladder · blind L2/L3 cross-review · verify-then-report (§1.4) · UI golden path + edge matrix · type ≠ feature honesty · screenshots 3 widths · neighbor regression watch · graphify before guessing · smallest reproduce (§1.1, §31) — §17–§22, §25–§27, §31 |
| F051–F060 Git & shipping | step-commit at every verified boundary (§1.4) · surgical edits & orphan cleanup (§1.3) · `<area>: S<n> <outcome>` format · no amend · push/PR only on explicit request · named-file staging, never `git add -A` · stash before history ops · force-push & --no-verify hard-deny — §24, §28.3, §43.4 |
| F061–F070 Design excellence | direction → DESIGN.md tokens → type/color/layout/motion → a11y minimums → responsive 375/768/1440 → 3-width screenshot QA → design-debt gate; frontend-design · taste-skill · design-review suite · design-system capture — §25 |
| F071–F080 Memory & state | auto-memory scoping · verify-before-recommend · rsrs-cli 1.0.20 in ~/.npm-global (awaiting `rsrs register`) · graphify living map · THREE state layers (context/disk/memory) · PROGRESS.md handoff artifacts — §10, §33, §37 |
| F081–F090 AI playbook | evals before shipping · structured output + schema (§29) · codex:rescue (§31/§5) · ponytail PT badge (§43.1) · subagent-driven-development (§16.5) · voltagent-qa-sec ×9 + ruflo-swarm (§16.4) · deep-research (skills) — §5, §16, §29, §31, §43.1 |
| F091–F100 Ops & extensibility | one-file contract · §42 cold-start index → §0.3 · ~/.claude/RUNBOOK.md + contract-lint.py for machine state (backups, health check, self-verify) · recipes §38 · onboarding §39 · incident §40 · cross-repo §41 · verified-names rule — §37–§42 |

**Rule:** when any feature changes, edit its home section AND this range's one-line row in the same change. §37 machine facts stay in sync. No ghost features. Machine-state inventory (backups, health check) lives in `~/.claude/RUNBOOK.md`, not here.

**Footer:** This file is the operating contract. If it conflicts with a repo's `CLAUDE.md`, the repo file wins for that repo. If the user says something different in the session, the user wins. End each task with: what changed, what was verified, and what was not verified.
