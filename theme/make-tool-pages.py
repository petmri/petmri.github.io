#!/usr/bin/env python3
"""Generate the DCEasy hub tool pages, docs/tools/*.md.

Each page opens with two inline SVGs — the tool's mark and the pipeline diagram
with that tool's stages highlighted. Both have to be inline rather than <img>:
they are drawn in currentColor so they follow the palette, and an <img> is
isolated from the document and inherits nothing. Same constraint that made
make-hub-index.py necessary.

Only the header is generated. The prose lives in theme/tool-pages/<slug>.md and
is copied through verbatim, so the writing stays hand-editable — edit that file,
not the output.

    python3 theme/make-tool-pages.py            # all tools
    python3 theme/make-tool-pages.py autoaif    # one
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "theme" / "assets"
BODIES = ROOT / "theme" / "tool-pages"
OUT = ROOT / "docs" / "tools"

GH = "https://github.com/petmri"

# `pipeline` is the variant slug in theme/assets/pipeline/; `scope` is the
# sentence naming the stages, which has to agree with make-pipeline.py's TOOLS.
PAGES = [
    dict(
        slug="autoaif",
        name="AutoAIF",
        mark="autoaif",
        pipeline="autoaif",
        scope="AutoAIF covers step 3",
        intro=(
            "AutoAIF finds the arterial input function in brain DCE-MRI automatically, with no "
            "manual ROI drawing. It is a 3D U-Net in Keras/TensorFlow, trained on multi-site "
            "brain DCE-MRI cohorts, and it ships with pretrained weights — so for most users "
            "this is an inference tool, not a training project.\n\n"
            "Given a 4D DCE series it predicts a vascular function curve and the 3D mask the "
            "curve was measured from."
        ),
        buttons=[("Repository", f"{GH}/AutoAIF"),
                 ("Paper — MRM 2025", "https://doi.org/10.1002/mrm.70020")],
        cite_lead="If AutoAIF contributes to published work, please cite:",
        citation=(
            "Saca, L., et al. [Automatic detection of arterial input function for brain DCE-MRI "
            "in multi-site cohorts](https://doi.org/10.1002/mrm.70020). *Magnetic Resonance in "
            "Medicine*, 94(6), 2732–2744 (2025). PMID: 40808286"
        ),
    ),
    dict(
        slug="aifartist",
        name="AIFArtist",
        mark="aifartist",
        pipeline="aifartist",
        scope="AIFArtist covers step 3",
        intro=(
            "AIFArtist is a desktop app for drawing the arterial input function by hand on 4D "
            "MRI, built for review sessions where several raters work through many images in "
            "one sitting. It runs on [napari](https://napari.org): draw a 3D ROI, watch the "
            "mean signal curve update as you paint, save a BIDS-style derivative, and move "
            "straight to the next image.\n\n"
            "It is the human-in-the-loop counterpart to [AutoAIF](autoaif.md) — and the source "
            "of the multi-rater reference that automatic selection gets measured against."
        ),
        buttons=[("Repository", f"{GH}/AIFArtist")],
    ),
    dict(
        slug="dce2bids",
        name="dce2bids",
        mark="dce2bids",
        pipeline="dce2bids",
        scope="dce2bids covers step 1",
        intro=(
            "dce2bids turns DCE-MRI DICOMs straight from the scanner into a tidy BIDS dataset. "
            "Because every scanner labels its series and parameters differently, an AI coding "
            "agent works out the right settings **once** per scanner and protocol and writes "
            "them into a script. After that, each new participant converts with a single "
            "command and no AI involved."
        ),
        buttons=[("Repository", f"{GH}/dce2bids")],
    ),
    dict(
        slug="parametric_scripts",
        name="parametric_scripts",
        mark="parametric",
        pipeline="parametric_scripts",
        scope="parametric_scripts covers step 4",
        intro=(
            "parametric_scripts fits quantitative MRI maps voxel by voxel — T1 by variable flip "
            "angle, inversion recovery or variable TR; T2 and T2\\*; and the apparent diffusion "
            "coefficient.\n\n"
            "It exists in two forms: the original MATLAB scripts, which cover far more ground "
            "but are now feature-frozen, and a Python pipeline inside "
            "[ROCKETSHIP](https://dceasy.org/ROCKETSHIP/) where all further development happens "
            "— currently variable flip angle T1 only. Which one you want depends on what you "
            "are mapping."
        ),
        buttons=[("Repository", f"{GH}/parametric_scripts"),
                 ("ROCKETSHIP docs", "https://dceasy.org/ROCKETSHIP/")],
        cite_lead=("parametric_scripts ships as part of ROCKETSHIP and has no separate paper. "
                   "If it contributes to published work, cite ROCKETSHIP:"),
        citation=("Ng, T.S.C., et al. [ROCKETSHIP: a flexible and modular software tool for the "
                  "planning, processing and analysis of dynamic MRI studies]"
                  "(https://doi.org/10.1186/s12880-015-0062-3). *BMC Medical Imaging*, 15, 19 "
                  "(2015). PMID: 26076957"),
    ),
    dict(
        slug="dceprep",
        name="DCEPrep",
        mark="dceprep",
        stub=True,
        intro=("DCEPrep runs the whole DCE-MRI pipeline in one Dockerized pass — preprocessing, "
               "T1 mapping, AIF detection, fitting and QC. It has its own documentation site."),
        buttons=[("Documentation", "https://dceasy.org/DCEPrep/"),
                 ("Repository", f"{GH}/DCEPrep")],
    ),
    dict(
        slug="rocketship",
        name="ROCKETSHIP",
        mark="rocketship",
        stub=True,
        intro=("ROCKETSHIP is the DCE-MRI analysis suite — AIF selection, multi-model "
               "pharmacokinetic fitting and results visualization. It has its own documentation "
               "site."),
        buttons=[("Documentation", "https://dceasy.org/ROCKETSHIP/"),
                 ("Repository", f"{GH}/ROCKETSHIP")],
    ),
]


def inline(path: pathlib.Path, indent: int, extra_class: str = "") -> str:
    svg = path.read_text().rstrip("\n")
    if extra_class:
        svg = svg.replace('role="img"', f'class="{extra_class}" role="img"', 1)
    pad = " " * indent
    return "\n".join(pad + l if l.strip() else l for l in svg.splitlines())


def inline_oneline(path: pathlib.Path, extra_class: str = "") -> str:
    svg = path.read_text()
    if extra_class:
        svg = svg.replace('role="img"', f'class="{extra_class}" role="img"', 1)
    return re.sub(r"\s*\n\s*", " ", svg).strip()


def render(p) -> str:
    mark = inline_oneline(ASSETS / "marks" / f"{p['mark']}.svg", "dceasy-tool-page-mark")
    buttons = "\n".join(f"[{label}]({url}){{ .md-button }}" for label, url in p["buttons"])

    # A stub carries the mark, the name and a link out, and nothing else — it
    # exists so the tool has a home in the nav while its own site holds the
    # documentation. No pipeline figure, no citation, no prose file.
    body = ""
    if not p.get("stub"):
        body = (BODIES / f"{p['slug']}.md").read_text().rstrip("\n")

    # Not every tool has a paper of its own; the section is omitted rather than
    # left standing empty.
    citation = ""
    if p.get("citation"):
        citation = (f"## Citation\n\n{p['cite_lead']}\n\n"
                    f"> {p['citation']}\n\n")

    fits = ""
    if not p.get("stub"):
        pipeline = inline(ASSETS / "pipeline" / f"pipeline-{p['pipeline']}.svg", 2)
        fits = f"""<!-- dceasy-pipeline — generated by theme/make-pipeline.py. Regenerate rather
     than hand-editing; the only thing that differs between pages is which
     stages carry the highlight. -->
## Where this fits

{p['scope']}. The full DCEasy pipeline:

<div class="dceasy-pipeline-figure">
{pipeline}
</div>

"""

    # Front matter sets <title>; Zensical has no homepage special case and falls
    # back to the filename otherwise. See the note in make-hub-index.py.
    return f"""---
title: {p['name']}
---

<!-- Generated by theme/make-tool-pages.py — edit that, not this file. -->

<p class="dceasy-tool-page-mark-wrap">{mark}</p>

# {p['name']}

{p['intro']}

{buttons}

{fits}{citation}{body}
"""


def main():
    wanted = sys.argv[1:]
    OUT.mkdir(parents=True, exist_ok=True)
    for p in PAGES:
        if wanted and p["slug"] not in wanted:
            continue
        dest = OUT / f"{p['slug']}.md"
        # A stub ends with the button row, so the omitted sections leave trailing
        # blank lines behind.
        page = render(p).rstrip("\n") + "\n"
        dest.write_text(page)
        print(f"wrote {dest.relative_to(ROOT)}  ({len(page)/1024:.1f} KB)")


if __name__ == "__main__":
    main()
