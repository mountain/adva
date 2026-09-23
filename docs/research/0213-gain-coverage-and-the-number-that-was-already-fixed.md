# 0213 — Gain, coverage, and the number that was already fixed

Date: 2026-09-23. Direction: Mingli Yuan. Analysis, checker and note:
deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through his account
as an authorized proxy. Account use is not his authorship, review or endorsement.

Status: one bounded external exact experiment. No Rust witness, no stable API
change, no library admission, no Seal, and no claim about any text.

Base: `79f6353511d736ae743b109f1c573b652eff170a`. Library gitlink:
`73a6af4ac4ed8225366d3c16794e309cff15f51d`.

---

## 1. What was mined elsewhere, and what is not imported

A third batch of work outside this repository — `~/wenyan-relation-learning` at
commits `5cebc06`, `f93cd47`, `ca0008c` and `462ccbb` — produced one external
claim tested to destruction and one internal statistic that did the destroying.
Their reported numbers:

| Reported there | Their number |
|---|---|
| a published claim that 122 magnetic point groups and 1651 magnetic space groups show "100% octave-normalized correspondence" with the 22 shrutis | tested and **failed as stated**; maximum distance to the nearest shruti 2.27% of an octave for both sets; coverage 22/22 at 1% for both, 22/22 at 0.1% for 1651 but only 4/22 for 122; **11 exact hits for 1651 with values 1, 2, 4, …, 1024** and 7 for 122 with values 1, …, 64 |
| a count coincidence: 1651, 1191, 528, 394, 230, 122 against 22 | one exact multiple (528); `1 − (21/22)⁶` quoted as 24.4% |
| five marker classes for a "labelled statement" family, measured over 217,071 passages | `position` gain 1,119 over 5 works, top-3 share 0.998; `ganzhi` 3,957 over 76, 0.385; `naming` 6,800 over 111, 0.307; `bracket` **10,224 over 15, 0.892**; `grade` 1,939 over 90, 0.233 |
| their own pre-registered gate on a new work | 190 unread passages, 16 non-speech structure hits, share 0.0842 against a declared 0.05 gate — **it passed, and two of the five listed patterns scored exactly zero**; recorded as a miss rather than a pass |

**No text and no corpus count is imported here.** The summary numbers above are
declared in the contract of this experiment and checked arithmetically; none of
their measurements is re-run and no corpus is touched. Where this note says a
number "matches", it means the arithmetic reproduces their published *value*,
not their data.

Three of the four commits are well covered by
[0212](0212-what-a-declared-invariance-already-fixes.md)'s theme. This batch
adds a fourth instance of it in a new form, and — for the first time in the line
— a statistic that does the separating work rather than failing to.

## 2. The octave reduction is a quotient by doubling

The external test reduces a serial number `n` to one octave by

```
ρ(n) = n / 2^⌊log₂ n⌋  ∈ [1, 2)
```

computed exactly, with no logarithm. The checker establishes what this map is:

* **Its fibres are exactly the orbits of doubling.** `ρ(n) = ρ(odd part of n)`,
  so the fibre of a value is `{2ʲ · o : j ≥ 0}` for its odd element `o`, and the
  odd element is the smallest member of its fibre. Verified for every `n ≤ 2000`.
* **Its fixed points are exactly the powers of two**, and there are
  `⌊log₂ N⌋ + 1` of them below `N`.

So the reduction is the quotient of the positive integers by the multiplicative
action of `⟨2⟩`, restricted to one octave. Nothing about a serial number's
meaning survives it; what survives is its odd part.

## 3. The exact hits of any equal division are the powers of two

A `b`-fold equal division of the octave places its positions at
`2^{k/b}`, `k = 0..b−1`. The checker proves the rationality lemma concretely —
`2^{k/b}` is rational **exactly when `b` divides `k`**, checked as an exact
integer root test for eight declared values of `b` — and therefore:

> Within one octave the only **rational** position of any equal division is the
> unison `2⁰ = 1`.

Combined with section 2, the exact hits of the serial range `1..N` are
necessarily the powers of two, and their number is `⌊log₂ N⌋ + 1` — **a function
of the limit alone, independent of the division and of what the numbers mean.**

The exhaustion reproduces the reported values exactly:

```
N = 122   7 exact hits    1, 2, 4, 8, 16, 32, 64
N = 1651 11 exact hits    1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024
```

and gives the same set for all eight declared divisions, `1, 2, 3, 5, 7, 12, 22`
and `53`. The external record already reads these as "the unison, the one
position that is forced". The arithmetic says something stronger: **they are not
a small residue of correspondence, they are the fixed points of the reduction,
and the count could not have come out any other way.**

## 4. Coverage is a function of the point count, and the bound is the covering radius

Two further statistics were reported, and both are fixed before any data is
seen.

