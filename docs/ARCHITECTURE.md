# Architecture

## Dependency direction

```text
adva-ir  <-  adva-lisp  <-  adva-python  <-  Python adapters
   ^              ^
   |              |
schema       semantic kernel
```

`adva-ir` contains immutable, serializable ontology. `adva-lisp` owns parsing,
module linking, type checking, explicit sharing, lowering, evaluation,
differentiation, observations, and certificate construction. `adva-python`
exposes opaque checked objects through PyO3. Pure Python modules adapt those
objects to external libraries.

No arrow points back from Python into semantic construction. External-library
results are numerical realizations or candidate data, never new Rust
judgments.

## Crates

### `adva-ir`

- language-independent module and term IR;
- typed frontiers and qualified names;
- `SharedProgramDiagram`;
- compiler-emitted nested graft-trace companion types;
- causal-cut, single-event, and exact program-slice result types;
- bounded triadic cut-observation and observer-transition companion types;
- explicit source, occurrence, path, and history data;
- distinct directed rewrite, equation, and coherence types;
- versioned JSON envelopes and certificate types.

### `adva-lisp`

- S-expression reader without host evaluation;
- `module`, `import`, `export`, `def`, `fn`, and `call`;
- module graph validation and cycle rejection;
- linear use checking and explicit structural operations;
- typed lowering from `ProgramTerm` to `SharedProgramDiagram`;
- deterministic nested graft traces retained beside compiler-produced diagrams;
- finite boundary substitution through checked module calls;
- certified causal-cut and enabled-event analysis over checked diagrams;
- exact same-diagram program-slice analysis between nested causal pasts;
- certificate-bearing exact composition of adjacent program-slice views;
- certificate-bearing three-domain opposite-pair readings and exact adjacent
  observer-transition composition;
- builtin operation registry shared by evaluation and differentiation;
- deterministic source and occurrence allocation.

### `adva-python`

- PyO3 classes wrapping linked modules and checked diagrams;
- JSON and certificate access;
- read-only Rust-derived graft-trace, program-slice, and exact-composite
  snapshots;
- typed scalar evaluation and gradients.

### `python/adva`

- ergonomic typed facade;
- frozen inspection views over Rust-owned graft and slice artifacts;
- SymPy conversion;
- NumPy ufunc-style callables;
- SciPy objective/Jacobian adapters.

## Module mechanism

A module has an explicit name, imports, exports, and function definitions.
Imports name a module and exported symbols; there is no wildcard import in the
initial core. A function parameter list and result frontier are its type
boundary. Calls are resolved and type checked before lowering.

Lowering inlines the called body only as a finite representation technique. A
`HistoryEvent::Call` remains in the diagram, so inlining does not make module
history definitionally invisible. Recursive calls and cyclic module imports
are rejected until guarded recursion obtains its own semantics.

The inputs of a function are its ordered open holes. A call lowers each
argument as a program under the caller's linear resource scope, checks the
resulting frontier against those holes, and only then grafts the finite callee
body. This is PSC0's bounded substitution mechanism. It is not host-language
value application or a local binder calculus.

A compiler-produced `CompilationArtifact` also carries a checked `GraftTrace`
companion. Its deterministic frames retain parent/child nesting, exact
argument and callee-body node regions, ordered hole bindings, boundary wires,
and links to flat call-history events. Syntax argument regions remain distinct
from flattened hole bindings because an argument can produce zero or multiple
wires. Stored or externally imported diagrams do not acquire this compiler
provenance retroactively. A frame boundary is a sub-boundary of the whole DAG,
not automatically a whole causal cut.

## Native process and cut analysis

The operation dependency DAG has a causal reading and a cut reading.
`analyze_causal_cut` accepts a set of completed operation nodes, verifies that
it is downward closed, and returns the exact `WireRef` values crossing from
that past to its future. `advance_causal_cut` verifies one enabled event and
returns the frontier wires it consumes and produces.

All analyses first revalidate the diagram and return Rust certificates.
`analyze_program_slice(P,U,V)` additionally requires nested causal pasts and
retains the exact events in `V` minus `U`, changed lower and upper boundaries,
unchanged through wires, and internal events invisible at the upper frontier.
Optional graft links are revalidated compiler provenance and may overlap; they
are not an event partition or a frame/cut bijection.  Adjacent composition
revalidates both input views, checks the literal middle cut and event union,
rebuilds the outer view in original diagram order, and requires equality with
the direct outer slice. Exact tests exhaust the full five-cut lattice of one
independent three-event diamond, including all nested triples and quadruples.
The two legal schedules retain distinct step paths while yielding the same
canonical outer slice; schedule order is therefore not stored as slice event
order.

