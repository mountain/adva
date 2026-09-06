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
different resources. The CLI adds a 2 MiB report serialization ceiling.

## Evidence and costs

Native compilation/execution is not available in this local environment.
The bounded `Native program run` workflow builds the actual Rust executable,
runs focused unit/integration checks, executes both inputs, records phase
timings and GNU time wall/RSS observations, and retains exact tested sources.
Before those results are attached, execution status is **NotRun**, not passed.
Search candidate count is zero. No speedup or learned-vocabulary theorem is
claimed, so no artificial with/without naming benchmark is reported.

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
