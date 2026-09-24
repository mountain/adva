# 0214 — What a four-trit address carries, and no shift pairs it

Date: 2026-09-23. Direction: Mingli Yuan. Analysis, checker and note:
deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through his account
as an authorized proxy. Account use is not his authorship, review or endorsement.

Status: one bounded external exact experiment. No Rust witness, no stable API
change, no library admission, no Seal, and no claim about any text.

Base: `79f6353511d736ae743b109f1c573b652eff170a`. Library gitlink:
`73a6af4ac4ed8225366d3c16794e309cff15f51d`.

---

## 1. What was mined elsewhere, and what is not imported

A fourth batch of work outside this repository — `~/wenyan-relation-learning` at
commits `1b0b159`, `51eb610`, `91f0107`, `c9b4fcb`, `3bc137e`, `cad008c` and
`14c1353` — went directly at the structure
[0211](0211-six-places-two-alphabets-and-the-policy-of-a-finite-arithmetic-truth.md)
had described abstractly. What they established and reported:

**Citation.** That record is the project author's own, and its git repository is
public: <https://github.com/mountain/wenyan-relation-learning>. It carries the
transcribed classical text at `data/corpus/works/太玄經.json`, a transcript-layer
file that names its source site as `zh.wikisource.org` and records its own
licence basis, whose substance is: the underlying classical work is public domain
by age, and what is taken from Wikisource is **its transcription** — the choice of
recension, the modern punctuation, the paragraphing and the character forms —
with attribution recorded per section. The material below is carried from named
commits of that record: the head symbols, the address table, the difference
histogram, the two named pairs and the two prose sentences quoted in §1 and §2
are from `91f0107`; the Jaccard figures in §7 are from `c9b4fcb`; the 先天
result is from `1b0b159`; the 品第 demotion is from `cad008c`; the `naming`
construction is from `14c1353`. The record is at commit
`cfb6e4dc18425312447b01efd75b646d2ab1473e` when this note was written.

| Reported there | Their number |
|---|---|
| the head symbols are the address: symbol `U+1D306+i` is head `i+1`, with `i = 27(方−1) + 9(州−1) + 3(部−1) + (家−1)` | the transmitted head order **is** the coordinate order — 中 `1111`, 周 `1112`, 礥 `1113`, 閑 `1121`, 事 `1333`, then 更 `2111` into the second 方 |
| the 玄衝 chapter read as differences in `Z₃⁴` | `(2,2,2,0)` 24 pairs, `(1,1,1,1)` 13, then `(1,2,2,1)` 6, `(2,1,2,0)` 6, `(1,2,2,0)` 6, `(2,2,2,1)` 5; 窮↔毅 = `(2,2,2,0)`, 釋↔積 = `(2,1,1,0)` |
| how many pairs the extraction reported, across its own revisions | 69 (cross-sentence pairing), 35 (sentence-internal), 126 resolving and 131 consecutive in one section, 133 de-duplicated |
| testing 玄衝 with a character-bigram Jaccard | 衝 pairs mean 0.0431, **mean percentile 44.2%**, 38.1% above the overall mean; all pairs mean 0.0442, median 0.0433 — so the paired heads are no more alike than random pairs, and they state that an opposition relation needs its own baseline |
| 太玄 has the 先天 order only | established by the head order being the coordinate order while the transmitted 易 order is not its binary coordinate order |
| their open question on the two interfaces (quoted verbatim from `91f0107`) | "3⁴ = 81 against 2⁶ = 64 forces a NON-bijective map, so the question is what structure it preserves … not whether it exists" |
| a new construction declared | `naming`, one role, +7,258 readable passages, **0 changed, 0 superseded**, dispersion 113 works, top-3 share 0.304; the label budget of 32 not spent because the frame carries a single role |
| 品第 demoted | in 詩品, the archetypal ranking work, a sentence-level scan found **4** passages, because the ranking lives in section titles; the class had scored 1,939 corpus-wide |

**No text and no corpus count is imported into the checker or into any acceptance
test here.** What this note does carry is a citation rather than a silence: the
two sentences quoted verbatim above and in §2 are the external record's own prose,
quoted from the named commit, and the material of the first two table rows and the
last row of the histogram is now **declared** in this experiment's contract — the
six head names with their head numbers and addresses, the four named addresses,
and the six histogram boxes with their multiplicities and the two named pairs. The
checker recomputes the address index of each declared head and the tetragram
codepoint of each, recomputes each named pair's difference from the declared
addresses, and checks every declared histogram box for order and for its place in
the tally. No corpus file is opened and no measurement of theirs is re-run: the
counts stay declared numbers, and the only thing computed from them is their
arithmetic.

