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
hashes validate, and no worker bytecode cache was created. The runner still exits
1 because the two helper defects are unfixed. The target helpers were not edited.

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

Authored by ChatGPT (OpenAI), through Mingli Yuan's account as an authorized proxy;
account use is not endorsement, review, or a correctness claim.
