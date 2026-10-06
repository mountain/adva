# Research 0253: Terminal resolution and the exact continuation tuple

Status: **bounded read-only receiving result**. This note adds no native
operation, framework `accept`, continuation permission, new fuel or vocabulary
word.

## Question and frozen boundary

[Research 0252](0252-read-only-terminal-resolution-receiving.md) can verify one
archived completed or scoped-cancelled terminal, but its receipt is not yet
bound to the continuation that would use it. This run asks one narrow question:
can a separate receiver bind that receipt to the exact same
problem--history--budget tuple, while every unknown or invalid result preserves
the tuple and adds no fuel?

The [initial contract](../../experiments/continuation_resolution_gate/contract.json)
freezes ten receiver processes, zero targets, 40,000 counted work units, one
second per receiver, twenty outer seconds and zero search candidates. The tuple
keeps three distinct components:

1. a problem identifier, attempt, pair, parent resolution-query coordinate and
   allowed terminal states;
2. an ordered two-entry history binding the parent query and receipt bytes;
3. an exact natural-number budget satisfying
   `initial_units = spent_units + remaining_units`.

The gate query binds the canonical tuple bytes and terminal-resolution receipt
bytes separately. `ContinuationReady` requires those exact coordinates, an
exact history link, parent `ResolutionVerified`, and agreement of attempt, pair
and allowed terminal state. The receiver only classifies a finite presentation;
it does not authorize a later computation.

Because a review of the merged predecessor exposed reliance on ordinary Python
assertions and direct evidence creation, this run also freezes two implementation
conditions. The supervisor and all receivers run with `python -O`, while every
check uses explicit rejection rather than `assert`. New evidence uses a
write-new temporary file, file synchronization, same-directory atomic
replacement and directory synchronization. These choices narrow an engineering
failure mode; they are not a power-loss proof.

## Executed distinctions

The sole valid replay passed 75 explicit checks over ten receiver processes.

| Case family | Outcome | Retained distinction |
| --- | --- | --- |
| Exact Alpha completion | `ContinuationReady(completed)` | exact selected tuple and receipt agree |
| Independent Gamma scoped cancellation | `ContinuationReady(cancelled)` | reuse on a different attempt, pair and budget |
| Parent terminal result remains unknown | `UnknownContinuationState` | an unresolved terminal cannot advance the tuple |
| Parent terminal result is invalid | `InvalidEvidence` | representation failure is not converted into readiness |
| Complete Gamma object under the Alpha gate query | `UnknownContinuationState` | a coherent substituted answer is not the selected answer |
| Self-consistent tuple with another attempt | `UnknownContinuationState` | updating the outer digest does not repair problem divergence |
| Self-consistent tuple with another history receipt digest | `UnknownContinuationState` | history must bind the exact received bytes |
| Changed budget under the old gate query | `UnknownContinuationState` | the budget is part of the selected tuple |
| Undeclared `replenishment_units` field | `InvalidEvidence` | this profile has no fuel-extension field |
| Noncanonical tuple bytes | `InvalidEvidence` | representation failure remains separate from semantic unknown |

For every syntactically valid tuple, the receipt's preserved object encodes to
the exact original bytes. For every case, all input digests before and after are
identical and `fuel_delta` is zero. All effect, retry, refund, mutation, native
and `free` authority flags remain false; no target starts.

The Alpha budget is exactly `(20, 7, 13)` and Gamma is `(23, 11, 12)` in
`(initial, spent, remaining)` order. They are project-original finite fixtures,
not reconstructions of all historical research costs. Their purpose is to test
typed preservation and no replenishment.

## Failure, correction and measured cost

The first execution stopped after nine receivers. The receiver correctly
returned `InvalidEvidence` for the undeclared replenishment field and returned
no parsed tuple; the supervisor incorrectly required every dictionary-shaped
input, including a rejected one, to round-trip as a parsed object. The nine
case directories are retained under
[`evidence/attempt-1`](../../experiments/continuation_resolution_gate/evidence/attempt-1/),
and the [failure record](../../experiments/continuation_resolution_gate/evidence/prior-implementation-failure.json)
classifies the result as `ImplementationFailure`, not a mathematical
counterexample.

The separately frozen
[correction contract](../../experiments/continuation_resolution_gate/correction-contract.json)
permits one change: require byte equality when the receiver returned a parsed
tuple, and otherwise require the expected `InvalidEvidence`. It changes no
receiver, input, semantic outcome, authority flag or resource limit. The sole
correction replay then produced the
[valid execution](../../experiments/continuation_resolution_gate/evidence/attempt-2/execution.json):

- 10 receiver processes and zero target processes;
- 75 explicit supervisor checks;
- 25,960 counted work units;
- 1.2213635359948967 seconds summed receiver time;
- 1.2313895620027324 seconds whole-run time;
- 16,696 KiB maximum measured child and supervisor RSS;
- 23,102 serialized case-payload bytes before the execution record;
- zero search candidates.

Across both attempts, 19 receivers report 51,920 counted work units and the
summed observed outer intervals are about 2.490643414 seconds. The failed
attempt stopped before recording peak memory, so the aggregate peak is
unmeasured; 16,696 KiB is only the highest measured value. Construction,
authoring and publication time are not measured. A later validation invocation
could not start `pytest` because that module is absent; direct standard-Python
loading then passed both test functions and launched one temporary ten-receiver
optimized replay. The combined direct-test, compile and claim-parse command took
1.567572069 seconds; that temporary replay's structural work was checked below
40,000 units but was not retained separately. Eight research-index checks also
passed in 0.118584962 seconds. The publication-boundary history check scanned
5,303 unique blobs and 14,097 members in 9.5025538 seconds and found no identified
withdrawn copy. The full accounting is in
[`evidence/summary.json`](../../experiments/continuation_resolution_gate/evidence/summary.json).

## Meaning and residual

No new word is justified. `ContinuationReady`, `UnknownContinuationState` and
`InvalidEvidence` are local protocol outcomes. The result says only that one
selected finite tuple and one selected Research 0252 receipt can be checked
together without changing the tuple or its budget. It does not itself perform
the next continuation.

This helps Mingli and subsequent agents prevent three handoff errors: advancing
after an unresolved terminal, attaching a correct receipt to the wrong problem
or history, and silently replacing the selected budget or adding fuel. Its
value for Jiamin's actual task remains unmeasured.

SHA-256 coordinates are not authentication. The experiment trusts its local
Python implementation and project-original archive. Atomic replacement and
`fsync` on this host do not prove power-loss durability, filesystem correctness,
hostile-process containment, distributed consistency or exactly-once execution.
The gate does not implement native `communicate`, `accept`, `free` or `Close`,
establish Research 0090 coverage or Research 0092 promotion, close M6, prove
hypothesized arithmetic truth or establish arithmetic universality.

The next minimum step is not to spend the preserved budget. It is to give a
second implementation the same gate query, tuple and receipt and require the
same three-way classification plus a byte-identical preserved tuple. Divergence
must remain unknown; agreement would still be finite implementation comparison,
not independent human review or native authority.

Authored by ChatGPT (OpenAI), contributed under Unknown v0.3 through Mingli
Yuan's authorized GitHub account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee.
