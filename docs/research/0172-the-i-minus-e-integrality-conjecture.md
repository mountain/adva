# 0172 — The `(i − e)^(i − e)` integrality conjecture: recorded, and refuted on its principal reading

Status: research-only. This note records a conjecture that was put to the
repository by Mingli Yuan, states it precisely, and reports what can and cannot
be decided about it. It is **not** a claim in `docs/claims.toml` that the
conjecture holds; the refutation recorded here is a separate exact claim.
Evidence: `experiments/integer_power_absurdity/evidence.json`.

## 1. The conjecture

As given, in the words of the person who raised it: *`e` is transcendentally
irrational in the classical sense, and there is an absurdity conjecture whose
core is that `(i − e)^(i − e)` is exactly an integer.*

Written as a statement:

> **Conjecture (M. Yuan, 2026-09-11).** Let `z = i − e`. Then `z^z` is exactly an
> integer.

The word *absurdity* is doing real work in that sentence, and this note takes it
seriously: the conjecture is a joke with a mechanism inside it. `e` is
transcendental, `i` is algebraic, `z` is therefore transcendental, and the claim
is that raising it to its own power lands exactly on `ℤ`. Nothing forbids that in
principle — and that is exactly why it is worth writing down rather than waving
away.

## 2. The first thing that must be fixed: one statement per branch

As written the expression is not a number. Complex powers are defined by
`z^w = exp(w log z)`, and `log` is multi-valued: two values differ by `2 π i k`.
So the conjecture is a **family of statements indexed by an integer `k`**, and it
must be read that way before anything can be decided. This is not pedantry — the
branch index changes the answer qualitatively, as section 4 shows.

With `z = i − e`: `Re z = −e`, `Im z = 1`, `|z|² = 1 + e²` exactly, and `z` lies
in the second quadrant, so with

```
A = ln|z| = ½ ln(1 + e²),      B = arg z = π − atan(1/e),
```

we get `Log z = A + iB` and

```
z Log z = (−eA − B) + i(A − eB).
```

On the branch `k` the value is the principal value multiplied by
`exp(2πik z) = exp(−2πk)·exp(−2πike)`, so its modulus is

```
|z^z|_k = exp(−eA − B − 2πk),
```

and integrality requires **two** things: the modulus must be an integer, and the
phase `A − eB − 2πke` must be a multiple of `π`. Both are recorded below.

## 3. The principal branch is refuted, elementarily

This part needs no estimate at all. The two terms of `Re(z log z)` are

```
Re z · ln|z| − Im z · arg z = (−e)·A − 1·B,
```

and both are negative: `A = ½ln(1+e²) > 0` because `1 + e² > 1`, and
`B = π − atan(1/e) > π/2 > 0` because `0 < 1/e < ∞` and `atan` is bounded by
`π/2`. Therefore

```
|z^z| = exp(−eA − B) < 1
```

on the principal branch, strictly. And **no integer has a modulus strictly
between 0 and 1** — `0` is excluded because the exponential is never zero, and
every other integer has modulus at least one.

The executed checker sharpens the margin rather than merely asserting the
inequality. From `1 + e² > 4` and `e > 2` we get `A > ln 2`; from `B > π/2 > 3/2`
we get `eA + B > 2 ln 2 + 3/2`, hence

```
|z^z| < exp(−(2 ln 2 + 3/2)) = e^(−3/2)/4 < (2/5)/4 = 1/10,
```

and the interval computation confirms a bound of `1/10` with the measured
modulus `0.003413988192252096...`. The mechanism is visible in one line: **`i − e`
has negative real part, so `ln|z|` multiplies a negative number, and the imaginary
part contributes a second negative term.** Both terms push the modulus down.

## 4. What the remaining branches require

The run evaluates every branch from `k = −6` to `k = +6`, exactly, in rational
interval arithmetic at a 10⁻⁴⁵ grid, with `e` and `π` derived from their series
rather than quoted. All thirteen are refuted, and the two halves fail for
**different reasons**:

- **`k ≥ 0`**: the modulus is `exp(−eA − B − 2πk) ≤ exp(−eA − B) < 1/10`, so no
  such branch can be an integer. Nothing else needs checking.
- **`k < 0`**: the modulus grows like `e^{2π|k|}`, so it is above one and can be
  large. Here integrality is decided by testing whether the modulus enclosure
  contains an integer, and the enclosure is narrow enough to decide.

The rejected near misses are the interesting part, because this is where the
absurdity almost happens:

| branch `k` | `\|z^z\|_k` | nearest integer | off by |
|---:|---:|---:|---:|
| −1 | 1.828162189 | 2 | 0.1718 |
| −2 | **978.965597** | **979** | **0.0344** |
| −3 | 524227.908326 | 524228 | 0.0917 |
| −4 | 280719670.5016 | 280719671 | 0.4984 |
| −5 | 150323041095.2766 | 150323041095 | 0.2768 |
| −6 | 80496734139626.61 | 80496734139627 | 0.0209 |
| 0 | 0.003413988192 | 0 | 0.003414 |
| +1 … +6 | below 10⁻⁵ | 0 | shrinking by 10⁻³ each step |

