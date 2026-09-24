# Yi, Taixuan and Weishi mathematical intake

The Rust documentary receiver accepted eight original mathematical materials
from Adva source commit `fabfdb2554599d97daf0c3b0a587e47f1ac2498d`. The source packet collects **72 scoped
mathematical statements**, **49 source references** and **16 correction records**.
The post-arrival external checker reproduced 44 selected statements in eleven
sections with 47,187 counted finite cases; its output is byte-identical to the
source evidence. The other 28 statements retain their existing bounded evidence.
All 127 tests across the nine existing experiment modules passed.

Authored and reviewed by Codex (OpenAI), under Unknown v0.3 through Mingli Yuan
as authorized account proxy. Account use is not his authorship, review,
endorsement or a correctness guarantee.

## Read the mathematics

- [Finite-observer explanation and material guide](../../packages/yi-taixuan-weishi-v1/materials/README.md).
- [Statement inventory](../../packages/yi-taixuan-weishi-v1/materials/claims.json).
- [Proof presentations](../../packages/yi-taixuan-weishi-v1/materials/proofs.md).
- [Corrections and observation-only reports](../../packages/yi-taixuan-weishi-v1/materials/corrections.json).
- [Fixed sources and prior evidence](../../packages/yi-taixuan-weishi-v1/materials/sources.json).

The bounded source audit covers the result families in those records, not all
classical literature. Raw texts, modern transcriptions, external implementations
and doctrinal claims have not been copied into this packet. The original packet
has one canonical home; the received directory is a reference copy, not a new
entry in the pinned mathematical library catalog.

## Executed receiving boundary

| Event | Result | New acceptance effects |
| --- | --- | --- |
| send-1 | Sent | No receiver acceptance inferred |
| receive-1 | AcceptedDocumentary | 1 |
| replay-1 | AlreadyAccepted | 0 |
| ack-1 | Acknowledged | 0 |

The [native receipt](../../received/yi-taixuan-weishi-2026-09-24-v2/receipt.json),
[contract](contract.json), [finite plan](run-plan.json),
[observations](transport-result.json), and [acknowledgment](sender-acknowledgment.json)
retain distinct events. All material bytes were written by Rust receive.
SHA-256 was independently recomputed against every received file.
The source-tree preflight additionally checked each source against the committed
Git tree; this is an operator obligation beyond the native profile's integrity
check of supplied source coordinates.

The [post-arrival result](post-arrival-evidence.json) is an external exact check,
separate from the receipt's `semantic_verification: NotRun` and
`native_admission: NotGranted`. No native proof object, SourceId, observer, Seal
or stable API has been created. The open Pascal growth obligation, library
catalog and consumer dependency lock retain their previous state.

## Reproduce with the pinned dependencies

Use source commit `fabfdb2554599d97daf0c3b0a587e47f1ac2498d` and machine commit
`df8b29ae58262e738ee03600965658c07a59d02a`. Build the machine with
`cargo build --locked --release -p adva-witness --bin adva`.
Verify the source tree and the byte pins in the contract and publication record
before dispatch. Follow the four commands in the machine's
[documentary profile](https://github.com/mountain/adva-machine/blob/df8b29ae58262e738ee03600965658c07a59d02a/spec/framework/documentary-exchange-v1.md),
using this contract, its BLAKE3 from `run-plan.json`, a new envelope path, a fresh
trusted receiving store and exactly its receiver/context strings. Stop on any
failure; no automatic retry is allowed. Source paths are relative to the pinned
Adva checkout. The catalog's `adva-library/` material prefix is a literal v1
profile convention, not an assertion that this is the actual library submodule.

After receive, run its `materials/check.py --expect SOURCE_EVIDENCE --output NEW_OUTPUT`
under the material's v3 finite contract, with `SOURCE_EVIDENCE` independently
obtained from that fixed source commit. Compare the new output bytes to the
pinned source evidence. The envelope is reconstructible; [its exact pins](envelope-pin.json)
are retained without a redundant encoded payload archive.

## Failures retained

The first intake, with exchange identifier ending in v1, is **not admitted for
use**. Its [failure record](failed-intake.json) retains native observations, the
post-check rejection and the wrong source-version claim. A missing local Git
author prevented the source commit, but the original supervisor still dispatched;
the native profile does not itself authenticate Git coordinates. A tuple/list
comparison after JSON decoding also caused a false mathematical mismatch.

The successor uses a new exchange identifier, checks committed source bytes
before sending and compares results in the JSON value domain. The complete
failed receiver directory and envelope remain in private forensic storage; that
archival move is not another receiving judgment. Earlier static-review and
build-environment issues are in [engineering-review.json](engineering-review.json).
The v3 mathematical contract and this transport plan account for predecessor
costs explicitly. No receipt or failure was overwritten to manufacture a pass.

The [integration record](validation.json) records tested scope and limitations.
It also corrects one plan label: `post_arrival` says v2, while the byte-pinned
material and executed mathematical contract were v3. The original plan is retained.
The original clone's all-local-history publication scan rejected legacy refs;
a fresh single-branch clone was used for publishing. No history was rewritten.
The source-stage check passed, and the final staged/history check must pass
before this commit is uploaded. This checks known withdrawn content, not all
possible copyright questions; the exact source and receiver publication reviews
are separate records.
