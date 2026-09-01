# A Finite Legendre Crossing-Coherence Prism

Status: exploratory research calibration extending
[`0042-atiyah-legendre-triadic-crossing.md`](0042-atiyah-legendre-triadic-crossing.md).

The executable calibration is
[`tests/python/test_legendre_crossing_coherence_prism.py`](../../tests/python/test_legendre_crossing_coherence_prism.py).

This note implements the next finite step of the triadic singular-crossing
programme.  It does not yet construct a new general cohomology theory, a
perverse schober for programs, or an `Omega` boundary.  Its purpose is more
basic and more decisive:

> make the three pairwise crossing comparisons executable, introduce an
> explicit observer-forgetting axis, and calculate which residuals survive
> when the classical Legendre monodromy closes.

The result is mixed.

1. The construction-to-space square commutes after construction history is
   forgotten.
2. The space-to-time square commutes strictly by symplectic duality.
3. The time-to-construction square commutes on its finite charge but cannot
   reconstruct the crossing history; it emits an exact constructive residual.
4. A three-cusp circuit using compatible actual monodromy matrices closes on
   the finite charge, but the construction history still grows.
5. A simultaneous choice of positive-unipotent lifts contributes the separate
   central residual `-I`.
6. A coarse projective observer forgets both residual channels and therefore
   sees closure.

Thus the first finite computation does **not** yet exhibit an irreducible
triadic 3-cocycle.  It does identify two independent lift-sensitive channels
that a future theory must keep distinct:

\[
\boxed{
\text{central linear lift residual}
\quad\oplus\quad
\text{construction-history residual}.
}
\]

This is already stronger than a verbal three-domain analogy.  It gives exact
maps, six path comparisons, observer-forgetting laws, and a falsifiable
boundary for the next stage.

This work remains research-local.  It adds no stable crossing, observer,
projective state, monodromy, charge, logical feature, residual, or coherence
API; does not modify `claims.toml`; and does not change the active
`ProgramSlice` priority or Rust semantic authority.

---

## 0. A correction of the geometry of the comparison diagram

The previous note used the phrase **crossing coherence cube** schematically.
That phrase needs refinement.

For one crossing `c`, the three pairwise comparison diagrams are

\[
K\longrightarrow X,
\qquad
X\longrightarrow t,
\qquad
t\longrightarrow K.
\]

Each comparison has two paths:

\[
F_{DE}\circ J_c^D
\qquad\text{and}\qquad
J_c^E\circ F_{DE}.
\]

The three squares form a cyclic three-square shell, more literally a
triangular prism of domains and crossing stages.  They are not automatically
the six faces of one ordinary cube.

A genuine cube appears after a third binary axis is introduced.  The present
calibration uses observer refinement:

\[
Q_{\mathrm{lifted}}
\longrightarrow
Q_{\mathrm{coarse}}.
\]

For each adjacent pair of domains, the three axes are then:

1. domain interpretation;
2. crossing before/after; and
3. lifted/coarse observation.

This produces three exact observer-coherence cubes, one for each pair
`K--X`, `X--t`, and `t--K`.  The three cubes are arranged cyclically.

The terminology used below is therefore:

- **crossing square** for one pair of domains;
- **crossing-coherence prism** for the cyclic assembly of three squares; and
- **observer-coherence cube** for one crossing square together with the
  forgetting axis.

A future higher-categorical theory may package these into another object, but
that structure should be earned by an exact construction rather than assumed
from the drawing.

---

# Part I. Finite carriers

## 1. The Legendre cusp data

Retain the three oriented vanishing directions from `0042`:

\[
\delta_0=(1,0),
\qquad
\delta_1=(0,1),
\qquad
\delta_\infty=(-1,-1).
\]

Let

\[
J=
\begin{pmatrix}
0&1\\
-1&0
\end{pmatrix}
\]

be the symplectic form.  The primitive positive transvection is

