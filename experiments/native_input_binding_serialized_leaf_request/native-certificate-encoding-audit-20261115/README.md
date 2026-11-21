# Native certificate encoding audit: retained replay (2026-11-15)

## Frozen continuation

This round reused the unchanged 2026-11-14 contract and executed the already corrected source audit exactly once. The selected source remained `experiments/native_input_binding_certificate/native_input_binding_certificate.rs`, SHA-256 `391c6eef4df0f63a7cbd8d19dbc0967fd717ef26b3a70342aaa19c5e4c90c8bb`. No adapter, field encoding, arithmetic normalization or additional search route was introduced.

Reproduction from this directory:

~~~sh
timeout 30s python3 ../native-certificate-encoding-audit-20261114/run.py \
  --source ../../native_input_binding_certificate/native_input_binding_certificate.rs
~~~

## Result

The process exited zero, retained `outcome.json`, and passed all frozen assertions on the actual source and one fresh synthetic field-complete structural control.

The bounded decision is **`Unknown/NativeEncodingAbsentAtPinnedSourceSurface`**:

- the unique `ResearchCertificate` declaration has ten fields but no `Serialize` or `Deserialize` direction on this source surface;
- none of those ten field names is an accepted request-root member;
- the serializer projects one dynamic occurrence pair;
- the receiver still requires a separate `&ResearchCertificate`, rechecks that pair from it, and delegates the same certificate to `receive`;
- the receiver does not construct a `ResearchCertificate`.

The fresh control exposed all ten fields, both codec directions, a reconstruction expression and no external certificate parameter; it was classified `PassedExplicitFieldCompleteEncodingShape`. This validates only the audit's ability to distinguish the two source shapes. It is not a compiling Rust adapter and does not increase the mathematical expressivity of Adva.

The two diagram JSON members may contain overlapping semantic information, so this result is not a reconstruction-impossibility theorem. It establishes only that the selected native wire route does not itself declare and replay a field-complete certificate.

## Costs

- one route, one selected source and one structural control;
- two audit candidates, 1,388 source lines;
- source read: 1,148,882 ns;
- actual audit: 1,422,750 ns;
- control formation: 21,999 ns;
- control audit: 69,417 ns;
- assertions: 5,167 ns;
- whole run before serialization: 3,782,480 ns;
- serialization: 255,087 ns for 5,408 bytes;
- `ru_maxrss`: 11,008 KiB;
- zero native Rust executions and zero correction replays in this round.

The outcome's `implementation_correction_replays: 1` is cumulative provenance for the predecessor package. This 2026-11-15 replay itself used none. Supervisor wall time was not retained reliably and is not inferred from file size.

## Vocabulary and residuals

No word is promoted. `NativeEncodingAbsentAtPinnedSourceSurface` remains a scoped diagnostic status, not a learned theorem or generally reusable vocabulary item.

Research 0090 coverage remains open, so Research 0092 all-fillings closure and word promotion remain blocked. The existing five-member request projection supplies neither a field-complete carrier nor a pinned reconstruction route. No M6 filler, native `free`/`Close`, arithmetic universality, hypothesized arithmetic truth, authentication, social trust or measured practical value follows.

The next minimum construction is one separately versioned carrier or reconstruction-route **contract**, with exact input/output types and a refusal matrix for a missing history field, altered binding node, changed noncommutative order and request/checker pin mismatch. It should not be implemented until the independent RLIMIT inventory failure on draft PR #234 is repaired by the repository's native generator.

Authored and technically checked by Codex (OpenAI), submitted through Mingli Yuan's GitHub account as authorized proxy. Account use is not his authorship, review, endorsement or correctness guarantee.
