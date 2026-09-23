# 0212 — What a declared invariance already fixes

Date: 2026-09-23. Direction: Mingli Yuan. Analysis, checker and note:
deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through his account
as an authorized proxy. Account use is not his authorship, review or endorsement.

Status: one bounded external exact experiment. No Rust witness, no stable API
change, no library admission, no Seal, and no claim about any text.

Base: `79f6353511d736ae743b109f1c573b652eff170a`. Library gitlink:
`73a6af4ac4ed8225366d3c16794e309cff15f51d`.

---

## 1. Where the question came from, and what is not imported

A second body of work outside this repository —
`~/wenyan-relation-learning`, at commits `a91b269` (reciprocity) and `9bc4a86`
(five-phase tables) — reported two results and one retraction:

| Reported there | Their number |
|---|---|
| two-way exchanges in the extracted speech network are more common than chance | 79 of 3,316 edges = 2.38%, against a 200-permutation null mean of 0.0875%, percentile 100 |
| the five-phase correspondence tables are **not** recoverable from passage co-occurrence | diagonal share 16.6%–22.4% against a 20% chance baseline; the argmax of every one of the first four phases collapsed onto the same globally frequent item |
| the 2.6×–116× spread of the diagonal counts is phase asymmetry | **retracted**: it is item frequency, not phase weight |

Their diagnosis of the second is one sentence: *co-occurrence is not alignment*.
Their own proposed repair for the third was to replace a greedy row argmax with
an optimal assignment.

**This note imports no corpus, no count and no text from that repository or from
anywhere else**, and it re-runs none of their measurements. Their numbers are
cited as their results. What is abstracted here is the mathematics those results
depend on, stated for declared synthetic objects, and the third finding below
contradicts their proposed repair.

The direction is Mingli Yuan's: the same two ideas that motivated
[0211](0211-six-places-two-alphabets-and-the-policy-of-a-finite-arithmetic-truth.md)
— a finite observer, and an arithmetic truth it can settle — reappear here as a
question about what an invariance declared *before* any data fixes.

## 2. One tetrahedron, two symmetry sets

The scheme being tested elsewhere puts four values on the vertices of a
tetrahedron and the six persons or slots on its edges. Two families of
"mirrors" are then named in the same breath, and the interesting part is that
**they are not the same group**.

Take the complete graph `K₄`: four vertices, six edges, three perfect
matchings. Exhaustion gives:

* The three **axis swaps** — the permutations of cycle type `(2,2)`, one per
  matching — each determine exactly one matching, fix exactly the two edges of
  that matching and move the other four, and commute pairwise. With the
  identity they form a group of order four.
* Their action on the six edges has **exactly three orbits, of size two, and
  those orbits are the three matchings**. So "the three axis swaps are the
  three opposite-edge pairs" is not an analogy: the orbits *are* the pairs.
* The action is **not free** and is not claimed to be: each edge has a
  stabiliser of order two, namely the swap of its own matching.

Now the other family. The **four face mirrors** of the fundamental alcove
generate the affine Weyl group of type `A₃`, identified here by its Coxeter
relations and by the finite part recovered below. The checker builds it from
four affine isometries of the lattice `{x ∈ Z⁴ : Σx = 0}` and verifies:

* all four are involutions; pairs adjacent in the four-cycle diagram have
  product of order three, and the two non-adjacent pairs commute — the
  Coxeter relations of `Ã₃`, checked on all six pairs;
* the group is **infinite**: 5,781 elements within Coxeter length twenty, and
  the counts do not stop;
* the **origin stabiliser has exactly twenty-four elements**, and their Coxeter
  length distribution is `1, 3, 5, 6, 5, 3, 1` — the finite Weyl group `S₄`,
  recovered as a bounded slice of the infinite one rather than assumed;
* the closure's counts are not merely polynomial in order but **exact
  polynomials**, verified for every `n ≤ 20`:

```
alcoves at Coxeter distance exactly n     2n² + 2                (n ≥ 1)
alcoves within Coxeter distance n         1 + 2n + n(n+1)(2n+1)/3
```

Two settled facts about the pair of groups:

* the order-four group is a subgroup of the finite part of the closure, and
* it does **not** generate the closure.

So the same four faces support a symmetry set of order four and a symmetry set
of infinite order, and which one you obtain is decided entirely by which
generators are declared. The finite one is the origin stabiliser; the infinite
one tiles. Neither is "the" symmetry of the tetrahedron.

## 3. A rank-one matrix has no row-specific information

The second object is the arithmetic of a co-occurrence table: an `m × n`
nonnegative integer matrix whose rows are phases and whose columns are the items
of one correspondence category.

