# Figure-Eight Through Characteristic: One Feature in Three Readings

Status: bounded exact research calibration following
[`0047-a1-nodal-through-crossing-geometry.md`](0047-a1-nodal-through-crossing-geometry.md),
[`0048-cellular-annulus-nodal-torus-dehn-twist.md`](0048-cellular-annulus-nodal-torus-dehn-twist.md),
[`0067-circular-three-form-interface-duality.md`](0067-circular-three-form-interface-duality.md),
and
[`0070-typed-surreal-through-forms.md`](0070-typed-surreal-through-forms.md).

The executable oracle is
[`test_figure_eight_through_characteristic.py`][fixture].  The knot word and
its affine interpretation come from the exploratory figure-eight notes in
[`aeg-paper`][aeg-note].

[fixture]: ../../tests/python/test_figure_eight_through_characteristic.py
[aeg-note]: https://github.com/mountain/aeg-paper/blob/master/notes/knots-and-loops/07-figure-eight-arithmetic-interpretation.tex
[presentation-note]: https://github.com/mountain/aeg-paper/blob/master/notes/knots-and-loops/11-figure-eight-presentation-problem-zh.tex

This note tests two proposals:

1. a through thread with enough closure data may be read as a knot; and
2. feature extraction may remove the multivaluedness of through resolutions.

The figure-eight knot $4_1$ supports a precise but narrower statement:

> A closed, oriented, based through history can have a Laurent-valued closure
> residual.  For one special presentation of $4_1$, construction history,
> spatial Alexander data, and temporal monodromy all yield the same
> characteristic, up to the declared units $\pm t^k$.

The common characteristic is

\[
\boxed{\Delta_{4_1}(t)=t^2-3t+1.}
\]

Feature extraction here does not choose one hidden thread and does not erase
all multiplicity.  It converts a family of closure conditions into a finite
Laurent presentation and retains the residual needed to audit that quotient.
This is better called **spectral organization of multivaluedness** than
unqualified forgetting.

Nothing in this note adds a stable knot, Laurent, Fox, monodromy, AEG word,
through, or feature operation.  The Rust core remains the sole semantic
authority.

---

## 0. Executive result

Use the special figure-eight relator

\[
w=\texttt{abbbaBAAB},
\]

where upper-case letters denote inverses.  The three exact readings are:

| three-form role | retained object | exact calculation |
|---|---|---|
| construction $K$ | chronological AEG word | translation defect $D_w(t)=-\Delta_{4_1}(t)$ |
| space $X$ | Alexander/Fox presentation | $\phi(\partial w/\partial b)=-\Delta_{4_1}(t)$ |
| time $t$ | fibre monodromy on $H_1$ | $\det(tI-M)=\Delta_{4_1}(t)$ |

Thus

\[
\boxed{
-D_w(t)
=
-\phi\!\left(\frac{\partial w}{\partial b}\right)
=
\det(tI-M)
=
\Delta_{4_1}(t)
}
\]

for

\[
M=
\begin{pmatrix}
2&1\\
1&1
\end{pmatrix}.
\]

The equalities are computed independently in the fixture using an exact
finite implementation of \(\mathbb Z[t,t^{-1}]\).  No floating-point
calculation establishes the polynomial identity.

---

## 1. What turns a through strand into a knot

A local term

\[
\langle L\mid_N R\rangle
\]

is only a typed passage relation.  It does not determine a knot.  A knot
reading additionally needs at least:

- a closure joining the exposed endpoints;
- an embedding or diagram with over/under crossing data;
- orientation;
- a base point or an explicit quotient by base-point change; and
- retained braid or chronological history.

Call such an enriched item a **closed through history**.  Only after these
certificates are present may its trace be encoded by a group word.  This
distinction blocks the invalid inference

\[
\text{one through relation}\Longrightarrow\text{one canonical knot}.
\]

The fixture starts with a declared figure-eight closure word.  It does not
derive that word from the present `ProgramSlice` surface.

---

