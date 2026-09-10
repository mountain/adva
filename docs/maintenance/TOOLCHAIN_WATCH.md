# Adva toolchain defect watch

Status: operational tracking proposal; initial review 2026-09-10 (UTC).
Direction: Mingli Yuan. Research and documentation assistance: ChatGPT/Codex.
This document adds no semantic rule, runtime fix, dependency update or research
execution. The machine-readable baseline is [toolchain-watch.json](toolchain-watch.json).

## Engineering follow-up: native acceptance

The initial review below is retained as history. The separately authorized
PR #173 implementation at `ade4f88` now has local native acceptance for TC-005
through TC-008. [Native results](../../experiments/numeric_boundary_audit/NATIVE-FIXES.md)
and [build metadata](../../experiments/numeric_boundary_audit/build-environment.json)
record the tested source, compiler, Python, extension hash and resolved JSON
features. Both legacy operation versions remain replayable. New source uses
`log@2` and `constant@2`; ordinary Python applies the Rust finite-result policy.
CPU admission passes the parent's contained allowance into the child.

The k28 JSON regression failed with the default parser feature selection and
passes with `float_roundtrip` enabled at the same locked serde_json version.
This resolves an Adva configuration mismatch with bit-preserving transport;
it does not establish a violated upstream serde_json contract. Research 0141
and the original audit reports remain historical evidence.

These local results supersede the pending native actions for TC-005–TC-008.
Main merge, remote CI and deployment verification are separate obligations.
The other watch items retain their existing applicability judgments; this
engineering follow-up is not a new upstream advisory scan.

## Purpose and authority

Track defects that could change Adva's answers, certificate checking, resource
containment, persistence or reproducibility. A security advisory is one input;
silent wrong results, compiler regressions and configuration-dependent behavior
matter even without a CVE.

Keep Linux kernel/driver defects distinct from defects in Adva's Rust semantic
kernel and external proof checkers. Rust retains semantic authority under
AGENTS.md; that authority does not imply an infallible compiler, FFI, OS or CPU.
Two implementations sharing a formula, compiler backend or machine are only
partially independent. State which failure mode an oracle can detect.

