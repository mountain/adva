# Atiyah's Local-to-Global Vision and a Legendre Triadic Crossing Calibration

Status: exploratory synthesis and finite research calibration extending
[`0036-triangular-symbolic-interpretation-learning-calculus.md`](0036-triangular-symbolic-interpretation-learning-calculus.md),
[`0038-triadic-characteristic-inference-calibration.md`](0038-triadic-characteristic-inference-calibration.md),
[`0039-square-map-branch-copy-calibration.md`](0039-square-map-branch-copy-calibration.md),
[`0040-cube-equivariance-degree-calibration.md`](0040-cube-equivariance-degree-calibration.md),
and
[`0041-elliptic-isogeny-triadic-characteristics.md`](0041-elliptic-isogeny-triadic-characteristics.md).

The executable finite calibration is
[`tests/python/test_legendre_triadic_crossing.py`](../../tests/python/test_legendre_triadic_crossing.py).

This note has two purposes.

First, it records a historical and conceptual alignment that should not be
lost.  In *Mathematics in the 20th Century*, Michael Atiyah selected the move
“from local to global” as his first major theme.  He emphasized that functions
and differential equations came to be understood through global data and the
distribution of their singularities rather than only through explicit local
formulae.  In the same essay he gave an unusually direct interpretation of
the geometry--algebra divide:

> Algebra is concerned with manipulation in time and geometry is concerned
> with space.

This is strikingly close to the temporal and spatial sides of the current
Adva research programme.  It is prior art for the time--space intuition and
must be acknowledged as such.

Second, the note identifies the narrower place where a new contribution may
remain possible.  The constructive domain is not merely another name for
algebra.  It records the typed program, source and occurrence identity,
sharing, scope, factorization, rewrite path, proof object, and residual through
which a temporal computation becomes a persistent object and through which a
spatial structure becomes executable.  The research question is whether one
singular boundary event has coordinated temporal, spatial, and constructive
realisations, together with a genuinely triadic coherence defect that cannot
be recovered from any one pair of domains.

The Legendre family supplies the first bounded classical calibration:

\[
E_\lambda:
\qquad
y^2=x(x-1)(x-\lambda),
\qquad
\lambda\in\mathbf P^1\setminus\{0,1,\infty\}.
\]

Its three cusps provide:

- three exact branch-point collisions in the constructive presentation;
- three vanishing directions and Dehn twists in the spatial topology;
- three period monodromies in the temporal or dynamical reading; and
- a central sign that disappears projectively but survives in a selected
  `SL(2,Z)` lift.

This is not yet an `Omega` theorem.  It is a finite classical model of a more
modest phenomenon:

> the base or projective description can close while a lifted carrier retains
> a central residual.

The note remains research-local.  It does not add a stable singularity,
vanishing-cycle, braid, Dehn-twist, period, monodromy, projective-local-system,
central-extension, `Omega`, or triadic-crossing API.  It does not modify
`claims.toml`, and it does not change the active `ProgramSlice` priority or
Rust semantic authority.

---

## 0. Executive statement

The current proposal can be compressed into one diagram:

\[
\boxed{
\text{branch construction crossing}
\longrightarrow
\text{vanishing-cycle surgery}
\longrightarrow
\text{period/history monodromy}.
}
\]

For a cusp `c`, the three realisations are provisionally

\[
J_c^K,
\qquad
J_c^X,
\qquad
J_c^t.
\]

They should not be identified.  They should be connected by typed
interpretation maps and comparison certificates:

\[
\rho_{KX}(J_c^K)\simeq J_c^X,
\qquad
\rho_{Xt}(J_c^X)\simeq J_c^t.
\]

The strong future question is whether there is a common boundary
characteristic

\[
\mathsf C_c
\]

such that

\[
\rho_K(\mathsf C_c)=J_c^K,
\qquad
\rho_X(\mathsf C_c)=J_c^X,
\qquad
\rho_t(\mathsf C_c)=J_c^t,
\]

and whether the three pairwise comparison squares assemble into a coherent
cube.  Its total defect, if nontrivial, is denoted

\[
\Theta_c.
\]

A theory becomes genuinely triadic only if `Theta_c` contains information
that cannot be reconstructed from any one or two of the domains.

---

# Part I. Atiyah's diagnosis

## 1. From local formulae to global organisation

Atiyah described one of the central changes of twentieth-century mathematics
as a move from local to global.  His examples are directly relevant here.

For a classical complex analyst, a function could be represented by an
explicit formula or local power series.  The global turn replaced that
exclusive emphasis by questions such as:

- where the function is defined;
- where it is singular;
- how singularities are distributed;
- what continuation around singularities does; and
- which global object is determined by those data.

