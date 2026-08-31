# From Dual-Cut Surgery to a Decorated Handle Operator

Status: exploratory research note extending
[`0034-triangular-spectral-cusp-semantics.md`](0034-triangular-spectral-cusp-semantics.md).
It sharpens one geometric direction into one bounded structural candidate. It
does not define a TQFT, Frobenius algebra, Fukaya category, stable category,
complex elliptic curve, spectrum API, or unrestricted program cobordism. It
does not change the active `ProgramSlice` implementation priority or promote a
claim to `claims.toml`.

The central revision is:

> The first construction-spectrum candidate should not be an arbitrarily
> closed edge relation. The existing checked fork--recombine fixture already
> has the shape `copy -> parallel branches -> add`. After a still-unbuilt
> oriented trace thickening, `copy` is a candidate copants, `add` is a
> candidate pants, and their composite is a decorated handle cobordism. In a
> genuine two-dimensional TQFT this composite is the handle operator
> `mu o Delta`, whose spectrum controls repeated genus construction.

The note follows the four-layer format: intuition, evidence, conservative
conclusion, and red-team opinion.

## 1. Intuition

### 1.1 Preserve the geometric direction before choosing a theory

The current direction is not simply

\[
\text{program}\longrightarrow\text{elliptic curve}.
\]

It is a sequence of geometric motions:

\[
\text{one cut cycle}
\longrightarrow
\text{split propagation}
\longrightarrow
\text{two decorated leaves}
\longrightarrow
\text{recombination}
\longrightarrow
\text{one cut cycle}.
\]

This motion is already present in the checked causal diamond

```text
copy -> {neg, id} -> add.
```

The two intermediate branches are not merely two coordinates. They are two
simultaneously present leaves between one incoming and one outgoing frontier.
The whole process therefore has a natural movie interpretation: a spatial cut
is transported in causal time, splits, receives two branch decorations, and
merges again.

The guiding semantic assignment is now:

| Role | First structural candidate |
|---|---|
| space | an instantaneous decorated dual-cut cycle |
| time | the ordered thickening from one causal cut to another |
| construction | the cobordism assembled from split, branch, and merge events |

These meanings are not attached to three cusp names. They are inferred from
how the structures transform.

### 1.2 Copy and add suggest copants and pants

In an oriented two-dimensional cobordism language, a pair of pants can be
read as a multiplication

\[
\mu:A\otimes A\longrightarrow A,
\]

while reversing its causal orientation gives a comultiplication

\[
\Delta:A\longrightarrow A\otimes A.
\]

The Adva diamond has the same input/output arities:

\[
\texttt{copy}:1\longrightarrow2,
\qquad
\texttt{add}:2\longrightarrow1.
\]

If branch operations `g` and `h` act on the two intermediate legs, the whole
diamond has the formal shape

\[
H_{g,h}
=
\mu\circ(g\otimes h)\circ\Delta.
\]

For the present fixture,

\[
H_{\mathrm{neg},\mathrm{id}}
=
\mu\circ(\mathrm{neg}\otimes\mathrm{id})\circ\Delta.
\]

Topologically, copants followed by pants along both intermediate circles is a
genus-one cobordism from one circle to one circle. The branch maps become
defect or decoration data on its two internal legs.

This gives a more structural source for elliptic intuition. A fork followed
by recombination creates one handle before any elliptic function is selected.

### 1.3 The construction spectrum becomes less arbitrary

For a commutative Frobenius algebra, the undecorated composite

\[
H=\mu\circ\Delta:A\longrightarrow A
\]

is the handle operator. Repeated genus construction is represented by powers
of `H`. In semisimple or unitary settings its eigenvalues control the response
to repeated handle attachment.

This suggests a sharper replacement for part of `0034`:

\[
\text{construction spectrum}
\quad\rightsquigarrow\quad
\operatorname{Spec}^{\dagger}(H_{g,h}),
\]

provided that a checked program construction supplies:

1. a state carrier for cut cycles;
2. typed split and merge maps;
3. a pairing making them appropriately dual;
4. a certified endomorphism after recombination; and
5. retained source, occurrence, frame, and surgery residuals.

The operator is no longer chosen by closing an arbitrary edge relation. It is
forced, if it exists at all, by a fork--recombine construction.

