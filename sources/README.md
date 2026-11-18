# Maintained design sources

The eight `DINDOT-*.ufo` directories are the editable design sources for the
unreleased **1.001 Google Fonts candidate**. Open them in any UFO 3 compatible
font editor. Their outlines, components, metrics, anchors and `features.fea`
files are maintained here. A normal build uses these sources directly; it does
not extract sources from a binary or run the historical procedural generator.

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
sh sources/build.sh
```

Outputs go to `fonts/ttf` and `fonts/webfonts`. The build invokes fontmake and
ttfautohint, then fixes timestamps for reproducible output. Explicit OpenType
features are compiled as written; automatic feature writers are disabled to
avoid replacing the reviewed kerning and mark positioning. The FEA is the
authoritative positioning source; UFO anchors also expose the attachment
locations for editing. If an anchor is moved, update its FEA positioning too.

## Provenance and migration

The initial UFO outlines were extracted from DINDOT's OFL-licensed v0.22.0
release, which was generated from DINish 4.007 and this project's procedural
design code. This conversion does not recover original designer control
points or make the upstream work our sole original design. It provides an
editable, standard source representation of our existing released outlines.
The original release and code remain available at the `v0.22.0` Git tag.

The one-time migration is recorded in `scripts/import_v022_sources.py` and
`documentation/google-fonts/source-migration.json`. To audit it, unpack the
original v0.22.0 release, install `requirements-import.txt`, and pass that
directory to the migration script. Running it overwrites the maintained UFOs;
it is **not** part of an ordinary build and should not be used after editing
the UFOs without first preserving those edits.

The migration changes the export grid from 8192 to 2048 UPM, updates metadata,
preserves all existing encoded characters and features, repairs missing mark
attachments, and supplies Latin Core's unencoded Catalan dots and dotted-i
form. Soft-dotted forms preserve each base's advance before above accents. New Cyrillic characters complete the mandatory orthographies reported
by Fontspector. Canonically decomposable letters use this family's existing
bases and accents. Non-decomposing en-ghe, ghe with middle hook and ka with
vertical stroke combine or extend this family's own outlines; their joins
are Boolean-unioned before saving. Palochka and Cyrillic AE reuse the
equivalent I and AE designs. These new Cyrillic designs remain subject to
native-reader and Google Fonts design review; a passing shaping check is not
a linguistic or typographic endorsement.

`procedural/` preserves the earlier generator, settings, DINish inputs and
its own pinned requirements for historical study. It builds into that folder
and does not control the current UFO sources. Its 0.22-era outputs are not a
second font family or an alternative version to install.

All font sources and build code are under the root SIL OFL 1.1, with the
upstream attribution in `AUTHORS.txt` and the license notices retained.

## Candidate 1.001 maintenance

`../scripts/prepare_1001_candidate.py` records the one-time update from the
1.000 sources. Normal builds continue to use these maintained UFOs directly.
Carons now use a real base plus the distinct alternate caron, with a visible
gap at every weight. The proportional-to symbol was redrawn at the common
math advance using its weight's existing stroke thickness. Redundant and
zero-length segments were removed; tiny axis errors were snapped and gentle
polyline turns were replaced by tangent quadratics with a maximum corner
displacement of 1.5/2048 em. The binary regression report measures the result.

U+00AD SOFT HYPHEN is left to the shaping engine. Six unreachable unencoded
legacy marks remain editable here but are excluded from export using the UFO
`public.skipExportGlyphs` convention. The normal build also writes a STAT table
with weight/style values and linked upright/italic records. No release ZIP or
live website font is replaced by these development-candidate changes.
