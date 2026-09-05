# ADR 0028: Transport local closure without collapsing history

## Status

Accepted for the version-zero research companion. This does not extend the
stable Lisp language or `adva.ir` version 1, discharge an M6 obligation, or
construct a Teichmüller/moduli-space semantics.

## Context

The verification frontier can refine and reopen obligations but its frozen
first method has no discharge predicate. A smaller exact question is available:
the witness kernel can decide equality in its finite commutative integer
polynomial fragment. The experiment must determine whether one such local
closure remains valid when embedded into larger one-hole contexts.

Reuse must not identify occurrences or erase the path by which a certificate
arrived. Negative observations also need disciplined names. A typed mismatch,
a counterexample, and an unverified challenge have different epistemic force;
calling all three false or absurd would introduce semantic drift.

## Decision

Add a frozen closure-transport method under the existing three-input and
three-output verification interface:

| Slot | Reading |
| --- | --- |
| `subject` | the exact distributivity candidate |
| `method` | the versioned exact-polynomial verifier |
| `object` | three scope maps, typed negative targets, and one challenge |
| `history` | local seal and three distinct transport receipts |
| `result` | local, staged, and direct certificates plus negative outcomes |
| `evidence` | path coherence and the append-only reopened frontier |

The local certificate embeds the complete two-node witness graph: one
`ArithmeticTransition` with zero actual and declared boundary, followed by one
`Seal`. Loading reconstructs the store, recomputes both content keys and
summaries, and requires additive residual zero and multiplicative residual one.

Each scope map contains exactly one distinguished input slot. Source and target
scope coordinates and occurrence coordinates must differ. Version zero freezes
the contexts

\[
f(t)=z+t,\qquad g(t)=bt,\qquad h(t)=b(z+t)=g(f(t)).
\]

Transport substitutes both sides of a closed identity into the same context and
reruns the exact witness predicate. The staged and direct routes must produce an
identical target certificate, while their receipts must remain distinct.

Persist these epistemic classes:

| Name | Required evidence |
| --- | --- |
| `identity` | one typed scope and an exact common normal form |
| `separation` | the same typed fragment, distinct normal forms, and a concrete counterexample |
| `incommensurate` | a typed-unit mismatch; neither truth nor falsity is claimed |
| `challenge` | a notice that reopens dependants but does not prove falsity |
| `absurdity` | reserved; version zero never emits it |

`absurdity` may be introduced only by a future method that validates a claim
and its negation under the same scope, interpretation, and verifier version.

## Consequences

- A locally closed structure can be reused at fresh occurrences and inside
  larger exact contexts.
- Equality of final certificates does not identify their histories.
- The arithmetic negative control is a real separation certificate rather than
  a renamed failed proof.
- Polynomial closure cannot answer ordered-holonomy or shared-truth units; both
  imports are explicitly rejected as incommensurate and record
  `target_hole_preserved`. Rejection does not silently close the question and
  does not automatically create an attacker-controlled new hole.
- A challenge propagates through the finite dependency cone. Prior certificates
  remain stored, so reopening is not deletion or retrospective falsification.
- The implementation is an algebraic scope graph. Interpreting its traces as
  paths in a geometric moduli space requires a separate typed construction.
