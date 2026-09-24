# Cross-language commit-snapshot receiver preflight

Status: **Unknown / paused after the one permitted correction replay**.

This bounded external experiment asks whether a Node.js standard-library
receiver can reproduce the existing Python `commit-state-reconcile` pair
judgment from archived JSON bytes, without opening SQLite, invoking Python
semantics, changing an allowance or granting retry.

The receiver uses an original strict JSON parser. It accepts only the subset
actually declared by the frozen contract: ASCII strings, unique object keys and
safe integers. Fractions remain integer pairs. Unsupported values return
`UnknownCommitState` rather than being coerced by JavaScript.

The first attempt stopped before semantic comparison because a floating timing
field could not pass the receiver's own integer-only canonicalizer. The sole
correction changed report time to integer nanoseconds. On replay, the archived
symmetric empty pair matched the Python result and projection digest, using
6,841 work units. The larger committed pair reached 10,001 units against a
10,000-unit per-call cap and therefore returned `UnknownCommitState`. The
campaign stopped; twelve planned cases are `NotRun`.

Replaying the frozen campaign should reproduce the nonzero paused outcome:

```sh
timeout 35s python3 -B -S experiments/commit_snapshot_node_receiver/run.py \
  --output /tmp/adva-commit-snapshot-node-receiver
```

See the [contract](contract.json), [research report](../../docs/research/commit-state-node-receiver-budget-pause.md),
compact [second-attempt result](evidence/execution.json), and [archive
manifest](evidence/manifest.json). The archive retains both attempts.

No new word or revision of `commit-state-reconcile` is claimed. The partial
agreement is finite process evidence, not authentication, native admission,
arithmetic truth, universality, Close, free, Seal or M6 closure.

Original code, prose and synthetic controls: ChatGPT (OpenAI), contributed
under Unknown v0.3 through Mingli Yuan's authorized account proxy; not his
review, endorsement or correctness guarantee. No external content is included.
