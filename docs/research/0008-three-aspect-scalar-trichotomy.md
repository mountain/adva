# Three-Aspect Scalar Trichotomy

Status: bounded red-team calibration, not a foundational choice of scalar
field.

## Starting intuition

Suppose six real degrees of freedom split as

$$
6=2+2+2
$$

and are interpreted as temporal, spatial, and relational aspects. Suppose
further that each aspect is a rank-one function between the other two, and
that the characteristic of the function is the aspect itself or a selected
unit of that aspect.

One cyclic orientation may be written

$$
\mathcal T\simeq[\mathcal S,\mathcal R],\qquad
\mathcal S\simeq[\mathcal R,\mathcal T],\qquad
\mathcal R\simeq[\mathcal T,\mathcal S].
$$

If every aspect is a complex line, then the dimension count closes:

$$
\dim_{\mathbb C}\operatorname{Hom}_{\mathbb C}(\mathbb C,\mathbb C)=1,
$$

while every line has two real dimensions. This makes complex enrichment a
plausible hypothesis.

It does not yet make it necessary.

## The competing two-dimensional algebras

Consider the one-parameter family

$$
A_\kappa=\mathbb R[j]/(j^2-\kappa),
\qquad \kappa\in\{-1,0,1\}.
$$

Writing a scalar as $a+bj$, multiplication is

$$
(a+bj)(c+dj)
=
(ac+\kappa bd)+(ad+bc)j.
$$

The three cases are:

| $\kappa$ | Algebra | Quadratic norm $N_\kappa(a,b)$ | Geometric type |
|---:|---|---|---|
| $-1$ | complex numbers | $a^2+b^2$ | elliptic |
| $0$ | dual numbers | $a^2$ | parabolic |
| $1$ | split-complex numbers | $a^2-b^2$ | hyperbolic |

Each algebra is two-dimensional over the reals. In each one, a scalar
$u\in A_\kappa$ determines a rank-one action

$$
L_u(x)=ux,
$$

and its characteristic is recovered without coordinates by

$$
L_u(1)=u.
$$

Composition also closes:

$$
L_u\circ L_v=L_{uv}.
$$

Consequently, three aspect units

$$
\tau,\sigma,\rho\in A_\kappa
$$

can act cyclically, and their complete cycle is again one characteristic:

$$
L_\rho L_\sigma L_\tau=L_{\rho\sigma\tau}.
$$

All three algebras satisfy this pattern. The two-by-two-by-two split and the
rank-one internal-function intuition therefore do not by themselves select
$\mathbb C$.

## Checked program calibration

The file tests/python/test_three_aspect_scalar_trichotomy.py implements the
three products as finite Adva programs over ordered pairs of checked Real
ports. Every reuse is mediated by explicit copy; Rust remains the authority
for types, linear use, occurrences, sources, history, and diagram validity.

The test-local Python adapter only reads the two checked outputs as the
coefficients of $1$ and $j$. It verifies:

1. each product realizes the declared $A_\kappa$ multiplication;
2. each characteristic is recovered by acting on the unit;
3. temporal, spatial, and relational units compose to one cycle
   characteristic;
4. conjugation
   $$
   \overline{a+bj}=a-bj
   $$
   is multiplicative in all three cases;
5. the quadratic norm
   $$
   N_\kappa(x)=x\bar x
   $$
   is multiplicative in all three cases.

Thus even conjugation and a multiplicative quadratic norm do not suffice to
select the complex field.

## What does distinguish the cases

Additional nondegeneracy conditions separate the three candidates.

### Complex case

For $\kappa=-1$,

$$
N_{-1}(a,b)=a^2+b^2.
$$

It is positive definite over the reals. Every nonzero element has inverse

$$
(a+bj)^{-1}=\frac{a-bj}{a^2+b^2}.
$$

The unit-norm group is the compact circle $S^1$. Hence phase is periodic and
oriented.

### Dual case

For $\kappa=0$, the nonzero generator is nilpotent:

$$
j^2=0.
$$

The norm is degenerate. This case naturally records first-order extension,
jets, or an infinitesimal shoulder that disappears after quotienting.

### Split case

For $\kappa=1$,

$$
(1+j)(1-j)=0.
$$

