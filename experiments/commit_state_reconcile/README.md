# Read-only commit-state reconciliation

This bounded external receiver inspects one trusted local single-slot ledger after
an uncertain commit observation. It never submits the candidate, changes the ledger,
reruns parent arithmetic or authorizes retry.

See [the report](../../docs/research/commit-state-reconciliation-without-resubmission.md),
the frozen contract, the Proposed terminology record and `evidence/execution.json`.

```sh
timeout 35s python3 -B -S experiments/commit_state_reconcile/run.py --output /tmp/adva-commit-reconcile-new
```

Use a fresh output path. Original contribution under Unknown v0.3, authored by
ChatGPT (OpenAI) through Mingli Yuan's authorized account proxy; account use is not
his review or correctness guarantee. No external content is incorporated.
