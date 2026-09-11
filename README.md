# Adva

**Typed symbolic computation and program geometry.** The native engine is a
small modular Lisp implemented in Rust. Rust owns typing, explicit sharing,
source and occurrence identity, history, calculus, certificates, and the
versioned intermediate representation. Python is an adapter layer for scientific
computing and visualization.

**Status: private pre-alpha research tool.** No open-source license has been
selected; see [`LICENSE`](LICENSE), and public licensing should be a separate,
explicit decision.

The repository implements ideas developed in `process-geometry`, but it is **not
the theory repository**. Mathematical claims remain scoped and registered; the
tool does not turn research targets into stable API promises.

> **Rust is the sole semantic authority.** Python may adapt checked IR to SymPy,
> NumPy, SciPy or a plot; it must not create or identify a semantic identity.
> Removing Python does not change any Rust judgment or certificate.

## What this is, and what it is not

- **It is** a native engine for typed symbolic computation in which every
  semantic transformation returns a result together with a certificate, and in
  which source, occurrence and history are explicit and serializable rather than
  derived from memory addresses, value equality or structural hashing.
- **It is not** a theorem prover, a general-purpose language, a self-modifying
  knowledge base, a stable public API, or evidence that the research targets it
  records have been reached.
- **Where no check exists, the claim is not made.** Search exhaustion produces
  `Unknown`, never a proof of nonexistence, and a green run is a statement about
  verification, not about progress.

## Run something now

Build the research entry point:

```bash
cargo build --release -p adva-witness --bin adva
```

The bounded research native program entry is `adva run program.adva --output
result.adva`. Run the first executable profile over a pinned program, into a
**fresh** output path:

```bash
target/release/adva run programs/native-run/arithmetic.adva \
  --output target/arithmetic-result.adva
```

Use a fresh output path: the profile refuses to overwrite. This first profile
wraps the existing Rust PSC0 compiler and f64 evaluator; see
[Research 0140](docs/research/0140-native-program-run.md) for its finite limits,
certificates, refusals and remaining exact-arithmetic work.

Load and recheck an existing library snapshot through Rust:

```bash
target/release/adva library check
target/release/adva library reuse
```

For a pinned Linux source build and a relocatable native runtime, see
[Bootstrap runtime v0](docs/BOOTSTRAP_RUNTIME_V0.md). The `library check` and
`library reuse` commands load and recheck existing snapshots; they do not execute
every library document and do not change the stored witness rules. The
bootstrap source bundle includes its required library files and preserves the
current private license.

## A first program

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

### Where the boundaries are

Successful JSON decoding is **not** semantic authorization. Stored diagrams
cross a separate checked boundary:

```python
from adva import load_program

restored = load_program(quadruple.ir)
assert restored.validation_certificate["linear_use"] == "checked"
assert restored.compilation_certificate is None
```

`load_program` returns only a diagram accepted by the Rust validator. Numerical
source selects `log@2` and correctly rounded `constant@2`; stored version-one
operations remain replayable. Ordinary Python evaluation requires finite
inputs and results and, when requested, a finite Jacobian, while Rust retains an
explicit raw IEEE replay. See
[ADR 0045](docs/adr/0045-rational-rounding-and-finite-numeric-boundaries.md) for
compatibility, JSON transport, and the distinction from error bounds.

The **first stable slice is binder-free inside function bodies**. Function
parameters are typed 0-cell boundaries; module-level `def` and `call` do not
introduce local term binders. Recursive module calls and cyclic imports are
rejected.

## What is stable, and what is research-only

The scope statement is [`docs/SEMANTIC_SCOPE.md`](docs/SEMANTIC_SCOPE.md) and the
working rules are [`AGENTS.md`](AGENTS.md). The split below follows them.

**Stable kernel** — the binder-free, finite, linear core:

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
- a PyO3 extension and typed Python facade;
- optional SymPy, NumPy, and SciPy adapters.

**Research-only companions** — checked, bounded, and not stable API. Each names its own finite scope and its refusals:

- bounded `TriadicObserverTransitionV0` companions that classify three input
  source fibres, derive three opposite-pair cut readings, retain source-free
  residuals, and compose occurrence ancestry exactly across adjacent slices;
- a bounded Python research machine that packages exact triadic interfaces,
  complete `ProgramSlice` carriers, and Rust-checked schedule traces without
  claiming stable feedback or allocating semantic identities;
- a research-only multi-hole through adapter that derives one typed
  relation-valued angle form from exact graft bindings and occurrence ancestry,
  with layered failure gates and the complete slice retained as residual;
- a one-compilation triangular research calibration that derives all three
  local opposite-domain angle relations while refusing undeclared
  same-source sibling connectors and global circular closure;
- a typed connector trichotomy that separates exact occurrence identity,
  provenance-preserving direct-sibling comparison, and an unauthorized
  many-to-one source quotient;
