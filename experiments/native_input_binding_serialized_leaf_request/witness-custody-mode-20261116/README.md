# Witness-custody mode: finite structural comparison (2026-11-16)

## Frozen problem

The predecessor audit showed that the selected five-member request projection is checked against an externally supplied ten-field `ResearchCertificate`; it does not reconstruct that certificate. This round asks a narrower formulation question:

> When a witness may either be carried as explicit fields or produced by a pinned reconstruction route, must the envelope state which custody branch supplies it?

The frozen universe has three modes (`omitted`, `carried`, `reconstructed`), every subset of the ten certificate fields, and five Boolean guards for recipe presence, reconstruction inputs, request pin, checker pin and noncommutative order. The single route exhausts `3 * 2^10 * 2^5 = 98,304` records.

Rational values are opaque. Additive zero, multiplicative unit, quotient guards, inverses and M6 are not evaluated.

## Result

The bounded decision is **`PassedFiniteCustodyDiscrimination`**.

When the custody mode is projected away, the 98,304 records collapse to 32,768 classes. Exactly 4,096 projected classes contain multiple incompatible statuses. One representative complete-field projection simultaneously admits:

- `StructurallyReady/CarriedFieldsPresent`;
- `Unknown/CustodyModeOmitted`;
- `Refused/MixedCustodyShape`.

When the mode is retained, all 98,304 classes are single-status classes; there are zero mixed-status classes.

This does not mean that a carried certificate is semantically valid. `StructurallyReady` means only that its declared structural obligations are present. A structurally complete reconstructed branch remains `Unknown/NativeReconstructionNotRun`.

## Proposed vocabulary

**witness-custody mode** is retained as a **Proposed** word.

- **Role:** select exactly one obligation family before semantic validation.
- **Input:** request/checker pins, preserved order, and either explicit carried fields or a pinned reconstruction recipe plus inputs.
- **Output relation:** a typed structural status together with any remaining native obligation.
- **Applicability:** a protocol permits both serialized witness carriage and witness reconstruction.
- **Witness:** the exhaustive 98,304-record comparison in `outcome.json`.
- **Refusal conditions:** omitted mode; mixed carried/reconstructed members; missing carried field; absent recipe/input; pin mismatch; changed noncommutative order.
- **Expansion/replay:** branch on the tag, execute only that branch's checks, and retain any semantic/native residual.
- **Residual:** neither a native ten-field codec nor a reconstruction route was implemented or executed.

The word adds 33 bytes to the measured canonical JSON example (115 to 148 bytes). The finite comparison shows a reduction from 4,096 ambiguous projected classes to zero when the tag is retained. One-shot formation timings are reported but are not used to claim a speed improvement.

## Fresh reuse

The same relation was reused on a new three-field `TransportCertificate` shape with `source`, `ordered_history` and `binding_node`:

- omitted complete witness -> `Unknown/CustodyModeOmitted`;
- carried complete witness -> `StructurallyReady/CarriedFieldsPresent`;
- missing ordered history -> `CertificateObstruction/MissingCarriedFields`;
- reconstruction shape -> `Unknown/NativeReconstructionNotRun`;
- altered order -> `Refused/NoncommutativeOrderMismatch`.

Reuse verification took 4,026 ns. This is a second finite structural instance, not evidence of general universality or social adoption.

## Costs

- one route; 98,304 candidates; zero correction replays;
- enumeration: 249,640,285 ns;
- verification: 7,425,738 ns;
- whole run before serialization: 257,182,245 ns;
- serialization: 128,842 ns for 4,235 bytes;
- supervisor wall time: 0.372515241 s;
- peak RSS: 53,696 KiB;
- baseline/explicit formation: 78,467 / 12,749 ns;
- baseline/explicit payload: 115 / 148 bytes;
- native executions: zero;
- outcome SHA-256: `8080c8da7178a4bbb0b17634903dabd0bb88430afbb9281ed3ea77ecf57d47a1`.

## Boundaries and continuation

This is a finite contract-language result. The proposed word is not promoted as a learned theorem. Research 0090 coverage remains open; therefore Research 0092 all-fillings closure and promotion remain blocked. No M6 filler, native `free`/`Close`, arithmetic universality, hypothesized arithmetic truth, authentication, social trust or measured practical adoption follows.

Draft PR #234 still has an independent RLIMIT inventory failure. This experiment does not import or install resource limits and does not repair or conceal that failure.

The next minimum continuation is to review whether `carried` and `reconstructed` are exhaustive for the intended receiver. If a third branch such as externally referenced custody is needed, add it before any Rust adapter is implemented. Otherwise, freeze the exact native field encoding and reconstruction-receipt schemas under this mode boundary.

Reproduction:

~~~sh
timeout 30s python3 run.py
~~~

Authored and technically checked by Codex (OpenAI), submitted through Mingli Yuan's GitHub account as authorized proxy. Account use is not his authorship, review, endorsement or correctness guarantee.
