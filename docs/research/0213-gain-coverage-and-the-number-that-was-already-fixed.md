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
| five marker classes for a "labelled statement" family, measured over 217,071 passages | `position` gain 1,119 over 5 works, top-3 share 0.998; `ganzhi` 3,957 over 76, 0.385; `naming` 6,800 over 111, **0.307** (see §6: the published third decimal is one low — the exact share is `0.3075` and its exact rounding is `0.308`); `bracket` **10,224 over 15, 0.892**; `grade` 1,939 over 90, 0.233 |
| their own pre-registered gate on a new work | 190 unread passages, 16 non-speech structure hits, share 0.0842 against a declared 0.05 line — the line is a **falsification** line (the prediction fails if the share is *below* 0.05), so the share is **above** it and the gate passed, while two of the five listed patterns scored exactly zero; the record kept the two apart, and §7 of this note originally reversed the direction |

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

## 4. Coverage is a function of the set's size, and the bound is the covering radius

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
the threshold at which all 22 positions are covered. The coverage test walks the
**odd** serial numbers, so what it returns is a **serial-number index bound**: the
smallest odd index by which every position has been covered. An index and the
number of odd points it contains differ by about a factor of two, and the point
counts are reported next to the bounds:

| tolerance | smallest odd serial-number index with full coverage | odd points up to that index |
|---|---:|---:|
| 1% | **113** | 57 |
| 0.1% | **1237** | 619 |

An earlier draft of this table called 113 and 1237 "the smallest number of points
at which all 22 positions are covered". They are not point counts: the bound
`113` is the index `2 · 57 − 1`, and its point set holds 57 odd numbers. The
threshold definition is unchanged — only the unit it is quoted in is corrected,
and the checker now reports both numbers.

Against those two index bounds the reported coverage is fully predicted:

```
N = 1651 > 1237 and > 113   →  22/22 at both tolerances   (reported: 22/22 and 22/22) ✓
N = 122  > 113 but < 1237   →  22/22 at 1%, not at 0.1%   (reported: 22/22 and 4/22)   ✓
```

**Both halves of the reported coverage behaviour follow from the declared
serial-number limit and the tolerance alone.** The observed contrast between 1651
and 122 — the part that looks like evidence — is exactly the contrast the
threshold predicts for two sets that differ only in size.

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
work breakdown and a work count. The exact top-three shares are these, and **four
of the five** reproduce the published three-decimal value under exact rounding:

| class | gain | works | top-3 share | reported |
|---|---:|---:|---:|---:|
| `bracket` | 10,224 | 15 | `190/213` = 0.8920 | 0.892 |
| `naming` | 6,800 | 111 | `123/400` = 0.3075 | 0.307 |
| `ganzhi` | 3,957 | 76 | `1523/3957` = 0.3849 | 0.385 |
| `grade` | 1,939 | 90 | `452/1939` = 0.2331 | 0.233 |
| `position` | 1,119 | 5 | `1117/1119` = 0.9982 | 0.998 |

**One of the five published digits is one unit low, and the exact arithmetic says
so.** The `naming` share is exactly `123/400 = 2091/6800 = 0.3075`, which is a
three-decimal **half-way** value: rounding it exactly gives `0.308`, and the
published string is `0.307`. That string is the *truncation* of the share, and it
is also what binary floating point yields here, because the nearest double to
`0.3075` lies just below it — the external record renders the share as
`+(2091 / 6800).toFixed(3)`. The other four published values are reproduced by
exact rounding exactly.

This note previously reported the table as five for five, and the reason it did is
worth keeping: the checker compared `f"{float(share):.3f}"` with the published
string, so the fifth row agreed **through the float's own error**, in an
experiment that declares that no floating-point value enters any acceptance test.
The checker now rounds in exact integer arithmetic — half away from zero, on the
exact rational — and records this row as a **disagreement** rather than a
confirmation: `0.307` is the published value, `0.308` is the exact three-decimal
value of the exact share, and the two differ by one unit in the last place.
Nothing was moved to make the old string survive.

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

The gate that the fourth reported item carried is a **falsification line**, and its
direction matters, so it is quoted before it is used. The preregistration that the
external record preserves reads: if the non-speech structure hits divided by the
unread passages is **below 1/20**, then the prediction does not hold
(`wenyan-relation-learning`, commit `ca0008c`,
`knowledge/relations/tangguoshibu-structure.json`, "preregistration"). The line is
therefore a **floor, not a ceiling**: the gate *passes* when the share is above it,
and the arithmetic of that record is:

```
non-speech hits   8 + 8 = 16   of  190 unread passages
share             16/190 = 8/95 = 0.084211  >  1/20 = 0.05
margin            the share is above the line, so the prediction is not falsified;
                  the gate would fail at 9 hits or fewer — 7 hits below 16
```