There are nonzero zero divisors and the norm is indefinite. Its unit-norm
locus is hyperbolic rather than compact, making it a natural carrier for
causal or boost-like scale separation.

Within this three-member family, either of the following extra requirements
selects the complex case:

- every nonzero scalar is invertible;
- the multiplicative quadratic norm is positive definite;
- the norm-one phase group is compact.

None of these requirements has yet been derived from program geometry.

## The stronger AEG inversion criterion

The real AEG calibration supplies a less arbitrary candidate condition.  Let

$$
S(z)=-\frac{1}{z}.
$$

For a general quadratic scalar $z=a+bj\in A_\kappa$,

$$
S_\kappa(a,b)
=
\left(
  \frac{-a}{a^2-\kappa b^2},
  \frac{b}{a^2-\kappa b^2}
\right).
$$

In the complex case the denominator is $a^2+b^2$.  Therefore $S_{-1}$:

- is defined on the entire punctured real plane;
- is an involution;
- maps $z$ to a scalar satisfying $zS_{-1}(z)=-1$;
- preserves the upper-half-plane condition $b>0$.

The other two cases fail this global chart property.

- For dual numbers, the whole nonzero nilpotent axis $a=0$ is
  non-invertible.
- For split-complex numbers, the two nonzero light rays $a=\pm b$ are
  non-invertible.  Across the components separated by those rays, the sign of
  the second coordinate need not be preserved.

Hence the following strengthened condition does select the complex member of
the tested family:

> There is a globally defined negative-inverse involution on every nonzero
> scalar, and it preserves one connected real AEG half-plane.

This condition is not imported merely for field elegance.  It is motivated by
the observed transition between two real AEG grids.

## Oriented lift of the time-space exchange

The chirality observation sharpens the inversion criterion.  Use a
homogeneous time-space pair $(t,s)$ and let

$$
J(t,s)=(-s,t),
\qquad
J=
\begin{pmatrix}
0&-1\\
1&0
\end{pmatrix}.
$$

On the projective chart $z=t/s$, this induces

$$
[t:s]\longmapsto[-s:t],
\qquad
z\longmapsto-\frac1z.
$$

There are now two different orders in play:

$$
[J]^2=1
\quad\hbox{projectively},
\qquad
J^2=-I
\quad\hbox{on the oriented lift}.
$$

In particular,

$$
J^{-1}=-J.
$$

The forward exchange $J$ and reverse exchange $J^{-1}$ therefore induce the
same projective involution, because projectivization forgets the central sign,
but they remain distinct on the oriented lift.  This gives a more intrinsic
meaning to chirality:

> Chirality is the central sign distinguishing the forward and reverse
> oriented lifts of one projective time-space exchange.

This becomes a direct complex-selection mechanism under one explicit bridge
hypothesis: the same oriented two-real-dimensional carrier represents both
the time-space exchange lift and the action of the quadratic generator.  The
action of $j$ on $(a,b)$ is

$$
L_j=
\begin{pmatrix}
0&\kappa\\
1&0
\end{pmatrix},
\qquad
L_j^2=\kappa I.
$$

For $\kappa=-1$, $L_j=J$: it is orientation-preserving, invertible, and has
order four before projectivization.  For $\kappa=1$, the split exchange has
square $+I$, determinant $-1$, and is already its own inverse on the lift.
For $\kappa=0$, the dual generator is singular and nilpotent.  Thus, within
the tested family, requiring an oriented time-space exchange whose projective
class has order two but whose lift distinguishes forward from reverse selects
the complex relation $j^2=-1$ once the bridge hypothesis is imposed.

The role of $i$ is consequently not first introduced as a numerical scalar.
It can be read as the oriented quarter-turn implementing time-space exchange;
the complex algebra is the closure of composing and scaling that exchange.
This does not yet prove that every program expression must use complex
foundational scalars.

There is a second boundary to the statement.  The matrix $J\in SL(2,\mathbb R)$
already defines the real-coefficient Möbius map $-1/z$; complex notation is
not, by itself, evidence that all underlying scalars are complex.  What is new
is that retaining the lift rather than quotienting to $PSL(2,\mathbb R)$
exposes the central sign.  Calling that sign chirality requires the oriented
program carrier to remember it.  The AEG frame reversal supplies evidence for
this reading, not yet a general theorem identifying the two carriers.

