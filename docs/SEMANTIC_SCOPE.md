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
