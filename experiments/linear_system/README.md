# Complete solution receipts for a small rational linear system

Status: bounded external experiment, 2026-09-17. PR #193 was merged after all
eight CI checks passed; baseline is `964759167c47ff472efad491e320a29dc4fb966a`.
This advances priority 3 of the [applied-mathematics roadmap](../../docs/research/applied-mathematics-contract-roadmap.md).

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
not his review, endorsement or correctness guarantee. Original code, prose and
synthetic evidence under Unknown v0.3. Another ChatGPT agent statically reviewed
the mathematics and both scripts; this does not imply institutional review.

## The distinction being checked

For a fixed typed equation Ax=b, a vector with zero residual establishes one
solution. It does not establish uniqueness or describe every solution. This
receiver checks three different finite witnesses:

| Outcome | Checked certificate | Mathematical conclusion |
| --- | --- | --- |
| UniqueSolution | Ax=b and BA=AB=I | Exactly one rational solution, x |
| InconsistentSystem | yᵀA=0 and yᵀb=1 | No rational solution |
| AffineSolutionFamily | Ax₀=b and a complete independent basis of ker A | All solutions x₀+Σtᵢvᵢ, tᵢ∈Q |
| UnknownCoverage | Ax₀=b with too few valid independent kernel directions | One verified solution, incomplete description of all solutions |

The mathematical scalar field is **Q**, not the finite set of allowed wire
fractions. Input and certificate bounds limit this implementation's admissions;
they do not make those fractions a closed finite arithmetic domain. A finite
certificate can justify a parameterized rational family by an explicit algebraic
argument, without enumerating all parameter values.

## Why the certificates suffice

If Ax=b and B is an inverse, any other solution z satisfies
B(Az−Ax)=z−x=0. This proves uniqueness. Both inverse products are checked.
B is a map from codomain to domain, not an untyped numeric array.

If yᵀA=0 while yᵀb=1, a putative solution would give
0=yᵀAx=yᵀb=1, a contradiction. This profile normalizes a nonzero contradiction
to one: a witness with yᵀb=c≠0 can be divided by c over Q, when the resulting
encoding fits the certificate bound. The value one here is neither a probability
density energy nor a scalar success score. y is a **codomain dual covector**;
a vector from the right nullspace is generally not this witness.

For a consistent system, subtracting one solution x₀ identifies all solutions
with x₀+ker A. The receiver computes rank for this two-by-two profile: nonzero
determinant means rank two; otherwise a nonzero entry means rank one; otherwise
rank zero. A nonzero independent set in the kernel must have exactly 2−rank(A)
vectors to span it. For rank one, a nonzero row (a,b) has kernel spanned by
(−b,a); the other row adds no independent constraint. For rank zero, two
independent vectors span Q². These elementary observations justify the finite
coverage check; they are not a proof-kernel artifact.

The family branch accepts different valid parameterizations. It refuses zero
or dependent directions rather than treating their count as dimension. With
too few valid independent directions it retains the actual checked particular
solution, residual and missing count, but no accepted complete solution claim.
Rank-two families use the unique-solution branch in this result taxonomy.

## Exact examples and reuse

A nonsymmetric unique example is

    A = [[2,1],[3,2]], b = (4,7)
    x = (1,2), B = [[2,-1],[-3,2]].

For the singular matrix A=[[1,2],[3,6]], b=(3,9) gives the complete family

    x = (3,0) + t(-2,1), t in Q.

The independently supplied parameterization (1,1)+s(2,−1) is also accepted.
Changing only the rhs to (3,10) instead yields the no-solution witness y=(−3,1).
The zero matrix is tested with zero rhs (two independent kernel directions)
and nonzero rhs (inconsistency). A further nonsingular rational input
A=[[1/2,1/3],[2/3,−1/2]], b=(0,17/6) yields x=(2,−3) and inverse
[[18/17,12/17],[24/17,−18/17]].

All three primary classes are reused under two actual basis changes:

    P = [[1,1],[0,1]], Q = [[0,1],[1,0]]
    A_new = Q^-1 A P, b_new = Q^-1 b
    x_new = P^-1 x, B_new = P^-1 B Q, y_new = Q^T y.

P changes the domain basis and Q the codomain basis. This is a two-space
coordinate change, not generally a conjugation. The unique example becomes
A_new=[[3,5],[2,3]], b_new=(7,4), x_new=(−1,2). The inconsistent example's
covector becomes (1,−3); incorrectly using P^-1 y is a refusal control.
The supervisor checks these correspondences from the actual produced receipts,
and checks family equations after mapping back to the original coordinates.
The receiving contracts independently validate each chart and bind its full
bases; they do not themselves accept an arbitrary cross-chart transport receipt.
Chinese space IDs exercise the declared serialization boundary.

## Receiving interface and protected dependencies

The [contract](contract.json) was frozen before execution. Expected request keys
are `question`, `domain`, `codomain`, `operator`, `rhs`, `interpretation`,
and `history`. Both spaces declare dimension two and ordered basis columns in
a fixed ambient coordinate convention. Bases must be independent; **A may be
singular**. Operator rows act on a column of domain coordinates and produce
codomain coordinates. The rhs explicitly belongs to the codomain. Interpretation
is `all-solutions-over-Q`. History and all representations are receiver-bound.

