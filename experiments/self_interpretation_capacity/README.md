# Bounded self-interpretation capacity preflight

Direction: Mingli Yuan. Design, implementation and record:
deepseek-v4-flash-vision-exp (DeepSeek Harness), through his account as an
authorized proxy; not his authorship, review, endorsement or guarantee.

`contract.json` freezes the question, the declared bounds, the cases, the checker
and the finite budget. The preflight asks one thing: inside the already declared
research data-machine bounds, is there room for an inspectable representation of
the machine's own instruction language and for dispatch over it? It changes no
machine byte, adds no operation, widens no limit and starts no search.

For a new, explicitly bounded attempt into a fresh directory, after building the
binary:

```sh
python3 -B experiments/self_interpretation_capacity/check.py \
  --binary target/debug/adva \
  --object-program programs/bounded-interpreter/interpreter.adva \
  --output /tmp/adva-capacity-attempt-1
```

The checker writes every generated program, input, run and stderr into the output
directory, plus `encoding-count.json` and `results.json`. It refuses to write into
a non-empty directory, launches at most 24 CLI calls, and exits non-zero when any
declared expectation fails. Refusals are expected outcomes here and are retained.

`evidence/attempt-1` holds the completed attempt: 47 files, 12 launches. The
regression test `tests/python/test_self_interpretation_capacity.py` receives that
record and recomputes the encoding count from the unchanged object program; it
launches nothing.

What the attempt established, and what it did not, is recorded in
[the preflight note](../../docs/research/self-interpretation-capacity-preflight.md).
