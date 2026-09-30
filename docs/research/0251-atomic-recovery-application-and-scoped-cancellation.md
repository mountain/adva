# Research 0251: Atomic recovery application and scoped cancellation

Status: **bounded local application result**. This note adds no native
operation, general exactly-once guarantee, retry permission or vocabulary word.

## Question and frozen boundary

[Research 0250](0250-pending-effect-and-bounded-no-effect-witnesses.md) can
receive later evidence about one pending consumption attempt, but its receipts
are read-only. This run asks whether exactly one such receipt can be applied
atomically to the unchanged pending ledger while replay, conflict, insufficient
evidence and context substitution remain non-authorizing.

The [frozen contract](../../experiments/recovery_receipt_application/contract.json)
fixes six invocations of the pinned Research 0250 receiver and ten application
processes. Each process has a one-second limit; the outer run has twenty
seconds, 50,000 counted work units, zero search candidates, zero target
processes and at most one implementation-correction replay. Inputs are
project-original canonical JSON. The storage assumptions are one trusted Linux
host, fcntl exclusion, same-directory atomic replacement, and file and
directory synchronization.

The application grammar is:

\[
\begin{aligned}
  \mathsf{pending}+\mathsf{EffectWitnessVerified}
      &\longrightarrow \mathsf{completed},\\
  \mathsf{pending}+\mathsf{NoEffectWitnessVerified}
      &\longrightarrow \mathsf{cancelled}_{C,[a,b]}.
\end{aligned}
\]

The second terminal retains the exact channel (C), closed interval
([a,b]), witness digest and null result digest. It means only that the
declared complete finite channel had no matching event in that interval. It is
not global nonoccurrence and grants no retry or refund authority.

## Executed distinctions

The valid run passed all 89 assertions.

| Case | Result | Ledger effect |
| --- | --- | --- |
| Alpha positive receipt | ResolutionApplied | one completed terminal |
| Exact Alpha replay | ReplayRefused | terminal bytes unchanged |
| Gamma complete finite no-effect receipt | ResolutionApplied | one scoped cancelled terminal |
| Exact Gamma replay | ReplayRefused | terminal bytes unchanged |
| Incomplete parent witness | UnknownConsumptionState | pending bytes unchanged |
| Alpha receipt against another Gamma attempt | InvalidContext | pending bytes unchanged |
| Exit after durable Delta replacement | process exit 24 | completed terminal remains |
| Delta retry after missing stdout | ReplayRefused | terminal bytes unchanged |
| Contradictory Epsilon receipts in two processes | one ResolutionApplied, one ConflictRefused | exactly one terminal |

Gamma, Delta and Epsilon are new-instance reuse. The Epsilon winner is
deliberately not fixed: either exact receipt may acquire the lock first. The
invariant is that only one becomes terminal and the other is refused.

Every returned application receipt records zero target processes and keeps
effect, retry, refund, native and free authority false. The application performs
only the declared ledger transition; it does not execute the target effect.

## Cost and retained correction

The [valid execution](../../experiments/recovery_receipt_application/evidence/attempt-1/execution.json)
uses six parent receiver processes and ten application processes. It reports:

- 89 assertions;
- 9,898 counted work units on receipted application paths;
- 0.5348037689982448 seconds of tool-process wall time;
- 0.5396292110017384 seconds for the whole supervisor interval;
- maximum child and supervisor RSS of 11,904 KiB each;
- zero target processes and zero search candidates.

The application process intentionally terminated after Delta's durable
replacement and before stdout. Its structural work is unmeasured rather than
zero.

The [first failed attempt](../../experiments/recovery_receipt_application/evidence/prior-implementation-failure.json)
is retained. A doubled backslash made the Python end anchor a literal
backslash-Z, so the first valid 64-hex pair digest was rejected. Six parent
receiver processes and one application process had started; the ledger stayed
byte-identical and no target started. The wrapper took about 0.203 seconds.
The one permitted correction replay changed only that anchor and then produced
the valid run.

Construction, serialization and publication time were not separately measured.
RSS figures are category maxima, not a concurrent total.

## Meaning and residual

No new word is justified. Existing terms for pending state, verified witness,
invalid context, conflict and replay are sufficient. ResolutionApplied is a
local receipt outcome, not a promoted native operation.

This helps Mingli and subsequent agents avoid applying the same recovery
receipt twice, silently choosing between contradictory receipts, or turning
bounded no-effect evidence into retry permission. Its value for Jiamin's
actual task remains unmeasured.

The experiment does not prove survival across power loss, disk failure or a
malicious process; authenticate the witness source; prove physical channel
exclusivity; or establish distributed exactly-once execution. It establishes
neither Research 0090 coverage, Research 0092 promotion, native free or Close,
M6 closure, hypothesized arithmetic truth nor arithmetic universality.

The next minimum step is a read-only independent terminal receiver. It should
recompute the source pending digest and recovery receipt digest from archived
bytes, verify either terminal without opening the mutable lock file, and return
UnknownResolutionState on any missing or divergent projection.

Authored by Codex (OpenAI), contributed under Unknown v0.3 through Mingli
Yuan's authorized GitHub account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee.
