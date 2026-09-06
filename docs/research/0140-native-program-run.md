# Research 0140: execute native Adva before host repetition

The first engineering dependency is a runnable Adva program on the existing
Rust kernel. Main `57c1d04bcfe51b82f6e559a61ca02e668f630b5a` already contains
the parser/compiler/evaluator and several research commands. Draft #136 adds
one particular native learn recipe; draft #139 stages two Pascal proposal
files and a Python supervisor with no actual native phase launches. None of
those drafts is merged. This change starts from main and does not claim their
proposals are available native methods.

## Frozen task and implementation

See `0140-native-program-run-contract.json` and ADR 0035. One route, no search:
execute a restricted existing PSC0 program from a strict `.adva` envelope.
The expression `x + y*z` is deliberately easy, leaving resources for checking
the input/compilation/result boundary. The selected inputs are (2,3,4) and the
fresh reuse instance (5,2,3). Required values are 14 and 11 respectively.

`adva run` resolves existing Rust operations through the existing registry.
The report retains the program, complete compilation artifact, evaluation
result, source/occurrence history, certificates, limits and phase costs.
Unknown schema, unsupported calls, excess source/depth/terms/copy/fuel, invalid
linearity and nonfinite results are explicit refusals. No native diagram can
be authorized merely by deserializing an externally supplied report.

## Reproduction

```sh
cargo build --release -p adva-witness --bin adva
target/release/adva run programs/native-run/arithmetic.adva --output target/arithmetic-result.adva
target/release/adva run programs/native-run/reuse.adva --output target/reuse-result.adva
cargo test -p adva-witness --lib native_run
cargo test -p adva-witness --test native_run_cli
```

Choose new output paths for replay; existing evidence is not overwritten.
For a five-second Linux process boundary, prefix a run with `timeout 5` and
use `ulimit -v 524288`. AST admission fuel and these host limits measure
different resources. The CLI adds a 2 MiB report serialization ceiling. Oversized input reports
count the bounded prefix read, not the complete file size. The regular-file
check follows open; the external process deadline also bounds a blocking path.
The current finite-output check covers inputs and final values, not every
intermediate value that the existing evaluator might later discard.

## Evidence and costs

Native execution completed in [workflow 34039297072](https://github.com/mountain/adva/actions/runs/34039297072),
job 101503009574, using Rust 1.98.1. Clippy passed. Seven unit methods and seven
actual CLI integration tests passed; two additional release invocations returned
14 and 11. The full reports and GNU time records are in `0140-native-run-evidence/`;
`0140-native-program-evidence.json` records hashes, tested sources, counts and costs.
The original generic CI Rust job stopped at formatting; its Python matrices and
arithmetic vocabulary checks passed. The formatter output is the exact source
that the successful native workflow compiled and tested, and is retained here.

Each positive program used five of sixteen AST admission units and evaluated
two operation nodes. Internal elapsed time before serialization was 0.173834 ms
and 0.127878 ms respectively. External process peak RSS was 4080 and 4228 KiB.
GNU time displayed wall time as `0:00.00`, which is rounded, not literally zero.
Release build reported 1m 21s; test-build costs are recorded separately. Native
unit and CLI test execution reported 0.01s and 0.02s. Serialization/publication
costs separately, total engineering time and whole-workflow peak memory were not
measured. Report sizes are storage sizes, never peak-memory measurements.

Search candidate count is zero; no semantic implementation repair or experiment
replay was needed. Formatting retention does not add a new mathematical run.
No speedup or learned-vocabulary theorem is claimed, so no artificial with/without
naming benchmark is reported. Native execution takes priority over draft #139's
later Python repetition; this result is not a six-step learning experiment.

## Use and remaining obligations

Mingli and subsequent agents get a concrete native entry point and a report
that distinguishes execution, rejection and filesystem failure. This removes
the missing execution dependency in later orchestration work. It does not yet
provide demonstrated value for Jiamin's practical task.

The existing Real backend is numerical f64. These small integer fixtures have
representable results, but their execution certificates do not prove exact
rational identities. Native exact Pascal checking, method-level resource
accounts for `learn`/`free`, communication acceptance, and self-interpretation
remain separate unfinished obligations. The two Pascal JSON proposal schemas
remain unsupported input for this command. `unknown-syntax-building` remains
paused. No new vocabulary theorem is formed.

Next smallest dependency: specify and wire one native method dispatch with
checked input/output and a persistent resource account, then make the Python
six-call supervisor invoke that exact implementation. Do not substitute six
independent arithmetic executions for six stateful learning steps.
