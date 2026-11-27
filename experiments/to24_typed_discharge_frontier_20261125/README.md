# Bounded typed-discharge-frontier audit

Date: 2026-11-25

## Dependency snapshot

- `mountain/adva` main: `6930599aa6132cdc5ec7165e0d1c8d8d09f3dee9`
- continuation PR: draft PR #235, predecessor head `ba51aee0d7ed88a11f032f27d591d31ae6a341fe`
- predecessor word: `typed interchange obligation`
- predecessor run SHA-256: `7552c8daf4fdc004babe7eefb9499cecd639c49236a8ca29cdaa035ebe251dd0`
- pinned target SHA-256: `114c136690b27063a8e7b3da111e699b8fe437cac488122079110d9bd54a275c`

The repository state still separates merged governance and dependency records from the unmerged bounded proposals on PR #235. Research 0090 coverage is not complete, so Research 0092 promotion remains blocked. Research 0123's `arithmetic-universality` and `hypothesized-arithmetic-truth` remain proposals rather than proved arithmetic or admitted trust.

## Frozen question and budget

Question: does the exact pinned finite A3 target register an admitted higher constructor that can discharge either checked typed interchange obligation? If not, can the exact missing capability frontier be retained without manufacturing a 3-cell?

The frozen domain is canonical finite JSON, exact SHA-256 coordinates, finite ordered capability sets, and the pinned S4 target presentation. The run used one route, two obligations, ten cases, and 264 constructed nodes, under the limits of 30 seconds and 100,000 candidates or nodes. One implementation-correction replay was permitted.

## Result

Status: `PassedBoundedTypedDischargeFrontier`.

The complete target inventory has four top-level keys: `descriptor`, `objects`, `one_cells`, and `two_cells`. It contains 24 objects, 72 one-cells, and 144 two-cells, for 240 target nodes. It declares no higher-constructor registry. Consequently, both the primary and fresh checked interchange obligations return:

`UnknownDischarge/NoRegisteredHigherConstructor`

with the ordered frontier:

1. `higher_constructor_registry`
2. `applicable_constructor`
3. `target_admission_receipt`
4. `boundary_witness`
5. `discharge_receipt`

A structurally plausible external proposal with the correct boundary remains `UnknownDischarge/ExternalConstructorUnadmitted`; it does not acquire target authority by being well shaped. The audit also replayed refusals for wrong boundaries, unsupported admission, premature discharge, premature equality, premature filler, changed target, and changed obligation. All ten expected results matched.

This is an exhaustive inventory result for one finite target representation. It is not a mathematical theorem that no 3-cell exists, not an impossibility theorem, and not a discharged obligation. It supplies no equality, confluence, filler, global M6 closure, Research 0090 coverage, Research 0092 promotion, arithmetic-universality, or hypothesized-arithmetic-truth result.

## Proposed vocabulary

### typed discharge frontier

- **Role:** retain the ordered target capabilities still missing between a checked higher obligation and an admissible discharge.
- **Input:** one target digest and complete finite target inventory, one checked typed obligation, and an optional external constructor proposal.
- **Output relation:** `UnknownDischarge` with an ordered frontier, or a target-, obligation-, boundary-, admission-, or promotion-specific refusal.
- **Applicability:** the checked obligation and target are exactly pinned, and the audit is restricted to explicitly declared target registries and receipts.
- **Witness:** the target top-level-key inventory and node counts, target and obligation digests, optional candidate digest, result, and ordered missing-capability list.
- **Counterexample / refusal:** a plausible external proposal remains unadmitted when the target has no registry; target or obligation drift, boundary mismatch, unsupported admission, and premature equality, higher-cell, filler, or discharge claims are refused.
- **Expansion / replay:** validate the obligation; inventory the target; locate an explicit higher-constructor registry; match boundary and applicability; require target-backed admission and a discharge receipt; otherwise return the remaining ordered frontier. Run `timeout 30s python3 run.py`.
- **Residual:** no search outside the exact target representation and no admitted constructor, 3-cell, discharge, equality, confluence, filler, coverage, promotion, or universality result.
- **State:** Proposed.

The fresh obligation reused the same audit and returned the same five-coordinate frontier. Thus the word was reused once on a new declared instance.

## Finite comparison

The checked-obligation-only projection serializes to 215 bytes. The typed frontier record serializes to 693 bytes, an added formation cost of 478 bytes. Six controls beyond the primary case collide with the primary under the base projection: the base record cannot say whether registry, applicability, admission, boundary, or discharge evidence is missing. The frontier record distinguishes those finite cases. No general expressivity, minimality, completeness, or asymptotic-efficiency theorem is claimed.

## Costs and correction

- predecessor verification: 2,513,446 ns
- target formation: 4,723,486 ns
- primary obligation formation: 149,354 ns
- fresh reuse formation: 110,766 ns
- ten-case validation: 1,769,458 ns
- whole run before serialization: 11,099,553 ns
- serialization: 382,544 ns
- serialized outcome: 11,311 bytes
- measured `ru_maxrss` before serialization: 11,008 KiB
- routes / cases / constructed nodes: 1 / 10 / 264
- implementation-correction replays: 1

The first execution changed wording in the pinned target descriptor and correctly failed with `PinnedTargetDigestMismatch`. The sole correction restored the exact predecessor descriptor. The mathematical object, question, cases, and budget were unchanged.

## Collaboration value and residual obligation

For Mingli Yuan, Jiamin Zhao, and later human or AI collaborators, this record prevents a checked higher obligation from silently becoming an admitted 3-cell. It says exactly which target-side capabilities are still absent and gives a replayable rejection vocabulary for superficially plausible external proposals.

The next minimum continuation is to specify a versioned higher-constructor-registry interface for this exact target, including applicability, boundary, admission, and discharge-receipt fields, while keeping the registry empty until a real constructor and target-backed admission witness exist.
