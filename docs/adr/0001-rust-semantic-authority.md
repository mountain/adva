# ADR 0001: Rust semantic authority and Python adapters

- Status: accepted
- Date: 2026-08-28

## Context

Adva must serve symbolic computation, explicit sharing geometry, future IR
backends, and scientific Python without creating two semantic authorities.
The earlier Python prototype demonstrated K1–K5 in a bounded fragment, but it
also allowed host implementation structure to sit too close to semantic
identity.

## Decision

Rust owns the Lisp engine and all semantic judgments. The typed computation
kernel and sharing-geometric kernel operate on the same
`SharedProgramDiagram`. Rust creates and checks sources, occurrences, histories,
types, cells, observations, calculus results, and certificates.

Python receives opaque checked Rust objects and versioned IR. It may provide
numerical realization, visualization, parameter scans, candidate search, and
SymPy/NumPy/SciPy adaptation. Python does not create or identify source/history
data and cannot authorize contraction, memoization, CSE, or cells.

## Consequences

- Removing Python preserves all semantic verdicts.
- The Python boundary is coarse-grained: modules, programs, IR documents,
  evaluation batches, and certificates—not per-node callbacks.
- Cross-language compatibility is based on versioned serialization, not PyO3
  object identity.
- Rust operations must provide both computation and lineage/differential rules.
- Experimental external-library conclusions must return candidate data that a
  Rust checker can independently validate.