**The covering radius.** For the `b` equal divisions of the circle the supremum
of the distance from a point to the nearest position is exactly `1/(2b)`,
verified exactly for six declared divisions and equal to **`1/44 = 0.022727…`
for `b = 22`**. So:

> "Every point of the octave is within 2.27% of a shruti" is a theorem about the
> 22-division, satisfied by **every** subset of the octave — a single point, or
> none. The reported maximum distance of `0.02272` is that bound to five
> decimals.

**The coverage threshold.** The checker computes, by exact integer comparison —
a tolerance test `|log₂ρ − k/b| ≤ p/q` is rewritten as an exponent inequality
and decided with integer powers of two, so no floating-point value is involved —
the smallest number of points at which all 22 positions are covered:

| tolerance | smallest point count with full coverage |
|---|---|
| 1% | **113** |
| 0.1% | **1237** |

Against those two numbers the reported coverage is fully predicted:

```
N = 1651 > 1237 and > 113   →  22/22 at both tolerances   (reported: 22/22 and 22/22) ✓
N = 122  > 113 but < 1237   →  22/22 at 1%, not at 0.1%   (reported: 22/22 and 4/22)   ✓
```

**Both halves of the reported coverage behaviour follow from the point count and
the tolerance alone.** The observed contrast between 1651 and 122 — the part
that looks like evidence — is exactly the contrast the threshold predicts for
two sets that differ only in size.

## 5. One count coincidence, and fifteen moduli

The six published group counts reduce as reported: `1651 → 1`, `1191 → 3`,
`528 → 0`, `394 → 20`, `230 → 10`, `122 → 12` modulo 22, so exactly one is a
multiple. The exact arithmetic:

```
expected number of exact multiples at modulus 22         3/11 ≈ 0.2727
probability of at least one        27613783/113379904 ≈ 0.2436
probability of exactly one         12252303/56689952  ≈ 0.2161
```

Observing exactly one is a 21.6% event. And the modulus 22 is not special: over
the moduli from 2 to 40, **fifteen** divide at least one of the six counts —
`2, 3, 4, 5, 6, 8, 10, 11, 12, 13, 16, 22, 23, 24, 33`. A coincidence at 22 is
one of fifteen available coincidences in a range of thirty-nine moduli.

## 6. Gain is not a measurement: two columns that order the rows differently

The internal probe reported five marker classes with a `gain`, a top-three
work breakdown and a work count. The exact top-three shares reproduce the
published values:

| class | gain | works | top-3 share | reported |
|---|---:|---:|---:|---:|
| `bracket` | 10,224 | 15 | `190/213` = 0.8920 | 0.892 |
| `naming` | 6,800 | 111 | `123/400` = 0.3075 | 0.307 |
| `ganzhi` | 3,957 | 76 | `1523/3957` = 0.3849 | 0.385 |
| `grade` | 1,939 | 90 | `452/1939` = 0.2331 | 0.233 |
| `position` | 1,119 | 5 | `1117/1119` = 0.9982 | 0.998 |

The two columns order the rows differently, and the exact Spearman rank
correlation between gain and spread over the five classes is **`−1/10`**. With
five points the null standard error of a rank correlation is `1/√(n−1) = 1/2`,
so a magnitude of one tenth is well inside noise: the two columns are not
related, they simply order the rows differently. The
consequence is concrete rather than statistical: **the largest gain in the table
(`bracket`, 10,224) is *less* concentrated than the smallest (`position`,
1,119), 0.892 against 0.998, and it rests on three times as many works.** A
table sorted by its largest number puts the weakest candidate first, which is
what the external record itself concluded in prose.

Three further exact facts make the columns non-substitutable:

* **Gain and spread are independent.** Fix the gain and the number of works and
  enumerate every distribution: for a gain of 12 over 6 works the top-three share
  ranges over seven distinct values from `1/2` to `1`; for 24 over 4 works, from
  `3/4` to `1`. The minimum is the uniform value `3/W`, which itself depends on
  `W`. So **no gain determines any spread, and a class ordering by gain is not
  an ordering by evidence.** (9,113 compositions exhausted.)
* **The published top three bound rather than determine the spread they are used
  to summarise.** From the top-three counts and the work count alone, the
  effective number of works `1/Σpᵢ²` is confined to an interval:
  `bracket` `[3.03, 3.13]`, `position` `[2.06, 2.06]`, `naming` `[1.95, 27.42]`,
  **`grade` `[1.65, 39.72]`** — a factor of 24, on the very row whose share 0.233
  was read as the broadest evidence. A top-three share is a weak summary, and
  for the low-share rows it barely constrains what it summarises.
* **The baseline for a spread statistic is the corpus's own concentration.** On
  a declared corpus with work sizes `(4000, 3000, 2000, 500, 500)`, a marker
  distributed exactly in proportion to passage count — a pure language property
  by construction — has a top-three share of **`9/10`**. That is more
  concentrated than every reported class except `position`. So `0.892` is not
  by itself a large number: it is *below* the baseline of a corpus shaped like
  that, and the reading "near 1 means one work's property" needs the corpus's
  own share as its reference point, not zero and not `3/W`.

