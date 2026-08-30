# Exact E0 Möbius–Cellular Edge Bridge

Status: bounded finite construction replacing the arbitrary projective labels
of the preceding calibration by exact rational points of the standard E0
upper-half-plane grid. It proves an edge-level bridge between the Möbius image
of that grid and the declared cellular dual of one checked causal diamond. It
does not prove that the two cell complexes are isomorphic.

## Source convention

This note follows the current Paper 0 convention:

\[
\mathfrak E_0=\{(x,y)\in\mathbb R^2:y>0\},\qquad
a(x,y)=-\frac{x}{y},
\]

with grid moves

\[
X_s(x,y)=(x-sy,y),\qquad
Y_k(x,y)=\left(x,\frac yk\right).
\]

Then (a\circ X_s=a+s), (a\circ Y_k=ka), and for (m\geq2),

\[
Y_m^{-1}X_s^mY_m=X_s.
\]

These are the definitions in
[`aeg-paper/paper-0/sections/03-paths.tex`](https://github.com/mountain/aeg-paper/blob/main/paper-0/sections/03-paths.tex).
Older `aeg-invitation` material uses a different E0/E1 naming convention. The
construction below is tied to the current Paper 0 notation, not to the older
label.

## Exact finite grid window

The checked program is the existing copy–branch–recombine diamond

```text
copy -> {neg, id} -> add.
```

It has the following exact **routing embedding** using only (X=X_1) and
(Y=Y_2):

| Routed program point | E0 coordinate | grid assignment (a=-x/y) |
|---|---:|---:|
| input | ((0,2)) | (0) |
| copy | ((0,1)) | (0) |
| neg | ((-1,1)) | (1) |
| id | ((0,1/2)) | (0) |
| branch midpoint | ((-1/2,1/2)) | (1) |
| add | ((-1,1/2)) | (2) |
| output | ((-1,1/4)) | (4) |

The six checked wires are routed by the words

| Wire | Grid word |
|---|---|
| input to copy | (Y) |
| copy to neg | (X) |
| copy to id | (Y) |
| neg to add | (Y) |
| id to add | (XX) |
| add to output | (Y) |

The inner cell has boundary

\[
(0,1)\xrightarrow{Y}(0,1/2)
\xrightarrow{X}(-1/2,1/2)
\xrightarrow{X}(-1,1/2)
\xrightarrow{Y^{-1}}(-1,1)
\xrightarrow{X^{-1}}(0,1).
\]

Thus its two paths from copy to neg verify exactly

\[
Y^{-1}X^2Y=X,
\]

the elementary (BS(2,1)) relation. No numerical tolerance or inferred
geometry is used.

## The second standard grid

Let

\[
J(z)=-\frac1z,
\qquad
J(x,y)=\left(
  -\frac{x}{x^2+y^2},
  \frac{y}{x^2+y^2}
\right).
\]

Applying (J) pointwise gives the second exact grid (J(G)). Its edges are
curved, not arbitrary labels:

- a horizontal line (y=c) becomes the circle
  \[
  u^2+\left(v-\frac1{2c}\right)^2=\frac1{4c^2},
  \]
  tangent to the real axis at (0);
- a vertical line (x=d\neq0) becomes the circle
  \[
  \left(u+\frac1{2d}\right)^2+v^2=\frac1{4d^2},
  \]
  whose center is on the real axis;
- the vertical line (x=0) is preserved.

The distinction between the two circle families matters: the first family is
a horocycle family tangent at (0), while the second is a geodesic-circle
family orthogonal to the real axis.

The assignment changes polarity:

\[
a(Jp)=-a(p).
\]

If (X^\vee=JXJ), (Y^\vee=JYJ), and
(B=(Y^\vee)^{-1}), conjugating the preceding relation gives

\[
B^{-1}X^\vee B=(X^\vee)^2.
\]

This is the exact (BS(1,2)) presentation after compensating for the reversed
scale polarity. The test checks the equality on exact rational coordinates.
The projective role of (J) is consistent with
[`aeg-paper/paper-0/sections/06-projective-unification.tex`](https://github.com/mountain/aeg-paper/blob/main/paper-0/sections/06-projective-unification.tex).

## Two meanings of “dual”

The construction now separates two objects that the preceding calibration
only placed side by side:

1. (J(G)) is the Möbius/projective image of the E0 grid;
2. (G^\dagger) is the cellular dual of the planar program embedding.

They are not identified as cell complexes. Instead the checked program-wire
set supplies a common finite index:

\[
J(G)\ \xleftarrow{\ J\circ\iota\ }\ E_{\mathrm{wire}}
\ \xrightarrow{\ \star\ }\ G^\dagger.
\]

Equivalently, on wire-indexed mod-two one-chains there is an exact partial
bridge

\[
\delta_G\bigl(J(e)\bigr)=e^\dagger.
\]

Every record retains the straight E0 path, its pointwise (J)-image, and the
two cellular-dual face vertices. A path with the right wire name but wrong
coordinates is rejected.

## Exhaustive finite law

For every downward-closed event past of the checked diamond, Rust supplies a
certified frontier (C). Its wire support maps first to the exact curved paths
in (J(G)) and then, through (delta_G), to the same mod-two cycle in
(G^\dagger).

For every enabled event (e), the program-wire star of (e) maps to the
boundary of its cellular-dual face, and the following square commutes:

\[
\delta_G\bigl(J(C\mathbin\triangle\operatorname{star}(e))\bigr)
=
\delta_G(J(C))\mathbin\triangle\partial e^\dagger.
\]

The test exhausts all certified pasts and every enabled step, rather than one
chosen schedule. Combined with the preceding nested-frame result, this gives
the intended bounded carrier

\[
P^*\longrightarrow J(G)
\mathop{\longrightarrow}^{\delta_G}G^\dagger
\mathop{\longrightarrow}^{S}G^\dagger
\longrightarrow P
\]

alongside the exact finite `P S P*` factorization already checked on this
fixture. The bridge shows that the scope/cut and grid/cellular constructions
can share wire identities. It does not yet show that the E0 assignment is the
program's variable valuation.

## The exposed obstruction

The bridge is deliberately only edge-level. This finite E0 window has seven
geometric vertices, whereas its cellular dual has two face-vertices (`outer`
and `diamond`). Therefore there is not even a vertex bijection extending the
wire correspondence on this window.

So the present result does **not** construct maps

\[
C_k(J(G))\longrightarrow C_{2-k}(G^\dagger)
\]

commuting with boundary and coboundary in every degree. It also works over
(\mathbb F_2), where orientation is forgotten, so contraction and expansion
are related by reversal but are not intrinsically distinguished by a sign.

The next essential task is now precise: either construct an oriented,
degree-reversing chain map for a suitable refinement of the two grids, or show
by a finite obstruction that no such refinement can preserve both E0
arithmetic incidence and program-cellular incidence. Extending the edge-index
span to arbitrary checked programs requires a canonical E0 routing or
planarization certificate as well.

There is a second, independent obstruction. The standard E0 point path is a
one-variable, orientation-preserving affine model: its generators act on a
value (t) as (t\mapsto t+s) and (t\mapsto kt) with (k>0). The checked
fixture contains generic negation and binary addition. In the concrete routing
above, the routed `neg` coordinate does not have assignment equal to the
negative of the routed `copy` coordinate, and the routed `add` assignment is
not the sum of its two inputs. More generally, (t+1=-t) and (2t=t) cannot
hold as identities in a free variable.

Therefore the present E0 embedding is geometric routing, not a valuation-
preserving interpretation of the multi-hole expression. A faithful general
(P^*) must add at least a multi-hole configuration carrier (for example a
fibered/product E0 state with explicit substitution maps), or prove that a
different elementary carrier represents reflection and binary grafting. This
is not repaired by improving the cellular dual alone.
