# 0220 — What a declared family and a declared shift already fix

Date: 2026-09-24. Direction: Mingli Yuan. Analysis, checker and note:
deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through his account
as an authorized proxy. Account use is not his authorship, review or endorsement.

Status: one bounded external exact experiment. No Rust witness, no stable API
change, no library admission, no Seal, and no claim about any text.

Base: `79f6353511d736ae743b109f1c573b652eff170a`. Library gitlink:
`73a6af4ac4ed8225366d3c16794e309cff15f51d`.

---

## 1. What this answers

Two claims arrived from the parallel line of work and they are the same claim
twice. The first: *a formula built from a text's own numbers equals the number
423, and it is the only such formula among sixteen thousand eight hundred
fifteen candidates.* The second: *the pairings of the eighty-one heads all shift
by forty, so seven pairs lie inside the cut at forty-seven and thirty-four
straddle it — and thirty-four is exactly the size of the cut's other side.*

Both claims are tested here **without importing anything**. The first is tested
by asking what share of the seven hundred twenty-nine praises a declared family
of expressions reaches at all: if the family reaches most of them, then "some
expression equals the target" was already fixed by the declaration. The second is
tested by asking, for a declared shift and a declared cut, how the pairs split:
if the crossing count equals the size of the cut's second side for forty of the
eighty cuts, then the agreement says nothing about forty-seven.

The results:

1. **The price of a hit is the coverage.** For the thirteen constants this record
   already declared, the family names **497 of 729 praises**, and that ratio is
   exactly the chance that a target drawn uniformly and independently is named.
   A separate record reports a much larger coverage for a much larger constant
   set; §2 states what that does and does not license.
2. **A family rich enough reaches everything.** The first seventy-three
   consecutive integers name **every one** of the 729 praises, so for that
   constant set "some expression equals 423" has probability one. Fourteen
   constants chosen by a declared greedy already suffice.
3. **The crossing count is an identity, not a finding.** For a shift `d` and a
   cut `c`, the number of pairs straddling the cut is `min(d, 81−c)` whenever
   `c ≥ d`, so it equals the size of the second side at **forty of the eighty
   cuts** for `d = 40`. The cut that is actually distinguished by this structure
   is **41**, not 47.

**No text and no corpus count is imported.** Every constant set, the family, the
shift and the cut are declared in this experiment's contract.

## 2. The price of a hit is the coverage

The family is the one 0218 declared: for constants `a, b` in a set `C` and
multipliers `k = 2 … 9`, the forms are

```
a,   a + b,   |a − b|,   k a + b,   k a − b
```

kept when the value lies in `Ω = {1, …, 729}`. The bare form carries no partner,
so a constant that happens to be the target contributes one expression and not
one per partner — that detail matters in §3.

> **Price.** If `C` is fixed before the target is named and the target is drawn
> uniformly from `Ω`, then `P(the family names it) = |image(C)| / 729`.

| declared constant set | `|C|` | praises named | coverage |
|---|---|---|---|
| the thirteen constants of 0218 | 13 | 497 | 497/729 = 0.6818 |
| those thirteen with 1 | 14 | 518 | 518/729 = 0.7106 |
| the structural constants `{1,2,3,4,9,27,40,81,729}` | 9 | 319 | 319/729 |
| the first nine integers | 9 | 90 | 10/81 |
| the first twenty-seven | 27 | 270 | 10/27 |
| the first forty | 40 | 400 | 400/729 |
| the first seventy-two | 72 | 720 | 80/81 |
| **the first seventy-three** | **73** | **729** | **1** |

Two structural facts, both decided by exhaustion and not by argument.

**The image is monotone in the constant set.** Adding a constant can only add
expressions, so it can only enlarge the image; verified over all 32 nested pairs
of the ten declared sets. A consequence that matters more than the fact itself:
**a unique hit cannot be created by adding constants.** It can only be destroyed.
A claim of uniqueness is therefore a claim about how small `C` was.

**The first `n` consecutive integers name exactly the first `10n` praises** while
`10n ≤ 729`, verified for every `n` up to 90 — the whole interval `[1, 10n]` is
reachable and nothing above it is. So the coverage of `{1, …, n}` is exactly
`min(10n, 729)/729`, which crosses nine tenths at `n = 66` and reaches **one** at
`n = 73`. For the family as declared, a document that supplies the seventy-three
integers 1 to 73 has made every praise expressible, and no expression over them
can be evidence of anything.

This is the quantitative form of the aperture the parallel line recorded as
"report coverage, not uniqueness". Two further numbers bound how small a
covering set can be: counting the expressions a set of size `m` can write gives
`m + 18m²`, which is below 729 until `m = 7`, so **no constant set of six or
fewer members can cover `Ω`**; and a declared deterministic greedy over the pool
`{1, …, 90}` reaches all 729 praises with **fourteen** constants,
`{1, 12, 26, 63, 65, 67, 70, 73, 75, 76, 80, 83, 86, 88}`. So the smallest
covering set lies in `[7, 14]`, and **the smallest covering set is not decided by
this experiment**. That residual is stated rather than papered over: the counting
bound is weak and the greedy is one declared search.

