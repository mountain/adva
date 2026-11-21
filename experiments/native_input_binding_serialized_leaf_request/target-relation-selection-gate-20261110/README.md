# Target relation-selection gate, 2026-11-10

**Finite result: `PassedFiniteRelationSelectionGate`.** This refines the
problem statement after an independent rereading of the 2026-11-09 proposed
adapter contract. It does not implement or execute a native receiver.

Main remains at
[`17e1842addcd9f9262eef87bd19c5eabcdc843e1`](https://github.com/mountain/adva/commit/17e1842addcd9f9262eef87bd19c5eabcdc843e1).
Draft PR #232 retained the predecessor at
[`2d5b6c18a7446d4f0aa3834c521cd7ad57a600a8`](https://github.com/mountain/adva/commit/2d5b6c18a7446d4f0aa3834c521cd7ad57a600a8)
before this continuation.

## Dependency correction

The predecessor v0 contract usefully required two diagram slots, qualified
endpoints and explicit outcome residuals. Its checker, however, only compared
each `relation` declaration with another declaration copied from the same JSON.
A coherent change to path, source, occurrence, diagram digest or request digest
could therefore preserve structural acceptance without showing that any actual
native endpoint existed. Its phrase `exact tuple equality` also obscured two
different judgments:

1. same-side binding of an independently request-pinned selector to one actual
   occurrence record; and
2. a separately selected binary relation on the two resolved endpoints.

The review input is recorded in [`review-input.json`](review-input.json). Its
33,689-byte archive has SHA-256
`645a897ccad15a9fd5fb0c3938d5a604bb34adebf52a1282fc3185adbb232926`.
The review was an independent rereading by Codex, not a different team/model,
formal proof or Mingli Yuan endorsement. This continuation does not repeat its
seven declaration probes or sixteen model cases.

The native type reference is decisive for one narrower correction:
[`OccurrencePath`](https://github.com/mountain/adva/blob/2d5b6c18a7446d4f0aa3834c521cd7ad57a600a8/crates/adva-ir/src/ids.rs#L45-L55)
is a transparent `Vec<u32>` and its root is `[]`. The predecessor's
`"output/0"` and `"input/0"` strings therefore cannot silently stand for this
type. A boundary port, if needed, must be a separate typed selector with its
own checked incidence.

## Frozen question and interface

The frozen [`contract.json`](contract.json), SHA-256
`e3bf3d8c735ad9d9fbb8a37af1c4a7801bc12a80b39f378999460c0fc52ed8f5`,
asks whether a finite gate can separate:

- `Bind_left` and `Bind_right`: each complete expected selector must equal one
  complete actual occurrence record on its independently admitted diagram;
- `PinnedPairMembershipV1`: the deliberately weak claim that both specified
  occurrences were located; and
- `CertifiedRelationV1`: a named relation requiring its own pinned checker,
  claim, evidence, parameters and quantifier/domain.

The proposed boundary is
[`relation-gate-v1.json`](relation-gate-v1.json), SHA-256
`a391a1087da1ddea4ea11531f8a94a115c2a5e5211aa156b70a363312885bbae`.
An absent relation, unavailable checker/evidence or failed receipt persistence
must remain `Unknown`. A checked binding mismatch, malformed path, invalid
witness or scoped false decision may be `Refused`. `Accepted` requires the
selected claim to pass and its receipt to be durably recorded.

No arithmetic is evaluated. Additive `A-B=0` and multiplicative `A/B=1` remain
separately typed; the latter retains all nonzero, invertibility and definedness
guards. At `A=B=0` quotient cancellation is undefined. Scalar equality cannot
erase identity, order or history.

## New-instance reuse and finite result

The eight exact inputs and expected outputs are in
[`cases.json`](cases.json), SHA-256
`2a9394713e425c278fb1d812820b62c996eda51cfc054321c4c653baa1589471`.
They use a new instance in which the two serialized diagram digests are equal,
while slots, contexts, sources and occurrences remain distinct. This tests that
byte equality neither identifies the endpoints nor prevents a weak
pair-membership result.

All 8/8 cases matched their predeclared outcomes:

| Case | Outcome | Exact boundary |
| --- | --- | --- |
| same digest, distinct slots, exact membership | `Accepted` | `QualifiedPairLocatedOnly`; no cross-side semantic claim |
| target relation not selected | `Unknown` | `TargetRelationUnderspecified` |
| actual root path changed from `[]` to `[1]` | `Refused` | `EndpointBindingMismatch` |
| same-value different-origin substitution | `Refused` | `EndpointBindingMismatch` under the unchanged request |
| certified checker unavailable | `Unknown` | `RelationCheckerUnavailable` |
| applicable certified checker returns false | `Refused` | `CertifiedRelationFalse` in that scope only |
| certified result true but record fails | `Unknown` | `ReceiptPersistenceFailure` |
| boolean used as a `u32` path item | `Refused` | `MalformedOccurrencePath` |

The exact retained output is [`outcome.json`](outcome.json), SHA-256
`70e4bc427a726c1d91f33a3457fe069549f6ec9a31905c006a40f0c85ca89b99`.
There were zero search candidates/nodes, opaque-request reads, diagram-byte
reads and native executions. No correction replay occurred.

| Measured stage | Cost |
| --- | ---: |
| finite evaluation before serialization | 375,619 ns |
| result serialization measurement | 145,800 ns |
| outer wall clock | 0.03 s |
| outer user / system CPU | 0.02 s / 0.01 s |
| process maximum RSS | 9,088 KiB |
| final stdout | 3,515 bytes |

Maximum RSS is Linux `RUSAGE_SELF` for the one Python process, not a process-
tree or system peak. Review reading, interface construction, report writing,
repository checks and upload time were not instrumented. File sizes are not
used as memory estimates.

## Replay and interpretation

From this directory:

```sh
timeout 30s python -B run_check.py
```

The runner imposes 10 seconds CPU, 256 MiB address space and 1 MiB output caps.
`evaluate.py` and `run_check.py` have SHA-256 values
`370820de880faf6b5d28bb25e9aa035ce525d70eb81bef9bad9045e5a093cf70`
and `3729db79a246f9abdd30e262d01542d287b77dd020ec78fb77f5861617180862`.

No word is formed or revised. `PinnedPairMembershipV1`,
`CertifiedRelationV1` and `relation-selection gate` are proposed interface
labels, not learned mathematics or native built-ins. This result corrects the
contract boundary without claiming greater expressivity or lower solver cost.

The real target relation remains unspecified. Rust diagram admission, actual
request-to-selector mapping, a pinned relation checker, native controls,
receipt persistence, independent human review and real-user utility remain
open. Research 0090 coverage is incomplete, so Research 0092 promotion remains
blocked. Pair membership, equal digests, equal scalar values and local-image
equality do not produce source transport, M6, native `free`/`Close`, arithmetic
universality or hypothesized arithmetic truth.

The result helps Mingli Yuan and later implementers avoid strengthening a
locator certificate into an unspecified transport theorem. It also gives
Jiamin Zhao and reviewers a precise reason why some failures are `Unknown`
rather than negative mathematical evidence. The smallest continuation is a
human or task-owner decision selecting C: either the weak pair-membership claim
or one exact named relation with its checker and evidence. Only then should a
Rust adapter be implemented and the corresponding native controls run.

Original contract refinement, evaluator and report by Codex (OpenAI), offered
under Unknown v0.3 and submitted through Mingli Yuan's GitHub account as an
authorized proxy. Account ownership is not authorship, review, endorsement or
a correctness guarantee.
