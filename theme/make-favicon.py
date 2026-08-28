#!/usr/bin/env python3
"""Wrap a mark from theme/assets/marks-16/ in the DCEasy favicon tile.

A favicon gets no inherited color from the page and needs more weight than a
24px header mark, so each one is baked: sky tile, navy glyph.

It builds from the 16px drawings, not the full-detail ones. Those are separate
drawings rather than scale-downs — fewer grid lines, fewer pins, larger dots —
because detail that reads at 48px turns to mush at 16. That is also why this no
longer fudges low opacities upward: the small drawings already dropped whatever
would not have survived.

    python3 theme/make-favicon.py rocketship dceprep
    python3 theme/make-favicon.py --all
"""
import re, sys, pathlib

TILE_BG, GLYPH = "#63C0F5", "#0D1F3C"
GLYPH_SCALE = 0.78
ROOT = pathlib.Path(__file__).resolve().parent
SRC, OUT = ROOT / "assets" / "marks-16", ROOT / "assets" / "favicons"

TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"
     role="img" aria-label="{name}">
  <rect width="24" height="24" rx="5" fill="{bg}"/>
  <g transform="translate(12,12) scale({scale}) translate(-12,-12)">
{body}
  </g>
</svg>
'''


def build(name: str) -> pathlib.Path:
    src = SRC / f"{name}.svg"
    raw = src.read_text()
    body = re.search(r"<svg[^>]*>(.*)</svg>", raw, re.S).group(1).strip("\n")
    label = re.search(r'aria-label="([^"]+)"', raw).group(1)
    body = body.replace('stroke="currentColor"', f'stroke="{GLYPH}"')
    body = body.replace('fill="currentColor"', f'fill="{GLYPH}"')
    # The glyph is scaled down inside the tile, which would thin every stroke
    # with it. Pre-divide so the design's 2 / 1.5 weights land as drawn.
    body = re.sub(
        r'stroke-width="([\d.]+)"',
        lambda m: f'stroke-width="{round(float(m.group(1)) / GLYPH_SCALE, 2)}"',
        body,
    )
    OUT.mkdir(exist_ok=True)
    dest = OUT / f"{name}.svg"
    dest.write_text(TEMPLATE.format(name=label, bg=TILE_BG, scale=GLYPH_SCALE, body=body))
    return dest


if __name__ == "__main__":
    names = [p.stem for p in sorted(SRC.glob("*.svg"))] if "--all" in sys.argv else sys.argv[1:]
    for n in names:
        print("wrote", build(n).relative_to(ROOT.parent))
