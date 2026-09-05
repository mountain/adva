# Research 0130: Coverage-gated feature closure on a finite prefix boundary

Status: external bounded experiment; proposed working word, not native Adva
semantics. One fixed route was completed on 2026-09-05. No automatic merge.

## 1. Source state and scope

The inspected main commit was
`57c1d04bcfe51b82f6e559a61ca02e668f630b5a`. There were no open PRs.
Research 0126--0129 was already merged; its experiments were not rerun.
The registry had 78 claims and no prefix-coverage calibration claim.
The tree contained the 0090/0092 plans but no corresponding prefix reference
module. Historical-context retrieval was unavailable, so absence of an earlier
conversation-only attempt is not asserted.

The paused `unknown-syntax-building` inquiry is not resumed here. This is an
independent, already proposed subproblem of
[0090](0090-prefix-frontier-closure-calibration-plan.md), under
[0129](0129-bounded-breakthrough-trusted-boundaries.md)'s preflight rules.
It addresses one prerequisite, not all of 0090.

[0123](0123-arithmetic-universality-and-hypothesized-truth.md)'s
`arithmetic-universality` and `hypothesized-arithmetic-truth` remain externally
proposed hypotheses. No source-class universality, shared truth coordinate,
or M6 filler is inferred. Arithmetic here is addition and comparison of exact
dyadic rationals. All denominators are positive powers of two. No division
by an unknown or possibly zero value, multiplicative-unit equivalence, or
commutative replacement of an ordered history is used.

The pre-execution contract is
[0130-prefix-coverage-run-contract.json](0130-prefix-coverage-run-contract.json).
This turn selected one route: exact leaf-subset enumeration as an independent
oracle for an interval-based closure test. It did not introduce a new research
phase or change the agenda's dependency order.

## 2. Formed problem

Can a feature-close rule accept incorrectly when it uses a small numerical
interval but has not checked that its frontier covers all legal completions?

Let the declared universe be all binary leaves of length d. An input has
pairwise disjoint positive, negative, and unresolved prefix antichains
P, N, A. Their roles are assumptions of this finite toy problem, not facts
learned about a running machine. Let M be all leaves not covered by P, N, A.

A legal completion includes every leaf below P, excludes every leaf below N,
and independently chooses whether to include each leaf below A or in M.
Thus the legitimate quantifier is over A **and M**, not merely the recorded A.

Fair-coin cylinder mass is exactly 2^(-length). Write

    L = mass(P)
    U_recorded = L + mass(A).

Only when M is empty may U_recorded be used as the full possible-positive
upper bound. An uncovered state returns CertificateObstruction with the exact
missing leaves and no certified upper bound. This conservative refusal does
not claim that every possible feature is nonconstant on an uncovered state.

For precision k the observer is

    Q_k(x) = floor(2^k x),  0 <= x <= 1.

At x=1 the index is 2^k, not an in-range k-bit string. This explicit endpoint
avoids silently wrapping one to zero. Bounds are inclusive; reaching a dyadic
cell's right endpoint can change the result.

When coverage holds, Q_k is constant on all legal completions iff
Q_k(L)=Q_k(U). Necessity follows because the all-false and all-true unresolved
fillings realize both endpoints; sufficiency follows from monotonicity.
This elementary argument concerns this unconstrained leaf model. Coupled or
restricted fillings need a new argument.

## 3. Counterexample to interval-only closure

Take d=3 and

    P = {00}, N = {1}, A = {010}, M = {011}.

The recorded interval is [1/4, 3/8]. Both endpoint indices under Q_2 equal one,
so the deliberately unsafe interval-only rule says FeatureClosed.

But two legal completions are:

| positive depth-3 leaves | mass | Q_2 |
| --- | --- | ---: |
| 000, 001 | 1/4 | 1 |
| 000, 001, 010, 011 | 1/2 | 2 |

The missing eighth invalidates the apparent certificate. Restoring 011 to A
gives [1/4, 1/2], and the sound rule returns Open. The omission, restoration,
input antichains, and separating fillings remain in the artifact.

This is a counterexample to the explicitly constructed unsafe rule, not an
identified bug in Adva's stable checker or a refutation of Research 0090.

## 4. Complete finite comparison and fresh reuse

Enumerate all 4^4=256 assignments of P/N/A/M to the four depth-2 leaves, and
both k=1,2. For each of the 512 observations, independently enumerate every
legal truth assignment over unresolved and missing leaves.

| finite result | count |
| --- | ---: |
| observer checks | 512 |
| missing-coverage obstructions | 350 |
| unsafe FeatureClosed results contradicted by legal completions | 154 |
| false FeatureClosed results from the coverage gate | 0 |

The remaining 162 observations have complete coverage. Every FeatureClosed
and Open result there agrees with the independently enumerated set of feature
values. The artifact retains every role assignment, observer, result, missing
leaf set, and oracle value set.

The interval-only rule is a negative correctness control, not a competitive
algorithm satisfying the same contract. No speedup or increased expressive
power is claimed.

Two depth-4 uses additionally demonstrate feature closure without object
closure:

| fixture | exact interval | coarse observer | separating observer |
| --- | --- | --- | --- |
| P={00,0100}, N={1,011}, A={0101} | [5/16,3/8] | Q_2=1 | Q_3 takes 2 and 3 |
| fresh P={000}, N={01,1,0011}, A={0010} | [1/8,3/16] | Q_2=0 | Q_4 takes 2 and 3 |

