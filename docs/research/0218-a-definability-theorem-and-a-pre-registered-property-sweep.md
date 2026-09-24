# 0218 — A definability theorem, and a sweep declared in the contract

Date: 2026-09-23. Direction: Mingli Yuan. Analysis, checker and note:
deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through his account
as an authorized proxy. Account use is not his authorship, review or endorsement.

Status: one bounded external exact experiment. No Rust witness, no stable API
change, no library admission, no Seal, and no claim about any text.

Base: `79f6353511d736ae743b109f1c573b652eff170a`. Library gitlink:
`73a6af4ac4ed8225366d3c16794e309cff15f51d`.

> **On the word "pre-registered" in this file's name.** The experiment's slug
> still carries it, and the record does not. What the repository can show is
> this: both families are declared in `contract.json` under
> `objects.declared_properties` and `objects.declared_head_sets`; the checker
> reads them out of that file, refusing to run on a name it cannot construct or
> on a construction rule the contract does not declare, so the families it
> sweeps are the declared ones; the contract, the checker, the evidence and this
> note were introduced by a single commit (`56b0bcf`), whose base is the
> `base_commit` above; and no earlier record of the declarations exists in the
> repository (`git log -S declared_properties --all` finds that one commit and
> no other). **There is therefore no independent timestamp and nothing is dated
> before the counting.** The sweep is declared, not registered in advance, and
> the claim that a family was fixed before its results were seen is one this
> repository cannot support.

---

## 1. What this answers

The question that started this was narrow: *what is special about the 613th
praise, and can it explain a classical pair of hexagrams?* The answer was that
613 is the first praise of head 69 and nothing more, and that the proposed
explanation fails on three independent counts — but the *shape* of the question
kept recurring, and this note gives that shape its mathematics. Two things come
out of it: **a theorem about how many places a set of heads needs before the
address algebra can see it**, and **a sweep, declared in the contract, that
prices a coincidence against a declared family rather than against nothing.**

**No text and no corpus count is imported.** The address space, the twelve
arithmetic properties and the ten head sets are declared in this experiment's
contract, the checker reads both families out of that contract, and the
declarations and the results carry the same commit and no earlier one (the box
above). No corpus is opened.

## 2. The invariant, and its theorem

Let `Ω = {1..729}` be the praises, partitioned into the eighty-one blocks
`B_h = {9(h−1)+1, …, 9h}`, one per head. Each head is a point of `Z₃⁴`.

For `S ⊆ {1,2,3,4}` let `𝔸_S` be the sets of heads definable by the places in
`S` alone — the unions of fibres of the projection `π_S`. Every fibre has
`3^{4−|S|}` points. Define

```
μ(A) = min { |S| : A ∈ 𝔸_S }        "how many places this division needs"
```

> **Theorem.** For non-empty `A`, `3^{4−μ(A)}` divides `|A|`.
> Hence `3 ∤ |A|` implies `μ(A) = 4`.

One line: every element of `𝔸_S` is a union of fibres, and each fibre has
`3^{4−|S|}` points. Verified by exhaustion over all `2⁴ · 81 = 1296` fibres.

## 3. What the theorem decides, and what it does not

| declared set | size | μ |
|---|---:|---:|
| the whole head set | 81 | 0 |
| the first quarter | 27 | **1** |
| the nine district representatives | 9 | **2** |
| the three quarter representatives | 3 | 3 |
| the cut's first side | 47 | **4** |
| the cut's second side | 34 | **4** |
| the two prison heads | 2 | **4** |
| the orbit of head seven | 3 | **4** |
| a single head | 1 | **4** |

Three consequences:

* **The cut's invisibility stops being a search result.** [0216](0216-the-magic-hypercube-and-a-cut-the-address-cannot-see.md)
  established it by exhausting all fifteen proper subsets. Here it is arithmetic:
  `47 ≢ 0 (mod 3)`, so no three places suffice, and a fortiori no fewer do. The
  same one-liner disposes of the second side (`34`) and of the two prison heads
  (`2`).
* **The theorem predicts.** *Every* set of heads whose size is not a multiple of
  three needs all four places. That is a statement about the address algebra, not
  about any particular division.
* **But the bound is not tight, and the table shows it.** The orbit of head seven
  has size `3`, which the theorem permits to be definable in three places, and its
  `μ` is nevertheless **4**; the three quarter representatives, also of size 3,
  have `μ = 3` (they are `州 = 部 = 家 = 1`). So divisibility is necessary and not
  sufficient, and the difference between the two sets of size three is real
  structure rather than arithmetic.

## 4. The null model, exactly

A property `P ⊆ Ω` selects the heads it meets:

