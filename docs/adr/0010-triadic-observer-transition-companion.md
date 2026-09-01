# ADR 0010: Triadic observer transitions as certified companion views

- Status: accepted
- Date: 2026-09-01

## Context

The completed `ProgramSlice` phase supplies exact process intervals, but the
three-domain research language still derived support hypergraphs and bracket
views in Python. Promoting a bracket tree directly would be premature: copy,
merge, discard, cycles, and shared children show that a wire or a Raw111 tree
cannot generally carry the complete evidence.

There is nevertheless an exact structure already present in the Rust kernel.
Every sourced cut-wire lineage position names one checked occurrence, every
occurrence names one source and one copy path, and `ProgramSlice` composition
preserves these identities. An explicit observer policy can assign the three
input sources to construction, space, and time without changing their semantic
types.

## Decision

Add version-zero companion types and Rust analyses for
`TriadicObserverTransitionV0`.

- `TriadicObserverPolicyV0` assigns exactly three input positions to the three
  roles, once each. Rust derives and checks the source map from the initial
  causal cut.
- `TriadicCutObservationV0` resolves every sourced lineage position to its
  exact occurrence and records source-free wires separately.
- Each domain view exposes incidences from the other two source domains and
  records its own-domain complement.
- `TriadicLineageLinkV0` relates lower and upper incidences precisely when they
  have the same source and the lower occurrence path prefixes the upper path.
- The complete exact `ProgramSlice` remains embedded as the residual.
- Adjacent transitions compose only in one unchanged diagram under one exact
  policy. Rust checks exact slice composition and independent finite-relation
  composition through the shared middle observation.
- Compiler graft traces remain optional companion provenance and are
  revalidated when supplied.

The types live beside process companion artifacts and do not change
`adva.ir` version 1.

## Consequences

- The three “opposite-side readings” now have one Rust-owned, auditable
  occurrence carrier.
- A sourced incidence is visible from two observer roles and hidden from its
  own role; the three views intentionally overlap.
- Source-free structure belongs to the residual and cannot be fabricated as a
  fourth domain.
- Copy is represented by one-to-many occurrence ancestry, merge by several
  retained incidences on one wire, and discard by absence of an upper
  descendant.
- Domain roles remain policy metadata rather than `ValueType`, wire type,
  physical coordinate, or intrinsic program ontology.
- The artifact is an observer view, not an active transformation, braid,
  specializer, proof, or logic judgment.
- A future bracket surface, right-to-forget witness, reverse dual, or
  normalization rule must be derived from this carrier with its own result and
  certificate type.
