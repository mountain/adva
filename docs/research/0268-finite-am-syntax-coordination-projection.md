# Research 0268: finite AM syntax coordination projection

Date: 2026-10-15. Status: bounded targeted result; complete local integration
is `Unknown/NotRun`. Codex (OpenAI), submitted through Mingli Yuan's authorized
account proxy, not his authorship, review or endorsement. Project-original
contribution under Unknown v0.3.

## Frozen dependency and question

Main remained `8585c5b965b84422b802d50f11f375aea171bd27`. Draft PR
[#217](https://github.com/mountain/adva/pull/217) had advanced to
`dbafa05442109b478d5ad6dcdac50a5692bbc7a1`: an independent resource review
replaced recursive dataclass equality with a cumulative iterative dual-view
comparison. Its CI, bounded acceptance, publication and machine-dependency
workflows all passed. Open PR #218 concerns research placement and is not a
dependency of this experiment.

The pre-execution [contract](../../experiments/bootstrap_zero_syntax_coordination/contract.json)
freezes one narrower question. Given an independently supplied valid
`WholeCut6` and an accepted research-local `AMTerm`, can a structured
constructor-by-constructor projection preserve exact constructor order and
every bound leaf while treating `BalancedZero`'s negative side as a view rather
than a second occurrence?

The grammar is exactly:

```text
Atom | Hole | Use | EmptyZero | PolarDual | Plus | Tensor |
BalancedZero | HistoryComposition
```

Formation retains PR #217's limits: 256 visited nodes and depth 32, plus 256
cumulative dual-comparison pairs and comparison depth 32. The arithmetic domain
is empty. Research 0123's `arithmetic-universality` and
`hypothesized-arithmetic-truth` remain proposed hypotheses. Research 0090 still
requires coverage, and Research 0092 may not promote pairwise syntax evidence
to all-fillings closure.

## The projection and conditional theorem

For an accepted term `t`, the checker constructs `C_W(t)` containing:

- the independently validated whole name;
- a structured prefix-delimited constructor word;
- ordered hole `(name, type)` leaves;
- ordered use `(source, occurrence, type)` leaves;
- the authoritative source occurrence/multiplicity and production ledgers;
- the ordered residual ledger; and
- counts of balanced dual views and history compositions.

Each leaf emits its exact tagged payload. `PolarDual` emits distinct open and
close tags. `Plus`, `Tensor`, and `HistoryComposition` emit distinct open,
middle and close tags around their ordered children. `BalancedZero` emits its
positive subtree once and then one `dual-view` marker; the prior formation
check has already required an exact structurally equal `PolarDual` view under a
cumulative finite budget.

This gives a small conditional theorem by structural induction. Every leaf
payload in `C_W(t)` is the corresponding payload in `t`; every composite step
preserves the ordered projections of its immediate children under a distinct
constructor tag. The structured tags are uniquely parseable, so two admitted
terms with one equal projection have the same constructor tree and leaf
payloads. For `BalancedZero`, the omitted second traversal is recoverable as
the required exact `PolarDual` of the retained positive tree. Source/type
soundness and occurrence uniqueness follow from the prior formation judgment,
not from the projection itself.

This proves only constructor-faithful syntax coordination conditional on the
research-local receiver. It does not interpret a history pair as temporal
composition, `BalancedZero` as additive zero or cancellation, or two terms as
denotationally equal.

## Executed finite calibration

One positive term contains all nine constructors. Its projection contains one
declared hole, one declared use, one balanced-view marker and one ordered
history composition. A separately named `coordination-fresh-` source has the
same constructor signature while retaining different whole, source and
occurrence identities. Swapping history children changes the projection;
`Plus`, `Tensor` and `HistoryComposition` remain distinct. The balanced form
contains one use and one view marker rather than two uses.

Four refusal controls block a cross-source use, duplicate occurrence,
mismatched dual and reordered residual ledger before a projection is returned.

The bounded exhaustive family starts from four fixed leaves and closes them
twice under all nine constructors, with exact deduplication. It contains 10,924
distinct candidates: 8,542 pass the existing formation boundary, 2,382 are
refused, and the accepted terms produce **zero projection collisions**. This is
a finite calibration of the inductive argument, not evidence about arbitrary
host objects, unlimited depth or semantic completeness.

## Retained failure, cost and integration residual

The first targeted run estimated 10,980 candidates before deduplication. The
actual generator deduplicated 56 already-present terms and returned 10,924, so
pytest stopped after eight passing cases and one count failure. That run is
retained in
[`prior-count-mismatch.json`](../../experiments/bootstrap_zero_syntax_coordination/evidence/prior-count-mismatch.json).
The single allowed implementation correction changed only the three expected
counts; it did not alter the generator, grammar or budget.

The corrected targeted replay passed nine pytest cases in 1.15 seconds. Wall
time including process launch was 1.510913118 seconds and child peak RSS was
46,828 KiB. Construction, formation validation, projection and fresh reuse were
not separately timed. Projection serialization cost is zero inside the
checker. There was one process and one correction replay.

The attempted complete Bootstrap Zero replay then failed before testing because
the Python subprocess wrapper passed the shell wildcard literally. Pytest ran
zero tests, returned code 4 after 0.307114 seconds and reached 27,604 KiB child
peak RSS. The correction allowance had already been spent, so this command was
not repaired or retried. Complete local integration is therefore
`Unknown/NotRun`; the prior exact PR #217 head remains independently green, but
its 1,093 tests are not a replay of this successor head. Exact outcomes are in
[`execution.json`](../../experiments/bootstrap_zero_syntax_coordination/evidence/attempt-1/execution.json).

## Vocabulary, help and residual

New vocabulary: **zero**. `SyntaxCoordinationProjection` is an internal program
record for this calibration, not a promoted Adva word. Existing formation,
source/occurrence, residual and coordination language is sufficient.

This helps Mingli and later agents distinguish three claims: a term formed; its
syntax projection preserved identities and order; its interpretations agreed.
Only the first two are addressed, and the second only for the AM fragment.
Jiamin's practical-task benefit remains unmeasured.

The broader WholeCut6 theorem in Research 0102 remains open for line/circle
views, routing, collision, fibres, split witnesses, traversal and every declared
exception. Rust correspondence, observer invariance, residual-preserving
close/reopen, 0090 coverage and 0092 scoped generation/promotion/reuse also
remain open. The smallest continuation is a new-contract complete-suite replay
using an explicitly expanded file list; only after that passes should the next
round add one non-AM built-in view to the coordination relation.
