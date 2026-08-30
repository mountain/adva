# Technical Report: The Program-Process Core of Adva

Status: self-contained handoff report updated through exhaustive exact slice
laws and the read-only Python facade. This report
describes the theory currently accepted by the project, the exact executable
core, the bounded research evidence, the unresolved mathematical questions,
and the separation between exact process structure and approximate numerical
realization.

This report is explanatory. Normative engineering boundaries remain in
`AGENTS.md`, `SEMANTIC_SCOPE.md`, `PROGRAM_PROCESS_CORE.md`, the ADRs, and
`claims.toml`.

## Executive summary

Adva no longer treats a matrix, vector, scalar value, or manifold as the
native object of program geometry. Its native object is an open finite
program, written abstractly as `Prog`: a typed expression DAG with ordered
holes, explicit sharing and discard, explicit source and occurrence identity,
and retained construction history.

One checked program process has three coupled readings:

- **K**, construction: substitution, grafting, scope nesting, and dependency;
- **C**, causality: enabled events and forward development from a completed
  past;
- **F**, frontier: the organization of cuts separating that past from its
  future.

These are not three unrelated objects and are not three matrices. They are
three readings of one process. Scalar evaluation, differentiation, symbolic
coefficient extraction, matrix-like tables, projective actions, complex fixed
points, and spectra are observations compiled from that process under
additional policies.

The stable Rust kernel now derives certified causal cuts, certified
single-event cut advances, compiler-emitted nested graft traces, and exact
same-diagram program slices.  For downward-closed event sets `U` contained in
`V`, `ProgramSlice(P,U,V)` retains the original events in `V` minus `U`, both
cuts, changed boundary wires, unchanged through wires, internal events,
occurrences, history, and optional graft intersections.

Adjacent slices now compose exactly after input revalidation, literal
middle-cut agreement, and event conservation.  The constructed outer view is
required to equal the directly analyzed outer slice, and exact fixtures cover
identity units, three-segment associativity, graft links, and hidden discard
history. The independent diamond is now exhausted over all 5 causal pasts, 14
nested pairs, 30 nested triples, and 55 nested quadruples. Two distinct linear
schedules yield one canonical outer slice, proving that schedule path is extra
data rather than slice event order.

Python now exposes graft traces, slices, and exact composites as typed
read-only snapshots of Rust results and certificates. Python cannot construct
or submit a slice, frame, or certificate to the semantic kernel.

Crucially, this next phase is exact and finite. It requires no floating-point
comparison and no infinite-series truncation. Floating point and truncation
enter only in later observation layers such as numerical process exponentials
or resolvents. They must never control structural identities, cut membership,
scope membership, or certificates.

## 1. The ontological decision

### 1.1 Native object

An Adva program is an open, typed, finite computation with:

- an ordered input frontier of named holes;
- an ordered output frontier;
- a finite expression DAG;
- explicit `copy`, `discard`, `swap`, and identity operations;
- explicit operation events;
- stable source identities;
- stable occurrence identities and occurrence paths;
- exact wire lineage;
- construction and call history.

"Affine" in this report refers to explicit resource discipline: inputs are
consumed linearly unless the program explicitly invokes structural copy or
discard. It does not mean that the native program is a vector, an affine
space, or a module.

The same numerical function may be computed by different programs. Therefore
none of the following implications is valid without an explicit observation
policy and a certificate:

```text
same value        => same program
same differential => same program
same cut frontier => same history
same matrix shadow => same program
same spectrum     => same program
```

### 1.2 Holes and substitution

A function input frontier is interpreted as an ordered family of holes.
`ProgramTerm::Call` is finite simultaneous substitution:

1. each argument is itself lowered as a program;
2. its produced frontier is checked against the corresponding callee holes;
3. the finite callee body is grafted onto those wires;
4. no argument is implicitly shared;
5. the call remains visible in checked history.

This is program substitution, not application of an already evaluated value.
The current compiler emits a certified companion graft trace with deterministic
nested frames, separate argument and callee-body regions, ordered hole maps,
and exact boundary wires.  It does not add this provenance to stored version-one
diagrams.

### 1.3 Program and value

For a program `P` and an observation policy `Q`, write

\[
[P]_Q
\]

for the observed value. The subscript is essential. A scalar result, a
Jacobian, a symbolic expression family, a projective action, or a spectrum
forgets different parts of the native process.

