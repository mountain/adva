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
- a single versioned Rust operation registry shared by parsing, typed lowering,
  lineage transport, evaluation, and forward differentiation;
- scalar evaluation and forward differential, each with a certificate;
- JSON IR round-trips with an explicit schema version;
- semantic diagram import in Rust with graph, linear-use, occurrence, source,
  history, and boundary certificates;
- Rust-certified completed causal cuts and single-event frontier replacement,
  derived without evaluating or rebuilding checked wire lineage;
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
[`docs/TECHNICAL_REPORT_PROGRAM_PROCESS_CORE.md`](docs/TECHNICAL_REPORT_PROGRAM_PROCESS_CORE.md),
and the approved next-phase implementation brief is
[`docs/NEXT_PHASE_PROGRAM_SLICES.md`](docs/NEXT_PHASE_PROGRAM_SLICES.md).
Longer-term work on observer-conditioned specialization, complex `Prog`
geometry, intrinsic-structure learning, and practical language calibrations is
tracked in
[`docs/RESEARCH_ENGINEERING_AGENDA.md`](docs/RESEARCH_ENGINEERING_AGENDA.md).

## Status and license

Adva is a private pre-alpha research tool. No open-source license has yet been
selected; see [`LICENSE`](LICENSE). Public licensing should be a separate,
explicit decision.