### 1.4 The exact-triangle reading comes after the cobordism

Suppose a future trace construction produces a cellular cobordism
`W_(U,V)` from an incoming cut cycle `Gamma_U` to an outgoing cut cycle
`Gamma_V`. The boundary inclusion gives a chain map

\[
C_\bullet(\Gamma_U)
\longrightarrow
C_\bullet(W_{U,V}).
\]

Its cofiber is represented by relative chains, leading to a distinguished
triangle

\[
C_\bullet(\Gamma_U)
\longrightarrow
C_\bullet(W_{U,V})
\longrightarrow
C_\bullet(W_{U,V},\Gamma_U)
\longrightarrow
C_\bullet(\Gamma_U)[1].
\]

The third term records what the process constructs relative to its incoming
boundary. This is the first precise candidate for the principle that the
third vertex is generated by the opposite-edge morphism.

The shift is not cosmetic. It records homological degree and sign data that
the current mod-two cycle model erases; an actual orientation still requires
an integer-chain lift.

### 1.5 Where the elliptic function could enter

There are two distinct elliptic routes, and they must not be conflated.

The first is topological:

\[
\text{copants}\circ\text{pants}
\longrightarrow
\text{one handle}.
\]

The second is complex and symplectic. On a symplectic two-torus, rational
slopes `(p,q)` define Lagrangian circles, their intersections generate
Fukaya morphisms, and holomorphic triangles define composition. Under
elliptic-curve mirror symmetry, theta functions appear in those composition
laws.

The proposed bridge is therefore not

\[
\text{handle}=\text{elliptic curve}.
\]

It is a research route:

\[
\text{program handle trace}
\longrightarrow
\text{oriented genus-one carrier}
\longrightarrow
\text{period or slope data}
\longrightarrow
\text{elliptic/Fukaya composition}.
\]

Every arrow requires a construction or an obstruction.

## 2. Evidence

### 2.1 The repository already has the required fork--recombine carrier

The fixture used from `0020` through `0032` is one checked DAG with operation
sequence

```text
copy -> {neg, id} -> add.
```

Rust supplies exact causal cuts, enabled events, slices, original wire IDs,
sources, occurrences, lineage, and nested graft-frame intersections. The two
legal schedules

```text
neg, id, add
id, neg, add
```

remain distinct histories but reach the same final checked cut. The
independent branch events commute only under the declared interchange law;
their identities are never collapsed.

This is precisely the finite process shape needed for a decorated handle
candidate:

\[
1\xrightarrow{\mathrm{copy}}2
\xrightarrow{\mathrm{neg}\otimes\mathrm{id}}2
\xrightarrow{\mathrm{add}}1.
\]

It is not yet a cobordism or a Frobenius-algebra action. The evidence is that
the arity, causal order, branch independence, and recombination pattern are
already exact program data.

### 2.2 A new bounded face-chain consequence

On the declared planar cellular dual in
[`0020-e0-dual-cut-surgery.md`](0020-e0-dual-cut-surgery.md), every checked
past `U` has a mod-two dual-cut cycle `gamma_U`. For every enabled event `e`,
the checked step law is

\[
\gamma_{U\cup\{e\}}
=
\gamma_U+\partial f_e^\vee
\qquad\text{over }\mathbf F_2,
\]

where `f_e^vee` is the dual event face.

For nested causal pasts \(U\subseteq V\), define the static event-face chain

\[
F_{U,V}
=
\sum_{e\in V\setminus U}f_e^\vee.
\]

Choose any legal schedule from `U` to `V` and sum the checked one-step laws.
Every intermediate cut appears twice and cancels. Therefore

\[
\boxed{
\partial F_{U,V}=\gamma_U+\gamma_V
}
\qquad\text{over }\mathbf F_2.
\]

The result is independent of the chosen linear schedule because the face
chain is indexed by the exact event set \(V\setminus U\), not by a word order.

For \(U\subseteq V\subseteq W\), exact event partition gives

\[
\boxed{
F_{U,W}=F_{U,V}+F_{V,W}
}.
\]

Thus the existing local face-surgery equation already integrates to a bounded
relative-chain law compatible with exact adjacent-slice composition.

This is a mathematical consequence of the existing finite evidence, not a
new stable repository claim. It holds on the declared cellular fixture over
`F_2`.

