# Whole-cut program cells: a non-linear seed

Status: bounded research calibration
Date: 2026-08-29
Executable witness: `tests/python/test_shared_expression_program_cells.py`

## Why raise the basic object

A module starts with two different kinds of thing: an algebra and a carrier on
which the algebra acts.  A matrix presentation introduces another choice, a
basis of that carrier.  This is useful after linearization, but it is too late
to serve as the ontology of program geometry.

An arithmetic program already has a more symmetric form.  It is an expression
with typed holes; expressions fill its holes; the result is again an
expression.  The program, its input, and its output therefore live in closely
related expression geometry.  Source sharing is part of the program and must
not be collapsed to equality of realized values.

This calibration raises the basic object by one small step.  Instead of an
expression or an operator, use a **program cell** consisting of:

1. a checked whole program;
2. its checked ordered trace of atomic calls;
3. every sequential cut induced by that trace;
4. the typed frontier and source occurrences carried by every cut.

No vector space, module, polynomial algebra, basis, or matrix is introduced.
The first version required the caller to declare one cut.  The refined
experiment reconstructs the atomic stages from checked call history and
generates the whole finite family of compatible cuts from the program itself.

## Two readings of one cell

Suppose a checked whole program has a declared cut

\[
  P=P_2\circ P_1.
\]

The temporal reading follows the stages from left to right:

\[
  x\longmapsto P_1(x)\longmapsto P_2(P_1(x)).
\]

Let \(U\) be an output neighborhood.  The spatial reading follows the same
cut from right to left:

\[
  P^*U=P_1^*(P_2^*U).
\]

For every input \(x\), both readings meet in the elementary pairing law

\[
  P(x)\in U
  \quad\Longleftrightarrow\quad
  x\in P^*U.
\]

The point of the experiment is not this logical equivalence by itself.  The
point is that the same checked cell carries both readings while retaining the
cut boundary and its source lineage.  Nothing external has to act on a
separate carrier.

## Sharing at the cut

Consider the two checked stages

\[
  S(x)=\operatorname{add}(\operatorname{copy}(x)),
  \qquad
  L(x)=\operatorname{scale}_2(x),
\]

followed by

\[
  Q(x)=\operatorname{mul}(\operatorname{copy}(x)).
\]

The whole programs \(Q\circ S\) and \(Q\circ L\) realize the same scalar
function

\[
  x\longmapsto4x^2.
\]

Consequently, every output interval has the same scalar inverse image under
the two programs.  Nevertheless, their program cells differ at the cut:

- the boundary after \(S\) carries two distinct occurrences of one source;
- the boundary after \(L\) carries one occurrence of that source.

The checked source geometry survives even when both the forward scalar action
and the backward scalar neighborhoods agree.  Thus a spatial carrier made only
from value neighborhoods is insufficient.  The program cell must retain the
source relation crossing its cuts.

## The unit is a visible empty stage

Let \(I(x)=x\) be a declared identity stage.  The two cuts

\[
  Q\circ S
  \qquad\text{and}\qquad
  Q\circ I\circ S

\]

emit the same checked operation nodes and realize the same values.  They do
not have the same call history.  In the richer program cell, the unit is an
explicit stage with no operation nodes, not an automatic erasure of history.

This is the first useful clue about the later appearance of a numerical unit:
`1` should arise only after a declared identity cell is observed or
objectified.  The current calibration does not identify it with a Jordan entry
or a holonomy invariant.

## Compatible cuts form a refinement lattice

Let a checked flat call trace contain (n) atomic stages

\[
  P_n\circ\cdots\circ P_2\circ P_1.
\]

There are (n-1) internal call boundaries.  In the present sequential
fragment, a compatible refinement is exactly a subset

\[
  R\subseteq\{1,\ldots,n-1\}.
\]

The subset partitions the ordered trace into consecutive blocks.  Refinement
adds a cut but never permutes a stage, merges a source, or changes the checked
whole.  Consequently the refinements form the finite Boolean lattice

\[
  \mathcal R(P)=\mathcal P(\{1,\ldots,n-1\}),
\]

decorated at every selected boundary by its typed frontier, left and right
call traces, and checked source lineage.  If (r_i) means adding cut (i),
then the finite data obey

\[
  r_i^2=r_i,
  \qquad
  r_ir_j=r_jr_i.
\]

This commutativity belongs to **resolution of one fixed program**, not to the
program stages themselves.  Temporal composition remains ordered and need not
commute.  The distinction gives a first precise form to the proposed duality:
the temporal side is an ordered trace, while the spatial side is its decorated
cut-refinement order.

## The three-stage diamond is flat

For three genuine stages there are two internal cuts.  Starting with the
uncut whole, one may expose the left boundary and then the right boundary, or
the right and then the left:

\[
\begin{array}{ccc}
 & \varnothing & \\
 \swarrow & & \searrow \\
 \{1\} & & \{2\} \\
 \searrow & & \swarrow \\
 & \{1,2\}. &
\end{array}
\]

The executable witness uses increment, shared doubling, and squaring.  The
two intermediate refinements are different.  Their terminal refinement
signature is nevertheless identical, including both typed boundaries and
their checked source lineages.  Forward evaluation and backward neighborhood
membership are unchanged by either refinement order.

This is a bounded **flatness result for cut refinement**.  It is not an
`EquationCell` or `CoherenceCell`, because Python is only reading Rust-checked
data and may not create semantic identities.  It does show that ordinary
three-stage sequential reassociation produces no holonomy at this level.

## What this supports

The experiment supports the following bounded dependency:

\[
  \boxed{
  \text{checked whole + atomic trace}
  \longrightarrow
  \begin{cases}
    \text{temporal composition},\\
    \text{decorated spatial cut refinement},\\
    \text{contravariant inverse-neighborhood reading}.
  \end{cases}
  }
\]

It also provides a direct no-go:

> Equal forward values and equal scalar inverse neighborhoods do not determine
> the shared program cell.

This makes modules and matrices unnecessary at the foundational level.  They
may still be obtained later by an observation that forgets source geometry and
linearizes the remaining finite data.

## What is not yet proved

The research-local `ProgramCell` is not a stable Adva API.  It reads checked
call, operation, occurrence, and source data but does not create semantic
identities.  The test uses flat leaf-call traces, one-input, one-output finite
`Real` programs, and open scalar intervals.  The Boolean description is proved
only for sequential call boundaries; it is not a theorem about arbitrary
sharing diagrams.

The next genuinely geometric test should leave the flat chain.  A branching
program with sharing and later recombination can have cuts that are not
independent.  Its compatible-cut family need not be a Boolean lattice, and
transporting boundary lineage around two refinement paths may either produce
a checked higher coherence or leave a nontrivial history loop.  That is the
first responsible place to test holonomy.  Numerical exponentials, spectral
scales, or Jordan-like residuals should remain downstream shadows until this
non-flat case is understood.
