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
- explicit source, occurrence, path, and history data;
- distinct directed rewrite, equation, and coherence types;
- versioned JSON envelopes and certificate types.

### `adva-lisp`

- S-expression reader without host evaluation;
- `module`, `import`, `export`, `def`, `fn`, and `call`;
- module graph validation and cycle rejection;
- linear use checking and explicit structural operations;
- typed lowering from `ProgramTerm` to `SharedProgramDiagram`;
- builtin operation registry shared by evaluation and differentiation;
- deterministic source and occurrence allocation.

### `adva-python`

- PyO3 classes wrapping linked modules and checked diagrams;
- JSON and certificate access;
- typed scalar evaluation and gradients.

### `python/adva`

- ergonomic typed facade;
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

## Operation library

Every builtin operation has one Rust definition of:

- input and output boundary rules;
- scalar realization;
- local forward differential;
- source and occurrence transport.

The first registry contains `id`, `tensor`, `swap`, `copy`, `discard`,
constants, `add`, `mul`, `scale`, `neg`, `sin`, `cos`, `exp`, and `log`.
Structural operations are diagram nodes, not Rust or Python aliases.

## Serialization

The interchange format is JSON with schema identifier `adva.ir` and version
`1`. IDs are written as data. They are never reconstructed from memory address,
Python `id()`, Rust pointer identity, hashes, values, or incidental object
sharing. The repository also publishes a JSON Schema under `schemas/`.

Binary encoding is intentionally deferred until profiling justifies it. A
future binary codec must preserve the same ontology and schema versioning.

## Stable versus research code

The stable slice contains finite modules, terms, diagrams, evaluation,
differentiation, explicit source partitions, and lossless serialization.

Objectification witnesses, higher cells beyond their data boundaries,
projective observers, generic proof transport, and compiler optimizations that
consume objectification certificates remain research targets. They must not be
simulated with booleans or Python callbacks.

