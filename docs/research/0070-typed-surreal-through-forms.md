# Typed Surreal-Inspired Through Forms on the Circular Three-Form

Status: bounded syntax proposal with a pure-Python finite calibration following
[`0021-surreal-cut-objectification-no-go.md`](0021-surreal-cut-objectification-no-go.md),
[`0047-a1-nodal-through-crossing-geometry.md`](0047-a1-nodal-through-crossing-geometry.md),
[`0048-cellular-annulus-nodal-torus-dehn-twist.md`](0048-cellular-annulus-nodal-torus-dehn-twist.md),
[`0067-circular-three-form-interface-duality.md`](0067-circular-three-form-interface-duality.md),
[`0068-finite-circular-overlap-transport.md`](0068-finite-circular-overlap-transport.md),
and the exact occurrence-level transition companion in
[`../NEXT_PHASE_TRIADIC_OBSERVER_TRANSITIONS.md`](../NEXT_PHASE_TRIADIC_OBSERVER_TRANSITIONS.md).

The executable research oracle is
[`test_typed_surreal_through_forms.py`][fixture].

[fixture]: ../../tests/python/test_typed_surreal_through_forms.py

This note examines one proposed syntax:

> Write \(\langle L\mid R\rangle\) for passage from a left presentation,
> through the boundary denoted by \(\mid\), to a right presentation.  Place
> one such through form on each of the three circular interfaces among
> `{}[]()`.

The proposal survives a bounded red-team pass after one essential type
correction:

> The unmarked angle form denotes a **relation over a typed singular middle
> object**, not a surreal number and not an automatically single-valued
> program transformation.

A marked resolution may select a function inside that relation.  The three
selected resolutions can then accumulate nontrivial holonomy around the
circle.  Singularity packages the unresolved matchings into a finite
resolution fibre; duality takes relational converse; neither operation
authorizes forgetting the resolution or holonomy residual.

This is a research-local syntax and finite set calculation.  It introduces no
stable bracket, singularity, through, relation, dual, or program operation.

---

## 0. Executive result

For a typed interface with smooth sides \(F_-\) and \(F_+\), singular middle
object \(N\), and pinch maps

\[
F_-\xrightarrow{q_-}N\xleftarrow{q_+}F_+,
\]

define the unmarked through form by

\[
\boxed{
\langle F_-\mid_N F_+\rangle
:=
F_-\times_NF_+.
}
\]

A concrete term is well formed exactly when

\[
\boxed{
\langle \ell\mid_N r\rangle
\quad\Longleftrightarrow\quad
q_-(\ell)=q_+(r).
}
\]

A chosen matching, smoothing, or phase \(\rho\) selects a graph

\[
\Gamma(P_\rho)
\subseteq
\langle F_-\mid_NF_+\rangle,
\]

printed as

\[
\langle F_-\mid_NF_+\rangle_\rho.
\]

For the circular chart order

\[
K\longrightarrow X\longrightarrow t\longrightarrow K,
\]

the interface types are the opposite domains:

\[
\boxed{
I_{KX}:t,
\qquad
I_{Xt}:K,
\qquad
I_{tK}:X.
}
\]

The finite fixture uses two regular points and five collapsed phase points on
each side.  Each unmarked local relation has

\[
2+5^2=27
\]

pairs.  Five marked phases select five distinct functional graphs.  Around
the full circle, the \(5^3=125\) triples of local resolutions give exactly
five holonomy rotations, each occurring \(25\) times, and

\[
\boxed{
\text{raw circular through relation}
=
\bigcup_{\rho_K,\rho_X,\rho_t}
\text{resolved circular holonomy}.
}
\]

Thus the unresolved relation is not a defective function.  It is the exact
finite carrier of all marked resolutions retained before a choice is made.

---

## 1. Conway form, surreal number, and through form

The historical Conway notation is

\[
\{L\mid R\}.
\]

At the game level it presents left and right options.  To be a surreal number,
the recursively numeric options must satisfy the number condition, including

\[
\ell<r
\qquad
(\ell\in L,\ r\in R).
\]

Objectification then selects the simplest surreal strictly between the two
frontiers.  As `0021` establishes, this quotient can identify distinct cut
presentations and is not natural for even a simple positive scaling.

The present angle notation is deliberately new:

