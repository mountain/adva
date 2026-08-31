# Triangular Spectral Reconstruction at the Three Cusps

Status: exploratory research note extending
[`0033-omega-type-computational-boundary.md`](0033-omega-type-computational-boundary.md).
It records a strong semantic intuition, the exact external and repository
evidence currently supporting it, the conservative conclusion justified at
this stage, and the main red-team objections. It is not a stable API proposal,
a theorem of unrestricted program geometry, a physical claim, or a promotion
to `claims.toml`.

The central proposal is:

> Time, space, and construction are the three nonzero directions of one
> marked rank-two carrier. The meaning of each vertex is supplied by an
> operator on the opposite edge. Each vertex therefore requires its own
> decorated spectral package. The three cusps are the boundary channels in
> which one vertex degenerates and its opposite-edge semantics is exposed.

## 1. Intuition

### 1.1 Vertex semantics comes from the opposite edge

Let an oriented semantic triangle have vertices

\[
T=\text{time},\qquad
S=\text{space},\qquad
C=\text{construction}.
\]

The vertices are not assigned independent primitive meanings. Instead, the
meaning of each vertex is reconstructed from the relation between the other
two:

\[
T\ \longleftarrow\ (S\leftrightarrow C),
\qquad
S\ \longleftarrow\ (C\leftrightarrow T),
\qquad
C\ \longleftarrow\ (T\leftrightarrow S).
\]

If the opposite-edge relations admit declared spectral closures, write

\[
\mathcal D_T=\operatorname{cl}_T(K_{SC}),
\qquad
\mathcal D_S=\operatorname{cl}_S(K_{CT}),
\qquad
\mathcal D_C=\operatorname{cl}_C(K_{TS}).
\]

The first spectral reading is then

\[
\Sigma_T=\operatorname{Spec}(\mathcal D_T),
\qquad
\Sigma_S=\operatorname{Spec}(\mathcal D_S),
\qquad
\Sigma_C=\operatorname{Spec}(\mathcal D_C).
\]

The closure symbol is essential. An edge may initially be a relation,
correspondence, transport, or map between different spaces; such an object has
no ordinary spectrum until a common carrier, a round trip, an adjoint pair, a
monodromy action, or another endomorphism-producing closure has been declared.

### 1.2 Three aspects from a rank-two carrier

Choose a symplectic period basis for a smooth elliptic fibre and write

\[
\delta_T=(1,0),
\qquad
\delta_S=(0,1),
\qquad
\delta_C=(1,1).
\]

Modulo two, these are exactly the three points of

\[
\mathbf P^1(\mathbf F_2)
=
\{(1,0),(0,1),(1,1)\}.
\]

They satisfy the cyclic identities

\[
\delta_T=\delta_S+\delta_C,
\qquad
\delta_S=\delta_C+\delta_T,
\qquad
\delta_C=\delta_T+\delta_S
\quad\text{over }\mathbf F_2.
\]

Thus three semantic aspects need not be three independent dimensions. They
may be the three nonzero polarities of a two-dimensional marked state. Over
the integers, signs and order must be restored; those choices are candidates
for orientation and chirality data.

The construction direction is especially suggestive:

\[
\delta_C=\delta_T+\delta_S.
\]

It says that construction is not an extra coordinate placed beside time and
space. It is the diagonal direction produced when a temporal history closes
against a spatial cut or gluing boundary.

### 1.3 Cusp as semantic inversion

At a nodal degeneration, one cycle vanishes. If the vanishing cycle is
`delta_T`, the time vertex is no longer directly present in the limiting
fibre. What remains visible is the gluing, transport, or residual relation
between the space and construction sides.

This motivates the cyclic reading

\[
T\text{-cusp}:\quad
\delta_T\to0,\quad K_{SC}\text{ is exposed},
\]

\[
S\text{-cusp}:\quad
\delta_S\to0,\quad K_{CT}\text{ is exposed},
\]

\[
C\text{-cusp}:\quad
\delta_C\to0,\quad K_{TS}\text{ is exposed}.
\]

A cusp is therefore not merely a broken vertex. It is a boundary channel in
which the opposite-edge semantics of that vertex becomes observable.

### 1.4 Why three spectra are necessary

The three candidate spectra have different semantic roles:

| Vertex reconstructed | Opposite edge | Candidate spectral meaning |
|---|---|---|
| time `T` | space--construction `SC` | evolution generator, energy/frequency, decay, resonance, causal Lyapunov data |
| space `S` | construction--time `CT` | adjacency or Laplace modes, propagation, geometric scale, spatial resonance |
| construction `C` | time--space `TS` | birthday and covering growth, graft modes, transfer spectrum, Hecke/isogeny spectrum, complexity and entropy |

