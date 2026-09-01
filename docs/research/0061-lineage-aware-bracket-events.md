# 0061 — Lineage-aware bracket events

Status: bounded executable research following
[`0059-tri-bracket-eigen-normalization-logic.md`](0059-tri-bracket-eigen-normalization-logic.md)
and
[`0060-checked-bracket-observer-bridge.md`](0060-checked-bracket-observer-bridge.md).

The executable fixture is
[`test_lineage_aware_bracket_events.py`][fixture].

[fixture]: ../../tests/python/test_lineage_aware_bracket_events.py

This stage answers one structural question left open by note 0060:

> Can the three brackets remain permanently juxtaposed while checked
> computation still exposes dependency, sharing, and observer normalization?

The bounded answer is yes, provided bracket containment is removed from the
checked carrier.  The checked public shells remain

```text
{}[]()
```

and cross-domain provenance lives in a separate, lineage-decorated
hypergraph.  A nested string such as `[{}()]` is only a partial observer
serialization of that graph.  It is neither the public boundary nor a Rust
program term.

This correction supports the no-entry part of the motivating intuition.  It
does not yet show that the three shells are computational primitives, that
their three emptiness readings have introduction and elimination rules, or
that they generate a universal machine.

---

## 0. Executive verdict

| question | bounded verdict |
|---|---|
| Must one bracket enter another in the checked carrier? | no; the three public shells remain juxtaposed |
| Where does cross-domain dependence live? | in a separate Rust-derived support hypergraph |
| Is `[{}()]` exact lineage syntax? | no; it forgets IDs, multiplicity, self support, and Rust lineage order |
| Can every support graph be shown as `Raw111`? | no; cycles fail both projections, while other obstructions are projection-policy relative |
| Does legal copy sharing violate the checked model? | no; one `SourceId` may have several distinct `OccurrenceId`s |
| Does visible flattening delete provenance? | no; `ProvenanceHide` moves an edge out of the surface and retains the hypergraph |
| Are local IDs global identities? | no; every witness is scoped to and rechecked against one validated diagram and slice |

The main correction to note 0060 is that there are two independent
forgettings, not one:

1. exact Rust lineage order may be sorted by an observer display policy; and
2. an exact incidence multigraph may be collapsed to a set of domain-support
   relations.

Both quotients must be named and both require a residual.

The implementation consequently versions three different choices: the base
observer role/display policy, the selected projection policy (strict direct
incidence or weak ancestry set), and the root-child promotion rule used by a
`ProvenanceHide` witness.  A witness binds all three; none may be inferred
from the others.

## 1. Fixed shells and a separate exact evidence graph

The declared triadic observer has three permanent output roles:

\[
B=\{b_K,b_X,b_t\}.
\]

Their calibrated presentation is always `{}[]()`.  The role assignment is an
observer convention over the checked `(t, X, K)` input and output indices;
Rust currently checks three `Real` ports, not three native bracket types.

For one validated function, its output-ready full `ProgramSlice`, and the
versioned observer policy \(Q\), the fixture derives the finite decorated
support object

\[
\mathcal H_Q=(B,S,O,I,C_{\rm copy};P),
\]

where:

- \(B\) contains each exact upper output consumer index and its exact
  `WireRef`;
- \(S\) contains every Rust `SourceId`, including sources absent from the
  upper frontier, decorated by the declared input-domain map;
- \(O\) contains the Rust `OccurrenceId`s, `SourceId`s, and
  `OccurrencePath`s;
- \(I\) contains ordered upper incidences
  \((b_D,j,o,s,E)\), saying that lineage position \(j\) of output role \(D\)
  contains occurrence \(o\) from source \(s\) declared in domain \(E\);
- \(C_{\rm copy}\) contains the exact copy hyperedges
  `parent_occurrence -> child_occurrences`; and
- \(P\) is the complete validated IR, validation certificate, every
  `ProgramSlice` field, slice certificate, and policy against which an
  observer witness is rechecked.

The helper checks that each copy child path is the parent `OccurrencePath`
extended by its branch index.  This Rust path is not an observer bracket path.
Discard and other operation events remain in the complete \(P\) snapshot;
only the copy genealogy is additionally indexed in \(\mathcal H_Q\).

