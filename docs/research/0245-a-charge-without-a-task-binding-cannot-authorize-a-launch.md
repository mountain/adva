# Research 0245: A charge without a task binding cannot authorize a launch

Status: **bounded negative result on the current v0 account schema**. This note
adds no native operation, theorem beyond the declared finite representation, or
vocabulary word.

## Question and dependency boundary

Research 0233 connected cumulative pre-spawn reservation to two real Node
receipts. Its remaining narrow interruption window was:

1. the cumulative trial account has durably recorded a charge;
2. the task journal has not yet recorded the corresponding reservation;
3. the process stops.

The question is not whether a host transaction could be added. It is whether
the already published `cumulative-trial-v0` representation contains enough
information to decide which task owns the retained charge and safely authorize
a launch after that interruption.

The [frozen contract](../../experiments/cumulative_charge_gap/contract.json)
fixes five project-original finite cases, five receiver processes, zero target
processes, 2,560 receiver work units, ten outer seconds and 131,072 retained
output bytes. The receiver is read-only. It may compare counts and arithmetic
totals, but it may not repair a journal, refund a charge, launch a task or grant
retry. All inputs are canonical bounded JSON. No external material is used.

This is downstream of resource continuity and `UnknownAttemptState`, not a new
step toward arithmetic universality. Research 0090 coverage, Research 0092
promotion, additive zero, multiplicative unit and ordered M6 histories are not
changed.

## The representation obstruction

The v0 trial account contains only this information:

```json
{"charges":[7],"profile":"cumulative-trial-v0"}
```

It contains no charge identifier, task coordinate, purpose or task-contract
digest. Consequently the same seven-unit charge can be paired by a totals-only
rule with both of these distinct claims:

- task alpha reserves seven units for `launch-alpha`;
- task beta reserves seven units for `launch-beta`.

Both comparisons satisfy

\[
\sum \text{trial charges}=\sum \text{task reservations}=7,
\]

yet one retained charge cannot establish that it belongs to both tasks. Total
equality is therefore not the missing relation. This is an indistinguishability
result about the declared bytes: a receiver cannot recover a task coordinate
that the charge record never carried.

The safe receiver returns `UnknownAttemptState` for both equal-total claims and
authorizes neither. It does the same in the actual gap, where a charge exists
and the journal is empty, and in the opposite mismatch, where a task reservation
exists without a trial charge. These outcomes preserve uncertainty; they are
not semantic counterexamples and not permissions.

## Executed result

The [retained execution](../../experiments/cumulative_charge_gap/evidence/attempt-1/execution.json)
passed 52 assertions over five independent receiver processes:

| Case | Charged | Reserved | Totals equal | Result |
| --- | ---: | ---: | --- | --- |
| gap alpha | 7 | 0 | no | `UnknownAttemptState` |
| gap beta, reuse instance | 11 | 0 | no | `UnknownAttemptState` |
| equal alpha | 7 | 7 | yes | `UnknownAttemptState` |
| equal beta | 7 | 7 | yes | `UnknownAttemptState` |
| missing charge | 0 | 5 | no | `UnknownAttemptState` |

Every case preserved both input files byte-for-byte. Every receipt set launch,
retry and account-mutation authorization to false. Native authority and
`free` authorization remained false. The deliberately unsafe totals-only
predicate authorized both equal-total task claims; the retained safe predicate
authorized neither. No target process started.

The beta gap is a new amount and task instance, so the refusal is not tied to
the seven-unit example. It does not show that every future account format must
refuse. It shows only that the present v0 bytes cannot justify a unique binding.

## Cost and replay

The retained run used five receiver processes, 188 counted receiver work units,
zero search candidates, zero target processes and no correction replay. Total
wall time was 0.141276141 seconds, of which the receiver processes used
0.138614054 seconds. Maximum child and supervisor RSS were each 11,648 KiB;
these are category maxima, not a concurrent-memory measurement. Reading,
implementation and publication time were not measured.

Replay from the repository root with a new output path:

```sh
python experiments/cumulative_charge_gap/run.py \
  --output /tmp/adva-cumulative-charge-gap
```

The [experiment directory](../../experiments/cumulative_charge_gap/) retains
the exact program, contract, five input pairs and five receipts. The test
`tests/python/test_cumulative_charge_gap.py` runs the same bounded construction
in a fresh temporary directory.

## Meaning and remaining obligation

No new word is necessary. Existing `UnknownAttemptState`, cumulative resource
accounting and explicit context binding already express the result. The reason
label `TrialChargeLacksTaskBinding` is a local diagnostic, not a promoted term.

This helps Mingli and subsequent agents avoid two unsafe reactions to an
interrupted reservation: silently refunding the retained charge or reusing it
to start whichever task happens to present an equal total. Its value for
Jiamin's actual task remains unmeasured.

The run assumes trusted local files and receiver code. It does not simulate
power loss, authenticate bytes, contain a malicious process, create an atomic
transaction, repair the gap or establish distributed exactly-once execution.
It does not prove native `free`, `Close`, M6 closure, hypothesized arithmetic
truth or arithmetic universality.

The next minimum step is representational: freeze a successor charge record
that binds a fresh `charge_id`, the exact task-contract digest, units and phase.
A read-only receiver should then accept one exact charge--reservation pair,
reject reuse of that charge by a second task, and still start no target process.

Authored by ChatGPT (OpenAI), contributed under Unknown v0.3 through Mingli
Yuan's authorized GitHub account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee.