## 2. Construction reading: the AEG path defect

Let the four letters act on an affine coordinate by

\[
\begin{aligned}
a(x)&=tx,& A(x)&=t^{-1}x,\\
b(x)&=x+1,& B(x)&=x-1.
\end{aligned}
\]

Apply the rightmost letter first.  Exact evaluation gives

\[
W_t(x)=x+3t-t^2-1
=x-\left(t^2-3t+1\right).
\]

The total scaling exponent is zero, so the only failure to close is the
translation

\[
D_w(t)=3t-t^2-1=-\Delta_{4_1}(t).
\]

This is a construction reading because it retains the ordered word.  A bag of
letter counts is insufficient: the fixture shuffles the same multiset of
letters to

\[
\texttt{aaAAbbbBB}
\]

and obtains the constant translation $1$, not an associate of
\(\Delta_{4_1}\).  The feature depends on ordered history.

There is also an important logical correction.  For generic $t$, this
affine assignment is not a representation of the knot group: its relator is
sent to a nonzero translation.  It descends through the relator only at
characters satisfying

\[
\Delta_{4_1}(t)=0.
\]

Before specialization, the accurate object is a free-word evaluation or Fox
cocycle with a measured relation defect.

---

## 3. Spatial reading: Fox derivative and Alexander residual

In the chosen one-relator presentation, abelianization sends

\[
\phi(a)=t,
\qquad
\phi(b)=1.
\]

The $b$-Fox derivative has three positive and two negative contributions:

\[
\begin{aligned}
\phi\!\left(\frac{\partial w}{\partial b}\right)
&=t+t+t-t^2-1\\
&=3t-t^2-1\\
&=-\Delta_{4_1}(t).
\end{aligned}
\]

The striking point is structural: the Fox prefix rule reads exactly the same
ordered prefixes that determine the affine translation defect.  The equality
is therefore not a numerical coincidence.

The invariant object is not a preferred spelling of the polynomial.  The
Alexander units produce the declared quotient

\[
p(t)\sim \pm t^k p(t).
\]

The fixture checks all cyclic base-point rotations of $w$.  Their raw AEG
residuals are different, while their canonical associates are all
\(\Delta_{4_1}\).  This is a bounded base-point check, not a proof of
invariance under arbitrary presentation change.

---

## 4. Temporal reading: monodromy

The figure-eight complement fibres over the circle.  On first homology of a
punctured-torus fibre, take the monodromy matrix

\[
M=
\begin{pmatrix}
2&1\\
1&1
\end{pmatrix}.
\]

Then

\[
\det(tI-M)
=t^2-\operatorname{tr}(M)t+\det(M)
=t^2-3t+1.
\]

The same finite expression therefore records the temporal return map.  This
matches the earlier pattern in which a finite visible cycle can close while
its lifted history retains holonomy: the base returns, but the fibre carries
a nontrivial action.

The present equality is especially clean because $4_1$ is fibreable.  It
must not be projected onto arbitrary knots without another construction.

---

## 5. Duality and the two closure characters

The deck-character duality is

\[
t\longmapsto t^{-1}.
\]

For the figure-eight characteristic,

\[
t^2\Delta_{4_1}(t^{-1})=\Delta_{4_1}(t).
\]

Its two real roots are

\[
t_- = \frac{3-\sqrt5}{2}=\varphi^{-2},
\qquad
t_+ = \frac{3+\sqrt5}{2}=\varphi^2,
\]

and

\[
t_-t_+=1.
\]

Hence the raw closure equation has two characters, while duality exchanges
them and leaves one reciprocal orbit.  This is the precise sense in which
feature extraction reduces a two-valued closure locus here.

Two cautions remain:

1. $t$ is a deck character or monodromy eigenvalue, not the identifier of a
   concrete through resolution.
2. The current finite surreal implementation does not exactly objectify these
   algebraic irrational roots.  The exact finite carrier is the polynomial
   and its rule, not a forced floating-point or finite-surreal replacement.

---

## 6. What “eliminating multivaluedness” can mean

