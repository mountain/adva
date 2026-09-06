# ADR 0040: scoped three-verifier arithmetic calibration

Status: accepted for bounded research only, 2026-09-06.

## Context

Research 0151 established library-driven proposal recipes, not an advantage
over ordinary macros. Independent formal arithmetic libraries can calibrate
selected proposals and expose domain/guard mismatches before further search.

## Decision

Implement Research 0152 in a new Rust example and a bounded Python supervisor.
Rust owns arithmetic syntax, candidate reconstruction, exact checking and
witnesses. Python only copies Rust-produced proof text to external checkers,
supervises finite resources and records evidence. No foreign proof or score
authorizes a native semantic identity. Preserve the old snapshots and source
fingerprints. Use pinned Lean core and a fully audited pinned set.mm database.

Keep theory interpretations, guards, translation, proof checks, search scores
and path histories separate. Batch external checking admits an entire round
only after every selected edge passes; provisional Rust search is not a
three-verifier result. Comparison uses the fixed contract's seeded random
and residual-guided arms, including failures and full checking overhead.

## Consequences

This can provide reproducible finite cross-calibration and search evidence.
It cannot establish three-computation, a general knowledge-space topology,
SGD, native contraction, a new stable operation, or a shorter-proof theorem.
Research 0090 and the research/engineering agenda remain prerequisites for
stronger promotion. Path deletion is not authorized by endpoint equality.
