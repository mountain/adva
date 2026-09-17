# Finite continuation ledger and the commit/reply boundary

Original research by ChatGPT (OpenAI), 2026-09-17, through Mingli Yuan's
authorized account proxy. Account use is not his review, endorsement or a
correctness guarantee. Original code, synthetic inputs and generated evidence
are contributed under Unknown v0.3. No external document or software is vendored.

## Question and frozen scope

PR #189 established a stateless checkpoint checker: a complete prefix may be
retained even when history capacity or abstract allowance blocks its pending
step. Repeating that checker does not by itself implement an acceptance ledger.

Starting from main `03c9c12`, this [contract](contract.json) fixes one
receiver-owned SQLite database, one complete expected checkpoint request, and
one accepted continuation slot. The finite effect is a stored checked receipt
and one abstract allowance debit in that same database. No decision action is
executed. The unchanged checkpoint, composition, scale, decision and probability
receivers remain the arithmetic checking chain.

The observation to test is narrow: **an absent reply does not tell a sender
whether the receiver committed**. A retry must consult the original receiver's
record rather than infer a fresh allowance from the sender's silence.

## Representation and state rule

Initialization is explicit and refuses an existing path. Submission opens only
an existing database. A missing file cannot silently become a renewed ledger.
The metadata binds the complete canonical expected request, initial/current
allowance and SHA-256 fingerprints of the ledger receiver and all five ancestor
receivers. Fingerprints are version checks, not authentication or native IDs.
This run tests matching fingerprints; adversarial checker/storage substitution
is not part of the executed family.

The candidate has exactly `profile`, `transition_key` and
`checkpoint_receipt`. A transition key is local to this ledger. Canonical
comparison preserves array order, histories and integer types while ignoring
JSON object-key ordering and whitespace. The full candidate and deterministic
result are stored, not only their digests.

Let the initial allowance be `(grant, spent, remaining) = (3,2,1)`. The only
committing state change in an accepted fixture is:

\[
  (\text{empty slot},(3,2,1))
  \longrightarrow
  (\text{one bound result},(3,3,0)).
\]

| Receiver state and input | Outcome | New debit |
| --- | --- | ---: |
| Empty slot, checked admissible continuation | `CommittedContinuation` | 1 |
| Occupied slot, same key and canonical candidate | `ReplayedContinuation` | 0 |
| Occupied slot, same key with changed candidate | `Conflict` | 0 |
| Occupied slot, different key | `PausedLedgerCapacity` | 0 |
| Changed expected question or allowance | `InvalidContext` | 0 |
| Empty slot, invalid parent receipt | `InvalidEvidence` | 0 |
| Empty slot, parent history/allowance pause | Parent pause | 0 |

The parent result contains the outcome, reason, retained checkpoint, resulting
allowance and original semantic delta. Per-call timing, work, debit delta and
replay status are outside that stored result. Replay retrieves an old checked
fact from trusted storage; `parent_checked=false` explicitly distinguishes it
from fresh arithmetic verification. It introduces no new theorem or native use.

The receiver executes `BEGIN IMMEDIATE`, validates its metadata and checks an
empty-slot candidate, then inserts the result and updates allowance within one
transaction. New success is reported only after `COMMIT`. Pauses and refusals
leave the logical tables unchanged. A COMMIT exception whose state is uncertain
requires reconciliation with the existing ledger; it does not claim a safe reset.

## Executed process-exit witnesses

The independent supervisor launches 48 fresh processes and checks SQLite rows
itself, without importing the ledger receiver. One symmetric fixture is reused
with a new asymmetric instance: prior `(3/5,2/5)`, observation rows
`(2/3,1/3)` and `(1/4,3/4)`, losses `((0,3),(2,0))`, cost `1/10`.
Both have scale steps `2`, `1/2`, and pending `3/2`, all within inherited bounds.

All 328 supervisor assertions pass:

- Twelve ledgers initialize, six in each family.
- Six successful submissions return a newly committed result. Two additional
  submissions commit but deliberately lose their reply. Thus eight databases
  record one accepted transition and one debit each; the four paused databases
  have no accepted transition.
- Eight retries return exactly the stored result with zero additional debit,
  including canonical JSON reordering and recovery of the two lost replies.
- Two actual exits with code 17 occur *after INSERT and UPDATE but before
  COMMIT*. The next independent SQLite reopen observes the original allowance
  and an empty slot. A later fresh submission commits once.
