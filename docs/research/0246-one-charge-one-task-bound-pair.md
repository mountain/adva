# Research 0246: One charge, one task, one bound pair

Status: **bounded positive relation check with a retained replay residual**.
This note adds no native operation, theorem beyond the declared finite
representation, or vocabulary word.

## Question and frozen boundary

Research 0245 showed that `cumulative-trial-v0` stores only charge amounts.
The same seven-unit charge therefore total-matched two distinct task journals,
and a safe receiver had to retain `UnknownAttemptState`. The next minimum
question was whether a successor representation could carry the missing
relation without granting a launch.

The [frozen contract](../../experiments/bound_charge_pair/contract.json) fixes
nine project-original cases, nine receiver processes, zero target processes,
8,192 counted receiver units, twelve outer seconds and 196,608 retained bytes.
The only proposed successor record is:

```text
charge = (charge_id, task_contract_sha256, units, phase=charged)
reservation = (charge_id, task_contract_sha256, units, phase=reserved)
```

The receiver recomputes `task_contract_sha256` from canonical task-contract
bytes. It requires unique identifiers inside each received finite object and
checks the directed phase pair. It is read-only. `BindingVerified` is a local
receipt outcome, not a promoted word, formal `accept`, launch authorization or
native judgment.

This is a resource-continuity experiment downstream of Research 0233 and 0245.
It does not change Research 0090 coverage, Research 0092 promotion, additive
zero, multiplicative unity, ordered M6 histories, hypothesized arithmetic truth
or arithmetic universality.

## Executed distinction

Three exact observations returned `BindingVerified`:

- task alpha, charge `charge-alpha-0001`, seven units;
- task gamma, a new task, identifier and eleven-unit amount;
- a read-only replay of the exact alpha bytes.

The replay produced the same semantic receipt. That is useful for independent
checking, but it also exposes the next residual: this stateless receiver cannot
tell a harmless recheck from a second consumption attempt. Because it starts no
target, no duplicate effect occurs in this experiment.

Six controls were refused:

| Control | Result | Exact reason |
| --- | --- | --- |
| beta reuses alpha identifier and seven units | `InvalidContext` | `AccountTaskMismatch` |
| beta lies with alpha's digest in its event | `InvalidContext` | `AccountTaskMismatch` |
| alpha reservation changes seven to six | `InvalidContext` | `ChargeUnitsMismatch` |
| account reverses `charged` to `reserved` | `InvalidEvidence` | `ChargePhase` |
| account repeats one charge identifier | `InvalidEvidence` | `DuplicateChargeId` |
| journal repeats one reservation identifier | `InvalidEvidence` | `DuplicateReservationChargeId` |

All eighteen input files remained byte-identical. Every receipt kept launch,
retry, account mutation, native and `free` authority false. No target process
started.

## Representation and verification cost

The comparison deliberately reuses the same two seven-unit tasks as Research
0245. The amount-only predicate still returns true twice. The v1 relation
verifies alpha and rejects beta because their canonical task-contract digests
differ.

This distinction is not free. The canonical alpha account-plus-journal grows
from 200 bytes in the v0 comparison representation to 523 bytes in v1, an
increase of 323 bytes. Six relation-field occurrences are stored: the charge
identifier, task digest and phase on both sides. No vocabulary word is formed.
One accepted alpha verification reports 583 structural work units.

The [retained run](../../experiments/bound_charge_pair/evidence/attempt-1/execution.json)
passed 83 assertions. Nine receiver processes took 0.2527573819970712 seconds;
the whole supervisor interval was 0.25707786599741667 seconds. Accepted paths
reported 1,752 structural work units in total. Rejected paths currently report
zero structural units after classification, so their validation cost is
represented by process wall time but is not separately metered; this is a
measurement residual, not zero work. Maximum child and supervisor RSS were each
11,776 KiB. There were zero search candidates and zero correction replays.
Reading, implementation and publication time were not measured.

Replay from the repository root with a new output path:

```sh
python experiments/bound_charge_pair/run.py \
  --output /tmp/adva-bound-charge-pair
```

## Meaning and remaining obligation

No new word is necessary. Existing context binding, `InvalidContext`,
`InvalidEvidence` and cumulative accounting express the result. The local
outcome `BindingVerified` states only that the two received records agree under
this frozen relation.

This helps Mingli and subsequent agents distinguish “the amounts agree” from
“this retained charge names this exact task”. It prevents a second, different
task from borrowing the first task's charge identifier under the checked
representation. Its value for Jiamin's actual task remains unmeasured.

The SHA-256 coordinate provides integrity within this trusted experiment, not
identity authentication, authorship or human-intent equivalence. Uniqueness is
local to the received finite account. The result assumes trusted files and
receiver code and supplies no power-loss recovery, hostile-process containment,
distributed transaction or exactly-once guarantee. Exact replay remains
observationally valid and no consumption state exists.

The next minimum step is therefore not another identity field. It is a finite,
durable consumption receipt that binds this verified pair and permits at most
one transition from `unconsumed` to `consumed`. A read-only recheck may reproduce
the judgment, but a second effect request must remain blocked; crash uncertainty
must return an unknown state rather than silently consume or refund again.

Authored by Codex (OpenAI), contributed under Unknown v0.3 through Mingli
Yuan's authorized GitHub account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee.
