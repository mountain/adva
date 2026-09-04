# ADR 0017: Keep reusable six-word witnesses in a Rust research companion

- Status: accepted for bounded research V0
- Date: 2026-09-04

## Context

The proposed six-word language needs two judgments that the current PSC0
kernel does not provide:

1. additive formation, where a signed boundary ledger must normalize to zero;
2. multiplicative execution transport, where the residual must normalize to
   one and any concrete intermediate zero is a fault.

The same witness should be reusable, but existing Adva boundaries prohibit
identifying program occurrences by equal values, structural equality, or a
content hash. The existing historical-character calibration remains a Python
research presentation and does not provide a Rust proof store or executable
exact arithmetic witness.

## Decision

Add `adva-witness` as a Rust research V0 crate depending only on `adva-ir`.

- The corrected six declarations live in one `SeedRegistryV0`.
- Formation uses a sparse signed ledger. Every composed or instantiated
  component must already have zero relative additive residual; invalid parts
  may not cancel each other after composition.
- The printed value `1` for `| : ||| = 1` retains three unit-slot occurrences.
  The `+` and `*` values each retain their central witness slot.
- Pure finite expressions use integer atoms, named holes, addition, and
  multiplication. They normalize exactly to sparse polynomials over `BigInt`.
- A transition carries the exact symbolic residual `after / before`. It closes
  only when numerator and denominator are the same canonical polynomial.
- Concrete execution visits the retained expression tree and returns
  `ZeroFault` as soon as any leaf or intermediate value is zero.
- A `WitnessProofV0` is one node in a finite dependency DAG. A BLAKE3 digest is
  used only as an artifact cache key and is collision-checked against content.
- `CellTemplateV0` is linear and has exactly three ordered, role-distinct
  holes. `FormedCellV0` certifies additive zero. Each instantiation receives a
  fresh instance ordinal and binds existing Rust-owned source, occurrence, and
  occurrence-path data. Repeated source IDs are allowed; repeated occurrence
  IDs are rejected as implicit sharing.
- `ExecutedCellV0` is available only when the instance artifact has additive
  residual zero, multiplicative residual one, and all concrete zero guards
  succeed. The program result is separate and need not equal one.

The companion schema is `adva.witness.research` version zero. It does not
change `adva.ir` version 1 or the stable Lisp operation registry.

## Consequences

- One verified parametric proof may be cached and reused by many fresh
  instances without collapsing their program identity.
- The original erroneous first type row `[] > {}` fails the seed ledger; the
  corrected row `[] > ()` passes.
- Equal polynomial shadows do not identify expression occurrences or create
  an `EquationCell`.
- The exact arithmetic is a bounded witness checker, not a newly approved Adva
  value type, parser, full interpreter, specializer, or general arithmetic
  program semantics.
- The V0 expression result is linear in its three template holes. Explicit
  copy must be represented upstream by distinct occurrence bindings rather
  than inferred from repeated variable spelling.

## Promotion gate

A stable successor requires a separate decision for its relationship to
`ProgramTerm::Call`, compiler `GraftTrace`, exact arithmetic value types,
explicit copy/discard in expression syntax, durable artifact import and
revalidation, and certificates that compose with existing program slices.
