# 0149 — Frozen library epochs and question-relative stability

Status: bounded research calibration; run contract written before execution.
This does not advance the stable phase order in the research agenda.

## Question and current level

Can a finite library evolve between runs while a fixed question acquires a
stable representation? Does repeating a zigzag supply progress by itself?
The environment and arithmetic/prime examples have run locally. No general
self-modifying Adva library or convergence mechanism is implemented.

This calibration is a Rust example over the existing research `ExactExprV0`
polynomial shadow, not a new stable API, native learner, specializer, hole
calculus, feedback semantics, or `EquationCell`. Its supplied candidate
catalogue is the entire **declared finite model**, not every possible program.

## Imported assumptions and boundary justification

- Rust and the existing exact integer polynomial normalizer are trusted.
  Observations are supplied fixture assumptions, not authenticated world data.
- The candidate catalogue, checker revision and question are immutable during
  a run. Candidate ordinals and content digests are research coordinates,
  never `SourceId`, `OccurrenceId`, signatures or program identities.
- Point values and canonical polynomial features are diagnostic observations.
  In particular, evaluating a polynomial shadow at zero does not execute
  `ExactExprV0::evaluate_guarded` or bypass its execution guards.
- Syntax histories remain separate even when polynomial features agree.
  Ordinary version-space elimination is the imported finite learning model;
  it is not a newly derived Adva learning law.
- Existing braid tests supply independent regression oracles. Their Artin
  action is test-local mathematics, not a stable braid-group implementation.
  Existing Rust Q4/M6 formation is not semantic filler replay or inverse
  execution. A six-pass no-evidence schedule here is a stuttering control,
  not a new implementation of a triadic zigzag.

## Protected obligations and checker

Retain the complete input catalogue, supplied observations, each completed
round, exclusions, residual candidates and pending suffix. No in-run insertion,
evidence deletion, arbitrary representative switching, or fuel reset. Bind
replay to the exact request (including question and catalogue); a changed
observer, method or library starts a different epoch and cannot inherit a
certificate by renaming. The old report remains readable.

For active candidates `F` and fixed question `Q`, admit `FeatureClosed` only
when `F` is nonempty and the fully checked image `chi_Q(F)` is a singleton.
`ModelGap` means the supplied evidence excludes the whole declared model.
`Open` means complete checking still permits differing answers. `Unknown`
means the next required work did not fit the budget; it is not nonexistence.
A completed no-change round has `strict_progress=false` (`NoProgress`), not
a closure certificate. An empty-model update is not productive progress.

The result retains a certificate with every surviving candidate's question feature and
all exclusion checks. Replay recomputes the result and compares complete
content under the original request, charging the same shared study ledger.
This is deterministic re-execution, not an independently implemented proof
checker. Tests also use explicit scalar expectations and tampered receipts.

If the target is in the initial catalogue and observations are applicable and
correct, elimination preserves it. Every strict update decreases `|F|` by at
least one, so at most `|F0|-1` such updates preserve nonemptiness. Plateaus have
no duration bound. Feature closure persists only under **nonempty refinements
of this same catalogue and question**; contradictory evidence or a library/
observer revision requires new checking. It does not certify global truth or
tell when arbitrary open-world learning converges.

## Frozen run contract

- At most 8 candidates; at most 31 expression nodes and depth 8 per candidate;
  only the existing constant/variable/add/multiply research constructors;
  variable `x`, integer constants in `[-16,16]`.
- At most 16 rounds; at most one supplied observation per round, integer input
  in `[-8,8]`, observed value in `[-1000000,1000000]`.
- Questions: point observation in `[-8,8]`, exact polynomial shadow, or full
  syntax presentation. No generated candidates or nested search.
- A single invocation has 50,000 shared logical units across the frozen case
  suite, receipt replay, negative audits and checkpointing. Per-case work
  caps restrict spending from that account, never refill it. Charge admission,
  expression-node validation, normalization, every evidence/feature comparison,
  each round commit, replay comparison and output checkpoint.
  The checkpoint unit is prepaid from this same account. Normalization and
  bounded serialization count as logical operations, not CPU instructions;
  the outer process limits also cover validation, hashing, I/O and host cost.
- Freeze at most 16 case/audit groups. Stop after those groups or the shared
  bound. A failed expected outcome is retained and stops the trial; there is
  no automatic repair-and-rerun of the research trial.
- One native trial, at most 15 seconds, 512 MiB address space and 1 MiB output;
  one JSON checkpoint to a new path, never overwrite existing evidence.
  Hard interruption has no guaranteed checkpoint and is `Unknown`/incomplete.
- Engineering validation is separate from trial units: at most 3 targeted
  build/test passes of 180 seconds each, one existing Python braid regression
  pass of 60 seconds, one full Rust regression pass of 180 seconds, and one
  clippy pass of 180 seconds. Each pass has a finite timeout; record failures
  as well as successes. No retry or new trial beyond these bounds without a
  revised contract and rechecked boundaries.

## Frozen controls

1. Delayed separating evidence after three unchanged rounds: plateau is open.
2. Two distinct expression histories with the same exact polynomial: feature
   closure without object/syntax closure.
3. Point question closed before the finer polynomial question.
4. Six no-evidence passes: unchanged candidates and no progress.
5. A fresh coefficient instance with the same checking recipe.
6. Duplicate evidence: retained history, no new constraint.
7. Evidence outside the model: `ModelGap`, not vacuous closure.
8. Zero and partial work caps: `Unknown` with retained pending rounds.
9. Tampered certificate, changed question, changed catalogue, and changed
   checker revision: receipt inapplicable, not a refutation of the old claim.
10. Existing braid controls: a central full twist and a pure commutator can
    return coarse endpoints/readouts without becoming the identity.

## Execution evidence

The immutable run output and subsequent execution log are kept separately in
`0149-evidence/`. This contract is not edited after the native trial. Historical
notes and prior artifacts are not rewritten by this run.
