# Affine programs, exponential observers, and the derived spectral carrier

Status: bounded research calibration
Date: 2026-08-29
Corrects: `0001-paired-spectral-objectification.md`
Executable witness: `tests/python/test_affine_exp_observer_spectrum.py`

## Question

The earlier experiment began with an arbitrary matrix.  That reverses the
dependency required by arithmetic expression geometry.  The corrected
question is:

> Does a native affine arithmetic program generate an exponential-polynomial
> observer carrier, and is its matrix-like transport derivable as the
> contravariant action on that carrier rather than assumed as state-space
> ontology?

This experiment uses no generic spectrum, pullback, or compiled-presentation
API.  Rust compiles, validates, evaluates, and differentiates the native
programs.  Python translates checked IR to a symbolic expression and performs
a finite, research-local observer compilation with an explicit residual.

## Native affine kernel

The state programs are

\[
  A_a(x)=x+a,
  \qquad
  M_m(x)=mx,
  \qquad x,a,m>0.
\]

They are expressed in Adva using only registered `add`, `mul`, `log`, `neg`,
and `exp` operations.  Their source and occurrence data remain checked Rust
IR.  No matrix enters either program.

Choose the multiplicative chart

\[
  y=\log x,
  \qquad
  q=e^{-y}=x^{-1}.
\]

Pulling the chart observations back along the affine programs gives

\[
  A_a^*y
  =
  y+\log(1+aq),
  \qquad
  A_a^*q
  =
  \frac{q}{1+aq},
\]

and

\[
  M_m^*y=y+\log m,
  \qquad
  M_m^*q=m^{-1}q.
\]

Thus the addition residual is not an ordinary polynomial in a Cartesian
coordinate.  It lies on the exponential ray

\[
  \log(1+aq)
  =
  \sum_{j\ge1}\frac{(-1)^{j+1}}{j}a^jq^j,
  \qquad q^j=e^{-jy}.
\]

This is the polynomial-like carrier tested here.

## Finite observer carrier

At order `K`, use the filtered module

\[
  \mathcal P_K
  =
  \operatorname{span}\{1,y,q,q^2,\ldots,q^K\}.
\]

The executable matrix experiment uses the positive-degree ray

\[
  V_K=\operatorname{span}\{q,q^2,\ldots,q^K\}
\]

and retains the coefficient of `q^(K+1)` as the first omitted residual.  This
is a quotient/truncation presentation, not a claim that the infinite carrier
closes finitely.

For `1 <= k <= K`,

\[
  A_a^*(q^k)
  =
  \left(\frac{q}{1+aq}\right)^k
  =
  \sum_{j\ge0}
  (-1)^j
  \binom{k+j-1}{j}
  a^j q^{k+j},
\]

while

\[
  M_m^*(q^k)=m^{-k}q^k.
\]

The corresponding finite tables are therefore derived coordinates of the
observer pullbacks:

- addition is upper degree-raising and unipotent;
- multiplication is diagonal on the exponential weights;
- every omitted term remains part of the presentation certificate.

The term `matrix-like` refers only to these derived action tables.  It does not
refer to a primitive state matrix, a frontier, or Adva runtime ontology.

## Contravariant affine law

The native state maps obey

\[
  M_m\circ A_a=A_{ma}\circ M_m.
\]

Observer pullback reverses order:

\[
  (M_m\circ A_a)^*
  =A_a^*\circ M_m^*
  =M_m^*\circ A_{ma}^*.
\]

If `C_A(a)` and `C_M(m)` are the matrices derived from the checked observer
images, the finite experiment verifies exactly

\[
  C_A(a)C_M(m)=C_M(m)C_A(ma).
\]

The matrix identity is evidence for a derived contravariant presentation of
the native noncommutative affine composition law.  It is not the definition
of that law.

## What carries the spectrum

The operator carrying finite spectral data is

\[
  D^*|_{V_K}:V_K\longrightarrow V_K
\]

modulo the recorded residual.  The matrix is a basis-dependent encoding of
this action.

For multiplication,

\[
  \sigma(M_m^*|_{V_K})
  =\{m^{-1},m^{-2},\ldots,m^{-K}\}.
\]

For addition, every eigenvalue of the truncated action is `1`, although
different values of `a` give different unipotent matrices and different
omitted residuals.  If

\[
  N_a=C_A(a)-I,
\]

then `N_a` is nilpotent on the finite degree filtration.  Consequently, a bare
eigenvalue set forgets the additive program.  The minimum responsible finite
spectral presentation is

\[
  \boxed{
    \text{filtered observer carrier}
    +\text{semisimple scale data}
    +\text{unipotent extension}
    +\text{truncation residual}
  }.
\]

This does not yet define the more intrinsic dual observation spectrum from
prime filters, characters, or a history-observer frame.  It identifies one
finite numerical presentation that such a construction would have to recover.

## History boundary

The native programs

\[
  \operatorname{add}(\operatorname{copy}(x))
  \quad\text{and}\quad
  \operatorname{scale}_2(x)
\]

still have the same realized scalar action, ordinary differential, finite
powers, and scalar eigenvalue, while their checked graphs, histories, source
partitions, and operation-rule certificates differ.  Hence the newly derived
action presentation does not remove the earlier no-go:

> An observer that factors only through a finite action shadow and its
> operator spectrum cannot be faithful to checked program history on this
> fragment.

A task-relative observation spectrum must report residual history fibres; it
cannot replace them with a matrix or an eigenvalue set.

## Executable checks

The experiment verifies:

1. native `add` and `mul` programs generate the four chart formulas above;
2. the addition residual is the finite Taylor slice of `log(1 + aq)` on the
   exponential ray;
3. matrix-like action tables are computed from the checked image of `q`, not
   supplied to the program;
4. the affine semidirect law is preserved with contravariant order;
5. multiplication produces scale eigenvalues, whereas addition survives in
   a nilpotent extension and residual despite an unchanged eigenvalue set;
6. equal scalar spectrum still does not recover checked source/history data.

SymPy is an adapter over checked IR and a coefficient oracle.  It creates no
semantic identities and issues no Adva certificate.

## Assessment

The result supports a bounded version of the corrected dependency:

\[
  \boxed{
  \text{native affine program}
  \longrightarrow
  \text{exp-polynomial observer carrier}
  \longrightarrow
  \text{derived matrix-like pullback}
  \longrightarrow
  \text{filtered spectral data and residual}
  }.
\]

It does not yet support a general program spectrum, an intrinsic probe-frame
spectrum, convergence-based learning, or objectification.  The next theory
gate is to state a finite carrier theorem that derives the allowed closure,
filtration, decoder, and residual from a declared observation policy `Q`, then
compare the resulting finite presentation with a history-augmented observation
tower.
