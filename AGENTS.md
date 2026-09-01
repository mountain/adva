# Agent instructions

Before modifying semantic code, read:

1. `README.md`
2. `docs/ARCHITECTURE.md`
3. `docs/SEMANTIC_SCOPE.md`
4. `docs/PROGRAM_PROCESS_CORE.md`
5. `docs/TECHNICAL_REPORT_PROGRAM_PROCESS_CORE.md`
6. `docs/NEXT_PHASE_TRIADIC_OBSERVER_TRANSITIONS.md`
7. `docs/claims.toml`
8. relevant ADRs under `docs/adr/`

Before starting or proposing a new research or engineering phase, also read
`docs/RESEARCH_ENGINEERING_AGENDA.md`. Its dependency order is part of the
project plan. The exact `GraftTrace` and `ProgramSlice` phase is complete. The
currently active implementation task is the bounded transition companion in
`docs/NEXT_PHASE_TRIADIC_OBSERVER_TRANSITIONS.md` unless a checked
counterexample or an explicit project decision changes it.

## Authority and dependency direction

- Rust is the sole authority for types, terms, diagrams, sources, occurrences,
  histories, cells, observers, calculus, and certificates.
- Python may adapt checked IR to SymPy, NumPy, SciPy, plotting, search, or
  experiments. Python must not create or identify semantic identities.
- The versioned JSON IR is the language-independent interchange boundary.
- External or stored diagrams enter semantic code only through the Rust
  `validate_diagram` / `import_diagram_json` boundary. Serde decoding alone is
  not authorization.
- `process-geometry` supplies theory and independent regression oracles. Do not
  silently copy its experimental claims into the stable API.

## Ontology discipline

Keep `TypedFrontier`, `DomainFrontier`, `CodomainFrontier`, `ProgramTerm`,
`SharedProgramDiagram`, `CausalCut`, `CausalStep`, `History`, `Value`,
`Occurrence`, `Source`,
`ProjectiveDevelopment`, `Probe`, `ObservationPolicy`,
`PredicateRegion`, `ProofObject`, `DirectedRewrite`, `EquationCell`,
`CoherenceCell`, and `ObjectificationWitness` distinct.

`SourceId` and `OccurrenceId` must be explicit, deterministic, stable under
serialization, and independent of memory addresses, object identity, value
equality, structural hashing, or accidental AST sharing.

Sharing is a program operation whose result has two ordered output ports on a
`TypedFrontier`; it is never a type modifier or host-language alias.
Treat a function boundary as an ordered family of holes and
`ProgramTerm::Call` as the current finite simultaneous-substitution mechanism.
Do not describe finite lowering as value application: argument programs are
grafted before evaluation. The flat call history is not yet a complete
nested-substitution carrier.
`DomainFrontier` and `CodomainFrontier` orient a 1-cell boundary; they do not
stand for the temporal and spatial sides of the semantic duality. No frontier
type may be presented as an implemented tensor product. Value equality and
observational equivalence never authorize contraction, memoization, CSE, or a
cell.

For `D: DomainFrontier -> CodomainFrontier`, reserve `D*` for a future
contravariant observer pullback. Do not implement it as a `ProgramTerm`,
boundary swap, inverse, dagger, involution, or unconditional matrix transpose.
Any executable pullback must be derived from a checked diagram and return a
certificate.

Directed normalization steps, invertible equation cells, and coherence cells
use different Rust types. Search exhaustion produces `Unknown`, never a proof
of nonexistence.

`CausalCut` and `CausalStep` are derived readings of a checked
`SharedProgramDiagram`. They must reuse exact `WireRef`, source, occurrence,
and lineage data. Python may request these Rust judgments but must not
reconstruct or authorize them.

Triadic domain labels are observer-policy metadata over exact input-source
fibres. They must not be installed as wire types or inferred from scalar
values. Opposite-pair views may overlap, while source-free and hidden
incidences remain in an explicit residual. A triadic observer transition is a
view of a `ProgramSlice`; it is not an active program transformation,
reversible transport, specialization result, or proof object.

## Scope

Stable code currently covers the binder-free, finite, linear core. Keep
objectification, generic higher proof transport, HPC, sheaf/stack semantics,
full abstraction, and physical interpretations out of the stable API.

All semantic transformations return a result together with a certificate.
Tests are evidence for the declared finite scope, not unrestricted theorems.

## Operation changes

Stable Lisp builtins are declared through the Rust `OperationSpec` registry.
Do not add separate parser, type-checker, evaluator, differential, or lineage
name tables. A new operation must declare its versioned boundary, exact
parameters, surface visibility, scalar differential realization, and explicit
`LineageRule`, with a registry completeness test. Changing an existing rule is
an IR-versioning decision, not an in-place reinterpretation.
