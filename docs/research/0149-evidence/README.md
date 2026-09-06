# Research 0149 execution record

Executed locally on 2026-09-06 under the preceding frozen
[contract](../0149-library-stability-and-zigzag.md). One standalone native trial
completed; no repair trial or continuation was run. The Rust example and
contract were not edited after this trial.

## Outcome

The [raw report](study.json) retains nine case receipts, their re-execution
results, four negative applicability audits, all frozen requests and source
digests. Every expected outcome matched. The cases include four feature
closures, two open questions, one model gap and two resource-limited Unknowns.
`Completed` describes the calibration, not a universally converged library.

| Case | Result | Retained distinction |
| --- | --- | --- |
| Delayed evidence | FeatureClosed, 4 candidates become 2 | Three unchanged revisit rounds were Open; only the later observation separates candidates. |
| Syntax question | Open with the same 2 candidates | `2*x` and `x+x` have equal polynomial shadows but different retained syntax. |
| Point question at zero | FeatureClosed with all 4 candidates | A question can be decided without choosing one object. |
| Six no-evidence passes | Open, no strict progress | Longer history does not eliminate possibilities. |
| Fresh coefficient three | FeatureClosed, 4 become 2 | The same supplied recipe works on a fresh finite instance. |
| Repeated evidence | FeatureClosed, no additional strict update | Repeated observations are retained, not counted as new constraints. |
| Evidence outside the model | ModelGap | Empty candidate coverage is not a vacuous success. |
| Zero / partial cap | Unknown / Unknown | Partial retains one completed round and four pending rounds. |

All four audits refused applicability: a forged feature, a changed question,
an enlarged catalogue and a changed method. Old receipts are retained. A
separate unit test keeps **all** old observations while adding `2*x*x` in a
new epoch; the previously closed polynomial question becomes Open. This is
the distinction between nonempty refinement and extension of the model.

Existing test-local braid oracles also passed: `(sigma1 sigma2)^3` returns
endpoint colours but has nonidentity Artin action, and the pure commutator
`sigma1^2 sigma2^2 sigma1^-2 sigma2^-2` has zero pairwise winding counts but
nonidentity action. Existing local normalization controls retain the separate
well-founded, directed normalization requirement. These regressions do not
turn the six-pass stuttering control into executable braid or M6 semantics.

## Costs and integrity

The shared logical ledger spent **1089 / 50000** units: 491 producing nine
receipts, 491 re-executing them, 18 replay admission/comparison charges,
88 negative-audit units and one prepaid checkpoint unit. No child or replay
received a fresh study account. These are abstract charges, not instructions.

[Measured native process cost](native-cost.txt): 0.10 seconds wall time,
0.07 seconds user time, peak RSS 4912 KiB, exit 0. The report is 165139 bytes.
These are one local observation, not portable performance claims.

Report SHA-256:
`034910fbd171a8fa77e3bbc08f161d2b7c49162e2ecda8c1d9492efa8ac7ab98`.

Source SHA-256:
`2293d5ebf1d053d3e04ca8dab7b90a5c60125b9e8a6d325dc1990a2983124576`.

Contract SHA-256:
`2bf8acfd34dddb60be5ba69070bd018d0c1a8d48d9f56e15f4f1463a3183d8d2`.

Cargo.lock SHA-256:
`b687d45dd12b4da84efdb0f258c8990fd867e23b666e38d6fdea59b7ac5b5e16`.

Hashes are integrity coordinates, not authentication. The exact normalizer,
example, lockfile and contract BLAKE3 digests are also embedded in the report.
Receipt serialization/reconstruction is covered by the tests; the standalone
trial re-executed its in-memory receipts before serializing the whole report.
There was no second standalone persisted-report verification run.

## Validation ledger

- Targeted pass 1, capped at 180 seconds: 9 initial example tests passed.
- Targeted pass 2, capped at 180 seconds: all 11 final example tests passed,
  then the standalone example built successfully. No third pass was needed.
- Existing Python braid and partial-normalization pass, capped at 60 seconds:
  16 tests passed in 0.17 seconds.
- Full `cargo test --workspace --offline`, capped at 180 seconds: passed
  (202 pre-existing Rust tests; example tests run separately).
- `cargo clippy --workspace --all-targets --all-features --offline -- -D warnings`,
  capped at 180 seconds: passed.
- New Rust source passes rustfmt; `git diff --check` passes. The environment
  audit had already found one unrelated existing rustfmt mismatch in
  `crates/adva-witness/src/prime_certificate.rs:163`; it was left untouched.

The executed Rust/Python test commands passed. A final all-claims dependency
audit did fail on an existing dangling reference:
`adva.bounded-verified.symbolic-probe-matrix-shadow.v0` depends on the absent
`adva.exact.structural-forward-differential.v1`. A read-only audit of `HEAD`
confirmed the same pre-existing issue; it was not changed here. TOML parsing,
unique claim IDs and the new claim's dependencies pass. CI now explicitly
tests this example, since ordinary workspace tests omit its embedded tests.

The standalone command used the already-built binary, a new output path,
`timeout 15s`, address-space limit `ulimit -v 524288`, and output-file limit
`ulimit -f 1024`, with `/usr/bin/time -v` covering the native process. Rust
also enforces the shared study account and bounded output envelope.

## Remaining boundary

This is a supplied finite-catalogue calibration, not live library admission or
self-generated syntax. It implements neither authenticated observation input,
append-only production storage, automatic candidate discovery, a general
braid normalizer nor open-world convergence detection. Future integration
must preserve the same frozen-epoch and question-applicability boundaries and
remain subject to the research agenda's stable promotion gates.
