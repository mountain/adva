# Bounded typed interchange obligation

Date: 2026-11-24

## Dependency snapshot

Adva `main` remains
`6930599aa6132cdc5ec7165e0d1c8d8d09f3dee9`.  The current instructions,
agenda, claim registry, Research 0090, 0092, 0103, 0118, 0121, 0122, 0123,
and the merged TO24 boundary note were reread before freezing this run.  The
open drafts remain PR #235, #234, and #232.  PR #235 is unmerged at
`2b3b8f3795b0c4f3aa509bd8ccd459ca4ee0792c`; its CI, publication-boundary,
and machine-dependency-continuity workflows all passed.

The dependency states remain separate:

- the fourteen-face TO24 cellular boundary is merged finite mathematical work;
- the signed face-sweep receipt, typed face anchor, typed comparison segment,
  and this continuation are unmerged finite experiments on PR #235;
- Research 0090 coverage remains incomplete, so Research 0092 global filling
  closure and vocabulary promotion remain blocked;
- `arithmetic-universality` and `hypothesized-arithmetic-truth` remain Proposed;
- no semantic comparison, native composition, common 3-cell, or Q4/M6 filler
  is obtained here.

## Frozen question

Can two retained typed comparison segments around one fixed disjoint square be
bound to one explicit independently replayable interchange rule without
identifying the composites or constructing a higher cell?

`contract.json` freezes the objects, types, quantifier, finite arithmetic
domain, candidate grammar, evaluation rules, and resource limits.  `input.json`
pins both predecessor implementations, the target digest, the rule, and two
disjoint squares.

## Construction and result

The primary square reuses the predecessor paths:

```text
213231 -> 231231 -> 231213
213231 -> 213213 -> 231213
```

The fresh reuse square is:

```text
132132 -> 312132 -> 312312
132132 -> 132312 -> 312312
```

For each square the checker reconstructs four typed anchors and two typed
comparison segments, then records:

- the target digest and exact registered rule id;
- both complete segments and their distinct intermediate galleries;
- the unique reversed factor-index correspondence;
- matching rewrite offsets, relations, and generating 2-cell ids;
- source, both intermediate words, and common target word;
- explicit `NotClaimed` / `NotConstructed` guards for equality, a higher cell,
  and a filler.

Both squares return
`TypedInterchangeObligationChecked/NoHigherCellConstructed`.  The checker
replays both factor orders.  Success of the second step in each order verifies
that the first disjoint equal-length rewrite leaves the other redex available
at its declared offset.

This result checks the boundary, rule, correspondence, and replay data of an
obligation.  It does not discharge that obligation or identify the composites.
The unfilled comparison and any higher filler remain distinct objects, as
required by Research 0103.

Eleven declared cases matched: two positive squares and specific refusals for
a changed target, unknown rule, wrong factor correspondence, wrong replay,
premature equality, premature higher cell, premature filler, duplicated
segment, and overlapping declared interval.

## Proposed word: typed interchange obligation

- **Role:** bind two retained comparison segments to one explicit admissible
  local-swap rule, factor correspondence, and two-order replay witness without
  discharging the higher comparison.
- **Input:** one versioned target, two valid typed comparison segments with
  common endpoints, a declared rule id, an explicit factor correspondence,
  and source/intermediate/target replay words.
- **Output relation:**
  `TypedInterchangeObligationChecked/NoHigherCellConstructed`, or a rule-,
  segment-, correspondence-, replay-, target-, independence-, or
  promotion-specific refusal.
- **Applicability:** exactly two equal-length rewrites occur on disjoint
  half-open sites, both orders form valid typed segments, and applying either
  first leaves the other redex available at the same site.
- **Witness:** both complete segments, target digest, registered rule payload,
  reversed factor correspondence, matched sites/relations/2-cells, and both
  exact word replays.
- **Counterexample/refusal boundary:** changing the rule, factor
  correspondence, replay witness, equality flag, higher-cell flag, or filler
  flag preserves the bare eligibility projection but is specifically refused.
- **Expansion/replay:** validate both segments; reconstruct the unique reversed
  factor correspondence; replay left-then-right and right-then-left; verify the
  common target and preservation of the other redex; retain every promotion
  guard.
- **Residual:** no discharge, semantic equality, native horizontal/vertical
  composition, common 3-cell, Q4/M6 filler, full fourteen-face pasting
  comparison, arbitrary coherence, Research 0090 coverage, or arithmetic
  universality.
- **State:** Proposed.

The bare eligibility projection is 351 bytes; the full primary obligation is
8,554 bytes, an 8,203-byte formation increase.  Six refused mutations collide
exactly under the bare projection.  The added record therefore distinguishes
the next check from six premature or malformed substitutes in this frozen
finite suite.  This is not a general expressivity, minimality, completeness,
or asymptotic efficiency theorem.

## Replay

From this directory, with the two predecessor sibling directories present:

```sh
timeout 30s python3 run.py
sha256sum contract.json input.json outcome.json run.py
```

Expected status: `PassedBoundedTypedInterchangeObligation`.

Retained `outcome.json` SHA-256:
`9b8992e609147c9e7b4794387d93acbf1b9c0878a02291d6b1681fe9fcd82cac`.

## Measured cost

- routes: 1;
- squares: 2;
- cases: 11;
- constructed nodes: 254, below the 100,000 limit;
- predecessor verification: 1,083,826 ns;
- target formation: 5,326,289 ns;
- primary obligation formation: 198,240 ns;
- fresh reuse formation: 128,045 ns;
- eleven-case validation: 5,954,254 ns;
- whole corrected run before serialization: 12,705,497 ns;
- serialization: 399,814 ns, producing 25,337 bytes;
- process `ru_maxrss`: 11,008 KiB, measured through `resource.getrusage`, not
  inferred from artifact size;
- implementation correction replays: 1.

The first invocation is an `ImplementationFailure`: it imported the comparison
module but incorrectly assumed that module had already instantiated its anchor
predecessor.  The sole correction explicitly pins and loads that predecessor.
No mathematical object, rule, case, or budget changed.

## Who this helps and the next minimum

Mingli Yuan, Jiamin Zhao, and later agents can now pass a precise higher
comparison request instead of the ambiguous phrase “these disjoint rewrites
should commute.”  A receiver can tell which rule, factor matching, and replay
must be checked, and can refuse a substituted rule or premature filler while
retaining the same endpoints.

The minimum continuation is one **obligation discharge candidate** for the
primary fixed square.  It must name the target's admissible higher constructor
or explicitly report that no such constructor is currently available.  Until
then, retain the checked obligation as an unfilled boundary: do not report
equality, confluence, a 3-cell, a filler, Research 0092 promotion, or arithmetic
universality.