**The multiplier range is a declared parameter.** These figures belong to
`k ≤ 9`. Holding the thirteen constants fixed and varying only the multiplier
range gives

| `k` up to | 2 | 3 | 4 | 5 | 6 | 7 | 8 | **9** | 12 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|
| praises named | 223 | 280 | 339 | 385 | 420 | 460 | 497 | **497** | 569 | 664 |

so the same constants name 497 praises or 223 depending on a bound nobody had to
state. A record that reports a coverage without declaring its multiplier range
has not reported a computable price at all, which is the same lesson one level
up: the family is only priced once every part of it is declared.

**What this does not license.** Another record reports 692 of 729 for a constant
set of eighty-three numbers taken from the text it studies, and twenty-five
expressions naming 423 there. Those figures are **that record's**, belong to a
constant set this experiment does not have and must not import, and are neither
reproduced nor re-derived here. What this experiment adds is the shape of the
statement and its threshold: coverage rises quadratically in the number of
constants, seventy-three consecutive integers already reach one, and at any
coverage `ρ` a family "hitting" a target is an event of probability `ρ`.

## 3. A target that is a declared constant proves nothing

423 is one of the thirteen constants 0218 declared. So the bare form `a` names
it, and "the family names 423" is a tautology for that set. This is worth
separating out because it is invisible in a count: the family names 423 by
**seven** expressions, but five of them survive removing 423 from `C`, and the
one that does not is the tautology.

| target | a declared constant? | expressions naming it | once 423 is not a constant |
|---|---|---|---|
| 421 | no | 3 | 1 |
| 423 | yes | 7 | 5 |
| 613 | no | **0** | 0 |

Removing the target shrinks the image from 497 to **472**. The discipline this
implies is short: **the constant set must exclude the target**, or the price is
not a price. It also explains an asymmetry in the earlier notes that was never
stated: 421 is named three times by the declared family and 613 is named **not at
all** without the trivial constant — the two numbers that started this line are
not symmetric with respect to the family, and the family was declared around one
of them.

## 4. Multiplicity, and why it is the wrong numerator

The number of expressions naming each praise is monotone in `C` too, for the same
reason, and it is bounded by the number of forms: at most `m + 18m²` for a set of
size `m`. Over the thirteen constants the histogram is

| expressions naming it | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| praises | 173 | 94 | 89 | 47 | 32 | 25 | 12 | 8 | 11 | 3 | 1 | 1 | 1 |

The largest multiplicity is **15**, at the praise 54, and 173 of the 497 reached
praises are named exactly once. A "unique hit" is therefore the *common* case at
this coverage: it is what happens to 35% of the reached targets, so it cannot be
the signature of a designed expression. And monotonicity kills the statistic as a
test: adding constants can only increase a multiplicity, so uniqueness can never
be evidence *for* a formula, only a report of a small `C`.

## 5. The crossing count of a declared shift

The second claim is about the eighty-one heads. Fix a shift `d` and a cut `c`, and
let the declared pairs be `(n, n + d)` for `n = 1, …, 81 − d`; a pair lies
*inside* the cut if `n + d ≤ c` and *straddles* it if `n ≤ c < n + d`. Both counts
have closed forms, and the checker verifies them against a direct count at **all
6 400 pairs** of a shift and a cut with no mismatch:

```
pairs(d)     = 81 − d
inside(d, c) = max(0, min(c − d, 81 − d))
straddle(d, c) = min(d, 81 − c)   for c ≥ d
```

For the declared shift and cut — `d = 40`, `c = 47` — this gives pairs **41**,
inside **7**, straddling **34**, and the second side of the cut has `81 − 47 = 34`
members. So the reported agreement is reproduced exactly, and it is an identity of
the shift rather than a fact about the cut:

> **The number of pairs straddling a cut equals the size of that cut's second
> side at every cut `c` with `81 − d ≤ c ≤ 80`.**

For `d = 40` that is the **forty cuts 41 through 80**. Every one of them exhibits
the same coincidence, and what distinguishes 47 is nothing: the crossing count is
`min(40, 81 − c)`, which is the constant 40 while `c ≤ 41` and then becomes
`81 − c` — the size of the second side — for every later cut. The only
distinguished cut in this structure is **`c = 81 − d = 41`**, where the second
member of a pair can first exceed the cut. And the `inside` count is not even a
switch: `inside(d, c) = c − d` for all `c ≥ d`, so "seven pairs lie inside" is
the subtraction `47 − 40`.

One line for the whole reading: **for any shift and any cut past the midpoint,
the crossing count is the size of the cut's second side, so a pairing law of this
shape can never make a cut special.** In particular the observation that "the
number of crossing pairs equals the number of heads on the other side" is not a
fact about the cut at all. The parallel record itself flagged this observation as
structurally different from its six earlier arithmetic negations — it asked where
the cut sits in the pairing structure rather than where the number 47 came from —
and the answer is that the pairing structure does not see the cut either.

