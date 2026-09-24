# Node receiver calibration and the cumulative replay boundary

Status: **finite semantic checks passed; overall InvalidBudgetEvidence**.
This continuation of PR #204 does not claim a resource-compliant campaign.
Base main: `79f6353511d736ae743b109f1c573b652eff170a`; parent PR commit:
`34e1c485d6639e3ca21b00e743c17f9a34631077`. Main and the open PR were checked
before this continuation. PR #203 is merged; #204 remains a draft.

## Question and correction of the premise

Can the same cross-language receiving checks complete with a budget derived
from their finite input size? The previous proposal to look for repeated
charging was a hypothesis. Inspection does not establish repeated parsing.
The archived committed request and two snapshots contain 14,161 JSON value
occurrences. The old 10,000-unit cap cannot finish even this parsing work.

The preflight independently compares three input measures. Counts are sums
over request, left snapshot and right snapshot; equal bytes in distinct roles
remain distinct inputs.

| Triple | Value nodes | Lexical tokens | 64-byte blocks | Bytes |
| --- | ---: | ---: | ---: | ---: |
| symmetric empty | 6,797 | 17,327 | 1,819 | 116,282 |
| symmetric committed | 14,161 | 35,987 | 2,661 | 170,244 |
| asymmetric empty | 6,797 | 17,327 | 1,832 | 117,155 |
| asymmetric committed | 14,161 | 35,987 | 2,688 | 171,951 |

These measures are not interchangeable units of computation. We retain the
old abstract rule (one unit per value-parser entry plus explicit check ticks)
and expose its partition. No semantic condition is removed. The new bound is
`ceil((14161 + 1024) / 1024) * 1024 = 15360` per call. The 1,024-unit reserve
is an explicit allocation, not an unrestricted complexity theorem. Its adequacy
is checked for the four valid instances. The frozen total is 215,040 units and
14 receiver calls, including any correction; the implementation failed to
preserve these totals across the replay, as detailed below.

## Why the input count is exact in this scope

A scalar contributes one value occurrence. An array/object contributes one
plus the sum of the occurrences of its elements/values. The parser calls
`value` exactly at those positions; an object key is not a value occurrence.
Induction on the finite parse tree gives the node count for successful parses.
The Node instrumentation is compared per input role against a separate Python
iterative tree walk. A separate Python lexical scanner checks Node's formula
`tokens = nodes + 2*keys + containers + commas`: one extra closing token per
container and one key/colon pair per object property.

Twelve complete role comparisons pass across the four valid cases. This does
not assert that each physical instruction is charged once. Canonicalization,
sorting, hash byte work, string scanning, I/O, reporting and supervision are
not fully priced by this abstract meter. The frozen byte, depth and wall-time
bounds remain essential. The Node old-space option is not a total RSS cap.

## Executed observations

The first attempt completed all four valid cases and six inherited refusals,
then failed while constructing the duplicate-key control. The inherited
supervisor expected compact JSON text but the archived request contains
whitespace. Its literal replacement marker did not exist. The sole correction
canonicalized only the generated control's base request before replacement;
archived baseline bytes and receiver predicates were unchanged. Both source
versions and both attempts are retained.

The second attempt passed all fourteen cases and 286 supervisory assertions:

- Two empty triples returned `ProvenUncommittedLedger`, at 6,841 units each
  (6,797 value nodes plus 44 check units).
- Two committed triples returned `StoredCommitted`, at 14,207 units each
  (14,161 value nodes plus 46 check units).
- Full semantic views matched the pinned Python records: outcomes, stored
  result, allowance, state, projection digest, builder provenance, and the
  no-authority fields.
- Six inherited controls rejected projection disagreement, same-builder
  provenance, candidate/expected-context changes, wrong pin and missing file.
- Four parser controls rejected duplicate keys, fractional spelling, an
  unsafe integer and a correctly repinned noncanonical snapshot.
