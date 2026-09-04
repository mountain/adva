# ADR 0020: Add checked research persistence for neutral Adva carriers

- Status: accepted for bounded research V0
- Date: 2026-09-04

## Context

ADR 0019 established two three-label views over neutral carriers but stopped
before implementing a persistent container. Serialization of a Rust value was
not enough: a reusable cycle needs a save boundary that retains the three
output positions and a load boundary that cannot silently copy, discard, or
misroute them.

The `.adva` suffix is already used for Lisp source. The new boundary therefore
must be self-describing and explicitly research-only rather than an implicit
reinterpretation of every `.adva` file.

## Decision

Add `AdvaDocumentV0` and its persistence operations to `adva-witness`.

- A document has schema `adva.neutral-carrier.research`, version zero, and one
  `MechanismOutputV0` payload containing `history`, `result`, and `evidence`.
- Saving rechecks nonempty artifact cache coordinates and canonical open
  frontiers before encoding. It writes a same-directory temporary file,
  flushes it, renames it over the requested `.adva` path, and synchronizes the
  directory on Unix.
- Loading checks the suffix, JSON shape, unknown fields, schema, version,
  artifact coordinates, and frontier canonicality.
- `ReloadPlanV0` contains exactly three explicit `CarrierRouteV0` values. Each
  output label and each input label must occur once. This is an exact
  relabelling, not copy, discard, contraction, or synthesis.
- A successful load returns `MechanismInputV0` together with a
  `ReloadCertificateV0` containing the canonical routes, document digest, and
  checked boundary fields.
- Python exposes thin path and JSON adapters in `adva.persistence`; all
  semantic checks and file writes remain Rust-owned.

No `.adva` program or example fixture is committed by this decision. The first
program is intentionally left for the user to author.

## Consequences

The local persistence seam is executable and auditable. A saved output triple
can be reused at a later input boundary without erasing its slot provenance.
Malformed, noncanonical, wrongly versioned, or non-bijectively routed content
is rejected.

The document is still a manifest of neutral carrier references. Its artifact
keys are cache coordinates, not embedded content or semantic identities.
Loading does not resolve those keys, validate their remote availability,
execute a mechanism, replay a proof, verify the origin of an output triple, or
schedule a subsequent step.

## Promotion gate

A stable format still requires a decision on coexistence or dispatch with Lisp
source, durable artifact resolution, cryptographic authenticity rather than a
local integrity digest, certified mechanism-output provenance, recovery and
locking policy for concurrent writers, migration rules, and integration with
stable `adva.ir` identities and certificates.
