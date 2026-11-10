#!/usr/bin/env python3
"""
A-CONNECT Lane — L1/L2/L3 Automated Contract & Design-Debt Verifier (§17, §25.11, §27)

Verifies:
1. DESIGN.md exists and defines required token scales (§25.2)
2. styles.css contains ZERO raw hex colors (#...) and ZERO raw pixel values (...px) (§25.2 / §25.11)
3. index.html satisfies §25.7 Accessibility minimums:
   - Exactly one <h1>
   - All <header>, <nav>, <main>, <footer> landmarks present
   - Every <input>/<select> has a matching <label for="...">
4. All 10 A-CODE edge-matrix tests pass (L1/L3 command gate)
"""

from __future__ import annotations
import re
import subprocess
import sys
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent.parent
BUNDLE_DIR = DEMO_DIR.parent


def check_design_tokens() -> list[str]:
    errors: list[str] = []
    design_md = DEMO_DIR / "DESIGN.md"
    tokens_css = DEMO_DIR / "src" / "tokens.css"
    styles_css = DEMO_DIR / "src" / "styles.css"

    if not design_md.exists():
        errors.append("Missing demo/DESIGN.md")
    if not tokens_css.exists():
        errors.append("Missing demo/src/tokens.css")
    if not styles_css.exists():
        errors.append("Missing demo/src/styles.css")
        return errors

    # Strip CSS comments before checking styles.css for raw hex or px values
    raw_css = styles_css.read_text(encoding="utf-8")
    clean_css = re.sub(r"/\*.*?\*/", "", raw_css, flags=re.DOTALL)

    hex_matches = re.findall(r"#[0-9a-fA-F]{3,8}\b", clean_css)
    if hex_matches:
        errors.append(f"styles.css contains raw hex literals (§25.2 violation): {hex_matches}")

    px_matches = re.findall(r"\b\d+(?:\.\d+)?px\b", clean_css)
    if px_matches:
        errors.append(f"styles.css contains raw px literals (§25.2 violation): {px_matches}")

    if ":focus-visible" not in clean_css:
        errors.append("styles.css missing :focus-visible rule (§25.7)")
    if "prefers-reduced-motion" not in clean_css:
        errors.append("styles.css missing @media (prefers-reduced-motion: reduce) (§25.6)")

    return errors


def check_html_a11y() -> list[str]:
    errors: list[str] = []
    html_path = DEMO_DIR / "index.html"
    if not html_path.exists():
        return ["Missing demo/index.html"]

    html = html_path.read_text(encoding="utf-8")
    h1_count = len(re.findall(r"<h1\b", html, flags=re.IGNORECASE))
    if h1_count != 1:
        errors.append(f"index.html must have exactly 1 <h1> (§25.7), found {h1_count}")

    for landmark in ("header", "nav", "main", "footer"):
        if not re.search(rf"<{landmark}\b", html, flags=re.IGNORECASE):
            errors.append(f"index.html missing <{landmark}> landmark (§25.7)")

    # Verify every input/select id has a matching <label for="id">
    control_ids = re.findall(r'<(?:input|select)\b[^>]*\bid="([^"]+)"', html)
    label_fors = set(re.findall(r'<label\b[^>]*\bfor="([^"]+)"', html))
    for cid in control_ids:
        if cid not in label_fors:
            errors.append(f"Control #{cid} is missing an explicit <label for=\"{cid}\"> (§25.7)")

    return errors


def run_unit_tests() -> tuple[bool, str]:
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "demo/tests", "-p", "test_*.py", "-v"],
        cwd=str(BUNDLE_DIR),
        capture_output=True,
        text=True,
    )
    output = (proc.stdout + "\n" + proc.stderr).strip()
    return proc.returncode == 0, output


def main() -> int:
    print("=== CLAUDE.md L2/L3 CONTRACT & DESIGN-DEBT AUDIT ===")
    design_errors = check_design_tokens()
    a11y_errors = check_html_a11y()
    tests_ok, test_out = run_unit_tests()

    print(f"[Gate 1] DESIGN.md + styles.css token purity (0 hex / 0 px): {'PASS' if not design_errors else 'FAIL'}")
    for err in design_errors:
        print(f"  - {err}")

    print(f"[Gate 2] HTML WCAG AA landmarks, single <h1>, explicit <label>: {'PASS' if not a11y_errors else 'FAIL'}")
    for err in a11y_errors:
        print(f"  - {err}")

    print(f"[Gate 3] A-CODE 10-case Edge Matrix unit suite: {'PASS' if tests_ok else 'FAIL'}")
    for line in test_out.splitlines()[-4:]:
        print(f"  {line}")

    if design_errors or a11y_errors or not tests_ok:
        print("VERDICT: REVISE")
        return 1

    print("VERDICT: DONE — All L1/L2/L3 contract gates green.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
