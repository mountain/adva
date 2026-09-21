# Two-builder agreement on a commit-state projection

Date: 2026-09-21. Status: bounded external experiment and revision of one
Proposed word; not native admission.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
not his review, endorsement or correctness guarantee. Original code, prose,
terminology and synthetic evidence are contributed under Unknown v0.3. No
external content is incorporated.

## Dependency and corrected question

Current main was `c09351ef76484ad2045fe76ae4eb7a219114b196`; draft PR 203 was the
only open pull request. Main's six relation-query planning documents do not
alter ledger or snapshot semantics. This experiment continues PR 203 rather
than opening a duplicate dependency chain.

The previous next step asked two builders to derive the complete snapshot body
byte-for-byte. That condition was wrong: the body deliberately includes
`builder_source_sha256`, and genuinely different implementations should retain
different provenance. Erasing that difference to force equality would weaken
the receipt.

The corrected frozen question is: **can two implementation-distinct builders
derive the same ledger projection while retaining different builder provenance,
so a receiver that opens neither ledger proceeds only on both conditions?**
The projection is every snapshot-body field except `builder_source_sha256`.
The contract fixes the objects, types, quantifiers, grammar, acceptance and
limits before execution.

The campaign allows 30 seconds, 24 child processes, three seconds per child,
128 MiB child address space, 10,000 work units per call and 100,000 total.
There is no search. One correction replay was available but not used. Research
0123 remains conjectural; this does not discharge Research 0090 coverage or
unlock Research 0092 vocabulary lifting.

## Implementations and receiver

The inherited builder uses the previous adapter and ledger validator. The new
builder does not import them. It independently:

- checks the exact two-table SQLite schema and absence of extra objects;
- parses every stored JSON value canonically;
- recomputes the frozen checker fingerprints;
- checks expected-request, allowance, transition, result and checkpoint
  bindings;
- emits the same snapshot profile with its own source fingerprint.

Both still use Python and SQLite. This is implementation separation, not a
different language, storage engine or trust domain.

`receive_pair.py` imports no SQLite module and accepts no ledger path. It checks
both receiver-selected byte pins, both internal body digests and both complete
snapshot structures. It then requires:

1. unequal nonempty builder-source maps; and
2. byte-identical canonical projections after removing only those maps.

Only then does it return the existing `StoredCommitted` or
`ProvenUncommittedLedger`; otherwise it returns `UnknownCommitState`.

## Executed result

The first campaign passed **171 supervisor assertions** in exactly **24 child
processes**. It used symmetric and asymmetric exact-rational families; the
second changes prior, observation kernel, loss and cost.

| Pair-receiver cases | Expected | Observed |
|---|---:|---:|
| Distinct builders, exact empty projection | 2 ProvenUncommittedLedger | 2 |
| Distinct builders, exact committed projection | 2 StoredCommitted | 2 |
| Projection disagreement or identical builder provenance | 2 UnknownCommitState | 2 |
| Changed candidate or expected history | 2 UnknownCommitState | 2 |
| Wrong right pin or missing right snapshot | 2 UnknownCommitState | 2 |

All four valid pairs have byte-identical projections and different source maps.
Both committed pairs recover the exact stored result and allowance `(3,3,0)`;
both empty pairs retain `(3,2,1)`. All ten pair calls report
`sqlite_opened=false`, `parent_checked=false`, `debit_delta=0` and
`retry_authorized=false`. All eight builder invocations leave their source
ledger bytes unchanged.

The disagreement control changes the right source-ledger digest and recomputes
the snapshot's own body digest and file pin. Thus it is internally consistent
but disagrees with the other builder and is refused. The copied-builder control
uses one valid inherited snapshot twice; equal output without distinct provenance
is also refused. This adds an expressible two-builder relation, not measured
solver acceleration or a proof that either implementation is correct.

## Cost and replay

The campaign used **4,176 counted work units**, zero search candidates and no
corrective replay. Wall time was **1.217350423 seconds**; summed child lifetime
was 1.112694104 seconds. Inherited construction took 0.181261728 seconds,
independent construction 0.155914837 seconds and pair reception 0.436612295
seconds. Serialization took 0.052495871 seconds; fixture construction measured
0.000065870 seconds.

Highest child RSS was **13,696 KiB (13.375 MiB)** and supervisor RSS was
**16,380 KiB (15.996 MiB)**. These are category maxima, not aggregate memory.
Research, reading, word formation and publication time were not measured.
Packing and byte verification took **0.141257083 seconds** outside campaign
time. The archive contains **111 files** and 2,280,045 expanded bytes, with
SHA-256 `f453b565f232dcac480afc8ab156e32e7683f4dff30667079c949d95b01d900e`.

Replay into a fresh output directory:

```sh
timeout 35s python3 -B -S experiments/commit_snapshot_crosscheck/run.py \
  --output /tmp/adva-commit-snapshot-crosscheck-new
```

`evidence/execution.json` is the compact result. The adjacent manifest hashes
all archived requests, snapshots, responses, ledgers and commands. Archive
verification establishes byte preservation only.

## Boundary, usefulness and next minimum

Agreement cannot exclude a common conceptual or Python/SQLite defect. Neither
byte pins nor builder agreement authenticate origin. There is no signature,
power-loss model, hostile replacement defense, external action or distributed
exactly-once guarantee. This changes neither additive-zero nor
multiplicative-unit domains and grants no native communicate/accept/free/Close/
Seal, M6 closure, universality, learning, acceleration or social trust.

It helps Mingli and later agents distinguish a corroborated finite projection
from a single implementation's self-consistent story, while preserving the
implementations' actual provenance. Benefit for Jiamin's real task remains
unmeasured.

The next minimum should test a **frozen cross-language reader** over the archived
snapshot bytes, without creating or modifying ledgers. Its only task is to
recompute canonical projection bytes and the three-way result. This would probe
shared Python assumptions while keeping storage and retry outside scope.
