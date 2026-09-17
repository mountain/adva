# Feasibility, lower bounds and quadratic optimality gaps

Status: bounded external research, 2026-09-17. This advances priority 5 of the
[applied-mathematics roadmap](../../docs/research/applied-mathematics-contract-roadmap.md)
after PR #195 merged with all eight checks passing, at baseline
`f6106ccb85d9712e9fb424319780a9c850442e8b`. It is an exact rational receiving
contract for supplied candidates and certificates, not a new optimizer or native
Adva operation.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
not his authorship, review, endorsement or correctness guarantee. Original
first-party code, exposition and synthetic evidence under Unknown v0.3. A second
ChatGPT agent reviewed the mathematics, protocol and implementations statically;
that is not institutional review or a proof-kernel check.

## One problem, three distinct obligations

For one or two ordered coordinates, fix

    f(x) = (x^T H x)/2 + c^T x + d,     l <= x <= u.

All coefficients and box endpoints are rational. The receiver requires H to
be symmetric positive semidefinite. Input size bounds are finite; the declared
domain is every rational point in the box, not a finite list or finite field.
The same lower-bound argument holds on the real box.

The receiver separately checks:

1. **Feasibility and upper bound:** the supplied point x belongs to the original
   box, and U=f(x). U bounds the infimum from above; it does not bound every
   other objective value from above.
2. **A global lower bound:** the supplied affine certificate establishes
   L<=f(y) for every y in the original box.
3. **The optimality gap:** L<=inf f<=U, so U-inf f<=U-L.

A small search region, a zero unconstrained gradient, matching means or repeated
solver success supplies none of these obligations automatically. This profile
contains no simplex search, sampling optimizer or automatic restart.

## The lower certificate and its elementary proof

Choose a rational anchor z; it need not be feasible. Compute

    g = H z + c.

For each coordinate choose b_i=l_i when g_i>=0, otherwise b_i=u_i. In particular,
zero gradient chooses the lower endpoint as a canonical tie convention. Define

    L = f(z) + g^T (b-z).

The exact expansion is

    f(y) = f(z) + g^T (y-z) + (y-z)^T H (y-z)/2.

Positive semidefiniteness makes the final term nonnegative. On a box, b minimizes
the affine term coordinate by coordinate, proving L<=f(y) throughout the box.
This is an elementary sufficiency argument, not a claim that finite sample
checks establish universal validity.

In one dimension PSD means H_00>=0. In two dimensions the receiver checks both
diagonal entries and the determinant are nonnegative. These conditions are
sufficient: when H_00>0 complete the square, leaving coefficient det(H)/H_00;
when H_00=0, det(H)>=0 forces the off-diagonal entry to vanish. Checking only
the determinant would admit diag(-1,-1), and checking only the diagonal entries
would admit [[0,1],[1,0]]. Both are refused. Nonsymmetric inputs are refused by
the profile rather than silently symmetrized.

The producer expands coefficients into a small polynomial, differentiates
monomials, and compares the two affine endpoint values explicitly. The receiver
uses bilinear matrix arithmetic, principal minors and gradient signs. Neither
imports the other or earlier experiments. Python and Fraction remain shared
trusted dependencies, so this is implementation separation, not disjoint trusted
computing bases.

## Exactness, approximation and missing evidence

| Received evidence | Outcome | Meaning |
| --- | --- | --- |
| Feasible x and complete bounds, U-L=0 | ExactOptimal | x is a global minimizer; uniqueness is not established |
| 0<U-L<=tolerance | EpsilonOptimal | Objective suboptimality is at most the declared absolute tolerance |
| U-L>tolerance | VerifiedGap | Bounds remain valid; this certificate has not met the requested tolerance |
| Feasible x and U, lower certificate absent | UnknownLowerBound | Retain feasibility/U, with no accepted optimality result |
| Incorrect certificate or substituted request | InvalidEvidence | Refuse the claimed conclusion; retain only independently verified components |
| Unsupported or malformed problem | InvalidContext | No judgment of mathematical infeasibility |

EpsilonOptimal describes objective value, not distance to an optimizer, relative
error, physical energy or equality. Positive certificate gap does not prove that
the candidate is nonoptimal. A zero gap does not prove uniqueness.

If the point or upper value fails, nothing is retained as a verified feasible
result. Once both pass, they survive missing or invalid lower evidence. Once
the full lower certificate passes, it also survives an invalid final gap or
classification. These diagnostic fields do not grant native authority or a
continuation budget. An absent bound and a false bound remain different outcomes.

## Worked exact examples

For H=[[2,1],[1,2]], c=(-1,-1), d=0 and box [0,1]^2, the point
x=z=(1/3,1/3) gives g=0 and L=U=-1/3. The same lower certificate with candidate
x=(0,0) gives U=0 and gap 1/3.

Conversely, keep the actually optimal candidate (1/3,1/3) but use anchor z=0.
Then g=(-1,-1), L=-2 and the certificate gap is 5/3. This is a verified but weak
bound, not proof that the candidate needs to move. Improving the bound can be
the relevant next action.

With the same H, c=(1,-2) and x=z=(0,1), the optimum is -1 but g=(2,0).
The constraint blocks the direction of decreasing x_1. Requiring the entire
gradient to vanish would incorrectly reject this boundary optimum.

For f(x,y)=(x+y-1)^2 on [0,1]^2, candidates (1,0) and (0,1) both have zero
gap using z=(1/2,1/2). This directly prevents interpreting ExactOptimal as
a unique answer. A constant objective supplies another tie control.

The fresh one-dimensional negative-coordinate instance f(x)=(x+1/2)^2 on
[-1,0], with z=-1/2 and candidate x=-3/4, gives L=0, U=1/16. For f(x)=x^2,
candidate 1/64 gives strictly positive gap 1/4096 even when tolerance 1/64
is met. Neither approximation nor normalization erases that difference.

