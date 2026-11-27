# Bounded typed face anchor

Date: 2026-11-22

## Dependency snapshot

This continuation was frozen against Adva `main` commit
`6930599aa6132cdc5ec7165e0d1c8d8d09f3dee9`.  The required repository
instructions, agenda, claim registry, Research 0090, 0092, 0103, 0118, 0121,
0122, 0123, and the merged TO24 boundary note were reread at that commit.

The statuses are deliberately distinct:

- the TO24 note's fourteen-face cellular boundary proposition is merged and
  proved in its declared finite setting;
- draft PR #235's executable signed face-sweep receipt is an unmerged finite
  experiment; all of its remote CI, publication-boundary, and dependency
  checks passed at `16ebee2700a57cd50d1788122d4e59810a4bfe2e`;
- `arithmetic-universality`, `hypothesized-arithmetic-truth`, the predecessor
  `signed face-sweep receipt`, and the word proposed below remain Proposed;
- Research 0090 coverage is incomplete, so this run cannot authorize Research
  0092 full-filling closure or vocabulary promotion;
- a common typed comparison between the two seven-step pastings, native
  relation-witness composition, and every Q4/M6 filler remain unconstructed.

## Frozen question

Can one occurrence retained by the signed face-sweep receipt be bound to an
explicit generating 2-cell in a finite A3 computad, including exact typed
prefix and suffix whiskers, and can the checker then be reused on the other
face type without claiming a common 3-cell or filler?

The objects, types, quantifier, arithmetic domain, grammar, evaluation rules,
and budget are frozen in `contract.json`.  `input.json` pins the predecessor
and supplies one M6 occurrence and one Q4 reuse occurrence.

## Construction and result

The external research checker deterministically constructs a finite
2-computad presentation with:

- 24 permutation objects;
- 72 directed adjacent-swap 1-cell generators;
- 144 directed Q4/M6 rank-two rewrite 2-cell generators.

For an occurrence `prefix + old + suffix -> prefix + new + suffix`, the anchor
records the target-presentation digest, the exact occurrence history, the
prefix 1-path, the local generating 2-cell, the suffix 1-path, both full global
paths, and their objects.  Validation reconstructs this data and checks every
composition boundary.

The canonical M6 occurrence `121321 -> 212321` and the fresh Q4 occurrence
`213231 -> 231231` both returned `TypedLocalComparisonAnchored`.  Changed
target, wrong 2-cell, wrong object, broken suffix whisker, missing occurrence
history, and premature higher-cell controls were refused for the declared
specific reasons.

This is syntax in a declared finite external presentation.  Python did not
create or identify a native Adva semantic identity.

## Proposed word: typed face anchor

- **Role:** bind one retained rewrite occurrence to a versioned target
  computad and an explicit, whiskered generating 2-cell.
- **Input:** a signed-face occurrence, target descriptor, exact before/after
  words, and the retained prefix/suffix history.
- **Output relation:** `TypedLocalComparisonAnchored`, or a target-, object-,
  2-cell-, whisker-, history-, path-, or promotion-specific refusal.
- **Applicability:** the occurrence is one declared Q4/M6 rank-two rewrite and
  the target contains its parallel local paths with exact global whiskers.
- **Witness:** target digest, global objects, ordered prefix and suffix paths,
  generating 2-cell id, and both full boundary paths.
- **Counterexample/refusal:** changing only the target digest leaves the old
  occurrence-only projection byte-identical but is refused as
  `TargetComputadMismatch`; wrong cells, objects, whiskers, paths, histories,
  or higher-cell claims are also refused.
- **Expansion/replay:** rebuild the target, replay the prefix to the local
  source, verify the 2-cell boundary, replay the common suffix from the local
  target, then compare all stored ids and paths.
- **Residual:** no comparison of the two complete pastings, native witness
  composition, 3-cell, Q4/M6 filler, arbitrary A_n coherence, arithmetic
  universality, or hypothesized arithmetic truth is obtained.
- **State:** Proposed.

The finite discrimination is concrete: the 268-byte occurrence projection has
the same SHA-256 before and after changing the target, whereas the 946-byte
anchor refuses the changed target.  This is not a theorem of general
expressivity or asymptotic efficiency.

## Replay

From this directory:

```sh
timeout 30s python3 run.py
sha256sum contract.json input.json outcome.json run.py
```

Expected status: `PassedBoundedTypedFaceAnchor`.

Retained `outcome.json` SHA-256:
`73820f52015070238c8ed6a3da07c635373e02ebd0bcb1483660f617fff4586f`.

## Measured cost

- routes: 1;
- target nodes: 240, below the 100,000 bound;
- target formation: 1,994,651 ns;
- occurrence-only projection formation: 24,724 ns and 268 bytes;
- typed anchor formation: 104,217 ns and 946 bytes;
- word formation overhead on this instance: 79,493 ns and 678 bytes;
- fresh Q4 formation plus validation: 63,845 ns;
- seven-case validation: 286,876 ns;
- whole run before serialization: 6,161,037 ns;
- serialization: 182,651 ns, final outcome 7,029 bytes;
- process `ru_maxrss`: 10,880 KiB, measured through
  `resource.getrusage`, not inferred from file size;
- implementation correction replays: 0.

## Who this helps and the minimum continuation

The anchor lets Mingli Yuan, Jiamin Zhao, or a later agent hand off one local
comparison without silently changing its target presentation, objects, or
whiskers.  It answers the smaller question “which typed 2-cell does this
occurrence denote?”  It does not answer whether fourteen such cells compose to
one common comparison.

The minimum continuation is one composition-only experiment: compose exactly
two adjacent anchored occurrences sharing a verified intermediate gallery,
retain both occurrence identities, and compare the composed typed boundary
with direct path concatenation.  A success would remain a two-occurrence
composition witness, not a 3-cell, M6 filler, or global TO24 closure.
