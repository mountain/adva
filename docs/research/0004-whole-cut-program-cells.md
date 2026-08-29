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
2. one declared way to cut it into checked stages;
3. the typed boundary at every cut;
4. the source occurrences that cross each boundary.

No vector space, module, polynomial algebra, basis, or matrix is introduced.

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

## What this supports

The experiment supports the following bounded dependency:

\[
  \boxed{
  \text{checked whole + cut + source boundary}
  \longrightarrow
  \begin{cases}
    \text{temporal composition},\\
    \text{spatial inverse-neighborhood reading}.
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
identities.  The test uses one-input, one-output finite `Real` programs and
open scalar intervals.

The next theorem must replace the declared two-stage cut by all compatible
cuts of one checked program and prove their three-stage associativity.  After
that, the first genuinely geometric test is whether two different cut paths
form a coherent cell or leave a nontrivial history loop.  Only then is it
responsible to ask whether numerical exponentials, spectral scales, or Jordan
units are shadows of this structure.