and of the five named patterns, two — `自…始` and `凡…皆` — scored **exactly
zero**. The gate is a function of the pair (numerator, denominator): **969
different component vectors** produce the same numerator 16, including one that
puts all 16 hits on a single pattern, **455 in which every one of the four
non-speech components is strictly positive**, and many that leave a named pattern
at zero. So a gate on the aggregate is not a test of the listed content, and it
passed while two of the five things it was written to detect were absent.

**A direction this section had backwards, corrected.** An earlier revision of this
section read the line as "the share must be *below* 1/20", answered "it is not",
and so reported the gate as **failed** — while §1's own table and this section's
own closing sentence reported it as **passed**, and the contract, the checker, the
evidence and `docs/claims.toml` all said the same. The note was therefore
self-contradictory in the one place where the two readings meet, and the places
that agreed agreed because they inherited the checker's direction without a source
for it. The external record settles the direction: its verdict on the prediction is
「未证伪」, *not falsified*, resting on `0.0842 > 0.05`, and it separately records
both that the two patterns it predicted scored zero and that a share line which
passes does not mean the format is right. So the direction kept is the checker's —
the falsification reading — and §1, §7, the contract, the claims entry and the
evidence now state it in the same terms. The record also does **not** record the
gate as a miss against its own threshold, as §1 and this section used to say: the
miss it recorded was its own prediction about the two patterns, which is a
different statement.

The arithmetic here adds the reason the pass carries no weight: the aggregate is
not a function of the components the prediction named.

## 8. What the checker ran

```console
python3 experiments/gain_and_coverage/checker.py --output experiments/gain_and_coverage/evidence.json
```

[`checker.py`](../../experiments/gain_and_coverage/checker.py) uses the standard
library only — integers and `Fraction`; no logarithm and no floating-point value
enters any acceptance test — and its output is compared against the retained
[`evidence.json`](../../experiments/gain_and_coverage/evidence.json) with
timings removed. The retained run records **79 assertions** over six sections in
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

**Decimal comparison is exact too, and one row changed when it was made exact.**
The five published three-decimal shares and the four-decimal gate value used to be
compared through `f"{float(share):.3f}"` and `f"{float(share):.4f}"`, which is the
one place a float still reached an acceptance test in a unit whose contract
forbids exactly that. Rounding is now done on the exact rational by integer
arithmetic, halves away from zero. Four of the five class rows still agree with
their published value; the `naming` row **flips from agreement to a recorded
disagreement**, for the reason given in §6 — the exact share is the half-way value
`0.3075`, so exact rounding is `0.308` while the published string is `0.307`, and
`0.307` is the truncation that a binary float also produces. The gate value
`0.0842` is unaffected: its exact four-decimal rounding *is* `0.0842`.
The claim in the contract and in `docs/claims.toml` has been narrowed from "the
five published values are reproduced" to "four are reproduced and the fifth is a
recorded one-unit disagreement".

Controls that keep the checks from being vacuous:

* the two declared limits are asserted to behave **differently** at the finer
  tolerance, so the coverage result is not one number reported twice;
* the finer tolerance is asserted to require a **larger** index bound than the
  coarser one, so the threshold is a threshold and not a constant;
* the gain order and the spread order are asserted to be **different** orders,
  so the rank-correlation claim is a comparison;
* the corpus baseline is asserted to be **above** the uniform-over-works value,
  so "the baseline is not `3/W`" is established rather than assumed;
* the declared numerator is asserted to be compatible both with a vector that
  leaves a named component at zero **and** with a vector in which all four
  components are strictly positive (455 of the 969), so the aggregate is shown
  not to determine the listed content. The two exactly-zero components themselves
  are **declared** numbers in the contract and are no longer dressed as a result:
  the line that asserted them restated the literal two lines above it and could
  not fail, and it has been replaced by the computed control just described.

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
  numbers, groups or music.** They are statements about the division and the size
  of the declared set. In particular the checker does *not* measure how well the
  declared points fit — the exact fit is not computed at all, and no claim is
  made about whether the point set could have been closer to the targets than it
  was. That question is left open, and it is the only one here that could have
  been evidence.
* **One published digit is contradicted, and only a digit.** The `naming`
  top-three share is published as `0.307`; its exact value is `2091/6800 =
  0.3075` and its exact three-decimal rounding is `0.308`. The arithmetic here
  contradicts that third decimal — it says nothing about the passage counts
  behind it, and it is not a claim that the external measurement was wrong about
  any passage. The same arithmetic leaves the other four published shares and the
  gate value `0.0842` exactly as published.
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