\[
L_\delta
=
I-\delta(J\delta)^T,
\]

and the positive unipotent cusp lift is

\[
U_\delta=L_\delta^2.
\]

The three selected positive lifts are

\[
U_0=
\begin{pmatrix}
1&2\\
0&1
\end{pmatrix},
\]

\[
U_1=
\begin{pmatrix}
1&0\\
-2&1
\end{pmatrix},
\]

and

\[
U_\infty=
\begin{pmatrix}
-1&2\\
-2&3
\end{pmatrix}.
\]

They obey

\[
U_0U_1U_\infty=-I.
\]

A compatible actual monodromy convention is

\[
M_0=U_0,
\qquad
M_1=U_1,
\qquad
M_\infty=-U_\infty,
\]

for which

\[
M_0M_1M_\infty=I.
\]

The positive lifts and the actual monodromies are projectively equal at every
cusp.  They differ only in the infinity-chart central sign.

## 2. Constructive state

A bounded constructive state is

\[
k=(q,p,h),
\]

where:

- `q in Z^2` is a finite construction-side charge;
- `p` names one concrete presentation; and
- `h` is an exact finite construction history.

The charge is not claimed to be a universal encoding of an Adva program.  It
is the finite carrier on which the Legendre crossing matrices act.  The
presentation and history retain information that the charge does not carry.

In the executable fixture:

```text
ConstructionState(
    charge=(m,n),
    presentation=...,
    history=(...),
)
```

The crossing action is

\[
J_c^K(q,p,h)
=
(M_cq,p,h\cdot[c]),
\]

where `[c]` is the exact crossing token appended to the construction history.
The same finite charge can therefore have multiple lifted constructions.

## 3. Spatial state

A bounded spatial state is an oriented homology charge

\[
x=q\in\mathbf Z^2.
\]

The crossing action is

\[
J_c^X(q)=M_cq.
\]

This carrier retains orientation and integral scale.  It is finer than a
projective vanishing direction.

## 4. Temporal state

A bounded temporal state is a period covector

\[
\ell\in(\mathbf Z^2)^*.
\]

The crossing action is contragredient:

\[
J_c^t(\ell)=M_c^{-T}\ell.
\]

This is not an arbitrary third copy of the same matrix representation.  It is
the action required to preserve the natural pairing between covectors and
cycles:

\[
\langle M_c^{-T}\ell,M_cq\rangle
=
\langle\ell,q\rangle.
\]

---

# Part II. The three interpretation maps

## 5. Construction to space

The first interpretation forgets presentation and history:

\[
F_{KX}(q,p,h)=q.
\]

It is deliberately lossy.  Its residual is the exact pair

\[
R_{KX}(q,p,h)=(p,h).
\]

This is the smallest finite model of the claim that a spatial or extensional
carrier need not retain the program that produced it.

## 6. Space to time

Use the symplectic form to convert a cycle into a covector:

\[
F_{Xt}(q)=Jq.
\]

The inverse finite conversion is

\[
F_{tX}(\ell)=-J\ell,
\]

because

\[
-JJ=I.
\]

The essential intertwining identity is

\[
\boxed{
JM=M^{-T}J
}
\]

for every

\[
M\in\operatorname{SL}(2,\mathbf Z)
=\operatorname{Sp}(2,\mathbf Z).
\]

This identity is the exact certificate for the space-to-time crossing square.

## 7. Time to construction

The temporal covector reconstructs only a canonical constructive charge:

\[
F_{tK}(\ell)
=
(-J\ell,p_{\mathrm{can}},\varnothing).
\]

The reconstructed presentation is explicitly canonical and the reconstructed
history is empty.  No temporal matrix or period covector is claimed to recover
source occurrences, call frames, rewrite choices, or the exact path that
created the charge.

The cyclic interpretation therefore satisfies

\[
F_{tK}F_{Xt}F_{KX}(q,p,h)
=
(q,p_{\mathrm{can}},\varnothing).
\]