- a bounded distributivity characteristic machine that gives learning and
  proof readouts over one exact rational polynomial feature while retaining
  two distinct checked process residuals;
- a research-only typed-aperture calibration that reads existing through
  relations as finite filling fibres, refuses implicit multivalued closure,
  and retains close/reopen history and the complete process residual;
- a Rust research V0 six-word witness companion with signed formation
  ledgers, exact integer-polynomial transport, finite proof DAGs, and reusable
  linear three-hole templates whose fresh instances bind existing semantic
  occurrences explicitly;
- a bounded neutral-carrier mechanism grammar that keeps
  `subject/method/object`, `compute/verify/learn`, and
  `history/result/evidence` distinct, rejects open compute subjects and
  objects, accounts for conditional verification, and retains partial learning
  fill proposals without changing the stable IR;
- a research-only neutral `.adva` document graph with canonical carrier and
  frame tables: mechanisms live on three-input/three-output transition edges,
  named entry points select checked frames, and later frames reuse earlier
  recorded carriers through explicit document-local references;
- a first bounded `reveal.adva` program whose observer-local names cover the
  six directed time/space/construction pairs while its checked `M6` relation
  remains explicitly open, together with the exact witness emitted by its
  first six-fuel run;

Several of these carry a parallel external check that is not native authority.
Three accepting verifiers are **not** a three-computation theorem, and a
registered external calibration is not native admission.

## Repository layout

| Path | What lives there |
|---|---|
| `crates/adva-ir` | versioned IR, typed frontiers, sources, occurrences, history |
| `crates/adva-lisp` | parser, typed lowering, module linking, operation registry, evaluation, differentiation |
| `crates/adva-witness` | Rust-certified cuts, slices, triadic transitions, the `adva` binary, research examples |
| `crates/adva-python` | the PyO3 extension |
| `python/adva` | the Python facade and the outer CLIs, including `adva.py` |
| `programs/` | `.adva` programs, including the retained byte-for-byte witnesses |
| `experiments/` | bounded external checks, each with a frozen contract and evidence |
| `adva-library/` | the content and library layer; a separate repository, see its own [README](adva-library/README.md) |
| `trials/` | the AEG-side rounds, the append-only receipt ledger, and the published feed |
| `docs/` | architecture, scope, agenda, ADRs, registered claims, and the research record |
| `tests/python/` | the Python test suite |

## Reading path

Before changing semantic code, read, in this order:

1. this file;
2. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md);
3. [`docs/SEMANTIC_SCOPE.md`](docs/SEMANTIC_SCOPE.md);
4. [`docs/PROGRAM_PROCESS_CORE.md`](docs/PROGRAM_PROCESS_CORE.md);
5. [`docs/TECHNICAL_REPORT_PROGRAM_PROCESS_CORE.md`](docs/TECHNICAL_REPORT_PROGRAM_PROCESS_CORE.md)
   — the self-contained current-state report;
6. [`docs/NEXT_PHASE_PROGRAM_SLICES.md`](docs/NEXT_PHASE_PROGRAM_SLICES.md),
   the completed exact-slice phase;
7. [`docs/NEXT_PHASE_TRIADIC_OBSERVER_TRANSITIONS.md`](docs/NEXT_PHASE_TRIADIC_OBSERVER_TRANSITIONS.md),
   the completed bounded transition task;
8. [`docs/claims.toml`](docs/claims.toml);
9. the relevant ADRs under [`docs/adr/`](docs/adr/).

Before proposing a new phase, also read
[`docs/RESEARCH_ENGINEERING_AGENDA.md`](docs/RESEARCH_ENGINEERING_AGENDA.md); its
dependency order is part of the plan. Before resuming a breakthrough search, use
the trusted-boundary and finite-run contract in
[Research 0129](docs/research/0129-bounded-breakthrough-trusted-boundaries.md):
it records the unresolved language-formation question, the vocabulary status, and
the requirement to stop without silently renewing the budget.

## Development and checks

```bash
cargo fmt --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace

python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
pytest

python -S python/adva/adva.py math-check --key-words
```

CI runs the Rust checks, the retained bounded examples, `pytest` on Python 3.11,
3.12 and 3.13, and the documentary catalog check. Several workflows re-run a
retained witness and compare the generated bytes with the committed file.

Two known-failing tests are recorded rather than hidden:
`tests/python/test_phase_runner.py` has 10 failures on macOS that reproduce on a
clean checkout, so they are a platform issue and not a regression signal.

## The research record

The repository's research narrative used to fill this README. It now lives in
[`docs/research/README.md`](docs/research/README.md), which also indexes all 192
notes and the retained evidence directories and explains what a note's status
line lets you cite it for.

Contributions to the record follow the conventions in
[`AGENTS.md`](AGENTS.md): a bounded experiment declares its contract, its
checker, its refusals and its residual before it runs, and reports exhaustion as
`Unknown`.