The same shift occurred for differential equations.  A solution need not be
available as one explicit elementary formula.  Its singularities,
continuation, asymptotics, and global solution sheaf can carry the decisive
information.

This suggests the first methodological principle for Adva:

> A characteristic should not be sought only as a local expression.  Its
> boundary, singular, continuation, and residual data may be the part that
> determines its global computational identity.

The current characteristic programme is therefore not separate from the
local-to-global tradition.  It is an attempt to make that tradition
operational for finite observers and executable program structures.

## 2. Geometry as space; algebra and algorithms as time

Atiyah's geometry--algebra distinction is unusually close to the current
terminology.

Geometry presents many relations simultaneously.  Its primary intuition is
spatial: adjacency, shape, intersection, curvature, global topology, and the
ability to inspect a configuration as a whole.

Algebra performs operations in sequence.  Atiyah explicitly included
algorithms and computer calculation in this temporal reading.  An operation
is followed by another operation; the result depends on order; the machine
receives and emits a stream.

Thus the time--space pair

\[
(t,X)
\]

is not, by itself, a new discovery.  Atiyah had already stated the conceptual
pair in nearly these terms.

This historical alignment strengthens the programme, but it also imposes a
research discipline:

- do not claim novelty for identifying algebra or algorithms with temporal
  succession;
- do not claim novelty for identifying geometry with simultaneous spatial
  organisation;
- do not claim novelty merely for moving between local formulae and global
  singularity data.

The possible new content must lie elsewhere.

## 3. Why construction is not merely a synonym for algebra

The constructive domain `K` is narrower than all of algebra and richer than a
flat sequence of algebraic operations.

A temporal execution may retain only an ordered trace

\[
e_1;e_2;\cdots;e_n.
\]

A constructive object retains how that trace was made persistent:

- the expression or program DAG;
- ordered holes and typed frontiers;
- source and occurrence identity;
- explicit copy and discard;
- sharing rather than repeated value equality;
- scopes and substitutions;
- factorization and presentation choices;
- rewrite and normalization witnesses;
- proof obligations and certificates; and
- the residual not carried by an extensional quotient.

One possible interpretation is that `K` is an **objectification of temporal
history**.  Another is that `K` is the grammar through which spatial
organisation becomes executable.  These interpretations need not be
identical, and the theory should not decide between them prematurely.

The working cyclic picture is:

\[
\boxed{
\text{temporal succession}
\longrightarrow
\text{spatial organisation}
\longrightarrow
\text{constructive objectification}
\longrightarrow
\text{temporal execution}.
}
\]

`K` is therefore not introduced as a third physical coordinate.  It is a
third computational mode, with its own locality and identity discipline.

## 4. The singularity as a conversion event

In the classical local-to-global picture, a singularity is not merely a bad
point where a formula fails.  It is frequently the finite local carrier of a
global transformation:

- a cycle vanishes;
- sheets collide;
- a continuation acquires monodromy;
- a basis jumps;
- a factorization mutates;
- a kernel or cokernel changes; or
- a global invariant is concentrated in a local contribution.

The triadic proposal sharpens this into a conversion question:

> When one fibre boundary is crossed, which temporal mode, spatial cycle, and
> constructive subprogram change together?

The word “together” is the substantive requirement.  Three unrelated
annotations do not form a theory.  The three changes must be related by exact
maps, and their failure to commute must be exposed as a typed obstruction.

---

# Part II. A candidate triadic singularity object

## 5. Stratified parameter base

Let

\[
\pi:\mathcal Y\longrightarrow B
\]

be a process or geometric family over a parameter base `B`, with discriminant
or singular locus

\[
\Delta\subset B.
\]

For a regular point

\[
b\in B^\circ:=B\setminus\Delta,
\]

associate a three-domain fibre

\[
\mathfrak F_b
=
(\mathcal T_b,\mathcal X_b,\mathcal K_b).
\]

Here:

- `T_b` stores states, periods, execution histories, or solution modes;
- `X_b` stores fibres, opens, cycles, covers, cuts, and topology;
- `K_b` stores expressions, diagrams, sources, occurrences, scopes, and
  certificates.

A regular path

\[
\gamma:b_0\rightsquigarrow b_1
\]

induces transports

\[
P_\gamma^t,
\qquad
P_\gamma^X,
\qquad
P_\gamma^K.
\]

A path meeting or encircling a boundary stratum `c` induces crossing data

\[
J_c^t,
\qquad
J_c^X,
\qquad
J_c^K.
\]

Regular transport, wall crossing, and singular specialization must remain
distinct operations.

## 6. Pairwise crossing squares

Suppose there are interpretation maps before and after a crossing:

\[
F_{tX}^{-}:\mathcal T_{-}\to\mathcal X_{-},
\qquad
F_{tX}^{+}:\mathcal T_{+}\to\mathcal X_{+}.
\]

