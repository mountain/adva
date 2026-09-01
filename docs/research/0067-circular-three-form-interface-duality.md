# Circular Three-Form Interface Duality

Status: bounded proposal with a pure-Python finite calibration following
[`0047-a1-nodal-through-crossing-geometry.md`](0047-a1-nodal-through-crossing-geometry.md),
[`0048-cellular-annulus-nodal-torus-dehn-twist.md`](0048-cellular-annulus-nodal-torus-dehn-twist.md),
[`0057-typed-vacua-constant-boundary-braids.md`](0057-typed-vacua-constant-boundary-braids.md),
[`0059-tri-bracket-eigen-normalization-logic.md`](0059-tri-bracket-eigen-normalization-logic.md),
[`0061-lineage-aware-bracket-events.md`](0061-lineage-aware-bracket-events.md),
and the corrected reverse-dual calculus in
[`0066-self-dual-characteristic-completion-calculus.md`](0066-self-dual-characteristic-completion-calculus.md).

The executable V0 fixture is
[`test_circular_three_form_interface_duality.py`][fixture].

[fixture]: ../../tests/python/test_circular_three_form_interface_duality.py

This note records one geometric proposal:

> The fixed display `{}[]()` may be read as a cut presentation of three typed
> boundary pairs on an oriented circle.  Each pair has two complementary arc
> readings.  One reading contains no other typed marks and presents a typed
> vacuum.  The other contains the two opposite typed pairs and presents a
> finite-observer-relative universal context.  Reversing this polarization is
> involutive, but it reverses process arrows.

The strongest new observation is not merely that every bracket has an inside
and an outside.  The three outside readings overlap.  Their intersection
nerve is exactly the boundary of a triangle.  Thus the first finite form of
"universality" is not one total object placed inside a finite observer.  It
is a three-chart cover together with overlap obligations.

This remains a proposal and a finite incidence calibration.  It is not a
complete logic, a descent theorem, a universal machine, a proof of absolute
finite representability, or a new Rust semantic identity.

---

## 0. Executive result

Fix the three domain colors

\[
\mathcal D=\{K,X,t\}
\]

and an oriented circle with six marked endpoints in cyclic order

\[
K^-\;K^+\;X^-\;X^+\;t^-\;t^+.
\]

For each domain \(D\), its two endpoints cut the circle into two open arcs:

\[
a_D^0,
\qquad
a_D^{\Omega_Q}.
\]

The first contains no other marked endpoint.  The complementary arc contains
the two opposite typed boundary pairs.  The finite readings are

\[
0_D=\operatorname{Read}(a_D^0),
\qquad
\Omega_{Q,D}=\operatorname{Read}(a_D^{\Omega_Q}).
\]

Here \(Q\) names the finite observer and its versioned policy.  The notation
does not assert an observer-independent global \(\Omega\).

The opposite-pair vocabulary is recovered exactly:

| boundary | vacuum-side content | universal-side content |
|---|---|---|
| \(K\) | \(0_K\) | \(\Omega_{Q,K}\sim X\otimes t\) |
| \(X\) | \(0_X\) | \(\Omega_{Q,X}\sim t\otimes K\) |
| \(t\) | \(0_t\) | \(\Omega_{Q,t}\sim K\otimes X\) |

The tensor glyph in this table is only the established opposite-pair reading.
It does not promote the current frontier types to an implemented tensor
product.

The public string is a cut presentation:

\[
\operatorname{Cut}_b(S^1_3)\in
\{\;{}[](),\;[](){},\;(){}[]\;\}.
\]

A choice of basepoint \(b\) selects which cyclic presentation is printed.
The circle has no distinguished first bracket before this calibration.

---

## 1. Why the circle is more than a drawing

On a line, `{}[]()` encourages three independent readings:

```text
{}    []    ()
```

The circular presentation adds two structures that the line hides:

1. every typed pair determines two complementary arcs; and
2. no typed pair is globally first.