### 2.3 Why the static face chain is not yet the process

The face chain forgets at least three kinds of data.

First, it forgets causal order among dependent events. `F_(U,V)` is a sum,
while the program retains a partial order and possibly several legal linear
histories.

Second, it does not by itself create identity cylinders for through-wires.
The exact `ProgramSlice` model deliberately retains wires present unchanged
at both boundaries. A true trace cobordism must thicken each such wire through
time rather than cancel its two appearances in a static mod-two equation.

Third, overlapping graft frames decorate one original event face; they do
not create several copies of it. The trace must retain the exact frame stack,
region role, source, occurrence, and lineage on each elementary piece.

The correct future carrier is therefore closer to

\[
\mathcal W_{U,V}
=
(F_{U,V},\text{causal poset},\text{through cylinders},
  \text{graft decorations},\text{interchange cells})
\]

than to the bare chain `F_(U,V)`.

### 2.4 Existing no-go results demand a decorated cobordism

The constant--discard fixture in `0020` has equal initial and terminal bare
dual-cycle support while retaining a nonempty internal history. Hence

\[
\gamma_U=\gamma_V
\centernot\Longrightarrow
\mathcal W_{U,V}=\text{identity cylinder}.
\]

The surreal objectification result in
[`0021-surreal-cut-objectification-no-go.md`](0021-surreal-cut-objectification-no-go.md)
proves the parallel intensional obstruction: distinct decorated cut forms can
objectify to the same number, and objectification does not commute with
ordinary positive scaling.

Consequently neither endpoint cycles, homology classes, scalar values, nor
surreal numbers can replace the decorated trace. Any TQFT-like state shadow
must be accompanied by a residual that preserves the process information
forgotten by the shadow.

### 2.5 Nested frame gluing already matches one cobordism requirement

In
[`0031-e0-nested-decorated-surgery-psp.md`](0031-e0-nested-decorated-surgery-psp.md),
the parent and child graft frames overlap on the same body events. The checked
construction attaches all intersecting frame roles to one NodeId-indexed face
surgery and never executes an event twice.

Adjacent program slices compose to the direct outer slice, and the matching
decorated surgery subwords reach the same final dual state. This supplies a
finite form of the gluing principle:

\[
\text{compose adjacent time intervals}
\quad\leftrightarrow\quad
\text{glue their decorated surgery traces}.
\]

A genuine cobordism functor would require this law for a declared category of
boundaries and traces. The repository currently establishes it only for the
bounded same-diagram fixture.

### 2.6 Two-dimensional TQFT supplies the external handle law

An oriented two-dimensional TQFT assigns a state space `A` to the circle and
linear maps to oriented surface cobordisms. The pants and copants give
multiplication and comultiplication

\[
\mu:A\otimes A\to A,
\qquad
\Delta:A\to A\otimes A.
\]

Their composite

\[
H=\mu\circ\Delta:A\to A
\]

is the handle operator. Its value on the unit is the Euler element. In
semisimple two-dimensional TQFTs the handle operator is diagonalizable; in a
unitary theory it is Hermitian, and its eigenvalues determine the response to
repeated handle addition.

This is an exact external example in which

\[
\text{split}\longrightarrow\text{merge}
\longrightarrow\text{genus construction}
\longrightarrow\text{spectrum}.
\]

It supplies the structural meaning missing from an arbitrary operator
closure. It does not supply an Adva Frobenius algebra.

### 2.7 Elliptic Fukaya composition supplies the external triangle law

For a symplectic two-torus, objects of the relevant Fukaya category include
geodesic Lagrangian circles with rational slopes and decorations. Morphisms
are generated by their intersection points. Composition is defined by counts
of holomorphic triangles bounded by three Lagrangian circles, with higher
compositions defined by higher polygons.

Under homological mirror symmetry for elliptic curves, these products are
expressed using theta functions and related elliptic series. This supplies an
external mechanism in which

\[
(p,q)\text{ leaves}
+
\text{intersections}
+
\text{triangular composition}
\longrightarrow
\text{elliptic functions}.
\]

It is substantially closer to the originating geometric intuition than
selecting an elliptic function from periodic notation alone. The missing step
is a functor from a checked program trace or its geometric presentation to
such Lagrangian data.

