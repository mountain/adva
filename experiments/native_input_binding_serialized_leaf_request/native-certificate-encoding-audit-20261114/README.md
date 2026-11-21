# Native certificate encoding audit (2026-11-14)

## Frozen question

On the pinned `ResearchCertificate` source surface, does the existing serialized-leaf request provide an explicit, field-complete, replayable encoding and reconstruction route for the ten certificate fields, or does it still depend on a separately supplied native certificate?

The frozen contract is in `contract.json`. It quantifies over one complete 1,389-line Rust source file at SHA-256 `391c6eef4df0f63a7cbd8d19dbc0967fd717ef26b3a70342aaa19c5e4c90c8bb`, one structural positive control, one route, a 30-second supervisor limit and at most 100,000 inspected nodes. Rational is opaque here: additive zero and guarded multiplicative unit remain different typed questions, and no inverse, commutation or M6 conclusion is in scope.

## Source evidence

Static inspection of the pinned file found:

- lines 46-58 declare exactly ten `ResearchCertificate` fields and derive only `Clone`, `Debug`, `Eq` and `PartialEq`;
- no `Serialize` or `Deserialize` derive or explicit implementation for `ResearchCertificate` occurs in the selected file;
- lines 650-668 serialize exactly five request members: profile, source diagram JSON, residual diagram JSON, external leaf, and one dynamic native occurrence pair;
- lines 673-747 require `certificate: &ResearchCertificate` separately from `encoded: &str`, rederive the one dynamic pair from that external certificate, and pass the same certificate to `receive`;
- the receiver imports and compares the two diagram JSON values, but it does not construct a `ResearchCertificate`.

Thus the source evidence supports the narrower judgment **`NativeEncodingAbsentAtPinnedSourceSurface`**: the selected wire route is a request projection checked against an already available certificate, not a native lossless certificate codec. This is not a repository-wide absence or reconstruction-impossibility theorem. In particular, the two diagrams may carry overlapping semantic information, but the selected receiver contains no field-by-field reconstruction of event mapping, forgotten occurrences/history, source bindings or binding-node history.

| Certificate field | Selected wire evidence |
| --- | --- |
| `source_snapshot` | source diagram bytes are imported and compared; no certificate field is reconstructed |
| `residual_snapshot` | residual diagram bytes are imported and compared; no certificate field is reconstructed |
| `static_value` | no explicit certificate member or reconstruction |
| `bound_source` | no explicit certificate member or reconstruction |
| `dynamic_source` | no explicit certificate member or reconstruction |
| `event_map` | no explicit certificate member or reconstruction |
| `occurrence_map` | one dynamic pair is projected and rechecked; the full ordered map is not carried |
| `forgotten_static_occurrences` | no explicit certificate member or reconstruction |
| `forgotten_static_history` | no explicit certificate member or reconstruction |
| `binding_node` | no explicit certificate member or reconstruction |

## Execution outcome

The retained final run status is **`Unknown/SerializationFailureAfterCorrectionLimit`**, not a successful tool certificate.

The initial invocation refused before analysis because the wrong prior source pin was used. The sole correction replay fixed the selected-source pin and comma-bearing Rust type parser. That replay completed the actual-source audit, a fresh field-complete synthetic control, and all pre-serialization assertions. It then failed while constructing the output because lowercase JSON booleans had been written in Python. No serialized outcome or in-process timing/memory record was retained. `attempts.json` preserves both failures. The literals are corrected in `run.py`, but the corrected script is deliberately **not rerun** in this round.

Reproduction for the next continuation, from this directory in the repository:

```sh
timeout 30s python3 run.py
```

The next run must either retain a successful JSON result with measured read/audit/control/verification/serialization costs and peak RSS, or preserve the new exact failure. It must not treat the synthetic positive control as a compiling Rust adapter.

## Claim boundary and continuation

No word is promoted. `NativeEncodingAbsentAtPinnedSourceSurface` is a scoped source judgment, not learned universal vocabulary. Research 0090 coverage remains open; Research 0092 promotion remains blocked. No M6 filler, native `free`/`Close`, arithmetic universality, hypothesized arithmetic truth, authentication, social trust or measured practical value follows.

The minimum continuation is one execution of the already corrected script. Only after a retained result should work begin on a separately versioned field-complete native carrier or a pinned native reconstruction route. The independent resource-inventory mismatch on draft PR #234 also remains open; this experiment does not install resource limits and must not be used to hide that CI failure.

Authored and technically checked by Codex (OpenAI), submitted through Mingli Yuan's GitHub account as authorized proxy. Account use is not his authorship, review, endorsement or correctness guarantee.
