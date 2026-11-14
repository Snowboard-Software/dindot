"""Greek statistical vocabulary and real scientific script features.

The shared Latin/Cyrillic skeletons are DINDOT's own. Distinct Greek letters
are drawn here rather than substituted with unrelated Latin characters.
"""

from copy import deepcopy
from math import ceil
import skia
from extensions import (
    ExtensionBuilder,
    cubic_path,
    rect,
    combine,
    subtract,
    transform,
    canonical,
)
from data_features import add_feature, register_feature
from kerning import add_pair_lookup, copy_kerning
from rounding import Segment, bounds, contours, path_from_contours
from shapely.affinity import translate
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

SUB_LETTERS = dict(zip("aehijklmnoprstuvx", "ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ"))
# The least white between a dialytika iota's dot and a following β δ ζ θ λ ξ,
# in em: 30 thousandths in every face, and the 3 the italics' slant takes.
DIALYTIKA_KERN_CLEAR = 0.033


def _ink(path):
    """The outline as one shapely area, its curves flattened; counters filled,
    which leaves every distance to another glyph as it is."""
    polys = []
    for contour in contours(path):
        pts = []
        for seg in contour:
            a = seg.points
            steps = 8 if len(a) > 2 else 1
            for k in range(1, steps + 1):
                q, t = list(a), k / steps
                while len(q) > 1:
                    q = [
                        (u[0] + (v[0] - u[0]) * t, u[1] + (v[1] - u[1]) * t)
                        for u, v in zip(q, q[1:])
                    ]
                pts.append(q[0])
        if len(pts) > 2:
            polys.append(Polygon(pts).buffer(0))
    return unary_union(polys)


def _vertical_edges(path, y):
    """The x of every vertical outline edge that passes height y, left to right."""
    return sorted(
        {
            seg.points[0][0]
            for contour in contours(path)
            for seg in contour
            if len(seg.points) == 2
            and abs(seg.points[0][0] - seg.points[1][0]) < 0.01
            and min(seg.points[0][1], seg.points[1][1])
            < y
            < max(seg.points[0][1], seg.points[1][1])
        }
    )


def _top_at(path, top):
    """`path` with every point above its middle moved down by the same amount,
    so its top is at `top`: o's overshoot taken off, its top stroke and
    straight sides kept."""
    ink = [bounds(c) for c in contours(path)]
    drop = max(b[3] for b in ink) - top
    middle = (min(b[1] for b in ink) + max(b[3] for b in ink)) / 2
    return path_from_contours(
        [
            [
                Segment(tuple((x, y - drop if y > middle else y) for x, y in s.points))
                for s in contour
            ]
            for contour in contours(path)
        ]
    )