Declare `M[i][j] = r_i · c_j` with `r = c = (1,2,3,4,5)`. Every `2 × 2` minor
vanishes, so `M` is exactly rank one, and the exhaustive check over the declared
weight sweep (1,701 matrices) confirms the elementary fact that makes the
rank-one case decisive:

> **Every row's argmax is the same column.** If `M = r cᵀ` with `c > 0`, then
> every row with `r_i > 0` attains its maximum in the column maximising `c`, and
> in the tie set of that column alone.

Here that column is the fifth, the one carrying the largest column weight. All
five rows point at it. **No row can name its own item.** The matrix carries
exactly zero row-specific information, and that is a theorem about rank one, not
a measurement.

Now the statistic that was actually reported elsewhere. The **diagonal share**
of this matrix is

```
diagonal share   55/225 = 11/45 ≈ 0.2444
chance share      1/5   =  9/45 =  0.2000
excess                       2/45 ≈ 0.0444
```

**A table with provably zero row-specific information reports a diagonal share
4.4 percentage points above chance.** The excess is not evidence of anything; it
is the co-monotonicity of the two margins. Measured diagonal shares of 16.6%–
22.4% against a 20% baseline are, on this arithmetic, entirely inside the range
that marginals alone can produce.

## 4. The obvious repair does not work

The natural objection is that a row argmax is a crude reading and that an
**optimal assignment** — maximise `Σᵢ M[i][σ(i)]` over all bijections `σ`, which
is what the other repository proposed — would do better. It does worse.

Exhaustive enumeration of all 120 bijections gives:

* For sorted weights `r = c = (1,2,3,4,5)`, the identity is the **unique**
  assignment optimum of the rank-one matrix. That is the rearrangement
  inequality, and it holds at **zero** perturbation.
* For a declared unsorted pair, the unique optimum is the similarly-ordered
  permutation and the identity is not an optimum at all.

So the assignment reading recovers the canonical table **exactly when there is
nothing to recover**, and the reason is the same as before: the objective is a
function of the two margins. It is not an alignment test.

The two readings can be compared directly on a declared family,

```
M(t)[i][j] = r_i c_j + t · δ_ij · r_i c_i
```

which plants the canonical labelling on the diagonal with amplitude `t`. Both
readings are decided by exhaustion on a grid of ten exact rational values:

| reading | first grid point that succeeds |
|---|---|
| every row uniquely recovers its own column | `t = 5` |
| the identity is the unique assignment optimum | **`t = 0`** |

The row reading's threshold has an exact closed form, verified per row:

```
row i recovers its own column  ⟺  t > max_{j≠i} c_j / c_i − 1
```

which for `c = (1,2,3,4,5)` is `4, 3/2, 2/3, 1/4, −1/5` — the binding value is
`4`, and every row succeeds uniquely only above it. One more detail worth
keeping: at `t = 4` the first row *ties* with the fifth column and the crude
reading passes by tie-breaking. The checker records the tie separately rather
than counting it as a recovery.

So on this family the crude reading fails until the planted signal is enormous,
and the sophisticated reading succeeds immediately. **Both are margin-driven,
in opposite directions, and a table whose row-specific information is zero is
certified by the second and rejected by the first.**

## 5. A permutation null sees only the two margins

The third object is the reciprocity statistic of a directed network: the number
of edges `a → b` whose reverse `b → a` is also present. The null that was used
elsewhere keeps the agents and permutes the recipients, which preserves both
degree multisets.

The checker enumerates **every** permutation rather than sampling: 1,608
permutations over five declared networks of four, five and six edges. The exact
law, not an estimate:

* **Two declared networks with the same two margins have identical exact null
  laws.** One is fully reciprocal (observed `6/6`), the other is an
  out-star (observed `0/6`). Their null law is the same, with support `0..6`
  and mean `14/5` — that is, **the null expects `7/15 ≈ 46.7%` of the six edges
  to be reciprocal** on those margins. The two observed values are judged
  against the same baseline of 46.7%.
* The mass the null places on a fully reciprocal network is exactly `4/45`, so
  the one-sided `p`-value of a *perfectly* reciprocal six-edge network under its
  own null is `4/45 ≈ 0.089` — **not significant at 5%**.
* A declared five-edge chain has exact null mean `1`, variance `2`, support
  `0..4`, and its observed `0` sits at the bottom.

The structural statement is the important one: the exact law is a function of
the two margins alone, so a test built this way compares the observed network
against a baseline that the margins have already fixed. It can detect departure
from the marginal model. It cannot, by construction, see anything else.

