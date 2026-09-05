# ADR 0032: Separate problem formation from value seeking

## Status

Accepted for one executable version-zero research experiment, subject to CI
replay. This does not change `adva.ir` version 1, the Lisp language, the three
stable mechanism labels, or the external trust boundary.

## Context

The preceding experiments can search a declared finite family and retain a
witness, but a closed search cannot manufacture the reality-facing question or
the value by which candidate answers should be ranked. Treating imagination as
an internal theorem would erase the very boundary the experiment is meant to
study.

The second custody proposal uses five declared failure domains and accepts
three receipts. In a quorum-overlap-only model, two three-of-five successor
quorums may intersect in exactly one domain. If that domain is adversarial,
their honest intersection is empty. That is a concrete surface defect from
which a finite problem can be formed.

## Decision

1. Keep one mechanism. Both new programs are `learn` edges with the common
   `(subject, method, object) -> (history, result, evidence)` boundary.
2. Add `problem-formation.adva`. It accepts a versioned problem-awareness
   carrier and an external imagination-resource carrier. It must construct and
   retain an exact counterexample before introducing the research words
   `problem-formation` and `problem`.
3. Freeze the first formed problem to five domains, one adversarial fault, the
   current three-receipt threshold, thresholds one through five, and five
   externally proposed feature directions.
4. Add `value-seeking.adva`. It enumerates the Cartesian product of the five
   thresholds and all 32 feature subsets in threshold-major, bit-mask order.
   Its resource supplies finite fuel and a cost budget.
5. Admit a candidate only when all noncompensating constraints hold:
   - a quorum remains formable after one unavailable domain;
   - every pair of successor quorums retains at least one honest domain after
     the adversarial budget is removed;
   - provenance, replay, challenge, and succession are each assigned to a
     distinct typed feature;
   - one additional compatible feature remains as a reserve; and
   - the declared cost is within budget.
6. Cost may order already-admissible candidates; it may not compensate for a
   missing invariant. The first value policy is therefore supplied by the
   method/resource boundary rather than derived from arithmetic.
7. Introduce `value-seeking` and `value` only when an exact witness is found.
   Persist the complete versioned witness in its producing transition and only
   its checked digest in the continued frontier.
8. Preserve suspension and exhaustion as distinct results. Fuel exhaustion is
   not nonexistence; complete exhaustion is negative only for the frozen finite
   family and predicate.

## Consequences

The current three-of-five proposal is refuted only under the declared
quorum-overlap model. The search can then find a least enumerated policy shape,
but it cannot establish that the five domains are actually independent, that
signatures or measurements are genuine, that custodians remain available, or
that the value policy deserves consent.

Imagination remains productive precisely because it crosses the interface as
explicit candidate directions and falsifiers. Replay can show which external
proposal led to which finite witness; it cannot derive the proposal from the
closed system or turn a digest into trust.
