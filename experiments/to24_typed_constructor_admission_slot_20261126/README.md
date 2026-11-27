# Bounded typed constructor admission slot

Date: 2026-11-26

## Dependency snapshot

- `mountain/adva` main: `6930599aa6132cdc5ec7165e0d1c8d8d09f3dee9`
- continuation PR: draft PR #235, predecessor head `85a6d5d4c79d32a1581dd1da60201ef98498b062`
- predecessor word: `typed discharge frontier`
- predecessor run SHA-256: `26f9eeecd5d0fee6926c40bca36ef8c74edb2cabc4d16c14f5f2588416d479b1`
- predecessor outcome SHA-256: `38abec9f14ebd6a5d0c6ccd870c48c6ed6ebc3ec23bcfd72edd67a92ae7e123c`
- pinned target SHA-256: `114c136690b27063a8e7b3da111e699b8fe437cac488122079110d9bd54a275c`

Main, the open draft set, AGENTS.md, the research engineering agenda, the claim registry, Research 0090, 0092, 0118, 0121, 0122 and 0123, and the predecessor record were reread before freezing this run. Main and those source bytes remain unchanged. All three workflows for the predecessor head passed.

The dependency states remain separate. The finite TO24 fourteen-face cellular boundary is merged work. The signed face-sweep receipt and its typed continuations on PR #235 are unmerged finite experiments. Research 0090 coverage remains incomplete, so Research 0092 all-fillings closure and vocabulary promotion remain blocked. Research 0123's `arithmetic-universality` and `hypothesized-arithmetic-truth` remain Proposed.

## Frozen question and budget

Can an exact, versioned, explicitly empty higher-constructor registry interface refine the missing-registry frontier without modifying the target or allowing the interface to grant itself target authority?

The frozen arithmetic domain is canonical finite JSON, exact SHA-256 coordinates, finite ordered field sets and state transitions, and the pinned S4 target presentation. The run used one route, two checked obligations, one empty interface, two admission slots, twelve cases, and 270 constructed nodes, under the limits of 30 seconds and 100,000 candidates or nodes. One implementation-correction replay was permitted.

## Construction and result

Status: `PassedBoundedTypedConstructorAdmissionSlot`.

The external interface is pinned to the exact target and declares:

- authority `ExternalInterfaceOnly`;
- no target-authority receipt;
- an exact six-field constructor-entry interface;
- transition order `Open -> ExternalCandidate -> TargetAdmitted -> Discharged`;
- an empty entry list;
- no equality, higher cell, or filler.

The primary and fresh obligations both return:

`OpenAdmissionSlot/EmptyExternalInterface`

A complete boundary-matching external candidate returns:

`UnknownAdmission/ExternalCandidateOnly`

It is not inserted into the registry and gains no target authority. Twelve declared cases all matched. The checker specifically refused a wrong boundary, target or obligation drift, forged target authority, direct insertion into the external-only registry, a premature discharge receipt, a changed entry-field set, premature semantic equality, and a premature filler.

This is a finite interface and refusal result. The external interface does not modify the exact target, create a target-owned registry, admit a constructor, discharge an obligation, identify composites, or construct a 3-cell or filler.

## Proposed vocabulary

### typed constructor admission slot

- **Role:** retain one explicit open target-and-obligation coordinate in a versioned external registry interface without granting registry membership or discharge.
- **Input:** one exact target digest, one checked typed obligation, one validated external empty registry interface, and an optional external constructor candidate.
- **Output relation:** `OpenAdmissionSlot`, `UnknownAdmission`, or a registry-, target-, obligation-, boundary-, authority-, discharge-, equality-, or filler-specific refusal.
- **Applicability:** the target and obligation are exactly pinned, the registry interface is external and empty, and no target-authority receipt exists.
- **Witness:** the registry interface digest and exact fields, target and obligation digests, open slot state, optional candidate, result, and residual authority/admission/discharge requirements.
- **Counterexample / refusal:** a complete boundary-matching proposal remains `UnknownAdmission`; self-issued target authority and direct entry insertion into the external-only interface are refused.
- **Expansion / replay:** verify the predecessor obligation; validate the registry schema, target pin, authority, field set, transition order and empty entries; bind one open slot; validate any candidate boundary; stop at `Unknown` unless a separately supplied target-owned registry and admission receipt exist. Run `timeout 30s python3 run.py`.
- **Residual:** no target-owned registry, admitted constructor, discharge receipt, semantic equality, higher cell, filler, Research 0090 coverage, Research 0092 promotion, arithmetic-universality, or hypothesized-arithmetic-truth result.
- **State:** Proposed.

The same interface was reused on the fresh checked obligation, producing a distinct target-and-obligation coordinate with the same open result.

## Finite comparison

The untyped declared-interface projection serializes to 220 bytes. The typed primary slot record serializes to 1,797 bytes, an added formation cost of 1,577 bytes. Eight cases beyond the primary collide with it under the untyped projection. That projection cannot distinguish an empty slot from an external-only candidate, forged authority, direct insertion, a changed field set, premature equality, premature filler, or premature discharge. The typed record separates these cases in the frozen suite.

No general expressivity, minimality, completeness, admission, or asymptotic-efficiency theorem is claimed.

## Measured cost and correction

- predecessor verification: 1,103,258 ns
- target formation: 3,170,517 ns
- primary obligation formation: 130,965 ns
- fresh obligation formation: 94,210 ns
- registry-interface formation: 11,878 ns
- primary-slot formation: 203,034 ns
- fresh-slot reuse: 106,819 ns
- twelve-case validation: 1,296,778 ns
- whole corrected run before serialization: 7,066,298 ns
- serialization: 400,779 ns
- serialized outcome: 9,818 bytes
- measured `ru_maxrss` before serialization: 11,008 KiB
- routes / cases / constructed nodes: 1 / 12 / 270
- implementation-correction replays: 1

The first passing output said “every direct self-admission route,” which exceeded the twelve frozen cases. The sole correction narrowed this to “each declared direct self-admission route.” The interface, cases, budget and decisions were unchanged.

## Collaboration value and next minimum

For Mingli Yuan, Jiamin Zhao, and later human or AI collaborators, the slot distinguishes “we know exactly where an admitted constructor would have to attach” from “the target has admitted one.” It lets a sender supply a candidate without transferring authority, and lets a receiver refuse self-issued admission or discharge while preserving the candidate and exact remaining obligation.

The next minimum continuation is read-only: identify one exact native Adva mechanism, if any, that could own a versioned higher-constructor registry and issue a target-backed admission receipt. If no such mechanism is present, retain that source-level absence as an explicit residual. Do not populate the slot or claim a target successor until that authority boundary exists.
