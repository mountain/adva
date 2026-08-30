# Read-Only Python Views of Grafts and Program Slices

Status: exact adapter result for WP5 of the program-slice phase. Python can
inspect Rust-certified graft traces, program slices, and adjacent-slice
composites. It cannot construct or submit any of those semantic objects.

## Native boundary

A compiled PyO3 `Program` now retains the compiler's complete
`GraftTraceArtifact` beside the validated diagram. A diagram imported from
`adva.ir` version 1 retains no such provenance.

The native object exposes three read operations:

- `graft_trace()` serializes the retained Rust result and certificate, or
  returns `None` for an imported diagram;
- `program_slice(lower, upper)` invokes the Rust analyzer and uses the retained
  graft trace when one exists;
- `compose_program_slices(lower, middle, upper)` derives both adjacent inputs
  inside Rust, invokes exact Rust composition, and serializes its result and
  certificate.

The composition method intentionally accepts three causal pasts rather than
Python-provided slice JSON. Thus Python cannot forge a `ProgramSlice`, mutate a
certificate, or make a reconstructed mapping authoritative by passing it back
to the semantic kernel.

## Typed facade

The public Python facade decodes the returned JSON into frozen adapter types:

- `GraftTraceView` and `GraftTraceAnalysis`;
- `ProgramSliceView` and `ProgramSliceAnalysis`; and
- `ProgramSliceCompositionAnalysis`.

These are inspection snapshots. Nested mappings may be copied or mutated by a
Python consumer, but no API accepts them as semantic input and no mutation can
change the native diagram, trace, slice, or certificate.

## Checked cases

Python tests verify that:

- a nested two-call compilation exposes the Rust root and both call frames;
- an exact copy/add interval exposes graft-linked slices and certificate
  fields;
- adjacent composition equals the direct outer slice;
- an imported diagram still admits compiler-independent slice analysis but
  has neither an invented graft trace nor graft intersections; and
- malformed node identifiers are rejected by the Python type guard while a
  non-past-closed middle cut is rejected by Rust.

No scalar evaluation is used as an oracle for these assertions.

## Remaining boundary

This facade closes the program-slice phase's inspection requirement, not the
theoretical synthesis problem. It adds no semantic authority to Python, no
stored graft provenance to `adva.ir` version 1, no observer probe or pullback,
no canonical E0 grid, and no `P*`.

The next mathematical question is now exposed without an adapter gap: which
extra decorated-boundary or schedule data, if any, makes a contravariant
synthesis map faithful to scope and substitution?