Studying only the construction spectrum would break the cyclic semantic
principle. If the triangle is fundamental, all three opposite-edge spectra are
required even when only one is computationally accessible in a particular
chart.

### 1.5 Omega on the construction edge

Let the time--space edge carry a self-delimiting construction dynamics. A
formal partition function is

\[
Z_U(s)
=
\sum_{U(p)\downarrow}e^{-s|p|},
\qquad
Z_U(\log2)=\Omega_U.
\]

If `Z_U` can be represented through a transfer operator
`L_(TS,s)`, the Omega-type boundary may occur where the relevant spectral
radius or determinant reaches a critical value, schematically

\[
\rho(\mathcal L_{TS,s})=1.
\]

In this reading, `Omega_U` is not an interesting eigenvalue of one cusp
monodromy. It is a noncomputable total mass or critical boundary value of the
entire time--space construction language.

## 2. Evidence

### 2.1 The exact three-cusp arithmetic

The level-two modular curve is

\[
Y(2)=\Gamma(2)\backslash\mathbb H
\cong
\mathbf P^1\setminus\{0,1,\infty\}.
\]

Its algebraic compactification is

\[
X(2)\cong\mathbf P^1,
\]

with three cusps represented on the boundary of `H` by

\[
\infty=\frac10,
\qquad
0=\frac01,
\qquad
1=\frac11.
\]

For a primitive slope `(p,q)`, reduction modulo two produces exactly three
nonzero parity classes. Since `Gamma(2)` acts trivially modulo two, those
classes cannot be identified inside `Y(2)`. This is an exact source of the
three marked directions, not a numerological analogy.

The modular lambda function supplies the quotient coordinate. The associated
Legendre family is

\[
E_\lambda:\qquad
y^2=x(x-1)(x-\lambda).
\]

The three singular parameter values are `lambda = 0, 1, infinity`. At these
values two branch points collide, and after stable completion the elliptic
fibre becomes nodal. The base curve `X(2)` itself remains smooth; the singular
objects are the fibres over its cusp points.

### 2.2 The figure-eight and the opposite-edge relation

The three-punctured sphere deformation retracts to a figure-eight, so

\[
\pi_1(Y(2))\cong F_2.
\]

For positively oriented loops around the three punctures,

\[
\gamma_T\gamma_S\gamma_C=1.
\]

Consequently each loop is determined by the ordered product of the other two:

\[
\gamma_T=(\gamma_S\gamma_C)^{-1},
\qquad
\gamma_S=(\gamma_C\gamma_T)^{-1},
\qquad
\gamma_C=(\gamma_T\gamma_S)^{-1}.
\]

This is an exact noncommutative skeleton for the statement that a vertex is
supplied by its opposite edge. Order and inversion retain the orientation
information that disappears in the mod-two cycle identities.

### 2.3 Vanishing cycles and local monodromy

For a nodal degeneration with vanishing cycle `delta`, the Picard--Lefschetz
formula acts on first homology by

\[
M_\delta(v)
=
v+\langle v,\delta\rangle\delta
\]

up to the chosen intersection and orientation convention. After the usual
unipotent normalization, a local monodromy has repeated eigenvalue `1`.
Depending on the lift from `PSL(2,Z)` to `SL(2,Z)`, a central sign may replace
`1` by `-1`; either way, the ordinary eigenvalue multiset is not a rich
spectrum.

This negative fact is useful evidence. It forces the proposed spectra away
from a bare cusp matrix and toward an operator built from paths,
correspondences, gluing, or repeated construction.

### 2.4 A common period equation with three singular channels

For a continuously transported cycle in the Legendre family, an elliptic
period `Pi(lambda)` satisfies

\[
\lambda(1-\lambda)\Pi''
+(1-2\lambda)\Pi'
-\frac14\Pi
=0.
\]

This is the hypergeometric equation with parameters `(1/2, 1/2; 1)`. Its
regular singular points are precisely

\[
0,\quad1,\quad\infty.
\]

Analytic continuation of its two-dimensional solution space produces the
monodromy representation associated with the marked elliptic periods. Thus
the three cusp channels already act on a common rank-two carrier. The
Picard--Fuchs equation supplies a precise external calibration for any future
claim that time, space, and construction spectra are three readings of one
underlying program-period system.

### 2.5 Farey transfer operators provide a nontrivial spectrum

