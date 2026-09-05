# ADR 0018: Derive witness bindings from certified graft frames

- Status: accepted for bounded research V0
- Date: 2026-09-04

## Context

ADR 0017 made witness templates and proof artifacts reusable, but its only
instantiation entry point required callers to assemble three complete
`HoleBindingV0` records. That duplicates information already retained by the
compiler: a `CompilationArtifact` contains the checked diagram and its
certified `GraftTrace`, and every ordered graft hole names its exact entry
wire.

Accepting a diagram and a trace as unrelated parameters would permit accidental
cross-compilation pairing. Choosing one occurrence silently from a merged wire
would also turn provenance ambiguity into hidden policy.

## Decision

Add `FormedCellV0::instantiate_from_graft` with these boundaries:

- it accepts one `CompilationArtifact` as the indivisible diagram/trace
  context and one exact `GraftFrameId`;
- both the compilation and graft certificates must report fully checked;
- the certificate frame ledger and root frame must still link to the compiled
  diagram;
- the selected frame must expose exactly three ordered holes and entry wires;
- each entry wire must be a checked diagram wire with exactly one lineage
  occurrence;
- source and path are looked up from that existing occurrence rather than
  supplied by the caller;
- repeated occurrences still fail as implicit aliasing; and
- the resulting instance records a `BindingOriginV0::GraftFrame` containing
  both certificate identifiers, frame identifier, scope path, caller, and
  callee.

The existing checked-diagram entry point remains available and records its
validation certificate in `BindingOriginV0::CheckedDiagram`.

## Consequences

- Ordinary compiler-produced triadic calls become reusable witness instances
  without manual reconstruction of source, occurrence, and path triples.
- The proof artifact remains reusable while every instance ordinal and every
  upstream occurrence identity stays distinct.
- Root/trace detachment, unknown frames, non-triadic frames, and empty or
  merged entry lineage fail before a proof-instantiation node is inserted.
- Merged lineage is a visible future design obligation. V0 provides no
  first-occurrence convention and no implicit quotient.

## Promotion gate

A stable successor needs an explicit algebra for a hole whose entry wire has
zero or multiple lineage occurrences, a decision about exact arithmetic in
program values, and a versioned relationship to `ProgramTerm`. This ADR does
not authorize any of those extensions.