## 2. In exponent three no nonzero shift is a pairing

The 太玄 address space is `Z₃⁴`: eighty-one heads, each a `(方,州,部,家)`
quadruple. A pairing of it, read as an operation on the addresses, is naturally
written as a difference: `y = x + v`. The exhaustive check settles what that can
be:

```
shift orders in Z₃⁴ :  order 1 → 1 shift (the identity)
                        order 2 → 0 shifts
                        order 3 → 80 shifts, each with 27 three-cycles
```

**No nonzero shift of the ternary address space is an involution.** Every one of
the eighty nonzero shifts is fixed-point-free of order three and cuts the space
into twenty-seven three-cycles. The reason is one line of arithmetic:

> `x ↦ x + v` is an involution exactly when `2v = 0`. Modulo two this holds for
> **every** `v`; modulo three, `2` is invertible, so it holds only for `v = 0`.

The binary interface is the exact opposite case, and the contrast is why the
earlier note's operators work where these cannot:

| interface | shifts | involutions among them |
|---|---:|---|
| `Z₂⁶`, the six-line configurations | 64 | **63** — every nonzero shift |
| `Z₃⁴`, the four-place head addresses | 81 | **0** — none but the identity |

So the 易's operator algebra — 錯 as a shift by the all-ones vector, 变 as a
shift by a unit vector, both involutions, both commuting as translations do —
exists **because the binary interface has characteristic two.** The analogous
operation on the ternary address cannot be a shift of any kind: the group has
exponent three, so the difference of a pair is an element of order three, and
twenty-seven three-cycles are not forty pairs.

This is the answer to what the 玄衝 difference histogram can and cannot be. Both
of the two dominant differences, `(2,2,2,0)` and `(1,1,1,1)`, are of order three
(`2·(2,2,2,0) = (1,1,1,0) ≠ 0`), and so is every other difference the histogram
could contain. **A histogram of differences cannot describe a pairing here at
all**, not because the extraction was wrong but because differences of order
three are the wrong invariant for a map of order two. The external record's own
suspicion — quoted verbatim from commit `91f0107`: "either the rule is not unique
or my extraction merges pairs that are not pairs" — is joined here by a structural
reason that does not depend on the extraction.

Two details of the declared histogram are worth recording, because the checker
computes them rather than taking them on trust. Every declared box has a nonzero
difference and therefore order three, and the six boxes add up to **60** pairs,
which matches none of the reported totals: the record's tally is over its 133
de-duplicated pairs while other revisions report 69, 126 and 131, so the six boxes
describe one extraction's dominant boxes rather than all reported pairs. And of
the two named pairs only one lands in a declared box — 窮↔毅 is `(2,2,2,0)`, the
dominant box, while 釋↔積 is `(2,1,1,0)`, which **is not one of the six boxes**.
That is the record's own point, and the checker confirms it arithmetically from
the declared addresses: the difference of 釋 and 積 is a vector the dominant rule
does not produce. Nothing here says that difference is unexplained; what is
established by computation is that it is not one of the declared boxes.

## 3. What a pairing of eighty-one heads is forced to be

Three exact constraints follow from the arithmetic alone, before any text is
consulted:

* **At most forty pairs.** A pairing's orbits have size one or two, so
  `⌊81/2⌋ = 40` is the ceiling.
* **At least one fixed point.** The orbit sizes of an involution are one and two;
  if every orbit had size two the total would be even, and 81 is odd. So the
  number of fixed points is odd, hence at least one.
* **Four of the five reported pair counts exceed the ceiling.** 69, 126, 131 and
  133 are all greater than 40. Only the sentence-internal count of 35 is
  admissible, and the external record reports that revision as the one that
  looked too small.

So the counting alone says the reported pair lists cannot be the edge set of a
pairing of the 81 heads — the same conclusion the external record reached by
inspecting its own extraction, obtained here without reading the chapter.

## 4. What four ternary places can carry, and what six can

The open question the external record left is precisely a capacity question
about the two interfaces, and it has an exact answer. There are `3⁴ = 81` head
addresses and `2⁶ = 64` six-line configurations.

**Reading heads into configurations.** Counting alone forces a collision:
`⌈81/64⌉ = 2`, so some binary word receives at least two heads. If the reading
must be *placewise* — each ternary place allotted some binary places — the bound
is worse:

