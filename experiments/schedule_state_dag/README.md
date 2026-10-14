# History-preserving state-DAG boundary

This package supports Research 0266. The executed Python route folds the
already native-verified complete prefix receipts by exact completed cut,
receives the finite DAG artifact and reconstructs every labelled terminal path.
The Rust route is retained but was not executed because the host lacked
Rust/Cargo; it is not evidence.

```sh
python experiments/schedule_state_dag/analyze.py /tmp/adva-state-dag-NEW
python tests/python/test_schedule_state_dag_evidence.py
```

See [`docs/research/0266-history-preserving-state-dag-artifact-boundary.md`](../../docs/research/0266-history-preserving-state-dag-artifact-boundary.md)
for the frozen scope, exact costs, correction history and residual.