- Two actual exits with code 19 occur *after COMMIT but before stdout*. Their
  stdout files are empty. Independent reopen observes the committed row; retry
  recovers that exact result without another debit.
- Two same-key conflicts, two different-key capacity refusals, two changed
  expected-context refusals, two reinitialization refusals, two missing-ledger
  refusals and two false-parent refusals preserve the prior logical ledger.
  False parent receipts do not poison the slot: subsequent valid submissions
  still succeed.
- Four history-capacity pauses and two zero-allowance pauses leave their
  ledgers unchanged. The underlying pending problem is retained in the request
  and returned checkpoint.

The four injected exits are intended observations, not implementation failures.
No corrective execution replay was required. Pre-execution static review added
explicit snapshot-connection closing, exact fault-phase checks and a campaign
deadline, and clarified the partial construction sub-timer.

## Transaction assumptions and remaining boundary

SQLite is configured with rollback-journal mode `DELETE`, `synchronous=FULL`,
explicit transactions and a 100 ms busy timeout. Its atomic-commit behavior
depends on the storage and operating-system assumptions described in the
[SQLite documentation](https://www.sqlite.org/atomiccommit.html). Python's
[transaction control documentation](https://docs.python.org/3/library/sqlite3.html#transaction-control)
describes explicit SQL transactions with `isolation_level=None`.

This experiment uses Python 3.12.14 and SQLite 3.53.1. It tests the two declared
process exits on trusted sequential local storage. It does not test power loss,
all journal/page-flush positions, disk-full conditions, network filesystems,
concurrent requests, corrupted/hostile databases or arbitrary storage rollback.
The schema and fingerprint checks do not provide cryptographic authentication.
Exactly-once delivery, external task execution and distributed transactions are
not established. A caller able to replace trusted storage lies outside this
contract. One accepted slot is not arbitrary continuing computation.

The [communication framework](../../docs/COMMUNICATION_FRAMEWORK.md) already
distinguishes reception, acceptance and observation of a reply. This is one
external calibration of its repetition/recording requirements, not general
communication conformance or a native `communicate` implementation. No new
vocabulary, `Close`, `free`, M6 closure or universal grammar result is claimed.

## Cost and reproducibility

The campaign has a 30 s alarm, at most 52 child invocations, three seconds per
child, 128 MiB child address space, a 192 KiB input envelope, a 128 KiB parent
envelope and a one-MiB database bound. Receiver work counts fixed SQL statements
and nested parent checks cumulatively, capped at 10,000 per invocation; the
largest observed invocation uses 1,337 units. SQLite's internal instructions
and recovery reads are timed but not counted as parent instruction work.

| Actual measurement | Value |
| --- | ---: |
| Primary fixture construction, partial sub-timer | 0.009604404 s |
| Input and observation serialization | 0.741841793 s |
| Fresh child startup and receiving | 10.003268232 s |
| Independent SQLite observations/recovery reads | 0.386565460 s |
| Complete campaign before final report write | 11.337059400 s |
| Cumulative receiver work, including injected exits | 24,914 units |
| Highest child peak RSS | 14,336 KiB |
| Supervisor peak RSS | 15,872 KiB |

Some control copies and pause envelopes are outside the construction sub-timer
but inside total campaign time. Reuse is included, not separately timed.
Final report writing, archiving, research, review, CI and publication are excluded.
File size is not a memory estimate. Cheap replay is not reported as acceleration:
it retrieves a stored result under stronger storage assumptions instead of
doing the same verification task more quickly.

From the repository root, choose a new output directory:

```sh
timeout 35s python3 -B -S experiments/decision_ledger/run.py --output /tmp/adva-decision-ledger-fresh
```

[The summary](evidence/result.json) retains all process outcomes, actual return
codes, timings and thirteen source hashes. [The manifest](evidence/manifest.json)
inventories every archived member, including exact requests, candidate bytes,
commands, stdout/stderr, before/after logical database snapshots and final
SQLite files. Use a new directory for a new campaign; archived databases are
historical evidence, not permission to initialize or reset a live receiver.

The result helps Mingli and later agents avoid charging a completed continuation
again when its reply was lost. Jiamin's actual decision benefit is unmeasured.
The next smallest step is a separately bounded two-process contention test:
distinguish a busy database from a corrupt ledger while checking whether two
simultaneous submissions can still produce only one debit. Concurrency is not
tested or authorized by the result here.