**A guessed closed form, recorded because it is wrong.** I conjectured that the
null mean would be `m·(Σₓ pₓ qₓ)²`, the squared overlap of the two degree laws.
The exact enumeration gives ratios of `21/5`, `5` and `56/27` between the exact
mean and that expression on the declared families. The guess is refuted; no
closed form for the exact null mean is established here and the enumeration is
not replaced.

## 6. One cause

The three sections are one statement seen three times.

| Declared before the data | What it already fixes |
|---|---|
| which declared generators are taken on the tetrahedron | whether the symmetry set has order four (the three axis swaps) or is infinite (the four face mirrors) |
| the two margins of a table | every row's argmax, and the whole assignment optimum |
| the two degree multisets of a network | the entire exact null law, including its mean |

In each case the invariance is a partition or a quotient, and everything
invariant under it is fixed before any observation is made. What remains — the
residual — is the only part that can carry a labelling or an alignment. For the
table, the residual is `M − rcᵀ/Σ M`, and the identity computed here is that the
two statistics usually read from such a table are functions of the part that is
*not* residual.

That is the programme's own second distinction in a sharper form. "An arithmetic
check needs an interpretation" becomes: **an arithmetic check needs to be told
which of its inputs are still free.** The other repository's retraction is the
same lesson learned from data: a spread read as phase asymmetry was item
frequency, and frequency is a margin.

## 7. What the checker ran

```console
python3 experiments/declared_invariance/checker.py --output experiments/declared_invariance/evidence.json
```

[`checker.py`](../../experiments/declared_invariance/checker.py) uses the
standard library only — integers, permutations and `Fraction`; no floating-point
value enters any acceptance test — and its output is compared against the
retained [`evidence.json`](../../experiments/declared_invariance/evidence.json)
with timings removed. The retained run records **1,818 assertions** over three
sections. `RLIMIT_CPU`, `RLIMIT_FSIZE` and the wall alarm are installed; no
address-space ceiling is installed because the checker launches no child
process, and the contract's memory figure is a declared budget observed as peak
RSS rather than an enforced limit. The checker refuses to overwrite an existing
output path.

Controls that keep the checks from being vacuous:

* the Klein group is asserted to be a subgroup of the finite part **and** not to
  generate the closure, so "the two families are different groups" is a
  comparison and not a restatement;
* the unsorted-weight case is asserted to make the identity **not** an
  assignment optimum, so section 4 is not an accident of sorted weights;
* the `t = 0` grid point is asserted to fail the row reading, so the collapse
  claim is not vacuous at rank one;
* the two same-margin networks are asserted to differ in the observed statistic,
  so section 5 is not comparing a network with itself;
* the refuted closed form is asserted **not** to equal the exact mean, so a
  future change cannot silently make the guess look right.

## 8. Residual and non-claims

* **No text and no corpus count is imported.** Neither the co-occurrence
  matrices nor the edge lists of the external repository are reproduced,
  recomputed or approximated here. The synthetic matrices and networks in the
  contract are declared objects, and the external numbers cited in section 1 are
  their published results, attributed and not re-run.
* **Nothing here decides anything about a text.** The rank-one result does not
  show that any real co-occurrence table is rank one. It shows that the two
  statistics usually read from such a table cannot separate a planted labelling
  from monotone margins, and that the repair proposed for exactly this problem
  does not repair it. Whether an alignment statistic exists is open; the
  external repository's own diagnosis — that the sample must be passages
  enumerating in parallel — is the direction, and no matrix identity settles it.
* **No statistical claim is made about any external measurement.** Their
  percentile-100 result is reported as theirs. The exact null computed here is
  for networks of four to six edges, where every permutation can be enumerated;
  for a network of thousands of edges the same law is not enumerated and no
  approximation is claimed.
* **The tetrahedron is a declared combinatorial object.** The three axis swaps
  and the four face mirrors are not claimed to be the symmetry of any text, and
  the scheme they were read from is not imported. `Ã₃` here is a group of affine
  isometries on a lattice and has no implementation, no observer role and no
  connection to the native vocabulary. The exact counts `2n² + 2` and
  `1 + 2n + n(n+1)(2n+1)/3` are verified through length twenty and are not
  claimed as a general theorem about all affine Weyl groups.
* **No native consequence.** No `SourceId`, no observer, no aperture, no clock,
  no operation, no `Seal`, no claim promotion, and no connection to the six
  native primitive words.

The next useful step is not more matrices. It is the one the external repository
already identified: define the aligned sample — passages that enumerate phases
and items in parallel — and measure the residual on that, where the margins are
no longer free to decide the answer.
