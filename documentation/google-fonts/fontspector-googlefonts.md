## FontSpector report

fontspector version: 1.9.0






## Check results




<details><summary>[1] dindot</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Check for codepoints not covered by METADATA subsets. (googlefonts/metadata/unreachable_subsetting)</summary>
    <div>


> This check ensures that all encoded glyphs in the font are covered by a subset declared in the METADATA.pb. Google Fonts splits the font into a set of subset fonts based on the contents of the `subsets` field and the subset definitions in the `glyphsets` repository.
>
> Any encoded glyphs which are not by any of these subset definitions will not be served in the subsetted fonts, and so will be unreachable to the end user.




Original proposal: [https://github.com/fonttools/fontbakery/issues/4097 and https://github.com/fonttools/fontbakery/pull/4273]





- ⚠️ **WARN** dindot/DINDOT-Bold.ttf: The following codepoints supported by the font are not covered by any subsets defined in the font's metadata file, and will never be served. You can solve this by either manually adding additional subset declarations to METADATA.pb, or by editing the glyphset definitions.

* U+02D8 BREVE: try adding one of: canadian-aboriginal, yi
* U+02D9 DOT ABOVE: try adding one of: canadian-aboriginal, yi
* U+02DB OGONEK: try adding one of: canadian-aboriginal, yi
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: cherokee, coptic, math, tifinagh
* U+0306 COMBINING BREVE: try adding one of: old-permic, tifinagh
* U+0307 COMBINING DOT ABOVE: try adding one of: todhri, canadian-aboriginal, old-permic, tifinagh, hebrew, coptic, duployan, malayalam, math, syriac, tai-le
* U+030A COMBINING RING ABOVE: try adding one of: syriac, duployan
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: cherokee, osage
* U+030C COMBINING CARON: try adding one of: cherokee, tai-le
... and 205 others

Or you can add the above codepoints to one of the subsets supported by the font: cyrillic-ext, cyrillic, greek, latin-ext, latin, vietnamese [code: unreachable-subsetting]




- ⚠️ **WARN** dindot/DINDOT-BoldItalic.ttf: The following codepoints supported by the font are not covered by any subsets defined in the font's metadata file, and will never be served. You can solve this by either manually adding additional subset declarations to METADATA.pb, or by editing the glyphset definitions.

* U+02D8 BREVE: try adding one of: canadian-aboriginal, yi
* U+02D9 DOT ABOVE: try adding one of: canadian-aboriginal, yi
* U+02DB OGONEK: try adding one of: canadian-aboriginal, yi
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: cherokee, coptic, math, tifinagh
* U+0306 COMBINING BREVE: try adding one of: old-permic, tifinagh
* U+0307 COMBINING DOT ABOVE: try adding one of: todhri, canadian-aboriginal, old-permic, tifinagh, hebrew, coptic, duployan, malayalam, math, syriac, tai-le
* U+030A COMBINING RING ABOVE: try adding one of: syriac, duployan
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: cherokee, osage
* U+030C COMBINING CARON: try adding one of: cherokee, tai-le
... and 205 others

Or you can add the above codepoints to one of the subsets supported by the font: cyrillic-ext, cyrillic, greek, latin-ext, latin, vietnamese [code: unreachable-subsetting]




- ⚠️ **WARN** dindot/DINDOT-Italic.ttf: The following codepoints supported by the font are not covered by any subsets defined in the font's metadata file, and will never be served. You can solve this by either manually adding additional subset declarations to METADATA.pb, or by editing the glyphset definitions.

* U+02D8 BREVE: try adding one of: canadian-aboriginal, yi
* U+02D9 DOT ABOVE: try adding one of: canadian-aboriginal, yi
* U+02DB OGONEK: try adding one of: canadian-aboriginal, yi
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: cherokee, coptic, math, tifinagh
* U+0306 COMBINING BREVE: try adding one of: old-permic, tifinagh
* U+0307 COMBINING DOT ABOVE: try adding one of: todhri, canadian-aboriginal, old-permic, tifinagh, hebrew, coptic, duployan, malayalam, math, syriac, tai-le
* U+030A COMBINING RING ABOVE: try adding one of: syriac, duployan
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: cherokee, osage
* U+030C COMBINING CARON: try adding one of: cherokee, tai-le
... and 205 others

Or you can add the above codepoints to one of the subsets supported by the font: cyrillic-ext, cyrillic, greek, latin-ext, latin, vietnamese [code: unreachable-subsetting]




- ⚠️ **WARN** dindot/DINDOT-Medium.ttf: The following codepoints supported by the font are not covered by any subsets defined in the font's metadata file, and will never be served. You can solve this by either manually adding additional subset declarations to METADATA.pb, or by editing the glyphset definitions.

* U+02D8 BREVE: try adding one of: canadian-aboriginal, yi
* U+02D9 DOT ABOVE: try adding one of: canadian-aboriginal, yi
* U+02DB OGONEK: try adding one of: canadian-aboriginal, yi
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: cherokee, coptic, math, tifinagh
* U+0306 COMBINING BREVE: try adding one of: old-permic, tifinagh
* U+0307 COMBINING DOT ABOVE: try adding one of: todhri, canadian-aboriginal, old-permic, tifinagh, hebrew, coptic, duployan, malayalam, math, syriac, tai-le
* U+030A COMBINING RING ABOVE: try adding one of: syriac, duployan
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: cherokee, osage
* U+030C COMBINING CARON: try adding one of: cherokee, tai-le
... and 205 others

Or you can add the above codepoints to one of the subsets supported by the font: cyrillic-ext, cyrillic, greek, latin-ext, latin, vietnamese [code: unreachable-subsetting]




- ⚠️ **WARN** dindot/DINDOT-MediumItalic.ttf: The following codepoints supported by the font are not covered by any subsets defined in the font's metadata file, and will never be served. You can solve this by either manually adding additional subset declarations to METADATA.pb, or by editing the glyphset definitions.

* U+02D8 BREVE: try adding one of: canadian-aboriginal, yi
* U+02D9 DOT ABOVE: try adding one of: canadian-aboriginal, yi
* U+02DB OGONEK: try adding one of: canadian-aboriginal, yi
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: cherokee, coptic, math, tifinagh
* U+0306 COMBINING BREVE: try adding one of: old-permic, tifinagh
* U+0307 COMBINING DOT ABOVE: try adding one of: todhri, canadian-aboriginal, old-permic, tifinagh, hebrew, coptic, duployan, malayalam, math, syriac, tai-le
* U+030A COMBINING RING ABOVE: try adding one of: syriac, duployan
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: cherokee, osage
* U+030C COMBINING CARON: try adding one of: cherokee, tai-le
... and 205 others

Or you can add the above codepoints to one of the subsets supported by the font: cyrillic-ext, cyrillic, greek, latin-ext, latin, vietnamese [code: unreachable-subsetting]




- ⚠️ **WARN** dindot/DINDOT-Regular.ttf: The following codepoints supported by the font are not covered by any subsets defined in the font's metadata file, and will never be served. You can solve this by either manually adding additional subset declarations to METADATA.pb, or by editing the glyphset definitions.

* U+02D8 BREVE: try adding one of: canadian-aboriginal, yi
* U+02D9 DOT ABOVE: try adding one of: canadian-aboriginal, yi
* U+02DB OGONEK: try adding one of: canadian-aboriginal, yi
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: cherokee, coptic, math, tifinagh
* U+0306 COMBINING BREVE: try adding one of: old-permic, tifinagh
* U+0307 COMBINING DOT ABOVE: try adding one of: todhri, canadian-aboriginal, old-permic, tifinagh, hebrew, coptic, duployan, malayalam, math, syriac, tai-le
* U+030A COMBINING RING ABOVE: try adding one of: syriac, duployan
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: cherokee, osage
* U+030C COMBINING CARON: try adding one of: cherokee, tai-le
... and 205 others

Or you can add the above codepoints to one of the subsets supported by the font: cyrillic-ext, cyrillic, greek, latin-ext, latin, vietnamese [code: unreachable-subsetting]




- ⚠️ **WARN** dindot/DINDOT-SemiBold.ttf: The following codepoints supported by the font are not covered by any subsets defined in the font's metadata file, and will never be served. You can solve this by either manually adding additional subset declarations to METADATA.pb, or by editing the glyphset definitions.

* U+02D8 BREVE: try adding one of: canadian-aboriginal, yi
* U+02D9 DOT ABOVE: try adding one of: canadian-aboriginal, yi
* U+02DB OGONEK: try adding one of: canadian-aboriginal, yi
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: cherokee, coptic, math, tifinagh
* U+0306 COMBINING BREVE: try adding one of: old-permic, tifinagh
* U+0307 COMBINING DOT ABOVE: try adding one of: todhri, canadian-aboriginal, old-permic, tifinagh, hebrew, coptic, duployan, malayalam, math, syriac, tai-le
* U+030A COMBINING RING ABOVE: try adding one of: syriac, duployan
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: cherokee, osage
* U+030C COMBINING CARON: try adding one of: cherokee, tai-le
... and 205 others

Or you can add the above codepoints to one of the subsets supported by the font: cyrillic-ext, cyrillic, greek, latin-ext, latin, vietnamese [code: unreachable-subsetting]




- ⚠️ **WARN** dindot/DINDOT-SemiBoldItalic.ttf: The following codepoints supported by the font are not covered by any subsets defined in the font's metadata file, and will never be served. You can solve this by either manually adding additional subset declarations to METADATA.pb, or by editing the glyphset definitions.

* U+02D8 BREVE: try adding one of: canadian-aboriginal, yi
* U+02D9 DOT ABOVE: try adding one of: canadian-aboriginal, yi
* U+02DB OGONEK: try adding one of: canadian-aboriginal, yi
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: cherokee, coptic, math, tifinagh
* U+0306 COMBINING BREVE: try adding one of: old-permic, tifinagh
* U+0307 COMBINING DOT ABOVE: try adding one of: todhri, canadian-aboriginal, old-permic, tifinagh, hebrew, coptic, duployan, malayalam, math, syriac, tai-le
* U+030A COMBINING RING ABOVE: try adding one of: syriac, duployan
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: cherokee, osage
* U+030C COMBINING CARON: try adding one of: cherokee, tai-le
... and 205 others

Or you can add the above codepoints to one of the subsets supported by the font: cyrillic-ext, cyrillic, greek, latin-ext, latin, vietnamese [code: unreachable-subsetting]



</div>
</details>


</div>
</details>


<details><summary>[3] dindot/DINDOT-SemiBold.ttf</summary>
<div>


<details>
    <summary>🔥 <b>FAIL</b> Check family name for GF Guide compliance. (googlefonts/family_name_compliance)</summary>
    <div>


> Checks the family name for compliance with the Google Fonts Guide. https://googlefonts.github.io/gf-guide/onboarding.html#new-fonts
>
> If you want to have your family name added to the CamelCase exceptions list, please submit a pull request to the camelcased_familyname_exceptions.txt file.
>
> Similarly, abbreviations can be submitted to the abbreviations_familyname_exceptions.txt file.
>
> These are located in the Lib/fontbakery/data/googlefonts/ directory of the FontBakery source code currently hosted at https://github.com/fonttools/fontbakery/




Original proposal: [https://github.com/fonttools/fontbakery/issues/4049]





- 🔥 **FAIL** "DINDOT" contains an abbreviation. [code: abbreviation]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check if each glyph has the recommended amount of contours. (contour_count)</summary>
    <div>


> Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only be constructured in a handful of ways. This means a glyph's contour count will only differ slightly amongst different fonts, e.g a 'g' could either be 2 or 3 contours, depending on whether its double story or single story.
>
> However, a quotedbl should have 2 contours, unless the font belongs to a display family.
>
> This check currently does not cover variable fonts because there's plenty of alternative ways of constructing glyphs with multiple outlines for each feature in a VarFont. The expected contour count data for this check is currently optimized for the typical construction of glyphs in static fonts.




Original proposal: [https://github.com/fonttools/fontbakery/issues/4829]





- ⚠️ **WARN** This check inspects the glyph outlines and detects the total number of contours in each of them. The expected values are
     inferred from the typical amounts of contours observed in a
     large collection of reference font families. The divergences
     listed below may simply indicate a significantly different
     design on some of your glyphs. On the other hand, some of these
     may flag actual bugs in the font such as glyphs mapped to an
     incorrect codepoint. Please consider reviewing the design and
     codepoint assignment of these to make sure they are correct.


    The following glyphs do not have the recommended number of contours:
* zero.osf (unencoded): found 3, expected one of: [2]
* zero.tlf (unencoded): found 3, expected one of: [2]
* zero.tosf (unencoded): found 3, expected one of: [2]
* uni2152 (U+2152): found 6, expected one of: [5, 10] [code: contour-count]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Shapes languages in all GF glyphsets. (googlefonts/glyphsets/shape_languages)</summary>
    <div>


> This check uses a heuristic to determine which GF glyphsets a font supports. Then it checks the font for correct shaping behaviour for all languages in those glyphsets.




Original proposal: [https://github.com/googlefonts/fontbakery/issues/4147]





- ⚠️ **WARN** Warning language shaping:

| Message                                                           | Languages             |
|-------------------------------------------------------------------|-----------------------|
| Auxiliary orthography codepoints:                                 | * fi_Latn (Finnish)   |
|   The following auxiliary characters are missing from the font: Ǥ |                       |
|   The following auxiliary characters are missing from the font: Ȟ |                       |
|   The following auxiliary characters are missing from the font: Ʒ |                       |
|   The following auxiliary characters are missing from the font: Ǯ |                       |
|   The following auxiliary characters are missing from the font: ǥ |                       |
|   The following auxiliary characters are missing from the font: ȟ |                       |
|   The following auxiliary characters are missing from the font: ʒ |                       |
|   The following auxiliary characters are missing from the font: ǯ |                       |
| Auxiliary orthography codepoints:                                 | * mn_Cyrl (Mongolian) |
|   The following auxiliary characters are missing from the font: ӊ |                       |
| Auxiliary orthography codepoints:                                 | * de_Latn (German)    |
|   The following auxiliary characters are missing from the font: ſ | * fr_Latn (French)    |
| Auxiliary orthography codepoints:                                 | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѣ | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѫ |                       |
| Auxiliary orthography codepoints:                                 | * ca_Latn (Catalan)   |
|   The following auxiliary characters are missing from the font: Ŀ |                       |
|   The following auxiliary characters are missing from the font: ŀ |                       |
| Auxiliary orthography codepoints:                                 | * en_Latn (English)   |
|   The following auxiliary characters are missing from the font: ʻ |                       |
| Auxiliary orthography codepoints:                                 | * el_Grek (Greek)     |
|   The following auxiliary characters are missing from the font: ἀ |                       |
|   The following auxiliary characters are missing from the font: ἄ |                       |
|   The following auxiliary characters are missing from the font: ἂ |                       |
|   The following auxiliary characters are missing from the font: ἆ |                       |
|   The following auxiliary characters are missing from the font: ἁ |                       |
|   The following auxiliary characters are missing from the font: ἅ |                       |
|   The following auxiliary characters are missing from the font: ἃ |                       |
|   The following auxiliary characters are missing from the font: ἇ |                       |
|   The following auxiliary characters are missing from the font: ὰ |                       |
|   The following auxiliary characters are missing from the font: ᾶ |                       |
|   The following auxiliary characters are missing from the font: ἐ |                       |
|   The following auxiliary characters are missing from the font: ἔ |                       |
|   The following auxiliary characters are missing from the font: ἒ |                       |
|   The following auxiliary characters are missing from the font: ἑ |                       |
|   The following auxiliary characters are missing from the font: ἕ |                       |
|   The following auxiliary characters are missing from the font: ἓ |                       |
|   The following auxiliary characters are missing from the font: ὲ |                       |
|   The following auxiliary characters are missing from the font: ἠ |                       |
|   The following auxiliary characters are missing from the font: ἤ |                       |
|   The following auxiliary characters are missing from the font: ἢ |                       |
|   The following auxiliary characters are missing from the font: ἦ |                       |
|   The following auxiliary characters are missing from the font: ἡ |                       |
|   The following auxiliary characters are missing from the font: ἥ |                       |
|   The following auxiliary characters are missing from the font: ἣ |                       |
|   The following auxiliary characters are missing from the font: ἧ |                       |
|   The following auxiliary characters are missing from the font: ὴ |                       |
|   The following auxiliary characters are missing from the font: ῆ |                       |
|   The following auxiliary characters are missing from the font: ἰ |                       |
|   The following auxiliary characters are missing from the font: ἴ |                       |
|   The following auxiliary characters are missing from the font: ἲ |                       |
|   The following auxiliary characters are missing from the font: ἶ |                       |
|   The following auxiliary characters are missing from the font: ἱ |                       |
|   The following auxiliary characters are missing from the font: ἵ |                       |
|   The following auxiliary characters are missing from the font: ἳ |                       |
|   The following auxiliary characters are missing from the font: ἷ |                       |
|   The following auxiliary characters are missing from the font: ὶ |                       |
|   The following auxiliary characters are missing from the font: ῖ |                       |
|   The following auxiliary characters are missing from the font: ῒ |                       |
|   The following auxiliary characters are missing from the font: ῗ |                       |
|   The following auxiliary characters are missing from the font: ὄ |                       |
|   The following auxiliary characters are missing from the font: ὂ |                       |
|   The following auxiliary characters are missing from the font: ὃ |                       |
|   The following auxiliary characters are missing from the font: ὸ |                       |
|   The following auxiliary characters are missing from the font: ὐ |                       |
|   The following auxiliary characters are missing from the font: ὔ |                       |
|   The following auxiliary characters are missing from the font: ὒ |                       |
|   The following auxiliary characters are missing from the font: ὖ |                       |
|   The following auxiliary characters are missing from the font: ὑ |                       |
|   The following auxiliary characters are missing from the font: ὕ |                       |
|   The following auxiliary characters are missing from the font: ὓ |                       |
|   The following auxiliary characters are missing from the font: ὗ |                       |
|   The following auxiliary characters are missing from the font: ὺ |                       |
|   The following auxiliary characters are missing from the font: ῦ |                       |
|   The following auxiliary characters are missing from the font: ῢ |                       |
|   The following auxiliary characters are missing from the font: ῧ |                       |
|   The following auxiliary characters are missing from the font: ὤ |                       |
|   The following auxiliary characters are missing from the font: ὢ |                       |
|   The following auxiliary characters are missing from the font: ὦ |                       |
|   The following auxiliary characters are missing from the font: ὥ |                       |
|   The following auxiliary characters are missing from the font: ὣ |                       |
|   The following auxiliary characters are missing from the font: ὧ |                       |
|   The following auxiliary characters are missing from the font: ὼ |                       |
|   The following auxiliary characters are missing from the font: ῶ |                       | [code: warning-language-shaping]



</div>
</details>


</div>
</details>


<details><summary>[3] dindot/DINDOT-Regular.ttf</summary>
<div>


<details>
    <summary>🔥 <b>FAIL</b> Check family name for GF Guide compliance. (googlefonts/family_name_compliance)</summary>
    <div>


> Checks the family name for compliance with the Google Fonts Guide. https://googlefonts.github.io/gf-guide/onboarding.html#new-fonts
>
> If you want to have your family name added to the CamelCase exceptions list, please submit a pull request to the camelcased_familyname_exceptions.txt file.
>
> Similarly, abbreviations can be submitted to the abbreviations_familyname_exceptions.txt file.
>
> These are located in the Lib/fontbakery/data/googlefonts/ directory of the FontBakery source code currently hosted at https://github.com/fonttools/fontbakery/




Original proposal: [https://github.com/fonttools/fontbakery/issues/4049]





- 🔥 **FAIL** "DINDOT" contains an abbreviation. [code: abbreviation]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check if each glyph has the recommended amount of contours. (contour_count)</summary>
    <div>


> Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only be constructured in a handful of ways. This means a glyph's contour count will only differ slightly amongst different fonts, e.g a 'g' could either be 2 or 3 contours, depending on whether its double story or single story.
>
> However, a quotedbl should have 2 contours, unless the font belongs to a display family.
>
> This check currently does not cover variable fonts because there's plenty of alternative ways of constructing glyphs with multiple outlines for each feature in a VarFont. The expected contour count data for this check is currently optimized for the typical construction of glyphs in static fonts.




Original proposal: [https://github.com/fonttools/fontbakery/issues/4829]





- ⚠️ **WARN** This check inspects the glyph outlines and detects the total number of contours in each of them. The expected values are
     inferred from the typical amounts of contours observed in a
     large collection of reference font families. The divergences
     listed below may simply indicate a significantly different
     design on some of your glyphs. On the other hand, some of these
     may flag actual bugs in the font such as glyphs mapped to an
     incorrect codepoint. Please consider reviewing the design and
     codepoint assignment of these to make sure they are correct.


    The following glyphs do not have the recommended number of contours:
* zero.osf (unencoded): found 3, expected one of: [2]
* zero.tlf (unencoded): found 3, expected one of: [2]
* zero.tosf (unencoded): found 3, expected one of: [2]
* uni2152 (U+2152): found 6, expected one of: [5, 10] [code: contour-count]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Shapes languages in all GF glyphsets. (googlefonts/glyphsets/shape_languages)</summary>
    <div>


> This check uses a heuristic to determine which GF glyphsets a font supports. Then it checks the font for correct shaping behaviour for all languages in those glyphsets.




Original proposal: [https://github.com/googlefonts/fontbakery/issues/4147]





- ⚠️ **WARN** Warning language shaping:

| Message                                                           | Languages             |
|-------------------------------------------------------------------|-----------------------|
| Auxiliary orthography codepoints:                                 | * ca_Latn (Catalan)   |
|   The following auxiliary characters are missing from the font: Ŀ |                       |
|   The following auxiliary characters are missing from the font: ŀ |                       |
| Auxiliary orthography codepoints:                                 | * el_Grek (Greek)     |
|   The following auxiliary characters are missing from the font: ἀ |                       |
|   The following auxiliary characters are missing from the font: ἄ |                       |
|   The following auxiliary characters are missing from the font: ἂ |                       |
|   The following auxiliary characters are missing from the font: ἆ |                       |
|   The following auxiliary characters are missing from the font: ἁ |                       |
|   The following auxiliary characters are missing from the font: ἅ |                       |
|   The following auxiliary characters are missing from the font: ἃ |                       |
|   The following auxiliary characters are missing from the font: ἇ |                       |
|   The following auxiliary characters are missing from the font: ὰ |                       |
|   The following auxiliary characters are missing from the font: ᾶ |                       |
|   The following auxiliary characters are missing from the font: ἐ |                       |
|   The following auxiliary characters are missing from the font: ἔ |                       |
|   The following auxiliary characters are missing from the font: ἒ |                       |
|   The following auxiliary characters are missing from the font: ἑ |                       |
|   The following auxiliary characters are missing from the font: ἕ |                       |
|   The following auxiliary characters are missing from the font: ἓ |                       |
|   The following auxiliary characters are missing from the font: ὲ |                       |
|   The following auxiliary characters are missing from the font: ἠ |                       |
|   The following auxiliary characters are missing from the font: ἤ |                       |
|   The following auxiliary characters are missing from the font: ἢ |                       |
|   The following auxiliary characters are missing from the font: ἦ |                       |
|   The following auxiliary characters are missing from the font: ἡ |                       |
|   The following auxiliary characters are missing from the font: ἥ |                       |
|   The following auxiliary characters are missing from the font: ἣ |                       |
|   The following auxiliary characters are missing from the font: ἧ |                       |
|   The following auxiliary characters are missing from the font: ὴ |                       |
|   The following auxiliary characters are missing from the font: ῆ |                       |
|   The following auxiliary characters are missing from the font: ἰ |                       |
|   The following auxiliary characters are missing from the font: ἴ |                       |
|   The following auxiliary characters are missing from the font: ἲ |                       |
|   The following auxiliary characters are missing from the font: ἶ |                       |
|   The following auxiliary characters are missing from the font: ἱ |                       |
|   The following auxiliary characters are missing from the font: ἵ |                       |
|   The following auxiliary characters are missing from the font: ἳ |                       |
|   The following auxiliary characters are missing from the font: ἷ |                       |
|   The following auxiliary characters are missing from the font: ὶ |                       |
|   The following auxiliary characters are missing from the font: ῖ |                       |
|   The following auxiliary characters are missing from the font: ῒ |                       |
|   The following auxiliary characters are missing from the font: ῗ |                       |
|   The following auxiliary characters are missing from the font: ὄ |                       |
|   The following auxiliary characters are missing from the font: ὂ |                       |
|   The following auxiliary characters are missing from the font: ὃ |                       |
|   The following auxiliary characters are missing from the font: ὸ |                       |
|   The following auxiliary characters are missing from the font: ὐ |                       |
|   The following auxiliary characters are missing from the font: ὔ |                       |
|   The following auxiliary characters are missing from the font: ὒ |                       |
|   The following auxiliary characters are missing from the font: ὖ |                       |
|   The following auxiliary characters are missing from the font: ὑ |                       |
|   The following auxiliary characters are missing from the font: ὕ |                       |
|   The following auxiliary characters are missing from the font: ὓ |                       |
|   The following auxiliary characters are missing from the font: ὗ |                       |
|   The following auxiliary characters are missing from the font: ὺ |                       |
|   The following auxiliary characters are missing from the font: ῦ |                       |
|   The following auxiliary characters are missing from the font: ῢ |                       |
|   The following auxiliary characters are missing from the font: ῧ |                       |
|   The following auxiliary characters are missing from the font: ὤ |                       |
|   The following auxiliary characters are missing from the font: ὢ |                       |
|   The following auxiliary characters are missing from the font: ὦ |                       |
|   The following auxiliary characters are missing from the font: ὥ |                       |
|   The following auxiliary characters are missing from the font: ὣ |                       |
|   The following auxiliary characters are missing from the font: ὧ |                       |
|   The following auxiliary characters are missing from the font: ὼ |                       |
|   The following auxiliary characters are missing from the font: ῶ |                       |
| Auxiliary orthography codepoints:                                 | * fi_Latn (Finnish)   |
|   The following auxiliary characters are missing from the font: Ǥ |                       |
|   The following auxiliary characters are missing from the font: Ȟ |                       |
|   The following auxiliary characters are missing from the font: Ʒ |                       |
|   The following auxiliary characters are missing from the font: Ǯ |                       |
|   The following auxiliary characters are missing from the font: ǥ |                       |
|   The following auxiliary characters are missing from the font: ȟ |                       |
|   The following auxiliary characters are missing from the font: ʒ |                       |
|   The following auxiliary characters are missing from the font: ǯ |                       |
| Auxiliary orthography codepoints:                                 | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѣ | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѫ |                       |
| Auxiliary orthography codepoints:                                 | * mn_Cyrl (Mongolian) |
|   The following auxiliary characters are missing from the font: ӊ |                       |
| Auxiliary orthography codepoints:                                 | * de_Latn (German)    |
|   The following auxiliary characters are missing from the font: ſ | * fr_Latn (French)    |
| Auxiliary orthography codepoints:                                 | * en_Latn (English)   |
|   The following auxiliary characters are missing from the font: ʻ |                       | [code: warning-language-shaping]



</div>
</details>


</div>
</details>


<details><summary>[3] dindot/DINDOT-Bold.ttf</summary>
<div>


<details>
    <summary>🔥 <b>FAIL</b> Check family name for GF Guide compliance. (googlefonts/family_name_compliance)</summary>
    <div>


> Checks the family name for compliance with the Google Fonts Guide. https://googlefonts.github.io/gf-guide/onboarding.html#new-fonts
>
> If you want to have your family name added to the CamelCase exceptions list, please submit a pull request to the camelcased_familyname_exceptions.txt file.
>
> Similarly, abbreviations can be submitted to the abbreviations_familyname_exceptions.txt file.
>
> These are located in the Lib/fontbakery/data/googlefonts/ directory of the FontBakery source code currently hosted at https://github.com/fonttools/fontbakery/




Original proposal: [https://github.com/fonttools/fontbakery/issues/4049]





- 🔥 **FAIL** "DINDOT" contains an abbreviation. [code: abbreviation]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check if each glyph has the recommended amount of contours. (contour_count)</summary>
    <div>


> Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only be constructured in a handful of ways. This means a glyph's contour count will only differ slightly amongst different fonts, e.g a 'g' could either be 2 or 3 contours, depending on whether its double story or single story.
>
> However, a quotedbl should have 2 contours, unless the font belongs to a display family.
>
> This check currently does not cover variable fonts because there's plenty of alternative ways of constructing glyphs with multiple outlines for each feature in a VarFont. The expected contour count data for this check is currently optimized for the typical construction of glyphs in static fonts.




Original proposal: [https://github.com/fonttools/fontbakery/issues/4829]





- ⚠️ **WARN** This check inspects the glyph outlines and detects the total number of contours in each of them. The expected values are
     inferred from the typical amounts of contours observed in a
     large collection of reference font families. The divergences
     listed below may simply indicate a significantly different
     design on some of your glyphs. On the other hand, some of these
     may flag actual bugs in the font such as glyphs mapped to an
     incorrect codepoint. Please consider reviewing the design and
     codepoint assignment of these to make sure they are correct.


    The following glyphs do not have the recommended number of contours:
* zero.osf (unencoded): found 3, expected one of: [2]
* zero.tlf (unencoded): found 3, expected one of: [2]
* zero.tosf (unencoded): found 3, expected one of: [2]
* uni2152 (U+2152): found 6, expected one of: [5, 10] [code: contour-count]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Shapes languages in all GF glyphsets. (googlefonts/glyphsets/shape_languages)</summary>
    <div>


> This check uses a heuristic to determine which GF glyphsets a font supports. Then it checks the font for correct shaping behaviour for all languages in those glyphsets.




Original proposal: [https://github.com/googlefonts/fontbakery/issues/4147]





- ⚠️ **WARN** Warning language shaping:

| Message                                                           | Languages             |
|-------------------------------------------------------------------|-----------------------|
| Auxiliary orthography codepoints:                                 | * ca_Latn (Catalan)   |
|   The following auxiliary characters are missing from the font: Ŀ |                       |
|   The following auxiliary characters are missing from the font: ŀ |                       |
| Auxiliary orthography codepoints:                                 | * de_Latn (German)    |
|   The following auxiliary characters are missing from the font: ſ | * fr_Latn (French)    |
| Auxiliary orthography codepoints:                                 | * mn_Cyrl (Mongolian) |
|   The following auxiliary characters are missing from the font: ӊ |                       |
| Auxiliary orthography codepoints:                                 | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѣ | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѫ |                       |
| Auxiliary orthography codepoints:                                 | * fi_Latn (Finnish)   |
|   The following auxiliary characters are missing from the font: Ǥ |                       |
|   The following auxiliary characters are missing from the font: Ȟ |                       |
|   The following auxiliary characters are missing from the font: Ʒ |                       |
|   The following auxiliary characters are missing from the font: Ǯ |                       |
|   The following auxiliary characters are missing from the font: ǥ |                       |
|   The following auxiliary characters are missing from the font: ȟ |                       |
|   The following auxiliary characters are missing from the font: ʒ |                       |
|   The following auxiliary characters are missing from the font: ǯ |                       |
| Auxiliary orthography codepoints:                                 | * en_Latn (English)   |
|   The following auxiliary characters are missing from the font: ʻ |                       |
| Auxiliary orthography codepoints:                                 | * el_Grek (Greek)     |
|   The following auxiliary characters are missing from the font: ἀ |                       |
|   The following auxiliary characters are missing from the font: ἄ |                       |
|   The following auxiliary characters are missing from the font: ἂ |                       |
|   The following auxiliary characters are missing from the font: ἆ |                       |
|   The following auxiliary characters are missing from the font: ἁ |                       |
|   The following auxiliary characters are missing from the font: ἅ |                       |
|   The following auxiliary characters are missing from the font: ἃ |                       |
|   The following auxiliary characters are missing from the font: ἇ |                       |
|   The following auxiliary characters are missing from the font: ὰ |                       |
|   The following auxiliary characters are missing from the font: ᾶ |                       |
|   The following auxiliary characters are missing from the font: ἐ |                       |
|   The following auxiliary characters are missing from the font: ἔ |                       |
|   The following auxiliary characters are missing from the font: ἒ |                       |
|   The following auxiliary characters are missing from the font: ἑ |                       |
|   The following auxiliary characters are missing from the font: ἕ |                       |
|   The following auxiliary characters are missing from the font: ἓ |                       |
|   The following auxiliary characters are missing from the font: ὲ |                       |
|   The following auxiliary characters are missing from the font: ἠ |                       |
|   The following auxiliary characters are missing from the font: ἤ |                       |
|   The following auxiliary characters are missing from the font: ἢ |                       |
|   The following auxiliary characters are missing from the font: ἦ |                       |
|   The following auxiliary characters are missing from the font: ἡ |                       |
|   The following auxiliary characters are missing from the font: ἥ |                       |
|   The following auxiliary characters are missing from the font: ἣ |                       |
|   The following auxiliary characters are missing from the font: ἧ |                       |
|   The following auxiliary characters are missing from the font: ὴ |                       |
|   The following auxiliary characters are missing from the font: ῆ |                       |
|   The following auxiliary characters are missing from the font: ἰ |                       |
|   The following auxiliary characters are missing from the font: ἴ |                       |
|   The following auxiliary characters are missing from the font: ἲ |                       |
|   The following auxiliary characters are missing from the font: ἶ |                       |
|   The following auxiliary characters are missing from the font: ἱ |                       |
|   The following auxiliary characters are missing from the font: ἵ |                       |
|   The following auxiliary characters are missing from the font: ἳ |                       |
|   The following auxiliary characters are missing from the font: ἷ |                       |
|   The following auxiliary characters are missing from the font: ὶ |                       |
|   The following auxiliary characters are missing from the font: ῖ |                       |
|   The following auxiliary characters are missing from the font: ῒ |                       |
|   The following auxiliary characters are missing from the font: ῗ |                       |
|   The following auxiliary characters are missing from the font: ὄ |                       |
|   The following auxiliary characters are missing from the font: ὂ |                       |
|   The following auxiliary characters are missing from the font: ὃ |                       |
|   The following auxiliary characters are missing from the font: ὸ |                       |
|   The following auxiliary characters are missing from the font: ὐ |                       |
|   The following auxiliary characters are missing from the font: ὔ |                       |
|   The following auxiliary characters are missing from the font: ὒ |                       |
|   The following auxiliary characters are missing from the font: ὖ |                       |
|   The following auxiliary characters are missing from the font: ὑ |                       |
|   The following auxiliary characters are missing from the font: ὕ |                       |
|   The following auxiliary characters are missing from the font: ὓ |                       |
|   The following auxiliary characters are missing from the font: ὗ |                       |
|   The following auxiliary characters are missing from the font: ὺ |                       |
|   The following auxiliary characters are missing from the font: ῦ |                       |
|   The following auxiliary characters are missing from the font: ῢ |                       |
|   The following auxiliary characters are missing from the font: ῧ |                       |
|   The following auxiliary characters are missing from the font: ὤ |                       |
|   The following auxiliary characters are missing from the font: ὢ |                       |
|   The following auxiliary characters are missing from the font: ὦ |                       |
|   The following auxiliary characters are missing from the font: ὥ |                       |
|   The following auxiliary characters are missing from the font: ὣ |                       |
|   The following auxiliary characters are missing from the font: ὧ |                       |
|   The following auxiliary characters are missing from the font: ὼ |                       |
|   The following auxiliary characters are missing from the font: ῶ |                       | [code: warning-language-shaping]



</div>
</details>


</div>
</details>


<details><summary>[3] dindot/DINDOT-SemiBoldItalic.ttf</summary>
<div>


<details>
    <summary>🔥 <b>FAIL</b> Check family name for GF Guide compliance. (googlefonts/family_name_compliance)</summary>
    <div>


> Checks the family name for compliance with the Google Fonts Guide. https://googlefonts.github.io/gf-guide/onboarding.html#new-fonts
>
> If you want to have your family name added to the CamelCase exceptions list, please submit a pull request to the camelcased_familyname_exceptions.txt file.
>
> Similarly, abbreviations can be submitted to the abbreviations_familyname_exceptions.txt file.
>
> These are located in the Lib/fontbakery/data/googlefonts/ directory of the FontBakery source code currently hosted at https://github.com/fonttools/fontbakery/




Original proposal: [https://github.com/fonttools/fontbakery/issues/4049]





- 🔥 **FAIL** "DINDOT" contains an abbreviation. [code: abbreviation]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check if each glyph has the recommended amount of contours. (contour_count)</summary>
    <div>


> Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only be constructured in a handful of ways. This means a glyph's contour count will only differ slightly amongst different fonts, e.g a 'g' could either be 2 or 3 contours, depending on whether its double story or single story.
>
> However, a quotedbl should have 2 contours, unless the font belongs to a display family.
>
> This check currently does not cover variable fonts because there's plenty of alternative ways of constructing glyphs with multiple outlines for each feature in a VarFont. The expected contour count data for this check is currently optimized for the typical construction of glyphs in static fonts.




Original proposal: [https://github.com/fonttools/fontbakery/issues/4829]





- ⚠️ **WARN** This check inspects the glyph outlines and detects the total number of contours in each of them. The expected values are
     inferred from the typical amounts of contours observed in a
     large collection of reference font families. The divergences
     listed below may simply indicate a significantly different
     design on some of your glyphs. On the other hand, some of these
     may flag actual bugs in the font such as glyphs mapped to an
     incorrect codepoint. Please consider reviewing the design and
     codepoint assignment of these to make sure they are correct.


    The following glyphs do not have the recommended number of contours:
* zero.osf (unencoded): found 3, expected one of: [2]
* zero.tlf (unencoded): found 3, expected one of: [2]
* zero.tosf (unencoded): found 3, expected one of: [2]
* uni2152 (U+2152): found 6, expected one of: [5, 10] [code: contour-count]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Shapes languages in all GF glyphsets. (googlefonts/glyphsets/shape_languages)</summary>
    <div>


> This check uses a heuristic to determine which GF glyphsets a font supports. Then it checks the font for correct shaping behaviour for all languages in those glyphsets.




Original proposal: [https://github.com/googlefonts/fontbakery/issues/4147]





- ⚠️ **WARN** Warning language shaping:

| Message                                                           | Languages             |
|-------------------------------------------------------------------|-----------------------|
| Auxiliary orthography codepoints:                                 | * el_Grek (Greek)     |
|   The following auxiliary characters are missing from the font: ἀ |                       |
|   The following auxiliary characters are missing from the font: ἄ |                       |
|   The following auxiliary characters are missing from the font: ἂ |                       |
|   The following auxiliary characters are missing from the font: ἆ |                       |
|   The following auxiliary characters are missing from the font: ἁ |                       |
|   The following auxiliary characters are missing from the font: ἅ |                       |
|   The following auxiliary characters are missing from the font: ἃ |                       |
|   The following auxiliary characters are missing from the font: ἇ |                       |
|   The following auxiliary characters are missing from the font: ὰ |                       |
|   The following auxiliary characters are missing from the font: ᾶ |                       |
|   The following auxiliary characters are missing from the font: ἐ |                       |
|   The following auxiliary characters are missing from the font: ἔ |                       |
|   The following auxiliary characters are missing from the font: ἒ |                       |
|   The following auxiliary characters are missing from the font: ἑ |                       |
|   The following auxiliary characters are missing from the font: ἕ |                       |
|   The following auxiliary characters are missing from the font: ἓ |                       |
|   The following auxiliary characters are missing from the font: ὲ |                       |
|   The following auxiliary characters are missing from the font: ἠ |                       |
|   The following auxiliary characters are missing from the font: ἤ |                       |
|   The following auxiliary characters are missing from the font: ἢ |                       |
|   The following auxiliary characters are missing from the font: ἦ |                       |
|   The following auxiliary characters are missing from the font: ἡ |                       |
|   The following auxiliary characters are missing from the font: ἥ |                       |
|   The following auxiliary characters are missing from the font: ἣ |                       |
|   The following auxiliary characters are missing from the font: ἧ |                       |
|   The following auxiliary characters are missing from the font: ὴ |                       |
|   The following auxiliary characters are missing from the font: ῆ |                       |
|   The following auxiliary characters are missing from the font: ἰ |                       |
|   The following auxiliary characters are missing from the font: ἴ |                       |
|   The following auxiliary characters are missing from the font: ἲ |                       |
|   The following auxiliary characters are missing from the font: ἶ |                       |
|   The following auxiliary characters are missing from the font: ἱ |                       |
|   The following auxiliary characters are missing from the font: ἵ |                       |
|   The following auxiliary characters are missing from the font: ἳ |                       |
|   The following auxiliary characters are missing from the font: ἷ |                       |
|   The following auxiliary characters are missing from the font: ὶ |                       |
|   The following auxiliary characters are missing from the font: ῖ |                       |
|   The following auxiliary characters are missing from the font: ῒ |                       |
|   The following auxiliary characters are missing from the font: ῗ |                       |
|   The following auxiliary characters are missing from the font: ὄ |                       |
|   The following auxiliary characters are missing from the font: ὂ |                       |
|   The following auxiliary characters are missing from the font: ὃ |                       |
|   The following auxiliary characters are missing from the font: ὸ |                       |
|   The following auxiliary characters are missing from the font: ὐ |                       |
|   The following auxiliary characters are missing from the font: ὔ |                       |
|   The following auxiliary characters are missing from the font: ὒ |                       |
|   The following auxiliary characters are missing from the font: ὖ |                       |
|   The following auxiliary characters are missing from the font: ὑ |                       |
|   The following auxiliary characters are missing from the font: ὕ |                       |
|   The following auxiliary characters are missing from the font: ὓ |                       |
|   The following auxiliary characters are missing from the font: ὗ |                       |
|   The following auxiliary characters are missing from the font: ὺ |                       |
|   The following auxiliary characters are missing from the font: ῦ |                       |
|   The following auxiliary characters are missing from the font: ῢ |                       |
|   The following auxiliary characters are missing from the font: ῧ |                       |
|   The following auxiliary characters are missing from the font: ὤ |                       |
|   The following auxiliary characters are missing from the font: ὢ |                       |
|   The following auxiliary characters are missing from the font: ὦ |                       |
|   The following auxiliary characters are missing from the font: ὥ |                       |
|   The following auxiliary characters are missing from the font: ὣ |                       |
|   The following auxiliary characters are missing from the font: ὧ |                       |
|   The following auxiliary characters are missing from the font: ὼ |                       |
|   The following auxiliary characters are missing from the font: ῶ |                       |
| Auxiliary orthography codepoints:                                 | * ca_Latn (Catalan)   |
|   The following auxiliary characters are missing from the font: Ŀ |                       |
|   The following auxiliary characters are missing from the font: ŀ |                       |
| Auxiliary orthography codepoints:                                 | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѣ | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѫ |                       |
| Auxiliary orthography codepoints:                                 | * de_Latn (German)    |
|   The following auxiliary characters are missing from the font: ſ | * fr_Latn (French)    |
| Auxiliary orthography codepoints:                                 | * en_Latn (English)   |
|   The following auxiliary characters are missing from the font: ʻ |                       |
| Auxiliary orthography codepoints:                                 | * mn_Cyrl (Mongolian) |
|   The following auxiliary characters are missing from the font: ӊ |                       |
| Auxiliary orthography codepoints:                                 | * fi_Latn (Finnish)   |
|   The following auxiliary characters are missing from the font: Ǥ |                       |
|   The following auxiliary characters are missing from the font: Ȟ |                       |
|   The following auxiliary characters are missing from the font: Ʒ |                       |
|   The following auxiliary characters are missing from the font: Ǯ |                       |
|   The following auxiliary characters are missing from the font: ǥ |                       |
|   The following auxiliary characters are missing from the font: ȟ |                       |
|   The following auxiliary characters are missing from the font: ʒ |                       |
|   The following auxiliary characters are missing from the font: ǯ |                       | [code: warning-language-shaping]



</div>
</details>


</div>
</details>


<details><summary>[3] dindot/DINDOT-BoldItalic.ttf</summary>
<div>


<details>
    <summary>🔥 <b>FAIL</b> Check family name for GF Guide compliance. (googlefonts/family_name_compliance)</summary>
    <div>


> Checks the family name for compliance with the Google Fonts Guide. https://googlefonts.github.io/gf-guide/onboarding.html#new-fonts
>
> If you want to have your family name added to the CamelCase exceptions list, please submit a pull request to the camelcased_familyname_exceptions.txt file.
>
> Similarly, abbreviations can be submitted to the abbreviations_familyname_exceptions.txt file.
>
> These are located in the Lib/fontbakery/data/googlefonts/ directory of the FontBakery source code currently hosted at https://github.com/fonttools/fontbakery/




Original proposal: [https://github.com/fonttools/fontbakery/issues/4049]





- 🔥 **FAIL** "DINDOT" contains an abbreviation. [code: abbreviation]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check if each glyph has the recommended amount of contours. (contour_count)</summary>
    <div>


> Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only be constructured in a handful of ways. This means a glyph's contour count will only differ slightly amongst different fonts, e.g a 'g' could either be 2 or 3 contours, depending on whether its double story or single story.
>
> However, a quotedbl should have 2 contours, unless the font belongs to a display family.
>
> This check currently does not cover variable fonts because there's plenty of alternative ways of constructing glyphs with multiple outlines for each feature in a VarFont. The expected contour count data for this check is currently optimized for the typical construction of glyphs in static fonts.




Original proposal: [https://github.com/fonttools/fontbakery/issues/4829]





- ⚠️ **WARN** This check inspects the glyph outlines and detects the total number of contours in each of them. The expected values are
     inferred from the typical amounts of contours observed in a
     large collection of reference font families. The divergences
     listed below may simply indicate a significantly different
     design on some of your glyphs. On the other hand, some of these
     may flag actual bugs in the font such as glyphs mapped to an
     incorrect codepoint. Please consider reviewing the design and
     codepoint assignment of these to make sure they are correct.


    The following glyphs do not have the recommended number of contours:
* zero.osf (unencoded): found 3, expected one of: [2]
* zero.tlf (unencoded): found 3, expected one of: [2]
* zero.tosf (unencoded): found 3, expected one of: [2]
* uni2152 (U+2152): found 6, expected one of: [5, 10] [code: contour-count]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Shapes languages in all GF glyphsets. (googlefonts/glyphsets/shape_languages)</summary>
    <div>


> This check uses a heuristic to determine which GF glyphsets a font supports. Then it checks the font for correct shaping behaviour for all languages in those glyphsets.




Original proposal: [https://github.com/googlefonts/fontbakery/issues/4147]





- ⚠️ **WARN** Warning language shaping:

| Message                                                           | Languages             |
|-------------------------------------------------------------------|-----------------------|
| Auxiliary orthography codepoints:                                 | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѣ | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѫ |                       |
| Auxiliary orthography codepoints:                                 | * mn_Cyrl (Mongolian) |
|   The following auxiliary characters are missing from the font: ӊ |                       |
| Auxiliary orthography codepoints:                                 | * de_Latn (German)    |
|   The following auxiliary characters are missing from the font: ſ | * fr_Latn (French)    |
| Auxiliary orthography codepoints:                                 | * en_Latn (English)   |
|   The following auxiliary characters are missing from the font: ʻ |                       |
| Auxiliary orthography codepoints:                                 | * ca_Latn (Catalan)   |
|   The following auxiliary characters are missing from the font: Ŀ |                       |
|   The following auxiliary characters are missing from the font: ŀ |                       |
| Auxiliary orthography codepoints:                                 | * fi_Latn (Finnish)   |
|   The following auxiliary characters are missing from the font: Ǥ |                       |
|   The following auxiliary characters are missing from the font: Ȟ |                       |
|   The following auxiliary characters are missing from the font: Ʒ |                       |
|   The following auxiliary characters are missing from the font: Ǯ |                       |
|   The following auxiliary characters are missing from the font: ǥ |                       |
|   The following auxiliary characters are missing from the font: ȟ |                       |
|   The following auxiliary characters are missing from the font: ʒ |                       |
|   The following auxiliary characters are missing from the font: ǯ |                       |
| Auxiliary orthography codepoints:                                 | * el_Grek (Greek)     |
|   The following auxiliary characters are missing from the font: ἀ |                       |
|   The following auxiliary characters are missing from the font: ἄ |                       |
|   The following auxiliary characters are missing from the font: ἂ |                       |
|   The following auxiliary characters are missing from the font: ἆ |                       |
|   The following auxiliary characters are missing from the font: ἁ |                       |
|   The following auxiliary characters are missing from the font: ἅ |                       |
|   The following auxiliary characters are missing from the font: ἃ |                       |
|   The following auxiliary characters are missing from the font: ἇ |                       |
|   The following auxiliary characters are missing from the font: ὰ |                       |
|   The following auxiliary characters are missing from the font: ᾶ |                       |
|   The following auxiliary characters are missing from the font: ἐ |                       |
|   The following auxiliary characters are missing from the font: ἔ |                       |
|   The following auxiliary characters are missing from the font: ἒ |                       |
|   The following auxiliary characters are missing from the font: ἑ |                       |
|   The following auxiliary characters are missing from the font: ἕ |                       |
|   The following auxiliary characters are missing from the font: ἓ |                       |
|   The following auxiliary characters are missing from the font: ὲ |                       |
|   The following auxiliary characters are missing from the font: ἠ |                       |
|   The following auxiliary characters are missing from the font: ἤ |                       |
|   The following auxiliary characters are missing from the font: ἢ |                       |
|   The following auxiliary characters are missing from the font: ἦ |                       |
|   The following auxiliary characters are missing from the font: ἡ |                       |
|   The following auxiliary characters are missing from the font: ἥ |                       |
|   The following auxiliary characters are missing from the font: ἣ |                       |
|   The following auxiliary characters are missing from the font: ἧ |                       |
|   The following auxiliary characters are missing from the font: ὴ |                       |
|   The following auxiliary characters are missing from the font: ῆ |                       |
|   The following auxiliary characters are missing from the font: ἰ |                       |
|   The following auxiliary characters are missing from the font: ἴ |                       |
|   The following auxiliary characters are missing from the font: ἲ |                       |
|   The following auxiliary characters are missing from the font: ἶ |                       |
|   The following auxiliary characters are missing from the font: ἱ |                       |
|   The following auxiliary characters are missing from the font: ἵ |                       |
|   The following auxiliary characters are missing from the font: ἳ |                       |
|   The following auxiliary characters are missing from the font: ἷ |                       |
|   The following auxiliary characters are missing from the font: ὶ |                       |
|   The following auxiliary characters are missing from the font: ῖ |                       |
|   The following auxiliary characters are missing from the font: ῒ |                       |
|   The following auxiliary characters are missing from the font: ῗ |                       |
|   The following auxiliary characters are missing from the font: ὄ |                       |
|   The following auxiliary characters are missing from the font: ὂ |                       |
|   The following auxiliary characters are missing from the font: ὃ |                       |
|   The following auxiliary characters are missing from the font: ὸ |                       |
|   The following auxiliary characters are missing from the font: ὐ |                       |
|   The following auxiliary characters are missing from the font: ὔ |                       |
|   The following auxiliary characters are missing from the font: ὒ |                       |
|   The following auxiliary characters are missing from the font: ὖ |                       |
|   The following auxiliary characters are missing from the font: ὑ |                       |
|   The following auxiliary characters are missing from the font: ὕ |                       |
|   The following auxiliary characters are missing from the font: ὓ |                       |
|   The following auxiliary characters are missing from the font: ὗ |                       |
|   The following auxiliary characters are missing from the font: ὺ |                       |
|   The following auxiliary characters are missing from the font: ῦ |                       |
|   The following auxiliary characters are missing from the font: ῢ |                       |
|   The following auxiliary characters are missing from the font: ῧ |                       |
|   The following auxiliary characters are missing from the font: ὤ |                       |
|   The following auxiliary characters are missing from the font: ὢ |                       |
|   The following auxiliary characters are missing from the font: ὦ |                       |
|   The following auxiliary characters are missing from the font: ὥ |                       |
|   The following auxiliary characters are missing from the font: ὣ |                       |
|   The following auxiliary characters are missing from the font: ὧ |                       |
|   The following auxiliary characters are missing from the font: ὼ |                       |
|   The following auxiliary characters are missing from the font: ῶ |                       | [code: warning-language-shaping]



</div>
</details>


</div>
</details>


<details><summary>[3] dindot/DINDOT-MediumItalic.ttf</summary>
<div>


<details>
    <summary>🔥 <b>FAIL</b> Check family name for GF Guide compliance. (googlefonts/family_name_compliance)</summary>
    <div>


> Checks the family name for compliance with the Google Fonts Guide. https://googlefonts.github.io/gf-guide/onboarding.html#new-fonts
>
> If you want to have your family name added to the CamelCase exceptions list, please submit a pull request to the camelcased_familyname_exceptions.txt file.
>
> Similarly, abbreviations can be submitted to the abbreviations_familyname_exceptions.txt file.
>
> These are located in the Lib/fontbakery/data/googlefonts/ directory of the FontBakery source code currently hosted at https://github.com/fonttools/fontbakery/




Original proposal: [https://github.com/fonttools/fontbakery/issues/4049]





- 🔥 **FAIL** "DINDOT" contains an abbreviation. [code: abbreviation]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check if each glyph has the recommended amount of contours. (contour_count)</summary>
    <div>


> Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only be constructured in a handful of ways. This means a glyph's contour count will only differ slightly amongst different fonts, e.g a 'g' could either be 2 or 3 contours, depending on whether its double story or single story.
>
> However, a quotedbl should have 2 contours, unless the font belongs to a display family.
>
> This check currently does not cover variable fonts because there's plenty of alternative ways of constructing glyphs with multiple outlines for each feature in a VarFont. The expected contour count data for this check is currently optimized for the typical construction of glyphs in static fonts.




Original proposal: [https://github.com/fonttools/fontbakery/issues/4829]





- ⚠️ **WARN** This check inspects the glyph outlines and detects the total number of contours in each of them. The expected values are
     inferred from the typical amounts of contours observed in a
     large collection of reference font families. The divergences
     listed below may simply indicate a significantly different
     design on some of your glyphs. On the other hand, some of these
     may flag actual bugs in the font such as glyphs mapped to an
     incorrect codepoint. Please consider reviewing the design and
     codepoint assignment of these to make sure they are correct.


    The following glyphs do not have the recommended number of contours:
* zero.osf (unencoded): found 3, expected one of: [2]
* zero.tlf (unencoded): found 3, expected one of: [2]
* zero.tosf (unencoded): found 3, expected one of: [2]
* uni2152 (U+2152): found 6, expected one of: [5, 10] [code: contour-count]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Shapes languages in all GF glyphsets. (googlefonts/glyphsets/shape_languages)</summary>
    <div>


> This check uses a heuristic to determine which GF glyphsets a font supports. Then it checks the font for correct shaping behaviour for all languages in those glyphsets.




Original proposal: [https://github.com/googlefonts/fontbakery/issues/4147]





- ⚠️ **WARN** Warning language shaping:

| Message                                                           | Languages             |
|-------------------------------------------------------------------|-----------------------|
| Auxiliary orthography codepoints:                                 | * de_Latn (German)    |
|   The following auxiliary characters are missing from the font: ſ | * fr_Latn (French)    |
| Auxiliary orthography codepoints:                                 | * mn_Cyrl (Mongolian) |
|   The following auxiliary characters are missing from the font: ӊ |                       |
| Auxiliary orthography codepoints:                                 | * ca_Latn (Catalan)   |
|   The following auxiliary characters are missing from the font: Ŀ |                       |
|   The following auxiliary characters are missing from the font: ŀ |                       |
| Auxiliary orthography codepoints:                                 | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѣ | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѫ |                       |
| Auxiliary orthography codepoints:                                 | * el_Grek (Greek)     |
|   The following auxiliary characters are missing from the font: ἀ |                       |
|   The following auxiliary characters are missing from the font: ἄ |                       |
|   The following auxiliary characters are missing from the font: ἂ |                       |
|   The following auxiliary characters are missing from the font: ἆ |                       |
|   The following auxiliary characters are missing from the font: ἁ |                       |
|   The following auxiliary characters are missing from the font: ἅ |                       |
|   The following auxiliary characters are missing from the font: ἃ |                       |
|   The following auxiliary characters are missing from the font: ἇ |                       |
|   The following auxiliary characters are missing from the font: ὰ |                       |
|   The following auxiliary characters are missing from the font: ᾶ |                       |
|   The following auxiliary characters are missing from the font: ἐ |                       |
|   The following auxiliary characters are missing from the font: ἔ |                       |
|   The following auxiliary characters are missing from the font: ἒ |                       |
|   The following auxiliary characters are missing from the font: ἑ |                       |
|   The following auxiliary characters are missing from the font: ἕ |                       |
|   The following auxiliary characters are missing from the font: ἓ |                       |
|   The following auxiliary characters are missing from the font: ὲ |                       |
|   The following auxiliary characters are missing from the font: ἠ |                       |
|   The following auxiliary characters are missing from the font: ἤ |                       |
|   The following auxiliary characters are missing from the font: ἢ |                       |
|   The following auxiliary characters are missing from the font: ἦ |                       |
|   The following auxiliary characters are missing from the font: ἡ |                       |
|   The following auxiliary characters are missing from the font: ἥ |                       |
|   The following auxiliary characters are missing from the font: ἣ |                       |
|   The following auxiliary characters are missing from the font: ἧ |                       |
|   The following auxiliary characters are missing from the font: ὴ |                       |
|   The following auxiliary characters are missing from the font: ῆ |                       |
|   The following auxiliary characters are missing from the font: ἰ |                       |
|   The following auxiliary characters are missing from the font: ἴ |                       |
|   The following auxiliary characters are missing from the font: ἲ |                       |
|   The following auxiliary characters are missing from the font: ἶ |                       |
|   The following auxiliary characters are missing from the font: ἱ |                       |
|   The following auxiliary characters are missing from the font: ἵ |                       |
|   The following auxiliary characters are missing from the font: ἳ |                       |
|   The following auxiliary characters are missing from the font: ἷ |                       |
|   The following auxiliary characters are missing from the font: ὶ |                       |
|   The following auxiliary characters are missing from the font: ῖ |                       |
|   The following auxiliary characters are missing from the font: ῒ |                       |
|   The following auxiliary characters are missing from the font: ῗ |                       |
|   The following auxiliary characters are missing from the font: ὄ |                       |
|   The following auxiliary characters are missing from the font: ὂ |                       |
|   The following auxiliary characters are missing from the font: ὃ |                       |
|   The following auxiliary characters are missing from the font: ὸ |                       |
|   The following auxiliary characters are missing from the font: ὐ |                       |
|   The following auxiliary characters are missing from the font: ὔ |                       |
|   The following auxiliary characters are missing from the font: ὒ |                       |
|   The following auxiliary characters are missing from the font: ὖ |                       |
|   The following auxiliary characters are missing from the font: ὑ |                       |
|   The following auxiliary characters are missing from the font: ὕ |                       |
|   The following auxiliary characters are missing from the font: ὓ |                       |
|   The following auxiliary characters are missing from the font: ὗ |                       |
|   The following auxiliary characters are missing from the font: ὺ |                       |
|   The following auxiliary characters are missing from the font: ῦ |                       |
|   The following auxiliary characters are missing from the font: ῢ |                       |
|   The following auxiliary characters are missing from the font: ῧ |                       |
|   The following auxiliary characters are missing from the font: ὤ |                       |
|   The following auxiliary characters are missing from the font: ὢ |                       |
|   The following auxiliary characters are missing from the font: ὦ |                       |
|   The following auxiliary characters are missing from the font: ὥ |                       |
|   The following auxiliary characters are missing from the font: ὣ |                       |
|   The following auxiliary characters are missing from the font: ὧ |                       |
|   The following auxiliary characters are missing from the font: ὼ |                       |
|   The following auxiliary characters are missing from the font: ῶ |                       |
| Auxiliary orthography codepoints:                                 | * en_Latn (English)   |
|   The following auxiliary characters are missing from the font: ʻ |                       |
| Auxiliary orthography codepoints:                                 | * fi_Latn (Finnish)   |
|   The following auxiliary characters are missing from the font: Ǥ |                       |
|   The following auxiliary characters are missing from the font: Ȟ |                       |
|   The following auxiliary characters are missing from the font: Ʒ |                       |
|   The following auxiliary characters are missing from the font: Ǯ |                       |
|   The following auxiliary characters are missing from the font: ǥ |                       |
|   The following auxiliary characters are missing from the font: ȟ |                       |
|   The following auxiliary characters are missing from the font: ʒ |                       |
|   The following auxiliary characters are missing from the font: ǯ |                       | [code: warning-language-shaping]



</div>
</details>


</div>
</details>


<details><summary>[3] dindot/DINDOT-Medium.ttf</summary>
<div>


<details>
    <summary>🔥 <b>FAIL</b> Check family name for GF Guide compliance. (googlefonts/family_name_compliance)</summary>
    <div>


> Checks the family name for compliance with the Google Fonts Guide. https://googlefonts.github.io/gf-guide/onboarding.html#new-fonts
>
> If you want to have your family name added to the CamelCase exceptions list, please submit a pull request to the camelcased_familyname_exceptions.txt file.
>
> Similarly, abbreviations can be submitted to the abbreviations_familyname_exceptions.txt file.
>
> These are located in the Lib/fontbakery/data/googlefonts/ directory of the FontBakery source code currently hosted at https://github.com/fonttools/fontbakery/




Original proposal: [https://github.com/fonttools/fontbakery/issues/4049]





- 🔥 **FAIL** "DINDOT" contains an abbreviation. [code: abbreviation]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check if each glyph has the recommended amount of contours. (contour_count)</summary>
    <div>


> Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only be constructured in a handful of ways. This means a glyph's contour count will only differ slightly amongst different fonts, e.g a 'g' could either be 2 or 3 contours, depending on whether its double story or single story.
>
> However, a quotedbl should have 2 contours, unless the font belongs to a display family.
>
> This check currently does not cover variable fonts because there's plenty of alternative ways of constructing glyphs with multiple outlines for each feature in a VarFont. The expected contour count data for this check is currently optimized for the typical construction of glyphs in static fonts.




Original proposal: [https://github.com/fonttools/fontbakery/issues/4829]





- ⚠️ **WARN** This check inspects the glyph outlines and detects the total number of contours in each of them. The expected values are
     inferred from the typical amounts of contours observed in a
     large collection of reference font families. The divergences
     listed below may simply indicate a significantly different
     design on some of your glyphs. On the other hand, some of these
     may flag actual bugs in the font such as glyphs mapped to an
     incorrect codepoint. Please consider reviewing the design and
     codepoint assignment of these to make sure they are correct.


    The following glyphs do not have the recommended number of contours:
* zero.osf (unencoded): found 3, expected one of: [2]
* zero.tlf (unencoded): found 3, expected one of: [2]
* zero.tosf (unencoded): found 3, expected one of: [2]
* uni2152 (U+2152): found 6, expected one of: [5, 10] [code: contour-count]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Shapes languages in all GF glyphsets. (googlefonts/glyphsets/shape_languages)</summary>
    <div>


> This check uses a heuristic to determine which GF glyphsets a font supports. Then it checks the font for correct shaping behaviour for all languages in those glyphsets.




Original proposal: [https://github.com/googlefonts/fontbakery/issues/4147]





- ⚠️ **WARN** Warning language shaping:

| Message                                                           | Languages             |
|-------------------------------------------------------------------|-----------------------|
| Auxiliary orthography codepoints:                                 | * mn_Cyrl (Mongolian) |
|   The following auxiliary characters are missing from the font: ӊ |                       |
| Auxiliary orthography codepoints:                                 | * ca_Latn (Catalan)   |
|   The following auxiliary characters are missing from the font: Ŀ |                       |
|   The following auxiliary characters are missing from the font: ŀ |                       |
| Auxiliary orthography codepoints:                                 | * en_Latn (English)   |
|   The following auxiliary characters are missing from the font: ʻ |                       |
| Auxiliary orthography codepoints:                                 | * el_Grek (Greek)     |
|   The following auxiliary characters are missing from the font: ἀ |                       |
|   The following auxiliary characters are missing from the font: ἄ |                       |
|   The following auxiliary characters are missing from the font: ἂ |                       |
|   The following auxiliary characters are missing from the font: ἆ |                       |
|   The following auxiliary characters are missing from the font: ἁ |                       |
|   The following auxiliary characters are missing from the font: ἅ |                       |
|   The following auxiliary characters are missing from the font: ἃ |                       |
|   The following auxiliary characters are missing from the font: ἇ |                       |
|   The following auxiliary characters are missing from the font: ὰ |                       |
|   The following auxiliary characters are missing from the font: ᾶ |                       |
|   The following auxiliary characters are missing from the font: ἐ |                       |
|   The following auxiliary characters are missing from the font: ἔ |                       |
|   The following auxiliary characters are missing from the font: ἒ |                       |
|   The following auxiliary characters are missing from the font: ἑ |                       |
|   The following auxiliary characters are missing from the font: ἕ |                       |
|   The following auxiliary characters are missing from the font: ἓ |                       |
|   The following auxiliary characters are missing from the font: ὲ |                       |
|   The following auxiliary characters are missing from the font: ἠ |                       |
|   The following auxiliary characters are missing from the font: ἤ |                       |
|   The following auxiliary characters are missing from the font: ἢ |                       |
|   The following auxiliary characters are missing from the font: ἦ |                       |
|   The following auxiliary characters are missing from the font: ἡ |                       |
|   The following auxiliary characters are missing from the font: ἥ |                       |
|   The following auxiliary characters are missing from the font: ἣ |                       |
|   The following auxiliary characters are missing from the font: ἧ |                       |
|   The following auxiliary characters are missing from the font: ὴ |                       |
|   The following auxiliary characters are missing from the font: ῆ |                       |
|   The following auxiliary characters are missing from the font: ἰ |                       |
|   The following auxiliary characters are missing from the font: ἴ |                       |
|   The following auxiliary characters are missing from the font: ἲ |                       |
|   The following auxiliary characters are missing from the font: ἶ |                       |
|   The following auxiliary characters are missing from the font: ἱ |                       |
|   The following auxiliary characters are missing from the font: ἵ |                       |
|   The following auxiliary characters are missing from the font: ἳ |                       |
|   The following auxiliary characters are missing from the font: ἷ |                       |
|   The following auxiliary characters are missing from the font: ὶ |                       |
|   The following auxiliary characters are missing from the font: ῖ |                       |
|   The following auxiliary characters are missing from the font: ῒ |                       |
|   The following auxiliary characters are missing from the font: ῗ |                       |
|   The following auxiliary characters are missing from the font: ὄ |                       |
|   The following auxiliary characters are missing from the font: ὂ |                       |
|   The following auxiliary characters are missing from the font: ὃ |                       |
|   The following auxiliary characters are missing from the font: ὸ |                       |
|   The following auxiliary characters are missing from the font: ὐ |                       |
|   The following auxiliary characters are missing from the font: ὔ |                       |
|   The following auxiliary characters are missing from the font: ὒ |                       |
|   The following auxiliary characters are missing from the font: ὖ |                       |
|   The following auxiliary characters are missing from the font: ὑ |                       |
|   The following auxiliary characters are missing from the font: ὕ |                       |
|   The following auxiliary characters are missing from the font: ὓ |                       |
|   The following auxiliary characters are missing from the font: ὗ |                       |
|   The following auxiliary characters are missing from the font: ὺ |                       |
|   The following auxiliary characters are missing from the font: ῦ |                       |
|   The following auxiliary characters are missing from the font: ῢ |                       |
|   The following auxiliary characters are missing from the font: ῧ |                       |
|   The following auxiliary characters are missing from the font: ὤ |                       |
|   The following auxiliary characters are missing from the font: ὢ |                       |
|   The following auxiliary characters are missing from the font: ὦ |                       |
|   The following auxiliary characters are missing from the font: ὥ |                       |
|   The following auxiliary characters are missing from the font: ὣ |                       |
|   The following auxiliary characters are missing from the font: ὧ |                       |
|   The following auxiliary characters are missing from the font: ὼ |                       |
|   The following auxiliary characters are missing from the font: ῶ |                       |
| Auxiliary orthography codepoints:                                 | * de_Latn (German)    |
|   The following auxiliary characters are missing from the font: ſ | * fr_Latn (French)    |
| Auxiliary orthography codepoints:                                 | * fi_Latn (Finnish)   |
|   The following auxiliary characters are missing from the font: Ǥ |                       |
|   The following auxiliary characters are missing from the font: Ȟ |                       |
|   The following auxiliary characters are missing from the font: Ʒ |                       |
|   The following auxiliary characters are missing from the font: Ǯ |                       |
|   The following auxiliary characters are missing from the font: ǥ |                       |
|   The following auxiliary characters are missing from the font: ȟ |                       |
|   The following auxiliary characters are missing from the font: ʒ |                       |
|   The following auxiliary characters are missing from the font: ǯ |                       |
| Auxiliary orthography codepoints:                                 | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѣ | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѫ |                       | [code: warning-language-shaping]



</div>
</details>


</div>
</details>


<details><summary>[3] dindot/DINDOT-Italic.ttf</summary>
<div>


<details>
    <summary>🔥 <b>FAIL</b> Check family name for GF Guide compliance. (googlefonts/family_name_compliance)</summary>
    <div>


> Checks the family name for compliance with the Google Fonts Guide. https://googlefonts.github.io/gf-guide/onboarding.html#new-fonts
>
> If you want to have your family name added to the CamelCase exceptions list, please submit a pull request to the camelcased_familyname_exceptions.txt file.
>
> Similarly, abbreviations can be submitted to the abbreviations_familyname_exceptions.txt file.
>
> These are located in the Lib/fontbakery/data/googlefonts/ directory of the FontBakery source code currently hosted at https://github.com/fonttools/fontbakery/




Original proposal: [https://github.com/fonttools/fontbakery/issues/4049]





- 🔥 **FAIL** "DINDOT" contains an abbreviation. [code: abbreviation]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check if each glyph has the recommended amount of contours. (contour_count)</summary>
    <div>


> Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only be constructured in a handful of ways. This means a glyph's contour count will only differ slightly amongst different fonts, e.g a 'g' could either be 2 or 3 contours, depending on whether its double story or single story.
>
> However, a quotedbl should have 2 contours, unless the font belongs to a display family.
>
> This check currently does not cover variable fonts because there's plenty of alternative ways of constructing glyphs with multiple outlines for each feature in a VarFont. The expected contour count data for this check is currently optimized for the typical construction of glyphs in static fonts.




Original proposal: [https://github.com/fonttools/fontbakery/issues/4829]





- ⚠️ **WARN** This check inspects the glyph outlines and detects the total number of contours in each of them. The expected values are
     inferred from the typical amounts of contours observed in a
     large collection of reference font families. The divergences
     listed below may simply indicate a significantly different
     design on some of your glyphs. On the other hand, some of these
     may flag actual bugs in the font such as glyphs mapped to an
     incorrect codepoint. Please consider reviewing the design and
     codepoint assignment of these to make sure they are correct.


    The following glyphs do not have the recommended number of contours:
* zero.osf (unencoded): found 3, expected one of: [2]
* zero.tlf (unencoded): found 3, expected one of: [2]
* zero.tosf (unencoded): found 3, expected one of: [2]
* uni2152 (U+2152): found 6, expected one of: [5, 10] [code: contour-count]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Shapes languages in all GF glyphsets. (googlefonts/glyphsets/shape_languages)</summary>
    <div>


> This check uses a heuristic to determine which GF glyphsets a font supports. Then it checks the font for correct shaping behaviour for all languages in those glyphsets.




Original proposal: [https://github.com/googlefonts/fontbakery/issues/4147]





- ⚠️ **WARN** Warning language shaping:

| Message                                                           | Languages             |
|-------------------------------------------------------------------|-----------------------|
| Auxiliary orthography codepoints:                                 | * ca_Latn (Catalan)   |
|   The following auxiliary characters are missing from the font: Ŀ |                       |
|   The following auxiliary characters are missing from the font: ŀ |                       |
| Auxiliary orthography codepoints:                                 | * de_Latn (German)    |
|   The following auxiliary characters are missing from the font: ſ | * fr_Latn (French)    |
| Auxiliary orthography codepoints:                                 | * el_Grek (Greek)     |
|   The following auxiliary characters are missing from the font: ἀ |                       |
|   The following auxiliary characters are missing from the font: ἄ |                       |
|   The following auxiliary characters are missing from the font: ἂ |                       |
|   The following auxiliary characters are missing from the font: ἆ |                       |
|   The following auxiliary characters are missing from the font: ἁ |                       |
|   The following auxiliary characters are missing from the font: ἅ |                       |
|   The following auxiliary characters are missing from the font: ἃ |                       |
|   The following auxiliary characters are missing from the font: ἇ |                       |
|   The following auxiliary characters are missing from the font: ὰ |                       |
|   The following auxiliary characters are missing from the font: ᾶ |                       |
|   The following auxiliary characters are missing from the font: ἐ |                       |
|   The following auxiliary characters are missing from the font: ἔ |                       |
|   The following auxiliary characters are missing from the font: ἒ |                       |
|   The following auxiliary characters are missing from the font: ἑ |                       |
|   The following auxiliary characters are missing from the font: ἕ |                       |
|   The following auxiliary characters are missing from the font: ἓ |                       |
|   The following auxiliary characters are missing from the font: ὲ |                       |
|   The following auxiliary characters are missing from the font: ἠ |                       |
|   The following auxiliary characters are missing from the font: ἤ |                       |
|   The following auxiliary characters are missing from the font: ἢ |                       |
|   The following auxiliary characters are missing from the font: ἦ |                       |
|   The following auxiliary characters are missing from the font: ἡ |                       |
|   The following auxiliary characters are missing from the font: ἥ |                       |
|   The following auxiliary characters are missing from the font: ἣ |                       |
|   The following auxiliary characters are missing from the font: ἧ |                       |
|   The following auxiliary characters are missing from the font: ὴ |                       |
|   The following auxiliary characters are missing from the font: ῆ |                       |
|   The following auxiliary characters are missing from the font: ἰ |                       |
|   The following auxiliary characters are missing from the font: ἴ |                       |
|   The following auxiliary characters are missing from the font: ἲ |                       |
|   The following auxiliary characters are missing from the font: ἶ |                       |
|   The following auxiliary characters are missing from the font: ἱ |                       |
|   The following auxiliary characters are missing from the font: ἵ |                       |
|   The following auxiliary characters are missing from the font: ἳ |                       |
|   The following auxiliary characters are missing from the font: ἷ |                       |
|   The following auxiliary characters are missing from the font: ὶ |                       |
|   The following auxiliary characters are missing from the font: ῖ |                       |
|   The following auxiliary characters are missing from the font: ῒ |                       |
|   The following auxiliary characters are missing from the font: ῗ |                       |
|   The following auxiliary characters are missing from the font: ὄ |                       |
|   The following auxiliary characters are missing from the font: ὂ |                       |
|   The following auxiliary characters are missing from the font: ὃ |                       |
|   The following auxiliary characters are missing from the font: ὸ |                       |
|   The following auxiliary characters are missing from the font: ὐ |                       |
|   The following auxiliary characters are missing from the font: ὔ |                       |
|   The following auxiliary characters are missing from the font: ὒ |                       |
|   The following auxiliary characters are missing from the font: ὖ |                       |
|   The following auxiliary characters are missing from the font: ὑ |                       |
|   The following auxiliary characters are missing from the font: ὕ |                       |
|   The following auxiliary characters are missing from the font: ὓ |                       |
|   The following auxiliary characters are missing from the font: ὗ |                       |
|   The following auxiliary characters are missing from the font: ὺ |                       |
|   The following auxiliary characters are missing from the font: ῦ |                       |
|   The following auxiliary characters are missing from the font: ῢ |                       |
|   The following auxiliary characters are missing from the font: ῧ |                       |
|   The following auxiliary characters are missing from the font: ὤ |                       |
|   The following auxiliary characters are missing from the font: ὢ |                       |
|   The following auxiliary characters are missing from the font: ὦ |                       |
|   The following auxiliary characters are missing from the font: ὥ |                       |
|   The following auxiliary characters are missing from the font: ὣ |                       |
|   The following auxiliary characters are missing from the font: ὧ |                       |
|   The following auxiliary characters are missing from the font: ὼ |                       |
|   The following auxiliary characters are missing from the font: ῶ |                       |
| Auxiliary orthography codepoints:                                 | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѣ | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѫ |                       |
| Auxiliary orthography codepoints:                                 | * mn_Cyrl (Mongolian) |
|   The following auxiliary characters are missing from the font: ӊ |                       |
| Auxiliary orthography codepoints:                                 | * en_Latn (English)   |
|   The following auxiliary characters are missing from the font: ʻ |                       |
| Auxiliary orthography codepoints:                                 | * fi_Latn (Finnish)   |
|   The following auxiliary characters are missing from the font: Ǥ |                       |
|   The following auxiliary characters are missing from the font: Ȟ |                       |
|   The following auxiliary characters are missing from the font: Ʒ |                       |
|   The following auxiliary characters are missing from the font: Ǯ |                       |
|   The following auxiliary characters are missing from the font: ǥ |                       |
|   The following auxiliary characters are missing from the font: ȟ |                       |
|   The following auxiliary characters are missing from the font: ʒ |                       |
|   The following auxiliary characters are missing from the font: ǯ |                       | [code: warning-language-shaping]



</div>
</details>


</div>
</details>






### Summary

| 🔥 FAIL | ⚠️ WARN | ℹ️ INFO | ✅ PASS | ⏩ SKIP |
| ---|---|---|---|---|
| 8 | 24 | 94 | 823 | 453 |
| 1% | 2% | 7% | 59% | 32% |
