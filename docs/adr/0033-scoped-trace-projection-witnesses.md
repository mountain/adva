# ADR 0033: Add scoped trace projection witnesses

Status: accepted for the research V0 companion; no stable API promotion.

## Context

Research 0114 keeps three cross-side characteristic questions open. Its
existing fixture also contains a positive count factorization and a negative
example for recovery of the full construction projection. These facts need
separate checked statements rather than edits to historical open states.

## Decision

- Add a research-only count rule, temporal path witness, and paired projection
  witness in `adva-witness`. Reuse the existing path validator and encoder;
  expose that internal function only within the crate.
- Require a nonempty complete three-port recorded path and checked u32
  arithmetic for temporal counts. Retain the complete path and digest.
- Derive the construction obstruction only from a checked common calibration:
  equal time and space inputs, unequal complete construction outputs.
- Freeze the pair schema and method identifier. Recheck all source and
  derived data on checked decoding. Keep all five original M6 questions.
- Provide a Cargo example and a CI byte replay without extending the `adva`
  CLI, Lisp, neutral document schema, or version-one IR.

## Consequences

The count result is reusable on shorter checked paths. The negative result
survives exchange of the two mechanism labels in a fresh checked document.
Malformed paths and forged claims are rejected. No verification obligation
is discharged, and no digest, projection match, or structural count acquires
execution provenance, ordered holonomy, or external truth. A new method is
required for any later semantic admission.
