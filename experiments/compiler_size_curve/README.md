# Compiler size curve and the bootstrapping budget

Direction: Mingli Yuan. Design, construction, execution and record:
deepseek-v4-flash-vision-exp (DeepSeek Harness), through his account as an
authorized proxy; not his authorship, review, endorsement or guarantee.

`contract.json` freezes the question, the declared lowering, the generated grid, the
reference implementation and the finite budget. The calibration generates a compiler,
written in the research data-machine language, for each declared source shape;
measures its instruction count against the bound of 128; and for every shape that fits,
compiles its whole declared family, instantiates each residual and executes it directly
against an independent host-side reference implementation.

For a new, explicitly bounded attempt into a fresh directory, after building the
binary:

```sh
python3 -B experiments/compiler_size_curve/check.py \
  --binary target/debug/adva \
  --output /tmp/adva-compiler-curve-attempt-1
```

The checker writes every program, input and run under `raw/`, archives them into
`attempt.tar.gz` after verifying every member digest, and keeps `curve.json`,
`ceiling-compiler.adva`, the generated compilers, every emitted residual and
`results.json` loose. It refuses to write into a non-empty directory, launches at most
256 CLI calls, and exits non-zero when any case disagrees.

`evidence/attempt-1` holds the completed attempt: ten generated shapes, 28 executed
cases, 43 launches, verdict Passed. The regression test
`tests/python/test_compiler_size_curve.py` receives the record and regenerates the
compilers; it launches nothing.

The curve, its marginal costs and what it implies for bootstrapping are recorded in
[the note](../../docs/research/compiler-size-curve-and-bootstrapping-budget.md).
