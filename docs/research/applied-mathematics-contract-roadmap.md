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
