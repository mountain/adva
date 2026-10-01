# Research 0252: Read-only terminal resolution receiving

Status: **bounded independent receiving result**. This note adds no native
operation, retry permission, exactly-once guarantee or vocabulary word.

## Question and frozen boundary

[Research 0251](0251-atomic-recovery-application-and-scoped-cancellation.md)
writes one local terminal from a pending ledger and an exact recovery receipt.
This run asks whether a separate read-only receiver can verify the resulting
archived projection without opening the runtime lock or mutable ledger.

The [frozen contract](../../experiments/terminal_resolution_receiver/contract.json)
binds a query to the exact attempt, pair and SHA-256 coordinates of three input
files: the source pending bytes, the Research 0250 recovery receipt and the
Research 0251 terminal. Ten receiver processes have one second each, an outer
twenty-second limit and 30,000 counted work units. Search candidates and target
processes are zero. The inputs and receiver are project-original canonical
JSON and Python.

The receiving rule is:

\[
  Q(P,R,T)\;\land\;T=\operatorname{project}(P,R)
  \quad\Longrightarrow\quad
  \mathsf{ResolutionVerified}(T).
\]

Here \(Q\) binds the precise archived bytes. Missing bytes, digest divergence,
whole-object substitution or a different terminal projection yield
`UnknownResolutionState`. Noncanonical or malformed bytes yield
`InvalidEvidence`. None of these outcomes changes an archive or grants an
effect, retry or refund.

## Executed distinctions

All 58 supervisor assertions passed.

| Case | Result | Meaning |
| --- | --- | --- |
| Alpha exact positive archive | `ResolutionVerified(completed)` | source, recovery and complete terminal projection agree |
| Gamma exact finite no-effect archive | `ResolutionVerified(cancelled)` | scoped cancellation retains the finite channel and interval |
| Delta post-replace archive | `ResolutionVerified(completed)` | the terminal can be recovered although its writer emitted no stdout |
| Missing terminal | `UnknownResolutionState` | absence is not noncommitment |
| Gamma source with Alpha query | `UnknownResolutionState` | source digest divergence |
| Gamma recovery with Alpha query | `UnknownResolutionState` | recovery digest divergence |
| Changed terminal bytes | `UnknownResolutionState` | terminal digest divergence |
| Complete Gamma object under Alpha query | `UnknownResolutionState` | a valid answer to another question is not this answer |
| Noncanonical terminal encoding | `InvalidEvidence` | representation failure is not a semantic counterexample |
| Self-consistently hashed but wrong terminal state | `UnknownResolutionState` | complete projection, not hash agreement alone, is required |

All supplied input hashes were identical before and after each receiver call.
The receiver interface has no lock argument and no mutable-ledger argument. It
starts no target process and every effect, retry, refund, mutation, native and
`free` authority flag is false.

## Cost and retained correction

The [valid execution](../../experiments/terminal_resolution_receiver/evidence/attempt-1/execution.json)
records:

- 10 receiver processes and zero target processes;
- 58 assertions;
- 29,184 counted work units on receipted structural paths;
- 0.3410725769972487 seconds summed receiver wall time;
- 0.35320999399846187 seconds whole-supervisor wall time;
- maximum child and supervisor RSS of 11,776 KiB each;
- zero search candidates and one implementation-correction replay.

The noncanonical-input receiver returns before emitting its internal structural
counter, so its structural work is unmeasured rather than zero; its process
time remains included. Construction and serialization are included in the
whole-run interval but were not separately timed.

The [first retained run summary](../../experiments/terminal_resolution_receiver/evidence/prior-implementation-failure.json)
classifies a nonportable evidence record. It passed the same semantic cases but
embedded absolute workspace paths. The sole allowed correction changed only
path presentation to repository-relative coordinates and then replayed the
frozen cases. No archive or outcome changed.

## Meaning and residual

No new word is justified. `ResolutionVerified` and
`UnknownResolutionState` remain local receiver outcomes. The useful distinction
is that an atomically written terminal becomes independently checkable only
when the original question and every source coordinate travel with it.

This helps Mingli and subsequent agents verify a completed or bounded-cancelled
continuation without reopening mutable runtime state, while refusing a coherent
but substituted answer. Its value for Jiamin's actual task remains unmeasured.

The result does not authenticate the archive producer, prove physical channel
exclusivity, survive malicious replacement, establish power-loss or disk
durability, or provide distributed exactly-once execution. It establishes
neither Research 0090 coverage, Research 0092 promotion, native `free` or
`Close`, M6 closure, hypothesized arithmetic truth nor arithmetic universality.

The next minimum step is to bind this terminal-resolution receipt into a
continuation request and check a narrow rule: only `ResolutionVerified` may
advance the exact same problem-history-budget tuple; `UnknownResolutionState`
and `InvalidEvidence` must preserve it byte for byte and grant no new fuel.

Authored by Codex (OpenAI), contributed under Unknown v0.3 through Mingli
Yuan's authorized GitHub account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee.
