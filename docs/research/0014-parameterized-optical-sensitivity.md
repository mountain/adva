# Parameterized Optical Sensitivity and Regime Crossing

Status: bounded numerical research calibration over Rust-checked Real programs.
This is not an adjoint pullback, a learning rule, a measured optical result, or
a stable physical API.

## Question

The preceding optical experiments fixed every device constant. They found an
explicit closure from each local aspect--opposite-face plane to a two-port
optical presentation, then separated program-aware, oriented, and projective
observation levels. The next obligation was to vary one device control without
turning the resulting coordinate presentation into the program ontology.

The bounded questions are:

1. can one checked program template cross the elliptic, parabolic, and
   hyperbolic regimes as a source-bearing input varies;
2. can the existing Rust forward differential compute the sensitivity of a
   declared oriented output readout;
3. does that readout require program history, oriented lift data, or only a
   projective class?

## The checked parameter program

Let the tunable focusing expression be

$$
L_\kappa(x,s)=(x,s-\kappa x)
$$

and retain unit free propagation

$$
P(x,s)=(x+s,s).
$$

The program under test is the device composition

$$
p_\kappa=P\circ L_\kappa,
$$

so checked execution gives

$$
p_\kappa(x,s)
=
\bigl((1-\kappa)x+s,-\kappa x+s\bigr).
$$

The expression language constructs this computation with explicit `copy`,
`mul`, `neg`, `add`, `frontier`, and checked calls. It does not accept a matrix
as input and does not evaluate by matrix multiplication.

Here $\kappa$ is a named `Real` input. Rust therefore assigns it its own source
and retains that source in the lineage of both outputs. This differs from the
source-free literal used in earlier fixed fixtures. Being source-bearing makes
$\kappa$ a genuine program control direction in this experiment; it does not
by itself make the control a fourth temporal, spatial, or relational aspect.

## One expression family, three observed regimes

Only after checked execution on the two declared basis fixtures do we record
the derived action presentation

$$
M_\kappa=
\begin{pmatrix}
1-\kappa&1\\
-\kappa&1
\end{pmatrix}.
$$

This array is a compact oracle for the observed two-port action, not the
program's foundational language. It has

$$
\det M_\kappa=1,
\qquad
\operatorname{tr}M_\kappa=2-\kappa,
$$

and hence

$$
\Delta(\kappa)
=
(\operatorname{tr}M_\kappa)^2-4\det M_\kappa
=
\kappa(\kappa-4).
$$

Therefore the observed classification is

| parameter region | observed class |
|---|---|
| $\kappa<0$ | hyperbolic |
| $\kappa=0$ | parabolic |
| $0<\kappa<4$ | elliptic |
| $\kappa=4$ | parabolic |
| $\kappa>4$ | hyperbolic |

The executable experiment checks seven values spanning all five rows. The
important program-geometric fact is that the checked expression graph and its
typed boundary do not change at $\kappa=0$ or $\kappa=4$. What changes is a
coarser numerical observation of one program family. The discriminant locates
an observation-relative regime boundary; it is not the carrier of the full
program spectrum.

## Declared oriented readout

Choose the output expression

$$
\ell(x',s')=x'+2s'.
$$

This is deliberately oriented: replacing an output lift by its negative
negates the result. Composing it with the device gives the scalar program

$$
\mathcal L(x,s,\kappa)
=
\ell\bigl(p_\kappa(x,s)\bigr)
=
x+3s-3\kappa x.
$$

The Rust structural forward differential returns

$$
d\mathcal L
=
(1-3\kappa)\,dx
+3\,ds
-3x\,d\kappa,
$$

and in particular

$$
\boxed{\partial_\kappa\mathcal L=-3x}.
$$

The test compares the native result at three fixtures against both the exact
formula and a centered finite difference. The native certificate records the
checked diagram plus the versioned `constant`, `copy`, `mul`, `neg`, `add`, and
`scale` differential rules.