Where the shift *does* carry information is that it is a fixed shift. That part
stands: `81 − 40 = 41` pairs, all of the same length, and no other length occurs.
The arithmetic negation is only of the cut's position, not of the shift.

## 6. The gauge correction, and two numbers that do not follow from the law

The parallel record corrected an earlier conclusion of its own — "the shift is not
a fixed displacement" — and gave as the cause a wrong choice of gauge: in the
four-place coordinates, adding forty to a head number is not adding a constant
vector, because the addition carries. That diagnosis is right, and it is exactly
the odometer structure of note 0214. Made exact:

`40 = 1111₃`, so `n ↦ n + 40` is adding `1111₃` to the base-three numeral of
`n − 1`, with carries. Carries distort the coordinate difference, and the
difference is exactly `(1,1,1,1)` precisely when no carry occurs. For the 41 pairs
that happens at **16** of them — the heads whose four digits are all 0 or 1 — and
the difference takes eight values with multiplicities `16, 4, 4, 4, 4, 4, 4, 1`.
The general count is exact and was verified for all eighty shifts:

```
pairs with a constant coordinate difference = ∏ (3 − digit of the shift)
```

which is `2⁴ = 16` for `d = 40` because all four of its digits are 1.

Two numbers in the record cannot be reproduced from the stated law. The law says
the pairs are `(1,41) … (41,81)` and that all 35 differ by forty; the same note
then splits them into 7 inside plus 34 straddling, which is 41. **Arithmetic gives
41 pairs, not 35**, and the coordinate reading gives **16** pairs with a constant
difference, not the 13 that was recorded against 35. The correction was right in
kind — the coordinate gauge is the wrong one — and both of its numbers are
inconsistent with the law it corrects to. This experiment decides only what the
stated law implies; it makes no claim about the pair list the record drew from
its source.

## 7. What the checker ran

`experiments/coverage_and_crossing/checker.py` against
`experiments/coverage_and_crossing/contract.json`, five sections, **820
assertions**, `ExternalExactPass`, in 1.4 s wall.

`RLIMIT_CPU`, `RLIMIT_FSIZE` and the wall alarm are installed; **no address-space
ceiling is installed**, because this checker launches no child process — the
convention 0211 had to adopt after its first version broke the frozen resource
inventory. An existing output file is refused, never overwritten.

`tests/python/test_coverage_and_crossing.py` re-runs the checker in a temporary
directory and compares the mathematical payload of the fresh run with the
retained evidence, section by section, with timing and platform keys removed. No
floating-point value enters any acceptance test: coverages are compared as
`Fraction`s parsed from the exact strings in the evidence, and the recorded
floats are never read by a test.

## 8. Residual and non-claims

- **No text and no corpus count is imported.** No constant list taken from a text
  is imported; every constant set here is declared in the contract. The figures
  another record reports for its own eighty-three constants are cited as that
  record's, are neither reproduced nor re-derived, and are not the quantities
  computed here.
- **The smallest covering constant set is not decided.** The counting bound gives
  `≥ 7`, a declared greedy gives `14`, and the true minimum is somewhere in
  between. Nothing here claims the greedy is optimal.
- **The multiplier range and the form list are declared, not natural.** All
  coverage figures belong to `k ≤ 9` and to these five forms. A record that does
  not declare its multiplier range has not stated a computable price.
- **The coverage is a ratio, not a probability of anything that happened.** It is
  the chance a target drawn uniformly and independently of the constant set is
  named, and no target here was drawn that way; it is the right denominator for a
  hit and not a p-value.
- **The crossing identity is a statement about one declared shift on the head
  numbers.** It is not a claim about pairings, oppositions, seasons, calendars or
  any other structure, and nothing here says what any shift means.
- **The pair count recorded elsewhere is not claimed to be wrong about its
  source.** What is decided is what the stated law implies arithmetically: forty-one
  pairs, sixteen of them with a constant coordinate difference.
- **No claim that any number's presence in or absence from the image is
  meaningful, intended, or evidence about any text.**
- **No SourceId, observer, aperture, clock, operation, native witness or Seal is
  created**, and no claim is promoted beyond `bounded-experiment`.

## 9. What changed in the repository

- `experiments/coverage_and_crossing/checker.py`, `contract.json`, `evidence.json`
  — the bounded experiment, 820 assertions.
- `tests/python/test_coverage_and_crossing.py` — twelve tests over the retained
  evidence, the fresh-run payload, the no-overwrite rule, the coverage ladder, the
  interval statement, the bracketed minimum, the excluded target, the
  multiplicity, the crossing identity, the gauge, the contract's protected list,
  this note's residual, and the registered claim.
- `docs/claims.toml` — `adva.bounded-experiment.coverage-and-crossing.v0`.
- `docs/research/README.md` — this note added to the index and the numbered count
  advanced.
