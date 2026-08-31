# Elliptic Isogenies as a Classical Triadic Characteristic Calibration

Status: exploratory research calibration extending
[`0038-triadic-characteristic-inference-calibration.md`](0038-triadic-characteristic-inference-calibration.md),
[`0039-square-map-branch-copy-calibration.md`](0039-square-map-branch-copy-calibration.md),
and
[`0040-cube-equivariance-degree-calibration.md`](0040-cube-equivariance-degree-calibration.md).

This note raises the preceding polynomial calibration to actual elliptic
curves and actual isogenies.  Its purpose is not to rename standard
elliptic-curve data as temporal, spatial, and constructive.  The purpose is
to test whether one classical morphism already admits three rigorously linked
readings of the kind required by the triadic characteristic programme.

The bounded answer is positive.

> For a complex elliptic curve, one isogeny has an exact temporal reading on
> the universal cover and tangent line, an exact spatial reading as a finite
> quotient and covering, and an exact constructive reading as a rational map
> generated from a finite kernel.  In the complex-multiplication examples,
> these readings satisfy
>
> \[
> N(\alpha)
> =
> |\det M_\alpha|
> =
> \deg\phi
> =
> |\ker\phi|.
> \]

The three explicit calibrations are:

1. multiplication by two on
   \(E_0:y^2=x^3+1\), of degree four;
2. a degree-two quotient of
   \(E_i:y^2=x^3-25x\), which becomes multiplication by \(1+i\)
   after complex reidentification; and
3. a degree-three quotient of
   \(E_\omega:y^2=x^3+1\), which becomes multiplication by
   \(1-\omega\), with \(\omega=e^{2\pi i/3}\), after complex
   reidentification.

The executable calibration is
[`tests/python/test_elliptic_isogeny_characteristics.py`](../../tests/python/test_elliptic_isogeny_characteristics.py).

This remains research-local.  It does not add a stable elliptic-curve,
isogeny, complex-scalar, period-lattice, projective-coordinate, kernel, dual,
or characteristic API.  SymPy supplies exact external algebra.  Adva checks
only bounded real projective numerator/denominator circuits and their source
and occurrence lineage.  The active `ProgramSlice` priority and Rust semantic
authority remain unchanged.

## 1. Why the characteristic should be an isogeny

The preceding calibrations sought one finite characteristic \(c\) with three
typed interpretations

\[
\rho_t(c),
\qquad
\rho_X(c),
\qquad
\rho_K(c).
\]

For elliptic curves the natural candidate is not a point, a period, a scalar,
or a polynomial.  It is an isogeny

\[
\phi:E\longrightarrow E'.
\]

An isogeny is simultaneously:

- a group homomorphism on points;
- a nonconstant morphism of smooth projective curves;
- a finite quotient with finite kernel;
- a finite covering over \(\mathbf C\); and
- a rational map in Weierstrass coordinates.

These are not analogies.  They are equivalent classical presentations of one
typed morphism.

The provisional triadic readings are

\[
\rho_t(\phi)
=
\text{point, tangent, and period transport},
\]

\[
\rho_X(\phi)
=
\text{kernel, quotient, covering degree, and inverse image},
\]

and

\[
\rho_K(\phi)
=
\text{kernel-generated rational map and checked arithmetic circuit}.
\]

The word “temporal” is an interpretation added by the programme.  Classical
theory supplies a composable group morphism; an actual temporal semantics
still requires a task, an iteration, a state, and an observation horizon.

## 2. The classical compatibility package

### 2.1 Universal-cover and tangent reading

Let

\[
\Lambda_j
=
\mathbf Z\omega_{j,1}+\mathbf Z\omega_{j,2}
\subset\mathbf C.
\]

Complex uniformization gives

\[
\Phi_j:
\mathbf C/\Lambda_j
\overset{\sim}{\longrightarrow}
E_j(\mathbf C).
\]

Every morphism of complex tori fixing zero is induced by a unique complex
number \(\alpha\) satisfying

\[
\alpha\Lambda_1\subseteq\Lambda_2.
\]

Thus an isogeny is represented on the universal cover by

\[
z\longmapsto\alpha z.
\]

At the identity it induces a typed line map

\[
d\phi_0:T_0E_1\longrightarrow T_0E_2.
\]

For invariant differentials

\[
\eta_{E_1}=\frac{dx}{2y},
\qquad
\eta_{E_2}=\frac{dX}{2Y},
\]

