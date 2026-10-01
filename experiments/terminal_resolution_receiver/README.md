# Terminal resolution receiver

This bounded experiment independently receives archived bytes from Research
0251. It recomputes the source-pending and recovery-receipt digests, checks the
complete terminal projection and never accepts a mutable ledger or lock path.

Run from the repository root:

```sh
python experiments/terminal_resolution_receiver/run.py \
  --output /tmp/adva-terminal-resolution-receiver
```

`UnknownResolutionState` preserves a missing or divergent archive as an open
question. It is not completion, cancellation, retry permission or a refund.
