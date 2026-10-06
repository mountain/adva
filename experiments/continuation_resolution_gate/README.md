# Continuation resolution gate

This project-original finite experiment binds one Research 0252
terminal-resolution receipt to one exact canonical tuple containing a problem,
history and cumulative natural-number budget.

`ContinuationReady` is returned only when the selected query binds both input
byte strings, the history binds the receipt, the parent result is
`ResolutionVerified`, and the problem's attempt, pair and allowed terminal
state agree. It is a local receiver outcome, not framework `accept`, launch
permission or native authority.

Unknown and invalid paths keep the input file bytes unchanged, return zero fuel
delta and grant no effect, retry, refund, mutation, native or `free` authority.
The supervisor and receivers run under `python -O`, use explicit rejection
rather than `assert`, and form new evidence with write-new same-directory
atomic replacement plus file and directory synchronization.

The first attempt is retained under `evidence/attempt-1`: the receiver correctly
rejected an undeclared budget field, while the supervisor incorrectly required
that rejected object to round-trip as a parsed tuple. The sole correction replay
is `evidence/attempt-2`; `evidence/summary.json` accounts for both attempts.

Reproduce the retained semantic cases into a new directory:

```sh
python -O experiments/continuation_resolution_gate/run.py \
  --output /tmp/adva-continuation-resolution-gate
```

This does not prove power-loss durability, authentication, hostile-process
containment, distributed consistency, exactly-once execution, arithmetic
universality, M6 closure or a native Adva continuation operation.

Authored by ChatGPT (OpenAI), contributed under Unknown v0.3 through Mingli
Yuan's authorized GitHub account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee.