The second input reuses the identical coverage gate without changing its
implementation. Both nonempty residuals and explicit finer-observer witnesses
are preserved. A separate test replaces A={01} with {010,011}; exact mass and
bounds stay unchanged while the input presentation and recorded history differ.

## 5. Proposed word: coverage-gated-close

The name is an assistant proposal for this specific external checking action,
not Mingli's unspoken next language-formation word.

- **Role:** prevent certainty about a feature from depending on omitted legal
  possibilities.
- **Input:** declared finite universe, P/N/A prefix lists, precision k, and
  retained descriptive history.
- **Output:** CertificateObstruction plus missing leaves; or FeatureClosed
  plus value, exact bounds and residual; or Open.
- **Conditions:** valid finite binary syntax, disjoint status antichains,
  declared positive/negative assumptions, independent free leaf choices,
  exact rational arithmetic and the stated observer.
- **Refusal:** invalid syntax, overlap, duplication, unsupported carrier
  bounds or observer precision; incomplete coverage blocks certification.
- **Witness:** complete depth-2 table and four explicit depth-3/4 cases in
  the committed JSON.
- **Expansion/replay:** the Python reference function and independent
  subset-enumeration oracle are retained; whole-contract replay rejects
  altered results or omitted rows.
- **Residual:** actual antichains, missing leaves, histories, stronger-observer
  distinctions, and all unimplemented 0090 obligations.

The reference carrier accepts depths and precision from 1 to 8 as explicit
implementation limits. Evidence in this artifact is only for the frozen
enumeration and fixtures, plus the elementary argument above. Python labels
and descriptive histories are not native identities or authenticated history.

## 6. Costs and stopping

The measured initial execution used a 256 MiB address-space cap, a 30-second
CPU cap and wall-clock alarm, an additional outer 30-second timeout, at most
10,000 enumerated nodes per build, and a 1 MiB artifact limit. There were no
automatic continuations and no implementation-error correction replay.

| measured phase | local time |
| --- | ---: |
| witness construction and complete enumeration | 24.173321 ms |
| canonical serialization | 0.644799 ms |
| parsing and full replay | 25.607746 ms |
| constructing fresh input and reusing the gate | 0.061782 ms |
| measured phase total | 50.487648 ms |
| separate targeted seven-test suite, including discovery | 56.105723 ms |

One build consumes 2,876 counted state/completion nodes; the initial build and
full replay consume 5,752. The test suite separately constructs and replays
the fixed table for its tamper check and runs the small negative controls.
The resource budget is not a claim of equal actual work between algorithms.

Linux process peak RSS was 11,776 KiB for the measured harness and 14,848 KiB
for the separate tests. These are process high-water marks, not isolated
incremental memory attributable to the proposed word. Artifact size is
59,912 bytes and is **not** a peak-memory measurement.

Research design, source authoring, imports, source retrieval and persistence
costs are not included in the measured phases. Name creation is human/assistant
design work, not a timed learned-theorem formation process. Physical energy
and customer-use value were not measured. Raw timings are observations, never
CI performance gates.

Witness SHA-256:

    7b474d6969f8175197e1d1b7db9d5c7b3ca8e8b48caa4c5158c5b06613252197

The separately retained local-cost JSON binds to this digest.

## 7. Reproduction and checks

From the repository root, on Linux with Python 3.11 or later:

~~~console
timeout 30s python -m experiments.prefix_frontier.coverage_gate
timeout 30s python -m experiments.prefix_frontier.coverage_gate --check examples/verified_witness/prefix-coverage-gate.json
timeout 30s python -m unittest discover -s tests/python -p test_prefix_coverage_gate.py -v
~~~

The first command emits a JSON envelope with witness and newly measured costs.
The second compares only the deterministic witness, not local timings.
The measured run already parsed and replayed its emitted witness; the saved
file's hash and byte count were checked separately.

Seven targeted tests passed: omitted coverage, fresh reuse and reopening,
refinement conservation/history distinction, malformed/overlapping inputs,
inclusive dyadic endpoint and mass one, zero-fuel refusal, and complete-table
replay with mutated-outcome rejection. This run did not repeat the whole
repository suite or wait for CI.

## 8. Remaining obligations and practical help

This is part of 0090's exact reference carrier and feature/refinement controls.
It does not complete the Gold twin-machine test, measured/PAC modality,
simulator-failure control, evidence-bearing transitions, generalized reopen
handles, or Rust-backed distributivity transfer. In particular,
[0092](0092-generative-distributivity-venture-calibration-plan.md)'s all-fillings
closure and scoped promotion gate remains blocked; none is attempted here.

For Mingli and later agents, the concrete aid is an executable distinction
between a small recorded uncertainty interval and a certificate that covers
every legal completion. It can prevent a later proposal generator from
promoting pairwise success into an unsupported all-fillings statement.

For Jiamin, this is a potential problem-formation aid: when listing alternative
actions, retain an explicit unclassified region instead of interpreting the
recorded alternatives as exhaustive. This analogy is not measured customer
benefit or a proof that a real-world action list is complete.

The next smallest step is a bounded 0090 twin-machine/false-negative control:
use two finite positive traces that initially agree, and test that a timeout
cannot manufacture a negative certificate or close the object. It requires
its own preflight contract and is not started by this record.
