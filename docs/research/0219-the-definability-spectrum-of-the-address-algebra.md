# 0219 — The definability spectrum of the address algebra

Date: 2026-09-23. Direction: Mingli Yuan. Analysis, checker and note:
deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through his account
as an authorized proxy. Account use is not his authorship, review or endorsement.

Status: one bounded external exact experiment. No Rust witness, no stable API
change, no library admission, no Seal, and no claim about any text.

Base: `79f6353511d736ae743b109f1c573b652eff170a`. Library gitlink:
`73a6af4ac4ed8225366d3c16794e309cff15f51d`.

---

## 1. What this answers

Note 0218 proved a lower bound: a set of heads definable by `k` of the four
ternary places has a size divisible by `3^{4−k}`, so a division whose size is not
divisible by three needs all four places. That theorem says how many places a
division *needs*. It does not say **how many rival divisions were available at
that price** — and without that, "the nine heads are a block of two places" is
an assertion with no denominator.

This note supplies the denominator, and the denominator turns out to say
something I did not expect when I started. Three results:

1. **The spectrum has an exact shape**, `|𝔸_S| = 2^{3^{|S|}}`: two, eight, five
   hundred twelve, one hundred thirty four million, and the whole power set.
2. **The union of all algebras up to two places is exactly 3014 sets**, small
   enough to enumerate in full — and the union beyond two places is not
   enumerable at this budget, which is stated rather than hidden.
3. **The "prior" I set out to compute is a bad measure of surprise**, and the
   arithmetic says so on its own: the smallest prior in the table belongs to the
   *coarsest* division, and a prior can be made arbitrarily small by choosing a
   weak level rather than a remarkable one. §5 is that argument.

**No text and no corpus count is imported.** The address space and the eight
declared divisions are in this experiment's contract. No corpus is opened.

## 2. The spectrum, level by level

The eighty-one heads are the points of `Z₃⁴`; a subset `S` of places induces a
partition into `3^{|S|}` blocks of `3^{4−|S|}` heads, and `𝔸_S` is the algebra of
unions of those blocks.

> **Spectrum.** `|𝔸_S| = 2^{3^{|S|}}`, depending only on `|S|`.

| `|S|` | subsets `S` | blocks per partition | block size | `|𝔸_S|` |
|---|---|---|---|---|
| 0 | 1 | 1 | 81 | 2 |
| 1 | 4 | 3 | 27 | 8 |
| 2 | 6 | 9 | 9 | 512 |
| 3 | 4 | 27 | 3 | 134 217 728 |
| 4 | 1 | 81 | 1 | 2 417 851 639 229 258 349 412 352 |

Two things follow, and both matter for how far this line can be pushed.

**The growth is doubly exponential in the level.** One extra place multiplies
the number of blocks by three and the algebra by a factor of `2^{2·3^k}`: from
`2^9 = 512` at two places to `2^{27} = 134 217 728` at three. So the coarse levels
are tiny and the fine levels are not.

**The enumerable window is exactly levels 0, 1 and 2.** To enumerate the union
at level `k` this checker must build every algebra of that level: 1, 4, 6, 4 and
1 of them. At level 2 that is six algebras of five hundred twelve sets each —
3072 set unions, nothing. At level 3 it is four algebras of `2^{27}` sets each,
about `5.4 · 10^8` sets, which is beyond this budget; and at level 4 the single
algebra *is* the power set, `2^81` sets. The contract therefore fixes
`exhaustion_level = 2` and the levels above it are **counted, not enumerated**,
with the consequence taken up in §4.

## 3. The union up to two places, enumerated

Eleven algebras — one at level 0, four at level 1, six at level 2 — have
`2 + 4·8 + 6·512 = 3106` sets between them. Their union has **3014**, so 92 sets
appear in more than one algebra. The algebras are nested and the nesting is
strict: adding a place to `S` always enlarges `𝔸_S`, and two different single
places share only the empty set and the whole set.

The cumulative union is exactly

```
|𝔸_∅ ∪ ⋃_{|S|=1} 𝔸_S| = 26        |⋃_{|S|≤2} 𝔸_S| = 3014
```

and the size distribution over those 3014 sets is

| size | 0 | 9 | 18 | 27 | 36 | 45 | 54 | 63 | 72 | 81 |
|---|---|---|---|---|---|---|---|---|---|---|
| count | 1 | 54 | 216 | 480 | 756 | 756 | 480 | 216 | 54 | 1 |

Three remarks, in order of how much they are worth.

- **Every size is a multiple of nine**, which is the 0218 theorem read the other
  way: a set expressible at two places is a union of nine-element blocks. The
  table has ten rows because the multiples of nine in `[0, 81]` are ten.
- **The distribution is symmetric** — `d(s) = d(81−s)` — and that is *forced*,
  not found: the complement of a set expressible by `S` is expressible by `S`.
  It is reported as a consistency check on the enumeration and not as a result.
