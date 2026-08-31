# Elliptic Isogenies as Triadic Characteristics

Status: exploratory classical calibration extending
[`0038-triadic-characteristic-inference-calibration.md`](0038-triadic-characteristic-inference-calibration.md),
[`0039-square-map-branch-copy-calibration.md`](0039-square-map-branch-copy-calibration.md),
and
[`0040-cube-equivariance-degree-calibration.md`](0040-cube-equivariance-degree-calibration.md).

This note raises the difficulty of the characteristic-inference programme by
moving from polynomial maps on one affine line to genuine morphisms of
elliptic curves. It studies three exact examples:

1. multiplication by two on the equianharmonic curve
   \(E_0:y^2=x^3+1\);
2. a rational two-isogeny between two \(j=1728\) models; and
3. a rational three-isogeny between two \(j=0\) models.

The examples are chosen so that the temporal, spatial, and constructive
readings are all classical and independently computable.

The central finding is:

> A classical isogeny is an exact finite calibration of a triadic
> characteristic. Its temporal reading is the group action and the induced map
> on the tangent line or invariant differential. Its spatial reading is the
> finite kernel, lattice index, covering degree, and generic inverse fibre. Its
> constructive reading is a finite rational map obtained from kernel data,
> classically through division polynomials or Vélu-type formulae. These are not
> three analogies: traditional elliptic-curve theory proves exact coherence
> laws among them.

For complex multiplication, the coherence becomes especially transparent.
After choosing a complex uniformization, an endomorphism is multiplication by
an imaginary-quadratic number \(\alpha\), and

\[
\boxed{
\deg(\phi_\alpha)
=
|\ker\phi_\alpha|
=
[\Lambda:\alpha\Lambda]
=
|\det M_\alpha|
=
N(\alpha).
}
\]

The dual isogeny is represented by the conjugate characteristic
\(\bar\alpha\), and

\[
\boxed{
\widehat\phi_\alpha\circ\phi_\alpha
=
[N(\alpha)].
}
\]

Thus the reverse or dual process is not an inverse. It closes only after a
degree-scaling endomorphism. This gives a precise classical model for the
earlier intuition that forward and reverse processes may coexist without
being simple inverses.

This remains a research note. It does not add a stable elliptic-curve,
isogeny, complex-multiplication, pullback, characteristic, graph, relation, or
spectrum API. The exact rational and complex calculations use SymPy as an
external mathematical oracle. Adva is used only for bounded, checked
projective coordinate circuits; Rust remains the authority for program,
source, occurrence, history, and certificate identity. No entry is promoted
to `claims.toml`, and the active `ProgramSlice` priority is unchanged.

## 1. Why isogenies are the right next calibration

### 1.1 Polynomial maps were only shadows of the desired structure

The square and cube calibrations studied maps

\[
x\longmapsto x^2,
\qquad
x\longmapsto x^3.
\]

They exposed several important distinctions:

- forward value evolution versus reverse fibres;
- real versus complex branch counts;
- algebraic degree versus construction occurrence multiplicity;
- invariance versus equivariance;
- sequential words versus copied arithmetic DAGs.

But these maps did not carry an intrinsic group law. Their composition was
ordinary function composition, and their spatial branching depended strongly
on the chosen affine coordinate.

An elliptic curve supplies more structure:

- a smooth projective genus-one curve;
- a distinguished origin \(O\);
- an abelian group law;
- a one-dimensional tangent space at \(O\);
- invariant differentials;
- a complex-torus uniformization over \(\mathbf C\); and
- finite morphisms compatible with all of the above.

An isogeny

\[
\phi:E\longrightarrow E'
\]

is therefore a stronger characteristic candidate than a bare polynomial map.
It is simultaneously:

- a group homomorphism;
- a finite geometric map;
- a map of tangent lines;
- a map of period lattices; and
- an explicitly constructible rational transformation.

### 1.2 One source object, not three unrelated examples

The calibration fixes one isogeny \(\phi\) and reads it through three typed
interfaces.

The **temporal interface** follows points:

\[
P,\phi(P),\phi^2(P),\ldots
\]

when domain and codomain have been identified, or follows a composable chain
of isogenies otherwise. Infinitesimally it reads the induced map

\[
d\phi_O:T_OE\longrightarrow T_OE'.
\]

