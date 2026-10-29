# Serialized leaf cross-process replay boundary

Date: 2026-10-29  
Status: finite experiment on draft PR #229; not merged  
Frozen contract: `experiments/native_input_binding_serialized_leaf_request/process-replay-contract-20261029.json`  
Outcome: `experiments/native_input_binding_serialized_leaf_request/process-replay-outcome-20261029.json`

## Dependency and status reading

The repository reading was frozen at main commit
`a6872d1f6a1c767757b3d0cf696fe029a61b1d2a`. PR #228 is merged. PR #229
was the only open pull request and remained a mergeable draft; this run extends
that same isolated branch. `AGENTS.md`, the research engineering agenda,
`docs/claims.toml`, Research 0090, 0092, 0118, 0121, 0122 and 0123, and the
predecessor serialized-leaf reports were reread before execution.

The dependency classification is unchanged:

- merged results include the native finite structural receiver and the
  complete finite whole-cut boundary through PR #228;
- PR #229's serialized external-leaf request and fresh-instance controls are
  unmerged finite experiments;
- `arithmetic-universality` and `hypothesized-arithmetic-truth` remain Proposed
  words from Research 0123, not proved mathematics;
- Research 0090 coverage remains incomplete, so Research 0092 all-fillings
  closure and vocabulary promotion remain blocked;
- local image equality remains insufficient for an M6 filler.

## Frozen question

Can a request emitted as canonical UTF-8 bytes by one Rust process be received
by another process that independently recompiles the exact same named module
and source, while two nearby substitutions remain refused?

The exact module is `native-binding-process`, the source body is
`(frontier (use static) (use dynamic))`, the arithmetic value is canonical
`1/1`, and the external leaf tuple is
`(s-KX-L, occ-KX-L, t-KX-L, tocc-KX-L)`. The native and residual signatures
remain respectively `Real, Real -> Real, Real` and `Real -> Real, Real`.
Additive zero, multiplicative inversion, noncommutative algebra and new
arithmetic laws are not exercised. Existing occurrence paths, ordered wires
and history are checked by the unchanged receiver.

One route was allowed: one emitter child and three receiver children, each with
a ten-second deadline. The request limit was 65,536 bytes, the matching
receiver was given 512 structural work units, search was fixed at zero, and
one implementation-correction replay was reserved.

## Construction and result

The parent test starts a producer child. That child independently compiles the
frozen named module and writes the resulting serialized request to a temporary
file. The parent reads those exact bytes only to construct a same-length
profile mutation. Three fresh test-harness children then compile their own
artifacts and read a file:

| Receiver | Input | Result |
|---|---|---|
| same name and source | producer bytes | `Certified` |
| renamed module | producer bytes | `Refused("serialized source or residual snapshot mismatch")` |
| same name and source | profile `v0` changed byte-for-byte to `v1` | `Refused("serialized request profile mismatch")` |

The accepted child does not reconstruct identity from bytes. It recompiles the
declared source and the existing receiver requires both imported canonical
diagrams to equal those independently supplied current artifacts. The renamed
control shows why the same local graph shape is insufficient. The profile
control shows that snapshot agreement cannot bypass the request schema.

This is a successful finite process replay, not a theorem about arbitrary
processes, machines or implementations.

## Correction retained rather than hidden

Commit `fe9b1bd29c75330813f4cc071f62382efffeebdc` passed every semantic
assertion, but it launched each worker through GNU `timeout`. Four timeout
supervisors plus four test workers meant eight descendant process instances,
which violated the frozen four-child accounting. That run is classified as
`ImplementationResourceAccountingFailure`; it is not admitted as the result.

The sole permitted correction removed all wrapper processes. At valid commit
`28a1f431522bf9f2a52475ccfaa0ea174d60cb0f`, the parent launches exactly four
test children, polls each direct handle, and kills it only if its ten-second
deadline expires. No mathematical expectation, source object, byte mutation,
receiver or budget was changed.

## Verification and measured cost

The corrected bounded workflow run
[`40890515988`](https://github.com/mountain/adva/actions/runs/40890515988)
passed formatting, unchanged-lock Clippy, the selected Rust regressions, and
the Bootstrap Zero replay. Its native job
[`123505722490`](https://github.com/mountain/adva/actions/runs/40890515988/job/123505722490)
records:

- 14 native-certificate tests passed in 0.06 seconds, including the process
  replay;
- 41 selected Rust tests passed in 0.25 seconds across the four suites;
- Clippy completed in 9.89 seconds and Rust test compilation in 7.38 seconds;
- 1,110 Bootstrap Zero tests passed in 2.98 seconds;
- the valid native job occupied about 34.087 wall seconds including setup,
  checkout, toolchain and cleanup;
- exactly four direct test children were launched; search candidates were zero;
- the matching receiver received a 512-unit structural allowance; exact
  consumption was not measured, and both negative controls refused before the
  structural receiver;
- exact request length, serialization/file-I/O phases and peak memory were not
  measured. The request was asserted strictly below 65,536 bytes. File size is
  not reported as memory.

The invalid first native job occupied about 50.111 seconds and started four
timeout supervisors plus four workers. Across both attempts the recorded
native-job wall is about 84.198 seconds. Publication checks passed. Machine
dependency and full CI were still running at the evidence checkpoint and were
not repeatedly awaited. The preceding PR-head full CI had one inherited
Python 3.11 Java-constructor timeout while Rust and Python 3.12/3.13 passed;
that separate integration residual is neither repaired nor attributed to this
experiment.

## Vocabulary and utility

No new word is proposed. Existing terms already express the useful boundary:
serialized request binding, exact source/residual snapshots, refusal, Unknown,
and process-scoped replay. Naming a synonym would not add expression power.

For Mingli Yuan and later agents, the result supplies a replayable distinction
between "the same bytes were accepted twice by one in-memory construction" and
"a fresh process rebuilt the same declared object and checked those bytes."
It also preserves the nearby renamed-instance and profile-substitution
rejections. For Jiamin Zhao, practical task value remains unmeasured; this is
process reliability evidence, not demonstrated application benefit.

## Residuals and next step

Both producer and consumer remain instances of the same test binary, Rust
implementation, compiler, dependency graph and host. There is no independent
implementation, authenticated producer, hostile-child containment,
cross-machine result, crash recovery, power-loss result or distributed
consistency. Nothing here establishes native `free`, Close, M6 closure,
Research 0090 coverage, Research 0092 promotion, arithmetic universality or
hypothesized arithmetic truth.

The smallest continuation is to keep this exact one-request family but replace
the consumer test mode with a separately compiled consumer executable whose
source coordinate is pinned independently of the producer. The renamed and
profile controls should remain unchanged; no larger case family is needed.