It closes on the finite charge and canonicalizes the construction.

The round-trip residual is

\[
R_{\triangle}(q,p,h)
=(p,h).
\]

---

# Part III. Six paths and three crossing squares

## 8. The construction--space square

The two paths are

\[
F_{KX}J_c^K(q,p,h)
=
M_cq,
\]

and

\[
J_c^XF_{KX}(q,p,h)
=
M_cq.
\]

Thus

\[
\boxed{
F_{KX}J_c^K
=
J_c^XF_{KX}
}
\]

on the spatial charge.

The equality does not say that construction history survives.  The left path
contains the appended token `[c]` before `F_(KX)` forgets it; the right path
never stores that token in the spatial carrier.

The commuting square is therefore strict on its declared output and lossy in
its residual channel.

## 9. The space--time square

The two paths are

\[
F_{Xt}J_c^X(q)
=
JM_cq,
\]

and

\[
J_c^tF_{Xt}(q)
=
M_c^{-T}Jq.
\]

Symplecticity gives

\[
JM_c=M_c^{-T}J,
\]

hence

\[
\boxed{
F_{Xt}J_c^X
=
J_c^tF_{Xt}.
}
\]

This square is strict in the finite calibration and carries no extra history
field.

## 10. The time--construction square

The two charge paths are

\[
F_{tK}J_c^t(\ell)
=
-JM_c^{-T}\ell,
\]

and

\[
J_c^KF_{tK}(\ell)
=
M_c(-J\ell).
\]

The symplectic identity also gives

\[
-JM_c^{-T}=M_c(-J),
\]

so the charges agree.

But the construction histories are

\[
\varnothing
\]

and

\[
[c]
\]

respectively.  Therefore the exact result is

\[
\boxed{
F_{tK}J_c^t
\simeq
J_c^KF_{tK}
\quad\text{with residual}\quad[c].
}
\]

This is the first executable failure of strict cyclic reconstruction.  The
failure does not occur in the finite charge or in the classical monodromy.  It
occurs in construction history.

## 11. The six path report

For each cusp, the executable fixture evaluates:

```text
K-cross -> K-to-X
K-to-X -> X-cross

X-cross -> X-to-t
X-to-t -> t-cross

t-cross -> t-to-K
t-to-K -> K-cross
```

The report is:

| square | extensional result | exact residual |
|---|---|---|
| `K -> X` | equal | presentation and history forgotten by interpretation |
| `X -> t` | equal | none in the finite charge/covector model |
| `t -> K` | equal charge | one crossing-history token |

This finite result does not establish a universal triadic obstruction.  It
locates the first obstruction in the selected model.

---

# Part IV. Observer refinement

## 12. The lifted observer

The lifted observer records:

- signed integral charge or covector;
- the actual `SL(2,Z)` matrix convention;
- construction presentation;
- exact finite history; and
- the distinction between positive lifts and actual monodromies.

Call it

\[
Q_{\mathrm{lifted}}.
\]

## 13. The coarse observer

The coarse observer records only:

- the projective line of a nonzero charge;
- the projective matrix class modulo `+-I`; and
- the extensional cusp carrier.

It forgets:

- vector sign;
- the infinity-chart lift sign;
- presentation;
- source and occurrence history; and
- crossing tokens.

Call it

\[
Q_{\mathrm{coarse}}.
\]

For a nonzero vector `v`, define

\[
[v]=[-v].
\]

For an invertible matrix `M`, define

\[
[M]=[-M].
\]

## 14. Forgetting maps

Each domain has a forgetting map

\[
\pi_K:K_{\mathrm{lifted}}\to K_{\mathrm{coarse}},
\]

\[
\pi_X:X_{\mathrm{lifted}}\to X_{\mathrm{coarse}},
\]

and

\[
\pi_t:t_{\mathrm{lifted}}\to t_{\mathrm{coarse}}.
\]

