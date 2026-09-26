# Bound charge pair

This project-original finite experiment tests the successor of the amount-only
charge obstruction in Research 0245. A `cumulative-trial-v1` charge binds a
fresh identifier, the SHA-256 coordinate of canonical task-contract bytes, a
positive integer amount and phase `charged`. A task reservation repeats the
identifier, digest and amount at phase `reserved`.

The receiver is read-only. `BindingVerified` reports only that one received
account record and one received reservation agree under the frozen relation. It
does not authorize launch, retry, mutation or native `free`. Replaying the same
pair produces the same observation and is deliberately **not** an exactly-once
mechanism.

Replay from the repository root with a fresh path:

```sh
python experiments/bound_charge_pair/run.py --output /tmp/adva-bound-charge-pair
```

Project-original Codex (OpenAI), Unknown v0.3, submitted through Mingli Yuan's
authorized account proxy. Account use is not authorship, review, endorsement or
a correctness guarantee.