After choosing nonzero invariant differentials \(\omega_E,\omega_{E'}\), this
map is represented by a scalar \(c_\phi\) defined by

\[
\phi^*\omega_{E'}
=
c_\phi\,\omega_E.
\]

The **spatial interface** reads inverse images, the finite kernel, and the
covering structure. In characteristic zero a nonzero isogeny is separable, and

\[
\deg\phi
=
|\ker\phi|.
\]

Over \(\mathbf C\), a complex uniformization identifies an isogeny with a
linear map between lattices, so its degree is a lattice index.

The **constructive interface** reads the finite rational expressions that
realize the map in chosen Weierstrass coordinates. Given an admissible finite
kernel, classical formulae construct the quotient curve and its isogeny.

The hypothesis being tested is not that all three interfaces contain the same
data. It is that they are typed presentations of one finite characteristic
with exact compatibility certificates.

## 2. The classical triadic dictionary

Let

\[
E(\mathbf C)\simeq\mathbf C/\Lambda,
\qquad
E'(\mathbf C)\simeq\mathbf C/\Lambda'.
\]

A complex analytic homomorphism is induced by a scalar
\(\alpha\in\mathbf C\) satisfying

\[
\alpha\Lambda\subseteq\Lambda'.
\]

Write the induced isogeny as

\[
\phi_\alpha:
\mathbf C/\Lambda
\longrightarrow
\mathbf C/\Lambda',
\qquad
z\bmod\Lambda
\longmapsto
\alpha z\bmod\Lambda'.
\]

### 2.1 Temporal reading

On the universal cover, temporal evolution is simply

\[
z\longmapsto\alpha z.
\]

On the tangent line at the origin,

\[
d\phi_{\alpha,0}(v)=\alpha v.
\]

With compatible invariant differentials, the pullback multiplier is the same
scalar:

\[
\phi_\alpha^*\omega_{E'}
=
\alpha\,\omega_E.
\]

Thus the traditional local temporal characteristic is not an arbitrary
eigenvalue. It is the actual tangent representation of the isogeny.

### 2.2 Spatial reading

The kernel is

\[
\ker\phi_\alpha
\simeq
\alpha^{-1}\Lambda'/\Lambda.
\]

When source and target lattices are the same,

\[
\ker\phi_\alpha
\simeq
\alpha^{-1}\Lambda/\Lambda.
\]

If \(M_\alpha\) is the integral matrix of multiplication by \(\alpha\) in a
chosen lattice basis, then

\[
|\ker\phi_\alpha|
=
|\det M_\alpha|.
\]

For a separable isogeny,

\[
\deg\phi_\alpha
=
|\ker\phi_\alpha|.
\]

This degree is also the number of points in a generic geometric fibre,
counted with multiplicity.

### 2.3 Constructive reading

Choose Weierstrass equations for \(E\) and \(E'\). The same map becomes

\[
\phi(x,y)
=
\left(
\frac{N_x(x)}{D_x(x)},
\frac{N_y(x,y)}{D_y(x,y)}
\right).
\]

The coordinate expression is a chart presentation, not the intrinsic
isogeny. It may have denominators and apparent poles at kernel points; in the
projective curve those points map regularly to \(O\).

The classical kernel-to-map direction is:

\[
\boxed{
\text{finite subgroup }K
\longrightarrow
E/K
\longrightarrow
\phi_K:E\to E/K.
}
\]

Vélu's formulae make this constructive for Weierstrass models. This is close
to the current Adva ambition: a finite, typed, auditable characteristic should
unfold into an executable construction.

### 2.4 Coherence laws

The three readings satisfy:

\[
\boxed{
\text{tangent multiplier}
\quad\leftrightarrow\quad
\text{lattice action}
\quad\leftrightarrow\quad
\text{kernel and degree}
\quad\leftrightarrow\quad
\text{rational construction}.
}
\]

For a CM endomorphism by \(\alpha\),

\[
N(\alpha)
=
\alpha\bar\alpha
=
|\det M_\alpha|
=
|\ker\phi_\alpha|
=
\deg\phi_\alpha.
\]

The dual isogeny corresponds to the conjugate lattice action:

\[
M_{\bar\alpha}M_\alpha
=
N(\alpha)I.
\]

This is the classical exact certificate joining temporal, spatial, and
constructive data.

## 3. Calibration I: multiplication by two

Consider

\[
E_0:
\qquad
y^2=x^3+1.
\]

This curve has \(j=0\), but the endomorphism

\[
[2]:E_0\to E_0
\]

exists on every elliptic curve. We use this model because it has a simple
rational point

\[
P=(2,3).
\]

### 3.1 Temporal point calculation

The tangent slope at \(P\) is

\[
m
=
\frac{3x_P^2}{2y_P}
=
\frac{12}{6}
=
2.
\]

Therefore

\[
x_{2P}
=
m^2-2x_P
=
4-4
=
0,
\]

and

\[
y_{2P}
=
m(x_P-x_{2P})-y_P
=
2(2)-3
=
1.
\]

Hence

\[
\boxed{
[2](2,3)=(0,1).
}
\]

### 3.2 Constructive coordinate formula

For a generic point \((x,y)\in E_0\),

\[
x([2]P)
=
\frac{x(x^3-8)}{4(x^3+1)},
\]

and

\[
y([2]P)
=
\frac{x^6+20x^3-8}
     {8y(x^3+1)}.
\]

Since \(y^2=x^3+1\), the second denominator may also be written \(8y^3\).

The executable fixture checks exactly that these expressions preserve the
curve equation. It also checks that the projective \(x\)-coordinate pair

\[
\bigl(
x(x^3-8),\,
4(x^3+1)
\bigr)
\]

is emitted by a checked Adva circuit with explicit copies and multiplications.

### 3.3 Temporal infinitesimal characteristic

Let

\[
\omega=\frac{dx}{2y}.
\]

The rational formula satisfies

\[
[2]^*\omega
=
2\omega.
\]

So the temporal tangent characteristic is

\[
c_{[2]}=2.
\]

### 3.4 Spatial characteristic

On any complex uniformization,

\[
z\longmapsto2z.
\]

In a lattice basis, the matrix is

\[
M_2
=
\begin{pmatrix}
2&0\\
0&2
\end{pmatrix}.
\]

Therefore

\[
|\det M_2|=4.
\]

The kernel is the two-torsion subgroup

\[
E_0[2].
\]

Its finite affine points have \(y=0\) and

\[
x^3+1=0.
\]

Together with \(O\), there are four geometric kernel points:

\[
|\ker[2]|=4.
\]

Thus

\[
\boxed{
c_t=2,
\qquad
d_X=4,
\qquad
|\ker|=4.
}
\]

The temporal scalar and spatial degree are not numerically equal. They are
linked by the norm law:

\[
N(2)=2\cdot2=4.
\]

### 3.5 Dual characteristic

The dual of \([2]\) is again \([2]\), but it is not the inverse. Instead,

\[
[2]\circ[2]
=
[4].
\]

Equivalently,

\[
M_2M_2
=
4I.
\]

This is the first exact warning against interpreting the reverse computation
as a literal inverse.

## 4. Calibration II: a \(j=1728\) two-isogeny

Take the quartic-twist pair

\[
E_i:
\qquad
y^2=x^3-25x,
\]

and

\[
E_i':
\qquad
y^2=x^3+100x.
\]

Both have

\[
j=1728.
\]

The source has the rational two-torsion point

\[
T=(0,0).
\]

### 4.1 Kernel and rational quotient map

The subgroup

\[
K_2=\{O,T\}
\]

defines a degree-two quotient isogeny

\[
\phi_2:E_i\longrightarrow E_i'.
\]

A normalized formula is

\[
\boxed{
\phi_2(x,y)
=
\left(
\frac{x^2-25}{x},
\frac{y(x^2+25)}{x^2}
\right).
}
\]

The denominators vanish at \(T\), but this is the projective statement that
\(T\) maps to the origin \(O\) of the target curve.

The fixture verifies symbolically that

\[
\left(\frac{y(x^2+25)}{x^2}\right)^2
=
\left(\frac{x^2-25}{x}\right)^3
+
100\left(\frac{x^2-25}{x}\right)
\]

modulo the source equation.

### 4.2 Actual rational point

The point

\[
P=(-4,6)
\]

lies on \(E_i\), since

\[
6^2=(-4)^3-25(-4)=36.
\]

Its image is

\[
x(\phi_2(P))
=
\frac{16-25}{-4}
=
\frac94,
\]

and

\[
y(\phi_2(P))
=
6\frac{16+25}{16}
=
\frac{123}{8}.
\]

Hence

\[
\boxed{
\phi_2(-4,6)
=
\left(\frac94,\frac{123}{8}\right).
}
\]

The target equation is satisfied exactly.

### 4.3 Normalized differential

Let

\[
\omega_i=\frac{dx}{2y},
\qquad
\omega_i'=\frac{dX}{2Y}.
\]

For the displayed quotient formula,

\[
\phi_2^*\omega_i'
=
\omega_i.
\]

Thus the rational Vélu-style quotient is normalized:

\[
c_{\phi_2}=1
\]

relative to these two chosen Weierstrass differentials.

This does **not** mean the associated CM endomorphism has multiplier \(1\).
The quotient curve has not yet been identified with the source curve.

### 4.4 Re-identification with the CM curve

Over \(\mathbf C\), choose

\[
u_i=\frac{1-i}{2}.
\]

Then

\[
u_i^4=-\frac14,
\]

so the coordinate change

\[
\iota_i:
E_i'\longrightarrow E_i,
\qquad
(X,Y)
\longmapsto
(u_i^2X,u_i^3Y)
\]

is an isomorphism, because

\[
100u_i^4=-25.
\]

The pullback of invariant differentials is

\[
\iota_i^*\omega_i
=
u_i^{-1}\omega_i'.
\]

Since

\[
u_i^{-1}=1+i,
\]

the composite endomorphism

\[
\psi_i
=
\iota_i\circ\phi_2:
E_i\longrightarrow E_i
\]

has temporal multiplier

\[
\boxed{
c_{\psi_i}=1+i.
}
\]

The normalized quotient map and the CM endomorphism are therefore two charts
of the same construction, related by an explicit codomain isomorphism.

### 4.5 Gaussian lattice calculation

Use the Gaussian lattice basis

\[
(1,i).
\]

Multiplication by \(1+i\) sends

\[
1\longmapsto1+i,
\]

and

\[
i\longmapsto-1+i.
\]

Thus

\[
M_{1+i}
=
\begin{pmatrix}
1&-1\\
1&1
\end{pmatrix},
\]

with

\[
\det M_{1+i}=2.
\]

The conjugate characteristic \(1-i\) has matrix

\[
M_{1-i}
=
\begin{pmatrix}
1&1\\
-1&1
\end{pmatrix}.
\]

Their product is

\[
M_{1-i}M_{1+i}
=
2I.
\]

Therefore

\[
\boxed{
N(1+i)=2
=
|\ker\phi_2|
=
\deg\phi_2.
}
\]

The dual isogeny corresponds, after compatible identifications, to the
conjugate Gaussian factor:

\[
\widehat\psi_i\circ\psi_i=[2].
\]

### 4.6 Triadic reading

This example supplies:

\[
\text{temporal feature}
=
1+i,
\]

\[
\text{spatial feature}
=
\text{index-two sublattice and two-point kernel},
\]

and

\[
\text{constructive feature}
=
\left(
\frac{x^2-25}{x},
\frac{y(x^2+25)}{x^2}
\right)
\]

together with the chart isomorphism \(\iota_i\).

The shared characteristic is not just the scalar \(1+i\), nor just the
kernel, nor just the rational formula. It is the certified relation among all
three.

## 5. Calibration III: a \(j=0\) three-isogeny

Take

\[
E_\omega:
\qquad
y^2=x^3+1,
\]

and

\[
E_\omega':
\qquad
y^2=x^3-27.
\]

Both have

\[
j=0.
\]

The source contains the order-three subgroup

\[
K_3
=
\{O,(0,1),(0,-1)\}.
\]

### 5.1 Kernel and rational quotient map

The quotient by \(K_3\) is the degree-three isogeny

\[
\phi_3:E_\omega\longrightarrow E_\omega'
\]

with normalized formula

\[
\boxed{
\phi_3(x,y)
=
\left(
\frac{x^3+4}{x^2},
\frac{y(x^3-8)}{x^3}
\right).
}
\]

The kernel points \(x=0\) map projectively to \(O\).

The fixture checks the exact identity

\[
\left(
\frac{y(x^3-8)}{x^3}
\right)^2
=
\left(
\frac{x^3+4}{x^2}
\right)^3
-27
\]

modulo \(y^2=x^3+1\).

### 5.2 Actual rational point

For

\[
P=(2,3),
\]

we obtain

\[
x(\phi_3(P))
=
\frac{8+4}{4}
=
3,
\]

and

\[
y(\phi_3(P))
=
3\frac{8-8}{8}
=
0.
\]

Hence

\[
\boxed{
\phi_3(2,3)=(3,0).
}
\]

The image is the rational two-torsion point of \(E_\omega'\).

### 5.3 Normalized differential

With

\[
\omega_\omega=\frac{dx}{2y},
\qquad
\omega_\omega'=\frac{dX}{2Y},
\]

the formula satisfies

\[
\phi_3^*\omega_\omega'
=
\omega_\omega.
\]

Again, the quotient map is normalized relative to the selected source and
target models.

### 5.4 Re-identification with the CM curve

Let

\[
\omega
=
e^{2\pi i/3},
\qquad
\omega^2+\omega+1=0.
\]

Choose

\[
u_\omega
=
\frac{1}{1-\omega}.
\]

Since

\[
(1-\omega)^6=-27,
\]

we have

\[
u_\omega^6=-\frac1{27}.
\]

Therefore

\[
\iota_\omega:
E_\omega'\longrightarrow E_\omega,
\qquad
(X,Y)
\longmapsto
(u_\omega^2X,u_\omega^3Y)
\]

is an isomorphism.

Its differential multiplier is

\[
u_\omega^{-1}
=
1-\omega.
\]

Consequently the composite

\[
\psi_\omega
=
\iota_\omega\circ\phi_3
\]

has temporal CM characteristic

\[
\boxed{
c_{\psi_\omega}
=
1-\omega.
}
\]

### 5.5 Eisenstein lattice calculation

Use the Eisenstein basis

\[
(1,\omega).
\]

Multiplication by \(1-\omega\) sends

\[
1\longmapsto1-\omega,
\]

and

\[
\omega
\longmapsto
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

with

\[
\det M_{1-\omega}=3.
\]

The conjugate characteristic is

\[
1-\omega^2=2+\omega,
\]

whose matrix is

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

Therefore

\[
\boxed{
N(1-\omega)=3
=
|\ker\phi_3|
=
\deg\phi_3.
}
\]

The dual relation is

\[
\widehat\psi_\omega\circ\psi_\omega=[3].
\]

### 5.6 Triadic reading

This example supplies:

\[
\text{temporal feature}
=
1-\omega,
\]

\[
\text{spatial feature}
=
\text{index-three sublattice and three-point kernel},
\]

and

\[
\text{constructive feature}
=
\left(
\frac{x^3+4}{x^2},
\frac{y(x^3-8)}{x^3}
\right)
\]

together with the chart isomorphism \(\iota_\omega\).

The appearance of the Eisenstein norm

\[
a^2-ab+b^2
\]

is not decorative. For \(1-\omega\), it is exactly the covering degree.

## 6. The three examples in one table

| example | temporal multiplier \(\alpha\) | lattice matrix \(M_\alpha\) | spatial degree | kernel order | constructive presentation |
|---|---:|---|---:|---:|---|
| multiplication by two | \(2\) | \(\begin{psmallmatrix}2&0\\0&2\end{psmallmatrix}\) | \(4\) | \(4\) | duplication formula |
| \(j=1728\) quotient | \(1+i\) after CM identification | \(\begin{psmallmatrix}1&-1\\1&1\end{psmallmatrix}\) | \(2\) | \(2\) | rational two-isogeny |
| \(j=0\) quotient | \(1-\omega\) after CM identification | \(\begin{psmallmatrix}1&1\\-1&2\end{psmallmatrix}\) | \(3\) | \(3\) | rational three-isogeny |

In all three cases,

\[
\boxed{
\alpha\bar\alpha
=
|\det M_\alpha|
=
|\ker\phi_\alpha|
=
\deg\phi_\alpha.
}
\]

This is the strongest exact classical support so far for a common
three-domain characteristic.

## 7. What traditional theory says the characteristic really is

### 7.1 It is not merely a scalar

The scalar \(\alpha\) exists only after choosing:

- a complex uniformization;
- a basis or fractional ideal for the period lattice;
- an identification of source and target CM curves; and
- compatible invariant differentials.

Without these choices, the intrinsic temporal datum is the line map

\[
d\phi_O:T_OE\longrightarrow T_OE'.
\]

Thus an absolute scalar should be treated as a chart coordinate on a typed
one-dimensional morphism.

### 7.2 It is not merely a kernel

A finite subgroup \(K\subset E\) determines a quotient isogeny up to a
suitable target isomorphism, but the target model and normalization matter.
The same kernel can be presented through different Weierstrass coordinates,
different rational formulae, and different differential scalars.

### 7.3 It is not merely a rational formula

Coordinate formulae can obscure intrinsic smoothness. The denominators of the
two- and three-isogenies vanish at kernel points, but the projective morphisms
are regular there.

Conversely, the \(x\)-coordinate shadow can exhibit critical points and
branching even when the full isogeny is unramified. A spatial observer of

\[
x:E\longrightarrow\mathbf P^1
\]

sees a different branch structure from an observer of the full elliptic
curve.

### 7.4 A safer characteristic package

The present calibration suggests a research object of the form

\[
\mathsf{EllChar}_Q(\phi)
=
\left(
E,E',\phi;
d\phi_O;
K_\phi;
M_{\phi,Q};
\deg\phi;
\Phi_{\mathrm{coord},Q};
\widehat\phi;
\Pi_Q;
R_Q
\right).
\]

Its components are:

- `E`, `E'`: typed source and target curves;
- `phi`: the intrinsic isogeny;
- `dphi_O`: the temporal tangent map;
- `K_phi`: the finite kernel subgroup scheme or bounded point presentation;
- `M_(phi,Q)`: a lattice matrix in a declared complex observer chart;
- `deg phi`: the intrinsic finite degree;
- `Phi_(coord,Q)`: a coordinate or projective-circuit presentation;
- `hat phi`: the dual characteristic;
- `Pi_Q`: checked compatibility certificates; and
- `R_Q`: chart, field-of-definition, source, occurrence, and normalization
  residuals.

This is deliberately a research package, not a stable Rust type.

## 8. Exact compatibility diagrams

### 8.1 Point evaluation and coordinate construction

For a checked coordinate presentation,

\[
\begin{CD}
E @>{\phi}>> E'\\
@V{\operatorname{coord}}VV
@VV{\operatorname{coord}'}V\\
\mathbf P^2 @>>{\Phi_{\mathrm{coord}}}> \mathbf P^2
\end{CD}
\]

should commute on its declared chart, with kernel points handled
projectively.

### 8.2 Uniformization and lattice action

Over \(\mathbf C\),

\[
\begin{CD}
\mathbf C @>{z\mapsto\alpha z}>> \mathbf C\\
@VVV @VVV\\
\mathbf C/\Lambda @>>{\phi_\alpha}> \mathbf C/\Lambda'
\end{CD}
\]

commutes exactly.

### 8.3 Differential compatibility

At the origin,

\[
d\phi_O
\]

is the tangent shadow of the same scalar \(\alpha\). In differential-form
language,

\[
\phi^*\omega_{E'}
=
c_\phi\omega_E.
\]

For the normalized rational quotient maps in the two CM examples,

\[
c_\phi=1.
\]

After the codomain is identified with the source CM curve,

\[
c_{\iota\circ\phi}
=
1+i
\]

or

\[
c_{\iota\circ\phi}
=
1-\omega.
\]

This shows exactly where chart calibration enters the temporal feature.

### 8.4 Kernel, lattice quotient, and degree

For the CM endomorphism chart,

\[
\ker\phi_\alpha
\simeq
\alpha^{-1}\Lambda/\Lambda.
\]

Therefore

\[
|\ker\phi_\alpha|
=
[\Lambda:\alpha\Lambda].
\]

An integral basis converts this to

\[
[\Lambda:\alpha\Lambda]
=
|\det M_\alpha|.
\]

Traditional theory then identifies this with the algebraic degree.

### 8.5 Duality

The dual isogeny is characterized intrinsically by

\[
\widehat\phi\circ\phi
=
[\deg\phi]_E,
\]

and

\[
\phi\circ\widehat\phi
=
[\deg\phi]_{E'}.
\]

In the CM chart this is simply

\[
\bar\alpha\alpha=N(\alpha).
\]

This is a precise, nontrivial forward--reverse closure law.

## 9. Relation to the previous affine, square, and cube calibrations

### 9.1 The variance signature survives

For an isogeny \(\phi:E\to E'\):

- points and constructions move covariantly;
- regions and predicates move contravariantly by inverse image.

Thus the previous variance signature remains:

\[
(+,-,+).
\]

But the spatial pullback now acts on opens of a curve, not merely intervals of
an affine line.

### 9.2 Full-map degree and coordinate-shadow branching must be separated

For \(x\mapsto x^2\), algebraic degree, generic complex fibre count, and
branching were properties of the whole map.

For an elliptic isogeny, the full map in characteristic zero is unramified,
while the projected rational function

\[
x\circ\phi:E\to\mathbf P^1
\]

can have its own critical points and branch behaviour.

Therefore:

\[
\boxed{
\text{branching of an observer projection}
\ne
\text{ramification of the intrinsic process}.
}
\]

This is a major refinement of the observer-relative characteristic idea.

### 9.3 Construction multiplicity still differs from geometric degree

The checked projective coordinate circuits use explicit copies to build
powers and shared numerators or denominators. Their occurrence counts depend
on:

- the selected coordinate formula;
- common-subexpression sharing;
- available primitive operations;
- lowering strategy; and
- the chosen output frontier.

They need not equal the isogeny degree or kernel order.

Traditional elliptic-curve theory therefore reinforces the typed degree
vector introduced in `0040`.

### 9.4 A kernel is a stronger finite vocabulary than sample values

Finite point probes can fit many rational maps. A finite subgroup satisfying
the elliptic group laws determines a quotient structure with much stronger
constraints.

This suggests a general learning principle:

> When available, learn a finite compositional kernel or relation carrier,
> rather than only fitting values of the unfolded map.

For elliptic curves, Vélu's construction makes this principle exact.

## 10. Algorithmic meaning

### 10.1 Kernel-to-map compilation

The traditional input is a finite kernel presentation:

\[
K=\langle P\rangle
\quad\text{or}\quad
\psi_K(x).
\]

The output is:

\[
(E',\phi_K).
\]

This is already a finite characteristic compiler. It turns a spatial finite
subgroup into a constructive rational program whose temporal execution is
group-compatible.

### 10.2 Degree prediction without solving every fibre

Once the lattice matrix or kernel order is certified,

\[
\deg\phi
=
|\det M_\phi|
=
|K|
\]

predicts the generic geometric fibre size. It is unnecessary to solve a new
degree-\(\ell\) equation for every target point merely to know the number of
generic sheets.

### 10.3 Dual construction

Given \(\phi\), one can construct \(\widehat\phi\) and check

\[
\widehat\phi\phi=[\deg\phi].
\]

This supplies an unusually strong bidirectional certificate:

- forward computation;
- reverse or dual computation;
- a scalar closure law; and
- an exact obstruction to treating the dual as an inverse.

### 10.4 Projective circuits avoid artificial singularities

The executable fixture stores the \(x\)-coordinate maps as pairs

\[
(N_x,D_x)
\]

rather than dividing prematurely. This preserves a finite projective
construction and avoids treating a denominator zero as an ordinary floating
point failure.

The three checked pairs are:

\[
\left(
x(x^3-8),\,
4(x^3+1)
\right),
\]

\[
\left(
x^2-25,\,
x
\right),
\]

and

\[
\left(
x^3+4,\,
x^2
\right).
\]

For a generic target coordinate \(u\), the equations

\[
N_x-uD_x=0
\]

have degrees \(4\), \(2\), and \(3\), matching the respective isogeny
degrees.

### 10.5 Classical complexity already distinguishes representation choices

Naive Vélu evaluation for a prime-degree isogeny scales essentially linearly
in the degree. Modern square-root Vélu methods reorganize the kernel
calculation through baby-step--giant-step and fast polynomial techniques,
achieving soft-\(O(\sqrt\ell)\) field operations in the supported setting.

This matters for the present programme:

> The finite characteristic is not only a semantic quotient. Its internal
> representation and factorization determine whether extracting or unfolding
> it is computationally useful.

The same isogeny can be represented by:

- an explicit kernel point list;
- a kernel polynomial;
- a lattice or ideal;
- a composition of prime-degree isogenies;
- a rational map; or
- a projective arithmetic circuit.

These are classically equivalent only with explicit conversion algorithms and
costs.

## 11. Theoretical significance for the larger programme

### 11.1 A characteristic can be a morphism with several exact shadows

The previous examples risked suggesting that a characteristic is a compressed
number, tuple, or circuit. Elliptic curves show a more stable formulation:

> A characteristic may be an intrinsic morphism whose temporal, spatial, and
> constructive features are functorial shadows.

This reverses the direction of ontology. The common object is not assembled
by forcing three feature vectors to agree. The common object is the isogeny;
the feature vectors are derived readings.

### 11.2 Traditional theory supplies a complete local coherence theorem

In the CM examples, the following quantities coincide exactly:

\[
N(\alpha),
\quad
|\det M_\alpha|,
\quad
[\Lambda:\alpha\Lambda],
\quad
|\ker\phi_\alpha|,
\quad
\deg\phi_\alpha.
\]

Traditional theory has already proved the coherence that our general
three-domain programme is seeking.

The new work is not to rename these facts. It is to identify which part of
this pattern survives for general programs:

- What replaces the period lattice?
- What replaces the finite kernel?
- What replaces the tangent multiplier?
- What replaces the algebraic norm?
- What replaces the dual isogeny?
- What replaces Vélu's kernel-to-map compiler?
- Which equalities remain exact, and which require residuals?

### 11.3 The dual relation is a model for non-invertible reversal

The law

\[
\widehat\phi\phi=[\deg\phi]
\]

has the desired qualitative shape:

- the reverse map exists;
- it is canonical;
- it is not generally an inverse;
- forward followed by reverse produces a controlled scale action; and
- the scale is the spatial degree.

This may be the cleanest traditional mathematical model yet for the proposed
forward/reverse interaction in the three-computer system.

### 11.4 Chart changes explain apparent disagreement among features

The normalized quotient isogenies have differential multiplier \(1\), while
their CM endomorphism presentations have multipliers \(1+i\) and
\(1-\omega\).

There is no contradiction. The source and target tangent lines were
identified differently.

Thus feature comparison across domains or charts must include transport:

\[
c_{\iota\circ\phi}
=
c_\iota c_\phi.
\]

A scalar characteristic without its chart transition is incomplete.

### 11.5 The finite observer should declare its geometric level

An observer may inspect:

1. the full smooth projective curve;
2. the real locus;
3. the complex torus;
4. the \(x\)-coordinate line;
5. a finite torsion subgroup;
6. a formal neighbourhood of \(O\); or
7. a numerical point sample.

These observers infer different branch, degree, and symmetry profiles. The
intrinsic isogeny coordinates them, but does not make their observations
identical.

## 12. Conservative conclusion

The three computations establish, in bounded exact form, that:

1. a classical elliptic isogeny supports temporal, spatial, and constructive
   readings of one intrinsic map;
2. the tangent multiplier, lattice action, finite kernel, degree, and rational
   map satisfy exact compatibility laws;
3. in CM charts, degree is the imaginary-quadratic norm of the temporal
   multiplier;
4. multiplication by two yields the profile \(2\mapsto4\);
5. the \(j=1728\) two-isogeny yields \(1+i\mapsto2\);
6. the \(j=0\) three-isogeny yields \(1-\omega\mapsto3\);
7. the dual characteristic is conjugate in CM coordinates and composes to
   multiplication by the degree;
8. normalized quotient maps and CM endomorphism maps differ by explicit chart
   isomorphisms;
9. projective coordinate circuits provide a finite constructive
   representation without premature division; and
10. observer projections can introduce branch behaviour absent from the
    intrinsic isogeny.

The exact classical pattern is:

\[
\boxed{
\text{temporal tangent action}
\longleftrightarrow
\text{period-lattice action}
\longleftrightarrow
\text{finite kernel and degree}
\longleftrightarrow
\text{constructive rational map}.
}
\]

## 13. Claims explicitly not made

This note does not claim:

- that every program characteristic is an isogeny;
- that every three-domain feature admits a norm formula;
- that construction occurrence count equals isogeny degree;
- that an \(x\)-coordinate branch is intrinsic ramification;
- that the CM scalar is observer-independent;
- that a finite kernel always exists for an arbitrary program quotient;
- that dual program transformations always exist;
- that duality implies invertibility;
- that the elliptic group law has been added to stable Adva;
- that SymPy computations authorize semantic identities in Rust;
- that the displayed rational expressions are globally safe affine programs;
- that the three-computer theory has been reduced to classical elliptic-curve
  theory; or
- that the current calculations solve the earlier surreal \(L/R\) reduction
  problem.

## 14. Red-team opinion

### 14.1 The examples are selected for exceptional symmetry

The \(j=0\) and \(j=1728\) curves have extra endomorphisms. Their norm laws are
especially transparent. A generic elliptic curve over \(\mathbf C\) has
endomorphism ring \(\mathbf Z\), so only integer multiplication survives as a
self-endomorphism.

The next calibration must include a non-CM rational isogeny to ensure that the
method does not depend on an imaginary-quadratic scalar shortcut.

### 14.2 The temporal scalar is normalization-dependent

The quotient maps have differential multiplier \(1\); the CM endomorphism
charts have multipliers \(1+i\) and \(1-\omega\). Reporting only one of these
without the target differential and chart isomorphism would be misleading.

### 14.3 The coordinate degree can be misread

For these examples the equation

\[
N_x-uD_x=0
\]

has degree equal to the isogeny degree. This is useful but should not be turned
into a universal definition. Coordinate cancellation, inseparability,
weighted projective models, and different observer projections can change the
visible polynomial degree.

### 14.4 Kernel point lists are not always the right representation

Over large fields or for large degree, enumerating every kernel point may be
expensive or impossible over the base field. Kernel polynomials, ideals,
Galois-stable subgroup schemes, or composed low-degree factors can be more
appropriate.

### 14.5 Complex multiplication is not defined over every displayed base field

The rational two- and three-isogenies are defined over \(\mathbf Q\), while
the self-endomorphism interpretations by \(1+i\) and \(1-\omega\) require
complex or suitable number-field identifications. Field of definition belongs
in the residual.

### 14.6 The full curve is essential

If only the \(x\)-coordinate is kept, then \(P\) and \(-P\) are identified.
The resulting shadow can create apparent information loss and branching that
the full isogeny does not have. This is a concrete warning against inferring
the source ontology from one observer projection.

## 15. Next research sequence

The most informative next sequence is:

1. **Non-CM control:** choose a rational elliptic curve with a rational
   two- or three-isogeny but \(j\ne0,1728\), and repeat the kernel, degree,
   differential, dual, and coordinate checks without identifying the map with
   multiplication by a CM scalar.
2. **Legendre family:** study
   \[
   E_\lambda:y^2=x(x-1)(x-\lambda)
   \]
   and its full two-torsion. This connects the finite characteristic work to
   the modular \(\lambda\)-line and its three boundary values
   \(0,1,\infty\).
3. **Observer comparison:** compute the same isogeny through the full complex
   curve, its real locus, the \(x\)-line, and a finite torsion observer, and
   record the exact forgetting maps among their feature profiles.
4. **Dual execution:** implement bounded projective circuits for an isogeny
   and its dual, then certify their composite against multiplication by the
   degree.
5. **Kernel-to-circuit compilation:** implement a research-local,
   certificate-bearing Vélu calibration for one small rational kernel without
   promoting it to a stable API.
6. **Period and chart transport:** attach exact lattice matrices and
   differential transitions to the rational projective circuits.
7. **Only then revisit the three-cusp picture:** compare the Legendre
   degenerations, CM points, and the earlier tri-cusp semantics without
   identifying them prematurely.

The Legendre step is likely the most important bridge to the larger theory.
It places:

- three distinguished two-torsion points;
- three degeneration channels \(0,1,\infty\);
- period transport;
- modular transformations;
- finite isogenies; and
- explicit algebraic construction

inside one traditional family.

## 16. Executable scope

The accompanying test
`tests/python/test_elliptic_isogeny_triadic_characteristics.py` checks:

- exact \(j\)-invariants for the selected models;
- the point calculation \([2](2,3)=(0,1)\);
- the complete duplication rational map;
- the two-isogeny
  \[
  (-4,6)\mapsto(9/4,123/8);
  \]
- the three-isogeny
  \[
  (2,3)\mapsto(3,0);
  \]
- exact preservation of all source and target curve equations;
- pullback multipliers \(2,1,1\) for the displayed rational models;
- CM chart multipliers \(2,1+i,1-\omega\);
- lattice determinants \(4,2,3\);
- dual lattice products \(4I,2I,3I\);
- kernel orders \(4,2,3\);
- generic projective \(x\)-fibre degrees \(4,2,3\); and
- checked Adva projective coordinate circuits for all three \(x\)-maps.

The test is a bounded calibration, not a general isogeny implementation.

## References

- A. V. Sutherland, *18.783 Elliptic Curves*, MIT lecture notes, especially
  the lectures on isogenies, kernels and division polynomials, endomorphism
  rings, elliptic curves over \(\mathbf C\), and complex multiplication.
- J. H. Silverman, *The Arithmetic of Elliptic Curves*, Chapters III and VI.
- J. Vélu, “Isogénies entre courbes elliptiques,”
  *C. R. Acad. Sci. Paris Sér. A-B* **273** (1971), 238–241.
- SageMath Reference Manual, *Isogenies* and *Complex multiplication for
  elliptic curves*.
- D. J. Bernstein, L. De Feo, A. Leroux, and B. Smith,
  “Faster computation of isogenies of large prime degree,” ANTS XIV, 2020.
- LMFDB entries and knowledge pages for the \(j=0\) and \(j=1728\) CM
  isogeny classes and their twists.