The extractor reads every complete output from
`ProgramSlice.upper.frontier`.  It does not read only `upper_boundary`:
unchanged output wires occur in `through_wires` and would otherwise disappear.

For every upper cut wire, Rust serializes `sources` in the same order and with
the same multiplicity as `wire.lineage`.  The fixture therefore uses
position-wise strict zipping.  It never converts this data to a set while
building \(\mathcal H\).

Ownership remains explicit:

| datum | owner |
|---|---|
| diagram, cuts, slice, `WireRef`, `SourceId`, `OccurrenceId`, copy links | Rust |
| `K/X/t` role map and `K<X<t` display order | declared observer convention |
| support hypergraph dataclasses and bracket projections | executable research helper |

Python copies and compares Rust identifiers.  It never allocates a semantic
identifier or treats an observer path as a Rust occurrence path.  All
identifiers remain local to the revalidated diagram in \(P\).

## 2. Three orders that must not be conflated

For checked spatial multiplication, the upper spatial wire has exact source
and occurrence order

\[
(t,K),
\]

because the checked `mul` consumes its temporal argument before its
construction argument.  A lineage-order bracket display would therefore be

```text
[(){}]
```

Note 0060 displayed

```text
[{}()]
```

by the declared color order `K<X<t`.  This is a useful stable display, but it
is not exact lineage order and it is not a checked event schedule.  The exact
order remains in \(I\).

Thus the fixture distinguishes:

1. **lineage order**, owned by the Rust upper `WireRef`;
2. **display order**, declared by the observer; and
3. **causal schedule order**, represented only by a NodeId-indexed path of
   certified cut advances.

No implication is asserted between these orders.

## 3. Two Raw111 projections

The one-color-once forest cannot be both exact and conveniently permissive.
0061 therefore supplies two differently typed decisions.

### 3.1 Strict direct-incidence projection

`project_raw111_strict` filters self support into the residual but never
deduplicates a foreign incidence.  Each remaining ordered upper incidence
must become one direct parent-child edge.  The projection rejects:

- two foreign occurrences of the same child color under one parent as
  `repeated-foreign-color`;
- one child color under two parents as `shared-foreign-child`; and
- every directed domain cycle.

If it succeeds, every domain occurs once and child order is the exact Rust
lineage order.  The result is named `StrictRaw111WithResidual`, not an exact
term, because the surface omits self support, ports, identifiers, copy
genealogy, and the checked program.

The identity triad gives `{}[]()`.  Checked spatial multiplication succeeds
as `[(){}]`: its two foreign incidences are distinct colors and their exact
lineage order is `(t,K)`.  A support chain with direct edges `K>X,X>t`
succeeds as `{[()]}` even though it fails the separate ancestry-set reading
below.

### 3.2 Weak domain-support-set observation

`observe_domain_support_set` deliberately forgets self support, IDs,
multiplicity, and lineage order.  It retains the full hypergraph as a
residual and forms the foreign relation

\[
R_{\mathcal H}
=
\{(D,E)\mid D\ne E\text{ and an incidence }b_D\leadsto E\text{ exists}\}.
\]

The result can be `ObservedWithResidual` or `NotRepresentable`; it is never
classified as exact.

One ambiguity must be fixed before serializing \(R_{\mathcal H}\).  A nested
term can encode either immediate parent-child edges or the strict
ancestor-descendant relation.  Note 0059 defines stability through descendant
domains, so this stage chooses the second reading.  Consequently, a weak
projection exists exactly when \(R_{\mathcal H}\) is a strict forest order:

1. it is acyclic;
2. it is transitive; and
3. the ancestor set of every domain is totally ordered by
   \(R_{\mathcal H}\).

The unique transitive reduction then supplies the immediate bracket tree.
The fixture checks that taking all bracket ancestries reconstructs
\(R_{\mathcal H}\) exactly.

It does not silently complete a non-transitive relation and does not silently
choose a spanning tree.  The strict direct-incidence projection above is the
separately named alternative; neither projection may substitute for the
other.

The finite decision table is:

| checked fixture | foreign relation | strict result | weak result |
|---|---|---|---|
| identity | empty | `{}[]()` with residual | `{}[]()` with residual |
| spatial multiplication | \(X>K,X>t\) | `[(){}]` with residual | `[{}()]` with residual |
| ancestry chain | \(K>X,K>t,X>t\) | `NotRepresentable`: shared foreign `t` | `{[()]}` with residual |
| non-transitive chain | \(K>X,X>t\) | `{[()]}` with residual | `NotRepresentable`: missing \(K>t\) ancestry |
| temporal-spatial cycle | \(X>t,t>X\) | `NotRepresentable` | `NotRepresentable`: cycle |
| copied temporal shared child | \(K>t,X>t\) | `NotRepresentable` | `NotRepresentable`: incomparable ancestors |
| two temporal occurrences under X | \(X>t,X>t\) | `NotRepresentable`: repeated foreign color | `{}[()]` with a two-incidence residual fibre |

The copied shared-child row is not a rejection of sharing by Adva.  Its one temporal source
is legally copied into three distinct final occurrences, and Rust certifies
linear use.  What fails is only the attempt to give the single `t` cell two
incomparable ancestors without choosing one and discarding the other.

## 4. A typed provenance event, not an overloaded split

Note 0060 called for a future split or discharge certificate.  That wording
is too broad.  Three observer events have different proof obligations:

| event sort | visible action | required evidence |
|---|---|---|
| `ProvenanceHide` | remove one support edge from the display only | exact upper port plus complete ordered source/occurrence incidence bundle |
| `PendingDischarge` | mark an obligation complete | exact lower/upper cuts and a NodeId-indexed certified causal-step path |
| `DefectDischarge` | establish a value equation | input binding plus checked evaluation result and certificate |

0061 implements only `ProvenanceHide`.  It must not be renamed to an
unqualified `split` or `discharge`.

The test-local witness contains:

- the event kind `provenance-hide`;
- the observer-policy version;
- the weak ancestry-set projection-policy version;
- the fixed root-child promotion-rule version;
- the complete canonical snapshot of the validated IR, validation
  certificate, re-derived slice, slice certificate, and policy;
- the exact before-surface and its visible/residual incidence partition;
- the observer-local parent path and child index;
- the parent domain, exact output consumer, and exact upper `WireRef`;
- the child domain together with the complete ordered bundle of matching
  `(lineage_index, OccurrenceId, SourceId, OccurrencePath)` incidences; and
- the committed after-surface under that bound promotion rule.

The parent bracket is an output-role shell, not an `OccurrenceId`.  The child
binding is an incidence bundle, not one color label.  The bracket path is only
a locator in the before-surface; it is not a Rust `OccurrencePath`.

Applying a witness calls the Rust-backed extractor again, reconstructs the
full checked snapshot, and exact-compares the relevant port and incidence
bundle.  A forged path, child index, source, occurrence, wire, or snapshot is
rejected.

The observer state enforces the lossless partition

\[
I=I_{\rm visible}\mathbin{\dot\cup}I_{\rm residual}.
\]

Both sides must remain stable subsequences of the observer-canonical support
order induced by \(Q\), which preserves Rust lineage order inside each output
port, and every domain-pair fibre must lie wholly on one side.  The state also
checks that the surface contains each color exactly once and that its full
ancestry relation equals the domain-pair set of \(I_{\rm visible}\).  A
surface edit, fibre split, or reorder without the matching evidence
transition is therefore rejected.

`ProvenanceHide` moves the complete incidence fibre of one displayed domain
edge from the first set to the second.  It never mutates \(\mathcal H_Q\).
For the repeated temporal fibre, both distinct occurrences must move
together; a witness containing only one is rejected.  Replaying a consumed
witness is also rejected by its complete before-state commitment.

The snapshot scope matters because current IDs are local to one validated
diagram.  Separately compiled programs can reuse `NodeId`, `SourceId`,
`OccurrenceId`, `WireRef`, and predictable certificate labels.  The fixture
compiles spatial multiplication and spatial addition with the same support
surface.  Their checked values differ, their complete snapshots differ, and a
multiplication witness is rejected when replayed against addition.

For the calibrated X-shaped star, both visible hide orders remain possible:

\[
(K,t)\qquad\text{and}\qquad(t,K).
\]

After display calibration both reach `{}[]()`.  The exact hypergraph remains
unchanged and still contains \(X>K\) and \(X>t\).  These are observer trace
orders, not Rust schedules, and visible flatness does not assert that source
dependence vanished.

