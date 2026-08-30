# ADR 0006: Program process before values and compiled projections

- Status: accepted
- Date: 2026-08-30

## Context

The initial kernel correctly preserved explicit sharing, sources,
occurrences, histories, and ordered frontiers, but the stable Rust API still
made numerical evaluation easier to access than causal cuts. Completed pasts,
cut frontiers, and frontier transport were reconstructed only in Python
research tests. This left the architecture short of the theory's central
dependency: constructive substitution, causal development, and cut
organization are readings of one checked program process.

There is also a terminology risk. The Lisp `exp` builtin is a pointwise
expression operation. A process exponential, resolvent, matrix action, and
spectrum require a closed transport and declared observation data. Installing
those names before the common carrier would reverse the intended dependency.

## Decision

Adva treats an open finite program as the native object.

- A function input frontier is its ordered family of holes.
- `ProgramTerm::Call` is PSC0's bounded simultaneous substitution: argument
  programs are checked against the callee boundary and grafted without
  implicit sharing.
- `SharedProgramDiagram` is the checked occurrence DAG produced by finite
  substitution and lowering.
- Scalar evaluation is a certified projection of this DAG.

For every validated finite diagram, Rust may derive a `CausalCut` from a
downward-closed set of operation nodes. The cut contains the unchanged checked
wires whose producers are program inputs or lie in the completed past and
whose consumers remain in the future. Rust may also derive a `CausalStep` for
one enabled event and record the exact consumed and produced cut wires.

Both operations return certificates. They create no values, equations,
coherence cells, source identities, or occurrence identities.

Process exponentials, resolvents, characteristic factorizations, matrices,
spectra, projective completions, and complex scalar completions remain derived
research constructions. The executable `exp` builtin must never be described
as the exponential of a program transport.

## Consequences

- Causality and frontier organization now share one Rust semantic authority
  instead of being separately reconstructed by Python.
- The stable core gains `analyze_causal_cut` and `advance_causal_cut`, but not
  enumeration of all opens, a topology object, arbitrary cut gluing,
  contravariant probe transport, or higher interchange cells.
- Current module calls provide only finite named boundary substitution.
  Preserving nested substitution frames and boundary maps requires a future
  versioned IR decision.
- Matrix and spectral experiments must begin from checked cut transport and
  retain an explicit residual.
- Equality of values, frontiers, or schedule endpoints still does not identify
  program histories.
