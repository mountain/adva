# First Futamura-style observation

Direction: Mingli Yuan. Design, construction, execution and record:
deepseek-v4-flash-vision-exp (DeepSeek Harness), through his account as an
authorized proxy; not his authorship, review, endorsement or guarantee.

`contract.json` freezes the question, the source family, the observation policy, the
residual encoding, the checker and the finite budget. The calibration compiles the
129 frozen regular arithmetic trees with a compiler built from the frozen interpreter
by a declared rule, instantiates every emitted residual and executes it directly, and
compares interpreter, residual and an independent recursive oracle.

For a new, explicitly bounded attempt into a fresh directory, after building the
binary:

```sh
python3 -B experiments/futamura_first_projection/check.py \
  --binary target/debug/adva \
  --interpreter programs/bounded-interpreter/interpreter.adva \
  --archive experiments/bounded_native_interpreter/evidence/attempt-1/primary.tar.gz \
  --output /tmp/adva-futamura-attempt-1
```

The checker writes every program, input and run under `raw/`, archives them into
`attempt.tar.gz` after verifying every member digest, and keeps `compiler.adva`,
`results.json` and every emitted residual loose. It refuses to write into a non-empty
directory, launches at most 512 CLI calls, and exits non-zero when any case
disagrees.

`evidence/attempt-1` holds the completed attempt: 129 trees, 387 launches, 1,161
archived files, verdict Passed. The regression test
`tests/python/test_futamura_first_projection.py` receives the record and rebuilds the
compiler from the frozen interpreter; it launches nothing.

The theory this instantiates, the projection statements in this repository's terms,
and the measured reasons projections two and three are blocked today are in
[the note](../../docs/research/futamura-projections-in-adva-terms.md).