- **The coarse window is minuscule.** 3014 sets out of `2^81` is a fraction of
  about `1.2 · 10^{−21}`, while a *single* three-place division already has
  134 217 728 sets. What is expressible at one or two places is a vanishing
  sliver of what is expressible at three.

## 4. Above two places: counted, not seen, and almost always vacuous

For a level that is not enumerated the checker falls back on exact binomial
counting per subset: a level-`k` partition has `3^k` blocks of size `3^{4−k}`, so
the number of its unions of size `s` is `C(3^k, s / 3^{4−k})` when `3^{4−k}`
divides `s`, and zero otherwise, summed over the `C(4,k)` subsets. **The four
subsets at level 3 overlap, and the overlaps are not subtracted**, so the level-3
figures are upper bounds for the union and not counts of it. For size nine at
three places that sum is `4 · C(27,3) = 11700`, against the *exact* 54 at two
places and `C(81,9) = 260 887 834 350` sets of that size altogether: the true
level-3 count lies between 54 and 11700 and this experiment does not decide
where.

At level 4 the algebra is the whole power set, and there the fallback is not an
approximation but the exact answer: **every** set of heads is expressible, so
`μ(A) = 4` carries no information whatever. That is worth stating plainly
because the 0218 theorem is most often invoked at `μ = 4`: the cut, the two
prison heads and every singleton are all "needing four places", and all that
says is that their sizes are not divisible by three. Under the reading of this
note, `μ = 4` is the *vacuous* end of the spectrum, and `μ = 2` with a declared
size is the informative end.

## 5. Pricing a division, and why the price is not what it looks like

For a declared division `A` the price is

```
π(A) = (number of sets of size |A| expressible at level ≤ μ(A)) / C(81, |A|)
```

which is the share of same-size sets that a division of that size could have
had for free at the level `A` is credited with. The eight declared divisions:

| division | size | μ | rivals of that size | all sets of that size | π |
|---|---|---|---|---|---|
| all heads | 81 | 0 | 1 | 1 | 1 |
| first quarter | 27 | 1 | **12** | 2 306 279 447 501 851 002 720 | **1 / 192 189 953 958 487 583 560** |
| nine district representatives | 9 | 2 | 54 | 260 887 834 350 | 3 / 14 493 768 575 |
| three quarter representatives | 3 | 3 | 108 | 85 320 | 1 / 790 |
| cut before | 47 | 4 | — | — | 1 |
| cut after | 34 | 4 | — | — | 1 |
| two prison heads | 2 | 4 | — | — | 1 |
| orbit of seven | 3 | 4 | — | — | 1 |

The nine are one of **54** nine-element sets expressible at two places out of
`260 887 834 350` of that size: an exact ratio of `3 / 14 493 768 575`, about one
in 4.83 billion. That is the denominator I wanted.

**And it does not mean what I wanted it to mean.** The smallest price in the
table is not the nine's. It is the first quarter's, `1 / 192 189 953 958 487 583
560` — about eleven orders of magnitude smaller — and the reason is not that the
quarter is a more remarkable division but that **level one is a weaker level**.
The numerator of a price is a count *inside a level*, so it is bounded by the
size of that level:

```
π(A) ≤ |𝔸 at level μ(A)| / C(81, |A|),     2 + 4·8 + 6·512 → 2, 26, 3014.
```

Level one contains 26 sets in total, of which 12 have size 27; the quarter is one
of those 12. Level two contains 3014 sets, of which 54 have size 9. A price is
therefore small exactly when the level is small. Anyone can obtain an
arbitrarily impressive-looking price by choosing a coarse level: at level 0 the
price of the single set of size 81 is 1, but at level 1 a set of size 27 already
costs one in `1.9 · 10^{20}` *no matter which of the twelve it is*. **The price
measures the level, not the division.** It prices definability, as promised in
the contract, and it explicitly cannot be read as a measure of how surprising,
intended or meaningful a division is.

This is the second time in this line that a number I computed turned out to be
about the wrong object. 0218 corrected a coincidence price upward by a factor of
33 because the property in question hit 8.6 heads rather than one. Here the
correction is conceptual and larger: the quantity is monotone in the weakness of
the level, so its ordering is close to *backwards* from the ordering one would
want as a surprise measure. Under a uniform null over subsets of a fixed size —
the null 0218 used — every same-size division has the same probability, and the
differences between these ratios are entirely differences between levels.

## 6. A number this checker got wrong, and the fix

The first run of `definable_of_that_size` took its numerator from the union of
*all* algebras up to the exhaustion level rather than from the union at the
declared division's own level. For the first quarter, whose `μ` is 1, it
therefore reported **480** rivals — the count of size-27 sets expressible at *two*
places — instead of the correct **12**. The error is recorded here and in the
contract's residual rather than silently repaired: the field
`the_quarter_count_moved_from_480_to_12_when_the_level_was_restricted` is in the
evidence, and the checker now also asserts the corrected numerator against the
size of level one.

