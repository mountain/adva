# 0217 — What the address sees, and what the grid already forces

Date: 2026-09-23. Direction: Mingli Yuan. Analysis, checker and note:
deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through his account
as an authorized proxy. Account use is not his authorship, review or endorsement.

Status: one bounded external exact experiment. No Rust witness, no stable API
change, no library admission, no Seal, and no claim about any text.

Base: `79f6353511d736ae743b109f1c573b652eff170a`. Library gitlink:
`73a6af4ac4ed8225366d3c16794e309cff15f51d`.

---

## 1. What was mined elsewhere, and what is not imported

A seventh batch outside this repository — `~/wenyan-relation-learning` at commits
`b4c1df5`, `bc2d4dd`, `5bbad34`, `eec9916`, `0a7bc30`, `81af322`, `cb839b4`,
`321c6d8` and `9554b7f` — closed the line that
[0216](0216-the-magic-hypercube-and-a-cut-the-address-cannot-see.md) had opened.

| Reported there | Their number |
|---|---|
| **the source text states its own address algorithm** | `家一置一，二置二，三置三；部一勿增，二增三，三增六；州一勿增，二增九，三增十八；方一勿增，二增二十七，三增五十四` |
| the calendar is stated in the text too | `三十六策以律七百二十九贊，凡二萬六千二百四十四策`, `七十二策為一日，凡三百六十四日有半` |
| the split at 47/48 against every modulus | only the trivial one works, and they give a proof in two cases |
| the two heads the text pairs across the split | 易 pairs 困 and 井 there; 太玄 pairs 文 with head 7 and 禮 with head 8 |
| one division the text names | the nine 行 of the 三生 chain, `9 行 × 40 日 = 360 日` |
| the river diagram in the text | `一與六共宗，二與七共明，三與八成友，四與九同道，五與五相守`, and the adjacent table uses those numbers |
| a new aperture, **A9** | "a resemblance is not evidence until chance is measured"; their worked case: 552 ratios × 11 targets, best 0.603%, against a same-size null whose median best is 0.106% |
| a correction | an earlier reading of the split as a phase boundary was withdrawn: the position law is exact `81/81`, the phase correlation only `79%` |

**No text and no corpus count is imported.** The formulas, the constants and the
counts are declared in this experiment's contract; the checker verifies their
arithmetic and the structural consequences. No corpus is opened and none of
their measurements is re-run.

## 2. The text states its own address algorithm

This is the batch's most consequential item for this line. Every earlier note
here — [0211](0211-six-places-two-alphabets-and-the-policy-of-a-finite-arithmetic-truth.md),
[0214](0214-what-a-four-trit-address-carries-and-no-shift-pairs-it.md),
[0216](0216-the-magic-hypercube-and-a-cut-the-address-cannot-see.md) — took the
address formula as a **declared** object and said the textual identification was
left to a sourced review. The external record has now produced that source: the
text itself gives the algorithm.

```
家一置一，二置二，三置三
部一勿增，二增三，三增六
州一勿增，二增九，三增十八
方一勿增，二增二十七，三增五十四
```

which is to say `head = 家 + 3(部−1) + 9(州−1) + 27(方−1)`, and that is

```
index = 27·方 + 9·州 + 3·部 + 家      (places counted from zero)
```

The checker confirms the two agree on **all eighty-one heads**, and that the
place weights are the successive multiples of three the text lists: `0,1,2` then
`0,3,6` then `0,9,18` then `0,27,54`.

So the four-place ternary address is no longer an inference from a block of
symbols. It is the map the text states, and the earlier notes' declared object is
the text's own object. That is exactly what 0211 §12 asked for, and this note
records that the request has been met rather than re-deriving it.

## 3. A division the address does see

With the address in hand, the two divisions of the heads can be compared.

The text's own nine-fold series — the nine 行 of the 三生 chain, `9 × 40 = 360`
days — names nine heads. The checker computes which heads have their last two
places at their first value:

```
heads 1, 10, 19, 28, 37, 46, 55, 64, 73      spacing constant at 9
```

and they are **exactly** that set — the fiber of the projection onto the last two
places over `(1,1)`. So:

> the nine-fold series is **definable in the address algebra**: it is fixed by
> **two** of the four places, with the other two running freely over `3 × 3 = 9`
> values.

That is a positive result and it is worth stating next to the negative ones,
because it shows the address algebra is not simply blind to the text's divisions.
It sees this one at a glance — two constraints out of four.

