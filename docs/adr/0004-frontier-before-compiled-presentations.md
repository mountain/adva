# ADR 0004: Frontier before compiled presentations

- Status: accepted
- Date: 2026-08-28

## Context

The bootstrap used `tensor` for an AST form that recursively lowered several
terms and concatenated their output wires. It created no operation node, had no
tensor-product object, and carried no associator, interchange, or coherence
data. The name therefore asserted substantially more mathematics than the IR
implemented.

Process Geometry also has promising polynomial-like and matrix-like
constructions. Existing calibrations give them narrower meanings:

- a polynomial-like object is a chart- and observer-relative scalar carrier,
  basis, coefficient system, or recurrence;
- a matrix-like object is an action or transport presentation relative to a
  declared basis, often useful for offline compilation and replay.

Neither is a generic parallel-product constructor. Existing evidence also
separates a native process evaluator from its optional coefficient and matrix
compilers.

## Decision

The core surface form is `frontier`, represented by
`ProgramTerm::Frontier`. It means only an ordered typed open boundary. It does
not create a program node and does not claim Cartesian, tensor, direct-sum, or
matrix semantics.

The old `tensor` surface form is rejected rather than retained as an alias.
This prevents pre-release schema version 1 from acquiring two names with
different theoretical expectations.

Polynomial-like and matrix-like structures will enter, if earned, as separate
compiled artifacts over a checked `SharedProgramDiagram`. Their provisional
engineering names are `PolynomialPresentation` and `ActionPresentation`:

- `PolynomialPresentation` must declare chart, observer, basis/support,
  coefficient domain, truncation or closure, decoder, and residual
  certificate;
- `ActionPresentation` must declare source presentation, basis, action or
  transport table, composition law, decoder, and replay certificate.

These names are construction targets, not stable Rust types in this phase.
They may be promoted only after an additional independent calibration forces a
common interface beyond the current power-dominant scalar example.

## Consequences

- The executable IR no longer implies that its multiple-output syntax is a
  monoidal tensor product.
- Sharing remains an explicit `copy` operation with two occurrence paths.
- Polynomial and action presentations cannot silently become the ontology of
  the nonlinear process or its default numerical evaluator.
- A later interpretation may map a `Frontier` into a monoidal product, direct
  sum, module basis, or another target, but that map and its coherence are
  additional checked data.
