# Finite Markov dynamics, contraction and retained perturbation bounds

Status: bounded external research, 2026-09-17. After PR #196 merged with all
eight checks passing, this advances priority 6 of the
[applied-mathematics roadmap](../../docs/research/applied-mathematics-contract-roadmap.md).
Baseline: `e4868eff9f46437a5e637ab7d4b713f351d2226b`.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
not his authorship, review, endorsement or correctness guarantee. Original
first-party code, exposition and synthetic evidence under Unknown v0.3. A second
ChatGPT agent statically reviewed the mathematics and implementations. This is
not institutional review or a proof-kernel artifact.

## What is being certified

The caller supplies an ordered two-state space, one time-homogeneous transition
kernel K, initial probability law p_0, stationary reference pi, finite horizon,
initial and per-step error allowances, final tolerance and ordered history.

    K = [[a, 1-a], [b, 1-b]],       p_{t+1} = p_t K.

Every entry is nonnegative and each row sums to one. The fixed row-vector
direction matters. Multiplying a probability row by K preserves both mass one
and nonnegativity. These laws are stipulated inputs; this experiment does not
learn a physical transition law or infer a joint process from observations.

The earlier [kernel composition experiment](../kernel_composition/README.md)
connects three distinct spaces through separate probability receipts. Repeated
dynamics on one space requires a different boundary. This new receiver imports
neither that implementation nor its parent probability receiver. Their code,
limits, claims and histories remain unchanged methodological references.

## Contraction lives on the probability simplex

For p=(x,1-x), the first coordinate after one step is

    T(x) = b + (a-b)x.

For any two probability laws p,r,

    TV(p,r) = (|p_0-r_0| + |p_1-r_1|)/2,
    TV(pK,rK) = |a-b| TV(p,r).

Thus q=|a-b| is an exact global factor on this two-state probability simplex.
The elementary scalar identity supplies the all-laws argument, not the finite
control points in the campaign. The factor is not silently taken to be a matrix
norm on arbitrary vectors. In particular, conservation and strict contraction
are compatible because differences of probability laws have total mass zero.

The receiver checks the supplied pi is a probability law with pi*K=pi.
For the fixed map, exact trajectories satisfy TV(p_t,pi)=q^t TV(p_0,pi).
If q<1 this supplies strict contraction; if q=1 it supplies only nonexpansion.
The latter does not establish either convergence or nonuniqueness. The swap
kernel has the unique stationary law (1/2,1/2), while nonstationary starts
alternate forever under that exact map. Identity instead fixes every law.
Finding one stationary law and verifying convergence are distinct tasks.

This report only executes the declared finite horizons. Its fixed-map identity
does not promise that an actual system keeps the same kernel, error allowances
or physical interpretation for unobserved future time.

## Two errors and two bounds

Let h_t be a supplied approximate probability trajectory. Check

    TV(h_0,p_0) <= initial_error,
    TV(h_{t+1},h_t K) <= epsilon_t.

Define B_0=initial_error and B_{t+1}=q B_t+epsilon_t. The triangle inequality
and the exact contraction identity prove, step by step,

    TV(h_t,p_t) <= B_t.

This is error relative to the exact trajectory, not distance to stationarity.
For the latter, use

    S_t = q^t TV(p_0,pi) + B_t,
    TV(h_t,pi) <= S_t.

The factor starts at 1 at t=0 even when q=0. No bound is silently clamped to 1.
A bound greater than 1 remains a valid, loose bound in this canonical profile.
Each row records its actual residual, actual two distances, B_t and S_t. An
upper error allowance is not identified with an observed residual. Every
approximate row must still be a normalized nonnegative law.

Finite per-step allowances are not an infinite-time noise model. Even for a
contractive fixed map, persistent permitted perturbations need not disappear.
No physical energy, density normalization theorem, native identity or `free`
is inferred from a small or vanishing distance.

## Worked examples and refusals

For a=3/4, b=1/4, p_0=(1,0) and pi=(1/2,1/2), q=1/2. The exact first
coordinates through t=4 are 1, 3/4, 5/8, 9/16, 17/32. Their final distance
to pi is 1/32. With zero errors and tolerance 1/32 the full horizon is certified.

