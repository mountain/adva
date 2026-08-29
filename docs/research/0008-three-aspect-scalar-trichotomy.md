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

## Consequence for the six-dimensional intuition

The experiment leaves three live interpretations.

### One complex enrichment

All three aspects may be complex lines. This requires program geometry to
derive a positive norm, compact phase, or equivalent division property. The
six real degrees of freedom would then form a locally complex rank-three
carrier, though not necessarily a globally trivial $\mathbb C^3$.

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

The bounded result is negative but useful:

> Two real dimensions per aspect, cyclic rank-one action, recovery of a
> function from its unit characteristic, conjugation, and multiplicative norm
> do not select the complex field.

The next theoretical question is therefore not “can the three aspects be
written over $\mathbb C$?” They can. It is:

> Does the checked time-space-relation calculus intrinsically derive positive
> norm and compact phase, or does it instead require a scalar geometry that
> also contains parabolic and hyperbolic degeneration?

No stable complex type, quadratic scalar API, spectral carrier, triality
object, or field-selection theorem is introduced by this calibration.

