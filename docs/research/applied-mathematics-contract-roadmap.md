# Applied mathematics after the initial finite probability interface

Status: repository-informed proposal, 2026-09-17. This records the next
obligations; it does not install new keywords, semantic types or library entries.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
not his review or correctness guarantee. Original contribution under Unknown
v0.3. The audit below is a source review, not a fresh test of every cited module.

## The main gap

Adva already has mathematical operations and adapters. The missing layer is a
set of compatible contracts for quantities, uncertainty, approximation, solving
and accepting a result. A uniform scalar or spelling does not make those
contracts interchangeable. The current finite probability work supplies one
small concrete interface rather than a completed universal mathematical language.

Relevant existing capabilities are:

- Rust `Real`/`Bool`, scalar operations, forward differential and Jacobian:
  `crates/adva-ir/src/term.rs`, `crates/adva-lisp/src/operation.rs` and `eval.rs`.
  `Real` is binary64; the reported numerical policy explicitly gives no error
  bound. Finite output is weaker than validated numerical accuracy.
- Research data machines have checked i64 operations, bounded execution and
  replay; `crates/adva-witness/src/arithmetic.rs` also implements exact BigInt
  polynomial expressions. Exchangeable polynomial values do not erase ordered
  histories or noncommutative actions.
- `python/adva/core.py` exposes Rust-backed value/gradient and `ScipyObjective`
  adapters. Access to a solver is not an optimality or stability certificate.
- `experiments/golden_ratio_operator_lift/receipt.py` and
  `python/adva/operator_receipt.py` already explore dimensions, bases and
  operator transport. Their native authority is not granted.
- `experiments/finite_group_probability/` and `experiments/probability_receipt/`
  supply exact finite density, joint-law, observation and conditioning examples.
  The receipt receiver is external; only the separate mean-constraint program
  has the native execution evidence described in its own record.
- `ontology/physics/basic-dimensions.md` proposes dimensions and carefully
  distinguishes them from units and coordinates; it does not implement a
  physical measurement or conversion calculus.

## Dependency order and minimum useful witnesses

| Priority | Contract still needed | First finite witness and refusal |
| --- | --- | --- |
| 1 | Numerical observable, dimension, unit, scale and reference point | Rational metre-to-centimetre conversion: expectation scales by 100 and variance by 10,000, while probabilities are unchanged. Refuse incompatible dimensions. Start with linear conversions; affine temperatures require an explicit origin. |
| 2 | Finite conditional/transition kernel | A two-state rational row-stochastic matrix, typed source and target, checked composition and a posterior from a supplied joint law. Keep zero-probability conditioning undefined; do not infer independence from marginals. |
| 3 | Linear algebra with explicit carrier, basis and direction | Extend existing matrix receipts to solve a small rational Ax=b with a checked residual. Distinguish unique solution, inconsistent system and an affine family of solutions. A matrix is not automatically an invertible group action. |
| 4 | Reliable approximation, intervals and comparisons | Rational enclosures propagated through a bounded expression; refuse division through a zero-containing denominator. Distinguish numerical rounding error from probabilistic uncertainty and unobserved cases. A known denominator bound can justify a specific exact-zero bridge; small residual alone cannot. |
| 5 | Constrained optimization with certificates | Finite rational candidate set or a small convex quadratic: provide a feasible solution and a verified lower bound. Claim optimality only when the gap closes; a budget stop retains the gap. A contracted simplex or matching mean is not a general stopping certificate. |
| 6 | Discrete dynamics and stability | A two-state transition kernel or rational map with a verified one-step contraction/conservation condition and a stated finite time horizon. Bound propagated error. Identity or periodic transitions are controls against assumed convergence. |
| 7 | Statistical estimation and identifiability | Fixed finite hypothesis family and sampling law; enumerate the possible samples to verify one confidence rule's coverage. Unknown mechanism, sample variability and computational error remain distinct. |
| 8 | Learning, decisions and practical benefit | A supplied finite decision problem with an explicit loss, observations and two actions. Compare a fixed policy with an updated policy under equal total cost including construction and verification. Test a new instance; repeated execution alone is not learning or benefit. |

