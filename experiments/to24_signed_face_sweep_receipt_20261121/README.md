# Bounded A3 signed face-sweep receipt

Date: 2026-11-21

## Frozen question

Can the two seven-rewrite paths newly merged in
`docs/research/to24-reduced-expression-boundary.md` be independently checked
as one signed fourteen-face cellular boundary while retaining the occurrence
history of every rewrite, without constructing a typed comparison or an M6
filler?

The frozen contract is `contract.json`.  The exact paths and source pins are
in `input.json`.

## Dependency and claim boundary

This run is based on `main` commit
`6930599aa6132cdc5ec7165e0d1c8d8d09f3dee9` and source-note blob
`804a7f31ec73a9bdd3914359b47505e27fdca77c`.  The merged TO24 note proves the
finite signed-boundary proposition.  This directory supplies an independent,
executable finite check of that calculation; it does not promote a new global
theorem.

The repository state inspected before freezing the problem was:

- merged: the TO24 reduced-expression boundary note and its explicit two
  paths;
- open proposal: draft PR #234, including the corrected historical run pin
  `0d17fa7c7bab22a07c5ea1b919532ec32c034e46` and checkout pin
  `d80a7d46f06cd1ab1c4ec791f9424b6a83b126bc`;
- proposed vocabulary, not a theorem: Research 0123's
  `arithmetic-universality` and `hypothesized-arithmetic-truth`;
- finite evidence only: Research 0118's local transport and the searches in
  Research 0105/0106;
- still open: a common typed comparison in a target category, Q4/M6 fillers,
  the 0090 coverage dependency needed before any 0092 global closure, and
  arithmetic universality in either direction.

`AGENTS.md`, `docs/RESEARCH_ENGINEERING_AGENDA.md`, and `docs/claims.toml`
were read at their current `main` versions.  The experiment does not modify
the claim registry.  Additive-zero and multiplicative-unit types and domains
are untouched.

## Result

One route was run.  It exhaustively enumerated all `3^6 = 729` generator
words, recovering exactly 16 reduced expressions for `w0 = 4321` and 18
local rewrite edges.  Replaying the supplied paths produced exactly six Q4
and eight M6 face occurrences, each with coefficient `+1` or `-1`; their
signed edge boundary is zero.

The canonical receipt passed.  Six altered receipts were refused for the
specific expected reason, one nonlocal path was refused, and a fresh reuse on
both paths reversed passed.  In particular, reordering two occurrences
leaves the chain-only projection byte-identical but is refused by the full
receipt.  This is the finite distinction supplied by the proposed word; no
general expressivity or asymptotic efficiency claim is made.

## Proposed word: signed face-sweep receipt

- **Role:** bind a signed cellular face chain to the ordered local rewrite
  occurrences that produced it.
- **Input:** two finite reduced-expression paths with common endpoints and a
  declared Q4/M6 local rewrite grammar.
- **Output relation:**
  `VerifiedFundamentalBoundary/OccurrenceHistoryRetained`, or an occurrence-,
  face-, sign-, coverage-, locality-, or promotion-specific refusal.
- **Applicability:** every adjacent pair is a declared rank-two rewrite and
  both paths lie in the same finite A3 reduced-expression graph.
- **Witness:** the 16-vertex/18-edge graph, fourteen canonical occurrences,
  six altered receipts, one nonlocal path control, and one reversed-path
  reuse.
- **Counterexample:** an occurrence permutation with the same signed
  face-chain projection is refused as `OccurrenceOrderMismatch`.
- **Expansion/replay:** replay both galleries; derive each rank-two coset face
  from the prefix permutation; orient it from the local path difference;
  telescope the two sweeps; check all fourteen coefficients and zero edge
  boundary; retain every occurrence.
- **Refusal:** nonlocal rewrite, unequal endpoints, missing/reordered
  occurrence, wrong face/sign/coefficient, nonzero boundary, incomplete
  coverage, or any claim that the receipt itself provides a typed comparison
  or filler.
- **Residual:** no common typed comparison, native composition of relation
  witnesses, arbitrary `A_n` coherence, Q4/M6 filler, arithmetic-universality,
  or hypothesized-arithmetic-truth result is constructed.
- **State:** Proposed.

## Exact replay

From this directory:

```sh
timeout 30s python3 run.py
sha256sum contract.json input.json outcome.json run.py
```

Expected terminal status:

```text
PassedBoundedSignedFaceSweepReceipt
```

`outcome.json` SHA-256:
`5bc41bae849500d4fbd60e8d1032af088d2cc97e713ad9a0e0f152cc61dd7436`.

## Measured cost

- routes: 1;
- search candidates: 729 (below the 100,000 bound);
- receipt cases: 8, plus one nonlocal path control;
- enumeration, evaluation, and verification: 7,620,942 ns;
- canonical receipt construction: 117,033 ns;
- chain-only formation: 64,250 ns and 303 serialized bytes;
- occurrence-preserving receipt formation: 165,193 ns and 3,330
  serialized bytes;
- vocabulary formation overhead in this instance: 3,027 bytes and 100,943
  ns over the chain-only projection;
- final serialization: 239,314 ns and 8,511 bytes;
- process `ru_maxrss`: 10,624 KiB (platform-reported maximum resident set,
  not inferred from file size);
- implementation correction replays: 0.

The unavailable external `/usr/bin/time` command was not treated as a replay:
the research program had not started, and the recorded memory is Python's
`resource.getrusage` value.

## Smallest continuation

Choose one of the fourteen stored occurrences and state one typed target
category plus one comparison object for that occurrence.  Check that single
comparison against this receipt's face id, orientation, prefix permutation,
and before/after words.  A successful check remains one local typed
obligation; it must not be reported as an M6 filler or global closure.