The executable fixture checks that forgetting commutes with:

- `K -> X` interpretation;
- `X -> t` interpretation;
- `t -> K` interpretation;
- every actual cusp crossing;
- every positive-lift cusp crossing; and
- the projective identification of the infinity sign.

Thus each pairwise crossing square, together with the lifted-to-coarse axis,
forms a finite observer-coherence cube.

## 15. Coarse closure of the time--construction square

The lifted time--construction square has history residual `[c]`.

After applying `pi_K`, both histories are erased.  Therefore the coarse square
commutes strictly:

\[
\pi_KF_{tK}J_c^t
=
\pi_KJ_c^KF_{tK}.
\]

This gives a precise finite meaning to the statement:

> forgetting can make a non-closed lifted computation appear closed.

The appearance of closure is not an error if the observer policy explicitly
declares the forgotten data.  It becomes an error only if the coarse equality
is silently lifted back to construction identity.

---

# Part V. The three-cusp circuit

## 16. Actual monodromy closure

For the compatible actual convention,

\[
M_0M_1M_\infty=I.
\]

Applying the declared column-vector path product therefore returns the finite
charge to itself.

The constructive circuit still appends three tokens.  With the right-to-left
function-application convention used by the fixture, the exact history suffix
is

```text
cross:infinity
cross:one
cross:zero
```

Thus the actual classical carrier closes while the construction history does
not:

\[
(q,p,h)
\longmapsto
(q,p,h\cdot[\infty,1,0]).
\]

This is a finite paracyclic pattern:

\[
\text{same carrier type and charge, new history layer}.
\]

No noncomputability is involved.

## 17. Positive-lift central residual

For the simultaneous positive-unipotent representatives,

\[
U_0U_1U_\infty=-I.
\]

The corresponding lifted construction state becomes

\[
(q,p,h)
\longmapsto
(-q,p,h\cdot[\infty,1,0]).
\]

The total finite defect can therefore be recorded as

\[
\boxed{
\mathcal D_Q
=
(-I,[\infty,1,0]).
}
\]

The two components have different meanings:

- `-I` is a central choice of linear lift;
- `[infinity, one, zero]` is an exact construction history.

The actual monodromy convention removes the first component but not the
second.  A projective observer removes both.

This proves that the two residual channels must not be identified.

## 18. Coarse projective closure

Since

\[
[q]=[-q]
\]

and the coarse observer erases the history suffix,

\[
\pi_K(q,p,h)
=
\pi_K(-q,p,h\cdot[\infty,1,0]).
\]

Hence both the actual and positive-lift circuits close for
`Q_coarse`.

This is the minimal finite observer-relative closure theorem of the current
programme.

---

# Part VI. Checked constructions

## 19. Two presentations of the zero cusp

The Adva fixture constructs the zero-cusp polynomial in two ways.

The first specializes the generic program:

\[
x(x-1)(x-\lambda)
\quad\text{at}\quad
\lambda=0.
\]

The second directly constructs

\[
x^2(x-1).
\]

Their SymPy values agree exactly, but their checked IR and histories differ.

## 20. Two presentations of the one cusp

Likewise, the generic specialization

\[
x(x-1)(x-\lambda)
\quad\text{at}\quad
\lambda=1
\]

and the direct factorized construction

\[
x(x-1)^2
\]

have equal values and distinct checked histories.

## 21. Later crossing preserves the distinction

Both presentations are assigned the same finite charge.  Therefore their
spatial and temporal images agree.

Applying the same cusp crossing appends the same crossing token to each exact
history.  Since their prefixes differ, the lifted construction states remain
distinct after the later crossing:

\[
h_{\mathrm{generic}}\cdot[c]
\ne
h_{\mathrm{factorized}}\cdot[c].
\]

This is stronger than merely preserving provenance at the cusp.  The
constructive distinction survives subsequent composition.

