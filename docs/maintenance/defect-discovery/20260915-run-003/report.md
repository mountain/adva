# Bounded defect discovery report

Checked: 2026-09-15T15:14:23.030331+00:00
Declared source: `2df905c63e34cd4a607ecc58409b9cda3f15bc34` (not a deployed binary identity).

| Probe | Evidence state | Violations | Upstream submission |
| --- | --- | ---: | --- |
| exp-cross-zero | BoundedPass | 0 | NotEligible: local adapter, no upstream attribution |
| constant-inverse | BoundedPass | 0 | NotEligible: local adapter, no upstream attribution |
| segmented-execution | BoundedPass | 0 | NotEligible: local adapter, no upstream attribution |

## exp-cross-zero

- invariant: exp([-1,1]) encloses exp(-1) and exp(1)
- oracle: Exact series fact exp(1) > 1+1=2; exp(-1)=1/exp(1)
- scope: Helper accepts crossing-zero intervals; retained branch experiment not rerun
- common_mode: CPython integer/Fraction arithmetic and host hardware remain shared
- severity: NoDemonstratedImpact
- impact: Only the declared finite relation and mutations were checked
- next_step: Retain bounded coverage; extend only under a new finite contract
- open_obligations: Retained experiment consumers, deployment, concurrent calls, independent interpreter/compiler/hardware, and upstream applicability remain unverified

Next: validate intended helper domain, minimize, and add a regression before proposing a local fix.

## constant-inverse

- invariant: Constant polynomial c times its truncated inverse equals one
- oracle: Exact reciprocal of a nonzero rational constant; no polynomial inversion oracle
- scope: Helper-level domain extension; frozen x^2+1 experiment is not refuted
- common_mode: CPython/Fraction shared; expected result does not call MPoly arithmetic
- severity: NoDemonstratedImpact
- impact: Only the declared finite relation and mutations were checked
- next_step: Retain bounded coverage; extend only under a new finite contract
- open_obligations: Retained experiment consumers, deployment, concurrent calls, independent interpreter/compiler/hardware, and upstream applicability remain unverified

Next: validate intended helper domain, minimize, and add a regression before proposing a local fix.

## segmented-execution

- invariant: Fuel segmentation preserves endpoint and charged steps; forged receipts rejected
- oracle: Metamorphic relation and explicit receipt field mutations
- scope: Three finite closed terms, four cuts each; no prefix search or native Rust certificate
- common_mode: Both segments and receipt replay share pure_segment; correlated semantic errors escape
- severity: NoDemonstratedImpact
- impact: Only the declared finite relation and mutations were checked
- next_step: Retain bounded coverage; extend only under a new finite contract
- open_obligations: Retained experiment consumers, deployment, concurrent calls, independent interpreter/compiler/hardware, and upstream applicability remain unverified

Next: validate intended helper domain, minimize, and add a regression before proposing a local fix.

## Limits and attribution

NativeReproduced means the actual Python helper ran twice with identical evidence. It does not mean a native Rust certificate, an upstream defect, or deployed-product impact.
A bounded pass does not prove correctness. Clocks enforce a host resource limit; their presence alone is not a mathematical defect. Fraction/CPython and hardware remain shared assumptions.
No Rust/LLVM, kernel, BLAS, FFI, concurrent mutation, filesystem fault injection, or upstream reproducer was executed. Source content hashes and resource limits are in report.json.
Authored by ChatGPT (OpenAI), submitted through Mingli Yuan's GitHub account as an authorized proxy. Account use is not endorsement, review, or a correctness claim.