The time--space crossing square asks for a certificate

\[
\eta_{tX}:
F_{tX}^{+}\circ J_c^t
\Longrightarrow
J_c^X\circ F_{tX}^{-}.
\]

Likewise:

\[
\eta_{XK}:
F_{XK}^{+}\circ J_c^X
\Longrightarrow
J_c^K\circ F_{XK}^{-},
\]

and

\[
\eta_{Kt}:
F_{Kt}^{+}\circ J_c^K
\Longrightarrow
J_c^t\circ F_{Kt}^{-}.
\]

These comparison cells are not extensional value equalities.  They must state
which identities, observations, and residuals they preserve.

## 7. The crossing coherence cube

The three pairwise squares assemble into a cube.  Its total boundary can
carry a residual transformation

\[
\Theta_c
=
\eta_{Kt}\star\eta_{XK}\star\eta_{tX}.
\]

This notation is schematic until a 2-category or another exact carrier is
chosen.

There are three possible outcomes.

### Strict coherence

\[
\Theta_c=1.
\]

All three implementations describe the same crossing without residual.

### Central or projective coherence

\[
\Theta_c=\tau_c,
\]

where `tau_c` is a central sign, shift, deck action, grading increment, or
other explicitly typed automorphism.

### Open coherence

The finite observer cannot certify closure.  The result is

```text
Unknown(partial_cube, residual, missing_refinement)
```

rather than a false equality or a proof of nonexistence.

## 8. Common vanishing carrier

A stronger proposal introduces one boundary carrier

\[
V_c
\]

with three realisations:

\[
V_c^t,
\qquad
V_c^X,
\qquad
V_c^K.
\]

Possible meanings are:

| domain | possible vanishing realisation |
|---|---|
| time | disappearing mode, merged history, stalled or undecided process class |
| space | vanishing cycle, collapsing sheet, disappearing hole or open component |
| construction | eliminated factor, invalidated normal form, copied or merged subgraph, unresolved proof obligation |

The strong local law would say that each crossing defect factors through its
vanishing realisation:

\[
J_c^D-1
=
\operatorname{var}_D\circ\operatorname{can}_D,
\qquad
D\in\{t,X,K\}.
\]

This is inspired by nearby- and vanishing-cycle formalisms.  It is not yet a
general theorem for programs.

---

# Part III. The Legendre family as a finite 3-cusp model

## 9. The family and its discriminant

Consider

\[
E_\lambda:
\qquad
y^2=x(x-1)(x-\lambda).
\]

The affine cubic is

\[
f_\lambda(x)=x(x-1)(x-\lambda).
\]

Its polynomial discriminant is

\[
\operatorname{disc}_x(f_\lambda)
=
\lambda^2(\lambda-1)^2.
\]

For the standard Weierstrass model, the elliptic discriminant differs by the
usual constant factor:

\[
\Delta(\lambda)
=
16\lambda^2(1-\lambda)^2.
\]

The `j`-invariant is

\[
j(\lambda)
=
256
\frac{(1-\lambda+\lambda^2)^3}
{\lambda^2(1-\lambda)^2}.
\]

It has poles at

\[
0,
\qquad
1,
\qquad
\infty.
\]

The transformations

\[
\lambda\mapsto1-\lambda,
\qquad
\lambda\mapsto\lambda^{-1},
\]

belong to the anharmonic action that permutes branch-point charts while
preserving `j`.

These three cusps are therefore global moduli boundaries, not three arbitrary
labels added to the same equation.

## 10. Constructive branch presentation

The double cover of `P^1` is branched at

\[
\{0,1,\lambda,\infty\}.
\]

A homogeneous binary-quartic presentation of the branch divisor is

\[
F_\lambda(X,Z)
=
X(X-Z)(X-\lambda Z)Z.
\]

The three cusp limits are exact factor collisions.

### Cusp at zero

\[
F_0(X,Z)
=
X^2(X-Z)Z.
\]

The moving factor `X-lambda Z` collides with `X`.

### Cusp at one

\[
F_1(X,Z)
=
X(X-Z)^2Z.
\]

The moving factor collides with `X-Z`.

### Cusp at infinity

Set

\[
\mu=\lambda^{-1}
\]

and rescale the quartic by `mu`:

\[
\mu F_{1/\mu}(X,Z)
=
X(X-Z)(\mu X-Z)Z.
\]

Then

\[
\lim_{\mu\to0}
\mu F_{1/\mu}(X,Z)
=
-X(X-Z)Z^2.
\]

The moving branch factor collides with the point at infinity, represented by
`Z=0`.

The constructive cusp words can therefore be recorded as

\[
X,
\qquad
X-Z,
\qquad
Z.
\]

These are factors in a chosen branch presentation.  They are not yet cycles
in homology, and they are not yet period monodromy matrices.

