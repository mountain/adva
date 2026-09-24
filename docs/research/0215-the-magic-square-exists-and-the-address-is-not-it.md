# 0215 — The magic square exists, and the address is not it

Date: 2026-09-23. Direction: Mingli Yuan. Analysis, checker and note:
deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through his account
as an authorized proxy. Account use is not his authorship, review or endorsement.

Status: one bounded external exact experiment. No Rust witness, no stable API
change, no library admission, no Seal, and no claim about any text.

Base: `79f6353511d736ae743b109f1c573b652eff170a`. Library gitlink:
`73a6af4ac4ed8225366d3c16794e309cff15f51d`.

---

## 1. What was mined elsewhere, and what is not imported

A fifth batch outside this repository — `~/wenyan-relation-learning` at commits
`7fe929d` and `29e353c` — asked whether the eighty-one head addresses admit a
magic square, and answered with a construction and a refusal.

| Reported there | Their number |
|---|---|
| a true nine by nine magic square can be constructed on the eighty-one heads | magic sum **369**, each of 1..81 once |
| the Lo Shu is an affine bijection of `(Z/3)²` | asserted, and "making it magic is one coordinate transformation" |
| the composite of the magic-square permutation with the native pairing | **0 of 35 pairs** survive — so the two are "completely incompatible" |
| the grid of the permuted square | each row and column carries **3** 方州 classes, which does not align with the native grouping |
| verdict | constructible, but **not a 後天**, because it carries none of the tradition's own labelling; no annotatable phenomenon cycle was found |
| one corpus count | 明史 built at 3,490,496 characters, 26,533 passages, read at 3,654; a manifest race silently dropped 2 of 138 works |

**No text and no corpus count is imported.** The addresses, counts and reported
numbers are declared in this experiment's contract; the checker verifies their
arithmetic and the structural consequences. No corpus is opened and none of
their measurements is re-run.

The direction is Mingli Yuan's, and the interesting part of this batch is
genuinely interesting: **the address space has a grid structure of its own, and
the question "is it magic?" has an exact answer that nobody had computed.**

## 2. The grid is forced, and it is not magic

The address formula is

```
i = 27(方−1) + 9(州−1) + 3(部−1) + (家−1)
```

and it factors: writing `r = 3(方−1) + (州−1)` and `c = 3(部−1) + (家−1)`, both
in `0..8`, gives `i = 9r + c`. **So the eighty-one heads carry a canonical nine
by nine grid with no choice at all** — rows indexed by the first pair of ternary
places, columns by the second pair — and the entry at `(r, c)` is `9r + c + 1`.

Is that grid magic? The magic constant for order nine is `9(81+1)/2 = 369`, and
the exhaustion gives:

```
row sums      45, 126, 207, 288, 369, 450, 531, 612, 693        = 81r + 45
column sums   333, 342, 351, 360, 369, 378, 387, 396, 405       = 9c + 333
diagonals     369 and 369
```

**It is not magic** — the row sums span 45 to 693 — and yet **exactly four of its
twenty lines already reach 369**: the middle row, the middle column, and *both*
diagonals. The diagonals are worth writing out, because they are not accidents of
the arithmetic:

```
main diagonal   1, 11, 21, 31, 41, 51, 61, 71, 81     = 10r + 1
other diagonal  9, 17, 25, 33, 41, 49, 57, 65, 73     = 8r + 9
```

both arithmetic progressions of nine terms about the centre 41, hence both
`9 × 41 = 369`. So the address's own grid is already four-twentieths magic, and
the failure is confined to the sixteen off-centre rows and columns.

## 3. The affine family, and where the magic constant comes from

A magic square on the heads is a permutation of `Z₉²`; the natural finite family
to search is the affine one,

```
value(r, c) = n · ((αr + βc + e) mod n) + ((γr + δc + f) mod n) + 1
```

which reads the grid coordinates through a `2 × 2` matrix and reassembles the
two residues. Two facts come out of it exactly.

**When is it a permutation?** The entries are `1..n²`, each once, **exactly when
the determinant `αδ − βγ` is a unit modulo `n`** — verified for every coefficient
quadruple at orders three, five and nine (7,267 matrices). This is where the
order under study bites, and section 4 records what it cost me.

**Where does 369 come from?** If the two coefficients `β` and `δ` are units, then
as the column index runs, `βc` runs over all residues, so the row sum is

```
n · n(n−1)/2  +  n(n−1)/2  +  n  =  n(n² + 1)/2
```

which is **exactly the magic constant**, derived rather than quoted: 15 at order
three, 65 at order five, **369 at order nine**. The verified cases cover 6,864
unit-coefficient configurations.

## 4. How many affine magic squares, and the mistake the count exposed

Counting them by exhaustion, with the entries required to be a permutation:

| order | affine magic squares | coefficient matrices admitting one |
|---|---:|---:|
| 3 | **8** | 8 |
| 5 | **1,472** | 192 |
| 9 | **3,528** | 648 |

