# Cumulative reservation with the Node snapshot receiver

This bounded experiment connects the merged cumulative reservation prototype
to one empty and one committed invocation of the existing calibrated Node
snapshot receiver. The valid result is `PassedAfterCorrectionReplay`; the
first attempt is retained as `InvalidContext` because it mistyped the full main
commit coordinate. Its reservations were not refunded or reset.

Read the [research report](../../docs/research/0233-cumulative-reservation-on-real-node-receiving.md),
[contract](contract.json), [execution](evidence/execution.json) and
[manifest](evidence/manifest.json) together. The evidence archive contains
both attempts, their exact executed sources, inputs, outputs and accounts.

This is a single-writer research prototype over trusted local programs. It is
not a hard CPU meter, authentication mechanism, native Adva ledger, `free`,
M6 closure or universality result. No new vocabulary is proposed.

Original experiment by Codex (OpenAI), Unknown v0.3, through Mingli Yuan's
authorized account proxy; not his review, endorsement or guarantee.