An observation may be useful, faithful on a declared fragment, and precisely
certified without becoming the ontology.

## 2. One process and three readings

### 2.1 K: construction and grafting

K records:

- which argument programs fill which ordered holes;
- the nesting of substitution frames;
- explicit structural copy and discard;
- the partial order generated by data dependency;
- residual construction history not visible in a value.

A sequential evaluator chooses a linear extension of this partial order. The
schedule is not the construction order itself.

### 2.2 C: causal development

C chooses a downward-closed set of completed events. An event is enabled when
all of its direct predecessor events are complete. Advancing the event moves
the causal boundary forward and replaces the wires consumed by the event with
the wires it produces.

Independent enabled events may be scheduled in different orders. Equal final
values or equal final frontiers do not identify these histories.

### 2.3 F: cut organization

F reads the exact wires crossing from a completed causal past to its future.
Each crossing retains:

- the original `WireRef`;
- its unique consumer position;
- its occurrence lineage;
- the source attached to every occurrence.

A single cut is only a snapshot. The spatial reading required by the theory
is the organization of cuts and the program intervals between them.

### 2.4 What "time-space duality" may mean

The current defensible statement is:

> Construction dependency, causal advance, and cut nesting are readings of
> one checked program process. Forward scope organization and reverse cut
> organization are candidates for a covariant/contravariant correspondence.

The project has not proved a bijection between syntax scopes and causal cuts.
Such a bijection may fail:

- arbitrary causal cuts need not coincide with call boundaries;
- sharing may make a syntactic region nontrivial at its boundary;
- `discard` may hide an event from a frontier snapshot;
- independent events create cuts not selected by syntax nesting;
- parent and child graft-frame regions may overlap on the same events; and
- a zero-event call frame has no nonempty event-region intersection.

The compiler now retains enough graft information to test these failures.
Current evidence rules out a total frame-to-nonempty-slice bijection on PSC0;
a future correspondence must use extra boundary or syntax data or remain a
partial certified relation.

## 3. Current executable architecture

### 3.1 Rust authority

Rust is the sole semantic authority. The dependency direction is:

```text
adva-ir <- adva-lisp <- adva-python <- Python adapters and experiments
```

`adva-ir` owns serializable identities and result types. `adva-lisp` owns
parsing, linking, type checking, linear-use checking, lowering, validation,
evaluation, differentiation, causal-cut analysis, and certificate
construction. Python may adapt checked results but may not allocate or infer
semantic identities.

### 3.2 Exact stable objects

The stable core currently includes:

- `ProgramTerm` and finite module/function definitions;
- typed domain and codomain frontiers;
- `SharedProgramDiagram`;
- deterministic `SourceId`, `OccurrenceId`, and `OccurrencePath`;
- versioned operation specifications;
- explicit history and lineage;
- diagram validation artifacts;
- compilation, evaluation, and differentiation certificates;
- `CausalCut` and `CausalCutCertificate`;
- `CausalStep` and `CausalStepCertificate`;
- compiler companion `GraftTrace` and `GraftTraceCertificate`;
- `ProgramSlice` and `ProgramSliceCertificate`;
- `ProgramSliceCompositionArtifact` and
  `ProgramSliceCompositionCertificate`.

For a validated diagram and a completed node set `U`,
`analyze_causal_cut(P, U)` checks that `U` is downward closed and returns the
exact crossing wires. `advance_causal_cut(P, U, e)` checks that `e` is enabled
and records the before cut, after cut, consumed wires, and produced wires.
`analyze_program_slice(P,U,V)` checks nested pasts and records the exact event
interval, boundary changes, through wires, internal events, occurrences, and
history.  With compiler provenance it also links nonempty graft-frame region
intersections. `compose_program_slices(P,A,B)` revalidates adjacent inputs and
returns the exact canonical outer view with a composition certificate.

These judgments do not evaluate any scalar.

Rust tests additionally exhaust the independent three-event diamond over all
5 causal pasts, 14 nested pairs, 30 nested triples, and 55 nested quadruples.
They verify exact direct/composed equality and associativity throughout. The
two legal linear schedules remain different step paths but yield one canonical
outer slice; one path explicitly demonstrates that adjacent event vectors
cannot be composed by concatenation.

### 3.3 Current numerical realization