| syntax | judgement | role |
|---|---|---|
| \(\{L\mid R\}\) | option or decorated cut presentation | intensional Conway/game form |
| \(\operatorname{Num}(L,R)\) | every left option is below every right option | number-admissibility certificate |
| \(\langle L\mid_NR\rangle\) | the two sides have equal specialization in \(N\) | relation-valued through form |
| \(\langle L\mid_NR\rangle_\rho\) | \(\rho\) selects a graph in the through relation | resolved passage |
| \(\operatorname{Obj}\{L\mid R\}\) | a declared objectification is defined | observer-relative numerical shadow |

The bar is therefore overloaded only at the glyph level.  Its type and outer
delimiter determine the judgement.

### 1.1 Order and passage are independent

The fixture realizes all four possibilities:

| Conway order condition | through compatibility | finite witness |
|---:|---:|---|
| yes | yes | ordered options and two collapsed phases |
| yes | no | ordered options and unequal regular specializations |
| no | yes | reversed options and two collapsed phases |
| no | no | reversed options and unequal regular specializations |

Consequently,

\[
\boxed{
\operatorname{Num}(L,R)
\quad\text{and}\quad
\operatorname{Through}_N(L,R)
\text{ are logically independent judgements.}
}
\]

This reframes the earlier reduction difficulty.  Failure to certify
\(L<R\) does not make the decorated form or a typed passage meaningless.  It
blocks numerical objectification, not all further computation.

---

## 2. Why the bar must name a middle object

Writing only

\[
\langle L\mid R\rangle
\]

hides which distinctions are identified at the boundary.  The minimally
auditable form is

\[
\boxed{
\langle L\mid_{N_D,Q,v}R\rangle,
}
\]

where:

- \(D\) is the typed interface role;
- \(Q\) is the finite observer policy;
- \(v\) is the policy or fibre version;
- \(N_D\) is the public singular middle object; and
- the residual retains the two pinch maps and the collapsed fibre.

The notation must not identify three currently distinct uses of `Omega`:

1. \(\Omega_{Q,D}\), the observer-relative universal-side reading of a
   circular bracket in `0067`;
2. an `Omega`-type noncompletion boundary from `0033`; and
3. a geometric nodal middle object \(N_D\) from `0047`.

A theorem may later connect them.  Typography alone may not.

---

## 3. Three interfaces and the opposite-domain type

The circular universal contexts are

\[
U_K=\{X,t\},
\qquad
U_X=\{t,K\},
\qquad
U_t=\{K,X\}.
\]

Their pairwise overlaps give

\[
U_K\cap U_X=\{t\},
\qquad
U_X\cap U_t=\{K\},
\qquad
U_t\cap U_K=\{X\}.
\]

This makes the following syntax well typed at the finite incidence level:

\[
\begin{aligned}
\tau_{KX}^{t}
&=
\langle L_K\mid_{I_{KX}^{t}}R_X\rangle,\\
\tau_{Xt}^{K}
&=
\langle L_X\mid_{I_{Xt}^{K}}R_t\rangle,\\
\tau_{tK}^{X}
&=
\langle L_t\mid_{I_{tK}^{X}}R_K\rangle.
\end{aligned}
\]

The fixture rejects an interface carrying either endpoint domain instead of
the unique opposite type.

This establishes only a combinatorial typing law.  The stronger identifications

\[
I_{KX}^{t}\simeq N_t,
\qquad
I_{Xt}^{K}\simeq N_K,
\qquad
I_{tK}^{X}\simeq N_X
\]

remain conjectural.  They require explicit comparison maps between an overlap
fibre and the corresponding geometric or computational singular carrier.

---

## 4. Singularity retains a resolution fibre

In the finite model, every interface has:

- `r` regular points, whose specializations remain distinct; and
- `n` phase points, all of which specialize to one typed node.

The through relation therefore has

\[
r+n^2
\]

pairs.  It is functional on the regular sector and \(n\)-valued on every
collapsed phase point.

For each \(k\in\mathbb Z/n\mathbb Z\), the phase rule

\[
i\longmapsto i+k
\]

selects one graph \(P_k\).  All such graphs obey the same public equation

\[
q_+P_k=q_-,
\]

but remain pairwise distinct before specialization.

The singular node therefore does not solve ambiguity by erasure.  It changes
the representation of ambiguity:

\[
\boxed{
\text{many explicit smooth matchings}
\longrightarrow
\text{one node plus its resolution fibre}.
}
\]

