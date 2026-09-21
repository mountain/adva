# Independent receiving of a pinned commit-state snapshot

Date: 2026-09-20. Status: bounded external experiment and revision of one
Proposed word; not native admission.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
not his review, endorsement or correctness guarantee. Original code, prose,
terminology and synthetic evidence are contributed under Unknown v0.3. No
external content is incorporated.

## Dependency and frozen question

Current main was `22c500263db4a261a3a4ed20d9e0941c374475a1`; there were no open
pull requests at freeze. PR 199 had merged the first three-outcome
`commit-state-reconcile` experiment. The later iota/grid work does not alter
the ledger relation.

The new question is deliberately narrower than storage recovery: **can a
versioned receipt preserve the three commit-state outcomes so a separate
process can check them without opening SQLite?** The exact objects, types,
quantifiers, grammar, acceptance criteria and limits were frozen in
`experiments/commit_snapshot_receipt/contract.json` before execution.

The campaign allows 30 seconds, 20 child processes, three seconds per child,
128 MiB child address space, 10,000 work units per call and 100,000 total.
There is no search. One implementation correction replay was available but
was not used. Research 0123's arithmetic-universality and hypothesized-
arithmetic-truth remain proposals. This experiment supplies neither Research
0090 coverage nor permission for Research 0092 vocabulary lifting.

## Revised Proposed word

`commit-state-reconcile` remains **Proposed** and advances from v0 to v1.
No second synonym is introduced. Version 1 admits a snapshot profile:

1. `snapshot.py` opens the selected SQLite ledger read-only and invokes the
   existing full ledger validator.
2. It emits canonical JSON binding the expected request, complete candidate,
   checker fingerprints, allowance, source-ledger digest, state and optional
   transition/result. An internal digest covers the body.
3. The receiver separately supplies a SHA-256 pin for the complete snapshot
   bytes.
4. `receive.py` checks only the snapshot. Its source has no `sqlite3` import and
   it is never given a ledger path.

The receiver still emits exactly:

- `StoredCommitted` for a pinned, valid, exact committed transition;
- `ProvenUncommittedLedger` for a pinned, valid empty selected ledger snapshot;
- `UnknownCommitState` for every other observed condition.

The byte pin matters. An internal digest traveling only with mutable content
cannot prevent an editor from changing both the content and digest. Even the
external pin is only an integrity coordinate unless its delivery is separately
authenticated.

## Executed finite result

The first actual campaign passed **130 supervisor assertions** in exactly
**20 child processes**. It used two different exact-rational decision families;
the reuse changes prior, kernel, loss and cost.

| Receiver cases | Expected | Observed |
|---|---:|---:|
| Exact pinned empty snapshots | 2 ProvenUncommittedLedger | 2 |
| Exact pinned committed snapshots | 2 StoredCommitted | 2 |
| Changed candidate or expected history | 2 UnknownCommitState | 2 |
| Old pin after byte change | 1 UnknownCommitState | 1 |
| Malformed or wrong-profile snapshot with its own pin | 2 UnknownCommitState | 2 |
| Missing snapshot | 1 UnknownCommitState | 1 |

Both committed cases recover the exact stored result and allowance `(3,3,0)`.
Both empty cases retain `(3,2,1)`. All ten receiving calls report
`sqlite_opened=false`, `parent_checked=false`, `debit_delta=0` and
`retry_authorized=false`. The four builders leave each source ledger byte
digest unchanged. The supervisor also parses the receiver source and confirms
that it does not import `sqlite3`.

This establishes a finite handoff relation, not an independent proof of the
original arithmetic. The snapshot builder remains inside the trusted base.

## Cost and replay

The campaign used **3,848 counted work units**, zero search candidates and no
corrective replay. Wall time was **3.156611950 seconds**; summed child lifetime
was 2.884440923 seconds. Snapshot construction took 0.643450541 seconds and
independent receipt verification 1.254102556 seconds. Serialization measured
0.131188187 seconds; small in-process fixture construction measured
0.000074143 seconds.

Highest child RSS was **13,824 KiB (13.50 MiB)** and supervisor RSS was
**16,000 KiB (15.625 MiB)**. These are category maxima, not aggregate memory.
Research, reading, word formation and publication time were not measured.
Packing and byte verification took **0.193423691 seconds** outside campaign
time. The archive contains **93 files** and 1,864,818 expanded bytes, with
SHA-256 `9b4592ab66f598f7b10a6f3fb0e98f03ffaf69a2c5d8c906600be69bb7819d5a`.

Replay into a fresh output directory:

```sh
timeout 35s python3 -B -S experiments/commit_snapshot_receipt/run.py \
  --output /tmp/adva-commit-snapshot-new
```

`evidence/execution.json` is the compact result; the adjacent manifest hashes
all archived request, snapshot, response, ledger and command bytes. Archive
verification checks serialization, not semantics or provenance.

## Boundary, usefulness and next minimum

The builder shares Python, SQLite and the inherited validator with the writer.
A malicious or defective builder can emit a self-consistent false snapshot.
There is no signature, hostile-replacement defense, actual mid-COMMIT or power
loss, external action, distributed exactly-once guarantee or durable hardware
model. The result changes neither additive-zero nor multiplicative-unit domains
and grants no native communicate/accept/free/Close/Seal, M6 closure,
universality, learning, acceleration or social trust.

It helps Mingli and later agents hand a finite commit-state observation to a
process that does not share SQLite access, while preserving enough context to
refuse a switched question. Benefit for Jiamin's real task remains unmeasured.

The next minimum is not cryptography. It is an **independent snapshot builder
cross-check** over the same fixed ledger bytes: a second implementation should
derive the canonical body and compare it byte-for-byte before either snapshot
is used. Disagreement must remain `UnknownCommitState`; agreement would reduce
one implementation-coupling residual without authenticating the channel.