Injecting +1/16 into the first coordinate after every transition, and -1/16
into the second, gives 1, 13/16, 23/32, 43/64, 83/128. Each local residual is
exactly 1/16; errors attain B_t=0, 1/16, 3/32, 7/64, 15/128. The final
stationarity bound is S_4=19/128. This supplies a sharp finite accumulation
witness instead of merely testing a loose inequality.

The asymmetric reuse has a=1/2, b=1/4, pi=(1/3,2/3) and q=1/4. Other
fixtures cover negative a-b (alternating deviations with shrinking distance),
equal rows q=0, horizon zero, identity, swap, initial perturbation, conservative
unused error allowance, and an unclamped bound of 5.

Starting from p_0=pi=(1,0), these two complete kernels have the same exact and
approximate stationary trajectory but different global factors:

| Kernel | q | Observation from this start |
| --- | --- | --- |
| [[1,0],[0,1]] | 1 | Every stored law is (1,0) |
| [[1,0],[1/2,1/2]] | 1/2 | Every stored law is (1,0) |

The unused row is given, not identified by that trajectory. The campaign
recomputes the second certificate completely, then submits it against the
first requested kernel. The receiver must refuse the changed question.

Another control uses a conservative error allowance although the approximate
trace equals the exact trace. Its actual final distance meets tolerance but
the selected certified bound does not. Under this profile, claiming tolerance
from that bound is refused. This does not deny the independently checked actual
distance; a different receiving rule could explicitly authorize that use.

## Receiving and coverage order

The [frozen contract](contract.json) specifies every input/output field. Before
checking a candidate, the receiver validates the entire expected kernel, initial
law, stationary law, horizon and error list, including future allowances beyond
a supplied partial trace. It then checks exact context binding and q, followed
by consecutive trace rows. Only fully verified rows enter `verified_prefix`.

| Outcome | Permitted interpretation |
| --- | --- |
| CertifiedTolerance | Complete declared horizon and S_horizon<=tolerance |
| VerifiedHorizon | Complete horizon and valid bounds; this bound exceeds tolerance |
| UnknownCoverage | Valid proper prefix; retain explicit missing time indices |
| InvalidEvidence | Wrong trace, bound, claim or question binding; retain only completed verified rows |
| InvalidContext | Unsupported/malformed input, not a theorem of impossible dynamics |

`regime` separately records StrictContraction or Nonexpansive. A stationary
identity/swap trace may meet tolerance while remaining Nonexpansive. A prefix
of an equal-row trajectory already reaches the stationary law, yet cannot be
reported as the complete requested horizon. Coverage takes precedence over a
currently satisfied tolerance. This is a trace-coverage contract, not a denial
that the algebraic map predicts later exact values.

Bounded receiver exhaustion is UnknownBudget; unexpected implementation failure
is ImplementationFailure. Neither is a mathematical counterexample. All native,
close and free authorization flags remain false, including successful outcomes.

## Independence, resources and replay

The producer uses two-component row-matrix products, half-L1 distances and
maximum pairwise row distance. The receiver independently uses the scalar affine
map and scalar absolute differences after checking probability normalization.
Neither imports the other. Shared Python/Fraction and operating-system limits
remain trusted dependencies. A second static review does not make either side
infallible or replace a formal proof kernel.

Input fractions have absolute numerator and denominator at most 64; trace
fractions and receiver arithmetic intermediates admit at most 512 bits. That
larger bound is needed, for example, for 83/128. Histories have at most four
entries, but trace time is separately indexed through a horizon from zero to
six. Finite wire limits do not turn the probability simplex into a finite field
or finite sample space of candidate laws.

The supervisor permits at most 50 fresh receiving calls and 30 wall seconds.
Each child has 3 wall/CPU seconds, 128 MiB address space, 32 KiB per input,
256 KiB file output and 10,000 counted work units. Producer and control work
each have 10,000 units; total counted work is at most 100,000. The 2 MiB evidence
allowance is checked before the final summary. Fixed fixtures bound supervisor
construction. These are trusted bounded tools, not a hostile-service sandbox.
There is no automatic horizon/error-budget increase, restart or fuel renewal.

