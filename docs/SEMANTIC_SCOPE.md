# Semantic scope: PSC0 bootstrap

This repository begins with a finite, binder-free, linear core inspired by the
Typed Sharing Diagram Calculus. `PSC0` is an engineering scope label, not a
claim that the surrounding calculus has been completely presented.

## Included

- immutable typed module and function terms;
- finite acyclic module linking;
- orientation-free `TypedFrontier` values and distinct `DomainFrontier` and
  `CodomainFrontier` function boundaries;
- explicit `id`, composition by typed `call`, ordered `frontier`, `swap`,
  `copy`, and `discard`;
- finite named simultaneous substitution: call arguments are open programs
  grafted into a callee's checked ordered input holes;
- deterministic compiler-emitted nested graft frames with separate argument
  regions, ordered hole bindings, callee-body regions, and boundary wires;
- selected real arithmetic operations;
- deterministic source and occurrence paths;
- lossless history and JSON round-trip;
- checked semantic import for canonical finite diagrams with empty rewrite
  traces;
- scalar realization and forward differentials;
- one versioned Rust declaration for each builtin's boundary, realization,
  differential, and lineage rule;
- value and source/history observations as different interfaces;
- Rust-certified downward-closed causal cuts and one-enabled-event frontier
  replacement over validated finite diagrams;
- exact same-diagram `ProgramSlice` analysis between nested causal pasts,
  including through wires, internal events, and optional graft intersections;
- exact composition of adjacent canonical slices, including identity units,
  event conservation, direct equality, and finite associativity;
- exhaustive exact slice-law tests on all cuts and nested intervals of one
  independent three-event causal diamond, with distinct schedule paths kept
  separate from the common canonical interval;
- read-only Python inspection of Rust-owned graft traces, slices, and exact
  composites, without accepting reconstructed semantic artifacts from Python.
- Rust-owned `TriadicObserverTransitionV0` companions for exactly three input
  sources assigned once each to construction, space, and time, with
  occurrence-level opposite-pair cut views, source-free residual wires,
  copy-path ancestry, and exact adjacent relation composition.
- read-only Python invocation and inspection of those exact Rust triadic
  transition and composition artifacts.

## Explicitly excluded

- reconstruction of graft provenance for stored or imported diagrams;
- local term binders, alpha equivalence, arbitrary graph-context
  substitution, and substitution across unlinked program stores;
- recursion and cyclic modules;
- stable feedback, event re-enabling, and semantic epoch allocation;
- implicit contraction, aliases, memoization, and CSE;
- merge or source identification;
- normalization as an in-place mutation;
- deriving equation cells from equal values or equal observations;
- objectification search or stable objectification APIs;
- generic proof transport or a choice among `Cat`, `Gpd`, and stratified
  alternatives;
- full HPC, sheaf/stack semantics, universality, faithfulness, fullness, and
  full abstraction;
- enumeration as a stable topology API, cross-diagram slice composition, probe
  pullback, process exponentials, resolvents, characteristic factorization,
  and program spectra;
- physical interpretations of curvature, mass, or spacetime.
- intrinsic construction/space/time wire types, arbitrary-domain observer
  policies, Raw111 bracket trees or typed apertures as stable ontology,
  stable open/close operations, right-to-forget rules, active triadic
  normalization, reverse-dual proof search, specialization, interpreter
  semantics, and universal computation.

## Bounded research companion

The Rust `adva-witness` crate may check the corrected six initial declarations,
finite signed formation ledgers, pure add/multiply expression witnesses, and
linear three-hole template instances. It reuses verified proof artifacts by a
nonsemantic content key while every instance retains a fresh instance ordinal
and explicit bindings to existing Rust-owned sources and occurrences. It does
not extend `adva.ir` version 1, allocate semantic identity, add a stable scalar
type, infer copy from repeated variables, create equation cells, or define the
general program constructor or interpreter. A formed template may derive its
three bindings from one compiler-owned `CompilationArtifact` and one certified
ordered graft frame. The adapter requires singleton lineage at each entry wire
and retains the compilation certificate, graft certificate, frame identifier,
scope path, caller, and callee; it does not guess a source when an entry wire
has empty or merged lineage. The same research crate may check a neutral
carrier grammar with the input labels `subject/method/object`, edge labels
`compute/verify/learn`, and output labels `history/result/evidence`.
Computation rejects open subject or object frontiers; verification permits
only an exactly declared or explicitly discharged frontier; learning returns a
finite partial fill proposal and retains replacement subholes. These
research-local frontier coordinates are not stable semantic holes, logical
obligations, or apertures. The checker performs no execution, proof replay,
learning synthesis, or feedback. A separate research-only `.adva` document
codec may persist neutral carriers as graph vertices and
`compute/verify/learn` as transition-frame labels. Each frame names exactly
three input carrier references and retains exactly three output positions;
the output positions are either all ready or all recorded. Named entry points
select frames, and a later frame may reuse earlier recorded outputs through
the same document-local carrier references. The Rust boundary checks schema,
version, canonical table order, reference resolution, cache-coordinate
nonemptiness, canonical frontiers, exact boundary slot use, and every mechanism
formation judgment, then returns a digest and load certificate. It is not a
stable format promotion, does not reinterpret Lisp source, does not resolve
cached artifacts, and does not certify that recorded outputs arose from a
mechanism execution.

The research crate may also check the formation of two explicitly profiled
relation cells. `Q4` admits only the `ab => ba` interchange word with a trace
monoid process lift and Klein-four Coxeter shadow. `M6` admits only the
`aba => bab` braid word with a positive braid-monoid lift and `S3` shadow.
Both raw paths remain present. Open boundaries require an explicit residual
cache reference; filled boundaries cite one directional witness and may retain
a residual. The returned certificate covers formation and reference presence
only: it does not replay the witness, authorize reverse transport, prove path
or program equality, implement conjugacy, or extend `AdvaDocumentV0`. Candidate
carrier commands (`join/cut/close`) and traversal commands (`step/run`) remain
outside this relation checker and have not been promoted to CLI syntax.

