# Cumulative reservation through a correction

Status: **bounded synthetic experiment passed; real receiver integration open**.
Parent draft PR #204: `ca7be68fd5caba3f68582a6bb7f774c5e7e943ce`.
Main checked at start: `79f6353511d736ae743b109f1c573b652eff170a`.
The main agenda, AGENTS instructions, claims and Research 0123 were rechecked.
PR #203 is merged; #204 is the only open PR found. The earlier
`InvalidBudgetEvidence` remains invalid and is not reclassified by this work.

## Frozen question and dependency

The immediate blocker is the supervisor's reset of cumulative work on a
correction replay. This is upstream of relying on any bounded search or
receiving claim. We use synthetic children to check that boundary before
rerunning the real Node receiver. Research 0123's arithmetic-universality and
hypothesized-arithmetic-truth remain proposals. This local resource result does
not discharge Research 0090 coverage or authorize Research 0092 promotion.

The [frozen contract](../../experiments/cumulative_budget_supervisor/contract.json)
selects eight scenarios, positive integer reservations and an ordered journal.
It permits at most twenty controlled launch attempts and 400 reserved fixture
units across any correction replay, 0.5 seconds per child, thirty seconds per
trial invocation, at most one implementation correction, 32 journal events,
32 KiB per journal and 1 MiB retained output. The trial-level allowance is a
separate file retained across invocations. No search or full Node campaign is
performed. Fixture output is tiny and trusted; this is not a hostile service.

## Minimal arithmetic invariant

For a fixed work allowance W and call allowance K, let

    R = sum of all admitted reservation amounts
    C = number of admitted reservations

The supervisor checks `R+r <= W` and `C+1 <= K` before recording a reservation
and attempting a launch. The reservation is recorded before the subprocess
call. It is retained after success, spawn failure, nonzero exit, malformed
receipt, or timeout. There is no refund transition. Settlement and correction
do not change R or C. Therefore, by induction over admitted events, R and C
never exceed their original allowances. This is an elementary invariant of
the declared transition rules, not a machine-checked proof of Python or the OS.

Reported successful work is a separate observation. A child claiming more than
its reservation yields `BudgetViolation` and permanently blocks this task's
continuation. Unknown work retains the whole reservation. A recorded launch
without settlement yields `UnknownAttemptState`; reconstruction does not make
it safe to rerun. The journal is canonical JSON, bound to an exact task
contract; exclusive creation refuses accidental initialization over it.

An outer trial account charges before each controlled launch attempt, including
failed spawn and independent inspection. Its accounting is conservative: a
charge preceding a subsequently refused task reservation would also remain.
The prototype requires a single sequential writer and intact local files;
deletion, hostile replacement, concurrent writers and interrupted writes are
outside its guarantee.

## Observed checks

All 65 assertions passed on the first trial, with no implementation correction.

| Scenario | Retained observation |
| --- | --- |
| Success, exit failure, correction, reconstruction, reuse | Reservations `[3,3,3]` exhaust cap 9; reported successful work totals only 3. Correction preserves the first 6 units. A fourth reservation is refused. |
| Failed executable start | Reservation 4 remains against cap 5. Correcting the executable cannot admit a reservation of 2. |
| Version-like probe | A zero-work receipt still consumes its one reserved unit and the last call slot. |
| Malformed receipt, correction, overreported work | Both reservations remain; the report of 5 against reservation 4 yields terminal `BudgetViolation`. |
| Unsettled reservation on reload | The retained reservation remains charged; new launches are blocked by `UnknownAttemptState`. |
| Binding/type controls | Existing-file reinitialization, changed task, Boolean/zero/negative reservation and a fabricated refund event are refused without changing journal bytes. |
| Timeout and new-instance reuse | Timeout retains reservation 2; after one recorded correction, a terminating fixture consumes the remaining reservation 2. |
| Fresh interpreter inspection | A separate Python process reconstructs exactly the same final state, without changing the journal. Its own launch is charged. |

