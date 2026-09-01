# Finite-Observer Tri-Cusp Surreal Reduction

Status: exploratory synthesis and research specification extending
[`0021-surreal-cut-objectification-no-go.md`](0021-surreal-cut-objectification-no-go.md),
[`0033-omega-type-computational-boundary.md`](0033-omega-type-computational-boundary.md),
[`0034-triangular-spectral-cusp-semantics.md`](0034-triangular-spectral-cusp-semantics.md),
[`0035-decorated-handle-cobordism-calibration.md`](0035-decorated-handle-cobordism-calibration.md),
and
[`0036-triangular-symbolic-interpretation-learning-calculus.md`](0036-triangular-symbolic-interpretation-learning-calculus.md).

This note records the complete current discussion in four deliberately
separated layers: originating intuition, supporting evidence, conservative
conclusions, and red-team objections. It then gives a bounded reduction
contract, a candidate runtime representation, a time-zero calibration, and a
research sequence. It is not a stable Adva API, an unrestricted theorem about
all surreal numbers, a proof that the three program computers are elliptic, a
claim in `claims.toml`, or a change to the active `ProgramSlice` priority.

The motivating confidence is:

> If Conway, as a finite observer, can construct a surreal number from
> admissible left and right options, then a finite program should be able to
> enact the same construction, refine it, and make it move. The ambition is
> not to store a God's-eye completion in memory. It is to program the finite
> observations, certificates, refinements, and residuals through which the
> construction becomes operational.

The central engineering revision is:

> **Dynamics acts on a decorated cut presentation; surreal objectification is
> performed last.** A bare surreal number is an extensional result, not the
> runtime carrier from which program history, scope, sharing, orientation, or
> a reverse process can be reconstructed.

The central mathematical proposal is:

> Forward and reverse computation are two simultaneously active period
> directions of one marked rank-two carrier. The three computers are three
> cyclic readings of that carrier, not three independent pairs of axes. A
> finite observer extracts a bounded spectral vocabulary, builds one shared
> decorated DAG, and produces certified left and right frontiers. Refinement
> may reconstruct the DAG while preserving an explicit residual and the
> coherence of the Conway cuts.

## 0. The reduction problem

The desired object is an observer-relative reduction operation

\[
\operatorname{Reduce}_{Q,B}(P)
=
(G_{Q,B},R_{Q,B},\Pi_{Q,B}),
\]

where:

- `P` is a checked program, arithmetic expression, open expression, or
  decorated history;
- `Q` is a finite observer and its declared task;
- `B` is a finite observation and computation budget;
- `G_(Q,B)` is one finite shared reduction DAG;
- `R_(Q,B)` is the accountable residual outside the operational reduction;
  and
- `Pi_(Q,B)` is a certificate for the laws that were actually checked.

A useful budget has at least four components,

\[
B=(n,\Lambda,K,\varepsilon),
\]

with construction or birthday depth `n`, spectral energy cutoff `Lambda`,
description or graph budget `K`, and numerical certification scale
`varepsilon`. Energy alone cannot make the runtime vocabulary finite: many
different expressions can carry the same period charge. A structural or
observational quotient is also required.

The output contract should eventually enforce six laws:

1. **finiteness:** finite input and budget produce a finite operational DAG;
2. **semantic accountability:** evaluation of the DAG together with the
   residual agrees with the declared source semantics;
3. **cut admissibility:** every certified left option is below every certified
   right option;
4. **tri-cusp covariance:** the three chart readings reduce to one marked
   global state;
5. **refinement coherence:** a finer observer or larger budget refines rather
   than silently contradicts the previous certified observation; and
6. **composition compatibility:** addition, multiplication, grafting,
   substitution, objectification, and truncation commute where certified and
   otherwise emit a residual.

Only after these laws are stated separately can one ask whether the reduction
is canonical, convergent, learnable, or universal.

## 1. Originating intuition

### 1.1 The finite observer is inside the Conway construction

The proper class `No` is not the content of one machine state. Conway's
definition does not require one constructor to enumerate the completed class
before making the next cut. It requires admissible earlier options and the
order condition

\[
L<R.
\]

This suggests an operational inversion of viewpoint. A finite observer does
not receive the whole surreal universe as data. It maintains a finite,
certified frontier

\[
C_{Q,B}=(L_{Q,B}\mid R_{Q,B};D_{Q,B}),
\]

where `D_(Q,B)` retains source, occurrence, scope, period, cocycle, and
residual decorations. Refinement can add or replace frontier witnesses while
preserving the previously certified inequalities.

The finite observer hypothesis is therefore not that every surreal has a
literal finite tree. It is that a useful computational fragment admits finite
presentations or effective refinement procedures whose bounded observations
are Conway-admissible.

### 1.2 Forward and reverse are simultaneous periods

An earlier description treated reverse computation mainly as a learning
pullback or an energy-descending reconstruction. That is only the
representation-level dynamics. At the process level, the revised intuition
is stronger:

> the forward `p` direction and reverse `q` direction coexist and turn at the
> same time.

Let

\[
E_\tau=\mathbf C/(\mathbf Z\omega_+\oplus\mathbf Z\omega_-)
\]

be a marked genus-one carrier. A history has a period grade

\[
h(p,q)=p\omega_+ + q\omega_-.
\]