This is an implementation order, not a classification proving that the eight
topics are disjoint or that all preceding work must finish before any parallel
research. Exact finite arithmetic permits the first kernel and decision example
without waiting for a general floating-point error calculus or differential
equation solver. The event/observation foundation should accept general finite
spaces; groups are optional action structure and must not impose reversibility
on every state transition.

## The next compact application

Use two declared states, two observation labels and two possible actions.
Specify a rational prior, a rational observation kernel and a rational loss
table with a fixed unit. On each positive-probability observation, compute
the posterior and both conditional expected losses. Return the minimizing
action together with the explicit comparison and tie set, not a forced choice.

The receiving boundary fixes the state/observation/action carriers, kernel
direction, prior, loss, units and resource allowance. Its checks verify mass,
conditioning and the finite comparison. A zero-probability observation remains
unresolved for that conditional decision; swapping action roles or changing
loss must change the question, even if a final number happens to be unchanged.

This would connect the current probability work to an action that a person can
understand and challenge. A synthetic example establishes executable semantics;
Mingli or Jiamin's real task still needs its actual observations and loss
interpretation. Do not invent those preferences or call a synthetic win social
trust, general learning or a universal speedup.

## Reuse existing research rather than duplicate it

- `docs/research/operator-lift-receipt-boundary-v0.md`: matrix scope and basis.
- `docs/research/simplex-contraction-pascal-calabi-reduction.md`: contraction
  and exactness are different obligations.
- `experiments/sharkovsky_interval_extension/`: finite dynamics with declared
  extension boundaries, not general stability.
- `docs/research/0089-failure-frontiers-observer-relative-closure.md`: instance
  distributions and completion-space distributions must remain distinct.
- `experiments/evidence_stutter/`: repetition is not evidence of learning.
- `docs/RESEARCH_ENGINEERING_AGENDA.md`: observer specialization, generalization,
  practical programs and intrinsic compilation retain their dependency order.

The tool frontier is therefore a chain of checked interpretations: quantity,
observation, conditional update, finite decision and retained residual. Existing
arithmetic, differentiation and solver interfaces can support it when their
actual contracts meet. Native admission and the library's open growth obligation
remain separate; this document changes neither.

## First decision continuation, 2026-09-17

The [finite decision experiment](../../experiments/finite_decision/README.md) now
connects the existing probability receiver to a declared prior, observation
kernel, loss and cost. Five exact contexts pass; 41 changed-evidence controls
and two unsupported contexts are refused. The receiving chain retains complete
tie sets and leaves zero-probability conditioning undefined. Cost can reverse
the acquisition choice, and the same informative channel can have zero decision
value under a different loss. This is an external finite result, not native
probability syntax or practical validation of human preferences.

The next small step returns to priority 1: transport the loss and observation
cost through a checked positive unit scaling. Scaling both must preserve action
and acquisition minimizers; scaling only one changes the decision problem.
The frozen original campaign and its resource account remain unchanged.

## Common loss-scale continuation, 2026-09-17

After PR #187 was merged, the [scale receipt](../../experiments/decision_scale/README.md)
checked a common positive scaling of every loss and the observation cost. Seven
transports preserve probabilities, all minimizers and null events. Twenty-seven
evidence controls and six unsupported requests are refused; ten controls have
two arithmetically valid endpoints but fail the requested correspondence. Scaling
only loss or only cost can reverse the observe-versus-skip choice. Forward and
inverse transport recover numbers and unit labels while retaining two steps.

This realizes one finite part of priority 1; unit compatibility remains a
declared premise. No native operation or vocabulary is added. The next small
obligation is receiving a two-step composition with its exact intermediate
context and ordered history, without replacing that history by a product factor.

## Two-step composition continuation, 2026-09-17

