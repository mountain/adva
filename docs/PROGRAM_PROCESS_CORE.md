# Program Process Core

Status: architectural doctrine for the finite Adva core. The causal-cut and
program-slice APIs described below are exact in their declared scope. Process exponentials,
resolvents, characteristic factorization, objectification, and a foundational
complex scalar field remain research targets.

## The ontological decision

Adva begins with programs, not with values, vectors, matrices, or manifolds.
The native object is an open, finite, affine program:

- its ordered input frontier consists of named holes;
- its body is an expression DAG after explicit sharing is lowered;
- a source and each of its occurrences remain distinct;
- composition grafts actual argument programs into the holes of another open
  program;
- evaluation is one observation of the resulting process, not its identity.

In the current binder-free core, a `FunctionDefinition` is an open program and
`ProgramTerm::Call` is the bounded simultaneous-substitution operation.
Compilation may inline the finite callee body, but checked call history,
operation dependency, sources, occurrences, and lineage remain available.
Local binders, alpha equivalence, arbitrary graph contexts, recursion, and
cyclic substitution remain outside PSC0.

Consequently,

```text
same value does not imply same program
same differential does not imply same program
same compiled action or spectrum does not imply same program
```

No optimization may erase this residual without a declared observation policy
and an appropriate certificate.

## One process, three readings

Write `Prog` for the native open-program carrier. The letters below name
readings of one program process; they are not three unrelated scalar
structures.

### K: construction and substitution

The constructive reading records which open programs are grafted into which
holes, the nesting of those scopes, explicit copy and discard, and the
dependency partial order of the generated events. A legal evaluation schedule
is a linear extension of this construction order; it is not the order itself.

### C: causal and evaluative development

The causal reading orients construction from a completed past toward enabled
future events. Crossing one enabled node replaces the frontier wires it
consumes by the wires it produces. Independent enabled events may admit
different schedules while retaining distinct histories.

### F: cut and frontier organization

The frontier reading selects a downward-closed set of completed events and
reads the checked wires crossing from that past to its future. The result is
an occurrence-decorated open boundary, not a tuple of values and not a vector
space.

These readings are coupled:

```text
construction dependency -> legal causal advance -> new open cut
```

Conversely, the family of completed pasts determines the finite causal order.
Forward scope nesting and reverse cut nesting are therefore covariant and
contravariant readings of the same grafted DAG.

## The exact Rust slice

For a Rust-validated `SharedProgramDiagram`, Adva now exposes:

- `analyze_causal_cut(diagram, completed)`, which checks that `completed` is a
  downward-closed node set and returns every exact wire whose producer is a
  program input or completed event and whose consumer is still in the future;
- `advance_causal_cut(diagram, completed, event)`, which checks that `event` is
  enabled and returns the consumed and produced cut wires;
- `analyze_program_slice(diagram, lower, upper)`, which checks nested causal
  pasts and retains exact interval events, changed boundary wires, unchanged
  through wires, internal events, occurrences, and node-associated history;
- `compose_program_slices(diagram, left, right)`, which revalidates adjacent
  views, checks middle-boundary and event agreement, and returns the exact
  canonical outer view;
- causal-cut, causal-step, slice, and composition certificates, which record
  only their checked finite obligations.

The cut reuses the diagram's `WireRef` values unchanged. It does not rebuild
source or occurrence identities, evaluate expressions, simplify equal values,
or assert a higher cell. Python receives these results through frozen adapter
views over serialized Rust judgments. Composition inputs are derived again
from three causal pasts inside Rust; Python cannot submit a reconstructed slice
or certificate.

This promotes the common carrier of causality and cuts into the semantic
kernel without claiming a topology API, cross-diagram composition, a general
cut-transport functor, or a stable observer pullback.  Equal cut frontiers may
still bound a nonempty interval, and zero-event graft frames have no canonical
nonempty event intersection. On the complete five-cut lattice of one
independent three-event diamond, exact tests cover all nested pairs, triples,
and quadruples. The two legal schedules have different step paths but the same
outer slice, showing that a chosen linear extension is extra data rather than
part of the canonical interval.

## Values and compiled presentations

