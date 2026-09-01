# ADR 0011: A bounded three-layer research machine above PSC0

- Status: accepted
- Date: 2026-09-01

## Context

The stable kernel now exposes exact causal cuts, `ProgramSlice` intervals, and
`TriadicObserverTransitionV0`. These artifacts already support three distinct
readings of one finite process:

1. a triadic interface reading at each endpoint;
2. a spatial carrier retaining the complete interval; and
3. a chosen causal schedule through that interval.

The research programme needs an executable instrument that keeps these layers
together, can replay a declared experiment, and reports finite obstructions.
Promoting feedback, recursion, normalization, or universal computation would
be premature. A finite acyclic PSC0 diagram cannot re-enable an event after it
has entered the completed causal past.

## Decision

Expose the existing Rust triadic-transition analyses through a read-only PyO3
and typed Python boundary. The boundary accepts only a three-role policy and
causal-past node IDs; Rust derives and certifies the result. Python-built
transition, slice, cut, occurrence, and certificate values are never accepted
as semantic inputs.

Add `adva.research.ResearchMachineV0` as a nonauthoritative, bounded companion:

- `ResearchCodeV0` is a strict, versioned, JSON-serializable experiment input;
- `InterpretationCellV0` packages exact lower and upper triadic interfaces, the
  complete Rust `ProgramSlice`, and one Rust-checked step trace;
- `FeedbackWitnessV0` records a finite number of endpoint-matched replay
  epochs, with fresh research-run references but unchanged static Rust event
  identities;
- `RunArtifactV0` retains cells, residuals, remaining schedule, verdict,
  reason, and a deterministic replay digest;
- one global fuel bound stops the run without turning exhaustion into a
  nonexistence claim.

The only positive replay criterion in version zero is literal equality of the
Rust cut frontier. Literal equality of complete cuts cannot hold for a
nonempty forward interval in a finite DAG and is reported as
`not_representable`. Frontier equality authorizes only repetition of the same
checked finite experiment; it does not connect the upper boundary to a newly
allocated semantic lower boundary.

## Consequences

- The repository gains a runnable three-layer instrument without changing
  `adva.ir` version 1 or PSC0 ontology.
- Schedule history remains distinct from the canonical `ProgramSlice`: two
  legal schedules can inhabit the same outer cell while producing different
  replay digests.
- Every abstraction retains the complete slice residual and Rust certificate.
- Epoch references are explicitly research-execution coordinates. They are
  not `NodeId`, `OccurrenceId`, source identity, or proof of event renewal.
- `supported` means only that the declared bounded run passed its checks.
  `fuel_exhausted`, `obstruction`, and `not_representable` remain distinct.
- Stable feedback, cyclic programs, active triadic normalization, a logic
  judgement, a compiler, and universal computation remain future promotion
  tasks requiring Rust-owned types, rules, and certificates.

