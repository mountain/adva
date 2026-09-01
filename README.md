# Adva

Adva is a tool for typed symbolic computation and program geometry. Its native
engine is a small modular Lisp implemented in Rust. Rust owns typing, explicit
sharing, source and occurrence identity, history, calculus, certificates, and
the versioned intermediate representation. Python is an adapter layer for
scientific computing and visualization.

The repository implements ideas developed in `process-geometry`, but it is not
the theory repository. Mathematical claims remain scoped and registered; the
tool does not turn research targets into stable API promises.

## Initial executable slice

- immutable `ProgramTerm`, `TypedFrontier` with distinct `DomainFrontier` and
  `CodomainFrontier` orientations, module IR, and `SharedProgramDiagram`;
- explicit `copy`, `discard`, `swap`, `id`, ordered `frontier` construction,
  arithmetic and elementary unary operations;
- stable serializable `SourceId`, `OccurrenceId`, `OccurrencePath`, and
  `History`;
- Rust module parsing, imports, exports, linking, and typed lowering;
- compiler-emitted certified `GraftTrace` companions retaining nested call
  frames, argument regions, ordered hole bindings, and callee-body regions;
- a single versioned Rust operation registry shared by parsing, typed lowering,
  lineage transport, evaluation, and forward differentiation;
- scalar evaluation and forward differential, each with a certificate;
- JSON IR round-trips with an explicit schema version;
- semantic diagram import in Rust with graph, linear-use, occurrence, source,
  history, and boundary certificates;
- Rust-certified completed causal cuts and single-event frontier replacement,
  derived without evaluating or rebuilding checked wire lineage;
- exact certified `ProgramSlice` intervals retaining changed boundaries,
  unchanged through wires, internal events, occurrences, and history;
- exact adjacent-slice composition with identity, event-conservation, and
  associativity certificates over one unchanged diagram;
- bounded `TriadicObserverTransitionV0` companions that classify three input
  source fibres, derive three opposite-pair cut readings, retain source-free
  residuals, and compose occurrence ancestry exactly across adjacent slices;
- a bounded Python research machine that packages exact triadic interfaces,
  complete `ProgramSlice` carriers, and Rust-checked schedule traces without
  claiming stable feedback or allocating semantic identities;
- a PyO3 extension and typed Python facade;
- optional SymPy, NumPy, and SciPy adapters.

The first slice is binder-free inside function bodies. Function parameters are
typed 0-cell boundaries; module-level `def` and `call` do not introduce local
term binders. Recursive module calls and cyclic imports are rejected.

## Lisp example

```lisp
(module arithmetic
  (export shared-double square)

  (def shared-double
    (fn ((x Real)) Real
      (add (copy (use x)))))

  (def square
    (fn ((x Real)) Real
      (mul (copy (use x))))))
```

Modules can import exported definitions:

```lisp
(module client
  (import arithmetic shared-double)
  (export quadruple)

  (def quadruple
    (fn ((x Real)) Real
      (call arithmetic/shared-double
        (call arithmetic/shared-double (use x))))))
```

## Python

```python
from adva import link_modules

workspace = link_modules([ARITHMETIC_SOURCE, CLIENT_SOURCE])
quadruple = workspace.function("client", "quadruple")

value = quadruple.evaluate({"x": 3.0})
value, gradient, certificate = quadruple.value_and_gradient({"x": 3.0})

sympy_expression = quadruple.to_sympy()
numpy_function = quadruple.numpy_callable()
objective = quadruple.scipy_objective()
```

A finite three-layer experiment is serialized and replayed separately from the
stable semantic kernel:

```python
from adva.research import ResearchCodeV0, ResearchMachineV0

code = ResearchCodeV0.from_json(encoded_experiment)
artifact = ResearchMachineV0().run(code)
print(artifact.verdict, artifact.replay_digest)
```

`adva.research` always rederives cuts, steps, slices, and triadic observations
through Rust. Its finite replay epochs are audit records, not a feedback,
recursion, normalization, or universal-computation semantics.

Stored diagrams cross a separate checked boundary:

```python
from adva import load_program

restored = load_program(quadruple.ir)
assert restored.validation_certificate["linear_use"] == "checked"
assert restored.compilation_certificate is None
```

Successful JSON decoding is not semantic authorization. `load_program` returns
only a diagram accepted by the Rust validator.

The scientific adapters never create, merge, identify, or forget sources. They
consume checked Rust IR. Removing Python does not change Rust judgments or
certificates.

## Development

```bash
cargo fmt --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace

python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
pytest
```

Read [`AGENTS.md`](AGENTS.md), [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md),
[`docs/SEMANTIC_SCOPE.md`](docs/SEMANTIC_SCOPE.md), and
[`docs/PROGRAM_PROCESS_CORE.md`](docs/PROGRAM_PROCESS_CORE.md) before changing
semantic code. The self-contained current-state report is
[`docs/TECHNICAL_REPORT_PROGRAM_PROCESS_CORE.md`](docs/TECHNICAL_REPORT_PROGRAM_PROCESS_CORE.md).
The completed exact-slice phase is recorded in
[`docs/NEXT_PHASE_PROGRAM_SLICES.md`](docs/NEXT_PHASE_PROGRAM_SLICES.md); the
active bounded transition task is
[`docs/NEXT_PHASE_TRIADIC_OBSERVER_TRANSITIONS.md`](docs/NEXT_PHASE_TRIADIC_OBSERVER_TRANSITIONS.md).
The first executable three-layer research instrument and its strict promotion
boundary are recorded in
[`docs/research/0074-three-layer-research-machine-v0.md`](docs/research/0074-three-layer-research-machine-v0.md).
Longer-term work on observer-conditioned specialization, complex `Prog`
geometry, intrinsic-structure learning, and practical language calibrations is
tracked in
[`docs/RESEARCH_ENGINEERING_AGENDA.md`](docs/RESEARCH_ENGINEERING_AGENDA.md).

## Status and license

Adva is a private pre-alpha research tool. No open-source license has yet been
selected; see [`LICENSE`](LICENSE). Public licensing should be a separate,
explicit decision.