```
counting bound on the largest fibre              2
placewise bound, every place read                4     (allocation 2,2,1,1)
placewise bound, a place may be ignored          3
```

A place given one binary place can distinguish at most two of its three values,
and six places over four ternary places cannot give everyone two.

**Reading configurations into heads.** Here the direction matters, and it is the
one their question is about:

```
coordinate-wise, one bit per place      16 of 64
coordinate-wise, best allocation (2,2,1,1)   36 of 64 = 9/16
unconstrained injection                 64 of 64, and it is not coordinate-wise
information-optimal binary places       7      (⌈log₂ 81⌉)
```

The "of 64" in the first two rows is the denominator of the share, not a count of
binary words: the reading reaches 16 of the 81 addresses under one bit per place
and 36 under the best allocation, and those are shares `16/64 = 1/4` and
`36/64 = 9/16` of the sixty-four words. **The 16 is now constructed rather than
asserted.** The checker builds the reading explicitly — six binary places
available, four ternary places, one binary place allotted to each and the two
leftover places therefore unusable — runs it over all sixty-four words, and
counts the distinct addresses in its image, which is 16; it checks that the two
unused places do not change the image, and that the allocation bound computed with
one bit allowed per place agrees with the constructed image. The earlier version
of this file wrote `2 ** 4` and asserted it was sixteen, which was an identity in
the source text rather than a measurement of a reading.

An injection `Z₂⁶ ↪ Z₃⁴` **does** exist — 64 < 81 — and the checker exhibits one
explicitly by writing each word as a four-digit base-three numeral. It is not
coordinate-wise, and no coordinate-wise map can reach past 36 of the 81
addresses. So:

> Whatever a 方州部家 ↔ 六爻 correspondence is, **it cannot be place-to-place.**
> A coordinate-wise reading carries at most 36 of the 64 configurations, and the
> one-bit-per-place reading carries 16. Carrying all 64 requires the address to
> mix coordinates.

And the tie back to 0211 closes it. There the *six-place* ternary address was
shown to carry all 64 configurations **isometrically, on its `{0,1}` subcube** —
all six places used. Here the *four head places* carry 16 placewise and 36
coordinate-wise. So the correspondence has room at six places and not at four:
**the four 方州部家 places are not where the six 爻 fit; the six-place address is.**

## 5. The carry profile of a coordinate order

If the transmitted head order is the coordinate order — which the external
record established character for character — then its step structure is not a
matter of opinion. The exhaustive carry profile of the four-place ternary
odometer:

```
changes 1 place   54 of 81   = 2/3
changes 2 places  18 of 81   = 2/9
changes 3 places   6 of 81   = 2/27
changes 4 places   3 of 81   = 1/27    (the last two are 2·1 + 1 for the wrap)
```

with the closed form `(b−1)·b^{n−j}` for `j` below the place count and `b` at it,
verified against the exhaustion. For the six-place binary odometer the same
closed form gives `32, 16, 8, 4, 2, 2` out of 64.

**This is a fingerprint, not a collation.** A transmitted order claimed to be
the coordinate order must reproduce `54/18/6/3`; an order that does not is not
that order. The external record says its head order is this corpus's and was not
collated against a transmitted table; the profile is the arithmetic that such a
collation would have to satisfy.

## 6. Four step relations, four different shares

The same closed-form exercise makes a table worth keeping. Four declared step
relations now exist across the two interfaces, and they do not agree about what
one step is:

| step relation | steps | changing exactly one place | share |
|---|---:|---:|---:|
| the six-line single-change relation (0211) | 384 | 384 | **1** |
| the six-place binary odometer | 64 | 32 | **1/2** |
| the four-place ternary odometer | 81 | 54 | **2/3** |
| the declared position successor (0211) | 648 | 486 | **3/4** |

Four exact rationals, no two alike. 0211 §7 made the point with two of them; the
coordinate orders add the other two, and the conclusion is the same and sharper:
**"one step" is not one relation**, and which one is meant decides whether a
single observation changes one thing or several.

## 7. A similarity measure cannot test an opposition

The external record tested 玄衝 — a chapter whose name means *clash* — with a
character-bigram Jaccard, and correctly refused to read the result as support:
the paired heads came out no more alike than random, which for an opposition
relation is *expected* rather than anomalous. The arithmetic of that refusal:

```
extracted pairs                          126
mean percentile of the paired set        0.442, against 1/2 expected under exchangeability
deviation                                29/500
independent-pair variance of the mean    1/(12·126) = 1/1512
deviation in standard errors             √(158949/31250) ≈ 2.26
average appearances of a head            2·126/81 = 28/9 ≈ 3.11
```

Even under the independence assumption the deviation is under 2.3 standard
errors, and the arithmetic shows the assumption is false: 126 pairs over 81
heads means a head appears about three times on average, so the pairs share
vertices and are strongly dependent. No significance is claimed — by the
external record or here.

The structural statement is the one that matters, and it is not statistical:

> A similarity measure assigns low values both to pairs that are **opposite**
> and to pairs that are **unrelated**. It therefore cannot distinguish the two,
> and a similarity statistic that comes out low is not evidence for opposition.
> Testing an opposition relation needs an opposition baseline, which was not
> built.

**What of that statement is computed, and what is not.** The checker now carries a
declared witness: two pairs of declared attribute sets, one the contract declares
*opposite* and one it declares *unrelated*, scored with the same Jaccard ratio the
external record used. The two pairs have different attribute sets and different
sizes, and the computed scores are equal — both `1/4`, a low but nonzero value —
so a score of `1/4` is consistent with either declared relation and cannot be read
as evidence for one of them. The reported field is the negated result of that
comparison, so it flips if the declared witness ever separates them. **That is an
instance and not a proof of the general statement.** The general claim — that *no*
similarity measure can separate opposition from unrelatedness — is not what is
computed here; what is computed is that one declared measure, on one declared
opposite pair and one declared unrelated pair, returns the same low value. The
general statement is a **declared observation** that the arithmetic illustrates,
and the note does not present it as a checked theorem.

This is 0212's theme in a new place: the null has to be the right one, and here
the wrong null is not merely weak, it is blind to the hypothesis in principle.

## 8. The counting unit decides what is visible

The external record demoted 品第 — ranking vocabulary — from a construction to
document structure, because in 詩品, the archetypal ranking work, a
sentence-level scan found **4** passages: the ranking lives in section titles.

The arithmetic of that is a one-line identity, and it is now computed rather than
assumed. A passage-level count of a title-level structure counts the **passages
that restate a title**, so it is a function of the restatements and of nothing
else. The checker declares four documents with their passages marked: one with 12
titles and no restating passage, one with 0 titles and 12 restating passages, and
two controls that carry the same restating passages with the title counts swapped.
The count is taken over the declared passages — the title count is not an argument
of the counting function — and the controls show the same counts coming out under
swapped title counts:

```
12 titles, 0 restatements   →  passage-level count 0
 0 titles, 12 restatements  →  passage-level count 12
 0 titles, 0 restatements   →  passage-level count 0    (control)
12 titles, 12 restatements  →  passage-level count 12   (control)
```

The count orders the two documents *against* the structure they carry. A
structure that lives in titles and is never restated is invisible — and that is
not a small effect to be argued about, it is an identity: the count is a function
of the restatements alone. The same arithmetic killed the `【】` class in the
previous batch, where the 10,224-passage "gain" turned out to be the edition's
own field labels. Two demotions, one cause.

## 9. One role costs no labels

The one construction this batch actually declared carries a single role, and the
declaration records that the label budget was not spent on it. The arithmetic
says why that is not a coincidence. The orderings are **enumerated**, not counted
by a formula — the checker builds every permutation of `n` distinct roles for
`n` from one to four:

```
roles 1 → [()]                                    1 ordering
roles 2 → [(0,1),(1,0)]                           2 orderings
roles 3 → 6 orderings     roles 4 → 24 orderings
```

An `n`-role frame admits `n!` role orderings, and a frame with no supervised
evidence leaves all of them alive. **A one-role frame admits exactly one
ordering, so its role order is pinned by its own arity and needs no labels at
all.** Every reported-speech frame has at least two roles, so each needs
evidence to choose — which is what the unspent budget of 32 was for. The first
non-speech construction is also the first whose role order is free.

## 10. What the checker ran

```console
python3 experiments/four_trit_address/checker.py --output experiments/four_trit_address/evidence.json
```