Following the merge of PR #188, the [composition receiver](../../experiments/decision_scale_composition/README.md)
checks two ordered scale contracts and their complete intermediate context.
Six compositions pass; 28 evidence controls and four unsupported contexts are
refused. In six controls both local steps and the final context agree with
their declared arithmetic, but a different intermediate unit blocks composition.
The final scalar product alone is insufficient.

Two factors 8 and 4 are admitted as a bounded two-step path while an actual
one-step request for factor 32 is refused by the unchanged factor bound.
Conversely loss 8 with factors 16 then 1/16 is refused at intermediate 128,
despite its final numerical return. History, intermediate bounds and the
resource account remain explicit; no universal or native authority follows.
The next continuation obligation is a bounded checkpoint at history capacity,
with no erased prefix or automatic renewal of fuel.

## Checkpoint boundary continuation, 2026-09-17

The [checkpoint receiver](../../experiments/decision_checkpoint/README.md)
now rechecks and retains a complete scale prefix while separating history
capacity, abstract attempt allowance and actual checking cost. Two third-step
continuations pass at history length four; six pauses retain their exact pending
task, including two reloads from actual receiver output. Twenty-two evidence
controls and seven unsupported contexts are refused. Erasing history or
replenishing a candidate's allowance cannot turn a pause into a continuation.

The checker is stateless: this adds neither durable recovery nor exactly-once
consumption. The next finite obligation is a receiver-owned transition ledger
that distinguishes an identical replay from a conflicting repeated submission.
No native operation, capacity increase or new vocabulary follows.

## Receiver ledger continuation, 2026-09-17

After PR #189 merged, the [finite ledger](../../experiments/decision_ledger/README.md)
adds one receiver-owned SQLite slot per fixed checkpoint request. Same-key,
same-content submissions return the stored result without another abstract
debit; changed payloads conflict and a different key cannot bypass occupied
capacity. Both result and debit commit in one transaction. The arithmetic
receiving chain and its finite history limit remain unchanged.

A 48-process campaign passes 328 assertions across two families, including a
new asymmetric instance. Real process exits before commit leave an empty slot
and the original allowance; exits after commit but before the reply retain one
debit and allow exact result recovery. These are sequential local-storage
witnesses, not distributed exactly-once or power-loss guarantees. No new word or
native effect is admitted. The next finite question is simultaneous submission
and the distinction between lock contention and invalid ledger contents.

## Bounded overlapping delivery, 2026-09-17

Following PR #190, the [contention adapter](../../experiments/decision_ledger_contention/README.md)
retains the unchanged arithmetic and one-slot ledger engine under a new explicit
receiving profile. Eight two-process episodes distinguish pre-transaction SQLite
BUSY from invalid contents. An unchanged old-profile control reports InvalidLedger
on the same lock schedule, outside its original sequential evidence scope.

After the holder terminates, a single explicit retry either returns the stored
result, reports conflict/capacity, or commits after an invalid holder was refused.
Complete post-quiescence SQL observations show one final debit in all nine ledgers.
The first campaign passes 500 assertions in 39 processes; new asymmetric reuse,
non-database bytes and both profile refusal directions are included. New and old
ledgers are not migrated. No new native word or authority follows.

The next small obligation is holder termination before releasing the transaction
gate, with bounded contender recovery and preservation of the original question.
This remains a future failure position; the present evidence does not establish
arbitrary concurrency, fairness or distributed exactly-once delivery.

## Return to quantity and observable mathematics, 2026-09-17

PR #191 completes the declared two-process contention witness. Its holder-exit
follow-up remains an engineering obligation; it does not block the next
mathematical contract. We now return to priority 1 rather than indefinitely
extend local-storage machinery.

The [observable unit receiver](../../experiments/observable_unit_transport/README.md)
directly reuses the unchanged probability receiver. Its four-unit formal registry
checks matching Length/Time dimensions, positive derived scales and common zero
origins. Observable means scale by a, variances by a squared, while probability,
reference density energy and hidden residual remain unchanged. All conditional
moments and zero-event nulls are retained. This closes the first restricted
linear-unit witness, not a general physical dimension or measurement calculus.

