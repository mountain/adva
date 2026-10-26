# Exact open-line leaf labels do not repin a native input-binding request

Date: 2026-10-25. Status: bounded finite refusal boundary checked on draft
PR 226; not merged. Baseline `main` was
`2154b3c6716e7b5a19b98b81aca7940c0c93fe7d`, and the tested branch head was
`ae6d76354385dcfc68394413d1c71396e26e7ee6`.

This record is project-original work by ChatGPT (OpenAI), submitted through
Mingli Yuan's authorized GitHub account proxy. It is not his authorship,
review, endorsement or correctness guarantee. It is contributed under Unknown
v0.3 and imports no external expression or payload.

## Dependency and claim boundary

Merged `main` already contains the finite open-line formation chain through PR
225. Draft PR 226 contains the later finite thread-order and renaming work;
draft PR 227 is a separate finite positivity and epistemic-identity model. The
current change extends PR 226 and remains unmerged.

Research 0090's general coverage obligation remains open, so Research 0092
promotion remains blocked. Research 0123's `arithmetic-universality` and
`hypothesized-arithmetic-truth` remain Proposed. The present fixture uses
`Rational::ONE` only as the already existing static input to one native
input-binding test. It does not identify multiplicative unity with additive
zero and makes no arithmetic-universality judgment.

## Frozen question

The contract froze one route, zero search candidates, two exact external leaf
substitutions and at most one correction replay. It asked whether the current
private Rust research receiver could accept either correspondence merely by
changing `SourceId` and `OccurrenceId` labels in a cloned certificate:

- `s-KX-L/o-KX-L` to
  `open-reuse-s-KX-L/open-reuse-o-KX-L`;
- `s-tK-R/o-tK-R` to
  `open-reuse-s-tK-R/open-reuse-o-tK-R`.

The native positive control was the minimal zero-event source
`(frontier (use static) (use dynamic))` at `Rational::ONE`. Its
`ExpectedRequest` independently retained the complete native source snapshot,
residual context and static value. The test was not permitted to design a new
serialized request, reconstruct Rust identity in Python or modify a native
diagram to carry the external names.

## Result

The unmodified certificate was `Certified`. The fixture had exactly one mapped
dynamic occurrence. Changing only that occurrence's proposed source and local
occurrence labels, on both the source and residual sides, caused each declared
external leaf to be exactly:

```text
Refused("qualified source occurrence mismatch")
```

The refusal happens before a changed proposal can repin the caller's native
source snapshot. It therefore establishes a small negative boundary: exact
project-local string labels are not a substitute for the native receiver's
qualified source occurrence. The second leaf reuses the same boundary on a
different exact open-line occurrence rather than expanding the grammar.

This is not an impossibility result. A future bridge may be constructible, but
it must provide more than label equality: at minimum, a validated native
`SharedProgramDiagram`, qualified context and complete source/occurrence/path
mapping selected against an independent request. The existing certificate and
request structs remain private research objects, not a public or stable schema.

No new word was required. Existing `QualifiedOccurrence`, `ExpectedRequest`,
`Certified` and `Refused` already express the tested distinction. The result
does not construct `Close`, native `free`, an M6 filler, unrestricted
alpha-equivalence, Research 0090 coverage, Research 0092 promotion, arithmetic
truth or arithmetic universality.

## Execution and cost

GitHub Actions bounded-acceptance run
[`40204251184`](https://github.com/mountain/adva/actions/runs/40204251184)
used Rust 1.99.1. Published-source `rustfmt`, locked `clippy` and the selected
locked tests all passed. Clippy reported 5.53 seconds; the test build reported
6.29 seconds. The new test passed within the native certificate binary's 11
tests in 0.02 reported seconds. Across the four selected test binaries, 38
tests passed and none failed, with 0.21 seconds as the sum of their reported
test times. The native job occupied approximately 32.33 wall seconds including
checkout, toolchain and cache work.

The new test made three receiver calls: one positive control and two refusals,
each supplied 512 structural work units. The private counter does not expose
remaining work, so actual consumed receiver units are not measured. Peak and
concurrent memory were not reported; file sizes are not used as a memory proxy.
Search, candidate generation and arithmetic evaluation costs were zero.
The frozen contract is 3,490 bytes, the canonical execution record is 3,445
bytes and this report is 6,843 bytes before its final commit. Serialization
time was not measured separately.

The first workflow run,
[`40204075359`](https://github.com/mountain/adva/actions/runs/40204075359),
stopped at `rustfmt --check` before compilation. It requested only mechanical
tuple and assignment compaction. That failure is retained as
`FormattingFailureBeforeCompilation`; the sole allowed correction replay made
those changes and is the successful run above. There was no second correction.

## Replay

In a fresh isolated checkout with the existing locked Rust dependencies:

```console
rustfmt --edition 2024 --check experiments/native_input_binding_certificate/native_input_binding_certificate.rs
test ! -e crates/adva-lisp/tests/native_input_binding_certificate.rs
cp experiments/native_input_binding_certificate/native_input_binding_certificate.rs \
  crates/adva-lisp/tests/native_input_binding_certificate.rs
cargo clippy --locked -p adva-lisp --test native_input_binding_certificate -- -D warnings
cargo test --locked -p adva-lisp --test native_input_binding_certificate \
  --test process --test graft_trace --test diagram_validation
```

The frozen input, exact outcomes, workflow coordinates and missing measurements
are recorded in
`experiments/native_input_binding_open_line_leaf/evidence/execution.json`.

## Use and next obligation

This helps Mingli and later agents avoid silently turning external string
coordinates into Rust semantic identities when handing a witness across the
open-line/native boundary. It also tells a future implementer exactly what is
missing rather than treating refusal as a failed theorem. Practical value for
Jiamin Zhao's real tasks remains unmeasured.

The smallest next step is to specify, without yet promoting it, one versioned
serialized request that contains a complete native diagram and qualified
occurrence mapping, then ask the existing native importer and receiver to
validate that request read-only. It must retain `Unknown` or `Refused` on any
diagram, context, path or source-binding mismatch and must not fall back to
Python identity reconstruction.