## 4. A division no modulus sees

The split at 47/48 was already shown in 0216 to be invisible to every proper
subset of the four places. This batch asks the neighbouring question: **is it a
congruence?** The checker exhausts all eighty moduli from two to eighty-one:

```
moduli that make {1..47} a union of complete residue classes:   81 only
nontrivial moduli that work:                                     0
moduli that fail, each with a witness pair:                     79
```

`m = 81` is trivial — every residue class is a single head, so every subset
qualifies. So **the split is not a congruence**, and this is a proof rather than a
search failure. Their two-case argument checks out on the data:

* for `m ≤ 34` the tail `{48..81}` is thirty-four consecutive heads, which
  outnumbers the `m` classes, so it carries every class and would have to be the
  whole set;
* for `m ≥ 35` the tail's thirty-four elements are pairwise incongruent, and
  every completion of the complementary classes sends some member back into the
  tail.

Two algebras, two negatives, one split: **not definable by the places, not
definable by a modulus.** Any explanation that lives in either algebra is
excluded, and what remains is the external record's own candidate — a
transmitted editorial boundary — which this experiment neither tests nor
excludes.

## 5. And the split is a translate of a boundary the text does pair

The batch also reports that the text's own pairing chapter sends head 7 across
the split, to head 47, and head 8 to head 48. Written as addresses:

```
head  7 = (0,0,2,0)   head 47 = (1,2,0,1)      displacement (1,2,1,1)
head  8 = (0,0,2,1)   head 48 = (1,2,0,2)      displacement (1,2,1,1)
```

**The same displacement carries both pairs.** The boundary at 47/48 is therefore
the image of the boundary at 7/8 under one operation on the address space — and
that operation is one of the shifts
[0214](0214-what-a-four-trit-address-carries-and-no-shift-pairs-it.md) studied,
so it has order **three**, not two, and carries the heads in three-cycles:

```
7 → 47 → 69 → 7
8 → 48 → 67 → 8
```

with all eighty-one heads split into **twenty-seven** three-cycles.

This is recorded as a structural coincidence in the text's own pairing and not as
an explanation of the split. It does not say why forty-seven; it says that
whichever mechanism put the boundary at 7/8 also put one at 47/48 by the same
displacement, so the two boundaries are not independent facts about the text.

## 6. The river diagram is a quotient by five

