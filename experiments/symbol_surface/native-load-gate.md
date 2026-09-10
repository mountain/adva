# Native read-only load gate

Status: **Prepared; execution NotRun**. Direction: Mingli Yuan. Preparation:
ChatGPT. Base: `mountain/adva@91f57d01f94fcd1a2f58cfb59832c263e99315d4`.

## Observed integration

Adva PR #171 is merged, and the outer repository now pins adva-library at
`f0312ca4a109e8ca26cc01cb678750ad889c95be` (library PR #2). This closes the
version-reference integration gap. It does not discharge any of the nine
mathematical/representation obligations in the symbol-surface source.

The next question in the library's `symbol-surface/handoff.json` is whether
the original envelope passes the existing read-only Rust document loader
while retaining its nine frontier annotations. The new integration test
`crates/adva-witness/tests/symbol_surface_load.rs` makes this question directly
reproducible through the existing API; it adds no loader or semantic rule.

## Four checks prepared

1. Load the actual source file through `load_adva_document_v0`, select
   `inspect`, require `Ready`, absent recorded outputs and a `Conditional`
   verification admission with the exact same nine sites. Check that the
   source file bytes remain unchanged.
2. Remove one declaration while retaining the subject site. Require rejection
   by the existing mechanism boundary, not an apparent closure.
3. Supply only one member of the output triple. Require `PartialFrameOutput`.
4. Replace a structure key by a nonempty key with no associated payload.
   Loading is expected to remain conditional. This exposes the deliberate
   boundary: the native loader checks the envelope and mechanism form, not
   the truth, availability or integrity of external mathematical payloads.

The nine native frontier sites are documentary coordinates in this example.
Preserving them is not a native encoding or proof of the nine logical goals.
The in-memory negative controls leave all source and library bytes unchanged.
None of these tests calls an evaluator, game runner, search or native `free`.

## Reproduction and exit

From a checkout containing the source fixture, with the repository's Rust
toolchain and locked dependencies:

```sh
timeout 180s cargo test --locked -p adva-witness --test symbol_surface_load
```

The wall-clock budget includes compilation. A timeout retains Unknown and
requires a fresh finite plan; it does not prove a loader defect. There are
four fixed tests, no search candidates and no automatic retries. No library
submodule is needed by this particular test: it reads the outer source file.

Do not overwrite historical `NotRun` reports if this later passes. Record the
new tested commit, command, four outcomes and actual costs in a successor
receipt. Even a complete pass establishes only the stated loading boundary.

## Current execution evidence

No Rust compiler or Cargo was available in the local environment. These
tests have not been compiled, formatted with rustfmt or executed locally;
their expected results are not observed results.

The existing main CI run
[34422169798](https://github.com/mountain/adva/actions/runs/34422169798)
reports failure for Rust and Python 3.11/3.12/3.13. All four job step lists
are empty, and the retrieved Rust/Python log endpoints returned missing-blob
errors. This does not identify the cause or demonstrate a code-test failure.
No billing, permission or runner diagnosis is asserted without evidence.

Search/evaluation/game operations performed this turn: zero. Native test
runtime and peak memory: unmeasured because NotRun. Research, source review
and network costs are not included in a claimed performance result.

This receipt advances the handoff from an informal next question to a bounded
native check that another authorized executor can run directly. It reports
no peer acknowledgment, newly learned theorem or automatic reciprocal runner.