### 2.8 Stable categories explain the opposite-edge third term

In a stable category, every morphism has a fiber and a cofiber, and
fiber--cofiber sequences produce distinguished triangles in the homotopy
category. This supplies a coherent form of

\[
\text{edge morphism}\longrightarrow\text{third object}.
\]

The relative-chain triangle in Section 1.4 is the elementary chain-complex
instance of this principle. It should be introduced only after the actual
incoming boundary, trace complex, and inclusion map have been constructed.
Merely drawing three semantic vertices does not create an exact triangle.

### 2.9 Executable classification-level calibration

The companion research test
[`test_decorated_handle_cobordism.py`](../../tests/python/test_decorated_handle_cobordism.py)
now performs two exact finite checks.

First, it obtains the existing four-event diamond from Rust and exhausts its
six downward-closed causal pasts, all twenty nested pairs, and all fifty
nested triples. For every pair it checks

\[
\partial F_{U,V}=\gamma_U+\gamma_V,
\]

and for every triple it checks the boundary shadow of

\[
F_{U,W}=F_{U,V}+F_{V,W}.
\]

Second, it declares one explicit minimal-saddle presentation:

- `copy` is a connected genus-zero `1 -> 2` copants;
- `neg` and `id` are separately decorated genus-zero cylinders;
- `add` is a connected genus-zero `2 -> 1` pants; and
- ordered middle circles are glued exactly, with every checked event ID used
  once.

Euler characteristic is additive under circle gluing, so the composite has

\[
\chi=-1+0+0-1=-2,
\qquad
b=2,
\]

and the orientable-surface classification equation

\[
\chi=2-2g-b
\]

gives

\[
\boxed{g=1}.
\]

The test checks this result by exact integer arithmetic, verifies both
parenthesizations of the gluing, and retains the two distinct legal event
schedules while assigning them one canonical decorated surface signature.

It also installs its own red-team witness. Replacing the declared genus-zero
copy patch by a genus-one `1 -> 2` patch preserves exactly the same event ID
and boundary arity but makes the total genus equal to two. Therefore

\[
\boxed{
\text{fork--recombine arity alone does not force a handle}.
}
\]

The genus-one result is exact conditional evidence for the explicit
minimal-saddle law, not a theorem derived from current Adva operation arities.

### 2.10 Explicit finite cellulation

The second companion test
[`test_decorated_handle_cellulation.py`](../../tests/python/test_decorated_handle_cellulation.py)
upgrades the classification record to one actual finite oriented 2-complex.
It uses only elementary quadrilateral cells:

- `copy` is a `5 x 3` rectangular grid with two open interior unit squares,
  hence a planar copants with thirteen faces;
- `neg` and `id` are separate four-band cylinders, with four faces each;
- `add` is a second thirteen-face grid pants; and
- the four declared branch port circles are glued by orientation-reversing
  vertex identifications.

After quotienting the declared ports, the complex has

\[
V=48,
\qquad
E=84,
\qquad
F=34,
\]

so

\[
\chi=V-E+F=-2.
\]

The test does not infer surfacehood from this global count. It checks that
every edge is incident to one or two faces, every interior edge receives the
two opposite face orientations, every interior vertex link is a circle, and
every boundary vertex link is an interval. It then finds exactly the two
unglued outer boundary circles and obtains

\[
g=\frac{2-b-\chi}{2}=1.
\]

The four cross-patch seams are also exact: `copy-neg`, `neg-add`, `copy-id`,
and `id-add`, each with four edges. Face decorations retain the four Rust
event identities and the causal layers `(0, 1, 1, 2)`.

The elementary pieces are now wrapped as composable cellulations with ordered
input and output circles. A research-local tensor places the two branch
cylinders side by side, while `then` performs only the declared
orientation-reversing circle identifications. The two parenthesizations

\[
(\mathrm{copy}\mathbin{;}\mathrm{branches})\mathbin{;}\mathrm{add}
\qquad\text{and}\qquad
\mathrm{copy}\mathbin{;}(\mathrm{branches}\mathbin{;}\mathrm{add})
\]

produce the same canonical oriented cells, event patches, and external ports.
Thus associativity now holds at the finite cellulation level, not only in the
surface-classification shadow.

