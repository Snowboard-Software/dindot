## FontSpector report

fontspector version: 1.9.0






## Check results




<details><summary>[10] dindot/DINDOT-SemiBold.ttf</summary>
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
    <summary>⚠️ <b>WARN</b> Check accent of Lcaron, dcaron, lcaron, tcaron (alt_caron)</summary>
    <div>


> Lcaron, dcaron, lcaron, tcaron should NOT be composed with quoteright or quotesingle or comma or caron(comb). It should be composed with a distinctive glyph which doesn't look like an apostrophe.
>
> Source: https://ilovetypography.com/2009/01/24/on-diacritics/ http://diacritics.typo.cz/index.php?id=5 https://www.typotheque.com/articles/lcaron




Original proposal: [https://github.com/fonttools/fontbakery/issues/3308]





- ⚠️ **WARN** Lcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** dcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** lcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** tcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]



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
    <summary>⚠️ <b>WARN</b> Check math signs have the same width. (math_signs_width)</summary>
    <div>


> #,         It is a common practice to have math signs sharing the same width         (preferably the same width as tabular figures accross the entire font family).
>
> This probably comes from the will to avoid additional tabular math signs knowing that their design can easily share the same width.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3832]





- ⚠️ **WARN** The most common width is 1070 among a set of 27  math glyphs.
The following math glyphs have a different width, though:
width=1440: uni221D [code: width-outliers]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Does the font contain a soft hyphen? (soft_hyphen)</summary>
    <div>


> The 'Soft Hyphen' character (codepoint 0x00AD) is used to mark a hyphenation possibility within a word in the absence of or overriding dictionary hyphenation.
>
> It is sometimes designed empty with no width (such as a control character), sometimes the same as the traditional hyphen, sometimes double encoded with the hyphen.
>
> That being said, it is recommended to not include it in the font at all, because discretionary hyphenation should be handled at the level of the shaping engine, not the font. Also, even if present, the software would not display that character.
>
> More discussion at: https://typedrawers.com/discussion/2046/special-dash-things-softhyphen-horizontalbar




