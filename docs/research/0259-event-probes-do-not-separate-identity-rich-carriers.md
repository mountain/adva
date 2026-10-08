# Research 0259: Event probes do not separate identity-rich carriers

Date: 2026-10-08. Status: finite external counterexample calibration.

Question, experiment, and report: **Codex (OpenAI)**. Submitted through Mingli
Yuan's GitHub account as an authorized proxy. Account use is not his
authorship, technical review, endorsement, or a correctness guarantee.
Project-original contributions are offered under Unknown v0.3.

Inspected base:
`mountain/adva@e16134412b2ab4ca88d9d013743e06bcd6e06baf`. Research
0258 proves that all event-membership probes separate the downsets of one
fixed finite event poset. This round asks whether that statement lifts to the
identity-rich states that Adva must retain.

## 1. Frozen problem and budget

The finite carrier is the fork

\[
e_0<e_L,\qquad e_0<e_R.
\]

Its five downsets are fixed. The exact carrier additionally records a
`SourceId` assignment, an `OccurrenceId` assignment, and one legal linear
history. The family contains the Cartesian product of:

- two leaf-source assignments;
- two leaf-occurrence assignments;
- the two legal orders of the incomparable leaves.

Hence there are eight exact carriers and forty exact states \((C,I)\). The
event observer intentionally forgets the carrier:

\[
O(C,I)=(\mathbf 1_{e_0\in I},
        \mathbf 1_{e_L\in I},
        \mathbf 1_{e_R\in I}).
\]

The contract fixes all 780 unordered state pairs before execution. It permits
at most 100,000 comparison units and 30 wall seconds. There is no candidate
search, no native execution, no vocabulary proposal, and no permission to
change the family after seeing a result.

## 2. Exact result

Within any one exact carrier, the five membership vectors are distinct:

\[
O(C,I)=O(C,J)\Longrightarrow I=J.
\]

Across carriers the same implication fails immediately:

\[
C\ne C'\quad\text{and}\quad I=I'
\Longrightarrow O(C,I)=O(C',I').
\]

The exhaustive run found zero membership collisions within a fixed carrier
and **140 collisions** across different exact carriers. Each of the three
single-field differences—source only, occurrence only, and history only—has
20 witnessed colliding pairs. The retained history-only witness has the same
event set, order, sources, occurrences and ideal; it differs only in whether
\(e_L\) or \(e_R\) appears first after \(e_0\).

This gives the required boundary:

> The complete event-membership family is separating only relative to a fixed
> carrier. It is not an injective observation of the disjoint union of
> identity-rich carriers.

This is an elementary finite counterexample, not a new unrestricted theorem.
The phrase “carrier-relative separation” is used descriptively here and is
not promoted as Adva vocabulary.

## 3. Refinement ladder

The same fixed family was compared under four observation profiles:

| Observation retained | Colliding unordered pairs |
| --- | ---: |
| event membership only | 140 |
| event membership + sources | 60 |
| event membership + sources + occurrences | 20 |
| event membership + sources + occurrences + history | 0 |

The final row is injective only because the finite experiment retains every
coordinate used to generate its states. It is not a proof that these fields
are sufficient for native Adva objects: aperture positions, alternatives,
cells, connector compatibility, and other residuals are outside the family.
Nor does retaining the complete object beside an observation make the
observation itself faithful.

The older coarse event-count observer also has eight within-carrier
collisions: for each carrier, \(\{e_0,e_L\}\) and
\(\{e_0,e_R\}\) have the same size. Full event membership separates that
particular collision, exactly as Research 0258 states.

## 4. Refusals

Five controls are rejected before observation:

1. a missing source assignment;
2. duplicate occurrence identities;
3. a history that places \(e_L\) before its prerequisite \(e_0\);
4. an ideal containing an unknown event;
5. the non-downset \(\{e_L\}\), which omits \(e_0\).

These controls prevent the refinement ladder from “solving” a collision by
silently accepting malformed exact states.

## 5. Execution and costs

The retained run reports:

- 63 checks;
- 3,900 pair-comparison units;
- zero search candidates;
- 0.014127538 seconds;
- 11,264 KiB maximum supervisor RSS;
- 2,192 serialized bytes before the telemetry record.

One earlier execution reached 780 comparisons and stopped before evidence
serialization because the supervisor expected 16, rather than eight,
same-cardinality within-carrier ideal pairs. The five-ideal fork has one such
unordered pair per carrier. The failure is retained with unmeasured time and
memory; the only correction changed that expected constant to eight without
changing the family or question.

One optimized fresh replay used 3,900 units, 0.013490076 seconds and 15,680 KiB
RSS. Its deterministic result and five controls were byte-identical to the
retained evidence. The standard-library test route performed one further
fresh replay in 0.010930243 seconds and 12,544 KiB RSS. Thus the three accepted
runs used 11,700 comparison units and 0.038547857 measured execution seconds;
including the retained failed attempt gives 12,480 known comparison units.
`pytest` was unavailable, so the two unchanged test functions were invoked
through `runpy`.

Reproduce into a new path:

```sh
python3 experiments/observer_identity_collision/run.py \
  --output /tmp/observer-identity-collision
```

The source, frozen contract, failure, result, controls, telemetry and byte
manifest are under
[`experiments/observer_identity_collision/`](../../experiments/observer_identity_collision/).

## 6. What advanced and what remains open

Research 0258's fixed-poset separation theorem remains intact. This result
rules out only an **unqualified lift** from downset separation to exact Adva
state separation. A Galois or Henkin-style completion may correctly construct
an ideal while still forgetting which source, occurrence or history produced
it.

This helps Mingli and later agents state the native bridge more precisely:
before calling a family faithful, name the carrier coordinate being held
fixed and the quotient being separated. It also protects human/AI handoffs
from treating equal coarse observations as permission to replace an exact
history.

No new vocabulary or claims-registry entry is added. The run supplies no Rust
certificate, native probe, triadic halt-word realization, M6 filler,
arithmetic universality, hypothesized arithmetic truth, `free` authority, or
evidence of practical value for Jiamin.

The next minimum step is now narrower: obtain **one Rust-checked
`ProgramSlice` carrier**, keep its exact sources, occurrences and history,
and find two legal native observation inputs that share the existing event
projection. Then test one actual source-, occurrence-, or history-sensitive
probe. If no such pair or probe can be extracted through the existing Rust
boundary, retain that as the next `Unknown` rather than reconstructing
semantic identities in Python.