The text states the river diagram's pairing outright: `一與六共宗，二與七共明，
三與八成友，四與九同道，五與五相守`, and the adjacent correspondence table uses
exactly those numbers (`一六`, `二七`, `三八`, `四九`, `五五`). The checker
identifies what that pairing is:

* on the **ten** numbers (with ten written as zero) the shift `x ↦ x + 5` is an
  involution with **no fixed point**, and its pairs are `{1,6} {2,7} {3,8} {4,9} {5,10}`;
* restricted to the **nine** numbers, exactly one element — `5` — has its partner
  outside the range, so the fifth pair has only one member present.

**The river diagram is the reduction modulo five, and `五與五相守` is what that
reduction looks like when the partner of five is written outside the list.** The
five labels of the correspondence table are then a function of the residue class
alone, which the checker verifies over all nine numbers.

So the table in the text and the diagram in the text are the same arithmetic
object, and it is a quotient. This matters for the negative results recorded
earlier in this line: the correspondence table **is** in the text, in column
form, with the numbers attached — what failed before was a passage-level
co-occurrence reading of it, which is the method
[0213](0213-gain-coverage-and-the-number-that-was-already-fixed.md) predicted
would fail and whose replacement it named.

## 7. The near miss the grid already forces

The batch reports a calendrical near miss and, in the same breath, records the
new aperture A9: *a resemblance is not evidence until chance is measured.* The
arithmetic here applies it to that very near miss.

The text's own numbers give the calendar exactly:

```
36 × 729 = 26,244 counted units ;  26,244 / 72 = 364.5 days   so one praise is half a day
729 praises = 364.5 days ;  the two extra praises = 1 day ;  the year = 365.5 days
```

so the boundaries between heads are at multiples of `9 × 0.5 = 4.5` days, and the
split at head 47 falls at `423 praises = 211.5` days, dividing the cycle into
`423 + 306 = 729` praises, that is `211.5 + 153 = 364.5` days.

Now the statistic. The twenty-four seasonal nodes sit at `(k−1) · 365.5/24`,
which is `(k−1) · 731/48` days, and the cut's distance to the **nearest** head
boundary is reported as **1.71 days**, about `0.80%` of the node. Two facts
decide what that is worth:

* **The grid forces it.** The boundaries are spaced `4.5` days apart, so **every**
  node lies within `2.25` days of some boundary, whatever the data are. There is
  no set of twenty-four nodes for which this statistic can be large. This is the
  same shape as the covering radius of
  [0213](0213-gain-coverage-and-the-number-that-was-already-fixed.md) §4: a
  maximum-distance statistic bounded by the declared geometry, not by anything
  measured.
* **The reported node is not even the closest.** Exhausting all twenty-four:

| | node | day | gap (days) | relative |
|---|---:|---:|---:|---:|
| closest | 14 | 197.98 | **0.0208** | **0.0105%** |
| median | — | — | — | 0.609% |
| **reported** | **15** | **213.21** | **1.708** | **0.801%** |
| furthest | — | — | 2.104 | 3.42% |

The reported node ranks **fourteenth of twenty-three** by closeness, its gap
(`41/24` days) is *above* the `1.125`-day value an even spread would give, and
**another node is more than seventy-six times closer** — a coincidence far
tighter than the one reported, sitting unnoticed at 197.98 days.

So the near miss is not a near miss. It is a node in the middle of the pack, made
to look close by a grid whose spacing guarantees closeness. This is A9 applied to
the batch that announced A9, which is the right way round: the criterion is worth
exactly as much as it costs its own author.

## 8. What the checker ran

```console
python3 experiments/address_and_scale/checker.py --output experiments/address_and_scale/evidence.json
```

[`checker.py`](../../experiments/address_and_scale/checker.py) uses the standard
library only — integers and `Fraction`; no floating-point value enters any
acceptance test — and its output is compared against the retained
[`evidence.json`](../../experiments/address_and_scale/evidence.json) with timings
removed. The retained run records **91 assertions** over six sections in well
under a second, having exhausted 81 heads twice, 80 moduli with a witness pair
recorded for each of the 79 that fail, 81 heads again for the three-cycle
decomposition, and all 24 calendar nodes. `RLIMIT_CPU`, `RLIMIT_FSIZE` and the
wall alarm are installed; no address-space ceiling is installed because the
checker launches no child process. The checker refuses to overwrite an existing
output path.

Controls that keep the checks from being vacuous:

* the nine-row set is asserted to need **exactly two** place constraints with the
  other two places free, so "the address sees it" is a count and not a claim;
* the congruence result is asserted to have **79** failing moduli each with a
  witness, so the negative is not an empty family;
* the two pairs are asserted to share **one** displacement and the displacement
  to have order **three**, so the translate relation is a computation;
* the ten-number shift is asserted **fixed-point free** and the nine-number
  restriction to leave **exactly one** number without a partner, so `五與五相守`
  is derived rather than quoted;
* the calendar's reach is asserted to be `9/4` days and every node asserted to
  lie within it, so the bound is universal and not an average;
* the reported node is asserted to be **worse than the median** and to be beaten
  by a factor greater than seventy-six, so section 7 is a ranking.

## 9. Residual and non-claims

* **No text and no corpus count is imported.** Every formula and constant here is
  declared in the contract; the checker measures nothing.
* **The address formula is checked against the formula the external record
  reports the text to state**, not against a collated edition. This note does not
  perform that collation and does not claim it. What it records is that the
  declared object of 0211/0214/0216 now has a stated source, and that the two
  agree arithmetically.
* **The two invisibility results are about two declared algebras, not about
  cause.** That the split is invisible to the places and to every modulus does not
  show it has no cause; the external record's own remaining candidate, a
  transmitted editorial boundary, is neither tested nor excluded here.
* **The translate relation is recorded, not explained.** It shows the two
  boundaries are not independent; it does not say why either is where it is.
* **No claim about calendars, seasons or astronomy** beyond the arithmetic of the
  text's own counts, and no claim that the year or the nodes describe a real sky.
* **The near-miss analysis removes one piece of evidence and supplies none.** It
  shows that the reported closeness is what the grid forces and that a closer node
  exists unnoticed; it does not show that no alignment between heads and seasons
  exists.
* **No claim about the river diagram's history.** That its pairing is a quotient,
  and that the text states it, is not a claim about where either came from.
* **No native consequence.** No `SourceId`, observer, aperture, clock, operation
  or `Seal`; the address, the displacement and the quotient are not claimed as
  native structures.
