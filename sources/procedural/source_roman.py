"""Roman numerals, drawn from DINish's own parts.

extend(font, style) adds them to a DINish master that was just loaded, before
DINDOT rounds it, so rounding, spacing, italics and hinting treat them like
DINish's own letters. Every measure is read from the master, so each weight
gets its own strokes. It returns {glyph name: decision}.

Ⅰ to Ⅻ have feet, as DIN 17 and DIN 16 (1940) draw I, II, V, X and VIII:

- The strokes are DINish's own: I's stem, V's arms and X's diagonals, at
  their own weight.
- A foot is a bar with the weight of E's arms across the end of a stroke, at
  the cap height and on the baseline (on V only at the top, where its arms
  end), centred on the stroke where the stroke meets it.
- The white between I's stems is Ш's: DINish's own white between upright
  strokes joined by a bar. Every foot is as long as I's stem and that white,
  so it reaches half the white past a stem on both sides and the feet of
  neighbouring strokes meet and run on as one bar: over and under III, and
  from V's right arm into it, as the sheets draw VIII. In the sheets too the
  feet reach out by half the white between the stems (1/7 h of 2/7 h), that
  white is two thirds of H's counter, as Ш's is in DINish, and every foot has
  the same length, on a diagonal as on a stem.
- The feet on V's two arms, and on X's four ends, stand that same white
  apart, as in the sheets: V and X spread their arms until they do (V at the
  top, X at the top and the bottom, so it stands as wide at both, and as
  wide as V), each arm made wider across by the cosine of its new lean, so
  it keeps its weight.
- Outside its feet a numeral keeps the white E keeps beyond its arms, and on
  V's side, where only a top foot stands, the white T keeps beyond its bar.

The sheets show only I, V and X, and add that Roman numerals may also be
written without feet. Ⅼ Ⅽ Ⅾ Ⅿ are DINish's L, C, D and M.

ⅰ to ⅿ are the lowercase letters as DINDOT sets the word (ⅳ is iv): every
letter where DINDOT's spacing profiles put it in the word (DINish kerns none
of these pairs), with the word's own side bearings. They kern like their
first letter on the left and their last letter on the right.

PROFILE_BASES names the letter whose rounding and spacing profile each
numeral follows: I, V or X for the footed capitals (the stroke that sets the
side bearings), the letter itself for Ⅼ Ⅽ Ⅾ Ⅿ, and for a small numeral the
letter that is not i, or i.
"""

from itertools import pairwise

import skia
from fontTools.misc.roundTools import otRound

from kerning import copy_kerning
from source_cyrillic import _bounds, _clip, _column, _composite, _glyph, _outline, _rect, _runs, _union

CAPITALS = {
    0x2160: "I",
    0x2161: "II",
    0x2162: "III",
    0x2163: "IV",
    0x2164: "V",
    0x2165: "VI",
    0x2166: "VII",
    0x2167: "VIII",
    0x2168: "IX",
    0x2169: "X",
    0x216A: "XI",
    0x216B: "XII",
}
PLAIN = {0x216C: "L", 0x216D: "C", 0x216E: "D", 0x216F: "M"}
SMALL = {cp + 0x10: word.lower() for cp, word in {**CAPITALS, **PLAIN}.items()}


def _name(cp):
    return f"uni{cp:04X}"


def _base(word):
    """The letter a numeral's rounding and spacing profile follows."""
    if len(word) == 1:
        return word
    rest = [c for c in word if c.lower() != "i"]
    return rest[0] if rest else word[0]


PROFILE_BASES = {
    _name(cp): {"I": "I", "V": "V", "X": "X", "L": "L", "C": "C", "D": "D", "M": "M"}[_base(word)]
    for cp, word in {**CAPITALS, **PLAIN}.items()
}
PROFILE_BASES.update({_name(cp): _base(word) for cp, word in SMALL.items()})


def _spacing(char):
    """(width factor, tracking) that build_text gives the letter: its outline
    stretches by the factor and its advance gains the tracking, half a side."""
    from build_text import CONFIG

    rule = CONFIG["profiles"].get(char, CONFIG["default"])
    return rule["width_factor"], max(0, rule["tracking"] + CONFIG["tracking_shift"])


def _final(units, char):
    """A white of DINish `units` beside `char` (a side bearing) as DINDOT sets it."""
    factor, tracking = _spacing(char)
    return units * factor + tracking / 2


def _source(final, char):
    """The DINish white that comes out as `final` in a glyph spaced like `char`."""
    factor, tracking = _spacing(char)
    return (final - tracking / 2) / factor