Five exact transports and 32 refusals pass in 37 fresh processes, including
seconds-to-milliseconds reuse and inverse conversion from actual receiver output.
Two zero-probability coordinate substitutions preserve every reported statistic
but fail the explicitly stronger complete-carrier contract. The observables are
still equal almost surely; statistical equivalence and pointwise representation
faithfulness must remain separate.

The next mathematical step is priority 2: a typed two-by-two transition-kernel
composition with an explicit middle carrier and marginal. Existing decision
receipts cover one kernel, not this ordered composition. A naive three-stage
binary joint has eight atoms and exceeds the probability parent's six-atom
limit. Use compatible checked four-atom interfaces with an explicit supplied
Markov premise, or justify a separate receiving profile; do not widen a frozen
ancestor silently. General units, affine origins and physical calibration remain
open while this finite kernel task proceeds.

## Typed kernel composition, 2026-09-17

After PR #192 merged, the [finite kernel receiver](../../experiments/kernel_composition/README.md)
advances priority 2 through three checked four-atom interfaces AB, BC and AC.
Typed direction, complete middle prior and ordered history are receiver-bound.
The explicit Markov extension supplies J(a,b,c)=p(a)K(a,b)L(b,c); it is not
inferred from adjacent distributions. All original parent bounds remain fixed.

Forty fresh receiving processes pass 397 assertions: five accepted compositions,
24 evidence refusals, two dependence Unknowns and nine unsupported contexts.
Eighteen evidence refusals pass all three local arithmetic checks. Two four-state
models share complete adjacent laws yet have opposite endpoint dependence;
local density energies of 1 coexist with endpoint energy 2. An unspecified
premise remains Unknown, while a requested Markov extension rejects those
endpoints. Unused zero-mass kernel rows remain stipulated rather than learned.
A distinct asymmetric fixture and Chinese space IDs provide fresh reuse.

This establishes a finite composition and posterior interface under supplied
premises, not arbitrary dependence inference or general Markov-process tooling.
The next mathematical witness is priority 3: a bounded rational Ax=b receiver
with explicit spaces, basis and direction. Check the residual and distinguish
unique solutions, inconsistency and affine families. Existing operator receipts
are a starting point; matrix equality or zero residual does not alone certify
invertibility or uniqueness. General units, native import and the separate
ledger-holder-exit obligation remain open.

## Complete rational linear-system receipts, 2026-09-17

After PR #193 merged, the [linear-system receiver](../../experiments/linear_system/README.md)
advances priority 3 with explicit two-dimensional domain/codomain bases and
column direction. The old fixed-word invertible-operator profile is unchanged;
a new separate receiving contract admits singular A without weakening that
ancestor. The scalar field is Q; finite wire bounds are not a closed finite field.

A solution plus a checked two-sided inverse certifies uniqueness. A codomain
covector y with y^T A=0 and y^T b=1 certifies inconsistency. A particular solution
and exactly 2-rank(A) independent kernel directions certify a complete affine
family. Valid but missing directions retain the particular solution and return
UnknownCoverage, not an all-solutions claim. Alternate parameterizations are
accepted, and actual two-space basis reuse distinguishes vector transport from
covector transport.

The first campaign passes 468 assertions in 44 fresh processes: ten complete
classifications, two partial-family results, 20 evidence refusals and 12 context
refusals. Exact synthetic examples cover all three classes, rank zero, rational
coefficients, non-symmetric matrices and fresh chart reuse. No native authority,
universality or actual human benefit is claimed.

The next mathematical witness is priority 4: rational interval enclosures through
a bounded expression, including division through a zero-containing interval as
a refusal. Keep exact-zero proof, small residual and unresolved sign distinct;
input interval uncertainty is not automatically a sampling probability or a
floating-point error model. Arbitrary linear-system dimensions, formal proof
artifacts, native import and the separate ledger-holder-exit obligation remain open.
