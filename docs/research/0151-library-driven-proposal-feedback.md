# Research 0151: Library-driven proposal feedback, with macro ablation

Status: finite run contract, written before execution on 2026-09-06.
Results belong in `0151-evidence/`, not in this frozen contract.

## Question, authorization and level

Can a disk-reloaded checked Research 0150 witness generate a new exact
arithmetic proposal, and can a retained, checked composite **proposal recipe**
change the next bounded candidate family? The user authorized proceeding and
continuing after success. This contract permits one trial with at most three
stages (two conditional continuations), not automatic restart or unbounded
growth. This is a Rust-hosted research proposal mechanism, not Adva interpreting
its own syntax, discovering a stable operation, or completing Research 0092.

The agenda and Research 0092 dependency gate still apply. No all-fillings
coverage/invariance certificate is available here. The strongest positive
judgment is `AcceptedPair`; general vocabulary promotion has status
`CertificateObstruction`. A saved recipe is proposal data, not a universally
transportable certificate or an aperture character.

## Imported boundary

The sole initial recipe comes from word 0 of the checked, pinned
`adva-library/stability/epoch-0001.json` (and its checked parent). Its two
retained expressions are `2*x` and `x+x`. Research 0150's Rust loader must
rederive the snapshots and witness graph. Existing arithmetic normalization,
`ArithmeticTransition`, `Seal`, and concrete nonzero guards supply the checker.
No serialized status, hash, or ordinal is semantic authority.

The generator handles `ExactExprV0` arithmetic syntax, NOT `ProgramTerm`.
Replacing occurrences of the named arithmetic variable is a host proposal
construction. Each expanded pair is checked afresh; there is no unchecked
generic substitution rule. Repeated arithmetic syntax is not native program
sharing. No diagram, SourceId, OccurrenceId, EquationCell, copy, discard,
specializer, braid inverse, or stable hole operation is constructed here.
Native program realization and its explicit-copy/correspondence obligations
remain `NotRepresentableInThisExperiment`. Both expanded expression trees and
their occurrence counts remain visible, without quotienting their histories.

## Frozen generator and independent calibration input

The generator takes ONLY an ordered recipe book, an enabled-recipe list and
a shared budget. It does not take observations, expected coefficients, a
target expression, a reward, or a table of successful candidates.

Enumerate by exact surface size 1 through 3. At size 1 emit `x`, then `2`.
At later sizes emit unary recipe references (newest recipe first, then prior
ones), followed by ordered binary `Add` and `Multiply` for each nonempty
left/right size split and prior-layer pair. Retain syntactic duplicates; do
not use polynomial equality for candidate identity or pruning. Stop at 64
candidates per search. A recipe reference costs one surface node, plus its
argument's size. Full definition and expansion costs are separately charged.

The task checker, not the generator, receives three explicit, synthetic
calibration tasks, in this fixed order:

| Stage | supplied `(input, output)` pairs |
| --- | --- |
| 0 | `(1,4), (2,8), (-1,-4)` |
| 1 | `(1,8), (2,16), (-1,-8)` |
| 2 | `(1,32), (2,64), (-1,-32)` |

Agreement at these points is not discovery of a world law or uniqueness of
the inferred polynomial. Each candidate also needs an exact pair witness and
guard checks. Retain every visited candidate and prediction, not just the
first accepted one. Select the first accepted candidate as the next recipe;
its definition must actually reference the newest available recipe.

## Controls, continuation, and honest success

Each stage runs three searches with the same surface limit and task:

1. `LibraryEnabled`: all checked proposal recipes available;
2. `NewestDisabled`: remove only the newest recipe from proposal generation;
3. `OrdinaryMacro`: the same definition bodies and expansion/checking rules,
   without claiming that a witness-backed name is a new language primitive.

Record generation, definition inspection, expansion, checking, and persistence
costs separately. Ordinary macros must pay definition and expansion costs too.
Compare candidate traces and full search work, not just compressed surface
length. If macros match, report **no demonstrated advantage over ordinary
macros**, even if the enabled/disabled comparison shows bounded feedback.
The disabled outcome is `Open` after completing the finite grammar, never a
proof that the target is unrepresentable with more surface nodes.

Continuation requires all of: an `AcceptedPair`, an actual newest-recipe
reference, no accepted disabled candidate, matching macro control, durable
checkpoint and complete disk replay. On failure stop with retained results.
After stage 2 stop at the declared limit and report the coverage/native
realization obstructions. No extra stage, fuel reset, or general promotion is
authorized by success. This checks a small representation-feedback mechanism,
not the stronger endogenous scope breakthrough of Research 0091/0092.

## Retained state and checking

The exploration journal is separate from the immutable knowledge snapshots.
It may retain `Open`, rejected candidates, guard failures, and `Unknown`.
It never publishes epoch 2 or weakens Research 0150's publication gate.
Each stage records its complete recipe book, task, candidate order, expanded
pairs, predictions, native pair artifacts, cost vector, selected proposal and
residuals. A source/dependency revision and original snapshot digest bind it.

Write only new stage paths with no-overwrite same-directory staging and
hard-link publication. Reload by bounded regular-file reads, regenerate the
stage from a fresh checked base and prior replays, and compare the complete
record. A separate replay CLI is read-only with respect to the journal.
Serde decoding alone cannot create a reusable recipe book. Replay shares the
implementation with production; it is not an independent proof implementation.
Partial journals are diagnostic records, not resumable semantic authority.

## Enforced finite limits

- One shared `LibraryBudgetV0`, maximum 50,000 logical units, including base
  loads, proposal construction, definition checks, expansion traversals,
  normalization, guards, witness insertion, audits, replay and checkpointing.
  Prepay final report storage from this same account. No reset on continuation.
- Three stages, three searches per stage, at most 64 generated proposals per
  search; surface trees at most 3 nodes; at most four recipes including seed.
- Exact expanded trees: at most 127 nodes, depth at most 16; variables only
  `x`, literals only `2`; every traversal charged. Recipe references must go
  strictly backwards through the definition list. Arithmetic is bounded by
  these structural caps before normalization. Bound failures are retained.
- Three observations per task, nonzero inputs in `[-8,8]` and outputs in
  `[-1000000,1000000]`; point zero is a negative guard control, never successful
  guarded execution.
- At most four 1 MiB checkpoint/report files in the trial directory; each
  serialization and read checked against the 1 MiB cap. Same-path overwrite
  is refused. No mutable latest pointer or automatic crash recovery.
- Native trial: supervisor timeout 60 seconds, 512 MiB virtual-memory limit,
  1 MiB per-file OS size limit. Logical units are not CPU instructions; the
  supervisor covers noncooperative host work. Interrupted staging files and
  any completed journal entries are retained; do not claim completed replay.
- Engineering validation is not an adaptive research search: at most three
  focused test invocations, two workspace test/Clippy passes, one recorded
  trial, and one separate read-only replay invocation. Each invocation has
  an outer timeout; no research retry after inspecting an unfavorable result.

Tests cover target-blind generation, ablation, fresh pair verification,
guard refusal, missing/cyclic references, zero/partial fuel, changed tasks,
forged receipts and bounded publication. Unknown retains checked prefixes and
a pending cursor. Missing boundary evidence or failed checkpoint blocks
continuation. Existing 0149/0150 checker sources, contracts, snapshots and
artifacts, and Cargo.lock, must remain byte unchanged.
