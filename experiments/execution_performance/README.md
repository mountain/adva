# Execution cost of the existing bootstrap and first projection

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized GitHub account
proxy. Account ownership is not authorship, review or a correctness guarantee.

The [received measurement and comparison](../../docs/research/execution-performance-comparison.md)
uses `evidence/local-01`; all 78 cases passed. The complete sample distribution
is retained, including variation between runs of identical target code.

Question: does the received self compiler run faster after self compilation,
and how does the existing dynamic residual compare with Rust directly running
the same source instructions and with the Adva subset interpreter?

This measurement receives the frozen v1 compiler and ten fixtures, plus all
eight v0 dynamic-residual programs at inputs 7 and 9. It does not extend either
language or repeat the historical campaigns. The v1 seed is Python, not a Rust
compiler for the structured language. All measured execution uses the unchanged
Rust checked data-machine APIs. PSC0 is a different language and is not treated
as an equivalent integer/control-flow baseline.

The protected observations are return/rejection status and exact returned data;
rejection messages and traces between interpreter and residual are not equated.
The v1 seed/C1/C2 target bytes must agree, structural correspondence must pass,
and C1/C2 execution traces must agree. Each measured case first executes and
passes full native replay, outside timing. Existing frozen negative controls
remain in the associated regression suites. No native semantic identities,
certificates, new specializer or general speed theorem are claimed.

Build and run with a Python environment containing `blake3`:

```sh
cargo build --locked --release -p adva-witness --example execution_performance
python3 -B experiments/execution_performance/run.py \
  --binary target/release/examples/execution_performance \
  --output target/execution-performance-01
```

Use a fresh output directory. The child is pinned to one permitted CPU and is
limited to 600 wall seconds, 540 CPU seconds, 1 GiB address space and 16 MiB per
output file. There is one child process and no retries/resumption. Preparation
only receives fixed bounded archives. Builds and regression tests are separate.
A nonzero exit/timeout retains partial output and supplies no completed timing
claim. There are 78 cases: two self compilations, twenty fixture executions,
eight v0 compilations and forty-eight v0 executions. Each has one untimed
execution and full replay; self compilations have three single-run samples,
others nine batches of 32, 64 or 128 runs. Case order rotates and reverses each
round. The Rust harness caps suite size, iterations and sample count.

Timing includes normal admission, initialization, full trace/state hashing,
internal JSON serialization for the report size check and destruction. It
excludes process startup, input JSON parsing, file I/O, separate replay and
external structural checking. There is no unchecked execution mode. V0 compile
timing also excludes host residual decoding/loading, so it cannot by itself
establish an end-to-end break-even point. Samples are local wall-clock
observations on one shared host, not universal hardware or memory benchmarks.

`suite.json`, per-sample JSONL, environment/binary/source hashes and result JSON
make the comparison inspectable. Retain failed observations as failures; never
discard them to select a more favorable sample.
