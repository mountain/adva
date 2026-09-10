# ADR 0045: Exact-ratio rounding and explicit finite numerical boundaries

- Status: implemented; validation recorded in the numeric audit follow-up
- Date: 2026-09-10
- Continues: ADR 0003, ADR 0035, ADR 0044

## Problem and behavior

Separately converting an i64 numerator and denominator to f64 loses information
before division. For 9007199254740995/9007199254740994 it returns the float above
one, although nearest rounding of the exact ratio is one. The ordinary Python
entry points also return NaN/Infinity and overflowing Jacobians with structural
certificates; serializing such Rust results silently substitutes JSON null.
The default JSON parser changes the k28 input 0.9999999962747097 by one ULP.

## Versioned constants

`Rational::as_f64` now computes a 53-bit significand and the exact division
remainder in u128, then rounds once, nearest with ties to even. A nonzero ratio
of signed i64 magnitudes lies between 2^-63 and 2^63, so its rounded result is
normal and finite. Aligning the numerator to the significand needs at most 117
bits, and doubled remainders also fit u128. There is no approximate operand
conversion or dependency on a floating rounding comparison.

`constant@1` explicitly retains the old separately-rounded division.
`constant@2` uses the new conversion. The single registry supplies the newest
constant version to numeric syntax; parsing a numeric atom now emits an
explicit zero-argument `Apply` term. Existing `ProgramTerm::Constant` and
`OperationRef::constant` still lower to version one, so stored terms and diagrams
retain their old meaning. Both versions use the same source-free Real boundary,
exact value parameter and MergeInputs rule. Constants remain unavailable as
parenthesized Lisp list forms. The IR envelope and history schemas stay v1.

This extends ADR 0044's source-versus-stored-IR compatibility distinction:
reparsing source with a new compiler can change an artifact, while replaying
its pinned operation versions preserves their realizations. Old runtimes
reject version-two operations. Frozen kernel contracts must still refuse
source drift; their pins and old evidence are not rewritten to admit this fix.

## Finite application boundary

The existing Rust `evaluate` / `evaluate_with_differential` APIs retain raw
IEEE replay, including special values where the recorded rule permits them.
New `evaluate_finite` / `evaluate_with_finite_differential` functions apply a
separate policy: reject nonfinite inputs and final values, and, when a Jacobian
is requested, reject every nonfinite final derivative. Their certificate IDs
and scopes name the finite policy without changing recorded operation IDs.
Unused differentials and intermediate values are not certified finite.

PyO3's ordinary evaluation and differentiation entry points now use these
Rust policies, so Python and SciPy callers receive ValueError instead of a
nonfinite numerical result. The existing native `adva run` finite input/output
checks remain in force. Independent SymPy/NumPy numerical adapters retain
their external-library semantics; the finite policy is not an interval or
conditioning guarantee and does not create a theorem or semantic identity.

All three public scalar-bearing IR result types (`EvaluationResult`,
`DifferentialResult`, `Observation::Value`) refuse to serialize nonfinite
numbers. Their valid finite JSON shape is unchanged. Diagnostic replay can
still record special values explicitly as bit strings, as the audit example
does. A structural certificate cannot silently accompany a null scalar.

## JSON transport

The workspace enables serde_json's `float_roundtrip` feature without changing
its pinned version. A regression that previously decoded k28 one ULP low now
matches the independently computed dyadic input exactly, and a native envelope
test checks input bits, product output, and serialized-report bits. This is a
transport correction, not a change to multiplication. Old research reports
remain historical evidence and are not overwritten or retroactively accepted.

## Verification boundary

Rust regressions cover directed unit-neighbor cases, both half-ULP ties, signs,
i64 endpoints, legacy replay, finite policy refusals, scalar versus derivative
overflow, JSON refusal and bit-preserving transport. Python compares 518
literal cases to an independent Fraction oracle and tests nine exact dyadic
log chains, direct PyO3 guards, SciPy refusal and checked IR reload.
These are numerical implementation checks in a finite scope; structural
identity and library proof admission remain independent of floating values.
