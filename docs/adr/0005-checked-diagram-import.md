# ADR 0005: Checked diagram import boundary

- Status: accepted
- Date: 2026-08-29

## Context

`SharedProgramDiagram::from_json` proves only that a document decodes under
the supported schema and version. Serde can construct data that the compiler
would never emit: duplicate identifiers, forward graph references, forged
lineage metadata, reused frontier endpoints, source changes across copy, or
history events that do not match the graph.

Treating successful decoding as semantic authorization would let Python or a
stored document introduce implicit contraction, source merging, or false
history while retaining a well-shaped JSON object.

## Decision

The Rust Lisp kernel exposes `import_diagram_json` and `validate_diagram`.
Successful validation returns a `DiagramValidationArtifact` containing the
immutable diagram and a `DiagramValidationCertificate`.

The checker validates, for the finite `adva.ir` version 1 scope:

- non-empty, unique, and boundary-consistent identifiers;
- canonical rational parameters and registered operation boundaries;
- unique, topologically ordered node producers;
- exact producer-derived wire types and lineage;
- exactly one consumption of every domain or node-output endpoint;
- codomain type and order;
- exact occurrence-path records and distinct independent input sources;
- source preservation and binary path extension at every explicit copy;
- a disjoint partition of occurrences into source roots and copy children;
- graph-matching operation and copy history;
- an empty rewrite trace.

Call identifiers are checked, but imported call provenance is not replayed
without the linked source modules. The certificate scope states this boundary.
Non-empty rewrite traces fail closed until a stable rewrite-certificate checker
exists.

Evaluation and differentiation invoke the same integrity checker even for a
Rust value supplied directly. The Python `load_program` entry point can only
return a program after the Rust importer succeeds. Imported programs have a
validation certificate but no compilation certificate.

## Consequences

- JSON decoding remains available as a data-model operation and is documented
  as weaker than semantic import.
- Python cannot authorize source identity, aliasing, contraction, or history
  by editing JSON.
- Moving values between host objects or serialization addresses has no effect
  on validation.
- A validation certificate proves only the listed finite implementation
  invariants. It does not certify objectification, rewrite correctness,
  proof-cell existence, or a general mathematical theorem.
