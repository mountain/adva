# Read-only Python operator-check adapter, version zero

Date: 2026-09-10. Continues the external operator-lift receipt experiment in
PR #180, parent `d1e3c9093e263d5d16314e838ff76b197e2aece9`. Main remained
`60b37d8a4c155994acc7207f2feecc1da7cc6441`; #180 remained a draft stacked on
unmerged #179. This step changes the Python CLI's external dispatch only.

## Usable command

From a source checkout of this branch, with Linux and Python's standard library:

```sh
timeout 5s python -B -S python/adva/adva.py operator-check \
  --question experiments/golden_ratio_operator_lift/example-question.json \
  --receipt experiments/golden_ratio_operator_lift/example-receipt.json \
  --output /tmp/adva-operator-report-fresh.json
```

The output name must not exist. These two example inputs are the exact bytes
retained by the successful fresh-basis integration test. There is no Rust
build, Python package import, or source-PDF requirement for this command.
This is source-checkout integration, not a packaged standalone distribution:
the adapter requires its pinned `experiments/.../receipt.py` source.

## Division of responsibility

| Object | Responsibility |
| --- | --- |
| Local question | Receiver-selected version, label and exact rational context |
| Incoming receipt | Submitted observations, preserved as received |
| Pinned external checker | Inverse, basis, ordered-word replay, residual and coverage checks |
| Python adapter | Byte retention, local context selection, one bounded invocation, output protocol and fresh report |

The local question schema is `adva.external.operator-question.v0` with fields
`schema`, `question_id`, and `context`. Its context follows the preceding
receipt schema. The label is a local string, not a Rust identity. The adapter
computes the expected context fingerprint from this local file, never from
the receipt's self-declared fingerprint. Mathematical validity of the context
still passes through the external checker; the receiver remains responsible
for choosing a context that represents the intended real question.

The checker source must match SHA-256
`263fa9048e663024ffb6c6f393a2e9a1ed93208f966778c2dc33761ea10db10e`.
Both checker bytes and incoming bytes are copied to private temporary files
before execution. Thus the invoked checker and input are the snapshots that
were recorded, rather than subsequently reread original paths. Updating this
pin requires another explicit review. This is a trusted local backend, not
a sandbox for arbitrary third-party code or an authentication system.

The report keeps exact Base64 input bytes, lengths and byte digests, the local
context fingerprint, raw checker stdout/stderr, its exit code and result, and
execution costs. Byte identity and canonical context equality are separate:
whitespace may change the former while preserving the latter. No normalization
replaces retained receipt bytes. Inputs are never written by the command.
Oversized, unreadable and symbolic-link inputs are refused before execution;
they are not claimed to have been completely retained.

The existing fresh-report writer installs the report without overwriting an
existing path. Input snapshots live only in a temporary directory. The saved
report is the durable replay carrier. A save error remains an error; no report
is claimed available if installation fails.

## Outcomes and limits

The adapter keeps `ClosedForAllTranslationsByLinearity`, `UnknownCoverage`,
`Refuted`, and invalid-evidence statuses distinct. Its own exit codes are 0
for scoped closure, 3 for unknown coverage/resource/execution, and 2 for other
refusals or refutations. A checker exit/status mismatch, changed result context
or native-authority escalation is a protocol error. The adapter checks the
protocol and delegates arithmetic to the pinned implementation.

Every report states `native_admission=NotGranted` and `native_free=NotGranted`.
There are no Rust certificates, semantic IDs, source-history equivalences,
M6 fillers, stable operations, or native `free`/`Seal` additions. The original
algebraic proof and receipt coverage limitations remain unchanged.

Regular input files are capped at 16 KiB each. Each request makes at most one
backend call, with a 3-second wall wait, 5 CPU seconds, 256 MiB address-space
limit, 32 KiB per output stream, and no core dump. The 5-second CPU hard limit
matches the checker, which installs that limit itself; the outer wall wait is
stricter. The adapter kills the backend process group at timeout/cleanup.
The final report cap is 256 KiB. Use the shown outer timeout to bound the
complete CLI, including local reads and persistence. No retry or fuel refill
is implemented. Process peaks are not simultaneous combined memory figures.

## Retained integration evidence

The [run contract](../../experiments/golden_ratio_operator_lift/adapter-contract.json)
was frozen before execution. The first attempt encountered one implementation
error in **test fixture selection**, after seven CLI invocations and six
backend calls: an existing `oversized-input` fixture consisted of spaces, but
the suite tried to parse it to obtain a local question context. It failed
before invoking the oversized-input case. No incorrect closure was returned.

[The failure record](../../experiments/golden_ratio_operator_lift/adapter-first-failure.json)
retains the exception, failed code digest and known execution counts. Temporary
partial reports were removed on the exception and are not claimed retained.
An [explicit correction contract](../../experiments/golden_ratio_operator_lift/adapter-correction-contract.json)
authorized one corrected fixed-suite replay with aggregate caps of 17 CLI
calls and 12 backend calls. It did not weaken the checker or acceptance rules.
No second correction or further replay was attempted.

The corrected [evidence](../../experiments/golden_ratio_operator_lift/adapter-evidence.json)
passes **13 checks**:

- actual CLI: fresh nonstandard basis, whitespace-only change, changed
  self-rehashed operator against the old question, missing direction,
  third-direction counterexample, and forged residual;
- input boundary: malformed local question, oversized input, symbolic link;
- persistence: existing output is refused and remains byte-identical;
- protocol boundary: changed backend context, granted native authority, and
  mismatched exit code are rejected.

The successful bounded-input cases compare both original files after execution
and decode report Base64 back to their exact bytes. UnknownCoverage remains
unknown through both checker and CLI. All reports deny native authority.
There is no exhaustive filesystem/concurrency or operating-system isolation
claim; the input evidence describes the bytes actually read.

The corrected suite took 655.383 ms before final serialization/write, comprising
10 CLI invocations and 6 backend calls. Serialization plus JSON round-trip took
0.604 ms; the suite peak RSS was 12,928 KiB. The first failed attempt's tool
wall measurement was 576.089 ms; finer first-attempt timings are unavailable.
Total attempts made 17 CLI invocations and 12 backend calls, with zero search
candidates. Final write, research, coding and network time were not separately
measured. Timing is not a speedup claim.

Reproduce the integration suite with a fresh output path:

```sh
timeout 20s python -B -S experiments/golden_ratio_operator_lift/check_adapter.py \
  --output /tmp/operator-adapter-evidence-fresh.json
```

The retained correction count refers to this research session's history;
rerunning that script does not recreate the historical failed attempt.

## What this step establishes

The arithmetic receipt can now enter the existing Python CLI with a separately
selected question and a byte-preserving result. It supports the intended
separation of question selection, arithmetic verification, and boundary
transport. It does not establish a universal language or real-task value for
Jiamin.

The next engineering step is to validate this branch in the ordinary repository
environment and resolve #179's existing integration prerequisites, before
considering merge. A future native importer remains a separate decision;
the present external result must not be silently promoted while integrating.