class _Parts:
    """Per-weight strokes and measures, read from this DINish master."""

    def __init__(self, font):
        self.font = font
        self.cap = font["OS/2"].sCapHeight
        hm = font["hmtx"]
        stem = _crossings(_rings(font, "I"), self.cap / 2)
        assert len(stem) == 1, stem
        self.stem = stem[0]
        # The white between Ш's stems: DINish's own white between upright
        # strokes joined by a bar, as DINDOT stretches Ш
        sha = _runs(_outline(font, "Shacyr"), self.cap / 2)
        assert len(sha) == 3, sha
        counter = sum(b[0] - a[1] for a, b in pairwise(sha)) / 2 * _spacing("Ш")[0]
        self.white = {c: counter / _spacing(c)[0] for c in "IVX"}
        e = _outline(font, "E")
        x0, _, x1, _ = _bounds(e)
        arms = _column(e, (x0 + x1) / 2)
        assert arms[0][0] == 0 and arms[-1][1] == self.cap, arms
        self.bottom = arms[0][1]  # E's lowest arm, from the baseline
        self.top = self.cap - arms[-1][0]  # E's top arm, down from the cap height
        e_side = _final(hm["E"][0] - x1, "E")
        t_side = _final(_bounds(_outline(font, "T"))[0], "T")
        self.side = {c: {"feet": _source(e_side, c), "top foot": _source(t_side, c)} for c in "IVX"}

    def foot(self, base):
        """A foot's length: I's stem and half the white on either side."""
        return self.stem[1] - self.stem[0] + self.white[base]


def _rings(font, letter):
    """DINish's straight-sided `letter` as point rings."""
    glyph = font["glyf"][letter]
    coords, ends, flags = glyph.getCoordinates(font["glyf"])
    assert all(f & 1 for f in flags), (letter, "curves")
    out, start = [], 0
    for end in ends:
        out.append([tuple(map(float, p)) for p in coords[start : end + 1]])
        start = end + 1
    return out


def _crossings(rings, y):
    """Where straight-sided rings cross height y: their ink runs, left to
    right, exactly."""
    xs = []
    for ring in rings:
        for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1]):
            if (ay - y) * (by - y) < 0:
                xs.append(ax + (bx - ax) * (y - ay) / (by - ay))
    xs.sort()
    return list(zip(xs[::2], xs[1::2]))


def _at(p, q, y):
    """x where the line through p and q crosses height y."""
    return p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1])


def _meet(p, q, r, s):
    """Where the line through p and q meets the line through r and s."""
    d = (q[0] - p[0]) * (s[1] - r[1]) - (q[1] - p[1]) * (s[0] - r[0])
    t = ((r[0] - p[0]) * (s[1] - r[1]) - (r[1] - p[1]) * (s[0] - r[0])) / d
    return p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])


def _band(bottom, top, spread_bottom, spread_top, cap):
    """A straight stroke from its bottom end (x0, x1) on the baseline to its top
    end at the cap height, the ends moved apart by their spreads (negative to
    the left), kept at its upright width: an arm that leans further is made
    wider across, by the cosine of its lean."""
    lean = ((top[0] + top[1]) - (bottom[0] + bottom[1])) / 2 / cap
    bottom = [x + spread_bottom for x in bottom]
    top = [x + spread_top for x in top]
    after = ((top[0] + top[1]) - (bottom[0] + bottom[1])) / 2 / cap
    grow = ((1 + after * after) / (1 + lean * lean)) ** 0.5
    ends = []
    for x0, x1 in (bottom, top):
        middle, half = (x0 + x1) / 2, (x1 - x0) / 2 * grow
        ends.append((middle - half, middle + half))
    (b0, b1), (t0, t1) = ends
    return [(b0, 0.0), (t0, cap), (t1, cap), (b1, 0.0)]


def _v(font, cap, spread):
    """DINish's V with its arms spread at the top by `spread` each, their
    bottoms and their weight kept."""
    (ring,) = _rings(font, "V")
    low = sorted(p for p in ring if p[1] == 0)
    high = sorted(p for p in ring if p[1] == cap)
    (crotch,) = [p for p in ring if 0 < p[1] < cap]
    assert len(low) == 2 and len(high) == 4, ring
    middle = (low[0][0] + low[1][0]) / 2
    assert abs((high[0][0] + high[3][0]) / 2 - middle) < 1, ("V is not symmetric", ring)
    # The left arm, from the flat bottom to its top: its inner edge runs on
    # down to the baseline, beyond the crotch.
    inner = _at(high[1], crotch, 0)
    arm = _band((low[0][0], inner), (high[0][0], high[1][0]), 0, -spread, cap)
    mirror = [(2 * middle - x, y) for x, y in reversed(arm)]
    crotch = _meet(arm[3], arm[2], mirror[0], mirror[1])
    return [[(low[0][0], 0.0), arm[1], arm[2], crotch, mirror[1], mirror[2], (low[1][0], 0.0)]]


