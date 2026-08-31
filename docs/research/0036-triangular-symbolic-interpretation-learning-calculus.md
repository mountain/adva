# A Triangular Symbolic Calculus for Computation and Open-Ended Learning

Status: exploratory core research note extending
[`0033-omega-type-computational-boundary.md`](0033-omega-type-computational-boundary.md),
[`0034-triangular-spectral-cusp-semantics.md`](0034-triangular-spectral-cusp-semantics.md),
and
[`0035-decorated-handle-cobordism-calibration.md`](0035-decorated-handle-cobordism-calibration.md).

This note proposes a minimal symbolic architecture rather than a stable Adva
API. It does not promote a claim to `claims.toml`, identify the physical world
with a universal computer, prove a canonical compactification, or claim that
an unrestricted learner can compute a complete world theory. The active
`ProgramSlice` priority and Rust semantic authority remain unchanged.

The central revision is:

> Time, space, and construction are not only three interpretations attached
> to a triangle. They are three modes of computation, three forms of
> locality, and three grammars for unfolding complexity. Each computer
> extracts a characteristic fiber from the opposite process through a finite
> observer's controlled forgetting, and unfolds it in the next domain. A
> feature is therefore not merely a flat section: it is a finite vocabulary
> on an observational quotient, dynamics descends to that quotient, and its
> form survives transport between local observer charts. The triangular
> scheme closes in type, but its lifted history and holonomy need not close.
> A learner of the whole three-cycle must learn the quotient, descended
> dynamics, holonomy, and accountable residual. Its complete characteristic
> may lie at an Omega-type noncomputable boundary.

The note follows the project research format: intuition, evidence and
structural formalization, conservative conclusion, and red-team opinion.

## 1. Intuition

### 1.1 Finite structure is a common symbolic domain

The purpose of a finite formalism is not merely to approximate a completed
infinite object. A finite, composable, auditable syntax can serve as the
common domain of several interpretations. Geometry, time evolution,
construction, probability, and compactification then arise through typed
interpretation rather than being inserted into the syntax as a single final
ontology.

The minimal carrier begins with an oriented triangle

\[
\Delta=(t,X,K),
\]

where:

- `t` is the temporal mode;
- `X` is the spatial mode; and
- `K` is the constructive mode.

Let cyclic rotation be

\[
\rho(t)=X,
\qquad
\rho(X)=K,
\qquad
\rho(K)=t,
\qquad
\rho^3=1.
\]

The triangle is not only a picture. It is a typing discipline for three
different complexity conversions.

### 1.2 A vertex reads the process on its opposite edge

The semantic principle is that a vertex is informed by the oriented process
on the opposite edge. For each mode `v`, introduce a characteristic map

\[
\operatorname{char}_v^{\pm}:
\operatorname{Proc}(\rho v,\rho^2v)
\longrightarrow
C_v.
\]

The superscript records the two orientations of the opposite edge. The result
is a characteristic fiber `C_v`, and a finite characteristic word is written

\[
c_v\in C_v.
\]

The word is not an inert label. It has an interpretation that unfolds a new
term in the next domain:

\[
\operatorname{unfold}_v:
C_v
\longrightarrow
\operatorname{Term}_{\rho v}.
\]

Thus the general motion is

\[
\boxed{
\operatorname{Proc}(\rho v,\rho^2v)
\xrightarrow{\operatorname{char}_v}
C_v
\xrightarrow{\operatorname{unfold}_v}
\operatorname{Term}_{\rho v}.
}
\]

The first arrow condenses a process into a characteristic. The second arrow
expands that finite characteristic through the grammar of another domain.

### 1.3 The exponential is the algebra--function bridge

The symbol `e` must retain its essential scale meaning. It is not merely an
encoding marker. For each mode, choose a matched function theory and algebra:

\[
\mathcal F_v(S_v,Y_v),
\qquad
\mathcal A_v(Y_v).
\]

An admissible generator

\[
A\in\mathcal A_v(Y_v)
\]

must exponentiate to a one-parameter transport

\[
E_{v,A}(s):=e^{sA}.
\]

In the standard linear case the types are

\[
e^{sA}\in\operatorname{End}(Y_v),
\qquad
e^{sA}c\in Y_v.
\]

The transport should satisfy

\[
E_{v,A}(0)=1,
\qquad
E_{v,A}(r+s)=E_{v,A}(r)E_{v,A}(s),
\]

and the generator equation

\[
d_vE_{v,A}(s)=A E_{v,A}(s).
\]

This equation is not licensed for an arbitrary map `A:Y_v -> Y_v`. The
matched algebra and function theory must specify which generators admit a
flow, semigroup, formal exponential, or appropriate nonlinear substitute.

### 1.4 Characteristics are covariantly constant fibers

Define the matched derivative

\[
D_{v,A}:=d_v-A.
\]

A characteristic function satisfies

\[
D_{v,A}f=0.
\]

In the standard case this is equivalent to

\[
f(s)=e^{sA}c,
\qquad
c=e^{-sA}f(s).
\]

The function varies in the ordinary sense, but its transported-back fiber
does not:

\[
d_v\bigl(e^{-sA}f(s)\bigr)=0.
\]

The flat sections are therefore

\[
\mathsf{Flat}_{v,A}=\ker D_{v,A}.
\]

