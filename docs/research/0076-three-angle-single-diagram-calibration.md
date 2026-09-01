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

The first grounded adapter derived only one relation-valued angle.  The present
experiment asks whether all three opposite-domain readings can be obtained
without combining separately compiled programs or fabricating cross-diagram
identity.

The bounded answer is:

[
oxed{
T_{KX}^{t},quad T_{Xt}^{K},quad T_{tK}^{X}
	ext{ coexist in one checked diagram and one complete slice.}
}
]

But the stronger conclusion is refused:

[
oxed{
T_{tK}^{X}circ T_{Xt}^{K}circ T_{KX}^{t}
	ext{ is not yet a grounded circular relation.}
}
]

The obstruction is exact.  Adjacent angles use distinct copy siblings in the
domain they appear to share.  They have a common checked source but different
occurrence identities.  No rule currently authorizes identifying them.

## 1. One six-hole configuration

The fixture has root sources (K,X,t).  Each source is copied once, producing

[
K_0,K_1,qquad X_0,X_1,qquad t_0,t_1.
]

A single checked call fills one ordered six-hole configuration.  Its body
contains three disjoint calls to the same two-hole addition program:

[
(K_0,X_0),qquad (X_1,t_0),qquad (t_1,K_1).
]

Those bodies produce the three local angle candidates

[
T_{KX}^{t}subseteq K_0	imes X_0,qquad
T_{Xt}^{K}subseteq X_1	imes t_0,qquad
T_{tK}^{X}subseteq t_1	imes K_1.
]

Every relation is the literal finite fibre product of two exact lower-cut
incidences over one exact pair-frame exit wire.  Rust supplies the diagram,
graft frames, cuts, slice, occurrence ancestry, and observer transition.
Python only indexes and compares those unchanged artifacts.

An independent source-free constant followed by discard lies outside the
three pair bodies.  It remains in the complete outer `ProgramSlice` attached
to every angle.

## 2. Validation gates

Every run reports nine ordered gates.

| gate | finite obligation |
|---|---|
| Rust origin | one `KernelFunction` supplies checked transition, slice, graft trace, ancestry, and identities |
| six-hole configuration | one parent has six ordered holes and exactly three disjoint active two-hole bodies |
| three angles | the bodies realize exactly (K	o Xmid t), (X	o tmid K), and (t	o Kmid X) |
| occurrence conservation | six distinct lower incidences are used exactly once, two per domain |
| schedule independence | legal schedule permutations have distinct traces but one equal observer transition and slice |
| residual retention | all local projections retain the full constant--discard and three-add residual |
| local duality | relational converse is involutive without claiming inverse execution |
| global closure | raw incidence composition is empty and exposes three missing sibling connectors |
| promotion boundary | no stable semantics, forgetting, connector, or circular closure is authorized |

A failure blocks every later gate.  In particular, a schedule with a missing
event is an obstruction, not an alternative history.

## 3. Schedule evidence

After the three copy events have completed, the three addition events are
independent.  The source-free constant must precede its discard.  The
experiment executes three legal orders on the same compiled function.

Their checked event words differ, but their observer transitions and canonical
outer `ProgramSlice` are equal.  Thus schedule variation is preserved as
history while the angle extraction depends only on the common exact carrier.

This is bounded evidence for one fixture.  It is not a general confluence or
schedule-coherence theorem.

## 4. Why the apparent triangle does not close

Writing only source labels hides the essential mismatch:

[
K	o X	o t	o K.
]

At occurrence resolution, the actual chain is

[
K_0	o X_0,qquad
X_1	o t_0,qquad
t_1	o K_1.
]

Ordinary relation composition compares the intermediate incidence indices
literally.  Therefore it would require

[
X_0=X_1,qquad t_0=t_1,qquad K_1=K_0.
]

All three equalities are false.  Each pair consists of distinct occurrences
created by the same checked copy and sharing one source.  Source equality is
not occurrence equality, and copy ancestry is not an implicit contraction.

If future work adds a connector

[
C_Dsubseteq D_0	imes D_1
]

for each domain (D), its meaning must be explicit.  At least three
possibilities must remain distinguished:

1. exact identity of one occurrence;
2. a reversible routing or comparison witness between copy siblings; and
3. an authorized quotient that deliberately forgets the sibling distinction.

Only the third performs semantic forgetting, so it requires a right-to-forget
rule and a retained residual or certificate.  This experiment authorizes none
of them.

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

The diagram looks circular only after erasing occurrence identity.  Treating
copy siblings as equal would silently add contraction and provenance hiding.
The current evidence therefore supports a *local triangular atlas*, not a
global circle or a three-computer execution cycle.

## 6. Relation to the proposed three-view IR

This calibration grounds two of the proposed views in one object:

- the triadic interface assigns the opposite-domain types;
- the multi-hole program provides active, noninvertible pair computations;
- the through presentation records the three local finite relations.

What is still absent is the comparison data that glues the local charts.  That
missing data is a precise target for the future IR: connectors must not be
inferred from typography, scalar equality, or source equality.

The next decisive experiment should introduce one explicitly typed
same-domain connector candidate and compare three readings: provenance-
preserving sibling comparison, authorized quotient, and refusal.  The test
must show which, if any, makes the circular composite nonempty while keeping
the complete process residual auditable.

## 7. Conservative conclusion

The three-angle shape is now executable without cross-diagram fabrication.
This is a meaningful strengthening of the one-angle result: all local charts
share one exact carrier and remain stable under the tested legal schedules.

The experiment simultaneously identifies the missing piece.  A shared source
does not glue distinct occurrences.  Until a typed connector and its
right-to-forget conditions are defined and certified, the correct global
answer is `not_representable`.
