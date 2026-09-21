# Two-builder commit-snapshot cross-check

This bounded external experiment advances the Proposed word
`commit-state-reconcile`. The inherited snapshot builder and a direct-schema
implementation read the same finite ledger. Their complete snapshots retain
different builder provenance, while the ledger-derived projections must be
byte-identical. A third process opens neither ledger and permits an ordinary
commit-state outcome only when both pinned snapshots are individually valid,
their projections agree, and their builder-source maps differ.

Any disagreement, copied provenance, changed question, wrong pin or missing
snapshot yields `UnknownCommitState`. No outcome grants retry, new fuel,
native acceptance or arithmetic replay.

Replay from the repository root into a fresh directory:

```sh
timeout 35s python3 -B -S experiments/commit_snapshot_crosscheck/run.py \
  --output /tmp/adva-commit-snapshot-crosscheck-new
```

See the [frozen contract](contract.json), the
[research report](../../docs/research/commit-state-two-builder-projection-agreement.md),
the [v2 proposed-word record](../../docs/terminology/commit-state-reconcile-v2.json),
and the compact [execution evidence](evidence/execution.json).

Original code, prose and synthetic evidence: ChatGPT (OpenAI), contributed
under Unknown v0.3 through Mingli Yuan's authorized account proxy; not his
review, endorsement or correctness guarantee. No external content is included.
