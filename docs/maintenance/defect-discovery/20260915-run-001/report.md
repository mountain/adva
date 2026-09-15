# Bounded defect discovery report

Checked: 2026-09-15T14:19:13.061802+00:00
Declared source: `20ff8a77ab45aa8388ee1058cad21faaeb07d16f` (not a deployed binary identity).

| Probe | Evidence state | Violations | Upstream submission |
| --- | --- | ---: | --- |
| exp-cross-zero | NativeReproduced | 1 | NotEligible: local adapter, no upstream attribution |
| constant-inverse | NativeReproduced | 8 | NotEligible: local adapter, no upstream attribution |
| segmented-execution | BoundedPass | 0 | NotEligible: local adapter, no upstream attribution |

## exp-cross-zero

- invariant: exp([-1,1]) encloses exp(-1) and exp(1)
- oracle: Exact series fact exp(1) > 1+1=2; exp(-1)=1/exp(1)
- scope: Helper accepts crossing-zero intervals; retained branch experiment not rerun
- common_mode: CPython integer/Fraction arithmetic and host hardware remain shared

Counterexample: `cross-zero`
```json
{
  "actual": [
    "1",
    "1359140914229522623116063096221826380556539287/500000000000000000000000000000000000000000000"
  ],
  "expected": "lo < 1/2 and hi > 2 (necessary enclosure conditions)",
  "inputs": [
    "-1",
    "1"
  ],
  "name": "cross-zero",
  "verdict": "Violation"
}
```

Next: validate intended helper domain, minimize, and add a regression before proposing a local fix.

## constant-inverse

- invariant: Constant polynomial c times its truncated inverse equals one
- oracle: Exact reciprocal of a nonzero rational constant; no polynomial inversion oracle
- scope: Helper-level domain extension; frozen x^2+1 experiment is not refuted
- common_mode: CPython/Fraction shared; expected result does not call MPoly arithmetic

Counterexample: `constant--1-order-1`
```json
{
  "actual": {
    "0,0": "1"
  },
  "expected": {
    "0,0": "-1"
  },
  "inputs": {
    "constant": "-1",
    "nvars": 2,
    "order": 1
  },
  "name": "constant--1-order-1",
  "verdict": "Violation"
}
```

Counterexample: `constant--1-order-2`
```json
{
  "actual": {
    "0,0": "1"
  },
  "expected": {
    "0,0": "-1"
  },
  "inputs": {
    "constant": "-1",
    "nvars": 2,
    "order": 2
  },
  "name": "constant--1-order-2",
  "verdict": "Violation"
}
```

Counterexample: `constant-2-order-1`
```json
{
  "actual": {
    "0,0": "1"
  },
  "expected": {
    "0,0": "1/2"
  },
  "inputs": {
    "constant": "2",
    "nvars": 2,
    "order": 1
  },
  "name": "constant-2-order-1",
  "verdict": "Violation"
}
```

Counterexample: `constant-2-order-2`
```json
{
  "actual": {
    "0,0": "1"
  },
  "expected": {
    "0,0": "1/2"
  },
  "inputs": {
    "constant": "2",
    "nvars": 2,
    "order": 2
  },
  "name": "constant-2-order-2",
  "verdict": "Violation"
}
```

Counterexample: `constant-3-order-1`
```json
{
  "actual": {
    "0,0": "1"
  },
  "expected": {
    "0,0": "1/3"
  },
  "inputs": {
    "constant": "3",
    "nvars": 2,
    "order": 1
  },
  "name": "constant-3-order-1",
  "verdict": "Violation"
}
```

Counterexample: `constant-3-order-2`
```json
{
  "actual": {
    "0,0": "1"
  },
  "expected": {
    "0,0": "1/3"
  },
  "inputs": {
    "constant": "3",
    "nvars": 2,
    "order": 2
  },
  "name": "constant-3-order-2",
  "verdict": "Violation"
}
```

Counterexample: `constant-1/2-order-1`
```json
{
  "actual": {
    "0,0": "1"
  },
  "expected": {
    "0,0": "2"
  },
  "inputs": {
    "constant": "1/2",
    "nvars": 2,
    "order": 1
  },
  "name": "constant-1/2-order-1",
  "verdict": "Violation"
}
```

Counterexample: `constant-1/2-order-2`
```json
{
  "actual": {
    "0,0": "1"
  },
  "expected": {
    "0,0": "2"
  },
  "inputs": {
    "constant": "1/2",
    "nvars": 2,
    "order": 2
  },
  "name": "constant-1/2-order-2",
  "verdict": "Violation"
}
```

Next: validate intended helper domain, minimize, and add a regression before proposing a local fix.

## segmented-execution

- invariant: Fuel segmentation preserves endpoint and charged steps; forged receipts rejected
- oracle: Metamorphic relation and explicit receipt field mutations
- scope: Three finite closed terms, four cuts each; no prefix search or native Rust certificate
- common_mode: Both segments and receipt replay share pure_segment; correlated semantic errors escape

Next: validate intended helper domain, minimize, and add a regression before proposing a local fix.

## Limits and attribution

NativeReproduced means the actual Python helper ran twice with identical evidence. It does not mean a native Rust certificate, an upstream defect, or deployed-product impact.
A bounded pass does not prove correctness. Clocks enforce a host resource limit; their presence alone is not a mathematical defect. Fraction/CPython and hardware remain shared assumptions.
No Rust/LLVM, kernel, BLAS, FFI, concurrent mutation, filesystem fault injection, or upstream reproducer was executed. Source content hashes and resource limits are in report.json.
Authored by ChatGPT (OpenAI), submitted through Mingli Yuan's GitHub account as an authorized proxy. Account use is not endorsement, review, or a correctness claim.
