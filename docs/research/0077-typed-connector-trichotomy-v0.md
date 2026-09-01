# Typed Connector Trichotomy V0

Status: bounded executable research experiment following
[0076](0076-three-angle-single-diagram-calibration.md) and
[ADR 0014](../adr/0014-typed-connector-trichotomy.md).

The implementation is
`adva.connector_research.ConnectorCalibrationMachineV0`; the fixture and
negative control are in
`tests/python/test_typed_connector_calibration.py`.

This note introduces no stable connector, copy inverse, contraction,
`ProvenanceHide`, circular execution, right-to-forget rule, logic, or
universality semantics.

---

## 0. Question and result

The single-diagram triangle exposed three missing same-domain connections.
This experiment asks what happens when those apparent connections are read in
three different ways:

1. strict identity of exact occurrences;
2. an explicit comparison relation between direct copy siblings; and
3. projection of occurrences to their checked source.

The finite result is a trichotomy:

| reading | occurrence cycle | source cycle | information loss | semantic promotion |
|---|---:|---:|---:|---:|
| exact identity | empty | absent | none | refused |
| direct-sibling comparison | one diagonal pair | absent | none | refused |
| source quotient | absent | one diagonal pair | occurrence distinction | refused |

Thus two different constructions make a finite relation look closed, but for
different reasons. Neither currently licenses a closed program process.

## 1. Exact boundary data

For the checked triangular fixture, write the three local relations as

\[
A_{KX}:K_0\mathrel{\relbar\joinrel\longrightarrow}X_0,
\qquad
A_{Xt}:X_1\mathrel{\relbar\joinrel\longrightarrow}t_0,
\qquad
A_{tK}:t_1\mathrel{\relbar\joinrel\longrightarrow}K_1.
\]

The three gaps are therefore

\[
X_0\dashrightarrow X_1,
\qquad
t_0\dashrightarrow t_1,
\qquad
K_1\dashrightarrow K_0.
\]

Each endpoint retains its exact lower-cut incidence index, `OccurrenceId`,
`SourceId`, observer domain, and `OccurrencePath`. In the positive fixture,
each pair has paths $p0$ and $p1$ for one common checked parent path $p$.
The adapter does not allocate a connector identity.

## 2. Reading I: strict occurrence identity

For each domain $D$, strict identity is

\[
I_D=\{(i,i):\operatorname{domain}(i)=D\}.
\]

Because adjacent angle endpoints are different incidences,

\[
X_0\neq X_1,
\qquad
t_0\neq t_1,
\qquad
K_0\neq K_1.
\]

Consequently the exact-incidence composite

\[
I_K\circ A_{tK}\circ I_t\circ A_{Xt}\circ I_X\circ A_{KX}
\]

is empty. Identity preserves all provenance, but it does not bridge copy
siblings. This is the correct negative control against implicit contraction.

## 3. Reading II: direct-sibling comparison

For two exact occurrences $d_0,d_1$, the bounded fixture admits a sibling
comparison only when:

- their `SourceId` values are equal;
- their `OccurrenceId` values are different;
- their paths have equal positive length;
- deleting the final branch index gives the same parent path; and
- the two final indices are exactly $0$ and $1$.

The test-local relation is symmetric:

\[
S_D=\{(d_0,d_1),(d_1,d_0)\}.
\]

With all three $S_D$, finite relation composition gives

\[
S_K\circ A_{tK}\circ S_t\circ A_{Xt}\circ S_X\circ A_{KX}
=\{(K_0,K_0)\}.
\]

This is a genuine occurrence-indexed candidate relation. It does not identify
$d_0$ with $d_1$: both IDs and both paths remain present.

The symmetry belongs to the comparison relation, not to program execution.
It does not make `copy` invertible, reconstruct a consumed parent, or prove a
coherence cell. Python has checked a finite relation over Rust-owned
coordinates; Rust has not certified a connector.

## 4. Reading III: source quotient

The third reading uses the already checked field

\[
q_D(i)=\operatorname{SourceId}(i).
\]

In the fixture, every domain fibre contains two distinct occurrences and one
source. Applying $q$ to the three angle relations gives

\[
K\to X,
\qquad
X\to t,
\qquad
t\to K,
\]

so source-level composition yields

\[
K\to K.
\]

The closed source cycle is mathematically immediate, but the map is
many-to-one. It forgets the distinction between the two occurrences, their
branch positions, and which local angle consumed each sibling. The complete
`ProgramSlice` remains attached as residual evidence, but no current result
authorizes using this projection as semantic equality or global closure.

## 5. The cousin counterexample

The negative fixture refines only the construction source. Its two surviving
construction paths are

\[
(0)
\qquad\text{and}\qquad
(1,0).
\]

They have the same source and distinct occurrence identities, but they are not
direct siblings: neither is obtained from the same parent by taking the two
branches $0$ and $1$.

The experiment therefore reports:

- strict identity: no cycle;
- direct-sibling comparison: `not_representable`;
- source quotient: a nonempty source cycle.

This is the decisive red-team result. Source projection can close a diagram
even when the finer copy geometry supplies no local sibling witness. Therefore
source closure is too coarse to justify occurrence closure.

## 6. Residual and validation gates

Every trial remains nested in the same triangular artifact. The complete outer
slice retains all three additions and the independent source-free
constant--discard process.

The ordered gates are:

| gate | obligation |
|---|---|
| triangle carrier | reuse one supported local triangle and its raw closure obstruction |
| typed boundaries | retain three distinct same-source occurrence pairs |
| exact identity | diagonal relations do not cross distinct occurrences |
| sibling comparison | direct siblings close exactly; cousins are refused |
| source quotient | three two-occurrence source fibres project to one source cycle |
| residual retention | all readings retain the complete common slice |
| promotion boundary | relation closure, semantic closure, and forgetting authority remain distinct |

A bounded calibration is supported when it reports the expected contrast. A
trial-level `not_representable` is therefore evidence, not failure of the
whole comparison.

## 7. Interpretation for the future IR

The experiment separates two previously conflated missing structures.

First, a provenance-preserving comparison can glue local charts while keeping
both endpoints. This suggests a relational atlas or span-like layer for
through forms. It can carry openness as unresolved multiplicity rather than
eliminating it.

Second, a quotient can compress that multiplicity into a finite feature. This
is closer to learning or normalization, but it needs an explicit observation
policy, a right-to-forget condition, and residual evidence. It cannot be
inferred merely because the quotient makes a cycle close.

A future IR may therefore need both:

\[
\text{comparison witness}
\quad\neq\quad
\text{forgetting quotient}.
\]

The former says how two retained occurrences are related. The latter says why
their difference is irrelevant for a declared task.

## 8. Conservative conclusion

The missing connector is not one operation with three spellings. There are at
least two structurally different ways to repair the local triangle:

- preserve the fibre and add comparison data; or
- collapse the fibre under a declared observation.

The first closes a finite occurrence relation without erasing provenance. The
second closes a coarser source relation but can also create a false positive on
same-source cousins. Neither is yet a semantic execution cycle.

The next mathematical task is to state the minimal evidence type for the first
reading and the minimal right-to-forget judgment for the second. Only then can
we ask whether either participates in the proposed logic or normalization
language.