An independent audit sums reservation events without using the supervisor's
fold function. It checks every admitted reservation prefix and final totals.
The source, inputs, final journals, failure outputs and audit are archived.
The refused controls check byte preservation; the audit is not authentication.

For comparison, a finite arithmetic control reproduces the previous reset
pattern: 6 units before reset plus 6 admitted after reset totals 12 against the
same original cap of 9. The new scheme admits only 3 more and refuses further
reservation. This is a small counterfactual accounting comparison, not an
executed old-receiver benchmark or measured speedup.

## Costs and reproduction

The executed trial charged ten controlled launch attempts and 27 fixture units
against its cumulative caps of twenty and 400. Nine were fixture start attempts,
including one failed executable start; one was fresh-process inspection. Thus
nine child processes actually started. The driver itself is a separate measured
supervisor process. The unfinished-reservation scenario constructs a journal
event without starting a child, and is not reported as an actual controller
crash test.

- Total trial: 0.271394263 seconds; 65 assertions; zero searches or corrections.
- Construction of task journals: 0.000691213 seconds.
- Verification phase: 0.241083535 seconds, including construction and child time.
- Fresh-process inspection: 0.029298952 seconds.
- Instrumented serialization subtotal: 0.001674604 seconds; incomplete because
  reconstructed objects' earlier timings are not aggregated. It must not be
  treated as total serialization cost.
- Maximum child RSS: 11,776 KiB; supervisor RSS: 11,776 KiB. These are maxima,
  not concurrent total memory. No physical-memory cap is claimed.
- Packing and per-file byte verification: 0.007751737 seconds.
- Archive: seventeen files, 34,313 expanded bytes; SHA-256
  `63773f9fc14458cf0f3b7623486e5b8ab18dec043b080e982e1cf9dc9e16147c`.

Reading, coding and publication time are not separately measured. Fixture-unit
accounting does not price all Python validation, I/O or physical instructions.
Work is self-reported by trusted fixtures; a malicious process can exceed an
abstract reservation before being caught. The subprocess timeout is a separate
bound and the prototype does not monitor arbitrary process trees.

From the repository root, a new finite trial can be reproduced with:

```sh
timeout 30s python3 experiments/cumulative_budget_supervisor/run.py \
  --output /tmp/adva-cumulative-attempt-1 \
  --trial-account /tmp/adva-cumulative-trial.json
```

If making the one permitted correction, retain the **same** trial-account path
and use a new output directory. Do not delete or recreate the account to bypass
its allowance. No correction was needed in the recorded trial.

See [execution](../../experiments/cumulative_budget_supervisor/evidence/execution.json)
and [manifest](../../experiments/cumulative_budget_supervisor/evidence/manifest.json).
The receiving runtime and the previous frozen artifacts are unchanged.

## Reuse and remaining boundary

No new terminology is justified. Existing correction, continuation, failure,
Unknown and resource-contract distinctions suffice. The prototype gives Mingli
and subsequent agents a concrete way to prevent correction from automatically
granting more task resources. The timeout/reuse instance checks that the rule
is not specific to a normal exit failure. Jiamin's practical benefit remains
unmeasured.

The next smallest step is to connect this reservation interface to one empty
and one committed Node receiving invocation under a new fixed contract, with
the receiver's maximum abstract work bound reserved in advance. The previous
Node counter can report cap+1 on exhaustion, so that possible stopping tick
must also be reserved or the checker must use a separately versioned
pre-increment guard. Do not silently equate this prototype with a hard CPU fuel
meter or claim that the entire fourteen-case campaign is now resource-valid.

Power-loss recovery, concurrent/distributed exactly-once execution, hostile
journal replacement, independent mathematical verification of child answers,
native Adva fuel/free/Seal, M6 closure and universality remain open. Additive
zero and multiplicative unit retain their separate typed domains, including
nonzero conditions and ordered histories; reservation arithmetic introduces
no new identification of semantic objects.

Original code, fixtures and analysis by Codex (OpenAI), contributed under
Unknown v0.3 through Mingli Yuan's authorized account proxy. Account use is not
his review, endorsement or correctness guarantee. No external source content
was incorporated.