## 11. Temporal analytic presentation: the Picard--Fuchs equation

A standard period is proportional to the hypergeometric function

\[
{}_2F_1\!\left(\frac12,\frac12;1;\lambda\right).
\]

It satisfies

\[
\boxed{
\lambda(1-\lambda)y''
+
(1-2\lambda)y'
-
\frac14y
=0.
}
\]

This differential equation has regular singular locations at

\[
0,
\qquad
1,
\qquad
\infty.
\]

Thus the same three cusp positions appear in:

- the discriminant of the algebraic fibre;
- the collision of branch factors;
- the singularities of the period equation; and
- the monodromy of the solution space.

This is exactly the sort of local-to-global relation Atiyah emphasized: the
singular set is finite, while continuation around it organises the global
solution system.

## 12. The spatial vanishing lattice

Choose a rank-two symplectic lattice

\[
H=\mathbf Z a\oplus\mathbf Z b
\]

with intersection form

\[
\langle a,b\rangle=1.
\]

Let

\[
\delta_0=a,
\qquad
\delta_1=b,
\qquad
\delta_\infty=-a-b.
\]

Then

\[
\delta_0+\delta_1+\delta_\infty=0,
\]

and the cyclic pairings are

\[
\langle\delta_0,\delta_1\rangle
=
\langle\delta_1,\delta_\infty\rangle
=
\langle\delta_\infty,\delta_0\rangle
=1.
\]

This is the oriented `A_2`-type pattern that repeatedly appeared in the
three-cusp discussion.  It is now attached to a concrete elliptic family.

The sign of a vanishing cycle does not change its Dehn transvection.  The
linear relation among the three oriented representatives still matters for
cyclic bookkeeping.

## 13. Primitive crossing and cusp monodromy

Use column vectors and the symplectic matrix

\[
J=
\begin{pmatrix}
0&1\\
-1&0
\end{pmatrix}.
\]

For a primitive vanishing vector `delta`, define the chosen Dehn
transvection

\[
L_\delta
=
I-\delta(J\delta)^T.
\]

It preserves `J` and fixes `delta`:

\[
L_\delta^TJL_\delta=J,
\qquad
L_\delta\delta=\delta.
\]

A labelled branch point making one full circuit around its collision partner
produces the squared action

\[
U_\delta
=
L_\delta^2
=
I-2\delta(J\delta)^T.
\]

For the three chosen directions:

\[
U_0
=
\begin{pmatrix}
1&2\\
0&1
\end{pmatrix},
\]

\[
U_1
=
\begin{pmatrix}
1&0\\
-2&1
\end{pmatrix},
\]

and

\[
U_\infty
=
\begin{pmatrix}
-1&2\\
-2&3
\end{pmatrix}.
\]

Each has determinant one and trace two.

The assignment

\[
\text{branch half-twist}
\longmapsto
L_\delta
\longmapsto
U_\delta=L_\delta^2
\]

is the finite three-stage crossing chain:

- construction records a braid or factor-collision operation;
- space records the Dehn surgery on the vanishing cycle; and
- time records the induced period or history monodromy.

## 14. Braid relation and label transport

For the two primitive directions `a` and `b`, the transvections satisfy

\[
L_aL_bL_a
=
L_bL_aL_b.
\]

This is the `B_3` braid relation.

Crossings do not commute without changing their labels.  For any symplectic
transport `g`,

\[
L_{g\delta}
=
gL_\delta g^{-1}.
\]

Equivalently,

\[
L_\delta g
=
gL_{g^{-1}\delta}.
\]

This is a precise classical model of the deformed crossing law found in the
affine and polynomial calibrations:

> moving one crossing through another transport changes the characteristic
> label carried by the crossing.

The program rewrite problem should therefore not be modelled by a universal
swap.  The generic operation is transport of the label together with a
certificate for the new crossing.

## 15. Projective closure and the central lift

The three positive-unipotent cusp representatives satisfy

\[
\boxed{
U_0U_1U_\infty=-I.
}
\]

Projectively, `I` and `-I` define the same element of `PSL(2,Z)`.  Hence the
three cusp transformations close in the projective local system:

\[
[U_0][U_1][U_\infty]=[I].
\]

A compatible `SL(2,Z)` monodromy convention can absorb the sign into the
infinity matrix:

\[
M_0=U_0,
\qquad
M_1=U_1,
\qquad
M_\infty=-U_\infty,
\]

so that

\[
M_0M_1M_\infty=I.
\]

The same central sign occurs in the primitive braid representation:

\[
(L_aL_b)^3=-I,
\]

while

\[
(L_aL_b)^6=I.
\]

This finite calculation is important, but it must be interpreted carefully.

### What it shows

It gives an exact classical example in which:

