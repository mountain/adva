# Independent two-diagram contract revision

Integration date: 2026-11-11. **Proposed interface and finite review evidence
only; no native adapter or target acceptance.** English is the primary
integration description; the frozen [Chinese review](REVIEW.md) retains the
full argument and its original 2026-11-10 observation date.

## Problem and corrected meaning

The [v0 proposal at the reviewed commit](https://github.com/mountain/adva/blob/2d5b6c18a7446d4f0aa3834c521cd7ad57a600a8/experiments/native_input_binding_serialized_leaf_request/target-adapter-contract-review-20261109/adapter-obligation-v0.json)
uses the phrase `exact tuple equality` for an ordered pair whose two endpoints
have different roles and identities. Its Python checker compares each
declaration with a duplicate declaration in the same input; it neither resolves
native occurrences nor checks a named binary relation.

The [revised JSON contract](adapter-obligation-v1-proposed.json) separates:

1. **Same-side binding:** after independently importing the exact supplied
   diagrams, compare each actual native occurrence's complete qualified tuple
   with the independently request-bound expected selector on that same side.
2. **Selected claim:** either locate the pinned ordered pair, or check a named
   relation using its separately pinned applicable checker and evidence.
3. **Recorded outcome:** bind the request, receiver context, checker, ordered
   pair, claim, evidence, budget and permitted use on the same receiving route.

Whole left/right tuple equality is not required. The protocol slots remain
ordered and distinct; digests or ID strings may coincide or differ without
deciding semantic identity. Each selector retains its own diagram and context.
Same-value substitution against an unchanged request is refused; a separately
bound value-equality request may have a different, explicitly weaker purpose.

## A-D obligations

| Obligation | Required boundary in the proposal |
| --- | --- |
| A: request | Independently fixed original bytes/context/profile; versioned decoder; exact extraction of both diagram byte strings and selectors; checked lossless mapping for an alternate representation |
| B: two admissions | Rust admission and applicable certificates for the two actual supplied diagrams; no replacement by generated pass-through programs |
| C: binding and relation | Joint occurrence record matching, then the explicitly selected claim; individual field membership and equality of observations do not supply a relation |
| D: outcome | One bound receipt with evidence, premises, cost, residuals and purpose; successful required recording precedes emitted Accepted |

The native path is `OccurrencePath(Vec<u32>)`, including root `[]`. A textual
`input/0` or `output/0` is not implicitly converted into that type. If a boundary
port is required, it needs a separate selector and checked native incidence.
Occurrence path alone is not a globally unique lookup key. Context must be
preserved or derived by a stated, checked mapping.

The proposed relation branches have deliberately different conclusions:

| Branch | Exact scope |
| --- | --- |
| `PinnedPairMembershipV1` | Both exact caller-designated occurrences were jointly located; `QualifiedPairLocatedOnly` |
| `CertifiedRelationV1` | A named predicate under fixed profile, parameters, domain/quantifier, evidence and retained premises |

The legacy native successor establishes the first kind of membership result,
not an arbitrary transport theorem. The real target's `selected_relation`
therefore remains `null`; merging this proposal does not choose or strengthen
the target claim. No fallback from transport to value equality is permitted.

`Accepted` requires all checks for the selected purpose and a recorded receipt.
`Refused` names a checked mismatch, malformed material, failed guard, invalid
presented witness or scoped false decision; it need not refute existence of
every possible witness. `Unknown` retains an unspecified relation, unavailable
applicable checking/evidence, exhausted budget or failed receipt persistence.
An invalid submitted witness and an absent witness are different outcomes.

## Counterexamples and retained evidence

The original audit plan, program, output and manifest are frozen unchanged:

- [audit-plan.json](audit-plan.json): seven structural calls, sixteen finite
  model cases, no candidate search or native execution.
- [reproduce.py](reproduce.py): invokes the byte-pinned v0 checker and an
  explicitly defined finite mathematical model, not an Adva receiver.
- [audit-results.json](audit-results.json): original 2026-11-10 output.
- [manifest.json](manifest.json) and [sources.json](sources.json): exact bytes,
  source revisions and scope of the original package.

The seven structural calls comprise **one canonical baseline and six altered
documents**, not seven mutations. Coherent replacements of path, source,
occurrence and diagram pin, and changes to the request pin or schema, still
receive the checker's structural result. This demonstrates its declared scope,
not a native false acceptance.

The sixteen model cases include a valid relation between different identities,
wrong paths, spliced source/occurrence/path fields, equal-value unrelated
endpoints, equal local images without transport evidence, reversed order,
membership-only and value-only purposes, unavailable evidence, exhausted budget,
foreign receipts and recording failure. Their results are model judgments.
The original runtime/measurement limitations remain in the frozen report.

## Compatibility with the latest draft

At integration preflight, main was
`17e1842addcd9f9262eef87bd19c5eabcdc843e1`; draft PR #232 had advanced to
`f2406dae6851ba4c0727176d0028394a6f97a8a8`. Its
[2026-11-10 relation-selection gate](https://github.com/mountain/adva/blob/f2406dae6851ba4c0727176d0028394a6f97a8a8/experiments/native_input_binding_serialized_leaf_request/target-relation-selection-gate-20261110/README.md)
already cites this review archive and adopts the same two relation branches,
native path type and three-way outcomes. No semantic conflict was found in
that scoped comparison. The gate's eight synthetic cases are separate evidence;
they are not replayed or absorbed into the sixteen-case review count.

This standalone integration preserves the complete A-D proposal and review
inputs on main without merging the unrelated inventory/helper work in #232.
The unmerged draft's records stay at their original commit references. This
does not assert that #232 as a whole has been independently re-audited.

## Replay and continuation

From this directory, use a new output filename:

```sh
timeout 30s python3 -B reproduce.py > replay-results.json 2> replay-stderr.txt
```

The script enforces CPU 10 seconds, address space 256 MiB and regular-file
output 1 MiB. The outer timeout supplies the 30-second wall bound. Keep the
frozen result; variable timing/RSS fields are not byte-for-byte replay targets.
The separate [integration plan](integration-plan.json) bounds the one local
packaging replay; [integration validation](integration-validation.json) records
its result. No helper controls, 430-coordinate inventory or native target
checks are requested by that plan.

Next, specify C as qualified pair membership or one exact named relation and
bind that meaning to the original request. Only then implement the appropriate
Rust receiving profile and its actual positive/negative controls. The JSON is
a proposed contract document, not a JSON Schema validator or implemented API.
Native controls remain NotRun; Research 0090 coverage, Research 0092 promotion,
M6, native free/Close and arithmetic universality remain unresolved/blocked.

## Authorship and publication basis

Original review, proposed JSON and new finite model tooling: Codex (OpenAI),
offered under Unknown v0.3. This is a fresh rereading, not a different
team/model, formal verification or human technical signoff. The source snapshots
are exact first-party Adva files at the revisions in `sources.json`, retaining
their original notices; no third-party software or external research content is
vendored. The original archive was 33,689 bytes, SHA-256
`645a897ccad15a9fd5fb0c3938d5a604bb34adebf52a1282fc3185adbb232926`.

Integration authored and checked by Codex (OpenAI), submitted through Mingli
Yuan's GitHub account as authorized proxy. Account use is not his authorship,
review, endorsement or a correctness guarantee. The frozen report's statement
that it made no GitHub submission describes the earlier audit, not this later
authorized integration.
