# From boundary audit to reviewable corrections

Source baseline: main `7be406bfa6a3b7a5ef619081157e3b113da0cd40`.
Original audit commit: `acc950528b1f2b47a56d2a0e5a11c292adcf880b`.
Date: 2026-09-10. Existing draft PR #173; no main merge.

## Implemented changes

- Register the direct-division log differential as `adva.builtin:log@2`.
  New Lisp parsing resolves the active version through the single registry.
  Legacy `log@1` remains executable from versioned terms and checked diagrams.
- Refuse a Quine child launch when the remaining aggregate or per-child CPU
  allowance cannot contain a positive integer-second limit. Refusal precedes
  call-record mutation, output-file creation and `Popen`.
- Add native regression tests and a diagnostic comparing both log versions.
  Preserve all original audit measurements in `report.json`.
- Make the old audit script refuse source drift before running. Its baseline
  assertions deliberately describe the old implementation, so it must not
  relabel a modified checkout as evidence about the pinned baseline.

See ADR 0044 for the compatibility decision and numerical-policy boundaries.
No existing theorem claim or stored library artifact is promoted or rewritten.

## Completed execution

```sh
python tests/python/test_quine_cpu_budget.py
```

Six unittest methods passed, with subcases at CPU remainders 0, 0.25,
`nextafter(1, 0)`, 1, 1.25, 2 and 8.75 seconds. A changed per-child cap and a
changed child-CPU observation are separate reuse controls. One admitted real
Python child printed `ok` and exited zero. Other limit/launch tests use mocks
to inspect refusal and configured limits without deliberately overspending.

The test suite reported 0.022 seconds. Its enclosing fresh-process run measured
116.931 ms, with completed-child maximum RSS 20,016 KiB on Linux. This is not
a simultaneous process-tree memory peak. `fix-verification.json` records the
measured command and scope. Research, editing, network, serialization and
native execution costs are not included. An attempted `/usr/bin/time` wrapper
was unavailable; it did not execute the tests. The Python measurement wrapper
then ran them once successfully, without an implementation correction.

Running the baseline-only `audit.py` on this changed source was also checked:
it exited before model execution, identified `operation.rs` as changed and
directed the caller to the original commit. This refusal is intentional.

## Native gates still required

```sh
cargo fmt --check
timeout 120s cargo test --locked -p adva-lisp --lib operation::tests
timeout 120s cargo test --locked -p adva-lisp --test numeric_boundary
timeout 120s cargo test --locked --release -p adva-lisp --test numeric_boundary
timeout 120s cargo run --locked -p adva-lisp --example numeric_boundary_audit
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace
```

Rust/Cargo are not installed locally. The previous PR head's remote Rust job
`102823135360` was marked failed with an empty step list; its log endpoint
returned `BlobNotFound`. Therefore it supplies neither a native counterexample
nor a successful native test. No repeated CI reruns were requested, and the
failure cause has not been attributed to the implementation.

The native diagnostic now emits `adva.native-numeric-boundary-diagnostic.v1`:
ten log rows (five inputs, each with versions 1 and 2), three rational rows,
and six input-admission rows. Bit patterns represent nonfinite results without
using invalid JSON NaN/Infinity numbers. The existing baseline report remains
version zero and has not been regenerated from new code.

For the original C/Python audit, run `audit.py` from a separate checkout at
`acc950528b1f2b47a56d2a0e5a11c292adcf880b`. Expected old behavior is three
avoidable log-gradient overflows, two non-nearest rational conversions, and
the sub-second limit expansion. Those results are not post-fix Rust evidence.

## Remaining obligations and practical help

Native debug/release replay is the next smallest step. The new source compiler
version selection can change regenerated log-bearing artifacts; frozen
contracts must reject changed protected source until separately migrated.
Rational conversion, finite-input/Jacobian policy and the old JSON input/output
bit discrepancy remain open. No whole-repository floating-point safety claim
or guarantee of strict physical CPU accounting is made.

This helps runtime maintainers preserve historical rule identity while
reviewing a numerical correction, and helps finite research runners stop
before silently increasing a remaining resource bound. No new vocabulary is
needed, and no end-user benefit for Jiamin has been measured.
