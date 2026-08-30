# Finite E0 Dual-Cut Surgery and a Conditional PSP-Star Factorization

Status: bounded Python research construction over Rust-certified causal cuts.
It defines one finite projective frame, one declared planar cellular embedding,
and one exact cut-level factorization. It is not a stable E0 grid, `pullback`,
`ProgramSlice`, normal-form, or expression-level factorization API.

## Question

The preceding program-process work produced an occurrence-aware causal cut,
expression-valued backward sections, exact nested-cut composition, and a
matrix-like coefficient shadow. The remaining geometric question can be
stated in an elementary form.

Given a checked transformation process between open arithmetic expressions,
can its causal frontier be presented on a finite E0 grid so that:

1. the primal causal cut becomes a cycle on the dual grid;
2. crossing one enabled event becomes one local cycle expansion or
   contraction;
3. the resulting surgery word supplies a schedule-independent characteristic
   expression; and
4. an analysis/synthesis pair gives a factorization of the form
   \(T=P S P^\ast\) without forgetting holes, sources, occurrences, or
   substitution scopes?

The present calibration proves the first three statements and a cut-level
version of the fourth on one finite fixture. It also isolates the exact reason
the full expression statement cannot yet be certified: `adva.ir` version 1
retains a flat call event but not the nested graft frame and its boundary maps.

## Minimal projective E0 frame

Use homogeneous point and predicate coordinates

\[
v=\binom{X}{Y},
\qquad
\varphi=(R,S),
\qquad
a(v)=-\frac{X}{Y},
\qquad
b(\varphi)=-\frac{R}{S}.
\]

The oriented lift of the negative reciprocal is

\[
J=
\begin{pmatrix}
0&-1\\
1&0
\end{pmatrix},
\qquad
Jv=\binom{-Y}{X},
\qquad
J^2=-I.
\]

Projectively this is the involution \(a\mapsto-1/a\), exchanging zero and
infinity. Predicate transport is contravariant:

\[
\varphi\longmapsto\varphi J^{-1}=(-S,R),
\]

and the incidence pairing is preserved:

\[
(\varphi J^{-1})(Jv)=\varphi(v).
\]

The executable finite frame uses the bounded additive point grid

\[
G_A^{(2)}=\{-2,-1,0,1,2,\infty\}
\]

and its exact negative-reciprocal image \(J(G_A^{(2)})\). This checks the
projective point/covaluation relationship, including the oriented central
sign. It does **not** prove that a previously intended infinite E0 standard
grid is canonically identical to the combinatorial planar dual used below.
That identification remains declared chart data in this witness.

## Checked primal graph and its dual cycle

Adjoin one boundary vertex for every program input and output to the checked
operation DAG. A checked linear wire is then a primal edge. Inputs are always
on the completed side of a cut; outputs are always on its future side.

For a downward-closed completed event set \(U\), let \(\delta U\) be the set
of primal edges crossing from the input-plus-completed side to the
future-plus-output side. This is exactly the edge support returned by Rust's
`analyze_causal_cut`.

Choose a cellular planar embedding of the finite primal graph in the E0 chart.
Each primal edge has one cellular-dual edge. The dual of the cut is

\[
\gamma_U=(\delta U)^\vee.
\]

Because a primal cut is a coboundary, \(\gamma_U\) is a relative mod-two
cycle. Boundary bridges become self-loops on the outer dual face and therefore
contribute even degree.

If event \(e\notin U\) is enabled, every edge incident to \(e\) changes cut
membership and no other edge changes. Hence

\[
\delta(U\cup\{e\})
=
\delta U\mathbin{\triangle}\operatorname{star}(e).
\]

The dual of the primal vertex star is the boundary of the dual face
\(f_e^\vee\). Therefore

\[
\boxed{
\gamma_{U\cup\{e\}}
=
\gamma_U\mathbin{\triangle}\partial f_e^\vee
}.
\]

The symmetric difference replaces one part of the current cycle by the
complementary part of one face boundary. Geometrically this is the elementary
cycle expansion/contraction operation. Copy and recombination are still
explicit program events; the operation does not identify their occurrence
lineages.

## The bounded presentation pair

For the declared finite cellular model, define a research-local analysis map

\[
P_G^\ast:
\operatorname{Cut}(D,U)
\longrightarrow
(U,\gamma_U,\operatorname{Dec}_D),
\]

where `Dec_D` is the unchanged checked source, occurrence, lineage, producer,
and consumer decoration attached to every dual edge. The completed past is
retained deliberately; a bare cycle is not the whole process state.

The read-only synthesis map

\[
P_G:(U,\gamma_U,\operatorname{Dec}_D)
\longrightarrow
\operatorname{Cut}(D,U)
\]

looks up the same pre-indexed Rust wires. It creates no source, occurrence,
cell, certificate, or semantic identity. On every causal cut of the fixture,

\[
P_G P_G^\ast=I
\]

holds as exact checked-data equality.