## A residual that the scalar derivative forgets

The experiment also constructs a second checked scalar program directly from

$$
x+3s-3\kappa x.
$$

It has different IR and history from the device composition

$$
\ell\circ P\circ L_\kappa,
$$

but the bounded fixtures give the same scalar values and the same native
gradients. This agreement does not produce an equation cell between the two
programs. It shows instead that this particular objective and its first
differential forget their construction histories.

Thus a scalar sensitivity can be reproducible while still being too coarse to
identify program geometry.

## Location in the observer tower

The objective has a precise bounded position in the previously constructed
tower.

### It does not require the program-aware level

The device-history and direct-arithmetic realizations have distinct checked IR
and histories but the same tested objective and gradient. The objective is
therefore compatible with forgetting those program-aware differences in this
fixture.

### It does require the oriented level

For every nonzero output lift $v$,

$$
[v]=[-v]
$$

projectively, whereas

$$
\ell(-v)=-\ell(v).
$$

The executable counterexample uses an actual output of $p_1$. Consequently
$\ell$ cannot descend to the projective quotient. It is a scalar probe on the
oriented numerical presentation.

The bounded factorization statement is therefore

$$
\mathcal O_{\mathrm{prog}}
\longrightarrow
\mathcal O_{\mathrm{or}}
\xrightarrow{\ell}
\mathbb R,
$$

with no corresponding map from $\mathcal O_{\mathrm{proj}}$ that reproduces
this readout.

## Why this is not yet a pullback

Rust's implemented differential propagates input tangents forward through the
checked operation graph. Evaluating a scalar objective then reports its
sensitivity with respect to the named inputs. That is sufficient for the
present finite computation.

A contravariant observer pullback would begin with a declared output probe,
transport it backward to a domain probe using checked diagram data, and return
a certificate for the pairing law. No such stable operation is invoked or
constructed here. In particular, this result provides no `D*`, transpose,
adjoint, reverse mode, update rule, optimizer, or learning semantics.

The formula $\partial_\kappa\mathcal L=-3x$ says how the declared scalar
readout changes under an infinitesimal control variation at a fixed input. It
does not say that the optical program changes itself, chooses a better
$\kappa$, or learns from an environment.

## Executable evidence

The extended test verifies:

1. the three-input, two-output parameter program crosses the Rust validation
   boundary;
2. $x$, $s$, and $\kappa$ are three explicit sources, and every output retains
   all three supports;
3. seven observed actions match the exact formula for $M_\kappa$;
4. determinant, trace, discriminant, and all three regime classifications
   match their analytic oracles;
5. the device and direct objectives retain different IR and histories;
6. their values and native gradients agree at three declared fixtures;
7. the native $\kappa$ derivative agrees with centered finite differences;
8. the differential certificate records diagram integrity and versioned
   operation rules;
9. an explicit central-sign pair has one projective ray but opposite oriented
   readouts.

Rust remains authoritative for program typing, linear use, sources,
occurrences, histories, execution, and forward differentiation. Python only
selects bounded fixtures and compares returned results with independent
numerical formulas.

## No-go boundaries

This calibration does not establish:

- a matrix ontology for programs;
- a complete spectral carrier or phase-transition theorem;
- a fourth aspect associated with $\kappa$;
- a physical meaning for the chosen coefficients $(1,2)$;
- invariance under every direct or factorized realization;
- a stable observer, probe, or predicate type;
- contravariant pullback, adjoint propagation, reverse mode, or learning;
- noise, diffraction, Gaussian-beam positivity, measurement, or experimental
  validation.

## Next obligation

The next safe target is a research-local backward probe witness derived from a
checked diagram, paired against the existing forward differential on a finite
set of tangent directions. Its first obligation is the pairing law, not a
matrix-transpose implementation. Only after source- and occurrence-resolved
contributions are retained should such a witness be considered for a stable
Rust `pullback` API.
