# Symbolic Probe Linearity and the Expression-Valued Matrix Shadow

Status: bounded Python research construction over one Rust-checked exponential
optical diagram.  It derives a finite matrix-like observation from symbolic
probe transport.  It does not install vectors, covectors, modules, matrices,
or transposes as native program ontology.

## Question

The exponential cut experiment showed that a fixed output probe generates
exp-polynomial demand coefficients while preserving occurrence-decorated cut
composition.  A fixed probe cannot yet explain why a matrix-like form should
appear, or whether that appearance is merely imposed from ordinary linear
algebra.

The present experiment introduces two independent symbolic probe generators

$$
\lambda_0,\lambda_1
$$

that are explicitly distinct from program inputs, source identities, and
occurrence identities.  It asks:

1. is backward transport linear in these generators at every checked
   endpoint;
2. does this linearity survive every nested causal-cut factorization; and
3. do the extracted expression coefficients reproduce the numerical transpose
   reading of Rust's forward differential?

## Program and probe interfaces

The checked two-output exponential optical program is

$$
F(x,s,\kappa)
=
\left(
\exp\bigl((1-\kappa)x+s\bigr),
-\kappa x+s
\right).
$$

Its declared symbolic output probe is

$$
\lambda=(\lambda_0,\lambda_1).
$$

Program input leaves retain their original checked occurrence and source audit
data.  Probe leaves carry only a probe-generator name.  They cannot be emitted
by the existing fresh replay compiler because that compiler has no declared
probe ports.  This prevents accidental identification of an observer
direction with a program source.

## Probe-linear extraction

Every demand expression is inspected by a bounded sparse coefficient
extractor.  It accepts only expressions of the form

$$
C+\sum_i A_i\lambda_i,
$$

where $C$ and $A_i$ are probe-free program expressions.

The extractor does not normalize the coefficient expressions.  It only uses
the syntax-directed laws required to expose probe dependence:

- addition merges equal probe names;
- negation negates each coefficient;
- multiplication is accepted only when at most one factor depends on probes;
- `exp` is accepted only when its argument is probe-free.

If two probe-dependent factors are multiplied, or a probe enters `exp`, the
extractor rejects the expression as nonlinear in the probe generators.

For every endpoint in this experiment the constant part is structurally
absent:

$$
C=0.
$$

Thus the field is not merely affine in the chosen probe; it is homogeneous of
degree one in the probe syntax.

## Endpoint-wise linearity

At every checked endpoint $e$, numerical evaluation verifies

$$
Q_e(\lambda+\mu)
=
Q_e(\lambda)+Q_e(\mu),
$$

and

$$
Q_e(a\lambda)=aQ_e(\lambda)
$$

for independent declared assignments and a nontrivial scalar $a$.  The zero
probe evaluates to the zero demand at every endpoint.

The extracted coefficients also reconstruct each evaluated endpoint demand:

$$
Q_e(\lambda)
=
\sum_i A_{e,i}\lambda_i.
$$

This is checked on the full occurrence-decorated field, not only at program
inputs.

## The matrix-like root shadow

Write

$$
Z=\exp\bigl((1-\kappa)x+s\bigr).
$$

Coefficient extraction at the three input endpoints gives

$$
\begin{pmatrix}
Q_x\\
Q_s\\
Q_\kappa
\end{pmatrix}
=
\underbrace{
\begin{pmatrix}
(1-\kappa)Z & -\kappa\\
Z & 1\\
-xZ & -x
\end{pmatrix}
}_{M_F(x,s,\kappa)}
\begin{pmatrix}
\lambda_0\\
\lambda_1
\end{pmatrix}.
$$

The entries in the first column contain `exp`; the second column remains in
the non-exponential arithmetic fragment.  All entries are probe-free program
expressions.

At three numerical inputs, the experiment asks Rust for the forward
differential of the checked two-output program and verifies entry by entry
that

$$
M_F(u)=J_F(u)^{\mathsf T}.
$$

This notation reports an equality in the selected finite input/output port
chart.  It does not define a native transpose operation or identify the
program with a coordinate array.

## The optical cut shadow

At the cut immediately before the final `exp` event, coefficient extraction
gives the diagonal-looking chart shadow

$$
\begin{pmatrix}
Z & 0\\
0 & 1
\end{pmatrix}.
$$

