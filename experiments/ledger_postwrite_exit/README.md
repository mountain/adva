# Post-write holder exit before COMMIT

This original finite harness pauses the unchanged ledger receiver after both
application writes and before `COMMIT`, runs one real contender, kills the owned
holder and permits exactly one bounded retry. It is an external SQLite schedule
test, not a native Adva operation or a power-loss result.

See the [research report](../../docs/research/ledger-postwrite-exit-before-commit.md),
the frozen contract and `evidence/execution.json`.

```sh
timeout 35s python3 -B -S experiments/ledger_postwrite_exit/run.py --output /tmp/adva-postwrite-exit-new
```

Use a fresh output path. Original contribution under Unknown v0.3, authored by
ChatGPT (OpenAI) through Mingli Yuan's authorized account proxy; account use is
not his review or a correctness guarantee. No external content is incorporated.