- projective closure forgets a sign;
- a selected linear lift retains the sign;
- a central braid element acts nontrivially on the lifted carrier; and
- the residual disappears after one more central circuit.

### What it does not show

It does not by itself establish:

- a canonical Adva history residual;
- a nontrivial triadic 3-cocycle;
- an `Omega` singularity;
- a failure of the actual fundamental-group monodromy relation; or
- observer-independent nonclosure.

The sign depends on the lift and convention.  It becomes structural only when
the lift data are part of the declared observer or state.

Nevertheless, it is the first exact finite calibration of the slogan:

\[
\boxed{
\text{projective or typed closure}
\quad\text{with}
\quad
\text{nontrivial lifted residue}.
}
\]

---

# Part IV. Three domains of one cusp

## 16. A finite typed cusp table

For the Legendre family, one bounded table is:

| cusp | constructive collision | spatial vanishing cycle | primitive spatial crossing | temporal cusp monodromy |
|---|---|---|---|---|
| `0` | `X` collides with `X-lambda Z` | `delta_0=a` | `L_a` | `U_0=L_a^2` |
| `1` | `X-Z` collides with `X-lambda Z` | `delta_1=b` | `L_b` | `U_1=L_b^2` |
| `infinity` | `Z` collides with `mu X-Z` | `delta_infinity=-a-b` | `L_delta` | projective class of `U_infinity` |

The columns are not values of one untyped field.  Their connection is a chain
of interpretations.

A candidate finite cusp characteristic is

\[
\mathsf C_c
=
(
\beta_c,
\delta_c,
L_c,
U_c;
\Omega_c,
R_c
),
\]

where:

- `beta_c` is a branch factor or braid generator;
- `delta_c` is the spatial vanishing class;
- `L_c` is its primitive Dehn action;
- `U_c` is the period or history monodromy;
- `Omega_c` certifies the comparison maps; and
- `R_c` retains chart, lift, orientation, construction, and observer choices.

## 17. The constructive residual already appears in the finite fixture

The executable fixture contains both:

\[
x(x-1)(x-\lambda)ig|_{\lambda=0}
\]

and the independently factorized cusp program

\[
x^2(x-1).
\]

They have equal scalar denotation, but distinct checked histories and IR.
Likewise at `lambda=1`:

\[
x(x-1)(x-\lambda)ig|_{\lambda=1}
=
x(x-1)^2
\]

extensionally, while the construction paths remain distinct.

This is the smallest current evidence that the constructive channel is not
recoverable from the classical fibre alone.

The generic affine program uses:

- three explicit occurrences of `x`; and
- one explicit occurrence of the parameter.

The specialized factorized cusp programs use three occurrences of `x`, but
their copy, call, and operation histories differ from generic evaluation at a
constant parameter.

The distinction is not yet a new mathematical invariant.  It is a concrete
piece of data that traditional equality of polynomials discards and Adva can
retain.

## 18. The time--space--construction interpretation

The three domains can now be stated without metaphor.

### Temporal domain

The period solution space of the Picard--Fuchs equation is transported around
a cusp:

\[
\Pi
\longmapsto
M_c\Pi.
\]

This is a sequential continuation or history action.

### Spatial domain

A cycle in the elliptic fibre collapses and its neighbourhood undergoes a
Dehn twist:

\[
x
\longmapsto
L_{\delta_c}x.
\]

This is topological surgery on the fibre.

### Constructive domain

A branch presentation crosses a factor collision or braid:

\[
(X-aZ)(X-bZ)
\rightsquigarrow
(X-aZ)^2
\]

at the boundary, with a declared branch word and specialization history.

This is a transformation of the finite presentation from which the fibre is
constructed.

The Legendre family therefore supports a precise statement:

> one cusp has a branch construction, a vanishing topology, and a period
> action linked by classical comparison maps.

The possible new research begins only when the constructive history and
finite-observer residual are included in those comparison maps.

---

# Part V. Relation to an Omega-type boundary

## 19. Three different meanings of “singularity”

The programme must distinguish at least three notions.

### Geometric singularity

A fibre degenerates, a discriminant vanishes, or a cycle collapses.

### Computational singularity

A reduction, normalization, continuation, or learning process has no total
completion procedure under the declared observer.

### Chaitin `Omega`

For a specified universal prefix-free machine `U`,

\[
\Omega_U
=
\sum_{U(p)\downarrow}2^{-|p|}
\]

is its halting probability.

These are related only after a construction is supplied.  A geometric cusp is
not automatically a Chaitin `Omega`, and an undecided computation is not
automatically represented by a vanishing cycle.

## 20. Finite precursor: central lift residual

The Legendre calculation gives a finite residual:

\[
U_0U_1U_\infty=-I.
\]

This is fully computable and finite-order.  It is therefore not an
`Omega`-type noncomputable completion boundary.

