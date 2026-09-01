# Checked Bracket Observer Bridge

Status: bounded bridge calibration following
[`0058-checked-gate-braid-composition.md`](0058-checked-gate-braid-composition.md)
and
[`0059-tri-bracket-eigen-normalization-logic.md`](0059-tri-bracket-eigen-normalization-logic.md).

The executable fixture is
[`test_checked_bracket_observer_bridge.py`][fixture].

[fixture]: ../../tests/python/test_checked_bracket_observer_bridge.py

This note performs the interpretation experiment requested at the end of note
0059.  It asks whether the exact checked spatial gate can be the abstract
one-edge containment `split`.

The answer has one negative and one positive part:

> `spatial-update` is not a containment split.  The two operations have
> incompatible value, composition, resource, occurrence, and boundary
> invariants.  There is, however, an exact finite observer bridge on the
> Boolean core: a mixed containment pattern can encode the one-bit spatial
> equation defect.  Checked `X` then projects to a conditional split macro or
> no-op, while the Rust-owned slice remains in an evidence fibre.

Plain three-bracket syntax is consequently a quotient observer, not the
native checked carrier.  This is a useful merge of the two research lines,
but it is not a new Rust rewrite, a universal machine, or an identification
of syntax containment with compiler graft containment.

---

## 0. Executive verdict

The fixture separates four claims that had previously been easy to conflate.

| question | bounded verdict | authority |
|---|---|---|
| Is one checked `X` one elementary `split`? | no | Rust values, IR, cuts, slices, lineage plus finite counterexample |
| Does checked `X` expose a bracket-like dependency surface? | yes: an unordered support star, displayed as `[{}()]` by policy | quotient of exact Rust source support |
| Can `X` project to normalization? | yes on eight Boolean states: conditional split/no-op | exhaustive decorated observer |
| Is plain bracket syntax faithful to the checked program? | no | rank, source, occurrence, and history loss |

The bridge classification used here is:

- `Exact`: the target retains the checked object and its identity evidence;
- `ObservedWithResidual`: the visible surface is a quotient, while a residual
  retains the exact checked evidence;
- `NotRepresentable`: the proposed surface carrier cannot encode the checked
  shape without an arbitrary choice.

Current plain brackets achieve only `ObservedWithResidual`.

## 1. Three sorts, not one

The first correction is a typing correction.

### 1.1 Raw111

Let

\[
\operatorname{Raw}_{111}
\]

be the thirty ordered forests containing exactly one `K`, one `X`, and one
`t` domain cell.  Mixed containment is permitted.  The abstract operation

\[
\operatorname{split}
\subseteq
\operatorname{Raw}_{111}\times\operatorname{Raw}_{111}
\]

cuts one root-child edge and preserves the three domain cells.

### 1.2 Flat111

Let

\[
\operatorname{Flat}_{111}
=\{p\in\operatorname{Raw}_{111}\mid e(p)=0\}.
\]

This six-object sort contains the flat color permutations.  The fixture uses
unsigned adjacent Coxeter moves `s_1` and `s_2` only on this flat sort.  These
moves record the endpoint projection

\[
\pi:B_3\longrightarrow S_3.
\]

They are not signed Artin words and cannot distinguish
\(\sigma_i\) from \(\sigma_i^{-1}\).

### 1.3 PublicBoundary

The checked gate has one fixed typed public interface

\[
\Omega_\partial=K\otimes X\otimes t.
\]

Its implementation parameter order is `(t, x, k)` and inputs are mapped by
name.  Outputs are mapped by their declared role and index in the same order.
The glyph `{}[]()` presents this one calibrated interface.  A nested raw
forest is not itself a checked boundary, and a `split` that changes the number
of forest roots does not change the checked gate's 3-to-3 arity.

## 2. The exact checked gate

The fixture compiles a wrapper around the same gate as note 0058:

\[
X(t,x,k)=(t,t\wedge k,k)
\]

on the Boolean core.  The wrapper exists only to expose an exact nested
compiler graft trace.  Its flattened checked program has:

- three lower and three upper boundary wires;
- no through wire across the full slice;
- two `copy` nodes, one `discard`, and one `mul`;
- final source profiles

  \[
  L(t)=\{t\},\qquad L(X)=\{t,K\},\qquad L(K)=\{K\};
  \]

- no old spatial input source in the upper frontier; and
- four final leaf occurrences derived from the copied temporal and
  construction occurrences, not three preserved input occurrences.

These facts come from the Rust-validated diagram, cuts, `ProgramSlice`, and
event history.  Python neither creates nor reassigns their identifiers.

## 3. Why direct identification fails

### 3.1 Value and rank

Checked `X` forgets the old spatial value.  For example,