- Every refusal matched a cause-specific reason. None passed merely by
  hitting the work cap. The asymmetric pair supplies new-instance reuse.

There is no arithmetic replay, SQLite access, allowance debit or retry grant
by the Node receiver. Matching archived results does not authenticate a
builder or prove the parent arithmetic. Rational encodings, nonzero and
invertibility conditions, ordered histories, additive-zero and multiplicative-unit
domains are not redefined by this receiving experiment.

## Invalid cumulative resource evidence

The runner reset its counters on restart. The first attempt spent 115,341
units in ten receiver calls; the replay spent 125,813 in fourteen. Their sum
is **241,154**, exceeding the frozen 215,040 by **26,114**. Twenty-four receiver
calls exceed fourteen. Two additional `node --version` probes were also not
included in that call counter; actual Node process starts total 26.

The per-attempt `Passed` output is retained verbatim, but the archive's root
`execution.json` supersedes it with **InvalidBudgetEvidence**. The permitted
single correction did not authorize resetting cumulative fuel. No further
receiver execution or budget revision was made after this was recognized.
No overall bounded-success claim follows from the finite semantic checks.

| Measured item | Value |
| --- | ---: |
| Static input preflight | 0.062156874 s |
| First attempt | 1.014893276 s; 242 assertions |
| Sole corrected replay | 1.170198232 s; 286 assertions |
| Attempts combined | 2.185091508 s; 528 assertions |
| Receiver work, both attempts | 241,154 units |
| Maximum child RSS | 50,076 KiB |
| Maximum supervisor RSS | 13,872 KiB |
| Archive packing and byte verification | 0.151624525 s |
| Retained archive | 148 files; 3,306,634 expanded bytes |
| Search candidates | 0 |

Archive SHA-256: `21ae58ad449e722dab118cfd22d773be26a1fe556b2ae412c0e59d2cb1a0af73`.
RSS figures are per-category maxima, not concurrent aggregate memory. Reading,
coding and publication time are not separately measured. Runtime phases are
retained in both attempt records; construction and semantic verification are
not separately timed. No acceleration or user-value measurement is claimed.

## Evidence, replay and next obligation

The [contract](../../experiments/commit_snapshot_node_receiver/calibrated/contract.json),
[input preflight](../../experiments/commit_snapshot_node_receiver/calibrated/preflight.json),
[cumulative audit](../../experiments/commit_snapshot_node_receiver/calibrated/evidence/execution.json)
and [manifest](../../experiments/commit_snapshot_node_receiver/calibrated/evidence/manifest.json)
retain exact source/input pins, requests, stdout, failure and both source versions.
The original #204 source and evidence are unchanged.

The archived runner is a diagnostic reproduction, not a safe cumulative
supervisor. Its single-attempt invocation is:

```sh
timeout 35s python3 experiments/commit_snapshot_node_receiver/calibrated/run.py \
  --output /tmp/adva-node-calibration-one-attempt
```

Do not repeatedly invoke it to obtain a compliant campaign. The next step is
an outer supervisor whose spent-work and started-process counters survive a
correction. Reserve resources before launch, charge failed starts and version
probes, and preserve unrun cases when the remainder is insufficient. Validate
that supervisor using tiny synthetic child receipts before another full run.

No new or revised vocabulary is needed. This helps Mingli and subsequent
agents distinguish an input-size obstruction, a semantic refusal and an
invalid resource audit. Benefit to Jiamin's real task is still unmeasured.
Authentication, hostile input hardening, power-loss recovery, distributed
consistency, native communication/free/Seal, M6 and arithmetic universality
remain outside this finite result. 0090 coverage and 0092 promotion obligations
are not discharged.

Original analysis and instrumentation: Codex (OpenAI), under Unknown v0.3,
through Mingli Yuan's authorized account proxy, not his review, endorsement or
correctness guarantee. Incorporated fixture bytes and inherited code are the
project-original parent experiments; no third-party material was added.
