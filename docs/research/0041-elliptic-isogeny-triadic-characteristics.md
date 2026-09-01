# Elliptic Isogenies as a Classical Triadic Characteristic Calibration

Status: exploratory research calibration extending
[`0038-triadic-characteristic-inference-calibration.md`](0038-triadic-characteristic-inference-calibration.md),
[`0039-square-map-branch-copy-calibration.md`](0039-square-map-branch-copy-calibration.md),
and
[`0040-cube-equivariance-degree-calibration.md`](0040-cube-equivariance-degree-calibration.md).

This note tests the triadic characteristic method on actual elliptic curves
and actual isogenies.  The aim is not to relabel classical elliptic-curve data
as temporal, spatial, and constructive.  It is to identify one classical
object whose three representations are related by exact theorems.

The central result is:

> A complex elliptic isogeny has a temporal representation on the universal
> cover and tangent line, a spatial representation as a finite quotient and
> covering, and a constructive representation as a rational map generated
> from a finite kernel.  In the CM examples,
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

The executable calibration is
[`tests/python/test_elliptic_isogeny_characteristics.py`](../../tests/python/test_elliptic_isogeny_characteristics.py).

This remains research-local.  It adds no stable elliptic-curve, isogeny,
complex-scalar, period-lattice, kernel, dual, projective-coordinate, or
characteristic API.  SymPy supplies exact external algebra.  Adva checks only
bounded real projective circuits and their source and occurrence lineage.  The
active `ProgramSlice` priority and Rust semantic authority remain unchanged.

## 1. The classical characteristic carrier

The candidate characteristic is an isogeny

\[
\phi:E\longrightarrow E'.
\]

It admits three typed readings:

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
\text{kernel-generated rational map and checked circuit}.
\]

The word “temporal” is additional interpretation.  Classical theory supplies
a composable group morphism; a temporal semantics still requires a declared
state, iteration, task, and observation horizon.

### 1.1 Universal-cover and tangent representation

For lattices \(\Lambda_j\subset\mathbf C\), complex uniformization gives

\[
\Phi_j:
\mathbf C/\Lambda_j
\overset{\sim}{\longrightarrow}
E_j(\mathbf C).
\]

Every torus morphism fixing zero is induced by a unique complex number
\(\alpha\) satisfying

\[
\alpha\Lambda_1\subseteq\Lambda_2,
\]

and is lifted by

\[
z\longmapsto\alpha z.
\]

At the identity, the intrinsic object is a typed line map

\[
d\phi_0:T_0E_1\longrightarrow T_0E_2.
\]

After choosing invariant differentials

\[
\eta_{E_1}=\frac{dx}{2y},
\qquad
\eta_{E_2}=\frac{dX}{2Y},
\]

it is represented by a scalar \(c_\phi\):

\[
\phi^*\eta_{E_2}=c_\phi\eta_{E_1}.
\]

Thus the scalar is relative to source and target ports; the line map is the
more intrinsic temporal characteristic.

### 1.2 Spatial representation

For an endomorphism of \(\mathbf C/\Lambda\), multiplication by \(\alpha\)
has

\[
\ker\phi_\alpha
=
\alpha^{-1}\Lambda/\Lambda
\]

and

\[
\deg\phi_\alpha
=
[\Lambda:\alpha\Lambda].
\]

If \(M_\alpha\) is its integral lattice matrix,

\[
\deg\phi_\alpha
=
|\det M_\alpha|.
\]

In characteristic zero every nonzero isogeny is separable, so

\[
|\ker\phi|=\deg\phi.
\]

For imaginary-quadratic \(\alpha\),

\[
|\det M_\alpha|
=
N(\alpha)
=
\alpha\bar\alpha.
\]

The spatial reading therefore unifies finite kernel, lattice index, generic
fibre cardinality, covering degree, and contravariant inverse image.

### 1.3 Constructive representation

A finite subgroup

\[
G\subset E(\overline{k})
\]