The order-three count is a validation rather than a result: there are exactly
**eight** 3×3 magic squares using 1..9, and the affine family finds exactly eight.
That is a coincidence of order three and is not claimed as a theorem — but it is
the reason to trust the family at the other orders.

**A mistake of mine, recorded because the arithmetic caught it.** My first probe
of this count used the test "the determinant is not zero modulo `n`", which is
invertibility over a *field*. At orders three and five that is the same thing; at
order nine it is not, and the probe reported **6,024** where the correct count is
**3,528** — an over-count of **2,496**, all of it non-invertible matrices whose
rows happen to be constant because the row coefficients are still units. The
checker now computes both and asserts that they agree at the prime orders and
differ by exactly 2,496 at order nine. **"The determinant is nonzero" is not
invertibility modulo `3²`**, and the one order in this note where it matters is
the order the whole question is about.

**The family is odd-order only.** The same exhaustion at orders four, six and eight
returns **zero** affine magic squares — for every coefficient matrix and every
shift. So the family is an odd-order family, and this is worth stating because
this repository has its own magic-square line: the order-four search in
[0119](0119-characteristic-magic-square-closure-family.md), which enumerates
normal order-four assignments under a Rust witness. **The 880 normal order-four
magic squares are outside the affine family**, which is a statement about two
different constructions and not a comparison of counts.

**The standard construction is in the family, with one matrix for every order.**
The de la Loubère construction — start one at the top middle, then step up and
right, dropping down on a collision — is magic, is a permutation, and is
**affine at all three orders with the same coefficient matrix** `(1, 1, 1, 2)`:

```
n = 3   α,β,γ,δ = 1,1,1,2   shifts (e,f) = (2, 1)   centre 5
n = 5   α,β,γ,δ = 1,1,1,2   shifts (e,f) = (3, 1)   centre 13
n = 9   α,β,γ,δ = 1,1,1,2   shifts (e,f) = (5, 1)   centre 41
```

with `e = (n+1)/2`, `f = 1`, and the centre always `(n²+1)/2`. So **one `2 × 2`
matrix generates the standard magic square in every odd order, and the order
enters only through the translation.** The count is not a multiple of the shift count at any of the three
orders (8 against 9, 1472 against 25, 3528 against 81), so the shifts are
constrained and not free — which is exactly the Lo Shu case, where `γ + δ ≡ 0`
forces one specific shift.

So the external record's construction is sound, and the arithmetic says something
stronger than "one is constructible": **the standard square is a single affine map
applied at every odd order, and 3,528 of its siblings are magic at order nine.**

**A note on the repository's own line.** [0119](0119-characteristic-magic-square-closure-family.md)
searches normal magic squares of order **four** with a native Rust witness, exact
line-sum and characteristic-polynomial certificates, and a sixteen-member orbit
under three frozen transformations. That line and this note share a name and
nothing else: order four against order nine, a native bounded search against an
external classification, a witness over assignments against a count over affine
maps. The one place they touch is the sentence above — the order-four squares
0119 searches are not affine, so neither result can be read as evidence for the
other, and neither is cited as such.

## 5. Preserving none of thirty-five pairs is what chance does

The external record's refusal rests on one number: after composing the
magic-square permutation with the native pairing, **0 of 35 pairs** survive, read
as "completely incompatible". The arithmetic of that number:

```
unordered pairs of 81 heads                        C(81,2) = 3240
chance that one given pair is preserved            35/3240 = 1/92.6
expected number of preserved pairs                 35 × 35/3240 = 245/648 ≈ 0.378
probability of preserving none, by Markov          ≥ 1 − 245/648 = 403/648 ≈ 0.622
independent-pair estimate                          ≈ 0.684
```

**Preserving nothing is what a random permutation does at least 62% of the time.**
So `0/35` refutes preservation — which is all the external record claims to have
measured — but it is not evidence of *antagonism*, and "completely incompatible"
reads more into the zero than the zero carries. A statistic that could separate
"the magic square ignores the pairing" from "the magic square opposes it" would
have to be built for that question, and none was.

This is the fourth time in this line that the number reported and the number the
question needs are different numbers. It is not a criticism of the external
record, which reached the same verdict by refusing to over-read its own result:
**constructible, but carrying none of the tradition's own labelling.**

## 6. The alignment statistic

The address has four ternary places, so it has two coarsenings to nine classes:
by the first pair — which are exactly the rows — and by the second pair — which
are exactly the columns. Counting how many distinct classes appear along each
line gives an alignment statistic:

| labelling | row incidences | column incidences | total |
|---|---:|---:|---:|
| first pair (方,州) on the canonical grid | **9** | 81 | 90 |
| second pair (部,家) on the canonical grid | 81 | **9** | 90 |
| the block pattern, three classes per row | 27 | 27 | 54 |
| maximum possible | 81 | 81 | 162 |

