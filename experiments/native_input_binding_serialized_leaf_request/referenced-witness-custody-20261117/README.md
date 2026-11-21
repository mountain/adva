# Referenced witness custody: an equal-budget finite discrimination

Date: 2026-11-17

## Frozen question

Does the two-value proposed vocabulary `witness-custody mode = carried | reconstructed` exhaust the receiver-side custody cases needed by the serialized request relation, or is a separately typed `referenced` branch needed for evidence held outside the request?

The comparison freezes one 11-bit structural universe (2,048 evidence shapes), the same request/checker pin and noncommutative-order refusals, and equal evaluation budgets of 6,144 branch-shape nodes per grammar. The two-branch grammar uses a budget-preserving `reserved-unexpressed` slot; the revised grammar replaces that slot with `referenced`. Arithmetic contents remain opaque.

## Result

Status: `PassedFiniteReferencedCustodyNeed`.

Across 12,288 total evaluations, all 4,096 paired `carried`/`reconstructed` classifications were invariant. The complete external-reference target was not ready under the old grammar: its two typed branches refused a mixed custody shape and the reserved slot returned `Unknown/UnexpressedCustodyMode`. Under the revised grammar, the same shape was uniquely `StructurallyReady/ReferencedReceiptPresent`.

Exactly one shape became newly ready. Typed controls returned:

- missing authority pin: `CertificateObstruction/MissingAuthorityPin`;
- missing retrieval receipt: `CertificateObstruction/MissingRetrievalReceipt`;
- digest mismatch: `Refused/ReferenceDigestMismatch`;
- the carried control remained `StructurallyReady/CarriedFieldsPresent` in both grammars.

A fresh reuse instance, an external `TransportCertificate` manifest, reproduced the complete, missing-authority, missing-receipt, and changed-digest distinctions without changing the grammar.

## Vocabulary revision (Proposed only)

`witness-custody mode` is revised from `carried | reconstructed` to `carried | reconstructed | referenced`.

- Role: state how the receiver can obtain the exact witness bytes without conflating custody mechanisms.
- Referenced input: locator, content digest, authority pin, retrieval receipt, request/checker pins, and preserved noncommutative order.
- Applicability: witness bytes are external and are neither carried fields nor reconstructed from a recipe.
- Output relation: `StructurallyReady/ReferencedReceiptPresent`; semantic import remains residual.
- Witness: this equal-budget finite comparison plus the fresh external-manifest reuse.
- Refusal: mixed custody members; absent locator/digest/authority/receipt; digest mismatch; pin mismatch; or changed order.
- Expansion/replay: resolve the pinned locator, verify authority and digest against the receipt, import the bytes, then run native semantic validation.
- Residual: this round performed no external fetch, byte import, or native certificate validation.

Formation added 13 serialized bytes to the finite vocabulary representation. The revision therefore improves expressibility only for this frozen structural universe; it is not a theorem that these three values exhaust all custody modes.

## Reproduction

```sh
timeout 30s python3 run.py
python3 -m json.tool outcome.json >/dev/null
sha256sum outcome.json
```

The observed outcome is 5,569 bytes with SHA-256 `b97456304cfaa4486e20e225f334572e859081711420cdf0fe4619094d063e43`.

## Measured cost

- route count: 1;
- evaluated nodes: 12,288;
- evaluation: 61,091,577 ns;
- verification: 25,742 ns;
- serialization: 168,493 ns;
- fresh reuse: 7,701 ns;
- peak RSS reported by `getrusage`: 9,344 KiB;
- external fetches/native executions: 0/0;
- implementation correction replays: 0.

The missing `/usr/bin/time` launcher failed before Python started and consumed no search node; in-program `getrusage` supplied the memory measurement.

## Boundaries and residual obligations

This is finite structural evidence, not semantic certificate acceptance, a native adapter, Research 0090 coverage, Research 0092 promotion, M6 filling, arithmetic universality, hypothesized arithmetic truth, social trust, or measured practical adoption. Addition-to-zero and multiplication-to-one domains were not inspected or conflated. The independent CI inventory/RLIMIT mismatch remains unrepaired.

The smallest continuation is to freeze and test the schema of the locator/authority/receipt triple against one real native import boundary, without claiming that successful retrieval supplies semantic acceptance.
