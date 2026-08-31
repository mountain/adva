# Elliptic Isogenies as a Classical Triadic Characteristic Calibration

Status: exploratory research calibration extending
[`0038-triadic-characteristic-inference-calibration.md`](0038-triadic-characteristic-inference-calibration.md),
[`0039-square-map-branch-copy-calibration.md`](0039-square-map-branch-copy-calibration.md),
and
[`0040-cube-equivariance-degree-calibration.md`](0040-cube-equivariance-degree-calibration.md).

This note raises the difficulty of the preceding polynomial examples by using
actual elliptic curves and actual isogenies.  The purpose is not to import
elliptic-curve terminology into Adva by analogy.  It is to ask whether the
temporal, spatial, and constructive readings of one finite characteristic
already occur as rigorously linked objects in a mature classical theory.

The central answer is:

> For a complex elliptic curve, one isogeny has three exact classical
> readings.  On the universal cover it is multiplication by a complex scalar
> `alpha`; spatially it is a finite covering whose degree is the lattice index
> and kernel size; constructively it is a rational map that can be recovered
> from its finite kernel.  In the CM cases these readings satisfy
>
> \[
> N(\alpha)
> =
> \deg\phi
> =
> |\ker\phi|,
> \]
>
> and the dual isogeny corresponds to complex conjugation.

This is a genuine classical three-way compatibility law.  It gives a strong
calibration for the characteristic method, but it also forces several
revisions:

1. the shared characteristic is primarily a typed morphism, not a scalar;
2. a scalar multiplier appears only after tangent lines or period lattices are
   identified;
3. an isogeny is unramified over the complex numbers even when its coordinate
   rational functions contain poles and powers;
4. the dual is a scaled reverse, not an inverse; and
5. the classical morphism forgets construction history that Adva must retain
   as source, occurrence, circuit, certificate, and residual data.

The three explicit examples are:

\[
[2]:E_0\longrightarrow E_0,
\qquad
E_0:y^2=x^3+1,
\]

a degree-four multiplication map;

\[
\phi_i:E_i\longrightarrow E_i',
\qquad
E_i:y^2=x^3-25x,
\quad
E_i':y^2=x^3+100x,
\]

a degree-two quotient isogeny that becomes multiplication by `1+i` after a
complex reidentification; and

\[
\phi_\omega:E_\omega\longrightarrow E_\omega',
\qquad
E_\omega:y^2=x^3+1,
\quad
E_\omega':y^2=x^3-27,
\]

a degree-three quotient isogeny that becomes multiplication by `1-omega`
after a complex reidentification, where

\[
\omega=e^{2\pi i/3},
\qquad
\omega^2+\omega+1=0.
\]

The executable calibration is in
[`tests/python/test_elliptic_isogeny_characteristics.py`](../../tests/python/test_elliptic_isogeny_characteristics.py).

This remains research-local.  It does not add a stable elliptic curve,
isogeny, complex scalar, period lattice, rational-map, projective-coordinate,
kernel, dual, or characteristic API.  SymPy supplies exact external algebra.
Adva checks only bounded real projective numerator/denominator circuits and
their construction lineage.  The active `ProgramSlice` priority and Rust
semantic authority remain unchanged.

## 1. Research question

The preceding calibrations treated a characteristic as a finite object with
three typed interpretations:

\[
\rho_t(c),
\qquad
\rho_X(c),
\qquad
\rho_K(c).
\]

The affine example used a parameter pair `(k,b)`.  The square and cube examples
forced the carrier to include branch, equivariance, critical, and explicit
copy data.

Elliptic curves provide a sharper test because classical mathematics already
relates four presentations of the same map:

1. a group homomorphism on points;
2. multiplication on a complex torus;
3. a finite covering with a finite kernel; and
4. a rational map in Weierstrass coordinates.

The question is therefore:

> Can one classical isogeny serve as a nontrivial exact model of a triadic
> characteristic, and if so, what does classical theory identify that our
> program-geometric account should keep distinct?

The candidate characteristic is an isogeny

\[
\phi:E\longrightarrow E'.
\]

Its three readings are provisionally:

\[
\rho_t(\phi)
=
\text{point and tangent transport},
\]

\[
\rho_X(\phi)
=
\text{inverse image, finite cover, kernel, and lattice index},
\]

and

\[
\rho_K(\phi)
=
\text{kernel-generated rational map and checked arithmetic circuit}.
\]

The use of the word “temporal” is interpretive: classical theory calls this a
group action or morphism, not time.  The calibration is meaningful only if the
three readings are linked by exact laws rather than labels.

## 2. Classical carrier: the isogeny

### 2.1 Why an isogeny is the right bounded object

An isogeny of elliptic curves is a nonconstant morphism

\[
\phi:E\longrightarrow E'
\]

