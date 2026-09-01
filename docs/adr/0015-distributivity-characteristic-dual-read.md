# ADR 0015: Keep Distributivity Feature Equality Separate from Program Equality

Status: accepted for bounded research V0

## Context

Task two of the three-task validation plan compares `a(x+y)` with `ax+ay`.
The programs have one exact rational polynomial normal form but different
checked diagrams, copy requirements, occurrences, event histories, and graft
frames.  Treating the common polynomial as program identity would silently
erase precisely the construction evidence the experiment is meant to test.

The future IR proposal also requires one authoritative process core with
several evidence-bearing presentations, not several independently mutable
program copies.

## Decision

Add a research-only `DistributivityCharacteristicMachineV0` that:

1. accepts two separately compiled, three-input, one-output PSC0 programs;
2. retains each unchanged Rust IR, compilation and validation certificate;
3. derives one exact triadic boundary transition, its three opposite-pair
   transition relations, one complete `ProgramSlice`, and compiler graft
   evidence from each core;
4. verifies exact adjacent slice and observer composition at one nontrivial
   causal cut;
5. projects the scalar outputs into a bounded canonical feature in
   `Q[a,x,y]`;
6. retains all events, occurrences, histories, and graft frames as residual;
7. uses the same characteristic extractor for learning and proof readouts;
8. returns distinct proved, refuted, observationally equal,
   not-representable, and fuel-exhausted task outcomes; and
9. records explicit refusal of program identification, equation-cell
   construction, provenance erasure, and full learning/proof self-duality.

The positive proof result is a finite polynomial-normalization span with a
fixture-specific factored/expanded operation profile.  It is not a stable
logical judgment or Rust proof object.

## Consequences

- One checked core can support several presentations without a round-trip
  requirement.
- `ObservationallyEqual` becomes executable as a research result while
  remaining distinct from definitional or cell equality.
- A task may compare features only when its observation policy is explicit
  and both full residuals are retained.
- The expanded program's `copy`, constant, and discard history remains
  visible even when its polynomial feature equals the factored program.
- Exact feature inequality yields a finite rational counterexample; budget
  exhaustion does not.
- Python and SymPy remain nonauthoritative adapters over checked cores.

## Rejected alternatives

### Identify equal polynomial features with programs

Rejected because it would conflate extensional polynomial equality with
diagram identity and erase copy, discard, occurrence, and schedule evidence.

### Construct an equation cell in Python

Rejected because only Rust may own semantic cells and the present experiment
has no certified rewrite path between the diagrams.

### Call the two readouts a proved self-duality

Rejected because V0 shares a characteristic kernel but supplies no
contravariant equivalence of rule complexes, branching, or schedules.

### Permit feature projection without residuals

Rejected because the hidden process distinctions are the evidence needed to
audit the abstraction and prevent accidental program identification.

## Promotion gate

Promotion requires a Rust-owned exact polynomial certificate or a
proof-relevant normalization trace, a declared observer policy and
right-to-forget judgment, negative tests beyond the named fixtures, and an
explicit decision about how proof steps reverse on the learning side.
