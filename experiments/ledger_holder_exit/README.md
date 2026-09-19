# Bounded ledger holder exit

This original external test harness closes one explicitly pending pre-write
holder-exit test from `decision_ledger_contention`. It reuses unchanged receivers;
it does not implement or admit a new native operation.

See [the report](../../docs/research/ledger-holder-exit-without-new-permission.md),
the frozen `contract.json`, and `evidence/execution.json`.

```sh
timeout 35s python3 -B -S experiments/ledger_holder_exit/run.py --output /tmp/adva-holder-exit-new
```

Both the output path and every database must be fresh. Only owned child processes
are killed, after an explicit gate-readiness handshake. Exactly one retry is
allowed per episode. Archive packing and SHA-256 replay are described in the
report; they do not replace semantic validation.

Authored by ChatGPT (OpenAI), through Mingli Yuan's account proxy, not his review
or correctness guarantee. Original code, notes and generated fixtures/evidence:
Unknown v0.3. No imported external content.