The executable scalar type is `Real`, realized as `f64` by evaluation and
forward differentiation. Rational constants are represented exactly in the
IR before numerical realization. Elementary functions such as `exp`, `sin`,
`cos`, and `log` are numerical at evaluation time.

The current evaluation certificate certifies the checked diagram, input
boundary, executed rules, and related structural obligations. It is not a
rounding-error, conditioning, overflow, underflow, NaN, or interval-enclosure
certificate. Current `f64` results must therefore be read as ordinary
numerical projections, not verified real-number values.

The following must never depend on `f64` equality or tolerance:

- whether a diagram is valid;
- whether a node is enabled;
- whether a completed set is downward closed;
- which wire crosses a cut;
- source or occurrence identity;
- lineage preservation;
- scope or frame membership;
- structural composition of finite slices.

### 3.4 Bounded research witnesses

Python research tests have established bounded evidence for:

- finite causal-open enumeration on selected diagrams;
- occurrence-decorated backward demand fields;
- expression-valued backward transport;
- exact unsimplified composition across nested cuts in selected fixtures;
- pointwise `exp` extension of the symbolic coefficient language;
- probe linearity in a declared finite chart;
- matrix-like coefficient tables derived from symbolic probe transport;
- agreement of those tables with a transpose reading of Rust's forward
  Jacobian at declared numerical inputs;
- real paraxial programs whose projective fixed-point equations have complex
  roots after observation.

These tests do not install stable probes, cut transport, matrices,
transposes, complex scalars, process exponentials, resolvents, spectra, or
objectification.

## 4. Exact structure versus floating point and truncation

### 4.1 Why the separation matters

There are three distinct questions:

1. **Structural identity:** are these the same nodes, wires, occurrences,
   scopes, and histories?
2. **Symbolic identity:** do two expressions agree under a declared exact
   equational theory or normal form?
3. **Numerical approximation:** do two realized quantities agree within a
   declared error model?

Conflating them would let a tolerance erase program history or let a finite
series approximation masquerade as a process theorem.

### 4.2 Four-layer separation

| Layer | Native data | Equality or judgment | Approximation allowed |
|---|---|---|---|
| Process structure | finite typed DAG, frames, cuts, slices, identities | exact Rust data and certificates | no |
| Symbolic observation | declared expression language | exact syntax or declared rewrite certificate | only if explicitly introduced |
| Numerical realization | `f64`, future complex or interval values | policy-relative error comparison | yes |
| Analytic completion | limits, series, process exponential, resolvent, spectrum | convergence and remainder certificate | necessarily |

The next phase belongs entirely to the first row.

### 4.3 Floating-point discipline

Numerical tests are legitimate when they test a numerical observation. They
are not evidence for structural equality unless an independent structural
certificate already supplies that equality.

Every future approximate observation must declare at least:

- scalar domain and precision;
- rounding or interval policy;
- absolute and relative error interpretation;
- conditioning assumptions;
- the exact checked program and observation policy being realized.

A failed tolerance comparison means that a numerical calibration failed. A
successful comparison does not create an equation cell or identify programs.

### 4.4 Finite truncation discipline

PSC0 programs, causal cuts, and program slices are finite. No truncation is
required to construct or compose them.

Truncation enters only after a later phase closes or repeats a process and
asks for an analytic completion. For example, a declared endotransport `K_P`
might admit chart-relative approximants

\[
C_P^{(N)}(t)
=
\sum_{n=0}^{N}\frac{t^nK_P^n}{n!}
\]

or, under an explicitly justified geometric-series condition,

\[
F_P^{(N)}(z)
=
\frac{1}{z}\sum_{n=0}^{N}\left(\frac{K_P}{z}\right)^n.
\]

Neither finite sum is definitionally the process exponential or resolvent.
An approximation certificate would have to record:

- the chosen process closure;
- observation chart and carrier;
- truncation order `N`;
- convergence assumptions;
- norm or error model, which is itself observation-relative;
- a checked or independently validated remainder bound;
- failure, success, or unknown convergence status.

For example, after choosing a normed numerical carrier, an exponential tail
may be bounded by a term of the form

\[
e^{|t|\lVert K_P\rVert}
\frac{(|t|\lVert K_P\rVert)^{N+1}}{(N+1)!},
\]

while a resolvent geometric tail requires
`q = ||K_P|| / |z| < 1` and may be bounded by

\[
\frac{1}{|z|}\frac{q^{N+1}}{1-q}.
\]