**The canonical grid is the arrangement in which both coarsenings are aligned at
once**: each first-pair class fills a row and each second-pair class fills a
column, total incidence 90 against a maximum of 162. The reported grid, with
three classes per row and per column, has total incidence 54 — *more mixed than
the canonical one on both axes at once*. So "the address has a grid structure"
and "that grid aligns the two coarsenings" are the same statement, and any
candidate 後天 ordering can be measured against it.

## 7. A count that is a function of an index

The second commit in this batch found an engineering failure that is worth its
own arithmetic: a manifest was written from a snapshot, and the **two works
inserted after the snapshot were absent from it** while their files sat on disk.

```
snapshot                  136 works
inserted afterwards         2
directory                 138 works
manifest                  136 works   ← internally consistent, and wrong
lost share                2/138 = 1/69
```

The point is not the fix but the shape: **every statistic computed from the
manifest is a function of the snapshot alone**, so the manifest cannot show its
own loss. No count, ratio or consistency check over the index detects a missing
row, because the index is self-consistent by construction. The external record
says exactly this — "the guard was in the wrong place" — and the arithmetic says
why: the guard protected the wrong object.

The scale is what made it worth finding. The work added in the same commit is
**11.8% of the corpus by characters** (3,490,496 of 29,544,900) and is read at
**13.8%** (3,654 of 26,533 passages), so two missing rows were hiding a
twelfth of the corpus from every official measurement.

## 8. What the checker ran

```console
python3 experiments/eighty_one_magic_square/checker.py --output experiments/eighty_one_magic_square/evidence.json
```

[`checker.py`](../../experiments/eighty_one_magic_square/checker.py) uses the
standard library only — integers and `Fraction`; no floating-point value enters
any acceptance test — and its output is compared against the retained
[`evidence.json`](../../experiments/eighty_one_magic_square/evidence.json) with
timings removed. The retained run records **21,079 assertions** over six sections
in about eight seconds, having exhausted 81 cells of the canonical grid, 7,267
coefficient matrices for the entry-set equivalence, 6,864 unit-coefficient
configurations, 547,795 affine squares across the three orders (twice, once per
invertibility test), and the declared pair and class populations.
`RLIMIT_CPU`, `RLIMIT_FSIZE` and the wall alarm are installed; no address-space
ceiling is installed because the checker launches no child process. The checker
refuses to overwrite an existing output path.

Controls that keep the checks from being vacuous:

* the canonical grid is asserted **not** to be magic, and asserted to attain the
  magic constant on exactly four lines, so the result is a count and not a
  yes-or-no;
* the two invertibility tests are asserted to **agree at the prime orders and to
  differ by exactly 2,496 at order nine**, so section 4's mistake is retained as
  evidence rather than as prose;
* the order-three count is asserted to be **8**, the classical value, so the
  family is validated before it is used at the other orders;
* the two aligned labellings are asserted to share total incidence **90** and the
  block labelling to be **below** it, so the alignment claim is a comparison;
* the Markov bound is asserted to be **above three fifths**, so "ordinary" is a
  bound and not an impression;
* the manifest loss is **computed as a set difference between two declared
  listings** rather than written into a range, and one declared manifest is
  compared against **two declared directories whose losses differ** (two works and
  three), so "no statistic from the manifest can detect the loss" is an exhibited
  comparison and not a restatement.

## 9. Residual and non-claims

* **No text and no corpus count is imported.** The counts and the two addresses
  are declared numbers in the contract; the checker verifies their arithmetic
  consistency. Nothing here is a measurement of a corpus.
* **No claim about what any figure means, and none about a tradition.** The grid
  is a grid of addresses; no claim is made that anyone ever placed anything in
  it, and the external record's own verdict — constructible but not a 後天 — is
  reported, not adjudicated.
* **The affine family is not claimed to exhaust the magic squares of orders five
  or nine.** It coincides with the classical count at order three, and that
  coincidence is recorded as a coincidence of order three.
* **The preservation arithmetic bounds a probability.** It shows that preserving
  nothing is ordinary; it does not describe the reported permutation, and it does
  not show that the permutation is what the external record says it is.
* **The class incidence statistic is computed on a declared block labelling**, not
  on the reported permuted grid, which is not available here. It gives the
  statistic a second and a maximum value; it does not measure the reported grid.
* **The manifest model is a model.** It is not an audit of any pipeline, and the
  numbers used are the ones the external record published. The two listings and
  the manifest are declared in the contract; what the checker computes is the set
  difference between them and the arithmetic of the shares. That the two declared
  directories lose different numbers of works under one and the same manifest is
  a property of the declared model, not a measurement of any real directory.
* **No native consequence.** No `SourceId`, observer, aperture, clock, operation
  or `Seal`; the address space, its grid and the affine family are not claimed as
  native structures.
