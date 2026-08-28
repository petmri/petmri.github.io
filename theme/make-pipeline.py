#!/usr/bin/env python3
"""Generate the DCEasy pipeline diagram as a static SVG, one variant per tool.

Six stages in two rows, drawn directly as SVG rather than with Mermaid. See
theme/README.md for why Mermaid was dropped.

Every stroke and label uses currentColor, so the diagram inherits the page's
text color and reads in both the light and slate palettes. Only the highlight
is a fixed color; dceasy.css brightens it for slate.

    python3 theme/make-pipeline.py --all
"""

import argparse
import pathlib

ACCENT = "#16707f"

# (number, title, subtitle, tools) laid out left-to-right, top row then bottom.
NODES = [
    ("1 · Convert",    "DICOM → BIDS",     "dce2bids"),
    ("2 · Preprocess", "motion · bias",    "DCEPrep"),
    ("3 · AIF",        "input function",   "AutoAIF / AIFArtist"),
    ("4 · T1 map",     "VFA / IR",         "parametric_scripts"),
    ("5 · PK fit",     "Ktrans · ve · vp", "ROCKETSHIP + Gpufit"),
    ("6 · Analyze",    "compare · QC",     "ROCKETSHIP"),
]

# Which stages each tool is responsible for. 1-indexed to match the labels.
TOOLS = {
    "overview":           [],
    "dce2bids":           [1],
    "dceprep":            [2, 3, 4, 5, 6],
    "autoaif":            [3],
    "aifartist":          [3],
    "parametric_scripts": [4],
    "rocketship":         [5, 6],
    "gpufit":             [5],
}

LABELS = {
    "overview":           "DCEasy processing pipeline",
    "dce2bids":           "DCEasy processing pipeline, with step 1 highlighted as dce2bids' scope",
    "dceprep":            "DCEasy processing pipeline, with steps 2 to 6 highlighted as DCEPrep's scope",
    "autoaif":            "DCEasy processing pipeline, with step 3 highlighted as AutoAIF's scope",
    "aifartist":          "DCEasy processing pipeline, with step 3 highlighted as AIFArtist's scope",
    "parametric_scripts": "DCEasy processing pipeline, with step 4 highlighted as parametric_scripts' scope",
    "rocketship":         "DCEasy processing pipeline, with steps 5 and 6 highlighted as ROCKETSHIP's scope",
    "gpufit":             "DCEasy processing pipeline, with step 5 highlighted as Gpufit's scope",
}

# Column x for the rect, and the text inset within it.
COL_X = [10, 290, 570]
ROW_Y = [10, 176]


def node_svg(index, on):
    """One stage box. `index` is 0-based; `on` marks it as in scope."""
    title, subtitle, tools = NODES[index]
    x = COL_X[index % 3]
    y = ROW_Y[index // 3]
    tx = x + 20
    if on:
        # fill-opacity rather than an 8-digit hex: #RRGGBBAA is fine in
        # browsers but not in every SVG rasterizer, and these files are also
        # used outside the docs.
        box = (f'fill="{ACCENT}" fill-opacity=".12" stroke="{ACCENT}" '
               f'stroke-width="2.5" stroke-opacity="1"')
        tool = f'fill="{ACCENT}" opacity="1"'
        cls = ' class="dceasy-pipeline-on"'
    else:
        box = 'fill="none" stroke="currentColor" stroke-width="1" stroke-opacity=".35"'
        tool = 'fill="currentColor" opacity=".8"'
        cls = ""
    return f"""    <g{cls}>
      <rect x="{x}" y="{y}" width="240" height="96" rx="4" {box}/>
      <text x="{tx}" y="{y + 32}" fill="currentColor" font-size="17" font-weight="600">{title}</text>
      <text x="{tx}" y="{y + 54}" fill="currentColor" opacity=".62" font-size="13">{subtitle}</text>
      <text x="{tx}" y="{y + 76}" {tool} font-family="JetBrains Mono, monospace" font-size="12.5">{tools}</text>
    </g>"""


def build(tool):
    active = TOOLS[tool]
    nodes = "\n".join(node_svg(i, (i + 1) in active) for i in range(6))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 282"
     class="dceasy-pipeline" role="img" aria-label="{LABELS[tool]}"
     font-family="'IBM Plex Sans', Helvetica, sans-serif">
    <!-- connectors: 1→2→3, wrapping down and back to 4→5→6 -->
    <g stroke="currentColor" fill="none" opacity=".45" stroke-width="1.5">
      <path d="M254 58 H282"/>
      <path d="M534 58 H562"/>
      <path d="M254 224 H282"/>
      <path d="M534 224 H562"/>
      <path d="M690 106 V116 Q690 128 678 128 H142 Q130 128 130 140 V168" stroke-linecap="round"/>
    </g>
    <g fill="currentColor" opacity=".45">
      <path d="M281 52.5 L290 58 L281 63.5 Z"/>
      <path d="M561 52.5 L570 58 L561 63.5 Z"/>
      <path d="M281 218.5 L290 224 L281 229.5 Z"/>
      <path d="M561 218.5 L570 224 L561 229.5 Z"/>
      <path d="M124.5 167 L130 176 L135.5 167 Z"/>
    </g>
{nodes}
</svg>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tool", nargs="?", choices=sorted(TOOLS))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default=str(pathlib.Path(__file__).parent / "assets" / "pipeline"))
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    targets = sorted(TOOLS) if args.all else [args.tool or "overview"]
    for t in targets:
        path = out / f"pipeline-{t}.svg"
        path.write_text(build(t))
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
