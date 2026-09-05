# ADR 0026: Separate reality grounding from the custody envelope

## Status

Accepted for the version-zero inquiry experiment. This adds optional research
data and does not change `adva.ir` version 1.

## Context

The first inquiry transition proposed an anchor-relative `representation` but
did not say what makes an anchor meaningful on the reality side or how the
record survives damage. A hash alone detects a changed byte string; it cannot
prevent deletion, identify an author, recover a lost copy, make independent
observers agree, or establish that a claim is true. Treating those properties
as one notion of trust would reproduce the semantic drift that the interface
is intended to expose.

The second transition must therefore preserve two separate questions:

1. Under what operational condition does a formal coordinate refer to a
   reality-side observation?
2. Under what declared fault model can the observation record remain
   attributable, available, and recoverable?

## Decision

`HypothesisCandidateV0` and `HypothesisV0` may carry an optional
`RealityBoundaryV0`. It contains:

- an external coordinate schema, observation protocol, and meaning criterion;
- a fixed policy requiring protocol-bound independent remeasurement;
- a fixed statement that receipts do not establish truth;
- explicit threat classes and protected properties;
- a `CustodyPlanV0` with failure-domain count, observation and recovery
  thresholds, declared fault budget, preservation strategies, and recovery
  drills.

The protected properties remain distinct:

| Property | Candidate mechanism | What it does not establish |
| --- | --- | --- |
| integrity | content address and append-only parent chain | survival or truth |
| authenticity | signatures, rotation, and revocation | truth of the signed claim |
| availability | diverse replicas and erasure-coded exports | semantic correctness |
| fork accountability | transparency log and retained conflicting branches | absence of disagreement |
| semantic reproducibility | independent protocol-conforming remeasurement | universal or observer-free truth |

The candidate threat vocabulary is `deletion`, `mutation`, `equivocation`,
`key_compromise`, and `correlated_capture`. Lists must be nonempty and unique.
Custody thresholds must be positive and no larger than the declared number of
independent failure domains. Strategies and recovery drills must be explicit.

The optional field is omitted when absent. Consequently the first resource,
hypothesis, candidate identity, and committed digests remain byte-for-byte
stable. When the field is present, it participates in the name-independent
candidate identity and is copied exactly into the hypothesis.

Vocabulary history now records only words that were actually inserted. The
second transition therefore introduces `custody`, not `hypothesis` again.

## Consequences

The machine can reject malformed local custody declarations and retain an
auditable threat model. It still does not deploy replicas, verify signatures,
perform remeasurement, execute recovery drills, or prove Byzantine agreement.
Numeric thresholds are policy coordinates rather than resilience theorems.

Reality-side meaning remains conditional on a concrete observation. The
second run can propose how such meaning and preservation should be tested, but
all five arithmetic obligations must remain open until actual observations and
typed witnesses are supplied.
