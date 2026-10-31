# Serialized leaf separately compiled consumer boundary

Date: 2026-10-30  
Status: finite experiment on draft PR #229; not merged  
Frozen contracts: `experiments/native_input_binding_serialized_leaf_request/pinned-consumer-contract-20261030.json` and correction overlay `pinned-consumer-contract-20261030-v1.json`  
Outcome: `experiments/native_input_binding_serialized_leaf_request/pinned-consumer-outcome-20261030.json`

## Dependency and status reading

The run began from main commit
`a6872d1f6a1c767757b3d0cf696fe029a61b1d2a`. PR #229 was the only open pull
request and remained an unmerged draft. `AGENTS.md`, the research engineering
agenda, `docs/claims.toml`, Research 0090, 0092, 0118, 0121, 0122 and 0123,
and the predecessor serialized-leaf records were reread before the contract
was frozen.

The status partition is unchanged. The native finite structural receiver and
complete finite whole-cut boundary through PR #228 are merged. PR #229's
serialized request work is an unmerged finite experiment. Research 0123's
`arithmetic-universality` and `hypothesized-arithmetic-truth` remain Proposed
words, not proved mathematics. Research 0090 coverage is incomplete and
therefore does not permit Research 0092 all-fillings closure or vocabulary
promotion. Local image equality creates no M6 filler.

## Frozen question and route

Can a separately compiled Rust integration-test executable receive the exact
canonical request bytes emitted by the existing producer target when it
independently rebuilds the same named source, while a renamed module and a
changed request profile remain refused?

The one frozen request uses module `native-binding-process`, body
`(frontier (use static) (use dynamic))`, rational value `1/1`, and external
leaf `(s-KX-L, occ-KX-L, t-KX-L, tocc-KX-L)`. Native and residual signatures
remain `Real, Real -> Real, Real` and `Real -> Real, Real`. Additive zero,
multiplicative unit or inversion, and new noncommutative arithmetic laws are
not exercised. Existing ordered wires, occurrences and histories remain
checked by the shared native receiver.

Only one route was allowed: one producer target invocation followed by three
invocations of a distinct consumer target. Search was zero. Each consumer was
supplied 512 structural work units; request size was bounded by 65,536 bytes;
the workflow job had a 15-minute limit; one implementation correction replay
was reserved.

The source coordinates were pinned separately:

| Target source | SHA-256 |
|---|---|
| producer and shared receiver | `096ea35d381ed281075c2b157945a5b16cee406ba2f2ff04334917a740d80e0b` |
| separate consumer wrapper | `bb048a76b5ff5b06c7890f4f0714ca12f68f261575606cd3ae4d05a6e15f6fbb` |

The wrapper imports the shared receiver source as a Rust module. It is a
distinct Cargo test target and source coordinate, not an independently written
receiver.

## Retained invalid attempt and sole correction

Workflow run
[`41069579145`](https://github.com/mountain/adva/actions/runs/41069579145)
stopped at `rustfmt` because one wrapper call required single-line formatting.
No compilation, source-coordinate check or semantic test executable ran. The
attempt is retained as `InvalidContext`, not evidence.

The sole allowed correction changed only that layout and updated the pinned
wrapper digest. It did not change the question, object, cases, receiver,
expected outcomes or budgets. The corrected contract overlay records that no
further implementation replay remained.

## Finite result

Corrected bounded workflow run
[`41069822924`](https://github.com/mountain/adva/actions/runs/41069822924)
and native job
[`124110672838`](https://github.com/mountain/adva/actions/runs/41069822924/job/124110672838)
passed both source-digest checks and all three consumer cases:

| Consumer case | Result |
|---|---|
| same module and source | `Certified` |
| renamed module | `Refused("serialized source or residual snapshot mismatch")` |
| profile `v0` changed to `v1` in consumer memory | `Refused("serialized request profile mismatch")` |

The consumer sees only the request file and its case selector. In every case
it builds its current source, residual, proposed certificate and expected
request inside the separately compiled target. The matching result therefore
extends the previous same-binary process replay to a second compiled test
target. The two controls preserve the distinction between local graph shape,
qualified source identity and request-profile lineage.

This is a successful finite same-repository replay. It is not a theorem about
arbitrary executables or implementations.

## Actual cost

The valid route used four Cargo supervisor invocations and four semantic test
executables: one emitter and three consumers. Exact compiler subprocess count
was not measured. The route occupied about 0.908 seconds of workflow wall
time. The first consumer-target build reported 0.68 seconds; the three test
cases themselves each reported 0.00 seconds at test-harness resolution.

Unchanged-lock Clippy reported 3.73 seconds. Selected Rust compilation reported
5.41 seconds. The existing four suites passed 41 tests, including 14 native
certificate tests in 0.05 seconds; the separately launched route added four
one-test process passes. The valid native job occupied about 23.536 seconds
including setup and cleanup. The invalid native job occupied about 10.824
seconds. Bootstrap Zero replay passed 1,110 tests in 2.39 seconds.

The matching consumer received a 512-unit structural allowance. Exact
structural consumption was not measured; both controls refused before that
receiver. Exact request length, serialization cost, file-I/O cost and peak
memory were not measured. The request was asserted strictly below 65,536
bytes. File size is not substituted for memory.

## Vocabulary and utility

No new word is proposed. Existing terms already state the result: serialized
request binding, pinned source coordinate, `Certified`, `Refused` and
`InvalidContext`. A synonym would add no measured expression power, so no word
formation or reuse claim is made.

For Mingli Yuan and later agents, this record separates three claims that were
previously easy to blur: replay in one binary, replay in a separately compiled
target, and replay by an independent implementation. Only the middle claim is
added here, with both nearby refusals retained. For Jiamin Zhao, actual task
value remains unmeasured.

## Residuals and next step

Producer and consumer still share the receiver source, Rust toolchain,
dependency graph and host. There is no independent implementation,
cross-machine transport, authentication, hostile-input hardening, crash
recovery, power-loss result or distributed consistency. Nothing establishes
native `free`, Close, M6 closure, Research 0090 coverage, Research 0092
promotion, arithmetic universality or hypothesized arithmetic truth.

The smallest continuation is to freeze the current canonical request as an
opaque fixture and implement a minimal consumer that does not import the
producer test module. It should recheck only the request envelope and current
snapshot binding needed for these same three cases, under a separately pinned
source coordinate. No new arithmetic family or larger search is needed.
