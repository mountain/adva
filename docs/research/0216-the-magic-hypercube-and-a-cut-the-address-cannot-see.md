# 0216 — The magic hypercube, and a cut the address cannot see

Date: 2026-09-23. Direction: Mingli Yuan. Analysis, checker and note:
deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through his account
as an authorized proxy. Account use is not his authorship, review or endorsement.

Status: one bounded external exact experiment. No Rust witness, no stable API
change, no library admission, no Seal, and no claim about any text.

Base: `79f6353511d736ae743b109f1c573b652eff170a`. Library gitlink:
`73a6af4ac4ed8225366d3c16794e309cff15f51d`.

---

## 1. What was mined elsewhere, and what is not imported

A sixth batch outside this repository — `~/wenyan-relation-learning` at commits
`b7cee9f`, `f41c66c`, `5da8a87`, `251aa42`, `4cbee25` and `2a29797` — produced a
positive construction with an exact condition and the cleanest proxy chain this
line has yet recorded.

| Reported there | Their number |
|---|---|
| a **four-dimensional magic hypercube on the eighty-one addresses**, constructed | `v(x) = 1 + Σⱼ 3ʲ((Mx)ⱼ mod 3)` with `M = J − 2I`, "invertible over `Z/3` and **every entry nonzero**"; 1..81 once each; **all 108 one-dimensional lines sum to 123**; the classical square is the two-place case |
| the ninth position of each head is named one way in 47 heads and another in 34 | the split is **contiguous**: heads 1..47 one way, 48..81 the other, no exception |
| where that cut falls in the address | head 47 = `方2 州3 部1 家2`, head 48 = the same three places and `家3` — the cut is **not** at a place boundary |
| four successive readings of the split, three of them wrong | yang/yin (refuted, 6 counterexamples), the first place (demoted to a proxy), yin-and-yang set against each other (refuted, 9–10 counterexamples), head index (exact) |
| an ending-structure statistic | the last three heads total 14; over all `C(81,3) = 85,320` selections, 4,735 reach at least 14 → **p = 0.0555**, not significant |
| a consolidation record | `knowledge/relations/taixuan-line.json`, with verified positive, verified negative, not significant and not separated kept apart |

**No text and no corpus count is imported.** The construction, the cut and the
reported counts are declared in this experiment's contract; the checker verifies
their arithmetic and the structural consequences. No corpus is opened and none
of their measurements is re-run.

This batch lands directly on
[0215](0215-the-magic-square-exists-and-the-address-is-not-it.md)'s subject and
extends it: 0215 asked about the same eighty-one values read as a nine by nine
grid; this asks about them read as a four-dimensional array of side three.

## 2. The hypercube, and the exact condition

The construction is one line: take the four ternary coordinates, multiply by a
`4 × 4` matrix over `Z/3`, read the result's base-three digits, add one.

```
value(x) = 1 + Σⱼ 3ʲ ((M x)ⱼ mod 3)          M = J − 2I
```

With `M = J − 2I` — one off the diagonal, minus one on it — the checker finds
**every entry nonzero**, determinant `2` (so invertible), and the values are
`1..81` exactly once. And all **108** one-dimensional coordinate lines —
`4` directions times `3³ = 27` lines each, three cells per line — sum to

```
123 = 3 · (81 + 1) / 2
```

which is the standard hypercube magic constant `m(mᵈ+1)/2` for `m = 3`, `d = 4`.
Their claim is both correct and, as it turns out, much stronger than they stated:

> **The coordinate lines are constant exactly when `M` has no zero entry.**

The reason is one line of arithmetic. Writing the line in direction `j` through a
point `x`, the sum over the three cells is

```
3 + 3·Σ_{k : M_kj ≠ 0} 3ᵏ  +  3·Σ_{k : M_kj = 0} 3ᵏ ((Mx)_k mod 3)
```

The first two terms are constants and add to `3 + 3(1+3+9+27) = 123`. The third
term vanishes precisely when column `j` has no zero entry, and otherwise it
varies with `x` unless the corresponding row of `M` is zero. So for a matrix with
no zero row:

**constant lines in every direction ⟺ no zero entry.** The checker establishes
both halves by exhaustion over declared families rather than by the derivation
alone:

* **sufficiency**: all **65,536** matrices with every entry nonzero give constant
  lines — every one of them, no exception;
* **necessity**: of the **22,440** invertible binary matrices with a zero entry
  and no zero row, **zero** give constant lines.

The count that matters follows: **22,272** of the zero-free matrices are
invertible, and each gives a distinct magic hypercube. So there are **22,272**
magic hypercubes of this shape on the eighty-one addresses, not one — and the
external record's chosen matrix is one of them.

Invertibility is a separate condition, and the two conditions do different jobs:
**no zero entry makes the lines constant; invertibility makes the values a
permutation.** A zero-free matrix that is singular has constant lines and repeats
values; it is a semi-magic array, not a magic hypercube.

## 3. The declared line set is the whole content

The same construction is **not** magic along its diagonals. The eight main
diagonal directions — the lines `t ↦ t·d` for `d ∈ {1,2}⁴` up to sign — have
sums

```
123, 123, 123, 123, 6, 12, 30, 84
```

so exactly four of the eight happen to reach the magic constant and four do not.
The construction is therefore magic along its **coordinate lines only**.

This is not a defect; it is the exact place where the word "magic" is decided,
and the same distinction shows up one dimension down. At two places, with
`M = [[1, 1], [1, 2]]` and no shift, the construction gives

```
1 8 6
5 3 7
9 4 2
```

whose rows and columns are all `15` — the six coordinate lines — while its two
diagonals are `6` and `18`. **The matrix gives the coordinate lines; the shift
buys the diagonals.** With the shift `(2, 1)` the same formula gives

```
8 1 6
3 5 7
4 9 2
```

both diagonals `15`, which is the classical square — and this is exactly what
[0215](0215-the-magic-square-exists-and-the-address-is-not-it.md) found
independently, where the whole affine family was enumerated and the classical
square came out at coefficient matrix `(1,1,1,2)` with shift `(2,1)`.

So three objects now sit on one formula:

| reading | lines declared | constant | how many |
|---|---|---:|---|
| four places, three per side | 108 coordinate lines of 3 | **123** | 22,272 matrices |
| two places, nine per side | 20 lines of 9 (rows, columns, two diagonals) | **369** | 3,528 ([0215](0215-the-magic-square-exists-and-the-address-is-not-it.md)) |
| the same values in the natural grid | only the four central lines reach it | 369 | 1 arrangement |

**Same eighty-one values, three line sets, three answers.** The magic property is
a property of the declared lines and not of the values — which is this line's
recurring finding, now with a construction instead of a negative result.

## 4. A cut the address cannot see

The second object is a split of the eighty-one heads at forty-seven: the ninth
position of each head is named one way in heads `1..47` and the other way in
heads `48..81`, contiguously, with no exception. The seed fact was verified
earlier in the external record (the sectioning assumption holds: 81 heads times
10 passages, first-passage spacing constant at 10).

The address arithmetic is exact and worth stating: head 47 has index 46 and
address

```
46 = 27·1 + 9·2 + 3·0 + 1   →   (方 2, 州 3, 部 1, 家 2)
47 = 27·1 + 9·2 + 3·0 + 2   →   (方 2, 州 3, 部 1, 家 3)
```

so the two heads across the cut are in the **same three-place block** and differ
in exactly one place, `家`, by one step.

Now the question that can be decided exactly: **can any proper subset of the four
places see this split?** A subset sees it when the two sides never share a
projection onto those places. The checker exhausts all **15** proper subsets:

```
subsets that separate the split:    only (方, 州, 部, 家) — all four
proper subsets that separate it:    0
```

**No proper subset of the four places separates the cut.** Any reading that uses
some but not all of `方州部家` necessarily confuses the two sides; only the full
address, which distinguishes every head, sees it. And the cut is not at a place
boundary either: it lies strictly inside the second place's range (`方2` covers
heads 28..54).

This is a sharper statement than "no structural variable was found". It is a
statement about **definability**: the split is invisible to the address algebra,
so the ninth-position name marks a division that the address layer provably
cannot express. Whether that division is a phase, a transmitted variant or
something else is a separate question, and this experiment does not answer it.

## 5. Four readings, three of them proxies

The most transferable thing in this batch is the chain. The same split was read
four times, and each reading was refuted by the next:

| version | reading | fate | what killed it |
|---|---|---|---|
| v1 | yang heads take one name, yin heads the other | **refuted** | 6 counterexamples in the first place |
| v2 | the first place decides | **demoted to a proxy** | the first place is entirely before the cut, the third entirely after, and the second **straddles** it |
| v3 | the head statement sets yin and yang against each other | **refuted** | 9–10 heads on the other side do exactly that |
| v4 | head index at most 47 takes one name, at least 48 the other | **exact** | — |

v2 is the instructive one. Its "variable" is real — fixing the second place does
separate the two groups — and it is still not the law, because the second place's
range is cut by the split rather than aligned with it. Every earlier version was
a **correlate of the index**, and the index was the answer all along.

The external record's own summary of why: *the residual was read head by head
rather than treated as noise or as a regex problem.* The third version had
declared the residual a limitation of its pattern, which would have closed the
question one step early.

The arithmetic of the one statistic in the chain that is checked here:

```
selections of three heads from eighty-one      C(81,3) = 85,320
selections totalling at least fourteen                    4,735
exact share                          947/17,064 = 0.055497
declared threshold                                             0.05
```

above the threshold, so **not significant** — and the external record says so
rather than reporting the near miss as a finding.

## 6. What the checker ran

```console
python3 experiments/magic_hypercube/checker.py --output experiments/magic_hypercube/evidence.json
```

[`checker.py`](../../experiments/magic_hypercube/checker.py) uses the standard
library only — integers and `Fraction`; no floating-point value enters any
acceptance test — and its output is compared against the retained
[`evidence.json`](../../experiments/magic_hypercube/evidence.json) with timings
removed. The retained run records **49 assertions** over four sections in about
forty-three seconds, having exhausted 65,536 zero-free matrices, 22,440
invertible binary matrices with a zero entry and no zero row, 108 coordinate
lines, 8 diagonal directions and 15 proper subsets of the four places.
`RLIMIT_CPU`, `RLIMIT_FSIZE` and the wall alarm are installed; no address-space
ceiling is installed because the checker launches no child process. The checker
refuses to overwrite an existing output path.

Controls that keep the checks from being vacuous:

* the diagonal sums are asserted to have **five distinct values** and four
  directions at the constant, so "the diagonals are not constant" is a count and
  not an impression;
* the two-place construction is asserted to have diagonals `6` **and** `18`, and
  the shifted one **both** `15`, so section 3 is a comparison of two objects;
* the number of proper subsets is asserted to be **15**, and the separating set
  to be exactly the full one, so the invisibility claim is exhaustive;
* the necessity family is asserted to have exactly **22,440** members, so an
  accidental empty family cannot make necessity look proved;
* the p-value is asserted to be **above** one twentieth, so a near miss is not
  silently promoted.

## 7. Residual and non-claims

* **No text and no corpus count is imported.** The construction, the cut and the
  counts are declared; the checker measures nothing.
* **The cut is described, not explained.** That no proper subset of the places
  can see it says nothing about why it is at 47. The external record's own
  candidate — that the head statements change phase at the cut — is not tested
  here, and this experiment does not choose between a phase and a transmitted
  variant.
* **No claim that coordinate lines are the lines that matter.** The whole content
  of section 3 is that they are not the only lines one could declare, and that
  the declared set decides the answer. The diagonal result shows this
  construction is not magic along diagonals; it does not show that no
  construction of this shape can be.
* **The two-place case is one shift, not a classification.** The full
  classification of order-three magic squares is 0215's, not this note's.
* **Necessity is exhausted on the declared family only.** The general statement
  is given as a derivation; the binary family of 22,440 matrices is the evidence,
  and matrices over `{0,1,2}` with a zero entry are not exhausted.
* **The proxy chain is reported, not re-derived.** Only the arithmetic of its
  last statistic is checked; the counterexample counts of v1 and v3 are declared
  numbers from the external record.
* **No claim about a tradition.** That a magic hypercube can be built on these
  eighty-one addresses says nothing about whether anyone built one, and this
  experiment does not claim the construction was known anywhere.
* **No native consequence.** No `SourceId`, observer, aperture, clock, operation
  or `Seal`; the construction and the cut are not claimed as native structures.