Its role is more modest.  It demonstrates a mechanism by which:

1. local cusp data close projectively;
2. a richer lift retains extra information;
3. the residual is central and compositional; and
4. forgetting the lift makes the path appear closed.

This is a suitable finite calibration before any universal-computation claim.

## 21. Observer tower and structural noncompletion

Let finite observers form a refinement tower

\[
Q_0\preceq Q_1\preceq Q_2\preceq\cdots.
\]

At stage `n`, the observer computes finite crossing data

\[
\mathcal C_{c,Q_n}
=
(
J_{c,Q_n}^t,
J_{c,Q_n}^X,
J_{c,Q_n}^K,
\Theta_{c,Q_n},
R_{c,Q_n}
).
\]

A structural `Omega`-type boundary would mean:

- every finite stage is computable and auditable;
- refinement yields better crossing data;
- no total algorithm can certify that all future residual is zero; and
- there is no computable global trivialization of the complete observer
  tower.

This condition is weaker and more general than identifying a real number
`Omega_U`.

## 22. Machine-relative numerical Omega

Only after the constructive domain explicitly contains a universal
prefix-free interpreter can the numerical quantity

\[
\Omega_U
\]

enter.

A rigorous triadic theorem would then require maps that preserve or account
for the prefix weights across all three domains.  One would need to show that
the same unresolved halting mass appears as:

- temporal noncompletion or unbounded stopping uncertainty;
- spatial failure of a computable global closure or selection; and
- constructive unresolved program branches.

No such theorem is established here.

The correct research sequence is:

\[
\boxed{
\text{finite central residual}
\to
\text{observer-relative coherence residual}
\to
\text{structural noncompletion}
\to
\text{machine-relative }\Omega_U.
}
\]

Skipping these intermediate steps would turn a mathematical programme into a
metaphor.

---

# Part VI. Candidate theoretical contribution

## 23. Triadic singular-crossing object

A future bounded object may have the form

\[
\mathbb S_{Q,c}
=
(
B,\Delta,c;
\mathcal T,\mathcal X,\mathcal K;
V_c^t,V_c^X,V_c^K;
J_c^t,J_c^X,J_c^K;
\eta_{tX},\eta_{XK},\eta_{Kt};
\Theta_{c,Q},R_{c,Q}
).
\]

The fields must remain typed.

- `B, Delta, c` describe the stratified parameter boundary;
- `T, X, K` are the three computational fibres;
- `V_c^D` are the three vanishing realisations;
- `J_c^D` are the three crossing actions;
- `eta` values are pairwise comparison certificates;
- `Theta` is the total triadic coherence defect; and
- `R` is the accountable observer residual.

## 24. Triadic singular-crossing conjecture

A disciplined conjecture is:

> For a suitably typed finite process family with temporal, spatial, and
> constructive realisations, every simple boundary stratum admits a finite
> observer-relative crossing characteristic whose three realisations are
> compatible up to an explicit total coherence defect.  Observer refinement
> transports the characteristic and defect functorially or returns a checked
> residual.

In symbols, for

\[
Q\preceq Q',
\]

one seeks

