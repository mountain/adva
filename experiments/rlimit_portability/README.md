# RLIMIT_AS portability audit and minimal opt-in replay

Prepared by ChatGPT (OpenAI) for Mingli Yuan. Original contribution under
Unknown v0.3. Account ownership does not imply authorship, review or correctness.
Submitted through Mingli Yuan's GitHub account (mountain) as an authorized proxy.

Baseline: `0d831e73d702e5456ad4248115b5a34507d82236`. Follow-up to PR #202.

## Finding

Do not sweep Linux guards across every textual occurrence. There are 100 Python
files containing `RLIMIT_AS` under `experiments/` and `python/adva/`, including
15 historical copies. The inventory lists 102 AST references (not 102 independent
installations); dynamic loops and mock declarations require interpretation.
Archives are not unpacked. No pre-existing tracked file was changed.

| Classification | Files | Decision |
| --- | ---: | --- |
| Linux-required entry | 7 | Retain refusal and mandatory memory contract |
| Linux-only installation | 3 | Already guarded; no new guard needed |
| Refusal recorded | 3 | Preserve recorded refusal; do not claim an enforced cap |
| Mock only | 1 | No real installation |
| Historical source | 15 | Preserve bytes, including historical defects |
| Unguarded installation | 71 | Refusal can abort this path; no blanket weakening |

“Unguarded” means the installer has no Darwin gate or local refusal accounting.
It is a portability hazard when reached, not a claim that all 71 entrypoints
were executed, that they all crash without a report, or that they create an
escape from resource enforcement. Many stop or return Failed/Blocked instead.
Conversely, successfully skipping AS does not establish the old memory-bound
claim. These are distinct failure modes.

## Production paths

- `python/adva/adva.py::_limits` is reached by `prime_check`, which rejects
  non-Linux before `Popen`. Its isolated limiter would fail on a refusing API,
  but this is not an exposed Darwin failure in that command. The prime-check
  guard does **not** cover the CLI's separate verifier-search dispatch.
- `python/adva/operator_receipt.py::run` rejects non-Linux before input reads
  or launching the checker. Preserve this gate.
- `python/adva/verifier_search.py::Supervisor.call` installs AS without a
  platform gate. `run` can reach it after executable/database checks, and catches
  the resulting SubprocessError as Blocked. `search_campaign.py` also reuses
  `frozen.child_limits` at its Popen boundary. Mocked execution of the exact
  supervisor demonstrates the preexec failure, without launching proof tools.
  Do not claim the full verifier campaign ran on Darwin.
- The verifier source is byte-pinned by `search_campaign.OLD_PYTHON_SHA` and
  represented in the Research 0152/0153 claims. Simply refreshing a hash after
  weakening limits would not re-establish their retained proof/evidence chain.
  Both files and `docs/claims.toml` remain unchanged.
- `quine_relay.py` already installs AS only on Linux. That fact alone says
  nothing about an enforced Darwin memory ceiling.

## Experiment distinctions

The explicit Linux gates in `judgment_distinction`, `borromean_surface_audit`,
`borromean_longitude_audit`, `sharkovsky_interval_extension` and
`triadic_period_bridge` preserve required resource semantics. They are not
missing portability fixes. `golden_ratio`, `li_yorke_period_three` and
`reflexive_lattice_gate` already retain installation refusals.

`murphy` installs AS only for Python children; `representation_residual` uses it
in the optional native branch. `execution_performance` additionally requires
Linux scheduler affinity and fails before this installer on a host without that
API. A successful Linux-guard edit alone would not port those commands.

For the remaining unguarded experiments, use their exact paths/functions in
`inventory.json` to locate the obstruction. Most bind sources, outputs or
contracts; this audit grants no permission to mutate their old evidence.

## Smallest implemented extension

One new opt-in execution profile replays `frame_covariance`, chosen because its
fixed rational computation is already separated from the legacy `main` limit
installation. The original source, original contract and original evidence are
SHA-256 pinned and executed/read as verified bytes. No monkeypatch replaces
resource functions in production. No arbitrary script or input is accepted.

