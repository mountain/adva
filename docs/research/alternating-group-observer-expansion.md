# Faithful inclusion and the boundary of a finite observer

Authored by ChatGPT (OpenAI). Submitted through Mingli Yuan's GitHub
account (mountain) as an authorized proxy.

Status: external exact finite experiment plus an elementary mathematical
argument, 2026-09-10. Base main:
`42882e6f723ec7ab9c008a810f187b06887a2c74`.
No new vocabulary name, native operation, semantic identity or library
catalog entry is proposed.

## Question and dependencies

Can a faithful extension preserve every old group element while making
an old separating observer insufficient on the enlarged domain? What is
the minimum additional observation in the fixed point-image grammar?

This calibrates the identifiability question in
[agenda Track C](../RESEARCH_ENGINEERING_AGENDA.md#3-track-c-learning-intrinsic-world-structure).
Its objects are external permutations, not checked world programs or
ProgramSlice histories. Native specialization and intrinsic-learning
dependencies remain outstanding; this does not advance those phases.
Only open PR #172 was present at inspection; its native load regression
gate is independent and unused. The merged golden-operator profile does
not become a finite permutation representation by renaming its matrices.

The user selected this finite follow-up after the discussion of all finite
simple groups. This experiment does not construct a universal carrier for
all simple groups or reprove the simplicity of alternating groups.

## Frozen interface

The contract is
[contract.json](../../experiments/alternating_observer/contract.json).
A permutation is the tuple of its images on labels 1 through n.
Composition is (p*q)(i)=p(q(i)). The even permutations for n=5 and n=6
are enumerated completely. Inclusion appends a fixed sixth point.
Q_B(p) records the images of the distinct point labels in B, in order.
There is no floating point, epsilon quotient, or identification of histories.

The candidate grammar for the minimum is exactly coordinate subsets.
An arbitrary observer could encode a whole permutation as one integer;
therefore the stated minimum is not a lower bound for arbitrary encodings.

One execution is permitted, at most 10 seconds and 100000 work units,
256 MiB address space and 1 MiB output. The implementation installs
RLIMIT_AS and RLIMIT_CPU; the command below supplies the wall timeout.
Finite dimension at most six bounds the inner arithmetic of each unit.
No automatic continuation or scope expansion occurs.

## Mathematical argument

Two even permutations with equal images on n-2 specified points differ
by an even permutation fixing these points. Only two points remain: the
only nonidentity permutation supported there is a transposition, which
is odd. Thus the two even permutations are equal.

With at most n-3 observed points, choose three unobserved labels. The
identity and a 3-cycle on those labels are distinct even permutations
with identical observations. Hence the minimum number of point-image
observations is n-2 for n >= 3.

In particular Q_(1,2,3) separates A5. The inclusion fixing point 6 is
injective and preserves composition, so this observer still separates
the embedded copy of A5. Once the admitted domain becomes all of A6,
identity and (4 5 6) give the same first three images. Observing point 4
distinguishes them, and Q_(1,2,3,4) separates all of A6.

This is a classical elementary argument written out here, not a novelty
claim or a machine-checked formal proof. Finite enumeration below checks
only the two declared degrees.

## Executed evidence

[replay.py](../../experiments/alternating_observer/replay.py) and
[evidence.json](../../experiments/alternating_observer/evidence.json)
retain the exact domains, every tested coordinate subset, fibre counts,
counterexample pairs, refusal controls and costs.

| Domain | Observer | Distinct observations | Fibre size |
|---|---|---:|---:|
| A5, 60 elements | (1,2,3) | 60 | 1 |
| A5 embedded in A6 | (1,2,3) | 60 | 1 |
| A6, 360 elements | (1,2,3) | 120 | 3 |
| A6, 360 elements | (1,2,3,4) | 360 | 1 |

All 840 permutations in S5 and S6 were inspected. Inversion parity and
cycle-count parity agreed on each. All 3600 A5 multiplication pairs
preserved the inclusion, and all 96 coordinate subsets were checked.
Minimum coordinate counts were 3 and 4 respectively.

Reuse changed the observer to (2,4,5): it separates A5 but not A6.
Adding point 1 separates A6. This is a new observation instance within
the same finite domain, not a new-degree experiment.

Missing coverage returned UnknownCoverage; a duplicate replacing a
missing element and an odd permutation each returned InvalidDomain.
Zero fuel returned UnknownResource. Completeness is compared with the
internally enumerated domain, not inferred from a supplied element count.
Serialization replay restored the full A6 domain and rechecked separation.

The checker is a fixed fixture harness, not a general validator for
untrusted remote JSON. A failed assertion would stop the process; the
external timeout may kill without a partial report. Neither event is
a no-solution certificate. This successful run had zero corrections.

## Costs and practical interpretation

Measured inside the process:

- construction: 3.067 ms;
- inclusion and initial verification: 5.596 ms;
- complete coordinate-subset search: 14.916 ms;
- nonprefix reuse: 0.449 ms;
- payload serialization and replay: 1.337 ms;
- total before final report write: 26.269 ms;
- work units: 31487; peak process RSS: 12032 KiB (11.75 MiB).

These phase times exclude some setup and controls. Final report writing
time, network, report authorship and total session time were not separately
measured. File size is not memory usage. No measured speedup is claimed.

This helps Mingli and the receiving agent distinguish an embedding failure
from an observer whose declared scope has grown. The repair adds one point
query per observed element: greater discrimination has an explicit cost.
It is not free information, social-trust verification or evidence of
universal grammar completeness. Customer value for Jiamin remains untested.

## Reproduce and continue

From the repository root on Linux:

```sh
timeout 10s python -B -S experiments/alternating_observer/replay.py --output /tmp/adva-alternating-observer-fresh.json
```

Use a fresh output filename; the saved evidence is never overwritten.
No third-party Python package or Rust toolchain is needed for this
external experiment.

The minimum next step is to bind a versioned observer receipt to the
explicit old and enlarged domain plus coordinate policy. A receiver must
reject a separation receipt reused with the enlarged domain, exhibit the
3-cycle collision, and verify the one-coordinate repair. This remains
a proposed engineering step. Native admission would additionally require
the existing Rust diagram and identity boundaries, not a Python digest.
