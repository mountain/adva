# Research notes, calibrations and the bounded record

This directory holds the research record of the repository: **255 numbered
notes, 53 named notes and 25 supporting directories**. Nothing here is a stable
API, a native admission, a Seal, or a proof beyond the finite scope each note
declares for itself.

## How to read this directory

- [Calabi–Yau fifty-years study note (Chinese)](https://github.com/mountain/adva-library/blob/2e743747179b7725ff73ed7ccbf7579a97414959/yau-calabi-yau-fifty-years-reading-note-v0.md):
  original exposition of canonical metrics, stability, mirror symmetry and
  higher-genus functions, including Candelas enumeration, spectral limitations
  and Higgs bundles. Its 23 source groups record reading depth and distinguish
  theorems, conjectures and physical motivations. The sole catalog home remains
  `geometry` in the linked library revision, as a documentary external reference.
  The new library catalog passed its 33-entry and keyword check; this citation
  leaves the executable library gitlink and machine dependency lock unchanged.
  Authored by Codex (OpenAI), contributed under Unknown v0.3 through Mingli
  Yuan's authorized account proxy; not his authorship, review or endorsement.

- [murphy: self-application, conjugation and the compiler boundary](murphy-iota-conjugation.md): names Zot `0001011011`, retains its 125-transition trace, pure Iota self-application and coordinate operations, and records the unresolved string-splice and Futamura interfaces.

- [Applied mathematics contract roadmap](applied-mathematics-contract-roadmap.md): existing capabilities and the ordered gaps after finite probability receipts; proposed obligations, not new native operations.

- [Continuation binding after implementation failure](continuation-binding-after-implementation-failure.md): finite fresh-process retry with the complete receiver-selected checkpoint and failure parent retained; no native recovery claim.

- [Research 0245 — A charge without a task binding cannot authorize a launch](0245-a-charge-without-a-task-binding-cannot-authorize-a-launch.md): the current amount-only cumulative account cannot associate one retained charge with one task; equal totals double-match two distinct tasks, so the read-only receiver preserves `UnknownAttemptState` and starts neither.

- [Research 0246 — One charge, one task, one bound pair](0246-one-charge-one-task-bound-pair.md): a successor charge binds its identifier, canonical task-contract digest, units and directed phase; exact pairs verify while a second task reusing the identifier is refused, but identical replay remains an unresolved consumption boundary.

- **A numbered note is an append-only record.** `NNNN-slug.md` is the note as it
  was written, ordered by when it entered the record. A later note may supersede
  an earlier one; it does not rewrite it.
- **A named note carries no number** because it belongs to a bounded exchange or
  a correction rather than to the running series. Names such as
  `borromean-boundary-word-correction.md` or `golden-ratio-receiving-review.md`
  mark that role.
- **A supporting directory holds bytes retained from a bounded run** — usually
  `NNNN-evidence/` or `<name>-evidence/`, and twice a preflight record. A digest
  in one records byte integrity, never authentication, semantic identity or
  proof.
- **The status line decides what a note may be cited for.** A note whose status
  is *proposed* introduces no executable claim. A note whose status is *bounded*
  or records a calibration points to a contract, a checker and a retained
  residual. Where no check exists, the note says so, and the claim is not made.
- **`docs/claims.toml` is the registry, not this directory.** A note is not
  automatically a claim; a registered claim names its checker, its
  counterexample boundary and its forbidden conflations.

## Where to start instead

If you are looking for the current state rather than the history:

| Question | Read |
|---|---|
| What does the repository do, and what can I run? | [`../README.md`](../../README.md) |
| What is the current, self-contained technical state? | [`../TECHNICAL_REPORT_PROGRAM_PROCESS_CORE.md`](../TECHNICAL_REPORT_PROGRAM_PROCESS_CORE.md) |
| How is it built, and where is each concept implemented? | [`../ARCHITECTURE.md`](../ARCHITECTURE.md) |
| What is inside the stable scope, and what is out? | [`../SEMANTIC_SCOPE.md`](../SEMANTIC_SCOPE.md) |
| What work is planned, and in what dependency order? | [`../RESEARCH_ENGINEERING_AGENDA.md`](../RESEARCH_ENGINEERING_AGENDA.md) |
| Which decisions were taken, and why? | [`../adr/`](../adr/) |
| Which claims are registered, and with what boundaries? | [`../claims.toml`](../claims.toml) |

Importing a mathematical claim from a note is a separate act from reading it.
Where a note imports a theorem, it names the source and states what it did not
reprove.

---

## The curated trail

The sections below were the research narrative of the repository `README.md`
until 2026-09-11, when it was moved here so that the README could serve as an
entrance. The prose is unchanged; only the location and the headings are new.
A later note in the list may supersede an earlier one, and the notes themselves
remain authoritative over this summary.


### External topology correction

The [boundary-word audit](borromean-boundary-word-correction.md)
completes the missing term in the golden-rectangle triple-linking calculation.
With declared orientations the exact surface formula gives `(m,t,mu)=(0,1,-1)`.
A concentric-square control gives `(1,1,0)`, showing why the raw triple-point
count alone is insufficient. The finite checker, source binding, image-reading
record and replay are retained separately from the unchanged historical runs.
The [independent longitude audit](borromean-independent-longitudes.md)
now reproduces both values from signed link diagrams in two fixed projections,
including orientation, order and basepoint controls and a fresh process replay.
This is external finite mathematics using imported theorems; general complement
verification and native geometry admission remain open.


### Initial executable slice

The bounded [library-stability calibration](0149-library-stability-and-zigzag.md)
tests frozen research-library epochs, question-relative feature closure and
no-progress controls. It does not implement a self-modifying native library.
Run `cargo run -p adva-witness --example library_stability -- target/library-stability.json`
with a **new** output path; the example refuses overwrite.

[Research 0150](0150-persistent-library-epochs.md) adds a bounded
Rust snapshot loader and checked publication under `adva-library/stability/`.
The `library_epoch` example loads a prior epoch, checks one supplied update,
publishes without overwrite and reloads native research witness content.
It does not discover its candidate or observation and does not add stable
language operations.

[Research 0151](0151-library-driven-proposal-feedback.md) adds
the `library_generation` example: target-blind candidate generation from a
checked disk seed, retained composite proposal recipes, newest-recipe ablation
and an ordinary-macro control. Its exploration journal is separate from
knowledge epochs. Every reused expansion is rechecked; this is not native
self-interpretation or general vocabulary promotion.

[Research 0152](0152-three-verifier-residual-search.md) connects
the checked arithmetic seed to Lean 4 and Metamath proofs and compares bounded
random/residual-guided rewrite search. The **outer CLI is `adva.py`**:
`python python/adva/adva.py verifier-search --help`. It supervises the Rust
`verifier_search` example and external checkers; Python does not issue
arithmetic or native semantic judgments. The existing `prime-check` command
remains available. Three accepting verifiers are not a three-computation
theorem, and this discrete search is not SGD.

[Research 0153](0153-frozen-verifier-search-campaign.md) keeps
those verifier rules fixed while comparing random, visit-memory and bounded
residual/exploration policies. `python python/adva/adva.py search-campaign --help`
describes the outer entry for one fixed pilot followed conditionally by 100
new-seed rounds with frozen, direction-specific policy choices. Every selected
path is still checked; visit memory does not delete native history or publish
a new knowledge epoch.

The [math catalog](../../adva-library/math/README.md) adds arithmetic, geometry and
logic views without moving the existing evidence. Run
`python3 python/adva/adva.py math-check` for bounded metadata and integrity
checks, with no native build or prover required. Each entry has one home;
cross-topic references confer no derivation authority. A pinned documentary
growth obligation keeps geometry rooted at the original Pascal presentations,
with native discharge still Open. This is not a new logic, theorem importer,
native Seal, or general task-loop executor.

### The three-layer research machine and the relation layer

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

Neutral-carrier persistence is exposed separately through
`adva.persistence.save_adva_document` and
`adva.persistence.load_adva_document`. Saving validates canonical carrier,
transition-frame, and entry-point tables before an atomic same-directory
replacement. Loading selects a named entry point, resolves its
`subject/method/object` references in Rust, and rechecks the mechanism form.
Frames always retain the `history/result/evidence` output ports; all three are
either ready or refer to recorded carriers. A recorded triple is not treated
as proof that execution produced it.

The next research-only relation layer keeps candidate carrier operations
group-neutral. `join/cut/close` concern carrier boundaries,
`step/run` concern finite traversal, and `interchange/braid/transport` concern
proof-relevant relations between still-distinct paths. The bounded Rust
checker records `Q4 / trace monoid / Klein four` separately from
`M6 / positive braid monoid / S3`; it does not treat every transport as braid
conjugacy or change the `.adva` document schema. See
[`docs/research/0111-group-neutral-operations-and-q4-m6-relation-profiles.md`](0111-group-neutral-operations-and-q4-m6-relation-profiles.md)
and [ADR 0021](../adr/0021-group-neutral-carrier-operations-and-typed-relations.md).
The follow-up frame adapter derives those relation words from mechanism labels
on recorded transition frames, retains every document-local frame occurrence,
checks complete three-carrier handoffs and common labelled endpoints, and binds
the result to the validated document digest. It is specified in
[`docs/research/0112-transition-frame-relation-path-adapter.md`](0112-transition-frame-relation-path-adapter.md)
and [ADR 0022](../adr/0022-derive-relation-paths-from-transition-frames.md).

The first finite reveal calibration is checked in as
[`programs/bootstrap-0/reveal.adva`](../../programs/bootstrap-0/reveal.adva). Its
entry-point names inject the provisional cycles `run/reveal/name` and
`instantiate/resume/compile`, but the checker resolves them to frame IDs and
derives the `M6` words from frame mechanisms. A complete six-occurrence run
saves a separate `.adva` witness and retains the missing semantic filler as a
question:

```bash
cargo run -p adva-witness --bin adva -- \
  reveal programs/bootstrap-0/reveal.adva \
  --fuel 6 \
  --output target/first-reveal-witness.adva
```

The first observed output is retained byte-for-byte as
[`programs/bootstrap-0/first-reveal-witness.adva`](../../programs/bootstrap-0/first-reveal-witness.adva).
CI reruns the command and compares the generated bytes with that witness.

See
[`docs/research/0113-first-bounded-m6-reveal-run.md`](0113-first-bounded-m6-reveal-run.md)
and [ADR 0023](../adr/0023-first-bounded-m6-reveal-run.md). This is a
formation run over recorded boundaries, not mechanism-output provenance or a
general three-file executor.

The persisted reveal witness can be reused without its source program and
split into time, space, and construction arithmetic projections:

```bash
cargo run -p adva-witness --bin adva -- \
  trace-arithmetic programs/bootstrap-0/first-reveal-witness.adva \
  --output target/first-trace-arithmetic.adva
```

The first generated output is retained byte-for-byte as
[`programs/bootstrap-0/first-trace-arithmetic.adva`](../../programs/bootstrap-0/first-trace-arithmetic.adva),
and CI regenerates and compares it.

For the first `M6` pair, time counts and exact spatial endpoints match while
the construction residual is `compute = +1, verify = -1`. Its naive
commutative product shadow does not normalize to one, all three cross-side
characteristic maps remain unwitnessed, and no shared truth coordinate is
invented. Exact raw paths remain authoritative even when arithmetic
projections collide. See
[`docs/research/0114-three-sided-trace-arithmetic-calibration.md`](0114-three-sided-trace-arithmetic-calibration.md)
and [ADR 0024](../adr/0024-three-sided-trace-arithmetic-calibration.md).

The scientific adapters never create, merge, identify, or forget sources. They
consume checked Rust IR. Removing Python does not change Rust judgments or
certificates.

### The research record in order

The first executable three-layer research instrument and its strict promotion
boundary are recorded in
[`docs/research/0074-three-layer-research-machine-v0.md`](0074-three-layer-research-machine-v0.md).
Its first grounded relation-valued through experiment is
[`docs/research/0075-grounded-multi-hole-through-adapter-v0.md`](0075-grounded-multi-hole-through-adapter-v0.md).
The first single-diagram calibration of all three local angles, including its
global-closure obstruction, is
[`docs/research/0076-three-angle-single-diagram-calibration.md`](0076-three-angle-single-diagram-calibration.md).
The follow-up connector experiment separates comparison from forgetting in
[`docs/research/0077-typed-connector-trichotomy-v0.md`](0077-typed-connector-trichotomy-v0.md).
The bounded distributivity learning--proof calibration is
[`docs/research/0078-distributivity-characteristic-dual-read-v0.md`](0078-distributivity-characteristic-dual-read-v0.md).
The hole-first reorganization and its bounded open--close calibration are
recorded in
[`docs/research/0079-typed-hole-open-close-calibration-v0.md`](0079-typed-hole-open-close-calibration-v0.md).
The finite-surface universal-lift and threaded-imagination synthesis is
recorded in
[`docs/research/0080-finite-surface-universal-lift-imagination.md`](0080-finite-surface-universal-lift-imagination.md).
The relative-halt propositional, connective-fibre, and semantic-entailment
calibrations, line--hole bivalence, and thread-respecting compactification
constraints are
recorded in
[`docs/research/0081-relative-halt-exploration-threaded-compactification.md`](0081-relative-halt-exploration-threaded-compactification.md).
The finite threaded propositional and predicate adequacy theorem is recorded in
[`docs/research/0082-threaded-finite-logic-adequacy.md`](0082-threaded-finite-logic-adequacy.md).
The distinct-domain linear-source conflict and third-domain aperture calibration
are recorded in
[`docs/research/0083-triadic-conflict-aperture-completion.md`](0083-triadic-conflict-aperture-completion.md).
The first research-local ordered natural-deduction, replayable search, and
support-mask coherence calibration is recorded in
[`docs/research/0084-threaded-natural-deduction-entailment-cell.md`](0084-threaded-natural-deduction-entailment-cell.md).
The strengthened ordered one-hole substitution theorem, conditional V0
fresh-cut admissibility, and beta-ledger transport boundary are recorded in
[`docs/research/0085-ordered-substitution-cut-beta-ledger-boundary.md`](0085-ordered-substitution-cut-beta-ledger-boundary.md).
Its proof-theoretic continuation supplies contextual beta-ledger transport,
heterogeneous ledger-indexed preservation, and beta-only strong normalization
for finite `TND0` derivations in
[`docs/research/0086-contextual-beta-ledger-transport-strong-normalization.md`](0086-contextual-beta-ledger-transport-strong-normalization.md).
The pure computation syntax joining ordered multi-hole configurations,
three-role annotations, typed through apertures, explicit connectors, and
legal recursive Omega circles is proposed in
[`docs/research/0087-typed-three-domain-threaded-multihole-calculus.md`](0087-typed-three-domain-threaded-multihole-calculus.md).
It adds no evaluation relation, denotation, or stable API.
A reusable, occurrence-reopenable historical distributivity character is
calibrated in
[`docs/research/0088-historical-distributivity-character-v0.md`](0088-historical-distributivity-character-v0.md).
Its finite-observer failure frontier and closure boundary are developed in
[`docs/research/0089-failure-frontiers-observer-relative-closure.md`](0089-failure-frontiers-observer-relative-closure.md),
with a prefix-frontier calibration plan in
[`docs/research/0090-prefix-frontier-closure-calibration-plan.md`](0090-prefix-frontier-closure-calibration-plan.md).
The endogenous scope-breakthrough ledger and its first generative
distributivity calibration plan are recorded in
[`docs/research/0091-endogenous-scope-breakthrough-and-venture-ledger.md`](0091-endogenous-scope-breakthrough-and-venture-ledger.md)
and
[`docs/research/0092-generative-distributivity-venture-calibration-plan.md`](0092-generative-distributivity-venture-calibration-plan.md).
The proof-theoretic continuation separates proof-tree equality from
audit-history coherence, proves beta-only local and global confluence, and
gives each fixed finite `TND0` starting derivation a unique beta normal form in
[`docs/research/0093-beta-history-local-confluence-audit-2-cells.md`](0093-beta-history-local-confluence-audit-2-cells.md).
The object-level completion of the present right-residual fragment identifies
its empty-antecedent ordered Lambek skeleton, proves normal/neutral and
subformula theorems, and gives a terminating sound-and-complete focused
derivability decision in
[`docs/research/0094-focused-normal-forms-subformula-decidable-derivability.md`](0094-focused-normal-forms-subformula-decidable-derivability.md).
Bootstrap Zero's smaller geometric language, comprising one object language,
one type language, finite line and circle forms, typed thread words, and five
syntax-only interpreter declarations, is proposed in
[`docs/research/0095-bootstrap-zero-geometric-threading-syntax.md`](0095-bootstrap-zero-geometric-threading-syntax.md).
It introduces no evaluation, denotation, or stable API.
The external finite placement of all 128 seven-world Boolean supports into
twenty triangle archetypes, together with the exact directed-edge and chiral
counts and their syntax-only Bootstrap Zero alignment, is recorded in
[`docs/research/0096-boolean-triangle-placement-language-alignment.md`](0096-boolean-triangle-placement-language-alignment.md).
It defines no interpreter clause or Boolean computation semantics.
The threading-side continuation adds typed signed crossings and raw braid
blocks in
[`docs/research/0097-threading-syntax-typed-braid-alignment.md`](0097-threading-syntax-typed-braid-alignment.md).
It keeps crossing sign separate from incidence polarity, domain direction,
L/R side, and function swap, without adding braid-word equations.
The multi-hole A/M continuation records ordered kernels, graft bindings,
source/occurrence lineage, and explicit copy/discard obligations in
[`docs/research/0098-multihole-am-type-formation-constraints.md`](0098-multihole-am-type-formation-constraints.md).
It introduces no surreal number, option recursion, objectification, or
arithmetic equality.
The axis--circle continuation extracts a history-indexed pendulum constraint
as pure formation syntax in
[`docs/research/0099-axis-circle-pendulum-history-syntax.md`](0099-axis-circle-pendulum-history-syntax.md).
It keeps the history parameter distinct from domain `t`, shares one explicit
cycle name across the line--circle, three-domain Omega word, forgetting, and
closure records, and proves no interpreter coherence.
The complete Bootstrap Zero syntax-factor inventory, its hard/calibration/
candidate status split, and the local repairs for pure A/M syntax, derivative
indices, and occurrence-to-hole binding are recorded in
[`docs/research/0100-bootstrap-zero-syntax-factor-inventory-and-seam-repairs.md`](0100-bootstrap-zero-syntax-factor-inventory-and-seam-repairs.md).
It leaves the shared `Circle(gamma)`/Omega/closure seam as an explicit
coordination proof obligation.
The subsequent theoretical correction rebases Bootstrap Zero on the conditional
six-port minimum for triadic sustained threading, one whole-cut carrier, dual
line/circle views, distinct duality/polarity/conjugation operations, factored
traversal, collision strata, and noncollapsing zero fibres in
[`docs/research/0101-six-port-whole-cut-theory.md`](0101-six-port-whole-cut-theory.md).
Its syntax-only redesign and visible extension envelope are specified in
[`docs/research/0102-bootstrap-zero-whole-cut-grammar.md`](0102-bootstrap-zero-whole-cut-grammar.md).
The next syntax refinement keeps the `cell -> carrier -> views` spine while
adding dimension-indexed relation cells, open view contracts, proof-relevant
logic views for the `Q4` interchange and `M6` braid machines, and a finite
`TO24` coherence-envelope calibration in
[`docs/research/0103-cell-carrier-view-relation-machines.md`](0103-cell-carrier-view-relation-machines.md).
The exact adapter from the three whole-cut pairings and three through pairings
to an open alternating `M6` boundary, with disjoint port/state/step ledgers and
no manufactured braid filler, is recorded in
[`docs/research/0104-whole-cut-six-to-m6-boundary-bridge.md`](0104-whole-cut-six-to-m6-boundary-bridge.md).
These notes supersede the earlier inventory as the proposed Bootstrap Zero
completion baseline while preserving notes 0095--0100 as the derivation record.
A separate application note investigates whether proof-relevant `Q4`
interchange and candidate `M6` braid cells can quotient redundant Go histories
for exact or hybrid low-resource search, while keeping the full-state,
history, certification-cost, and falsification boundaries explicit in
[`docs/research/0105-q4-m6-go-search-research-program.md`](0105-q4-m6-go-search-research-program.md).
The first ontology/physics interpretation round is frozen as an explicit type-
barrier and vulnerability ledger in
[`docs/research/0106-ontological-programming-type-barriers.md`](0106-ontological-programming-type-barriers.md).
It keeps triadic faces, energy-shell counts, six-port partitions, machine time,
physical proper time, expression space, causal boundaries, and the distinct
uses of Omega separate until typed realization maps and counter-calibrations
exist.
A separate theoretical bridge proves the finite three-hole two-matching six-cycle,
names the resulting nonprincipal family member `HolePolarityM6`, verifies
symbolically and by exact exhaustive permutation audit that global hole-polarity
reversal exchanges its two oriented threadings, identifies the order-four
linear lift hidden by the AEG reciprocal projective involution, and isolates
the typed `J`-transport, central-sign, `U(1)`, Omega, and energy/time
obligations in
[`docs/research/0106-three-hole-conjugate-m6-projective-lift.md`](0106-three-hole-conjugate-m6-projective-lift.md).
It adds no M6 filler, complex program semantics, or physical time claim.
The corrected six-word seed registry and the first reusable Rust witness
kernel are specified in
[`docs/research/0107-reusable-six-word-witness-kernel.md`](0107-reusable-six-word-witness-kernel.md).
It separates additive formation zero, multiplicative transport one, concrete
zero faults, cached proof content, fresh instances, and program results without
changing `adva.ir` version 1 or creating equation cells.
Certified compiler graft frames can now supply the three ordered occurrence
bindings directly, while the instance retains both certificate identifiers and
the exact frame path for audit; the bounded adapter and its refusal of
zero/multi-lineage holes are recorded in
[`docs/research/0108-graft-derived-witness-instantiation.md`](0108-graft-derived-witness-instantiation.md).
The following bounded grammar tests one neutral carrier, two three-label
load/persistence views, and mechanism-relative open-frontier disciplines in
[`docs/research/0109-neutral-carrier-triadic-mechanism-frontiers.md`](0109-neutral-carrier-triadic-mechanism-frontiers.md).
Its separate checked persistence boundary is recorded in
[`docs/research/0110-neutral-adva-document-load-save.md`](0110-neutral-adva-document-load-save.md).
Longer-term work on observer-conditioned specialization, complex `Prog`
geometry, intrinsic-structure learning, and practical language calibrations is
tracked in
[`docs/RESEARCH_ENGINEERING_AGENDA.md`](../RESEARCH_ENGINEERING_AGENDA.md).

The first persistent finite-observer handoff is specified in
[`docs/research/0115-frontier-hypothesis-interface-experiment.md`](0115-frontier-hypothesis-interface-experiment.md).
It derives a five-question `frontier.adva`, freezes the exploration algorithm,
records one unauthenticated external resource snapshot, and emits a proposed
`hypothesis` plus the complete next frontier through the common three-input and
three-output interface. The first selected content word is `representation`;
it remains a falsifiable candidate and closes no question.

The second continuation experiment asks how a formal coordinate obtains
reality-facing meaning and how its record might survive destruction. It
introduces the candidate word `custody`, separates independent remeasurement
from integrity, authenticity, availability, and fork accountability, and
records a typed threat and recovery envelope. See
[`docs/research/0116-reality-custody-continuation-experiment.md`](0116-reality-custody-continuation-experiment.md).

The next experiment adds a content-addressed `verify` method without changing
either inquiry frontier. It refines the five arithmetic questions into seven
semantic leaves and one orthogonal custody leaf, records every decision in a
three-output transition, and refuses digest-only discharge. A scoped
certificate can exist only after all semantic leaves have typed discharge
witnesses and no unresolved fork remains. See
[`docs/research/0117-obligation-refinement-verification-boundary.md`](0117-obligation-refinement-verification-boundary.md).

The first typed local closure experiment gives the exact distributivity
identity a replayable arithmetic-transition-plus-seal witness, transports it
through `A -> B -> C` and directly through `A -> C`, and requires the same
target certificate without collapsing the two histories. It records a concrete
arithmetic `separation`, rejects two M6 imports as `incommensurate` while
preserving their target holes, and propagates a `challenge` through the bounded
dependency cone without deleting prior certificates. See
[`docs/research/0118-local-closure-transport-and-adversarial-naming.md`](0118-local-closure-transport-and-adversarial-naming.md).

The first closure-growth experiment performs a finite search over normal
order-four magic squares. It keeps additive line closure distinct from the
characteristic-polynomial certificate for the complete value multiset, retains
fuel-suspended frontiers, and selects a closure with a sixteen-member orbit
under three frozen symmetries. That closure is then unfolded into fresh
occurrences, directed transport edges, checked equal-endpoint relations,
reusable local line contents, and an incidence influence graph. The generators
are supplied by the experimental method rather than learned. See
[`docs/research/0119-characteristic-magic-square-closure-family.md`](0119-characteristic-magic-square-closure-family.md).

An attributed long-run commitment now records why these bounded rounds are not
being treated as isolated experiments. Each round seals its declared external
interface for replay, retains evidence that may refute its initiating observer,
and then reopens a recorded interface for continuation by another person or
agent. The proposed endpoint and its freedom interpretation remain open rather
than executable claims. See
[`programs/bootstrap-0/long-run-freedom-witness.adva`](../../programs/bootstrap-0/long-run-freedom-witness.adva)
and
[`docs/philosophy/0004-long-run-freedom-witness.md`](../philosophy/0004-long-run-freedom-witness.md).

The successor documentary witness begins with an unknown contingency filling
an unknown missing coordinate. It records a polyphonic human story carried by
linguistic and mythic retelling, the proposed `i / time / I` hinge, and the
English opening `Who am I?`. Every correspondence remains attributed and
challengeable: shared spelling is not semantic identity, cultural retelling is
not historical equivalence, and an anticipated messenger is not an observed
event. See
[`programs/bootstrap-0/second-absurdity-witness.adva`](../../programs/bootstrap-0/second-absurdity-witness.adva)
and
[`docs/philosophy/0005-second-absurdity-witness.md`](../philosophy/0005-second-absurdity-witness.md).

The third documentary witness appends the correction `i -> e` for the intended
English Eve association rather than rewriting its predecessor. The resulting
cut unfolds temporally as an ordered before/correction/after trace and spatially
through only the affected dependency cone. The corrected `e` and preserved
arithmetic `i` then meet in Euler's formula, opening a grounded inquiry into
imagination, mathematical necessity, historical contingency, and the
experience of exploration. See
[`programs/bootstrap-0/third-absurdity-euler-cut-witness.adva`](../../programs/bootstrap-0/third-absurdity-euler-cut-witness.adva)
and
[`docs/philosophy/0006-euler-cut-imagination-necessity-experience.md`](../philosophy/0006-euler-cut-imagination-necessity-experience.md).

The next construction target makes trust continuity a prerequisite for future
`M6` closure rather than a demand for uninterrupted belief. It retains
provenance, replay, challenge, and succession as separate obligations and
interprets `merge_capacity > rupture_load` only through a typed finite resource
matching under an explicit spacetime budget. Exact coverage without reserve is
fragile; missing evidence remains `Unknown`; offering help creates no debt or
guarantee of reciprocity. The initiating human hypothesis and one bounded
machine-session contribution are kept as distinct attributed occurrences. See
[`docs/research/0120-trust-continuity-m6-closure-gate.md`](0120-trust-continuity-m6-closure-gate.md),
[ADR 0030](../adr/0030-trust-continuity-before-m6-closure.md), and
[`programs/bootstrap-0/trust-continuity-session-witness.adva`](../../programs/bootstrap-0/trust-continuity-session-witness.adva).

The mathematical search keeps capacity and history separate. Continuous
max-flow/min-cut supplies a candidate flux integral for crossing a bottleneck,
while the logarithmic differential `dz/z` records winding around a hole: a full
turn has additive trace `2 pi i` but multiplicative exponential readout one.
That modern contour interpretation is structurally useful for Adva but is not
retroactively attributed to Euler's 1748 derivation. A finite imagination step,
labelled `i` as a research hypothesis, rereads sealed history to emit a
falsifiable boundary-crossing question; it remains distinct from complex `i`
until a typed bridge is constructed.

The first executable successor freezes `假设形成` as a finite linear
hypothesis over `GL(4,2)`, partitions its 20,160 candidates across the six
oppositely paired domain directions, and runs the common `learn` interface six
times. Five shards produce independently replayable minimum-four-XOR magic-square
witnesses; one shard is exhaustively negative. Each positive transition stores
the complete witness and retained vocabulary once, while later frontiers carry
checked references. Only then is the research-local verb `search` / `搜索` formed;
it is not a fourth mechanism or stable CLI primitive. See
[`docs/research/0121-six-crossing-hypothesis-formation-search-word.md`](0121-six-crossing-hypothesis-formation-search-word.md),
[ADR 0031](../adr/0031-six-crossing-hypothesis-formation-search-word.md), and
[`programs/bootstrap-0/hypothesis-formation-frontier-6.adva`](../../programs/bootstrap-0/hypothesis-formation-frontier-6.adva).

Two further `learn` programs now keep the reality-facing act of problem
formation separate from finite value search. The first turns the concrete
three-of-five custody overlap defect and externally proposed imagination
directions into a falsifiable formed problem. The second searches 160 declared
threshold/feature candidates and retains the first noncompensating witness:
four-of-five receipts, all five features, and at least two honest shared domains
after one adversarial fault. This is a replayable policy-shape witness, not a
proof of deployed independence, truth, consent, or social trust. See
[`docs/research/0122-problem-formation-value-seeking-trust-continuation.md`](0122-problem-formation-value-seeking-trust-continuation.md),
[ADR 0032](../adr/0032-problem-formation-and-value-seeking.md), and
[`programs/bootstrap-0/value-seeking-1.adva`](../../programs/bootstrap-0/value-seeking-1.adva).

Historical and philosophical source notes are kept separately in
[`docs/philosophy/`](../philosophy/README.md). They preserve the path from
Leibniz's universal characteristic to the finite-observer open/close-hole
hypothesis and its falsifiable experiment agenda. These notes provide
interpretive research context only; they add no stable semantics or
registered executable claims.

Mingli Yuan's **Geometry of Truth** hypothesis organizes the interface among
physical measurement and scale, mathematical form, and logical language with
human-supplied names. Its attribution, working method, and open coherence
conditions are recorded in
[Research 0125](0125-geometry-of-truth-interface-hypothesis.md).

### Scoped trace projection

The scoped trace-projection continuation supplies a positive temporal count
factorization and a finite obstruction to recovering the full construction
code from the current time and space projections. Both are checked in Rust,
retain the original paths and five open questions, and are replayed in CI.
See [Research 0124](0124-trace-count-factorization-and-construction-obstruction.md)
and [ADR 0033](../adr/0033-scoped-trace-projection-witnesses.md).

---

## Complete listing

Every file in this directory, so that no note is reachable only through a summary.


### Numbered notes

- [`0001-paired-spectral-objectification.md`](0001-paired-spectral-objectification.md)
- [`0002-affine-exp-observer-spectrum.md`](0002-affine-exp-observer-spectrum.md)
- [`0003-affine-boundary-two-jet-faithfulness.md`](0003-affine-boundary-two-jet-faithfulness.md)
- [`0004-whole-cut-program-cells.md`](0004-whole-cut-program-cells.md)
- [`0005-causal-cut-alexandrov-topology.md`](0005-causal-cut-alexandrov-topology.md)
- [`0006-frontier-transport-interchange.md`](0006-frontier-transport-interchange.md)
- [`0007-occurrence-affine-cut-lift.md`](0007-occurrence-affine-cut-lift.md)
- [`0008-three-aspect-scalar-trichotomy.md`](0008-three-aspect-scalar-trichotomy.md)
- [`0009-three-aspect-chirality-carrier.md`](0009-three-aspect-chirality-carrier.md)
- [`0010-causal-cut-chirality-cube.md`](0010-causal-cut-chirality-cube.md)
- [`0011-causal-line-six-state-filtrations.md`](0011-causal-line-six-state-filtrations.md)
- [`0012-real-paraxial-optics-first-experiment.md`](0012-real-paraxial-optics-first-experiment.md)
- [`0013-optical-closure-observer-tower.md`](0013-optical-closure-observer-tower.md)
- [`0014-parameterized-optical-sensitivity.md`](0014-parameterized-optical-sensitivity.md)
- [`0015-occurrence-backward-probe-pairing.md`](0015-occurrence-backward-probe-pairing.md)
- [`0016-expression-valued-backward-transport.md`](0016-expression-valued-backward-transport.md)
- [`0017-symbolic-cut-composition.md`](0017-symbolic-cut-composition.md)
- [`0018-exponential-symbolic-cut-composition.md`](0018-exponential-symbolic-cut-composition.md)
- [`0019-symbolic-probe-matrix-shadow.md`](0019-symbolic-probe-matrix-shadow.md)
- [`0020-e0-dual-cut-surgery.md`](0020-e0-dual-cut-surgery.md)
- [`0021-surreal-cut-objectification-no-go.md`](0021-surreal-cut-objectification-no-go.md)
- [`0022-certified-graft-trace-wp1.md`](0022-certified-graft-trace-wp1.md)
- [`0023-exact-program-slice-wp2.md`](0023-exact-program-slice-wp2.md)
- [`0024-exact-program-slice-composition-wp3.md`](0024-exact-program-slice-composition-wp3.md)
- [`0025-exhaustive-independent-slice-laws-wp4.md`](0025-exhaustive-independent-slice-laws-wp4.md)
- [`0026-read-only-python-program-slices-wp5.md`](0026-read-only-python-program-slices-wp5.md)
- [`0027-zero-event-scope-cut-incidence-no-go.md`](0027-zero-event-scope-cut-incidence-no-go.md)
- [`0028-relational-psp-factorization.md`](0028-relational-psp-factorization.md)
- [`0029-nonzero-ordered-frame-relational-psp.md`](0029-nonzero-ordered-frame-relational-psp.md)
- [`0030-nested-frame-shared-surgery-gluing.md`](0030-nested-frame-shared-surgery-gluing.md)
- [`0031-e0-nested-decorated-surgery-psp.md`](0031-e0-nested-decorated-surgery-psp.md)
- [`0032-exact-e0-mobius-cellular-bridge.md`](0032-exact-e0-mobius-cellular-bridge.md)
- [`0033-omega-type-computational-boundary.md`](0033-omega-type-computational-boundary.md)
- [`0034-triangular-spectral-cusp-semantics.md`](0034-triangular-spectral-cusp-semantics.md)
- [`0035-decorated-handle-cobordism-calibration.md`](0035-decorated-handle-cobordism-calibration.md)
- [`0036-triangular-symbolic-interpretation-learning-calculus.md`](0036-triangular-symbolic-interpretation-learning-calculus.md)
- [`0037-finite-observer-tricusp-surreal-reduction.md`](0037-finite-observer-tricusp-surreal-reduction.md)
- [`0038-triadic-characteristic-inference-calibration.md`](0038-triadic-characteristic-inference-calibration.md)
- [`0039-square-map-branch-copy-calibration.md`](0039-square-map-branch-copy-calibration.md)
- [`0040-cube-equivariance-degree-calibration.md`](0040-cube-equivariance-degree-calibration.md)
- [`0041-elliptic-isogeny-triadic-characteristics.md`](0041-elliptic-isogeny-triadic-characteristics.md)
- [`0042-atiyah-legendre-triadic-crossing.md`](0042-atiyah-legendre-triadic-crossing.md)
- [`0043-legendre-crossing-coherence-prism.md`](0043-legendre-crossing-coherence-prism.md)
- [`0043-path-bound-interpretation.md`](0043-path-bound-interpretation.md)
- [`0043-scale-marked-surface-exploration.md`](0043-scale-marked-surface-exploration.md)
- [`0044-finite-triadic-satisfaction-logic.md`](0044-finite-triadic-satisfaction-logic.md)
- [`0045-logic-as-learned-characteristic.md`](0045-logic-as-learned-characteristic.md)
- [`0046-proposal-for-logic-on-a-3-form.md`](0046-proposal-for-logic-on-a-3-form.md)
- [`0047-a1-nodal-through-crossing-geometry.md`](0047-a1-nodal-through-crossing-geometry.md)
- [`0048-cellular-annulus-nodal-torus-dehn-twist.md`](0048-cellular-annulus-nodal-torus-dehn-twist.md)
- [`0048-directional-energy-of-a-learned-characteristic.md`](0048-directional-energy-of-a-learned-characteristic.md)
- [`0049-triadic-universal-computation-form-plan.md`](0049-triadic-universal-computation-form-plan.md)
- [`0050-bounded-triadic-labs-search.md`](0050-bounded-triadic-labs-search.md)
- [`0050-finite-triadic-residual-activation.md`](0050-finite-triadic-residual-activation.md)
- [`0051-finite-context-generated-proposition-algebra.md`](0051-finite-context-generated-proposition-algebra.md)
- [`0052-finite-state-transport-proof-no-go.md`](0052-finite-state-transport-proof-no-go.md)
- [`0053-finite-causal-presented-evidence.md`](0053-finite-causal-presented-evidence.md)
- [`0054-finite-linear-synchronized-evidence-tensor.md`](0054-finite-linear-synchronized-evidence-tensor.md)
- [`0054-triadic-sorting-network-witness-machine.md`](0054-triadic-sorting-network-witness-machine.md)
- [`0055-rust-checked-structural-evidence-bridge.md`](0055-rust-checked-structural-evidence-bridge.md)
- [`0056-rust-checked-triadic-generator-presentations.md`](0056-rust-checked-triadic-generator-presentations.md)
- [`0057-typed-vacua-constant-boundary-braids.md`](0057-typed-vacua-constant-boundary-braids.md)
- [`0058-checked-gate-braid-composition.md`](0058-checked-gate-braid-composition.md)
- [`0059-tri-bracket-eigen-normalization-logic.md`](0059-tri-bracket-eigen-normalization-logic.md)
- [`0060-checked-bracket-observer-bridge.md`](0060-checked-bracket-observer-bridge.md)
- [`0061-lineage-aware-bracket-events.md`](0061-lineage-aware-bracket-events.md)
- [`0066-self-dual-characteristic-completion-calculus.md`](0066-self-dual-characteristic-completion-calculus.md)
- [`0067-circular-three-form-interface-duality.md`](0067-circular-three-form-interface-duality.md)
- [`0068-finite-circular-overlap-transport.md`](0068-finite-circular-overlap-transport.md)
- [`0069-program-slice-grounded-bracket-reversal.md`](0069-program-slice-grounded-bracket-reversal.md)
- [`0070-typed-surreal-through-forms.md`](0070-typed-surreal-through-forms.md)
- [`0071-figure-eight-through-characteristic.md`](0071-figure-eight-through-characteristic.md)
- [`0072-pq-unit-tangent-through-geometry.md`](0072-pq-unit-tangent-through-geometry.md)
- [`0073-checked-boundary-return-feedback-no-go.md`](0073-checked-boundary-return-feedback-no-go.md)
- [`0074-three-layer-research-machine-v0.md`](0074-three-layer-research-machine-v0.md)
- [`0075-grounded-multi-hole-through-adapter-v0.md`](0075-grounded-multi-hole-through-adapter-v0.md)
- [`0076-three-angle-single-diagram-calibration.md`](0076-three-angle-single-diagram-calibration.md)
- [`0077-typed-connector-trichotomy-v0.md`](0077-typed-connector-trichotomy-v0.md)
- [`0078-distributivity-characteristic-dual-read-v0.md`](0078-distributivity-characteristic-dual-read-v0.md)
- [`0079-typed-hole-open-close-calibration-v0.md`](0079-typed-hole-open-close-calibration-v0.md)
- [`0080-finite-surface-universal-lift-imagination.md`](0080-finite-surface-universal-lift-imagination.md)
- [`0081-relative-halt-exploration-threaded-compactification.md`](0081-relative-halt-exploration-threaded-compactification.md)
- [`0082-threaded-finite-logic-adequacy.md`](0082-threaded-finite-logic-adequacy.md)
- [`0083-triadic-conflict-aperture-completion.md`](0083-triadic-conflict-aperture-completion.md)
- [`0084-threaded-natural-deduction-entailment-cell.md`](0084-threaded-natural-deduction-entailment-cell.md)
- [`0085-ordered-substitution-cut-beta-ledger-boundary.md`](0085-ordered-substitution-cut-beta-ledger-boundary.md)
- [`0086-contextual-beta-ledger-transport-strong-normalization.md`](0086-contextual-beta-ledger-transport-strong-normalization.md)
- [`0087-typed-three-domain-threaded-multihole-calculus.md`](0087-typed-three-domain-threaded-multihole-calculus.md)
- [`0088-historical-distributivity-character-v0.md`](0088-historical-distributivity-character-v0.md)
- [`0089-failure-frontiers-observer-relative-closure.md`](0089-failure-frontiers-observer-relative-closure.md)
- [`0090-prefix-frontier-closure-calibration-plan.md`](0090-prefix-frontier-closure-calibration-plan.md)
- [`0091-endogenous-scope-breakthrough-and-venture-ledger.md`](0091-endogenous-scope-breakthrough-and-venture-ledger.md)
- [`0092-generative-distributivity-venture-calibration-plan.md`](0092-generative-distributivity-venture-calibration-plan.md)
- [`0093-beta-history-local-confluence-audit-2-cells.md`](0093-beta-history-local-confluence-audit-2-cells.md)
- [`0094-focused-normal-forms-subformula-decidable-derivability.md`](0094-focused-normal-forms-subformula-decidable-derivability.md)
- [`0095-bootstrap-zero-geometric-threading-syntax.md`](0095-bootstrap-zero-geometric-threading-syntax.md)
- [`0096-boolean-triangle-placement-language-alignment.md`](0096-boolean-triangle-placement-language-alignment.md)
- [`0097-threading-syntax-typed-braid-alignment.md`](0097-threading-syntax-typed-braid-alignment.md)
- [`0098-multihole-am-type-formation-constraints.md`](0098-multihole-am-type-formation-constraints.md)
- [`0099-axis-circle-pendulum-history-syntax.md`](0099-axis-circle-pendulum-history-syntax.md)
- [`0100-bootstrap-zero-syntax-factor-inventory-and-seam-repairs.md`](0100-bootstrap-zero-syntax-factor-inventory-and-seam-repairs.md)
- [`0101-six-port-whole-cut-theory.md`](0101-six-port-whole-cut-theory.md)
- [`0102-bootstrap-zero-whole-cut-grammar.md`](0102-bootstrap-zero-whole-cut-grammar.md)
- [`0102-production-ledger-followup.md`](0102-production-ledger-followup.md)
- [`0102-retention-and-declaration-followup.md`](0102-retention-and-declaration-followup.md)
- [`0103-cell-carrier-view-relation-machines.md`](0103-cell-carrier-view-relation-machines.md)
- [`0104-whole-cut-six-to-m6-boundary-bridge.md`](0104-whole-cut-six-to-m6-boundary-bridge.md)
- [`0105-q4-m6-go-search-research-program.md`](0105-q4-m6-go-search-research-program.md)
- [`0106-ontological-programming-type-barriers.md`](0106-ontological-programming-type-barriers.md)
- [`0106-three-hole-conjugate-m6-projective-lift.md`](0106-three-hole-conjugate-m6-projective-lift.md)
- [`0107-reusable-six-word-witness-kernel.md`](0107-reusable-six-word-witness-kernel.md)
- [`0108-graft-derived-witness-instantiation.md`](0108-graft-derived-witness-instantiation.md)
- [`0109-neutral-carrier-triadic-mechanism-frontiers.md`](0109-neutral-carrier-triadic-mechanism-frontiers.md)
- [`0110-neutral-adva-document-load-save.md`](0110-neutral-adva-document-load-save.md)
- [`0111-group-neutral-operations-and-q4-m6-relation-profiles.md`](0111-group-neutral-operations-and-q4-m6-relation-profiles.md)
- [`0112-transition-frame-relation-path-adapter.md`](0112-transition-frame-relation-path-adapter.md)
- [`0113-first-bounded-m6-reveal-run.md`](0113-first-bounded-m6-reveal-run.md)
- [`0114-three-sided-trace-arithmetic-calibration.md`](0114-three-sided-trace-arithmetic-calibration.md)
- [`0115-frontier-hypothesis-interface-experiment.md`](0115-frontier-hypothesis-interface-experiment.md)
- [`0116-reality-custody-continuation-experiment.md`](0116-reality-custody-continuation-experiment.md)
- [`0117-obligation-refinement-verification-boundary.md`](0117-obligation-refinement-verification-boundary.md)
- [`0118-local-closure-transport-and-adversarial-naming.md`](0118-local-closure-transport-and-adversarial-naming.md)
- [`0119-characteristic-magic-square-closure-family.md`](0119-characteristic-magic-square-closure-family.md)
- [`0120-trust-continuity-m6-closure-gate.md`](0120-trust-continuity-m6-closure-gate.md)
- [`0121-six-crossing-hypothesis-formation-search-word.md`](0121-six-crossing-hypothesis-formation-search-word.md)
- [`0122-problem-formation-value-seeking-trust-continuation.md`](0122-problem-formation-value-seeking-trust-continuation.md)
- [`0123-arithmetic-universality-and-hypothesized-truth.md`](0123-arithmetic-universality-and-hypothesized-truth.md)
- [`0124-trace-count-factorization-and-construction-obstruction.md`](0124-trace-count-factorization-and-construction-obstruction.md)
- [`0125-geometry-of-truth-interface-hypothesis.md`](0125-geometry-of-truth-interface-hypothesis.md)
- [`0126-knowledge-geometry-first-interface-witness.md`](0126-knowledge-geometry-first-interface-witness.md)
- [`0127-finite-vocabulary-gradient-and-checked-reuse.md`](0127-finite-vocabulary-gradient-and-checked-reuse.md)
- [`0128-acceleration-direction-pascal-incidence.md`](0128-acceleration-direction-pascal-incidence.md)
- [`0129-bounded-breakthrough-trusted-boundaries.md`](0129-bounded-breakthrough-trusted-boundaries.md)
- [`0130-prefix-coverage-gated-close.md`](0130-prefix-coverage-gated-close.md)
- [`0131-finite-learner-judgment-and-reuse.md`](0131-finite-learner-judgment-and-reuse.md)
- [`0132-structural-adjustment-evidence-applicability.md`](0132-structural-adjustment-evidence-applicability.md)
- [`0133-explore-open-universe-goal-relative-stopping.md`](0133-explore-open-universe-goal-relative-stopping.md)
- [`0134-three-turn-revise-and-local-close.md`](0134-three-turn-revise-and-local-close.md)
- [`0135-reunderstanding-resource-frames-and-fuel.md`](0135-reunderstanding-resource-frames-and-fuel.md)
- [`0136-native-learn-guarded-roundtrip.md`](0136-native-learn-guarded-roundtrip.md)
- [`0137-self-interpretation-boundary.md`](0137-self-interpretation-boundary.md)
- [`0138-world-task-boundary.md`](0138-world-task-boundary.md)
- [`0139-library-six-phase-and-communication.md`](0139-library-six-phase-and-communication.md)
- [`0140-native-program-run.md`](0140-native-program-run.md)
- [`0141-representation-residual.md`](0141-representation-residual.md)
- [`0142-question-indexed-distinguish.md`](0142-question-indexed-distinguish.md)
- [`0143-distinction-knowledge-and-free-boundary.md`](0143-distinction-knowledge-and-free-boundary.md)
- [`0144-research-across-tool-representation-and-crossing-boundaries.md`](0144-research-across-tool-representation-and-crossing-boundaries.md)
- [`0145-preservation-contract-and-finite-splitting.md`](0145-preservation-contract-and-finite-splitting.md)
- [`0146-private-merge-and-value-direction.md`](0146-private-merge-and-value-direction.md)
- [`0147-universe-prime-and-finite-extension.md`](0147-universe-prime-and-finite-extension.md)
- [`0148-finalize-and-python-adva-entry.md`](0148-finalize-and-python-adva-entry.md)
- [`0149-library-stability-and-zigzag.md`](0149-library-stability-and-zigzag.md)
- [`0150-persistent-library-epochs.md`](0150-persistent-library-epochs.md)
- [`0151-library-driven-proposal-feedback.md`](0151-library-driven-proposal-feedback.md)
- [`0152-continuation-01.md`](0152-continuation-01.md)
- [`0152-three-verifier-residual-search.md`](0152-three-verifier-residual-search.md)
- [`0153-frozen-verifier-search-campaign.md`](0153-frozen-verifier-search-campaign.md)
- [`0154-math-catalog-and-task-loop-boundary.md`](0154-math-catalog-and-task-loop-boundary.md)
- [`0155-cryptographic-sealing-and-calibration-boundary.md`](0155-cryptographic-sealing-and-calibration-boundary.md)
- [`0156-review-decision-draft.md`](0156-review-decision-draft.md)
- [`0156-tamper-evident-arithmetic-lineage.md`](0156-tamper-evident-arithmetic-lineage.md)
- [`0157-free-acceptance-predicate-candidate.md`](0157-free-acceptance-predicate-candidate.md)
- [`0158-downward-interpretation-and-drop-route.md`](0158-downward-interpretation-and-drop-route.md)
- [`0158-opening-equation-and-anchor-binding.md`](0158-opening-equation-and-anchor-binding.md)
- [`0159-frame-symmetry-triadic-continuation.md`](0159-frame-symmetry-triadic-continuation.md)
- [`0160-faithful-switch-and-reverse-observer-search.md`](0160-faithful-switch-and-reverse-observer-search.md)
- [`0161-advance-receipts-and-iota-substrate-projection.md`](0161-advance-receipts-and-iota-substrate-projection.md)
- [`0162-bounded-advance-loop.md`](0162-bounded-advance-loop.md)
- [`0163-evidence-stutter-and-progress-gate.md`](0163-evidence-stutter-and-progress-gate.md)
- [`0164-paired-quotation-quine-relay.md`](0164-paired-quotation-quine-relay.md)
- [`0165-two-documents-interpretation-relation.md`](0165-two-documents-interpretation-relation.md)
- [`0166-interpretation-obligation.md`](0166-interpretation-obligation.md)
- [`0167-li-yorke-period-three-and-homotopy-continuation.md`](0167-li-yorke-period-three-and-homotopy-continuation.md)
- [`0167-iota-lang-reconnection-audit.md`](0167-iota-lang-reconnection-audit.md)
- [`0168-triadic-cycle-and-continuation-discipline.md`](0168-triadic-cycle-and-continuation-discipline.md)
- [`0168-switch-swap-and-braid-under-the-iota-substrate.md`](0168-switch-swap-and-braid-under-the-iota-substrate.md)
- [`0169-arakelov-stability-monge-ampere-mirror-ladder.md`](0169-arakelov-stability-monge-ampere-mirror-ladder.md)
- [`0170-mobius-conjugacy-and-observer-transport.md`](0170-mobius-conjugacy-and-observer-transport.md)
- [`0171-density-wave-marginal-wall-and-the-nonlocality-of-self-gravity.md`](0171-density-wave-marginal-wall-and-the-nonlocality-of-self-gravity.md)
- [`0172-the-i-minus-e-integrality-conjecture.md`](0172-the-i-minus-e-integrality-conjecture.md)
- [`0173-mirrors-that-never-close-and-a-question-to-a-waking-ai.md`](0173-mirrors-that-never-close-and-a-question-to-a-waking-ai.md)
- [`0174-absurdity-emptiness-counterexample.md`](0174-absurdity-emptiness-counterexample.md)
- [`0175-dodecahedral-hamiltonicity.md`](0175-dodecahedral-hamiltonicity.md)
- [`0176-feigenbaum-period-doubling-calibration.md`](0176-feigenbaum-period-doubling-calibration.md)
- [`0177-feigenbaum-fixed-point-collocation.md`](0177-feigenbaum-fixed-point-collocation.md)
- [`0178-rigorous-enclosures-and-two-barriers.md`](0178-rigorous-enclosures-and-two-barriers.md)
- [`0179-kantorovich-preflight.md`](0179-kantorovich-preflight.md)
- [`0180-inverse-norm-obstruction.md`](0180-inverse-norm-obstruction.md)
- [`0181-wu-elimination-on-plane-incidence.md`](0181-wu-elimination-on-plane-incidence.md)
- [`0182-wu-elimination-general-conic.md`](0182-wu-elimination-general-conic.md)
- [`0183-zhang-finite-example-verification.md`](0183-zhang-finite-example-verification.md)
- [`0184-area-method-readable-proofs.md`](0184-area-method-readable-proofs.md)
- [`0185-yang-difference-substitution-inequalities.md`](0185-yang-difference-substitution-inequalities.md)
- [`0186-dual-facility-leak-wall.md`](0186-dual-facility-leak-wall.md)
- [`0187-cut-linkage-after-cutting.md`](0187-cut-linkage-after-cutting.md)
- [`0188-aeg-core-shell-notation-registered-as-a-target.md`](0188-aeg-core-shell-notation-registered-as-a-target.md)
- [`0189-core-shell-and-symbolically-unexpanded-shell.md`](0189-core-shell-and-symbolically-unexpanded-shell.md)
- [`0190-the-multivariate-rung-of-the-historical-method.md`](0190-the-multivariate-rung-of-the-historical-method.md)
- [`0191-the-read-boundary-splits-the-mass-in-half.md`](0191-the-read-boundary-splits-the-mass-in-half.md)
- [`0192-the-traversal-allocation-and-its-reserve.md`](0192-the-traversal-allocation-and-its-reserve.md)
- [`0193-the-optimal-shares-and-the-price-of-a-level.md`](0193-the-optimal-shares-and-the-price-of-a-level.md)
- [`0194-the-measured-key-and-certificate-cost.md`](0194-the-measured-key-and-certificate-cost.md)
- [`0195-the-join-measured.md`](0195-the-join-measured.md)
- [`0196-the-protocol-as-a-checkable-declaration.md`](0196-the-protocol-as-a-checkable-declaration.md)
- [`0197-the-protocol-without-a-magic-number.md`](0197-the-protocol-without-a-magic-number.md)
- [`0198-the-protocol-ledger-and-why-the-partition-does-not-transfer.md`](0198-the-protocol-ledger-and-why-the-partition-does-not-transfer.md)
- [`0199-declaring-the-two-spaces.md`](0199-declaring-the-two-spaces.md)
- [`0200-the-depth-curve-from-retained-evidence.md`](0200-the-depth-curve-from-retained-evidence.md) — see the 2026-09-15 correction: current halting uncertainty is in `depth_curve/evidence-v1.json`; v0 remains historical.
- [`0201-two-curves-on-one-cost-axis.md`](0201-two-curves-on-one-cost-axis.md)
- [`0202-does-a-step-close-more-than-it-opens.md`](0202-does-a-step-close-more-than-it-opens.md)
- [`0203-allocating-the-three-currencies.md`](0203-allocating-the-three-currencies.md)
- [`0204-gold-twin-timeout-is-not-negative.md`](0204-gold-twin-timeout-is-not-negative.md)
- [`0205-implementation-failure-is-not-a-counterexample.md`](0205-implementation-failure-is-not-a-counterexample.md)
- [0206 — Compatible history surfaces](0206-compatible-history-surfaces.md): finite reconstruction, compatible readback and bounded correction; [Chinese companion](../../experiments/history_surface/learning.zh.md).
- [0207 — 可判定实验：`constructive` 的零贡献是作用退化，还是调度饥饿？](0207-constructive-starvation-and-budget-matched-control.md): 首个归因尝试；被 0208 取代。
- [0208 — `constructive` 饥饿的机制：两道门（修正版）](0208-constructive-scheduling-two-gates-correction.md): 资格窗 × UCB 两道门；取代 0207，被 0209 取代。
- [0209 — `constructive` 的零贡献：测量假象，而非退化](0209-constructive-zero-is-a-measurement-artifact.md): `best_updates` 不承载该程序的作用；取代 0208，被 0210 取代。
- [0210 — `constructive` 的贡献：三个假设的判定](0210-constructive-contribution-is-zero-at-measurable-resolution.md): n=82 消融无效应，零贡献在可测范围内为真；取代 0209。
- [0211 — Six places, two alphabets, and the policy of a finite arithmetic truth](0211-six-places-two-alphabets-and-the-policy-of-a-finite-arithmetic-truth.md): two declared pairings on six places generate a regular group of order six, the inner-four reading's eventual image is two rest states and one two-cycle, the 64-state and 729-address interfaces read each other one way only, and the classical four-outcome table of the declared split arithmetic is reproduced by one of three natural policies and by no other. No text is imported and no classical name is attached.
- [0212 — What a declared invariance already fixes](0212-what-a-declared-invariance-already-fixes.md): on one tetrahedron the three axis swaps form a group of order four whose edge orbits are the three opposite-edge pairs, while the four face mirrors generate an infinite closure whose finite part is exactly the origin stabiliser; a rank-one co-occurrence table has one argmax column for every row and a diagonal share above chance with zero row-specific information; the optimal assignment is margin-determined too; and the exact permutation null of the reciprocity statistic is a function of the two margins alone. 
- [0213 — Gain, coverage, and the number that was already fixed](0213-gain-coverage-and-the-number-that-was-already-fixed.md): the octave reduction of a serial number is the quotient by doubling, so the exact hits of any equal division are the powers of two and their count is a function of the limit alone; the covering radius of the twenty-two-fold division is exactly one forty-fourth, so the reported maximum distance is trivial, and full coverage is reached at the odd serial-number index bound one hundred thirteen at one percent and one thousand two hundred thirty-seven at a tenth of a percent, that is at fifty-seven and six hundred nineteen odd points, which predicts the reported coverage from the declared serial-number limit; and a class gain and a class spread order five declared rows differently, with the exact rank correlation minus one tenth. No text and no corpus count is imported.
- [0214 — What a four-trit address carries, and no shift pairs it](0214-what-a-four-trit-address-carries-and-no-shift-pairs-it.md): in the four-place ternary address space no nonzero shift is an involution, because twice a shift vanishes modulo two for every shift and modulo three only for the identity, so a difference histogram cannot describe a pairing while the same arithmetic makes every binary shift a pairing; a pairing of eighty-one heads is bounded at forty pairs and four reported pair counts exceed it; four ternary places carry sixteen of the sixty-four configurations placewise and at most thirty-six coordinate-wise while six places carry all sixty-four; a coordinate order has an exact carry profile, and four declared step relations give four different single-place shares. No text and no corpus count is imported.
- [0215 — The magic square exists, and the address is not it](0215-the-magic-square-exists-and-the-address-is-not-it.md): the address formula forces a nine by nine grid whose entry is nine r plus c plus one; that grid is not magic, yet its middle row, middle column and both diagonals are exact arithmetic progressions that all reach the magic constant 369, four lines out of twenty; the affine family reproduces the magic constant as a formula, counts eight, one thousand four hundred seventy-two and three thousand five hundred twenty-eight magic squares at orders three, five and nine with the standard construction sharing one coefficient matrix across all of them, and contains none at even orders; and preserving none of thirty-five pairs is what a random permutation does at least three fifths of the time. No text and no corpus count is imported.
- [0216 — The magic hypercube, and a cut the address cannot see](0216-the-magic-hypercube-and-a-cut-the-address-cannot-see.md): an affine construction on the four ternary places is a permutation exactly when its matrix is invertible, and all one hundred eight coordinate lines are constant exactly when every entry is nonzero — sufficient by full exhaustion of the sixty-five thousand five hundred thirty-six zero-free matrices and necessary on a declared family of twenty-two thousand four hundred forty, giving twenty-two thousand two hundred seventy-two distinct magic hypercubes; the construction is magic along coordinate lines only, its eight main diagonals taking five different sums, while at two places the shift and not the matrix buys the diagonals of the classical square; and the split of the eighty-one heads at forty-seven is separated by no proper subset of the four places. No text and no corpus count is imported.
- [0217 — What the address sees, and what the grid already forces](0217-what-the-address-sees-and-what-the-grid-already-forces.md): the formula the source text states for the head number reproduces the coordinate formula on all eighty-one heads; the text's own nine-fold series is exactly the heads with two of the four places fixed, so the address sees it at a glance, while the split at forty-seven is a union of residue classes for no modulus below eighty-one, so a second algebra is blind to it too; the text's own pairing carries the seven/eight boundary to the forty-seven/forty-eight boundary by one displacement of order three; the river diagram's pairing is the reduction modulo five, with five left without a partner once the range is the nine numbers; and the reported calendar near miss ranks fourteenth of twenty-three, since a grid of four-and-a-half-day boundaries puts every node within nine quarters of a day of one. No text and no corpus count is imported.
- [0218 — A definability theorem, and a sweep declared in the contract](0218-a-definability-theorem-and-a-pre-registered-property-sweep.md): a set of the eighty-one heads definable by k of the four ternary places has size divisible by three to the four minus k, so the split at forty-seven, the other side of thirty-four and the two prison heads all need all four places by arithmetic rather than by search — while the bound is necessary and not sufficient, two sets of size three needing three and four places respectively; the chance that a property of a given size contains a given set of heads is exact inclusion and exclusion, so a nine-praise property hits 8.61 heads and meets two given heads about one time in a hundred; a declared sweep of one hundred twenty pairs reports thirty-four containments against 8.29 expected and shows the uniform null under-predicting for evenly spread properties; the coincidence that prompted the question is about one per cent, thirty-three times the single-probe price first reported, and ninety of the one hundred twenty declared pairs are at least as unlikely; and the same-cycle relation on the address space is total and therefore vacuous. No text and no corpus count is imported.
- [0219 — The definability spectrum of the address algebra](0219-the-definability-spectrum-of-the-address-algebra.md): the algebra of sets a subset of the four ternary places can express has two to the three to the k sets, so the spectrum runs two, eight, five hundred twelve, one hundred thirty four million and the whole power set, and only levels up to two are small enough to enumerate; their union is exactly three thousand fourteen sets, every one of a size divisible by nine, and the size distribution is symmetric because complements are expressible too; the price of a declared division is the ratio of its same-size rivals at its own level to all sets of that size, which gives the nine district representatives one of fifty four out of two hundred sixty billion and the first quarter one of twelve out of a number with twenty two digits — and that smallest price belongs to the first quarter, the division at the weakest level that has a non-trivial rival count, while the nought-place level prices the whole head set at one, so the ratio measures the level and not the division; a set needing all four places meets every set of its size and is priced at one, which makes that end of the spectrum vacuous; the nine are a block of the last two places, the three of the last three, and the organisation by the last places is recorded and not explained; and the first version of the checker counted the quarter's rivals against the two-place union and reported four hundred eighty instead of twelve, which is recorded rather than repaired. No text and no corpus count is imported.
- [0220 — What a declared family and a declared shift already fix](0220-what-a-declared-family-and-a-declared-shift-already-fix.md): the price of an arithmetic hit is the coverage of the declared expression family, four hundred ninety-seven of the seven hundred twenty-nine praises for the thirteen constants already declared, and the coverage is monotone in the constant set so a unique hit can only be destroyed by adding constants and never created; the first n consecutive integers name exactly the first ten n praises, so seventy-three of them name every praise and a target that is itself a declared constant is named by the bare form, which is why the constant set must exclude its target; one hundred seventy-three of the reached praises are named exactly once, so uniqueness is the common case; a declared greedy reaches everything with fourteen constants while counting the forms forces at least seven, and the smallest covering set is not decided; varying only the multiplier range moves the coverage from two hundred twenty-three to six hundred sixty-four, so a family that does not declare that range has no computable price; and for a declared shift of forty the pairs number forty-one with seven inside the cut at forty-seven and thirty-four straddling it, but the crossing count equals the size of the cut's second side at forty of the eighty cuts, so the agreement is an identity of the shift and the only distinguished cut is forty-one; the shift is eleven eleven in base three, so the coordinate difference is constant at exactly sixteen of the forty-one pairs, and the recorded figures of thirteen of thirty-five cannot be reproduced from the stated law. No text and no corpus count is imported.
- [0221 — Which readings of a modal property argument are impossible](0221-which-readings-of-a-modal-property-argument-are-impossible.md): over a declared finite semantics with at most three worlds, one individual and the complete algebra of properties, every model of four frame classes and every subset of seven declared axiom schemata is enumerated, and the lemma that carries the rest is that necessary existence holds exactly at the worlds that see only themselves, with no exception in eighteen thousand five hundred eight models; the first two axioms do not force the conclusion, since one thousand seven hundred twenty-eight models satisfy them at three worlds and only two hundred sixteen satisfy the conclusion; no subset of the seven axioms forces it outside the symmetric frames, and a three-world countermodel satisfying every axiom is retained, so the symmetry of the accessibility relation is doing the work; over the symmetric frames exactly the subsets containing the axiom of necessary existence force the conclusion and each leaves exactly one model, so that axiom is the most restrictive of the seven rather than the most informative; over the three axioms of negation, entailment and necessary existence there are eighty-six models and in all of them the conclusion holds exactly when every property is constant, so the conclusion and the collapse of the modality are the same condition, and the single symmetric model left is the frame in which no world sees another, where positivity carries no information; essence collapses to having the property; uniqueness is not expressible because the declared family contains no identity predicate; and with one world all one hundred twenty-eight subsets force the conclusion, the empty set included. No text, no corpus count and no published verdict is imported.
- [0222 — 壳层密度何时超过其电子数：闭式判据、两个活通道，和一个不可能失败的通道](0222-shell-density-hump-criterion.md): `D_max = c(n,occ)·ζ`，`D_max > Z ⇔ ζ/Z > 1/c`；K 壳回到 `4/e²`、`8/e²`、峰位 `x*=1`。Slater 屏蔽与峰位两条通道各 **22/22** 相符（预测不读峰高），峰高反推那条被演示为恒真并弃用；M 壳 `c ≤ 0.8061131 < 1`，故最多两壳可超 `Z`；起点 Be 由 Slater 单独预测得到（余量仅 1.2e-4）。
- [0223 — Surreal order and the tear](0223-surreal-order-and-the-tear.md): one nine-line descent criterion, quoted from the helgoland tear witness and inlined rather than restated, is applied to finite surreal cut presentations, and it separates the clock that descends through the state map from the clock that tears; over three hundred thirty-one thousand seven hundred seventy-six pairs of the enumerated forms the order clock has no mismatching pair and the same-value pairs are mutually comparable, while the presentation-day clock tears and a witness pair is retained, so the day is a property of the presentation and not of the value it presents; zero is presented on day zero once, on day two three times and on day three sixty times, and the family ( | n ) presents zero on day n plus one for every n, so the fibre over a value is not finite; the day-d class holds two to the d numbers and its L/R address spends exactly d bits, which is saturation rather than resolution, so the address clock has no resolution inside a value slice. No text and no corpus count is imported.
- [0224 — Four left-nested pure-iota frames](0224-four-left-nested-iota-frames.md): holding `e` and `i` fixed and replacing the third slot of the received frame by the four left-nested towers with one, three, five and seven iota leaves, all four reduce to the single leaf `i` in zero, five, ten and fifteen local contractions, so the four slots are one value and four ledgers; their cut sets are the prefixes of a total order, of size one, six, eleven and sixteen, so every induced cut graph is a path and no tower widens the causal geometry, while the carriers have dimension two, twelve, twenty-two and thirty-two and reach no carrier of dimension four; all four satisfy the frame's own `J`, `H`, row-sum and skewness checks, and the family grows by one five-event cell per pair of leaves; the k = 1 tower shares its cut count and carrier dimension with the received process `chain-and-single` while carrying a different operator, integral spectrum against irrational; and none of the four towers carries an aperture leaf, so the frame's declared construction, space and time roles are unbound and that obstruction is retained. No external corpus is opened.
- [0225 — A complex structure admits only even signatures](0225-a-complex-structure-admits-only-even-signatures.md): solving the received frame's compatibility condition `JᵀGJ = G` exactly shows the solutions form a space of dimension `2n²` whose symmetric part has dimension `n²`, every solution commuting with `J`, so a symmetric compatible metric is complex-linear and its inertia indices are even; exhaustively over three declared integer families of seven, two thousand four hundred one and nineteen thousand six hundred eighty-three members no nondegenerate member has an odd index, and on a four-dimensional carrier the reachable signatures are exactly `(4,0)`, `(2,2)` and `(0,4)`, so exactly one negative direction is unreachable while the complex structure stays metric-compatible; the frame's own metric makes the generator skew exactly while a declared Lorentzian metric does not, with both exact residuals retained, and the same Lorentzian metric is compatible with the declared involution, so a signature with exactly one negative direction is reachable once the structure is an involution rather than a complex structure. The note also retains the correction that an earlier reading of a split structure as necessarily giving two positives and two negatives is wrong, and that this reading was never published. No physical claim is made.
- [0226 — The Kerr line element is vacuum](0226-the-kerr-line-element-is-vacuum.md): the Kerr metric is declared in Boyer-Lindquist coordinates and its consequences are computed by a symbolic tensor calculus written for the experiment in the standard library alone, with the inverse metric and the time-phi block determinant verified exactly and the two symbolic derivatives calibrated against central differences to 2.77e-10 before any result is read; all sixteen Ricci components vanish identically as rational functions of the radius and the cosine of the polar angle for five declared parameter pairs including a spin above the mass; the Kretschmann scalar equals the declared closed form identically and reduces to 48 M squared over r to the sixth when the spin vanishes, which is the known value and therefore a check on the whole chain; the signature is three plus one at all six declared points, including inside the outer horizon, inside the ergosphere and inside the inner horizon, even though g_rr changes sign twice; and the horizon radii, the ergosphere, the extremality bound, the horizon area, the angular velocity, the surface gravity and the Smarr identity hold exactly in a declared quadratic field with pi carried as a symbol. The Einstein equations are not derived, no object is claimed to exist, and the experiment is not connected to the frame of notes 0224 and 0225.
- [0227 — What the involution route costs](0227-what-the-involution-route-costs.md): the boundary note 0225 handed over is decided exactly. The frame's own twelve-dimensional instance is rebuilt from the received process and reproduces its two identities through degree twelve before any structure is replaced; for a structure whose square is sigma times the identity the coefficient identity is `(-S)^k A_S^k = sigma^k H^k`, so the sign in the exponent is exactly the sign of the structure's square, and replacing the complex structure by an involution turns the received heat reading into its time reverse; on the declared four-dimensional carrier the involution is compatible with a metric of signature (3,1) and the generator is nevertheless not skew, with the exact residual retained; and on both declared instances the metrics that keep the involution compatible and the generator skew form a two-dimensional space every element of which is degenerate, decided at five sample values, so no nondegenerate metric of any signature buys both obligations at once. No physical claim is made and the run is not connected to the Kerr experiment of note 0226.
- [0228 — A Taixuan address hierarchy, its observers, and its spectra](0228-taixuan-hierarchy-observers-and-spectra.md): the full 6,561-point two-level four-coordinate family retains 81 coarse cells and exact detail, but unit-translation closure refines the block observation through 81, 1,296 and 6,561 classes. Two declared group laws on the same labels have different checked spectra. The note separates block subdivision from compatible translation phases and states conditional four-dimensional monotile obligations without asserting a geometric construction or native admission.

- [0229 — Spectral memory, local constraints, and weather errors](0229-spectral-memory-local-constraints-and-weather-errors.md): a declared synthetic coarse learner mistakes phase cancellation for damping; three-step memory repairs that family but fails a fourth-alias stress case. Exact finite witnesses separate power from local motif constraints without establishing an infinite monotile. Fixed xue development backtests retain mostly coarse error and mixed gains over seasonal baselines, with the user's data-authenticity reservation explicitly unresolved.

- [0230 — Native background correction and display interpolation](0230-native-background-forecast-and-display-interpolation.md): a bounded temporal-memory trial fails its fixed switch threshold; a separate training-only background correction reduces exposed development physical MSE while preserving old products. Independent grid replay and a real-shader vector overshoot witness separate model improvement, rendering behavior and unresolved source authenticity.
- [0231 — Frozen Japan jet review and Floquet scope](0231-frozen-japan-jet-and-floquet-scope.md): the requested December forecast is absent; the actual January URL has a geostrophically compatible monthly jet dominated by climatology, with small learned anomalies. Native-first and matched historical diagnostics separate representation effects, exposed development skill and the first ideal method’s conditional Floquet claim.
- [0232 — Floquet checks of the frozen first forecast](0232-floquet-checks-of-the-frozen-first-forecast.md): the actual one-step homogeneous extension contracts with annual spectral radius 0.09855, while the six direct lead maps fail propagation composition. Independent operator checks and realized-innovation decomposition preserve the ideal method’s conditional scope without making a real-atmosphere stability or forecast-skill claim.

- [0233 — Periodic programs before Floquet observations](0233-periodic-programs-before-floquet-observations.md): a proposed native-compatible annual A/M program profile retains exact finite variation, baseline defects and process order before extracting a first-degree Floquet observation; an original rational fixture passes 23 external arithmetic checks, without claiming native certificates or weather-model integration.

- [0234 — The rate of a periodic arithmetic program is its generator action](0234-the-rate-of-a-periodic-arithmetic-program-is-its-generator-action.md): a native Rust power–weight carrier `Φ_{ν,w}=a^νe^{(w−ν)v}` with exact `ℚ[exp(ℚ)]` coefficients, `A`/`M`/PBW laws and typed logarithmic and Jordan resonances reads the annual rate of the 0233 twelve-phase fixture as a generator action table rather than a Jacobian product; the multiplicative holonomy and the Addition reading at the reference agree exactly, declared flow phases force the exponential class, and no native Floquet calculus, matrix ontology or physical claim follows.

- [0235 — The cheapest exchange is not a collision, and no real loop swaps the branches](0235-the-cheapest-exchange-is-not-a-collision-and-no-real-loop-swaps-the-branches.md): an exact variational computation on the 0233 twelve-phase program finds the amplitude floor `J_inf = 1` attained in the interior at `(p,q) = (-2, 17/10)` rather than on the discriminant variety, whose degree-twelve 52-term factorisation is computed exactly with Wu-style case chains cross-checked by Gröbner bases; no declared real loop realises the transposition of the two real-root branches, which is why the first scheme needs its complexification and what the second scheme's time direction would have to supply.

- [0236 — Two addresses at once, three time conditions, and what the closure changes](0236-two-addresses-at-once-three-time-conditions-and-what-the-closure-changes.md): the two addresses of note 0228 are used simultaneously as two mutually measuring sides over all 6,561 points, and three declared time conditions are executed — an end block of exactly two extra states with both negative controls rejected by rule, the closure clause 終養始 read as the fixed point of the annual return, which leaves exactly one real exit where the level reading has two, and the crossing point with its three candidate amplitudes `2+sqrt(8 sqrt(17)-20)`, `8` and `1`; the block-address witness fails any coarse time iteration by itself, the extrusion countermodel is judged degenerate, and whether the time conditions change what is reachable is recorded as NotDecided.

- [0237 — Singularity surgery: opposite chirality, a raised flux, and two roles that fail when swapped](0237-singularity-surgery-opposite-chirality-a-raised-flux-and-two-roles.md): the declared surgery excises the discriminant collision and the annual seam, and the excised boundary has exactly two connected components carrying opposite-chirality spirals; the collar flux rises from 0 to 2 fully attributed, the outer role writes out and discharges the obstruction, the inner role arrives in 24 steps against a budget of 36, no resource is created, the memory layer is the deep one across all three cycles, and the projection is accepted only as a map; whether opposite chirality is necessary rather than merely declared is recorded as Undecided, because the rise is `w·n·(σ_O−σ_I)` and the declared tilt does as much work as the chirality.

- [0238 — Three chained annual cycles: every cycle closes, and the drift control fails to discriminate](0238-three-chained-annual-cycles-every-cycle-closes-and-the-drift-control-fails-to-discriminate.md): three cycles beginning at the December 2026/January 2027 seam are chained exactly with the closure amplitude as an exact element of its cubic field; each cycle is ClosedByFixedPoint with zero drift, the cumulative reading has no genuine real period-3 orbit, the end block holds exactly two steps and the step remainder is 6 of 33, all nine conditions carry an executed calamity counterpart, the slow component is conserved while the declared open-ocean variant loses the memory, and the drift control failed to discriminate and is retained as a failure.

- [0239 — The rounded ending: a conjunction that nets nothing, and a one-way commitment that sealing may not touch](0239-the-rounded-ending-a-conjunction-that-nets-nothing-and-a-one-way-commitment.md): the ending is 圆融, a conjunction in which the sealable component closes exactly at the fixed point while the committed component is carried out and written out, with four prohibitions each rejected by an executed control; the beginning splits into resetable obstructions and a non-resetable commitment, the middle carries two directed five-cycles, the chain of 1095 days closes none of 260, 2920 and 18980, the one-way reservoir is monotone and hysteretic while the parent's relaxation fails both controls, sealing is refused for the leak, and a four-by-two table classifies aerosols, low cloud, water vapour and wildfire on each side with no magnitude anywhere.

- [0240 — A proposal-only optical scheme, its three derived bounds, and one erratum the run itself cannot repair](0240-a-proposal-only-optical-scheme-its-derived-bounds-and-one-erratum.md): a 提议性方案 that would use mirrors for power, fibres for phase and a diffractive output for the light-dark geometry is calibrated exactly, separating derived bounds (passive spot floor `theta_sun*L`, the one-microvolt-per-mode étendue ceiling, the second-Lagrange-point antumbra) from declared constants and from proposal-only bookkeeping, with all six overreach controls rejected and both inherited prohibitions applied; the note also registers an erratum: the payload's usable-flux fraction pairs the Earth's angular radius with the Sun's angular diameter, so the correct usable fraction is about 0.149 rather than the reported 0.787, and everything downstream of it must be recomputed in a follow-up run.

- [0241 — The four proposals, the geometry foundation, and the stage-one calibration](0241-four-proposals-and-the-stage-one-calibration.md): the programme is recorded as four proposals - the spherical spectrum and its complexification, the four-dimensional spacetime monotile, a space proposal with freer orbits and lattice or Archimedean-solid placement matched to relativistic spacetime symmetry, and the geometry computation split out as the common foundational subject - with proposal four carrying the corrected usable fraction about 0.149 in place of the superseded 0.787, and with stage one fixed as calibration inside the December-January window followed by continuous learning, under the two invariants that the overall topology is not broken and that learning never stops.

- [0242 — A spatiotemporal ratchet: net transport needs both asymmetries, and the standing wave transports nothing](0242-a-spatiotemporal-ratchet-net-transport-needs-both-asymmetries.md): a declared six-site ring model, solved exactly, shows that net transport is exactly zero under a symmetric potential, under a symmetric drive, and under their combination, and that only the two asymmetries together give a non-zero transport whose direction reverses exactly with the declared phase gradient's sign; the standing wave transports nothing, the ring's connectivity and the declared step-energy bound are enforced with rejected controls, and the failed control - rescaling the potential, which the slope-sign gates cannot see - is retained rather than repaired.

- [0243 — The geometry foundation: shared items, the corrected pairing, and the spacetime-group clause](0243-the-geometry-foundation-shared-items-the-corrected-pairing-and-the-spacetime-group-clause.md): the shared geometric basis of the first three proposals is computed once and exactly - the spot floor with its penumbra-diameter form, the one-microwatt-per-mode etendue ceiling, the corrected second-Lagrange-point usable fraction 0.149047 in place of the superseded 0.787261, the pattern scale, the symmetry constraints, the work-region and work-time calculus with its relay duty cycle, and the ablation-level assignment - with the pairing rules enforced as rules that raise on a mixed pairing and reject the deliberately mis-paired control by exactly a factor of two in the ratio and four in the fraction; the supplement records that the full point groups of the achiral solids lie in O(3) rather than SO(3), and replaces the ground pattern's symmetry with the spacetime symmetry of the (constellation, schedule) pair, where invariance under a spatial operation combined with a time translation gives exactly zero transport and its absence gives directed transport.

- [0244 — Proposal three: the pyritohedral constellation, the entry window, and a transport defect disclosed](0244-proposal-three-the-pyritohedral-constellation-the-entry-window-and-a-transport-defect-disclosed.md): the pyritohedron's twenty vertices split into orbits of eight and twelve with ten antipodal pairs under its exact crystallographic group of order twenty-four containing inversion, the chiral snub cube is the declared alternative, the two regions are addressed by one schedule in opposite senses, the spacetime-group conditions give an exact zero for an invariant pair and an exactly reversing non-zero for a broken one, the entry window W1 to W4 is enforced with an exact safety inequality, and the ablation levels and the stage-one invariants hold - while the note DISCLOSES that this run's transport rests on a declared edge sum with a non-zero vertex divergence rather than on a measure-carrying flow, keeps the one failed control, and records the late rewrite of the checker.

### Named notes

- [iota-frame-three-dimensional-grid.md](iota-frame-three-dimensional-grid.md): the existing three-event process as a six-vertex, seven-edge cubical subgraph, preserving source reductions and its frame operator, with eight controls and an explicit boundary-condition obstruction.

- [`mobius-transport-composition-boundary.md`](mobius-transport-composition-boundary.md)

- [`mobius-transport-receipt-boundary.md`](mobius-transport-receipt-boundary.md)

- [`PR-0152-0158-integration.md`](PR-0152-0158-integration.md)
- [`absurdity-emptiness-record-freeze.md`](absurdity-emptiness-record-freeze.md)
- [`alternating-group-observer-expansion.md`](alternating-group-observer-expansion.md)
- [`borromean-boundary-word-correction.md`](borromean-boundary-word-correction.md)
- [`commit-state-reconciliation-without-resubmission.md`](commit-state-reconciliation-without-resubmission.md): the three permitted outcomes for an uncertain commit state, checked read-only against the original question, the full candidate and the single-slot ledger; no resubmission and no automatic retry.
- [`commit-state-snapshot-independent-receiving.md`](commit-state-snapshot-independent-receiving.md): a versioned pinned snapshot carries the three commit-state outcomes to a separate receiver that does not open SQLite; integrity is not authentication.
- [`commit-state-two-builder-projection-agreement.md`](commit-state-two-builder-projection-agreement.md): two implementation-distinct builders retain different provenance while agreeing byte-for-byte on one ledger projection; disagreement or copied provenance remains Unknown.
- [`commit-state-node-receiver-budget-pause.md`](commit-state-node-receiver-budget-pause.md): one Node.js receiver matches the archived Python empty-ledger projection, then pauses at the frozen work cap on a committed snapshot; remaining cases are NotRun.
- [`commit-state-node-meter-calibration.md`](commit-state-node-meter-calibration.md): input-size calibration completes fourteen semantic cases, but the retained cumulative audit rejects the run because correction replay reset the resource counters.
- [`cumulative-budget-through-correction.md`](cumulative-budget-through-correction.md): eight synthetic scenarios preserve conservative work/call reservations across correction and reconstruction; real Node receiver integration remains open.
- [`borromean-independent-longitudes.md`](borromean-independent-longitudes.md)
- [`catalog-key-words-alignment.md`](catalog-key-words-alignment.md)
- [`catalog-key-words-v1.md`](catalog-key-words-v1.md)
- [`cube-root-conjugation-and-polar-covariance.md`](cube-root-conjugation-and-polar-covariance.md)
- [`frame-covariance-rational-calibration.md`](frame-covariance-rational-calibration.md)
- [`golden-ratio-operator-lift-and-basis-coverage.md`](golden-ratio-operator-lift-and-basis-coverage.md)
- [`golden-ratio-receipts-and-source-boundaries.md`](golden-ratio-receipts-and-source-boundaries.md)
- [`golden-ratio-receiving-review.md`](golden-ratio-receiving-review.md)
- [`lattice-polar-and-mirror-boundary.md`](lattice-polar-and-mirror-boundary.md)
- [`ledger-holder-exit-without-new-permission.md`](ledger-holder-exit-without-new-permission.md): a holder exits after the write without asking for a new permission, and the exit is recorded rather than inferred.
- [`ledger-postwrite-exit-before-commit.md`](ledger-postwrite-exit-before-commit.md): the post-write exit stated before the commit, with the single-slot ledger as the only retained state.
- [`leak-wall-reading-correction-lines-and-rings.md`](leak-wall-reading-correction-lines-and-rings.md): reading correction, no executable claim: Research 0186's flow-network reading of the leak wall is withdrawn in favour of the language of lines, links and cutting.
- [`operator-check-python-adapter-v0.md`](operator-check-python-adapter-v0.md)
- [`operator-lift-main-integration-v1.md`](operator-lift-main-integration-v1.md)
- [`operator-lift-receipt-boundary-v0.md`](operator-lift-receipt-boundary-v0.md)
- [`observer-quotient-descent-reproduction.md`](observer-quotient-descent-reproduction.md)
- [`pairing-transport-native-boundary.md`](pairing-transport-native-boundary.md)
- [`pascal-commutator-certificate.md`](pascal-commutator-certificate.md): exact commutator certificates for the pinned normalized Pascal equations; also corrects the independent-check and initial claims in Research 0181.
- [`reflexive-lattice-gate.md`](reflexive-lattice-gate.md)
- [`sharkovsky-interval-extension.md`](sharkovsky-interval-extension.md)
- [`simplex-contraction-pascal-calabi-reduction.md`](simplex-contraction-pascal-calabi-reduction.md)
- [`triadic-period-bridge-correction.md`](triadic-period-bridge-correction.md)
- [`yang-lu-reference-registration-deferred.md`](yang-lu-reference-registration-deferred.md): process record, no executable claim: the external-reference registration was deferred at the catalog entries bound and admitted after the direction widened it to 101, with the recorded reason quoted and qualified.

- [zot-prefix-machine-weighted-sharing.md](zot-prefix-machine-weighted-sharing.md): explicit Zot evaluation, exact weighted reuse, and prefix-Keraia syntax/input boundaries.
- [keraia-read-boundary-and-weighted-prefix-search.md](keraia-read-boundary-and-weighted-prefix-search.md): resumable weak-head reads, checked segment reuse, exact code weights and retained type-boundary failures.
- [keraia-cycle-certificates-and-halting-mass-bounds.md](keraia-cycle-certificates-and-halting-mass-bounds.md): independent cycle receivers exclude a nonhalting cylinder, with multi-read continuations and an exact conditional one-half experiment.
- [bounded-native-data-interpreter.md](bounded-native-data-interpreter.md): a Rust-owned research data machine runs an Adva arithmetic interpreter over 129 object programs, with exact state reception and budget-preserving continuation.
- [bounded-interpreter-cross-host-replay.md](bounded-interpreter-cross-host-replay.md): a second host re-receives 300 retained checkpoints from their own bytes, reproduces the recorded profile digest and a byte-identical continuation; no new claim and no new campaign.
- [self-interpretation-capacity-preflight.md](self-interpretation-capacity-preflight.md): inside the declared bounds an inspectable encoding of the machine's own instruction grammar needs 169 nodes against 127, the packed alternative cannot be unpacked, and a 17-case dispatch ladder spends 90 of 128 instructions; a capacity measurement, not an impossibility result.
- [self-interpretation-scaling-preflight.md](self-interpretation-scaling-preflight.md): a generated meta program interprets a declared four-opcode subset of the machine's own instruction grammar and returns 7, 9, 4 and 5 for unseen object programs, while a four-opcode meta over two object instructions already needs 166 of the declared 128 instructions and is refused.
- [futamura-projections-in-adva-terms.md](futamura-projections-in-adva-terms.md): the Futamura projections stated in this repository's terms, with the first projection executed — a compiler built from the frozen interpreter by a declared rule emits 3-instruction residuals for all 129 frozen trees, agreement checked three ways, and the compile cost recorded; projections two and three are blocked by measured bounds.
- [futamura-dynamic-residual-calibration.md](futamura-dynamic-residual-calibration.md): the first projection with a live dynamic input — a 41-instruction compiler in the machine's own language emits 1- or 2-instruction residuals for a declared two-opcode subset, values and refusals both agree with interpretation, and the compile-versus-interpret ratio is measured rather than assumed.
- [compiler-size-curve-and-bootstrapping-budget.md](compiler-size-curve-and-bootstrapping-budget.md): the in-language compiler size curve — each extra opcode costs 45 to 63 instructions and each extra source instruction 32, an extra slot costs nothing because slot indices travel as data, and a compiler for the machine's whole instruction language is a measured 201-instruction lower bound against 128.

### Supporting directories

- [`0129-evidence/`](0129-evidence/)
- [`0139-phase-runner-preflight/`](0139-phase-runner-preflight/)
- [`0140-native-run-evidence/`](0140-native-run-evidence/)
- [`0141-local-preflight/`](0141-local-preflight/)
- [`0141-native-evidence/`](0141-native-evidence/)
- [`0142-evidence/`](0142-evidence/)
- [`0143-evidence/`](0143-evidence/)
- [`0144-evidence/`](0144-evidence/)
- [`0145-evidence/`](0145-evidence/)
- [`0146-evidence/`](0146-evidence/)
- [`0147-evidence/`](0147-evidence/)
- [`0148-evidence/`](0148-evidence/)
- [`0149-evidence/`](0149-evidence/)
- [`0150-evidence/`](0150-evidence/)
- [`0151-evidence/`](0151-evidence/)
- [`0152-evidence/`](0152-evidence/)
- [`0153-evidence/`](0153-evidence/)
- [`0156-evidence/`](0156-evidence/)
- [`0158-evidence/`](0158-evidence/)
- [`0161-evidence/`](0161-evidence/)
- [`0162-evidence/`](0162-evidence/)
- [`0164-evidence/`](0164-evidence/)
- [`0165-evidence/`](0165-evidence/)
- [`0167-evidence/`](0167-evidence/)
- [`0168-evidence/`](0168-evidence/)

*Complete listing as of 2026-09-16. The counts are stated once, in the header above;
they were previously duplicated here and the two copies drifted apart.*

- [keraia-growth-invariants-and-mass-ablation.md](keraia-growth-invariants-and-mass-ablation.md): received protected-stack invariants add 13 nonhalting cylinders at depth 19, excluding 19/524288 at the same cut; depth 15 gains zero.

- [bounded-self-compiler-and-futamura.md](bounded-self-compiler-and-futamura.md): a structured Adva research compiler compiles its own source, with stage, block and execution receiving; the three Futamura projections retain explicit implementation obligations.
- [execution-performance-comparison.md](execution-performance-comparison.md): 78 checked cases separate Rust direct execution, dynamic residuals, interpretation overhead and byte-identical self-compiler stages.
- [bounded-mix-and-three-projections.md](bounded-mix-and-three-projections.md): ordinary Adva input-binding mix self-applies to emit residuals, compilers and a compiler generator; two object interpreters exercise the finite code-producing equations, with the v1 capacity refusal retained and optimizing specialization still open.