Run from repository root with a fresh output path:

```sh
python3 -B -S experiments/markov_horizon/run.py --output /tmp/adva-dynamics-fresh
```

To independently replay the noisy trace:

```sh
mkdir /tmp/adva-dynamics-evidence
tar -xzf experiments/markov_horizon/evidence/attempt-1.tar.gz -C /tmp/adva-dynamics-evidence
python3 -B -S experiments/markov_horizon/receive.py \
  --expected /tmp/adva-dynamics-evidence/attempt-1/valid/accumulated-noise/expected.json \
  --candidate /tmp/adva-dynamics-evidence/attempt-1/valid/accumulated-noise/candidate.json
```

## Executed evidence and costs

The first campaign passed **906 assertions in 50 fresh receiving processes**:
seven CertifiedTolerance, eight VerifiedHorizon, two UnknownCoverage,
19 InvalidEvidence and 14 InvalidContext. There was no failed campaign or
corrective replay. The 15 complete fixtures contain **63 verified trace rows**;
the two partial records retain four more rows with their future indices missing.

The supervisor retains 135 finite pair controls for mass and the distance
identity, plus the stated analytic mixing/noise sequences. Those finite pairs
are not an all-laws proof. Both the sharp accumulated error and the unchanged
trajectory/different-factor witness were checked. The asymmetric reuse passed
in a fresh process.

Measured campaign wall time was **9.536699227 seconds**. Counted work was
3,820 receiver units, 1,385 producer units and 1,620 control units; search
candidates were zero. Construction took 0.018051642 s, receiving 9.110917746 s,
serialization 0.143851428 s and finite controls 0.026140203 s. The fresh
asymmetric reuse receiver used 0.181677739 s and 148 work units within these
totals. Some setup/bookkeeping is included only in total wall time.

Highest child RSS was **10,496 KiB (10.25 MiB)** and supervisor RSS was
**13,184 KiB (12.875 MiB)**, separate Linux process high-water marks rather than
an aggregate system peak. Archive construction additionally took 0.112338770 s.
Reading, research, static review, final documentation/manifest writing, network
and CI costs were not separately measured. No acceleration is claimed.

[execution.json](evidence/execution.json) records every result and source hash.
[manifest.json](evidence/manifest.json) inventories **267 exact files** in
[attempt-1.tar.gz](evidence/attempt-1.tar.gz): original inputs, candidate traces,
commands, outputs, finite pair controls and contract. Archive size is 21,158
bytes, SHA-256
`d6fe75c63c8f813c667e7e8811d167907ccfcd43e197c54d01cf5c1d2f9887d8`.
All nested files are original code-related data or synthetic evidence. Archive
size is not peak memory. Empty stderr files are retained; archived command
paths require substitution when replayed elsewhere. Dedicated CI imposes an
outer 35-second timeout and preserves outputs on failure.

The 512-bit guards cover serialized rationals and explicit arithmetic helper
steps. Fraction's internal comparison temporaries are trusted and not separately
bit-metered; the process address-space bound applies independently. This is an
implementation qualification to the contract's resource wording, not a checked
hostile-input or universal arithmetic-cost certificate.

## Result in the larger roadmap

This helps people and agents distinguish mass conservation, convergence of exact
maps, finite approximation errors, coverage and the evidence needed to stop.
It supports bounded reliable progress while showing why one apparently stable
trajectory cannot identify a global contraction property. Practical benefit to
Mingli or Jiamin, measured acceleration, learned vocabulary, native admission,
M6 closure and universal grammar are not established. No library entry or native
runtime is changed. The separate ledger-holder-exit obligation remains open.

The next roadmap step is priority 7: a fixed finite hypothesis family and
sampling law, with complete enumeration of possible samples to check one
confidence rule's coverage. The transition law here was supplied; statistical
identification of it from observations is a different obligation. Sampling
variability, approximation error and an unknown mechanism must remain distinct.
