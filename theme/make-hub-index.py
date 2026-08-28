#!/usr/bin/env python3
"""Generate the DCEasy hub landing page, docs/index.md.

The page inlines three kinds of SVG — the family band, the pipeline diagram and
one mark per tool card. All three have to be inline rather than <img>: the band
carries live text that needs the page's webfont, and the marks and diagram are
drawn in currentColor so they follow the palette. An <img> is isolated from the
document and gets neither.

That makes the page tedious to hand-edit, hence this generator.

    python3 theme/make-hub-index.py
"""
import pathlib, re, textwrap

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "theme" / "assets"
OUT = ROOT / "docs" / "index.md"

GH = "https://github.com/petmri"

TOOLS = [
    dict(slug="dce2bids", name="dce2bids", lang="Python · AI-assisted", stage="Step 1 — convert",
         body="Converts raw DCE-MRI DICOMs straight from the scanner into a tidy BIDS dataset. "
              "An AI coding agent works out the right per-scanner settings once; after that each "
              "new participant converts with a single command, with guardrails and verification "
              "around it.",
         links=[("Documentation", "tools/dce2bids.md"), ("Repository", f"{GH}/dce2bids")]),
    dict(slug="dceprep", name="DCEPrep", lang="Shell · Python · Docker", stage="Steps 2–6 — automated",
         body="The whole pipeline in one container: motion correction, bias field correction, "
              "z-axis normalization, VFA T1 mapping, AIF detection, K<sup>trans</sup> fitting "
              "ROCKETSHIP, and per-case and population QC reports.",
         links=[("Documentation", "https://dceasy.org/DCEPrep/"), ("Repository", f"{GH}/DCEPrep")]),
    dict(slug="parametric", name="parametric_scripts", lang="MATLAB", stage="Step 4 — T1 mapping",
         body="Generates T1 (inversion recovery and variable flip angle), T2, T2* and ADC maps, "
              "with a fitting GUI, batch processing and parallel fitting. Reads NIfTI and Analyze.",
         links=[("Documentation", "tools/parametric_scripts.md"),
                ("Repository", f"{GH}/parametric_scripts")]),
    dict(slug="autoaif", name="AutoAIF", lang="Python · deep learning", stage="Step 3 — AIF",
         body="Finds the arterial input function automatically — no manual ROI drawing. Pretrained "
              "on multi-site brain DCE-MRI cohorts, outputs a vascular function curve and a 3D "
              "mask, and supports fine-tuning on new datasets.",
         links=[("Documentation", "tools/autoaif.md"), ("Repository", f"{GH}/AutoAIF"),
                ("Paper — MRM 2025", "https://doi.org/10.1002/mrm.70020")]),
    dict(slug="aifartist", name="AIFArtist", lang="Python", stage="Step 3 — AIF",
         body="Manual AIF annotation when you want a human in the loop, or a multi-rater reference "
              "to check AutoAIF against. Live ROI curve preview, BIDS-style derivative outputs with "
              "the rater ID in the filename, and flag-and-skip for poor AIFs.",
         links=[("Documentation", "tools/aifartist.md"), ("Repository", f"{GH}/AIFArtist")]),
    dict(slug="rocketship", name="ROCKETSHIP", lang="MATLAB", stage="Steps 5–6 — fit and analyze",
         body="A GUI-driven suite for full DCE-MRI analysis: pre-contrast T1 mapping, AIF selection "
              "and fitting, multi-model pharmacokinetic fitting (Tofts, Extended Tofts, Patlak, "
              "2CXM, FXR, tissue uptake) and results visualization.",
         links=[("Documentation", "https://dceasy.org/ROCKETSHIP/"), ("Repository", f"{GH}/ROCKETSHIP"),
                ("Paper — BMC Med Imaging 2015", "https://doi.org/10.1186/s12880-015-0062-3")]),
    dict(slug="gpufit", name="Gpufit", lang="CUDA · C++", stage="Step 5 — acceleration",
         body="Levenberg–Marquardt curve fitting on the GPU, with the DCE models built in — Patlak, "
              "Tofts, Extended Tofts, tissue uptake, 2CXM, T1 FA exponential. Full CPU parity, "
              "Python and MATLAB wrappers, prebuilt binaries. Useful for accelerating any DCE "
              "pipeline, not only ours.",
         links=[("Repository", f"{GH}/Gpufit")]),
]


def inline(path: pathlib.Path, indent: int, extra_class: str = "") -> str:
    svg = path.read_text().rstrip("\n")
    if extra_class:
        svg = svg.replace('role="img"', f'class="{extra_class}" role="img"', 1)
    pad = " " * indent
    return "\n".join(pad + l if l.strip() else l for l in svg.splitlines())


def inline_oneline(path: pathlib.Path, extra_class: str = "") -> str:
    """Collapse an SVG to a single line.

    Inside a list item, indentation is significant: four spaces is list content
    and eight is a code block. A multi-line SVG in a card is one stray space
    away from being rendered as source. Collapsing sidesteps the whole problem.
    """
    svg = path.read_text()
    if extra_class:
        svg = svg.replace('role="img"', f'class="{extra_class}" role="img"', 1)
    return re.sub(r"\s*\n\s*", " ", svg).strip()


