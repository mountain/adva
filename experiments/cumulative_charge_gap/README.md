# Cumulative charge gap

This bounded project-original experiment checks the interruption window after a
cumulative trial charge but before the task journal records its reservation.
It demonstrates that the current v0 charge schema has no task-binding field and
that equality of totals can double-match one charge to two different tasks.

The read-only receiver therefore returns `UnknownAttemptState`, mutates no
account and authorizes no launch or retry. It does not repair the gap or model
power loss and is not a native Adva operation.

Run from the repository root after reading the frozen contract:

```sh
python experiments/cumulative_charge_gap/run.py \
  --output /tmp/adva-cumulative-charge-gap
```

Authored by ChatGPT (OpenAI). Submitted through Mingli Yuan's GitHub account as
an authorized proxy; account use is not review or a correctness guarantee.
