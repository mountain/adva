# A saved prefix is not permission to append a step

Original research by ChatGPT (OpenAI), 2026-09-17, through Mingli Yuan's
authorized account proxy. Account use is not his review, endorsement or a
correctness guarantee. The code, synthetic fixtures and report are contributed
under Unknown v0.3; no external text or dataset is incorporated.

## Question and dependency

The two-step scale experiment at `2444b1f` preserves complete intermediate
receipts and both history entries. Its unchanged decision profile admits at
most four history entries. Can a receiver reload that complete checked prefix
without silently treating preservation as permission to continue?

The earlier `experiments/continuation_binding/` already checked exact state,
failure-parent and abstract allowance binding. This experiment adds the narrow
case of a *valid arithmetic prefix at an unsupported next-history boundary*.
It does not claim to invent checkpointing or general recovery.

The frozen [contract](contract.json) precedes execution. An independent producer
constructs receipts; a fresh receiver rechecks them through the unchanged
composition, scale, decision and probability receivers. Python and Fraction
remain shared trusted dependencies. The source hashes are in the retained
execution result. No native machine, library import or semantic ID is created.

## Exact input, output and order

The receiver selects `prefix_request`, `pending_step` and an abstract
`allowance = {grant, spent, remaining}`. The candidate carries the complete
prefix receipt, exact endpoint, pending step and allowance in a checkpoint,
plus a possible third-step receipt and `allowance_after`.

Pending factors, labels and numeric bounds are validated before the history
gate. For example, a legal prefix with losses `8 -> 16 -> 8` does not hide the
unsupported pending multiplication by 16: its next loss would be 128. This is
`InvalidContext`, not a harmless history pause or a mathematical counterexample.

After the entire prefix is independently checked and bound:

| Boundary | Required candidate | Result |
| --- | --- | --- |
| Endpoint has four history entries | Null next receipt, unchanged allowance | `PausedHistoryCapacity` |
| Endpoint has space, remaining allowance is zero | Null next receipt, unchanged allowance | `PausedAllowance` |
| Endpoint has space and allowance | Full next scale receipt, exact previous endpoint receipt, one-unit debit | `AcceptedCheckpointContinuation` |
| Changed binding, false result or unauthorized continuation | No accepted checkpoint/result | `InvalidEvidence` |

History capacity takes precedence when both gates are exhausted. A pause retains
the full prefix, endpoint and pending task, without adding a semantic result.
Refusals retain the receiver-selected request and an empty semantic delta.
The original candidate remains in the evidence, even when rejected.

The abstract attempt allowance is bounded by four and obeys
`remaining = grant - spent`. It accounts for a proposed next receipt, not the
CPU cost of checking it. Verification costs are measured separately, and all
ancestor checks spend a single cumulative receiver work budget. This stateless
checker does not consume an external resource or prevent repeated submissions.

## Executed witnesses

One campaign runs 37 fresh receiver processes and passes 211 supervisor
assertions:

- Two continuations pass, including an asymmetric prior/kernel/loss reuse.
  One initial history entry becomes three after the prefix and exactly four
  after the next checked step. Allowance `3/2/1` becomes `3/3/0`.
- Four capacity pauses include two initial checks and two reloads. Each reload
  actually reads `checkpoint_retained` from the preceding receiver's output
  file. All four entries and the pending task survive unchanged; next-step
  checking does not run.
- Two no-allowance cases pause. Supplying an otherwise valid next receipt at
  zero allowance is separately refused in both families.
- Twenty-two evidence controls are refused, including history deletion,
  allowance renewal, changed pending factor, equal-valued prefixes with
  different histories, false prefix/next arithmetic, substituted next source,
  execution on pause, and incorrect debits.
- Seven unsupported expected contexts are refused, including Boolean,
  negative or inconsistent allowance, invalid pending factors and the pending
  arithmetic overflow above.

No runtime failure or correction replay was needed. Static review before the
first run corrected a proposed reload that merely reused a producer copy, and
added the zero-allowance execution controls. The final frozen contract and exact
executed sources are preserved; neither change was a post-result repair.

## Reproduction and retained evidence

From the repository root, use a fresh output directory:

```sh
timeout 35s python3 -B -S experiments/decision_checkpoint/run.py --output /tmp/adva-decision-checkpoint-fresh
```

Replay a retained input independently after unpacking the archive:

```sh
tar -xzf experiments/decision_checkpoint/evidence/attempt-1.tar.gz -C /tmp
python3 -B -S experiments/decision_checkpoint/receive.py --expected /tmp/attempt-1/symmetric/continue/expected.json --candidate /tmp/attempt-1/symmetric/continue/candidate.json
```

[The manifest](evidence/manifest.json) inventories every archive member with
bytes and SHA-256. [The execution summary](evidence/result.json) records per-case
outcomes, reasons, work, timing and all eleven source hashes. Each exact request,
candidate, stdout and stderr is retained. SHA-256 is an integrity inventory,
not a signature or source authentication claim.

The campaign cap is 30 seconds / 40 processes; each receiver is capped at three
seconds, 128 MiB address space and 10,000 cumulative work units. There is no
search. The outer wire limit is 128 KiB, with unchanged 64 KiB composition and
32 KiB scale envelopes enforced inside it.

| Measured cost | Result |
| --- | ---: |
| Construction | 0.066015306 s |
| Input serialization and reload | 0.315611238 s |
| Child startup and receiving | 7.257405945 s |
| Complete campaign before final report write | 7.815981434 s |
| Cumulative receiver work | 29,381 units |
| Largest single receiver work | 1,299 units |
| Highest child peak RSS | 13,036 KiB |
| Supervisor peak RSS | 16,768 KiB |

Reuse and checkpoint roundtrip are included but not separately timed. Final
report writing, archiving, research, static review, CI and publication are not
included in those measurements. Archive size is not used as a memory estimate.
These are finite reliability checks, not measured acceleration.

## Residual and next smallest step

No new vocabulary is needed. The result helps Mingli and later agents preserve
an unfinished decision without erasing the path that makes it meaningful.
Jiamin's actual observations, preferences and benefit remain unmeasured.

There is no durable transaction, exactly-once ledger, authentication, concurrent
recovery, capacity enlargement, arbitrary-length composition, physical unit
certification, action execution, native fuel, `Close`, `free`, M6 closure or
universal grammar result. In particular, a history-capacity pause stays paused
on replay: saving it cannot manufacture more room.

The next small obligation is to bind a *receiver-owned finite ledger* to the
accepted continuation: an identical repeated submission should return the prior
result without another abstract debit, while a conflicting submission under the
same transition key must be refused. That needs a new bounded contract and
explicit transaction assumptions; it is not implemented here.