Finite `L/R` words act by Möbius transformations and index Farey cylinders.
Minkowski's question-mark function conjugates the Farey map with the dyadic
tent map, transporting binary prefix cylinders to arithmetic boundary
cylinders. This is the exact bridge used in `0033` to write halting mass as a
boundary measure.

Transfer operators of the Farey map have a genuine spectral theory related to
the modular surface, dynamical zeta functions, and the Selberg zeta function.
This supplies an established external example in which:

\[
\text{binary/arithmetic construction words}
\longrightarrow
\text{transfer operator}
\longrightarrow
\text{modular spectral data}.
\]

It does not prove that Adva construction has the same operator. It shows that
the proposed construction-spectrum mechanism is mathematically available in
the exact modular/Farey geometry already under consideration.

### 2.6 Isogeny and Hecke correspondences provide a second spectrum

The E0 scale operation `Y_k` in
[`0032-exact-e0-mobius-cellular-bridge.md`](0032-exact-e0-mobius-cellular-bridge.md)
has determinant/degree behaviour closer to a finite isogeny or Hecke
correspondence than to a modular automorphism. A family of degree-indexed
correspondences is a natural candidate for construction by covering layer.

In classical modular-form theory, commuting Hecke operators act on finite
dimensional spaces, and a normalized eigenform has a `q`-expansion whose
coefficients encode its Hecke eigenvalues. This gives a disciplined candidate
for the relation

\[
\text{birthday or covering degree }n
\longleftrightarrow
q^n\text{ grade}
\longleftrightarrow
\text{construction spectral coefficient }a_n.
\]

No Hecke action on Adva programs has been constructed. The evidence is the
structural compatibility of a degree-indexed covering operation with a known
arithmetic spectral mechanism.

### 2.7 Existing repository evidence requires decorated spectra

The objectification collision and non-naturality proved in
[`0021-surreal-cut-objectification-no-go.md`](0021-surreal-cut-objectification-no-go.md)
show that equal objectified values cannot recover distinct decorated forms.
The same warning applies to spectra: equal eigenvalue multisets cannot recover
different edge operators, source identities, occurrences, or surgery
histories.

The nested E0 surgery and Möbius bridge notes show that checked program wires,
decorated surgeries, and E0 paths can coexist on a finite common carrier, but
only at bounded edge level. They do not yet provide three canonical spectral
closures. Therefore any proposed spectral carrier must retain the operator,
its marking, and an explicit residual rather than only a list of eigenvalues.

## 3. Conservative and safe conclusion

### 3.1 What can currently be stated

The present evidence supports the following bounded conclusions.

1. The three cusps of `X(2)` are exactly the three nonzero mod-two slope
   classes of a marked rank-two period lattice.
2. After choosing a program marking, those classes may consistently be named
   `T`, `S`, and `C`, with `delta_C = delta_T + delta_S` under one orientation
   convention.
3. Their pairwise intersection determinants have absolute value one, so they
   form a minimal Farey triangle rather than three independent coordinate
   axes.
4. The fundamental-group relation gives an exact cyclic sense in which every
   cusp loop is determined by the ordered opposite pair.
5. A single normalized cusp monodromy has trivial ordinary eigenvalues.
   Nontrivial spectra must come from a larger path, transfer, differential,
   correspondence, or gluing operator.
6. The opposite-edge spectral principle is compatible with the modular and
   repository evidence, but it is still a semantic hypothesis rather than a
   proved reconstruction theorem.
7. `Omega_U` may be studied as a boundary mass or critical value of the
   construction-edge dynamics. It is not established as an eigenvalue, a
   modular invariant, or one of the three algebraic cusps.

### 3.2 Minimal candidate carrier

A future bounded calibration may use a research-local object of the form

\[
\mathfrak T
=
\bigl(
  V,\langle-,-\rangle,
  \delta_T,\delta_S,\delta_C,
  K_{SC},K_{CT},K_{TS},
  \operatorname{cl}_T,
  \operatorname{cl}_S,
  \operatorname{cl}_C,
  \mathfrak S_T,
  \mathfrak S_S,
  \mathfrak S_C,
  \chi
\bigr),
\]

where:

- `V` is one exact marked rank-two carrier;
- the three `delta` values are primitive directions with declared signs;
- each `K_AB` is a typed and checked opposite-edge relation;
- each `cl_V` declares how that relation becomes an endomorphism suitable for
  spectral analysis;
- `chi` records orientation and chirality conventions; and
- each `S_V` is a decorated spectral package, not a scalar spectrum.

At minimum,

\[
\mathfrak S_V
=
\bigl(
  \mathcal D_V,
  \sigma(\mathcal D_V),
  \text{multiplicity or spectral measure},
  \text{marking},
  R_V
\bigr).
\]