A complete domain round trip

\[
K\to X\to t\to K
\]

canonicalizes both states to the same empty-history construction.  The
round-trip residual is therefore exactly the information needed to audit that
identification.

The present fixture does not yet show different future **extensional** values
from the two histories.  It shows different future lifted constructions under
the same crossing.  A later calibration must test whether a
construction-sensitive continuation can turn that intensional difference into
a later observational difference.

---

# Part VII. What has and has not been found

## 22. What the finite calculation establishes

The calibration establishes:

1. three explicit typed carriers `K`, `X`, and `t`;
2. three explicit interpretation maps;
3. three explicit crossing actions;
4. six executable crossing paths;
5. strict `K--X` charge compatibility;
6. strict `X--t` compatibility by symplectic duality;
7. charge-level `t--K` compatibility with exact history residual;
8. lifted-to-coarse forgetting maps in all three domains;
9. observer-forgetting commutation with interpretations and crossings;
10. strict actual monodromy closure on the finite charge;
11. central `-I` residual for simultaneous positive lifts;
12. independent construction-history accumulation;
13. projective coarse closure after declared forgetting; and
14. persistence of distinct Adva construction histories under later crossing.

## 23. What it does not establish

The calibration does not establish:

- a universal common vanishing object for arbitrary programs;
- a literal ordinary cube containing all three domains at once;
- a nontrivial irreducible triadic 3-cocycle;
- a new topological invariant of the Legendre family;
- a stable observer or residual API;
- that construction history always affects future extensional behaviour;
- that the central sign is intrinsic rather than lift-dependent;
- that every coarse closure arises through projectivization;
- that the full three-computer cycle is elliptic;
- that any finite residual is a Chaitin `Omega` phenomenon; or
- that the logical language under parallel investigation is already the
  canonical characteristic language.

## 24. Why the absence of an irreducible triadic defect is informative

A new theory should not manufacture a three-way obstruction merely because it
would be interesting.

In this fixture, the current residuals can be located:

- the central sign belongs to the choice of linear lift;
- the history suffix belongs to the constructive channel;
- the symplectic space--time square is strict.

Thus the total defect is decomposable.  This is a useful negative result.  It
sets a promotion gate:

> Do not call a defect genuinely triadic until it cannot be assigned to one
> domain or reconstructed from one pairwise comparison.

A future example must defeat this decomposition.

---

# Part VIII. Interface with the parallel logical-characteristic line

## 25. Logic as a possible early characteristic language

A parallel research line is investigating an important interpretation:

> a logical language may be the first stable characteristic acquired during
> learning.

This is compatible with the present work, but the two lines should not yet be
collapsed.

The crossing calibration already emits propositions of the form:

```text
KX-square: Yes
Xt-square: Yes
Kt-charge-square: Yes
Kt-history-square: No(residual = cross:c)
positive-three-cusp-lift: central(-I)
actual-three-cusp-monodromy: identity
coarse-observer-closure: Yes
```

A logic layer could quote these as a finite theory with proofs,
countercertificates, and unknown obligations.  In that role, logic is not a
fourth domain.  It is a candidate characteristic language for recording which
relations among the three domains have stabilized for observer `Q`.

## 26. Required interface discipline

Any future integration should preserve at least:

1. the observer index `Q`;
2. the domain types of every proposition;
3. the distinction between value equality, projective equality, and
   construction identity;
4. `Yes`, checked `No`, and `Unknown`;
5. the exact residual named by a failed square;
6. the hypotheses under which a crossing matrix or chart is selected; and
7. proof terms or certificates rather than untracked assertions.

The current note therefore leaves an explicit future port:

\[
\operatorname{quote}_{\mathrm{logic}}:
\operatorname{CoherenceReport}_Q
\longrightarrow
\operatorname{Theory}_Q.
\]

No implementation or universality claim is made here.

## 27. A possible learning interpretation

The two lines may eventually meet as follows:

\[
\text{raw three-domain observations}
\longrightarrow
\text{finite crossing report}
\longrightarrow
\text{logical characteristic theory}
\longrightarrow
\text{new predictions and refinements}.
\]

The first learned logical characteristic need not describe the whole world.
It may state only:

- which domains currently commute;
- where a residual appears;
- which observer forgets it;
- which crossing laws are stable; and
- what evidence would force refinement.

This would turn logic into an operational boundary language for learning,
rather than an externally imposed final axiom system.

---

# Part IX. Algorithmic interpretation

## 28. Constant-size crossing updates

Each finite crossing acts by a `2 x 2` integer matrix and one history-token
append.  The crossing update is therefore constant size relative to the
underlying geometric family.

No period integral or full polynomial reconstruction is required for every
crossing once the finite characteristic is known.

## 29. Incremental observer refinement

The coarse observer can be computed from the lifted state by:

- primitive-vector normalization modulo sign;
- matrix normalization modulo the central sign; and
- erasure of finite history.

The forgetting maps are explicit and deterministic.  A system can therefore
maintain both observers incrementally rather than recomputing the coarse model
from raw history.

## 30. Localized failure diagnosis

The six-path report identifies where non-closure occurs.

In this calibration:

- a failed `K--X` charge comparison would indicate a construction-to-spatial
  interpretation error;
- a failed `X--t` comparison would violate symplectic duality;
- the observed `t--K` mismatch is confined to history reconstruction;
- a noncentral matrix discrepancy would indicate a chart or path-order error;
  and
- failure only after forgetting would indicate an invalid observer quotient.

Thus the prism is not merely a representation.  It is a diagnostic graph.

## 31. Compression and accountability

The coarse state is smaller because it identifies:

\[
v\sim-v
\]

and erases construction history.  The lifted state retains the information
needed for audit and future construction-sensitive tasks.

The algorithmic pattern is:

\[
\boxed{
\text{operational quotient}
+
\text{exact residual channel}.
}
\]

This is the same architecture that appeared in the earlier characteristic
calibrations, now applied to a singular crossing circuit.

---

# Part X. Conservative conclusion

## 32. The current finite theorem pattern

For the bounded Legendre fixture and declared matrices:

\[
F_{KX}J_c^K
=
J_c^XF_{KX},
\]

\[
F_{Xt}J_c^X
=
J_c^tF_{Xt},
\]

and

\[
F_{tK}J_c^t
\simeq
J_c^KF_{tK}
\quad\text{with residual}\quad[c].
\]

For the three-cusp circuit:

\[
M_0M_1M_\infty=I,
\]

while

\[
U_0U_1U_\infty=-I.
\]

The lifted construction history grows in both conventions.  The coarse
projective observer sees closure in both conventions.

## 33. The main conceptual result

The main result is not that the Legendre family has a new invariant.  It is
that the three-domain programme can now state exactly which information each
comparison preserves and which information it forgets.

The finite pattern is:

\[
\boxed{
\text{classical carrier closure}
\quad\not\Rightarrow\quad
\text{construction-history closure}.
}
\]

And:

\[
\boxed{
\text{coarse observer closure}
\quad\not\Rightarrow\quad
\text{lifted identity}.
}
\]

These are precise observer-relative statements, not metaphors.

## 34. Relation to `Omega`

The residuals in this note are finite and completely computable.

The central sign has order two.  The history suffix is an explicit finite
word.  Neither is a Chaitin `Omega` value or an `Omega`-type completion
obstruction.

Their relevance is methodological.  They demonstrate how a coarse observer
can see closure while a lifted state retains accountable data.  A future
`Omega` programme would require an infinite observer-refinement tower for
which no computable final zero-residual certificate exists.

This finite prism is a prerequisite, not evidence that such a theorem already
holds.

---

# Part XI. Red-team opinion

## 35. The charge model is deliberately small

