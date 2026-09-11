# Independent verification of the finished 25-124 batch

Date: 2026-09-11. This verification was run by the assistant (DeepSeek Harness)
from a second session, submitted through Mingli Yuan's account as an authorized
proxy. It re-verifies the batch recorded in
[`README.md`](README.md) and committed as `7a91899`; it does not modify, extend
or reinterpret any artifact.

## What was checked, and by what

Two routes, neither of which reuses `continuation-driver.py`.

**A. The declared CLI check**, for all 100 rounds: `adva-labs-search verify` on
`run<N>-report.json` and on `run<N>-tampered.json`.

**B. An independent arithmetic reimplementation.** A Python implementation
recomputes, for the best sequence stored in each report, the aperiodic
autocorrelations `C_k = sum_i s_i s_{i+k}`, the energy `E = sum_k C_k^2` and the
merit factor `n^2 / (2E)`, and compares them to the stored `correlations`,
`energy` and `merit_factor`. This shares no code with the Rust checker; its
agreement is a second implementation agreeing, not a replay of the first.

Each round also carries a **one-flip sensitivity control**: the middle element of
the sequence is negated and the arithmetic recomputed, which must move. A check
that cannot move under a tampered sequence would be evidence of nothing.

## Result

| Measurement | Result |
|---|---|
| Rounds checked | 100 |
| A. CLI verify exited 0 on the report | 100 / 100 |
| A. CLI verify rejected the tampered copy | 100 / 100 |
| B. stored correlations, energy and merit reproduced exactly | 100 / 100 |
| One-flip sensitivity controls that moved the arithmetic | 100 / 100 |
| Problems found | **0** |

Freshly re-run from this directory before this record was written, with identical
output. The script is retained beside this file as
[`independent-verify-2026-09-11.py`](independent-verify-2026-09-11.py) and is
read-only: it opens no file for writing, and a `git status` after a run shows no
modified artifact.

## What this does and does not establish

- **It establishes** that every stored best sequence in runs 25-124 recomputes to
  the stored energy and merit factor under a second implementation, that the
  declared CLI accepts each report, and that it rejects each one-field tampered
  copy. The batch's acceptance record is therefore reproduced, not merely
  restated.
- **It does not establish** anything about search quality. Every round is a
  sampled search; no optimality at any length is claimed by this check or by the
  batch, the separate exhaustive command for `N <= 25` was not run, and no
  published merit table is imported for comparison. The length trend the batch
  reports is a length effect in a finite sample.
- **It does not re-run any search.** Only the verification half of each round was
  replayed; the search half is taken from the retained report bytes.
- **It does not review the batch's own reasoning**, its contract revisions, or the
  archive note it records about the concurrent commit that swept 68 artifacts.
  That note stands as written by its author.

## Reproduce

```sh
python3 independent-verify-2026-09-11.py
```

It requires the workspace build at `target/debug/adva-labs-search` and the
artifacts in this directory, and prints the table above.
