# Holder exit releases a lock, not a semantic obligation

Date: 2026-09-17. Status: bounded external experiment, not native admission.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy.
The proxy is not his review, endorsement or correctness guarantee. This original
report, harness and synthetic generated evidence are contributed under Unknown
v0.3. No external publication, software source, image or dataset is imported.

## Dependency and question formation

The frozen main is `b9d54665881ffa6877075e980f381db36a1aeaf4`.
At initial inspection there were no open PRs. Previous nightly continuation,
ledger and contention experiments are already merged; they are not rerun here.
Read Research 0123 with the agenda, claims registry, publication boundary and
current communication framework: arithmetic-universality and hypothesized-
arithmetic-truth remain research positions, not consequences of this experiment.

This follows the explicitly open next step in
`experiments/decision_ledger_contention/README.md`: an actual holder exit after
transaction readiness but before gate release, followed by one bounded retry.
It supports the conditional continuation concern of Research 0122; it does not
satisfy Research 0090's general coverage obligation or unlock 0092 vocabulary
lifting. The merged iota/i/exponential frame does not discharge storage duties.

The exact question is: **does the disappearance of contention preserve the
original question and resources while leaving arithmetic checking compulsory?**
This is narrower than general crash recovery. The inherited receiver, producer,
gate and arithmetic ancestors are not modified. The claims registry's old
contention result remains historically scoped; this report is a separately
bounded follow-up, not a rewrite of its original coverage.

## Frozen contract

See `experiments/ledger_holder_exit/contract.json`, written before execution.
Types are strict JSON records, exact rational pairs and bounded integer quotas;
the original grant/spent/remaining is `(3,2,1)`. Histories, source interpretation,
receiver fingerprints, ordered scale operations and candidate syntax remain
fixed. There is one trusted local SQLite database and at most one accepted slot
per episode. Python, Fraction, SQLite and the existing receiver remain trusted.

Exactly four schedules are tested, not all schedules:

1. Original symmetric instance, valid retry.
2. Asymmetric new-instance reuse, valid retry.
3. Original instance, a false claimed net value `[7,1]` on retry.
4. Asymmetric instance, receiver history changed to `substituted-origin` on retry.

The asymmetric producer changes the prior, observation kernel, loss and cost,
not merely a fixture name. The raw expected requests retain every exact value.
The two negative retries deliberately violate the frozen question or arithmetic;
their expected outcome is refusal, not successful continuation.

The supervisor starts a holder and waits for its pipe readiness record after
`BEGIN IMMEDIATE`, before metadata reads or candidate checking/writes. A live
contender must return pre-transaction `LedgerBusy` (SQLite primary code 5).
Only the owned holder is then killed with SIGKILL and reaped. No release byte is
sent. Full logical schema and rows are observed before the sole explicit retry.
Thus this experiment kills a process, not an arithmetic proof or a remote worker.

The campaign is bounded by 30 seconds, outer limit 35 seconds, 16 children,
at most two overlapping children, 3 seconds per child, 10,000 receiver units per
call and 100,000 total. Child address space is limited to 128 MiB and regular
files to 2 MiB. Readiness has a 1.5-second bound. Search candidates: zero.

## Executed result

The first campaign passed **223 assertions**, with **16 child invocations** and
**5,007 counted receiver units**. No implementation correction or corrective
replay was needed.

| Episode | Contender while holder lives | After holder exit | Sole retry | Final accepted slots |
|---|---|---|---|---:|
| Symmetric valid | LedgerBusy | Exact original logical state | CommittedContinuation | 1 |
| Asymmetric reuse valid | LedgerBusy | Exact original logical state | CommittedContinuation | 1 |
| False arithmetic | LedgerBusy | Exact original logical state | InvalidEvidence | 0 |
| Changed context | LedgerBusy | Exact original logical state | InvalidContext | 0 |

All four holders actually exited with `-SIGKILL`, produced no receiver reply,
and remained live until the injection. All four `LedgerBusy` results have no
authoritative allowance or accepted result and perform no parent checking.
All four post-exit logical snapshots equal their pre-state. This is logical
application-state equality, not equality of all filesystem or journal bytes.

The successful retries independently check the arithmetic, preserve the entire
request binding and commit exactly one full candidate/result pair and one debit:
`(3,2,1) -> (3,3,0)`. The false arithmetic is checked and refused; changed context
is refused before arithmetic. Neither refusal mutates the ledger. Acquiring a
new transaction cannot silently reset quota, replace history or validate a false
claim. A missing reply from the killed process is not a mathematical negative.

## Reproduction and evidence

From the repository root on a compatible POSIX/Python/SQLite environment:

```sh
timeout 35s python3 -B -S experiments/ledger_holder_exit/run.py --output /tmp/adva-holder-exit-new
python3 -B -S experiments/ledger_holder_exit/pack.py /tmp/adva-holder-exit-new /tmp/adva-holder-exit-packed
```

Choose fresh output directories: existing paths are refused. There is no need
to run any older full experiment campaign. The report is `execution.json`;
raw inputs, outputs, commands, SQL observations and final databases are in
`experiments/ledger_holder_exit/evidence/attempt-1.tar.gz`. The adjacent manifest
hashes every archived file. The packer reopens the archive and checks each file's
length and SHA-256; this is serialization verification, not an independent
mathematical implementation or another execution campaign. The execution record
also fingerprints the imported receiver chain and this harness.

## Measured costs and limitations

One campaign: **4.267344887 seconds**. Primary valid episode:
1.092227225 seconds; asymmetric valid reuse: 1.041804593 seconds. Negative
episodes: 1.093676818 and 1.025570734 seconds. Included phase measurements:
construction 0.023227610 seconds, serialization 0.140974562 seconds and full-state
observation 0.060535435 seconds. Child lifetimes sum to 5.337456710 seconds but
overlap; they must not be added to wall time. Receiver-only verification time is
not separately measured from subprocess execution and scheduling.

Highest child peak RSS: **13,824 KiB (13.5 MiB)**; supervisor peak RSS:
**14,592 KiB (14.25 MiB)**. Neither is aggregate concurrent memory. File size is
not used as a memory proxy. Receiver units include partial holder work reported
at readiness, but not supervisor/OS work. Final execution-report serialization,
archive checking and publication are outside the campaign wall measurement;
the packer records its own elapsed time. Research, reading, writing, network
cost and exact attribution/word-formation labor are not separately measured.
This is not a speedup comparison. There is no new word-formation claim.

## Boundary, usefulness and next minimum

**New vocabulary: zero.** Existing `LedgerBusy`, `InvalidEvidence`,
`InvalidContext` and `CommittedContinuation` suffice. The new harness name is
an experiment identifier, not a learned operation or theorem. The witness
helps Mingli and later agents resume a finite decision check without confusing
host progress with permission to change its question. Real benefit for Jiamin's
tasks has not been measured.

Only one pre-read/pre-write exit point in four schedules is covered. It does
not prove arbitrary crash safety, power-loss durability, fairness, hostile
storage resilience, distributed exactly-once behavior or external action
atomicity. Previous sequential post-write tests cannot be silently promoted to
overlapping post-write coverage. The arithmetic receiver is unchanged; additive
zero and multiplicative one domains are neither generalized nor newly tested.
No native free/Close/Seal, M6 filler, universal grammar, acceleration, learning
or social trust is granted.

The next smallest step is a separately frozen gate **after the pending row and
debit writes but before COMMIT**, then the same four explicit schedules. That
would test rollback under contention at one additional point; it must not be
called power-loss testing. Do not enlarge to distributed recovery or renew fuel.