The two directions define a `Z^2` action when they commute and a projective or
decorated action when their interchange carries a cocycle. The reverse
direction is not a temporal alternation in which the machine runs forward,
stops, and runs backward. Nor is it necessarily the inverse of the forward
operator. It is a second oriented generator.

There are consequently two distinct uses of the word reverse:

1. the intrinsic `q`-period process, simultaneous with the `p`-period
   process; and
2. the observer or learning pullback that revises coefficients, factorization,
   chart, or graph structure from a target or residual.

They may couple, but they must not be identified by notation.

### 1.3 Three computers are three readings of one lattice

Choose oriented primitive cycles

\[
\delta_T=a,
\qquad
\delta_S=b,
\qquad
\delta_C=-a-b.
\]

Then

\[
\delta_T+\delta_S+\delta_C=0
\]

and, for a compatible orientation,

\[
\langle\delta_T,\delta_S\rangle
=
\langle\delta_S,\delta_C\rangle
=
\langle\delta_C,\delta_T\rangle
=1.
\]

Modulo two the signs disappear and the three cycles become exactly

\[
(1,0),\quad(0,1),\quad(1,1),
\]

the three nonzero classes in `P^1(F_2)` used in `0034`. The oriented integer
lift is essential: the mod-two picture alone cannot carry chirality or
distinguish forward from reverse.

Each computer reads the ordered pair on the edge opposite its vertex:

| computer | forward basis direction | reverse basis direction |
|---|---:|---:|
| `T` | `delta_S` | `delta_C` |
| `S` | `delta_C` | `delta_T` |
| `C` | `delta_T` | `delta_S` |

Thus

\[
B_T=(\delta_S,\delta_C),
\qquad
B_S=(\delta_C,\delta_T),
\qquad
B_C=(\delta_T,\delta_S).
\]

They are three oriented bases of one lattice, not six independent axes. If

\[
h=xa+yb,
\]

the exact local coordinates are

\[
\begin{aligned}
(p_C,q_C)&=(x,y),\\
(p_T,q_T)&=(y-x,-x),\\
(p_S,q_S)&=(-y,x-y).
\end{aligned}
\]

No floating-point calibration is needed for these transitions. The order
three matrix

\[
R=
\begin{pmatrix}
0&-1\\
1&-1
\end{pmatrix},
\qquad
R^3=I,
\]

sends `delta_T` to `delta_S`, `delta_S` to `delta_C`, and `delta_C` to
`delta_T`.

### 1.4 The elliptic object unifies two periods and three channels

The most economical internal object is not a collection of three unrelated
cusps. It is a marked elliptic curve with its full nonzero two-torsion. In the
Legendre family

\[
E_\lambda:\qquad y^2=x(x-1)(x-\lambda),
\]

the three nonzero two-torsion points are

\[
P_0=(0,0),
\qquad
P_1=(1,0),
\qquad
P_\lambda=(\lambda,0),
\]

with

\[
P_0+P_1+P_\lambda=0.
\]

This is the elliptic-curve form of the same three-nonzero-elements relation
seen in the mod-two homology lattice. The cusp values `lambda=0,1,infinity`
are three degenerations of this one marked object. They should be read as
three collision or vanishing-cycle channels, not as three independent
initial states.

The three computers may therefore be modelled first by the three nonzero
two-torsion readings, while the three cusps describe their boundary
degenerations. This separates the smooth runtime carrier from its compactified
failure channels.

### 1.5 The first elliptic carrier must retain quasi-periodic history

A bare Weierstrass function is too objectified for the runtime role:

\[
\wp(z+p\omega_1+q\omega_2)=\wp(z).
\]

It identifies all lattice translates and therefore forgets the period path.
Theta and sigma functions instead transform quasi-periodically. Schematically,

\[
\sigma(z+p\omega_1+q\omega_2)
=A_{p,q}(z)\sigma(z),
\]

where the automorphy factor `A_(p,q)` can retain orientation, winding, and a
line-bundle cocycle.

The proposed carrier order is consequently

\[
\boxed{
\text{decorated theta/sigma section}
\longrightarrow
\text{elliptic or lambda shadow}
\longrightarrow
\text{surreal objectification when admissible}.
}
\]

The three theta constants `theta_2`, `theta_3`, and `theta_4`, or equivalently
the three nonzero half-period values, supply one simultaneous three-component
vocabulary. They are not yet identified with the three program computers, but
they are the smallest classical elliptic package with the right level-two
permutation structure.

### 1.6 Period energy gives a finite scale vocabulary

For a fixed marked `tau` in the upper half-plane, the normalized lattice
energy is

\[
Q_\tau(p,q)
=
\frac{|p+q\tau|^2}{\operatorname{Im}\tau}.
\]

It is a positive definite quadratic form. Hence, for every finite cutoff
`Lambda`,

\[
\{(p,q)\in\mathbf Z^2:Q_\tau(p,q)\le\Lambda\}
\]

is finite. This provides a precise first mechanism by which an `H^2` observer
can select a finite spectral vocabulary by scale.

At the equianharmonic calibration

\[
\tau_*=e^{2\pi i/3},
\]

the three primitive directions `1`, `tau_*`, and `-1-tau_*` have the same
length, cyclic rotation is multiplication by `tau_*`, and

\[
Q_{\tau_*}(p,q)
\propto
p^2-pq+q^2.
\]

The energy shells are of `A_2` or hexagonal type. This is a natural symmetric
calibration point, not a claim that every learned or physical state has
`j=0`.