The executable witness is intentionally limited to complete fibres on
depth-one, root-child support stars.  In ancestry semantics a deep split can
remove several ancestor pairs at once.  The transitive-chain surface therefore
offers no witness in this fixture; a future general witness must bind that
complete quotient delta rather than only the selected parent-child pair.

## 5. What the fixture establishes

The fixture establishes:

1. a finite extractor, total on the fixture's output-ready full slices, for
   fixed shells, exact upper ports, ordered incidences, source identities,
   occurrence identities and paths, and copy hyperedges;
2. inclusion of through wires by reading the complete upper frontier;
3. separation of Rust lineage order `(t,K)` from display order `(K,t)`;
4. a strict, direct, incidence-preserving `Raw111` decision whose success is
   explicitly typed `StrictRaw111WithResidual`;
5. a separately typed weak support-set ancestry observation;
6. the strict-forest-ancestry representability criterion;
7. positive identity, X-star, direct-chain, and transitive-ancestry cases;
8. exact counterevidence for non-transitive ancestry, cycles, repeated foreign
   colors, and incomparable ancestors;
9. legal one-source/three-occurrence copy sharing without occurrence aliasing;
10. a lossless visible/residual incidence partition whose set quotient
    round-trips to the surface ancestry;
11. an artifact- and policy-scoped, proof-relevant, complete-fibre
    `ProvenanceHide` event; and
12. rejection of path, observer/projection/promotion policy, port, incidence,
    after-state, stale-state, and cross-program witness tampering.

The cycle fixture contains an explicit checked `swap`; its construction
output is a through wire.  This is the regression that would be lost by an
`upper_boundary`-only extractor.

## 6. The merge architecture

The two research lines now fit into one dependent typed stack:

\[
\boxed{
(P,Q,B_3)
\longmapsto
\mathcal H_Q(P)
\longmapsto
\operatorname{ObserverView}_{Q,\pi}(\mathcal H_Q(P))
}
\]

This arrow is not a Cartesian product: lineage support is extracted from the
checked slice, and the view depends on both that support and the selected
projection policy \(\pi\).

- `FixedBoundary3` preserves the intuition that the three shells are always
  juxtaposed;
- `CheckedProgramSlice` owns computation, resources, event identity, and
  certificates;
- `LineageSupport` owns cross-domain source and occurrence evidence without
  forcing it into a tree; and
- `ObserverView` may render, hide, normalize, or reject a surface while
  retaining a typed residual.

This is a better merge than making nested brackets the program itself.
Cycles and sharing remain ordinary checked evidence even when the tree
observer fails.  Conversely, a flat surface cannot erase the checked
computation that produced it.

There is also a decisive residual no-go: spatial `add` and spatial `mul` have
the same alpha-normalized lineage-support shape but different checked values.
Therefore that structural shape, without its checked-program snapshot, is
not a complete semantic carrier.

## 7. Implication for the three-bracket intuition

The intuition survives at the interface level:

> `{}`, `[]`, and `()` can be three invariant, non-nesting observer shells.
> Computation acts on checked programs and evidence attached to those shells;
> nesting is only one optional visualization of a support or defect relation.

What has not survived is the stronger claim that the three empty glyphs alone
are already computational primitives.  A primitive requires typed
introduction, elimination, and composition rules.  None are supplied merely
by assigning three names to empty shells.

Likewise, braid or Coxeter transport can govern boundary order, but it cannot
by itself distinguish spatial `add` from spatial `mul`, delete a value defect,
or represent a support cycle as a forest.  The running map therefore needs at
least a checked value/resource action plus an independently typed transport
history.

## 8. Nonclaims and next gate

This note does not establish:

- a stable bracket, support-hypergraph, or witness API;
- a Rust bracket rewrite or diagram-to-diagram transformation;
- that observer paths or local IDs are globally canonical;
- a pending-obligation or value-defect discharge certificate;
- a general deep-ancestry or single-incidence provenance-hide rule;
- a faithful plain-bracket encoding of values, programs, or histories;
- a signed braid action on lineage evidence;
- branching, zero testing, unbounded storage, or interpretation; or
- universality.

No stable API or claim registry entry should be added from this fixture.

The next numbered gate remains a checked signed-history carrier.  Before any
universality experiment, it must show how a signed crossing acts alongside
the fixed shells without altering source or occurrence authority, and it must
retain pure-braid information that the current display sorting forgets.