This proves existence of one finite manifold cellulation for the declared
minimal patches. It still does not prove that current program semantics
canonically selects those patches, or that arbitrary slices admit compatible
cellulations.

## 3. Conservative and safe conclusion

### 3.1 What advanced exactly

The following bounded conclusions are currently justified.

1. The checked Adva fixture has exact fork--parallel--recombine structure with
   one input, two ordered branch occurrences, and one output.
2. Its existing mod-two face-surgery law integrates to
   \(\partial F_{U,V}=\gamma_U+\gamma_V\) on the declared cellular dual.
3. The face chains add under nested intervals exactly as program event sets
   compose.
4. The classification test exhaustively checks the interval face-chain law
   and computes genus one for the declared minimal-saddle trace.
5. A finite quadrilateral cellulation now realizes that full trace with
   exact program seams, two boundary circles, local manifold links, and genus
   one.
6. The hidden-handle witness proves that event arity does not select this
   minimal cellulation.
7. The repository retains further causal and graft decorations needed to
   extend the cellulation from the full fixture to arbitrary slices.
8. In established 2D TQFT, copants followed by pants gives the handle
   operator `mu o Delta`, and the spectrum of that operator has genuine genus
   meaning.
9. Therefore a decorated handle operator is a disciplined candidate for the
   construction spectrum of this fixture.
10. No canonical program-to-cellulation functor, Adva Frobenius algebra, TQFT
    functor, handle operator, or elliptic-curve presentation has yet been
    constructed.

### 3.2 The minimal research object

The bounded carrier should remain research-local and typed approximately as

\[
\mathbb W_{U,V}
=
(\Gamma_U,\Gamma_V,
  \mathcal W_{U,V},
  \preceq_{U,V},
  \mathcal D_{U,V},
  \chi_{U,V}),
\]

where:

- `Gamma_U` and `Gamma_V` are separate boundary copies even if their wire
  supports agree;
- `W_(U,V)` is a finite time-thickened cellular trace;
- the partial order records causal dependency;
- `D_(U,V)` retains sources, occurrences, wire lineage, graft-frame roles,
  and event identities;
- `chi_(U,V)` records orientation and the comparison with the current
  mod-two face-chain shadow.

The existing `ProgramSlice` remains semantic authority. `W_(U,V)` is a
research presentation derived from one validated slice and must never create
program identity.

### 3.3 Two exact calibration levels and the remaining obligation

The classification-level calibration passes under the explicit law that each
split or merge contributes the connected genus-zero surface of minimal
topology. The cellulation-level calibration now also passes for one standard
presentation of the complete four-event diamond. It establishes an actual
finite oriented surface rather than only compatible classification data. Its
three declared causal layers also compose associatively as exact cellulations.

The remaining obligation is no longer bare existence. It is canonicity and
composition:

1. derive the elementary patches from a free or universal program-trace
   construction rather than selecting them by hand;
2. generate separate boundary copies for every checked interval `(U,V)`;
3. thicken all interval through-wires into exact identity strips;
4. extend the established three-layer associativity to every adjacent causal
   interval without duplicating events or overlapping graft frames;
5. realize the two legal branch schedules through one explicit interchange
   cell while retaining them as distinct histories;
6. map the oriented cellulation back to the static face chain `F_(U,V)` and
   prove that the mod-two equation is its shadow; and
7. isolate a no-hidden-genus principle or exhibit the program datum that
   measures otherwise invisible handles.

This is sharper than introducing a general derived or Fukaya ontology: it
asks whether program semantics determines the topology already observed in
the bounded witness.

### 3.4 Only then ask for the handle operator

If the topological calibration passes, the next question is whether a finite
state assignment can be made functorial:

\[
Z(\Gamma) = A_\Gamma,
\qquad
Z(\mathcal W_{U,V}):A_{\Gamma_U}\to A_{\Gamma_V}.
\]

For the diamond this would produce a candidate

\[
H_{\mathrm{neg},\mathrm{id}}
=
\mu\circ(N\otimes I)\circ\Delta.
\]

Before taking a spectrum, the calibration must state:

- the coefficient field or exact ring;
- the finite state carrier;
- whether `Delta` and `mu` are program maps, relations, chain maps, or only
  geometric presentations;
- the pairing or adjunction that relates them;
- the role of `neg` and `id` as branch defects;
- the complete residual back to checked program data; and
- the sense in which repeated application represents repeated construction.

