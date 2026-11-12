# Google Fonts readiness review

DINDOT is being proposed for Google Fonts. This folder records an initial QA run
on the unchanged 0.22.0 release fonts from commit
`caa8a1f2abf0caa36ba15a305c5f9c8e37a85cb6`, on 12 November 2026.
It is not a claim of acceptance or production readiness.

Submission and exception discussion: [google/fonts#11316](https://github.com/google/fonts/issues/11316).

## QA evidence

- [Full Google Fonts profile report](fontspector-googlefonts.md)
- [Machine-readable result counts](qa-summary.json)
- [Latin Core codepoint coverage for all eight styles](latin-core-coverage.json)

The official `fontspector-v1.9.1` release asset for Apple Silicon was used; the
binary and generated report identify the checker as **1.9.0**.

```sh
fontspector -p googlefonts -J 4 --timeout 10 \
  --json fontspector-googlefonts.json \
  --ghmarkdown fontspector-googlefonts.md fonts/*.ttf
```

The checker reported 697 PASS, 131 WARN, 69 FAIL, 485 SKIP and 100 INFO
subresults. There were no FATAL or ERROR results. The command exited 1 because
of the failures. These are individual reported results, not 69 separate design
problems: they repeat across styles and name-table platforms.

The 69 failing results belong to eight check IDs:

| Check | Failing results | Work or review needed |
| --- | ---: | --- |
| `googlefonts/family_name_compliance` | 8 | Resolve the all-caps/abbreviation naming rule with Google Fonts. |
| `googlefonts/font_names` | 4 | Normalize the RIBBI typographic name-table records for Google Fonts. |
| `googlefonts/name/version_format` | 16 | Google Fonts requires an internal version of at least 1.000; current release files report 0.922. |
| `googlefonts/name/line_breaks` | 16 | Put the copyright notice on one line while retaining all upstream credit. |
| `googlefonts/unitsperem` | 8 | Review the 8192 UPM precision or rescale with outline and metric comparison. |
| `dotted_circle` | 8 | Attach `horncomb` to the dotted-circle glyph. |
| `googlefonts/glyphsets/shape_languages` | 8 | Review the inferred script/language coverage, missing orthography and mark shaping. |
| `googlefonts/repo/dirname_matches_nameid_1` | 1 | This check expects the Google Fonts family-directory layout; it was run in the upstream `fonts/` folder. |

All eight faces contain all **319 encoded codepoints** in the current
[GF Latin Core NAM file](https://github.com/googlefonts/glyphsets/blob/main/data/results/nam/GF_Latin_Core.nam).
This codepoint comparison is separate from unencoded glyph, OpenType-feature
and language-shaping requirements. It does not override the shaping failures.

## Source and build workflow

The design is maintained as procedural Python, settings and licensed DINish
inputs. There is currently no UFO/Glyphs source tree or fontmake build pipeline.
The [Google Fonts onboarding guide](https://googlefonts.github.io/gf-guide/onboarding.html)
requires those standard sources and builds, or an explicitly approved exception.
The preferred upstream directory structure also remains to be adopted.

A clean Python 3.12 build previously completed all sixteen TTF/WOFF2 outputs,
but exact-byte comparison first differed at `DINDOT-BoldItalic.ttf`. This is
already documented in the repository README. This QA run did not rebuild,
patch or replace any release fonts.

## Authorship and AI assistance

DINDOT is a DINish derivative with GetDot modifications. The upstream credits
and SIL OFL 1.1 notices remain in `AUTHORS.txt`, `OFL.txt` and the font metadata.
AI assistance has been used for development tooling, repository packaging,
documentation, QA and submission preparation under Rick Radewagen's direction.
This does not replace the attribution of the original DINish and D-DIN work.

The specimen images are separately copyrighted GetDot assets, as described in
`images/README.md`; they are not part of the OFL font-software license.
