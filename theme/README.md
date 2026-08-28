# DCEasy shared theme

Single source of truth for the look of every DCEasy documentation site.

| File | Copy to | As |
| --- | --- | --- |
| `dceasy-base.yml` | each site's repo root | `dceasy-base.yml` |
| `dceasy.css` | each site's docs dir | `docs/stylesheets/dceasy.css` |
| `assets/pipeline/pipeline-<tool>.svg` | inlined into the site's `index.md` | see below |
| `assets/banners/<site>.svg` | inlined at the top of the site's `index.md` | see below |
| `assets/dceasy-mark-white.svg` | each site's docs dir | `docs/assets/dceasy-mark-white.svg` |
| `assets/favicons/<site>.svg` | each site's docs dir | `docs/assets/favicon.svg` |

Each site's `mkdocs.yml` then starts with:

```yaml
INHERIT: ./dceasy-base.yml
```

and holds only what genuinely differs: `site_name`, `site_description`, `site_url`,
`repo_url`, `repo_name`, `nav`, and anything site-specific (ROCKETSHIP's MathJax
`extra_javascript`, for instance).

## The pipeline diagram

`make-pipeline.py` generates the family pipeline diagram — six stages in two rows, with
one tool's stages highlighted:

```bash
python3 theme/make-pipeline.py --all      # writes theme/assets/pipeline/
```

Paste the matching file **inline** into the site's `index.md`, inside a
`<div class="dceasy-pipeline-figure">`, under the `<!-- dceasy-pipeline -->` marker.
Inline rather than `<img>` on purpose: every stroke and label is `currentColor`, so an
inlined diagram inherits the page's text colour and reads in both palettes. Referenced as
an image it would be isolated from the page and stuck on one.

The highlight is the one fixed colour. It ships as presentation attributes so the file
still reads standalone, and `dceasy.css` swaps it to the sky accent under `slate`, where
the teal falls below contrast minimums.

This replaced a Mermaid version. Mermaid routes links between subgraphs centre-to-centre,
so it could not draw the wrap from stage 3 back to stage 4; it also needed hard-coded
fills that broke in dark mode, and pulled ~400 KB of JavaScript to lay out a fixed graph.

## Marks

Three directories, one system:

| Directory | What it holds | Used at |
| --- | --- | --- |
| `assets/marks/` | full detail, `currentColor`, 24px grid | 24px and up |
| `assets/marks-16/` | **separate drawings**, not scale-downs | 16px |
| `assets/favicons/` | generated — sky tile, navy glyph | browser tabs |

The 16px set exists because shrinking does not work: at two-thirds scale a 2px stroke lands
on 1.33px and blurs, AIFArtist's dash disintegrates, and Gpufit's eight pins merge into the
body. The small drawings shed detail instead — four pins not eight, a 2x2 grid not 3x3,
larger dots.

```bash
python3 theme/make-favicon.py --all       # marks-16/ -> favicons/
```

The generator pre-divides every `stroke-width` by the glyph scale, so the design's two
weights (2 for the subject, 1.5 for anything supporting it) survive being scaled into the
tile.

`dceasy-mark-white.svg` is the header logo. It has to be baked white because `theme.logo`
renders an `<img>`, and an image is isolated from the document — no `currentColor`, no
inherited anything. Its axis sits at `.45` rather than the design's `.3`: the three-tier
opacity ramp is calibrated for a mark on a page ground, and white ink on the navy header is
a different problem. At `.3` the axis measures 2.65:1 against `#0D1F3C`.

## Banners

One band per site, in `assets/banners/`. The plot is the constant — the same four kinetic
curves everywhere, which is what makes the sites read as one family — and the right-hand
slot is the variable: the rocket for ROCKETSHIP, slices snapping into registration for
DCEPrep, the pipeline stages riding the family curve for the hub.

**Inline them, do not use `<img>`.** The wordmark is live `<text>`, and an SVG loaded as an
image cannot reach the document's webfonts, so IBM Plex Sans would silently fall back.
Verified in the browser: the ROCKETSHIP wordmark measures 357px in Plex against 369px in the
Helvetica fallback.

Each file's gradient id is namespaced (`dceasy-band-<site>`) because ids go global once the
SVG is inlined.

On an index page the band replaces the `# Sitename` heading rather than sitting under it —
wrap it in `<h1 class="dceasy-band-figure">` so the page keeps one real heading, named from
the SVG's `aria-label`. Do not add a front-matter `title:` to compensate: Material appends
the site name to `page.meta.title`, and the homepage ignores `page.title` regardless.

The plate is a fixed light gradient in both palettes — a deliberate call. A light ground
reads as a printed figure and avoids stacking a second dark slab under an already-navy
header. `dceasy.css` §8 adds a hairline in slate so it does not float.

## Rules that are easy to get wrong

**`theme.features` must not be redeclared by a site.** Lists replace rather than merge,
so a site that declares even one feature silently drops the other twelve. Add new features
to `dceasy-base.yml` instead.

**`markdown_extensions` and `plugins` use dict syntax** (`admonition: {}`, not
`- admonition`) precisely so sites *can* add entries without redeclaring the set. Keep it
that way.

**`INHERIT` takes a local relative path.** It cannot fetch a URL, which is why these files
have to be copied rather than referenced. Until the sync workflow exists, changing the theme
means updating this directory and re-copying to each site.

## Verifying a change

From a site repo, after copying both files:

```bash
mkdocs build --strict
```

Then confirm the merge resolved as expected:

```bash
python -c "from mkdocs.config import load_config; c=load_config('mkdocs.yml'); print(len(c['theme']['features']), 'features;', len(c['markdown_extensions']), 'extensions')"
```

Thirteen features is the current baseline. A lower number means a site redeclared the list.