The candidate has `profile`, an exact copy of that selected `request`, and
one typed `claim`. Profile is `adva.research.linear-system.v0`.
Rationals are canonical numerator/positive-denominator integer pairs. Input
components are bounded by 64, certificate components by 4096, intermediate
receiver components by 512 bits. Booleans, floats, duplicate JSON keys,
nonfinite constants, noncanonical rationals and zero denominators are rejected.
A JSON parse failure has no decoded request; its original bytes remain in the
recorded input. Other refusals retain the decoded expected request.

[`golden_ratio_operator_lift/receipt.py`](../golden_ratio_operator_lift/receipt.py)
provides a useful precedent for exact bases and complete direction coverage,
but its fixed-word, invertible-operator and rational-string profile cannot
serve as this solver. It and its adapter pins are unchanged. This receiver is
new original code; it imports neither that checker nor the probability checker.
It does not create native semantic identities, source or history objects.

The producer uses bounded Gaussian row elimination, retaining the full left
row transformation. The independent receiving process uses certificate equations
and the two-by-two determinant/rank rule; it imports no producer code. Both
share Python and Fraction. The supervisor also evaluates finitely many rational
points in each family. Those samples are checks of examples, not evidence for
the all-parameters quantifier by themselves.

## Measured campaign

The first campaign passed **468 assertions in 44 fresh receiving processes**:

| Outcome | Count |
| --- | ---: |
| UniqueSolution | 3 |
| InconsistentSystem | 3 |
| AffineSolutionFamily | 4 |
| UnknownCoverage | 2 |
| InvalidEvidence | 20 |
| InvalidContext | 12 |

Controls include a singular matrix advertised as uniquely solved, a missing
or forged inverse, wrong particular solution, wrong covector direction, zero/
non-kernel/duplicate/dependent kernel vectors, missing directions, transposed
operator, substituted rhs/bases/question/history, wrong profile and invalid
numeric or shape inputs. Unsupported contexts are profile refusals, not
mathematical no-solution results. Only a checked contradiction yields
`InconsistentSystem`. No new native vocabulary is installed.

Wall time: **7.591924611 s**. Counted receiver work: **1,319 units**; producer
elimination work: **192 units**; search candidates: zero. These are explicit
implementation counters, not processor instructions. Instrumented construction
took 0.004919988 s, receiving 7.297160089 s, serialization 0.094519778 s and
independent observation 0.012034077 s. The three fresh chart-reuse receivers
took 0.448080019 s within that receiving total. Some setup, copying and bookkeeping
appear only in the campaign wall total. Highest child RSS was 10,624 KiB
(10.375 MiB); supervisor RSS 13,056 KiB (12.75 MiB), not a summed machine peak.
Archive construction additionally took 0.062988057 s. Research, static review,
final report/manifest writing, network and CI costs were not separately measured.
No speedup or expression-power increase is claimed.

Before execution, static review found and corrected an omitted deadline callback
and a supervisor assumption that a rejected floating JSON input would already
have a decoded request. There was **no failed experiment and no corrective replay**.
This is finite evidence, not a proof of implementation correctness for every input.

## Replay and retained evidence

Run from the repository root with a fresh output path:

```sh
python3 -B -S experiments/linear_system/run.py --output /tmp/adva-linear-fresh
```

Linux and the Python standard library suffice. The campaign caps execution at
44 processes or 30 wall seconds. Each child has 3 wall/CPU seconds, 128 MiB
address space, 32 KiB per input and 10,000 counted work units. Aggregate counted
producer/receiver work is capped at 100,000; producer alone at 10,000. There is
no automatic retry, scope enlargement or renewal of fuel. CI adds an outer
35-second timeout and retains failure outputs.

[execution.json](evidence/execution.json) records every result, timing and source
hash. [manifest.json](evidence/manifest.json) inventories **232 exact files** in
[attempt-1.tar.gz](evidence/attempt-1.tar.gz): inputs, candidate certificates,
command lines, actual stdout/stderr, finite independent observations and contract.
The archive is 16,846 bytes with SHA-256
`b2d9427bb9e658bcef3b89a46aeb275d62e1504b5e6e42acf4fa336a943a8edd`.
Archive size is storage cost, not memory. Stored commands preserve the original
paths; adapt them after extraction. To check one preserved example:

```sh
mkdir /tmp/adva-linear-evidence
tar -xzf experiments/linear_system/evidence/attempt-1.tar.gz -C /tmp/adva-linear-evidence
python3 -B -S experiments/linear_system/receive.py \
  --expected /tmp/adva-linear-evidence/attempt-1/primary/family/expected.json \
  --candidate /tmp/adva-linear-evidence/attempt-1/primary/family/candidate.json
```

## Residual and next step

This gives people and agents a small, inspectable way to request and distinguish
a complete solution, a genuine contradiction and a partial result. It has not
been evaluated on Mingli or Jiamin's actual decisions. General dimensions,
symbolic coefficients, numerical conditioning, arbitrary basis-transport receipts,
formal proof-kernel verification and native admission remain open. Certificate
bounds can exclude otherwise legitimate mathematical witnesses. No `Close`,
`free`, M6 filler, universality, measured learning or human benefit follows.

The next roadmap step is priority 4: bounded rational interval arithmetic with
explicit outward enclosures and refusal of division through a zero-containing
denominator. Preserve the distinction between exact zero, a small residual and
an interval containing zero. The older ledger-holder-exit obligation remains a
separate open engineering task.
