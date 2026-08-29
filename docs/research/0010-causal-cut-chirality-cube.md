# Causal-Cut Derivation of the Chirality Carrier

Status: bounded endogenous derivation on one checked local three-cube, not a
general cubical or Clifford API.

## Question

The preceding calibration represented the six-dimensional carrier as

$$
W
=
(T\oplus SR)
\oplus
(S\oplus RT)
\oplus
(R\oplus TS)
$$

and used an external grade-aware geometric product to obtain a common
orientation action $J^2=-I$.  That model clarified the target but left its
main algebraic ingredients as assumptions.

The present question is stricter:

> Can the grade, anticommutation, positive direction pairing, and chirality
> action be derived from the interaction of checked causality, completed
> cuts, and source-decorated frontiers?

The answer is positive on one minimal local three-direction program cube.
The derivation also identifies exactly why interchange alone is insufficient.

## The checked three-branch fixture

One checked input is copied twice to produce three distinct occurrences of
one source.  At the resulting cut, three unary events are simultaneously
enabled on disjoint frontier wires:

$$
e_1=\mathrm{neg},\qquad
e_2=\mathrm{scale}_2,\qquad
e_3=\mathrm{id}.
$$

Their scalar outputs are later recombined, but the local calibration stops
after the three independent events.  If $U$ is the completed past containing
the two copy events, define

$$
U_A
=
U\cup\{e_i\mid i\in A\},
\qquad
A\subseteq\{1,2,3\}.
$$

All eight $U_A$ are checked completed pasts.  They form a Boolean interval
$B_3$ inside the generally non-Boolean Alexandrov lattice of the whole
program.

This local cube simultaneously carries the three readings:

| reading | checked datum | role |
|---|---|---|
| causality | enabled forward inclusions $U_A\subset U_{A\cup\{i\}}$ | directs time |
| cut | membership of each event in the completed past | records which construction crossed |
| frontier | three distinct occurrences of one source and their replacements | supplies the spatial boundary |

The cube is not imposed on an arbitrary value space.  Its vertices, edges,
and frontier decorations are read from one Rust-checked program diagram.

## Generation edges and cut coordinates are dual

Let $g_j$ denote the forward edge that moves $e_j$ from the future across the
cut into the completed past.  Every direction has a cut-membership coordinate

$$
x_i(U_A)
=
\begin{cases}
1,&i\in A,\\
0,&i\notin A.
\end{cases}
$$

The discrete change of $x_i$ along $g_j$ is

$$
dx_i(g_j)=\delta_{ij}.
$$

This pairing is not a separately chosen Euclidean metric.  Its diagonal
$+1$ comes from the causal orientation: a legal forward step changes its own
event from future to past exactly once.  Its off-diagonal zero comes from
independence: moving $e_j$ does not change whether another event $e_i$ has
crossed the cut.

The cut therefore supplies a co-direction dual to every generation
direction.

## Interchange derives the exterior sign

Every pair of independent directions forms two checked schedules with the
same final source-decorated frontier:

$$
g_i g_j
\quad\Longleftrightarrow\quad
g_j g_i.
$$

There are six square faces in the three-cube.  Orienting the directions by
their deterministic checked order gives opposite orientations to the two
boundary paths of each square.  Consequently the oriented composite obeys

$$
g_i\wedge g_j=-g_j\wedge g_i.
$$

This is the endogenous origin of the bivector sign used in the preceding
model.  It comes from oriented interchange of construction histories, not
from commutativity or noncommutativity of the scalar arithmetic operations.

The three-dimensional orientation is the sign of a schedule permutation.
Cyclic permutations preserve it; one adjacent interchange reverses it.

## Why interchange alone does not produce complex structure

Let $\varepsilon_i$ be exterior multiplication by $g_i$.  Interchange gives

$$
\varepsilon_i\varepsilon_j
+
\varepsilon_j\varepsilon_i
=
0.
$$

But it also gives

$$
\varepsilon_i^2=0.
$$

Hence the pure exterior volume

$$
\varepsilon_1\varepsilon_2\varepsilon_3
$$

is nilpotent when applied twice.  A concurrency cube by itself therefore
produces an exterior or dual-like structure, not the desired order-four
orientation lift.

This is a useful no-go:

> Interchange supplies grade and antisymmetry, but cannot by itself derive
> $\Omega^2=-1$.

The missing operation must use the dual information carried by the cut.

## Cut contraction completes the action

Let $\iota_i$ contract an oriented composite by the cut cochain $dx_i$.  Its
definition is fixed by the derived incidence pairing

$$
dx_i(g_j)=\delta_{ij}
$$

and the alternating orientation of composite directions.  Define

$$
c_i=\varepsilon_i+\iota_i.
$$

