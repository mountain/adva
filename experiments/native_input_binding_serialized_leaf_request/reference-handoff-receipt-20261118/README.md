# Reference-handoff receipt at a pinned native boundary

Date: 2026-11-18

## Frozen question

Can the referenced branch proposed on 2026-11-17 be expanded into a replayable
locator/authority/digest receipt for the exact bytes expected by one existing
native consumer, without treating successful byte retrieval as semantic
certificate acceptance?

The target is the merged source
experiments/native_input_binding_certificate/native_input_binding_serialized_consumer.rs
at main commit 8fc38427f2a479b4e8e84802e1873cff14d54566. That source reads
ADVA_SERIALIZED_LEAF_REQUEST_PATH, uses byte/work budgets 65,536/512, requires
exact canonical bytes, and names native acceptance only in the matching test
case. The pinned payload is the 4,464-byte canonical-request-20261031.json.

The route has five declared instances, three receipt controls and five source
surface assertions: twelve counted units, at most 30 seconds and no more than
one correction replay.

## Result

Composite status: RetrievedExactBytes/NativeAcceptanceUnknown.

The bounded byte-retrieval sub-result passed:
PassedBoundedReferenceRetrieval.

- The decoded payload was exactly 4,464 bytes and had SHA-256
  d4d619a621ac7fd2943daa9c6eb0757acc79023314ecf9ed7dcf2f9cb0c84d4d.
- The repository, commit, path and Git blob pin matched.
- The matching instance returned Retrieved/ByteExact.
- Wrong authority, wrong digest and a one-byte-too-small budget returned
  Refused/AuthorityPinMismatch, Refused/ContentDigestMismatch and
  Refused/ByteBudgetExceeded.
- A valid receipt returned StructurallyReady/ReceiptBoundBytes.
- Missing and digest-altered receipts returned
  CertificateObstruction/MissingRetrievalReceipt and
  Refused/ReceiptDigestMismatch.
- A fresh 70-byte synthetic payload reused the resolver and receipt validator.

The pinned Rust source surface also contains all five required handoff patterns.
However, this execution environment has neither cargo nor rustc. The native
consumer was therefore not run. No Python mirror result is substituted for the
native outcome.

## Proposed word

reference-handoff receipt is a **Proposed** word.

- Role: bind retrieved bytes to their locator, authority tuple, digest and
  bounded retrieval event without granting semantic acceptance.
- Input: pinned locator and authority, expected digest, byte budget and
  retrieved bytes.
- Output relation: Retrieved/ByteExact, then
  StructurallyReady/ReceiptBoundBytes.
- Applicability: witness-custody mode is referenced and an external byte
  sequence must be handed to a separately pinned consumer.
- Witness: five fixed instances, three receipt controls, the pinned Rust
  source-surface check and one fresh reuse.
- Refusal: authority mismatch, byte-budget exhaustion, content-digest
  mismatch, missing receipt, or receipt digest/length mismatch.
- Expansion: resolve bounded bytes; compare the complete authority tuple;
  verify length and digest; carry receipt and bytes together; invoke the pinned
  native consumer.
- Residual: native execution and semantic certificate acceptance were not
  performed.

The byte-only baseline serialized to 96 bytes. The explicit receipt form
serialized to 699 bytes, a formation cost of 603 bytes. This records additional
authority and retrieval history in the frozen comparison; it is not a global
expressivity or efficiency theorem.

## Reproduction

    timeout 30s python3 run.py
    python3 -m json.tool outcome.json >/dev/null
    sha256sum outcome.json

The retained outcome is 4,853 bytes with SHA-256
ab1c8086980a4b2bacc5d94de618f4f06068c2420dfe7635efcd9591365d1180.

## Measured cost

- one route and twelve counted units;
- fixture decode/read: 42,023 ns;
- consumer source read: 16,615 ns;
- evaluation and verification: 235,134 ns;
- serialization: 117,487 ns;
- whole run before serialization: 406,783 ns;
- process peak RSS: 10,368 KiB;
- zero execution-time network fetches and zero native executions;
- one correction replay.

The correction changed only the fresh instance's retrieval-medium label from
the canonical mirror label to synthetic-in-memory. It did not change any
classification or mathematical boundary.

## Boundaries and next obligation

This is a finite receipt-formation and byte-retrieval result. It is not native
consumer acceptance, semantic certificate acceptance, proof that three custody
modes are exhaustive, Research 0090 coverage, Research 0092 promotion, M6
filling, arithmetic universality, hypothesized arithmetic truth, social trust,
or measured practical adoption. Addition-to-zero and multiplication-to-one
domains remain distinct and were not evaluated. The independent RLIMIT
inventory mismatch remains open.

The smallest continuation is to replay the same receipt and exact bytes in an
environment with the pinned Rust toolchain, recording the native consumer's
actual result without widening its byte or work budget.