there is a scalar \(c_\phi\) such that

\[
\phi^*\eta_{E_2}
=
c_\phi\eta_{E_1}.
\]

The scalar depends on the chosen source and target differential bases.  The
intrinsic temporal object is the line map, not the untyped number.

### 2.2 Spatial reading

On complex tori,

\[
\ker\phi_\alpha
=
\alpha^{-1}\Lambda_2/\Lambda_1.
\]

For an endomorphism of \(\mathbf C/\Lambda\), multiplication by \(\alpha\)
has degree

\[
\deg\phi_\alpha
=
[\Lambda:\alpha\Lambda].
\]

If \(M_\alpha\) is the integral matrix of multiplication by \(\alpha\) in a
lattice basis, then

\[
\deg\phi_\alpha
=
|\det M_\alpha|.
\]

In characteristic zero every nonzero isogeny is separable, so

\[
|\ker\phi|
=
\deg\phi.
\]

For an imaginary-quadratic integer \(\alpha\),

\[
|\det M_\alpha|
=
N(\alpha)
=
\alpha\bar\alpha.
\]

The same spatial characteristic is therefore visible as a finite kernel, a
lattice index, a generic fibre cardinality, a covering degree, and a
contravariant inverse-image operation.

### 2.3 Constructive reading

A finite subgroup

\[
G\subset E(\overline{k})
\]

determines a separable quotient isogeny

\[
\phi_G:E\longrightarrow E/G
\]

up to isomorphism of the codomain.  Vélu formulas construct both a model for
\(E/G\) and rational functions for \(\phi_G\).

This supplies a classical finite compiler

\[
\boxed{
G
\longmapsto
(E/G,\phi_G).
}
\]

But a classical morphism does not determine a unique arithmetic circuit.
Coordinate changes, projective rescalings, addition chains, common
subexpressions, and copy placement may all vary.  The constructive channel
must therefore retain

\[
\text{morphism}
+
\text{presentation}
+
\text{certificate}
+
\text{residual}.
\]

### 2.4 Dual reading

For an isogeny of degree \(d\), the dual isogeny is characterized by

\[
\widehat\phi\circ\phi=[d],
\qquad
\phi\circ\widehat\phi=[d].
\]

It is not generally an inverse.  In the CM setting the dual corresponds to
complex conjugation:

\[
\widehat{\phi_\alpha}
=
\phi_{\bar\alpha},
\]

and hence

\[
\phi_{\bar\alpha}\circ\phi_\alpha
=
[N(\alpha)].
\]

This gives an exact classical model of a scaled reverse channel: reverse after
forward produces a central scale action rather than the identity.

## 3. A bounded elliptic triadic form

The calibration can be packaged as

\[
\mathfrak E_Q(\phi)
=
\left(
T_Q(\phi),
X_Q(\phi),
K_Q(\phi);
\Omega_Q(\phi),
R_Q(\phi)
\right),
\]

where

\[
T_Q(\phi)
=
(d\phi_0,\alpha,\text{point probes}),
\]

\[
X_Q(\phi)
=
(\ker\phi,\deg\phi,M_\alpha,\phi^{-1}),
\]

and

\[
K_Q(\phi)
=
(u,v,s,t,\text{kernel witness},\text{circuit}).
\]

The comparison certificate contains at least