\[
\pi_{Q'Q}
(\mathsf C_{c,Q'})
\simeq
\mathsf C_{c,Q},
\]

and

\[
\pi_{Q'Q}
(\Theta_{c,Q'})
\simeq
\Theta_{c,Q},
\]

or an explicit obstruction.

## 25. Genuine-triadicity criterion

The theory is not genuinely triadic merely because it stores three fields.
At least one of the following should be established.

### Non-pairwise obstruction

There exists a crossing for which all three pairwise squares are separately
realisable, but their total cube has

\[
\Theta_c\ne1,
\]

and `Theta_c` cannot be reconstructed from any pair alone.

### Construction-sensitive future transport

There exist raw programs `P` and `P'` with the same traditional morphism,
period action, and fibre topology, but different construction provenance,
such that a later crossing acts differently unless the residual is retained.

### Triadic noncompletion theorem

For a declared universal finite-observer family, no total computable learner
can globally trivialize the three crossing systems, and the obstruction is
transported consistently among temporal, spatial, and constructive
realisations.

Without one of these results, the theory risks being a useful data schema but
not a new mathematical structure.

---

# Part VII. Algorithmic consequences

## 26. Local crossing updates

Picard--Lefschetz-type actions are low-rank updates:

\[
U_\delta
=
I-2\delta(J\delta)^T.
\]

Applying the crossing to a period or homology vector avoids recomputing the
entire fibre.  The update cost is controlled by the representation of
`delta` and the pairing.

This suggests an Adva algorithmic pattern:

```text
cross(boundary_characteristic, current_feature):
    read typed vanishing carrier
    compute local pairing
    apply low-rank temporal/spatial update
    rewrite only the affected constructive subgraph
    emit comparison certificate and residual
```

## 27. Label-aware normalization

The conjugation law

\[
L_\delta g
=
gL_{g^{-1}\delta}
\]

implies that a normalization engine should transport labels while reordering
crossings.

A rewrite entry should therefore contain at least:

```text
CrossingRule {
    left_operator,
    right_transport,
    transported_label,
    target_diagram,
    certificate,
    residual,
}
```

A global alphabetical or left/right sort is generally insufficient.

## 28. Multi-domain error localization

The same cusp can be checked through:

- discriminant and factor collision;
- vanishing-cycle relation;
- symplectic preservation;
- braid relation;
- Picard--Fuchs singularities;
- monodromy product; and
- checked program history.

A mismatch can be localized to a typed channel rather than reported as one
undifferentiated failure.

For example:

- correct polynomial degeneration but wrong monodromy indicates a topology or
  orientation error;
- correct monodromy but wrong construction lineage indicates a program
  lowering error;
- correct pairwise maps but nonclosing cube indicates a coherence residual;
- incomplete candidate search returns `Unknown`, not inconsistency.

## 29. Compact global description from singular generators

A finite set of cusp operators can generate the global continuation group.
This is a direct algorithmic form of the local-to-global principle:

\[
\boxed{
\text{finite singular data}
+
\text{composition laws}
\longrightarrow
\text{global transport}.
}
\]

The representation remains compact only if the program stores the generators,
relations, and residuals rather than expanding every path action separately.

---

# Part VIII. Research sequence

## 30. Completed finite calibration

The current executable fixture checks:

1. the Legendre cubic discriminant;
2. the `j`-invariant and its three cusp poles;
3. exact branch-factor collisions at `0`, `1`, and `infinity`;
4. the hypergeometric Picard--Fuchs equation;
5. the three oriented vanishing directions;
6. symplectic primitive twists;
7. the `B_3` braid relation;
8. cusp monodromy as squared primitive twists;
9. projective closure with a central `-I` lift;
10. exact closure after the infinity sign convention is included; and
11. distinct Adva construction histories for equal specialized cusp
    polynomials.

This is a finite calibration, not a full singularity engine.

## 31. Next phase A: exact crossing certificates

The next implementation should define research-local result records, without
promoting them to stable API:

```text
FiniteCrossingCharacteristic
CrossingComparisonCertificate
TriadicCrossingResidual
```

Each result should point to existing Rust-owned identities rather than create
new semantic identity in Python.

The minimum laws are:

- typed domain and codomain;
- exact vanishing carrier;
- symplectic or declared pairing preservation;
- construction-source preservation;
- comparison-square commutation;
- central-lift accounting; and
- `Unknown` for incomplete search.

## 32. Next phase B: two construction presentations

Construct the same regular Legendre fibre and cusp specialization in at least
two ways:

1. expanded arithmetic expression;
2. factorized expression;
3. shared DAG with cached intermediate factors; and
4. projective binary-quartic presentation.

Then cross the same cusp and compare:

- scalar or algebraic denotation;
- vanishing cycle;
- period monodromy;
- source and occurrence transport;
- rewrite path; and
- residual.

The decisive test is whether later composition can distinguish two
constructions that traditional geometry identifies.

## 33. Next phase C: crossing coherence cube

Implement three explicit interpretation maps for the bounded fixture:

\[
K\to X,
\qquad
X\to t,
\qquad
t\to K.
\]

Calculate all six paths around the cube and determine whether the total defect
is:

- identity;
- central `-I`;
- a construction-history shift; or
- an unresolved residual.

No general claim should precede this finite computation.

## 34. Next phase D: observer refinement

Introduce two finite observers:

- `Q_coarse`, which records only projective monodromy and fibre isomorphism;
- `Q_lifted`, which also records oriented homology basis, branch braid,
  construction history, and central sign.

The forgetting map should satisfy:

\[
Q_{\mathrm{lifted}}\longrightarrow Q_{\mathrm{coarse}}.
\]

The central sign should disappear under forgetting in a declared and
certified way.  This is the minimal observer-relative model needed before an
`Omega` discussion.

## 35. Next phase E: computational boundary

Only after the finite crossing calculus is stable should a universal
prefix-free construction be embedded.  The research question is then whether
unresolved completion mass is transported coherently among the three domains.

The Legendre central sign is a finite-order calibration of lifted residual,
not evidence for the answer.

---

# Part IX. Conservative conclusions

## 36. What Atiyah already provides

Atiyah's review already gives the following conceptual foundations:

1. the move from local formulae to global organisation;
2. the importance of singularities for global functions and differential
   equations;
3. geometry as spatial intuition;
4. algebra and algorithms as temporal succession; and
5. unification as a dominant later-twentieth-century theme.

These ideas should be cited as intellectual ancestry, not rediscovered under
new labels.

## 37. What the Legendre calibration establishes

Within a fixed convention, the finite model establishes:

1. three exact cusps in one elliptic family;
2. three branch-factor collisions;
3. three oriented vanishing directions with one linear relation;
4. braid generators lifting to Dehn transvections;
5. cusp monodromy as the squared primitive action;
6. projective three-cusp closure;
7. a central sign in one selected linear lift;
8. exact monodromy closure after the sign is typed into the infinity chart;
9. equal cusp polynomials with distinct checked construction histories; and
10. a concrete chain from construction crossing to spatial surgery to
    temporal monodromy.

## 38. What remains potentially new

The potential new contribution is not the classical Legendre mathematics.
It is the programme of adding:

- finite observer contracts;
- explicit temporal, spatial, and constructive computational fibres;
- source and occurrence preserving construction history;
- typed comparison certificates;
- a total triadic coherence defect;
- observer refinement of the defect; and
- a rigorous route from finite residuals to an `Omega`-type noncompletion
  theorem.

## 39. Claims not made

This note does not claim:

- that construction is a third physical dimension;
- that Atiyah proposed the present three-computer system;
- that every singularity has one common finite vanishing carrier;
- that pairwise comparison automatically forms a coherent cube;
- that `-I` is an observer-independent residual;
- that the Legendre cusps are `Omega` singularities;
- that every program boundary is governed by Picard--Lefschetz theory;
- that branch braid, Dehn twist, and period monodromy are identical objects;
- that equal extensional functions authorize program identity; or
- that a stable Adva singularity API is ready.

---

# Part X. Red-team opinion

## 40. The third domain may collapse into enriched algebra

A critic may argue that construction history is simply algebra with
provenance.  To refute this, the theory must produce a theorem or obstruction
that disappears when provenance is forgotten and cannot be recovered from
temporal and spatial data.

## 41. The central sign is convention-dependent

The equation

\[
U_0U_1U_\infty=-I
\]

uses selected trace-`+2` lifts.  Another compatible monodromy convention
places the sign in the infinity matrix and restores exact product identity.
The sign becomes meaningful only after lift data are declared.  It is not by
itself a canonical global anomaly.

## 42. Legendre is unusually symmetric

The three branch points, rank-two homology, `B_3` action, and modular
interpretation make the example exceptionally clean.  A general singular
program family may have:

- higher-rank vanishing lattices;
- nonisolated discriminant strata;
- noninvertible specialization;
- wild monodromy;
- no finite branch presentation; or
- no useful common characteristic.

The general theory may therefore require exit-path categories, schober-like
objects, relations, or higher cells rather than matrices.

## 43. Pairwise analogies may still dominate

It is easy to construct three pairwise correspondences and call them a cube.
The programme has new content only when the cube has a calculable coherence
law and a genuinely triadic obstruction.

## 44. Omega remains remote

A finite central sign, a nontrivial monodromy, and an infinite observer tower
are all compatible with completely computable mathematics.  Chaitin `Omega`
requires a specific universal prefix-free machine and an exact weight
construction.  The analogy must not substitute for that embedding.

## 45. Constructive residual may be too representation-dependent

If every change of arithmetic circuit creates a new residual, the theory may
record implementation noise rather than intrinsic structure.  Observer and
task contracts must specify which construction distinctions matter and which
are intentionally quotiented.

---

# Part XI. Immediate working thesis

The most economical current thesis is:

\[
\boxed{
\text{global computational structure is generated by local singular
crossings, but the complete crossing is visible only through coordinated
 temporal, spatial, and constructive realisations.}
}
\]

Atiyah supplies the local-to-global and time--space intellectual background.
The Legendre family supplies the first exact three-cusp calibration.  Adva's
possible contribution is to retain the construction and observer layers that
classical equivalence normally forgets.

The next decisive object is not another suggestive diagram.  It is an
explicit, finite crossing coherence cube whose six faces are computed and
whose total defect is either certified, centralized, or returned as
`Unknown` with an accountable residual.

---

## References and provenance

- Michael Atiyah, *Mathematics in the 20th Century*, Bulletin of the London
  Mathematical Society 34 (2002), 1--15,
  DOI `10.1112/S0024609301008566`.  The article is based on his Fields Lecture
  at the World Mathematical Year 2000 Symposium.
- Classical Picard--Lefschetz theory, the braid-group action on branch points,
  and the mapping-class action on the homology of an elliptic fibre provide
  the mathematical background for the finite matrices used here.
- The formulas, matrix conventions, branch degenerations, Picard--Fuchs
  equation, and Adva construction histories used by this note are checked in
  `tests/python/test_legendre_triadic_crossing.py`.
