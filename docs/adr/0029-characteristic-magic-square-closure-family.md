# ADR 0029: Let one arithmetic closure generate a bounded internal family

## Status

Accepted for the version-zero research companion, subject to executable replay.
This does not add a stable solver, scalar type, symmetry quotient, or closure
operator to `adva.ir` or the Lisp language.

## Context

Research 0118 established that one exact polynomial identity can be transported
without identifying occurrences or erasing route provenance. That experiment
started with a closure selected in advance. It therefore did not test whether a
finite search could discover a closure, preserve interruption, and then use the
new certificate as an internal generator of further structure.

A suitable first problem must have a large finite search space, an exact local
and global closure predicate, several nontrivial symmetries, overlapping local
constraints, and a known positive control. The order-four normal magic-square
problem supplies all five without requiring approximate arithmetic.

## Decision

Search assignments of `1..=16` to sixteen row-major cells. Four rows, four
columns, and two diagonals must each have additive residual

\[
\sum_{i\in L}x_i-34=0.
\]

The complete-domain and no-repetition condition is witnessed independently by
the exact characteristic-polynomial identity

\[
\prod_{i=0}^{15}(t-x_i)=\prod_{k=1}^{16}(t-k).
\]

The two checks must not substitute for one another. The frozen negative control
swaps two cells: it preserves the characteristic polynomial but breaks several
line incidences and is therefore a `separation`, not an execution zero.

Use the common triadic interface under the existing `learn` CLI command:

| slot | reading |
| --- | --- |
| `subject` | pending finite search frontier |
| `method` | frozen row-major depth-first policy and exact pruning contract |
| `object` | recorded node fuel |
| `history` | expansion/cut counts, unselected closures, and two fill schedules |
| `result` | selected exact closure and arithmetic separation control |
| `evidence` | closure family, coherence checks, influence graph, and next frontier |

Earlier valid solutions are retained by content digest. The selection rule stops
at the first solution whose orbit under clockwise rotation, vertical reflection,
and complement `x -> 17 - x` has sixteen distinct members. This is an explicit
experimental choice favoring a richer generated family; it does not make the
earlier eight-member closures false or inferior in any observer-independent
sense.

Once selected, the closure is unfolded under the three generators. Content-equal
members are shared, but every member has a fresh research-local occurrence.
Every member emits three directed generator edges. Six relations are checked at
every member: rotation order four, reflection order two, complement order two,
the two complement interchange squares, and reflection--rotation conjugacy.
The ten local line constraints are also intersected by exact shared cell
coordinates, producing a finite influence graph.

## Consequences

- One discovered closure becomes a generator rather than merely a terminal
  answer.
- Different fill schedules can share one endpoint content while retaining
  different histories and factor-ledger traces.
- The generated family distinguishes members, edges, coherence relations,
  reusable local line content, and overlapping constraint occurrences.
- Fuel exhaustion remains an open, replayable frontier. Resumption must reach
  the same selected content as one uninterrupted run under the same frozen
  method.
- A valid but unselected closure is retained rather than renamed as failure.
- A line-incidence failure is not encoded as a multiplicative zero; the branch
  is separated or cut.

The result is a finite closure ecology, not evidence that arbitrary certificates
self-organize, that every local closure has productive descendants, or that the
generated graph is a semantic moduli space. The three transformations are
problem-specific automorphisms supplied by the frozen method. Future experiments
must learn or justify generators rather than assume them.
