# Native numerical boundary corrections

Date: 2026-09-10. Continues the audit and initial correction in draft PR #173.
The upstream main baseline is `7be406bfa6a3b7a5ef619081157e3b113da0cd40`;
the initial correction is `61a7ae4`. Both the embedded and standalone
adva-library checkouts are synchronized to
`ba5be9fb672520ed22a7f2d923c1481bbe03aacc` and require no content changes.

## Corrected behavior

| Boundary | Previous result | Current behavior |
| --- | --- | --- |
| Log differential with a tiny argument | Reciprocal overflows before a finite multiplication | New source uses `log@2` and divides each incoming derivative directly by the argument |
| Exact rational conversion | 9007199254740995/9007199254740994 becomes the float above one | `constant@2` rounds the exact ratio once, to 1.0 |
| Ordinary native Python evaluation | NaN/Infinity or overflowing derivatives can accompany a structural certificate | Rust finite entry points reject nonfinite inputs, final outputs and requested final Jacobians |
| Result serialization | A nonfinite scalar becomes JSON null | Scalar-bearing IR result types refuse serialization |
| JSON input transport | 0.9999999962747097 changes by one ULP | serde_json `float_roundtrip` preserves the k28 input and report bits |
| Child CPU limit | Subsecond remainder expands; a forked child recomputes against different accounting | Parent admits only a contained whole-second allowance and passes it unchanged into the child |

ADRs [0044](../../docs/adr/0044-versioned-log-differential-and-budget-admission.md)
and [0045](../../docs/adr/0045-rational-rounding-and-finite-numeric-boundaries.md)
specify the operation and policy boundaries. Stored `log@1`, `constant@1` and
legacy Constant terms retain their previous realizations. The raw Rust replay
APIs remain available; finite-policy certificate IDs and scopes are explicit.
Reparsing source selects the new versions and can produce different artifacts.

## Acceptance

`native-verification.json` records commands, outcomes and diagnostic hashes.
`native-diagnostic.json` retains the actual Rust diagnostic. Its debug and
release outputs are byte-identical, including ten log cases, four rational
cases, legacy and finite input admission, and the k28 JSON bit comparison.

The Rust workspace passes 229 tests. Release validation of adva-ir and
adva-lisp passes 64 tests. The four explicit CI research example targets pass
37 tests. Formatting and workspace Clippy with warnings denied pass.
The Python native extension was rebuilt from this source before verification.
The numerical regression compares 518 literal ratios against Python Fraction,
including 256 adjacent unit-boundary cases and 256 seeded signed cases, and
checks nine exact dyadic log chains. Direct PyO3 and SciPy refusals are included.

The Python full suite passes 1637 tests and 10 subtests; one optional ed25519
backend test is skipped because that backend is not installed.
The retained Quine evidence checker accepts all 152 files from the two original
runs and 50 calls. The catalog checker accepts all 20 current library entries;
its documentary open obligation remains open.

Example reproduction, from a built development environment:

```sh
cargo fmt --check
cargo clippy --locked --workspace --all-targets --all-features -- -D warnings
cargo test --locked --workspace
cargo test --locked --release -p adva-ir -p adva-lisp
cargo test --locked -p adva-witness --example library_stability --example library_generation --example verifier_search --example search_campaign
cargo run --locked -q -p adva-lisp --example numeric_boundary_audit
cargo run --locked --release -q -p adva-lisp --example numeric_boundary_audit
VIRTUAL_ENV="$PWD/.venv" .venv/bin/maturin develop --locked
.venv/bin/python -m pytest -q
.venv/bin/python experiments/quine_relay/verify_evidence.py
.venv/bin/python -S python/adva/adva.py math-check --key-words
```

Initial full-suite attempts hit the environment's `/tmp` quota. A second
attempt exposed a catalog fixture copying the entire checkout, including build
and temporary directories; it was stopped. The fixture now copies only catalog
metadata and declared pinned files, retaining its omission and growth checks.
Completed retries use a writable TMPDIR; the Python full-suite directory is
outside the checkout. Two optical calibration expectations were also updated
to the new constant version while retaining their mathematical assertions.

These are implementation regressions within the stated scope. They do not
prove numerical stability of arbitrary compositions, exact real arithmetic,
strict physical CPU accounting, or the truth of a library theorem. Historical
audit reports, research evidence, contracts, obligations and library pins are
preserved; old baseline scripts intentionally refuse changed source.