def _x(font, cap, spread_top, spread_bottom):
    """DINish's X as its two strokes, their ends spread apart at the top and
    at the bottom, their weight kept."""
    (ring,) = _rings(font, "X")
    low = sorted(p[0] for p in ring if p[1] == 0)
    high = sorted(p[0] for p in ring if p[1] == cap)
    assert len(low) == 4 and len(high) == 4, ring
    rising = _band(low[:2], high[2:], -spread_bottom, spread_top, cap)
    falling = _band(low[2:], high[:2], spread_bottom, -spread_top, cap)
    return [rising, falling]


def _union_rings(rings):
    paths = []
    for ring in rings:
        p = skia.Path()
        p.addPoly([skia.Point(*q) for q in ring], True)
        paths.append(p)
    return _union(*paths)


def _solve(gap, want):
    """The spread (each side) that makes gap(spread) == want."""
    lo, hi = -200.0, 400.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if gap(mid) < want:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _element(font, parts, letter, base):
    """A stroke element: its outline as rings, and the middles of its strokes
    where they meet their feet, as {"top": [x], "bottom": [x]}, left to
    right. V and X spread their arms until the feet on their ends stand the
    white apart, as the feet of separate strokes do."""
    cap, apart = parts.cap, parts.foot(base) + parts.white[base]
    top, bottom = cap - parts.top, parts.bottom
    if letter == "I":
        rings = _rings(font, "I")
    elif letter == "V":
        rings = _v(font, cap, _solve(lambda s: _span(_v(font, cap, s), top), apart))
    else:
        spreads = [0.0, 0.0]
        for _ in range(6):
            spreads[0] = _solve(lambda s: _span(_x(font, cap, s, spreads[1]), top), apart)
            spreads[1] = _solve(lambda s: _span(_x(font, cap, spreads[0], s), bottom), apart)
        rings = _x(font, cap, *spreads)
    ends = {"top": _middles(rings, top)}
    if letter != "V":
        ends["bottom"] = _middles(rings, bottom)
    return rings, ends


def _middles(rings, y):
    """The middles of the strokes the rings cross at height y."""
    return [(a + b) / 2 for a, b in _crossings(rings, y)]


def _span(rings, y):
    """How far apart a letter's two strokes stand at height y, middle to middle."""
    middles = _middles(rings, y)
    assert len(middles) == 2, middles
    return middles[1] - middles[0]


def _move(path, dx):
    out = skia.Path(path)
    out.offset(dx, 0)
    return out


def _footed(font, parts, word):
    """The numeral `word` (I, V and X) with feet, as one outline, and its
    advance."""
    base = _base(word)
    foot = parts.foot(base)
    pieces, bars = [], {"top": [], "bottom": []}
    x = 0.0
    previous = None
    for letter in word:
        rings, ends = _element(font, parts, letter, base)
        if previous is not None:
            # this element's feet meet the last one's
            x = previous - ends["top"][0] + foot
        # The strokes end a unit into their feet, so they join them and a
        # steep arm cannot reach out past its foot's end (Bold's X did by 4
        # units when it ran halfway in).
        low = parts.bottom - 1 if "bottom" in ends else -1
        high = parts.cap - parts.top + 1
        pieces.append(_move(_clip(_union_rings(rings), -1000, low, 3000, high), x))
        for level, middles in ends.items():
            bars[level].extend((m + x - foot / 2, m + x + foot / 2) for m in middles)
        previous = x + ends["top"][-1]
    # Feet that meet are one bar. Separate feet stand a whole white apart;
    # DINish's X leans a unit, so its foot can miss its neighbour's by one.
    merged = {}
    for level, runs in bars.items():
        out = []
        for a, b in sorted(runs):
            if out and a <= out[-1][1] + parts.white[base] / 10:
                out[-1][1] = max(out[-1][1], b)
            else:
                out.append([a, b])
        merged[level] = out
    feet = [_rect(a, parts.cap - parts.top, b, parts.cap) for a, b in merged["top"]]
    feet += [_rect(a, 0, b, parts.bottom) for a, b in merged["bottom"]]
    path = _union(*pieces, *feet)
    x0, _, x1, _ = _bounds(path)

    def side(letter):
        return parts.side[base]["top foot" if letter == "V" else "feet"]

    # whole units, so the left side bearing is the outline's own
    left, right = round(side(word[0])), side(word[-1])
    path = _move(path, left - x0)
    return path, x1 - x0 + left + right, merged