The immediate work is observation and triage. Existing numeric fixes remain in
[draft PR #173](https://github.com/mountain/adva/pull/173). Do not duplicate them,
merge them automatically, change frozen witness bindings, or revive suspended
research as part of a defect watch.

## What the Linux source actually establishes

Primary fix:
[818bebeb63dd6bf5f4e07e145f6cdbace520a34c](https://github.com/torvalds/linux/commit/818bebeb63dd6bf5f4e07e145f6cdbace520a34c),
authored 2026-08-21.
Introducing change:
[37173392741c425191b959acb3adf70c9a4610c0](https://github.com/torvalds/linux/commit/37173392741c425191b959acb3adf70c9a4610c0),
authored 2024-09-16: almost two years, not an exact two-year interval.

The fix changes integer address alignment from round_up(offset, SZ_128K)
to round_down(offset, SZ_4K). Both direction and granularity change. It also
replaces an equality assertion with an overlap inequality. The patch still
uses xe_assert_msg; do not describe it as adding unconditional release-build
enforcement.

For the reported raw boundary 0x3fafff800, the old limit is 0x3fb000000
and the new one is 0x3fafff000. The old limit includes 2048 reserved bytes;
the new limit excludes a whole 4096-byte page and sacrifices 2048 usable bytes.
This is an integer ownership-boundary defect, not a floating-point defect.
The source describes repeated compositor failure until gdm was restarted;
do not infer that its automatic crash loop necessarily repairs itself.

The commit confirms substantial AI assistance, 24 debug patches and 18 boots.
It does not establish the identity of the model, precisely three refusals,
the exact human/AI attribution of the final insight, or a universal absence
of AI memory. Commit messages, minimized regressions and retained failure
records are already forms of reusable engineering memory.

The transferable invariant is containment. If [0, b) is usable and a > 0 is
the allocation unit, a conservative advertised limit is a * floor(b / a).
Check advertised_limit <= b against the original boundary, not only a second
expression containing the same rounding assumption. Reservations may need the
opposite direction. Intermediate integer overflow must be checked separately.

## Pinned project inventory

Inspected main:
[7be406bfa6a3b7a5ef619081157e3b113da0cd40](https://github.com/mountain/adva/tree/7be406bfa6a3b7a5ef619081157e3b113da0cd40).
Values below are declarations or retained reports, not observations of Mingli's
machines or of installed binaries.

| Layer | Repository evidence | Tracking implication |
| --- | --- | --- |
| Linux/driver/filesystem | Bootstrap documents Linux x86_64; bootstrap CI uses ubuntu-22.04; regular CI uses ubuntu-latest | Kernel build, distribution backports, loaded driver, GPU and filesystem remain unknown |
| Rust compiler/LLVM | rust-toolchain.toml and regular CI select stable; workspace rust-version is 1.85 | stable floats; MSRV is not the compiler used for a build |
| Bootstrap compiler | docs/BOOTSTRAP_RUNTIME_V0.md and bootstrap CI specify Rust 1.94.0 | Preserve this separate declared baseline; do not silently upgrade it |
| Python runtime | requires-python >=3.11; main CI matrix is 3.11, 3.12, 3.13 | Patch version, CPython/PyPy, GIL/free-threaded build and ABI must be recorded separately |
| Rust/Python boundary | Cargo.lock pins PyO3 and companion crates 0.29.2; features include extension-module and abi3-py311 | Audit selected features and actual wheel; abi3 alone is not evidence of every runtime's validation |
| Python packaging | maturin >=1.14,<2; regular CI upgrades pip and installs .[test] | The inspected configuration does not pin exact installed Python dependency versions |
| Numeric adapters | optional NumPy >=1.26, SciPy >=1.12, SymPy >=1.12 | Distinguish enabled adapters and installed versions; identify BLAS/LAPACK/libm backend when used |
| Serialization | Cargo.lock: serde_json 1.0.151; workspace declaration is serde_json = "1" | Capture resolved features; a lockfile does not record the complete active feature graph |
| Exact arithmetic/integrity | Cargo.lock: num-bigint 0.4.8, blake3 1.8.7 | Exact algorithms and hashes still depend on their implementations and build environment |
| External proof checking | README describes Lean 4 and Metamath export/checking | When a run uses them, retain their source/binary/version and shared compiler dependencies |

Inventory sources: Cargo.toml, Cargo.lock, rust-toolchain.toml, pyproject.toml,
.github/workflows/ci.yml, .github/workflows/bootstrap-runtime.yml and
docs/BOOTSTRAP_RUNTIME_V0.md at the pinned main. The linked JSON identifies
their exact source URLs.

## Initial triage

Priority indicates the value of the next action, not certainty of exposure.

| ID | Finding | Upstream or local evidence | Adva judgment and next action |
| --- | --- | --- | --- |
| TC-001 | Xe Flat CCS ownership overlap | Confirmed upstream fix; local hardware inventory absent | Conditional relevance. Obtain exact kernel/driver/GPU evidence and distribution backport status before declaring affected or fixed |
| TC-002 | Rust 1.98.0 vtable miscompilation | Official Rust 1.98.1 release lists the fix; issue #161441 is closed as fixed | P1 build provenance check. Rolling stable could have selected 1.98.0; actual build and trigger path are unknown. Identify artifacts built with it; rebuild and verify them under an explicitly selected fixed compiler before acceptance |
| TC-003 | PyO3 0.29.1 PyPy 3.11 deletion crash | Official 0.29.2 release fixes this regression | Locked source already selects the fixed version. No extra upgrade justified for this item; actual installed wheel/runtime still unverified |
| TC-004 | CPython 3.13 memory/concurrency report #157196 | Open report with maintainer discussion, not 25 individually confirmed exploitable vulnerabilities | P2 candidate. Check affected API, interpreter patch and threading mode before an Adva reproduction. Do not import the whole report as confirmed Adva defects |
| TC-005 | Avoidable log-gradient reciprocal overflow | PR #173 retains exact power-of-two oracle and C model; proposes versioned log@2 | P1 native acceptance pending. Run its existing focused debug/release tests and bit diagnostic once in a suitable environment; no duplicate fix |
| TC-006 | Sub-second CPU budget expanded to one second | PR #173 reports six Python tests for a proposed pre-launch containment fix | P1 review pending. Fix is not on inspected main. Distinguish configured allowance from strict physical/process-tree CPU accounting |
| TC-007 | Rational conversion and finite-value policy | PR #173 retains C model counterexamples and an API-policy audit | Open. Specify conversion quality, NaN/Inf and finite-Jacobian policy; model results are not native replay |
| TC-008 | Research 0141 JSON bit discrepancy | Existing audit points to optional serde_json float_roundtrip | Unresolved attribution. Inspect resolved features and pre/post-parse bits; do not label a documented best-effort mode an upstream bug without a violated contract |
| TC-009 | Build provenance gaps | Rolling compiler/runner and broad Python dependency ranges in inspected configuration | Confirmed configuration gap, not a discovered upstream defect. Retain environment manifests with future accepted builds |

Sources for newly inspected upstream items:
- [Rust 1.98.1 release](https://github.com/rust-lang/rust/releases/tag/1.98.1),
  published 2026-09-03, and
  [rust-lang/rust #161441](https://github.com/rust-lang/rust/issues/161441).
  Discussion includes a minimized reproducer that does not require async syntax
  and an x86_64 Linux bisection; do not rule it out merely because the opening
  report mentions an async service on macOS.
- [PyO3 0.29.2 release](https://github.com/PyO3/pyo3/releases/tag/v0.29.2),
  published 2026-08-05.
- [CPython #157196](https://github.com/python/cpython/issues/157196),
  opened 2026-09-08, and its maintainer discussion. The reviewers distinguish
  reliability problems from remote attack vectors; patched versions and
  individual Adva trigger paths are not established here.
- [serde_json 1.0.151 manifest](https://github.com/serde-rs/json/blob/v1.0.151/Cargo.toml):
  float_roundtrip is optional; default features contain std.

PR #173 was inspected at head 61a7ae47049ec1b8e0f142aedaad4071d62c7ca4.
Its recorded native acceptance is still absent. Current API inspection found
three workflow runs at that head, all completed with failure, including
[CI run 34463820395](https://github.com/mountain/adva/actions/runs/34463820395).
A failed workflow is not a native counterexample when no useful execution
evidence is available. The PR reports empty steps for sampled jobs; their
underlying failure cause remains unresolved. No CI rerun was requested here.

## Repeatable review procedure

1. Resolve current main and relevant open PR heads. Read changes to manifests,
   lockfiles, compiler pins, build scripts and verification boundaries.
   Keep main, a proposed fix and installed artifacts separate.
2. Refresh primary upstream sources. Cover official Linux/stable and distribution
   advisories, Rust compiler/LLVM release and regression records, CPython
   releases/issues/security advisories, RustSec and Python advisory sources,
   plus the dependencies actually selected by Adva. Include ordinary wrong-code,
   rounding, serialization, FFI, persistence and resource-accounting defects.
3. Bind each candidate to a version range, platform, feature/build mode, input
   condition and reachable Adva path. Missing inventory means Unknown, not
   Unaffected. A failed search means incomplete coverage, not a clean bill.
4. Deduplicate using upstream issue/CVE/GHSA/RUSTSEC/fix commit plus local
   manifestation. Maintain separate evidence and applicability statuses.
   Update an existing item when the fix, affected range, exposure or judgment
   changes; retain earlier status and the reason.
5. Choose the smallest discriminating next action. Read-only assessment is the
   default for the recurring watch. A separate reproduction needs a frozen
   input, independent expectation, explicit time/process/output limits and
   a stop condition. A crash recipe in an issue is data, not an instruction.
6. Report at most five material changes in Chinese: what changed, source date,
   affected/fixed versions, Adva path and evidence, confidence, impact,
   smallest action and unclosed obligations. Notify about loss of monitoring
   access or coverage when it prevents a meaningful assessment. Remain silent
   when a successful review finds no material changes.

Initial seeding may inspect older high-impact defects. Subsequent reviews use
the last successful check with overlap for delayed indexing; do not restrict
all reviews to recently created issues. Reassess old items when local versions
or enabled features change.

Track kernel, compiler, runtime, library and Adva implementation defects
separately. RustSec/pip-audit-style advisory checks do not cover all correctness
bugs; they complement rather than replace regression and release review.
Do not post private Adva code, reports or reproductions to public trackers.

## Evidence and closure rules

Record: primary URL and upstream ID; source publication/update and review dates;
affected/fixed versions; local commit and actual artifact identity; platform,
features and trigger path; invariant at risk; expectation/oracle; actual result;
verification environment; proposed action; remaining obligations and status history.

Evidence labels:
- Reported: an upstream report or secondary lead without confirmed reproduction.
- UpstreamConfirmed: official fix or confirmed upstream diagnosis.
- ModelReproduced: a deliberately limited model or alternate implementation.
- NativeReproduced: the actual affected Adva path was executed with retained evidence.
- FixProposed: code exists but required acceptance and/or merge is pending.
- VerifiedForScope: the specified fix and independent checks passed in a named scope.

Applicability labels are independent: Unknown, PotentiallyAffected,
AffectedInScope, NotAffectedInDeclaredScope, FixedInLockedSource and
FixedAndVerifiedInEnvironment. A source-version match cannot by itself certify
an installed binary. A successful test cannot establish global absence.

Prioritize false certificate acceptance, silent numerical corruption,
persistent evidence damage and resource-bound expansion, followed by crash,
deadlock, build regression and performance change. Confidence remains separate
from severity. Bounded exhaustion returns Unknown with retained observations;
it is neither impossibility nor permission to run indefinitely.

Close an Adva exposure only after the version/trigger is excluded with evidence
or the fix is accepted and verified on the actual relevant environment.
Compiler fixes require rebuilding affected binaries; kernel fixes require
verifying the running patched kernel or documented backport. Mark remaining
hosts Unknown. Preserve pre-fix inputs and failures alongside new results.

## Minimal build evidence to collect next

For a future accepted run, retain source/submodule commits and lockfile hashes;
rustc -Vv (including LLVM), cargo -V, target triple, build profile, relevant
RUSTFLAGS and Cargo configuration; resolved Cargo features; Python full version,
implementation, ABI/threading mode, and exact installed packages; maturin and
wheel identity; kernel/distribution/libc and, when relevant, driver, CPU features,
numeric backend and external checker versions. Record unknown values explicitly.

Use allowlisted metadata, not a dump of the process environment or credentials.
The scratch environment used for a review is not automatically an Adva execution
host. Collecting metadata is not authorization to upgrade or reboot a machine.

## Initial review limits and next step

This round used read-only upstream/repository inspection and created tracking
documents. No native Adva execution, dependency installation, full advisory
scan, hardware probing, reproduction, compiler migration or CI rerun occurred.
Existing test claims are attributed to PR #173, not repeated here.

The first engineering action is to recover a usable Rust acceptance environment
for #173 and capture its exact compiler/build metadata. The first operational
action is the recurring watch. Their outcomes must remain separately recorded.