An outside-box anchor is admitted because the quadratic identity is global.
A singleton box is also admitted; a poor anchor may still give a positive
gap although its only feasible point must be optimal.

Adding one to the objective shifts both L and U by one and leaves their gap
unchanged. The campaign constructs this shifted certificate completely, then
submits it to the receiver expecting the original objective. It must be
refused even though its own arithmetic is correct. Equal gaps do not bind a
question. Similarly, another endpoint at zero gradient may give the same valid
affine minimum but is refused by this canonical-certificate profile; this is
a policy mismatch, not a false mathematical lower bound.

## Contract, resources and replay

The [frozen contract](contract.json) fixes the exact wire fields, arithmetic
scope, positive/negative cases, budgets and exit conditions before execution.
The request binds question, ordered axes, H,c,d, original box, tolerance,
history and the fixed minimization scope. A candidate binds that exact request,
a feasible point and upper value, an optional lower certificate and final claim.
The lower certificate carries anchor, gradient, canonical corner and value.

All input/point/anchor rational components have absolute numerator and positive
denominator at most 64 and must be canonical. Certificate components and
receiver arithmetic intermediates are limited to 512 bits. Booleans and JSON
floating-point numbers are not accepted as rational integers. No native IDs,
source identities, hidden solver or code execution are imported from the request.

The campaign has 48 receiving calls at most, a 30-second total wall limit and
100,000 aggregate counted work units. Each receiving process has a 3-second
wall/CPU limit, 128 MiB address-space limit, 32 KiB per input, 256 KiB file-output
limit and 10,000 counted work units. Producer and direct-point controls each have
10,000 work units. The evidence allowance is 2 MiB, checked before final summary.
The fixed grammar and fixtures bound supervisor work. These are bounded trusted
research tools, not hostile-service security guarantees.

From the repository root, using a fresh output directory:

```sh
python3 -B -S experiments/quadratic_gap/run.py --output /tmp/adva-quadratic-fresh
```

To replay one retained example, extract the archive to a fresh directory and
invoke the receiver with its two input paths:

```sh
mkdir /tmp/adva-quadratic-evidence
tar -xzf experiments/quadratic_gap/evidence/attempt-1.tar.gz -C /tmp/adva-quadratic-evidence
python3 -B -S experiments/quadratic_gap/receive.py \
  --expected /tmp/adva-quadratic-evidence/attempt-1/valid/weak-bound/expected.json \
  --candidate /tmp/adva-quadratic-evidence/attempt-1/valid/weak-bound/candidate.json
```

## Executed evidence and costs

The first campaign completed **603 assertions in 48 fresh receiving processes**:
six ExactOptimal, two EpsilonOptimal, five VerifiedGap, two UnknownLowerBound,
20 InvalidEvidence and 13 InvalidContext. All selected retention and refusal
controls passed. There was no failed campaign or corrective replay.

Direct rational evaluation retained **91 sample points** as controls, including
the two distinct rank-one minimizers. These are not the full-box proof, which
comes from the stated algebraic identity and checked PSD conditions. The changed
constant countercontrol has independently recomputed shifted upper/lower values
and exactly the same gap, but is refused against the original request.

The campaign used 1,958 receiver work units, 778 producer units and 532
point-evaluation units; search candidates were zero. Measured campaign wall time
was **7.977450931 s**. Instrumented construction took 0.010531769 s, receiving
7.637142588 s, serialization 0.103064490 s and point observations 0.012520770 s.
The fresh negative-coordinate reuse receiver took 0.181270588 s and 44 work
units within those totals. Remaining setup/bookkeeping is included only in total
wall time. Highest child RSS was **10,368 KiB (10.125 MiB)**, supervisor RSS
**12,928 KiB (12.625 MiB)**; these are separate process high-water marks, not
an aggregate system peak. Archive construction additionally took 0.074152189 s.
Research, static review, final documentation/manifest writing, network and CI
costs were not separately measured. No speedup is claimed.

[execution.json](evidence/execution.json) records all outcomes, measured costs
and three source hashes. [manifest.json](evidence/manifest.json) inventories
**257 exact files** in [attempt-1.tar.gz](evidence/attempt-1.tar.gz), including
requests, candidates, commands, raw outputs, point observations and frozen
contract. Archive size is 15,727 bytes, SHA-256
`2495ee1cea519afd8373ec3718ac5264d795a04b6317894120d1b529b2f0ded3`.
All nested files are reviewed original code-related data or synthetic evidence;
file size is not a memory measurement. Raw stderr is preserved, including the
empty files. Absolute paths in archived commands require substitution after
extraction. A focused CI job imposes a 35-second outer timeout and retains
outputs on failure.

## Continuation and limits

This gives people and agents an explicit distinction between improving a
candidate, improving its certificate and accepting a stated tolerance. It
supports the original direction of bounded reliable progress, while identifying
the missing global bound in an unconditional simplex stopping rule. It does
not establish solver acceleration, learned vocabulary or practical benefit to
Mingli or Jiamin without an actual workload and its costs.

Existing interval, linear-system and decision receipts remain unchanged
methodological references, not imported runtime or derivation parents. There
is no new library entry, native operation, Close/free, M6 filler, universal
grammar, physical energy interpretation or proof-kernel artifact. The separate
ledger-holder-exit obligation remains open.

The next roadmap step is priority 6: one bounded discrete dynamical system with
an exact contraction or conservation certificate and a finite time horizon.
Identity and periodic dynamics must remain countercontrols against an assumed
convergence claim. General optimization, stronger lower certificates and
dependency-aware interval interpretation remain separate open tasks.
