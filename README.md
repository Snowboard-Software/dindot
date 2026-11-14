# DINDOT

Rounded industrial type by [GetDot](https://www.getdot.ai/), derived from
[DINish](https://github.com/playbeing/dinish).

**[Try the specimen](https://www.getdot.ai/dindot/)** · **[Download the release](https://github.com/Snowboard-Software/dindot/releases/latest)**

[![DINDOT specimen: industrial roots, friendly by nature](images/dindot-specimen.jpg)](https://www.getdot.ai/dindot/)

The published release **0.22.0** contains four weights with matching italics, supplied as
TrueType for desktop use and WOFF2 for self-hosted websites.

| Weight | Upright | Italic |
| --- | --- | --- |
| 400 | Regular | Italic |
| 500 | Medium | Medium Italic |
| 600 | SemiBold | SemiBold Italic |
| 700 | Bold | Bold Italic |

DINDOT has rounded corners, circular dots and tabular figures for data tables.
The release covers 949 encoded characters per face. Consult the live specimen
for character coverage and OpenType features.

## A look at DINDOT

![DINDOT Regular, Medium, SemiBold and Bold, with their matching italics](images/dindot-weights-and-italics.jpg)

Four weights, each with a matching italic. Upright and slanted lettering share
the same rounded details.

[![Rendered railway departure board with DINDOT lettering, aligned times and platform numbers](images/dindot-departure-board.webp)](https://www.getdot.ai/dindot/#data)

A rendered departure-board specimen, with all lettering set in DINDOT. Explore
more [examples in use](https://www.getdot.ai/dindot/#data) on the specimen page.

**Development status:** this branch contains an unreleased **1.000 Google Fonts
candidate**, with editable UFO sources and 987 encoded characters per face.
The existing v0.22.0 download and live specimen are unchanged. See the
[engineering and QA record](documentation/google-fonts/README.md).

## Install

For the development candidate, install the `.ttf` files in
[`fonts/ttf/`](fonts/ttf/). Use the release download above for the published version.

For a website, copy `fonts/` and `dindot.css` together and load the stylesheet:

```html
<link rel="stylesheet" href="/assets/dindot/dindot.css">
```

```css
body { font-family: 'DINDOT', sans-serif; }
.amount { font-variant-numeric: lining-nums tabular-nums; }
```

The stylesheet includes all eight real styles. `data-presets.css` provides
optional UI and numeric presets. Aligning decimals across values also needs
an appropriate table or grid layout.

## Editable sources and build

The eight [`sources/DINDOT-*.ufo`](sources/) files are the maintained design
sources. They include editable outlines, components, metrics, anchors and
OpenType feature source. The original generator and licensed DINish inputs
are preserved under [`sources/procedural/`](sources/procedural/).

Use Python 3.12 and the locked build dependencies:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
sh sources/build.sh
python verify_release.py
```

The standard fontmake build produces eight hinted TTFs in `fonts/ttf` and eight
WOFF2s in `fonts/webfonts`. The UFO sources are used directly; no binary source
extraction or procedural regeneration is performed during normal builds.
See [`sources/README.md`](sources/README.md) for migration provenance and editing
instructions. The original v0.22.0 release, its sources and checksums remain
available at its Git tag and release page.

Regression checks compare all original glyph outlines and advances, required
Latin Core glyphs, OpenType feature behavior and corrected mark sequences.
The workflow also performs two clean builds and compares every output byte.
See [validation instructions and results](documentation/google-fonts/README.md).

## Google Fonts readiness

Submitted for review in [google/fonts#11316](https://github.com/google/fonts/issues/11316).
Catalog acceptance is pending. The definitive menu name remains **DINDOT**;
Google Fonts naming-policy approval is still required.

The [engineering and QA record](documentation/google-fonts/README.md) includes
the editable-source migration, current report, regression results and visual
proof. New Cyrillic designs are candidates for native-reader design review.
Automated QA does not establish final design approval or catalog acceptance.

## License and credits

DINDOT is licensed under the **[SIL Open Font License 1.1](OFL.txt)**, including
commercial use, embedding, modification and redistribution under that license.

Copyright 2026 GetDot for the DINDOT modifications. Copyright 2021–2024 The DINish
Project Authors for the upstream font. DINish derives from Altinn-DIN and D-DIN;
the original D-DIN design is by Charles Nix / Monotype, commissioned by Datto.
See [`AUTHORS.txt`](AUTHORS.txt) and [`sources/procedural/source/README.md`](sources/procedural/source/README.md) for credits
and the exact upstream inputs. These acknowledgements do not imply endorsement.

Please retain the license and contributor notices when redistributing the fonts.
The GetDot name and logo are separate brand assets and are not included in the
font license.

## Feedback

Please open a GitHub issue with the font style, character or text sample,
application and platform needed to reproduce a problem. The specimen and latest
font downloads are at [getdot.ai/dindot](https://www.getdot.ai/dindot/).
