# Adoption of the formal communication vocabulary

Status: **adopted framework vocabulary**, 2026-09-16. English is primary.
Direction and adoption requested by Mingli Yuan. Authored by ChatGPT (OpenAI),
submitted through his authorized account proxy; account use is not technical
review or a correctness guarantee.

`communicate`, `send`, `receive`, `acknowledge` and `accept` are formal Adva
framework words. Their canonical specification is maintained in `adva-machine`.
The adoption establishes vocabulary and requirements; the general native
communication operation and its executable conformance profile remain
unimplemented.

## Fixed documentation dependency

| Item | Exact reference |
| --- | --- |
| Repository | `https://github.com/mountain/adva-machine` |
| Revision | `6c7f6515114e121cc2d4c0481bc416e81737a8c3` |
| Normative specification | [Communication v1](https://github.com/mountain/adva-machine/blob/6c7f6515114e121cc2d4c0481bc416e81737a8c3/spec/framework/communication-v1.md) |
| Specification SHA-256 | `53e10429b608b2e6a6b4ccbe2f007f201217e5f5180a4280941a054c193a7599` |
| Registry | [Framework vocabulary v1](https://github.com/mountain/adva-machine/blob/6c7f6515114e121cc2d4c0481bc416e81737a8c3/spec/framework/vocabulary-v1.json) |
| Registry SHA-256 | `2b63d0240207b53cb33b2dfd2800f10b48de2590e6763f9cfe348fbd6e58c66a` |
| Decision | [ADR 0047](https://github.com/mountain/adva-machine/blob/6c7f6515114e121cc2d4c0481bc416e81737a8c3/docs/adr/0047-formal-communication-vocabulary.md) |

These are documentation references, not an executable-machine upgrade or a
receipt of a knowledge-object exchange. The executable consumer continues to
use [its existing machine lock](../dependencies/adva-machine.lock.json): machine
`e62d88dcc83fc4967260866518029942b9631b71` with library
`73a6af4ac4ed8225366d3c16794e309cff15f51d`. Historical runs keep their original
contracts. The specification's registry records its own historical sources;
those research notes remain unchanged.

## Meaning for the knowledge repository

Communication connects declared interfaces under a receiving contract. The
presentation travels with its source, dependencies, assumptions, evidence and
unresolved obligations. Receiver observations determine which continuation is
permitted. A received or acknowledged message can still be refused for use;
an `Unknown` result can be successfully communicated without resolving its
underlying question.

The existing library catalog illustrates why these distinctions matter. At
library revision `73a6af4`, 32 entries have exactly one home each: seven in
arithmetic, eight in geometry and seventeen in logic. Cross-topic references
produce 37 memberships. The manifest refers to 108 distinct files, 43 of them
outside the library under the inherited parent layout. Preserving a filename
alone cannot preserve every receiving obligation of such an entry.

Future knowledge and library migrations must bind the original entry and its
dependencies, declare the target receiving interface and intended use, perform
the required checks, and retain the receiver outcome. Direct host copying,
moving, renaming or Git synchronization cannot replace that exchange. When a
required operation is absent, its declared profile must be implemented before
content is migrated. Ordinary specification and code authoring remain
engineering work, and must not be reported as a `communicate` execution.

Changing the owning topic is a separately justified catalog revision. The
framework adoption does not move an entry, create a derivation parent, alter
the pinned Pascal obligation or promote a proposed document to a theorem.
The [dependency continuity direction](KNOWLEDGE_MACHINE_BOUNDARY.md) remains
in force.

## Current implementation boundary

The [existing documentary receiver](../adva-library/symbol-surface/receipts/native-load-v0/README.md)
is a useful finite precursor: it checks a fixed reply against its handoff and
preserves the original obligations. It is not the new general operation.
Likewise, native graph import and persistence provide checks for their own
representations; they do not by themselves supply an exchange protocol.

The first [bounded Rust profile](https://github.com/mountain/adva-machine/blob/df8b29ae58262e738ee03600965658c07a59d02a/spec/framework/documentary-exchange-v1.md)
now implements that local receiving route. The [first executed exchange](../knowledge/exchanges/party-naming-layer-2026-09-16-v1/README.md)
receives the original naming entry for documentary reference. Its contract pins
this checker separately; it does not upgrade the executable consumer lock.
The source catalog home, unresolved native identity and human acceptance
obligations remain intact. General communication remains open.

## Scoped application of transport/communication v2

The [two-receiver iota experiment](../knowledge/exchanges/iota-process-knowledge-2026-09-17-v1/README.md)
applies the [fixed v2 distinction](https://github.com/mountain/adva-machine/blob/efa4031cd18b315b25179d1b4967ff6bdd5060a8/spec/framework/transport-communication-v2.md):
the existing Rust documentary crossing is transport, and the finite term/ledger
comparison supplies separately checked interpretation work. The native command
spelling and v1 receipts remain unchanged.

Both adva and adva-machine receive exactly the same eight iota materials under
different contracts and contexts. Each then reconstructs the declared cuts and
runs its own identity/discard/copy probes through the pinned external machine.
The executable consumer lock above is unchanged; this scoped trial binds its
machine separately. Counterexamples, missing-evidence outcomes and the source's
full-ancestry residual remain visible. One agent authored the adapters; repeated
runs do not imply independent participants or human agreement.

The source catalog belongs to adva-iota. Its `logic` home and the legacy
profile's `adva-library/` material prefix do not register a new global library
entry. Documentary acceptance, finite interpretation, object execution and
physical claims retain distinct judgments. General communication remains open.

## Adoption checks

The two documentation digests above were checked against the exact machine
commit. Forty-six local links across this adoption note, the repository README
and the dependency direction resolved. The catalog counts above were computed
from the pinned manifest. All 13 existing machine-dependency regression tests
passed. Executable locks, library contents and historical evidence were
unchanged; these are documentation/continuity checks, not an executed exchange.


## Clean-history reference resolution, 2026-09-16

The active documentation links above now use the published post-withdrawal
history. The normative specification and vocabulary registry have the same
SHA-256 values; their frozen content and embedded historical coordinates were
not rewritten. The [machine history map](https://github.com/mountain/adva-machine/blob/df8b29ae58262e738ee03600965658c07a59d02a/governance/withdrawals/history-map-2026-09-16.json)
and [library history map](https://github.com/mountain/adva-library/blob/c7b34d237dbb9f9675a5692af0bd8dcf44982139/governance/withdrawals/history-map-2026-09-16.json)
provide the explicit resolution route:

| Historical coordinate | Clean coordinate | Role |
| --- | --- | --- |
| `1277d46efdaa48d93fe950828d349d3bfcdc1a0a` | `6c7f6515114e121cc2d4c0481bc416e81737a8c3` | Vocabulary adoption |
| `0c1e972d6b2b955b0a5361f755cf2560ce44a248` | `ba192941ba86ae0d3942f582d22ddb0bc6c7c900` | Historical predecessor machine |
| `4a53db6493389e046bd7293be9e3ae335ea2e9c7` | `73a6af4ac4ed8225366d3c16794e309cff15f51d` | Historical/pinned library |

The current executable lock independently selects `e62d88d`; the new exchange
selects `df8b29a`. These distinct bindings are deliberate. The old local clones
were not merged into the cleaned main branches. The two documentation byte pins
were rechecked at `6c7f651`, the current catalog check passed, and all 13 existing
machine-dependency tests passed. These checks supplement the original adoption
checks above; actual reception has its own native receipt and observations.

## Iota interpretation frame continuation

The [frame reception](../knowledge/exchanges/iota-frame-knowledge-2026-09-17-v1/README.md)
uses the existing transport route for a successor package carrying iota, i as a
complex structure and e through exponential coefficients. The frame binds the
process, domain boundaries, metric, observer, clocks, resource account and
residuals. Twelve finite charts pass 4,062 assertions after arrival at each
receiver. The identical witness is produced by the same checker, not independent
verifiers. The previous iota packet remains a required exact dependency.

This is an actual finite interpretation comparison over rational matrices and
retained processes. Documentary reception still records native admission
NotGranted; the separate FrameCovarianceChecked result introduces no general
interpretation engine or stable Frame API. The executable consumer lock remains
unchanged. Exact profiles, archives, controls and reproduction are in the local
receiving record. Original addition: Codex (OpenAI), Unknown v0.3, through Mingli
Yuan's account proxy; not his review or endorsement.
