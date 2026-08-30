# Zero-Event Scope/Cut Incidence No-Go

Status: bounded exact-data counterexample for the first return from program
slices to `P*`. It uses only Rust-certified graft traces, cuts, steps, and
slices through their read-only Python facade. It does not install a stable
pullback, relation, matrix, dual grid, or PSP-star theorem.

## Minimal program

Take a two-output open program

```text
frontier(call identity-callee(x), neg(y)).
```

The identity call has a genuine compiler graft frame but emits no operation
node: its argument region and callee-body region are empty, and its entry and
exit wire are the same original wire `x`. The independent `neg(y)` is the only
event, numbered zero.

The causal-past lattice has two elements:

\[
c_0=\varnothing,
\qquad
c_1=\{0\}.
\]

The frame wire `x` crosses both certified cuts. Hence the zero-event call is
compatible with both identity slices

\[
\operatorname{Slice}(c_0,c_0)
\quad\text{and}\quad
\operatorname{Slice}(c_1,c_1).
\]

Both slices have empty graft intersections because intersections are defined
by operation-node membership. Nevertheless their whole cuts differ exactly.

## The independent surgery orbit

Advancing event zero moves `c_0` to `c_1`. The step consumes and produces only
the `y` branch; it does not touch the frame's entry/exit wire. Thus the two
compatible placements form one orbit of an independent cut surgery that fixes
all current data local to the zero-event frame.

Write `F` for the frame and define the research-local incidence relation

\[
F\;R\;c
\quad\Longleftrightarrow\quad
\text{the entry and exit wires of }F\text{ cross }c
\text{ and }\operatorname{Slice}(c,c)\text{ is event-empty}.
\]

Then

\[
R(F)=\{c_0,c_1\}.
\]

The smallest support compatible with independent surgery is therefore the
two-element fibre, not either individual cut.

## Why syntax order does not repair it

Swapping the two output terms changes the graft scope path from the first
frontier position to the second. It does not change the causal ambiguity: the
identity-call frame is still compatible with both cuts.

Using frontier position to choose `c_0` or `c_1` would silently turn ordered
boundary presentation into causal time. PSC0 does not authorize that
identification.

## Exact conclusion

This does not prove that no set-theoretic selector exists. One can choose the
least or greatest compatible past. It proves the narrower and relevant no-go:

> The present graft and slice data do not uniquely determine a scope-faithful,
> surgery-stable cut placement for every frame.

Any single-valued selector adds a policy not contained in the frame. Therefore
the most elementary honest candidate for the current `P*` is a finite
scope/cut incidence relation, or equivalently a set-valued map. A single-valued
`P*` requires extra structure.

There are three possible next moves:

1. retain the whole incidence fibre and formulate `P S P*` as exact relational
   composition on the finite cut graph;
2. add explicit zero-cost scope-boundary markers to the causal structure and
   test whether they make placement single-valued; or
3. quotient cuts by independent surgery, sacrificing the exact cut and path
   identities that the current kernel deliberately preserves.

Option 1 changes the least ontology and is the next bounded calibration.
Option 2 may eventually justify a new stable artifact but requires a separate
design decision. Option 3 conflicts with the current identity-preserving
objective unless the lost residual is retained explicitly.
