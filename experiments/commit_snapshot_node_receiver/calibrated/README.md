# Calibrated Node receiving continuation

Overall status: **InvalidBudgetEvidence**. Four valid cases and ten refusals
passed on the sole correction replay, but the runner reset counters between
attempts and exceeded the frozen cumulative work and call limits.

Read the [research report](../../../docs/research/commit-state-node-meter-calibration.md)
and authoritative [cumulative audit](evidence/execution.json) before reuse.
The per-attempt `Passed` record is not overall acceptance. No further campaign
was run after discovery. No vocabulary was created or revised.

This directory is a versioned research continuation; the parent source,
contracts, failed runs and pins are preserved. `receive_pair.mjs` retains all
semantic checks and adds measured input accounting plus a calibrated cap.
`run.py` is retained as executed, including its cumulative-supervision defect.
The evidence archive includes both attempts and exact source snapshots.

Original continuation by Codex (OpenAI), Unknown v0.3; through Mingli Yuan's
authorized account proxy, not his review or guarantee.
