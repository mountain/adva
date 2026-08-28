# Semantic scope: PSC0 bootstrap

This repository begins with a finite, binder-free, linear core inspired by the
Typed Sharing Diagram Calculus. `PSC0` is an engineering scope label, not a
claim that the surrounding calculus has been completely presented.

## Included

- immutable typed module and function terms;
- finite acyclic module linking;
- typed input and output frontiers;
- explicit `id`, composition by typed `call`, `tensor`, `swap`, `copy`, and
  `discard`;
- selected real arithmetic operations;
- deterministic source and occurrence paths;
- lossless history and JSON round-trip;
- scalar realization and forward differentials;
- value and source/history observations as different interfaces.

## Explicitly excluded

- local term binders, substitution, and alpha equivalence;
- recursion and cyclic modules;
- implicit contraction, aliases, memoization, and CSE;
- merge or source identification;
- normalization as an in-place mutation;
- deriving equation cells from equal values or equal observations;
- objectification search or stable objectification APIs;
- generic proof transport or a choice among `Cat`, `Gpd`, and stratified
  alternatives;
- full HPC, sheaf/stack semantics, universality, faithfulness, fullness, and
  full abstraction;
- physical interpretations of curvature, mass, or spacetime.

## Equality interfaces

The initial core distinguishes:

1. definitional equality of immutable IR;
2. realized value equality for declared inputs;
3. observational equivalence under a named policy;
4. explicit-cell equivalence, which requires an `EquationCell` value.

Only the first two are executable in the bootstrap. Observational result types
are present for K1/K2 calibration. No interface lifts an observation back to a
cell.

## Certificates

Compilation and module linking return a `CompilationCertificate`. Evaluation
and forward differentiation return their own certificates. A certificate says
only what its fields and scope record. It does not certify a general theorem.

Search-style APIs, when introduced, must return `Yes`, `No` with a checked
countercertificate, or `Unknown`. Timeout and exhaustion are `Unknown`.