If these data do not arise naturally, the handle-spectrum proposal should be
rejected rather than normalized into existence.

### 3.5 Relationship to birthday, covering, and Omega

Repeated handles give powers

\[
H^n.
\]

This makes handle count a plausible construction grade. It does not prove

\[
n=\text{birthday}=\text{covering degree}.
\]

That identification requires a separate comparison between program graft
depth, exact covering data, and cobordism composition. Likewise an Omega-type
boundary might eventually appear in a weighted generating function over
finite constructions, but it is not supplied by the handle operator alone.

The safe dependency order is

\[
\text{decorated trace}
\to
\text{handle endomorphism}
\to
\text{construction grading}
\to
\text{weighted completion}
\to
\text{Omega comparison}.
\]

### 3.6 Relationship to the three cusp semantics

The present result does not identify the three cusps with time, space, and
construction. It supplies a possible symmetry-breaking mechanism:

- choosing incoming and outgoing boundaries selects a causal orientation;
- an instantaneous boundary cycle supplies the spatial role;
- pants/copants composition supplies the construction role.

Only after this role assignment is functorial under chart changes should it
be compared with the three ends of
\(\mathbf P^1\setminus\{0,1,\infty\}\) and the three mod-two slope classes.

## 4. Red-team opinion

### 4.1 A mod-two face chain is not a surface

The current dual object is a graph with mod-two cycles and event-face
boundaries. A sum of faces may be nonmanifold, may repeat an edge in a way
that cancels algebraically, and may have no oriented smoothing. The equation

\[
\partial F_{U,V}=\gamma_U+\gamma_V
\]

is a chain identity, not a proof of a cobordism.

One declared full-diamond cellulation has now been built and all of its vertex
links are checked locally. This removes the bare existence objection on that
presentation. It does not identify the cellulation with the earlier mod-two
dual face chain, prove compatibility for every interval, or establish that
the chosen smoothing is canonical.

### 4.2 Program copy and addition are not yet Frobenius operations

The arities match comultiplication and multiplication, but arity does not
imply Frobenius compatibility. A Frobenius algebra requires associativity,
coassociativity, units, counits, a nondegenerate pairing, and compatibility
laws. Adva `copy` preserves occurrence distinction, while ordinary algebraic
diagonals often erase exactly the intensional data Adva protects.

The first useful outcome may be a decorated or noncommutative variant, a
relation, or a no-go theorem rather than a Frobenius algebra.

### 4.3 The branch operations create defects

`neg` and `id` are not topologically invisible. Treating them as two plain
cylinders would erase the arithmetic difference between the branches. A more
accurate model may require defect lines, labelled cobordisms, open--closed
TQFT, or a category-valued state assignment.

The undecorated handle `mu o Delta` is therefore only the base topology. The
program candidate is \(\mu\circ(N\otimes I)\circ\Delta\) with a provenance
residual.

### 4.4 A topological handle is not a complex elliptic curve

A genus-one oriented surface does not by itself carry a complex modulus,
period lattice, algebraic equation, or elliptic function. Moving from the
topological handle to an elliptic curve requires additional conformal,
symplectic, or complex data.

The handle observation explains why an elliptic direction is plausible. It
does not select `tau`, `lambda`, `wp`, theta functions, or a compactification.

### 4.5 The two pair-of-pants appearances may be unrelated

There are currently two pair-of-pants objects:

1. the modular base
   \(Y(2)=\mathbf P^1\setminus\{0,1,\infty\}\);
2. the proposed local split/merge cobordisms in a program trace.

Their common topology is suggestive but does not identify them. A valid bridge
must map program boundary data to modular or Lagrangian boundary data and
intertwine gluing.

### 4.6 Spectrum requires a state functor

The topological trace alone has no ordinary operator spectrum. A spectrum
appears only after a functor assigns an exact module, vector space, chain
complex, or other endomorphism carrier to the boundary cycle.

Different state functors can produce different spectra. The theory must show
why one is selected by program semantics rather than by analyst preference.

### 4.7 Linearization may repeat the objectification error

Passing from a decorated program trace to a finite vector space may identify
distinct histories, frames, or source occurrences. The no-go in `0021`
applies in spirit: a quotient shadow cannot support exact reconstruction
without a residual.

