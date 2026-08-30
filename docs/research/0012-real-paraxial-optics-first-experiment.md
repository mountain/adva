# First Physical Simulation: Real Paraxial Optics

Status: bounded numerical calibration of fixed, ideal, normalized paraxial
programs. This is not a wave-optics solver, measured optical experiment, or
stable physical API.

## Purpose

The causal-cut work derived an order-four local orientation action before any
physical model was chosen. This experiment asks whether a real physical
composition exposes the same mechanism without putting complex numbers into
the checked program.

Paraxial optics is the narrowest useful case. Free propagation and thin
focusing are composable operations, and their real two-port action induces
the Möbius law used by the Gaussian beam parameter. We test:

1. whether checked arithmetic expressions represent the device history and
   numerical propagation;
2. whether an order-four lift and complex fixed points appear only after
   analysing a real program;
3. whether repeated propagation recovers the three projective stability
   regimes;
4. whether program geometry retains information forgotten by the final
   numerical action.

The first three are classical optical calibration, not new mathematics. The
fourth is the program-geometric question.

## Real starting point

Use the normalized paraxial ray presentation

$$
r=(x,s),
$$

where $x$ is transverse height and $s$ is paraxial slope. This ordered pair is
a declared physical presentation, not the ontology of program space. Unit
free propagation and unit focusing act as

$$
P(x,s)=(x+s,s),
\qquad
L(x,s)=(x,s-x),
$$

with inverses

$$
P^{-1}(x,s)=(x-s,s),
\qquad
L^{-1}(x,s)=(x,s+x).
$$

All four are Adva Lisp programs using only real inputs, explicit copy,
addition, and negation. The unit choices make the experiment dimensionless.
No complex scalar, matrix operation, division, or Gaussian beam parameter
occurs in the checked program.

The familiar two-by-two arrays are used only as compact descriptions of the
numerical action observed after evaluation. They are not semantic inputs.

## A real device chain with an order-four lift

Consider the symmetric physical history

$$
F=P\circ L\circ P.
$$

Checked evaluation gives

$$
F(x,s)=(s,-x),
\qquad
F^2(x,s)=(-x,-s),
\qquad
F^4(x,s)=(x,s).
$$

The inverse device history is

$$
F^{-1}=P^{-1}\circ L^{-1}\circ P^{-1},
\qquad
F^{-1}(x,s)=(-s,x)=-F(x,s).
$$

The two lifts differ on the ordered real pair but induce the same projective
map. In the chart $z=x/s$,

$$
z\longmapsto-\frac1z.
$$

Thus real device composition reproduces the oriented-lift distinction:

$$
F^{-1}=-F,
\qquad
F^2=-I,
$$

while the projective action forgets the central sign.

## Where the complex fixed point enters

Only after evaluating the real action do we solve

$$
z=-\frac1z.
$$

The fixed points satisfy

$$
z^2+1=0,
\qquad
z=\pm i.
$$

This is non-circular in a limited sense: Adva executes only real programs;
complex values enter when the observed real projective action is completed by
its non-real fixed points.

It is not a complete derivation of the Gaussian beam parameter. The real ray
ratio $x/s$ and the beam parameter $q$ are different physical objects even
though they carry the same Möbius action. The real equation also produces
both signs. Selecting $+i$ still requires the physical upper-half-plane or
positive-width condition.

## Three repeated optical cells

Three checked programs are iterated:

| regime | composition | observed action | trace | discriminant |
|---|---|---|---:|---:|
| elliptic | $P\circ L$ | $(x,s)\mapsto(s,s-x)$ | 1 | $-3$ |
| parabolic | $P$ | $(x,s)\mapsto(x+s,s)$ | 2 | 0 |
| hyperbolic | $P\circ L^{-1}$ | $(x,s)\mapsto(2x+s,x+s)$ | 3 | 5 |

Every observed action has determinant one, so the sign of

$$
\Delta=\operatorname{tr}(F)^2-4
$$

gives the classical stability class.

Starting from $(1,1)$, the elliptic example is periodic:

$$
(1,1)\to(1,0)\to(0,-1)\to(-1,-1)\to(-1,0)\to(0,1)\to(1,1).
$$

After twelve steps the parabolic example reaches

$$
(13,1),
$$

while the hyperbolic example reaches

$$
(121393,75025).
$$

The elliptic fixed points form a non-real conjugate pair, the parabolic
translation has its fixed point at the projective boundary, and the
hyperbolic fixed points are real.

## Same numerical action, different program geometry

The quarter-turn is implemented in two ways:

1. a direct value expression $D(x,s)=(s,-x)$;
2. the physical device history $F=P\circ L\circ P$.

They agree on every tested numerical input and have the same observed
two-port action. Nevertheless their checked IR, call and copy histories, and
output source support differ.

The direct program sends one source to each output. In the factorized program,
intermediate additions make both final outputs depend on both original
sources, even though exact arithmetic cancellation reduces the value to
$(s,-x)$. Adva does not erase that dependence merely because an external
algebraic simplifier can.

Hence

$$
\text{same numerical action}
\centernot\Longrightarrow
\text{same checked program geometry}.
$$

This residual is not automatically a physical observable. A future equation
or observation certificate may authorize forgetting it. The result instead
gives the closure theory a precise obligation: state which observer is
allowed to identify the two programs.

## Relation to the six-state carrier

On each aspect--opposite-face plane, the previously derived local action is
an order-four rotation up to orientation. The optical device chain realizes
the same law on a physical two-port presentation. This is evidence for a
candidate physical shadow, not yet a semantic derivation of optics from the
six-state carrier.

The missing bridge should construct a declared closure map

$$
\operatorname{ev}_{\mathrm{opt}}:
W(P)\longrightarrow Q_{\mathrm{opt}}
$$

and verify

$$
\operatorname{ev}_{\mathrm{opt}}\,\Omega_P
=
F\,\operatorname{ev}_{\mathrm{opt}}.
$$

Without this commuting map, similarity of the order-four actions remains a
calibration match.

## Executable certificate

The Python test file for this experiment checks:

1. Rust validation of every fixed two-input, two-output optical program;
2. exact direct, factorized, inverse, half-turn, and full-turn propagation;
3. the projective negative reciprocal on real chart values;
4. $F^2=-I$, $F^{-1}=-F$, and fixed points $\pm i$ obtained after real
   evaluation;
5. determinant-one shadows with traces $1,2,3$ and all three regimes;
6. periodic, linear, and exponential numerical trajectories;
7. equality of the direct and device-factorized numerical shadows;
8. inequality of their IR, histories, and source-support geometry.

Rust owns program checking, explicit sharing, source identity, occurrence
lineage, and numerical execution. Python supplies the bounded simulation,
fixed-point calculation, and classical optical oracle.

## Supported and unsupported conclusions

The simulation supports:

- real program composition can realize the oriented lift of
  $z\mapsto-1/z$;
- complex fixed points can enter after rather than before real execution;
- repeated checked programs recover the classical projective trichotomy;
- program geometry retains a construction residual beyond the numerical
  ABCD shadow.

It does not:

- simulate a field, diffraction, interference, aperture, loss, gain, or
  noise;
- derive the Gaussian $q$ parameter or identify it with a ray coordinate;
- derive upper-half-plane positivity;
- implement observer pullback, adjoint propagation, or a parameter gradient;
- demonstrate learning, spectral selection, or certified objectification;
- derive the full six-state carrier from optics;
- establish a new optical stability theorem.

This is the fixed-program computation layer of the proposal. External
parameter adjustment and internally objectifying feedback remain later
layers.

## Next obligation

The next step should construct the smallest explicit observation/closure
interface between the checked expression carrier and the optical projective
carrier. It must state:

1. which source and history information the optical observer preserves;
2. which cancellation residual it may forget;
3. how forward device action transports the observed state;
4. what pairing is required before a reverse or adjoint action can be
   claimed.

Only after that bridge commutes should the experiment introduce a tunable
focusing parameter, an output objective, and a checked comparison with the
classical adjoint gradient.
