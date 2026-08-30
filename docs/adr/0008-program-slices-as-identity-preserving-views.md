# ADR 0008: Program slices as identity-preserving views

- Status: accepted
- Date: 2026-08-30

## Context

A causal cut is only one frontier snapshot.  It does not retain the events
between two cuts, and equal snapshots can hide different histories.  The
minimal counterexample is a constant consumed by explicit discard while an
independent input wire passes through unchanged: the lower and upper frontier
wires are equal, but two operation events occurred.

The next exact carrier therefore has to be an interval in one unchanged
checked diagram.  It must not be recompiled as a fresh program, because fresh
lowering would allocate new occurrence identities and lose literal endpoint
agreement.

## Decision

For downward-closed node sets `U` and `V` in one validated diagram, with
`U` contained in `V`, Rust derives `ProgramSlice(P,U,V)` as a companion view.
It retains:

- the certified lower and upper cuts;
- original operation nodes in `V` minus `U`;
- lower wires consumed in the interval;
- upper wires produced in the interval;
- exact through wires present at both cuts;
- events with no produced wire on the upper cut;
- original occurrences and node-associated copy/operation history relevant
  to the interval; and
- optional links to nonempty argument/body intersections of a revalidated
  compiler `GraftTrace`.

The two cut frontiers are checked to partition into changed boundary wires and
through wires.  No value, floating-point comparison, rewriting, or new
semantic identifier participates.

The basic analysis accepts every validated version-one diagram.  Graft links
are optional because imported diagrams have no compiler provenance.  An
empty-node call frame has no nonempty causal-region intersection, so the
analysis returns no frame link for it rather than assigning an arbitrary cut.

## Consequences

- Equal lower and upper frontier snapshots no longer imply an empty process
  interval.
- A `ProgramSlice` is exact same-diagram data, not a materialized standalone
  diagram and not a value-level observation.
- Graft intersections may overlap: a root frame and nested call frame can both
  contain the same event.  They are links, not an event partition.
- Node-associated history excludes flat source and call records.  Source
  provenance is retained by occurrences; call provenance is available only
  through a validated graft link.
- Exact adjacent-slice composition remains WP3 and requires its own
  certificate.
- No observer pullback, dual grid, `P*`, or `T = P S P*` theorem is introduced.