class ScienceBuilder(ExtensionBuilder):
    def stroke(self, commands, width=None):
        p = cubic_path(commands)
        out = skia.Path()
        skia.Paint(
            Style=skia.Paint.kStroke_Style,
            StrokeWidth=width or self.stem,
            StrokeCap=skia.Paint.kButt_Cap,
            StrokeJoin=skia.Paint.kRound_Join,
        ).getFillPath(p, out, resScale=8)
        return canonical(out)

    def alias_letter(self, ch, base, advance=None):
        """The Greek letter as its Latin (or Cyrillic) skeleton, with that
        letter's kerning on both sides, so Greek text kerns as Latin does
        (Τό as Tó), DINish's own Α included."""
        if ord(ch) in self.font.getBestCmap():
            name = self.font.getBestCmap()[ord(ch)]
        else:
            width = self.font["hmtx"][base][0] if advance is None else advance
            name = self.compose(
                ch,
                [(base, (1, 0, 0, 1, 0, 0))],
                width,
                "Greek",
                "The shared DINDOT skeleton, mapped to the correct Greek Unicode character.",
            )
        copy_kerning(self.font, name, base)
        return name

    def letter(self, ch, path, width=600):
        if ord(ch) in self.font.getBestCmap():
            return self.font.getBestCmap()[ord(ch)]
        return self.add(
            ch,
            path,
            width,
            "Greek",
            "Drawn Greek anatomy; native stem weight and rounded terminal system.",
        )

    def greek(self):
        cm = self.font.getBestCmap()
        for ch, base in {
            "Α": "A",
            "Β": "B",
            "Ε": "E",
            "Ζ": "Z",
            "Η": "H",
            "Ι": "I",
            "Κ": "K",
            "Μ": "M",
            "Ν": "N",
            "Ο": "O",
            "Ρ": "P",
            "Τ": "T",
            "Υ": "Y",
            "Χ": "X",
            "Π": "Pecyr",
            "Φ": "Efcyr",
            "μ": cm[0xB5],
            "ι": "dotlessi",
            "ν": "v",
            "ο": "o",
            "ρ": "p",
            "υ": "u",
        }.items():
            self.alias_letter(ch, base)
        t = self.stem
        h = 707
        # Each weight's own x-height (DINish's OS/2 reads 519 in Medium and
        # SemiBold too), so τ π σ ζ κ χ ψ stand as tall as x in every weight.
        xh = max(bounds(c)[3] for c in contours(self.outline("x")))
        self.letter(
            "Γ", transform(self.outline("L"), d=-1, y=h), self.font["hmtx"]["L"][0]
        )
        self.letter(
            "Δ",
            subtract(
                cubic_path([("M", 45, 0), ("L", 320, 707), ("L", 595, 0), ("Z",)]),
                cubic_path(
                    [
                        ("M", 45 + t * 1.3, t),
                        ("L", 320, 707 - t * 2.6),
                        ("L", 595 - t * 1.3, t),
                        ("Z",),
                    ]
                ),
            ),
            640,
        )
        self.letter(
            "Λ",
            self.stroke(
                [("M", 70, t * 0.19), ("L", 320, 707 - t / 2), ("L", 570, t * 0.19)]
            ),
            640,
        )
        ow = self.font["hmtx"]["O"][0]
        self.letter(
            "Θ",
            combine(
                self.outline("O"),
                rect(ow * 0.23, 353 - t * 0.46, ow * 0.77, 353 + t * 0.46),
            ),
            ow,
        )
        self.letter(
            "Ξ",
            combine(
                rect(65, 0, 555, t),
                rect(92, 353 - t * 0.45, 528, 353 + t * 0.45),
                rect(65, h - t, 555, h),
            ),
            620,
        )
        self.letter(
            "Σ",
            self.stroke(
                [
                    ("M", 565, h - t / 2),
                    ("L", 80, h - t / 2),
                    ("L", 340, 353),
                    ("L", 80, t / 2),
                    ("L", 565, t / 2),
                ]
            ),
            640,
        )
        uw = self.font["hmtx"]["U"][0]
        self.letter(
            "Ψ",
            combine(
                transform(self.outline("U"), d=0.66, y=240),
                rect(uw / 2 - t / 2, 0, uw / 2 + t / 2, h),
            ),
            uw,
        )
        omega = self.stroke(
            [
                ("M", 225, t / 2),
                ("C", 75, 130, 55, 240, 75, 435),
                ("C", 95, 635, 205, 707 - t / 2, 320, 707 - t / 2),
                ("C", 435, 707 - t / 2, 545, 635, 565, 435),
                ("C", 585, 240, 565, 130, 415, t / 2),
            ]
        )
        self.letter("Ω", combine(omega, rect(55, 0, 240, t), rect(400, 0, 585, t)), 640)
        # Lowercase forms keep the lowercase rhythm; ascenders and descenders
        # on beta/theta/lambda and gamma/eta/rho/phi/chi/psi remain meaningful.
        o = self.outline("o")
        ow = self.font["hmtx"]["o"][0]
        self.letter(
            "α",
            combine(
                o,
                self.stroke(
                    [
                        ("M", ow - 78, xh),
                        ("C", ow - 95, 370, ow - 130, 120, ow - 72, 30),
                        ("C", ow - 45, -5, ow - 8, 12, ow + 5, 42),
                    ],
                    t * 0.92,
                ),
            ),
            ow + 55,
        )
        bw = self.font["hmtx"]["B"][0]
        beta = transform(self.outline("B"), a=0.87)
        self.letter(
            "β",
            combine(beta, rect(75 * 0.87, -205, (75 + t) * 0.87, 100)),
            round(bw * 0.87),
        )
        self.letter(
            "γ",
            self.stroke(
                [
                    ("M", 55, 475),
                    ("C", 190, 610, 290, 310, 310, -205),
                    ("M", 306, -160),
                    ("C", 325, 95, 410, 355, 520, 519),
                ]
            ),
            580,
        )
        delta = combine(
            transform(o, d=0.81),
            self.stroke(
                [
                    ("M", ow - 120, 385),
                    ("C", ow - 75, 505, 140, 535, 160, 640),
                    ("C", 175, 705, 305, 730, 405, 650),
                ]
            ),
        )
        self.letter("δ", delta, ow + 20)
        # ε is DINish's з turned round, as Greek and Cyrillic fonts draw the
        # pair, so it has DIN's cut terminals and o's height. Its strokes had
        # been drawn centred on the x-height and the baseline, so it stood
        # half a stroke over both.
        ze = self.font["hmtx"]["zecyr"][0]
        self.letter("ε", combine(transform(self.outline("zecyr"), a=-1, x=ze)), ze)
        self.letter(
            "ζ",
            self.stroke(
                [
                    ("M", 85, xh - t / 2),
                    ("L", 470, xh - t / 2),
                    ("C", 390, 400, 175, 260, 125, 155),
                    ("C", 30, 5, 170, -30, 315, -70),
                    ("C", 450, -110, 405, -190, 275, -170),
                ]
            ),
            550,
        )
        # η is n with its right stem run down to the descender: the stem's own
        # edges, read at half the x-height, and up to there, so the stem's
        # rounded foot is filled and nothing steps at the baseline.
        n = self.outline("n")
        stem_left, stem_right = _vertical_edges(n, xh / 2)[-2:]
        self.letter(
            "η",
            combine(n, rect(stem_left, -205, stem_right, xh / 2)),
            self.font["hmtx"]["n"][0],
        )
        theta = transform(self.outline("O"), a=0.86)
        tw = round(self.font["hmtx"]["O"][0] * 0.86)
        self.letter(
            "θ",
            combine(theta, rect(tw * 0.2, 353 - t * 0.43, tw * 0.8, 353 + t * 0.43)),
            tw,
        )
        self.letter(
            "κ", transform(self.outline("k"), d=xh / 707), self.font["hmtx"]["k"][0]
        )
        self.letter(
            "λ",
            self.stroke(
                [
                    ("M", 70, 675),
                    ("C", 175, 740, 230, 605, 275, 500),
                    ("L", 505, 0),
                    ("M", 320, 420),
                    ("L", 80, 0),
                ]
            ),
            580,
        )
        self.letter(
            "ξ",
            self.stroke(
                [
                    ("M", 415, 665),
                    ("C", 240, 750, 110, 650, 140, 535),
                    ("C", 165, 440, 300, 395, 405, 395),
                    ("M", 405, 395),
                    ("C", 185, 420, 75, 315, 140, 205),
                    ("C", 195, 110, 355, 130, 390, 45),
                    ("C", 450, -75, 350, -160, 245, -175),
                ]
            ),
            530,
        )
        # τ's stem and π's right leg are DINish t's stem and foot, under the
        # bar, and π's left leg has t's stem. A drawn hook, a stroke turned
        # tighter than half its width, left a lump inside the turn and dipped
        # under the baseline, and in Bold it folded once the stems reached the
        # x-height.
        tee = self.outline("t")
        stem_left, stem_right = _vertical_edges(tee, xh / 2)[:2]
        stem = stem_right - stem_left
        foot = subtract(tee, rect(-1000, xh / 2, 2000, 2000))

        def leg(x):
            """t's stem and foot on the centre line x, up into the bar."""
            dx = x - (stem_left + stem_right) / 2
            return combine(
                transform(foot, x=dx),
                rect(stem_left + dx, xh / 2 - 1, stem_right + dx, xh - t / 2),
            )

        pi = combine(
            rect(50, xh - t, 570, xh),
            rect(165 - stem / 2, 0, 165 + stem / 2, xh - t / 2),
            leg(435),
        )
        self.letter("π", pi, 620)
        # σ is o's bowl with its top run on as the bar. The bowl comes down to
        # the x-height, where τ's and π's bars stand, and the bar starts at the
        # top of the bowl at the top stroke's own thickness, so the two meet
        # without a step. The bar ends 8% of the x-height past the bowl, as in
        # Fira Sans, Noto Sans and Roboto, with r's right bearing, so σ is
        # about as wide as o.
        bowl = _top_at(o, xh)
        outer, counter = sorted(contours(bowl), key=lambda c: bounds(c)[3])[::-1]
        apex = max((s.points[0] for s in outer), key=lambda p: p[1])
        end = bounds(outer)[2] + 0.08 * xh
        r = self.outline("r").computeTightBounds()
        self.letter(
            "σ",
            combine(bowl, rect(apex[0], bounds(counter)[3], end, xh)),
            round(end + self.font["hmtx"]["r"][0] - r.right()),
        )
        # ς is c's top and bowl, and at the bottom of the bowl its stroke runs
        # on into the tail at the bowl's own thickness: right, then down and
        # back under the baseline, its curl ending under c's top terminal.
        # c's lower arm is left out. It was c with a tail stroke laid on its
        # lower terminal, and the join kinked.
        cee = self.outline("c")
        box = cee.computeTightBounds()
        apex = min((s.points[0] for c in contours(cee) for s in c), key=lambda p: p[1])
        cut = _ink(cee).intersection(LineString([(apex[0], -1000), (apex[0], 1000)]))
        _, bottom, _, top = min(getattr(cut, "geoms", [cut]), key=lambda g: g.bounds[1]).bounds
        x, y, right = apex[0], (bottom + top) / 2, box.right()
        tail = self.stroke(
            [
                ("M", x, y),
                ("C", x + 110, y, right - 25, y - 20, right - 25, -60),
                ("C", right - 25, -125, right - 80, -168, right - 160, -178),
            ],
            top - bottom,
        )
        bowl = subtract(cee, rect(x, -1000, 2000, (box.top() + box.bottom()) / 2))
        self.letter("ς", combine(bowl, tail), self.font["hmtx"]["c"][0])
        self.letter("τ", combine(rect(55, xh - t, 535, xh), leg(295)), 580)
        phi = combine(
            o,
            self.stroke(
                [
                    ("M", ow * 0.67, 700),
                    ("C", ow * 0.35, 505, ow * 0.46, 145, ow * 0.48, -205),
                ]
            ),
        )
        self.letter("φ", phi, ow)
        self.letter(
            "χ",
            transform(self.outline("x"), d=(xh + 205) / xh, y=-205),
            self.font["hmtx"]["x"][0],
        )
        self.letter(
            "ψ",
            combine(
                transform(self.outline("u"), d=0.84, y=85),
                rect(ow / 2 - t / 2, -205, ow / 2 + t / 2, xh),
            ),
            self.font["hmtx"]["u"][0],
        )
        small_omega = self.stroke(
            [
                ("M", 75, 500),
                ("C", -5, 300, 65, t / 2, 195, t / 2),
                ("C", 300, t / 2, 320, 175, 320, 290),
                ("C", 320, 175, 340, t / 2, 445, t / 2),
                ("C", 575, t / 2, 645, 300, 565, 500),
            ]
        )
        self.letter("ω", small_omega, 640)
        self.letter(
            "ϕ", combine(o, rect(ow / 2 - t / 2, -205, ow / 2 + t / 2, 707)), ow
        )
        self.letter(
            "ϑ",
            self.stroke(
                [
                    ("M", 95, 365),
                    ("C", 185, 240, 435, 235, 465, 420),
                    ("C", 510, 725, 225, 800, 155, 565),
                    ("C", 55, 230, 165, -65, 340, 45),
                    ("C", 440, 110, 500, 235, 480, 335),
                ]
            ),
            570,
        )
        self.letter(
            "ϵ",
            combine(self.outline("c"), rect(90, 259 - t * 0.4, 345, 259 + t * 0.4)),
            ow,
        )
        self.alias_letter("Ω", self.mappings[ord("Ω")])

    def kern_greek(self):
        """Kerning for the drawn Greek letters (not in greek(), which
        source_greek also runs to read the recipes).

        ε σ ς ω are round on the left as o is, so Τε and Τω kern as Το; Γ's
        arm ends on the right as T's does, so Γο kerns as To (Noto Sans and
        Fira Sans set them so). source_greek does the same for α, ά, έ, ώ.

        ϊ and ΐ carry DINish's dieresis, whose right dot reaches past the
        iota, and β δ ζ θ λ ξ rise on the left. Where a dot comes closer than
        DIALYTIKA_KERN_CLEAR, the pair kerns apart, sized so the shipped face
        keeps that white once build_text keeps its share of every kern (Fira
        Sans kerns ϊβ apart too)."""
        from build_text import KERNING_KEPT

        for ch in "εσςω":
            copy_kerning(self.font, self.mappings[ord(ch)], "o", right=False)
        copy_kerning(self.font, self.mappings[ord("Γ")], "T", left=False)
        cmap = {**self.font.getBestCmap(), **self.mappings}
        target = DIALYTIKA_KERN_CLEAR * self.font["head"].unitsPerEm
        pairs = {}
        for a in "ϊΐϋΰ":
            first = cmap[ord(a)]
            left = _ink(self.outline(first))
            advance = self.font["hmtx"][first][0]
            for b in "βδζθλξ":
                second = cmap[ord(b)]
                gap = left.distance(translate(_ink(self.outline(second)), advance))
                kern = ceil((target - gap) / KERNING_KEPT)
                if kern > 0:
                    pairs[(first, second)] = kern
                    self.records[second].setdefault("dialytika_kerns", {})[first] = kern
        add_pair_lookup(self.font, pairs)

    def commit(self):
        for table in self.font["cmap"].tables:
            if table.isUnicode():
                table.cmap.update(self.mappings)
        classes = self.font["GDEF"].table.GlyphClassDef.classDefs
        for name in self.records:
            classes[name] = 1

    def mark_anchors(self):
        """Extend real GPOS base anchors to Greek, including combining accents."""
        for lookup in self.font["GPOS"].table.LookupList.Lookup:
            if lookup.LookupType != 4:
                continue
            for sub in lookup.SubTable:
                for cp, name in self.mappings.items():
                    if self.records[name]["family"] != "Greek":
                        continue
                    bases = self.records[name].get("native_components", [])
                    source = bases[0] if len(bases) == 1 else None
                    if source not in sub.BaseCoverage.glyphs:
                        source = "O" if 0x391 <= cp <= 0x3A9 or cp == 0x2126 else "o"
                    if source not in sub.BaseCoverage.glyphs:
                        continue
                    i = sub.BaseCoverage.glyphs.index(source)
                    rec = deepcopy(sub.BaseArray.BaseRecord[i])
                    dx = (self.font["hmtx"][name][0] - self.font["hmtx"][source][0]) / 2
                    for anchor in rec.BaseAnchor:
                        if anchor is not None:
                            anchor.XCoordinate = round(anchor.XCoordinate + dx)
                    sub.BaseCoverage.glyphs.append(name)
                    sub.BaseArray.BaseRecord.append(rec)
                sub.BaseArray.BaseCount = len(sub.BaseArray.BaseRecord)

    def scripts(self):
        for base, ch in SUB_LETTERS.items():
            if ord(ch) in self.font.getBestCmap():
                continue
            # Keep descenders (j/p) inside the original line box. A small
            # optical lift preserves the common scale without Windows clipping.
            bottom = self.outline(base).computeTightBounds().top() * 0.63
            shift = max(-165, -240 - bottom)
            self.compose(
                ch,
                [(base, (0.63, 0, 0, 0.63, 0, shift))],
                round(self.font["hmtx"][base][0] * 0.63),
                "subscripts",
                "Native lowercase at scientific inferior scale; descenders receive a small baseline lift within the original line box.",
            )
        self.commit()
        cm = self.font.getBestCmap()
        sub = {cm[ord(ch)]: cm[ord(out)] for ch, out in zip("0123456789", "₀₁₂₃₄₅₆₇₈₉")}
        # Figure style/width lookups run earlier in GSUB. Cover those inputs
        # too so subs/sinf still work with lining + tabular figures enabled.
        for word, out in zip(
            [
                "zero",
                "one",
                "two",
                "three",
                "four",
                "five",
                "six",
                "seven",
                "eight",
                "nine",
            ],
            "₀₁₂₃₄₅₆₇₈₉",
        ):
            for suffix in ["", ".tlf", ".osf", ".tosf"]:
                name = word + suffix
                if name in self.font.getGlyphOrder():
                    sub[name] = cm[ord(out)]
        sub.update({cm[ord(ch)]: cm[ord(out)] for ch, out in SUB_LETTERS.items()})
        for ch, out in {
            "+": "₊",
            "-": "₋",
            "−": "₋",
            "=": "₌",
            "(": "₍",
            ")": "₎",
        }.items():
            sub[cm[ord(ch)]] = cm[ord(out)]
        add_feature(self.font, "subs", sub)
        add_feature(self.font, "sinf", sub)
        sup = {
            cm[ord(ch)]: cm[ord(out)]
            for ch, out in {
                "+": "⁺",
                "-": "⁻",
                "−": "⁻",
                "=": "⁼",
                "(": "⁽",
                ")": "⁾",
                "i": "ⁱ",
                "n": "ⁿ",
            }.items()
        }
        add_feature(self.font, "sups", sup)

    def build(self):
        self.greek()
        self.kern_greek()
        self.commit()
        self.mark_anchors()
        self.scripts()
        # The native alternate-a lookup includes both Latin and Cyrillic
        # drawings; make it reachable in localized languages and Cyrillic too.
        register_feature(self.font, "ss02")
        clipped = []
        for name in self.records:
            glyph = self.font["glyf"][name]
            glyph.recalcBounds(self.font["glyf"])
            if (
                getattr(glyph, "yMin", 0) < -self.font["OS/2"].usWinDescent
                or getattr(glyph, "yMax", 0) > self.font["OS/2"].usWinAscent
            ):
                clipped.append(
                    (name, getattr(glyph, "yMin", 0), getattr(glyph, "yMax", 0))
                )
        if clipped:
            raise ValueError((self.style, "scientific glyphs exceed line box", clipped))
        self.font["OS/2"].recalcUnicodeRanges(self.font)
        self.font["OS/2"].recalcAvgCharWidth(self.font)
        return self.records


def extend_science(font, style, radius, to_glyph):
    from curve_cleanup import clean_contour
    from rounding import contours, path_from_contours

    def export(path):
        return to_glyph(path_from_contours([clean_contour(c) for c in contours(path)]))

    records = ScienceBuilder(font, style, radius, export).build()
    for record in records.values():
        record["bounded_curve_refit"] = 0.18
    return records
