# Bounded defect discovery and upstream reporting

This is engineering regression discovery, separate from the read-only daily
[toolchain watch](TOOLCHAIN_WATCH.md). It neither resumes research search nor
changes mathematical semantics. The user requested executable discovery,
retained reports, and agent submissions on 2026-09-15.

## Frozen v1 run contract (written before execution)

- Question: do the actual research helpers preserve exponential interval
  enclosure, constant inverse identity, and segmented execution/receipt binding?
- Current level: external Python helpers, not native Rust semantic authority.
- Inputs: `exp_interval([-1,1],16)` and the zero control; five nonzero rational
  constants at orders 1 and 2; three closed Keraia terms, four cuts each, and
  mutations of steps, endpoint cursor, and endpoint profile. No generated search.
- Oracles: exact elementary exponential bounds, rational reciprocals, and
  metamorphic execution relations. Cross-domain justification is the helper's
  explicit arithmetic or receipt contract, not a heuristic score.
- Imported assumptions: CPython integers/Fraction, OS enforcement, filesystem,
  and hardware. Keraia replay shares its evaluator: this is not independent
  semantic verification. Separate compiler or hardware failures remain possible.
- Protected obligations: no Rust certificate issuance, no proof of unrestricted
  correctness, no new mathematical library admission, no ledger fuel reset,
  no reinterpretation of the frozen experiments' accepted claims.
- Limits: three probes, two fresh processes each, at most 32 cases per probe;
  each worker gets 5 CPU seconds, 10 wall seconds, 512 MiB address space and
  1 MiB per output file. Parent starts no more than six workers within a
  75-second run deadline. Retention is capped at 8 MiB and each source at 1 MiB.
  Checking and the second replay are inside these limits. Source retention and
  report publication are finite-size operations; the CI outer job is capped at
  three minutes, including setup and upload. This is a reviewed-code resource
  guard, not a sandbox for hostile code or fork bombs.
- Exit: `0` bounded pass; `1` repeatable contract violation; `2` Unknown (including
  worker error, differing replay, limit installation failure, or exhaustion).
  Never automatically retry with more fuel. An interrupted/incomplete directory
  without a valid `COMPLETE.json` must not be accepted as a report.

The executable limits are in `scripts/defect_discovery/run.py:CONTRACT`.
Changing probe families or limits requires updating this contract before running.
The cross-zero and constant-denominator inputs extend helper coverage; they do
not by themselves refute the narrower retained research experiments.

## Run and retain

From a Linux checkout with Python 3.11 or later, no extra packages are needed:

```sh
python scripts/defect_discovery/test_discovery.py
python scripts/defect_discovery/run.py --source-commit "$(git rev-parse HEAD)" --out /tmp/adva-defects-run-001
python scripts/defect_discovery/verify.py /tmp/adva-defects-run-001
```

Use a fresh output directory. `report.json` is the fixed machine report;
`report.md` is its human rendering. Both carry the same finite evidence, with
per-case expected/actual values, two replay receipts, interpreter/host identity,
source hashes, common-failure assumptions, and open obligations. Actual source
copies are retained under `sources/` and workers execute that snapshot.
The supplied commit is a declared identity; file hashes are the identity of the
executed source. This distinction also handles dirty trees and partial checkouts.
No claim about installed wheels or rebuilt/deployed binaries follows.
`verify.py` checks report/source hashes and replay-state consistency without
executing the target again. Integrity checking is not correctness certification.

The manual GitHub workflow **Bounded defect discovery** produces the same artifact
and preserves failures. It uses read-only repository permissions. It does not
file issues from CI, and a finding intentionally makes the discovery step red.
No full repository build or private submodule is required by these three adapters.

## Fixed report fields and evidence states

Every finding records: exact source/version and date, invariant, input, expected
result and independent justification, actual result, witness, environment,
replay hashes, scope, common-failure risk, severity/impact judgment, minimal next
step, and open obligations. Machine discovery deliberately leaves upstream
attribution `NotEligible`; the agent must investigate ownership next.

- `Unknown`: execution or evidence incomplete; never report this as a pass.
- `BoundedPass`: this input family passed this checker twice.
- `NativeReproduced`: actual target Python implementation ran twice and produced
  identical counterexample evidence, as opposed to a C or mathematical substitute.
  This label does **not** mean a native Rust certificate.
- `UpstreamContractViolation`: an agent has separately established that the
  dependency, rather than our adapter/precondition/serialization, breaks its
  documented contract. Package checks cannot establish this judgment themselves.
- Proposed fix, source fix, merged PR, installed dependency, rebuilt binary, and
  environment acceptance stay separate milestones in the ongoing TC ledger.

