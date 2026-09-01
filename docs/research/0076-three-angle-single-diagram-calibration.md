# Three-Angle Single-Diagram Calibration V0

Status: bounded executable research experiment following
[0074](0074-three-layer-research-machine-v0.md),
[0075](0075-grounded-multi-hole-through-adapter-v0.md), and
[ADR 0013](../adr/0013-single-diagram-three-angle-calibration.md).

The implementation is `adva.triangular_research.TriangularThroughMachineV0`;
the fixture is
`tests/python/test_three_angle_single_diagram_calibration.py`.

This note introduces no stable circular through object, sibling connector,
permission to forget, normalization rule, logic, interpreter, or universality
semantics.

---

## 0. Question and bounded answer

The first grounded adapter derived only one relation-valued angle. This
experiment asks whether all three opposite-domain readings can be obtained
without combining separately compiled programs or fabricating cross-diagram
identity.

The bounded answer is:

\[
\boxed{
T_{KX}^{t},\quad T_{Xt}^{K},\quad T_{tK}^{X}
\text{ coexist in one checked diagram and one complete slice.}
}
\]

But the stronger conclusion is refused:

\[
\boxed{
T_{tK}^{X}\circ T_{Xt}^{K}\circ T_{KX}^{t}
\text{ is not yet a grounded circular relation.}
}
\]

The obstruction is exact. Adjacent angles use distinct copy siblings in the
domain they appear to share. They have a common checked source but different
occurrence identities. No rule currently authorizes identifying them.

## 1. One six-hole configuration

The fixture has root sources (K,X,t). Each source is copied once, producing

\[
K_0,K_1,\qquad X_0,X_1,\qquad t_0,t_1.
\]

A single checked call fills one ordered six-hole configuration. Its body
contains three disjoint calls to the same two-hole addition program:

\[
(K_0,X_0),\qquad (X_1,t_0),\qquad (t_1,K_1).
\]

Those bodies produce the three local angle candidates

\[
T_{KX}^{t}\subseteq K_0\times X_0,\qquad
T_{Xt}^{K}\subseteq X_1\times t_0,\qquad
T_{tK}^{X}\subseteq t_1\times K_1.
\]

Every relation is the literal finite fibre product of two exact lower-cut
incidences over one exact pair-frame exit wire. Rust supplies the diagram,
graft frames, cuts, slice, occurrence ancestry, and observer transition.
Python only indexes and compares those unchanged artifacts.

An independent source-free constant followed by discard lies outside the
three pair bodies. It remains in the complete outer `ProgramSlice` attached
to every angle.

## 2. Validation gates

Every run reports nine ordered gates.

| gate | finite obligation |
|---|---|
| Rust origin | one `KernelFunction` supplies checked transition, slice, graft trace, ancestry, and identities |
| six-hole configuration | one parent has six ordered holes and exactly three disjoint active two-hole bodies |
| three angles | the bodies realize exactly (K\to X\mid t), (X\to t\mid K), and (t\to K\mid X) |
| occurrence conservation | six distinct lower incidences are used exactly once, two per domain |
| schedule independence | legal schedule permutations have distinct traces but one equal observer transition and slice |
| residual retention | all local projections retain the full constant--discard and three-add residual |
| local duality | relational converse is involutive without claiming inverse execution |
| global closure | raw incidence composition is empty and exposes three missing sibling connectors |
| promotion boundary | no stable semantics, forgetting, connector, or circular closure is authorized |

A failure blocks every later gate. In particular, a schedule with a missing
event is an obstruction, not an alternative history.

## 3. Schedule evidence

After the three copy events have completed, the three addition events are
independent. The source-free constant must precede its discard. The experiment
executes three legal orders on the same compiled function.

Their checked event words differ, but their observer transitions and canonical
outer `ProgramSlice` are equal. Thus schedule variation is preserved as
history while angle extraction depends only on the common exact carrier.

This is bounded evidence for one fixture. It is not a general confluence or
schedule-coherence theorem.

## 4. Why the apparent triangle does not close

Writing only source labels hides the essential mismatch:

\[
K\to X\to t\to K.
\]

At occurrence resolution, the actual chain is

\[
K_0\to X_0,\qquad
X_1\to t_0,\qquad
t_1\to K_1.
\]

Ordinary relation composition compares the intermediate incidence indices
literally. Therefore it would require

\[
X_0=X_1,\qquad t_0=t_1,\qquad K_1=K_0.
\]

All three equalities are false. Each pair consists of distinct occurrences
created by the same checked copy and sharing one source. Source equality is
not occurrence equality, and copy ancestry is not an implicit contraction.

If future work adds a connector

\[
C_D\subseteq D_0\times D_1
\]

for each domain (D), its meaning must be explicit. At least three
possibilities must remain distinguished:

1. exact identity of one occurrence;
2. a comparison witness between retained copy siblings; and
3. an authorized quotient that deliberately forgets the sibling distinction.

Only the third performs semantic forgetting, so it requires a right-to-forget
rule and retained residual evidence. This experiment authorizes none of them.

## 5. Positive, negative, and red-team results

### Positive

- All three typed local angles come from one compilation, diagram, policy, cut
  interval, and complete slice.
- The parent configuration has six exact holes; the three active bodies
  partition its body region.
- Every copied occurrence participates in exactly one angle.
- Legal schedules retain distinct histories over one canonical carrier.
- Each local relation has a well-defined involutive converse.
- Source-free activity is not erased by local feature extraction.

### Negative controls

- An alternative schedule with a different event set is rejected before any
  closure claim.
- A schedule containing the same event twice is rejected at request
  construction.
- Raw local relations do not compose merely because adjacent endpoints share a
  source label.

### Red-team conclusion

The diagram looks circular only after erasing occurrence identity. Treating
copy siblings as equal would silently add contraction and provenance hiding.
The current evidence therefore supports a local triangular atlas, not a global
circle or a three-computer execution cycle.

## 6. Relation to the proposed three-view IR

This calibration grounds the three proposed readings in one object:

- the triadic interface assigns the opposite-domain types;
- the multi-hole program provides active, noninvertible pair computations; and
- the through presentation records the three local finite relations.

What remains absent is comparison data that glues the local charts. Connectors
must not be inferred from typography, scalar equality, or source equality.

The follow-up experiment is
[0077](0077-typed-connector-trichotomy-v0.md). It compares strict occurrence
identity, provenance-preserving direct-sibling comparison, and source
projection without promoting any of them to semantic closure.

## 7. Conservative conclusion

The three-angle shape is executable without cross-diagram fabrication. All
local charts share one exact carrier and remain stable under the tested legal
schedules.

The experiment simultaneously identifies the missing piece. A shared source
does not glue distinct occurrences. Until a typed connector and its
right-to-forget conditions are defined and certified, the raw global answer
remains `not_representable`.
