# ADR 0003: Single Rust operation registry

- Status: accepted
- Date: 2026-08-28

## Context

An Adva builtin is simultaneously a typed program generator, a numerical
operation, a differential rule, and a transport rule for source occurrences.
The initial bootstrap named the same operations separately in the parser,
lowerer, and evaluator. Although every definition remained in Rust, this left
room for the computational and sharing-geometric meanings to drift.

## Decision

Every stable builtin version is declared once as an `OperationSpec`. The
declaration contains:

- namespace, name, and version;
- whether the operation is a Lisp surface form;
- exact parameter names;
- input and output type boundaries;
- an explicit `LineageRule`;
- the scalar forward-differential realization.

The parser recognizes surface operations through this registry. Typed lowering
resolves the same declaration before it transports lineage. Evaluation and
forward differentiation resolve it again and reject an IR node whose
parameters or boundaries no longer match the registered version.
Differential certificates record the fully versioned rule identifier.

`tensor` remains a term constructor rather than a scalar operation node.
Numeric literals lower to the registered `constant` operation but `constant`
is not exposed as a Lisp list form.

## Consequences

- Adding a builtin requires one semantic declaration and a completeness test.
- Operation versions are part of the IR contract; changing a rule requires a
  new version rather than reinterpretation.
- Imported or externally stored IR cannot bypass operation-boundary checking.
- The registry does not authorize optimization, source merging, proof cells,
  or objectification.
- General reverse mode, higher derivatives, symbolic simplification, and
  non-scalar realizations require later, separately scoped interfaces.
