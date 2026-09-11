# Symbol-surface native load: one version-bound advance

This profile answers the next minimal question in the library's
`symbol-surface/handoff.json`: can the unchanged envelope pass the existing
Rust document loader, preserving its nine open frontier annotations?

The completed first run and its interpretation are recorded in
[RESULTS.md](RESULTS.md); [reply.json](reply.json) binds the response to
the exact incoming handoff and its retained native result.

The source boundary is adva `91f57d0`, library `f0312ca`, and PR 170's eight
archived files. The exact handoff and the prior byte-observer receipt are
both pinned. [contract.json](contract.json) fixes all input hashes, eight
native load calls, eight controls, finite limits and exit conditions before
execution. The original `byte-observer-v0` profile remains unchanged.

**Contract successor, and what a frozen replay would now do.** The active
contract is [contract-v1.json](contract-v1.json), which supersedes
`contract.json` by digest and states two moved inputs instead of rewriting it: the
symbol-surface README pin, after the unearned game label was withheld, and the
base commit, because this profile requires that nothing under `Cargo.toml`,
`Cargo.lock` and `crates` has changed since it. The run-01 evidence below keeps
the frozen version-zero contract and its original digests as the record of what
that run actually executed, so a literal replay of run-01 now fails on the README
pin **by design rather than by drift**: an input changed after that run. Use the
successor, and read `supersedes.note` in it for the reasoning.

The new outer profile invokes existing code: it builds the Rust/PyO3 extension
offline, copies the fresh library to its evidence directory and directly loads
that artifact. `load_adva_document_json` calls `load_adva_document_v0` in Rust.
No Rust semantic code or operation registry is modified, and no installed
Python extension is replaced. The outer Python checks byte bindings and the
returned protocol; it does not issue the load certificate.

Eight finite calls load the original, the library copy, the same original
again, three structurally invalid envelopes, an invalid entrypoint, and the
same envelope with no external payload files. The last control makes explicit
that the native loader checks the document's cache-coordinate strings without
resolving or proving the external payload. Separately, the outer SHA256 check
must reject altered payload bytes. Source files and historical statuses are
never rewritten.

Run once under the frozen contract, with a fresh output directory:

```sh
timeout 190s python3 python/adva/adva.py advance \
  --profile symbol-surface-load-v0 \
  --output target/advance-symbol-surface-20260910-01
```

The 180-second account includes preflight, all child processes, rebuilding,
controls, source copying, inventory and checkpoint checks. A 190-second outer
timeout provides the final host limit. Hard termination or storage failure can
prevent a completed checkpoint; partial files remain. No automatic retries or
next round are performed. Authoring, engineering tests and later integrity
checks are outside the experiment timing.

Success is `VariationObserved` with `NativeEnvelopeLoaded`, a ready frame,
conditional verification formation, nine remaining frontier annotations and
no recorded outputs. This is a new native load result, not mathematical proof,
mechanism execution, new knowledge epoch, `free`, or a Rust Seal. The frontier
coordinates index the external annotations and are not a native encoding of
the mathematical tasks listed there.

Engineering checks, separate from the actual trial:

```sh
.venv/bin/python -m pytest -q tests/python/test_advance_surface_boundary.py \
  tests/python/test_advance_boundary.py tests/python/test_persistence.py \
  tests/python/test_math_catalog.py
```

The complete 54-file run is retained under [`evidence/run-01/`](evidence/run-01/).
The executed shared library is losslessly gzip-compressed; the manifest records
both original and stored byte lengths and SHA256 hashes. All other files are
unchanged byte copies, including the original report and implementation snapshots.
Historical absolute paths remain as recorded. Verify the archive without loading
the shared library or restarting the experiment:

```sh
python3 experiments/advance_symbol_surface/verify_evidence.py
```