`adva.research.ResearchMachineV0` may orchestrate finite runs over the included
Rust artifacts. Its interpretation cells retain exact interfaces, slices,
step certificates, and schedule order. Its optional frontier-matched replay
repeats one static checked experiment and records only nonsemantic epoch
coordinates. This is executable research evidence, not an extension of PSC0
semantics. Exact-cut return for a nonempty interval remains unrepresentable;
fuel exhaustion returns partial evidence and never proves nonexistence.

`adva.research.MultiHoleThroughMachineV0` may additionally select one certified
call frame, classify its ordered holes by two opposite source domains, and
propose a finite relation over a declared upper-cut-wire quotient.  Its
incidence numbers only index unchanged Rust artifacts, its layered report is
not a certificate, and its complete `ProgramSlice` remains attached.  It does
not authorize a stable through object, forgetting, active normalization,
specialization, relation composition, logic, or universality.

`adva.triangular_research.TriangularThroughMachineV0` may derive three such
local angle relations from one checked six-hole configuration and compare
declared legal schedules on the same compiled function.  Its global-closure
record is an obstruction: same-source copy siblings remain distinct
occurrences, so no connector is inferred and the raw circular composite stays
unrepresentable.  The adapter authorizes neither sibling identification nor a
stable triangle, connector, closure, or confluence law.

`adva.connector_research.ConnectorCalibrationMachineV0` may compare diagonal
occurrence identity, a test-local symmetric relation between exact direct copy
siblings, and the many-to-one projection to checked source identity.  A finite
comparison relation may close while retaining both occurrences; source
projection may also close after forgetting their distinction.  Neither result
is a semantic connector, copy inverse, contraction, `ProvenanceHide`,
right-to-forget judgment, circular execution, or Rust certificate.

`adva.characteristic_research.DistributivityCharacteristicMachineV0` may
compare two separately compiled three-input scalar programs through a bounded
exact rational-polynomial feature.  Each program retains its unchanged Rust
IR, triadic observer transition, three opposite-pair relations, compiler graft
presentation, complete `ProgramSlice`, identities, occurrences, and history.
The learning readout may report task-relative observational equality; the
proof readout may attach one bounded normalization-span witness.  Neither
readout identifies programs, creates an `EquationCell`, authorizes
provenance erasure or a stable right to forget, proves full learning/proof
self-duality, or extends Rust semantics.

`adva.hole_research.HoleOpenCloseMachineV0` may read an existing through
candidate as one typed aperture with a finite observed filling fibre, or read
the three local triangular interfaces as the presentation `{}[]()`.  Closing
selects only an existing relation element, refuses implicit choice on a
multivalued fibre, and retains every alternative and the complete
`ProgramSlice`.  Reopening retains the selected filling and close/open trace.
The adapter creates no semantic hole identity, vocabulary, singularity,
forgetting permission, active normalization, open logic, or Rust certificate.


`adva.historical_character_research.HistoricalDistributivityMachineV0` may
package the proved bounded distributivity artifact as one research-local
historical character with a polynomial scope, both original residuals, and an
occurrence-observer reopen handle. It may propose fresh finite typed
variable-permutation and multiplicative-context instances; every generated
program pair is sent through the existing Rust-backed checks and retains fresh
checked names, source text, substitution provenance, and both instance
residuals. Occurrence refinement may re-expose the explicit copy distinction
without refuting the common polynomial law. This adapter is not a Rust
certificate or native specializer and authorizes no semantic identity,
equation cell, source quotient, provenance erasure, fixed infinite family,
deck transformation, hyperbolic lift, logic, or universality.


## Equality interfaces

The initial core distinguishes:

1. definitional equality of immutable IR;
2. realized value equality for declared inputs;
3. observational equivalence under a named policy;
4. explicit-cell equivalence, which requires an `EquationCell` value.

Only the first two are executable in the bootstrap. Observational result types
are present for K1/K2 calibration. No interface lifts an observation back to a
cell.

## Certificates

Compilation and module linking return a `CompilationCertificate`.
Compiler-produced artifacts additionally carry a `GraftTraceArtifact` whose
certificate checks deterministic frame identity, nesting, regions, hole
bindings, boundary maps, and call-history links. It does not certify an
observer pullback or the factorization `T = P S P*`. `ProgramSliceArtifact`
separately certifies nested causal pasts, exact event difference, boundary and
through-wire partitions, internal-event retention, original identities,
lineage, and optional graft consistency. `ProgramSliceCompositionArtifact`
certifies revalidated inputs, middle-boundary agreement, exact event
partition, original identities, lineage, and equality with the direct outer
slice. Evaluation and forward differentiation return their own certificates. Semantic JSON
import returns a distinct `DiagramValidationCertificate`; decoding alone does
not. A certificate says only what its fields and scope record. It does not
certify a general theorem.

`TriadicObserverTransitionCertificateV0` checks one total three-source policy,
exact cut-incidence partitions, occurrence ancestry, preservation of the
complete embedded slice residual, and optional graft consistency.
`TriadicObserverTransitionCompositionCertificateV0` separately checks input
revalidation, policy and middle-observation agreement, exact slice
composition, finite ancestry-relation composition, and equality with the
direct outer transition. Neither certificate authorizes forgetting, bracket
normalization, a proof judgment, or a residual executable program.

Search-style APIs, when introduced, must return `Yes`, `No` with a checked
countercertificate, or `Unknown`. Timeout and exhaustion are `Unknown`.