\[
X(0,0,0)=X(0,1,0)=(0,0,0).
\]

It has rank four on the eight Boolean states and is idempotent:

\[
X^2=X.
\]

A payload-preserving split still distinguishes the two old `X` payloads.
The complete undecorated normalizer of note 0059 sends all thirty raw forests
to one surface, so it has rank one.  Neither map can be conjugate to checked
`X` on the plain carrier.

### 3.2 Composition

An elementary split removes exactly one containment edge.  Starting at

```text
[{}()]
```

one split leaves one edge and a second split removes the remaining edge.
Checked `X`, by contrast, takes every defect state to its fixed locus in one
application.  One partial, one-edge rewrite therefore cannot realize the
whole checked gate macro on this two-edge pattern.  This is a supporting
composition obstruction; the typed resource contradiction below is decisive.

### 3.3 Resource and occurrence evidence

The abstract split preserves the same three domain cells and has no declared
copy, discard, multiplication, or source substitution.  Checked `X` instead:

1. discards the old spatial source;
2. copies the temporal source;
3. copies the construction source;
4. forms a new spatial output from the two copied branches; and
5. replaces parent occurrences by exact copy children in the final lineage.

Any interpretation that reflects values, `SourceId`, `OccurrenceId`, or the
resource ledger is contradicted by these invariants.

### 3.4 Boundary type

The checked slice remains in one fixed 3-to-3 hom-set.  A raw one-edge split
promotes a child and increases the number of forest roots by one.  Therefore
raw roots cannot simultaneously be interpreted as checked external ports.

The proposed direct equation is ill-typed and rejected:

\[
\boxed{\text{No exact type-preserving interpretation maps one }
\operatorname{ProgramSlice}_X\text{ to one split.}}
\]

## 4. A source-support observer

There is nevertheless a Rust-grounded bracket observation.  Declare the
input and output domain maps by the checked signature.  For every upper
domain role \(D\), draw a foreign-support edge

\[
D\longrightarrow E
\]

when the exact upper wire for \(D\) contains an input source from
\(E\ne D\).  Self-support is omitted.  Empty source support creates no
foreign child.

Only an acyclic graph in which every domain has at most one foreign parent
can be serialized as an ordinary forest.  A general bridge must return
`NotRepresentable` for a shared child, cycle, or other nonforest result rather
than choose an arbitrary spanning tree.  The present executable helper is
deliberately X-specific; cycle and sharing guards are deferred to the
lineage-aware carrier.

For checked `X`, the exact source profiles give

\[
G_X=\{X\to K,\;X\to t\}
\]

The support star is unordered.  The fixture uses the declared display policy
\(K<X<t\) for roots and siblings, producing the observer surface

```text
[{}()]
```

with stable domains \(\{K,t\}\).  Relative to this observer the checked gate
creates, rather than removes, visible dependency nesting:

\[
{}[]()
\xrightarrow{\operatorname{activate}_X}
[{}()].
\]

This `activate_X` is not the one-edge `inject` of note 0059.  It adds two
foreign-support edges at once and carries the noninvertible resource witness.

The single-root string is an internal dependency quotient, not the public
boundary.  A boundary-preserving display needs three permanent output shells
and repeated-colored provenance cells.  Omitting self-support gives

```text
{}[{}()]()
```

while a fully explicit lower and upper lineage display would be
`{{}}[[]](())` and `{{}}[{}()](())`.  Exact occurrence and source references
are still needed to represent sharing.  The one-color-once `Raw111` carrier
is therefore useful as a control quotient but cannot by itself be the checked
3-to-3 lineage carrier.

The two split schedules from `[{}()]` reach the same flat calibrated surface:

\[
(X{>}K;X{>}t)\quad\text{and}\quad(X{>}t;X{>}K).
\]

Their traces remain distinct.  Flattening means only that the dependency
edges have moved out of the visible observer surface.  The residual still
retains \(X\to\{K,t\}\), the old-`X` discard, copy parent/children,
node DAG, cuts, and the exact slice certificate.

The existing research label `split:D>E` is itself only a trace hint.  For
example, `{[]()}` and `{()[]}` can both take `split:K>X` to the same
`{()}[]` surface with the same label.  The old sibling position is not
recoverable.  A future discharge certificate must include the exact parent
and child occurrences, child index or before-path, original IDs, and the
checked source/occurrence witness.  This note never treats the short label as
such a certificate.

The checked four-node DAG has exactly eight causal linearizations: the two
copies must precede `mul`, while `discard` is independent.  Projecting each
linearization, by a declared research policy, to the relative order of the
temporal and construction copy events gives exactly two fibres of size four,
one for each split order above.  Rust certifies the causal schedules and IDs,
not this copy-to-split interpretation.  Forgetting the split order then gives
the one calibrated endpoint:

\[
8\ \text{checked schedules}
\longrightarrow
2\ \text{split schedules}
\longrightarrow
1\ \text{surface}.
\]

The final `ProgramSlice` records the event set, not those eight
linearizations.  A schedule-sensitive bridge must therefore retain the
NodeId-indexed cut path in its residual.

Thus source support gives a factorization, not an equation:

\[
\text{checked gate}
\longrightarrow
\text{dependency activation}
\longrightarrow
\text{residualized surface normalization}.
\]

### 4.1 Pending obligation versus retained provenance

The same glyph can be used by a second, explicitly slice-relative observer.
For a fixed checked slice and causal cut, let a dependency remain visible
while the declared upper output wire is not yet ready.  Once all three upper
wires are on the cut frontier, move those obligations into the residual and
show the flat surface.

In the fixture there is a legal past-closed cut containing both copies and
the multiplication but not the independent discard.  At that cut all three
outputs are ready, so the pending surface is `{}[]()`, yet the old spatial
discard remains enabled.  Only the full upper cut is quiescent.

This makes the distinction executable:

\[
\text{pending surface flat}
\centernot\Longrightarrow
\text{machine halt}.
\]

The provenance observer still renders `[{}()]` at the same upper state,
because the new spatial value continues to derive from temporal and
construction sources.  Pending obligation and retained provenance are two
different observer sorts and must not share an unqualified \(\Phi\).

## 5. The finite defect bridge

The strongest positive result is a different observer whose containment edge
means a pending equation defect, not produced dependency provenance.

For a Boolean state \((t,x,k)\), define

\[
\delta_X=x\oplus(t\wedge k).
\]

Retain \((t,k)\) as fibre data and encode the defect by

\[
E(t,x,k)=
\begin{cases}
(t,k,\;{}[]()) & \delta_X=0,\\
(t,k,\;[{}()]) & \delta_X=1.
\end{cases}
\]

The inverse decoder is

\[
x=(t\wedge k)\oplus\delta_X.
\]

Hence the decorated code, unlike the plain surface, is a bijection on all
eight input states.  The two driver-labelled defect edges occur together and
encode one Boolean defect flag.  They have the same glyphs as the support
surface in section 4 but inhabit a different observer sort.  Let \(N_X\) be
the traced, multivalued normalization relation for the joint pattern
by the two possible orders of `X>K` and `X>t`, followed by flat calibration,
and otherwise do nothing.  Let \(\bar N_X\) forget the trace and retain its
unique endpoint code.  Exhaustive checked evaluation establishes the
endpoint-code law

\[
\boxed{E\circ X=\bar N_X\circ E}
\]

on all eight Boolean states.  Exactly four states are already fixed and take
the no-op branch; exactly four contain the defect pattern and take a two-split
macro.  Both split schedules have the same endpoint and retain different
traces.  The four endpoints are still distinguished by the retained
\((t,k)\) fibre.

The intermediate one-edge surfaces are valid `Raw111` terms but are not in
the image of the binary encoder \(E\); only the complete macro is decoded.

The joint pattern carries exactly one bit, matching the two-to-one fibres of
checked `X`.  It is a finite value shadow of the discarded spatial defect,
not an occurrence or source certificate.  The checked resource residual is
still required.

For real-valued states the corresponding next ansatz is

\[
r_X=x-tk,
\]

with a flat surface for \(r_X=0\) and a payload-bearing defect edge for
\(r_X\ne0\).  This note does not claim or test that extension.

## 6. Compiler graft containment is a third structure

The wrapper's certified `GraftTraceArtifact` contains exactly

```text
root -> spatial-update call -> spatial-body call
```

with deterministic frame IDs, checked parent/child relations, and exact
`root_body` and `callee_body` roles.  The full `ProgramSlice` intersects the
two call frames, but it does not reparent them.  Requesting cuts or slices
leaves the compiler trace unchanged.

This gives a positive answer to a narrower question: Adva already has an
authoritative construction-scope containment tree.  It does not give three
domain colors to those frames, and it is not the dependency or defect forest
above.  The three structures must remain typed separately:

| containment | owner | meaning | mutable by `ProgramSlice`? |
|---|---|---|---|
| graft frame parent/child | compiler certificate | finite call substitution scope | no |
| source-support edge | read-only checked observer | cross-domain output dependence | observer only |
| defect edge | decorated finite observer | unsatisfied value equation | conditional quotient |

An active checked reparenting operation would require a future Rust-owned
diagram-to-diagram rewrite artifact with old/new identity maps and a
residual.  It cannot be smuggled into `graft_intersections`.

