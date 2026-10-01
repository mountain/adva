# Single consumption receipt

This project-original finite experiment follows Research 0247. It separates
repeatable verification of a charge--task binding from the state of one local
consumption chain.

The file-backed research tool uses the states `unconsumed`, `pending` and
`consumed`. A process exit after recording `pending`, or a second contender
after one contender records it, returns `UnknownConsumptionState` and never
resets the chain. A completed chain stores one project-original test marker;
later reconciliation reproduces that observation while a later reservation is
blocked. No target effect starts and no receipt authorizes one.

Replay from the repository root with a fresh path:

```sh
python experiments/single_consumption_receipt/run.py \
  --output /tmp/adva-single-consumption
```

This is a trusted, single-host Linux experiment, not a power-loss or
distributed exactly-once implementation.

Project-original Codex (OpenAI), Unknown v0.3, submitted through Mingli Yuan's
authorized account proxy. Account use is not authorship, review, endorsement or
a correctness guarantee.