### 1.7 One global DAG, three local views

A mode selected by the finite observer should carry at least

\[
(h=(p,q),\chi,\kappa,\text{spectral packet},\text{residual link}),
\]

where `chi` records marking or chirality and `kappa` records the part of
history not captured by the abelian period grade. The runtime should contain
one hash-consed global DAG. The `T`, `S`, and `C` computers derive their local
coordinates and local interpretations from that object.

Addition, multiplication, and grafting combine charges, but finite energy
sublevels are not closed under those operations. Therefore truncation must
have the form

\[
xy
=
P_\Lambda(xy)
+R_\Lambda(x,y),
\]

not silent deletion. The residual is where out-of-band modes, failed chart
intertwiners, source distinctions, and numerical uncertainty remain visible.

### 1.8 Reverse learning stabilizes a changing graph

The intrinsic `q` direction already exists. Learning uses terminal demands,
prediction error, or residuals to update how the simultaneous `p/q` process
is finitely represented. A representation free energy may have the form

\[
\mathcal F_{Q,B}(G)
=
D_Q(\operatorname{Eval}G,P)^2
+\alpha\operatorname{DL}(G)
+\beta\operatorname{Tail}_\Lambda(G)
+\gamma\operatorname{Instab}(G)
+\delta\operatorname{HolDef}(G).
\]

The semantic or predictive term is mandatory; otherwise the empty or zero
graph is a trivial minimum. A proximal update can permit graph reconstruction,

