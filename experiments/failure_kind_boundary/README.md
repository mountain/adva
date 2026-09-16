# Failure-kind boundary calibration

This project-original finite experiment continues Research 0090 and Research
0204. It distinguishes a checker implementation failure from a semantic
counterexample while binding and preserving the same object, early history and
unresolved set.

Run:

```console
timeout 65s python -B -S experiments/failure_kind_boundary/supervise.py \
  --output-dir /tmp/adva-failure-kind
```

The two fixed families, types, acceptance conditions and budgets are frozen in
`contract.json`. The receiver does no search. A counterexample must name an
event that the receiver independently checks against the bound finite machine.
An implementation-failure receipt may name a phase and bounded failure code,
but it may not contain or imply a semantic conclusion.

All code, prose, fixtures and generated evidence in this directory are original
to this contribution and are contributed under Unknown v0.3. No external
content is incorporated.

Direction: Mingli Yuan. Implementation, argument and review: ChatGPT (OpenAI),
submitted through his account as an authorized proxy; not his authorship,
review, endorsement or correctness guarantee.
