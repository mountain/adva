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
completed bounded transition task is
[`docs/NEXT_PHASE_TRIADIC_OBSERVER_TRANSITIONS.md`](docs/NEXT_PHASE_TRIADIC_OBSERVER_TRANSITIONS.md).
The first executable three-layer research instrument and its strict promotion
boundary are recorded in
[`docs/research/0074-three-layer-research-machine-v0.md`](docs/research/0074-three-layer-research-machine-v0.md).
Its first grounded relation-valued through experiment is
[`docs/research/0075-grounded-multi-hole-through-adapter-v0.md`](docs/research/0075-grounded-multi-hole-through-adapter-v0.md).
The first single-diagram calibration of all three local angles, including its
global-closure obstruction, is
[`docs/research/0076-three-angle-single-diagram-calibration.md`](docs/research/0076-three-angle-single-diagram-calibration.md).
The follow-up connector experiment separates comparison from forgetting in
[`docs/research/0077-typed-connector-trichotomy-v0.md`](docs/research/0077-typed-connector-trichotomy-v0.md).
The bounded distributivity learning--proof calibration is
[`docs/research/0078-distributivity-characteristic-dual-read-v0.md`](docs/research/0078-distributivity-characteristic-dual-read-v0.md).
The hole-first reorganization and its bounded open--close calibration are
recorded in
[`docs/research/0079-typed-hole-open-close-calibration-v0.md`](docs/research/0079-typed-hole-open-close-calibration-v0.md).
The finite-surface universal-lift and threaded-imagination synthesis is
recorded in
[`docs/research/0080-finite-surface-universal-lift-imagination.md`](docs/research/0080-finite-surface-universal-lift-imagination.md).
The relative-halt propositional, connective-fibre, and semantic-entailment
calibrations, line--hole bivalence, and thread-respecting compactification
constraints are
recorded in
[`docs/research/0081-relative-halt-exploration-threaded-compactification.md`](docs/research/0081-relative-halt-exploration-threaded-compactification.md).
The finite threaded propositional and predicate adequacy theorem is recorded in
[`docs/research/0082-threaded-finite-logic-adequacy.md`](docs/research/0082-threaded-finite-logic-adequacy.md).
The distinct-domain linear-source conflict and third-domain aperture calibration
are recorded in
[`docs/research/0083-triadic-conflict-aperture-completion.md`](docs/research/0083-triadic-conflict-aperture-completion.md).
The first research-local ordered natural-deduction, replayable search, and
support-mask coherence calibration is recorded in
[`docs/research/0084-threaded-natural-deduction-entailment-cell.md`](docs/research/0084-threaded-natural-deduction-entailment-cell.md).
The strengthened ordered one-hole substitution theorem, conditional V0
fresh-cut admissibility, and beta-ledger transport boundary are recorded in
[`docs/research/0085-ordered-substitution-cut-beta-ledger-boundary.md`](docs/research/0085-ordered-substitution-cut-beta-ledger-boundary.md).
Its proof-theoretic continuation supplies contextual beta-ledger transport,
heterogeneous ledger-indexed preservation, and beta-only strong normalization
for finite `TND0` derivations in
[`docs/research/0086-contextual-beta-ledger-transport-strong-normalization.md`](docs/research/0086-contextual-beta-ledger-transport-strong-normalization.md).
The pure computation syntax joining ordered multi-hole configurations,
three-role annotations, typed through apertures, explicit connectors, and
legal recursive Omega circles is proposed in
[`docs/research/0087-typed-three-domain-threaded-multihole-calculus.md`](docs/research/0087-typed-three-domain-threaded-multihole-calculus.md).
It adds no evaluation relation, denotation, or stable API.
A reusable, occurrence-reopenable historical distributivity character is
calibrated in
[`docs/research/0088-historical-distributivity-character-v0.md`](docs/research/0088-historical-distributivity-character-v0.md).
Its finite-observer failure frontier and closure boundary are developed in
[`docs/research/0089-failure-frontiers-observer-relative-closure.md`](docs/research/0089-failure-frontiers-observer-relative-closure.md),
with a prefix-frontier calibration plan in
[`docs/research/0090-prefix-frontier-closure-calibration-plan.md`](docs/research/0090-prefix-frontier-closure-calibration-plan.md).
The endogenous scope-breakthrough ledger and its first generative
distributivity calibration plan are recorded in
[`docs/research/0091-endogenous-scope-breakthrough-and-venture-ledger.md`](docs/research/0091-endogenous-scope-breakthrough-and-venture-ledger.md)
and
[`docs/research/0092-generative-distributivity-venture-calibration-plan.md`](docs/research/0092-generative-distributivity-venture-calibration-plan.md).
The proof-theoretic continuation separates proof-tree equality from
audit-history coherence, proves beta-only local and global confluence, and
gives each fixed finite `TND0` starting derivation a unique beta normal form in
[`docs/research/0093-beta-history-local-confluence-audit-2-cells.md`](docs/research/0093-beta-history-local-confluence-audit-2-cells.md).
The object-level completion of the present right-residual fragment identifies
its empty-antecedent ordered Lambek skeleton, proves normal/neutral and
subformula theorems, and gives a terminating sound-and-complete focused
derivability decision in
[`docs/research/0094-focused-normal-forms-subformula-decidable-derivability.md`](docs/research/0094-focused-normal-forms-subformula-decidable-derivability.md).
Bootstrap Zero's smaller geometric language, comprising one object language,
one type language, finite line and circle forms, typed thread words, and five
syntax-only interpreter declarations, is proposed in
[`docs/research/0095-bootstrap-zero-geometric-threading-syntax.md`](docs/research/0095-bootstrap-zero-geometric-threading-syntax.md).
It introduces no evaluation, denotation, or stable API.
The external finite placement of all 128 seven-world Boolean supports into
twenty triangle archetypes, together with the exact directed-edge and chiral
counts and their syntax-only Bootstrap Zero alignment, is recorded in
[`docs/research/0096-boolean-triangle-placement-language-alignment.md`](docs/research/0096-boolean-triangle-placement-language-alignment.md).
It defines no interpreter clause or Boolean computation semantics.
The threading-side continuation adds typed signed crossings and raw braid
blocks in
[`docs/research/0097-threading-syntax-typed-braid-alignment.md`](docs/research/0097-threading-syntax-typed-braid-alignment.md).
It keeps crossing sign separate from incidence polarity, domain direction,
L/R side, and function swap, without adding braid-word equations.
The multi-hole A/M continuation records ordered kernels, graft bindings,
source/occurrence lineage, and explicit copy/discard obligations in
[`docs/research/0098-multihole-am-type-formation-constraints.md`](docs/research/0098-multihole-am-type-formation-constraints.md).
It introduces no surreal number, option recursion, objectification, or
arithmetic equality.
The axis--circle continuation extracts a history-indexed pendulum constraint
as pure formation syntax in
[`docs/research/0099-axis-circle-pendulum-history-syntax.md`](docs/research/0099-axis-circle-pendulum-history-syntax.md).
It keeps the history parameter distinct from domain `t`, shares one explicit
cycle name across the line--circle, three-domain Omega word, forgetting, and
closure records, and proves no interpreter coherence.
The complete Bootstrap Zero syntax-factor inventory, its hard/calibration/
candidate status split, and the local repairs for pure A/M syntax, derivative
indices, and occurrence-to-hole binding are recorded in
[`docs/research/0100-bootstrap-zero-syntax-factor-inventory-and-seam-repairs.md`](docs/research/0100-bootstrap-zero-syntax-factor-inventory-and-seam-repairs.md).
It leaves the shared `Circle(gamma)`/Omega/closure seam as an explicit
coordination proof obligation.
The subsequent theoretical correction rebases Bootstrap Zero on the conditional
six-port minimum for triadic sustained threading, one whole-cut carrier, dual
line/circle views, distinct duality/polarity/conjugation operations, factored
traversal, collision strata, and noncollapsing zero fibres in
[`docs/research/0101-six-port-whole-cut-theory.md`](docs/research/0101-six-port-whole-cut-theory.md).
Its syntax-only redesign and visible extension envelope are specified in
[`docs/research/0102-bootstrap-zero-whole-cut-grammar.md`](docs/research/0102-bootstrap-zero-whole-cut-grammar.md).
The next syntax refinement keeps the `cell -> carrier -> views` spine while
adding dimension-indexed relation cells, open view contracts, proof-relevant
logic views for the `Q4` interchange and `M6` braid machines, and a finite
`TO24` coherence-envelope calibration in
[`docs/research/0103-cell-carrier-view-relation-machines.md`](docs/research/0103-cell-carrier-view-relation-machines.md).
The exact adapter from the three whole-cut pairings and three through pairings
to an open alternating `M6` boundary, with disjoint port/state/step ledgers and
no manufactured braid filler, is recorded in
[`docs/research/0104-whole-cut-six-to-m6-boundary-bridge.md`](docs/research/0104-whole-cut-six-to-m6-boundary-bridge.md).
These notes supersede the earlier inventory as the proposed Bootstrap Zero
completion baseline while preserving notes 0095--0100 as the derivation record.
A separate application note investigates whether proof-relevant `Q4`
interchange and candidate `M6` braid cells can quotient redundant Go histories
for exact or hybrid low-resource search, while keeping the full-state,
history, certification-cost, and falsification boundaries explicit in
[`docs/research/0105-q4-m6-go-search-research-program.md`](docs/research/0105-q4-m6-go-search-research-program.md).
A separate theoretical bridge proves the finite three-hole two-matching six-cycle,
names the resulting nonprincipal family member `HolePolarityM6`, verifies
symbolically and by exact exhaustive permutation audit that global hole-polarity
reversal exchanges its two oriented threadings, identifies the order-four
linear lift hidden by the AEG reciprocal projective involution, and isolates
the typed `J`-transport, central-sign, `U(1)`, Omega, and energy/time
obligations in
[`docs/research/0106-three-hole-conjugate-m6-projective-lift.md`](docs/research/0106-three-hole-conjugate-m6-projective-lift.md).
It adds no M6 filler, complex program semantics, or physical time claim.
The corrected six-word seed registry and the first reusable Rust witness
kernel are specified in
[`docs/research/0107-reusable-six-word-witness-kernel.md`](docs/research/0107-reusable-six-word-witness-kernel.md).
It separates additive formation zero, multiplicative transport one, concrete
zero faults, cached proof content, fresh instances, and program results without
changing `adva.ir` version 1 or creating equation cells.
Certified compiler graft frames can now supply the three ordered occurrence
bindings directly, while the instance retains both certificate identifiers and
the exact frame path for audit; the bounded adapter and its refusal of
zero/multi-lineage holes are recorded in
[`docs/research/0108-graft-derived-witness-instantiation.md`](docs/research/0108-graft-derived-witness-instantiation.md).
Longer-term work on observer-conditioned specialization, complex `Prog`
geometry, intrinsic-structure learning, and practical language calibrations is
tracked in
[`docs/RESEARCH_ENGINEERING_AGENDA.md`](docs/RESEARCH_ENGINEERING_AGENDA.md).

Historical and philosophical source notes are kept separately in
[`docs/philosophy/`](docs/philosophy/README.md). They preserve the path from
Leibniz's universal characteristic to the finite-observer open/close-hole
hypothesis and its falsifiable experiment agenda. These notes provide
interpretive research context only; they add no stable semantics or
registered executable claims.

## Status and license

Adva is a private pre-alpha research tool. No open-source license has yet been
selected; see [`LICENSE`](LICENSE). Public licensing should be a separate,
explicit decision.