No eigenvalue equality may authorize program identity, contraction, an
equation cell, or memoization.

### 4.8 Exact triangles do not automatically name the vertices

A cofiber triangle can formalize how a third object is generated from a
morphism. It does not prove that the three terms are time, space, and
construction. Those meanings must still be inferred from variance under
causal composition, cutting, and graft refinement.

### 4.9 Fukaya and theta-function evidence remains external

Rational-slope Lagrangians, holomorphic triangle counts, and theta functions
belong to a symplectic torus with analytic data. The current E0 route is an
exact rational routing of one program graph and explicitly fails to preserve
generic negation and binary addition as E0 valuations.

No Fukaya product should be claimed until a valuation- or incidence-faithful
geometric carrier is constructed.

### 4.10 Omega remains beyond the present bridge

Neither a handle operator nor a genus expansion produces Chaitin Omega.
Machine-dependent prefix-free halting mass requires effective enumeration,
measure, and a non-effective completion boundary. Those ingredients are not
part of ordinary finite 2D TQFT.

At most, the handle construction supplies a possible grading on which a later
weighted completion could be tested.

### 4.11 Falsification criteria

The decorated-handle proposal should be weakened or rejected if any of the
following occurs on the minimal fixture:

1. the finite cellulation cannot be extended from the full diamond to all
   certified intervals with compatible boundaries;
2. copy and add patches cannot be glued without identifying distinct
   occurrences or adding untracked data;
3. the two legal branch schedules yield non-equivalent decorated traces after
   the certified interchange square;
4. adjacent trace gluing disagrees with exact `ProgramSlice` composition;
5. the alleged genus depends on arbitrary drawing choices;
6. no natural state carrier makes split--merge an endomorphism;
7. every possible spectrum is dominated by an arbitrary quotient or pairing;
8. the oriented lift conflicts with the exact E0 and causal incidences; or
9. the construction loses the constant--discard history or overlapping graft
   decorations.

The most valuable negative result would identify the earliest failed arrow:

\[
\text{cut surgery}
\longrightarrow
\text{trace cobordism}
\longrightarrow
\text{state functor}
\longrightarrow
\text{handle operator}
\longrightarrow
\text{construction spectrum}.
\]

## Working summary

The strongest current direction is

\[
\boxed{
\texttt{copy}
\to
\{\texttt{neg},\texttt{id}\}
\to
\texttt{add}
\quad\leadsto\quad
H_{\mathrm{neg},\mathrm{id}}
=
\mu\circ(\mathrm{neg}\otimes\mathrm{id})\circ\Delta.
}
\]

The left side is checked finite program structure. The right side is a
research target motivated by pair-of-pants gluing. One explicit finite
cellulation now witnesses the topological handle for the complete diamond.
Between that witness and an intrinsic program handle lies the next exact
obligation: construct the trace functorially for every checked interval,
preserve every event, through-wire, source, occurrence, lineage, and graft
role, and prove a no-hidden-genus principle.

If that obligation passes, the construction-spectrum question becomes
sharply posed. If it fails, the obstruction will locate the exact point at
which topological field-theory language ceases to respect program semantics.

## Selected references

- O. Dumitrescu and M. Mulase, "Edge Contraction on Dual Ribbon Graphs and
  2D TQFT," <https://arxiv.org/abs/1508.05922>.
- J. Couch, Y. Fan, and S. Shashi, "Circuit Complexity in Topological Quantum
  Field Theory," <https://arxiv.org/abs/2108.13427>.
- J. Lurie, "Stable Infinity Categories,"
  <https://arxiv.org/abs/math/0608228>.
- A. Polishchuk and E. Zaslow, "Categorical Mirror Symmetry: The Elliptic
  Curve," <https://arxiv.org/abs/math/9801119>.
- A. Polishchuk, "Massey and Fukaya Products on Elliptic Curves,"
  <https://arxiv.org/abs/math/9803017>.
- D. Nadler, "Wrapped Microlocal Sheaves on Pairs of Pants,"
  <https://arxiv.org/abs/1604.00114>.
- A. Polishchuk and A. Vaintrob, "Matrix Factorizations and Singularity
  Categories for Stacks," <https://arxiv.org/abs/1011.4544>.
