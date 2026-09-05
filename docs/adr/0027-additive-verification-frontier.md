# ADR 0027: Add verification as an append-only frontier layer

## Status

Accepted for the version-zero research companion. This does not change
`InquiryFrontierV0`, `AdvaDocumentV0`, the Lisp language, or `adva.ir` version
1.

## Context

The first two inquiry transitions preserve five arithmetic obligations but
cannot change their state: `InquiryObligationStateV0` contains only `Open`, and
the frontier checker requires exact equality with the original calibration.
Changing that enum or equality rule would retroactively change the meaning and
content coordinates of already published frontier files.

The `custody` hypothesis also exposes a distinction hidden by a scalar hole
count. Turning one broad question into several typed observations may increase
the number of leaves while reducing ambiguity. Preservation work is necessary
for continuation but must not be conflated with semantic truth. Finally, a
checker hidden inside the installed CLI can drift without appearing in the
trace.

## Decision

Introduce four independent research schemas:

- `VerificationContractV0`, the explicit method carrier;
- `VerificationPacketV0`, the requested refinement, discharge, reopening, or
  fork record;
- `VerificationTransitionV0`, the complete three-input/three-output edge;
- `VerificationFrontierV0`, the residual typed obligation graph.

The fixed slots are interpreted as follows:

| Slot | Verification reading |
| --- | --- |
| `subject` | an immutable inquiry frontier or a later verification frontier |
| `method` | a content-addressed, versioned verifier contract |
| `object` | a finite verification packet |
| `history` | exact input digests, decisions, and leaf-count delta |
| `result` | open or scoped-closed status and an optional certificate |
| `evidence` | the complete residual frontier and next-input coordinates |

The verification frontier embeds the complete origin inquiry frontier and its
digest. Its first five nodes must retain the original coordinates, types, and
details. New semantic nodes have parent obligations; custody nodes are
orthogonal and have none. Parent order is acyclic and every refined state must
name exactly its ordered children.

Obligation states are `Open`, `Refined`, `Discharged`, and `Reopened`.
Discharge stores witness, verifier, and scope coordinates. Reopening stores the
prior witness and counterevidence rather than deleting either. Unresolved forks
retain both branch coordinates. `ScopedClosed` requires zero open or reopened
semantic leaves and zero unresolved forks; custody leaves are reported
separately.

The first verifier is deliberately refinement-only. It can apply typed
refinements, reopen a structurally present discharge, and retain forks. It
records every discharge request as rejected because no typed semantic
predicate has yet been implemented. A digest reference alone can never create
a certificate.

## Consequences

- Existing inquiry artifacts and their BLAKE3 coordinates remain unchanged.
- Checker interpretation becomes part of each transition rather than ambient
  CLI state.
- Refinement may increase the number of open leaves; progress must be assessed
  by typed specificity and discharge evidence, not hole count alone.
- Semantic closure and custody readiness remain separately inspectable.
- A future discharge-capable method requires a new version or explicit
  migration. It cannot silently replace the first verifier.
- The implementation supplies an auditable state machine, not the missing
  characteristic maps, ordered holonomy proof, external observation, or
  recovery drill.
