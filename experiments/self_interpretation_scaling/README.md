# Bounded self-interpretation scaling preflight

Direction: Mingli Yuan. Design, implementation and record:
deepseek-v4-flash-vision-exp (DeepSeek Harness), through his account as an
authorized proxy; not his authorship, review, endorsement or guarantee.

`contract.json` freezes the question, the declared subset, the cases, the checker
and the finite budget. The preflight generates meta programs that interpret object
programs of a declared subset of this machine's own instruction grammar, executes
the ones that fit the declared 128-instruction bound, and submits the ones that do
not. It changes no machine byte, adds no operation, widens no bound and starts no
search.

For a new, explicitly bounded attempt into a fresh directory, after building the
binary:

```sh
python3 -B experiments/self_interpretation_scaling/check.py \
  --binary target/debug/adva \
  --output /tmp/adva-scaling-attempt-1
```

The checker writes every generated meta program, object bundle, run and refusal into
the output directory, plus `results.json`. It refuses to write into a non-empty
directory, launches at most 24 CLI calls, and exits non-zero when any declared
expectation fails. Runtime refusals are expected outcomes; their reason is read from
the retained run report, because the CLI prints one generic line for them.

`evidence/attempt-1` holds the completed attempt: 43 files, 11 launches. The
regression test `tests/python/test_self_interpretation_scaling.py` receives that
record and rebuilds the length model from the generator; it launches nothing.

What the attempt established, and what it did not, is recorded in
[the scaling note](../../docs/research/self-interpretation-scaling-preflight.md),
next to the [capacity preflight](../self_interpretation_capacity/README.md) it
follows.
