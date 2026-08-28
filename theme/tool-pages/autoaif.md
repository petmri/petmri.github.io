## When to reach for it

Use AutoAIF when you have **brain** DCE-MRI and you want the AIF chosen the same way every
time. See [the arterial input function](../concepts/dce-mri.md#the-arterial-input-function)
for the background. It is most worth it on cohorts: manual AIF selection is the step where inter-rater
variability creeps into K<sup>trans</sup>, and a fixed model removes that variance even where it
does not strictly improve accuracy on any single case.

Reach for something else when:

| Situation | Use instead |
| --- | --- |
| Not brain — the model was trained on brain only | [AIFArtist](https://github.com/petmri/AIFArtist) |
| You want a human in the loop, or a multi-rater reference to validate against | [AIFArtist](https://github.com/petmri/AIFArtist) |
| You are already running the whole pipeline in one go | [DCEPrep](https://dceasy.org/DCEPrep/), which calls AutoAIF for you |

Input images should be gzipped NIfTI (`.nii.gz`) in radiological orientation. Dimensions do
not need to match the training data — everything is resampled to 256×256×32×32 internally and
the outputs are resampled back — but the training set spanned roughly 208×256×40×50 to
320×320×14×64, and inputs far outside that range are worth resampling yourself first.

## Requirements

- Python 3.9+
- TensorFlow 2.12+ / Keras 2.12+

!!! note "`requirements.txt` is the GPU install"

    It includes `cupy`, `tensorrt` and `tensorrt_cu12`, which are CUDA-only. On a CPU-only or
    Apple Silicon machine, install the remaining dependencies directly instead:

    ```bash
    pip install matplotlib nibabel numba numpy pandas Pillow \
      pingouin plotly psutil scipy tensorboard tensorflow
    ```

    Inference then runs on CPU, more slowly but with identical results.

## Install

```bash
git clone https://github.com/petmri/AutoAIF.git && cd AutoAIF
python3 -m venv tf && source tf/bin/activate
pip install -r requirements.txt
```

Then fetch the pretrained weights. They are a release asset rather than part of the
repository, so cloning alone is not enough:

```bash
# ~470 MB
curl -L -o model_weight_huber1.h5 \
  https://github.com/petmri/AutoAIF/releases/latest/download/model_weight_huber1.h5
```

## Worked example

One subject, from a preprocessed DCE series to an AIF mask and figures:

```bash
source tf/bin/activate

python main_vif.py --mode inference \
  --input_path  /data/derivatives/DCEPrep/sub-01/sub-01_desc-hmc_DCE.nii.gz \
  --model_weight_path model_weight_huber1.h5 \
  --save_output_path /data/derivatives/AutoAIF/sub-01/ \
  --save_image 1
```

That writes four files into `--save_output_path`, named after the input:

| File | What it is |
| --- | --- |
| `sub-01_desc-hmc_DCE_float_mask.nii` | The raw per-voxel probability map, resampled back to the input geometry |
| `sub-01_desc-hmc_DCE_mask.nii` | The AIF ROI proper — the highest-probability voxels, binarised |
| `sub-01_desc-hmc_DCE_curve.svg` | The vascular function, normalised to its own baseline |
| `sub-01_desc-hmc_DCE_mask.svg` | The ROI overlaid on the image, at the mask's centre-of-mass slice |

Drop `--save_image 1` and you get the two NIfTIs only, which is what you want in a batch run.

!!! tip "Check the overlay before you trust the curve"

    `_mask.svg` is the fastest sanity check in the pipeline. The ROI should land in a major
    artery, not in a vein or a hyperintense edge artefact. If it does not, nothing downstream
    is worth fitting.

## A cohort

Pass one image per call and loop in the shell:

```bash
source tf/bin/activate

for img in /data/derivatives/DCEPrep/sub-*/sub-*_desc-hmc_DCE.nii.gz; do
  sub=$(basename "$img" | cut -d_ -f1)
  python main_vif.py --mode inference \
    --input_path "$img" \
    --model_weight_path model_weight_huber1.h5 \
    --save_output_path "/data/derivatives/AutoAIF/$sub/"
done
```

The weights load once per invocation, which dominates runtime on short series. For a large
cohort it is worth batching inside a single Python process instead.

## Fine-tuning on your own data

The shipped weights were trained on multi-site brain DCE-MRI, and they generalise across
scanners better than a single-site model would. Retraining is still worth it if your sequence,
field strength or contrast protocol sits well outside that range — and the same entry point
trains a model from scratch.

### Dataset layout

Organise the data by site. Each site needs an `images/` folder and a `masks/` folder, with one
mask per image under the same filename:

```
dataset
├── site1
│   ├── images
│   │   └── id_x.nii.gz
│   └── masks
│       └── id_x.nii.gz
├── site2
│   ├── images
│   │   └── id_x.nii.gz
│   └── masks
│       └── id_x.nii.gz
└── site3
    ├── images
    │   └── id_x.nii.gz
    └── masks
        └── id_x.nii.gz
```

Every folder directly under `dataset` is treated as a site, except those whose names begin
with `test` or `TF` — which is what keeps the generated `TFRecords` directory from being
picked up as one.

!!! warning "Two constraints that will not announce themselves"

    **All NIfTI files must be 32-bit.** Nothing checks this up front.

    **Filenames must start with a subject ID followed by an underscore.** The split is taken on
    everything before the first `_`, so `sub-01_ses-1_DCE.nii.gz` and `sub-01_ses-2_DCE.nii.gz`
    are correctly recognised as one subject and land in the same split. Filenames without an
    underscore make every image its own subject, which quietly leaks sessions across the
    train/test boundary.

### Running it

```bash
source tf/bin/activate

python main_vif.py --mode training \
  --dataset_path /path/to/dataset/ \
  --save_checkpoint_path /path/to/checkpoints/ \
  --epochs 200 \
  --batch_size 1
```

`--epochs 200` and `--batch_size 1` are the defaults and can be omitted. `--model_name` selects
the architecture — `best` (the shipped one), `attn` or `modified_attn`. `python main_vif.py -h`
lists everything.

The split is 80/10/10 train/validation/test **per site**, on a fixed seed. It is written to
`train_set.txt`, `val_set.txt` and `test_set.txt` in the checkpoint directory on the first run
and reused verbatim if those files are already there — so a resumed or repeated run keeps the
same test set, and forcing a fresh split means deleting them. TFRecords are likewise only
generated when they are not already present.

Training also writes `log.txt`, `history.npy` and a `history.png` loss curve into the
checkpoint directory, and TensorBoard logs under `logs/fit/`.

### Hyperparameter search

`--mode hp_tuning` sweeps convolution kernel sizes — the first/last layers and the body
independently — and logs each trial to TensorBoard through the HParams plugin:

```bash
python main_vif.py --mode hp_tuning \
  --dataset_path /path/to/dataset/ \
  --save_checkpoint_path /path/to/tuning/
```

Each trial gets its own subdirectory named after its parameters, and a trial whose directory
already exists is skipped — so an interrupted sweep resumes where it stopped rather than
starting over. It is a full grid, so budget accordingly.
