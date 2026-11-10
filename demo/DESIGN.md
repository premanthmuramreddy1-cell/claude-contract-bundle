# DESIGN.md — Contract Comparison Demo Design System
---
direction: "terminal/monospace + single accent · dense dashboard + hairline rules"
hue_relationship: "neutral slate ramp + single amber-gold operational accent"
colors:
  surface: "#0d1117"
  raised: "#161b22"
  border: "#30363d"
  text: "#e6edf3"
  text-muted: "#8b949e"
  accent: "#f0883e"
  success: "#3fb950"
  warn: "#d29922"
  danger: "#f85149"
fonts:
  display: "'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace"
  body: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
radii:
  sm: "0.25rem"
  md: "0.5rem"
spacing:
  s-1: "0.25rem"
  s-2: "0.5rem"
  s-3: "0.75rem"
  s-4: "1rem"
  s-5: "1.5rem"
  s-6: "2rem"
  s-7: "3rem"
  s-8: "4rem"
---

## 1. Aesthetic Direction (§25.1)
**Direction:** `terminal/monospace + single accent · dense dashboard + hairline rules`
Built for engineering comparison: high-contrast operational surfaces, tabular metrics, hairline `1px` borders using `--c-border`, and zero decorative motion or gradients in the contract-compliant surface.

## 2. Token Scale (§25.2)
| Scale | Token | Value | Role |
|---|---|---|---|
| Display | `--t-4xl` | `clamp(1.75rem, 3vw + 0.75rem, 2.5rem)` | Page statement (max 1/page) |
| H1 / Section | `--t-2xl` | `1.35rem` | Primary lane heading |
| Body | `--t-base` | `1rem` (line-height `1.6`) | Prose and payload inspector (`45–75ch`) |
| Meta | `--t-sm` | `0.875rem` | Telemetry badges, captions, table cells |
| Space | `--s-1` .. `--s-8` | `4, 8, 12, 16, 24, 32, 48, 64px` | Layout & component spacing |
| Radius | `--r-sm`, `--r-md` | `0.25rem`, `0.5rem` | Two radii only |

## 3. Color Roles & Light/Dark Maps (§25.4)
- **Dark mode (default):** `--c-surface`, `--c-raised`, `--c-border`, `--c-text`, `--c-text-muted`, `--c-accent`, `--c-success`, `--c-warn`, `--c-danger`.
- **Light mode (`[data-theme="light"]`):** Dedicated second token map (never `filter: invert(1)`).
- **Color-not-alone:** Every verdict badge pairs semantic color with an explicit text prefix (`[PASS]`, `[WARN]`, `[FAIL]`, `[BLOCKED]`).

## 4. Accessibility & Responsive Matrix (§25.7–§25.8)
- Exactly one `<h1>`, no skipped heading levels (`h1 → h2 → h3`).
- Visible `:focus-visible` outline (`2px solid var(--c-accent)`, contrast ≥ 4.5:1).
- Every interactive control has `min-height: 44px; min-width: 44px` and explicit `<label for="...">`.
- Landmarks required: `<header>`, `<nav>`, `<main>`, `<footer>`.
- Responsive breakpoints verified at `375×667` (4-col stack), `768×1024` (8-col split), and `1440×900` (12-col side-by-side).
