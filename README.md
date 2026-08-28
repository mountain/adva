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

- immutable `ProgramTerm`, module IR, and `SharedProgramDiagram`;
- explicit `copy`, `discard`, `swap`, `id`, `tensor`, arithmetic and elementary
  unary operations;
- stable serializable `SourceId`, `OccurrenceId`, `OccurrencePath`, and
  `History`;
- Rust module parsing, imports, exports, linking, and typed lowering;
- scalar evaluation and forward differential, each with a certificate;
- JSON IR round-trips with an explicit schema version;
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
and [`docs/SEMANTIC_SCOPE.md`](docs/SEMANTIC_SCOPE.md) before changing semantic
code.

## Status and license

Adva is a private pre-alpha research tool. No open-source license has yet been
selected; see [`LICENSE`](LICENSE). Public licensing should be a separate,
explicit decision.

