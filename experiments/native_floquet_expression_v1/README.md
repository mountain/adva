# Periodic A/M programs and a declared Floquet observation

The [research note](../../docs/research/0233-periodic-programs-before-floquet-observations.md)
proposes a native-compatible expression profile. This directory contains its
small original **external arithmetic calibration**. It does not construct
Adva programs, assign source/occurrence identities, call the Rust checker, issue
a semantic certificate, fit meteorological data or change a forecast.

The fixture has twelve seasonal phases: two quadratic anomaly steps and ten
translations. Its exact annual return is

```
E(h) = (3/8) h + (1/8) h^2 + (1/64) h^3 + (1/512) h^4.
```

The first-degree multiplier is 3/8. Reversing the two nonlinear steps preserves
that multiplier but changes higher coefficients. A shifted periodic reference
has nonzero propagation defects. These are controls against identifying a full
process with its spectrum or a periodic reference with a periodic solution.

The one original contracted launch passed **23 checks** using Python 3.14.4
and exact `fractions.Fraction` arithmetic. No numerical tolerances or external
packages were used. The checker compares the full composed polynomial with a
separately stated expansion and with five nested phase evaluations, retains
nonlinear residuals, rejects omission of finite multiplication cross terms,
and checks the constants in a finite-amplitude bound. The displayed interval
bound is proved by the note's triangle inequality; five evaluations alone are
not its proof.

For a read-only replay, from the repository root on POSIX, use a **fresh output
path**:

```sh
python3 experiments/native_floquet_expression_v1/check.py --output /tmp/native-floquet-replay.json
```

This invocation enforces 20 seconds wall time, 10 seconds CPU, 256 MiB address
space and 1 MiB output-file size. It refuses to overwrite its output. It runs
one fixed fixture, with no search, retries or network access. Reproduction is a
separate finite check, not a reset of the original launch allowance. Keep
`contract.json`, `report.json`, `launch-ledger.json` and `execution-receipt.json`
unchanged. The original supervisor imposed an additional 25-second timeout.

`PassedExternalArithmeticCalibration` means only those declared checks passed.
The report explicitly records `native_semantic_certificate: NotConstructed`.
Closure of a generic observer language, certified variation across native
slices, and weather-model integration remain open. The degree argument about
polynomial eigenobservers is documentary mathematics, not one of the 23 checks.

Authored by Codex (OpenAI), project-original under Unknown v0.3, submitted
through Mingli Yuan's authorized account proxy. This does not assert his
authorship, review, endorsement or a correctness guarantee. No third-party
text, implementation, dataset or dependency is included.
