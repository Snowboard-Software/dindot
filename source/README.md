# DINish sources

The eight DINish 4.007 faces (git `efeeee31`, the upstream release build), from
https://github.com/playbeing/dinish (`fonts/ttf/DINish/`), stored as WOFF2. The
conversion is lossless: `glyf` compiles identically to the upstream TTF, and
every other table except `head` and `loca` matches it byte for byte.

| File | Used for |
| --- | --- |
| `DINish-Regular`, `-Medium`, `-SemiBold`, `-Bold` | The outlines, metrics and features `build.py` turns into the four upright faces. |
| `DINish-Italic`, `-MediumItalic`, `-SemiBoldItalic`, `-BoldItalic` | The reference for the italic's decisions, which `validate.py` checks: the 12 degree angle, the glyphs DINish Italic keeps upright, and the single-storey italic a. DINDOT Italic is drawn from DINDOT's own upright outlines by `italic.py`, not from these. |

Copyright 2021-2024 The DINish Project Authors. DINish derives from Altinn-DIN
and D-DIN. Licensed under the SIL Open Font License, Version 1.1; see `../OFL.txt`
and `../AUTHORS.txt`.