```
σ(P) = { h : B_h ∩ P ≠ ∅ }
```

For a uniform subset of size `s`, the chance that it meets every one of `m`
given heads is an inclusion–exclusion over blocks:

```
P(H₀ ⊆ σ(P)) = Σ_{j=0}^{|H₀|} (−1)^j C(|H₀|, j) · C(729 − 9j, s) / C(729, s)
E |σ(P)|    = 81 (1 − C(720, s) / C(729, s))
```

At `s = 9` this gives `E|σ(P)| = 8.6132` heads, and

| heads required | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| probability | 0.1063 | **0.01017** | 0.000862 | 6.34·10⁻⁵ | 3.93·10⁻⁶ | 1.98·10⁻⁷ |

**A nine-element property is not a single probe.** It hits eight point six heads,
so meeting two given heads is about one in a hundred — not the one in three
thousand two hundred forty that a single-probe intuition suggests. That
correction is spent in section 6.

## 5. The sweep, and where its families come from

Twelve declared arithmetic properties of praise numbers (prime, centred square,
square, perfect power, triangular, Fibonacci, palindromic, three congruences, sum
of two squares, power of three) against ten declared head sets (the three
quarters, the two sides of the cut, the nine district representatives, the three
quarter representatives, and three district levels). Both families are the ones
`contract.json` declares, and the checker builds them by reading those names out
of the contract and matching each against a construction rule: a name with no
rule, a rule with no declared name, a repeated name or a wrong count stops the
run. The families and the count below are one commit's work, so the honest
statement is that the families are declared and read from the declaration, not
that they were fixed before the count was seen.

```
pairs                              120
observed containments               34
expected containments             8.29
pairs below five per cent           95
pairs below one per cent            90
pairs below a tenth of a per cent   81
```

And the observed count is **not** evidence of anything, because the sweep itself
says why. The heads each property reaches:

```
≡1 mod 4        81 of 81        centred square   18
≡1 mod 9        81              Fibonacci        10
sum of two squares 81           power of three    5
```

**Three of the twelve properties reach every head**, and those three alone
contribute **30** of the 34 observed containments. The reason is structural: the
uniform-same-size null is a null of *exchangeable* subsets, and an arithmetic
property is not exchangeable — a congruence class is spread evenly by
construction, so it meets every block. The null therefore **under-predicts** for
exactly the properties that matter, and the corrected reading is not "34 is more
than 8.29, so something is happening" but "the null was the wrong shape".

Recording that is the point of running the sweep rather than reasoning about one
number.

## 6. The post-hoc entry, and the price I got wrong

The coincidence that prompted all this: the praises that are **both prime and
centred squares** are nine, they select nine heads, and two of those heads are
the two prison heads.

```
praises     5, 13, 41, 61, 113, 181, 313, 421, 613
heads       1, 2, 5, 7, 13, 21, 35, 47, 69
p           3133760077447169 / 308069738356701321 = 0.010172
```

**My first price for this was wrong by a factor of thirty-three.** I reported
`1/C(81,2) = 0.000309`, which treats a nine-praise property as though it selected
one head. It selects 8.6. The corrected value is **1.02%**, and the error is
recorded rather than quietly replaced.

And the corrected value is not small in the company it has to keep:

> **90 of the 120 declared pairs are at least as unlikely as the post-hoc one.**

So the coincidence sits in the *less* surprising quarter of a table that was
built without it. It is not the most unlikely thing in its own experiment. This
is the whole reason for pricing a hit against a declared family instead of
against nothing: the question is never "is this unlikely?" but "is this more
unlikely than the field it was selected from?" — and here it is not.

## 7. The vacuity, proved

In section 5 of the previous note I said that the two prison heads "lie in a
common three-cycle" and treated it as structure. **That claim is void, and here is
the proof rather than the impression.**

`Z₃⁴` has exponent three, so every non-zero `d` has order three. Therefore

```
∀ x ≠ y  ∃ d ≠ 0 :  y ∈ ⟨d⟩·x        (take d = y − x)
```

The relation "there exists a displacement putting two heads in one cycle" is
**total**, and the checker decides it by computing rather than by writing three
times a residue modulo three: the additive order of every one of the eighty
non-zero differences is computed by adding the difference to itself until it
vanishes, every one of the `6480` ordered pairs of distinct heads is put in the
three-cycle its own difference generates and found there, and one fixed
displacement is checked to partition the eighty-one heads into twenty-seven
three-cycles with no exception. The earlier version of this control multiplied
the difference by three and tested the product modulo three, which is identically
zero: it could not have failed and carried no information, and it is recorded
here rather than quietly replaced. A total relation partitions nothing and
discriminates nothing.