For nonnormal or infinite-dimensional operators, the resolvent,
pseudospectrum, and domain may be more informative than a point spectrum.
Those choices must be explicit.

### 3.3 Reconstruction must remain partial and certified

The strong triangular reconstruction equations should currently be written as
partial research targets:

\[
T
\dashleftarrow
\operatorname{Reconstruct}_T(\mathfrak S_T;R_T),
\]

\[
S
\dashleftarrow
\operatorname{Reconstruct}_S(\mathfrak S_S;R_S),
\]

\[
C
\dashleftarrow
\operatorname{Reconstruct}_C(\mathfrak S_C;R_C).
\]

The dashed arrow means that reconstruction is defined only on a declared
fragment with a certificate. Spectrum equality alone never authorizes program
identity, an equation cell, contraction, or source reconstruction.

### 3.4 First bounded research obligation

The next exact calibration should remain small while testing the risky idea
rather than only its safe prefix arithmetic:

1. choose one orientation and one exact `T/S/C` marking of the Legendre
   period lattice;
2. compute the three vanishing cycles and monodromy matrices with exact
   integers;
3. place the existing checked causal diamond and its three semantic readings
   on the same marked carrier;
4. define three finite opposite-edge relations without identifying their
   source or occurrence data;
5. declare one explicit spectral closure for each relation and compute its
   exact characteristic polynomial, eigenprojections where defined, and
   residual;
6. test cyclic relabelling, orientation reversal, and the effect of changing
   the initial chart;
7. compare the construction closure with a finite Farey transfer operator and
   with the existing `Y_k` covering action, recording agreement or a precise
   no-go witness.

This calibration should remain in research tests. It does not justify public
time-spectrum, space-spectrum, construction-spectrum, Hecke, or Omega APIs.

## 4. Red-team opinion

### 4.1 The semantic labels are not canonical

The unmarked modular geometry has an `S_3` symmetry permuting the three
cusps. Calling them time, space, and construction requires extra program data.
If the semantics changes under an arbitrary relabelling with no compensating
chart transformation, the proposal is only nomenclature.

The correct invariant may be the oriented triangular relation plus the
observer marking, not three globally named cusp points.

### 4.2 A cusp is not a singular point of the compactified base

`X(2)` is a smooth projective line. The nodal singularity occurs in the
elliptic fibre over a cusp, not in the base point itself. Program claims must
specify whether a singularity belongs to the moduli base, a fibre, a total
space, an operator, or a measure. Moving silently among these meanings would
invalidate the argument.

### 4.3 Opposite-edge semantics is not yet a reconstruction theorem

The relations

\[
\delta_T=\delta_S+\delta_C
\]

modulo two and

\[
\gamma_T=(\gamma_S\gamma_C)^{-1}
\]

in the base fundamental group do not by themselves prove that the full time
semantics can be reconstructed from a space--construction operator. They
provide a topological skeleton. A faithful semantic result still requires a
functor, a reconstruction domain, and a residual theorem.

### 4.4 An edge does not automatically have a spectrum

If `K_SC` maps a space carrier to a construction carrier, its eigenvalues are
undefined. Forming `K_SC* K_SC`, a round trip, a block operator, a monodromy,
or a transfer operator produces different spectra. A result that depends
strongly on an arbitrary closure choice would not be intrinsic.

The first calibration must compare several natural closures and identify
which additional law, if any, selects one.

### 4.5 Eigenvalues are too lossy

Nonisomorphic operators and geometries can be isospectral. Even a full
eigenvalue multiset with multiplicities may lose eigenvectors, spectral
measures, boundary conditions, source identity, and nonnormal behaviour. The
decorated spectral package and residual are mandatory if the theory is to
respect the existing objectification no-go.

### 4.6 The three proposed spectra may live in different categories

A time generator may be unbounded or non-self-adjoint, a spatial Laplacian may
be self-adjoint, and a construction transfer operator may be bounded but
nonnormal. Hecke operators form yet another arithmetic correspondence
algebra. A single word `spectrum` must not conceal these categorical
differences.

The unification target should first be a common spectral calculus or a typed
family of spectral packages, not one undifferentiated eigenvalue set.

### 4.7 Mod-two symmetry erases chirality

Over `F_2`, addition and subtraction coincide. The elegant cyclic identities
therefore forget the signs that distinguish positive from negative
intersection and forward from reverse transport. The theory must lift the
triangle to oriented integer cycles before using it to explain chirality or
time reversal.

### 4.8 Transfer, Hecke, and Picard--Fuchs spectra are not interchangeable

