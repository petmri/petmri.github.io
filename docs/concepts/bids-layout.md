---
title: The expected BIDS layout
---

# The expected BIDS layout

Every DCEasy tool downstream of conversion locates its inputs by convention rather than by
explicit configuration. This requires that the dataset conform to the layout produced by
[dce2bids](../tools/dce2bids.md).

## Raw data organization

```text
<bids_root>/
├── dataset_description.json
├── .bidsignore
├── README
└── sub-<label>/
    └── ses-<label>/
        ├── anat/
        │   ├── sub-<l>_ses-<l>_T1w.nii.gz          # structural
        │   └── sub-<l>_ses-<l>_flip-0N_VFA.nii.gz  # one per flip angle, N = 1..4
        └── dce/
            └── sub-<l>_ses-<l>_DCE.nii.gz          # the 4D dynamic series
```

Two aspects of this layout depart from the BIDS specification and warrant explanation.

**The `dce/` datatype is non-standard.** No BIDS specification for DCE-MRI has yet been
ratified, so DCEasy retains the `dce/` directory and `DCE` suffix and excludes them from
validation by means of `.bidsignore`. Placement under `perf/` was considered and rejected, that
datatype denoting arterial spin labeling; a derivatives-only layout was likewise rejected, DCE
constituting acquired rather than processed data. The decision is subject to revision should a
BIDS extension proposal for DCE be adopted.

**`VFA` in `anat/` is standard.** The suffix is defined for variable flip angle T1 mapping.
Individual flip series are disambiguated by the `flip-<index>` entity rather than by the angle
itself, which is recorded in the corresponding sidecar and read from there by the tools.

## Sidecar metadata

Quantitative analysis depends upon acquisition parameters, which must accompany the image data.
`RepetitionTime`, `EchoTime`, `FlipAngle` and `MagneticFieldStrength` are required for
modeling and are read by the tools rather than being re-entered.

Three points merit particular attention.

!!! warning "Temporal resolution has no single DICOM field"

    Frame-to-frame spacing is the principal timing quantity in DCE-MRI, yet no single DICOM tag
    carries it reliably. The NIfTI `pixdim[4]` field frequently holds the per-excitation
    repetition time in milliseconds rather than the frame interval, and conversion tools
    deposit the correct value under a different key for each vendor.

    dce2bids normalizes this to a `TemporalResolution` key expressed in seconds, records the
    provenance of the value in `TemporalResolutionSource`, and sets
    `TemporalResolutionReview: true` where the determination was uncertain. This flag should be
    inspected before a fit is accepted, an incorrect temporal resolution scaling every derived
    rate constant.

!!! warning "The contrast agent must be recorded"

    The `ContrastBolusAgent` field is frequently absent from the DICOM header, and the
    relaxivity of the agent is required for conversion to concentration. dce2bids therefore
    requires the agent, supplied either by the operator or read from the header, and terminates
    rather than inferring a value where the two disagree or where neither is available.

**Flip angles must be distinct within a subject.** Duplicate angles across VFA series indicate
that two series collided during conversion, a condition on which `verify_bids.py` fails rather
than warns. Repetition time is additionally expected to be consistent across the flip series of
a subject.

## Derivatives

Processed data is written beneath `derivatives/`, one directory per tool:

```text
<bids_root>/derivatives/
├── DCEPrep/
│   └── sub-<l>/
│       └── sub-<l>_desc-hmc_DCE.nii.gz   # motion-corrected dynamic series
├── AIFArtist/
│   └── sub-<l>/
│       ├── sub-<l>_desc-raterXX_label-AIF_mask.nii.gz
│       └── desc-raterXX_flags.csv
└── AutoAIF/
    └── sub-<l>/
```

The `desc-hmc_DCE` convention is load-bearing. It is the pattern on which
[AIFArtist](../tools/aifartist.md) constructs its queue: given `derivatives/DCEPrep` as input,
it locates every motion-corrected series beneath it, across sessions and runs, without further
specification.

Source entities are preserved through processing, so that `task`, `acq` and `run` propagate into
derivative filenames and multi-run sessions do not collide.

## Verification

Each conversion writes a report to `code/bids_status_report.txt`. The file `code/selection.tsv`
records which series were converted and which were excluded, and should be consulted first where
an expected acquisition is absent. A dataset may be re-checked at any point:

```bash
scripts/verify_bids.py /data/study-1_bids
```

Uniform ✓ and `0 fail` indicate a conforming dataset.

## Non-conforming data

The majority of the pipeline presumes this layout, though not all of it requires it. AIFArtist
accepts a manifest, either a plain text file of paths or a delimited file containing a `path`
column. ROCKETSHIP's Python configurations may name every input file explicitly rather than
discovering it, at the cost of also specifying the acquisition parameters that would otherwise
be read from the sidecars.

This trade-off constitutes the argument for conversion: under BIDS the convention carries the
metadata, whereas in its absence the metadata must be supplied manually, for every analysis, and
correctly.