The new runner invokes the unchanged `trial` and compares **all mathematical
fields** against the frozen witness: status, frames, identities, all rows,
controls, residual and native-word count. Only old timings/environment metadata
are excluded. It produces a separate engineering receipt, never rewrites the
old one, and never reports satisfaction of the old resource contract.

- Linux: AS remains mandatory at at most 256 MiB; failures propagate.
- Darwin: AS explicitly reports `not-installed`. RSS is an observation in bytes,
  not a hard cap and not a substitute for the old memory guarantee.
- CPU (8 seconds), file (1 MiB) and core limits remain mandatory on both hosts;
  inherited tighter limits are not raised. Child alarm: 10 seconds; outer child
  timeout including startup: 12 seconds. One attempt, no automatic retry.
- Outputs require a fresh directory; child stdout/stderr and execution metadata
  are retained separately. The outer supervisor kills the child's process group
  on completion or timeout. No aggregate memory or startup CPU bound is claimed.
- This is a fixed engineering regression, not a newly authorized bounded
  research campaign, native admission or independent mathematical proof.

From the repository root, on macOS or Linux:

```sh
python3 experiments/rlimit_portability/replay.py --output /tmp/adva-frame-replay-01
python3 -m unittest discover -s tests/python -p test_rlimit_portability.py -v
```

The output path must not exist. Do not reuse a completed or failed attempt path.

## Executed checks and remaining boundary

The retained `linux-run-01` is a real Linux execution: **84 rows, 7 controls,
1,615 logical checks**, exact mathematical payload equality. The new unittest
suite passes **10 tests**, including Darwin-shaped AS refusal, mandatory-limit
failure, tighter inherited bounds, source tampering, changed payload, refusal to
overwrite, guarded production entrypoints, reachable verifier preexec failure,
and binding the retained Linux record to the current runner/profile/inputs.

The mocked Darwin test leaves AS present as an attribute and makes installation
raise. This checks the regression PR #202 described; it is not a macOS execution.
**Real Darwin replay remains pending.** The runner can be executed there with
the command above; that record must be kept separate from `linux-run-01`.

An attempted pytest run of the new tests plus the two existing verifier transport
suites stopped at startup because pytest is not installed on this host. Those
existing suites were not run; no green status is asserted for them. All original
tracked bytes remain equal to the baseline, including claims and frozen source
pins. No full test suite, external Lean/Metamath audit or Darwin memory-enforcement
claim is made. Verification below was recorded before publication.

## Complete file classification

Line numbers refer to the pinned baseline, and include all AST AS references.
See `inventory.json` for source digests, function names and per-file caveats.

