# Mean constraint match

`mean-constraint-match` names a **Proposed research condition**: the mean
cardinality of a finite weighted subset distribution matches a chosen target.
It is implemented by an Adva research data-machine v0 program, not a new native
primitive. Host assembly only resolves instruction labels.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
account use is not his authorship, review or correctness guarantee. All added
code, prose, fixtures and evidence are project-original under Unknown v0.3.
No article text, figures, textbook content or external code is incorporated.

## Exact question

For all subsets S of {1,...,n}, assign positive weight t^|S|, where t=a/b.
The sum is Z(t)=(1+t)^n. Write J=|S| under the resulting probability distribution.
Then

    mean(J/k) = n*a / [k*(a+b)]
    variance(J/k) = n*a*b / [k^2*(a+b)^2].

The program checks the domain first, then compares `n*a == k*(a+b)`.
Unreduced pairs such as 1/2 and 2/4 are permitted. Fractions are returned as
positive-denominator integer pairs; they need not be reduced.

Inputs satisfy **1 <= k <= n <= 6** and **1 <= a <= b <= 8**. These are this
program's capacity bounds, not restrictions on the general elementary identity.
Values outside these limits are rejected. All intermediate integers are at
most 16^6 = 16,777,216, well within checked signed i64. No floating point,
division, logarithm, exponential approximation or square root is used.

Mean matching makes the derivative of log(Z(t)/t^k) with respect to log(t)
vanish: that derivative is k*(mean(J/k)-1). This is an interior optimum for
k<n/2 and an endpoint match for k=n/2. For k>n/2 the constrained optimum on
0<t<=1 is t=1 but there is no mean match. Mean matching is not a test for
every possible constrained optimum.

## Variance and the proposed std question

If `std` denotes standard deviation, `std-constraint-match` would need an
independently specified target sigma_0. We do not introduce that term without
such a target. The program instead reports the exact variance. A future bound
sigma <= q with rational q>=0 can compare variance <= q^2 without square roots.

At mean match, variance(J/k)=(n-k)/(n*k). It need not vanish and is not generally
one. For fixed n and matched k, it is already fixed by this model: a second
target may be redundant or inconsistent. Matching both moments in an arbitrary
distribution would still not establish equality of distributions or coverage.
The term energy, if used, denotes this dimensionless normalized mean only;
no identification with physical energy or native Adva fuel is made.

## Coverage is a separate output

The coverage question is fixed: do subsets of size <=k exhaust **all** subsets?
When k=n they do. When k<n, the full subset is omitted and has positive mass
a^n/(a+b)^n. The program returns this explicit witness mass, which is only a
lower bound on the entire omitted mass. It never labels that lower bound as
the complete tail probability. In particular, obtaining mean 1 cannot turn
the coverage flag on.

For input (3,1,1,2), the output gives mean 3/3, variance 6/9, incomplete coverage
and an omitted full-subset witness of mass 1/27. The full omitted mass is 7/27;
that larger quantity is not what this program computes. For fresh reuse
(5,2,2,3), mean is 10/10, variance 30/100 and the witness mass is 32/3125.

## Files and execution

- `mean-constraint-match.adva`: 103 instructions, 16 typed registers.
- `input.json`: tag-0 data node with integer fields [n,k,a,b]=[3,1,1,2].
- `build.py`: deterministic first-party label assembler; not an Adva compiler.
- `check.py`: bounded fixtures, external simulation and actual CLI checking.
- `contract.json`: fixed mathematical, resource and authority boundary.

Build the inherited native runner and execute into a new output path:

```sh
cargo build --locked -p adva-witness --bin adva
target/debug/adva data-run programs/mean-constraint-match/mean-constraint-match.adva \
  --input programs/mean-constraint-match/input.json \
  --fuel 2048 --quantum 2048 --output /tmp/mean-match-run.adva
target/debug/adva data-run programs/mean-constraint-match/mean-constraint-match.adva \
  --input programs/mean-constraint-match/input.json \
  --fuel 2048 --quantum 0 --check /tmp/mean-match-run.adva \
  --output /tmp/mean-match-check.adva
```

This uses the inherited v0 research runner. No machine dependency lock is
upgraded. This is ordinary program authoring, not knowledge migration or a
native communication exchange. Rust remains the native execution authority.

Output is a tag-0 node with three fields:

1. Tag 1: [mean numerator, mean denominator].
2. Tag 2: [normalized variance numerator, denominator].
3. Tag 3: [tag 4 [mean-match bit, coverage-complete bit], omitted-witness
   numerator, common normalizer (a+b)^n]. The witness numerator is zero only
   when the named coverage is complete.

All scalar fields are integer data. `Returned` alone is not a match: inspect
the explicit bit and scope. A rejection is not a mathematical impossibility
result. A fuel-limited run has no terminal answer and retains its native status.

## Remaining boundary

The first retained [external calibration](evidence/external-summary.json)
passes all 16 fixtures: eight valid calculations, six program/domain refusals
and two wire/type refusals. The oracle enumerates every subset (at most 64),
calculates exact first and second moments, and compares the normalized mean
and variance with the program's output. This is not a second use of the closed
form as its own oracle. Four valid fixtures match the mean target.

The campaign used 30 simulation calls including repeats, 0.250714394 seconds
and peak process RSS 14,080 KiB (13.75 MiB). No native call ran on the authoring
host, which lacks Rust tooling. Reading, assembly, authoring, archival and
publication time are outside that measurement; phases within the campaign
were not separately timed. The archive retains 95 exact files and a per-member
digest manifest. Repetition of the external interpreter is not independent
native replay. The dedicated PR CI is the separately recorded native gate.

Reproduce external calibration into a new directory, or pass a built native
binary to execute and independently receive every valid run record:

```sh
timeout 120s python -B -S programs/mean-constraint-match/check.py --output /tmp/mean-match-external
timeout 120s python -B -S programs/mean-constraint-match/check.py --binary target/debug/adva --output /tmp/mean-match-native
```

The candidate language here is unordered subsets. No correspondence to Adva
program histories, noncommuting words or unrestricted arithmetic syntax is
assumed. A faster formula for this factorized family does not establish faster
search over arbitrary programs. No native free, M6 filler, universal grammar,
physical interpretation or human intent is certified.

The next useful extension requires a concrete dispersion requirement: a
variance budget or a bound on Pr(|J/k-1|>=epsilon). It must retain both the
chosen distribution and the coverage question. New vocabulary is unnecessary
until that question has an intended use and an independently checked result.