that sends the identity to the identity.  It is automatically a group
homomorphism.  Over the complex numbers it has finite kernel and is a finite
unramified covering.

This object already combines the three kinds of structure needed here:

- algebraic: it is given by rational functions;
- geometric: it is a finite map of smooth projective curves; and
- dynamic: it transports points and composes with other isogenies.

A bare point, period, or polynomial coefficient does not combine these roles.

### 2.2 Standard coordinate form

For short Weierstrass models in characteristic zero, an isogeny can be written
in standard affine form

\[
\phi(x,y)
=
\left(
\frac{u(x)}{v(x)},
\frac{s(x)}{t(x)}y
\right).
\]

The degree is

\[
\deg\phi
=
\max(\deg u,\deg v).
\]

For a complex endomorphism in standard form one has more precisely

\[
\deg u=\deg v+1=\deg\phi.
\]

This is already a construction--space compatibility law: the degree of the
coordinate rational function agrees with the geometric degree of the map.

### 2.3 Complex uniformization

Let

\[
\Lambda=\mathbf Z\omega_1+\mathbf Z\omega_2
\subset\mathbf C
\]

be a lattice.  Complex uniformization gives an analytic and algebraic group
isomorphism

\[
\Phi:\mathbf C/\Lambda
\overset{\sim}{\longrightarrow}
E(\mathbf C).
\]

Every morphism of complex tori fixing zero is induced by a unique complex
number `alpha` satisfying

\[
\alpha\Lambda_1\subseteq\Lambda_2.
\]

The corresponding diagram is

\[
\begin{CD}
\mathbf C/\Lambda_1 @>{z\mapsto\alpha z}>>
\mathbf C/\Lambda_2\\
@V{\Phi_1}V{\sim}V @VV{\sim}V{\Phi_2}\\
E_1(\mathbf C) @>{\phi_\alpha}>>
E_2(\mathbf C).
\end{CD}
\]

Thus the scalar `alpha` is not an arbitrary encoding of the isogeny.  It is
its exact lift to the universal cover.

### 2.4 The typed temporal feature

At the identity, an isogeny induces a linear map

\[
d\phi_0:T_0E\longrightarrow T_0E'.
\]

Both tangent spaces are one-dimensional, but a scalar is obtained only after
choosing bases.  Equivalently, for invariant differentials

