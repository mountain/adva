# ADR 0009: Exact adjacent composition of program-slice views

- Status: accepted
- Date: 2026-08-30

## Context

`ProgramSlice(P,U,V)` is an identity-preserving view of one checked diagram.
The next obligation is to compose adjacent views for nested causal pasts
`U <= V <= W` without recompilation, new semantic identities, or evaluation.

Concatenating event vectors is not canonical.  Independent events can appear
in the original diagram order differently from the order in which adjacent
slices are presented.  Boundary data also cannot be concatenated: a wire that
passes through the first slice may be consumed in the second and therefore
becomes a changed boundary wire of the composite.

## Decision

Rust composes two adjacent slices only relative to their unchanged source
diagram.  The operation:

1. rederives both input slices and requires exact equality;
2. requires literal equality of the middle causal cut;
3. requires disjoint input event sets;
4. checks that their union is exactly `W` minus `U`;
5. builds the outer view from that original-ID union and the outer cuts; and
6. requires exact equality with the directly analyzed outer slice.

Composition of graft-linked slices additionally requires the original graft
trace and revalidates it.  A basic composition call rejects graft-linked input
instead of silently dropping the links.

`ProgramSliceCompositionCertificate` records input revalidation, boundary
agreement, event partition, original-ID and lineage preservation, and exact
direct/composed equality.

## Consequences

- Identity slices are exact left and right units.
- Three adjacent nonempty slices compose associatively because both
  parenthesizations equal the same canonical outer view.
- Internal constant and discard events survive composition even when the
  outer frontier snapshots are identical.
- Composition uses original diagram order, not slice concatenation order.
- The result is still a view of one diagram, not a standalone materialized
  program and not cross-program transport.
- This establishes the finite same-diagram checkpoint but does not define a
  frame/cut bijection, observer pullback, `P*`, or `T = P S P*`.
