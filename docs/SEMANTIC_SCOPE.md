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
  event conservation, direct equality, and finite associativity.

## Explicitly excluded

- reconstruction of graft provenance for stored or imported diagrams;
- local term binders, alpha equivalence, arbitrary graph-context
  substitution, and substitution across unlinked program stores;
- recursion and cyclic modules;
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

Search-style APIs, when introduced, must return `Yes`, `No` with a checked
countercertificate, or `Unknown`. Timeout and exhaustion are `Unknown`.