The first makes vacuum and universal-context readings two polarizations of one
boundary.  The second turns startup ordering into an explicit cut choice.

An abstract circle does not possess a planar inside and outside.  Therefore
the primitive data must not be described as an intrinsic inside/outside
partition.  V0 retains:

\[
\mathsf{Circular3}_Q
=
\left(
S^1,
(\partial_D^-,\partial_D^+)_{D\in\mathcal D},
\nu,
b,
Q,
R
\right),
\]

where \(\nu\) is a coorientation or selected-side convention, \(b\) is an
optional linearizing cut, and \(R\) is residual evidence.  "Inside" and
"outside" are convenient names only after \(\nu\) is selected.

The boundary endpoints themselves are not contents of either open arc.  This
is why the universal-side content for \(D\) is the opposite pair rather than
all three domains.

---

## 2. The missing gluing datum: a circular cover nerve

Let

\[
U_D=\mathcal D\setminus\{D\}.
\]

Then

\[
U_K=\{X,t\},
\qquad
U_X=\{t,K\},
\qquad
U_t=\{K,X\}.
\]

These outside readings are not three disjoint containers.  They satisfy

\[
U_K\cap U_X=\{t\},
\qquad
U_X\cap U_t=\{K\},
\qquad
U_t\cap U_K=\{X\},
\]

while

\[
U_K\cap U_X\cap U_t=\varnothing.
\]

Therefore their nerve has three vertices, three edges, and no filled
two-simplex.  Its Euler characteristic is

\[
\chi=3-3=0,
\]

so the nerve is the boundary of the two-simplex:

\[
\boxed{N(\{U_K,U_X,U_t\})\cong \partial\Delta^2\simeq S^1.}
\]

This is the first precise answer to the finite-representation problem in this
line of work.  A finite observer need not contain one completed totality.
It can retain:

1. three typed local universal readings;
2. their three pairwise overlaps;
3. transition or comparison evidence on those overlaps; and
4. a coherence obligation around the cycle.

V0 establishes only the incidence nerve.  It does not yet supply transition
maps, a Cech cocycle, effective descent, or a theorem that compatible local
readings glue to a unique global interpretation.  That missing coherence is
now sharply located rather than hidden inside the word "universal".

---

## 3. Polarization and contravariant reversal

Write one polarized boundary as

\[
B_D=(\partial_D,a_D^{\mathrm{sel}},a_D^{\mathrm{comp}},\nu_D).
\]

Define the side reversal

\[
B_D^\star
=
(\partial_D,a_D^{\mathrm{comp}},a_D^{\mathrm{sel}},-\nu_D).
\]

Then

\[
\boxed{(B_D^\star)^\star=B_D.}
\]

It is tempting but wrong to apply this only to states and leave arrows in the
same direction.  The corrected 0066 discipline requires

