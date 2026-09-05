# Grounded Multi-Hole Through Adapter V0

Status: bounded executable research experiment following
[0070](0070-typed-surreal-through-forms.md),
[0074](0074-three-layer-research-machine-v0.md), and
[ADR 0012](../adr/0012-grounded-multi-hole-through-adapter.md).

The implementation is `adva.research.MultiHoleThroughMachineV0`; the fixture
is `tests/python/test_grounded_multi_hole_through_adapter.py`.

This note introduces no stable through type, specialization, permission to
forget, active normalization, logic, interpreter, or universality semantics.

---

## 0. Result

One angle of the proposed circular through syntax can now be grounded in the
current exact program carrier:

\[
\boxed{
T_{Xt}^{K}=F_X\times_{N_K}F_t.
}
\]

Here `F_X` and `F_t` are not invented phase points.  They are exact lower-cut
incidence indices occupying the ordered holes of one checked call frame.
`N_K` is not yet a geometric Omega singularity.  It is the explicitly declared
finite quotient that sends an upper occurrence incidence to its exact upper
cut-wire index, restricted to the frame exits.

This is enough to connect the three-computer observer and one active multi-hole
program without pretending that the observer transition itself is already a
through cospan.

## 1. The checked fixture

The program has three root sources assigned to construction `K`, space `X`,
and time `t`.  Its active call frame has the ordered holes

\[
H=(x,t_0,t_1).
\]

One syntax argument supplies `x`; a second argument copies `t` and supplies two
outputs to the two remaining holes.  The callee merges all three occurrences
onto one output wire.  An independent source-free constant is discarded, and
the construction input passes through unchanged.

This fixture simultaneously exposes facts that a one-point expression model
cannot state:

- syntax arguments and ordered holes are different collections;
- copy creates two distinct time occurrences;
- merge retains all three occurrences on one wire;
- a source-free constant--discard component remains process residual; and
- construction, space, and time remain observer metadata, not wire types.

The lower cut is taken after the time copy.  The upper cut is taken after the
complete four-event interval.  Both cuts, the interval, the graft frame, and
all ancestry links are rederived by Rust from the same `KernelFunction`.

## 2. The declared finite construction

Let `i` be a selected lower incidence.  Rust already supplies the ancestry
relation

\[
i\leadsto j
\]

to an upper incidence `j`.  Let

\[
\pi(j)=\operatorname{upperCutWireIndex}(j)
\]

for upper incidences on exact frame exit wires.  The adapter declares

\[
q_X=\pi\circ\leadsto\mid_{F_X},
\qquad
q_t=\pi\circ\leadsto\mid_{F_t}.
\]

These are relations rather than assumed total functions: later copy may give
one lower incidence several exit images, while discard may give it none.
The through carrier is computed literally as

\[
T_{Xt}^{K}
=
\{(x,t):q_X(x)\cap q_t(t)\ne\varnothing\}.
\]

The middle quotient forgets only which lineage position on one exact upper
wire was used.  It does not identify sources, occurrences, paths, holes,
events, or programs.  All of those remain available through the attached
interpretation cell and complete `ProgramSlice`.

## 3. Positive evidence

The fixture yields

\[
|F_X|=1,
\qquad
|F_t|=2,
\qquad
|T_{Xt}^{K}|=2.
\]

Both time occurrences have the same public middle wire but remain different
members of the relation.  Therefore `T_Xt^K` is not a function from the space
incidence to the time incidences.  The copy ambiguity has been represented as
a finite fibre rather than resolved or erased.

Relational converse gives

\[
(T_{Xt}^{K})^\star=(T_{Xt}^{K})^{\mathsf{op}},
\qquad
((T_{Xt}^{K})^\star)^\star=T_{Xt}^{K}.
\]

This is a dual reading of the relation, not a reverse execution of copy, add,
discard, or the complete slice.

The exact observer carrier is also split across a middle cut containing the
source-free constant wire.  Rust verifies literal middle-observation
agreement, exact slice composition, ancestry-relation composition, and equality
with the direct outer transition.  This checks the carrier beneath the through
proposal.  It does not yet prove that arbitrary derived through relations
compose.

## 4. Layered validation

Every run reports the same ordered gates:

| gate | finite obligation |
|---|---|
| Rust origin | transition, slice, policy, ancestry, IDs, and graft trace are checked |
| interface typing | two chart domains are distinct; the third domain types the interface |
| ordered holes | each hole reuses one exact lower-cut entry wire and one chart fibre |
| same-diagram identity | frame body, entry, exit, and slice intersection use one diagram |
| middle quotient | each surviving side reaches a frame exit under exact ancestry |
| fibre product | relation equals the common-image construction exactly |
| residual retention | the complete original `ProgramSlice` remains attached |
| relational duality | converse is involutive without claiming inverse execution |
| adjacent composition | the underlying Rust transition composes exactly |
| promotion boundary | no stable semantics, forgetting, normalization, or universality is authorized |

A failed gate blocks later conclusions.  It does not rewrite a failure as
success merely because another observation looks similar.

## 5. Negative controls

Three controls delimit the result.

1. If the interface is labeled by either endpoint domain rather than the
   unique opposite domain, the candidate is `not_representable` before a
   relation is built.
2. If two same-typed holes pass through separate `id` operations to two
   distinct output wires, both specialization relations exist but their fibre
   product is empty.  Equal `Real` types do not fabricate a middle object.
3. If the right hole is discarded while the left hole survives, the right
   specialization is empty.  The result is a partial obstruction with the
   discard event and complete residual retained, not `ProvenanceHide`.

These controls are as important as the positive fixture: the new relation is
created by exact shared incidence on a declared quotient, not by bracket
spelling, type equality, or a desire for totality.

## 6. What has and has not been connected

The experiment supplies one finite bridge:

\[
\boxed{
\text{ordered holes}
\longrightarrow
\text{opposite-domain incidence carriers}
\longrightarrow
\text{declared wire quotient}
\longrightarrow
\text{through relation}
}
\]

The three-computer side contributes the source-domain policy and exact
opposite-side occurrence carrier.  The multi-hole program contributes active,
noninvertible copy, merge, and discard.  The through reading records which
opposite-side incidences can pass through one common program-produced feature.
The complete process residual prevents this bridge from becoming an extensional
value equality.

The following remain open:

- a configuration *space* containing several alternative fillings of the same
  holes, rather than one checked filling;
- certified substitution maps between such configurations;
- the other two circular interfaces and their global composite;
- a justified comparison between the finite wire quotient, geometric nodal
  fibres, and either use of `Omega`;
- selected resolutions and their provenance;
- composition laws for derived through relations;
- an active normalizer, specializer, or interpreter; and
- any completeness, termination, confluence, or universality theorem.

## 7. Conservative conclusion

The missing piece was not another bracket constructor.  It was a small but
explicit quotient between exact multi-hole program incidence and a public
feature carrier.  Once that quotient is stated, copy and merge naturally
produce a relation-valued fibre, discard naturally produces partiality, and
the triadic observer gives the interface its opposite-domain type.

This validates one local shape of the larger idea.  It does not yet identify
the full program space with the through machine.  The next decisive experiment
is to keep the same ordered holes while varying checked fillings, then ask
whether their candidate quotients and through relations admit a certified
same-source comparison without cross-diagram identity fabrication.