The same integral charge is used on the constructive and spatial sides.  This
is a calibration convenience, not a theorem that arbitrary program
constructions carry canonical homology charges.

A future theory must derive the construction-to-charge map from an exact
program or branch presentation.

## 36. The temporal carrier is a covector model

The temporal state is represented by an integral covector.  Actual analytic
period values are complex and parameter-dependent.  The present model checks
the transformation law, not numerical period integration.

## 37. The history residual is currently domain-local

The failure of the `t--K` square is fully attributable to the constructive
history channel.  It is therefore not yet a genuinely irreducible triadic
obstruction.

This is a limitation, not a defect to hide.

## 38. Projective forgetting is task-dependent

Identifying `v` with `-v` is legitimate only for a task that observes a line
rather than an oriented cycle.  A chirality-sensitive task must use the lifted
observer.

## 39. Canonical reconstruction is a choice

The map `t -> K` returns a canonical empty-history construction.  Another
canonical section could be selected.  The residual depends on this section,
although the impossibility of reconstructing arbitrary source history from a
covector does not.

## 40. Equal geometry may still imply equal future values

The fixture shows that two classical-equal cusp presentations retain distinct
histories under a later crossing.  It does not yet show that a subsequent
extensional observation distinguishes them.

A stronger contribution requires a task whose future behaviour depends on the
construction history in a principled, typed way.

## 41. Logic may summarize rather than generate the structure

The parallel logical-characteristic line could provide a valuable finite
language.  But a logical summary of the crossing report does not by itself
construct the temporal, spatial, or constructive carriers.

The relation between learned logic and underlying three-domain structure must
be tested in both directions.

---

# Part XII. Next project

## 42. Construction-sensitive continuation

The next decisive experiment should start from two constructions that are
classically equal at a cusp:

\[
P_{\mathrm{generic}}|_c
\simeq
P_{\mathrm{factorized},c}.
\]

Then introduce a typed continuation operator

\[
\operatorname{Continue}_{Q,c\to b}
\]

that must use declared construction information rather than only the common
value.

The experiment should determine whether:

1. both histories necessarily produce the same future extensional process;
2. they remain different only as audit records;
3. one history supports a continuation that the other does not;
4. specialization and continuation fail to commute; or
5. the difference appears only after another cusp crossing.

This is the point at which construction history may become an operational
state variable rather than provenance alone.

## 43. Logical quotation port

In parallel, define a small read-only logical quotation of the coherence
report:

```text
square(K,X,c) = yes
square(X,t,c) = yes
square(t,K,c) = residual(cross:c)
closure(actual) = yes-on-charge
closure(positive-lift) = central(-I)
closure(coarse-observer) = yes
```

The quotation should preserve certificates and `Unknown`.  It should not yet
control the underlying crossing calculus.

## 44. Promotion gate for a genuinely triadic defect

A future result may be called genuinely triadic only if it supplies an
obstruction `Theta` satisfying all of the following:

1. each pairwise square is individually certified;
2. `Theta` survives all assignments to a single-domain residual;
3. `Theta` cannot be reconstructed from any two domains alone;
4. observer refinement transports `Theta` coherently; and
5. at least one finite executable fixture computes it.

Until then, the correct output is a decomposed residual report rather than a
3-cocycle claim.

---

## 45. Short review

The initial intuition was that one fibre-boundary event should have
coordinated temporal, spatial, and constructive effects.  The present result
supports that intuition at the level of exact finite maps.

The decisive findings are:

\[
\boxed{
\text{space--time crossing compatibility is symplectic duality},
}
\]

\[
\boxed{
\text{time cannot reconstruct exact construction history},
}
\]

and

\[
\boxed{
\text{coarse projective closure can hide both lift sign and history}.
}
\]

The next bottleneck is no longer writing a larger classical monodromy table.
It is demonstrating whether construction history can alter a later typed
continuation or whether it remains a separable audit channel.
