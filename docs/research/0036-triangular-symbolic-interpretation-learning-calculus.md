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
> extracts a characteristic fiber from the opposite process and unfolds it
> in the next domain. The triangular scheme closes in type, but its lifted
> history need not close. A learner of the whole three-cycle is therefore an
> open-ended theory-generating process whose complete characteristic may lie
> at an Omega-type noncomputable boundary.

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

### 1.5 A construction word has function semantics

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

### 1.6 The three computers

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

### 1.7 Three forms of locality

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

### 1.8 The triangle closes in type but not in history

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

### 1.9 Learning the complete cycle

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

At finite stage `n`, a learner may output

\[
\mathcal L_n
=
(
C_t^{(n)},C_X^{(n)},C_K^{(n)};
A_t^{(n)},A_X^{(n)},A_K^{(n)};
\mathfrak T_n,\mathfrak X_n,\mathfrak K_n;
C_\triangle^{(n)},A_\triangle^{(n)};
R_n
).
\]

The output contains:

- current characteristic vocabularies;
- current algebra--function matches;
- current unfolding interpreters;
- a current hypothesis for the whole-cycle eigencharacteristic; and
- an explicit unexplained residual.

Learning updates form a chain

\[
\mathcal L_0
\preceq
\mathcal L_1
\preceq
\mathcal L_2
\preceq
\cdots.
\]

The order should mean refinement and residual accountability, not necessarily
literal inclusion of parameter vectors. A chart change may replace one
presentation by another while preserving predictions and certified
structure.

Gold's identification-in-the-limit model supplies a narrow external analogy:
a learner may eventually stabilize on a correct representation without being
able to announce the stage at which correctness became permanent. The
present learner is richer and no theorem transfers automatically, but the
distinction between eventual adequacy and finite certification is directly
relevant.

### 2.13 Omega as a conditional completion boundary

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

### 2.14 Relationship to the current Adva calibration

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

1. its temporal application chain;
2. its spatial open cover and compatible gluing;
3. its construction scopes and explicit substitutions;
4. the three characteristic words extracted from opposite processes;
5. one complete typed cycle; and
6. the exact residual after returning to the original state type.

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
9. an open-ended learner that emits finite theories and explicit residuals;
   and
10. a conditional route from universal prefix-free computation to an
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
\rho,
P_t,P_X,P_K,
C_t,C_X,C_K,
A_t,A_X,A_K,
U,\Gamma,\mathsf{App},
\Phi,
\tau_n,
R_n
).
\]

It must retain:

- the exact finite source process;
- all three interpretations without identifying them;
- characteristic maps and their domains;
- open-cover, scope, and application interfaces;
- the complete-cycle transition;
- the lifted layer or monodromy residual; and
- the observation task under which the characteristics were selected.

No interpretation may create program identity.

### 3.3 Proposed research sequence

The safest high-pressure sequence is:

1. write a formal grammar and typing judgments for the three domains;
2. choose one finite Adva fixture with nontrivial application, scope, and open
   gluing;
3. implement research-local quote and unfold maps for that fixture;
4. test cyclic typing and residual reconstruction;
5. define one finite full-cycle operator `Phi`;
6. learn a bounded characteristic of repeated `Phi` from generated traces;
7. red-team identifiability under chart and scope changes;
8. only then introduce weighted prefix codes and completion; and
9. compare the effective boundary with a machine-specific `Omega_U`.

The work should remain in research notes and bounded tests until the carriers
and no-go results stabilize.

### 3.4 What would count as real progress

The next result should not be another suggestive renaming. It should provide
at least one of:

- a finite model satisfying all three grammars and their compatibility laws;
- a proof that one characteristic extractor is invariant under a declared
  scale action;
- a counterexample showing that one triangular rotation cannot preserve the
  required residual;
- an identifiable finite family of full-cycle operators;
- a no-go theorem separating eventual learning from finite certification; or
- an exact obstruction to expressing one domain's locality in another.

### 3.5 Claims explicitly not made

The present note does not claim:

- that all features are eigenvectors;
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

### 4.13 Falsification criteria

The proposal should be weakened or rejected if any of the following occurs:

1. no finite fixture exhibits genuinely different open, scope, and
   application grammars;
2. opposite-edge characteristics cannot be typed without circular
   definitions;
3. no matched algebra--function pair supports the required quote--unfold law;
4. cyclic rotation necessarily destroys source or occurrence information;
5. full-cycle composition cannot retain an exact residual;
6. the alleged meta-characteristic changes arbitrarily under harmless chart
   refinements;
7. learning success depends on an oracle equivalent to the target
   characteristic;
8. the prefix code is not effective or not prefix-free;
9. the proposed Omega comparison is invariant under no declared machine
   equivalence; or
10. the three complexity conversions cannot be distinguished empirically or
    formally.

## Working summary

The proposed minimal motion is

\[
\boxed{
\operatorname{Proc}(\rho v,\rho^2v)
\xrightarrow{\operatorname{char}_v}
C_v
\xrightarrow{\operatorname{unfold}_v}
\operatorname{Term}_{\rho v}.
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

Characteristics are covariantly constant or eigenform fibers generated by a
matched algebra and function theory:

\[
D_{v,A}f=0,
\qquad
f(s)=e^{sA}c.
\]

The complete cycle

\[
\Phi
=
\mathfrak K\circ\mathfrak X\circ\mathfrak T
\]

closes in type while its lifted history can remain open. The learner searches
for characteristics of this entire cycle and emits an unbounded sequence of
finite, testable theories with explicit residuals. If that search contains a
universal prefix-free halting problem, its complete halting characteristic
has an Omega-type noncomputable boundary.

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