def _small(font, word, style):
    """[(letter glyph, x)] for the word as DINDOT sets it, and the advance,
    for a glyph spaced like the word's profile letter.

    build_text stretches each letter by its width factor, gives it its
    tracking and, in Bold, widens it between its stems (CONFIG growth); the
    numeral gets its profile letter's factor and tracking and grows as one.
    So each letter's middle is put where the word sets it, and the advance is
    the word's."""
    from build_text import CONFIG

    hm, gl = font["hmtx"], font["glyf"]
    grow = CONFIG["growth"].get(style, 1)
    stem = CONFIG["ink_widths"][style]["lowercase"][0]
    factor, tracking = _spacing(_base(word))
    middles, x = [], 0.0
    for ch in word:
        f, t = _spacing(ch)
        g = gl[ch]
        middle = (g.xMin + g.xMax) / 2
        # build_text's growth: stretched by grow about the stem's middle
        middles.append(x + t / 2 + f * (middle * grow - (grow - 1) * (g.xMin + stem / 2)))
        x += hm[ch][0] * f + t + (grow - 1) * f * (g.xMax - g.xMin - stem)
    first = gl[word[0]]
    start = (middles[0] - tracking / 2 + (grow - 1) * factor * (first.xMin + stem / 2)) / factor
    start -= (first.xMin + first.xMax) / 2 * grow
    left = start + first.xMin
    shift = tracking / 2 - (grow - 1) * factor * (left + stem / 2)
    placed = [(word[0], start)]
    for ch, m in zip(word[1:], middles[1:]):
        g = gl[ch]
        placed.append((ch, (m - shift) / (factor * grow) - (g.xMin + g.xMax) / 2))
    last = gl[word[-1]]
    right = placed[-1][1] + last.xMax
    advance = (x - tracking - (grow - 1) * factor * (right - left - stem)) / factor
    return placed, advance


# The small numerals, whose letters build.py puts where the masters draw them.
SET_AS_TEXT = [_name(cp) for cp in SMALL]


def _letters(font, style):
    """[(codepoint, name, glyph, advance, decision, kerning models)]."""
    parts = _Parts(font)
    out = []
    for cp, word in CAPITALS.items():
        path, advance, feet = _footed(font, parts, word)
        joined = [f"{len(feet[k])} {k} bar{'s' if len(feet[k]) != 1 else ''}" for k in ("top", "bottom") if feet[k]]
        out.append(
            (
                cp,
                _name(cp),
                _glyph(path),
                advance,
                (
                    f"DIN 17's {word} with feet: DINish's {', '.join(sorted(set(word)))} strokes as far apart as"
                    f" Ш's, each end on a foot of E's arm weight as long as the stem and that white;"
                    f" the feet make {' and '.join(joined)}."
                ),
                None,
            )
        )
    for cp, word in PLAIN.items():
        out.append(
            (
                cp,
                _name(cp),
                _composite(font, [(word, 0, 0)]),
                font["hmtx"][word][0],
                f"DINish's {word}: DIN 16 and 17 draw feet on I, V and X only.",
                (word, word),
            )
        )
    for cp, word in SMALL.items():
        placed, advance = _small(font, word, style)
        # Its own metrics: build.py moves the letters after rounding.
        glyph = _composite(font, [(ch, otRound(x), 0) for ch, x in placed], None)
        out.append(
            (
                cp,
                _name(cp),
                glyph,
                advance,
                f"DINish's {' '.join(word)} as DINDOT sets the word {word}, spaced like {_base(word)}.",
                (word[0], word[-1]),
            )
        )
    return out


def extend(font, style):
    """Add the numerals to a freshly loaded DINish master; return
    {glyph name: decision}."""
    cmap = font.getBestCmap()
    letters = [r for r in _letters(font, style) if r[0] not in cmap]
    order = list(font.getGlyphOrder())
    decisions = {}
    for cp, name, glyph, advance, decision, _ in letters:
        assert name not in font["glyf"].glyphs, name
        order.append(name)
        font.setGlyphOrder(list(order))
        font["glyf"][name] = glyph
        glyph.recalcBounds(font["glyf"])
        font["hmtx"][name] = (otRound(advance), otRound(getattr(glyph, "xMin", 0)))
        decisions[name] = decision
    for table in font["cmap"].tables:
        if table.isUnicode():
            for cp, name, *_ in letters:
                table.cmap[cp] = name
    if "GDEF" in font and font["GDEF"].table.GlyphClassDef:
        defs = font["GDEF"].table.GlyphClassDef.classDefs
        for _, name, *_ in letters:
            defs[name] = 1
    for _, name, _, _, _, models in letters:
        if models:
            left, right = models
            copy_kerning(font, name, left, left=True, right=False)
            copy_kerning(font, name, right, left=False, right=True)
            if left == right:
                decisions[name] += f" Kerns as {left}."
            else:
                decisions[name] += f" Kerns as {left} on its left side and {right} on its right."
    font["OS/2"].recalcUnicodeRanges(font)
    return decisions
