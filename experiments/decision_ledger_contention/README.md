# Bounded contention at a receiver-owned continuation ledger

The first frozen campaign passed: two overlapping submissions can preserve one
stored continuation and one abstract debit in the declared schedules. A contender
that fails to acquire its transaction returns `LedgerBusy`, separately from
invalid database contents. This is a finite local experiment, not a proof over
all concurrent executions or an exactly-once guarantee for external actions.

Author: ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy. This
identifies authorship and account authorization; it does not imply his review,
endorsement, or a correctness guarantee. The adapter, scheduling harness,
synthetic inputs, report, and generated evidence are original work under
Unknown v0.3. No external source text or software is incorporated here.

## Frozen question and receiving boundary

The base is `f8341c815dc43e70fecb1749701141a72669d610`, which contains the
previous sequential ledger experiment. [contract.json](contract.json) was
saved before this campaign ran. The new profile is
`adva.research.decision-ledger-contention.v0`.

For one receiver-owned SQLite file, one fixed checkpoint question, one accepted
slot, and two trusted local processes, can overlapping submissions preserve the
existing arithmetic and allowance checks while distinguishing lock contention
from invalid storage? Each episode allows one explicitly scheduled contender
retry after the holder has terminated. There is no receiver retry loop, allowance
renewal, question substitution, ledger migration, or external task execution.

The input contract reuses the previous exact rational checkpoint profile:

- `expected` contains `prefix_request`, `pending_step`, and `allowance`.
- The candidate envelope contains exactly `profile`, `transition_key`, and
  `checkpoint_receipt`. A key is a string of 1 through 80 characters.
- The checkpoint retains the full two-step prefix, endpoint, pending third
  step, and allowance. Its ancestors use the same finite state, observation,
  action, rational, history, and scaling bounds as the existing receivers.
- Every episode starts with allowance `{grant: 3, spent: 2, remaining: 1}`.
  A successful commit stores the result and changes it to
  `{grant: 3, spent: 3, remaining: 0}` in one transaction.
- Exact canonical candidate equality at an occupied key permits replay of the
  stored result without another debit. A changed payload at that key gives
  `Conflict`; a different key gives `PausedLedgerCapacity`.

The old ledger receiver and all five arithmetic ancestors are unchanged. The new
adapter stores its own SHA-256 together with those six receiver hashes. Thus a
database binds seven receiver sources, the full expected question, the schema,
the initial allowance, and the new profile. The test-only gate is recorded in
the campaign source hashes but is not a new arithmetic rule. Both directional
old/new profile controls refuse access with `InvalidLedger`; neither silently
relabels or migrates the other profile's database.

`receive.py` retains the old JSON reply fields and adds `sqlite_diagnostic`.
That diagnostic records the exact SQLite code and name, its primary code,
the statement, and the connection's transaction flag. Classification uses
numbers rather than matching an English error message:

| Observed storage condition | Result in the new profile |
| --- | --- |
| Primary code 5 with `in_transaction` exactly false | `LedgerBusy` |
| Primary code 11 or 26 | `InvalidLedger` |
| Other codes, or BUSY during a transaction | `UnknownStorage` |
| Existing uncertain-COMMIT or cleanup boundary | Existing conservative reconciliation result takes precedence |

