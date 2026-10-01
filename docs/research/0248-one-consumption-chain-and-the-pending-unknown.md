# Research 0248: One consumption chain and the pending unknown

Status: **bounded single-host process-persistence result**. This note adds no
native operation, general exactly-once guarantee or vocabulary word.

## Question and frozen boundary

Research 0247 bound one retained charge to one exact task, but its read-only
receipt could be replayed indefinitely. Verification should be reproducible;
performing an effect should not be. The next question was therefore whether a
finite persistent state could keep those two roles separate.

The [frozen contract](../../experiments/single_consumption_receipt/contract.json)
uses two exact 0246 pairs and a three-state local ledger:

```text
unconsumed -> pending -> consumed
```

The first transition is protected by an exclusive file lock. Both transitions
use same-directory replacement after file and directory `fsync`. `reconcile`
never writes. The completed state stores a project-original marker digest, not
the result of a real effect. No command authorizes or starts a target program.

The contract fixes sixteen tool processes, zero target processes, 20,000
counted units, fifteen outer seconds, one declared exit after `pending`, zero
search candidates and zero implementation-correction replays. This is a trusted
Linux-host experiment. It does not modify Research 0090, 0092, additive zero,
multiplicative unity, ordered M6 histories, hypothesized arithmetic truth or
arithmetic universality.

## Executed state distinctions

Two normal chains completed:

- alpha: seven-unit parent pair;
- gamma: a different task, pair digest and eleven-unit parent amount.

Each moved once from `unconsumed` to `pending` and once from `pending` to
`consumed`. A later read-only reconciliation returned `StoredConsumed`. A
second alpha reservation returned the same stored receipt and did not mutate
the ledger.

Two incomplete cases exposed the boundary:

1. A process wrote `pending` and exited with the declared code 23 before
   emitting a receipt. Independent reconciliation returned
   `UnknownConsumptionState`; a later reservation returned the same outcome and
   did not clear or replace the pending attempt.
2. Two processes contended for one `unconsumed` gamma ledger. Exactly one
   returned `PendingRecorded`; the other returned
   `UnknownConsumptionState`. The retained ledger contained one attempt only.

A wrong pair digest returned `InvalidContext`, left the ledger unconsumed and
did not change its bytes. Across every receipt, effect, retry, refund, native and
`free` authority stayed false.

The key distinction is consequently finite and operational:

| State | Read-only result | Later reservation |
| --- | --- | --- |
| `unconsumed` | `ProvenUnconsumed` | may record the sole pending slot |
| `pending` | `UnknownConsumptionState` | blocked, no retry |
| `consumed` | `StoredConsumed` | blocked, existing receipt retained |

These are local experiment outcomes, not promoted framework words or native
judgments.

## Cost and replay

The [retained execution](../../experiments/single_consumption_receipt/evidence/attempt-1/execution.json)
passed 115 assertions over sixteen tool processes and zero target processes.
Receipted paths reported 4,408 structural work units. The deliberately exited
process emitted no receipt, so its structural cost is unmeasured rather than
zero. Tool-process wall subtotal was 0.7801158830000077 seconds and the whole
supervisor interval was 0.7860221089999868 seconds. Maximum child and supervisor
RSS were each 11,904 KiB. There were zero search candidates and zero correction
replays. Reading, implementation and publication time were not measured.

Replay from the repository root with a new output path:

```sh
python experiments/single_consumption_receipt/run.py \
  --output /tmp/adva-single-consumption
```

The alpha and gamma parent account/journal bytes are pinned separately. The
second pair is the required new-instance reuse; it does not inherit state from
alpha.

## Meaning and remaining obligation

No new word is justified. The existing distinctions between verification,
pending state, committed state, invalid context and unknown state suffice.
`UnknownConsumptionState` is a local diagnostic describing this exact ledger
profile.

This helps Mingli and subsequent agents avoid turning a reproducible proof of a
binding into a reproducible permission for an effect. It also gives a concrete
stop rule after a process disappears: retain `pending`; do not refund, retry or
silently complete it. Its value for Jiamin's actual task remains unmeasured.

The stored marker is test data and does not show that a real target effect ran.
`flock`, atomic replacement and `fsync` were exercised only on one trusted Linux
filesystem. There was no power cut, disk failure, hostile process, network,
distributed participant or authenticated identity. The result is not a general
exactly-once implementation. It establishes neither native `free`, `Close`, M6
closure nor arithmetic universality.

The next minimum step is to separate **effect evidence** from the local marker.
A versioned receiver should accept one externally produced, independently
checkable result digest for the pending attempt, refuse a result bound to a
different pair or attempt, and leave missing or conflicting evidence at
`UnknownConsumptionState`. It should still not run the effect itself.

Authored by Codex (OpenAI), contributed under Unknown v0.3 through Mingli
Yuan's authorized GitHub account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee.
