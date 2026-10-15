# One frozen Metamath proof-step language in Adva

The program uses existing `data-run-v1` instructions. It implements single-variable
token-string substitution, type and active-hypothesis checks, a proof stack of
depth four, and explicit refusals. It is a research calibration over the
[original fixed toy database](../../experiments/bounded_metamath_step/database.mm),
not a `.mm` parser or a general proof verifier.

```sh
cargo build --locked -p adva-witness --bin adva
target/debug/adva data-run-v1 programs/bounded-metamath-step/checker.adva \
  --input programs/bounded-metamath-step/input.json \
  --fuel 8192 --quantum 8192 --output target/mm-step-example.adva
```

Use a new output path. The supplied proof labels are `fq neg dup`; the expected
return is `|- ~ q ~ q`. All stack changes, token copies and comparisons appear
in the native trace. The authoring script is not loaded during execution.

Read the [contract](../../experiments/bounded_metamath_step/contract.json),
[cases](../../experiments/bounded_metamath_step/cases.json) and
[results with explicit limitations](../../docs/research/bounded-metamath-proof-step-v0.md).
`instruction-labels.json` maps authoring labels to bytecode positions for review.

Codex (OpenAI), Unknown v0.3, through Mingli Yuan's authorized account proxy;
not his authorship, review or correctness guarantee.