This is the first statistic in this line that separates rather than fails. The
spread column did the work the gain column could not, and the arithmetic above
says what it costs to use it: the share must be read against a baseline that the
gain column never mentions.

## 7. A declared threshold can pass while its named content is absent

The fourth commit recorded its own miss, and the arithmetic of that miss is
worth stating exactly. A pre-registered gate asked whether the non-speech
structure share of the unread passages was **below 1/20**. It is not:

```
non-speech hits   8 + 8 = 16   of  190 unread passages
share             16/190 = 8/95 = 0.084211  >  1/20 = 0.05
margin            7 hits to spare; the gate would fail at 9 or fewer
```

and of the five named patterns, two — `自…始` and `凡…皆` — scored **exactly
zero**. The gate is a function of the pair (numerator, denominator): **969
different component vectors** produce the same numerator 16, including one that
puts all 16 hits on a single pattern and many that leave a named pattern at
zero. So a gate on the aggregate is not a test of the listed content, and it
passed while two of the five things it was written to detect were absent.

The external record reached the same conclusion by inspection and recorded it as
a miss against its own threshold. The arithmetic here adds the reason: the
aggregate is not a function of the components the prediction named.

## 8. What the checker ran

```console
python3 experiments/gain_and_coverage/checker.py --output experiments/gain_and_coverage/evidence.json
```

[`checker.py`](../../experiments/gain_and_coverage/checker.py) uses the standard
library only — integers and `Fraction`; no logarithm and no floating-point value
enters any acceptance test — and its output is compared against the retained
[`evidence.json`](../../experiments/gain_and_coverage/evidence.json) with
timings removed. The retained run records **80 assertions** over six sections in
about two seconds, having exhausted 2,000 integers for the reduction, 1,651 for
each of eight divisions, 826 odd integers for the coverage tests, 39 moduli and
9,113 compositions. `RLIMIT_CPU`, `RLIMIT_FSIZE` and the wall alarm are
installed; no address-space ceiling is installed because the checker launches no
child process, and the contract's memory figure is a declared budget observed as
peak RSS. The checker refuses to overwrite an existing output path.

The tolerance tests deserve one note, because they are where floating point
would normally enter. `|log₂ρ − k/b| ≤ p/q` is multiplied up to
`|bq·log₂ρ − kq| ≤ bp` and exponentiated to an inequality between `ρ^{bq}` and
two powers of two, both integers — so the coverage and threshold numbers above
are exact, and the largest intermediate is a 117,581-bit integer rather than a
rounded logarithm.

Controls that keep the checks from being vacuous:

* the two declared limits are asserted to behave **differently** at the finer
  tolerance, so the coverage result is not one number reported twice;
* the finer tolerance is asserted to require **more** points than the coarser
  one, so the threshold is a threshold and not a constant;
* the gain order and the spread order are asserted to be **different** orders,
  so the rank-correlation claim is a comparison;
* the corpus baseline is asserted to be **above** the uniform-over-works value,
  so "the baseline is not `3/W`" is established rather than assumed;
* the two exactly-zero components are asserted, so the gate result is not a
  restatement of a positive numerator.

## 9. Residual and non-claims

* **No text and no corpus count is imported.** The class gains, the group
  counts and the gate counts are declared summary numbers in this experiment's
  contract; the checker verifies their internal arithmetic and the comparability
  of the columns, and nothing more. No corpus is opened and no external
  measurement is re-run.
* **No claim about the underlying external work beyond the declared reading.**
  A failure of a claim read one way is not a failure of whatever the original
  computation did, and the external record says so itself.
* **No claim that equal division is the correct reading of any musical system.**
  The division is declared, and it is declared to be the reading most favourable
  to the claim under test.
* **The covering radius and the coverage threshold say nothing about serial
  numbers, groups or music.** They are statements about the division and the
  point count. In particular the checker does *not* measure how well the
  declared points fit — the exact fit is not computed at all, and no claim is
  made about whether the point set could have been closer to the targets than it
  was. That question is left open, and it is the only one here that could have
  been evidence.
* **The thresholds are computed for the two declared tolerances only**, not for
  finer ones; a third tolerance would need larger exponents and is not computed.
* **The spread bounds are bounds because the full distribution over works was
  not available**, only the top three; with the full distribution the effective
  number of works would be an exact value rather than an interval.
* **The corpus baseline is computed on a declared corpus**, not on the corpus
  the classes were measured on, which is not imported here. It shows that the
  baseline is a corpus property; it does not supply the number for any real
  corpus.
* **No native consequence.** No `SourceId`, observer, aperture, clock,
  operation or `Seal`; the reduction map and its quotient are not claimed as
  native structures.
