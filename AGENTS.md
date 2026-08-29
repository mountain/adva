# Agent instructions

Before modifying semantic code, read:

1. `README.md`
2. `docs/ARCHITECTURE.md`
3. `docs/SEMANTIC_SCOPE.md`
4. `docs/claims.toml`
5. relevant ADRs under `docs/adr/`

## Authority and dependency direction

- Rust is the sole authority for types, terms, diagrams, sources, occurrences,
  histories, cells, observers, calculus, and certificates.
- Python may adapt checked IR to SymPy, NumPy, SciPy, plotting, search, or
  experiments. Python must not create or identify semantic identities.
- The versioned JSON IR is the language-independent interchange boundary.
- `process-geometry` supplies theory and independent regression oracles. Do not
  silently copy its experimental claims into the stable API.

## Ontology discipline

Keep `TypedFrontier`, `DomainFrontier`, `CodomainFrontier`, `ProgramTerm`,
`SharedProgramDiagram`, `History`, `Value`, `Occurrence`, `Source`,
`ProjectiveDevelopment`, `Probe`, `ObservationPolicy`,
`PredicateRegion`, `ProofObject`, `DirectedRewrite`, `EquationCell`,
`CoherenceCell`, and `ObjectificationWitness` distinct.

`SourceId` and `OccurrenceId` must be explicit, deterministic, stable under
serialization, and independent of memory addresses, object identity, value
equality, structural hashing, or accidental AST sharing.

Sharing is a program operation whose result has two ordered output ports on a
`TypedFrontier`; it is never a type modifier or host-language alias.
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
