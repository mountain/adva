# Active Task Brief: Exact Triadic Observer Transitions

Status: approved bounded engineering phase after completion of the exact
`GraftTrace` and `ProgramSlice` work. This phase supplies a Rust-grounded bridge
from exact program intervals to the three-domain research language. It does not
yet define the logic, a specializer, an interpreter, or universal computation.

## 1. Mission

For one validated finite diagram, one exact `ProgramSlice(P,U,V)`, and one
explicit assignment of the three input-source fibres to construction `K`,
space `X`, and time `t`, derive a certificate-bearing object

\[
\operatorname{TriadicObserverTransitionV0}(P,U,V;Q).
\]

It must contain:

1. the unchanged exact `ProgramSlice` as its complete process residual;
2. occurrence-level readings of both endpoint cuts;
3. three views, one for each domain, that expose the other two source-domain
   fibres and hide the observer's own fibre;
4. an exact lower-to-upper occurrence ancestry relation; and
5. exact composition across adjacent slices.

This is the smallest common engineering object currently justified by the
research. It makes “a vertex reads its opposite pair” executable without
pretending that every internal wire has one intrinsic time/space/construction
type.

## 2. Dependency checkpoint

The previous phase has met its exit condition:

- compiler graft frames are exact companion artifacts;
- `ProgramSlice` is an identity-preserving same-diagram interval;
- adjacent slice composition is exact, unital, and associative in the declared
  finite scope;
- Python exposure is read-only; and
- hidden internal events and unchanged through wires survive composition.

The new phase therefore uses `ProgramSlice`; it does not reopen or replace it.

## 3. The obstruction that fixes the design

Assigning one domain label directly to every internal cut wire is not
canonical. Explicit copy can create several occurrences from one source,
ordinary operations can merge lineages from several sources onto one wire,
and discard can remove a lineage from the upper cut. A wire may therefore
carry zero, one, or several source-domain incidences.

The observer carrier must be incidence-level:

\[
(\text{cut wire},\text{lineage position},\text{OccurrenceId},
  \text{SourceId},\text{domain}).
\]

Domain is policy metadata derived from an input position and exact source
identity. It is not a new semantic identity and not a `ValueType`.

## 4. Bounded definitions

### 4.1 Policy

`TriadicObserverPolicyV0` contains exactly three input-domain assignments, one
each for `K`, `X`, and `t`. Rust derives the corresponding source assignment
from the certified initial cut. V0 rejects:

- boundaries other than exactly three inputs;
- repeated or missing roles;
- an input with anything other than one checked root source occurrence; and
- a policy that does not cover the complete source partition.

This restriction is a calibration boundary, not a claim that all future
triadic programs have exactly three scalar inputs.

### 4.2 Cut observation

For every cut wire, Rust resolves each lineage position to its unchanged
`Occurrence`, `SourceId`, `OccurrencePath`, and policy domain. A source-free
wire is retained by exact wire index but belongs to none of the source-relative
charts.

For observer domain `D`, the opposite-pair view is

\[
V_D(c)=\{i\in\operatorname{Inc}(c):\operatorname{domain}(i)\ne D\}.
\]

The own-domain complement is recorded explicitly. Every sourced incidence is
visible in exactly two views and hidden in exactly one. Views overlap by
design; they are not a partition into three independent computers.

### 4.3 Transition relation

For lower incidence `a` and upper incidence `b`, define

\[
a\leadsto b
\iff
\operatorname{source}(a)=\operatorname{source}(b)
\quad\text{and}\quad
\operatorname{path}(a)\preceq\operatorname{path}(b),
\]

where `preceq` is occurrence-path prefix.

This uses the existing checked lineage semantics:

- ordinary operations retain occurrences;
- `copy` replaces a parent by children whose paths extend the parent path;
- merge retains every input occurrence in the output lineage; and
- discard has no upper descendant.

No scalar evaluation, output equality, structural hash, or Python identity
participates.

### 4.4 Complete residual

The observer transition embeds the full exact `ProgramSlice`. Hiding an
own-domain incidence from one chart, or keeping a source-free wire outside all
charts, does not erase it from the process carrier. When a compiler graft trace
is supplied, graft intersections remain in that embedded slice.

`complete` here means complete relative to the certified slice artifact and
the optional provenance supplied to the analysis. It does not reconstruct
graft provenance for imported version-one diagrams.

## 5. Composition law

For `U <= V <= W`, revalidate both transition inputs and require literal
equality of their middle cut observations. Compose the embedded slices through
the existing exact operation. Then require

\[
\leadsto_{U,W}
=
\leadsto_{U,V};\leadsto_{V,W}
\]

as finite relations on occurrence incidences, and require the resulting whole
artifact to equal the directly derived outer transition.

This law is stronger than comparing three marginal counts. It preserves the
copy ancestry needed to distinguish one source with two descendants from two
unrelated sources.

## 6. Mandatory distinctions

Keep these four objects separate:

| Object | Meaning |
|---|---|
| `ProgramSlice` | exact active process interval |
| triadic cut/transition view | observer projection over that interval |
| reversible transport | extra path or braid data, not introduced here |
| observer specialization | fresh residual program plus correspondence, deferred |

In particular, this phase does not identify the ancestry relation with program
execution, a proof, a braid, `D*`, or bracket normalization.

## 7. Required tests

1. one three-input fixture containing explicit copy, merge, identity,
   source-free constant, and discard;
2. exact reuse of all source and occurrence identities;
3. every sourced incidence visible twice and hidden once;
4. source-free wires retained outside all three views;
5. one lower occurrence relating to two copied upper descendants;
6. hidden constant/discard events retained in the embedded outer slice;
7. exact adjacent composition through a middle cut containing a source-free
   wire;
8. rejection of a repeated or incomplete domain policy; and
9. no numerical evaluation in structural tests.

## 8. Exit condition

The bounded phase is complete when:

- Rust owns all V0 result and certificate types;
- direct and composed transitions agree exactly;
- lineage relation composition is checked independently of slice equality;
- source-free, own-domain, and graft residuals cannot be silently erased;
- the checked fixture covers copy, merge, constant, and discard;
- architecture, semantic scope, claims, and an ADR state the boundary; and
- formatting, Clippy, Rust tests, and the repository CI matrix are green.

The highest-priority successor is then not “more brackets.” It is to decide
whether a certified observer transition is sufficient input for the proposed
reverse-dual characteristic logic, or whether logic requires a stronger
evidence/result type. Only after that decision should an executable residual
specializer or interpreter be added.

## 9. No-go boundary

This phase establishes no:

- intrinsic assignment of `K`, `X`, or `t` to arbitrary wires;
- stable general `ObservationPolicy` algebra;
- output-role support nesting or Raw111 bracket tree for arbitrary cuts;
- `ProvenanceHide` permission or right-to-forget theorem;
- active triadic rewrite, normalization, proof search, or universal machine;
- reversible braid/holonomy carrier;
- fresh residual program or observer specialization;
- equation, coherence, completeness, soundness, or universality theorem.

Those are downstream questions whose proposed rules must consume this exact
carrier or explain why it is insufficient.
