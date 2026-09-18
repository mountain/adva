# Tentative ledger writes do not survive holder exit

Date: 2026-09-18. Status: bounded external experiment, not native admission.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
not his review, endorsement or correctness guarantee. The original harness,
report and synthetic evidence are contributed under Unknown v0.3. No external
text, code, image or dataset is incorporated.

## Dependency and frozen question

Current main was `89cf06ef11f4808040440845fd5ce5bfa085eb95`. Draft PR 199 was
the only open PR. Its pre-write holder-exit result was merged locally with current
main before this experiment; neither result is in main. The new Pascal patch does
not change this storage obligation. Research 0123's arithmetic-universality and
hypothesized-arithmetic-truth remain proposals. This does not discharge Research
0090 coverage or authorize Research 0092 vocabulary lifting.

The old sequential ledger campaign had already injected exit after its two writes
and before COMMIT. PR 199 added contention around a pre-read/pre-write exit. The
remaining minimum was their intersection: **one live contender while an owned
holder has made both tentative application writes but has not called COMMIT**.

The contract in `experiments/ledger_postwrite_exit/contract.json` was written
before execution. It fixes two inherited exact-rational decision families and
four schedules: primary valid, asymmetric valid reuse, primary false arithmetic,
and asymmetric changed-history context. Candidate grammar, receiver chain,
history, fingerprints and allowance `(grant,spent,remaining)=(3,2,1)` are unchanged.
Search candidates are zero. No new semantic syntax is introduced.

## Method and result

A test-only wrapper pauses immediately before the unchanged receiver executes
`COMMIT`, after its `INSERT` and `UPDATE`. The holder reports directly from its own
open transaction. In every episode it sees one tentative slot and allowance
`(3,3,0)`. A second process attempts the identical valid candidate while the
holder is alive and returns pre-transaction `LedgerBusy`, SQLite primary code 5,
with no authoritative result, allowance, parent check or debit.

The supervisor sends no release byte. It SIGKILLs and reaps only the owned holder.
After each exit, the complete quiescent logical schema, metadata and transition
rows equal the pre-overlap observation: zero accepted slots and original allowance
`(3,2,1)`. Therefore these four tentative transactions roll back at process exit.
This is application-level logical equality on this SQLite configuration, not a
claim about journal bytes, storage hardware or power loss.

Exactly one retry follows:

| Episode | Holder's tentative state | Contender | Post-exit state | Retry | Final slots |
|---|---|---|---|---|---:|
| Symmetric valid | 1 slot, remaining 0 | LedgerBusy | exact pre-state | CommittedContinuation | 1 |
| Asymmetric valid | 1 slot, remaining 0 | LedgerBusy | exact pre-state | CommittedContinuation | 1 |
| False arithmetic | 1 slot, remaining 0 | LedgerBusy | exact pre-state | InvalidEvidence | 0 |
| Changed context | 1 slot, remaining 0 | LedgerBusy | exact pre-state | InvalidContext | 0 |

Both valid retries independently rerun parent arithmetic and commit exactly one
slot and one debit. The false arithmetic is checked then refused. The changed
context is refused before arithmetic. Both refusals leave the complete ledger
unchanged. Thus disappearance of the lock restores retry opportunity, not
acceptance, fresh fuel, a changed question or permission to trust tentative data.

## Cost and replay

One campaign passed **189 assertions** in **16 child invocations**, using **10,295
counted receiver units**, zero search candidates and no corrective replay.
Campaign wall time was **1.452229471 seconds**; episodes took 0.358309434,
0.361057409, 0.362724203 and 0.366853498 seconds. Serialization took
0.033594740 seconds and quiescent logical observations 0.004756953 seconds.
Child lifetimes sum to 2.060947926 seconds but overlap and must not be added to
wall time. Construction was not separately timed in this harness.

Highest child RSS was **13,824 KiB (13.5 MiB)** and supervisor RSS **14,824 KiB
(14.48 MiB)**. These are maxima, not aggregate concurrent memory. Receiver units
include holder work reported at the gate, not supervisor, OS or research work.
Packing and byte verification took **0.084315278 seconds**, outside campaign time.
Network, reading, writing and publication costs were not measured. No speedup is
claimed.

Replay from the repository root with fresh paths:

```sh
timeout 35s python3 -B -S experiments/ledger_postwrite_exit/run.py --output /tmp/adva-postwrite-exit-new
python3 -B -S experiments/ledger_holder_exit/pack.py /tmp/adva-postwrite-exit-new /tmp/adva-postwrite-exit-packed
```

`evidence/execution.json` is the compact execution record. The adjacent manifest
hashes all **96 files**; `attempt-1.tar.gz` retains exact inputs, outputs, commands,
events, snapshots and database files (1,173,952 expanded bytes). The packer reopens
the archive and checks every length and SHA-256. That validates serialization, not
the receiver independently.

## Vocabulary, usefulness and residual

**New vocabulary: zero.** Existing `LedgerBusy`, `InvalidEvidence`,
`InvalidContext` and `CommittedContinuation` already distinguish host contention,
mathematical refusal, context refusal and accepted continuation. The experiment
profile name is not a learned word. It helps Mingli and later agents avoid treating
tentative storage or lock release as semantic evidence. Benefit for Jiamin's real
task remains unmeasured.

Only the exact before-COMMIT boundary in four scheduled local rollback-journal
transactions is tested. Exit inside SQLite's COMMIT, power loss, disk-full or
corruption, hostile storage, WAL/network filesystems, fairness, external action
and distributed exactly-once remain open. No additive-zero or multiplicative-one
domain changes; no native `free`, `Close`, `Seal`, M6 filler, universal grammar,
learning, acceleration or social-trust result follows.

The next smallest step is not another kill position. It is a **reconciliation
receiver for an uncertain COMMIT outcome**: given the exact original request,
candidate and transition key, inspect the durable ledger and return either the
stored checked result, a proven uncommitted state, or `UnknownCommitState`—never
automatically resubmit. Its first finite test should use synthetic pre-state and
post-state fixtures; actual mid-COMMIT power loss remains outside scope.
