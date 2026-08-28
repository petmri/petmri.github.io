## When to reach for it

Use dce2bids at the start of a study, once per scanner or protocol. Every scanner labels its
series and parameters differently, and the usual cost of that is a conversion script hand-tuned
per site that nobody quite remembers the reasoning behind. dce2bids moves that work to an AI
coding agent, which inspects your actual DICOM headers, works out the mapping, and writes the
script — after which the AI is out of the loop entirely.

It converts exactly what a DCE study needs and leaves the rest of the session alone:

- the **dynamic DCE** series — the 4D contrast scan
- the **VFA** flip-angle scans, for T1 mapping
- one **structural** scan, usually a T1 MPRAGE

Everything downstream in DCEasy expects this layout, so converting here is what lets
[DCEPrep](https://dceasy.org/DCEPrep/) and [AIFArtist](aifartist.md) find their inputs by
convention rather than by configuration — see
[the expected BIDS layout](../concepts/bids-layout.md) for what it produces and why.

## Requirements

- **Linux.** Tested on Ubuntu 22.04. It may work on macOS or Windows via WSL2, but that is
  untested
- **A coding agent**, for the one-time setup only. Designed against Claude Code, Codex, VS Code
  with Copilot, and Cursor; any agent that can read and act on the repository's `SKILL.md`
  should work

!!! note "The AI is needed once, not every time"

    The agent's job is to work out the settings for a scanner and protocol. It writes those
    into a script, and every subsequent participant converts by running that script — no agent,
    no subscription, no variability between runs.

## One-time setup

```bash
git clone https://github.com/petmri/dce2bids.git
cd dce2bids
env/bootstrap.sh
```

`env/bootstrap.sh` installs the conversion tools into a local folder. It is optional — the
agent will run it for you — but running it yourself confirms the environment is sound before
you involve the agent. It is safe to re-run; it skips work already done.

## A new scanner or protocol

Open your coding agent in the `dce2bids` folder, give it access to your data directory, and ask
for the conversion in plain language:

> Convert all the DICOMs in `/data/study-1/` to BIDS using dce2bids. The contrast agent
> **[your contrast agent]** was used for all DCE scans.

!!! warning "Name the contrast agent"

    If you leave it out, the tool falls back to reading it from the DICOM headers — and if it
    is missing there, the conversion raises an error and stops. If the agent varies by subject
    or by date, say so in the request and that handling gets written into the script.

The repository ships worked configurations for several scanners and studies under `configs/` —
Philips Achieva and several Siemens protocols among them. Worth a look before starting from
scratch, since a near match shortens the setup considerably.

## Every run after that

The first run saves a script into the output dataset. Later participants need only:

```bash
/data/study-1_bids/code/run_dce2bids.sh
```

## What you get

Output lands next to the input by default — `/data/study-1/` in gives `/data/study-1_bids`:

```text
study-1_bids/            # the BIDS dataset root
├── sourcedata/          # sorted DICOM files
├── dataset_description.json
├── participants.tsv
├── participants.json
├── README
├── CHANGES
├── .bidsignore
├── code/
│   ├── run_dce2bids.sh          # the script to run for future cases
│   ├── selection.tsv            # which sequences were converted, and which were skipped
│   └── bids_status_report.txt   # the result of the conversion
├── sub-*/               # subject folders with BIDS data
└── derivatives/         # later processing lands here
```

`code/selection.tsv` is the one to read first when something is missing — it records what the
tool chose and what it passed over, which is usually enough to explain a surprise.

## Did it work?

Every conversion writes a full report to `code/bids_status_report.txt`. To re-check a dataset
at any point:

```bash
scripts/verify_bids.py /data/study-1_bids
```

Green ✓ throughout and `0 fail` means the dataset is sound. Any ✗ or ⚠ names what to look at in
plain terms.

## Going deeper

Ask your coding agent — it has the tool's `SKILL.md` and can run the steps, explain a warning,
or set up a new scanner. For internals and design rationale, see
[DESIGN.md](https://github.com/petmri/dce2bids/blob/main/DESIGN.md) in the repository.