The primary code is the low byte of an extended SQLite result code. SQLite
distinguishes BUSY (5), LOCKED (6), CORRUPT (11), and NOTADB (26); LOCKED is not
automatically assigned the BUSY retry rule. These are documented SQLite
categories, not new arithmetic judgments. See the
[SQLite result-code reference](https://www.sqlite.org/rescode.html).

If connection creation itself fails, the adapter has no transaction flag and
does not infer that a transaction was absent. Execution and deferred row-fetch
errors are classified; uncertain commit and cleanup handling remain in the old
engine. The experiment uses the inherited DELETE journal, FULL synchronization,
and `BEGIN IMMEDIATE` transaction configuration. The
[SQLite transaction documentation](https://www.sqlite.org/lang_transaction.html)
explains the transaction boundary used by the test.

`LedgerBusy` is deliberately narrow. It reports that this invocation did not
obtain its transaction under the declared local condition. It does **not** say
that the candidate is valid, that the expected question matches the ledger,
that another process has not committed, or that the caller may renew its budget.
All eight new-profile contenders returned no authoritative allowance or stored
result, `parent_checked: false`, `debit_delta: 0`, and primary code 5 before a
transaction. The full ledger is observed separately after the processes stop.

## Controlled overlap and evidence

Each episode initializes a fresh file and saves its full logical pre-state. A
holder process then signals a pipe only after `BEGIN IMMEDIATE` succeeds, before
reading ledger metadata or validating its candidate. The supervisor records that
holder's PID and checks it is alive. It starts the contender while the holder
waits on a second pipe, waits for the contender's refusal, again checks the holder
is alive, and only then releases the holder. This establishes overlap by an
explicit handshake rather than a sleep assumption.

The holder's gate wait remains inside its receiver deadline. No database
snapshot is read during that overlap. After the holder exits, the supervisor
reads the entire schema, metadata row, and transition rows, performs one fresh
contender retry, and takes another complete snapshot. It compares the full stored
candidate and result, unchanged context/profile/checkers/schema, and exact final
allowance. This checks the local database effect as well as the returned debit.

| New-profile episode | Holder after release | Contender after its one retry |
| --- | --- | --- |
| Primary: same candidate, canonical JSON equivalence | `CommittedContinuation` | `ReplayedContinuation` |
| Primary: same key, changed payload | `CommittedContinuation` | `Conflict` |
| Primary: alpha key then beta key | `CommittedContinuation` | `PausedLedgerCapacity` |
| Primary: beta key then alpha key | `CommittedContinuation` | `PausedLedgerCapacity` |
| Primary: invalid holder, valid contender | `InvalidEvidence` | `CommittedContinuation` |
| Asymmetric reuse: same candidate | `CommittedContinuation` | `ReplayedContinuation` |
| Asymmetric reuse: same key, changed payload | `CommittedContinuation` | `Conflict` |
| Asymmetric reuse: reversed key order | `CommittedContinuation` | `PausedLedgerCapacity` |

Before release, every contender in this table returned `LedgerBusy`. The
conflict fixture changes the pending task while retaining the envelope shape;
it is **not** described as a second arithmetically valid answer to the same fixed
question. The invalid-holder fixture instead changes the claimed net value to
`[7, 1]`; independent arithmetic checking returns `InvalidEvidence` with reason
`net_value:mismatch`. Its post-holder database equals its entire pre-state, and
the valid retry then makes the first commit. Thus holding the lock does not
establish that its holder deserves the accepted slot.

The asymmetric family provides three new-instance reuses of the same adapter
and schedule. In the same-candidate episodes, the retry changes JSON key order
while retaining canonical equality. The stored result is replayed with all
history intact and no additional arithmetic check or debit.

A ninth scheduled episode uses the unchanged old-profile receiver. Its contender
returns `InvalidLedger` with `database is locked`; after release, the holder
commits and its retry replays. This is an observed classification boundary outside
the old experiment's stated **sequential** scope. The old evidence and source are
preserved, not reinterpreted as a failed claim about concurrency.

Three further controls complete the campaign:

1. Original non-SQLite bytes produce `InvalidLedger` with primary 26,
   `SQLITE_NOTADB`, at `PRAGMA journal_mode=DELETE`; the raw bytes are unchanged.
2. The new receiver refuses the completed old-profile ledger, preserving its
   full logical state.
3. The old receiver refuses a completed new-profile ledger, likewise preserving
   its full logical state.

Every one of the nine scheduled SQLite ledgers ends with one transition and
exactly one allowance debit. These observations cover the selected schedules,
not every possible scheduler interleaving.

## Recorded costs and replay

The first campaign completed without an implementation correction or second
campaign replay. It launched **39 child processes**, passed **500 assertions**,
and counted **15,831 receiver work units**. Search candidates: **0**. Eight
new-profile episodes and one legacy episode use four processes each; the three
remaining controls use one each.

| Measurement | Observed value |
| --- | ---: |
| Supervisor campaign wall time | 9.873473221 seconds |
| Fixture construction | 0.084074539 seconds |
| Full-state observation | 0.110929136 seconds |
| Instrumented JSON serialization | 0.349267394 seconds |
| Subsequent archive construction and verification | 0.294163127 seconds |
| Sum of child lifetimes | 11.848214437 seconds |
| Largest child RSS | 13,824 KiB = 13.5 MiB |
| Supervisor peak RSS | 16,256 KiB = 15.875 MiB |

Child lifetimes overlap and therefore must not be added to the campaign wall
time. Arithmetic checking, lock waiting, and process launch costs are not
separately isolated by this measurement. Per-process times and work appear in
`execution.json`; reuse is recorded there by case, without claiming an independently
isolated reuse speedup. The RSS values are Linux `ru_maxrss` observations, not a
measurement of simultaneous aggregate memory. File size is not used as a memory
estimate. Archive work was measured after the campaign and is not included in
its wall time. Research, review, and network publication were not separately
timed. No acceleration claim follows from this run.

The frozen ceilings were 30 seconds for the campaign, 40 child launches, two
overlapping children, three seconds per child wall/CPU, 128 MiB address space per
child, 10,000 work units per receiver invocation, 1 MiB per database, 196,608
candidate wire bytes, a 1.5-second readiness wait, and a 4,096-byte gate message.
The busy timeout is 0.1 seconds. Pipe cleanup terminates and reaps outstanding
processes on failure. The recorded environment is Python 3.12.14 and SQLite
3.53.1; other environments can have different timing and must retain the same
declared bounds or report a bounded failure.

Run from the repository root, using a new output path:

```bash
python3 -B -S experiments/decision_ledger_contention/run.py --output /tmp/adva-contention-replay
```

The dedicated CI job adds a 35-second outer command timeout and a five-minute
job limit. It uploads whatever evidence was produced, including on failure.

Saved evidence is [execution.json](evidence/execution.json),
[manifest.json](evidence/manifest.json), and the complete
[attempt-1.tar.gz archive](evidence/attempt-1.tar.gz). The archive retains exact
expected inputs, candidates, commands, standard output/error, ordered pipe/PID
events, before/after full logical snapshots, final closed SQLite files, and source
hashes. Extract it into a fresh directory to inspect the individual cases;
re-execution uses the command above rather than archived absolute scratch paths.
The archive has 225 members and 176,429 bytes; its SHA-256 is
`fa5d0625d49f2079f6fd0295a33359095232e2c4f46192cf7fba37e3dd43ca8a`.

## Remaining obligation and usefulness

No new native vocabulary is introduced. `LedgerBusy` is a proposed result of
this external receiving profile, not a native language operation or a learned
theorem. Exact finite arithmetic continues to be checked by unchanged receivers;
this work adds a bounded storage-classification and scheduling witness. It
does not grant `Close`, `free`, M6 closure, or arithmetic universality, and does
not change additive-zero or multiplicative-one definitions.

The result helps Mingli and subsequent people or agents distinguish a temporarily
unavailable ledger from invalid contents and reconcile a retry against actual
stored history. It also demonstrates that lock acquisition alone does not imply
candidate validity. Its effect on Jiamin's real decision tasks is unmeasured.

The next smallest experiment is a separately frozen holder-exit case **after
the readiness signal but before gate release**: inspect the stopped holder's
ledger, then allow one bounded contender retry under the same question and
allowance. That case was not run here. Arbitrary interleavings, scheduler
fairness, starvation, power loss, general COMMIT/I/O faults, hostile storage,
authentication, and distributed or external exactly-once effects remain outside
the present witness.
