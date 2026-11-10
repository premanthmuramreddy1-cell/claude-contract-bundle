Pairs with → swarm.md (budget per task), recipes.md (trim recipes first), design.md (UI iteration cost), master §30, §36.

# PART 16 — TOKEN ECONOMICS (5-HOUR PROTOCOL)

## §30 Token economics: the 5-hour / 5-limit protocol

Your config: `autoCompact: true`, main model `fable-5-2`, subagent default `fable-5-1`, treat limits as a budget you spend, not a wall you discover — check your current usage before any T4 dispatch (`/usage` or the warning surface), never assume it.

```
┌── 5 sessions × 1 hour ─────────────────────────────────────────────────────┐
│ S1  orient + plan         │ ~15%  map read, PLAN block, contract matrix    │
│ S2  heavy build (batch A) │ ~40%  dispatch in ONE batch, cross-verify      │
│ S3  heavy build (batch B) │ ~30%  remaining units, merges, L1/L2           │
│ S4  verify + fix          │  ~10% L3 integration, UI screenshots           │
│ S5  finish + write-back   │  ~5%  commits, graphify --update, lessons      │
└─────────────────────────────────────────────────────────────────────────────┘
   if S2 overruns: consolidate into S3 and shrink S4 scope — never borrow from S5,
   because an unverified task costs more tomorrow than it saved today
```

### §30.1 Where tokens actually go

```
context growth per turn ─────────────────────────────  the silent multiplier
  system + tools          ░░░░░░░░░░░░ (fixed)
  CLAUDE.md (this file)   ████████████ (re-read with `wc -w ~/.claude/CLAUDE.md` — as of 2026-11-08.16: ~8,700 words · ~11k tokens, re-injected on each compaction)
  loaded skills           ████ per skill, permanent for the session
  file dumps              ██████ each one, until compacted
  subagent raw output     ██████ if >15 lines
  exploration loops       ██████████ the real villain — cap per §9
```

### §30.2 Compaction economics

```
autoCompact ON:  the transcript is summarized and CLAUDE.md is re-read from disk
                 every compaction costs ~this-file's size AGAIN
                 ► so keep the context small and compact ON PURPOSE, not by surprise
manual:  /compact <what to preserve>      ► compact at a step boundary, never mid-edit
         before compacting: write current PLAN + open step + uncommitted paths to
         PROGRESS.md, so the re-read after compaction is exact, not reconstructed
never:   let the harness compact you mid-step — you lose which accept: you were proving
```

### §30.3 The 12 commands that cut cost most

```
 1 answer T0/T1 with zero ceremony and zero tool calls
 2 read file ranges, never whole files (Read offset/limit)
 3 grep/glob before any agent dispatch
 4 ≤3 exploration agents before a plan exists (§9)
 5 dispatch in one parallel batch, never serially
 6 briefs ≤15 lines; shared header instead of 6× repeated constraints
 7 reports ≤15 lines; reject pasted source once, then hold the line
 8 fable-5-1 for mechanical tiers (now enforced: fable-5-1 effortLevel=low)
 9 never load a skill speculatively
10 filter long output (grep/tail/jq); headroom/context-mode for large files
11 graphify --update (not rebuild); --budget on queries
12 compact at step boundaries with the preserve-list written first
```

### §30.4 Tier budgets

| Tier | Agents | Brief cap | Report cap | New main reads | Rounds | Ceremony |
|---|---|---|---|---|---|---|
| T0 | 0 | — | — | 0–2 ranges | — | none |
| T1 | 0 | — | — | 1 range | — | 1 sentence |
| T2 | ≤1 | ≤10 lines | ≤15 | ≤5 files | 1 | steps + commits (T2 units get no retry loop; a failing unit re-plans, §18 round-2 rule is for T3/T4 units) |
| T3 | 4–6 | ≤15 | ≤15 | ≤6 files | 2 | PLAN + matrix |
| T4 | 10–16 | ≤15 | ≤15 | ≤8 files | 2 | PLAN + matrix + worktree |

### §30.5 Approaching a limit

```
detect:  usage warnings, 429, "weekly usage at N%", a paused capture notice
then:    1. commit the current verified step NOW (never hold uncommitted work across a wall)
         2. write PLAN + next-step + open questions to PROGRESS.md
         3. stop starting new units; finish the unit in flight or explicitly park it
         4. report state in §34 format so the next session resumes cold, correctly
never:   start a fresh 12-agent swarm at 90% budget · run a build with no accept: to "see"
         what happens · use --force/--no-verify to push past a failing hook
```

