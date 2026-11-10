Pairs with → human-output.md (ship-human laws), reference.md (AI screens), game-web.md (canvas/webgl), recipes.md (§38.4), master §25.

# PART 12 — DESIGN EXCELLENCE

## §25 Direction, tokens, build, review

### §25.1 Decision tree

```
is there an approved design/Figma? ──yes──► align to it (design-review, ui-alignment-review)
        │no
        ▼
new surface or reshaping? ── reshape ──► keep the contract, change one axis at a time
        │new
        ▼
pick ONE direction from: era | medium | typographic | palette | density | motif
        ▼
write DESIGN.md tokens BEFORE building ──► build ──► screenshot at 3 widths ──► audit
```

Direction options (name it in one line, then commit to it): *editorial serif + oversized display · brutalist grid + hard edges · terminal/monospace + single accent · print-poster + flat ink · soft-lux + generous whitespace · dense dashboard + hairline rules · toy/rounded + saturated · industrial + numbered*.

**Pillar discipline in design:** State aesthetic assumptions upfront (§1.1). Choose one committed direction and build only the components requested; eliminate gratuitous AI-decoration and speculative components (§1.2 simplicity first). Verify layout across 3 widths with executable proof (§1.4 goal-driven execution).

### §25.2 Design token contract

```
DESIGN.md (repo root)     — machine-readable + human-readable source of truth
  frontmatter: colors, fonts, radii, spacing, shadow/elevation scales
  body:        type ramp, grid, component rules, Do/Don't, motion, a11y notes
```

```
scale    name        value      role
display  --t-4xl     clamp(2.5rem, 6vw+1rem, 4.5rem)   page statement, max 2/page
h1       --t-3xl     2rem        section
body     --t-base    1rem/1.6    prose
meta     --t-sm      .875rem     labels, captions
space    --s-1..--s-8  4,8,12,16,24,32,48,64           one scale, no magic px
radius   --r-sm/md/full  .25rem/.5rem/9999px           pick 2 and stop
```

- Never a hard-coded hex or a raw `px` in a component when a token exists. `design-review:design-debt-review` finds them; `design-system-capture` extracts them from an existing UI, Figma variables, Tailwind config or CSS custom properties.
- Two scales maximum (type + space). A third usually means nobody owns the design.

### §25.3 Typography

```
one display face + one text face (two is the budget, three is noise)
≥16px body · line-height 1.5–1.75 for prose · measure 45–75ch
weights: 400 and 600/700 only unless the direction demands more
tabular numbers for data · optical sizing off for tiny labels · no justified prose
contrast of body text vs its background ≥ 4.5:1 (large text ≥ 3:1)
```

### §25.4 Color

- Build from one hue relationship (analogous, complementary, or single-hue + neutral ramp). State it in `DESIGN.md` in one line.
- Roles, not hexes: `surface · raised · text · text-muted · accent · success · warn · danger`. Semantic names survive a re-skin; `blue-500` does not.
- Dark mode = a second token map, not an inversion filter.
- Never convey meaning by color alone (a11y): pair with an icon or text.

### §25.5 Layout

```
grid: 12-col desktop · 8-col tablet · 4-col phone · gutter from the space scale
container queries over viewport media queries for components
fluid type/space with clamp(); no fixed 1440 assumptions
one primary job per screen; everything else is secondary or hidden
```

Use `design-review:responsive-design` for container-query/fluid/mobile-first implementation.

### §25.6 Motion

```
120–250ms · ease-out for entrances, ease-in for exits · transform/opacity only
nothing that moves for decoration alone
@media (prefers-reduced-motion: reduce) → disable all non-essential motion
skeletons/spinners only where latency is real
```

### §25.7 Accessibility minimums (per UI task)

```
☐ one h1, no skipped heading levels        ☐ every control keyboard reachable, in DOM order
☐ visible :focus-visible ≥ 3:1 contrast    ☐ inputs have real <label> (not placeholder)
☐ images: alt or alt=""                    ☐ touch targets ≥ 44×44
☐ color-not-alone                         ☐ landmarks: header/main/nav/footer
☐ forms: error text associated via aria-describedby, announced
```

`design-review:accessibility-review` (axe/Playwright + heuristics) and `voltagent-qa-sec:accessibility-tester` run these. Report WCAG AA pass/fail per item, with the file:line.

### §25.8 Responsive matrix — verify all of these, not one

| Width | Check |
|---|---|
| 375×667 | no horizontal scroll · tap targets · nav collapsed · type not truncated |
| 768×1024 | grid reflow · sidebar behavior · images not stretched |
| 1440×900 | max content width · whitespace intent · nothing orphaned |

RTL + a long-word/locale stress string on the same three.

### §25.9 Visual QA procedure

```
1. run the app (dev server), open the real route — never judge from code
2. screenshot 3 widths → .claude/screenshots/<step>-<w>.png
3. compare against DESIGN.md tokens + any approved frame (visual-regression-review)
4. read the console for errors/warnings
5. diff the screenshot against the baseline at a stated threshold; explain each
   meaningful change rather than trusting the pixel number
6. fix → repeat; do not "accept" drift silently
If you cannot run a browser here, say so in the NOT: line — do not claim visual parity.
```

### §25.10 Anti-patterns (these are what "AI slop" means)

```
✗ three-equal-cards feature row      ✗ gradient headline + glass everything
✗ purple/pink default palette        ✗ emoji as icons
✗ centered hero with 2 CTAs + "Get started"   ✗ Inter/system-ui everywhere, no direction
✗ rounded-2xl on everything          ✗ 6 type sizes with no scale
✗ lorem-ipsum shipped as copy        ✗ hover states that only change color
✗ a dashboard with 12 cards and no hierarchy
```

### §25.11 Design gate before any UI is called done

```
☐ direction named in one line and followed
☐ DESIGN.md tokens exist and components reference them
☐ 3 widths verified by screenshot (or explicitly not verifiable → say so)
☐ a11y minimums §25.7 checked
☐ no anti-pattern from §25.10 that you cannot justify
☐ design-review:design-debt-review clean, or debts listed as known
```

Tools: `frontend-design`, `taste-skill` (+ `high-end-visual-design`, `redesign-existing-projects`, `stitch-design-taste`), `ui-ux-pro-max`, `impeccable`, `design-review:*` (10 skills incl. `ui-designer`, `design-qa`, `component-library-alignment`, `design-md-review`, `visual-regression-review`), `imagegen` for raster assets.

