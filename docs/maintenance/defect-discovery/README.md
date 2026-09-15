# Retained discovery runs

This directory retains the first implementation of
[the frozen discovery workflow](../DEFECT_DISCOVERY.md).

## 2026-09-15 execution and correction record

Source baseline: `20ff8a77ab45aa8388ee1058cad21faaeb07d16f`.
Only the four target Python files and the runner were needed; this was a partial
API-fetched source snapshot, not a complete Git checkout or repository build.

`20260915-run-001` executed all three finite families twice. It found one
cross-zero exponential enclosure violation and eight constant inverse violations
per replay; all 24 segmented-execution/receipt checks passed. Exit code 1 means
findings were retained, not an infrastructure failure.

A provenance check then caught an extra trailing blank line introduced while
materializing each of the four target files. Their executable statements were
unchanged, but their Git blob hashes were **not** the main blobs. The first run
is retained as actually executed and must not be described as byte-identical to
main. Importing the probe also wrote a bytecode cache before the no-bytecode flag
was set; this incidental cache is not evidence and is excluded from commits.
The runner now disables bytecode before imports and launches workers with `-B`.

### Revised finite acceptance contract for run 002 (declared before execution)

One additional invocation, exactly the same three input families and two replays,
with the same resource ceilings. Purpose: verify exact fetched-source identity
after removing only the materialization-added blank line, confirm no worker
bytecode output, and exercise the completed severity/open-obligation reporting.
No mathematical search, extra inputs, or target semantic edit is authorized by
this follow-up. Stop after that invocation; retain findings or Unknown unchanged.

The four corrected files were checked using Git's blob SHA-1 encoding against
the GitHub file identities at the baseline:

| Target | Git blob SHA |
| --- | --- |
| integer_power_absurdity/calibration.py | a9d561e4307e8d367bf54d264f88d33c815f75e0 |
| aeg_core_shell_multivariate/calibration.py | 31ba29df0f424d1a006704734297799badce6c9a |
| keraia_read_machine/machine.py | 02bd4c31a531825dddb4084cf45ff368ab3991dc |
| keraia_read_machine/syntax.py | a9765048ba6fffccf697ce676a1a1360477978db |

### Attribution and unresolved impact

