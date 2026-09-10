# Operator-lift integration with merged scalar checker v1

Merge review, 2026-09-10. The producer merged #179 as
`d423ea83259b982a891d03cea3e3fcdc670a7876`, including successor
`34a7383e2d9bb3304ebe4809d2456365807ae52f`. The scalar source changed to
SHA-256 `ac145fccbbcd86d4b4ea399d680fe34c1fcd72a1208affef4125f890e9fbe845`.
Its diff corrects explanatory scope and adds calibration checks, PDF probes
and budget reporting. The imported affine operations retain their definitions;
the Laurent routine's explanatory text changed, not its computation.

The old operator-lift contract pins the previous scalar source and must not
silently accept this successor. It and its evidence remain byte-identical;
their original command requires the historical checkout. A new
`main-contract-v1.json` explicitly pins the new scalar source and the hash of
the original contract. It retains the same objects, word, obligations and
bounded budget. `replay_main.py` validates this predecessor binding before
calling the original operator checker under the selected successor contract.

Current entry:

```sh
timeout 10s python -B -S experiments/golden_ratio_operator_lift/replay_main.py \
  --output /tmp/operator-main-fresh.json
```

`main-evidence-v1.json` records 27 passed checks, 3,774 counted work units,
24.034 ms construction/validation, 0.584 ms serialization/round-trip and
15,872 KiB peak RSS. No search or correction replay occurred in this integration
check. It does not need the source PDF or rerun the full golden calibration.

The unchanged external Python CLI integration suite was checked once on the
snapshot with the new scalar source: 13 checks passed in 603.511 ms before
serialization/write, 10 CLI calls and 6 backend calls, suite peak RSS 12,928
KiB. `main-adapter-evidence.json` retains the result. Its `correction_replays`
field and `prior_attempt` refer to the earlier suite-development history;
this integration invocation performed no correction replay. Research/network
and final write costs are not measured, and no acceleration is claimed.

CI run 34491495960 reports failure for four jobs, all with empty step lists;
that is not a passing CI run and its cause remains unknown. No status override
or repeated workflow rerun was attempted. This review relies on the scoped
external execution and read-only Python boundary tests, not on native Rust
validation. These changes introduce no Rust semantics or certificates.

The PR is retargeted from the now-merged parent branch to main. This integration
record accompanies the user's explicit merge request. Prior notes saying
"unmerged", "draft", or naming the old invocation describe their historical
snapshots; they are not rewritten. Native free, Seal, M6, full coverage and
Pascal geometry obligations remain unchanged by repository integration.