def card(t):
    mark = inline_oneline(ASSETS / "marks" / f"{t['slug']}.svg", "dceasy-tool-mark")
    links = "\n".join(f"    [{label}]({url}){{ .dceasy-tool-link }}" for label, url in t["links"])
    return f"""-   {mark}

    <span class="dceasy-tool-name">{t['name']}</span>
    <span class="dceasy-tool-lang">{t['lang']}</span>

    ---

    {t['body']}

{links}
"""


def main():
    band = inline(ASSETS / "banners" / "dceasy.svg", 2)
    pipeline = inline(ASSETS / "pipeline" / "pipeline-overview.svg", 2)
    cards = "\n".join(card(t) for t in TOOLS)

    # Zensical always renders <title> as "{page title} - {site_name}" and has
    # no homepage special case, so there is no value here that yields a bare
    # "DCEasy". Without front matter it falls back to the filename — "Index -
    # DCEasy" — because the h1 is raw HTML and nothing extracts a title from it.
    # This only sets <title> and the social meta; the nav label stays "Home".
    page = f"""---
title: Quantitative DCE-MRI tools
---

<!-- Generated by theme/make-hub-index.py — edit that, not this file. -->

<h1 class="dceasy-band-figure">
{band}
</h1>

DCEasy is a set of open-source tools for quantitative dynamic contrast-enhanced MRI,
maintained by the PET/MRI Lab at Loma Linda University. Together they cover the whole path
from scanner output to parameter maps; each one is also usable on its own.

## Where each tool fits

<div class="dceasy-pipeline-figure">
{pipeline}
</div>

You can run the pipeline two ways.

**End to end.** [dce2bids]({GH}/dce2bids) converts the study to BIDS, then
[DCEPrep](https://dceasy.org/DCEPrep/) takes it the rest of the way in one Dockerized run —
preprocessing, T1 mapping, AIF detection, fitting and QC.

**Step by step.** Swap in your own tools at any stage, or use ours individually. The stages
are the six above; the cards below say which tool covers each.

## Tools

<div class="grid cards dceasy-tools" markdown>

{cards}
</div>

## Which tool do I need?

<div class="dceasy-need-table" markdown>

| I want to… | Use |
| --- | --- |
| Convert DCE DICOMs to BIDS | [dce2bids](tools/dce2bids.md) |
| Run the complete pipeline on BIDS data, automatically | [DCEPrep](https://dceasy.org/DCEPrep/) |
| Run preprocessing only — motion, alignment, artifact correction | [DCEPrep](https://dceasy.org/DCEPrep/) |
| Generate T1, T2 or ADC maps | [parametric_scripts](tools/parametric_scripts.md) |
| Find the AIF automatically, with deep learning | [AutoAIF](tools/autoaif.md) |
| Draw and save AIF ROIs by hand, across multiple raters | [AIFArtist](tools/aifartist.md) |
| Fit pharmacokinetic models through a GUI | [ROCKETSHIP](https://dceasy.org/ROCKETSHIP/) |
| Accelerate model fitting inside another pipeline | [Gpufit]({GH}/Gpufit) |
| Compare fit quality and parametric maps | [ROCKETSHIP](https://dceasy.org/ROCKETSHIP/) — Module E |

</div>

## Quick start

=== "DCEPrep"

    ```bash
    # The whole pipeline, in Docker
    docker pull lsaca05/dce:R2023a-main

    docker run --rm \\
      -v /path/to/rawdata:/data/rawdata \\
      -v /path/to/matlab.lic:/licenses/matlab.lic \\
      lsaca05/dce:R2023a-main \\
      ./preprocess_all.sh -d /data/rawdata -b -Z
    ```

=== "ROCKETSHIP"

    ```bash
    # -b dev: install.py and the Python module live on dev; master is still v1.3 MATLAB
    git clone -b dev https://github.com/petmri/ROCKETSHIP.git
    cd ROCKETSHIP
    python3 install.py

    ./rocketship_dce.sh          # DCE GUI
    ./rocketship_parametric.sh   # parametric T1 GUI
    ```

=== "AutoAIF"

    ```bash
    git clone https://github.com/petmri/AutoAIF.git && cd AutoAIF
    python3 -m venv tf && source tf/bin/activate
    pip install -r requirements.txt

    # Pretrained weights, ~470 MB
    curl -L -o model_weight_huber1.h5 \\
      https://github.com/petmri/AutoAIF/releases/latest/download/model_weight_huber1.h5

    python main_vif.py --mode inference \\
      --input_path /path/to/dce.nii.gz \\
      --model_weight_path model_weight_huber1.h5 \\
      --save_output_path /path/to/output/
    ```

=== "AIFArtist"

    ```bash
    git clone https://github.com/petmri/AIFArtist.git && cd AIFArtist
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt

    python aif_artist.py /path/to/bids_dataset --rater AB
    ```

## Contact and contributing

Questions are best raised as an issue on the relevant repository. For anything else, contact
the lab maintainer at [sabarnes@llu.edu](mailto:sabarnes@llu.edu). Pull requests are welcome
on all repositories.

[All repositories on GitHub]({GH}){{ .md-button }}
"""
    OUT.write_text(page)
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(page)/1024:.1f} KB)")


if __name__ == "__main__":
    main()
