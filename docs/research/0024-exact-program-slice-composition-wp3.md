# Exact Composition of Adjacent Program Slices

Status: exact finite Rust result for WP3 of the program-slice phase.  It proves
the first same-diagram structural checkpoint in the executable kernel.  It is
not recompilation, cross-program transport, observer pullback, or a PSP-star
factorization.

## Composition law

Let `U <= V <= W` be downward-closed event sets in one validated finite
diagram `P`.  Write

\[
A=\operatorname{Slice}(P,U,V),
\qquad
B=\operatorname{Slice}(P,V,W).
\]

The Rust operation checks the exact middle boundary and event partition, then
constructs

\[
B\circ A=\operatorname{Slice}(P,U,W)
\]

using the union of the original node identities and the outer endpoint cuts.
It finally compares every result field with the directly derived outer slice.

No new `NodeId`, `SourceId`, `OccurrenceId`, path, wire, or history event is
allocated.  No program is lowered again.

## Why concatenation is insufficient

Two adjacent event vectors need not concatenate into original diagram order.
Events in the second interval may be independent of events in the first and
may occur earlier in the compiler's deterministic topological order.  The
composition therefore forms a set union and filters the unchanged source
diagram to recover canonical order.

Likewise, boundary lists are recomputed as views of the outer endpoints.  A
wire through the first interval can be consumed in the second, so it is not a
through wire of the composite.

## Checked laws

The implementation and exact Rust fixtures establish:

- boundary agreement at the shared middle cut;
- disjoint event conservation and exact outer union;
- direct/composed equality of all slice fields;
- left and right identity slices;
- associativity for three nonempty adjacent slices;
- preservation of optional graft-frame intersections; and
- retention of a hidden constant followed by discard when the outer frontier
  snapshots are identical.

Associativity is intensional here: both parenthesizations are literally the
same canonical `ProgramSlice` data, not merely equal after evaluation.

## Effect on the motivating intuition

The first finite checkpoint survives:

> Exact program intervals between nested cuts compose while preserving every
> original semantic identity and internal event.

The stronger scope/cut intuition remains weakened.  Graft intersections are
overlapping partial links, and zero-event frames have no nonempty event-region
intersection.  Exact slice composition does not repair that obstruction.

Thus WP3 supplies a rigorous finite candidate for the compositional content
of `S`.  Constructing a contravariant synthesis map `P*`, a canonical E0 dual
grid, and an expression-level equality `T = P S P*` remain separate tasks.
