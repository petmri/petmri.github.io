## Two implementations

There are two, and which one you want depends entirely on what you are mapping.

The **MATLAB scripts** are the original. They are far and away the more capable of the two —
T1 three different ways, T2, T2\*, ADC, and a hook for a model you write yourself. They are
maintained and they work, but they are **feature-frozen**: no new models or features are going
into them.

The **Python pipeline** is where all future work happens. It lives inside
[ROCKETSHIP](https://dceasy.org/ROCKETSHIP/) rather than in this repository, and today it fits
**T1 from variable flip angle and nothing else**. Within that one job it is already the better
tool — B1 correction, BIDS sidecars, GPU acceleration and QC figures are all things the MATLAB
version never had — but the other maps have not been ported yet.

|  | Python, in ROCKETSHIP | MATLAB, this repository |
| --- | --- | --- |
| Status | Actively developed | Maintained, feature-frozen |
| T1 — variable flip angle | Yes, three variants | Yes |
| T1 — inversion recovery, variable TR | Not yet | Yes |
| T2 and T2\* | Not yet | Yes, five variants |
| ADC | Not yet | Yes, four variants |
| Custom model | Not yet | Yes, `user_input` |
| B1 correction | Yes | No |
| Reads acquisition parameters from BIDS | Yes | No |
| GPU acceleration | Yes, via Gpufit | No |
| Needs a MATLAB license | No | Yes |

**So, in practice.** If you want a VFA T1 map — which is what a DCE study needs — use the
Python pipeline. If you want inversion-recovery T1, T2, T2\*, ADC or a custom model, the MATLAB
scripts are the only option, and will remain so until those models are ported.

---

## The Python pipeline

Fits T1 and the equilibrium magnetization ρ voxel by voxel from a variable flip angle series —
several spoiled gradient echo images of the same anatomy at different flip angles. The
pre-contrast T1 map is what
[converts DCE signal to concentration](../concepts/dce-mri.md#conversion-of-signal-intensity-to-concentration).

| `fit_type` | Method | When |
| --- | --- | --- |
| `t1_fa_fit` | Nonlinear fit across all angles | The default, and the right choice unless you have a reason |
| `t1_fa_linear_fit` | Linearized form, solved directly | Faster, but noise on the signal biases the result |
| `t1_fa_two_point_fit` | Closed form from two flip angles | Where only two angles were acquired, or for a fast approximation |

Anything else is rejected outright rather than silently ignored.

### Install

It comes with ROCKETSHIP, whose installer sets up the environment and the acceleration
libraries:

```bash
git clone -b dev https://github.com/petmri/ROCKETSHIP.git
cd ROCKETSHIP
python3 install.py
```

No MATLAB license is required for the Python path.

### Run it

The installer writes a launcher for the GUI:

```bash
./rocketship_parametric.sh
```

Or from the command line, against a run configuration:

```bash
source .venv/bin/activate
python run_parametric_python_cli.py --config python/parametric_run_example.json
```

`run_parametric_bids_batch.py` applies the same configuration across a BIDS dataset.

### Configuration

Two files, with deliberately separate jobs. `python/parametric_defaults.json` holds every
default and preference — edit it to change behavior across all runs. A **run configuration**
names only the data and whatever that run overrides, which keeps configs short and makes the
difference between two runs visible.

Nothing in the source carries a fallback, so a key absent from both is an error rather than a
silent default, and an unrecognized key is rejected rather than ignored. Relative paths in a
run configuration resolve against **the configuration file's own directory**, so a config and
its data move together.

`tr_ms` and `flip_angles_deg` are read from the JSON sidecar beside each VFA image when you do
not supply them — which is what [dce2bids](dce2bids.md) writes.

!!! warning "An unset `b1_map_file` is not the same as no B1 correction"

    With no `b1_map_file` set, the pipeline looks beside each VFA image for
    `B1_scaled_FAreg.nii` or `.nii.gz` — the MATLAB naming convention — and uses the first it
    finds. Only if none is present are nominal flip angles used. The run summary reports which
    of the three happened: `explicit`, `auto` or `none`. Check it rather than assuming.

!!! note "Two more things that will stop a run"

    **Flip angle count must match the image.** `flip_angles_deg` needs one entry per flip frame
    of the image actually being fitted. A preprocessed VFA image combining fewer frames than
    there are sidecars is rejected rather than mispaired.

    **`backend: gpufit` is incompatible with B1-corrected `t1_fa_fit`.** Use `auto`, which
    falls back on its own, or `cpu`.

### What it writes

Into `output_dir`: the T1 map as
`<output_basename>_<fit_type>_<output_label>.nii.gz`, an `Rsquared_...` map, optionally the ρ
map, and QC figures. Voxels failing `rsquared_threshold` — 0.6 by default — are written as
`-1` rather than dropped, so a failed fit stays visible.

### Going deeper

- [Parametric walkthrough](https://dceasy.org/ROCKETSHIP/wiki/parametric-walkthrough/) — a
  worked run from images to maps
- [Parametric options](https://dceasy.org/ROCKETSHIP/parametric_options/) — every key, with
  units and resolution order

---

## The MATLAB scripts

The broader toolbox, and the one to use for anything other than VFA T1.

| You want | Fit type |
| --- | --- |
| T1 from variable flip angle | `t1_fa_fit`, `t1_fa_linear_fit` |
| T1 from inversion recovery | `t1_ti_exponential_fit` |
| T1 from variable TR | `t1_tr_fit` |
| T2 or T2\* | `t2_exponential`, `t2_exponential_plus_c`, `t2_linear_simple`, `t2_linear_weighted`, `t2_linear_fast` |
| ADC | `ADC_exponential`, `ADC_linear_simple`, `ADC_linear_weighted`, `ADC_linear_fast` |
| Something else | `user_input`, which fits a model you supply |

`t2_exponential_plus_c` adds a constant offset — Wood's model — for signal that does not decay
to zero. The `linear_fast` variants trade confidence intervals for speed on large volumes.

### Requirements

- MATLAB, with the **Curve Fitting**, **Image Processing**, **Statistics** and **Parallel**
  toolboxes
- The NIfTI toolbox on the MATLAB path

!!! note "Clone ROCKETSHIP rather than this repository"

    The MATLAB scripts are vendored into ROCKETSHIP at `parametric_scripts/`, alongside the
    NIfTI toolbox they depend on (`external_programs/niftitools/`). That copy works as-is.

    A standalone clone of this repository does **not** carry `load_nii`, `make_nii` or
    `save_nii`, and fails at save time with undefined-function errors unless you put the NIfTI
    toolbox on the path yourself.

Input images are NIfTI (`.nii`) or Analyze (`.hdr` / `.img`). DICOM is not read.

```matlab
addpath(genpath('/path/to/ROCKETSHIP'))
fitting_gui
```

Load the image series, enter the parameter for each — echo time, flip angle, inversion time or
b-value — pick the fit type and run. The GUI also builds and saves batch jobs, so a
configuration worked out interactively replays later without re-entering it.

### Scripted fitting

`fitting_script.m` is a template — copy it, edit the block at the top, run it:

```matlab
file_list       = {'echo1.nii';'echo2.nii';'echo3.nii'};  % one file per parameter value
parameter_list  = [10 20 30]';        % ms or degrees, matching file_list
fit_type        = 't2_exponential';   % see the table above
tr              = 20;                 % ms — only used by the T1 FA fits
rsquared_threshold = 0.2;             % fits below this are written as -1
data_order      = 'xyzfile';          % or 'xynz', 'xyzn' for a single 4D file
number_cpus     = 4;
roi_list        = '';                 % restrict the fit to ROIs instead of every voxel
xy_smooth_size  = 0;                  % in-plane smoothing before fitting, in voxels
odd_echoes      = 0;                  % fit only odd-numbered parameters
```

Get `data_order` right first: `xyzfile` means one 3D file per parameter value, while `xynz` and
`xyzn` describe a single file holding the whole series, differing in whether the parameter
dimension precedes or follows the slice dimension.

Restricting to `roi_list` is worth doing on large volumes — whole-brain voxelwise fitting with
confidence intervals is the slow path.

### What it writes

Beside the input, named from `output_basename` and the fit:

| File | What it is |
| --- | --- |
| `<basename>_<coefficient>_<input>.nii` | One map per fitted coefficient |
| `<basename>_<coefficient>_<input>_cilow.nii` / `_cihigh.nii` | Confidence bounds per coefficient |
| `<basename>_rsquared_<input>.nii` | Goodness of fit, voxelwise |
| `<basename>_<fit_type>_<input>.xls` | Tabulated results |
| `<basename>_<fit_type>_<input>.mat` | The job log, which reloads as a batch |

!!! tip "Read the R² map before the parameter map"

    `visualize_R2.m` and `quick_check.m` exist for this. A T1 map that looks reasonable can
    still rest on fits that never converged, and the R² map is where that shows.

### Batch processing

`calculateMap_batch.m` runs a list of jobs unattended; `makeNewbatch.m` and `load_batch.m`
build and reload them. Jobs saved from the GUI reload the same way, which is the intended route
from one worked case to a whole study. `parallelFit.m` distributes fitting across the cores set
by `number_cpus`.