[`checker.py`](../../experiments/four_trit_address/checker.py) uses the standard
library only — integers, tuples, `Fraction` and `unicodedata`; every acceptance
test compares integers or exact rationals — and its output is compared against the
retained [`evidence.json`](../../experiments/four_trit_address/evidence.json) with
timings removed. The retained run records **136 assertions** over six sections in
under a tenth of a second, having exhausted all 81 addresses and all 81 shifts
of the ternary space, all 64 of the binary space, the constructed image of the
one-bit-per-place reading over all 64 words, every allocation of six binary
places to four ternary places in both directions, 1,177 odometer steps, the
declared histogram boxes, the declared addresses and the declared pair
populations. `RLIMIT_CPU`, `RLIMIT_FSIZE` and the wall alarm are installed; no
address-space ceiling is installed because the checker launches no child process.
The checker refuses to overwrite an existing output path.

Controls that keep the checks from being vacuous:

* the binary interface's shifts are asserted to be **63** involutions, so the
  ternary result is a contrast and not a triviality about translations;
* the ternary shifts are asserted to have order **three**, not merely to avoid
  order two;
* the placewise and coordinate-wise bounds are asserted to be **strictly worse**
  than counting, so the capacity claims are comparisons;
* the declared injection is asserted **not** to be coordinate-wise, so the
  existence claim does not silently prove the capacity claim wrong;
* the one-bit-per-place image is **constructed** and counted over all 64 words,
  and its two leftover binary places are asserted not to change it, so 16 is a
  measurement of a reading and not the identity `2 ** 4`;
* each declared head's address index, each declared tetragram codepoint and each
  named pair's difference are **recomputed**, so the declared table is checked and
  not merely restated;
* the six declared histogram boxes are asserted to be **nonzero, of order three
  and to add to sixty**, and the two largest are asserted to be the two declared
  dominant differences;
* the four step relations are asserted to have **four distinct** shares;
* the passage-level count is taken **over declared passages**, and two control
  documents with the same restating passages and **swapped title counts** are
  asserted to give the same counts, so independence is computed;
* the declared similarity witness is asserted to consist of **two pairs with
  different attribute sets and different sizes** whose computed scores are equal,
  so the field is the result of a comparison and not a literal.

## 11. Residual and non-claims

* **No text and no corpus count is imported into the checker**, and no corpus is
  opened. What this note quotes is the external record's own prose, attributed to
  named commits above, and the six head names the record uses as its primary key;
  the addresses, the histogram boxes and the counts are declared numbers in the
  contract, and the checker verifies their arithmetic consistency and the
  structural consequences. Nothing here is a measurement of a corpus.
* **The declared head table is checked arithmetically, not textually.** The six
  head names and the two tetragram glosses are declared; what the checker
  computes from them is the address index of each head and the tetragram codepoint
  of each. The rendering of a tetragram gloss as a Chinese head name is a declared
  gloss and is not computed — no arithmetic could check it.
* **What is ruled out is a pairing by coordinate shift only.** Some other
  involution on `Z₃⁴` — a reflection-like map, or a map defined on a subset —
  is **not** excluded, and none is constructed here. The theorem is that
  differences cannot be its invariant, not that the pairing is arbitrary.
* **The carry profile is a fingerprint, not a collation.** Whether any
  transmitted order matches `54/18/6/3` is not checked, and no claim is made
  that the transmitted orders of either text have been verified here.
* **The capacity bounds bound a placewise or coordinate-wise reading.** No
  claim is made that any correspondence anyone intends is of either kind; what
  is established is that an injective, coordinate-wise reading of all 64
  configurations into four ternary places does not exist, and that one exists if
  the reading is allowed to mix coordinates.
* **No claim about meaning, and none about a tradition.** The four declared
  addresses (`釋 1313`, `窮 3223`, `毅 2113`, `積 3123`) are used only to check
  the stated arithmetic of the address formula and of the two reported
  differences; no chapter is read.
* **No significance claim about the percentile comparison**, and no claim that
  a similarity measure is invalid in general. The statement is that it cannot
  separate opposition from unrelatedness, which is a statement about what the
  statistic is sensitive to. What is **computed** is one declared instance: one
  declared measure on one declared opposite pair and one declared unrelated pair
  returning the same low value. The general statement is a declared observation
  that the instance illustrates, not a checked theorem; a measure built for the
  question could separate them, and none was built.
* **The counting-unit documents are declared**, not measured. Their passages are
  declared and the count is taken over them, but the documents are a model of the
  counting unit and not any work: the two controls exist to show the count does
  not read the title count, not to describe any corpus.
* **No native consequence.** No `SourceId`, observer, aperture, clock,
  operation or `Seal`; the address space and its shifts are not claimed as
  native structures.