The other seven rows are unaffected and why is worth saying, because it is the
reason the error was invisible. Level 2 is the exhaustion level, so its row was
already using the right union. Levels 3 and 4 do not use the union at all. Level
0's union and the level-2 union agree on the single set of size 81. The quarter
was the only declared division whose `μ` sits strictly below the exhaustion
level.

The corrected count is also the one that can be checked by hand: a one-place
division has three blocks of 27; there are four places; and no two of those
twelve blocks coincide, because the fibre of `π_S` through a point is the
coordinate line in the one direction `S` omits, which determines `S`.

## 7. Where the declared divisions sit, recorded and not explained

Of the six two-place partitions, exactly **one** has a block equal to a declared
division: `(2, 3)`, whose block containing the first head is the nine. The three
quarter representatives are a block of `(1, 2, 3)`, and the first quarter a block
of `(0)`. The cut's two sides of sizes 47 and 34 are unions of blocks of all four
places and of nothing smaller — they are not blocks at any level, which is what
the parity of 47 and 34 forces.

So the organisation runs through the **last** places: the nine are a fibre of the
projection onto places 2 and 3, the three of the projection onto 1, 2 and 3, the
quarter of the projection onto place 0 alone. In the vocabulary of the earlier
notes those are `(部, 家)`, `(州, 部, 家)` and `(方,)`. This is **recorded and not
explained**: the experiment measures the address algebra and offers no reason why
a division a text names should align with the last coordinates rather than the
first, and no test of that alignment is performed here. The names "quarter" and
"district" are conveniences carried over from the earlier notes; the objects
measured are coordinate sets.

One placement fact is a real constraint on any story: only one of the six
two-place partitions has a declared block, so the alignment is not the generic
outcome of "some pair of places happens to match something". The 54 nine-element
rivals are spread six to a partition, one of which is the declared one, and each
rival belongs to exactly one two-place partition.

## 8. What the checker ran

`experiments/definability_spectrum/checker.py` against
`experiments/definability_spectrum/contract.json`, five sections, **98
assertions**, `ExternalExactPass`, in 0.13 s wall.

`RLIMIT_CPU`, `RLIMIT_FSIZE` and the wall alarm are installed; **no
address-space ceiling is installed**, because this checker launches no child
process — the same convention 0211 had to adopt after its first version broke
the frozen resource inventory. An existing output file is refused, never
overwritten.

`tests/python/test_definability_spectrum.py` re-runs the checker in a temporary
directory and compares the mathematical payload of the fresh run with the
retained evidence, section by section, with timing and platform keys removed.
No floating-point value enters any acceptance test: the prices are compared as
`Fraction`s, and the `prior_float` field in the evidence is never read by a test.

## 9. Residual and non-claims

- **No text and no corpus count is imported.** The address space and the eight
  divisions are declared in the contract.
- **The price is a ratio inside the address algebra, not a p-value for any
  text.** The address formula is reported elsewhere to be the text's own, so
  address-expressibility and the text's naming are not independent, and this
  experiment neither tests that independence nor concludes from it. §5 shows the
  ratio is also monotone in the weakness of the level, which makes it a worse
  candidate for evidence, not a better one.
- **No statistical claim of any kind is made.** There is no null model here, no
  threshold and no significance; the sweep that had one is 0218, and its uniform
  null was already shown to under-predict for arithmetic properties.
- **The union is enumerated exactly only to two places.** The level-3 figures are
  per-subset binomial sums, **the overlaps are not subtracted**, and the true
  level-3 union lies between 54 and 11700 for size nine. Nothing here reports a
  level-3 union count as exact.
- **`μ = 4` is vacuous.** The four-place algebra is the whole power set, so a
  division needing four places meets every set of its size and its price is 1.
  Any argument that leans on a division "needing all four places" is leaning on
  a divisibility fact about its size and nothing more.
- **The organisation by the last places is recorded and not explained**, and no
  claim is made that coordinate expressibility is the right notion of structure
  for any purpose, or that any division is intended by anyone.
- **No SourceId, observer, aperture, clock, operation, native witness or Seal is
  created**, and no claim is promoted beyond `bounded-experiment`.

## 10. What changed in the repository

- `experiments/definability_spectrum/checker.py`, `contract.json`,
  `evidence.json` — the bounded experiment, 98 assertions.
- `tests/python/test_definability_spectrum.py` — twelve tests over the retained
  evidence, the fresh-run payload, the no-overwrite rule, the spectrum, the
  lattice, the prices, the placement, the rivals, the contract's protected list,
  this note's residual, and the registered claim.
- `docs/claims.toml` — `adva.bounded-experiment.definability-spectrum.v0`.
- `docs/research/README.md` — this note added to the index and the numbered
  count advanced.
