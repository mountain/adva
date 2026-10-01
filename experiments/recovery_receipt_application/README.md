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

## TC-050 correction (2026-10-01)

The live `apply.py` now validates nonempty attempt/channel identifiers, lowercase
64-digit SHA-256 coordinates, an ordered nonnegative integer coverage interval
(excluding Booleans), and completed/result versus cancelled/null consistency.
Before refusing a same-receipt replay it also compares the terminal's state,
context, witness, channel, coverage and result against that exact recovery receipt.
Malformed or divergent terminals return `InvalidEvidence` without ledger mutation.
This is receiver hardening within the existing trusted-host scope, not producer
authentication, permission to retry, or evidence of an external effect.

Historical Research 0251 remains pinned to the byte-identical
`apply_frozen_v0.py`; `run.py` selects this archived implementation and still
checks the original contract digest. It is retained solely for historical replay
and regression comparison, and is not the live application entry point.
Contracts, evidence, claim payloads and the Research 0252 receiver are unchanged.
The old weak replay validation remains an explicit limitation of the frozen run.

`tests/python/test_recovery_terminal_validation.py` exercises the live CLI and
shows each malformed same-receipt control passes the old replay shortcut before
being rejected by the corrected receiver. It also checks valid completion,
cancellation and replay, and malformed recovery digest rejection before conflict.
The focused application/terminal suites pass 41 tests on Python 3.12.

Project-original contribution under Unknown v0.3. Authored by Codex (OpenAI),
submitted through Mingli Yuan's GitHub account as an authorized proxy; account
use is not his authorship, review, endorsement or a correctness guarantee.
