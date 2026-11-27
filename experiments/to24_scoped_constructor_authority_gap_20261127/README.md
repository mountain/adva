# Bounded scoped constructor authority gap

Date: 2026-11-27

## Dependency snapshot

- `mountain/adva` main: `6930599aa6132cdc5ec7165e0d1c8d8d09f3dee9`
- continuation: open draft PR #235 at predecessor head `9c7fa3647c8501e679743fdc665de060de9910ec`
- predecessor word: `typed constructor admission slot`
- predecessor run SHA-256: `8a17a2bd07d672706da72ce51e88acbeb2788ae600fa1f272c8b38c5628ed2d4`
- predecessor outcome SHA-256: `60b4761457a661f79d45aaed64a8841696d8208c8ea1975e015acb4945a7db20`
- pinned A3 target SHA-256: `114c136690b27063a8e7b3da111e699b8fe437cac488122079110d9bd54a275c`

Main, the open draft set, `AGENTS.md`, the research engineering agenda, the
claim registry, Research 0090, 0092, 0118, 0121, 0122 and 0123, and the
predecessor record were reread before freezing this run. Main is unchanged.
PR #235 is open, draft, unmerged and mergeable; all three workflows on its
predecessor head passed.

The dependency states remain distinct. The finite TO24 fourteen-face boundary
is merged. The signed face-sweep receipt and its typed continuations are
unmerged finite experiments on PR #235. Research 0090 coverage remains open,
so Research 0092 all-fillings closure and vocabulary promotion remain blocked.
Research 0123's `arithmetic-universality` and
`hypothesized-arithmetic-truth` remain Proposed.

## Frozen question and budget

Among five exact source-pinned Adva surfaces, does any one mechanism both own
the A3 target and supply all eight capabilities needed for a versioned higher-
constructor registry plus target-backed admission and obligation-discharge
receipts?

The frozen domain is finite set subtraction over eight ordered capabilities,
five candidate mechanisms, eight exact Git blob pins, two obligation
coordinates and ten cases. Cross-surface union is not authorized. One route,
25 constructed nodes and ten cases were permitted, below 30 seconds and
100,000 nodes. One implementation-correction replay was available.

## Source-pinned inventory

| Candidate | Pinned role | Supported capabilities in this audit |
|---|---|---|
| builtin operation registry | versioned scalar `Real` operations | versioned identity; runtime semantic authority |
| witness seed and `Seal` | six-word seeds and arithmetic multiplicative closure | versioned identity; runtime semantic authority |
| claim registry | documentary claim identity, scope and evidence | versioned identity |
| publication admission | contribution rights and publication eligibility | versioned identity |
| external A3 admission slot | exact external A3 higher-constructor interface | target binding; versioned identity; higher kind; boundary applicability |

The source records pin `OperationSpec` and its ADR, `SeedRegistryV0`,
`WitnessProofV0::Seal`, `docs/claims.toml`, the publication boundary, ADR 0042,
and the predecessor external slot. Their exact paths, refs, blob ids and scope
statements are in `input.json`.

## Result

Status: `PassedBoundedScopedConstructorAuthorityGap`.

No single candidate covers all eight capabilities. More strongly, even the
declared union of all five supported sets lacks exactly:

1. `target_authority_issuer`;
2. `target_admission_receipt`;
3. `obligation_discharge_receipt`.

That union is diagnostic only and is not authorized as a composite mechanism.
The primary and fresh obligations both return:

`AuthorityGap/NoCandidateCoversAll`

All ten cases matched. The checker refuses promoting any of `OperationSpec`,
arithmetic `Seal`, claim registration, publication admission or the external
slot to full A3 constructor authority. It also refuses source-pin drift,
required-capability omission and cross-surface authority composition.

This is exhaustive only over the five declared source-pinned surfaces. It is
not a whole-repository absence theorem and does not prove that no future native
mechanism can exist.

## Proposed vocabulary

### scoped constructor authority gap

- **Role:** retain the exact missing authority capabilities after a declared
  finite inventory of possible constructor-owning surfaces has been checked.
- **Input:** one target and obligation coordinate, one ordered required-
  capability profile, and finitely many source-pinned candidate surfaces with
  scoped supported-capability sets.
- **Output relation:** `AuthorityGap` with per-candidate and declared-union
  residuals, `CandidateFound`, or a source-, inventory-, scope-, capability-,
  target-, obligation-, or union-specific refusal.
- **Applicability:** candidate inventory, source pins, capability meanings and
  the no-cross-surface-composition rule are frozen before evaluation.
- **Witness:** every source pin; the required profile; one supported/missing
  row per candidate; the declared-union residual; target and obligation
  digests; and the finite scope boundary.
- **Counterexample / refusal:** a scalar operation registry, arithmetic seal,
  documentary claim, publication admission or external slot cannot be
  promoted beyond its pinned scope merely because its name resembles one
  needed capability.
- **Expansion / replay:** verify source and predecessor pins; validate the
  exact inventory; subtract each supported set from the required profile;
  require one complete candidate; compute but do not authorize the union; and
  retain both residuals. Run `timeout 30s python3 run.py`.
- **Residual:** no target-authority issuer, admission receipt, discharge
  receipt, admitted constructor, higher cell, filler, Research 0090 coverage,
  Research 0092 promotion, arithmetic-universality or
  hypothesized-arithmetic-truth result is obtained.
- **State:** Proposed.

The same audit was reused on the fresh checked obligation and returned the
same three-capability declared-union residual.

## Finite comparison

The candidate-name-only projection serializes to 355 bytes. The typed primary
authority-gap record serializes to 3,826 bytes, an added formation cost of
3,471 bytes. Eight cases beyond the primary collide with it under the base
projection. Candidate names alone do not retain per-capability support, source
scope, missing sets, the union residual or the ban on authority composition.

No general expressivity, minimality, completeness, global source inventory or
efficiency theorem is claimed.

## Measured cost

- predecessor verification: 9,739,771 ns
- source-inventory formation: 85,015 ns
- primary analysis: 23,639 ns
- fresh-obligation reuse: 15,991 ns
- ten-case validation: 204,823 ns
- whole run before serialization: 10,354,820 ns
- serialization: 483,563 ns
- serialized outcome: 11,442 bytes
- measured `ru_maxrss` before serialization: 11,904 KiB
- routes / sources / candidates / cases / constructed nodes: 1 / 8 / 5 / 10 / 25
- implementation-correction replays: 0

The unavailable external `/usr/bin/time` command was not treated as a replay:
the research program had not started. Runtime and memory above are measured by
Python's monotonic clock and `resource.getrusage`; memory is not inferred from
file size.

## Collaboration value and next minimum

For Mingli Yuan, Jiamin Zhao and later human or AI collaborators, the gap
prevents three tempting scope errors: treating scalar-operation semantics,
arithmetic closure, or publication/claim admission as authority to change the
A3 target. A sender can now state exactly which source surface was checked and
which authority coordinate remains absent; a receiver can replay the matrix
without accepting a fabricated constructor or receipt.

The smallest continuation is to specify one target-owned authority-owner
interface, still without populating it: exact issuer identity and version,
target-successor rule, constructor-admission receipt fields, obligation-
discharge receipt fields, and a non-composition rule separating it from the
existing scalar operation, witness, claim and publication mechanisms. Until
that interface has an independent target-authority basis, the result remains
Unknown and the external slot stays empty.
