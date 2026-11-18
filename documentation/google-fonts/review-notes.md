# Remaining review findings

Candidate 1.001 resolves the actionable source, metadata and outline warnings.
The unfiltered Google Fonts profile still reports 24 WARN and eight FAIL
results. Those findings are retained in the raw report, not changed to PASS.
They represent three warning categories and one family-name decision across
eight styles.

## Dotted zero: eight contour-count warnings

The default zero has an outer outline, counter and circular dot. The checker
expects two contours in old-style/tabular zero variants; DINDOT intentionally
has three. U+2152 ONE TENTH likewise has an extra contour from its dotted zero.
Removing that contour would change the intended design.

[Design verification](review-design-verification.json) checks that every flagged
form has exactly one more contour than its `ss04` plain-zero counterpart, with
identical spacing. It also verifies selection of plain-zero forms alongside
old-style and tabular features in all eight faces. Review request: accept the
intentional extra dot contours.

## Optional orthography coverage: eight language warnings

Required Latin Core and the mandatory orthographies tested by Fontspector
pass. The remaining rows refer to auxiliary characters: polytonic Greek,
historical Cyrillic, a few extended Latin letters and Catalan legacy forms.
They are listed in [the coverage inventory](optional-coverage-review.json).
There are no unattached-mark messages in these warning results.

These optional forms are outside the currently drawn repertoire. Adding them
would be a character-set/design extension and needs language-aware drawings
and optical review. The current candidate does not claim polytonic Greek or
complete historical orthographies. Review request: confirm that this optional
coverage is acceptable for the submitted family and its intended language scope.

## Downstream subset serving: eight metadata warnings

The full desktop/self-hosted fonts contain 986 encoded characters. Fontspector
infers six catalog subsets and identifies 224 codepoints outside those inferred
sets. Its exact-version data, per-codepoint suggestions, and repertoire are in
[the serving audit](subset-serving-audit.json).

The additional characters include useful math, arrows, symbols, spacing and
combining marks. They should remain in the source font. Declaring unrelated
scripts to cover a shared mark would misrepresent the family. The current
`math`, `symbols` and `symbols2` groups are only partially covered (about 10.94%,
3.88% and 4.49% respectively); simply declaring them would create a different
metadata coverage warning. Ten codepoints are absent from every subset in the
checker data, including the combining horn/ogonek, some punctuation/control
characters, and encoded fi/fl ligatures.

No catalog METADATA.pb, publication date or accepted serving configuration is
asserted by this upstream candidate. Review request: agree the downstream
subset plan so the intended additional characters are served appropriately.
The existing full downloads retain their complete supported repertoire.

## Family name: eight failures

The definitive menu name remains DINDOT. The all-caps/abbreviation check fails
once per face. Naming approval and the shared DIN element in upstream RFNs
remain in the [existing submission](https://github.com/google/fonts/issues/11316)
and [upstream review record](upstream-licenses/README.md).

## Regression gate

`review-findings.json` records this reviewed project baseline. CI fails on new
warning/failure types, errors or fatals while keeping the raw profile report
unchanged. This project gate is not a waiver from Google Fonts or an assertion
that the family has been accepted.
