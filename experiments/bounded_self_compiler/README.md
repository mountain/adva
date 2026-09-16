# Bounded structured self compiler

This experiment builds and receives a compiler written in the same structured
Adva research subset that it compiles. See the [report and complete Futamura
contracts](../../docs/research/bounded-self-compiler-and-futamura.md) and
[ADR](../../docs/adr/bounded-self-compiler-research.md). The language and capacities
are separate from stable PSC0 and the frozen research v0 arithmetic interpreter.

The source language adds `Seq`, `If` and `While` to generic typed data-machine v1
primitives. It excludes raw jump/branch source instructions. The compiler
calculates their concrete target addresses. Use an explicit final `return` or
`reject` primitive outside structured controls; target admission still rejects
out-of-range generated exits and other invalid targets. `compiler.source.adva` is the actual
source; `author.py` only reproduces that file. `language.py` provides the external
seed and a separate wire codec. Native compilation uses neither the seed nor the
authoring script.

Reproduce a single explicit self compilation with fresh output paths:

```sh
cargo build --locked --release -p adva-witness --bin adva
./target/release/adva data-run-v1 \
  programs/bounded-self-compiler/compiler.seed.adva \
  --input programs/bounded-self-compiler/compiler.input.json \
  --fuel 200000 --quantum 200000 --output target/self-compiled.run.adva
```

The returned phase contains the complete target module as ordinary data. For
structural decoding and a correspondence receipt, use the small reusable CLI:

```sh
python experiments/bounded_self_compiler/compile.py \
  programs/bounded-self-compiler/compiler.source.adva \
  --compiler programs/bounded-self-compiler/compiler.seed.adva \
  --binary target/release/adva --output target/self-compiled
```

This explicitly requested compilation has its own fixed, bounded invocation;
it does not rerun the historical research campaign or refill a checkpoint.
The output directory must be new. It retains source, compiler, encoded input,
run, target, native admission receipt and structural compilation receipt.

`contract.json` freezes the original experiment; `contract-v1.json` records the
replacement contract after the retained attempt-1 mutation-visitor failure.
Successful successor evidence, when received, is at `evidence/attempt-2`. `supervise.py` permits one
primary/fresh pair into a new evidence directory, snapshots all source bytes and
verifies the byte-complete archives before removing its raw copies. Do not launch
it as an automatic retry. Historical evidence is received by `regression.py` and
`native_receive.py`; CI does not perform another exploratory campaign.

Preflight 1 stopped on a missing `blake3` import before Adva ran. Preflight 2
received self compilation. Preflight 3 exposed an experiment-harness error: the
CLI's documented-by-implementation rejection exit code is 2, while the harness
incorrectly expected 1. The correct native overflow rejection and the wrong
harness source are retained. Preflight 4 passed all ten fixture controls after
that correction. The native VM and compiler were unchanged by this fix. Full attempt 1 then
failed because the mutation visitor received a module instead of its body. Its
complete archive is retained. The v1 mutation preflight checks that changing the
compiler source changes emitted target code and causes the independent decoder
to refuse a malformed generated branch.

The checks are authored by ChatGPT (OpenAI), through Mingli Yuan's authorized
GitHub account proxy. Independently implemented checks do not imply independent
human review. Full second/third Futamura projections and a general self-applicable
specializer remain Open.