\[
\boxed{
(f:c\longrightarrow c')^\star:
(c')^\star\longrightarrow c^\star.
}
\]

Consequently a proof-side normalization sink does not dualize to a
learning-side forward normal form.  If

\[
c\longrightarrow_P 0_D
\]

is a local proof-oriented normalization, its candidate dual has the
generative orientation

\[
\Omega_{Q,D}\longrightarrow_L c^\star.
\]

An operational learner beginning with observations must search against this
generative arrow to infer a source or characteristic.  The circular picture
therefore supports the reverse-dual proposal without restoring the rejected
forward `NF/NF` equation.

The V0 typed node is chosen self-dual only as a minimal finite fixture.  This
is not a claim that every singular object in the future calculus is
self-dual.

---

## 4. Cutting the circle and startup calibration

There are three cuts that preserve every adjacent typed pair.  They yield the
three cyclic rotations

```text
{}[]()
[](){}
(){}[]
```

Selecting `{}[]()` therefore consists of at least:

1. choosing an orientation;
2. choosing a basepoint before the `K` pair; and
3. naming the three colors and their printed glyphs.

This is a finite version of startup calibration.  It removes an ambiguity in
presentation; it does not remove process history.  A cut through one member
of a bracket pair produces a half-pair linear word and is deliberately
`NotRepresentable` in the simple juxtaposed grammar.

Changing the cut merely gives a cyclic coordinate change at this level.  A
nontrivial lifted history or holonomy requires extra path, braid, cellular, or
cocycle data.  It cannot be inferred from the three printed rotations alone.

---

## 5. Collision at a typed singularity

Let the two endpoints of \(\partial_D\) approach one another.  The empty arc
collapses, while the complementary reading approaches the circle with one
typed node.  The public specialization is

\[
q_D:B_D\longrightarrow N_D.
\]

Both polarizations may have the same public image:

\[
q_D(B_D)=q_D(B_D^\star)=N_D.
\]

This equality is precisely why specialization is lossy.  A valid event must
retain a residual such as

\[
R_D=(\text{paired endpoints},\text{cyclic position},\nu_D,Q,\nu_Q).
\]

Without the residual, the node does not determine which side was selected or
which marked resolution produced it.  This is geometric support for the
existing separation among:

- `MayHide`: exact evidence remains in a retained fibre;
- `MayAbstract@S`: a declared stable face is projected;
- `MayForget@Q`: the discarded distinction is proved irrelevant to the
  declared observer questions; and
- `MayErase`: an irreversible authority not supplied by the present system.

`ProvenanceHide` is therefore specialization-like only when its exact fibre,
policy, artifact, and snapshot remain available.  It is not a unique inverse
pair with an unrestricted `Reveal` operation.

---

## 6. Through is a relation, not an automatic inverse

The earlier nodal programme distinguishes three operations:

\[
\text{around},
\qquad
\text{specialize},
\qquad
\text{through}.
\]

The circular boundary proposal inherits the same distinction.

### Around

Move the marked endpoints without collision.  The carrier stays smooth and
transport is invertible.  A lifted path may retain winding or holonomy even
when the printed boundary order returns.

### Specialize

Collide a typed pair.  The result is a quotient into \(N_D\); polarization,
matching, or phase may be lost from the public image and must enter a
residual.

### Through

Re-open the node on the other side.  Before a marking is selected, the honest
object is the cospan

\[
F_-\xrightarrow{q_-}N_D\xleftarrow{q_+}F_+
\]

or its fibre-product relation

\[
F_-\times_{N_D}F_+.
\]

It is functional away from the node and generally multi-valued over the
collapsed fibre.  A marked phase selects one deterministic resolution
\(P^k\) inside this relation.  Two choices differ by around transport:

\[
\boxed{(P^\ell)^{-1}P^k=T_D^{k-\ell}.}
\]

Thus side reversal does not grant permission to reconstruct hidden detail.
Recovery remains relation-valued until a witness chooses a resolution.

---

## 7. A finite three-form record

The candidate finite expression is not the bare six-character string.  It is
the typed record

\[
\mathfrak F_Q=
\left(
S^1_3,
(B_D)_{D\in\mathcal D},
(U_D)_{D\in\mathcal D},
(U_D\cap U_E)_{D\ne E},
\nu,
b,
Q,
R
\right).
\]

Its roles are separated as follows:

| field | role | what it does not claim |
|---|---|---|
| \(S^1_3\) | cyclic carrier with six typed marks | world topology |
| \(B_D\) | one polarized typed boundary | intrinsic planar inside/outside |
| \(U_D\) | opposite-pair universal reading | absolute totality |
| overlaps | comparison loci among local readings | completed descent |
| \(\nu,b\) | orientation and linearization calibration | process holonomy |
| \(Q\) | finite observer and policy version | observer independence |
| \(R\) | hidden pairing, phase, provenance, or open obligations | permission to erase |

Relative to a declared finite question family, this record may eventually be
called \(Q\)-complete when every permitted observation factors through it
with a certificate.  It must not be called absolutely complete in an open
world.

---

## 8. What V0 checks

The pure-Python fixture exhaustively checks the finite carrier:

1. every typed short arc is empty of other marks;
2. every complementary arc contains exactly the two opposite typed pairs;
3. the outside cover has three vertices, three edges, no two-simplex, and
   Euler characteristic zero;
4. side reversal swaps selected and complementary arcs, reverses
   coorientation, preserves types, and squares to the identity;
5. arrow reversal is contravariant and rejects the same-direction reading;
6. the three admissible cuts are exactly the cyclic linearizations, while
   half-pair cuts are not representable;
7. specialization identifies opposite polarizations only at the public typed
   node while retaining distinct residuals;
8. the finite through cospan is functional off the node and relational over
   the collapsed phase fibre; and
9. the difference of marked through-resolutions is the finite around
   rotation.

The fixture is an independent incidence and quotient oracle.  It constructs
no Adva source, occurrence, history, diagram, observer, certificate, or
semantic identity.  Rust remains authoritative for those objects.

---

## 9. Falsifiers and nonclaims

The proposal must be revised if any intended extension requires:

1. an intrinsic inside/outside on an uncooriented abstract circle;
2. treating the three outside readings as disjoint;
3. a canonical first bracket without a cut or calibration;
4. recovering a unique smoothing from an unmarked singular node;
5. applying \((-)^\star\) covariantly to process arrows;
6. calling a local \(\Omega_{Q,D}\) an observer-independent totality; or
7. erasing residual evidence merely because the public boundary is flat.

This note does not establish:

- a Cech, sheaf, stack, or descent semantics;
- a global object \(\Omega\), a Chaitin-`Omega` relation, or absolute
  universality;
- a complete logic or proof system on the circular form;
- that proof truth and learning novelty are identical readouts;
- a stable bracket, node, cospan, polarity, or circular-boundary API;
- a Rust-checked circular diagram or signed history;
- that a coordinate cut accounts for braid or Dehn-twist holonomy;
- a universal normalization machine; or
- permission to change the active exact `ProgramSlice` implementation
  priority.

---

## 10. Next local gate

The next experiment should add overlap transport, not another global symbol.
For each nonempty intersection \(U_D\cap U_E\), define a typed comparison map

\[
g_{DE}:\mathcal V_D|_{U_D\cap U_E}
\longrightarrow
\mathcal V_E|_{U_D\cap U_E}.
\]

Then test three increasingly strong possibilities:

1. the comparisons agree on directly shared checked evidence;
2. their cyclic composite retains a measurable residual or holonomy; and
3. a declared zero-holonomy certificate is sufficient for one bounded gluing
   result.

The likely trichotomy is:

\[
\boxed{
\text{compatible and glueable},
\quad
\text{compatible with residual holonomy},
\quad
\text{not representable under }Q.
}
\]

This would connect the circular nerve to the existing signed-history,
specialization, and reverse-dual logical lines without prematurely promoting
sheaf language into stable semantics.

---

## Conservative conclusion

The user's circular reading survives the first red-team pass in a precise
form:

\[
\boxed{
\text{typed vacuum}
\quad\stackrel{\star}{\longleftrightarrow}\quad
\text{opposite-pair universal context}
}
\]

on each boundary, with arrows reversed under \(\star\).  More importantly,
the three universal contexts form a circular overlap nerve:

\[
\boxed{
N(\{U_K,U_X,U_t\})\simeq S^1.
}
\]

This locates the missing component of finite representation.  The six glyphs
supply local typed boundaries; completeness, if attainable relative to a
finite observer, must come from overlap comparison and coherence.  At a
singularity, specialization forgets a marked distinction, while through
retains the complete relation of possible resolutions.  The finite form is
therefore not a closed totality but a compact interface for an open,
residual-bearing interpretation.
