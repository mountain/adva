# Replay-obligation frontier (2026-11-20)

## Frozen problem

Given the pinned historical native success connected on 2026-11-19, which changes in the current dependency snapshot require a replay? The output must distinguish dependency continuity from current native acceptance.

The objects, types, quantifier, arithmetic domain, candidate grammars, criteria and budget were frozen in [`contract.json`](contract.json) before execution. One route and ten fixed cases were used; no search was performed.

## Dependency and status reading

The latest `main` remained `8fc38427f2a479b4e8e84802e1873cff14d54566`. The open pull requests remained draft PR #234 at head `2f10293aad82a302c8db83e7f5a138b22fb54010` and draft PR #232 at head `f2406dae6851ba4c0727176d0028394a6f97a8a8`.

The source status partition is unchanged:

- merged finite evidence: PR #231's exact accepted-fixture successor workflow;
- unmerged proposals: the request/custody/receipt/join records on draft PR #234;
- proved mathematics added by this line: none;
- open targets: Research 0090 coverage, Research 0092 promotion, semantic `ResearchCertificate` acceptance, current native execution, arithmetic universality, hypothesized arithmetic truth and M6 filling.

Research 0090 still requires complete coverage before exact closure. Research 0092 explicitly may not skip that dependency. Research 0123 retains `arithmetic-universality` and `hypothesized-arithmetic-truth` as externally proposed words, not theorems.

## Pinned comparison

The historical record is [`historical-evidence.json`](historical-evidence.json); the current record is [`current-snapshot.json`](current-snapshot.json).

The historical workflow ran at commit `0d17fa7c7bab22a07c5ea1b919532ec32c034e46`; current `main` is a different commit. Nevertheless, all eleven declared dependency coordinates agree:

- fixture path, git blob, byte count and SHA-256;
- consumer path, git blob and SHA-256;
- consumer byte budget `65536` and structural work budget `512`;
- workflow path and git blob.

In particular, the fixture blob remains `c36ccf64108cce740f36a2c2d56765dacbe9318f`, the consumer blob remains `c7683e2eae755eb6e7d77672e166fc6dd22928d5`, and the workflow blob remains `dc85a0610283e532011683c70a567921dc2c2fb3`.

This comparison deliberately serializes only public artifact coordinates. Reasons or private narratives for earlier isolation are not inputs to the public evidence record.

## Result

Status: **`PassedBoundedReplayObligationFrontier`**.

For current `main` the explicit result is:

```text
ContinuityChecked/HistoricalEvidenceReusable
frontier=[]
current_acceptance=NotEstablished
```

An unrelated commit change therefore does not by itself force a replay. A fixture, consumer, workflow, byte-budget or work-budget change does. A missing current snapshot remains `CertificateObstruction/MissingCurrentSnapshot`; a failed historical record is refused.

The historical-success-only projection coalesced seven cases that the explicit frontier distinguishes. This is a finite comparison over the ten cases, not a general expressivity theorem.

A fresh synthetic dependency family reused the rule: identical dependencies at a different commit gave an empty frontier; simultaneous consumer and workflow drift produced the ordered frontier `consumer.git_blob_sha1, workflow.git_blob_sha1`.

## Proposed word

**replay-obligation frontier** (`Proposed`)

- Role: name the exact finite dependency coordinates that must be revalidated or replayed before historical acceptance can inform a changed current snapshot.
- Input: pinned historical native evidence and a current fixture/consumer/workflow/budget snapshot.
- Output: `ContinuityChecked/HistoricalEvidenceReusable` with an empty frontier, `ReplayRequired/DependencyDrift` with an ordered frontier, or a refusal/obstruction.
- Applicability: the historical acceptance is valid and both records declare the same repository and dependency family.
- Witness: eight canonical controls, one fresh exact reuse and one fresh two-coordinate drift reuse.
- Refusal: invalid historical workflow/case/outcome, repository mismatch or missing current snapshot.
- Expansion: verify historical success, compare the eleven coordinates in order, retain every difference, and keep current acceptance `NotEstablished`.
- Counterexample: current commit differs from the historical run commit while all eleven dependency pins agree; using commit inequality alone as a replay trigger is overbroad.
- Replay: `timeout 30s python3 run.py`.
- Residual: an empty frontier proves only dependency-pin continuity. It does not prove current execution, environment continuity, semantic acceptance, social trust, 0090 coverage, 0092 promotion, arithmetic universality or M6 filling.

## Same-budget grammar comparison

- Historical-success-only form: 88 bytes; formation 42,860 ns.
- Explicit frontier form: 1,013 bytes; formation 44,308 ns.
- Formation cost: 925 additional bytes and 1,448 additional ns in this run.
- Finite benefit: seven previously coalesced cases become distinguishable.

No global efficiency or expressive-power claim follows.

## Replay and cost

```bash
cd experiments/native_input_binding_serialized_leaf_request/replay-obligation-frontier-20261120
timeout 30s python3 run.py
sha256sum outcome.json
```

Observed output:

```text
{"baseline_bytes": 88, "cases": 10, "checks": {"all_expected": true, "canonical_commit_changed_but_frontier_empty": true, "false_coalescences_under_historical_only": 7, "never_current_acceptance": true}, "explicit_bytes": 1013, "ru_maxrss_kib": 10112, "serialized_bytes": 6555, "sha256": "c2b29e292d6df6276e3f2ff1995ce972822410e0d6915544863f45396efacd09", "status": "PassedBoundedReplayObligationFrontier"}
```

- Routes: 1.
- Fixed cases: 10.
- Search candidates/nodes: 0.
- Construction: 845,351 ns.
- Evaluation and verification: 239,146 ns.
- Serialization: 188,444 ns.
- Final outcome: 6,555 bytes, SHA-256 `c2b29e292d6df6276e3f2ff1995ce972822410e0d6915544863f45396efacd09`.
- Peak `ru_maxrss`: 10,112 KiB.
- Native executions: 0.
- Implementation correction replays: 0.
- Independent process-tree wall and memory measurements were not available; file size is not used as a peak-memory proxy.

The machine-readable result is [`outcome.json`](outcome.json).

## Claim boundary and next step

This is finite evidence plumbing. Additive-zero and multiplicative-unit normalization are untouched and their domains and histories remain separate. Local image equality does not produce an M6 filler.

The minimum continuation is to add one environment/toolchain coordinate only if a downstream consumer actually needs a stronger reuse policy. Otherwise the empty dependency frontier should remain a historical-context result, not trigger another native rerun or a claim of current acceptance.

### Historical source verification

The evidence `commit` is the [PR head recorded by Actions](https://github.com/mountain/adva/commit/0d17fa7c7bab22a07c5ea1b919532ec32c034e46). The [successful job](https://github.com/mountain/adva/actions/runs/41854211677/job/126658300901) checked out the [test merge commit](https://github.com/mountain/adva/commit/d80a7d46f06cd1ab1c4ec791f9424b6a83b126bc). The fixture, consumer and workflow blobs match at both commits. The November 2 source record documents an earlier run. Job 126658300901 is the source for the matching native result recorded here.
