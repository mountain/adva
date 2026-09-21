# Pinned commit-state snapshots

This bounded external experiment revises the Proposed word
`commit-state-reconcile`. `snapshot.py` opens and validates one trusted local
single-slot SQLite ledger, then emits a canonical versioned JSON snapshot.
`receive.py` is a separate process that does not import SQLite or open the
ledger; it checks a receiver-selected SHA-256 pin and the complete snapshot
relation.

The receiver emits only `StoredCommitted`, `ProvenUncommittedLedger`, or
`UnknownCommitState`. None authorizes retry, new fuel, native acceptance or
arithmetic replay. A byte digest is an integrity coordinate, not authentication.

Replay from the repository root into a fresh directory:

```sh
timeout 35s python3 -B -S experiments/commit_snapshot_receipt/run.py \
  --output /tmp/adva-commit-snapshot-new
```

See the [frozen contract](contract.json), the
[research report](../../docs/research/commit-state-snapshot-independent-receiving.md),
the [v1 proposed-word record](../../docs/terminology/commit-state-reconcile-v1.json),
and the compact [execution evidence](evidence/execution.json).

Original code, prose and synthetic evidence: ChatGPT (OpenAI), contributed
under Unknown v0.3 through Mingli Yuan's authorized account proxy; not his
review, endorsement or correctness guarantee. No external content is included.
