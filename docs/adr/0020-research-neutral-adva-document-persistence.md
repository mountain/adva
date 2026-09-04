# ADR 0020: Store neutral carriers as vertices and mechanisms as transition frames

- Status: accepted for bounded research V0
- Date: 2026-09-04

## Context

ADR 0019 established neutral carriers and the nine interface labels. The first
persistence implementation stored only one `history/result/evidence` triple
and required an external reload permutation. That representation was a valid
manifest, but it removed the mechanism from the document and could not state a
self-contained ready transition. It over-applied carrier neutrality to the
whole document.

Neutrality constrains vertices, not edges. A carrier must not become a
program/proof/model kind, while a document may retain mechanism-labelled
transitions among neutral carriers. Repeated use also needs explicit,
persistent references rather than loader-local relabelling.

The `.adva` suffix is already used for Lisp source. This boundary must remain
self-describing and research-only rather than reinterpret every `.adva` file.

## Decision

Replace the output-only V0 manifest with a canonical document graph.

- Schema `adva.neutral-carrier-graph.research`, version zero, contains
  `carriers`, `frames`, and `entrypoints` tables.
- `CarrierIdV0` and `FrameIdV0` are document-local storage coordinates. They
  are not sources, occurrences, values, or semantic identities.
- A stored carrier contains only `NeutralCarrierV0`: an artifact cache
  coordinate and canonical open frontier. It has no mechanism or persistent
  program/proof/model kind.
- `TransitionFrameV0` contains exactly one `subject/method/object` reference
  triple, one `compute/verify/learn` mechanism form, and the fixed
  `history/result/evidence` output boundary.
- A frame output is either fully ready (three absent references) or fully
  recorded (three present references). Partial output recording is rejected.
  "Recorded" does not assert that execution produced the carriers.
- Stored learning replacements refer to the same carrier table, preventing
  carrier duplication inside the frame representation.
- A later frame reuses an earlier output by naming the same carrier coordinate
  in its own labelled input position. This persisted reference structure is
  the output-to-input substitution record; no external reload permutation is
  required.
- Entry-point names are document-local selectors for starting frames.
- All three tables must be strictly ordered. Carrier keys and frontiers,
  references, boundary slot distinctness, mechanism-specific artifacts, and
  every `MechanismFormV0` admission are rechecked in Rust.
- Saving writes a same-directory temporary file, flushes it, renames it over
  the requested `.adva` path, and synchronizes the directory on Unix.
- Loading selects one named entry point only after validating the entire graph
  and returns the resolved transition plus a load certificate.
- Python remains a thin path, mapping, and entry-point adapter.

No `.adva` program, example, or fixture is committed. The first program is
intentionally left for the user to author.

## Consequences

The document can now distinguish a ready invocation from recorded history
without making either state intrinsic to a carrier. Mechanisms remain in the
document as edge labels. A recorded result, evidence carrier, or history can
be fed into any later input role by an explicit shared carrier reference, so
the reusable structure survives save and load.

The document is self-describing as an invocation graph but still contains
artifact cache references rather than embedded durable content. Loading does
not resolve those artifacts, authenticate them, execute a frame, prove the
origin of recorded outputs, allocate stable semantic identities, or schedule
feedback. A checked ready frame is a formation judgment, not a successful
computation, verification, or learning result.

## Promotion gate

A stable format still requires source/container dispatch with Lisp, durable
artifact resolution, cryptographic authenticity, certified mechanism-output
provenance, an executor transition that atomically records outputs, recovery
and locking for concurrent writers, migration rules, and integration with
stable `adva.ir` identities and certificates. Feedback or unbounded cycling
requires a separate approved semantics.