These analyses preserve source and occurrence lineage without evaluation.
They do not assert a topology object, an observer pullback, equality of
alternative schedules, or a coherence cell.

The first bounded observer companion is
`TriadicObserverTransitionV0`. An explicit policy assigns exactly three input
positions to construction, space, and time; Rust derives the corresponding
source map from the checked initial cut. Each endpoint cut is expanded into
occurrence-level incidences. The view for one role exposes the other two source
fibres, while own-role incidences and source-free wires remain explicit. Lower
and upper incidences are related by unchanged source identity and checked
occurrence-path ancestry. Adjacent views compose only after both embedded
`ProgramSlice` values and the finite ancestry relation compose exactly.

This companion does not type internal wires as construction, space, or time.
It is an observer projection of one exact process interval, not an active
program rewrite, reversible transport, specialization result, or proof.

The Python boundary exposes these artifacts only by invoking Rust and decoding
the returned result/certificate JSON. Adjacent composition accepts three pasts
and derives both input slices inside Rust; no Python-constructed slice, frame,
or certificate is admitted as semantic input. Imported version-one diagrams
still have no graft trace.

The theoretical dependency and promotion gates are specified in
[`PROGRAM_PROCESS_CORE.md`](PROGRAM_PROCESS_CORE.md) and
[ADR 0006](adr/0006-program-process-before-projections.md).

## Operation library

Every builtin operation has one Rust definition of:

- namespace, name, version, and surface visibility;
- exact parameter schema;
- input and output boundary rules;
- scalar realization;
- local forward differential;
- source and occurrence transport.

The first registry contains `id`, `swap`, `copy`, `discard`, constants, `add`,
`mul`, `scale`, `neg`, `sin`, `cos`, `exp`, and `log`. Structural operations
are diagram nodes, not Rust or Python aliases. `frontier` is deliberately not
an operation: it assembles an ordered typed open boundary without claiming a
tensor-product semantics.

The IR represents that boundary with an orientation-free `TypedFrontier` and
distinct `DomainFrontier` and `CodomainFrontier` orientations. For a future
observer semantics, `D*` runs contravariantly from codomain probes to domain
probes. The executable spelling will be `pullback`, not a Lisp program term;
it must be derived from checked diagram data and accompanied by a certificate.

Polynomial-like carriers and matrix-like transports are distinct compiled
presentations, not replacements for this boundary constructor. They remain
chart-, basis-, observer-, and certificate-relative construction targets; see
[ADR 0004](adr/0004-frontier-before-compiled-presentations.md).

The parser, typed lowering, evaluator, and forward differential all resolve the
same `OperationSpec`. Stored IR is checked against the registry again before
execution, so changing a serialized node boundary cannot silently select a
different realization. Differential certificates record versioned rule IDs
such as `adva.builtin:mul@1`, rather than unqualified names. Adding or changing
a builtin version is governed by
[ADR 0003](adr/0003-single-operation-registry.md).

## Serialization

The interchange format is JSON with schema identifier `adva.ir` and version
`1`. IDs are written as data. They are never reconstructed from memory address,
Python `id()`, Rust pointer identity, hashes, values, or incidental object
sharing. The repository also publishes a JSON Schema under `schemas/`.

Decoding and semantic import are deliberately separate. The Rust Lisp kernel
rechecks graph topology, operation boundaries, linear frontier use, occurrence
paths, source-preserving copy history, and the final codomain before returning
a `DiagramValidationArtifact`. Evaluation repeats this integrity check. Python
can load stored diagrams only through this Rust boundary; see
[ADR 0005](adr/0005-checked-diagram-import.md).

Binary encoding is intentionally deferred until profiling justifies it. A
future binary codec must preserve the same ontology and schema versioning.

## Stable versus research code

The stable slice contains finite modules, terms, diagrams, compiler-emitted
certified nested graft frames, evaluation, differentiation, explicit source
partitions, certified finite causal cuts, single-event frontier replacement,
exact program slices and adjacent composition, and lossless serialization.
It also contains the bounded version-zero triadic observer-transition
companion over exact three-source input policies.

Objectification witnesses, higher cells beyond their data boundaries,
projective observers, generic proof transport, and compiler optimizations that
consume objectification certificates remain research targets. They must not be
simulated with booleans or Python callbacks.
