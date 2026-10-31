# Serialized leaf requests bind each fresh native instance separately

## Status

Passed finite calibration. This research-only result separates reuse of a
receiving relation from transport of an old native identity. It is not a stable
request profile, an alpha-renaming theorem, a learned word, or evidence for M6
closure, arithmetic universality, hypothesized arithmetic truth, or universal
grammar.

The run starts from merged `main`
`a6872d1f6a1c767757b3d0cf696fe029a61b1d2a`, which contains the finite
serialized-leaf boundary from PR #228. The pre-execution contract is
[`fresh-instance-contract-20261028.json`](../../experiments/native_input_binding_serialized_leaf_request/fresh-instance-contract-20261028.json).

## Frozen question and objects

The sole route holds the typed zero-event body
`(frontier (use static) (use dynamic))`, canonical `Rational::ONE`, one
external leaf tuple, the version-zero JSON grammar, the Rust importer, the
native receiver, a 65,536-byte request limit and 512 structural units fixed.
It compiles exactly two instances:

1. module `native-binding`; and
2. independently parsed, linked and compiled module `native-binding-fresh`.

Their bodies, rational parameter, node count and occurrence count agree. Their
qualified source and residual function identities differ by construction. The
two fixed judgments are:

- an encoded request from the original module presented with all current
  objects from the fresh module must be `Refused("serialized source or residual
  snapshot mismatch")`; and
- a request serialized from the fresh module and presented with that same
  module's artifacts, certificate and expected request must be `Certified`.

There is no search and no additive-zero or multiplicative-inverse judgment.

## Result

Both judgments passed. The original request was imported successfully, but its
complete source/residual snapshots could not repin the fresh module. The fresh
instance then serialized its own complete diagrams and qualified occurrence
pair and the unchanged receiver returned its own certificate.

This supplies one new-instance reuse test for the receiving relation. It also
gives a replayable refusal against the stronger interpretation that an old
request transports identity merely because body shape, types and rational
parameter agree. It does not establish that every distinct module is fresh,
nor that same-name recompilation, arbitrary renaming or an independently
specified correspondence is safe.

The exact candidate source SHA-256 is
`a09c10d5c654d7d96feafb7789356366b696c128d79a3e57611a44d41970b79b`.
The bounded workflow is
[run 40711843054](https://github.com/mountain/adva/actions/runs/40711843054).
Its native job passed published and staged formatting, locked Clippy, 13 native
input-binding tests, 6 diagram-import tests, 2 graft tests and 19 process tests.
The whole-cut companion passed 1,110 Bootstrap Zero tests. Publication-boundary
validation also passed on this head.

## Costs and retained limits

- Routes: one; search candidates and search nodes: zero.
- New receiving calls: two. The mismatch is refused before the underlying
  structural receiver; the matching fresh request reaches that receiver with
  512 supplied units and is certified.
- Implementation correction replays: one, used only for two retained
  `rustfmt` line-wrap differences. The first attempt performed no compilation
  or receiving call.
- Clippy: 15.44 seconds.
- Test build: 8.46 seconds.
- Reported test execution: 0.00 seconds for 6 importer tests, 0.00 seconds for
  2 graft tests, 0.03 seconds for all 13 native input-binding tests and 0.19
  seconds for 19 process tests.
- Bootstrap Zero companion: 1,110 tests in 3.00 seconds.
- Both serialized requests were asserted below 65,536 bytes, but exact byte
  lengths were not printed by the frozen workflow.
- Construction, serialization, refusal validation and fresh certification
  times were not separately measured inside the 0.03-second test-file total.
- Peak memory was not reported. Artifact size is not used as a memory proxy.

Complete CI and machine-dependency continuity are integration checks, not
mathematical premises. Their state is reported separately from this bounded
result rather than used to enlarge it.

## Vocabulary and utility

No word is formed or revised. Existing terms—complete snapshot binding,
qualified occurrence, `Certified`, `Refused`, and `Unknown`—express the result.
The proposed `arithmetic-universality` and `hypothesized-arithmetic-truth` words
from Research 0123 remain Proposed.

For Mingli Yuan and later agents, the calibration prevents a useful receiver
from being misreported as an identity-transport theorem: a fresh instance may
reuse the relation only after binding its own complete request. It leaves an
exact failing request and a matching positive request for independent replay.
No measured value to Jiamin Zhao's real tasks is claimed.

Research 0090 coverage and dependent Research 0092 promotion remain open.
Local image equality still creates no M6 filler; native `free`, authentication,
persistence and general communication remain outside this result.

## Smallest continuation

Persist one matching fresh request as canonical bytes and let a second Rust
process independently compile the exact same named module and receive those
bytes. The next contract should distinguish process-boundary replay from module
renaming, keep the importer and receiver unchanged, and stop at `Refused` or
`Unknown` rather than introducing an implicit identity correspondence.

Authored by GPT-6 Codex, submitted through Mingli Yuan's GitHub account as an
authorized proxy. Original first-party work contributed under Unknown v0.3;
account use is not his authorship, review, endorsement or a correctness claim.
