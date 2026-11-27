# Bounded typed comparison segment

Date: 2026-11-23

## Dependency snapshot

Adva `main` remains
`6930599aa6132cdc5ec7165e0d1c8d8d09f3dee9`.  The current instructions,
agenda, claim registry, Research 0090, 0092, 0103, 0118, 0121, 0122, 0123,
and merged TO24 boundary note were reread before freezing this run.  Draft PR
#235 remained unmerged at
`9cd24591fe06dff4ff1d2f83ea6ddb0687c55302`; all seven remote checks for that
head had passed.

The dependency states remain distinct:

- the finite fourteen-face cellular boundary is merged mathematical work;
- the signed face-sweep receipt, typed face anchor, and this continuation are
  unmerged finite experiments on PR #235;
- Research 0090 coverage remains incomplete, blocking Research 0092 global
  filling closure and vocabulary promotion;
- `arithmetic-universality` and `hypothesized-arithmetic-truth` remain Proposed;
- no native relation-witness composition, common comparison of the two full
  seven-step pastings, 3-cell, or Q4/M6 filler exists here.

## Frozen question

Can exactly two adjacent typed face anchors be composed while retaining their
intermediate gallery and factor order, and can that construction be reused on
the other route around one disjoint commuting square without identifying the
two composites or adding a higher cell?

`contract.json` freezes the objects, types, quantifier, arithmetic domain,
candidate grammar, evaluation rules, and resource limits.  `input.json` pins
the predecessor implementation, target digest, and both routes.

## Construction

The run reuses the pinned 240-node A3 target presentation and builds four
anchors forming the square

```text
213231 -> 231231 -> 231213
213231 -> 213213 -> 231213
```

Each segment records:

- one target-presentation digest;
- two complete typed face anchors;
- ordered occurrence and 2-cell identities;
- the source, intermediate, and target gallery paths;
- the two half-open rewrite intervals;
- explicit `NotClaimed` / `NotConstructed` higher boundaries.

Both routes returned `TypedComparisonSegmentComposed`.  Their endpoint-only
projections are byte-identical.  Their intermediate paths are distinct, and
their two generating cells occur in reverse order.  The rewrite intervals are
disjoint and the factor-cell multisets agree, so the finite checker returns
`EligibleDisjointInterchangeBoundary/HistoriesRetained`.

This label records the preconditions for an interchange boundary.  It does
not identify the composites.  The unfilled boundary and any equality or
higher filler remain different objects, as required by Research 0103.

Eight declared cases passed: both routes plus refusals for reordering without
retyping, a missing factor, duplicated occurrence history, changed target,
premature interchange identification, and a premature higher cell.

## Proposed word: typed comparison segment

- **Role:** compose a short ordered sequence of typed face anchors while
  retaining the exact intermediate gallery and factor history.
- **Input:** one versioned target, exactly two adjacent anchors, ordered
  occurrence identities, and the declared source/intermediate/target chain.
- **Output relation:** `TypedComparisonSegmentComposed`, or a target-, factor-,
  history-, intermediate-boundary-, or promotion-specific refusal.
- **Applicability:** both anchors validate against the same target digest and
  the first target path equals the second source path exactly.
- **Witness:** both complete anchors, factor and occurrence ids, rewrite
  intervals, and the three gallery paths.
- **Counterexample:** the two valid square routes have identical endpoint-only
  projection but distinct intermediate paths and reverse factor order;
  endpoint-only data cannot say which route occurred.
- **Expansion/replay:** validate each anchor, compare the common intermediate
  path, replay the ordered factors, and retain the endpoint projection without
  deleting intermediate history.
- **Refusal:** target mismatch; missing, reordered, invalid, or duplicate
  factors; intermediate mismatch; altered history; or a premature claim of
  equality, interchange identification, higher cell, or filler.
- **Residual:** no semantic equality, native vertical/horizontal composition,
  3-cell, Q4/M6 filler, fourteen-face pasting comparison, arbitrary coherence,
  or arithmetic-universality result.
- **State:** Proposed.

The endpoint-only projection is 408 bytes; the full segment is 3,224 bytes.
The 2,816-byte increase retains data that distinguishes the two valid routes.
This is a finite discrimination result, not a general expressivity or
efficiency theorem.

## Replay

From this directory, with the predecessor sibling directory present:

```sh
timeout 30s python3 run.py
sha256sum contract.json input.json outcome.json run.py
```

Expected status: `PassedBoundedTypedComparisonSegment`.

Retained `outcome.json` SHA-256:
`4412836d89ba5e11790adbf471036421aa0c734f1a8af0bbd780e053180b3a36`.

## Measured cost

- routes: 1;
- constructed nodes: 246, below the 100,000 limit;
- predecessor pin and import verification: 10,494,643 ns;
- target formation: 3,411,938 ns;
- route A segment formation: 108,088 ns;
- route B reuse formation: 58,477 ns;
- eight-case validation: 781,881 ns;
- interchange-eligibility check: 95,865 ns;
- endpoint projection formation: 1,062 ns;
- whole run before serialization: 15,078,100 ns;
- serialization: 264,248 ns, producing 12,930 bytes;
- process `ru_maxrss`: 11,904 KiB, measured through
  `resource.getrusage`, not inferred from artifact size;
- implementation correction replays: 0.

## Who this helps and the next minimum

Mingli Yuan, Jiamin Zhao, and later agents can now hand off a short comparison
without collapsing “same endpoints” into “same construction.”  A receiver can
replay the intermediate gallery and reject lost, duplicated, or reordered
factors.

The minimum continuation is not a longer path.  It is a single interchange
obligation for this fixed square: specify the target's admissible interchange
rule and an independently checkable witness relating these two retained
segments.  Until that witness exists, retain
`EligibleDisjointInterchangeBoundary/HistoriesRetained`; do not report equality,
confluence, a 3-cell, or a filler.