All three are relevant, but they arise from different operators:

- Picard--Fuchs monodromy transports periods in the parameter base;
- a Farey transfer operator sums inverse branches of a dynamical map;
- Hecke operators sum finite isogeny correspondences.

Their relationships require explicit intertwiners. Similar modular notation
or shared `q`-expansions are not sufficient.

### 4.9 Generic halting coefficients should not be expected to be modular

A universal prefix machine produces machine-dependent, lower-c.e., random
halting data. Generic coefficient sequences of this kind will not satisfy the
algebraic recurrences, growth laws, or Hecke multiplicativity of modular
forms. If a modular construction spectrum exists, it must arise from a
special intrinsic program grammar, an observer quotient, an averaged
ensemble, or a residual-corrected shadow. It cannot be assumed for an
arbitrary universal machine.

### 4.10 Omega may be a measure boundary rather than a spectral point

The identity

\[
Z_U(\log2)=\Omega_U
\]

does not imply that `Omega_U` belongs to the operator spectrum. It may instead
be a total mass, a value of a partition function, a singularity of a
determinant, or a boundary value of a resolvent. These are different claims
and should be tested separately.

### 4.11 Finite spectra are vulnerable to spectral pollution

Exact finite matrices are necessary calibrations, but eigenvalues of finite
truncations may fail to converge to the spectrum of an infinite transfer or
causal operator. Any numerical continuation must state the topology of
operator convergence and distinguish genuine limiting spectrum from
truncation artefacts.

### 4.12 Falsification criteria

The triangular spectral proposal should be weakened or rejected if any of the
following persists after reasonable chart choices:

1. no typed opposite-edge closure is compatible with checked graft and slice
   composition;
2. the spectra are dominated by arbitrary closure or boundary-condition
   choices;
3. cyclic cusp relabelling has no coherent action on program semantics;
4. oriented integer lifts destroy the apparent three-way relation;
5. the construction spectrum has no stable relationship to birthday,
   covering degree, or prefix mass; or
6. the Omega relation can be obtained only by inserting the value as an
   external normalization.

The most valuable negative result would be a finite witness showing exactly
which arrow in

\[
\text{opposite edge}
\longrightarrow
\text{spectral closure}
\longrightarrow
\text{decorated spectrum}
\longrightarrow
\text{vertex reconstruction}
\]

cannot be made natural.

## Working summary

The current defensible synthesis is

\[
\boxed{
\mathfrak S_T=\operatorname{Spec}^{\dagger}(\mathcal D_{SC}),
\qquad
\mathfrak S_S=\operatorname{Spec}^{\dagger}(\mathcal D_{CT}),
\qquad
\mathfrak S_C=\operatorname{Spec}^{\dagger}(\mathcal D_{TS}),
}
\]

where `Spec^dagger` means the operator, its declared spectral data, marking,
and residual rather than a bare eigenvalue set. The construction package is
the candidate location for birthday, covering, prefix probability, transfer
or Hecke growth, and an Omega-type critical boundary. The cyclic principle
requires the time and space packages as well.

## Selected references

- T. Tao, "Elliptic Functions and Modular Forms," 2021,
  <https://terrytao.wordpress.com/2021/02/02/246b-notes-3-elliptic-functions-and-modular-forms/>.
- The Stacks Project, "The Legendre Family,"
  <https://stacks.math.columbia.edu/tag/03VA>.
- L. Yang, "Geometry and arithmetic associated to Appell hypergeometric partial differential equations,"
  <https://arxiv.org/abs/math/0309415>.
- F. Catanese, "Monodromy and Normal Forms," 2015,
  <https://arxiv.org/abs/1507.00711>.
- C. Series, "The Modular Surface and Continued Fractions," 1985,
  <https://doi.org/10.1112/jlms/s2-31.1.69>.
- G. Panti, "Multidimensional Continued Fractions and a Minkowski Function,"
  2007, <https://arxiv.org/abs/0705.0584>.
- C. Bonanno, "On the Generalised Transfer Operators of the Farey Map with
  Complex Temperature," 2022, <https://arxiv.org/abs/2211.11664>.
- W. Stein, "Computing with Newforms," in *Modular Forms: A Computational
  Approach*, <https://wstein.org/books/modform/modform/newforms.html>.
- G. Barmpalias, "Aspects of Chaitin's Omega," 2017,
  <https://arxiv.org/abs/1707.08109>.
- C. Schmidhuber, "Chaitin's Omega and an Algorithmic Phase Transition,"
  <https://arxiv.org/abs/1909.09231>.
