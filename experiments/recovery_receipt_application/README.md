# Recovery receipt application

This finite experiment applies exact Research 0250 receipts to canonical
`pending` ledgers under one local file lock and same-directory atomic replace.
It writes either a `completed` terminal or a separately scoped `cancelled`
terminal. Neither terminal grants retry, refund, effect, native or `free`
authority.

Run from the repository root:

```sh
python experiments/recovery_receipt_application/run.py \
  --output /tmp/adva-recovery-receipt-application
```

The cancellation state means only that one declared complete finite channel
and closed interval contained no matching event. It is not global evidence that
no effect occurred.
