# Serialized Open-Line Leaf Request: Positive Prefix, Negative-Control Construction Pause

## Status

Historical result, 2026-10-27: Unknown. Two finite positive receipts executed
and returned `Certified`, but the negative-control phase did not reach its
receiver assertions. This is not a
bridge certificate, a learned word, a theorem, or evidence for arithmetic
universality or universal grammar.

The continuation started from `main`
`03c37587c5c983647f302b6ef49aac6bd000626e` and draft PR #228 head
`03de0353888bc64ad8443cb3c685f1e323b163f1`. Open PR #227 is an independent
finite epistemic-identity proposal and was not used as a dependency. The
`arithmetic-universality` and `hypothesized-arithmetic-truth` words from
Research 0123 remain Proposed.

## Frozen continuation

The continuation contract is
[`experiments/native_input_binding_serialized_leaf_request/continuation-contract-20261027.json`](../../experiments/native_input_binding_serialized_leaf_request/continuation-contract-20261027.json).
It permits only the two `.result` projections required because
`import_diagram_json` returns `DiagramValidationArtifact`, while the caller's
current objects are `SharedProgramDiagram`s. Schema, fixtures, controls and
budgets otherwise remain inherited.

The continuation contract also corrects a documentary inconsistency without
rewriting the inherited contract: the actual serialized-request test uses the
zero-event source `(frontier (use static) (use dynamic))`; the older contract's
`source_body` field accidentally named the unrelated complex `BODY` fixture.

## Executed route

One route, zero search candidates:

1. compare `imported_source.result` and `imported_residual.result` with the
   independently supplied current diagrams;
2. retain canonical JSON equality, exact external-leaf equality and the exact
   qualified native occurrence pair;
3. call the unchanged native receiver with 512 structural work units;
4. retain the 65,536-byte serialized-request limit.

The first execution removed the inherited type mismatch, then Clippy rejected
the research-only receiver's eight explicit boundary arguments. The one
permitted correction replay added a local `clippy::too_many_arguments`
exception with no parameter, schema, budget or semantic change.

On replay, formatting and Clippy passed. Two frozen external leaf tuples then
passed the complete importer and receiver path and returned `Certified`.
This is reuse of the same bounded relation for a second external tuple, not a
new native program-instance reuse result.

## Exact residual

Before the negative assertion loop, Rust eagerly constructed all control
values. The intended valid-but-different source used:

```text
(frontier (copy (use static)) (use dynamic))
```

`copy` produces two outputs, so that body produces three values while the
fixture declares two. Compilation stopped with:

```text
function native-binding/source declares outputs
CodomainFrontier(TypedFrontier([Real, Real])), got [Real, Real, Real]
```

The first three negative values had been formed, but their receiver assertions
had not started. Therefore zero negative controls are counted as Refused. The
byte-budget control also did not execute. The correction allowance was already
consumed, so no further source edit or workflow replay was performed.

## Evidence and costs

- Candidate head:
  [`638caf5`](https://github.com/mountain/adva/commit/638caf52888bce6d4e921fea16221cb89e899e15)
- [bounded-acceptance replay](https://github.com/mountain/adva/actions/runs/40525724730)
- [structured outcome](../../experiments/native_input_binding_serialized_leaf_request/outcome-20261027.json)

Observed work:

- one route and zero search candidates;
- two new serialized receipt calls, both `Certified`;
- 6 diagram-import regressions, 2 graft regressions and all 11 inherited native
  input-binding tests passed before the new test failed;
- first Clippy attempt about 3.9 seconds;
- correction Clippy 7.01 seconds, test build 7.09 seconds, and native test file
  0.02 seconds;
- one correction replay;
- serialized byte counts and peak memory were not reported and are not inferred
  from file size.

Publication-boundary validation passed. The original report stated: "Full CI
and the bounded workflow are red because the new test failed." That attribution
was incorrect. At head `07b70993f504c8e8dd00ec68662f9f75de9071bc`, the
[bounded workflow](https://github.com/mountain/adva/actions/runs/40526045840)
failed at the ill-typed control described above. Independently,
[full CI](https://github.com/mountain/adva/actions/runs/40526045620)
stopped before builds at `scripts/check_research_index.py`: this note and the
import-artifact pause note were missing from the research index, whose header
still declared 64 named notes instead of 66. The Rust and three Python suites
were skipped, not executed and failed. A green publication check is not a
mathematical success claim.

## Vocabulary and utility

No word is formed or revised. Existing terms—validated import artifact,
complete snapshot binding, qualified occurrence, `Certified`, `Refused`, and
`Unknown`—remain sufficient.

For Mingli Yuan and later agents, this run separates three facts that should
not be collapsed: the import-artifact projection is type-correct, two positive
receipts execute, and the rejection boundary is still unverified because its
control generator is ill-typed. This prevents a positive prefix from being
reported as a complete receiving contract. No measured value to Jiamin Zhao's
real work is claimed.

## Smallest continuation

Replace only the ill-typed control body with a different valid two-output body,
for example `(frontier (id (use static)) (use dynamic))`. Keep the complete
request grammar, both positive tuples, all seven rejection expectations, byte
and structural budgets, and receiver unchanged. Execute the same bounded
workflow once. If it passes, record exact assertion counts and any measurable
serialization or memory costs; otherwise retain the next exact residual as
Unknown.

## Separately bounded continuation, 2026-10-28

The [new finite contract](../../experiments/native_input_binding_serialized_leaf_request/continuation-contract-20261028.json)
does not reset or rewrite the exhausted 2026-10-27 continuation. Its only
executable change replaces the three-output `copy` control with
`(frontier (id (use static)) (use dynamic))`: the same two-output boundary,
but a different complete source diagram. The receiver, schema, both positive
tuples, seven refusal expectations, byte-budget control and budgets remain
unchanged. The two existing notes are indexed, and the incorrect full-CI
attribution is corrected above with the original statement retained.

At contract preparation, the new execution result is pending. Prior failures,
the original contract and `outcome-20261027.json` remain frozen. Any subsequent
result must identify its own exact source bytes and executed checks; merging
the engineering correction is not promotion to a stable schema, a general
external/native bridge, or an arithmetic-universality claim.

The first local focused execution on 2026-10-28 passed with Rust 1.99.1:
published/staged formatting, locked Clippy, 12 native input-binding tests,
6 diagram-validation tests, 2 graft tests and 19 process tests. The serialized
test now reaches all 2 `Certified`, 7 exact `Refused` and 1 byte-budget `Unknown`
assertions. Research-index preflight and the combined index/Bootstrap Zero
suite passed (1,121 tests), as did the existing Python lint/format checks.
The candidate source SHA-256 is
`60ceaacdd398f83b10772ac6eae45eb61be4206b892bf414d63deef92b1efcea`.
These are local finite results, not a claim that remote integration has passed.

Continuation and correction authored by ChatGPT (OpenAI), submitted through
Mingli Yuan's GitHub account as an authorized proxy. Original first-party work
contributed under Unknown v0.3; account use is not his authorship, review,
endorsement or a correctness guarantee.
