# petmri.github.io

Source for **[dceasy.org](https://dceasy.org/)**, the hub for the DCEasy family of
DCE-MRI tools, and the source of truth for the shared theme all three DCEasy sites use.

## Layout

| Path | What it is |
| --- | --- |
| `docs/index.md` | the landing page — generated, see below |
| `docs/tools/` | one page per tool — generated, see below |
| `docs/concepts/` | background pages, written by hand |
| `theme/` | shared theme and asset generators, consumed by every DCEasy site |
| `mkdocs.yml` | hub config; inherits `theme/dceasy-base.yml` directly |

`theme/` is not published — it sits outside `docs/`, so the build never sees it.
See [theme/README.md](theme/README.md) for how the other repos consume it.

## Building

```bash
python3 -m venv .venv          # Zensical needs Python 3.10 or newer
.venv/bin/pip install -r requirements.txt
.venv/bin/zensical serve
```

`zensical build --strict` is what CI runs, and it validates internal links and anchors —
worth running before pushing, since a renamed heading breaks the build rather than
shipping a dead link.

The hub is built with [Zensical](https://zensical.org/) rather than Material for MkDocs.
Material reaches end of life on 5 November 2026, and there was no reason to build a new
site on it twice. ROCKETSHIP and DCEPrep are still on Material and migrate later.

## Editing generated pages

`docs/index.md` and everything in `docs/tools/` are **generated**. Editing them directly
is lost on the next run; edit the source and regenerate.

```bash
.venv/bin/python theme/make-hub-index.py     # docs/index.md
.venv/bin/python theme/make-tool-pages.py    # docs/tools/*.md, or pass one slug
```

Both exist for the same reason: the pages inline SVG — the family band, the pipeline
diagram, and the tool marks — and each has to be inline rather than an `<img>` to inherit
the page's colour and webfonts. An `<img>` is isolated from the document and gets neither.

For tool pages only the header is generated. The prose lives in `theme/tool-pages/<slug>.md`
and is copied through verbatim, so the writing stays hand-editable. Adding a tool is a dict
entry in `theme/make-tool-pages.py` plus a prose file; a stub that only links out to another
site sets `stub=True` and needs no prose file at all.

`docs/concepts/` is plain Markdown with no generator — nothing there inlines SVG.

## Deployment

`.github/workflows/docs.yml` builds with `--strict` and publishes to GitHub Pages on every
push to `main`. The custom domain lives in `docs/CNAME` so that it ends up inside the build
artifact; a CNAME existing only at the repo root is not part of the build output.
