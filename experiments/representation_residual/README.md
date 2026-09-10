# Representation residual: k28 JSON transport closure

- `run.py` — the original bounded external-representation suite (question-driven;
  launches the native backend once per case).
- `diagnose.py` — retained-evidence diagnosis of the product-k28 mismatch; it
  asserts the ORIGINAL frozen state and must not be relabeled against new code.
- `k28-replay-20260910.json` — closure record: replaying the retained
  `product-k28.program.adva` through the current native backend.

## Status (2026-09-10)

The research 0141 product-k28 input/reporting discrepancy is closed. The retained echo
showed a one-ulp transport discrepancy (`0.9999999962747097` ->
`0.9999999962747096`), so the Python exact-Fraction matcher rejected the
case. Fix `ade4f88` enables the workspace `float_roundtrip` feature and adds
the regression test
`native_input_and_report_preserve_k28_binary64_values`.

Replay of the retained program through the current backend reports
`y = 0.9999999962747097` (bits `0x3feffffffe000000`, exactly `1 - 2^-28`),
values `[1.0]`, and the echoed inputs equal the submitted JSON.

Retained evidence under `docs/research/0141-native-evidence/` is frozen and
unchanged.

## Merge review clarification

`float_roundtrip` selects the decimal-to-binary floating-point deserialization
path in serde_json (`src/de.rs`), rather than an output-formatting policy.
The old echoed lexeme alone did not isolate parsing from serialization; the
feature change and native regression address the input parsing/round-trip
boundary. This does not promise preservation of arbitrary JSON spellings.
Source: https://docs.rs/crate/serde_json/1.0.151/source/src/de.rs .
