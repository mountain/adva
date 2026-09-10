# meaning-bobenko-suris-pair-v0

The meaning of the relation between the two PDFs, found by meaning.py.

## Objects

| object | paper | year | pages | words |
|---|---|---|---|---|
| `0504358v1.pdf` | Bobenko–Suris, "Discrete Differential Geometry. Consistency as Integrability" | 2005 | 157 | 51,932 |
| `0608291v2.pdf` | Bobenko–Suris, "On Organizing Principles of Discrete Differential Geometry. Geometry of spheres" | 2006 | 57 | 18,515 |

Pins: `fddb511c…` / `79a55213…`. Vocabulary overlap coefficient 0.7677 —
the highest of all four pairs measured so far (same authors, same field,
eighteen months apart).

## What the alignment found (align.json)

| phrase | 2005 | 2006 | reading |
|---|---|---|---|
| consistency | 88 | 26 | the book's thesis; the survey's tool |
| integrab* | 137 | 30 | same |
| transformation group | 1 | 8 | the survey's second principle |
| principle | 10 | 19 | the survey is *about* principles |
| sphere | 60 | 239 | 4x: the survey's concrete domain |
| conical | 0 | 38 | entirely new |
| lie geometry | 0 | 24 | entirely new |
| curvature line | 7 | 30 | the survey's concrete problem |

Citation: 2006 cites 2005; the reverse never holds.

## Arithmetic of the pair

```
2005:  one principle, 157 pages, 51,932 words
         "consistency = integrability"   (naming the deep identity)
2006:  two principles, 57 pages, 18,515 words
         "unifies the circular and conical nets"  (using the identity)
```

Pages shrink to 36%, but sphere-vocabulary grows 4x. The pair's arithmetic
is a double movement:

```
principles:   1 → 2     (一分为二: the organizing act)
discretizations: 2 → 1  (合二为一: the unifying act)
```

## The meaning, in three readings

**1. Derivation reading.** The 2006 survey is the 2005 book, distilled and
directed: the book names the deep identity (multidimensional consistency of
a discrete net is integrability — local checkability composes into global
structure); the survey organizes that identity into two principles and
spends its concrete effort on one problem. This is the third derivation
pair in the collection (after the NeoLab strategy→pitch pair and the
Burau boundary pair), and it is the cleanest: the derived document is by
the same hands, cites its source, and inherits 77% of the vocabulary.

**2. Reverse-learning reading.** In 2005 the principle is the *result*;
in 2006 the principle is the *tool*. What was discovered becomes what
discovers: the consistency principle, once established, is applied to
Lie geometry and unifies two discretizations (circular and conical nets)
that previously looked like competitors. The counterexample of the
session's reverse-learning switch has a positive twin: a proof that
becomes a method is the same switch run forward.

**3. TrustBase reading.** "Consistency as integrability" is the purest
form of the session's thesis: the global object (the integrable surface)
is nothing but the closure of local checks (consistency on every
elementary cell). Trust — of a structure in its discretization — is
explicit, independently checkable, and bounded: it lives in each cell,
not in the whole. The 2006 survey then shows the payoff: the principle
organizes, and two competing discretizations turn out to be one.

## Holes

- No mathematics verified: neither the book's proofs nor the survey's
  convergence claims were re-run; the reading aligns measured surface
  facts only.
- Phrase counts are surface proxies; semantics of "principle" and
  "consistency" are not disambiguated.
- Only the two endpoints were probed: the 2005–2006 intermediate
  literature (e.g., other DDG surveys) was not downloaded.