Original proposal: [https://github.com/fonttools/fontbakery/issues/4046, https://github.com/fonttools/fontbakery/issues/3486]





- ⚠️ **WARN** This font has a 'Soft Hyphen' character. [code: softhyphen]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check font contains no unreachable glyphs (unreachable_glyphs)</summary>
    <div>


> Glyphs are either accessible directly through Unicode codepoints or through        substitution rules.
>
> In Color Fonts, glyphs are also referenced by the COLR table. And mathematical fonts also reference glyphs via the MATH table.
>
> Any glyphs not accessible by these means are redundant and serve only to increase the font's file size.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3160]





- ⚠️ **WARN** The following glyphs could not be reached by codepoint or substitution rules:

* acutecomb.loclPLK
* caroncmb.alt
* tonoscomb
* dieresistonoscomb
* circumflexcmb.case
* brevecmb.case
* hookabovecomb.case [code: unreachable-glyphs]



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
| Auxiliary orthography codepoints:                                 | * en_Latn (English)   |
|   The following auxiliary characters are missing from the font: ʻ |                       |
| Auxiliary orthography codepoints:                                 | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѣ | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѫ |                       |
| Auxiliary orthography codepoints:                                 | * mn_Cyrl (Mongolian) |
|   The following auxiliary characters are missing from the font: ӊ |                       |
| Auxiliary orthography codepoints:                                 | * ca_Latn (Catalan)   |
|   The following auxiliary characters are missing from the font: Ŀ |                       |
|   The following auxiliary characters are missing from the font: ŀ |                       |
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
|   The following auxiliary characters are missing from the font: ǯ |                       | [code: warning-language-shaping]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Do any segments have colinear vectors? (outline_colinear_vectors)</summary>
    <div>


> This check looks for consecutive line segments which have the same angle. This normally happens if an outline point has been added by accident.
>
> This check is not run for variable fonts, as they may legitimately have colinear vectors.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have colinear vectors:

* P (U+0050): from (665.0, 552.0) to (664.0, 552.0) is colinear with segment from (664.0, 552.0) to (398.0, 552.0)
* f (U+0066): from (473.0, 1414.0) to (474.0, 1414.0) is colinear with segment from (474.0, 1414.0) to (551.0, 1414.0)
* t_t: from (1207.0, 0.0) to (1151.0, 0.0) is colinear with segment from (1151.0, 0.0) to (1150.0, 0.0)
* ordfeminine (U+00AA): from (303.0, 1264.0) to (304.0, 1264.0) is colinear with segment from (304.0, 1264.0) to (409.0, 1264.0)
* Thorn (U+00DE): from (657.0, 312.0) to (656.0, 312.0) is colinear with segment from (656.0, 312.0) to (398.0, 312.0)
* ae (U+00E6): from (445.0, 616.0) to (446.0, 616.0) is colinear with segment from (446.0, 616.0) to (661.0, 616.0)
* Eng (U+014A): from (891.0, -346.0) to (890.0, -346.0) is colinear with segment from (890.0, -346.0) to (838.0, -346.0)
* eng (U+014B): from (649.0, -346.0) to (647.0, -346.0) is colinear with segment from (647.0, -346.0) to (595.0, -346.0)
* florin (U+0192): from (746.0, 1414.0) to (747.0, 1414.0) is colinear with segment from (747.0, 1414.0) to (779.0, 1414.0)
... and 45 others [code: found-colinear-vectors]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check there are no overlapping path segments (overlapping_path_segments)</summary>
    <div>


> Some rasterizers encounter difficulties when rendering glyphs with overlapping path segments.
>
> A path segment is a section of a path defined by two on-curve points. When two segments share the same coordinates, they are considered overlapping.




Original proposal: [https://github.com/google/fonts/issues/7594#issuecomment-2401909084]





- ⚠️ **WARN** The following glyphs have overlapping path segments:

* epsilontonos (U+03AD): Line(Line { p0: (579.0, 623.0), p1: (579.0, 623.0) }) has the same coordinates as a previous segment.
* epsilontonos (U+03AD): Quad(QuadBez { p0: (578.0, 451.0), p1: (578.0, 451.0), p2: (578.0, 451.0) }) has the same coordinates as a previous segment.
* epsilontonos (U+03AD): Quad(QuadBez { p0: (868.0, 715.0), p1: (868.0, 715.0), p2: (868.0, 715.0) }) has the same coordinates as a previous segment.
* uni0398 (U+0398): Line(Line { p0: (800.0, 597.0), p1: (800.0, 597.0) }) has the same coordinates as a previous segment.
* uni03B2 (U+03B2): Line(Line { p0: (178.0, 1414.0), p1: (178.0, 1414.0) }) has the same coordinates as a previous segment.
* uni03B2 (U+03B2): Line(Line { p0: (271.0, -410.0), p1: (271.0, -410.0) }) has the same coordinates as a previous segment.
* uni03B5 (U+03B5): Quad(QuadBez { p0: (580.0, 451.0), p1: (580.0, 451.0), p2: (580.0, 451.0) }) has the same coordinates as a previous segment.
* uni03B5 (U+03B5): Quad(QuadBez { p0: (771.0, 328.0), p1: (771.0, 328.0), p2: (771.0, 328.0) }) has the same coordinates as a previous segment.
* uni03D5 (U+03D5): Line(Line { p0: (479.0, 1414.0), p1: (479.0, 1414.0) }) has the same coordinates as a previous segment.
... and 2 others [code: overlapping-path-segments]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
>
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* a.ss02: Line(Line { p0: (922.0, 996.0), p1: (920.0, 56.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* agrave.ss02: Line(Line { p0: (922.0, 996.0), p1: (920.0, 56.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* aacute.ss02: Line(Line { p0: (922.0, 996.0), p1: (920.0, 56.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* acircumflex.ss02: Line(Line { p0: (922.0, 996.0), p1: (920.0, 56.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* atilde.ss02: Line(Line { p0: (922.0, 996.0), p1: (920.0, 56.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* adieresis.ss02: Line(Line { p0: (922.0, 996.0), p1: (920.0, 56.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* aring.ss02: Line(Line { p0: (922.0, 996.0), p1: (920.0, 56.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* amacron.ss02: Line(Line { p0: (922.0, 996.0), p1: (920.0, 56.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* abreve.ss02: Line(Line { p0: (922.0, 996.0), p1: (920.0, 56.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
... and 16 others [code: found-semi-vertical]



</div>
</details>


</div>
</details>


<details><summary>[7] dindot/DINDOT-BoldItalic.ttf</summary>
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
    <summary>⚠️ <b>WARN</b> Check accent of Lcaron, dcaron, lcaron, tcaron (alt_caron)</summary>
    <div>


> Lcaron, dcaron, lcaron, tcaron should NOT be composed with quoteright or quotesingle or comma or caron(comb). It should be composed with a distinctive glyph which doesn't look like an apostrophe.
>
> Source: https://ilovetypography.com/2009/01/24/on-diacritics/ http://diacritics.typo.cz/index.php?id=5 https://www.typotheque.com/articles/lcaron




Original proposal: [https://github.com/fonttools/fontbakery/issues/3308]





- ⚠️ **WARN** Lcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** dcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** lcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** tcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]



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
    <summary>⚠️ <b>WARN</b> Check math signs have the same width. (math_signs_width)</summary>
    <div>


> #,         It is a common practice to have math signs sharing the same width         (preferably the same width as tabular figures accross the entire font family).
>
> This probably comes from the will to avoid additional tabular math signs knowing that their design can easily share the same width.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3832]





- ⚠️ **WARN** The most common width is 1082 among a set of 27  math glyphs.
The following math glyphs have a different width, though:
width=1440: uni221D [code: width-outliers]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Does the font contain a soft hyphen? (soft_hyphen)</summary>
    <div>


> The 'Soft Hyphen' character (codepoint 0x00AD) is used to mark a hyphenation possibility within a word in the absence of or overriding dictionary hyphenation.
>
> It is sometimes designed empty with no width (such as a control character), sometimes the same as the traditional hyphen, sometimes double encoded with the hyphen.
>
> That being said, it is recommended to not include it in the font at all, because discretionary hyphenation should be handled at the level of the shaping engine, not the font. Also, even if present, the software would not display that character.
>
> More discussion at: https://typedrawers.com/discussion/2046/special-dash-things-softhyphen-horizontalbar




Original proposal: [https://github.com/fonttools/fontbakery/issues/4046, https://github.com/fonttools/fontbakery/issues/3486]





- ⚠️ **WARN** This font has a 'Soft Hyphen' character. [code: softhyphen]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check font contains no unreachable glyphs (unreachable_glyphs)</summary>
    <div>


> Glyphs are either accessible directly through Unicode codepoints or through        substitution rules.
>
> In Color Fonts, glyphs are also referenced by the COLR table. And mathematical fonts also reference glyphs via the MATH table.
>
> Any glyphs not accessible by these means are redundant and serve only to increase the font's file size.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3160]





- ⚠️ **WARN** The following glyphs could not be reached by codepoint or substitution rules:

* acutecomb.loclPLK
* caroncmb.alt
* tonoscomb
* dieresistonoscomb
* circumflexcmb.case
* brevecmb.case
* hookabovecomb.case [code: unreachable-glyphs]



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
|   The following auxiliary characters are missing from the font: ῶ |                       |
| Auxiliary orthography codepoints:                                 | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѣ | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѫ |                       |
| Auxiliary orthography codepoints:                                 | * en_Latn (English)   |
|   The following auxiliary characters are missing from the font: ʻ |                       |
| Auxiliary orthography codepoints:                                 | * ca_Latn (Catalan)   |
|   The following auxiliary characters are missing from the font: Ŀ |                       |
|   The following auxiliary characters are missing from the font: ŀ |                       |
| Auxiliary orthography codepoints:                                 | * mn_Cyrl (Mongolian) |
|   The following auxiliary characters are missing from the font: ӊ |                       | [code: warning-language-shaping]



</div>
</details>


</div>
</details>


<details><summary>[10] dindot/DINDOT-Bold.ttf</summary>
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
    <summary>⚠️ <b>WARN</b> Check accent of Lcaron, dcaron, lcaron, tcaron (alt_caron)</summary>
    <div>


> Lcaron, dcaron, lcaron, tcaron should NOT be composed with quoteright or quotesingle or comma or caron(comb). It should be composed with a distinctive glyph which doesn't look like an apostrophe.
>
> Source: https://ilovetypography.com/2009/01/24/on-diacritics/ http://diacritics.typo.cz/index.php?id=5 https://www.typotheque.com/articles/lcaron




Original proposal: [https://github.com/fonttools/fontbakery/issues/3308]





- ⚠️ **WARN** Lcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** dcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** lcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** tcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]



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
    <summary>⚠️ <b>WARN</b> Check math signs have the same width. (math_signs_width)</summary>
    <div>


> #,         It is a common practice to have math signs sharing the same width         (preferably the same width as tabular figures accross the entire font family).
>
> This probably comes from the will to avoid additional tabular math signs knowing that their design can easily share the same width.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3832]





- ⚠️ **WARN** The most common width is 1082 among a set of 27  math glyphs.
The following math glyphs have a different width, though:
width=1440: uni221D [code: width-outliers]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Does the font contain a soft hyphen? (soft_hyphen)</summary>
    <div>


> The 'Soft Hyphen' character (codepoint 0x00AD) is used to mark a hyphenation possibility within a word in the absence of or overriding dictionary hyphenation.
>
> It is sometimes designed empty with no width (such as a control character), sometimes the same as the traditional hyphen, sometimes double encoded with the hyphen.
>
> That being said, it is recommended to not include it in the font at all, because discretionary hyphenation should be handled at the level of the shaping engine, not the font. Also, even if present, the software would not display that character.
>
> More discussion at: https://typedrawers.com/discussion/2046/special-dash-things-softhyphen-horizontalbar




Original proposal: [https://github.com/fonttools/fontbakery/issues/4046, https://github.com/fonttools/fontbakery/issues/3486]





- ⚠️ **WARN** This font has a 'Soft Hyphen' character. [code: softhyphen]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check font contains no unreachable glyphs (unreachable_glyphs)</summary>
    <div>


> Glyphs are either accessible directly through Unicode codepoints or through        substitution rules.
>
> In Color Fonts, glyphs are also referenced by the COLR table. And mathematical fonts also reference glyphs via the MATH table.
>
> Any glyphs not accessible by these means are redundant and serve only to increase the font's file size.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3160]





- ⚠️ **WARN** The following glyphs could not be reached by codepoint or substitution rules:

* acutecomb.loclPLK
* caroncmb.alt
* tonoscomb
* dieresistonoscomb
* circumflexcmb.case
* brevecmb.case
* hookabovecomb.case [code: unreachable-glyphs]



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
| Auxiliary orthography codepoints:                                 | * de_Latn (German)    |
|   The following auxiliary characters are missing from the font: ſ | * fr_Latn (French)    |
| Auxiliary orthography codepoints:                                 | * en_Latn (English)   |
|   The following auxiliary characters are missing from the font: ʻ |                       | [code: warning-language-shaping]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Do any segments have colinear vectors? (outline_colinear_vectors)</summary>
    <div>


> This check looks for consecutive line segments which have the same angle. This normally happens if an outline point has been added by accident.
>
> This check is not run for variable fonts, as they may legitimately have colinear vectors.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have colinear vectors:

* uni2206 (U+2206): from (-20.0, 7.0) to (7.0, 78.0) is colinear with segment from (7.0, 78.0) to (509.0, 1429.0)
* uni2207 (U+2207): from (1102.0, 1233.0) to (1075.0, 1162.0) is colinear with segment from (1075.0, 1162.0) to (574.0, -188.0)
* uni0394 (U+0394): from (751.0, 278.0) to (752.0, 278.0) is colinear with segment from (752.0, 278.0) to (756.0, 278.0)
* uni0394 (U+0394): from (752.0, 278.0) to (756.0, 278.0) is colinear with segment from (756.0, 278.0) to (778.0, 278.0)
* uni0398 (U+0398): from (570.0, 578.0) to (569.0, 578.0) is colinear with segment from (569.0, 578.0) to (443.0, 578.0)
* uni0398 (U+0398): from (687.0, 835.0) to (688.0, 835.0) is colinear with segment from (688.0, 835.0) to (691.0, 835.0)
* uni0398 (U+0398): from (688.0, 835.0) to (691.0, 835.0) is colinear with segment from (691.0, 835.0) to (814.0, 835.0)
* uni039E (U+039E): from (848.0, 0.0) to (845.0, 0.0) is colinear with segment from (845.0, 0.0) to (842.0, 0.0)
* uni039E (U+039E): from (393.0, 0.0) to (390.0, 0.0) is colinear with segment from (390.0, 0.0) to (216.0, 0.0)
... and 12 others [code: found-colinear-vectors]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check there are no overlapping path segments (overlapping_path_segments)</summary>
    <div>


> Some rasterizers encounter difficulties when rendering glyphs with overlapping path segments.
>
> A path segment is a section of a path defined by two on-curve points. When two segments share the same coordinates, they are considered overlapping.




Original proposal: [https://github.com/google/fonts/issues/7594#issuecomment-2401909084]





- ⚠️ **WARN** The following glyphs have overlapping path segments:

* omegatonos (U+03CE): Quad(QuadBez { p0: (412.0, 269.0), p1: (412.0, 269.0), p2: (412.0, 269.0) }) has the same coordinates as a previous segment.
* uni03B2 (U+03B2): Quad(QuadBez { p0: (301.0, -410.0), p1: (301.0, -410.0), p2: (301.0, -410.0) }) has the same coordinates as a previous segment.
* uni03B2 (U+03B2): Quad(QuadBez { p0: (204.0, -410.0), p1: (204.0, -410.0), p2: (204.0, -410.0) }) has the same coordinates as a previous segment.
* uni03C0 (U+03C0): Line(Line { p0: (1107.0, 787.0), p1: (1107.0, 787.0) }) has the same coordinates as a previous segment.
* uni03C0 (U+03C0): Quad(QuadBez { p0: (1107.0, 787.0), p1: (1107.0, 787.0), p2: (1107.0, 787.0) }) has the same coordinates as a previous segment.
* uni03C9 (U+03C9): Line(Line { p0: (912.0, 277.0), p1: (912.0, 277.0) }) has the same coordinates as a previous segment. [code: overlapping-path-segments]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
>
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* a.ss02: Line(Line { p0: (941.0, 994.0), p1: (939.0, 64.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* agrave.ss02: Line(Line { p0: (941.0, 994.0), p1: (939.0, 64.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* aacute.ss02: Line(Line { p0: (941.0, 994.0), p1: (939.0, 64.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* acircumflex.ss02: Line(Line { p0: (941.0, 994.0), p1: (939.0, 64.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* atilde.ss02: Line(Line { p0: (941.0, 994.0), p1: (939.0, 64.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* adieresis.ss02: Line(Line { p0: (941.0, 994.0), p1: (939.0, 64.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* aring.ss02: Line(Line { p0: (941.0, 994.0), p1: (939.0, 64.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* amacron.ss02: Line(Line { p0: (941.0, 994.0), p1: (939.0, 64.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* abreve.ss02: Line(Line { p0: (941.0, 994.0), p1: (939.0, 64.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
... and 17 others [code: found-semi-vertical]



</div>
</details>


</div>
</details>


<details><summary>[7] dindot/DINDOT-Italic.ttf</summary>
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
    <summary>⚠️ <b>WARN</b> Check accent of Lcaron, dcaron, lcaron, tcaron (alt_caron)</summary>
    <div>


> Lcaron, dcaron, lcaron, tcaron should NOT be composed with quoteright or quotesingle or comma or caron(comb). It should be composed with a distinctive glyph which doesn't look like an apostrophe.
>
> Source: https://ilovetypography.com/2009/01/24/on-diacritics/ http://diacritics.typo.cz/index.php?id=5 https://www.typotheque.com/articles/lcaron




Original proposal: [https://github.com/fonttools/fontbakery/issues/3308]





- ⚠️ **WARN** Lcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** dcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** lcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** tcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]



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
    <summary>⚠️ <b>WARN</b> Check math signs have the same width. (math_signs_width)</summary>
    <div>


> #,         It is a common practice to have math signs sharing the same width         (preferably the same width as tabular figures accross the entire font family).
>
> This probably comes from the will to avoid additional tabular math signs knowing that their design can easily share the same width.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3832]





- ⚠️ **WARN** The most common width is 1048 among a set of 27  math glyphs.
The following math glyphs have a different width, though:
width=1440: uni221D [code: width-outliers]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Does the font contain a soft hyphen? (soft_hyphen)</summary>
    <div>


> The 'Soft Hyphen' character (codepoint 0x00AD) is used to mark a hyphenation possibility within a word in the absence of or overriding dictionary hyphenation.
>
> It is sometimes designed empty with no width (such as a control character), sometimes the same as the traditional hyphen, sometimes double encoded with the hyphen.
>
> That being said, it is recommended to not include it in the font at all, because discretionary hyphenation should be handled at the level of the shaping engine, not the font. Also, even if present, the software would not display that character.
>
> More discussion at: https://typedrawers.com/discussion/2046/special-dash-things-softhyphen-horizontalbar




Original proposal: [https://github.com/fonttools/fontbakery/issues/4046, https://github.com/fonttools/fontbakery/issues/3486]





- ⚠️ **WARN** This font has a 'Soft Hyphen' character. [code: softhyphen]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check font contains no unreachable glyphs (unreachable_glyphs)</summary>
    <div>


> Glyphs are either accessible directly through Unicode codepoints or through        substitution rules.
>
> In Color Fonts, glyphs are also referenced by the COLR table. And mathematical fonts also reference glyphs via the MATH table.
>
> Any glyphs not accessible by these means are redundant and serve only to increase the font's file size.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3160]





- ⚠️ **WARN** The following glyphs could not be reached by codepoint or substitution rules:

* acutecomb.loclPLK
* caroncmb.alt
* tonoscomb
* dieresistonoscomb
* circumflexcmb.case
* brevecmb.case
* hookabovecomb.case [code: unreachable-glyphs]



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
|   The following auxiliary characters are missing from the font: ǯ |                       |
| Auxiliary orthography codepoints:                                 | * mn_Cyrl (Mongolian) |
|   The following auxiliary characters are missing from the font: ӊ |                       | [code: warning-language-shaping]



</div>
</details>


</div>
</details>


<details><summary>[10] dindot/DINDOT-Regular.ttf</summary>
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
    <summary>⚠️ <b>WARN</b> Check accent of Lcaron, dcaron, lcaron, tcaron (alt_caron)</summary>
    <div>


> Lcaron, dcaron, lcaron, tcaron should NOT be composed with quoteright or quotesingle or comma or caron(comb). It should be composed with a distinctive glyph which doesn't look like an apostrophe.
>
> Source: https://ilovetypography.com/2009/01/24/on-diacritics/ http://diacritics.typo.cz/index.php?id=5 https://www.typotheque.com/articles/lcaron




Original proposal: [https://github.com/fonttools/fontbakery/issues/3308]





- ⚠️ **WARN** Lcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** dcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** lcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** tcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]



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
    <summary>⚠️ <b>WARN</b> Check math signs have the same width. (math_signs_width)</summary>
    <div>


> #,         It is a common practice to have math signs sharing the same width         (preferably the same width as tabular figures accross the entire font family).
>
> This probably comes from the will to avoid additional tabular math signs knowing that their design can easily share the same width.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3832]





- ⚠️ **WARN** The most common width is 1048 among a set of 27  math glyphs.
The following math glyphs have a different width, though:
width=1440: uni221D [code: width-outliers]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Does the font contain a soft hyphen? (soft_hyphen)</summary>
    <div>


> The 'Soft Hyphen' character (codepoint 0x00AD) is used to mark a hyphenation possibility within a word in the absence of or overriding dictionary hyphenation.
>
> It is sometimes designed empty with no width (such as a control character), sometimes the same as the traditional hyphen, sometimes double encoded with the hyphen.
>
> That being said, it is recommended to not include it in the font at all, because discretionary hyphenation should be handled at the level of the shaping engine, not the font. Also, even if present, the software would not display that character.
>
> More discussion at: https://typedrawers.com/discussion/2046/special-dash-things-softhyphen-horizontalbar




Original proposal: [https://github.com/fonttools/fontbakery/issues/4046, https://github.com/fonttools/fontbakery/issues/3486]





- ⚠️ **WARN** This font has a 'Soft Hyphen' character. [code: softhyphen]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check font contains no unreachable glyphs (unreachable_glyphs)</summary>
    <div>


> Glyphs are either accessible directly through Unicode codepoints or through        substitution rules.
>
> In Color Fonts, glyphs are also referenced by the COLR table. And mathematical fonts also reference glyphs via the MATH table.
>
> Any glyphs not accessible by these means are redundant and serve only to increase the font's file size.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3160]





- ⚠️ **WARN** The following glyphs could not be reached by codepoint or substitution rules:

* acutecomb.loclPLK
* caroncmb.alt
* tonoscomb
* dieresistonoscomb
* circumflexcmb.case
* brevecmb.case
* hookabovecomb.case [code: unreachable-glyphs]



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
| Auxiliary orthography codepoints:                                 | * de_Latn (German)    |
|   The following auxiliary characters are missing from the font: ſ | * fr_Latn (French)    |
| Auxiliary orthography codepoints:                                 | * en_Latn (English)   |
|   The following auxiliary characters are missing from the font: ʻ |                       |
| Auxiliary orthography codepoints:                                 | * mn_Cyrl (Mongolian) |
|   The following auxiliary characters are missing from the font: ӊ |                       |
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
| Auxiliary orthography codepoints:                                 | * ca_Latn (Catalan)   |
|   The following auxiliary characters are missing from the font: Ŀ |                       |
|   The following auxiliary characters are missing from the font: ŀ |                       | [code: warning-language-shaping]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Do any segments have colinear vectors? (outline_colinear_vectors)</summary>
    <div>


> This check looks for consecutive line segments which have the same angle. This normally happens if an outline point has been added by accident.
>
> This check is not run for variable fonts, as they may legitimately have colinear vectors.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have colinear vectors:

* aogonek (U+0105): from (453.0, 592.0) to (454.0, 592.0) is colinear with segment from (454.0, 592.0) to (717.0, 592.0)
* uni039B (U+039B): from (1036.0, 112.0) to (1001.0, 200.0) is colinear with segment from (1001.0, 200.0) to (761.0, 821.0)
* uni03B2 (U+03B2): from (212.0, 1414.0) to (556.0, 1414.0) is colinear with segment from (556.0, 1414.0) to (558.0, 1414.0)
* uni03B2 (U+03B2): from (556.0, 1414.0) to (558.0, 1414.0) is colinear with segment from (558.0, 1414.0) to (559.0, 1414.0)
* uni03B4 (U+03B4): from (691.0, 833.0) to (702.0, 830.0) is colinear with segment from (702.0, 830.0) to (713.0, 827.0)
* uni03B6 (U+03B6): from (649.0, 882.0) to (647.0, 882.0) is colinear with segment from (647.0, 882.0) to (643.0, 882.0)
* uni03B6 (U+03B6): from (478.0, 882.0) to (476.0, 882.0) is colinear with segment from (476.0, 882.0) to (246.0, 882.0)
* uni03B8 (U+03B8): from (550.0, 1290.0) to (549.0, 1290.0) is colinear with segment from (549.0, 1290.0) to (548.0, 1290.0)
* uni03C3 (U+03C3): from (528.0, 1038.0) to (529.0, 1038.0) is colinear with segment from (529.0, 1038.0) to (949.0, 1038.0)
... and 3 others [code: found-colinear-vectors]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check there are no overlapping path segments (overlapping_path_segments)</summary>
    <div>


> Some rasterizers encounter difficulties when rendering glyphs with overlapping path segments.
>
> A path segment is a section of a path defined by two on-curve points. When two segments share the same coordinates, they are considered overlapping.




Original proposal: [https://github.com/google/fonts/issues/7594#issuecomment-2401909084]





- ⚠️ **WARN** The following glyphs have overlapping path segments:

* eogonek (U+0119): Quad(QuadBez { p0: (627.0, -6.0), p1: (627.0, -6.0), p2: (627.0, -6.0) }) has the same coordinates as a previous segment.
* eogonek (U+0119): Line(Line { p0: (882.0, 138.0), p1: (882.0, 138.0) }) has the same coordinates as a previous segment.
* Omegatonos (U+038F): Quad(QuadBez { p0: (422.0, 150.0), p1: (422.0, 150.0), p2: (422.0, 150.0) }) has the same coordinates as a previous segment.
* uni03A9 (U+03A9): Quad(QuadBez { p0: (196.0, 150.0), p1: (196.0, 150.0), p2: (196.0, 150.0) }) has the same coordinates as a previous segment.
* uni03B2 (U+03B2): Quad(QuadBez { p0: (307.0, 1281.0), p1: (307.0, 1281.0), p2: (307.0, 1281.0) }) has the same coordinates as a previous segment.
* uni2126 (U+2126): Quad(QuadBez { p0: (196.0, 150.0), p1: (196.0, 150.0), p2: (196.0, 150.0) }) has the same coordinates as a previous segment. [code: overlapping-path-segments]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
>
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* a.ss02: Line(Line { p0: (912.0, 991.0), p1: (910.0, 47.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* agrave.ss02: Line(Line { p0: (912.0, 991.0), p1: (910.0, 47.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* aacute.ss02: Line(Line { p0: (912.0, 991.0), p1: (910.0, 47.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* acircumflex.ss02: Line(Line { p0: (912.0, 991.0), p1: (910.0, 47.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* atilde.ss02: Line(Line { p0: (912.0, 991.0), p1: (910.0, 47.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* adieresis.ss02: Line(Line { p0: (912.0, 991.0), p1: (910.0, 47.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* aring.ss02: Line(Line { p0: (912.0, 991.0), p1: (910.0, 47.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* amacron.ss02: Line(Line { p0: (912.0, 991.0), p1: (910.0, 47.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* abreve.ss02: Line(Line { p0: (912.0, 991.0), p1: (910.0, 47.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
... and 18 others [code: found-semi-vertical]



</div>
</details>


</div>
</details>


<details><summary>[10] dindot/DINDOT-Medium.ttf</summary>
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
    <summary>⚠️ <b>WARN</b> Check accent of Lcaron, dcaron, lcaron, tcaron (alt_caron)</summary>
    <div>


> Lcaron, dcaron, lcaron, tcaron should NOT be composed with quoteright or quotesingle or comma or caron(comb). It should be composed with a distinctive glyph which doesn't look like an apostrophe.
>
> Source: https://ilovetypography.com/2009/01/24/on-diacritics/ http://diacritics.typo.cz/index.php?id=5 https://www.typotheque.com/articles/lcaron




Original proposal: [https://github.com/fonttools/fontbakery/issues/3308]





- ⚠️ **WARN** Lcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** dcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** lcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** tcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]



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
    <summary>⚠️ <b>WARN</b> Check math signs have the same width. (math_signs_width)</summary>
    <div>


> #,         It is a common practice to have math signs sharing the same width         (preferably the same width as tabular figures accross the entire font family).
>
> This probably comes from the will to avoid additional tabular math signs knowing that their design can easily share the same width.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3832]





- ⚠️ **WARN** The most common width is 1060 among a set of 27  math glyphs.
The following math glyphs have a different width, though:
width=1440: uni221D [code: width-outliers]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Does the font contain a soft hyphen? (soft_hyphen)</summary>
    <div>


> The 'Soft Hyphen' character (codepoint 0x00AD) is used to mark a hyphenation possibility within a word in the absence of or overriding dictionary hyphenation.
>
> It is sometimes designed empty with no width (such as a control character), sometimes the same as the traditional hyphen, sometimes double encoded with the hyphen.
>
> That being said, it is recommended to not include it in the font at all, because discretionary hyphenation should be handled at the level of the shaping engine, not the font. Also, even if present, the software would not display that character.
>
> More discussion at: https://typedrawers.com/discussion/2046/special-dash-things-softhyphen-horizontalbar




Original proposal: [https://github.com/fonttools/fontbakery/issues/4046, https://github.com/fonttools/fontbakery/issues/3486]





- ⚠️ **WARN** This font has a 'Soft Hyphen' character. [code: softhyphen]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check font contains no unreachable glyphs (unreachable_glyphs)</summary>
    <div>


> Glyphs are either accessible directly through Unicode codepoints or through        substitution rules.
>
> In Color Fonts, glyphs are also referenced by the COLR table. And mathematical fonts also reference glyphs via the MATH table.
>
> Any glyphs not accessible by these means are redundant and serve only to increase the font's file size.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3160]





- ⚠️ **WARN** The following glyphs could not be reached by codepoint or substitution rules:

* acutecomb.loclPLK
* caroncmb.alt
* tonoscomb
* dieresistonoscomb
* circumflexcmb.case
* brevecmb.case
* hookabovecomb.case [code: unreachable-glyphs]



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
|   The following auxiliary characters are missing from the font: ῶ |                       |
| Auxiliary orthography codepoints:                                 | * de_Latn (German)    |
|   The following auxiliary characters are missing from the font: ſ | * fr_Latn (French)    |
| Auxiliary orthography codepoints:                                 | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѣ | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѫ |                       |
| Auxiliary orthography codepoints:                                 | * mn_Cyrl (Mongolian) |
|   The following auxiliary characters are missing from the font: ӊ |                       | [code: warning-language-shaping]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Do any segments have colinear vectors? (outline_colinear_vectors)</summary>
    <div>


> This check looks for consecutive line segments which have the same angle. This normally happens if an outline point has been added by accident.
>
> This check is not run for variable fonts, as they may legitimately have colinear vectors.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have colinear vectors:

* uni21BA (U+21BA): from (493.0, 773.0) to (418.0, 770.0) is colinear with segment from (418.0, 770.0) to (369.0, 768.0)
* uni21BA (U+21BA): from (270.0, 892.0) to (274.0, 903.0) is colinear with segment from (274.0, 903.0) to (284.0, 926.0)
* uni21BA (U+21BA): from (302.0, 972.0) to (312.0, 995.0) is colinear with segment from (312.0, 995.0) to (340.0, 1064.0)
* uni2206 (U+2206): from (17.0, 24.0) to (33.0, 68.0) is colinear with segment from (33.0, 68.0) to (501.0, 1359.0)
* uni2207 (U+2207): from (1043.0, 1217.0) to (1027.0, 1172.0) is colinear with segment from (1027.0, 1172.0) to (559.0, -119.0)
* uni03B2 (U+03B2): from (325.0, 174.0) to (549.0, 174.0) is colinear with segment from (549.0, 174.0) to (550.0, 174.0)
* uni03B5 (U+03B5): from (825.0, 734.0) to (825.0, 734.0) is colinear with segment from (825.0, 734.0) to (825.0, 734.0)
* uni03B6 (U+03B6): from (573.0, 856.0) to (569.0, 856.0) is colinear with segment from (569.0, 856.0) to (568.0, 856.0)
* uni03B6 (U+03B6): from (429.0, 856.0) to (426.0, 856.0) is colinear with segment from (426.0, 856.0) to (424.0, 856.0)
... and 12 others [code: found-colinear-vectors]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check there are no overlapping path segments (overlapping_path_segments)</summary>
    <div>


> Some rasterizers encounter difficulties when rendering glyphs with overlapping path segments.
>
> A path segment is a section of a path defined by two on-curve points. When two segments share the same coordinates, they are considered overlapping.




Original proposal: [https://github.com/google/fonts/issues/7594#issuecomment-2401909084]





- ⚠️ **WARN** The following glyphs have overlapping path segments:

* nine.dnom: Quad(QuadBez { p0: (343.0, 311.0), p1: (343.0, 311.0), p2: (343.0, 311.0) }) has the same coordinates as a previous segment.
* nine.numr: Quad(QuadBez { p0: (343.0, 885.0), p1: (343.0, 885.0), p2: (343.0, 885.0) }) has the same coordinates as a previous segment.
* uni03A9 (U+03A9): Line(Line { p0: (150.0, 190.0), p1: (150.0, 190.0) }) has the same coordinates as a previous segment.
* uni03B5 (U+03B5): Line(Line { p0: (591.0, 604.0), p1: (591.0, 604.0) }) has the same coordinates as a previous segment.
* uni03B5 (U+03B5): Line(Line { p0: (825.0, 734.0), p1: (825.0, 734.0) }) has the same coordinates as a previous segment.
* uni03B8 (U+03B8): Quad(QuadBez { p0: (311.0, 625.0), p1: (311.0, 625.0), p2: (311.0, 625.0) }) has the same coordinates as a previous segment.
* uni03B8 (U+03B8): Line(Line { p0: (778.0, 788.0), p1: (778.0, 788.0) }) has the same coordinates as a previous segment.
* uni03F5 (U+03F5): Quad(QuadBez { p0: (889.0, 684.0), p1: (889.0, 684.0), p2: (889.0, 684.0) }) has the same coordinates as a previous segment.
* uni2126 (U+2126): Line(Line { p0: (150.0, 190.0), p1: (150.0, 190.0) }) has the same coordinates as a previous segment.
... and 2 others [code: overlapping-path-segments]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Do outlines contain any semi-vertical or semi-horizontal lines? (outline_semi_vertical)</summary>
    <div>


> This check detects line segments which are nearly, but not quite, exactly horizontal or vertical. Sometimes such lines are created by design, but often they are indicative of a design error.
>
> This check is disabled for italic styles, which often contain nearly-upright lines.




Original proposal: [https://github.com/fonttools/fontbakery/pull/3088]





- ⚠️ **WARN** The following glyphs have semi-vertical/semi-horizontal lines:

* a.ss02: Line(Line { p0: (920.0, 991.0), p1: (918.0, 53.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* agrave.ss02: Line(Line { p0: (920.0, 991.0), p1: (918.0, 53.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* aacute.ss02: Line(Line { p0: (920.0, 991.0), p1: (918.0, 53.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* acircumflex.ss02: Line(Line { p0: (920.0, 991.0), p1: (918.0, 53.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* atilde.ss02: Line(Line { p0: (920.0, 991.0), p1: (918.0, 53.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* adieresis.ss02: Line(Line { p0: (920.0, 991.0), p1: (918.0, 53.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* aring.ss02: Line(Line { p0: (920.0, 991.0), p1: (918.0, 53.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* amacron.ss02: Line(Line { p0: (920.0, 991.0), p1: (918.0, 53.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
* abreve.ss02: Line(Line { p0: (920.0, 991.0), p1: (918.0, 53.0) }) (angle: -90.12 degrees, expected: -90.00 degrees)
... and 18 others [code: found-semi-vertical]



</div>
</details>


</div>
</details>


<details><summary>[2] dindot</summary>
<div>


<details>
    <summary>⚠️ <b>WARN</b> Ensure Fonts have 'ital' STAT axis. (opentype/STAT/ital_axis)</summary>
    <div>


> Check that related Upright and Italic have an 'ital' axis in the STAT table.
>
> Since the STAT table can be used to create new instances, it is important to ensure that such an 'ital' axis be the last one declared in the STAT table so that the eventual naming of new instances follows the subfamily traditional scheme (RIBBI / WWS) where "Italic" is always last.
>
> The 'ital' axis should also be strictly boolean, only accepting values of 0 (for Uprights) or 1 (for Italics). This usually works as a mechanism for selecting between two linked variable font files.
>
> Also, the axis value name for uprights must be set as elidable.




Original proposal: [https://github.com/fonttools/fontbakery/issues/2934, https://github.com/fonttools/fontbakery/issues/3668, https://github.com/fonttools/fontbakery/issues/3669]





- ⚠️ **WARN** Static font is missing the 'STAT' table. [code: no-stat-table]



</div>
</details>





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
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: cherokee, tifinagh, coptic, math
* U+0306 COMBINING BREVE: try adding one of: old-permic, tifinagh
* U+0307 COMBINING DOT ABOVE: try adding one of: coptic, duployan, tifinagh, tai-le, math, old-permic, hebrew, syriac, canadian-aboriginal, malayalam, todhri
* U+030A COMBINING RING ABOVE: try adding one of: duployan, syriac
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: osage, cherokee
* U+030C COMBINING CARON: try adding one of: cherokee, tai-le
... and 205 others

Or you can add the above codepoints to one of the subsets supported by the font: cyrillic-ext, cyrillic, greek, latin-ext, latin, vietnamese [code: unreachable-subsetting]




- ⚠️ **WARN** dindot/DINDOT-BoldItalic.ttf: The following codepoints supported by the font are not covered by any subsets defined in the font's metadata file, and will never be served. You can solve this by either manually adding additional subset declarations to METADATA.pb, or by editing the glyphset definitions.

* U+02D8 BREVE: try adding one of: canadian-aboriginal, yi
* U+02D9 DOT ABOVE: try adding one of: canadian-aboriginal, yi
* U+02DB OGONEK: try adding one of: canadian-aboriginal, yi
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: cherokee, tifinagh, coptic, math
* U+0306 COMBINING BREVE: try adding one of: old-permic, tifinagh
* U+0307 COMBINING DOT ABOVE: try adding one of: coptic, duployan, tifinagh, tai-le, math, old-permic, hebrew, syriac, canadian-aboriginal, malayalam, todhri
* U+030A COMBINING RING ABOVE: try adding one of: duployan, syriac
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: osage, cherokee
* U+030C COMBINING CARON: try adding one of: cherokee, tai-le
... and 205 others

Or you can add the above codepoints to one of the subsets supported by the font: cyrillic-ext, cyrillic, greek, latin-ext, latin, vietnamese [code: unreachable-subsetting]




- ⚠️ **WARN** dindot/DINDOT-Italic.ttf: The following codepoints supported by the font are not covered by any subsets defined in the font's metadata file, and will never be served. You can solve this by either manually adding additional subset declarations to METADATA.pb, or by editing the glyphset definitions.

* U+02D8 BREVE: try adding one of: canadian-aboriginal, yi
* U+02D9 DOT ABOVE: try adding one of: canadian-aboriginal, yi
* U+02DB OGONEK: try adding one of: canadian-aboriginal, yi
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: cherokee, tifinagh, coptic, math
* U+0306 COMBINING BREVE: try adding one of: old-permic, tifinagh
* U+0307 COMBINING DOT ABOVE: try adding one of: coptic, duployan, tifinagh, tai-le, math, old-permic, hebrew, syriac, canadian-aboriginal, malayalam, todhri
* U+030A COMBINING RING ABOVE: try adding one of: duployan, syriac
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: osage, cherokee
* U+030C COMBINING CARON: try adding one of: cherokee, tai-le
... and 205 others

Or you can add the above codepoints to one of the subsets supported by the font: cyrillic-ext, cyrillic, greek, latin-ext, latin, vietnamese [code: unreachable-subsetting]




- ⚠️ **WARN** dindot/DINDOT-Medium.ttf: The following codepoints supported by the font are not covered by any subsets defined in the font's metadata file, and will never be served. You can solve this by either manually adding additional subset declarations to METADATA.pb, or by editing the glyphset definitions.

* U+02D8 BREVE: try adding one of: canadian-aboriginal, yi
* U+02D9 DOT ABOVE: try adding one of: canadian-aboriginal, yi
* U+02DB OGONEK: try adding one of: canadian-aboriginal, yi
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: cherokee, tifinagh, coptic, math
* U+0306 COMBINING BREVE: try adding one of: old-permic, tifinagh
* U+0307 COMBINING DOT ABOVE: try adding one of: coptic, duployan, tifinagh, tai-le, math, old-permic, hebrew, syriac, canadian-aboriginal, malayalam, todhri
* U+030A COMBINING RING ABOVE: try adding one of: duployan, syriac
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: osage, cherokee
* U+030C COMBINING CARON: try adding one of: cherokee, tai-le
... and 205 others

Or you can add the above codepoints to one of the subsets supported by the font: cyrillic-ext, cyrillic, greek, latin-ext, latin, vietnamese [code: unreachable-subsetting]




- ⚠️ **WARN** dindot/DINDOT-MediumItalic.ttf: The following codepoints supported by the font are not covered by any subsets defined in the font's metadata file, and will never be served. You can solve this by either manually adding additional subset declarations to METADATA.pb, or by editing the glyphset definitions.

* U+02D8 BREVE: try adding one of: canadian-aboriginal, yi
* U+02D9 DOT ABOVE: try adding one of: canadian-aboriginal, yi
* U+02DB OGONEK: try adding one of: canadian-aboriginal, yi
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: cherokee, tifinagh, coptic, math
* U+0306 COMBINING BREVE: try adding one of: old-permic, tifinagh
* U+0307 COMBINING DOT ABOVE: try adding one of: coptic, duployan, tifinagh, tai-le, math, old-permic, hebrew, syriac, canadian-aboriginal, malayalam, todhri
* U+030A COMBINING RING ABOVE: try adding one of: duployan, syriac
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: osage, cherokee
* U+030C COMBINING CARON: try adding one of: cherokee, tai-le
... and 205 others

Or you can add the above codepoints to one of the subsets supported by the font: cyrillic-ext, cyrillic, greek, latin-ext, latin, vietnamese [code: unreachable-subsetting]




- ⚠️ **WARN** dindot/DINDOT-Regular.ttf: The following codepoints supported by the font are not covered by any subsets defined in the font's metadata file, and will never be served. You can solve this by either manually adding additional subset declarations to METADATA.pb, or by editing the glyphset definitions.

* U+02D8 BREVE: try adding one of: canadian-aboriginal, yi
* U+02D9 DOT ABOVE: try adding one of: canadian-aboriginal, yi
* U+02DB OGONEK: try adding one of: canadian-aboriginal, yi
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: cherokee, tifinagh, coptic, math
* U+0306 COMBINING BREVE: try adding one of: old-permic, tifinagh
* U+0307 COMBINING DOT ABOVE: try adding one of: coptic, duployan, tifinagh, tai-le, math, old-permic, hebrew, syriac, canadian-aboriginal, malayalam, todhri
* U+030A COMBINING RING ABOVE: try adding one of: duployan, syriac
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: osage, cherokee
* U+030C COMBINING CARON: try adding one of: cherokee, tai-le
... and 205 others

Or you can add the above codepoints to one of the subsets supported by the font: cyrillic-ext, cyrillic, greek, latin-ext, latin, vietnamese [code: unreachable-subsetting]




- ⚠️ **WARN** dindot/DINDOT-SemiBold.ttf: The following codepoints supported by the font are not covered by any subsets defined in the font's metadata file, and will never be served. You can solve this by either manually adding additional subset declarations to METADATA.pb, or by editing the glyphset definitions.

* U+02D8 BREVE: try adding one of: canadian-aboriginal, yi
* U+02D9 DOT ABOVE: try adding one of: canadian-aboriginal, yi
* U+02DB OGONEK: try adding one of: canadian-aboriginal, yi
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: cherokee, tifinagh, coptic, math
* U+0306 COMBINING BREVE: try adding one of: old-permic, tifinagh
* U+0307 COMBINING DOT ABOVE: try adding one of: coptic, duployan, tifinagh, tai-le, math, old-permic, hebrew, syriac, canadian-aboriginal, malayalam, todhri
* U+030A COMBINING RING ABOVE: try adding one of: duployan, syriac
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: osage, cherokee
* U+030C COMBINING CARON: try adding one of: cherokee, tai-le
... and 205 others

Or you can add the above codepoints to one of the subsets supported by the font: cyrillic-ext, cyrillic, greek, latin-ext, latin, vietnamese [code: unreachable-subsetting]




- ⚠️ **WARN** dindot/DINDOT-SemiBoldItalic.ttf: The following codepoints supported by the font are not covered by any subsets defined in the font's metadata file, and will never be served. You can solve this by either manually adding additional subset declarations to METADATA.pb, or by editing the glyphset definitions.

* U+02D8 BREVE: try adding one of: canadian-aboriginal, yi
* U+02D9 DOT ABOVE: try adding one of: canadian-aboriginal, yi
* U+02DB OGONEK: try adding one of: canadian-aboriginal, yi
* U+0302 COMBINING CIRCUMFLEX ACCENT: try adding one of: cherokee, tifinagh, coptic, math
* U+0306 COMBINING BREVE: try adding one of: old-permic, tifinagh
* U+0307 COMBINING DOT ABOVE: try adding one of: coptic, duployan, tifinagh, tai-le, math, old-permic, hebrew, syriac, canadian-aboriginal, malayalam, todhri
* U+030A COMBINING RING ABOVE: try adding one of: duployan, syriac
* U+030B COMBINING DOUBLE ACUTE ACCENT: try adding one of: osage, cherokee
* U+030C COMBINING CARON: try adding one of: cherokee, tai-le
... and 205 others

Or you can add the above codepoints to one of the subsets supported by the font: cyrillic-ext, cyrillic, greek, latin-ext, latin, vietnamese [code: unreachable-subsetting]



</div>
</details>


</div>
</details>


<details><summary>[7] dindot/DINDOT-MediumItalic.ttf</summary>
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
    <summary>⚠️ <b>WARN</b> Check accent of Lcaron, dcaron, lcaron, tcaron (alt_caron)</summary>
    <div>


> Lcaron, dcaron, lcaron, tcaron should NOT be composed with quoteright or quotesingle or comma or caron(comb). It should be composed with a distinctive glyph which doesn't look like an apostrophe.
>
> Source: https://ilovetypography.com/2009/01/24/on-diacritics/ http://diacritics.typo.cz/index.php?id=5 https://www.typotheque.com/articles/lcaron




Original proposal: [https://github.com/fonttools/fontbakery/issues/3308]





- ⚠️ **WARN** Lcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** dcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** lcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** tcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]



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
    <summary>⚠️ <b>WARN</b> Check math signs have the same width. (math_signs_width)</summary>
    <div>


> #,         It is a common practice to have math signs sharing the same width         (preferably the same width as tabular figures accross the entire font family).
>
> This probably comes from the will to avoid additional tabular math signs knowing that their design can easily share the same width.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3832]





- ⚠️ **WARN** The most common width is 1060 among a set of 27  math glyphs.
The following math glyphs have a different width, though:
width=1440: uni221D [code: width-outliers]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Does the font contain a soft hyphen? (soft_hyphen)</summary>
    <div>


> The 'Soft Hyphen' character (codepoint 0x00AD) is used to mark a hyphenation possibility within a word in the absence of or overriding dictionary hyphenation.
>
> It is sometimes designed empty with no width (such as a control character), sometimes the same as the traditional hyphen, sometimes double encoded with the hyphen.
>
> That being said, it is recommended to not include it in the font at all, because discretionary hyphenation should be handled at the level of the shaping engine, not the font. Also, even if present, the software would not display that character.
>
> More discussion at: https://typedrawers.com/discussion/2046/special-dash-things-softhyphen-horizontalbar




Original proposal: [https://github.com/fonttools/fontbakery/issues/4046, https://github.com/fonttools/fontbakery/issues/3486]





- ⚠️ **WARN** This font has a 'Soft Hyphen' character. [code: softhyphen]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check font contains no unreachable glyphs (unreachable_glyphs)</summary>
    <div>


> Glyphs are either accessible directly through Unicode codepoints or through        substitution rules.
>
> In Color Fonts, glyphs are also referenced by the COLR table. And mathematical fonts also reference glyphs via the MATH table.
>
> Any glyphs not accessible by these means are redundant and serve only to increase the font's file size.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3160]





- ⚠️ **WARN** The following glyphs could not be reached by codepoint or substitution rules:

* acutecomb.loclPLK
* caroncmb.alt
* tonoscomb
* dieresistonoscomb
* circumflexcmb.case
* brevecmb.case
* hookabovecomb.case [code: unreachable-glyphs]



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
| Auxiliary orthography codepoints:                                 | * de_Latn (German)    |
|   The following auxiliary characters are missing from the font: ſ | * fr_Latn (French)    |
| Auxiliary orthography codepoints:                                 | * ca_Latn (Catalan)   |
|   The following auxiliary characters are missing from the font: Ŀ |                       |
|   The following auxiliary characters are missing from the font: ŀ |                       |
| Auxiliary orthography codepoints:                                 | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѣ | * bg_Cyrl (Bulgarian) |
|   The following auxiliary characters are missing from the font: ѫ |                       |
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


<details><summary>[7] dindot/DINDOT-SemiBoldItalic.ttf</summary>
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
    <summary>⚠️ <b>WARN</b> Check accent of Lcaron, dcaron, lcaron, tcaron (alt_caron)</summary>
    <div>


> Lcaron, dcaron, lcaron, tcaron should NOT be composed with quoteright or quotesingle or comma or caron(comb). It should be composed with a distinctive glyph which doesn't look like an apostrophe.
>
> Source: https://ilovetypography.com/2009/01/24/on-diacritics/ http://diacritics.typo.cz/index.php?id=5 https://www.typotheque.com/articles/lcaron




Original proposal: [https://github.com/fonttools/fontbakery/issues/3308]





- ⚠️ **WARN** Lcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** dcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** lcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]




- ⚠️ **WARN** tcaron is decomposed and therefore could not be checked. Please check manually. [code: decomposed-outline]



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
    <summary>⚠️ <b>WARN</b> Check math signs have the same width. (math_signs_width)</summary>
    <div>


> #,         It is a common practice to have math signs sharing the same width         (preferably the same width as tabular figures accross the entire font family).
>
> This probably comes from the will to avoid additional tabular math signs knowing that their design can easily share the same width.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3832]





- ⚠️ **WARN** The most common width is 1070 among a set of 27  math glyphs.
The following math glyphs have a different width, though:
width=1440: uni221D [code: width-outliers]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Does the font contain a soft hyphen? (soft_hyphen)</summary>
    <div>


> The 'Soft Hyphen' character (codepoint 0x00AD) is used to mark a hyphenation possibility within a word in the absence of or overriding dictionary hyphenation.
>
> It is sometimes designed empty with no width (such as a control character), sometimes the same as the traditional hyphen, sometimes double encoded with the hyphen.
>
> That being said, it is recommended to not include it in the font at all, because discretionary hyphenation should be handled at the level of the shaping engine, not the font. Also, even if present, the software would not display that character.
>
> More discussion at: https://typedrawers.com/discussion/2046/special-dash-things-softhyphen-horizontalbar




Original proposal: [https://github.com/fonttools/fontbakery/issues/4046, https://github.com/fonttools/fontbakery/issues/3486]





- ⚠️ **WARN** This font has a 'Soft Hyphen' character. [code: softhyphen]



</div>
</details>





<details>
    <summary>⚠️ <b>WARN</b> Check font contains no unreachable glyphs (unreachable_glyphs)</summary>
    <div>


> Glyphs are either accessible directly through Unicode codepoints or through        substitution rules.
>
> In Color Fonts, glyphs are also referenced by the COLR table. And mathematical fonts also reference glyphs via the MATH table.
>
> Any glyphs not accessible by these means are redundant and serve only to increase the font's file size.




Original proposal: [https://github.com/fonttools/fontbakery/issues/3160]





- ⚠️ **WARN** The following glyphs could not be reached by codepoint or substitution rules:

* acutecomb.loclPLK
* caroncmb.alt
* tonoscomb
* dieresistonoscomb
* circumflexcmb.case
* brevecmb.case
* hookabovecomb.case [code: unreachable-glyphs]



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
| Auxiliary orthography codepoints:                                 | * en_Latn (English)   |
|   The following auxiliary characters are missing from the font: ʻ |                       |
| Auxiliary orthography codepoints:                                 | * ca_Latn (Catalan)   |
|   The following auxiliary characters are missing from the font: Ŀ |                       |
|   The following auxiliary characters are missing from the font: ŀ |                       |
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
| Auxiliary orthography codepoints:                                 | * mn_Cyrl (Mongolian) |
|   The following auxiliary characters are missing from the font: ӊ |                       |
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
|   The following auxiliary characters are missing from the font: ῶ |                       | [code: warning-language-shaping]



</div>
</details>


</div>
</details>






### Summary

| 🔥 FAIL | ⚠️ WARN | ℹ️ INFO | ✅ PASS | ⏩ SKIP |
| ---|---|---|---|---|
| 8 | 93 | 94 | 762 | 477 |
| 1% | 6% | 7% | 53% | 33% |