## Hyperbolic grid, ripple grid, and chirality

Write the real AEG generators in the upper-half-plane chart as

$$
A(z)=z+1,\qquad M_\lambda(z)=\lambda z,\qquad \lambda>0.
$$

Conjugation by $S(z)=-1/z$ gives

$$
S M_\lambda S=M_{\lambda^{-1}}
$$

and

$$
S A S(z)=\frac{z}{1-z}.
$$

Thus the scale direction is inverted, while the translation grid is changed
into a parabolic or ripple-type grid organized around the other fixed point.
For a Baumslag--Solitar-style relation

$$
M A M^{-1}=A^n,
$$

the conjugated presentation has scale generator $M^{-1}$ and the ripple
generator $SAS$.  This is the visible AEG consequence of the lift-level
chirality: exchanging time and space sends the selected scale direction from
its forward presentation to its reverse presentation.

It is important not to identify this with reversal of the ambient complex
orientation.  In real coordinates

$$
S(x,y)=
\left(
  \frac{-x}{x^2+y^2},
  \frac{y}{x^2+y^2}
\right),
$$

whose Jacobian determinant is

$$
\det DS=\frac{1}{(x^2+y^2)^2}>0.
$$

The Möbius involution is holomorphic and orientation-preserving on the plane.
The chirality change is not a reversal of that ambient plane.  It is the
difference between $J$ and $J^{-1}=-J$ on the oriented time-space lift, read
after projection as reversal of the selected real AEG generator frame.

This suggests a more careful duality statement:

> Complex inversion mediates between two real AEG presentations.  It preserves
> the ambient oriented carrier, while its two oriented lifts retain the
> forward/reverse chirality that the projective chart forgets.

## Consequence for the six-dimensional intuition

The experiment leaves three live interpretations.

### One complex enrichment

All three aspects may be complex lines.  For the time-space pair, the oriented
lift above derives a local complex structure directly from exchange.  Extending
it cyclically to the relational aspect still requires compatible exchange
maps and overlap laws.  The six real degrees of freedom could then form a
locally complex rank-three carrier, though not necessarily a globally trivial
$\mathbb C^3$.

### Three different quadratic aspects

The elliptic, parabolic, and hyperbolic cases may encode different roles:
phase/orientation, infinitesimal extension, and causal scale. It is tempting
to associate these with spatial, relational, and temporal aspects, but the
present experiment supplies no canonical assignment.

### A stratified scalar object

Complex, dual, and split behavior may be charts or strata of a larger
expression-valued scalar geometry. Degeneration of the quadratic form would
then move between semisimple phase, nilpotent extension, and hyperbolic
separation without choosing one field globally.

The last two possibilities would be lost by declaring the complex field too
early.

## Relation to spectrum and the Jordan shoulder

The trichotomy clarifies two earlier questions.

- Complex scalars naturally combine multiplicative scale and periodic phase.
- Dual scalars naturally carry a nilpotent extension. A Jordan shoulder is
  therefore not removed merely by complexification; it may record precisely
  the relational or historical extension that a field-valued spectrum
  forgets.

This suggests that a faithful program spectrum may require both a semisimple
character and a residual extension object. A complex eigenvalue can report
the first part, while occurrence, source, and transport data must retain the
second.

## Result and next criterion

The bounded result has a negative and a positive part:

> Two real dimensions per aspect, cyclic rank-one action, recovery of a
> function from its unit characteristic, conjugation, and multiplicative norm
> do not select the complex field.

But within the tested quadratic family:

> A global negative-inverse involution on the punctured carrier that preserves
> a connected real AEG half-plane does select the complex case.

The strengthened mechanism explains why:

> The projective time-space exchange has order two, while its
> orientation-preserving lift has order four: $J^2=-I$ and
> $J^{-1}=-J$.  The central sign is exactly the retained forward/reverse
> chirality.  Split and dual generators do not supply such a lift.

The next theoretical question is whether a third, relational exchange closes
with this time-space lift into the proposed cyclic internal-function object,
and whether the overlap signs form a globally coherent complex carrier or a
twisted expression-valued bundle.

No stable complex type, quadratic scalar API, spectral carrier, triality
object, or field-selection theorem is introduced by this calibration.
