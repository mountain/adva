# Numerical boundary audit prompted by the Xe alignment bug

## Correction follow-up

This directory retains the original audit below. The current draft also contains
the versioned `log@2` correction and contained CPU-limit admission. See
[FOLLOWUP.md](FOLLOWUP.md) and ADR 0044 for changes, passing Python tests and
the still-pending Rust gates. `report.json` is original pre-fix evidence.
Run the original `audit.py` at commit
`acc950528b1f2b47a56d2a0e5a11c292adcf880b`; on changed source, the current
script deliberately refuses to label new behavior as that baseline.

## Original audit scope and results

Frozen source: Adva main `7be406bfa6a3b7a5ef619081157e3b113da0cd40`.
Status: bounded source audit and external reproductions; native Rust run pending.
No production implementation, operation version, certificate schema or runtime
policy is changed. This is a continuation of the representation-boundary audit,
not a new semantic phase or proof of arithmetic universality.

Question: does the implementation introduce avoidable numerical boundary errors,
or return checks whose scope can be mistaken for finite/exact numerical validity?
Scope: all 41 Rust `crates/*/src/**/*.rs` files and 17 top-level Python `python/adva/*.py`
files, plus the relevant manifests and Research 0141. The source inventory
records exact Git blob and SHA-256 pins. Tests/examples, external experiments,
vendored dependencies and hardware memory allocation are not exhaustively audited.

Finite plan: one five-case log-gradient model, three rational conversions,
four Python input-boundary controls, three mocked resource-limit settings.
No iterative search or native binary loading. C build timeout 10 seconds,
execution timeout five seconds; Python orchestration timeout 30 seconds.
Exact Fraction arithmetic and power-of-two cases provide independent oracles.
The source methods for Python checks are extracted unchanged with Python AST;
the resource module is mocked so no real process limit or child is installed.

The motivating primary source is Linux commit
[818bebeb63dd](https://github.com/torvalds/linux/commit/818bebeb63dd6bf5f4e07e145f6cdbace520a34c),
dated 2026-08-21. It fixes integer address alignment, not floating point. The
patch changes upward 128 KiB alignment to downward 4 KiB alignment and changes
the overlap assertion. The assertion still uses `xe_assert_msg`; this patch
alone does not show that it becomes an unconditional release-mode check.

Run from a complete Adva checkout with C compiler and Python 3:

```sh
timeout 30s python3 experiments/numeric_boundary_audit/audit.py
```

The script prints JSON and uses temporary files for the C model. A separately
prepared native driver is supplied as `crates/adva-lisp/examples/numeric_boundary_audit.rs`.
Run it on a machine with the pinned Rust workspace available:

```sh
timeout 120s cargo run --locked -p adva-lisp --example numeric_boundary_audit
```

That command is pending here because Rust/Cargo are unavailable. C binary64
agreement supports the inspected arithmetic path, but is not an Adva execution.
The Rust driver records bit patterns and certificate fields without asserting
that nonfinite values are exact mathematical results.

The report and FINDINGS.md distinguish observed Python behavior, C models of
Rust arithmetic, existing known limitations and unresolved native obligations.
No private artifact is downloaded and no source semantics is changed merely
to produce a passing result. A stable fix must respect the operation/version
discipline and be checked in Rust in both debug and release configurations.
