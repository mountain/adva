# Research 0122: Problem formation and value seeking for trust continuation

## Question

Can a reality-side concern be compressed into a finite, falsifiable problem,
and can a separate bounded program find a reusable value witness without
pretending that imagination or value originated inside the closed arithmetic?

The experiment uses two `learn` programs:

| program | subject | method | object | successful result |
| --- | --- | --- | --- | --- |
| problem one | problem awareness | problem formation | imagination resource | formed problem |
| problem two | formed-problem frontier | value seeking | finite search resource | trust-continuation witness |

The first row connects problem consciousness to possible solution directions.
The second searches those directions under an explicit value policy. The rows
share the positional interface but do not collapse their carrier meanings.

## Surface problem

The input awareness records five declared custody failure domains, a current
threshold of three, and an adversarial-fault budget of one. Lexicographic
enumeration finds this counterexample after 21 quorum/fault cases:

```text
left successor quorum  = {0, 1, 2}
right successor quorum = {0, 3, 4}
shared domain          = {0}
adversarial domain     = {0}
honest overlap         = {}
```

Thus two locally accepted successors can share no honest custodian. This is
not a claim about a deployed system. It is a precise defect in the declared
policy envelope and therefore a suitable finite problem statement.

The imagination resource proposes five directions rather than answers:

| direction | protected reading |
| --- | --- |
| `signed_parent` | provenance |
| `replay_bundle` | replay |
| `fork_ledger` | challenge |
| `recovery_handoff` | succession |
| `independent_remeasurement` | replay-compatible reserve |

It also carries falsifiers and states what must still be obtained outside the
repository. The checker does not claim to have generated these directions.

## Finite value search

For each threshold from one through five, the method enumerates all 32 feature
subsets. Candidate ordinal is therefore

```text
(threshold - 1) * 32 + feature-mask
```

and the frozen family has 160 candidates. Candidate cost is threshold plus the
number of selected features. The first resource supplies 160 fuel units and a
cost budget of nine.

Admission is noncompensating. A cheap candidate that loses any protected
invariant cannot outrank a valid one. A candidate must satisfy availability,
honest successor overlap, a distinct typed assignment for all four invariants,
one compatible reserve, and the budget.

The first witness occurs at ordinal 127:

| coordinate | witnessed value |
| --- | ---: |
| threshold | 4 of 5 |
| selected features | all 5 |
| minimum intersection of two quorums | 3 |
| honest intersection after one adversarial fault | 2 |
| remaining domains after one unavailable fault | 4 |
| merge capacity | 5 |
| rupture load | 4 |
| total cost | 9 |

There are five possible four-of-five successor quorums. Any two share at least
three domains; after removing one adversarial domain, at least two honest
domains remain. Four receipts can still be collected after one of the five
domains is unavailable. Four features are assigned injectively to the four
obligations, and independent remeasurement remains as the compatible reserve.

Before that witness the run rejects 96 candidates for insufficient honest
overlap, 29 for missing invariant coverage, and two for lacking a reserve. A
resource with 127 fuel units suspends immediately before the witness and a
continued run finds it with one more candidate. With cost budget eight, all
160 candidates are exhausted without a witness: the only otherwise-admissible
candidate exceeds budget, while every threshold-five candidate fails the
one-domain-loss availability constraint.

## Word and storage formation

The first transition introduces the method word `problem-formation` and the
object word `problem`. The second introduces `value-seeking` and `value` only
after witness replay. The complete value witness carries its own research
schema/version and is embedded once in the value-seeking transition. The next
frontier retains the checked witness digest and cursor, so reuse does not copy
the full payload into every later frontier.

Reproduce both programs with:

```console
cargo run -p adva-witness --bin adva -- \
  learn \
  programs/bootstrap-0/problem-awareness.adva \
  programs/bootstrap-0/problem-formation.adva \
  programs/bootstrap-0/imagination-resource.adva \
  --output target/problem-formation-1.adva \
  --frontier-output target/problem-value-frontier-1.adva

cargo run -p adva-witness --bin adva -- \
  learn \
  target/problem-value-frontier-1.adva \
  programs/bootstrap-0/value-seeking.adva \
  programs/bootstrap-0/value-seeking-resource.adva \
  --output target/value-seeking-1.adva \
  --frontier-output target/value-seeking-frontier-1.adva
```

CI regenerates the four derived files and compares their exact bytes with the
committed artifacts.

The first retained content coordinates are:

| artifact | BLAKE3 coordinate |
| --- | --- |
| formed problem | `d60daeb4ab29e78ce7d6b7d704f3d151b1107737f3ab2d2f49893c34e031ec66` |
| trust-continuation witness | `b6eb2e78c81ef1b9f85991f6c22613c2082d4b31dafdda55f1ac169953d2c7a2` |

## Boundary

The witness is an arithmetic certificate for one policy shape, not stable
social trust. It assumes the domain count, fault model, feature meanings,
distinctness policy, candidate ordering, and cost model. It does not verify a
signature, measure an external event, prove custodian independence, prevent a
fork, execute recovery, establish consent, select a true natural-language
interpretation, or show that the proposed directions exhaust imagination.

The result nevertheless has a transferable local meaning: anyone can replay
the same counterexample and the same finite admission predicate, inspect the
external assumptions, challenge them without deleting the earlier record, and
continue from the retained frontier. Trust continuation here means preserved
conditions for accountable disagreement, not compulsory agreement.
