# First projection with dynamic residuals

Direction: Mingli Yuan. Design, construction, execution and record:
deepseek-v4-flash-vision-exp (DeepSeek Harness), through his account as an
authorized proxy; not his authorship, review, endorsement or guarantee.

`contract.json` freezes the question, the source subset, the compiler rule, the
observation, the cases and the finite budget. The calibration compiles all eight
source programs of the declared subset with a 41-instruction compiler written in the
same language, instantiates every emitted residual and executes it directly on the
dynamic value, and checks that values **and refusals** agree with interpretation.

For a new, explicitly bounded attempt into a fresh directory, after building the
binary:

```sh
python3 -B experiments/futamura_dynamic_residual/check.py \
  --binary target/debug/adva \
  --output /tmp/adva-dynamic-residual-attempt-1
```

The checker writes every program, input and run under `raw/`, archives them into
`attempt.tar.gz` after verifying every member digest, and keeps `interpreter.adva`,
`compiler.adva`, `results.json` and every emitted residual loose. It refuses to write
into a non-empty directory, launches at most 96 CLI calls, and exits non-zero when any
case disagrees.

`evidence/attempt-1` holds the completed attempt: eight source programs, two dynamic
values each, 40 launches, verdict Passed. The regression test
`tests/python/test_futamura_dynamic_residual.py` receives the record, regenerates the
compiler and re-decodes every residual; it launches nothing.

The measurement, its limits and its place in the projection ladder are in
[the note](../../docs/research/futamura-dynamic-residual-calibration.md), next to the
[static first-projection calibration](../futamura_first_projection/README.md).