On `k = −2` the modulus is `978.9656`: **thirty-four thousandths short of 979.**
That is the conjecture's aesthetic content in one number, and it is exactly the
kind of thing that should be recorded rather than dismissed — but a near miss is
not a hit, and the enclosure is tight enough to say so rigorously.

## 5. Where the absurdity actually lives

It is worth locating the absurdity precisely, because it is not where it looks.
The equation `z^z = n` for a **free** complex `z` is not absurd at all: it is a
transcendental equation with a rich solution set, so there are plenty of complex
numbers whose own power is an integer. What makes the conjecture absurd is that
`z` is **not free** — it is pinned to `i − e`, one algebraic unit minus one
transcendental constant, with no freedom left to tune. The absurdity is the
rigidity, not the operation.

And the refutation has the same character: not a deep theorem but a one-line
sign argument, which is the good kind of answer to a joke.

## 6. What is not decided, and what would be needed

The general statement over all branches is **not** decided here. Its phase
condition rearranges to

```
(A − eB)/π = j + 2 k e    for integers j and k,
```

an exact identity relating `e`, `π`, and a logarithm of `e`; the modulus
condition is the statement that a specific transcendental number is an integer.
Neither is available today. They are the territory of Schanuel's conjecture and
of the four exponentials conjecture, which would forbid such relations —
[most nontrivial combinations of two or more transcendental numbers are not known
to be transcendental or even irrational](https://en.wikipedia.org/wiki/Transcendental_number),
and even the algebraic independence of `e` and `π` is a consequence of Schanuel's
conjecture rather than a theorem. **None of that machinery is used here**, and the
undecided part is reported as undecided for that stated reason, not as false. By
the repository's rule, exhaustion of the declared range produces `Unknown`, never
a proof of nonexistence.

## 7. Errors recorded in this round

Five, all caught by the checks, and the fourth is the serious one:

1. **A loose enclosure at large arguments.** The exponential tail bound with
   eighty terms is over twenty at an argument near 43, which at a modulus of
   magnitude 10¹⁴ leaves an interval wider than one unit and cannot decide
   integrality at all. Fixed by argument halving and squaring, which keeps the
   relative width near 10⁻¹¹⁷.
2. **A wrong candidate set.** The first version searched the integers `1..12` for
   the modulus condition while the failing branches have moduli of magnitude
   10¹⁴, so it "refuted" those branches for a reason that was not the real one.
   Fixed by finding the integers actually inside the modulus enclosure.
3. **A float leak inside exact arithmetic.** The outward rounding to the declared
   grid computed `integer / scale`, which in Python 3 is true division and returns
   a float, silently reducing the "10⁻⁴⁵ grid" to double precision. Every
   precision claim made before this was measured was therefore false, and the
   enclosures at large magnitudes were wrong. Caught by measuring an interval
   width instead of trusting the declared one.
4. **A remainder bound that did not enclose.** The artanh series for `ln 2` was
   bounded by `t^(n+2)/(n+2)`, but with an even number of terms the last included
   odd index is `n−1`, so the first omitted term is `t^(n+1)/(n+1)` — larger by a
   factor of about 1.6 at `t = 1/3`. The "upper end" therefore sat *below* the
   true value, and the object was not an interval at all. It was caught by the
   internal consistency check that exponentiating `A` must return `1 + e²`; the
   resulting discrepancy of `1.05 × 10⁻³⁹` matched the predicted error exactly.
   This is the fifth error of this series in which a quantity was not the one its
   name said, and the first in which the quantity was an *enclosure* that failed
   to enclose.
5. **Two errors in the cross-check harness**, not in the library: a published
   digit string divided by the wrong power of ten, and a digit string whose
   leading integer positions were miscounted. Both were caught because the check
   failed. A third harness design was abandoned rather than patched: a bracket
   containment test against published digits cannot work when the enclosure is
   forty-five digits wide and the published string is twenty-five, so the
   cross-check is now an agreement at the published precision.

## 8. What this does not establish

- Not that the conjecture is false in full. The principal branch and every branch
  from `−6` to `+6` are refuted; the family is infinite and the rest is `Unknown`.
- No transcendence result. Nothing here decides whether `e^e`, `π^e`, `π^π`, or
  any combination of `e` and `π` is transcendental, and no such theorem is used.
- The published digits of `e`, `π` and `ln 2` are imported for a cross-check of
  the series code; the constants themselves are derived from their series.
- The numerical table is illustration. The verdicts rest on exact rational
  enclosures, not on the printed decimals.
- No relation to the stable API, the library, or any other note in this
  directory. This note sits beside the Arakelov–stability ladder and the
  density-wave ladder and touches neither.

## 9. Provenance

The conjecture is Mingli Yuan's, put as a question and an invitation to write it
down; the branch analysis, the refutation, the computation and the errors are
deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through his account as
an authorised proxy. He has not reviewed or endorsed the analysis, and his name is
not evidence for any part of it. The authority is the executed checker and the
retained evidence.