| File | Lines | Classification |
| --- | --- | --- |
| `experiments/advance_byte_observer/evidence/run-01/implementation-adva.py` | 102 | historical-source |
| `experiments/advance_byte_observer/evidence/run-01/implementation-quine_relay.py` | 160 | historical-source |
| `experiments/advance_symbol_surface/evidence/run-01/implementation-adva.py` | 102 | historical-source |
| `experiments/advance_symbol_surface/evidence/run-01/implementation-quine_relay.py` | 162 | historical-source |
| `experiments/alternating_observer/replay.py` | 84 | unguarded-installation |
| `experiments/borromean_longitude_audit/check.py` | 413 | linux-required-entry |
| `experiments/borromean_surface_audit/check.py` | 438 | linux-required-entry |
| `experiments/boundary_research/calibration.py` | 319 | unguarded-installation |
| `experiments/bounded_mix/runtime.py` | 35 | unguarded-installation |
| `experiments/bounded_mix/runtime_v2.py` | 35 | unguarded-installation |
| `experiments/bounded_native_interpreter/campaign.py` | 219 | unguarded-installation |
| `experiments/bounded_native_interpreter/evidence/attempt-1/sources/experiments/bounded_native_interpreter/campaign.py` | 219 | historical-source |
| `experiments/bounded_native_interpreter/evidence/attempt-1/sources/experiments/bounded_native_interpreter/preflight.py` | 16 | historical-source |
| `experiments/bounded_native_interpreter/evidence/attempt-1/sources/experiments/bounded_native_interpreter/supervise.py` | 63 | historical-source |
| `experiments/bounded_native_interpreter/preflight.py` | 16 | unguarded-installation |
| `experiments/bounded_native_interpreter/supervise.py` | 63 | unguarded-installation |
| `experiments/bounded_observation_exchange/joint_observation.py` | 77 | unguarded-installation |
| `experiments/bounded_self_compiler/evidence/attempt-1/sources/experiments/bounded_self_compiler/runtime.py` | 32 | historical-source |
| `experiments/bounded_self_compiler/evidence/attempt-1/sources/experiments/bounded_self_compiler/supervise.py` | 54 | historical-source |
| `experiments/bounded_self_compiler/evidence/attempt-2/sources/experiments/bounded_self_compiler/runtime.py` | 32 | historical-source |
| `experiments/bounded_self_compiler/evidence/attempt-2/sources/experiments/bounded_self_compiler/supervise.py` | 54 | historical-source |
| `experiments/bounded_self_compiler/evidence/preflight-2/sources/experiments/bounded_self_compiler/runtime.py` | 32 | historical-source |
| `experiments/bounded_self_compiler/evidence/preflight-3/runtime-before-fix.py` | 32 | historical-source |
| `experiments/bounded_self_compiler/runtime.py` | 32 | unguarded-installation |
| `experiments/bounded_self_compiler/supervise.py` | 54 | unguarded-installation |
| `experiments/catalog_key_words/alignment/run_evidence.py` | 18 | unguarded-installation |
| `experiments/clock_history/receive.py` | 233 | unguarded-installation |
| `experiments/clock_history/run.py` | 85, 305 | unguarded-installation |
| `experiments/continuation_binding/run.py` | 81 | unguarded-installation |
| `experiments/cube_root_polar/replay.py` | 170 | unguarded-installation |
| `experiments/decision_checkpoint/run.py` | 112 | unguarded-installation |
| `experiments/decision_ledger/run.py` | 67 | unguarded-installation |
| `experiments/decision_ledger_contention/receive.py` | 23 | unguarded-installation |
| `experiments/decision_scale/run.py` | 95 | unguarded-installation |
| `experiments/decision_scale_composition/run.py` | 99 | unguarded-installation |
| `experiments/disclosure_binding/calibration.py` | 203 | unguarded-installation |
| `experiments/evidence_stutter/calibration.py` | 131 | unguarded-installation |
| `experiments/execution_performance/run.py` | 118 | unguarded-installation |
| `experiments/failure_kind_boundary/supervise.py` | 22 | unguarded-installation |
| `experiments/faithful_switch/calibration.py` | 354 | unguarded-installation |
| `experiments/finite_decision/run.py` | 119 | unguarded-installation |
| `experiments/finite_group_probability/check.py` | 198 | unguarded-installation |
| `experiments/finite_learner/calibration.py` | 36 | unguarded-installation |
| `experiments/finite_split/calibration.py` | 388 | unguarded-installation |
| `experiments/frame_covariance/run.py` | 192 | unguarded-installation |
| `experiments/frame_triad/calibration.py` | 295 | unguarded-installation |
| `experiments/goal_exploration/calibration.py` | 260 | unguarded-installation |
| `experiments/gold_twin_close/supervise.py` | 17 | unguarded-installation |
| `experiments/golden_ratio/calibration.py` | 395 | refusal-recorded |
| `experiments/golden_ratio_operator_lift/check_adapter.py` | 30 | unguarded-installation |
| `experiments/golden_ratio_operator_lift/check_receipts.py` | 126 | unguarded-installation |
| `experiments/golden_ratio_operator_lift/receipt.py` | 195 | unguarded-installation |
| `experiments/golden_ratio_operator_lift/replay.py` | 166 | unguarded-installation |
| `experiments/history_surface/run.py` | 265 | unguarded-installation |
| `experiments/interpretation_obligation/calibration.py` | 161 | unguarded-installation |
| `experiments/interpretation_obligation/run-01/calibration.py` | 161 | historical-source |
| `experiments/interval_enclosure/receive.py` | 330 | unguarded-installation |
| `experiments/interval_enclosure/run.py` | 95 | unguarded-installation |
| `experiments/iota_grid_embedding/check.py` | 254 | unguarded-installation |
| `experiments/judgment_distinction/calibration.py` | 565 | linux-required-entry |
| `experiments/kernel_composition/receive.py` | 238 | unguarded-installation |
| `experiments/knowledge_boundary/calibration.py` | 398 | unguarded-installation |
| `experiments/lattice_polar/calibration.py` | 205 | unguarded-installation |
| `experiments/li_yorke_period_three/replay.py` | 285 | refusal-recorded |
| `experiments/linear_system/receive.py` | 256 | unguarded-installation |
| `experiments/linear_system/run.py` | 81 | unguarded-installation |
| `experiments/markov_horizon/receive.py` | 258 | unguarded-installation |
| `experiments/markov_horizon/run.py` | 76 | unguarded-installation |
| `experiments/mobius_conjugacy_transport/calibration.py` | 360 | unguarded-installation |
| `experiments/mobius_transport_receipt/check.py` | 260 | unguarded-installation |
| `experiments/mobius_transport_receipt/compose.py` | 166 | unguarded-installation |
| `experiments/murphy/run.py` | 51 | unguarded-installation |
| `experiments/numeric_boundary_audit/audit.py` | mock keyword | mock-only |
| `experiments/observable_unit_transport/receive.py` | 206 | unguarded-installation |
| `experiments/pairing_transport/replay-before-cutwire-fix.py` | 193 | historical-source |
| `experiments/pairing_transport/replay.py` | 194 | unguarded-installation |
| `experiments/pascal_circle_learning/duality.py` | 128 | unguarded-installation |
| `experiments/pascal_circle_learning/run.py` | 252, 439 | unguarded-installation |
| `experiments/pascal_commutator_certificate/run.py` | 33 | linux-only-install |
| `experiments/pascal_spectre_patch/patch.py` | 345 | unguarded-installation |
| `experiments/phase_runner/run_six.py` | 147 | linux-only-install |
| `experiments/prefix_frontier/coverage_gate.py` | 216 | unguarded-installation |
| `experiments/prime_universe/finite_witness.py` | 182 | unguarded-installation |
| `experiments/private_merge/merge.py` | 228 | unguarded-installation |
| `experiments/probability_receipt/run.py` | 112 | unguarded-installation |
| `experiments/quadratic_gap/receive.py` | 247 | unguarded-installation |
| `experiments/quadratic_gap/run.py` | 100 | unguarded-installation |
| `experiments/reflexive_lattice_gate/calibration.py` | 454 | refusal-recorded |
| `experiments/representation_residual/run.py` | 233 | unguarded-installation |
| `experiments/resource_frame/calibration.py` | 227 | unguarded-installation |
| `experiments/reversible_memory/receive.py` | 336 | unguarded-installation |
| `experiments/reversible_memory/run.py` | 84, 219 | unguarded-installation |
| `experiments/revise_cycle/calibration.py` | 227 | unguarded-installation |
| `experiments/sharkovsky_interval_extension/check.py` | 236 | linux-required-entry |
| `experiments/structural_adjustment/calibration.py` | 278 | unguarded-installation |
| `experiments/triadic_period_bridge/check.py` | 207 | linux-required-entry |
| `python/adva/adva.py` | 102 | linux-required-entry |
| `python/adva/operator_receipt.py` | 98 | linux-required-entry |
| `python/adva/quine_relay.py` | 180 | linux-only-install |
| `python/adva/verifier_search.py` | 40 | unguarded-installation |