These are examples of chart-relative numerical obligations, not native
definitions. The core must never silently select the norm, chart, stopping
rule, or convergence threshold.

### 4.5 Complex completion

Complex values may naturally appear when a real observed program is completed
spectrally or projectively. That does not require the native finite program to
be defined over a foundational complex field.

Any future complex implementation must state whether it is:

- an exact algebraic extension;
- a symbolic root object;
- a floating-point complex realization;
- an interval or ball enclosure;
- a projective chart value.

These types must not be interchangeable.

## 5. The remaining structural gap

### 5.1 Retained substitution history and its limit

The compiler companion now retains:

- the parent frame of a nested call;
- the ordered region that produced each argument boundary;
- the exact callee-body region introduced by the call;
- the entry and exit boundary of the frame;
- the relationship between a scope path and causal cuts.

That data makes K comparable with C and F, but it also exposes a no-go result:
frame intersections can overlap, while a zero-event call frame has no nonempty
node-region intersection. A total scope-to-slice map therefore needs more than
event membership.

### 5.2 Exact intervals without chosen schedules

`ProgramSlice` now makes the program between nested cuts an exact object, and
adjacent slices compose with certificates, identity units, and associativity.

Frontier equality alone is insufficient. A region may execute internal
constant and discard events, or alternative independent schedules, without
changing the observed frontier. The process interval must retain those
events. Conversely, the outer interval does not retain which independent
linear schedule was selected; a path-sensitive construction must add that
data explicitly.

### 5.3 No stable bidirectional transport

Expression-valued backward transport exists only as bounded Python research.
There is no stable identity-preserving Rust `pullback`, no general forward
section transport, and no proof that the research rules compose for arbitrary
validated diagrams.

This transport must be built on exact program slices, not on matrix shadows.

## 6. Candidate common object: ProgramSlice

Let `P` be one validated finite program DAG, and let `U` and `V` be
downward-closed event sets with `U` contained in `V`. Define the candidate

\[
\operatorname{ProgramSlice}_P(U,V)
\]

as a view of the same program containing:

- the lower certified cut at `U`;
- the upper certified cut at `V`;
- every original event in the set difference \(V\setminus U\);
- lower wires consumed by those events;
- upper wires produced by those events;
- unchanged through-wires present at both boundaries;
- internal events with no final boundary effect;
- original node, wire, source, occurrence, path, and lineage identities;
- any grafting frames intersecting the slice.

It is an open subprogram of `P`, not a function from numerical input values to
output values and not a matrix between two vectors.

### 6.1 Three readings of the slice

- K reads its intersecting graft frames and hole bindings.
- C reads its event dependency order and enabled advances.
- F reads its lower/upper cuts and their reverse organization.

The implementation should introduce one common structural object, not three
copies of the data named K, C, and F.

### 6.2 Candidate exact laws

For causal pasts `U <= V <= W` in one unchanged diagram:

1. **Identity**

   \[
   \operatorname{Slice}(U,U)=\operatorname{Id}_{\partial U}.
   \]

   The identity slice has no events but retains its boundary and through-wire
   identities.

2. **Event conservation**

   \[
   E_{U,W}=E_{U,V}\;\dot\cup\;E_{V,W}.
   \]

3. **Exact composition**

   \[
   \operatorname{Slice}(U,W)
   =
   \operatorname{Slice}(V,W)
   \circ
   \operatorname{Slice}(U,V),
   \]

   after a canonical composition that preserves the original IDs and performs
   no recompilation or relabeling.

4. **Boundary matching**

   The upper cut of `Slice(U,V)` is literally the lower cut of
   `Slice(V,W)` in the same diagram.

5. **Lineage preservation**

   Composition neither creates nor identifies sources or occurrences. Copy
   and discard remain explicit events.

6. **Associativity**

   Composition through four nested causal pasts is independent of
   parenthesization while retaining the same original process data.

These are design obligations until implemented and certified.

## 7. Candidate grafting record

A research `GraftTrace` should be emitted during compilation, before inlining
has erased scope boundaries. Each `GraftFrame` should at least record:

- a deterministic frame ID and scope path;
- optional parent frame;
- caller and callee qualified names;
- ordered callee holes;
- the argument-producing regions bound to those holes;
- the callee-body region introduced by the call;
- entry and exit wires;
- nested child frames;
- links to original history events.