For a program \(P\), write \([P]_Q\) for its observation under a declared
policy \(Q\). Ordinary scalar evaluation is one such policy. A matrix,
polynomial-like coefficient system, Jacobian, projective action, or spectrum
requires additional chart, basis, pairing, closure, and residual data.

The dependency direction is:

\[
\text{open program}
\longrightarrow
\text{checked shared DAG}
\longrightarrow
\text{causal/cut process}
\longrightarrow
\text{declared observation}
\longrightarrow
\text{optional numerical presentation}.
\]

No arrow is definitionally reversible.

The stable Lisp builtin `exp` is a pointwise expression constructor. It must
not be confused with a future process exponential of an endotransport. In
particular,

\[
\exp([P])\neq[\operatorname{ProcessExp}(P)]
\]

without an explicit process lift and a commuting observation law.

## Time completion, frontier completion, and the characteristic core

The following is the current unifying research target, not stable API.
Suppose a closed or repeated program induces an endotransport

\[
K_P:\mathcal H_Q\longrightarrow\mathcal H_Q
\]

on an occurrence-decorated cut-section carrier admitted by \(Q\). Its two
formal completions are

\[
C_P(t)=e^{tK_P}
\]

for forward causal development, and

\[
F_P(z)=(zI-K_P)^{-1}
\]

for frontier or boundary response. Formally they contain the same iterated
construction terms \(K_P^n\), organized respectively by temporal propagation
and cut depth. Where the analytic relation is defined,

\[
(zI-K_P)^{-1}
=
\int_0^\infty e^{-zt}e^{tK_P}\,dt.
\]

The plain reciprocal \(1/[P]\) is at most one chart value of this family; it
does not by itself retain process or cut organization.

If an observation policy selects a retract

\[
\mathcal H_Q
\mathop{\longrightarrow}^{F_P}
\mathcal V_P
\mathop{\longrightarrow}^{C_P}
\mathcal H_Q,
\qquad F_PC_P=I_{\mathcal V_P},
\]

then the candidate characteristic factorization is

\[
K_P=C_PV_PF_P+R_P,
\qquad
V_P=F_PK_PC_P.
\]

Here \(V_P\) is a characteristic process core. It reduces to a scalar
eigenvalue only for a simple one-dimensional semisimple component. Nilpotent
or extension data must remain in \(V_P\), and unselected history remains in
\(R_P\). Spectral convergence alone cannot create an
`ObjectificationWitness`.

## Complex completion

The current executable scalar core remains Real. Complex points already arise
after observing real projective programs and solving their fixed-point or
characteristic equations. Resolvent parameters, phases, conjugate roots, and
oriented lifts make complex semantic completion natural, but they do not yet
prove that every native program must use a foundational complex scalar field.

Therefore:

- complex arithmetic may enter a declared semantic or numerical completion;
- real checked programs remain valid native programs;
- no `Complex`, `PSL(2,C)`, loop-group, matrix, or spectrum type is installed
  by this architectural alignment.

## Promotion gates

The first promotion below is now complete; later promotions remain in
dependency order.

1. Exhaust the slice laws over a nontrivial independent finite diagram and add
   a read-only Python inspection facade after the Rust API stabilizes:
   completed without changing `adva.ir` version 1.
2. Decide separately whether compiler graft traces belong in a future stored
   IR version; imported diagrams currently have no graft provenance.
3. Introduce probes only with an explicit pairing and pullback certificate.
4. Close a declared endoprocess and distinguish a pointwise `exp` builtin from
   its process exponential.
5. Construct resolvent and characteristic retract data with residuals.
6. Promote any matrix, projective, complex, or spectral interface only as a
   replayable compiled observation.

The architectural invariant is simple:

> Every future value-level normal form must be compiled from a checked program
> process and must state exactly which construction and cut information it
> preserves or forgets.

The first post-phase `P*` calibration adds a sharper gate. A zero-event call
parallel to an independent event is compatible with the identity slice at
both endpoint cuts, and the independent step leaves the frame wire unchanged.
Current data therefore determine a scope/cut incidence fibre rather than a
unique placement. A single-valued `P*` must declare a selection policy or add
scope-boundary markers; otherwise `P*` should first be tested as a relation.