Its two rows remain attached to checked endpoint lineages of sizes four and
three.  Both endpoints have the same three-source support.  Thus even this
simple coefficient table does not contain the whole cut carrier: it omits the
occurrence geometry to which the coefficients are attached.

## Linearity and cut composition

The symbolic probe field is factored through every nested pair of completed
causal pasts in the exponential two-output diagram.  Direct and three-segment
transport again produce exactly equal unsimplified expressions at every
endpoint.  Every lower and upper cut demand remains probe-homogeneous.

Consequently the two laws coexist in the bounded fixture:

$$
\begin{aligned}
\mathcal B_{U\leftarrow W}
&=
\mathcal B_{U\leftarrow V}
\circ
\mathcal B_{V\leftarrow W},\\
\mathcal B_{U\leftarrow V}(a\lambda+b\mu)
&=
a\mathcal B_{U\leftarrow V}(\lambda)
+b\mathcal B_{U\leftarrow V}(\mu).
\end{aligned}
$$

Composition belongs to the expression-valued cut transport first; matrix-like
composition is a derived coefficient reading.

## Polynomial-like and matrix-like are co-generated

This experiment supplies a precise positive answer to the motivating
intuition.

- The **polynomial-like side** is the family of probe-free program expressions
  appearing as coefficients.  In the selected Real chart its first column is
  exp-polynomial.
- The **matrix-like side** is the finite organization of those same
  coefficients by demand endpoint and probe generator.
- The **common mechanism** is symbolic probe transport on the
  occurrence-decorated expression field.

Therefore the two presentations are not unrelated structures later forced to
match.  They are co-generated by one calculation.  They are still not
literally identical: the matrix-like presentation adds row and column
interface data, while the polynomial-like expressions retain their internal
construction syntax.

No triangular matrix is needed.  A triangular or normal form could arise only
after further choices about ordering, invariant subcarriers, iteration, and
expression equivalence.

## A bounded form of the dual-lift intuition

Choosing the two output probe generators in the finite port chart
automatically produces their backward coefficient sections at every causal
cut.  In that limited sense, a selected output fibre lifts a dual family on
the other side of the same checked program.

The qualification matters.  The probe basis is declared chart data, and the
experiment does not prove that an arbitrary geometric fibre canonically
chooses a global dual fibre.  What is endogenous is the transport once the
probe interface has been declared.

## Consequence for the spectral carrier

The expression-valued matrix $M_F$ is now a legitimate compiled observation,
but the richer carrier remains

$$
\text{occurrence-decorated probe-linear expression sections over causal cuts}.
$$

A future spectrum may be extracted from repeated endomorphic transport in a
chosen chart.  Before that step, the matrix-like shadows of adjacent cut
segments must be shown to compose using the same expression substitution and
occurrence transport as the native sections.

## Executable evidence

The extended optical test verifies:

1. strict syntactic separation of program input leaves and symbolic probe
   leaves;
2. rejection boundaries for probes inside `exp` or both factors of a product;
3. structurally zero constant term at every endpoint demand;
4. endpoint-wise additivity, homogeneity, zero preservation, and coefficient
   reconstruction;
5. a three-by-two root coefficient table with exp-polynomial first column and
   non-exponential second column;
6. entrywise equality of that table with Rust's forward Jacobian transpose at
   three inputs;
7. exact symbolic cut composition for every nested causal-open pair; and
8. a two-by-two optical-cut coefficient shadow attached to unchanged lineages
   of sizes three and four with equal three-source support.

## No-go boundaries

This calibration does not establish:

- a stable probe, dual fibre, vector, covector, module, or matrix object;
- canonical probe bases or global dualization;
- a native transpose, adjoint, dagger, or `D*` operation;
- a general symbolic proof of probe linearity for every builtin or diagram;
- expression equality, coefficient normalization, or canonical sparse form;
- matrix-like composition with expression substitution across separate
  programs;
- an invariant subcarrier, normal form, spectrum, or eigenobject;
- learning, parameter update, or physical dynamics.

## Next obligation

For two adjacent cut segments, extract their symbolic-probe coefficient tables
separately.  Then define the smallest expression-valued contraction law that
substitutes the intermediate forward expressions and sums over the shared cut
probe generators.  The result must agree endpoint-by-endpoint with coefficient
extraction after native section composition.

That experiment will decide whether matrix multiplication itself lifts from
ordinary scalar multiplication to an endogenous polynomial-like composition
law in program geometry.