The distinction between argument regions and callee-body regions must remain
explicit. Treating the whole call as one undifferentiated node set would hide
the very substitution process the trace is intended to preserve.

The first implementation should be a certified companion artifact. It should
not change the meaning of serialized `adva.ir` version 1. Promotion into a new
IR version requires evidence that the frame invariants are sufficient and
stable.

## 8. Counterexamples that must guide the design

The theory must survive at least the following finite cases:

1. an identity program with no operation event;
2. explicit copy followed by two distinct consumers;
3. explicit discard whose execution leaves no output wire;
4. a zero-input constant introduced inside a slice;
5. two independent enabled events with alternative schedules;
6. a wire that crosses both lower and upper cuts unchanged;
7. nested calls with ordered multi-output arguments;
8. two programs or slices with equal scalar values but different histories;
9. two completed pasts with equal frontier observations but different event
   content;
10. a call whose argument program contains its own nested call and explicit
    copy.

Any proposed representation that cannot state the difference in cases 3, 5,
8, or 9 is too extensional for the project.

## 9. Risk register

### Risk A: treating scope nesting and cut nesting as a proven bijection

Mitigation: implement both structures and search for finite counterexamples
before choosing theorem language.

### Risk B: storing only frame node membership

Node sets alone may not distinguish argument production, callee entry, body,
and exit. Mitigation: retain ordered boundary maps and region roles.

### Risk C: materializing slices by recompilation

Recompilation allocates fresh semantic identities and destroys literal
same-diagram comparison. Mitigation: represent slices as identity-preserving
views first.

### Risk D: confusing frontier equality with process equality

Discarded or internal events may be invisible at the boundary. Mitigation:
retain the complete event difference \(V\setminus U\) in every slice.

### Risk E: allowing numerical evidence to authorize structure

Tolerance-based tests cannot prove scope, identity, or composition. Mitigation:
make the next phase entirely independent of evaluation.

### Risk F: premature IR versioning

The correct frame representation is not yet known. Mitigation: begin with a
compiler-produced companion artifact and explicit promotion criteria.

### Risk G: premature analytic completion

Series truncations may look convincing while hiding an undefined carrier,
norm, or residual. Mitigation: defer process exponentials and resolvents until
exact slice transport exists.

## 10. Terminology and no-go boundaries

- `module` in current code means a Lisp namespace and linking unit. It does
  not introduce algebraic module theory.
- `Real` means the current declared scalar interface; its executable
  realization is `f64`.
- `exp` is a pointwise builtin operation, not a process exponential.
- a matrix-like table is a chart-organized coefficient observation, not the
  program.
- a cut is an occurrence-decorated open boundary, not a vector.
- a reverse dependency traversal is not reversed physical time.
- equal values, gradients, matrices, or spectra do not create an equation
  cell.
- complex roots observed from a real program do not establish a foundational
  complex program field.
- no current result establishes a manifold structure on program space.

## 11. Current conclusion

The first exact finite checkpoint now passes:

> Program intervals between nested causal cuts compose exactly in one
> unchanged occurrence-aware DAG, preserving every original identity and
> hidden internal event, with exact units and associativity.

The independent-diamond exhaustion strengthens this result but also isolates
an essential distinction: a slice is an interval of a partial order, whereas
a chosen linear schedule is extra path data. It does not establish that
substitution-scope nesting and reverse cut nesting are the same structure.
Graft links remain overlapping and partial, and zero-event frames prevent a
total frame-to-nonempty-slice map.

The read-only Python exposure of the stable Rust artifacts is now complete.
The next mathematical obligation is to identify the minimum extra
decorated-boundary data needed for a contravariant synthesis map `P*`, or to
prove by a finite counterexample that the proposed map must be weakened
further. This obligation does not depend on floating point, analytic
truncation, complex completion, or spectral factorization.

## Required companion reading

- `AGENTS.md`
- `ARCHITECTURE.md`
- `SEMANTIC_SCOPE.md`
- `PROGRAM_PROCESS_CORE.md`
- `adr/0001-rust-semantic-authority.md`
- `adr/0004-frontier-before-compiled-presentations.md`
- `adr/0006-program-process-before-projections.md`
- `claims.toml`
- `NEXT_PHASE_PROGRAM_SLICES.md`
- `RESEARCH_ENGINEERING_AGENDA.md`
