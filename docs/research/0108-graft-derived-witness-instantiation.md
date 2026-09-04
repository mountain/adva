# Graft-Derived Witness Instantiation

Status: bounded Rust research implementation. This note connects the reusable
six-word witness kernel to existing compiler substitution evidence without
changing `adva.ir` version 1 or `ProgramTerm`.

## 0. The removed manual step

The original V0 path was:

```text
DiagramValidationArtifact + three caller-built HoleBindingV0 records
    -> CellInstanceV0
```

The caller had to copy each occurrence identifier, source identifier, path,
hole index, and role even when the compiler had already emitted the exact
ordered graft boundary. The new bounded path is:

```text
CompilationArtifact + GraftFrameId
    -> verify linked certified triadic frame
    -> derive three HoleBindingV0 records
    -> CellInstanceV0 with BindingOriginV0::GraftFrame
```

The proof-DAG node and its BLAKE3 cache key are unchanged. Only the fresh
instance's binding construction and provenance record differ.

## 1. Why the whole compilation artifact is the input

`CompilationArtifact` packages one diagram, its compilation certificate, and
its `GraftTraceArtifact`. Taking that package as one argument makes the common
case resistant to accidental pairing of a diagram from compilation A with a
trace from compilation B.

The adapter also checks the remaining internal links it consumes:

1. both certificates report fully checked;
2. the certificate frame ledger exactly equals the trace frame order and has
   no repeated identifier;
3. the trace root still names the compiled function, boundary, node region,
   and outputs; and
4. the selected frame's hole, boundary-port, and entry-wire ledgers agree at
   every position.

Certificate identifiers are audit references. They do not become program,
source, occurrence, or artifact identities.

## 2. Singleton-lineage rule

For each of the three ordered entry wires, V0 requires

\[
|\operatorname{lineage}(w_i)|=1.
\]

The unique occurrence is resolved in the compiled diagram, and its existing
`SourceId` and `OccurrencePath` become the derived binding. A lineage of size
zero has no occurrence to bind. A lineage of size greater than one has more
than one defensible origin. Both return `NonSingletonGraftLineage`.

This is not a claim that merged lineage is invalid. It is a refusal to smuggle
in a projection policy. A later version may add an explicit multi-occurrence
hole carrier or a caller-declared selector, but either choice needs its own
formation and execution laws.

## 3. Retained provenance

Every instance now has one `BindingOriginV0`:

| variant | retained evidence |
|---|---|
| `CheckedDiagram` | diagram-validation certificate identifier |
| `GraftFrame` | compilation certificate, graft certificate, frame, scope path, caller, callee |

This record explains how the binding was obtained. It does not authorize
certificate replay after mutation and does not identify two otherwise distinct
instances.

## 4. Executable boundary tests

The Rust suite checks:

1. a certified three-hole call derives the same three singleton occurrences
   named by its entry wires;
2. source and path are recovered from the compiled occurrence ledger;
3. certificate and frame provenance survive into the instance;
4. the derived instance executes under the existing exact witness semantics;
5. an unknown frame and a certified two-hole frame are rejected;
6. a three-hole call whose first argument merges two source lineages is
   rejected without implicit selection; and
7. detaching the root outputs from the compiled diagram is rejected.

## 5. Nonclaims

This adapter does not compile witness expressions into Lisp, add witness terms
to `ProgramTerm`, reinterpret a graft frame as an equation cell, validate a
serialized certificate cryptographically, select from merged lineage, or make
the polynomial observation into stable program semantics. The Rust compiler
and its existing certificates remain the semantic authority for the diagram
and graft data that the research companion consumes.
