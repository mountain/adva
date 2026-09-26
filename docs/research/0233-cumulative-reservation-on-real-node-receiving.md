# Research 0233: Cumulative reservation on two real Node receipts

Status: **finite integration passed after one retained `InvalidContext` attempt**.
This note adds no native operation, theorem or vocabulary word.

## Question and frozen boundary

The merged cumulative supervisor had been tested only with tiny synthetic
children. The next open question was whether it could surround the existing
Node implementation of `commit-state-reconcile` without losing either the
semantic result or the resource history.

The [revised contract](../../experiments/cumulative_node_receiver/contract.json)
selects exactly two archived project-original cases:

- `symmetric-empty`, expected to return `ProvenUncommittedLedger`;
- `symmetric-committed`, expected to return `StoredCommitted`.

For each case the supervisor reserves 15,361 abstract units before starting
Node: the receiver's calibrated limit of 15,360 plus the possible tick that
detects exhaustion after increment. The correction replay may start exactly
two Node processes. Its task allowance is 30,722 units and two calls. The
cumulative account imports the first attempt's two reservations by exact byte
digest, so the overall bounds are 61,444 units and four calls. No search,
automatic retry or further correction is allowed.

The receiving inputs, the earlier Python observations, the Node source and the
supervisor source are pinned. The Node receiver may read only the three JSON
files supplied to it; its source imports only Node crypto, filesystem and
performance modules. It does not import Python, open SQLite or run another
process. Python supervises, independently recounts finite JSON values and
compares semantic projections. It does not grant native authority.

## Retained implementation error

The first execution produced the expected two semantic observations, but its
contract recorded a nonexistent full main coordinate ending in `87bd`. The
actual checked main was
`19ac70e4886a3096bec00c3f4ba0008fbdc48c5d`. That mismatch is unrelated to
the snapshot values, but it breaks exact context binding. The attempt is
therefore retained as `InvalidContext`, not promoted to evidence.

Its two reservations, 30,722 units in total, remain charged. The v1 cumulative
account imports the exact old account, execution, contract and runner digests.
The sole correction replay then charges two more reservations. This is an
explicit revised finite contract, not a reset or refund. Both complete attempts
and both exact executed sources are retained in the evidence archive.

## Result

All 82 correction-replay assertions passed.

| Case | Node outcome | Reserved | Reported receiver work | Unused reservation |
| --- | --- | ---: | ---: | ---: |
| symmetric empty | `ProvenUncommittedLedger` | 15,361 | 6,841 | 8,520 |
| symmetric committed | `StoredCommitted` | 15,361 | 14,207 | 1,154 |

For both cases:

- the complete semantic projection equals the archived Python result;
- independent Python traversal matches the Node value-node count for the
  request and both snapshots;
- `work_units` equals value nodes plus checks and remains below 15,360;
- SQLite and ledger-path flags are false;
- parent checking, debit, retry, native authority, `close` and `free` remain
  false.

The replay task journal ends with exactly two reservations totalling 30,722.
The cumulative account ends with four reservations totalling 61,444. An
additional task reservation and an additional cumulative charge are both
refused without changing their files. A changed task context is also refused.
The receiver's reported work is 21,048 in each attempt, 42,096 across both;
the conservative reserved total remains 61,444 and is not reduced to reported
work.

This establishes only that the declared reservation interface can wrap these
two real trusted receiver invocations while retaining a correction's previous
cost. It does not make the receiver's abstract counter a hard CPU fuel meter.

## Costs and replay

The invalid-context attempt used two Node processes, 74 assertions, 38,543
Python verifier units and 0.257062488 seconds wall time. Its Node subtotal was
0.221725499 seconds. The valid correction replay used two Node processes, 82
assertions, 38,727 verifier units and 0.201672876 seconds wall time; its Node
subtotal was 0.164872503 seconds. The two separately timed attempts therefore
sum to 0.458735364 seconds wall and 0.386598002 seconds Node time. They are not
one continuous elapsed measurement.

Across both attempts, the maximum observed child RSS was 49,636 KiB and the
maximum supervisor RSS was 14,592 KiB. These are category maxima, not
concurrent total memory. Packaging took 0.047452510 seconds and byte-for-byte
archive verification took 0.004170595 seconds. The archive has 40 files,
814,994 expanded bytes and 48,217 compressed bytes, with SHA-256
`35304bdab2842a134cb16b7d71621a5a79cec136d078a7f725bea536d086c1ce`.
There were zero search candidates and exactly one implementation correction
replay. Reading, coding and publication time were not measured.

From the repository root, replaying the second attempt requires the exact
first-attempt files and account retained in the evidence archive. Extract them
outside the repository, then run:

```sh
timeout 25s python3 experiments/cumulative_node_receiver/run.py \
  --output /tmp/adva-cumulative-node-attempt-2 \
  --trial-account /tmp/adva-cumulative-node-trial-v1.json \
  --prior-trial-account /tmp/attempt-1/trial-account.json \
  --prior-attempt /tmp/attempt-1
```

The output and trial-account paths must not exist. Reusing a different prior
account or changing the old source is rejected by digest. See the
[authoritative execution](../../experiments/cumulative_node_receiver/evidence/execution.json),
[invalid-context classification](../../experiments/cumulative_node_receiver/evidence/prior-invalid-context.json)
and [manifest](../../experiments/cumulative_node_receiver/evidence/manifest.json).

## Meaning and remaining boundary

No new word is justified. The existing Proposed
`commit-state-reconcile`, `InvalidContext`, correction and cumulative resource
distinctions are sufficient. This result helps Mingli and subsequent agents
connect a real receiving check to a finite allowance without making a
correction erase earlier cost. Its value for Jiamin's actual task remains
unmeasured.

The work counter is still supplied by trusted receiver code; wall timeout and
Node's old-space setting are separate and do not bound all CPU or physical
memory. The supervisor assumes one local writer, intact files and the host OS.
It supplies no authentication, malicious-child containment, power-loss
recovery or distributed consistency. The first attempt's semantic results are
retained only as observations; its false context coordinate remains invalid.

This does not prove arithmetic universality, hypothesized arithmetic truth,
Research 0090 coverage, Research 0092 promotion, M6 closure or native
`free`. Additive zero and multiplicative unit keep their separate typed
domains, nonzero conditions and ordered histories.

The next smallest step is to interrupt the narrow window after the cumulative
account is charged but before the task journal records its reservation. A
read-only reconciler should retain that charge, return an unknown launch state
and forbid process start until the two records are explicitly coordinated.

Original experiment, code and analysis by Codex (OpenAI), contributed under
Unknown v0.3 through Mingli Yuan's authorized account proxy. Account use is not
his review, endorsement or correctness guarantee. No external content was
incorporated.
