# ADR 0014: Separate sibling comparison from source quotient

- Status: accepted
- Date: 2026-09-01

## Context

The single-diagram triangular calibration grounds three local angle relations
but refuses their raw circular composite. Each adjacent pair consists of two
distinct occurrences carrying the same checked source. Treating that situation
as one generic "connector" would conflate at least three operations:

- strict identity of an occurrence;
- comparison of two retained copy siblings; and
- projection that identifies occurrences by source.

The last operation forgets information. The second need not, but its symmetry
must not be mistaken for inverse execution of `copy`.

## Decision

Add the research-only
`adva.connector_research.ConnectorCalibrationMachineV0`.

The adapter consumes one complete
`TriangularThroughArtifactV0` and compares three readings without changing
the Rust carrier.

1. Exact identity uses only diagonal incidence pairs.
2. Direct-sibling comparison relates two distinct same-source occurrences only
   when their checked paths share a parent and end in branches 0 and 1. The
   finite comparison is symmetric and retains both endpoint identities.
3. Source quotient projects each selected incidence to its existing checked
   `SourceId` and records the complete two-occurrence fibre.

Each trial separately records finite-composition and promotion verdicts. A
nonempty finite relation never implies semantic closure. Source projection
always records that forgetting is required and unauthorized.

The complete triangular `ProgramSlice` remains nested in the result. Python
allocates no source, occurrence, connector, quotient, proof, or certificate
identity.

A same-source cousin fixture is mandatory. Paths `(0,)` and `(1, 0)` must
not receive a direct-sibling witness, even though source projection still
closes the coarse source cycle.

## Consequences

- Strict occurrence identity leaves the triangular cycle empty.
- Three direct-sibling comparison relations close one finite
  occurrence-indexed candidate cycle while retaining all six occurrences.
- Projection to source also closes, but only after a visible many-to-one loss.
- The cousin fixture distinguishes the two positive mechanisms: sibling
  comparison refuses while source quotient still closes.
- A relational atlas may glue local charts without first quotienting their
  fibres.
- Source-level closure cannot justify occurrence-level closure, contraction,
  or `ProvenanceHide`.
- Symmetric comparison does not make copy reversible or construct a program
  path.
- No stable connector, right-to-forget judgment, circular through object,
  normalization, logic, confluence, interpreter, or universality claim is
  promoted. A stable successor requires Rust-owned result and certificate
  types.
