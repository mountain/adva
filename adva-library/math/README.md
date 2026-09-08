# Math: a constrained documentary topic view

This directory implements Mingli Yuan's proposal to place **arithmetic,
geometry and logic** under `math/`. Logic's proposed **降位** is recorded as
an organizational change: inference systems can be research content with
assumptions and evidence. A directory does not implement semantic lowering,
change the rules checking that content, or settle a historical classification
of logic. See [ADR 0042](../../docs/adr/0042-math-topic-catalog-without-semantic-authority.md).

## Two independent coordinates

- **Topic**: arithmetic, geometry, logic. An entry may appear in several views.
- **Recorded evidence state**: hypothesis, proposed document, checked research
  snapshot, proposal journal, bounded evidence, external calibration, policy
  evidence or checking-boundary description.

Neither coordinate is a native type, semantic identity, permission to execute,
or a new knowledge epoch. Topics are not assigned to compute/verify/learn or
Rust/Lean/Metamath. The tree is not a theorem about knowledge-space topology.

`manifest.json` records each documentary entry once, including its theory and
version, assumptions, scope, material/evidence references, original checker
description, reuse requirements and unresolved obligations. Three
`<topic>/index.json` files contain keys into that manifest, partitioned into
`owned` and `references`. Every entry has one `home`; new keys require its
topic prefix. Shared topic membership never grants local ownership, imports
programs, identifies two programs or copies their evidence.

## Current contents

| Topic | Entries | Examples |
| --- | ---: | --- |
| arithmetic | 6 | epochs 0/1, recipes, three-verifier calibration, 100-round evidence, Pascal presentation, crypto calibration reference |
| geometry | 3 | Pascal root, external Q4/M6 reference, proposed Pascal incidence-task successor |
| logic | 5 | external calibration reference, fixed rules, organizational proposal, existing finite logic tasks, proposed cryptographic trust boundary |

There are **11 distinct entries**, not fourteen independent results. Counts describe
this catalog only, not an inventory of all project knowledge. In particular,
Pascal remains proposed; M6 retains its missing filler; logic has no newly
installed native calculus. The old `adva-library/index.json` remains its
original two-document catalog.

[Research 0155: 密码学封存、双语言校准与信任边界](../../docs/research/0155-cryptographic-sealing-and-calibration-boundary.md)
adds a proposed document about SHA-256/BLAKE3 digests, Ed25519 signatures,
AES-256-GCM/ChaCha20-Poly1305 interoperability, independent trust roots and
bounded external calibration. Its single home is logic; arithmetic only
references the finite-computation discussion. This is not a classification of
all cryptography as logic. It adds no geometry entry, proof, installed crypto
dependency, signed obligation or executable task. The proposal has no checker
or execution evidence and does not change the Open growth obligation.

[Research 0159: 目录分割工程合同](../../docs/research/0159-library-directory-partition-contract.md)
把 adva-library 的目录角色、跨目录规则、准入程序与修订纪律收拢为一份
proposed 合同（JSON 同目录），并登记为本目录学条目（logic，
`logic-directory-partition-contract`）。它不改变检查器、增长义务或任何
已 pin 字节；math-check 通过仍只允许浏览声明引用。

## Read-only check through the outer CLI

From the repository checkout, using Python's standard library on POSIX:

```sh
python3 python/adva/adva.py math-check
```

For an optional fresh report (the parent directory must already exist):

```sh
python3 python/adva/adva.py math-check --output target/math-catalog-check.json
```

`--root /path/to/adva` chooses another checkout. The catalog location within
that root is fixed; entries cannot replace its policy or choose another
directory as a logic authority. This command requires neither the PyO3
extension nor Rust builds, Lean, Metamath, network access or search.

The checker checks strict schemas, explicit fields, topic coverage and SHA256
reference integrity. It refuses duplicate keys, unsupported status/permission
fields, changed policy, noncanonical/escaping paths, symbolic links and
nonregular referenced files. It reads only the declared catalogs and
references; an unlisted file cannot register itself by sitting in a folder.
Evidence is hashed, **not parsed or verified**. Consistent pins are not
authentication, and recorded statuses and prose are not validated for truth.

| Report status | Meaning | CLI exit |
| --- | --- | ---: |
| `CatalogConsistent` | Documentary shape, membership and referenced bytes match | 0 |
| `InvalidCatalog` | A checked constraint or file read failed | 2 |
| `Unknown` | A declared resource bound prevented completion | 3 |

Every report has `native_admission: not-granted`, `proofs_rechecked: false`,
and `recorded_claims_authenticated: false`. Success permits only browsing
declared references. Real reuse still needs the original Rust/prover checks
and their own contracts. The checker does not decide that a recorded theorem,
assumption, theory translation or checker is correct.

## Operational boundary

The fixed [growth obligation](constraints/growth-obligation-v0000.json) is
retained with a [documentary seal](constraints/growth-obligation-seal-v0000.json).
It records `Open` / native `Seal` **NotIssued**, not a discharged proof. Both
the checkpoint and the exact obligation pin are checked; there is no automatic
resealing command. The original root is `pascal-research-presentations` and
must retain the exact original Pascal documents.

Geometry candidates must cite earlier same-home parents reaching that root.
An external reference, cross-home parent, alternative root, missing or cyclic
parent chain, or asserted native discharge is refused. A candidate may retain
external derivation evidence, but no such reference is sufficient for native
admission. Q4/M6 remains an external reference. The existing Research 0128
Pascal task is a proposed successor with native import/transport still Open.
The checker admits **zero native geometry successors**.

These are catalog/CI gates and agent obligations, not an OS sandbox or a new
program publication mechanism. Existing geometric or logical routines outside
this catalog keep their original research scope. See the
[task-loop audit](../../docs/research/0154-math-catalog-and-task-loop-boundary.md)
for what they can already compute.

Bounds are 32 entries, 256 reference occurrences, 96 files, 256 KiB per
metadata file, 8 MiB per referenced file, 32 MiB total read bytes and a
five-second cooperative deadline between reads. No subprocesses, retries,
recursive imports, proof replay or pin repair are performed. This is a local
quiescent-checkout check, not an atomic repository snapshot or an OS watchdog
against blocking filesystem I/O. A fingerprint change requires a reviewed
catalog edit; the checker never updates a digest for the user.

Existing materials remain at their original locations. No epoch, recipe,
proof source, path log or verifier rule is moved or rewritten. The additive
CLI change gives `adva.py` a new hash: Research 0153's historical pins remain
unchanged and refer to its original runtime commit `5d956de` (merge `8c94621`).
Use that revision for the historical campaign; this catalog does not rerun it.

## Revision discipline

Add documentary keys explicitly, declare every applicable topic, and preserve
the distinction between an asserted evidence state and actual proof admission.
Keep cross-domain interpretation obligations visible. A new topic or schema
requires an explicit catalog version/design decision, not a reinterpretation
of v0. Studying a candidate logic never authorizes changing the frozen checker
inside a running experiment. Semantic promotion remains subject to the
existing research agenda and Rust authority boundary.