Probe IDs are stable local family keys, not replacements for TC numbers. Reuse
the existing TC number when a witness matches a known upstream ID/fix; allocate
new TC records only after reading the current ledger and deduplicating.

## Agent workflow: discover, attribute, submit, follow up

1. Read current `AGENTS.md`, this contract, current main, toolchain-watch records,
   and previous reports. Confirm versions/features. Run the finite suite once;
   retain all results, including controls and Unknown. Do not silently repair a
   failed checker and omit its failed run.
2. Challenge the oracle. Use mutation controls, exact identities, changed input
   ownership, segmentation or independent algorithms. A wall clock in resource
   enforcement alone is not a bug; Decimal alone is not exactness or outward
   rounding. A shared library/compiler/hardware must be named as a common risk.
3. Minimize within a declared finite follow-up budget. Establish the helper's
   admitted domain; distinguish a helper bug from an affected retained certificate.
   File/fix Adva-owned issues in Adva, not in CPython or LLVM. Do not label missing
   submodules, undefined behavior, invalid inputs, or mere differing outputs as
   an upstream defect without the violated contract.
4. For a real upstream candidate, make a standalone reproduction containing no
   private Adva source, credentials, data, host names, or nonessential paths.
   Record exact affected version, build flags, architecture, expected and actual
   results. Replay twice and retain outputs. Check a newer/fixed version when
   feasible; absence of a fixed version does not prevent reporting. Do not run
   upstream crash samples or privileged/kernel experiments without their own
   concrete authorized run contract.
5. Read the target's current contribution, AI attribution, and security policies.
   Search by upstream ID/fix and minimal symptom in open **and closed** issues.
   Follow the security reporting channel for security-sensitive findings; the
   public helper below explicitly excludes those. Record the searches and policy
   URLs/date in the candidate. Respect a target's prohibition on AI contributions.
6. Fill `docs/maintenance/defect-candidate.example.json`, then run
   `upstream.py prepare`. Review every byte of the resulting public `issue.md`
   and retained attachments. Validation is structural, not proof or permission.
   The user's instruction authorizes the agent to submit a qualified report;
   no additional approval ceremony is added here.
7. The agent submits through the GitHub connector, or runs `upstream.py submit
   PACKAGE --publish` with an already authenticated `gh`. The helper checks for
   its fingerprint in the target's issues before creating, checks authenticated
   access first, and writes a durable local receipt with URL/body hash. It makes
   at most one create call per invocation. On an ambiguous network result, inspect
   the remote before any retry; do not blindly create again. A genuine preexisting
   issue uses the configured `existing_issue_url` and is not duplicated.
8. Record upstream URL/ID, submission time and exact body hash in the next watch
   result. Follow maintainer triage and fixed/backported versions, then separately
   validate our source, rebuilt binaries and environment. Do not call a report
   upstream-confirmed until upstream actually confirms it.

The publication helper is optional transport, never an autonomous judge. It does
not accept local discovery reports as submission candidates, auto-upgrade their
classification, or post from scheduled read-only monitoring. Reporting a patch
instead of an issue additionally requires the target's tests and PR conventions.

### Candidate package commands

Place the completed candidate next to `reproducer.py`, `run-1.json`, and
`run-2.json`. Each replay record has this shape (identities/dates must reflect
actual separate executions; the example is not evidence):

```json
{
  "execution_id": "unique-retained-execution-id",
  "executed_at": "actual UTC timestamp",
  "evidence": "ActualUpstreamReproduction",
  "violation": true,
  "reproducer_sha256": "SHA256 of the exact reproducer.py bytes",
  "command": "exact bounded command, including flags",
  "environment": "upstream version, compiler/runtime, architecture and relevant features",
  "expected": "independently justified result",
  "actual": "retained observed result"
}
```

```sh
python scripts/defect_discovery/upstream.py prepare /path/to/candidate.json --out /path/to/new-package
python scripts/defect_discovery/upstream.py submit /path/to/new-package
# After agent attribution, deduplication, and public-content review:
python scripts/defect_discovery/upstream.py submit /path/to/new-package --publish
```

The command without `--publish` is local and makes no network request. Publication
requires `gh` already authenticated with the intended account; the script never
installs credentials or broadens permissions. Keep the package and its
`SUBMISSION.json` in the task's durable evidence store or repository. In a failed
create attempt, `SUBMISSION_ATTEMPT.json` deliberately blocks an automatic repeat.
Two parallel agents can still race across different packages before GitHub search
indexes a new issue; assign one publishing owner per target/fingerprint. Do not
claim globally exactly-once delivery from a search-based deduplication mechanism.

Authored by ChatGPT (OpenAI), submitted through Mingli Yuan's GitHub account as
an authorized proxy. Account ownership is not personal authorship, endorsement,
technical review, or a correctness claim.
