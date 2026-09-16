# First documentary library exchange

On 2026-09-16, the Rust `adva communicate` profile received the three original
materials of `logic-party-naming-layer` into the knowledge reference store.
The [native receipt](../../received/party-naming-layer-2026-09-16-v1/receipt.json)
records `AcceptedDocumentary`. The sender subsequently observed that exact
reply; its acknowledgment is retained in the library repository under
`exchanges/party-naming-layer-2026-09-16-v1/acknowledgment.json`.

Authored and reviewed by ChatGPT (OpenAI), contributed under Unknown v0.3
through Mingli Yuan's authorized account proxy; account use is not his review,
endorsement, authorship or correctness guarantee. English is primary.

## Fixed bindings

| Item | Reference |
| --- | --- |
| Source library | `c7b34d237dbb9f9675a5692af0bd8dcf44982139` |
| Rust machine | `df8b29ae58262e738ee03600965658c07a59d02a` |
| Operational profile | [documentary-library-entry-v1](https://github.com/mountain/adva-machine/blob/df8b29ae58262e738ee03600965658c07a59d02a/spec/framework/documentary-exchange-v1.md) |
| Receiving contract | [contract.json](contract.json), BLAKE3 `d56b733921712b3ed0482acd6652d0efbfe0f0358daf69d0bd8099c9003ad5d9` |
| Publication review | [completed admission record](../../../governance/publication/records/party-naming-layer-2026-09-16-v1.json) |
| Finite invocation plan | [run-plan.json](run-plan.json) |
| Executed result and byte pins | [result.json](result.json) |

The contract pins the source catalog and its complete selected entry, every
material, the publication review, checker source and Cargo.lock. The run result
also identifies the release binary's SHA-256. These pins establish integrity
relative to the selected inputs; endpoint authentication and legal judgment
remain outside the machine check. The existing research execution dependency
lock continues to select its earlier machine/library pair.

## Observations

| Attempt | Observed result | Acceptance effect | Bytes read |
| --- | --- | --- | --- |
| [send-1](observations/send-1.json) | `Sent`; receiver observation `Unknown` | None claimed | 111,094 |
| [receive-1](observations/receive-1.json) | `AcceptedDocumentary` | One reception | 74,891 |
| [replay-1](observations/replay-1.json) | `AlreadyAccepted` | Zero new receptions | 74,891 |
| [ack-1](observations/ack-1.json) | `Acknowledged` | Zero new receptions | 60,844 |

All four invocations exited 0, reading 321,720 bytes in total with no automatic
retry. Each invocation had an 8 MiB read budget, five-second cooperative
deadline and a separate 30-second supervisor timeout. The plan allowed only
these four invocations. The supervisor recorded stdout and compared received
SHA-256 values; all payload writing and receipt/acknowledgment creation occurred
inside the Rust protocol commands.

The three material files total 14,047 bytes and match both the reviewed source
SHA-256 values and source bytes. The original library files, manifest and
single `logic` home remain intact. The receiver's complete entry retains the
unresolved native three-machine identification and human acceptance obligations.
The Pascal sources and other catalog entries named in the documents are
source-relative documentary references, not recursively imported materials.

Before this exchange, the read-only catalog check returned `CatalogConsistent`
and naming check `MatchedDeclaredKeys`. The machine's pinned submodule is
`73a6af4`; its selected entry, manifest and three source files match the
standalone cleaned library `c7b34d2`. `adva-machine doctor` reported `Ready`
with all 14 specification and 11 library pins matched. The implementation had
15 passing communication tests, five existing library CLI tests, 36 toolchain
tests and a passing targeted clippy check. This repository's 13 dependency tests
also passed. The full historical research suites were not rerun for this change.

## Reproduction boundary

Use clean checkouts of the fixed machine and source revisions above. Build
with `cargo build --locked --release -p adva-witness --bin adva`. Obtain this
contract and review record from the receiver independently; verify the printed
contract pin before dispatch. The profile's command forms document all options.
Use a fresh temporary envelope path, an empty local store representing
`knowledge/received`, the exact receiver/context strings in the contract, and
distinct attempt coordinates. Run the four steps in the declared plan; stop
on failure, retain its observations and do not automatically clear a pending
directory or reset a budget.

The original transport envelope remains outside repository directories. Its
exact digest is retained and `send` deterministically reconstructs its bytes
from the fixed source, checker and contract. The received materials retain the
original nested `names/` paths beneath `materials/`. Do not substitute a host
copy of those files for the receiver, or treat a newly copied receipt as a
new receiving decision.

The source acknowledgment records the reply actually observed at that time;
it does not establish future storage availability. No source retirement, new
catalog home, native admission, proof discharge or human acceptance occurred.
General communication and migrations needing other receiving profiles remain
open. Broader reorganization can now proceed entry by entry after its additional
requirements are implemented and checked.