Let \(\mathcal R\) be a resolution fibre for a closed through history.  A
naive observer might select one element of \(\mathcal R\).  The present
experiment instead suggests a three-stage feature map:

\[
\mathcal R
\longrightarrow
\text{module or return action over }\mathbb Z[t,t^{-1}]
\longrightarrow
[\Delta(t)]_{\pm t^k}.
\]

The final class is finite syntax with open interpretation.  It forgets:

- a preferred base point;
- multiplication by an Alexander unit;
- individual representatives inside the module presentation; and
- many distinctions between knots sharing the same Alexander polynomial.

It retains:

- the ordered-history obstruction seen by the chosen quotient;
- the reciprocal duality;
- the closure-character locus; and
- a residual that can be recomputed in three different charts.

Therefore the supported claim is

\[
\boxed{
\text{feature extraction can replace unresolved crossings by a finite
spectral obstruction, with an explicit residual.}
}
\]

The unsupported stronger claim is

\[
\text{feature extraction uniquely reconstructs the through history.}
\]

Alexander data is incomplete; distinct knots can share the same polynomial,
and nontrivial knots can have \(\Delta=1\).

---

## 7. Presentation residual and the current no-go boundary

The affine interpretation works for the selected word.  The earlier
[`aeg-paper` presentation note][presentation-note] records that other standard
presentations do not expose the arithmetic factor in the same immediate way.
The missing datum is an explicit Tietze or presentation-change certificate.

Accordingly, the current feature should be packaged conceptually as

\[
\operatorname{ThroughCharacteristicV0}
=
(w,\phi,D_w,J_w,M,\Delta,u,\rho),
\]

where:

- $w$ is the based closure word;
- \(\phi\) is the declared abelianization;
- $D_w$ is the construction-path defect;
- $J_w$ is the retained Fox row or presentation matrix;
- $M$ is the temporal return map when one exists;
- \(\Delta\) is the common normalized feature;
- $u\in\{\pm t^k\}$ records an allowed unit change; and
- \(\rho\) retains presentation, closure, and provenance residuals.

Hiding $(w,\phi,J_w)$, or the unit witness before proving presentation
invariance would repeat the `ProvenanceHide` error at a new level.

---

## 8. What the fixture establishes

The exact fixture checks:

1. the AEG path has unit slope and translation \(-\Delta_{4_1}\);
2. the abelianized Fox derivative equals that translation exactly;
3. the monodromy characteristic polynomial equals \(\Delta_{4_1}\);
4. reciprocal duality preserves the characteristic up to units and exchanges
   the two real roots;
5. cyclic base-point changes alter raw residuals only by \(\pm t^k\); and
6. a shuffled word with identical letter counts fails the characteristic.

It does **not** establish:

- that every through strand canonically closes to a knot;
- that every knot admits this AEG spelling;
- invariance under arbitrary Tietze transformations;
- completeness of the Alexander characteristic;
- an implementation in the stable Adva language; or
- universal computation from knot closure.

---

## 9. Next falsifiable steps

The next bridge should remain research-local:

1. define a finite `ThroughClosureV0` certificate containing orientation,
   crossing, base-point, and closure provenance;
2. give two presentations of $4_1$ and an explicit Tietze trace between
   them, transporting both the Fox matrix and AEG defect;
3. compile a Laurent-affine word only after the core has an exact typed
   Laurent carrier or an explicit $(t,t^{-1})$ constraint—never by an opaque
   host callback;
4. compare two distinct knots with the same Alexander polynomial, forcing a
   higher residual rather than overstating completeness; and
5. test whether each of the three circular interfaces produces a compatible
   characteristic and whether their composition leaves a new holonomy
   residual.

The first calculation supports the proposed direction: a special symmetric
closed thread can make one feature visible simultaneously as construction
defect, spatial module order, and temporal spectrum.  The missing piece is no
longer the polynomial.  It is the typed closure-and-presentation transport
that tells us when the three readings belong to the same through history.
