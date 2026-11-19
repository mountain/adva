# Historical acceptance join (2026-11-19)

## Frozen question

Can the bounded `reference-handoff receipt` recorded on 2026-11-18 be joined to an already completed Rust workflow without changing the conclusion from **historical acceptance at a pinned run** into **current acceptance**?

The frozen objects, types, quantifier, arithmetic domain, grammars, criteria, and budget are in [`contract.json`](contract.json). One route was used. No search was performed.

## Dependency and status boundary

The latest `main` inspected for this run was `8fc38427f2a479b4e8e84802e1873cff14d54566`.

- Merged finite evidence: PR #231's accepted-fixture successor gate. Its final head `0d17fa7ca8fa240c3c478840975f0b7a241170b7` has successful workflow run [41854211677](https://github.com/mountain/adva/actions/runs/41854211677), job `126658300901`. The job verified the exact fixture and consumer pins, compiled both stages, accepted the matching case, and reported `SuccessorVerified`. The source record remains `FiniteWorkflowGatePassed`, not a general theorem.
- Unmerged proposal: the 2026-11-18 `reference-handoff receipt` is on draft PR #234. It retrieved exact bytes but did not execute Rust locally.
- Proved mathematics: none added here.
- This record: one finite join experiment over ten fixed cases.
- Still open: 0090 coverage, 0092 promotion, current native execution, independent implementation, semantic `ResearchCertificate` acceptance, arithmetic universality, hypothesized-arithmetic-truth, and M6 filling.

The additive-zero and multiplicative-unit domains are not used or conflated by this experiment.

## Exact evidence coordinates

The left record is [`reference-receipt.json`](reference-receipt.json). The right record is [`native-evidence.json`](native-evidence.json).

- Fixture: 4,464 bytes, SHA-256 `d4d619a621ac7fd2943daa9c6eb0757acc79023314ecf9ed7dcf2f9cb0c84d4d`, git blob `c36ccf64108cce740f36a2c2d56765dacbe9318f`.
- Consumer: 4,836 bytes, SHA-256 `ee07ea03ba1d9f451186a5e8a5eb3356da11d20faaa09e113381f958cfd4e1d3`, git blob `c7683e2eae755eb6e7d77672e166fc6dd22928d5`.
- Consumer budgets: 65,536 input bytes and 512 structural items.
- Historical execution: run `41854211677`, job `126658300901`, conclusion `success`, matching case `AcceptedCurrentFixture`, native successor `SuccessorVerified`.

The native evidence contains a second copy of the pins checked by the workflow. This is necessary: the first implementation allowed its consumer digest field to be changed without invalidating the record. The single permitted correction replay added this internal consistency check.

## Result

`PassedBoundedHistoricalJoin`.

The exact pair produced:

`HistoricallyJoined/NativeAcceptedAtPinnedRun`

It did not produce `AcceptedNow`. The fixed controls refused a changed fixture digest, changed consumer pin, changed byte budget, failed workflow, changed case, and changed native outcome; a missing retrieval record remained a certificate obstruction.

The digest-only projection falsely coalesced six refused cases with the exact positive case. This is only a comparison within these ten cases, not a general expressivity or complexity theorem.

A fresh 51-byte synthetic pair reused the join successfully. Changing only its workflow conclusion to `failure` produced `Refused/WorkflowNotSuccessful` while its digest-only projection still said `Match`.

## Proposed word

**historical acceptance join** (`Proposed`)

- Role: join exact retrieval custody to a separately pinned successful native run without upgrading historical evidence to current acceptance.
- Input: reference receipt; fixture coordinates; independently verified consumer path, digest, byte/work budgets; workflow run/job; case; consumer and native outcomes.
- Output relation: `HistoricallyJoined/NativeAcceptedAtPinnedRun`, or a coordinate-specific refusal/obstruction.
- Applicability: the shared fixture coordinates agree and the native record is internally consistent with its verified pins and successful workflow coordinate.
- Witness: eight canonical fixed cases, one fresh positive reuse, and one fresh failed-run reuse.
- Refusal: any shared coordinate differs; retrieval is not exact; native pins are incomplete or inconsistent; workflow is not successful; case/outcome differs; or either evidence side is missing.
- Expansion/replay: compare the six shared coordinates, validate the native record's internal pins and budgets, validate the run/job and matching-case outcome, then emit only the pinned historical relation. Run `python3 run.py`.
- Counterexample: a byte-identical fixture paired with a failed workflow remains `DigestProjection/Match` but is `Refused/WorkflowNotSuccessful`.
- Residual: no current Rust execution, freshness theorem, independent machine, semantic certificate acceptance, 0090 coverage, 0092 promotion, arithmetic theorem, or M6 filler.

## Replay and measured cost

```bash
cd experiments/native_input_binding_serialized_leaf_request/historical-acceptance-join-20261119
timeout 30s python3 run.py
sha256sum outcome.json
```

Observed final replay:

```text
{"cases": 10, "checks": {"all_expected": true, "digest_projection_false_coalescences": 6, "never_current_acceptance": true}, "ru_maxrss_kib": 10112, "serialized_bytes": 4426, "sha256": "235085519a8d2e4b956ea435445eedec137c3d563d0cdf1a0b63f89722f1df21", "status": "PassedBoundedHistoricalJoin"}
```

- Routes: 1.
- Search candidates/nodes: 0.
- Fixed cases: 10.
- Construction: 162,690 ns.
- Evaluation and verification: 239,590 ns.
- Serialization: 181,880 ns.
- Serialized outcome: 4,426 bytes; SHA-256 `235085519a8d2e4b956ea435445eedec137c3d563d0cdf1a0b63f89722f1df21`.
- Measured process maximum RSS: 10,112 KiB.
- External command wall time including interpreter startup: approximately 0.5 s as reported by the execution harness.
- Native executions in this run: 0; the native execution is pinned historical evidence.
- Implementation correction replays: 1.
- `/usr/bin/time` was unavailable, so no independent process-tree memory measurement was obtained. File size is not used as a memory proxy.

The machine-readable result is [`outcome.json`](outcome.json).