\[
G_{n+1}
\in
\operatorname*{argmin}_{G'}
\left(
\mathcal F_{Q,B}(G')
+\frac{1}{2\eta}d_{\mathrm{edit}}(G',G_n)^2
\right).
\]

Stability should mean persistence of certified semantics, finite sublevel
control, and coherent observer refinement. It should not mean that the graph
topology never changes. Reconstructing shared subexpressions is part of
learning rather than a failure of identity.

## 2. Supporting evidence

### 2.1 The existing surreal no-go selects the runtime layer

`0021` proves that distinct finite cut presentations can objectify to the same
surreal number and that objectification does not commute with even simple
positive scaling. In particular,

\[
\operatorname{Obj}(0\mid2)
=
\operatorname{Obj}(0\mid3)
=1,
\]

while acting on the options before objectification need not agree with acting
on the objectified result.

This does not show that finite observers cannot construct surreal numbers.
It shows that the runtime action must be

\[
\text{decorated form}
\xrightarrow{\text{program action}}
\text{decorated form}
\xrightarrow{\operatorname{Obj}}
\text{surreal number},
\]

with an explicit residual for the failed naturality square. The negative
result therefore supports, rather than blocks, the decorated-presentation
engine.

### 2.2 The three-cusp rank-two skeleton is exact

`0034` records the exact modular facts:

\[
Y(2)=\Gamma(2)\backslash\mathbb H
\cong
\mathbf P^1\setminus\{0,1,\infty\},
\]

and the three cusps correspond to the three nonzero primitive parity classes.
The three-punctured sphere has a free rank-two fundamental group with the
oriented boundary relation

\[
\gamma_T\gamma_S\gamma_C=1.
\]

This supplies both an abelian rank-two lattice and a noncommutative
opposite-edge skeleton. It does not itself prove program reconstruction, but
the number and incidence of the required channels are not numerology.

### 2.3 One Picard--Fuchs system already sees all three channels

Elliptic periods of the Legendre family satisfy

\[
\lambda(1-\lambda)\Pi''
+(1-2\lambda)\Pi'
-\frac14\Pi
=0.
\]

Its regular singular points are exactly `0`, `1`, and `infinity`, and its
solution space has rank two. Thus one analytic carrier supports all three
cusp continuations. This is direct evidence for studying the three computers
together rather than solving three unrelated local spectral problems.

### 2.4 Classical elliptic functions separate shadow from lift

The double periodicity of `wp`, the quasi-periodicity of sigma and theta, the
three nonzero half-periods, and the theta-constant expression of the modular
lambda function are established classical facts. They provide an exact model
of a pattern already required by the repository no-go results:

\[
\text{history-sensitive section}
\longrightarrow
\text{history-forgetting scalar shadow}.
\]

What remains open is whether the program period data produces the required
line bundle and automorphy factor naturally.

### 2.5 Farey and transfer-operator examples support finite spectral words

Finite `L/R` words already act by Möbius transformations and index Farey
cylinders. Classical transfer operators turn arithmetic branch words into
nontrivial spectral data. `0033` and `0034` record this as an established
external mechanism, not as an existing Adva operator.

The current proposal adds a computational interpretation: a stable finite
spectral packet can serve as a primitive word, and a particular finite change
can be represented by a shared DAG of such words. The exact program operator,
closure, convergence topology, and residual remain to be constructed.

### 2.6 Existing Adva work supplies the intensional data that must survive

The checked finite program work already retains distinctions that a scalar
value or eigenvalue set would lose:

- source and occurrence identity;
- ordered holes and scope paths;
- fork, branch, and recombination roles;
- exact causal slices and surgery history;
- overlapping graft decorations; and
- residuals for failed objectification or transport squares.

`0035` gives one finite handle-shaped cellulation candidate, while `0036`
separates temporal application, spatial open gluing, and constructive scope
assembly. These do not prove an elliptic reduction. They provide the exact
decorations against which any proposed reduction can be falsified.

### 2.7 Finite observers and coherent refinement are already required

`0036` places characteristics on observational quotients

\[
O_Q:\mathcal P\to Z_Q,
\qquad
Z_Q\simeq\mathcal P/{\sim_Q},
\]

and requires dynamics to descend strictly or through a residual. It also
organizes learners over process stage and observer refinement. The present
reduction contract is the surreal and spectral specialization of that
architecture.

### 2.8 Two bounded propositions are already available

For fixed `tau` and finite `Lambda`, positive definiteness of `Q_tau` proves
the **finite period-shell lemma**:

\[
\#\{(p,q)\in\mathbf Z^2:Q_\tau(p,q)\le\Lambda\}<\infty.
\]

The integer formulas in Section 1.3 prove the **tri-chart coordinate lemma**:
one global charge has three exact local coordinate pairs, and cycling the
charts three times returns the original pair. These are small results, but
they are sufficient to make the first calibration exact rather than
metaphorical.

### 2.9 First executable Adva calibration

The research fixture
[`test_finite_observer_tricusp_reduction.py`](../../tests/python/test_finite_observer_tricusp_reduction.py)
implements the first bounded computational layer of this note. A checked Adva
Lisp module, rather than a Python semantic reconstruction, performs:

1. explicit source-preserving fan-out for every repeated coordinate;
2. derivation of the `C`, `T`, and `S` chart coordinates from one global
   charge;
3. the cyclic rotation `R(p,q)=(-q,p-q)`; and
4. the equianharmonic `A_2` energy `p^2-pq+q^2`.

The surrounding Python code is deliberately a research oracle. It enumerates
one finite construction box, partitions it into visible and residual modes
under an energy budget, checks the exact integer formulas, and retains a
separately certified rational Conway cut. The test verifies:

- three cyclic rotations return the original global charge;
- the three local chart readings agree with exact integer formulas;
- the unit energy shell has exactly seven lattice modes;
- energy selection and cut order remain different certificate fields;
- observer refinement adds visible modes without reversing an existing cut;
  and
- two distinct decorated cut presentations remain distinct even when they
  objectify to the same finite surreal.

This fixture does not derive `L/R` from the period energy, introduce theta
data, promote a spectral or surreal API, or make Python an authority for
semantic identity. Its role is narrower and important: the simultaneous
period carrier, exact three-chart calibration, finite mode selection,
residual partition, and form-before-objectification discipline now execute in
the Adva test environment.

## 3. Conservative formal proposal

### 3.1 Three layers of surreal representation

The mechanism must distinguish:

| layer | carrier | computational status |
|---|---|---|
| semantic completion | the proper class `No` | not a runtime container |
| effective presentation | a finite program or guarded rule producing cuts | partial and fragment-relative |
| bounded observation | one finite decorated cut DAG under `(Q,B)` | executable and certifiable |

A machine with a set-sized finite alphabet has only a set of finite strings,
so no uniform finite coding can cover a proper class. The correct runtime
claim is instead

\[
\widehat x:B\longmapsto C_{Q,B},
\]

where `widehat x` is a finite presentation or effective generator and the
bounded cuts satisfy declared refinement laws. Not every surreal is thereby
declared computable or finitely presentable.

A literal finite well-founded Conway DAG reaches only a bounded construction
fragment. Transfinite examples such as `omega` require a finite rule,
iterator, oracle interface, or lazy presentation for an infinite option
family. A cyclic finite graph is not a DAG; if it represents infinite
unfolding, it needs a guardedness or fixed-point semantics and a separate
certificate.

### 3.2 Candidate runtime data

A research-local runtime may use the following conceptual schema:

```text
ObserverBudget
  observer_id
  task_signature
  construction_depth
  energy_cutoff
  description_budget
  certification_precision

GlobalCalibration
  tau_or_modulus
  oriented_basis(a, b)
  cycle_marking(delta_T, delta_S, delta_C)
  level_two_marking
  theta_or_sigma_trivialization
  arithmetic_units_and_primitive_dictionary
  baseline_residual

Presentation
  finite_root_or_guarded_generator
  refine(ObserverBudget) -> FiniteCutDAG
  coherence_certificate
  semantic_identity

Node
  operator
  shared_children
  global_charge(p, q)
  chirality_and_marking
  automorphy_or_commutator_cocycle
  decorated_spectral_packet
  certified_value_enclosure
  residual_link
  reduction_certificate
```

The three local coordinate pairs are derived values. Storing three mutable
copies would create an avoidable calibration drift. Semantic identity,
presentation identity, and numerical approximation identity must also remain
distinct.

### 3.3 Time-zero calibration

The symbol `t=0` denotes computation initialization, not the modular cusp
`lambda=0`. A single smooth global object should be initialized first:

\[
\mathcal I_0
=
(E_{\tau_0},a,b,
\delta_T,\delta_S,\delta_C,
\Theta_0,\mathcal U_0,\mathcal R_0).
\]

Here `Theta_0` denotes the theta/sigma gauge or line-bundle trivialization,
`mathcal U_0` the common arithmetic units and primitive semantic dictionary,
and `mathcal R_0` the declared background residual.

Calibration has four layers:

1. **geometric marking:** orientation, symplectic basis, chirality, three
   cycles, and level-two labels;
2. **arithmetic marking:** zero, unit one, addition, multiplication, hole,
   open, scope, and application primitives in the three interpretations;
3. **spectral marking:** operator domain, boundary condition, theta phase,
   eigen-subspace rather than unstable eigenvector conventions, and numerical
   normalization; and
4. **residual baseline:** the amount of holonomy, chart defect, or background
   curvature present before the first learned update.

The exact chart-transition tests are:

\[
M_{CT}M_{SC}M_{TS}=I,
\]

all three charts assign `(0,0)` to the same zero history, and each primitive
semantic operation commutes with chart transport either exactly or through a
named residual.

One smooth elliptic fibre cannot be simultaneously located at the three
distinct cusps. The time-zero carrier should lie in the interior and carry
three marked degeneration channels. The symmetric value `tau_*` is an
excellent reference calibration and unit-test fixture; a general instance
may start at another `tau_0` and record the transport from the reference.

### 3.4 Reduction pipeline

The proposed bounded pipeline is:

\[
\boxed{
\begin{aligned}
P
&\xrightarrow{\operatorname{Lift}}
\mathsf{Form}^{\dagger}(P)\\
&\xrightarrow{O_Q}
\mathsf{Form}^{\dagger}(P)/{\sim_Q}\\
&\xrightarrow{\operatorname{Grade}}
(p,q,\kappa,\chi)\\
&\xrightarrow{\operatorname{Spec}^{\dagger}_{T,S,C}}
\mathfrak S_{Q,B}\\
&\xrightarrow{P_B+R_B}
G_{Q,B}\oplus R_{Q,B}\\
&\xrightarrow{\operatorname{Cut}}
(L_{Q,B}\mid R_{Q,B};D_{Q,B})\\
&\xrightarrow{\operatorname{Obj}}
x_{Q,B}\in\mathbf{No}.
\end{aligned}
}
\]

The lift retains source, occurrence, sharing, hole, and scope data. The grade
records simultaneous period motion and a nonabelian residual. The decorated
spectrum contains the operator, domain, marking, eigenspaces or spectral
measure, stability data, and residual rather than only eigenvalues. The cut
is objectified only after its order certificate succeeds.

### 3.5 The missing order bridge

The lattice energy orders modes by scale. It does not define the Conway total
order. Equal-energy modes are common, and a lower-energy presentation need
not denote a smaller surreal number. Thus the central open construction is a
chart-covariant certified comparison

\[
\operatorname{Ord}_{Q,B}(x,y)
\in
\{x<y,x=y,x>y,\operatorname{undecided}\}.
\]

It must use more than `(p,q)`: at least oriented form data, theta or holonomy
decoration, the observer task, and exact or certified enclosures. The cut
frontiers are then

\[
L_{Q,B}(P)
=
\{\ell:\operatorname{Ord}_{Q,B}(\ell,P)=\ell<P\},
\]

\[
R_{Q,B}(P)
=
\{r:\operatorname{Ord}_{Q,B}(P,r)=P<r\}.
\]

The **tri-cusp order reconstruction conjecture** asks for a declared fragment
on which:

1. all `ell in L` and `r in R` satisfy `ell<r`;
2. chart rotation preserves the certified comparison;
3. objectification selects the simplest surreal between the two frontiers;
4. changing a harmless rewrite or graph sharing does not change the result;
   and
5. undecidable or numerically unresolved comparisons remain residuals rather
   than guessed signs.

This is the largest current mathematical gap. The identification

\[
p\equiv L,
\qquad
q\equiv R
\]

is not licensed. `p/q` are period degrees; `L/R` are sides of an order cut.
The reduction mechanism must construct the bridge between them.

### 3.6 Coherent finite frontiers

A finite observer need not materialize every option in an infinite cut. It may
maintain finite lower and upper frontiers together with generators for further
refinement. For `B preceq B'`, the desired monotonic pattern is

\[
L_{Q,B}
\preceq
L_{Q,B'},
\qquad
R_{Q,B'}
\preceq
R_{Q,B},
\]

in the sense that new lower evidence moves inward from below and new upper
evidence moves inward from above without violating a certified old
separation. The observer-relative surreal `x_(Q,B)` may change as the
frontiers refine. A stronger convergence theorem would identify conditions
under which the coherent net presents one semantic surreal.

This is a more precise form of the finite-observer Conway intuition: the
machine turns by repeatedly constructing and certifying finite cuts, not by
loading the completed proper class.

### 3.7 Composition and language expansion

Finite energy vocabularies are generally not closed under addition,
multiplication, substitution, or grafting. The reducer therefore needs a
three-way split:

\[
F
=
F_{\mathrm{ren}}
+F_{\mathrm{res}}
+F_{\mathrm{comp}},
\]

where the renormalized part is represented in the current vocabulary, the
residual part is auditable but not operationally compressed, and the
completion part justifies adding a genuinely new primitive. Language
expansion should be minimal, certified by a finite signature or congruence,
and closed under the declared composition rules.

Graph reconstruction is permitted, but it must preserve expression sharing,
semantic certificates, and the presentation/objectification distinction.

### 3.8 Numerical certification

A numerically stable reducer should not identify stability with the smooth
motion of individual eigenvectors. At degeneracies, only invariant spectral
subspaces may be stable. The numerical layer should therefore retain:

- interval or ball enclosures for comparisons and spectral values;
- invariant subspace projectors when eigenvalues cluster;
- resolvent or pseudospectral information for nonnormal operators;
- an explicit topology of operator convergence;
- a test for spectral pollution under truncation; and
- `undecided` results when a strict order cannot be certified.

For each fixed interior `tau`, the period shell is finite. Uniform stability
as `tau` approaches a cusp is a separate theorem: `Q_tau` loses uniform
coercivity along a degenerating direction. A primal/dual, cusp-renormalized,
or compact-collar energy may be required.

### 3.9 Learning contract

At finite stage, the learner should update

\[
(Q,B,\tau,G,\mathfrak S,\operatorname{Ord},R,\Pi),
\]

not only graph weights. It may refine the observer, change the spectral
vocabulary, transport the modulus, refactor the DAG, or add a primitive. Each
update must say which predictions and cut inequalities remain certified.

The desired stability object is a coherent family of finite sublevel
presentations, not one permanently frozen graph. A full-cycle learner remains
open-ended; if its target includes a universal prefix-free halting
characteristic, `0033` and `0036` imply an Omega-type boundary to finite
completion certification.

## 4. Conservative conclusions

The current discussion supports the following bounded statements.

1. A finite observer can manipulate finite decorated Conway forms and
   objectify a form after checking its order condition.
2. The objectified surreal number cannot generally replace the decorated
   form as the runtime carrier.
3. A proper class cannot be uniformly exhausted by ordinary finite machine
   codes; finite presentations and observer-indexed approximants are the
   correct computational target.
4. The three cusp classes arise exactly from one marked rank-two level-two
   structure.
5. An oriented integer lift gives three cyclic bases and exact transition
   matrices for one global period grade.
6. The forward and reverse period directions may consistently be modelled as
   simultaneous, while reverse learning remains a distinct update mechanism.
7. The Legendre family and its three nonzero two-torsion points provide a
   precise classical carrier in which two periods and three degeneration
   channels coexist.
8. Theta or sigma data is a better first history-sensitive carrier than a
   bare elliptic scalar shadow.
9. For fixed interior `tau`, period energy gives finite lattice shells and
   therefore a finite first spectral vocabulary.
10. A finite period shell alone does not make the expression vocabulary
    finite; construction and description bounds or a finite observational
    quotient are also necessary.
11. The three computers should be implemented as three derived views of one
    global decorated DAG.
12. Energy can govern truncation and representation learning, but it does not
    yet produce the Conway `L/R` order.
13. Time-zero calibration is one global marking with three derived charts,
    not three independently initialized computers.
14. A bounded prototype is already specifiable. A complete reduction theorem
    still requires the tri-cusp order bridge and cusp-uniform numerical
    control.

The note does **not** claim:

- that every surreal number has a finite or computable presentation;
- that every finite program has a canonical elliptic modulus;
- that the program `p/q` grades are already Conway left and right options;
- that `wp`, theta, sigma, or lambda is already an Adva runtime object;
- that three semantic labels are canonical without a program marking;
- that all three opposite-edge operators have the same kind of spectrum;
- that exact cyclic symmetry survives every chart and every observer;
- that finite spectral truncations converge without pollution;
- that graph-energy descent proves semantic learning; or
- that an open-ended universal learner can certify its own completion.

## 5. Red-team opinion

### 5.1 Proper-class finite encoding is impossible as a total claim

Finite strings over a set-sized alphabet form a set. They cannot uniformly
name a proper class. Any implementation that advertises a finite encoding of
all surreal numbers without an external class parameter, oracle, or semantic
scheme is misstated. The finite-observer hypothesis must name its representable
fragment and refinement interface.

### 5.2 Literal finite DAGs do not reach transfinite cuts

A finite well-founded cut DAG has only finitely many explicit ancestors.
Symbolic examples such as `omega` require a rule for infinitely many options.
Adding cycles to the graph does not solve this automatically; it changes the
semantic problem to guarded recursion or a fixed point. The implementation
must distinguish sharing DAGs from recursive presentation grammars.

### 5.3 Period abelianization loses program order

Mapping a word to `(p,q)` retains only its abelianized grade. If forward and
reverse generators do not commute, different histories can have the same
grade. A constant projective commutator may be retained by a line-bundle
cocycle. A state-dependent or higher commutator may require a noncommutative
torus, a free-group carrier, or higher genus. Genus one should be rejected if
it cannot carry the checked interchange residual.

### 5.4 Energy is not order

Positive definiteness and finite energy shells solve the selection problem
`which modes are visible?` They do not solve `which option is left?` A
proposal that sorts modes by energy and calls that the Conway order is false
unless an additional order theorem is proved.

### 5.5 The three computers may be an imposed marking

The unmarked level-two geometry permits permutations of the three nonzero
directions. Time, space, and construction meanings require operational data
from application, open gluing, and scope assembly. If the labels survive no
semantic test under chart rotation, the elliptic triangle is only a relabelled
modular picture.

### 5.6 One fibre cannot occupy three cusps

Initializing three machines separately at `0`, `1`, and `infinity` would
compare three degenerate fibres rather than three views of one state. The
simultaneous machine must live first on one smooth marked carrier and expose
three limiting channels. Confusing computation time zero with the zero cusp
would invalidate the calibration.

### 5.7 Theta phases are gauge data

Theta and sigma functions are quasi-periodic only after a lattice, line
bundle, characteristic, and normalization have been chosen. Their automorphy
factors are not observer-independent history labels. The time-zero gauge and
its chart cocycle must be stored and tested.

### 5.8 Finite spectrum is not a finite language

Even one eigenvalue or one charge can have infinitely many intensional program
presentations. A finite vocabulary claim requires a finite signature,
description budget, quotient congruence, or canonicalization theorem in
addition to spectral cutoff.

### 5.9 Cusp degeneration threatens numerical finiteness

For fixed `tau`, every energy sublevel is finite, but the number of cheap
lattice modes need not remain uniformly bounded as `tau` degenerates. A
three-chart description alone does not cure this if all three charts merely
re-express the same degenerating metric. A real stability theorem needs an
explicit renormalization or dual control.

### 5.10 Spectral eigenvalues are too lossy

Isospectral operators can differ in geometry, boundary data, source identity,
and dynamics. Nonnormal operators can have unstable eigenvalues. The runtime
must retain decorated spectral packages, resolvents or projectors where
needed, and residuals. Eigenvalue equality can never authorize program
identity by itself.

### 5.11 Objectification still fails to be natural

Acting on the surreal value and acting on its cut options need not agree. The
new mechanism avoids this only if all program dynamics occurs before
objectification or carries the failed naturality square as residual. Hiding
the decorated form after each step would reproduce the obstruction in
`0021`.

### 5.12 Reverse remains semantically ambiguous

The second period generator, orientation reversal, categorical dual,
analytic adjoint, reverse-mode derivative, and learning pullback are different
operations. A successful calibration may relate some of them. Using one
symbol `d^-` for all of them before that theorem would make the mechanism
unfalsifiable.

### 5.13 Graph energy admits trivial or pathological minima

Without a fixed semantic task, the empty graph minimizes many complexity
energies. With an overly strong residual, the operational graph may appear
small while the residual stores the complete source. Useful compression and
stable learning require a joint bound on operational description, residual
description, predictive error, and reconstruction cost.

### 5.14 A global finite observer may not exist

Three pairwise compatible finite charts need not glue to a bounded global
observer. The global object in the proposal is a marked semantic carrier, not
an assumption that one machine can store every distinction. Nontrivial
holonomy or failure of a global section may be the correct result.

### 5.15 Completion may remain undecidable

A finite observer can keep constructing valid surreal cuts without possessing
a finite certificate that all future relevant options have been seen. If the
source language is universal, the completion problem may include halting
information. Operational success should therefore be measured by bounded
cuts, predictions, certificates, and accountable residuals rather than a
promise of final omniscience.

### 5.16 Falsification criteria

The proposal should be weakened or rejected on a declared fragment if:

1. no nontrivial finite observer produces a cut with certified `L<R`;
2. chart rotation changes an objectified cut with no named residual;
3. the three local coordinate transitions fail exact cycle coherence;
4. no history-sensitive cocycle distinguishes checked words with equal
   `(p,q)` grade;
5. every spectral closure depends predominantly on arbitrary boundary or
   linearization choices;
6. finite sublevels fail to remain finite after the declared expression
   congruence and description budget;
7. numerical comparison repeatedly guesses signs near degeneracy;
8. graph reconstruction destroys source, occurrence, sharing, or scope
   identity;
9. the proposed order oracle requires access to the completed surreal it is
   meant to construct;
10. refinement can reverse an earlier certified inequality without exposing
    a failed certificate;
11. theta or elliptic notation contributes no invariant test beyond the
    original finite transition tables; or
12. the finite-observer engine succeeds only because the residual silently
    contains the entire uncompressed source.

## 6. Research sequence

### Phase 0: freeze the bounded contract

Define `ObserverBudget`, decorated cut frontiers, global period charge,
residual classes, and certificate judgments. Freeze the distinction among:

- process forward/reverse periods;
- orientation reversal;
- analytic or categorical adjoint;
- learning pullback; and
- Conway left/right order.

No implementation should collapse these terms for convenience.

### Phase 1: exact finite Conway kernel

Use a very small checked arithmetic fragment and exact integer or rational
arithmetic. Implement research-local finite forms with hash-consed sharing,
explicit left and right frontiers, source and occurrence decorations, and an
order certificate. Reproduce the `0021` collisions and verify the law:

\[
\text{act on form first, objectify last}.
\]

The first fragment may remain within finite-birthday dyadics. A separate
guarded presentation fixture should then represent one rule-generated cut
such as `omega`, without claiming a general transfinite engine.

### Phase 2: exact tri-chart calibration

At `tau_*`, store one global `(p,q)` charge and derive all three local pairs.
Check:

1. the order-three transition law;
2. equality of the three zero-state readings;
3. consistency of the primitive semantic dictionary;
4. orientation reversal and chirality signs;
5. a finite theta or cocycle table; and
6. exact residual around one full chart circuit.

This phase should use finite transition tables before differential connection
language.

### Phase 3: one simultaneous three-computer fixture

Choose one checked program with nontrivial application, open gluing, scope
assembly, and sharing. Construct one global DAG and three local readings.
Define one finite decorated spectral closure per opposite edge, without
pretending that their operator categories are identical.

The success criterion is not an attractive spectrum. It is a commuting and
auditable diagram from checked program data through all three readings and
back to one global residual.

### Phase 4: prove or refute the order bridge

Construct candidate comparison observables and test whether they induce
finite `L/R` frontiers compatible with the existing surreal order. The first
theorem should be restricted to the smallest nontrivial arithmetic fragment.
Compare at least:

- recursive form comparison;
- oriented period or intersection data;
- theta-phase or automorphy data;
- observer-relative interval enclosures; and
- the simplest-between rule.

A clean finite counterexample is as valuable as a positive theorem.

### Phase 5: stable spectral truncation

Add energy shells, description budgets, invariant-subspace tracking, interval
certification, and residual tails. Test chart changes and controlled motion
toward each cusp. State the exact topology in which truncated operators or
projectors are expected to converge.

### Phase 6: graph reconstruction and learning

Only after the finite reducer is certified should learning be allowed to
change the graph. Introduce a finite set of graph moves, a semantic fidelity
term, residual cost, and a proximal edit penalty. Test whether learned
refactorizations preserve cut inequalities and tri-chart covariance.

### Phase 7: effective completion

Organize bounded outputs into a coherent net over observer refinement and
computation budget. State which presentations converge to a semantic surreal,
which remain observer-relative, and which encounter an Omega-type inability
to certify completion.

## 7. Candidate statements to formalize

### Lemma A: tri-chart coordinate coherence

For the oriented cycles in Section 1.3, every `h in H_1(E,Z)` has the three
displayed integer coordinate pairs, and cyclic transition has order three.

Status: direct finite calculation.

### Lemma B: finite period shell

For fixed `tau in H` and finite `Lambda`, the set of integer charges with
`Q_tau(p,q) <= Lambda` is finite.

Status: direct consequence of positive definiteness.

### Proposition C: no total finite coding of `No`

No set of ordinary finite codes can surject onto the proper class of all
surreal numbers.

Status: foundational size obstruction; it limits the implementation claim but
does not obstruct finite observer-relative construction.

### Conjecture D: finite-observer Conway presentation

There exists a nontrivial program fragment and a family of finite observers
for which `Reduce_(Q,B)` produces coherent decorated cuts, and every successful
cut objectification agrees with the fragment's declared scalar semantics.

Status: principal bounded construction target.

### Conjecture E: tri-cusp order reconstruction

On a declared arithmetic fragment, one decorated global `p/q` carrier with
three cyclic readings determines a chart-covariant certified comparison whose
finite frontiers objectify to the correct surreal value.

Status: principal mathematical bridge; currently unproved.

### Conjecture F: stable finite-DAG sublevels

After quotienting by a finite observer congruence and bounding period energy,
description length, and residual cost, the admissible presentation sublevel is
finite or compact enough to support stable graph reconstruction.

Status: requires precise syntax, topology, and energy.

### Conditional theorem target G: open-ended completion boundary

If the refinement system contains the exact halting characteristic of a
universal prefix-free interpreter, no total computable reducer can terminate
with both the complete characteristic and a valid completeness certificate.

Status: conditional route from the standard Omega obstruction; it does not
limit bounded local reductions.

## Working summary

The proposed engine is

\[
\boxed{
\text{checked program}
\to
\text{decorated finite-observer presentation}
\to
\text{simultaneous }(p,q,\kappa)
\to
\text{one global three-view DAG}
\to
\text{certified }(L\mid R)
\to
\text{surreal objectification}.
}
\]

The three computers are not switched forward and backward in sequence. Their
two period directions coexist, and the three computers are cyclic bases of
one rank-two carrier. Elliptic level-two geometry explains how two periods,
three nonzero torsion readings, and three cusp degenerations can belong to one
object. Theta or sigma data is the candidate history-sensitive lift; `wp`,
`lambda`, eigenvalues, and surreal numbers are progressively more
objectified shadows.

Finite computation is obtained neither by denying the proper class nor by
claiming that energy alone solves everything. It is obtained by naming the
observer and budget, storing a finite presentation or refinement program,
selecting a finite decorated vocabulary, sharing it in one DAG, certifying a
finite Conway cut, and carrying every discarded distinction in an explicit
residual.

The current mechanism is therefore close to a complete research
specification but not yet a complete reduction theorem. The decisive missing
result is the order bridge:

\[
\boxed{
\text{energy determines what is visible;}
\qquad
\text{a still-unbuilt theorem must determine what is left and right.}
}
\]

If that theorem can be proved on a nontrivial finite fragment, the surreal
construction will no longer be only a terminal mathematical object. It will
become an executable, observer-relative process that can be transported,
refined, learned, and made to turn.

## Selected references

- J. H. Conway, *On Numbers and Games*, 2nd ed., A K Peters, 2001.
- H. Gonshor, *An Introduction to the Theory of Surreal Numbers*, Cambridge
  University Press, 1986.
- NIST Digital Library of Mathematical Functions, Chapter 20, "Theta
  Functions," <https://dlmf.nist.gov/20>.
- NIST Digital Library of Mathematical Functions, Chapter 23, "Weierstrass
  Elliptic and Modular Functions," <https://dlmf.nist.gov/23>.
- The Stacks Project, "The Legendre Family,"
  <https://stacks.math.columbia.edu/tag/03VA>.
- C. Series, "The Modular Surface and Continued Fractions," *Journal of the
  London Mathematical Society* 31(1), 1985,
  <https://doi.org/10.1112/jlms/s2-31.1.69>.
- G. Barmpalias, "Aspects of Chaitin's Omega," 2017,
  <https://arxiv.org/abs/1707.08109>.