determines a separable quotient isogeny

\[
\phi_G:E\longrightarrow E/G
\]

up to an isomorphism of the codomain.  Vélu formulas construct a model for
\(E/G\) and rational functions for \(\phi_G\):

\[
\boxed{
G
\longmapsto
(E/G,\phi_G).
}
\]

The classical morphism does not determine one arithmetic circuit.  Coordinate
changes, projective scaling, addition chains, common-subexpression choices,
and copy placement remain construction data and must be retained through a
certificate and residual.

### 1.4 Dual as scaled reverse

For an isogeny of degree \(d\), the dual satisfies

\[
\widehat\phi\circ\phi=[d],
\qquad
\phi\circ\widehat\phi=[d].
\]

It is not generally an inverse.  In a CM chart,

\[
\widehat{\phi_\alpha}
=
\phi_{\bar\alpha},
\]

so

\[
\phi_{\bar\alpha}\circ\phi_\alpha
=
[N(\alpha)].
\]

This is an exact classical example in which a canonical reverse channel does
not undo the forward channel but produces a central scale.

## 2. A bounded elliptic triadic form

The characteristic package is

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
(u,v,s,t,\text{kernel witness},\text{circuit}).
\]

The consistency certificate includes

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

The residual records the chosen Weierstrass models, invariant differentials,
lattice bases, field of definition, source--target identification, projective
representative, circuit, and source/occurrence lineage.

## 3. Example A: multiplication by two

Let

\[
E_0:y^2=x^3+1.
\]

The map

\[
[2]:E_0\longrightarrow E_0
\]

has affine form

\[
[2](x,y)
=
\left(
\frac{x(x^3-8)}{4(x^3+1)},
\frac{x^6+20x^3-8}{8y(x^3+1)}
\right).
\]

For \(P=(2,3)\), direct substitution gives

\[
[2](2,3)=(0,1).
\]

On the universal cover,