Direct expansion gives

$$
c_i c_j+c_j c_i=2\delta_{ij}I.
$$

Thus the Clifford relation is not assumed in this calibration.  It is the
combined action of:

1. wedge insertion from oriented interchange;
2. contraction from reading a generated direction back through the cut.

The first is construction-facing; the second is boundary-facing.  Their
pairing is directed by causality.

## The six-dimensional carrier reappears

Let $E=\langle g_1,g_2,g_3\rangle$.  The grades one and two form

$$
W=\Lambda^1E\oplus\Lambda^2E
$$

with cyclic basis

$$
(g_1,g_2,g_3,g_2g_3,g_3g_1,g_1g_2).
$$

Define the total checked-cut orientation action

$$
\Omega=c_1c_2c_3.
$$

The derived relations imply

$$
\Omega^2=-I
$$

on the full eight-dimensional exterior state and, in particular, on $W$.
Its restriction is

$$
\Omega(a,b,c,bc,ca,ab)
=
(-bc,-ca,-ab,a,b,c).
$$

Therefore

$$
W
=
\langle g_1,g_2g_3\rangle
\oplus
\langle g_2,g_3g_1\rangle
\oplus
\langle g_3,g_1g_2\rangle,
$$

and every pair carries

$$
\begin{pmatrix}
0&-1\\
1&0
\end{pmatrix}.
$$

The characteristic polynomial is again

$$
(\lambda^2+1)^3.
$$

This time the result is not obtained by feeding a chosen Clifford
multiplication table into the experiment.  The action is reconstructed from
the checked causal cube, its cut coordinates, and its interchange
orientations.

## Chirality under exchange

Permuting the three independent construction directions transports both
their cut coordinates and their oriented faces.  Exhaustively over all six
permutations,

$$
P_\pi\Omega P_\pi^{-1}
=
\operatorname{sgn}(\pi)\Omega.
$$

In particular, exchanging the two directions designated as temporal and
spatial sends

$$
\Omega\longmapsto-\Omega=\Omega^{-1}.
$$

The direction names are a chart assignment; the sign law itself is intrinsic
to the oriented local cube.  A different orientation choice reverses both
sides consistently.

## Executable certificate

The file tests/python/test_causal_cut_chirality_cube.py verifies:

1. the shared source becomes three distinct checked occurrences at the base
   frontier;
2. the eight event subsets are completed causal pasts;
3. every one of the twelve forward cube edges consumes and produces one
   checked frontier port while preserving source support;
4. all six schedules and all six interchange faces close on identical
   decorated frontiers;
5. the cut-coordinate differential is exactly the identity pairing;
6. wedge and cut contraction satisfy the Clifford anticommutator on all eight
   exterior basis states;
7. pure exterior volume is nilpotent, while the combined volume squares to
   $-I$;
8. the resulting six-dimensional action has three aspect--opposite-face
   planes and characteristic polynomial $(\lambda^2+1)^3$;
9. all six direction permutations obey the orientation-character chirality
   law.

Rust remains authoritative for the program, nodes, linear use, sources,
occurrences, and frontiers.  Python constructs a bounded cubical research
witness; it does not create a stable semantic CoherenceCell.

## Result and boundary

The experiment supports the proposed endogenous mechanism in a precise
bounded form:

> Causality orients generation; a cut records its dual membership
> coordinates; the frontier certifies independent spatial replacements;
> interchange supplies antisymmetry.  Wedge insertion and cut contraction
> then combine into an order-four orientation action.

The derivation still has boundaries.

- It is proved only for one local $B_3$ interval generated by three disjoint
  enabled events.
- The sign attached to an interchange square is an oriented chain convention
  over a checked witness, not yet a Rust semantic two-cell.
- The contraction is derived from event-membership cochains, not yet from the
  full expression-valued occurrence-affine frontier.
- Overlapping rewrites, non-Boolean local intervals, feedback, and forgetting
  may obstruct or twist the construction.
- No stable exterior, Clifford, complex, spectrum, or cubical API is added.

## General candidate mechanism

The calibration suggests a reusable theorem schema.

> Whenever $n$ independent checked frontier transports generate a local
> Boolean cut interval, its oriented generation edges and cut-membership
> cochains canonically produce wedge and contraction actions with
> $c_i c_j+c_j c_i=2\delta_{ij}$.

For $n=3$, edges and complementary square faces both number three:

$$
\binom31=\binom32=3.
$$

This is why the six-dimensional pairing

$$
3+3=2+2+2
$$

is especially natural.  The next obligation is to replace the Boolean event
coordinates by the richer occurrence-affine cut lift and determine whether
sharing, overlap, or objectification turns the common chirality into a
twisted local system rather than destroying it.