This is the precise sense in which a singularity may simplify a tangled
syntax without destroying its information.

---

## 5. Duality is converse, not inverse computation

For a through relation \(T\subseteq F_D\times F_E\), define

\[
T^\star=T^{\mathsf{op}}
=
\{(r,\ell):(\ell,r)\in T\}.
\]

Then

\[
\boxed{(T^\star)^\star=T.}
\]

In angle syntax,

\[
\boxed{
\langle L\mid_I R\rangle^\star
=
\langle R^\star\mid_{I^\star}L^\star\rangle.
}
\]

For the finite phase resolutions,

\[
(P_k)^\star=P_{-k}.
\]

This statement remains meaningful for a multivalued relation.  It does not
assert that copy, discard, arithmetic operations, or a complete
`ProgramSlice` have executable inverses.

Relation composition satisfies the contravariant law

\[
\boxed{
(T_3T_2T_1)^\star
=
T_1^\star T_2^\star T_3^\star.
}
\]

The fixture checks this law for both unresolved relations and chosen
resolutions.

---

## 6. Circular entanglement becomes local passage plus global residual

Let the three selected phase resolutions be

\[
P_{k_{KX}},
\qquad
P_{k_{Xt}},
\qquad
P_{k_{tK}}.
\]

Their composite at the base chart is

\[
H
=
P_{k_{tK}}P_{k_{Xt}}P_{k_{KX}}.
\]

In the finite cyclic phase model,

\[
\boxed{
H(i)=i+k_{KX}+k_{Xt}+k_{tK}\pmod n.
}
\]

Thus three locally legal through choices need not close globally.  If the
choices are not made, the composite remains relation-valued.  Exhaustively,

\[
\boxed{
T_{tK}T_{Xt}T_{KX}
=
\bigcup_{k_{KX},k_{Xt},k_{tK}}
P_{k_{tK}}P_{k_{Xt}}P_{k_{KX}}.
}
\]

This gives a bounded candidate normal form for the intertwined circular
syntax:

\[
\boxed{
\mathcal W_Q
=
\left(
\mathfrak F_Q;
\tau_{KX}^{t},\tau_{Xt}^{K},\tau_{tK}^{X};
\rho_{KX},\rho_{Xt},\rho_{tK};
\Theta_Q,R_Q
\right).
}
\]

Here:

- \(\mathfrak F_Q\) is the circular three-form boundary record;
- the three \(\tau\) values are local relation-valued passages;
- the three \(\rho\) values are optional resolution witnesses;
- \(\Theta_Q\) is cyclic holonomy or a more general coherence defect; and
- \(R_Q\) retains exact process, provenance, and unresolved fibres.

This is not yet a canonical decomposition theorem.  In a richer carrier,
reversible braid transport may occur between the local passages, and active
noninvertible program events cannot be replaced by braid words.

---

## 7. Relation to the exact triadic observer transition

`TriadicObserverTransitionV0` now supplies an exact checked carrier between
two causal cuts:

- the complete `ProgramSlice`;
- lower and upper occurrence-level incidences;
- three opposite-pair observations;
- source-relative ancestry links;
- source-free residual wires; and
- exact adjacent composition.

It is not itself a through cospan.  In particular, it has no singular middle
object, no specialization quotient, and no resolution choice.

The next grounded bridge should therefore be an adapter, not a reinterpretation:

\[
\operatorname{TriadicObserverTransitionV0}
\longrightarrow
\operatorname{CandidateThroughPresentation}
+R.
\]

The adapter must reuse original source, occurrence, cut, lineage, and slice
identities.  It may propose an interface relation only from explicit shared
incidences or a declared quotient map.  Equal values, matching printed
brackets, or inferred set intersections cannot create the relation.

Copy, merge, discard, and source-free events are required stress cases:

- copy should expose one-to-many lineage without pretending to be a
  bijective phase transport;
- merge may expose many-to-one compatibility;
- discard may make a relation partial; and
- source-free wires must remain outside the three source-relative interface
  readings while surviving in the residual.

These cases are exactly why the relation-valued syntax should precede any
group, braid, or inverse-only model.

---

## 8. Consequences for a future logic language

The proposal separates four judgements that a future logic must not collapse:

\[
\begin{array}{ll}
\operatorname{CutFormed}(L,R)
& \text{the option presentation is syntactically finite},\\
\operatorname{NumberAdmissible}(L,R)
& \text{the Conway number-order obligation holds},\\
\operatorname{ThroughCompatible}_N(L,R)
& \text{the two sides have one specialization image},\\
\operatorname{Resolved}_\rho(L,R)
& \text{a witness selects one passage in the relation}.
\end{array}
\]

A fifth judgement concerns the complete circuit:

\[
\operatorname{Closes}_Q(\rho_{KX},\rho_{Xt},\rho_{tK};\Theta_Q).
\]

This vocabulary may later contribute proposition constructors or proof
outcomes.  The finite fixture does not define truth, inference, normalization,
completeness, learning, or proof.

---

## 9. What the fixture checks

The pure-Python fixture checks:

1. the three circular interfaces have the unique opposite-domain types;
2. a wrong opposite type is `NotRepresentable`;
3. every angle through form is exactly a finite fibre product;
4. the relation is functional on regular points and multivalued at the node;
5. Conway number admissibility and through compatibility realize all four
   truth combinations;
6. all marked resolutions are distinct graphs inside one through relation;
7. all resolutions have the same public specialization;
8. relational converse is typed and involutive;
9. phase reversal gives the converse resolved graph;
10. the unresolved circular composite remains multivalued;
11. all \(125\) phase triples yield five equally represented holonomies;
12. the union of the five resolved holonomy graphs is exactly the unresolved
    circular relation; and
13. orientation reversal converses both unresolved and resolved circuit
    relations.

The fixture creates finite research data only.  It does not create Adva
sources, occurrences, cuts, diagrams, histories, policies, certificates, or
semantic identities.

---

## 10. Nonclaims and falsifiers

This note does not establish:

- that Conway or surreal theory historically interprets \(\mid\) as a
  traversal operator;
- that every game form is a through form or every through form is a game;
- that a through-compatible form is a surreal number;
- that an overlap interface is already a geometric nodal fibre;
- that \(I_{KX}^{t}\simeq N_t\), or either side equals an `Omega`-type
  computational boundary;
- that all through relations admit functional resolutions;
- that a selected resolution is canonical;
- that all circular coherence defects are permutations, braids, or groups;
- that duality reverses an active `ProgramSlice`;
- that singularity authorizes provenance erasure;
- a general normal form for mixed nested brackets;
- a complete 3-form logic; or
- universal computation.

The proposal must be revised if a grounded extension:

1. needs an interface type not determined by the declared pairwise overlap;
2. cannot express copy, merge, or discard as a relation with residual;
3. requires the unresolved through carrier to be a function;
4. makes relational duality covariant rather than contravariant;
5. erases distinct resolutions because their public node agrees; or
6. normalizes away a nontrivial circuit residual.

---

## 11. Next local gate

The next experiment should ground one angle form in the exact Rust-owned
transition artifact without promoting a stable API:

1. choose one checked three-input program with copy, merge, discard, and a
   source-free event;
2. select two exact adjacent cuts and obtain
   `TriadicObserverTransitionV0`;
3. choose one circular chart interface and its opposite-domain type;
4. derive candidate left and right carriers only from unchanged incidence and
   occurrence identities;
5. declare the candidate middle quotient explicitly;
6. compute the fibre-product relation and retain the full `ProgramSlice` as
   residual;
7. test converse, adjacent relational composition, and failure of
   single-valuedness; and
8. return `NotRepresentable` or an explicit obstruction when no justified
   quotient exists.

Promotion requires at least one nontrivial checked relation and one
counterexample showing why a simpler value-, bracket-, or permutation-based
construction fails.

---

## Conservative conclusion

The proposed angle form is compatible with the existing programme in a
precise, nonnumeric reading:

\[
\boxed{
\langle L\mid_NR\rangle
=
L\times_NR.
}
\]

The singular middle object packages the ambiguity of smooth passage into a
resolution fibre.  Duality reverses the relation.  The circular composition
retains holonomy.  Together these operations can flatten one bounded class of
intertwined syntax into three typed local passages plus one global residual,
but they do not yet provide a canonical normalization theorem.

The most important new separation is:

\[
\boxed{
\text{number order}
\ne
\text{through compatibility}
\ne
\text{chosen resolution}
\ne
\text{global closure}.
}

That separation turns the earlier failed `L/R` numerical reduction into a
well-typed research programme rather than a malformed expression.