After choosing a reference fiber, for example at `s=0`, the characteristic
vocabulary is

\[
C_{v,A}
=
\{f(0):f\in\mathsf{Flat}_{v,A}\}.
\]

Equivalently, each `c in C_(v,A)` is the transported-back value
`e^(-sA)f(s)` of one flat section. This distinction keeps a function in the
function theory and its finite characteristic word in the construction
vocabulary.

When `Av=lambda v`, the special eigenform law is

\[
e^{sA}v=e^{\lambda s}v,
\qquad
[e^{sA}v]=[v].
\]

The scale changes while the projective or intrinsic form remains. This is the
precise core of the intuition that a characteristic retains its eigenform
under scale action.

### 1.5 Finite observation creates the quotient on which a feature can exist

The previous account begins too late. It explains how a declared feature is
transported, but not how a feature becomes available. A feature requires a
finite observer that cannot retain every distinction in the source process.
For an observer `Q`, write

\[
O_Q:\mathcal P\longrightarrow Z_Q,
\qquad
p\sim_Q p'
\Longleftrightarrow
O_Q(p)=O_Q(p').
\]

The observed state space is an observational quotient

\[
Z_Q\simeq\mathcal P/{\sim_Q}.
\]

A characteristic vocabulary is useful only if it is constant on the fibers
of this observation:

\[
p\sim_Qp'
\Longrightarrow
c_Q(p)=c_Q(p').
\]

Nontrivial fibers are the source of compression. If every observer fiber is
a singleton, the characteristic merely renames the full process. Controlled
forgetting therefore precedes characteristic extraction:

\[
\boxed{
\text{finite observation}
\to
\text{controlled forgetting}
\to
\text{observational quotient}
\to
\text{stable feature}
\to
\text{cross-domain unfolding}.
}
\]

Forgetting must not mean silent destruction. The source process should map to
two coupled channels,

\[
p\longmapsto\bigl(c_Q(p),R_Q(p)\bigr),
\]

where `c_Q` is the finite operational channel and `R_Q` is the audit,
reconstruction, or obstruction residual. Full identity, observational
equivalence, and predictive equivalence are three different relations.

### 1.6 A feature has observational and transport invariance

Covariant constancy alone does not produce a feature. A candidate must first
survive the observer quotient and then retain its eigenform under the chosen
scale or chart transport. Schematically,

\[
C_{Q,A}
=
\operatorname{Inv}(\sim_Q)
\cap
\operatorname{Eig}(E_A).
\]

It must also support descended dynamics. For a process evolution `Phi`, the
strict form is

\[
O_Q\circ\Phi
=
\bar\Phi_Q\circ O_Q.
\]

If strict descent fails, the missing distinction must be exposed through a
residual rather than hidden in the notation. Thus a characteristic is not
just an element of `ker(d-A)`. It is a finite word on a nontrivial quotient
for which the relevant dynamics is well-defined and whose intrinsic form is
stable under transport.

### 1.7 Holonomy is structured memory across local observations

A finite observer generally has local charts rather than one globally exact
description. Let `Q_i` be local observer charts with transition maps

\[
g_{ij}:Z_{Q_i}|_{U_{ij}}\longrightarrow Z_{Q_j}|_{U_{ij}}.
\]

Transport around the oriented triangle can return with nontrivial holonomy:

\[
\operatorname{Hol}_{\gamma,Q}
=
g_{31}g_{23}g_{12}.
\]

The holonomy records history that is invisible in any single local quotient
but survives a circuit of interpretations. A feature may be strictly fixed,
an eigenform, or only projectively fixed:

\[
\operatorname{Hol}_{\gamma,Q}c=\lambda c,
\qquad
[\operatorname{Hol}_{\gamma,Q}c]=[c].
\]

When a connection is available, the candidate expression is

\[
\operatorname{Hol}_{\gamma,Q}
=
\mathcal P\exp\!\left(\oint_\gamma A_Q\right).
\]

Information loss alone does not imply holonomy: lossless systems can also
have nontrivial holonomy. The relevant claim is narrower. Local observation
quotients together with nontrivial transition transport can make history
reappear globally as effective holonomy.

### 1.8 The observer indexes the triangle; it is not a fourth vertex

The finite observer should not be added as a fourth computational mode. It
indexes all three modes:

\[
\Delta_Q=(t_Q,X_Q,K_Q).
\]

Observers form a refinement preorder or category. If `Q preceq Q'`, then
`Q'` distinguishes at least as much as `Q`, with a forgetting map

\[
\pi_{Q'Q}:Z_{Q'}\longrightarrow Z_Q.
\]

The full theory is therefore a family `Q mapsto Delta_Q`, not a view from an
unbounded external observer. Spatial opens, constructive scopes, and
temporal application horizons become observer-indexed:

\[
\tau_Q,
\qquad
\Gamma_Q,
\qquad
T_Q.
\]

There need not be a single global section that simultaneously realizes every
finite observer's distinctions.

### 1.9 A construction word has function semantics

A finite characteristic word must be interpretable as a function, otherwise
it cannot support functional programming. The interpretation is

\[
\llbracket-\rrbracket_A:
C_{v,A}
\longrightarrow
\mathcal F_v(S_v,Y_v),
\]

with

\[
\llbracket c\rrbracket_A(s)=e^{sA}c.
\]

This supplies a partial quote--unfold pair:

\[
\operatorname{quote}_A(f)=e^{-sA}f(s),
\qquad
\operatorname{unfold}_A(c)(s)=e^{sA}c.
\]

On the declared characteristic subtheory one expects

\[
\operatorname{quote}_A(\operatorname{unfold}_A(c))=c.
\]

The reverse direction may require a residual:

\[
\operatorname{unfold}_A(\operatorname{quote}_A(f))
+R_A(f)
\simeq
f.
\]

The residual protects source, occurrence, history, scope, and other
intensional information that the characteristic quotient may forget.

### 1.10 The three computers

The three vertices now carry three different computers.

| Computer | Feature | Output | Grammar |
|---|---|---|---|
| temporal `T` | `c_t` | space | open covers and gluing |
| spatial `X` | `c_X` | construction | scoped assembly and substitution |
| constructive `K` | `c_K` | time | successive application |

In symbols,

\[
\mathfrak T:C_t\longrightarrow\mathsf{OpenTerm}(X),
\]

\[
\mathfrak X:C_X\longrightarrow\mathsf{ScopeTerm}(K),
\]

and

\[
\mathfrak K:C_K\longrightarrow\mathsf{AppTrace}(t).
\]

The cycle converts the form in which complexity exists:

\[
\boxed{
\text{temporal feature}
\to
\text{spatial assembly}
\to
\text{construction assembly}
\to
\text{temporal application}.
}
\]

### 1.11 Three forms of locality

The three generated domains do not use the same composition rule.

In spatial semantics, an open set `U` is the unit of localization. A spatial
term is assembled through restrictions, overlaps, covers, and compatible
gluing.

In construction semantics, a scope or context `Gamma` is the unit of
localization. Terms may be assembled when their free occurrences, sources,
and substitutions are meaningful in the same declared scope.

In temporal semantics, a typed application arrow is the unit of sequential
locality. Terms compose when the output interface of one application matches
the input interface of the next.

The three interfaces are therefore:

| Domain | Local interface | Compatibility condition |
|---|---|---|
| space | overlap `U_i intersect U_j` | restrictions agree |
| construction | shared scope `Gamma` | binding, source, and substitution agree |
| time | adjacent input/output type | applications are composable |

Open sets and scopes should not be called fixed points of arbitrary dynamics.
They are invariant units of meaning under their respective localization and
restriction operations.

### 1.12 The triangle closes in type but not in history

Let one complete three-computer cycle be

\[
\Phi
=
\mathfrak K\circ\mathfrak X\circ\mathfrak T:
\mathcal S\longrightarrow\mathcal S.
\]

This is a typed closure. It does not assert a fixed point. Actual execution
may form an infinite lifted history

\[
S_0
\xrightarrow{\Phi}
S_1
\xrightarrow{\Phi}
S_2
\xrightarrow{\Phi}
\cdots,
\qquad
S_{n+1}\ne S_n.
\]

The base triangle closes, but its history may behave like a lift under a deck
or monodromy transformation

\[
S_{n+1}=\tau S_n.
\]

One circuit can therefore increase birthday, covering layer, construction
depth, or an exact residual without changing the type of the state.

### 1.13 Learning the complete cycle

Once the three arrows compose, the whole cycle becomes a higher process. It
may have its own characteristic map

\[
\operatorname{char}_\triangle:
\operatorname{Orb}(\Phi)
\longrightarrow
C_\triangle.
\]

The target characteristic need not be pointwise fixed. It may retain only an
eigenform:

\[
\operatorname{char}_\triangle(\Phi S)
=
e^{A_\triangle}
\operatorname{char}_\triangle(S),
\]

or projectively

\[
[\operatorname{char}_\triangle(\Phi S)]
=
[\operatorname{char}_\triangle(S)].
\]

The ultimate learner is the program that continually searches for the
characteristics of this complete three-cycle. It is not expected to stand
outside the cycle and return a final world description. It is itself one of
the cycle's finite processes.

## 2. Evidence and structural formalization

### 2.1 A minimal typed signature

A first research signature is

\[
\Sigma_\triangle
=
(
t,X,K,\rho;
d_v^\pm,A_v,E_{v,A},C_v,c_v;
Q,\preceq,O_Q,\sim_Q,R_Q,\pi_{Q'Q};
g_{ij},\nabla_Q,\operatorname{Hol}_{\gamma,Q};
U,\Gamma,@;
\operatorname{res},\operatorname{glue},
\operatorname{sub},\otimes_\Gamma,;
).
\]

Its roles are:

- `t`, `X`, and `K`: temporal, spatial, and constructive sorts;
- `rho`: cyclic rotation of the three sorts;
- `d_v^+` and `d_v^-`: derivatives associated with the two orientations of
  an opposite edge;
- `A_v` and `E_(v,A)`: a generator and its exponentiated transport;
- `C_v` and `c_v`: a characteristic fiber and one finite word;
- `Q`, `preceq`, and `O_Q`: finite observers, their refinement order, and
  observation maps;
- `sim_Q`, `R_Q`, and `pi_(Q'Q)`: observational equivalence, accountable
  residual, and forgetting along observer refinement;
- `g_(ij)`, `nabla_Q`, and `Hol_(gamma,Q)`: local chart transport, a candidate
  connection, and circuit memory;
- `U`: an open-set boundary of spatial localization;
- `Gamma`: a scope boundary of construction localization;
- `@`: typed application;
- `res` and `glue`: spatial restriction and compatible gluing;
- `sub` and `tensor_Gamma`: explicit substitution and same-scope assembly;
- `;`: temporal sequencing.

This is a signature, not yet a complete calculus. Formation, equality,
residual, and interpretation judgments must remain separate.

### 2.2 Rotation and derivative must not be conflated

The cyclic operator satisfies

\[
\rho^3=1.
\]

An exterior or chain derivative often satisfies a nilpotence law such as
`d^2=0`. These laws cannot both be imposed on one untyped operator. The safer
design is:

- `rho` rotates vertices and edge types;
- `d_v^+` and `d_v^-` read variation from the two orientations of the edge
  opposite `v`; and
- rotation covariance relates the three typed derivatives.

A candidate covariance law is

\[
\rho\,d_v^\pm(p)
\simeq
d_{\rho v}^\pm(\rho p).
\]

Whether orientation reversal gives a sign, an adjoint, a dual, or a chirality
change remains part of the future calculus.

### 2.3 Matched algebra and function axioms

For each mode, the matched pair should state at least:

1. which functions belong to `F_v(S_v,Y_v)`;
2. which generators belong to `A_v(Y_v)`;
3. when `E_(v,A)(s)` exists;
4. whether the transport is exact, formal, local, or only a semigroup;
5. how `d_v` acts on the chosen function theory; and
6. which residual is required for quote--unfold reconstruction.

The first calibration laws are

\[
E_{v,A}(0)=1,
\]

\[
E_{v,A}(r+s)=E_{v,A}(r)E_{v,A}(s),
\]

\[
d_vE_{v,A}(s)=AE_{v,A}(s),
\]

and

\[
D_{v,A}f=0
\iff
f(s)=E_{v,A}(s)c.
\]

The linear exponential is a calibration, not a universal ontology. A
nonlinear flow, formal substitution action, or noncommutative ordered
exponential may replace it in another chart.

### 2.4 Spatial grammar: open restriction and gluing

A minimal spatial judgment has the form

\[
U\vdash_X s.
\]

For an inclusion `V subseteq U`, restriction gives

\[
U\vdash_X s
\quad\Longrightarrow\quad
V\vdash_X s|_V.
\]

For a declared cover

\[
U=\bigcup_i U_i,
\]

compatible local terms satisfy

\[
s_i|_{U_i\cap U_j}
=
s_j|_{U_i\cap U_j}.
\]

Their gluing is

\[
U\vdash_X
\operatorname{glue}_U(s_i).
\]

The note does not require the full sheaf axiom as a program law. It records
open cover and compatible gluing as the minimal syntax by which the temporal
computer unfolds spatial complexity.

### 2.5 Construction grammar: scope, application, and explicit substitution

A minimal construction judgment has the form

\[
\Gamma\vdash_K k:K_0.
\]

Same-scope assembly is typed by

\[
\frac{
\Gamma\vdash_K k_1:K_1
\qquad
\Gamma\vdash_K k_2:K_2
}{
\Gamma\vdash_K
k_1\otimes_\Gamma k_2:K
}.
\]

Substitution must remain explicit:

\[
\sigma:\Delta\to\Gamma,
\qquad
\Delta\vdash_K k[\sigma]:K_0[\sigma].
\]

The first compatibility law is

\[
(k_1\otimes_\Gamma k_2)[\sigma]
=
k_1[\sigma]\otimes_\Delta k_2[\sigma].
\]

Application and substitution must not be silently identified. Application
executes a construction against an argument. Substitution changes the scoped
construction and must preserve source and occurrence residuals.

### 2.6 Temporal grammar: successive application

A minimal temporal term is a composable chain

\[
a_0
\xrightarrow{f_1}
a_1
\xrightarrow{f_2}
\cdots
\xrightarrow{f_n}
a_n.
\]

It unfolds as

\[
f_n@(\cdots(f_2@(f_1@a_0))\cdots),
\]

or as the typed sequential composite

\[
f_1;f_2;\cdots;f_n.
\]

Composition requires exact interface agreement. Equality of final values
does not identify histories, applications, or construction occurrences.

### 2.7 The three quote--unfold channels

The complete cyclic proposal is

\[
\operatorname{Proc}(X,K)
\xrightarrow{\operatorname{quote}_t}
C_t
\xrightarrow{\mathfrak T}
\mathsf{OpenTerm}(X),
\]

\[
\operatorname{Proc}(K,t)
\xrightarrow{\operatorname{quote}_X}
C_X
\xrightarrow{\mathfrak X}
\mathsf{ScopeTerm}(K),
\]

and

\[
\operatorname{Proc}(t,X)
\xrightarrow{\operatorname{quote}_K}
C_K
\xrightarrow{\mathfrak K}
\mathsf{AppTrace}(t).
\]

Each channel condenses one kind of complexity from an opposite process and
unfolds it through a different local grammar.

### 2.8 Assembly compatibility

Unfolding should preserve declared assembly. Schematically,

\[
\operatorname{unfold}_v
(\operatorname{assemble}_{C_v}(c_i))
\simeq
\operatorname{assemble}_{\rho v}
(\operatorname{unfold}_v(c_i)).
\]

The three concrete forms are:

- characteristic assembly maps to compatible open gluing;
- characteristic assembly maps to same-scope construction; and
- characteristic assembly maps to successive application.

The equivalence sign must carry a residual whenever the target grammar loses
history, source, scope, or occurrence data.

### 2.9 Complexity conversion is typed, not numerical by default

Let `cx_t`, `cx_X`, and `cx_K` be still-unspecified complexity observables.
The three computers suggest transports

\[
\operatorname{cx}_t(c_t)
\rightsquigarrow
\operatorname{cx}_X(\mathfrak T(c_t)),
\]

\[
\operatorname{cx}_X(c_X)
\rightsquigarrow
\operatorname{cx}_K(\mathfrak X(c_X)),
\]

and

\[
\operatorname{cx}_K(c_K)
\rightsquigarrow
\operatorname{cx}_t(\mathfrak K(c_K)).
\]

No equality, conservation law, or monotonicity is claimed until the task,
observer, units, and residual have been specified. The present claim is only
that complexity changes its representational mode through typed unfolding.

### 2.10 Full-cycle monodromy

The full-cycle operator

\[
\Phi:
\mathcal S\to\mathcal S
\]

returns to the same state type. A semantic fixed point would require

\[
\Phi(S)\simeq S.
\]

The weaker and more useful proposal is a lifted law

\[
S_{n+1}=\tau_n S_n,
\]

where `tau_n` retains the new layer, birthday, history, or residual generated
by one circuit. Projecting away `tau_n` makes the path look closed; retaining
it produces an open lifted history.

This supplies a possible structural relation among triangular rotation,
covering depth, construction grading, and the handle-count direction in
`0035`. No equality among those grades is yet established.

### 2.11 The meta-characteristic of the cycle

Treating `Phi` as a process introduces a higher characteristic theory:

\[
C_\triangle
=
\operatorname{Char}(\operatorname{Orb}(\Phi)).
\]

A strict invariant satisfies

\[
c_\triangle(\Phi S)=c_\triangle(S).
\]

An eigencharacteristic satisfies

\[
c_\triangle(\Phi S)
=
E_{\triangle,A}(1)c_\triangle(S).
\]

The projective form

\[
[c_\triangle(\Phi S)]
=
[c_\triangle(S)]
\]

allows scale, construction depth, or chart to change while intrinsic form is
retained.

### 2.12 The open-ended learner

At finite stage `n` and observer resolution `Q`, a learner may output

\[
\mathcal L_{n,Q}
=
(
C_{t,Q}^{(n)},C_{X,Q}^{(n)},C_{K,Q}^{(n)};
O_Q,\sim_Q,\bar\Phi_Q;
A_t^{(n)},A_X^{(n)},A_K^{(n)};
\mathfrak T_n,\mathfrak X_n,\mathfrak K_n;
C_\triangle^{(n)},A_\triangle^{(n)};
\operatorname{Hol}_{\gamma,Q}^{(n)},R_{n,Q}
).
\]

The output contains:

- current characteristic vocabularies;
- the current observation quotient and dynamics descended to it;
- current algebra--function matches;
- current unfolding interpreters;
- a current hypothesis for cross-chart holonomy;
- a current hypothesis for the whole-cycle eigencharacteristic; and
- an explicit unexplained residual.

Learning updates form a two-dimensional net

\[
\{\mathcal L_{n,Q}\}_{(n,Q)},
\]

with one direction advancing the observed cycles and another refining the
observer. The order should mean predictive refinement and residual
accountability, not literal inclusion of parameter vectors. A chart change
may replace one presentation by another while preserving predictions and
certified structure.

The learner's task is consequently fourfold:

\[
\boxed{
\text{learn cycle feature}
=
\text{learn observation quotient}
+
\text{learn descended dynamics}
+
\text{learn holonomy}
+
\text{manage residual}.
}
\]

It must also learn when its present observer is too coarse and should be
refined. If `N_Q` is the number of distinguishable finite signatures, then a
basic monotonicity check is

\[
Q\preceq Q'
\Longrightarrow
N_Q\le N_{Q'}
\Longrightarrow
\lceil\log_2N_Q\rceil
\le
\lceil\log_2N_{Q'}\rceil.
\]

This does not supply an optimal code, but it ties observer refinement to the
minimum number of bits required to name its distinctions.

Gold's identification-in-the-limit model supplies a narrow external analogy:
a learner may eventually stabilize on a correct representation without being
able to announce the stage at which correctness became permanent. The
present learner is richer and no theorem transfers automatically, but the
distinction between eventual adequacy and finite certification is directly
relevant.

### 2.13 The observation quotient is the missing generation layer

For each vertex `v`, the revised quote--unfold channel is

\[
\boxed{
P
\xrightarrow{O_Q}
P/{\sim_Q}
\xrightarrow{\operatorname{char}_{v,Q}}
C_{v,Q}
\xrightarrow{\operatorname{unfold}_{v,Q}}
\operatorname{Term}_{\rho v,Q}.
}
\]

The characteristic map must factor through `O_Q`. The dynamics must descend
strictly or through an explicit residual. These are separately testable
conditions; neither follows from the eigenform equation.

For a finite calibration, the kernel pairs of `O_Q` can be enumerated
exactly. One can then check:

1. which source distinctions are identified;
2. whether `c_(v,Q)` is constant on every identified pair;
3. whether `Phi` maps equivalent states to equivalent states;
4. which failures are captured by `R_Q`; and
5. whether refinement `Q preceq Q'` commutes with the forgetting maps.

### 2.14 Observer charts and effective holonomy

Given finite charts `Q_1`, `Q_2`, and `Q_3`, a bounded model can store exact
transition tables `g_(12)`, `g_(23)`, and `g_(31)`. Their composite defines a
finite circuit operator

\[
H_Q=g_{31}g_{23}g_{12}.
\]

This permits three distinct finite questions:

1. is `H_Q` the identity on observed states;
2. is a selected characteristic fixed or an eigenform of `H_Q`; and
3. does the residual reconstruct the difference between local closure and
   the lifted source history?

The finite transition-table formulation should precede differential
connection language. The latter becomes justified only when a coherent
family of refinements supports a limiting connection-like object.

### 2.15 Omega as a conditional completion boundary

Assume, as an additional hypothesis, that the complete triangular machine
contains a universal prefix-free interpreter `U`. Its halting probability is

\[
\Omega_U
=
\sum_{U(p)\downarrow}2^{-|p|}.
\]

Let `H_n` be the finite set of programs whose halting has been certified by
stage `n`. Then

\[
\Omega_{U,n}
=
\sum_{p\in H_n}2^{-|p|}
\]

is computable and

\[
\Omega_{U,0}
\le
\Omega_{U,1}
\le
\cdots
\longrightarrow
\Omega_U.
\]

For a universal prefix-free machine, `Omega_U` is a left-computably
enumerable algorithmically random real and is not computable. Therefore no
general finite stopping certificate can announce that the full halting mass
has been captured.

This supports a precise conditional statement:

> If learning the complete three-cycle includes learning the exact halting
> characteristic of a universal prefix-free interpreter, no total computable
> learner can terminate with that complete characteristic and a valid
> completeness certificate.

It does not prove that every local computation is nonterminating, that the
physical world is a prefix-free universal machine, or that every failure of
learning is an Omega phenomenon.

### 2.16 Relationship to the current Adva calibration

The finite handle cellulation in `0035` already contains shadows of the three
grammars:

- quadrilateral patches and boundary circles give one spatial open-gluing
  presentation;
- ordered ports and `then` give one temporal composition presentation; and
- event identities, branch roles, and tensor placement give one construction
  presentation.

The existing test does not separate these three roles into a symbolic
calculus. It is one interpretation sample. It should not be relabelled as an
implementation of the present theory.

The next finite calibration should choose one very small program and record,
for the same checked execution:

1. a finite observer and the exact distinctions it forgets;
2. its temporal application chain;
3. its spatial open cover and compatible gluing;
4. its construction scopes and explicit substitutions;
5. the three characteristic words extracted from observation quotients;
6. one complete typed cycle and its chart-transition holonomy; and
7. the exact residual after returning to the original state type.

## 3. Conservative and safe conclusion

### 3.1 What the present note establishes

The note establishes a coherent research architecture with the following
features:

1. a three-sorted symbolic domain `(t,X,K)`;
2. an opposite-edge characteristic principle;
3. a matched algebra--function bridge through `e^(sA)` and `D_(v,A)`;
4. characteristic words with executable function semantics;
5. three distinct locality grammars: opens, scopes, and applications;
6. three cyclic complexity-unfolding computers;
7. typed closure of one full cycle without semantic fixed-point closure;
8. a higher characteristic problem for the complete cycle;
9. finite observers whose controlled forgetting creates observational
   quotients;
10. a two-part invariance law: constancy on observer fibers and eigenform
    stability under transport;
11. local observer charts whose circuit transport can carry holonomy;
12. an observer-indexed, open-ended learner that emits finite theories and
    explicit residuals; and
13. a conditional route from universal prefix-free computation to an
    Omega-type inaccessible completion boundary.

These items form a disciplined proposal. They are not yet theorems about all
Adva programs, AEG, learning systems, or the physical world.

### 3.2 Minimal research object

A bounded finite state should be research-local and approximately typed as

\[
\mathbb T_n
=
(
\Delta,
Q,\preceq,O_Q,\sim_Q,
\rho,
P_t,P_X,P_K,
C_{t,Q},C_{X,Q},C_{K,Q},
A_t,A_X,A_K,
U,\Gamma,\mathsf{App},
\Phi,\bar\Phi_Q,
g_{12},g_{23},g_{31},\operatorname{Hol}_{\gamma,Q},
\tau_n,
R_{n,Q}
).
\]

It must retain:

- the exact finite source process;
- the observer, its quotient fibers, and its refinement relation;
- all three interpretations without identifying them;
- characteristic maps and their domains;
- open-cover, scope, and application interfaces;
- source and descended complete-cycle transitions;
- local chart transitions and their circuit holonomy;
- the lifted layer or monodromy residual; and
- the observation task under which the characteristics were selected.

No interpretation may create program identity.

### 3.3 Proposed research sequence

The safest high-pressure sequence is:

1. choose two finite observers of one source process, with one strictly
   refining the other;
2. enumerate their quotient fibers and exact residuals;
3. write a formal grammar and typing judgments for the three domains;
4. choose one finite Adva fixture with nontrivial application, scope, and open
   gluing;
5. implement research-local quote and unfold maps for that fixture;
6. test quotient constancy, dynamics descent, and residual reconstruction;
7. compose three finite chart transitions and calculate exact holonomy;
8. learn a bounded characteristic of repeated `Phi` across both observers;
9. red-team identifiability under observer, chart, and scope changes;
10. only then introduce weighted prefix codes and completion; and
11. compare the effective boundary with a machine-specific `Omega_U`.

The work should remain in research notes and bounded tests until the carriers
and no-go results stabilize.

### 3.4 What would count as real progress

The next result should not be another suggestive renaming. It should provide
at least one of:

- a finite model satisfying all three grammars and their compatibility laws;
- a proof that one characteristic extractor is invariant under a declared
  observation quotient and scale action;
- a finite nontrivial holonomy calculation with an exact audit residual;
- a counterexample showing that one triangular rotation cannot preserve the
  required residual;
- an identifiable finite family of full-cycle operators;
- a no-go theorem separating eventual learning from finite certification; or
- an exact obstruction to expressing one domain's locality in another.

### 3.5 Claims explicitly not made

The present note does not claim:

- that all features are eigenvectors;
- that information loss alone creates holonomy;
- that an observer-independent characteristic vocabulary exists;
- that every observation quotient supports descended dynamics;
- that every algebraic operator exponentiates;
- that every open set is dynamically invariant;
- that scopes are literally topological opens;
- that three complexity measures are equal or conserved;
- that the triangle has exact cyclic symmetry in every chart;
- that `Phi` has a computable fixed point or spectrum;
- that a universal learner exists for arbitrary process families;
- that an Omega number is independent of the chosen machine; or
- that physical nonclosure follows from Chaitin's theorem.

## 4. Red-team opinion

### 4.1 The triangle may be only a relabelling

Three names and three arrows do not create a theory. The proposal gains
content only when the three local interfaces differ operationally and the
conversion maps make falsifiable predictions. A fixture in which open gluing,
scope substitution, and function application all reduce to the same list
concatenation would not calibrate the theory.

### 4.2 The exponential may not exist

For unbounded linear operators, nonlinear maps, partial programs, and
noncommutative generators, `e^(sA)` may fail to exist globally, require an
ordering, or live only as a formal series. The matched algebra--function pair
must state its analytic or formal domain. Exponential notation cannot supply
that theorem.

### 4.3 A characteristic depends on the chosen transport

The equation

\[
c=e^{-sA}f(s)
\]

defines a characteristic only after `A`, the function space, and the action
have been chosen. Different admissible generators can yield different
characteristic vocabularies. The theory must explain whether `A` is declared,
learned, or determined by a universal property.

### 4.4 Open sets are localization units, not generic invariants

An open set can move under dynamics and need not be preserved by a process.
Its robust role is closure under spatial localization, restriction, inverse
image under continuous maps, and compatible gluing. Any stronger invariance
claim requires a declared action.

### 4.5 Scopes are not automatically spaces

Contexts and scopes support weakening, substitution, binding, and dependency.
They do not automatically carry intersections, covers, or sheaf gluing. The
parallel with open sets is structural and must be mediated by explicit maps.

### 4.6 Application loses intensional history easily

Two application chains can compute the same final value while differing in
source, cost, sharing, occurrence, and causal history. Temporal equality must
not erase those differences. The residual discipline from earlier Adva
no-go results remains mandatory.

### 4.7 Complexity conversion has no measure yet

The phrases temporal complexity, spatial complexity, and construction
complexity are typed directions, not current numerical invariants. Without a
task, observer, units, and comparison law, a conservation equation would be
empty or false.

### 4.8 Typed closure is not a world fixed point

The fact that `Phi:S -> S` is composable does not imply `Phi(S)=S`, periodic
execution, recurrence, compactness, or semantic completeness. The covering
and monodromy language is a candidate interpretation of the residual, not a
deduced theorem.

### 4.9 Omega must remain machine-specific and conditional

An Omega number is attached to a chosen universal prefix-free machine. It
does not by itself imply that every computation fails to halt or that the
physical world never closes. The present bridge is valid only when the
triangular learner contains the corresponding universal prefix-free halting
problem.

### 4.10 Learning in the limit is not universal prediction

Gold's framework shows how a learner may stabilize without knowing that it
has stabilized, but learnability depends strongly on the hypothesis class and
the information presentation. It does not provide a learner for arbitrary
computable worlds. The triangular theory must state its process family,
observations, negative evidence, and identifiability assumptions.

### 4.11 The meta-characteristic may itself be uncomputable

If `C_triangle` fully classifies the behavior of a universal interpreter, the
desired characteristic may be noncomputable. A useful learner must therefore
produce bounded invariants, predictions, certificates, and residuals rather
than silently assuming access to the completed characteristic.

### 4.12 Exact cyclic symmetry may break

Time, space, and construction may admit only a lax, adjoint, projective, or
chirality-sensitive cyclic relation. Forcing exact `rho` symmetry could erase
the same directional information that the positive and negative derivatives
were introduced to preserve.

### 4.13 Compression is not automatically useful information loss

A quotient can discard precisely the distinction needed for prediction or
composition. Smaller representation is not evidence of a better feature.
The quotient must be justified by a task, support descended dynamics, and
retain failures in `R_Q`. If the residual simply stores the complete source,
the operational channel may compress while the total representation does
not; that is still auditable but not a compression theorem.

### 4.14 Information loss does not entail holonomy

Holonomy occurs in lossless geometric settings, while many lossy quotients
have trivial circuit transport. The theory must not infer one from the
other. Its testable object is the composite of declared chart transitions.
The phrase effective holonomy is warranted only when local quotients and
their transport explain an observed global circuit memory.

### 4.15 Every characteristic is observer-relative

A coarse observer may report a stable feature that disappears under
refinement; a fine observer may distinguish states irrelevant to the task.
Neither observer is automatically true in an absolute sense. Claims must
name `Q`, the task, the refinement maps, and the equivalence relation under
which predictions are preserved.

### 4.16 A global observer or global section may not exist

Compatible pairwise observer charts need not glue to one bounded global
observer. Treating their union as a God's-eye state can silently reintroduce
unbounded memory and destroy the finite-observer thesis. Nonexistence or
noncomputability of a global section is a legitimate outcome, not a defect
to hide.

### 4.17 Falsification criteria

The proposal should be weakened or rejected if any of the following occurs:

1. no finite fixture exhibits genuinely different open, scope, and
   application grammars;
2. opposite-edge characteristics cannot be typed without circular
   definitions;
3. no matched algebra--function pair supports the required quote--unfold law;
4. cyclic rotation necessarily destroys source or occurrence information;
5. full-cycle composition cannot retain an exact residual;
6. no nontrivial observation quotient preserves the declared prediction
   task;
7. the alleged meta-characteristic changes arbitrarily under harmless chart
   refinements;
8. chart holonomy depends only on an arbitrary presentation and survives no
   declared equivalence;
9. learning success depends on an oracle equivalent to the target
   characteristic;
10. the prefix code is not effective or not prefix-free;
11. the proposed Omega comparison is invariant under no declared machine
   equivalence; or
12. the three complexity conversions cannot be distinguished empirically or
    formally.

## Working summary

The proposed minimal motion is

\[
\boxed{
P
\xrightarrow{O_Q}
P/{\sim_Q}
\xrightarrow{\operatorname{char}_{v,Q}}
C_{v,Q}
\xrightarrow{\operatorname{unfold}_{v,Q}}
\operatorname{Term}_{\rho v,Q}.
}
\]

Its three instances are

\[
C_t\xrightarrow{\mathfrak T}\mathsf{OpenTerm}(X),
\qquad
C_X\xrightarrow{\mathfrak X}\mathsf{ScopeTerm}(K),
\qquad
C_K\xrightarrow{\mathfrak K}\mathsf{AppTrace}(t).
\]

Characteristics are finite vocabularies on nontrivial observational
quotients. They are covariantly constant or eigenform fibers generated by a
matched algebra and function theory, and the dynamics must descend to their
observer quotient:

\[
D_{v,A}f=0,
\qquad
f(s)=e^{sA}c,
\qquad
O_Q\Phi=\bar\Phi_QO_Q.
\]

The finite observer indexes the whole triangle, `Delta_Q`, rather than
becoming a fourth vertex. Local observer charts may carry circuit memory

\[
\operatorname{Hol}_{\gamma,Q}=g_{31}g_{23}g_{12},
\]

while the two-channel representation `(c_Q,R_Q)` keeps operational
compression separate from audit and reconstruction.

The complete cycle

\[
\Phi
=
\mathfrak K\circ\mathfrak X\circ\mathfrak T
\]

closes in type while its lifted history can remain open. The learner searches
over a two-dimensional net of cycle stages and observer refinements. It must
learn the quotient, descended dynamics, holonomy, and residual. If that
search contains a universal prefix-free halting problem, its complete halting
characteristic has an Omega-type noncomputable boundary.

The finite syntax is therefore not the final ontology. It is the common
constructive carrier on which interpretation, cyclic computation, learning,
and inaccessible completion can be stated together without erasing their
differences.

## Selected references

- G. J. Chaitin, "A Theory of Program Size Formally Identical to Information
  Theory," *Journal of the ACM* 22(3), 1975,
  <https://doi.org/10.1145/321892.321894>.
- E. M. Gold, "Language Identification in the Limit," *Information and
  Control* 10(5), 1967,
  <https://doi.org/10.1016/S0019-9958(67)91165-5>.
- M. Abadi, L. Cardelli, P.-L. Curien, and J.-J. Levy, "Explicit
  Substitutions," *Journal of Functional Programming* 1(4), 1991,
  <https://doi.org/10.1017/S0956796800000186>.
- J. Cartmell, "Generalised Algebraic Theories and Contextual Categories,"
  *Annals of Pure and Applied Logic* 32, 1986,
  <https://doi.org/10.1016/0168-0072(86)90053-9>.
- C. S. Calude, M. J. Dinneen, and C.-K. Shu, "Computing a Glimpse of
  Randomness," *Experimental Mathematics* 11(3), 2002,
  <https://doi.org/10.1080/10586458.2002.10504481>.
