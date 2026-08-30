# Exact Program Slices Between Nested Causal Cuts

Status: exact finite Rust result for WP2 of the program-slice phase.  It is an
identity-preserving interval analysis, not recompilation, slice composition,
observer pullback, or a PSP-star factorization.

## Definition

Let `P` be one Rust-validated finite program diagram and let `U` and `V` be
downward-closed event sets with `U` contained in `V`.  The compiler-independent
analysis derives

\[
\operatorname{Slice}(P,U,V).
\]

Its event content is exactly `V` minus `U`, in original diagram order.  Its
lower and upper endpoints are the already certified cuts `cut(P,U)` and
`cut(P,V)`.

Every lower-cut wire has exactly one of two roles:

1. its consumer is an event in `V` minus `U`, so it is a lower boundary wire;
2. it remains unchanged on the upper cut, so it is a through wire.

Every upper-cut wire likewise is either produced by an interval event or is
the same through wire.  Rust checks both partitions exactly.

An interval event is recorded as internal when none of its produced wires is
on the upper cut.  This includes explicit discard and also earlier events
whose outputs are completely consumed by later events in the interval.

## Equal-frontier counterexample

Consider the binder-free finite body

```text
frontier(discard(1), use(x))
```

The constant and discard are nodes zero and one.  The input wire for `x`
crosses both the initial and final cuts unchanged.  Consequently the two
frontier wire lists are exactly equal, while the program slice contains both
nodes and both node-associated history events.

Thus

\[
\text{equal frontier snapshot}
\not\Rightarrow
\text{empty program interval}.
\]

This is not a corner case to quotient away: explicit discard is part of the
program ontology.

## Graft intersection

When supplied with a compiler `GraftTrace`, the analyzer first revalidates the
trace against the unchanged diagram.  It then records, for every frame with a
nonempty intersection, the exact interval nodes lying in each argument region
and in the callee-body region.

These links do not partition events.  Parent and child frames intentionally
overlap on nested events.  They also do not produce a frame/cut bijection.

There is a sharper finite obstruction: a call whose argument and body are
both identity wiring has a real graft frame but no operation node.  Node-set
causality cannot choose one distinguished interval for this zero-event frame.
The analyzer therefore reports an empty intersection instead of inventing a
causal location.  Any future total scope-to-cut map needs extra boundary or
syntax data beyond event-set intersection.

## Preserved data

The result reuses exact original:

- `OperationNode` and `NodeId` values;
- lower, upper, and through `WireRef` values;
- source-bearing occurrence identities and paths;
- copy parent/child history and operation history for interval nodes; and
- graft-frame identities when compiler provenance is present.

No scalar evaluation, approximate equality, matrix representation, or fresh
lowering is used.

## Established boundary

WP2 supplies the exact carrier needed for composition, but does not yet prove
composition.  WP3 must construct the outer interval from two adjacent slices,
check boundary equality and event conservation, and compare the result with
the direct outer slice on exhaustive nested pasts.

The result also does not define a dual cellular grid or observer pullback.
Accordingly it advances the structural content needed for `S`, but it does
not supply `P*` or establish `T = P S P*`.