\[
\phi^*\eta_{E'}=c_\phi\eta_E,
\]

\[
N(\alpha)=|\det M_\alpha|=\deg\phi,
\]

\[
|\ker\phi|=\deg\phi,
\]

\[
\max(\deg u,\deg v)=\deg\phi,
\]

and

\[
M_{\bar\alpha}M_\alpha
=
\deg(\phi)I.
\]

The residual records the Weierstrass models, invariant differentials, lattice
bases, field of definition, source--target identification, projective
representative, arithmetic circuit, and source/occurrence lineage.

## 4. Example A: multiplication by two

Let

\[
E_0:y^2=x^3+1.
\]

The multiplication-by-two isogeny is

\[
[2]:E_0\longrightarrow E_0.
\]

Its affine standard form is

\[
[2](x,y)
=
\left(
\frac{x(x^3-8)}{4(x^3+1)},
\frac{x^6+20x^3-8}{8y(x^3+1)}
\right).
\]

The second coordinate is equivalently

\[
\frac{(x^6+20x^3-8)y}{8(x^3+1)^2}.
\]

### 4.1 Actual point calculation

For

\[
P=(2,3),
\]

we obtain

\[
x([2]P)=0,
\qquad
y([2]P)=1,
\]

so

\[
[2](2,3)=(0,1).
\]

### 4.2 Three readings

On the universal cover,

\[
z\longmapsto2z,
\]

and

\[
[2]^*\eta=2\eta.
\]

The lattice matrix is

\[
M_2=
\begin{pmatrix}
2&0\\
0&2
\end{pmatrix},
\qquad
\det M_2=4.
\]

The kernel is the full two-torsion group

\[
E_0[2]
=
\{O\}\cup\{(r,0):r^3+1=0\},
\]

which has four geometric points.  The rational-function numerator has degree
four and its denominator degree three.  Therefore

\[
N(2)
=
|\det M_2|
=
\deg[2]
=
|E_0[2]|
=
4.
\]

The map is self-dual, and

\[
[2]\circ[2]=[4].
\]

## 5. Example B: a Gaussian degree-two isogeny

Consider

\[
E_i:y^2=x^3-25x.
\]

The point \(T=(0,0)\) has order two.  Quotienting by

\[
G_i=\{O,T\}
\]

gives

\[
\phi_i:E_i\longrightarrow E_i',
\qquad
E_i':y^2=x^3+100x,
\]

with

\[
\boxed{
\phi_i(x,y)
=
\left(
\frac{x^2-25}{x},
\frac{y(x^2+25)}{x^2}
\right).
}
\]

### 5.1 Actual point calculation

The point

\[
P_i=(-4,6)
\]

lies on \(E_i\).  Direct substitution yields

\[
\phi_i(-4,6)
=
\left(
\frac94,
\frac{123}{8}
\right),
\]

which lies on \(E_i'\).

### 5.2 Normalization and port closure

For

\[
X=x-\frac{25}{x},
\qquad
Y=y\left(1+\frac{25}{x^2}\right),
\]

we have

\[
\frac{dX}{dx}\frac{y}{Y}=1.
\]

Thus the Vélu quotient is normalized:

\[
\phi_i^*\eta_{E_i'}=\eta_{E_i}.
\]

Both curves have \(j=1728\).  Define

\[
u_i=\frac{1-i}{2}.
\]

Since

\[
100u_i^4=-25,
\]

the map

\[
\iota_i(x',y')
=
(u_i^2x',u_i^3y')
\]

identifies \(E_i'\) with \(E_i\) over \(\mathbf C\).  Closing the target port
produces

\[
\psi_i=\iota_i\circ\phi_i:E_i\to E_i,
\]

with

\[
\psi_i^*\eta_{E_i}
=
u_i^{-1}\eta_{E_i}
=
(1+i)\eta_{E_i}.
\]

Here the intended notation is the same parameter \(u_i\); the displayed
multiplier is

\[
\alpha_i=1+i.
\]

### 5.3 Lattice, kernel, construction, and dual

In the Gaussian basis \((1,i)\),

\[
M_{1+i}
=
\begin{pmatrix}
1&-1\\
1&1
\end{pmatrix},
\qquad
\det M_{1+i}=2.
\]

Hence

\[
N(1+i)
=
\deg\phi_i
=
|\ker\phi_i|
=
2.
\]

The projective \(x\)-coordinate is

\[
(x^2-25:x).
\]

The checked fixture constructs this pair from three explicit input
occurrences: two for the numerator and one for the denominator.  This
occurrence count is not the isogeny degree.

The conjugate matrix is

\[
M_{1-i}
=
\begin{pmatrix}
1&1\\
-1&1
\end{pmatrix},
\]

and

\[
M_{1-i}M_{1+i}=2I.
\]

This is the lattice form of

\[
\widehat\psi_i\circ\psi_i=[2].
\]

## 6. Example C: an Eisenstein degree-three isogeny

Let

\[
E_\omega:y^2=x^3+1.
\]

The subgroup

\[
G_\omega
=
\{O,(0,1),(0,-1)\}
\]

has order three.  The quotient isogeny is

\[
\phi_\omega:E_\omega\longrightarrow E_\omega',
\qquad
E_\omega':y^2=x^3-27,
\]

with

\[
\boxed{
\phi_\omega(x,y)
=
\left(
\frac{x^3+4}{x^2},
\frac{y(x^3-8)}{x^3}
\right).
}
\]

### 6.1 Actual point calculation

For \(P=(2,3)\),

\[
\phi_\omega(2,3)=(3,0),
\]

and the target equation gives \(0^2=3^3-27\).

### 6.2 Normalization and port closure

For

\[
X=x+\frac4{x^2},
\qquad
Y=y\left(1-\frac8{x^3}\right),
\]

we have

\[
\frac{dX}{dx}\frac{y}{Y}=1,
\]

so

\[
\phi_\omega^*\eta_{E_\omega'}
=
\eta_{E_\omega}.
\]

Both models have \(j=0\).  Put

\[
u_\omega=\frac1{1-\omega}.
\]

Because

\[
(1-\omega)^6=-27,
\]

we have

\[
-27u_\omega^6=1.
\]

The map

\[
\iota_\omega(x',y')
=
(u_\omega^2x',u_\omega^3y')
\]

identifies the target with the source over \(\mathbf C\).  The closed
endomorphism

\[
\psi_\omega
=
\iota_\omega\circ\phi_\omega
\]

has multiplier

\[
\alpha_\omega
=
u_\omega^{-1}
=
1-\omega.
\]

Again, \(u_\omega\) and the displayed \(\nu_\omega\) denote the same chosen
reidentification parameter; the intrinsic datum is the typed isomorphism.

### 6.3 Lattice, kernel, construction, and dual

In the Eisenstein basis \((1,\omega)\),

\[
M_{1-\omega}
=
\begin{pmatrix}
1&1\\
-1&2
\end{pmatrix},
\qquad
\det M_{1-\omega}=3.
\]

Thus

\[
N(1-\omega)
=
\deg\phi_\omega
=
|\ker\phi_\omega|
=
3.
\]

The projective \(x\)-coordinate is

\[
(x^3+4:x^2).
\]

The bounded fixture uses five explicit input occurrences: three for the
numerator and two for the denominator.  This is an implementation profile,
not a geometric degree.

For the conjugate scalar \(1-\omega^2\),

\[
M_{1-\omega^2}
=
\begin{pmatrix}
2&-1\\
1&1
\end{pmatrix},
\]

and

\[
M_{1-\omega^2}M_{1-\omega}=3I.
\]

This is the lattice form of

\[
\widehat\psi_\omega\circ\psi_\omega=[3].
\]

## 7. Cross-example table

| closed map | temporal scalar | lattice determinant | geometric degree | kernel size |
|---|---:|---:|---:|---:|
| `[2]` | `2` | `4` | `4` | `4` |
| Gaussian CM | `1+i` | `2` | `2` | `2` |
| Eisenstein CM | `1-omega` | `3` | `3` | `3` |

The constructive data are different:

| quotient map | projective `x` pair | `x`-map degree | fixture input leaves |
|---|---|---:|---:|
| `[2]` | `(x(x^3-8),4(x^3+1))` | `4` | not lowered here |
| `phi_i` | `(x^2-25,x)` | `2` | `3` |
| `phi_omega` | `(x^3+4,x^2)` | `3` | `5` |

The equalities

\[
N(\alpha)
=
|\det M_\alpha|
=
\deg\phi
=
|\ker\phi|
=
\deg_x\phi
\]

belong to the classical morphism and its standard form.  The fixture leaf
count belongs to a chosen program construction.

## 8. A decisive contrast with the polynomial calibrations

The affine-line maps

\[
x\mapsto x^2
\quad\text{and}\quad
x\mapsto x^3
\]

can have critical points and branched inverse images.  A nonzero complex
isogeny lifts to

\[
z\mapsto\alpha z
\]

with \(\alpha\ne0\), so it is locally biholomorphic and unramified.

Its finite degree is covering multiplicity, not ramification multiplicity.

The coordinate projection

\[
x:E'\longrightarrow\mathbf P^1
\]

is itself branched.  Consequently the rational function

\[
x\circ\phi:E\longrightarrow\mathbf P^1
\]

may display poles and critical behaviour even though \(\phi\) is unramified.
The correct typing rule is

\[
\boxed{
\text{branching of a coordinate shadow}
\ne
\text{ramification of the isogeny}.
}
\]

This distinction is essential for any program-geometric interpretation of
cuts and branches.

## 9. What traditional theory says the characteristic is

Traditional theory does not identify the characteristic with any one of

\[
\alpha,
\qquad
M_\alpha,
\qquad
\ker\phi,
\qquad
\left(\frac{u}{v},\frac{s}{t}y\right).
\]

The common object is the typed isogeny represented by all of them, together
with comparison maps.

This suggests the more stable formulation:

> A characteristic is an object in a representation groupoid, not merely a
> preferred normal-form value.

Changing a lattice basis, Weierstrass model, invariant differential,
projective representative, or arithmetic circuit changes the presentation
without necessarily changing the classical morphism.  These changes are not
literal identity at the program level.

## 10. Relation to the larger three-domain picture

### 10.1 What is already classical

Elliptic theory already gives an exact bridge

\[
\boxed{
\text{tangent or period multiplier}
\longleftrightarrow
\text{finite quotient and covering}
\longleftrightarrow
\text{kernel-generated rational map}.
}
\]

The three-domain programme should not claim that such bridges are absent from
traditional mathematics.

### 10.2 What the programme adds

The proposed generalization is different in five respects:

1. it makes the characteristic relative to a finite observer and task;
2. it treats inference from typed observations as a first-class algorithm;
3. it preserves variance explicitly;
4. it retains raw construction history and source/occurrence identity; and
5. it emits an accountable residual across representation changes.

### 10.3 A morphism comes before its scalar

The examples strongly support a typed-morphism ontology.  The scalar
\(\alpha\) appears only after the source and target tangent lines or period
lattices are identified.  This argues against storing general
characteristics as untyped numbers.

### 10.4 Periods are a carrier

In classical uniformization the period lattice is the integral carrier on
which the endomorphism acts:

\[
\alpha:\Lambda\longrightarrow\Lambda.
\]

The two lattice coordinates are not automatically two temporal directions.
Any larger interpretation of `p,q` must state whether they are process
directions, homology coordinates, periods, or observer charts.

### 10.5 Forward and reverse can be conjugate, not inverse

The CM examples supply a precise pair

\[
\alpha,
\qquad
\bar\alpha,
\]

with

\[
\bar\alpha\alpha=N(\alpha).
\]

This is a strong calibration for simultaneous forward and reverse channels,
but it does not prove that every program reverse is a CM conjugate.

### 10.6 Local normalization and circuit transport

The quotient maps have local differential multiplier `1`; the nontrivial CM
multiplier appears in the isomorphism that returns the target model to the
source model.  A full representational circuit can therefore carry
nontrivial transport even when one local edge is normalized.  This resembles
the earlier holonomy intuition, but no general holonomy theorem is claimed.

## 11. Characteristic inference in the elliptic setting

Given a degree bound \(D\), define a bounded candidate family of isogenies and
intersect three typed constraint sets:

\[
\operatorname{Char}_{Q,D}(O_t,O_X,O_K)
=
C_t(O_t)
\cap
C_X(O_X)
\cap
C_K(O_K).
\]

Temporal probes may include point images, action on torsion, repeated orbits,
and the invariant-differential multiplier.

Spatial probes may include degree, kernel, lattice index, generic fibres,
inverse images, and field-of-definition data.

Constructive probes may include exact rational identities, numerator and
denominator degrees, projective circuits, copy lineage, and a Vélu
reconstruction certificate.

A bounded solver has the form

```text
infer_isogeny(Q, degree_bound, observations):
    candidates = bounded_isogeny_family(Q, degree_bound)

    candidates &= temporal_constraints(observations.time)
    candidates &= spatial_kernel_and_degree_constraints(observations.space)
    candidates &= constructive_map_constraints(observations.construction)

    if search was not exhaustive:
        return Unknown(search_residual)

    if candidates is empty:
        return Inconsistent(countercertificate)

    if candidates has multiple elements:
        return Ambiguous(candidates, separating_probes)

    phi = the unique candidate
    return Unique(phi, certificates(phi), residuals(phi))
```

## 12. Algorithmic implications

### 12.1 Kernel-first synthesis

Searching over arbitrary degree-\(d\) rational maps introduces many
coefficients and curve-compatibility equations.  Searching over finite
subgroups or kernel polynomials can be much smaller.  Once a valid kernel is
fixed, Vélu construction produces a quotient model and map.

### 12.2 Norm-first synthesis in CM charts

For CM endomorphisms, a degree condition becomes a norm equation

\[
N(\alpha)=d.
\]

The examples reduce to

\[
N(2)=4,
\qquad
N(1+i)=2,
\qquad
N(1-\omega)=3.
\]

This replaces an unrestricted rational-function search by a finite search
for algebraic integers of bounded norm, followed by exact reconstruction.

### 12.3 Independent certificates

The same degree is checked by

- a lattice determinant;
- a CM norm;
- kernel cardinality;
- rational-function degree; and
- dual composition.

A disagreement identifies a faulty chart, kernel, formula, or circuit rather
than one undifferentiated failure.

### 12.4 Compact projective circuits

Rational maps should be stored as shared projective circuits, not fully
expanded numerator and denominator trees.  Sharing must remain explicit and
certificate-bearing; value equality does not authorize common-subexpression
identification.

### 12.5 Dual verification

Rather than inverting an isogeny pointwise, one can construct the dual and
verify

\[
\widehat\phi\circ\phi=[d].
\]

This replaces an impossible inverse requirement by an exact scaled-reverse
certificate.

## 13. Conservative conclusion

The three examples establish one bounded but nontrivial result.

A single classical isogeny can be represented consistently by

1. a point and tangent action;
2. a complex multiplier after port identification;
3. an integral lattice matrix;
4. a finite kernel and finite covering;
5. an explicit rational map;
6. a checked projective arithmetic circuit; and
7. a dual map whose composition gives central scale.

The minimal characteristic carrier is therefore not a scalar or a degree.  It
has the form

\[
\boxed{
\text{typed morphism}
+
\text{port and chart}
+
\text{tangent action}
+
\text{kernel and degree}
+
\text{rational realization}
+
\text{certificate}
+
\text{residual}.
}
\]

This supports the triadic characteristic method while sharply locating its
relationship to traditional theory: the compatibility laws are classical;
the observer-relative inference, construction provenance, and accountable
residual are the proposed extension.

## 14. Claims not made

This note does not claim that

- every Adva characteristic is an isogeny;
- every three-domain system has a period lattice;
- every forward/reverse pair is complex conjugation;
- every reverse process is a dual isogeny;
- every residual is holonomy;
- every program quotient is finite étale;
- the elliptic examples explain the whole three-computer architecture;
- the larger `p,q` directions are automatically elliptic periods;
- construction occurrence count is a geometric invariant; or
- the current fixture is a stable elliptic-curve implementation.

## 15. Red-team opinion

### 15.1 The examples are exceptional

The curves with \(j=1728\) and \(j=0\) have extra automorphisms and
imaginary-quadratic endomorphism rings.  A generic complex elliptic curve has
endomorphism ring \(\mathbf Z\).  The norm-scalar simplification is not generic.

### 15.2 Kernel does not fix a literal formula

A kernel determines the quotient isogeny up to target isomorphism.  A literal
Weierstrass equation and rational formula still require model choices.

### 15.3 Coordinate shadows can mislead

Poles and critical points of coordinate functions do not imply ramification
of the whole isogeny.  The whole morphism and every selected coordinate
shadow must remain typed separately.

### 15.4 Construction counts are implementation-dependent

The fixture uses three leaves for \((x^2-25:x)\) and five for
\((x^3+4:x^2)\).  A different explicit sharing DAG can change these numbers
without changing the isogeny.

### 15.5 Inference remains difficult in general

Larger examples require Galois-stable subgroup schemes, field extensions,
modular polynomials, nonprincipal ideals, coordinate-growth control, and
ambiguity management.  No general polynomial-time characteristic solver
follows from this calibration.

## 16. Next exact pressure tests

1. Construct the explicit dual degree-two and degree-three rational maps and
   verify
   \[
   \widehat\phi_2\circ\phi_2=[2],
   \qquad
   \widehat\phi_3\circ\phi_3=[3]
   \]
   in the constructive domain.
2. Hide one low-degree isogeny and infer it from point, tangent, kernel, and
   circuit observations.
3. Add a non-CM control to separate general kernel--degree--formula laws from
   exceptional CM norm laws.
4. Reduce one example modulo good primes and compare geometric kernel,
   rational kernel, Frobenius action, and observer-visible fibres.

## 17. Classical references

The surrounding classical statements are calibrated against:

1. Andrew V. Sutherland, *18.783 Elliptic Curves*, Lecture 4, “Isogenies”;
2. Lecture 5, “Isogeny kernels and division polynomials”;
3. Lecture 6, “Endomorphism rings”;
4. Lecture 14, “Elliptic curves over C (part I)”;
5. Lecture 16, “Complex multiplication”; and
6. Jacques Vélu, “Isogénies entre courbes elliptiques,” *C. R. Acad. Sci.
   Paris* 273 (1971), 238–241.
