# ADR 0002: Explicit finite Lisp modules

- Status: accepted
- Date: 2026-08-28

## Decision

The initial Lisp has explicit `module`, `import`, `export`, `def`, `fn`, and
`call` forms. Imports list symbols; wildcard imports are absent. Module names
and function names are serialized as qualified names.

Function parameters are typed boundaries. The PSC0 body has no local binding
form. Calls are linked and type checked in Rust. Lowering records module-call
history even when a finite callee body is inlined.

Recursive calls and cyclic import graphs are rejected. Guarded recursion will
require a later ADR and explicit observation-depth semantics.

## Rationale

This supplies real modular composition without introducing binder,
substitution, alpha-equivalence, or implicit sharing into the first core. It
also keeps external Python modules from becoming semantic namespaces.