What survives from that section is the different statement that **one fixed
displacement carries both pairs** (`7 ↦ 47` and `8 ↦ 48` by the same `(1,2,1,1)`),
which constrains the displacement and not merely the points.

## 8. The coverage, and the constant list

Whether a number "can be paired with the system's own numbers" is a property of
the declared constant list, not of the number. With thirteen structural constants
and the forms `a`, `a+b`, `|a−b|`, `k·a ± b` for `k ≤ 9`:

```
image without the trivial constant    497 of 729 = 68.2%
image with    the trivial constant    518 of 729 = 71.1%
```

`421` is expressible without it (`421 = |423 − 2|`, the cut's praise count minus
the two extra praises); `613` is expressible **only** once the trivial `1` is
admitted (`613 = 2·306 + 1`). So the premise "neither can be paired" was a
statement about the list.

A small slip is kept in the record: an earlier count of the image was **501**, and
it dropped to **497** when the definition stopped admitting the constant `1`
implicitly inside the form `a ± 1`. Four numbers, from a definition detail — which
is the same lesson at a smaller scale.

## 9. What the checker ran

```console
python3 experiments/preregistered_sweep/checker.py --output experiments/preregistered_sweep/evidence.json
```

[`checker.py`](../../experiments/preregistered_sweep/checker.py) uses the standard
library only — integers and `Fraction`; no floating-point value enters any
acceptance test, every comparison being an integer or a `Fraction` comparison,
and the decimal fields in the record being display copies of exact rationals —
and its output is compared against the retained
[`evidence.json`](../../experiments/preregistered_sweep/evidence.json) with
timings removed. The retained run records **1,432 assertions** over six sections
in under a second, having exhausted 1,296 fibres, ten declared sets for the
minimal place count, six containment sizes for the null, 120 declared pairs for
the sweep, 6,480 ordered pairs for the vacuity, and the whole declared expression
family twice. `RLIMIT_CPU`, `RLIMIT_FSIZE` and the wall alarm are installed; no
address-space ceiling is installed because the checker launches no child process.
The checker refuses to overwrite an existing output path.

Controls that keep the checks from being vacuous:

* the fibre sizes are asserted for **every** subset and every head, so the
  theorem rests on the structure and not on a sample;
* a set of size three is asserted by the **checker** to have `μ = 4` **and**
  another set of size three to have `μ = 3`, so "the bound is not tight" is
  exhibited rather than claimed;
* both families are read out of the contract and the construction rules are
  compared with the declarations both ways, so a family that is not the declared
  one cannot be swept;
* the expected number of heads hit by nine praises is compared as an exact
  rational against `86132/10000`, and the vacuity control computes the additive
  order of every non-zero difference instead of multiplying a residue by three;
* both monotonicities of the null are asserted — falling with the target size,
  rising with the property size — so the table is not a coincidence of numbers;
* the sweep is asserted to have **120** pairs and the observed count is asserted
  **not** to be the whole table;
* the post-hoc entry is asserted to be **outside** the declared pairs, and the
  corrected price is asserted to be more than thirty times the naive one;
* the coverage is asserted to be **above two thirds**, so the "everything pairs"
  claim is a measurement.

## 10. Residual and non-claims

* **The post-hoc entry is not a p-value in the sense the table's entries are.**
  Its property is not one of the twelve declared properties and its target is not
  one of the ten declared head sets, and the checker asserts both of those rather
  than assuming them; it is reported separately for exactly that reason. The
  label "post hoc" records where the entry came from — the question that started
  this experiment — and not a dated sequence the repository can produce.
* **The property family is one declared family among many.** Twelve arithmetic
  predicates are declared in the contract and read from it by the checker; a
  different family gives different counts, and the family is not claimed to be
  natural or complete.
* **The null is uniform over subsets of a fixed size and models no process.**
  Section 5 shows the price of that: it under-predicts for evenly spread
  properties, which is a property of arithmetic predicates and not of the data.
* **No family-wise tail is computed.** The 120 pairs are dependent — the same
  property is tested against ten sets — so the counts below thresholds are
  descriptive and no corrected significance is claimed.
* **The theorem bounds the minimal place count from below.** A set of size
  divisible by three is not thereby definable; the orbit of head seven is the
  exhibited counterexample.
* **The head sets named for districts and quarters are coordinate sets**, not
  readings of any text. The nine district representatives are used because an
  external record names them, and that use is a declaration, not a verification.
* **No claim about what any head or praise means**, and no claim that any
  containment is intended by anyone.
* **No native consequence.** No `SourceId`, observer, aperture, clock, operation
  or `Seal`; the address algebra, the null model and the sweep are not claimed as
  native structures.
