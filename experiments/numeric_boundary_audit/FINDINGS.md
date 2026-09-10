# Findings and limits

This file describes the original pinned audit. The proposed corrections and
their distinct verification status are in [FOLLOWUP.md](FOLLOWUP.md).

The audit supports a concrete concern about numerical boundaries. It does not
establish the Xe driver's memory-corruption bug in Adva or a whole-repository
absence of similar bugs. The 58 production files were scanned for floating
types, conversion, rounding, finite checks, casts and debug-only assertions;
relevant arithmetic and consuming call paths were then read. No floating-to-
allocation-size path analogous to the Xe VRAM allocator was found in that scope.

## 1. Log-chain gradient: avoidable intermediate overflow

Location: `crates/adva-lisp/src/operation.rs`, `evaluate_logarithm` and
`scale_gradient`. The current computation forms `1.0 / argument.value` first,
then multiplies each upstream derivative by that reciprocal.

Take the valid program `f(x)=log((1/1024)*x)`, at `x=2^-1020`.
Input, scale, intermediate `2^-1030`, logarithm and exact derivative `2^1020`
are representable/finite (the intermediate is subnormal). Nevertheless:

```
current derivative: (1 / 2^-1030) * 2^-10 = infinity
exact derivative:   2^1020, a finite binary64 number
local alternative:  2^-10 / 2^-1030 = 2^1020
```

The C model of the inspected Rust operation order produced infinity in three
of five cases, including a second scale of 2^-20; direct derivative division
matched the exact power-of-two oracle in all five. This is a strong implementation
bug candidate, not an unavoidable loss because the correct answer is too large.
Actual Rust compilation/execution remains NotRun locally. The supplied Rust
driver is the next native acceptance gate. The mathematical derivative of the
smooth expression is being tested, not a derivative of binary64 rounding.

Suggested fix direction: divide each upstream derivative by the argument,
rather than materializing its reciprocal first; then validate ordinary,
subnormal, true overflow and zero-gradient cases in Rust. This may change
last-bit results on other inputs, so it requires an explicit realization/
versioning decision before replacing a stable rule. The alternative tested
here is not a proof of correctly rounded gradients for arbitrary programs.

## 2. Rational conversion: two rounded operands can cross the unit boundary

Location: `crates/adva-ir/src/term.rs`, `Rational::as_f64`:
`self.numerator as f64 / self.denominator as f64`.

For `9007199254740992 / 9007199254740993`, both integer casts produce 2^53,
so the observed result is 1.0, bits `3ff0000000000000`. The uniquely nearest
binary64 value of the exact rational is `3fefffffffffffff`, below 1. Exact
Fraction distances to adjacent floats independently confirm that oracle.
A second case, `(2^53+1)/(2^53+2)`, errs in the other direction by one ULP;
the exactly representable `1/1024` control agrees.

This establishes a C binary64 model counterexample to *correct nearest
conversion* of the exact Rational object. The present API says numerical IEEE
realization, without a fully specified rounding-quality guarantee; that contract
needs clarification before calling every last-bit deviation a contract violation.
It must in any event not authorize exact multiplicative-unity or a directed
boundary conclusion. Native Rust bits remain a pending verification gate.

## 3. Finite-value guard differs between APIs

`python/adva/core.py::KernelFunction._check_inputs` accepts Python float NaN and
positive infinity in the actual extracted source method. It rejects booleans,
so the method does type validation, but does not establish finiteness.

By inspection, `crates/adva-lisp/src/eval.rs::validate_inputs` checks names,
and the `log` guard tests only `value <= 0.0`; that predicate is false for NaN.
The general evaluate/differential paths and PyO3 bridge do not subsequently
check all values/Jacobian entries for finiteness before returning structural
certificates. This is a boundary-policy gap, not proof that those certificates
claim exact numerical truth. Their scope concerns graph/rule execution.

The separate `adva run` research profile in `native_run.rs` already rejects
nonfinite inputs and final scalar outputs. That protection should be preserved.
It is not shared by all APIs and does not certify a finite Jacobian. A
consistent finite-only API policy or explicit nonfinite result status must be
chosen before calling numerical execution safe for optimizers/boundary decisions.

## 4. A directly analogous resource-bound expansion

`python/adva/quine_relay.py::Supervisor.restrictions` computes
`max(1, min(child_limit, floor(remaining)))`. When the aggregate CPU remainder
is 0.25 seconds, this installs a one-second RLIMIT_CPU. The exact method was
executed with a mocked `setrlimit`: the resulting configured bound exceeds the
remaining allowance. Controls at 1.25 and 2 seconds stay within the remainder.

The surrounding `check()` rejects an exhausted run before and after a child,
so this is not evidence that an overspent run will be accepted. It is evidence
that post-hoc rejection and a per-child minimum cannot promise a strict
aggregate pre-execution CPU bound. OS CPU-limit granularity is an additional
limit. No child process was launched to overspend resources in this control.
Prefer refusing another launch when less than the supported minimum remains,
or explicitly label the budget as soft with bounded overshoot. Do not increase
the remaining resource merely to fit an integer-valued interface.

## Known result not resolved by this round

Research 0141's native k28 input/reporting discrepancy remains open. The current
workspace pins serde_json 1.0.151 and requests `serde_json = "1"`; the upstream
manifest exposes optional `float_roundtrip`, not part of its default feature
list. This is a concrete diagnostic lead, not a proven root cause or a claim
about all resolved Cargo features. Collect native input/output `to_bits()` and
decoder/serializer controls before attributing the discrepancy.

Upstream feature reference:
https://github.com/serde-rs/json/blob/v1.0.151/Cargo.toml

## Fix order and resource account

1. Run the supplied Rust diagnostic once in the frozen workspace; retain bits,
   source and certificate scopes. Do not treat the C model as native success.
2. Specify finite-value and conversion contracts, then add narrow Rust regression
   gates and correct the local log differential arithmetic. Preserve history.
3. Correct or relabel the supervisor's sub-second admission boundary, with a
   focused mocked test. No broad repeated experiment is needed.
4. Separately resolve the existing JSON bit-pattern discrepancy.

The completed audit took 102.789 ms including its C build (87.741 ms), excluding
retrieval, authoring and report serialization. Python parent peak RSS was
15,124 KiB; maximum completed-child RSS 14,848 KiB. These are separate process
peaks, not a simultaneous total. No mathematical search was run, no runtime
rule was modified and no native Adva binary was executed. Zero exceptions from
the frozen audit suite; normal C/Python execution is not a proof of Rust parity.

The practical connection to the Linux incident is preserving the direction and
scope of a guarantee through each layer. An answer being finite or apparently
self-consistent is not an independent proof that it stayed inside that boundary.