## 7. Surface satisfaction is not machine halting

This bridge also fixes two terms from note 0059.

For a requested nonempty face \(S\), write only

\[
\operatorname{Sat}_S(p)
\quad\Longleftrightarrow\quad
S\subseteq\operatorname{Stable}(p).
\]

This is a surface predicate.  Machine halting additionally requires an
observer policy with no enabled active step:

\[
\operatorname{Halt}_{S,Q}(M)
=
\operatorname{Sat}_S(\operatorname{surface}(M))
\land
\operatorname{Quiescent}_Q(M).
\]

Accordingly, the old research-local status label `halted` has been renamed
`satisfied` in the face oracle; it is not a checked halt.  Fuel exhaustion
returns `unknown`; an unsatisfied face with available work is `open`, not a
proof of nontermination.

Likewise, the unsigned root swap in note 0059 is only the Coxeter endpoint
projection.  The corrected normalizer used here first performs all splits,
then applies `s_i` on `Flat111`.  Exact signed braid history remains the
separate transport sidecar from notes 0057 and 0058.

## 8. Merge architecture

The bounded merge object is a fibre-refined transition

\[
\widehat X=(X,\bar N_X,\rho_X),
\]

where:

- the checked projection is the Rust `spatial-update` slice;
- the defect-surface projection is conditional split/no-op;
- the source-support projection records dependency activation and subsequent
  residualized flattening; and
- \(\rho_X\) retains exact lower/upper wires, sources, occurrence lineage,
  copy/discard/mul events, graft intersections, slice certificate, and both
  observer traces.

Forgetting \(\rho_X\) is an explicit quotient.  Keeping it prevents the flat
surface from falsely claiming that provenance disappeared or that
`activate;split` was an invertible identity.

This architecture is preferable to assigning one overloaded meaning to
nested brackets:

1. pending code or equation defects belong to the normalization surface;
2. produced dependency and construction history belong to evidence;
3. the public three-port boundary remains fixed; and
4. signed transport history remains independent until a checked gate can
   observe it.

## 9. What is established

The fixture establishes:

1. exact checked value, resource, source, occurrence, boundary, and graft
   facts for one wrapped spatial gate;
2. a direct `split = X` counterexample from value rank and composition;
3. an exact foreign-source support projection to `[{}()]`;
4. two convergent split schedules with distinct traces;
5. the exact cardinalities \(8\to2\to1\) under the declared schedule projection;
6. an exhaustive eight-state decorated defect code;
7. the endpoint-code law \(E\circ X=\bar N_X\circ E\);
8. four no-op and four two-split-macro states;
9. separation of graft, dependency, defect, and public-boundary structures;
   and
10. the `ObservedWithResidual` merge classification.

## 10. Nonclaims

This note does not establish:

- that plain brackets are Adva's native code or occurrence carrier;
- a stable bracket, observer, defect, rewrite, or residual API;
- a Rust `DirectedRewrite`, `EquationCell`, or `CoherenceCell`;
- a general forest projection for cycles, sharing, or repeated colors;
- a real-valued payload-edge bridge;
- that current split traces are identity-complete certificates;
- that the checked gate observes pure braid history;
- three symmetric domain normalizers;
- branching, a zero test, unbounded memory, interpretation, or self-application;
- a faithful encoding of a known machine; or
- any form of universality.

In particular, the current construction flip is involutive rather than an
idempotent construction normalizer on the Boolean core.  It is better read as
a reopening or oscillation gate until a separate fixed-point semantics is
supplied.

## 11. Next falsifiable stages

The next stages should add one authority upgrade at a time:

1. **0061, lineage-aware bracket events:** define a Rust-derived decorated
   support hypergraph that retains cycles and sharing; only its projection to
   `Raw111` returns `NotRepresentable`.  Give split witnesses exact parent
   path, child index, and original IDs;
2. **0062, checked signed history carrier:** move signed crossing data out of
   Python-only logs without changing source or occurrence authority;
3. **0063, history-sensitive normalizer:** exhibit a checked observer with
   \(O(\beta)\ne O(\beta p)\) for some pure braid \(p\), while preserving
   quiescence and `unknown` residuals;
4. **0064, repeated occurrences and control:** after separate semantic
   approval, calibrate payload, sharing, discard/copy, zero test, and branch;
   and only then
5. **0065, bounded faithful simulation:** if those dependencies pass, encode a
   two-counter machine with explicit `INC`, `DECJZ`, and `HALT` obligations.

The normalization intuition survives, but in a more precise form:

> A bracket edge can be the visible shadow of an equation defect, while the
> checked program and its provenance live in a fibre.  Computation may project
> to normalization without being identical to bare topology normalization.