\[
z\longmapsto2z,
\qquad
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
four and its denominator degree three.  Hence

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

The map is self-dual and

\[
[2]\circ[2]=[4].
\]

## 4. Example B: a Gaussian degree-two quotient

Consider

\[
E_i:y^2=x^3-25x.
\]

The subgroup

\[
G_i=\{O,(0,0)\}
\]

has order two.  Its quotient is

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

For \(P_i=(-4,6)\),

\[
\phi_i(-4,6)
=
\left(
\frac94,
\frac{123}{8}
\right).
\]

The quotient is normalized because

\[
\frac{dX}{dx}\frac{y}{Y}=1,
\qquad
\phi_i^*\eta_{E_i'}=\eta_{E_i}.
\]

Both curves have \(j=1728\).  Set

\[
u_i:=\frac{1-i}{2}.
\]

Since \(100u_i^4=-25\), the map

\[
\iota_i(x',y')
=
(u_i^2x',u_i^3y')
\]

identifies \(E_i'\) with \(E_i\) over \(\mathbf C\).  The closed endomorphism

\[
\psi_i=\iota_i\circ\phi_i
\]

has multiplier

\[
\alpha_i=u_i^{-1}=1+i.
\]

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

Thus

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

The fixture constructs it from three explicit input leaves, not two.  The
construction multiplicity is therefore not the geometric degree.

For the conjugate scalar,

\[
M_{1-i}
=
\begin{pmatrix}
1&1\\
-1&1
\end{pmatrix},
\qquad
M_{1-i}M_{1+i}=2I,
\]

which is the lattice form of

\[
\widehat\psi_i\circ\psi_i=[2].
\]

## 5. Example C: an Eisenstein degree-three quotient

Let

\[
E_\omega:y^2=x^3+1,
\qquad
\omega=e^{2\pi i/3}.
\]

The subgroup

\[
G_\omega
=
\{O,(0,1),(0,-1)\}
\]

has order three.  Its quotient is

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

For \(P=(2,3)\),

\[
\phi_\omega(2,3)=(3,0).
\]

The quotient is normalized:

\[
\frac{dX}{dx}\frac{y}{Y}=1,
\qquad
\phi_\omega^*\eta_{E_\omega'}
=
\eta_{E_\omega}.
\]

Both models have \(j=0\).  Set

\[
u_\omega:=\frac1{1-\omega}.
\]

Because \((1-\omega)^6=-27\), we have

\[
-27u_\omega^6=1.
\]

The map

\[
\iota_\omega(x',y')
=
(u_\omega^2x',u_\omega^3y')
\]

identifies the target with the source.  The closed endomorphism

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

Therefore

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

The bounded fixture uses five explicit input leaves.  Again, circuit
multiplicity and geometric degree are different typed quantities.

For the conjugate scalar,

\[
M_{1-\omega^2}
=
\begin{pmatrix}
2&-1\\
1&1
\end{pmatrix},
\qquad
M_{1-\omega^2}M_{1-\omega}=3I,
\]

which is the lattice form of

\[
\widehat\psi_\omega\circ\psi_\omega=[3].
\]

## 6. Cross-example comparison

| closed map | temporal scalar | lattice determinant | degree | kernel size |
|---|---:|---:|---:|---:|
| `[2]` | `2` | `4` | `4` | `4` |
| Gaussian CM | `1+i` | `2` | `2` | `2` |
| Eisenstein CM | `1-omega` | `3` | `3` | `3` |

The construction profiles are different:

| quotient map | projective `x` pair | `x`-degree | fixture leaves |
|---|---|---:|---:|
| `[2]` | `(x(x^3-8),4(x^3+1))` | `4` | not lowered here |
| `phi_i` | `(x^2-25,x)` | `2` | `3` |
| `phi_omega` | `(x^3+4,x^2)` | `3` | `5` |

The equality

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

belongs to the classical morphism and its standard coordinate form.  The leaf
count belongs to a selected program presentation.

## 7. Coordinate branching is not isogeny ramification

The previous maps \(x\mapsto x^2\) and \(x\mapsto x^3\) were maps of the
affine line.  Their inverse images can branch at critical points.

A nonzero complex isogeny lifts to

\[
z\mapsto\alpha z
\]

with \(\alpha\ne0\), and is locally biholomorphic and unramified.  Its finite
degree is covering multiplicity, not critical ramification.

But the coordinate projection

\[
x:E'\longrightarrow\mathbf P^1
\]

is branched.  Therefore the rational function \(x\circ\phi\) may contain
poles and critical points even though \(\phi\) itself is unramified.  The
required typing rule is

\[
\boxed{
\text{branching of a coordinate shadow}
\ne
\text{ramification of the isogeny}.
}
\]

## 8. How traditional theory understands the three features

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
with exact comparison maps.

This suggests the stable formulation:

> A characteristic is an object in a representation groupoid, not merely one
> preferred normal-form value.

Changing a lattice basis, invariant differential, Weierstrass model,
projective representative, or arithmetic circuit changes the presentation
without necessarily changing the classical morphism.  At the program level,
these changes are not literal identity and their residual must remain
available.

## 9. Relation to the larger programme

### 9.1 What is already classical

Elliptic theory already provides an exact bridge

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

### 9.2 What the programme adds

The proposed extension is to make the bridge

- observer-relative;
- inferable from finite typed observations;
- explicit about covariance and contravariance;
- faithful to raw construction history; and
- residual-bearing across representation changes.

### 9.3 The morphism precedes the scalar

The scalar \(\alpha\) appears only after source and target tangent lines or
period lattices are identified.  This supports a typed-morphism ontology and
argues against treating general characteristics as untyped numbers.

### 9.4 Periods are a carrier

In uniformization the period lattice is the integral carrier on which the
endomorphism acts:

\[
\alpha:\Lambda\longrightarrow\Lambda.
\]

Its two coordinates are not automatically two temporal directions.  Any
larger `p,q` interpretation must specify whether they are periods, homology
coordinates, process directions, or observer charts.

### 9.5 Forward and reverse can be conjugate, not inverse

The CM examples give simultaneous channels

\[
\alpha,
\qquad
\bar\alpha,
\]

with

\[
\bar\alpha\alpha=N(\alpha).
\]

This is a precise model for scaled reverse transport.  It does not prove that
every program reverse is a CM conjugate.

### 9.6 Local normalization can hide global transport

The Vélu quotient maps have differential multiplier `1`; the nontrivial CM
multiplier appears only in the isomorphism that returns the target model to
the source.  A representation circuit can therefore carry nontrivial
transport even when one local edge is normalized.  This resembles the earlier
holonomy intuition, but no general holonomy theorem is asserted.

## 10. Inference and algorithmic implications

For a degree bound \(D\), define a bounded candidate family and intersect
three typed constraint sets:

\[
\operatorname{Char}_{Q,D}(O_t,O_X,O_K)
=
C_t(O_t)
\cap
C_X(O_X)
\cap
C_K(O_K).
\]

Temporal probes may include point images, torsion action, repeated orbits,
and differential multipliers.  Spatial probes may include degree, kernel,
lattice index, inverse images, and field-of-definition data.  Constructive
probes may include rational identities, numerator and denominator degrees,
projective circuits, copy lineage, and Vélu certificates.

The bounded solver remains

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

The examples reveal four concrete algorithmic advantages.

1. **Kernel-first synthesis.**  Searching over finite kernels can be much
   smaller than searching over arbitrary rational maps; Vélu then constructs
   the map.
2. **Norm-first synthesis in CM charts.**  The degree condition becomes
   \(N(\alpha)=d\), reducing the search to algebraic integers of bounded norm.
3. **Independent certificates.**  Determinant, norm, kernel size, coordinate
   degree, and dual composition independently check the same degree.
4. **Dual verification.**  Instead of pointwise inversion, verify
   \(\widehat\phi\circ\phi=[d]\).

No general polynomial-time solver follows from these small cases.

## 11. Conservative conclusion

The three examples show that one classical isogeny can be represented
consistently by

1. point and tangent transport;
2. a complex multiplier after port identification;
3. an integral lattice matrix;
4. a finite kernel and finite covering;
5. an explicit rational map;
6. a checked projective circuit; and
7. a dual map whose composition gives central scale.

The minimal characteristic carrier is therefore

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

The compatibility laws are classical.  Observer-relative inference,
construction provenance, and accountable residual are the proposed
extensions.

## 12. Red-team opinion

1. The \(j=1728\) and \(j=0\) examples are exceptional CM curves.  A generic
   complex elliptic curve has endomorphism ring \(\mathbf Z\).
2. A kernel determines a quotient isogeny only up to target isomorphism; a
   literal Weierstrass equation remains a model choice.
3. Coordinate criticality must not be confused with ramification of the whole
   isogeny.
4. Circuit leaf counts are implementation-dependent and must be certified by
   exact source and occurrence data.
5. Larger inference problems require Galois-stable subgroup schemes, field
   extensions, modular polynomials, ideal classes, and ambiguity management.

## 13. Next exact pressure tests

1. Construct explicit dual degree-two and degree-three rational maps and
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
4. Reduce an example modulo good primes and compare geometric kernel, rational
   kernel, Frobenius action, and observer-visible fibres.

## 14. Classical references

The surrounding theory is calibrated against:

1. Andrew V. Sutherland, *18.783 Elliptic Curves*, Lecture 4, “Isogenies”;
2. Lecture 5, “Isogeny kernels and division polynomials”;
3. Lecture 6, “Endomorphism rings”;
4. Lecture 14, “Elliptic curves over C (part I)”;
5. Lecture 16, “Complex multiplication”; and
6. Jacques Vélu, “Isogénies entre courbes elliptiques,” *C. R. Acad. Sci.
   Paris* 273 (1971), 238–241.