Let \(s_e\) toggle \(\partial f_e^\vee\) and add the enabled event to the
completed past. Every checked causal step in the fixture then satisfies

\[
\boxed{
\operatorname{Cut}(D,U\cup\{e\})
=
P_G\,s_e\,P_G^\ast\operatorname{Cut}(D,U)
}.
\]

This is the established PSP-star statement. It factors the cut transition,
not yet an arbitrary transformation between multi-hole expressions.

## Characteristic surgery expression

For a legal schedule \(e_1,\ldots,e_n\), define

\[
S_T=s_{e_n}\cdots s_{e_1}.
\]

The final dual cycle alone is too coarse. The characteristic expression is
the surgery path modulo only the interchange of simultaneously enabled,
wire-disjoint events:

\[
s_es_f=s_fs_e.
\]

The fork-recombine fixture has checked operation sequence

```text
copy -> {neg, id} -> add
```

and exactly two linear schedules. The test exhausts both schedules, verifies
the dual interchange square, and derives the common concurrency-layer normal
form

```text
(copy) ({neg, id}) (add)
```

This is a bounded trace characteristic, not a matrix diagonalization or a
general canonical rewrite theorem.

## Why the cycle must be decorated by history

The second fixture retains one input-to-output through-wire while executing an
internal constant followed by explicit discard. Its initial and terminal
frontiers, and hence their bare dual-cycle supports, are equal. The completed
pasts and surgery word are different.

Thus

\[
\text{same terminal dual cycle}
\centernot\Longrightarrow
\text{same process history}.
\]

The geometric carrier must retain at least the decorated surgery path or an
equivalent event-poset record. Homology or a final loop shape alone cannot be
the characteristic process.

## Typed expression-level target

For distinct multi-hole expression objects \(X\) and \(Y\), the well-typed
target is

\[
T=P_Y S_T P_X^\ast,
\]

not automatically one same-`P` conjugation. Analysis and synthesis would need
to satisfy

\[
P_XP_X^\ast=I_X,
\qquad
P_YP_Y^\ast=I_Y,
\]

on a declared admissible fragment. The one-`P` spelling is a special case
where source and target use one self-dual presentation.

For hole substitution \(E\circ_i F\), the desired contravariant gluing law is
schematically

\[
(E\circ_i F)^\ast
=
F^\ast\circ_i^\vee E^\ast.
\]

This law cannot be checked from the current flattened `SharedProgramDiagram`.
The call history records only the callee name; it lacks the parent frame,
ordered argument-producing regions, instantiated callee-body region, and
entry/exit boundary maps. Any Python reconstruction of those fields would
violate Rust semantic authority.

## Executable evidence

The bounded test verifies:

1. \(J^2=-I\) on the oriented homogeneous lift and projective order two;
2. exact negative-reciprocal transport of the bounded point grid;
3. preservation of the point-predicate incidence pairing under covariant and
   contravariant `J` transport;
4. exact `P_G P_G^*=I` reconstruction for every causal cut of the checked
   fork-recombine diagram;
5. the mod-two cycle condition for every dual cut and every event-face
   boundary;
6. the face-surgery equation for every enabled event at every completed past;
7. the closed dual interchange square for the two independent branch events;
8. equality of final states for both legal schedules and their common
   concurrency-layer normal form;
9. an explicit constant-discard history hidden by equal initial and terminal
   bare cycles; and
10. the current flat call-history boundary that blocks a scope-faithful
    expression-level `P*`.

No scalar evaluation, floating-point comparison, Jacobian, matrix
multiplication, or analytic truncation is used.

## No-go boundaries

This calibration does not establish:

- a canonical infinite E0 standard-grid definition;
- a theorem identifying `J(G)` with the cellular dual of every checked
  program embedding;
- a planarity theorem or a certified routing of crossings through explicit
  `swap` cells;
- an oriented integer-chain surgery law or a global chirality theorem;
- a stable `Probe`, `pullback`, `D*`, dual fibre, cycle, or grid API;
- nested-scope reconstruction, arbitrary hole substitution, binders,
  recursion, feedback, or cross-program semantic identity;
- correctness of algebraic rewrites merely because their cells are
  geometrically admissible;
- uniqueness or minimality of the presentation pair;
- an unrestricted factorization of every program transformation;
- an equation or coherence cell from the successful finite tests.

## Next obligations

1. Complete the approved `GraftTrace` and `ProgramSlice` phase so ordered hole
   bindings and nested scope boundaries become Rust-certified data.
2. Replace the declared diamond embedding by a finite grid-embedding
   certificate, using explicit `swap` events rather than silent wire
   crossings.
3. Lift mod-two support to oriented integer relative chains and relate the
   forward/reverse surgery sign to the oriented lift \(J^2=-I\).
4. Test the contravariant hole-gluing law on a nested two-hole call using the
   certified graft trace.
5. Only then construct expression-level \(P_X^\ast,P_Y,S_T\), require a
   replayable retraction or expose a residual, and decide whether the desired
   full factorization survives unchanged or must be weakened.
