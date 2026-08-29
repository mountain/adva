# Causal-Line Filtrations of the Six-State Carrier

Status: bounded derived regrouping on the checked local three-cube, not a
physical spacetime decomposition or a stable filtered-carrier API.

## Question

The causal-cut calibration derives the six-state carrier

$$
W
=
\Lambda^1E\oplus\Lambda^2E
=
\langle T,S,R,SR,RT,TS\rangle
$$

from one checked three-direction program neighbourhood.  Its orientation
action pairs each direction with its opposite face:

$$
\Omega:
T\leftrightarrow SR,
\qquad
S\leftrightarrow RT,
\qquad
R\leftrightarrow TS,
\qquad
\Omega^2=-I.
$$

The equalities

$$
6=2+2+2=3+3
$$

are already certified presentations of this local carrier.  The next question
is what happens after one checked generation direction is designated as a
one-dimensional causal line.  In particular, are the readings

$$
6=1+2+3=1+3+2
$$

two coordinate descriptions of the same split, a chirality reversal, or only
dimension numerology?

## What is chosen and what is derived

The checked cube supplies three source-bearing independent directions, their
cut cochains, and the derived action $\Omega$.  It does not label any direction
as physical time.  A causal-line chart chooses one direction

$$
L=\langle T\rangle
$$

and calls the other two direct directions

$$
H=\langle S,R\rangle .
$$

The letters are chart labels.  The executable test repeats the construction
with each of the three directions chosen as $L$, so the result is not tied to
the first checked node or to the names $T,S,R$.

Once $L$ is chosen, the remaining pieces are not chosen independently.
The derived opposite-face action selects

$$
\Omega(L)=\Lambda^2H=\langle SR\rangle
$$

and

$$
\Omega(H)=L\wedge H=\langle RT,TS\rangle .
$$

Consequently the carrier has the four-part split

$$
W
=
L
\oplus H
\oplus(L\wedge H)
\oplus\Lambda^2H,
$$

with dimensions

$$
1+2+2+1.
$$

This is the precise common refinement behind both three-block readings.
No Cartesian coordinate space is used to define it: $L$ is a checked
generation direction, $H$ contains the other checked directions, and the
other two pieces are selected by the causal-cut action.

## The two readings

The first reading keeps all oriented pair relations together:

$$
\mathcal F_{123}
=
L
\mid
H
\mid
\bigl((L\wedge H)\oplus\Lambda^2H\bigr),
$$

so its block dimensions are

$$
(1,2,3).
$$

The second lets the transverse chart retain its own orientation unit:

$$
\mathcal F_{132}
=
L
\mid
\bigl(H\oplus\Lambda^2H\bigr)
\mid
(L\wedge H),
$$

with dimensions

$$
(1,3,2).
$$

Thus the passage

$$
\mathcal F_{123}\longleftrightarrow\mathcal F_{132}
$$

is not a swap of a two-dimensional block with a three-dimensional block.
The underlying carrier and every carrier element stay fixed.  Exactly one
state,

$$
\Lambda^2H=\Omega(L),
$$

moves from the relation block to the transverse block.  We call this an
**orientation-unit transfer**.  The term records a change of filtered
interpretation, not an implemented program operation.

For the chart $L=T$, the exact membership table is:

| common part | basis states | dimension |
|---|---:|---:|
| causal line | $T$ | 1 |
| transverse pair | $S,R$ | 2 |
| causal relations | $RT,TS$ | 2 |
| transverse orientation | $SR$ | 1 |

The $(1,2,3)$ reading groups the last two rows.  The $(1,3,2)$ reading groups
the second and fourth rows.

## Why regrouping is not chirality reversal

The same $\Omega$ acts before and after regrouping.  What changes is the
pattern with which its arrows cross the three declared blocks.  Counting
arrows from source blocks to target blocks gives, for $L=T$,

$$
B_{123}
=
\begin{pmatrix}
0&0&1\\
0&0&2\\
1&2&0
\end{pmatrix},
\qquad
B_{132}
=
\begin{pmatrix}
0&1&0\\
1&0&2\\
0&2&0
\end{pmatrix}.
$$

These tables are filtered incidence summaries, not new semantic matrices.
They show that the two readings retain different information even though
the unfiltered carrier action and its characteristic polynomial

$$
(\lambda^2+1)^3
$$

are unchanged.  An ordinary scalar spectrum therefore cannot distinguish
the two readings; the filtration can.

An actual exchange of two checked directions is different.  If $P$ swaps the
two transverse directions, then it is an odd orientation change and

$$
P\Omega P^{-1}=-\Omega.
$$

The executable test verifies both facts separately:

1. orientation-unit transfer changes block membership but not $\Omega$;
2. an odd direction exchange reverses $\Omega$.

This prevents dimension regrouping from being mistaken for the forward versus
reverse chirality of a genuine time-space or aspect exchange.

## What the two-dimensional block does not yet prove

The transverse pair $H$ is a natural place to test the proposed
expression-to-expression form $X^Y$: one direction may be read as an open
input and the other as the expression that acts on it.  The present
calibration does not establish that interpretation.

A two-state block alone does not supply:

- an evaluation operation $X^Y\times Y\to X$;
- substitution of one checked hole into another;
- currying or an internal-Hom universal property;
- a stable exponential object;
- binders or function values in the Adva core.

Those operations are explicitly outside the current binder-free stable
language.  Calling $H$ an $X^Y$ carrier before evaluation and substitution
are derived would replace a theorem obligation with a name.

## The source-free control is a negative witness

The checked scale event also exposes a source-free constant control port.
It crosses the cut but has no checked source support.  The test rejects an
attempt to promote it to a fourth causal direction.  This matters because
the construction is selected by occurrence lineage, not by the number of
ordinary real-valued wires visible in a coordinate dump.

The negative witness does not claim that parameters have no geometry.
It shows only that their geometry cannot be silently identified with the
three source-bearing aspect directions.

## Executable certificate

The added tests in
`tests/python/test_causal_cut_chirality_cube.py` verify:

1. the derived sparse action
   $T\mapsto SR$, $S\mapsto RT$, $R\mapsto TS$ and the signed reverse
   action without treating a coordinate matrix as semantic authority;
2. the $1+2+2+1$ split for each of the three possible causal-line choices;
3. the two regroupings $1+2+3$ and $1+3+2$;
4. the unique transfer of the orientation state $\Omega(L)$;
5. the distinct filtered incidence profiles;
6. preservation of $\Omega$ under regrouping;
7. reversal of $\Omega$ under an actual odd transverse exchange;
8. rejection of the source-free control as a fourth causal line.

Rust remains authoritative for the program, source support, occurrences,
events, and cuts.  Python reads the already checked local carrier and audits
two research filtrations.  No stable time, exterior, filtration, complex, or
physical API is introduced.

## Result and boundary

The bounded result supports a precise part of the six-state intuition:

> Choosing one causal line refines the local six-state carrier as
> $1+2+2+1$.  The $(1,2,3)$ and $(1,3,2)$ readings differ by transferring
> the unique transverse orientation state paired with that line.  They are
> different filtered readings of one carrier, not by themselves a chiral
> pair.

The result does not identify the three-state block with three-dimensional
physical space, derive a Lorentz signature, construct $X^Y$, or explain why
one program direction is physical time.  It remains local to the same
independent Boolean cut interval.

The next calibrated obligation is physical closure.  A suitable first case is
real Gaussian ray propagation: construct propagation and focusing as checked
expressions, derive the oriented projective lift before introducing the
complex beam parameter, and only then ask whether the traditional complex
fixed point and stability spectrum are the closed numerical shadow of this
carrier.
