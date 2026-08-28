## When to reach for it

Reach for AIFArtist whenever a person needs to be the one choosing the ROI — and that is more
often than it sounds. See
[the arterial input function](../concepts/dce-mri.md#the-arterial-input-function) for what the
ROI is for.

| Situation | Why AIFArtist |
| --- | --- |
| Not brain data | [AutoAIF](autoaif.md) was trained on brain only; AIFArtist has no such limit |
| Validating automatic selection | Several raters annotate the same cases, giving you the reference AutoAIF's output is measured against |
| A case AutoAIF got wrong | Redraw it by hand without dropping the subject from the study |
| Establishing inter-rater variability | The rater ID is baked into every output filename, so multiple passes coexist |

It is built for volume. The queue auto-advances, prefetches the next image, and skips anything
the current rater has already done — so a review session is `Save and Next` on repeat rather
than a file dialog each time.

## Requirements

- Python 3
- A desktop session — this is a [napari](https://napari.org) GUI on Qt (PySide6), not a
  headless tool. Over SSH it needs X forwarding or a remote desktop

## Install

```bash
git clone https://github.com/petmri/AIFArtist.git && cd AIFArtist
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead.

## Worked example

Point it at a BIDS tree and name the rater:

```bash
source .venv/bin/activate

python aif_artist.py /data/derivatives/DCEPrep --rater AB
```

`--rater` is required — it identifies who is annotating and is embedded in every output
filename, which is what lets several people work the same dataset without collision.

The queue is built by finding every 4D `desc-hmc_DCE.nii` or `desc-hmc_DCE.nii.gz` anywhere
under the paths you give it, derivative datasets included. That naming is
[DCEPrep](https://dceasy.org/DCEPrep/)'s motion-corrected output, so pointing at
`.../derivatives/DCEPrep` is the intended path.

If your data is not BIDS, use a manifest instead — a plain text file with one path per line,
or a CSV/TSV with a `path`, `image`, `image_path` or `nifti` column:

```bash
python aif_artist.py --manifest image_list.tsv --rater AB
```

By default the queue opens at the first image this rater has not yet done, skipping anything
they have already saved or flagged. `--include-completed` reopens finished cases for editing,
and a saved ROI for that rater loads automatically when you return to one.

## What it writes

Outputs go to `./derivatives/AIFArtist` unless you pass `--output-root`:

| File | What it is |
| --- | --- |
| `*_desc-raterXX_label-AIF_mask.nii.gz` | The saved 3D ROI mask |
| `desc-raterXX_flags.csv` | Per-rater log of skipped cases, with `img` and `reason` columns |
| `dataset_description.json` | Written once at the derivative root |

Add `--write-sidecars` and each mask also gets a `.tsv` of the mean signal over time within the
ROI, and a `.json` recording rater, source image, shape and voxel count. Source entities such
as `task`, `acq` and `run` are preserved in the output names, so multi-run sessions do not
collide.

!!! tip "Turn the sidecars on if you want the curve as data"

    Without `--write-sidecars` you get the mask and nothing numeric. The `.tsv` is the ROI
    timeseries you would otherwise have to extract yourself.

## Reviewing efficiently

The curve panel updates live as you paint, and draws a separate trace per label — so painting
label 1 and label 2 in different vessels compares them directly, in place. Optional extra plots
normalize to the first or second timepoint, which is the quickest way to see whether the
baseline is usable.

The controls worth knowing before your first session:

| Action | Control |
| --- | --- |
| Toggle slice view and volume view | `Ctrl+Y` |
| Step through slices (2D) | `scroll` |
| Step through time frames | `Ctrl` + `scroll` |
| Adjust window upper / lower limit (3D) | `Shift` / `Alt` + `scroll` |
| Erase without changing paint mode | `right-click drag` on the ROI layer |
| Save the ROI and advance | `Ctrl+Enter` |

`Flag and Skip` records the current image as **Poor AIF** or **Missing baseline**, appends it
to that rater's flags CSV and moves on — flagged cases never come back for that rater. Use it
rather than leaving a bad ROI behind; the flags file is itself a study record.

Everything else — painting, fill, label selection — is standard napari labels-layer behavior.

## Full control reference

The [repository README](https://github.com/petmri/AIFArtist#controls-reference) documents every
viewer and dock control, including the ones not listed above.
