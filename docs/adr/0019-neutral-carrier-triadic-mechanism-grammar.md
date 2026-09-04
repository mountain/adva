# ADR 0019: Keep the neutral-carrier triadic mechanism grammar in the Rust research companion

- Status: accepted for bounded research V0
- Date: 2026-09-04

## Context

The reusable witness work exposed a new proposed organization. Computation,
verification, and learning are process labels, while program, proof, and model
are context-dependent readings of retained structure. Treating the latter as
three permanent file kinds made a learned model occupy a different ontological
level from the program or proof that may consume it on the next cycle.

The proposed correction uses one neutral `.adva` carrier, a three-label input
view (`subject`, `method`, `object`), three mechanism edges (`compute`,
`verify`, `learn`), and a three-label output view (`history`, `result`,
`evidence`). The repository already uses `.adva` for Lisp source, however, and
the current research does not authorize a new stable envelope or parser.

The syntax also needs mechanism-relative treatment of open structure.
Computation should reject unfilled subject or object structure; verification
should distinguish an explicit open context from an unexplained mismatch; and
learning should return a fill proposal rather than silently mutate or certify
the subject.

## Decision

Add a bounded checker to the existing `adva-witness` research crate.

- `NeutralCarrierV0` contains one witness-artifact cache coordinate and one
  research-local open frontier. It has no program, proof, or model variant.
- `MechanismInputV0` and `MechanismOutputV0` expose the two ordered label
  triples. `MechanismV0` supplies the three edge labels.
- A frontier site is a finite `(role, hole, occurrence)` coordinate. It is not
  promoted to `adva.ir::HoleId` and is not identified with a function hole,
  cut port, logical obligation, observer aperture, or singularity.
- Compute formation requires closed subject and object frontiers. The method
  frontier is retained for the existing instantiation/execution layer rather
  than reinterpreted by this checker.
- Verify formation permits a nonempty subject frontier only when it is exactly
  declared. A declared site absent from the current subject requires one
  explicit discharge witness. Undeclared sites, repeated discharge, and silent
  weakening are rejected.
- Learn formation requires a nonempty subject frontier and a nonempty finite
  `FillPlanV0`. Targets must be distinct current subject sites. Replacements
  may carry new subholes, which become the retained residual frontier.
- A fill plan is a proposal. Optional evidence does not make it a checked
  substitution, proof, certificate, or specialization result.

`ADVA_FILE_SUFFIX_V0` records the candidate common suffix only. This ADR does
not modify the existing Lisp source format, choose a multi-format container,
or change `adva.ir` version 1.

## Consequences

- The nine primitive words split into three input nouns, three mechanism verbs,
  and three output nouns. The 27 typed routes are their composites, not 27 new
  primitive labels.
- Program, proof, and model can be tested as mechanism-relative readings of one
  neutral carrier without being installed as file-kind enums.
- Open structure receives three distinct policies: compute refuses it,
  verification accounts for it, and learning proposes replacements for it.
- Learning may replace one hole by several smaller holes. No monotone decrease,
  termination, convergence, or successful synthesis claim follows.
- An unbounded global cycle is not implemented. Every checked form is a finite
  productive step; feedback, reloading, scheduling, and persistent container
  semantics remain separate decisions.

## Promotion gate

A stable successor requires a decision on the `.adva` source/container
boundary, Rust-owned identities and certificates, an exact relationship to
`ProgramTerm::Call` and `GraftTrace`, checked packing and unpacking laws,
cross-step substitution provenance, explicit `Unknown`, copy/discard rules,
and finite counterexamples for open computation, conditional verification,
partial learning, replacement collisions, and nonproductive feedback.
