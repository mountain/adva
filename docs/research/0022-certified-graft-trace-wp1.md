# Certified Graft Traces for Nested Multi-Hole Substitution

Status: exact finite Rust compiler result for WP1 of the program-slice phase.
It preserves nested binder-free call scopes as a companion to compilation.
It is not a local-binder calculus, `ProgramSlice`, causal-cut equivalence,
observer pullback, or expression-level PSP-star theorem.

## Question

The finite E0 surgery result requires an expression analysis that respects
ordered holes and substitution.  The surreal-cut no-go adds a hard
restriction: this analysis must retain the presented cut and its provenance
before objectification.

The first executable question is therefore:

> Can the existing finite compiler emit enough exact data to distinguish a
> call, its argument programs, its ordered hole bindings, its instantiated
> body, and nested calls on either side of that boundary?

For PSC0 the answer is yes, with two qualifications recorded below.

## Trace structure

For a compiled root program `R`, the compiler emits a rooted family of frames.
A call frame for

\[
C(A_0,\ldots,A_{m-1})
\]

retains two related maps.

First, every syntactic argument has an identity-preserving emitted region:

\[
A_i\longmapsto
(N_i; w_{i,0},\ldots,w_{i,k_i-1}),
\]

where `N_i` is the ordered set of original operation nodes emitted while
lowering the argument and the `w` values are its exact output wires.

Second, concatenating those output frontiers gives the ordered hole map:

\[
h_j\longleftarrow w_{i,r}.
\]

The frame stores `(i,r)` for every `h_j`.  It also retains the distinct
callee-body region, entry wires, exit wires, parent role, children, and call
history link.

This is stronger than storing one node set for the whole call.  It is also
more accurate than identifying syntax arguments with holes.

## Nested two-hole calibration

The main fixture compiles a root whose one frontier-valued argument fills two
holes of `pair`:

```text
root(x,y)
  = pair(frontier(neg-one(x), id-one(y)))

pair(left,right)
  = add-two(left,right)
```

The certified trace contains five frames:

1. the root;
2. the `pair` call;
3. `neg-one` inside argument zero of `pair`;
4. `id-one` inside the same argument; and
5. `add-two` inside the callee body of `pair`.

The `pair` argument region contains original nodes `0` and `1`, while its
callee-body region contains node `2`.  Both holes map to argument zero but to
different output indices.  The two argument children name `root` as caller;
the body child names `pair` as caller.  Recompiling the same linked modules
produces exactly the same frame IDs, paths, regions, wires, and certificate.

## Zero-output argument counterexample

The current call syntax concatenates the frontiers produced by all argument
terms.  Consequently this valid finite program exists:

```text
pair(discard(1), frontier(x,y))
```

The first syntactic argument emits `constant` and `discard` nodes but no wire.
The second emits two wires and fills both holes.  Any trace consisting only of
hole bindings would erase the first argument and its history.

The compiler therefore records argument regions independently of hole
bindings.  The exact test requires the first region to retain both nodes even
though no hole refers to it.

This counterexample does not invalidate finite substitution.  It invalidates
the simpler proposed representation

\[
\text{argument list}=\text{hole-binding list}.
\]

## Scope and cut are not yet identical

The trace gives an exact syntax-scope tree, but a frame boundary is generally
only a sub-boundary of the whole program.  Independent events and through
wires outside the frame can coexist at the corresponding causal stage.
Arbitrary causal cuts also need not be selected by a syntax frame.

Thus the current result supports a map

\[
\text{graft frame}
\longrightarrow
\text{regions and boundary wires in one checked DAG},
\]

not a bijection between frames and causal cuts.

The next `ProgramSlice` work must compute how frames intersect an interval
`(U,V)` rather than assigning one global slice to every frame by definition.

## Consequence for decorated surreal forms

The trace now supplies the missing construction data for a future research
presentation

\[
\mathsf{Form}_G(E)=
(L_E\mid R_E;
  \text{ordered holes},
  \text{scope path},
  \text{sources/occurrences},
  \text{surgery trace}).
\]

It does not yet construct `L_E`, `R_E`, or the dual surgery action.  It only
ensures that a later presentation need not infer substitution scope from flat
history or from an objectified value.

## Established facts

Within finite, acyclic, binder-free PSC0 compilation:

- frame identities are deterministic syntax-path data;
- parent/child nesting distinguishes argument and callee-body calls;
- every syntax argument region survives, including zero-output history;
- every ordered hole maps to one exact argument output wire;
- entry and exit wires retain original source and occurrence lineage;
- every call frame links exactly one flat call-history event and conversely;
- the unchanged `adva.ir` version-one diagram remains the semantic graph;
- the complete trace is checked before the artifact is returned.

No numerical evaluation, floating-point equality, normalization, matrix, or
analytic truncation enters these judgments.

## Remaining boundary

This result does not implement local binders, alpha equivalence,
capture-avoiding substitution, recursion, arbitrary graph contexts, imported
graft provenance, frame/slice equivalence, `P*`, or PSP-star factorization.

The next exact checkpoint is `ProgramSlice(P,U,V)`: retain the complete event
difference, through wires, hidden discard history, and intersecting frame
roles, then test identity-preserving composition on nested causal pasts.