Run 002 completed in 0.441 seconds with the same nine violating cases and 27
passing cases per replay (36 total cases, each replayed twice). Exact main-source
blob identities now match, both report hashes and all retained source SHA-256
hashes validate, and no worker bytecode cache was created. At the end of run 002
the runner exited 1 because the two helper defects were then unfixed and the
target helpers had not been edited. Both were subsequently fixed; see
[the fix record](#2026-09-15-fix-record-for-the-two-helper-defects) below.

The engineering control suite covers oracle mutants, Unknown vs pass, resource
installation failure, report integrity, duplicate replay identity, local/security
submission exclusion, modified packages, dry-run network absence, deduplication,
ambiguous publication, and retained submission receipts. These mocked transport
tests do not constitute a real upstream issue submission.

After run 002, the report consumer was added and the classifier tightened to
reject empty/unknown case verdicts. These do not change the executed probe or
target code. The final 14 engineering tests pass; their output is retained in
`engineering-tests.txt`. The report consumer accepts run 002 with its own
retained runner hashes. A complete staged whitespace check flags the four
intentionally preserved extra-blank-line run-001 sources; excluding that raw
historical snapshot, the staged whitespace check passes.

The exponential helper explicitly handles crossing-zero inputs but sets the
lower bound to `exp(0)=1`. Since `exp(1)>2`, `exp(-1)<1/2`; its returned interval
cannot contain the endpoint value. The inverse helper normalizes a nonzero
constant, then returns `one` early without the final reciprocal scaling. These
are actual Adva helper defects, not evidence of CPython/Fraction, SymPy, or LLVM
misbehavior. The currently frozen constant-inverse experiment uses constant term
one, so the new witness does not refute that experiment's retained conclusion.
The cross-zero caller/retained-certificate exposure also remains unestablished.

No upstream issue was submitted: neither new witness establishes an upstream
contract violation. Remote publication is tested with mocked transport only;
successful real GitHub submission and GitHub Actions execution remain untested.
The report transport's checks are structural; an agent still has to establish
attribution and inspect the public payload. No claim of full repository, native
Rust, deployment, FFI, or alternative-interpreter acceptance is made.

## 2026-09-15 fix record for the two helper defects

Runs 001 and 002 are retained above unchanged as the executed history. This
section records the repair that followed them. Nothing here rewrites those runs,
and neither report was regenerated.

Both defects named in run 002 were confirmed Adva-owned and fixed in place, in
the same files the probes execute:

| Helper | File | Defect | Repair |
| --- | --- | --- | --- |
| `exp_interval` | `experiments/integer_power_absurdity/calibration.py` | the crossing-zero branch returned `exp(0)=1` as its lower bound | each end is handed to the matching one-sided branch, so the lower bound is `exp(x.lo)` |
| `truncated_inverse` | `experiments/aeg_core_shell_multivariate/calibration.py` | the zero-remainder early exit returned `one` and dropped the normalization just applied | it returns `one.scale(1 / constant)` |

The exponential repair deliberately does not negate the crossing-zero interval:
`Interval(-x)` maps a crossing-zero interval onto another crossing-zero interval,
so that route recurses into the same branch forever. Sending `[x.lo, 0]` to the
non-positive branch and `[0, x.hi]` to the non-negative branch keeps `exp_reduced`
on the non-negative arguments it requires.

### The repair is evidence-neutral for the retained experiments

The frozen experiments were not re-interpreted, and this was established rather
than assumed, by instrumenting each helper and counting its actual call sites in
the frozen runs:

- `exp_interval`: 29 calls. Zero of them crossed zero, so the repaired branch was
  never taken by the retained experiments.
- `truncated_inverse`: 4 calls. The three series calls have constant term 1 and
  remainder `g = x^2`, which is non-zero, so they take the loop; the fourth is the
  refusal control, which has no constant term and is rejected before either path.
  The early exit was never reached.

The retained `evidence.json` files therefore cannot have depended on either
defect, and both frozen-replay tests still pass unchanged.

### Checks executed

- Both defects were reproduced before the fix and are gone after it. The three
  probe families were run directly, without the enforced resource profile of
  `run.py`, on CPython 3.14.6/macOS: 1 + 8 = 9 violations before, 0 violations
  after, with the same 36 cases (2 + 10 + 24).
- Four regression tests were added, two per helper. All four fail against the
  pre-fix helpers and all four pass against the repaired ones, which is the
  property that makes them regressions rather than decoration. The exponential
  test uses an independent rigorous oracle — the direct series with an explicit
  remainder bound, no argument halving and squaring, no outward grid, no interval
  type — and requires the returned interval to contain `exp` at both ends, which
  is necessary and sufficient for an increasing function. Loose rational bounds
  such as `exp(-1) < 1/2` are only necessary and cannot carry this test.
- `tests/python/test_integer_power_absurdity.py` and
  `tests/python/test_aeg_core_shell_multivariate.py`: 21 passed.
- `scripts/defect_discovery/test_discovery.py`: 14 passed.
- Whole `pytest` suite: 2722 passed, 11 failed, 1 skipped. The same 11 failures
  reproduce on the unmodified baseline, so they are pre-existing and
  environmental (a `preexec_fn` failure under the local macOS process model, and a
  frozen-output replay test), not effects of this repair.

### What was not executed

- The enforced-resource-profile runner was not run locally: `run.py --worker`
  refuses a non-Linux host, and this repair was prepared on macOS. A run 003
  artifact with the real ceilings requires a Linux host or the manual
  **Bounded defect discovery** workflow.
- Neither helper was checked against a native Rust certificate, a deployed
  binary, an alternative interpreter, or concurrent callers. The exposure of any
  retained certificate to the crossing-zero branch remains unestablished, exactly
  as run 002 recorded it.
- No upstream issue was filed, before or after the fix. The finding was Adva-owned
  throughout, and neither witness ever established an upstream contract
  violation. There is no security grade to assign: the disclosure path is
  `PublicNonSecurity` by construction and the transport refuses a
  security-sensitive finding outright.

Repair prepared by deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted
through Mingli Yuan's GitHub account as an authorized proxy. Account use is not
endorsement, review, or a correctness claim.

Authored by ChatGPT (OpenAI), through Mingli Yuan's account as an authorized proxy;
account use is not endorsement, review, or a correctness claim.