\[
\eta_E=\frac{dx}{2y},
\qquad
\eta_{E'}=\frac{dX}{2Y},
\]

there is a scalar `c_phi` such that

\[
\phi^*\eta_{E'}=c_\phi\eta_E.
\]

For a normalized Vélu quotient map, the chosen models make

\[
c_\phi=1.
\]

If an isomorphism

\[
\iota:E'\overset{\sim}{\longrightarrow}E
\]

is then used to close the map into an endomorphism

\[
\psi=\iota\circ\phi:E\longrightarrow E,
\]

the scalar of `psi` may be nontrivial.  In the two CM examples below it is
`1+i` or `1-omega`.

This yields the first major correction to a flat characteristic vocabulary:

> The intrinsic temporal object is a typed line map.  Its scalar is relative
> to a port, chart, invariant differential, or period-lattice identification.

### 2.5 The spatial feature

On complex tori, multiplication by `alpha` has kernel

\[
\ker\phi_\alpha
=
\alpha^{-1}\Lambda_2/\Lambda_1.
\]

For an endomorphism of `C/Lambda`, multiplication by `alpha` has degree

\[
\deg\phi_\alpha
=
[\Lambda:\alpha\Lambda].
\]

If `M_alpha` is the integral matrix of multiplication by `alpha` in a lattice
basis, then

\[
\deg\phi_\alpha
=
|\det M_\alpha|.
\]

When `alpha` is an imaginary-quadratic integer,

\[
|\det M_\alpha|
=
N(\alpha)
=
\alpha\bar\alpha.
\]

Over characteristic zero every nonzero isogeny is separable, hence

\[
|\ker\phi|=\deg\phi.
\]

Spatially, the same characteristic is therefore visible through:

- a finite covering;
- a generic fibre cardinality;
- a finite kernel subgroup;
- a lattice-index computation; and
- an inverse-image action on opens and functions.

The inverse-image law remains contravariant:

\[
(\phi_2\circ\phi_1)^{-1}
=
\phi_1^{-1}\circ\phi_2^{-1}.
\]

### 2.6 The constructive feature

A finite subgroup

\[
G\subset E(\overline{k})
\]

determines a separable quotient isogeny

\[
\phi_G:E\longrightarrow E/G
\]

up to an isomorphism of the codomain.  Vélu formulas construct an equation for
`E/G` and rational functions for `phi_G`.

This gives a classical kernel-to-program compiler:

\[
\boxed{
G
\longmapsto
(E/G,\phi_G)
}
\]

where the output is finite and exactly checkable.

But classical equality stops at the morphism.  Different rational
presentations, coordinate changes, projective rescalings, addition chains,
and arithmetic circuits may define the same isogeny.  Adva must therefore
retain a stricter constructive channel:

\[
K_{\mathrm{raw}}
\longrightarrow
\phi
\longrightarrow
K_{\mathrm{classical}},
\]

together with the residual that remembers source and occurrence structure.

### 2.7 The dual isogeny

For every isogeny

\[
\phi:E\longrightarrow E'
\]

of degree `d`, there is a unique dual isogeny

\[
\widehat\phi:E'\longrightarrow E
\]

satisfying

\[
\widehat\phi\circ\phi=[d],
\qquad
\phi\circ\widehat\phi=[d].
\]

On a CM torus, duality corresponds to complex conjugation:

\[
\phi_\alpha^\wedge=\phi_{\bar\alpha},
\]

and therefore

\[
\phi_{\bar\alpha}\circ\phi_\alpha
=
\phi_{\bar\alpha\alpha}
=
[N(\alpha)].
\]

This is not an inverse law.  It is a scaled reverse law.

For the larger program-geometric picture, this is a particularly useful
classical calibration:

> A reverse channel can be canonical and compositional without undoing the
> forward channel.  Forward followed by reverse may produce a central scale
> action rather than the identity.

## 3. A classical triadic form

A bounded elliptic characteristic can be written schematically as

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

with

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
(u,v,s,t,\text{kernel certificate},\text{circuit}).
\]

The consistency certificate `Omega_Q` contains at least:

### Differential compatibility

\[
\phi^*\eta_{E'}
=
c_\phi\eta_E.
\]

### Norm--degree compatibility

\[
N(\alpha)
=
|\det M_\alpha|
=
\deg\phi.
\]

### Kernel--degree compatibility

\[
|\ker\phi|
=
\deg\phi.
\]

### Coordinate--degree compatibility

\[
\max(\deg u,\deg v)
=
\deg\phi.
\]

### Dual compatibility

\[
M_{\bar\alpha}M_\alpha
=
\deg(\phi)I,
\]

corresponding to

\[
\widehat\phi\circ\phi=[\deg\phi].
\]

### Evaluation compatibility

\[
\operatorname{eval}
\bigl(
\rho_K(\phi)(P)
\bigr)
=
\rho_t(\phi)(P).
\]

### Open compatibility

\[
P\in\rho_X(\phi)(U)
\Longleftrightarrow
\rho_t(\phi)(P)\in U.
\]

The residual records choices not determined by the classical morphism:

- Weierstrass model;
- invariant differential;
- lattice basis;
- source and target identifications;
- field of definition;
- projective representative;
- arithmetic circuit;
- source and occurrence lineage; and
- bounded observer data.

## 4. Example A: multiplication by two

Let

\[
E_0:y^2=x^3+1.
\]

The multiplication-by-two map is

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

The second coordinate can equivalently be written in standard `r(x)y` form:

\[
\frac{(x^6+20x^3-8)y}{8(x^3+1)^2}.
\]

### 4.1 Actual point calculation

Take

\[
P=(2,3).
\]

Since

\[
3^2=2^3+1,
\]

we have `P in E_0(Q)`.  Substitution gives

\[
x([2]P)
=
\frac{2(8-8)}{4(8+1)}
=
0,
\]

and

\[
y([2]P)
=
\frac{64+160-8}{8\cdot3\cdot9}
=
1.
\]

Thus

\[
[2](2,3)=(0,1).
\]

### 4.2 Temporal reading

On the universal cover,

\[
z\longmapsto2z.
\]

For the invariant differential,

\[
[2]^*\eta=2\eta.
\]

The temporal scalar is therefore

\[
\alpha=2.
\]

### 4.3 Spatial reading

In any lattice basis,

\[
M_2=
\begin{pmatrix}
2&0\\
0&2
\end{pmatrix},
\]

so

\[
\det M_2=4.
\]

The kernel is the full two-torsion group:

\[
E_0[2]
=
\{O\}\cup
\{(r,0):r^3+1=0\},
\]

which has four points over the algebraic closure.  Hence

\[
|\ker[2]|
=
\deg[2]
=
4.
\]

As a map of complex elliptic curves, `[2]` is a four-sheeted unramified
covering.

### 4.4 Constructive reading

The `x`-coordinate has numerator degree four and denominator degree three, so

\[
\deg[2]=4.
\]

It can be constructed by the tangent formula, by division polynomials, or by
a finite arithmetic circuit.  These are different constructive
presentations of the same morphism.

### 4.5 Dual reading

The map `[2]` is self-dual:

\[
\widehat{[2]}=[2].
\]

Therefore

\[
[2]\circ[2]=[4],
\]

matching

\[
2\cdot2=N(2)=4.
\]

## 5. Example B: the Gaussian degree-two isogeny

Consider

\[
E_i:y^2=x^3-25x.
\]

The point

\[
T=(0,0)
\]

has order two.  Quotienting by

\[
G_i=\{O,T\}
\]

gives

\[
\phi_i:E_i\longrightarrow E_i',
\qquad
E_i':y^2=x^3+100x,
\]

with Vélu formula

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

The kernel is exactly `G_i`.

### 5.1 Actual point calculation

Take

\[
P_i=(-4,6).
\]

It lies on `E_i` because

\[
6^2=(-4)^3-25(-4)=36.
\]

The image is

\[
X
=
\frac{16-25}{-4}
=
\frac94,
\]

and

\[
Y
=
\frac{6(16+25)}{16}
=
\frac{123}{8}.
\]

Thus

\[
\phi_i(-4,6)
=
\left(
\frac94,\frac{123}{8}
\right).
\]

Indeed,

\[
\left(\frac{123}{8}\right)^2
=
\left(\frac94\right)^3
+
100\left(\frac94\right).
\]

### 5.2 Normalized temporal reading

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

Therefore

\[
\phi_i^*\eta_{E_i'}
=
\eta_{E_i}.
\]

The quotient formula is normalized.  If one looked only at these chosen
differentials, the temporal scalar would appear to be `1`.

### 5.3 Reidentification and the Gaussian scalar

Both curves have

\[
j=1728.
\]

Over the complex numbers define

\[
u_i=\frac{1-i}{2}.
\]

Since

\[
100u_i^4=-25,
\]

the coordinate change

\[
\iota_i:E_i'\longrightarrow E_i,
\qquad
(x',y')
\longmapsto
(u_i^2x',u_i^3y')
\]

is an isomorphism.

The composite

\[
\psi_i=\iota_i\circ\phi_i:E_i\longrightarrow E_i
\]

satisfies

\[
\psi_i^*\eta_{E_i}
=
u_i^{-1}\eta_{E_i}
=
(1+i)\eta_{E_i}.
\]

Thus the CM scalar is

\[
\alpha_i=1+i.
\]

The scalar was not absent from the normalized quotient.  It was stored in the
codomain chart and reappeared when the port was closed.

### 5.4 Spatial lattice reading

On the Gaussian lattice with basis `(1,i)`, multiplication by `1+i` is

\[
M_{1+i}
=
\begin{pmatrix}
1&-1\\
1&1
\end{pmatrix}.
\]

Indeed,

\[
(1+i)\cdot1=1+i,
\]

and

\[
(1+i)i=-1+i.
\]

Therefore

\[
\det M_{1+i}=2.
\]

This equals

\[
N(1+i)
=
(1+i)(1-i)
=
2,
\]

and also

\[
\deg\phi_i
=
|\ker\phi_i|
=
2.
\]

### 5.5 Constructive reading

The `x`-coordinate is represented projectively by

\[
(x^2-25:x).
\]

The executable fixture constructs this pair from three explicit occurrences
of one input:

- two occurrences feed `x^2-25`;
- one occurrence supplies the denominator `x`.

This construction multiplicity is `3`, not the isogeny degree `2`.  It is a
property of one arithmetic circuit, not a geometric degree.

### 5.6 Dual reading

Complex conjugation gives

\[
\bar\alpha_i=1-i.
\]

In the lattice basis,

\[
M_{1-i}
=
\begin{pmatrix}
1&1\\
-1&1
\end{pmatrix}.
\]

Then

\[
M_{1-i}M_{1+i}
=
2I.
\]

Classically this is

\[
\widehat\psi_i\circ\psi_i=[2].
\]

The reverse is not `1/(1+i)` as a torus endomorphism.  It is the conjugate
isogeny `1-i`, whose composition with the forward map produces central scale
`[2]`.

## 6. Example C: the Eisenstein degree-three isogeny

Let

\[
E_\omega:y^2=x^3+1.
\]

The points

\[
Q_+=(0,1),
\qquad
Q_-=(0,-1)
\]

together with `O` form a subgroup of order three:

\[
G_\omega=\{O,Q_+,Q_-\}.
\]

The quotient isogeny is

\[
\phi_\omega:E_\omega\longrightarrow E_\omega',
\qquad
E_\omega':y^2=x^3-27,
\]

with formula

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

Its kernel is exactly `G_omega`.

### 6.1 Actual point calculation

Again take

\[
P=(2,3).
\]

Then

\[
X
=
\frac{8+4}{4}
=
3,
\]

and

\[
Y
=
\frac{3(8-8)}{8}
=
0.
\]

Thus

\[
\phi_\omega(2,3)=(3,0),
\]

and the target equation holds:

\[
0^2=3^3-27.
\]

### 6.2 Normalized temporal reading

For

\[
X=x+\frac4{x^2},
\qquad
Y=y\left(1-\frac8{x^3}\right),
\]

we have

\[
\frac{dX}{dx}\frac{y}{Y}=1.
\]

Hence

\[
\phi_\omega^*\eta_{E_\omega'}
=
\eta_{E_\omega}.
\]

As in the Gaussian example, the Vélu quotient is normalized.

### 6.3 Reidentification and the Eisenstein scalar

Both models have

\[
j=0.
\]

Let

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

Therefore

\[
\iota_\omega:E_\omega'\longrightarrow E_\omega,
\qquad
(x',y')
\longmapsto
(u_\omega^2x',u_\omega^3y')
\]

is an isomorphism.

For

\[
\psi_\omega
=
\iota_\omega\circ\phi_\omega,
\]

the invariant differential transforms as

\[
\psi_\omega^*\eta_{E_\omega}
=
u_\omega^{-1}\eta_{E_\omega}
=
(1-\omega)\eta_{E_\omega}.
\]

The temporal CM scalar is therefore

\[
\alpha_\omega=1-\omega.
\]

### 6.4 Spatial lattice reading

In the Eisenstein basis `(1,omega)`,

\[
(1-\omega)\cdot1=1-\omega,
\]

and

\[
(1-\omega)\omega
=
\omega-\omega^2
=
1+2\omega.
\]

Thus

\[
M_{1-\omega}
=
\begin{pmatrix}
1&1\\
-1&2
\end{pmatrix},
\]

and

\[
\det M_{1-\omega}=3.
\]

Equivalently,

\[
N(1-\omega)
=
(1-\omega)(1-\omega^2)
=
3.
\]

This agrees with

\[
\deg\phi_\omega
=
|\ker\phi_\omega|
=
3.
\]

### 6.5 Constructive reading

The projective `x`-coordinate is

\[
(x^3+4:x^2).
\]

The bounded Adva fixture constructs it from five explicit input occurrences:

- three occurrences build `x^3+4`;
- two occurrences build `x^2`.

Again,

\[
d_{\mathrm{occ}}=5
\ne
d_{\mathrm{isog}}=3.
\]

A shared circuit could lower the occurrence count by explicitly constructing
and copying `x^2`; that would be another construction with the same classical
morphism.  The occurrence profile is intensional.

### 6.6 Dual reading

The conjugate scalar is

\[
\bar\alpha_\omega
=
1-\omega^2.
\]

Its lattice matrix is

\[
M_{1-\omega^2}
=
\begin{pmatrix}
2&-1\\
1&1
\end{pmatrix}.
\]

Then

\[
M_{1-\omega^2}M_{1-\omega}
=
3I.
\]

Thus

\[
\widehat\psi_\omega\circ\psi_\omega=[3].
\]

This is a degree-three exact instance of the scaled reverse law.

## 7. Cross-example comparison

The three examples can be summarized as follows.

| map after port closure | complex scalar | lattice matrix | norm / degree | kernel size |
|---|---:|---:|---:|---:|
| `[2]` | `2` | `[[2,0],[0,2]]` | `4` | `4` |
| Gaussian CM | `1+i` | `[[1,-1],[1,1]]` | `2` | `2` |
| Eisenstein CM | `1-omega` | `[[1,1],[-1,2]]` | `3` | `3` |

The coordinate and construction data are:

| quotient map | projective `x` pair | `x`-map degree | fixture leaf occurrences |
|---|---|---:|---:|
| `[2]` | `(x(x^3-8), 4(x^3+1))` | `4` | not lowered in this fixture |
| `phi_i` | `(x^2-25, x)` | `2` | `3` |
| `phi_omega` | `(x^3+4, x^2)` | `3` | `5` |

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

are intrinsic or standard-form classical laws.

The occurrence count is not part of this equality.  It belongs to a selected
construction.

## 8. A decisive contrast with the square and cube calibrations

The earlier maps

\[
x\longmapsto x^2
\quad\text{and}\quad
x\longmapsto x^3
\]

were maps of the affine line.  Their critical and branch behaviour was read
directly from real or complex inverse images.

A complex isogeny

\[
\phi:E\longrightarrow E'
\]

is different.  Its lift is

\[
z\longmapsto\alpha z
\]

with nonzero derivative `alpha` everywhere.  Therefore it is locally
biholomorphic and unramified.

The finite multiplicity

\[
\deg\phi=d
\]

is a covering multiplicity, not ramification at critical points.

However, the coordinate projection

\[
x:E'\longrightarrow\mathbf P^1
\]

is a degree-two branched map.  Consequently the rational function

\[
x\circ\phi:E\longrightarrow\mathbf P^1
\]

can have apparent branch and pole structure even though `phi` itself is
unramified.

This forces a strict typing rule:

\[
\boxed{
\text{branching of a coordinate shadow}
\ne
\text{ramification of the isogeny}.
}
\]

The same warning applies to numerical plots, real components, and selected
coordinate intervals.

## 9. How traditional theory interprets the three features

### 9.1 Temporal feature: tangent representation

Traditional theory reads the temporal scalar as the action on the universal
cover or tangent line:

\[
z\longmapsto\alpha z,
\]

or

\[
\phi^*\eta_{E'}=c_\phi\eta_E.
\]

This is the exact classical version of eigenform preservation under scale.

But it also shows that a scalar feature is chart-relative.  Without a chosen
source--target identification, the feature is a linear arrow between
different tangent lines.

### 9.2 Spatial feature: finite quotient

Traditional theory reads the spatial characteristic as:

\[
E\longrightarrow E/G,
\]

where `G` is a finite subgroup.  The geometric quotient, covering degree,
lattice index, and inverse-image multiplicity are all linked.

The finite kernel is a particularly strong spatial vocabulary because it is
both geometric and constructive.

### 9.3 Constructive feature: rational realization

Traditional theory reads the constructive feature as a rational map generated
from `G`, usually through Vélu formulas, division polynomials, or addition
laws.

The map is finite and executable, but its literal syntax is not canonical.
Classical theory retains the morphism class; Adva retains the checked
presentation and residual.

### 9.4 The common characteristic

The common characteristic is not any one of:

\[
\alpha,
\qquad
M_\alpha,
\qquad
G,
\qquad
(u/v,(s/t)y).
\]

It is the typed isogeny represented by all four, together with the comparison
certificates.

This suggests the general principle:

> A characteristic is an object in a representation groupoid, not merely one
> preferred normal-form value.

The different presentations are related by exact transports, but changing a
basis, model, differential, or circuit is not literal identity.

## 10. Characteristic inference in the elliptic setting

The preceding notes formulate inference as intersection of typed observation
fibres.  The elliptic version is:

\[
\operatorname{Char}_{Q,D}(O_t,O_X,O_K)
=
C_t(O_t)
\cap
C_X(O_X)
\cap
C_K(O_K),
\]

where the candidate family contains isogenies of degree at most `D`.

### 10.1 Temporal constraints

Temporal probes can include:

- exact point pairs `P -> phi(P)`;
- action on torsion points;
- the invariant-differential multiplier;
- repeated endomorphism orbits; and
- the characteristic polynomial on a torsion module.

A finite degree bound makes rational interpolation possible in principle, but
point data alone may remain ambiguous.

### 10.2 Spatial constraints

Spatial probes can include:

- a declared kernel subgroup;
- the degree;
- lattice-index data;
- generic fibre size;
- inverse images of selected opens; and
- field-of-definition information for kernel points.

For a separable isogeny, a complete kernel is far more informative than an
unstructured collection of point evaluations.

### 10.3 Constructive constraints

Constructive observations can include:

- numerator and denominator degrees;
- exact rational-map identities;
- the selected Weierstrass models;
- projective-coordinate circuits;
- copy and occurrence lineage;
- a Vélu reconstruction certificate; and
- a residual for coordinate changes.

### 10.4 Bounded algorithmic skeleton

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
    return Unique(
        phi,
        comparison_certificates(phi),
        representation_residuals(phi),
    )
```

Traditional theory supplies unusually strong transitions between candidate
representations:

\[
\alpha
\longleftrightarrow
M_\alpha,
\]

\[
G
\longmapsto
\phi_G,
\]

\[
\phi
\longmapsto
(\deg\phi,\ker\phi,\widehat\phi),
\]

and, after choosing uniformization,

\[
\phi
\longleftrightarrow
\alpha.
\]

These transitions are the algorithmic reason the three-domain intersection
can be much smaller than a search over arbitrary rational programs.

## 11. Algorithmic advantages visible in the calibration

### 11.1 Kernel-first synthesis

Searching over all rational maps of degree `d` introduces many coefficients
and algebraic constraints.  Searching over finite subgroup schemes or
Galois-stable kernels can be much smaller.

Once a kernel is fixed, Vélu construction produces the quotient model and map.

### 11.2 Norm-first synthesis in CM charts

In a CM endomorphism ring, a degree condition becomes a norm equation:

\[
N(\alpha)=d.
\]

For the present examples:

\[
N(2)=4,
\]

\[
N(1+i)=2,
\]

and

\[
N(1-\omega)=3.
\]

The search is reduced from rational functions to algebraic integers of bounded
norm, followed by exact reconstruction.

### 11.3 Independent cross-checks

The same degree is computed by:

- determinant of a lattice matrix;
- norm of a CM scalar;
- kernel cardinality;
- rational-function degree; and
- dual composition.

A disagreement localizes an error to a chart, kernel, formula, or circuit
rather than producing one undifferentiated failure.

### 11.4 Compact projective circuits

The rational maps should be stored as shared projective circuits, not fully
expanded numerator and denominator trees.

The Adva fixture already shows that even a tiny map has construction choices.
A future lowering should preserve common subexpressions only through explicit
copy and certified sharing, never by value equality or host-language aliasing.

### 11.5 Dual verification

Instead of attempting to invert an isogeny pointwise, one can construct or
infer its dual and verify

\[
\widehat\phi\circ\phi=[d].
\]

This replaces an impossible inverse requirement with an exact scaled reverse
certificate.

## 12. Implications for the larger program-geometric picture

### 12.1 Traditional theory already contains one exact three-domain model

The elliptic case supplies:

\[
\boxed{
\text{temporal multiplier}
\leftrightarrow
\text{spatial finite quotient}
\leftrightarrow
\text{constructive rational map}.
}
\]

This is not metaphorical.  Classical theorems prove the consistency laws.

Therefore the three-domain programme should not claim that such a relation is
entirely absent from traditional mathematics.  What is unusual in the present
programme is the attempt to make the relation:

- observer-relative;
- algorithmically inferable;
- applicable to general programs;
- explicit about variance;
- explicit about raw construction history; and
- residual-bearing across representation changes.

### 12.2 The characteristic is a morphism before it is a value

The examples strongly support replacing a flat feature value by a typed
morphism plus representations:

\[
\phi:E\to E'.
\]

The scalar `alpha` appears only after a port closure or trivialization.  This
matches the need for typed frontiers and argues against prematurely storing
all features as untyped numbers.

### 12.3 Periods are a carrier, not a second copy of time

In classical uniformization, the period lattice is the spatial carrier on
which the temporal multiplier acts:

\[
\alpha:\Lambda\longrightarrow\Lambda.
\]

The periods are not independent time directions.  Their basis records how the
endomorphism is embedded into a two-dimensional integral carrier.

This disciplines the larger two-period intuition: any proposed `p,q`
interpretation should specify whether `p,q` are process directions, lattice
coordinates, homology classes, or observer charts.  Elliptic theory does not
identify these automatically.

### 12.4 Forward and reverse become conjugate channels

For the CM examples:

\[
\alpha
\quad\text{and}\quad
\bar\alpha
\]

are simultaneously defined.  Their product is the central scale:

\[
\bar\alpha\alpha=N(\alpha).
\]

This is a precise classical model in which forward and reverse coexist and
are not temporal alternations.  But it is only a calibration: it does not
prove that every Adva forward/reverse pair is a CM conjugate pair.

### 12.5 Holonomy and chart change

The normalized quotient maps have differential multiplier `1`; the CM
multiplier appears in the isomorphism returning the codomain to the source
model.

Thus one circuit of representations can carry nontrivial chart transport even
when a local map is normalized.  This resembles the earlier holonomy
intuition, but no general holonomy theorem is claimed here.

### 12.6 What Adva adds beyond the classical morphism

Classical algebraic geometry identifies all valid rational presentations of
the same isogeny.  Adva must not.

It retains:

- which input occurrence fed which monomial;
- where copy occurred;
- how a projective pair was assembled;
- which source model and chart were used;
- which reduction or isomorphism was applied; and
- what was forgotten in passing to the extensional morphism.

The characteristic map therefore has the shape

\[
K_{\mathrm{raw}}
\longrightarrow
\operatorname{Isog}(E,E')
\]

with an explicit residual, rather than an identification of raw programs with
classical maps.

## 13. Conservative conclusion

The three examples establish the following bounded result.

For the multiplication-by-two map and the two CM quotient isogenies, one
finite classical object is represented consistently by:

1. a scalar or line map on the universal cover and invariant differential;
2. an integral lattice matrix;
3. a finite kernel and finite covering;
4. an explicit rational map;
5. a projective arithmetic circuit; and
6. a dual map whose composition gives central scale.

The principal exact identities are

\[
N(\alpha)
=
|\det M_\alpha|
=
\deg\phi
=
|\ker\phi|,
\]

and

\[
M_{\bar\alpha}M_\alpha
=
\deg(\phi)I.
\]

These identities strongly support the triadic characteristic method.

They also show that the minimal characteristic carrier must retain typed
representation data:

\[
\boxed{
\text{morphism}
+
\text{port / chart}
+
\text{tangent action}
+
\text{kernel / degree}
+
\text{rational realization}
+
\text{certificate}
+
\text{residual}.
}
\]

No single scalar, degree, kernel, or circuit is sufficient by itself.

## 14. Claims not made

This note does not establish that:

- every Adva characteristic is an isogeny;
- every three-domain system has a period lattice;
- every forward/reverse pair is complex conjugation;
- every reverse process is a dual isogeny;
- every residual is holonomy;
- every program quotient is finite étale;
- elliptic CM explains the full three-computer architecture;
- the `p,q` directions of the larger theory are elliptic periods;
- the three cusps are the three examples in this note;
- rational point probes uniquely determine an unrestricted isogeny;
- real inverse-image cardinality always equals complex degree;
- construction occurrence count is a geometric invariant; or
- the current Python fixture is a stable elliptic-curve implementation.

## 15. Red-team opinion

### 15.1 The examples are deliberately exceptional

The curves with `j=1728` and `j=0` have extra automorphisms and maximal
imaginary-quadratic endomorphism rings.  They were chosen because the scalar,
lattice, kernel, and formula readings are unusually transparent.

A generic elliptic curve over `C` has endomorphism ring `Z`.  The CM
calibration must not be mistaken for generic behaviour.

### 15.2 The temporal label is additional interpretation

Classical theory supplies a morphism and its compositions.  It does not call
them time.  The temporal reading becomes substantive only when a task defines
state evolution, repeated application, causality, or an observation horizon.

### 15.3 Scalars depend on ports

The normalized Vélu maps in this note have differential multiplier `1`, while
the port-closed CM endomorphisms have multipliers `1+i` and `1-omega`.

Any formulation that reports only one scalar without recording the source
and target differential bases is incomplete.

### 15.4 Kernel determines an isogeny only up to target isomorphism

The subgroup `G` canonically determines a quotient in the appropriate
categorical sense, but a literal Weierstrass equation and rational formula
still depend on model choices.

The target model is part of the constructive presentation, not the bare
kernel.

### 15.5 Coordinate branching can be misleading

The rational functions contain denominators, and the `x`-coordinate map may
have critical points.  This does not mean the isogeny itself is ramified over
`C`.

The whole curve map and its coordinate shadow must remain typed separately.

### 15.6 Occurrence count is implementation-dependent

The fixture uses three occurrences for `(x^2-25:x)` and five for
`(x^3+4:x^2)`.  A different explicit sharing DAG can change these numbers
without changing the isogeny.

Only Rust-certified source and occurrence data may support a construction
claim.

### 15.7 Inference can still be difficult

Kernel-first and norm-first search are powerful in these small cases.  Over
larger fields and degrees, one must handle:

- Galois-stable subgroup schemes;
- field extensions;
- isogeny classes;
- modular polynomials;
- non-principal ideals;
- coordinate growth; and
- ambiguous finite observations.

No general polynomial-time characteristic solver follows from the examples.

## 16. Next exact pressure tests

The next sequence should remain classical and finite.

### 16.1 Construct the explicit dual maps

For the degree-two and degree-three quotient maps, construct
`hat(phi_2)` and `hat(phi_3)` as rational maps and verify symbolically:

\[
\widehat\phi_2\circ\phi_2=[2],
\]

and

\[
\widehat\phi_3\circ\phi_3=[3].
\]

This would lift the current lattice-matrix certificate to the coordinate
construction domain.

### 16.2 Hidden-isogeny inference

Generate a bounded family of low-degree quotient isogenies, hide the kernel
and formula, and infer the characteristic from:

- a small set of point images;
- one differential multiplier;
- one kernel or preimage observation; and
- a projective circuit signature.

This would test the actual observation-fibre intersection algorithm.

### 16.3 A non-CM control

Add a rational elliptic curve with a low-degree isogeny but without using a
CM reidentification.  This would separate the general kernel--degree--formula
laws from the exceptional norm-scalar simplification.

### 16.4 Finite-field reduction

Reduce one example modulo good primes and compare:

- geometric kernel;
- rational kernel;
- Frobenius action;
- field of definition; and
- observer-visible fibre cardinality.

This would test how the same intrinsic isogeny changes under a finite
observer field.

## 17. Classical references used for calibration

The classical statements and formulas are calibrated against:

1. Andrew V. Sutherland, *18.783 Elliptic Curves*, Lecture 4, “Isogenies”;
2. Andrew V. Sutherland, Lecture 5, “Isogeny kernels and division
   polynomials”;
3. Andrew V. Sutherland, Lecture 6, “Endomorphism rings”;
4. Andrew V. Sutherland, Lecture 14, “Elliptic curves over C (part I)”;
5. Andrew V. Sutherland, Lecture 16, “Complex multiplication”; and
6. Jacques Vélu, “Isogénies entre courbes elliptiques,” *C. R. Acad. Sci.
   Paris* 273 (1971), 238–241.

The present note derives and checks the displayed special formulas directly;
the references supply the surrounding classical theory.
