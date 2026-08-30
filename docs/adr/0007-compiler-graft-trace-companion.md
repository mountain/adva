# ADR 0007: Compiler-emitted graft traces as companion artifacts

- Status: accepted
- Date: 2026-08-30

## Context

`ProgramTerm::Call` already performs finite typed substitution, but the
version-one diagram records only a flat `HistoryEvent::Call`.  It cannot say
which nested call occurred inside which argument or callee body, which output
of an argument frontier filled which ordered hole, or which original nodes
belong to those regions.

This missing information blocks the comparison between construction scopes,
causal development, and dual cuts.  It also blocks the proposed expression
factorization `T = P_Y S_T P_X*`: the finite E0 and surreal-cut calibrations
show that neither a bare cut cycle nor an objectified value can reconstruct
ordered substitution history.

There is a further compiler fact that the representation must respect.  One
syntactic call argument can produce several frontier wires, while an argument
containing explicit discard can produce no wire.  Therefore argument regions
and hole bindings are related but are not the same collection.

## Decision

Every successful `compile_function` returns a certified `GraftTraceArtifact`
inside its `CompilationArtifact`.

The trace contains one root frame and one frame for every finite call.  Each
frame retains:

- a deterministic `GraftFrameId` derived from the root function and syntax
  descent path;
- its parent, ordered children, and role in the parent;
- caller and callee names and the callee boundary;
- every syntactic argument region, including zero-output regions;
- an explicit map from each ordered hole to one argument output;
- the instantiated callee-body nodes;
- exact entry and exit wires;
- the corresponding flat call-history index.

Argument regions and callee-body regions are stored separately.  Nested calls
inside an argument are children of the containing call frame but retain the
caller's function as their caller.  Nested calls inside the callee body retain
the callee as their caller.  This distinction is checked from scope paths and
region roles.

The compiler independently validates the complete companion trace before
returning it.  `GraftTraceCertificate` checks deterministic identifiers,
parent/child nesting, ordered hole bindings, argument/body separation,
boundary maps, original node/wire membership, and exact call-history links.

The companion is not embedded in `SharedProgramDiagram` and does not change
the `adva.ir` version-one schema.  Imported stored diagrams therefore have no
compiler graft trace unless their linked source modules are recompiled.

## Consequences

- The finite construction reading K now has an exact compiler-produced scope
  tree without making Python a semantic authority.
- A frame entry or exit is a typed sub-boundary map.  It is not automatically
  one whole causal cut: unrelated wires outside the syntax frame may cross the
  same global cut.
- Syntax arguments, ordered holes, and emitted node regions cannot be
  identified pairwise.  Multi-output and zero-output arguments remain
  explicit.
- The trace is sufficient input for the next `ProgramSlice` intersection
  tests, but it does not itself define a slice or a scope/cut bijection.
- No `Probe`, `pullback`, `P*`, surreal objectification, equation cell, or
  stable dual presentation is introduced.
- Promotion into a future stored IR version requires a separate decision and
  a validation rule for imported provenance.
