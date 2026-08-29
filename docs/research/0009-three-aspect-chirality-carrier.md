# Three-Aspect Chirality Carrier

Status: bounded algebraic and checked-program calibration, not a foundational
Clifford or complex type.

## The six-dimensional clue

The proposal

$$
6=2+2+2
$$

becomes substantially sharper if each aspect is paired with the oriented
relation of the other two.  Let

$$
V=\langle T,S,R\rangle_{\mathbb R}
$$

record temporal, spatial, and relational generators.  The candidate
six-dimensional carrier is not six unrelated coordinates.  It is

$$
W=V\oplus\Lambda^2V
$$

with the cyclically oriented basis

$$
W
=
\langle T,SR\rangle
\oplus
\langle S,RT\rangle
\oplus
\langle R,TS\rangle.
$$

This realizes the proposed pattern literally:

| aspect | opposite oriented relation |
|---|---|
| temporal $T$ | spatial--relational $SR$ |
| spatial $S$ | relational--temporal $RT$ |
| relational $R$ | temporal--spatial $TS$ |

An aspect and the relation between the other two are not declared equal.
They are the two sides of one oriented pair.

## One orientation operator, not three unrelated complex units

Use a geometric product satisfying

$$
TS=-ST,\qquad SR=-RS,\qquad RT=-TR
$$

and first take

$$
T^2=S^2=R^2=1.
$$

The total orientation expression

$$
\Omega=TSR
$$

is central in the resulting three-generator algebra and obeys

$$
\Omega^2=-1.
$$

Left multiplication by $\Omega$ preserves $W$.  Writing

$$
J(x)=\Omega x,
$$

one obtains

$$
\begin{aligned}
J(T)&=SR, & J(SR)&=-T,\\
J(S)&=RT, & J(RT)&=-S,\\
J(R)&=TS, & J(TS)&=-R.
\end{aligned}
$$

Consequently,

$$
J^2=-I_W
$$

and each summand

$$
\langle T,SR\rangle,\qquad
\langle S,RT\rangle,\qquad
\langle R,TS\rangle
$$

is a real two-plane carrying the same complex structure.  Thus the complex
unit is not introduced three times as a scalar choice.  It is the single
global orientation expression $\Omega$ acting on three aspect--relation
pairs.

This is a more constrained interpretation of a locally complex rank-three
carrier than an arbitrary declaration $W\cong\mathbb C^3$.  The three complex
lines share one chirality.

## The projective chart on every pair

On any one pair, use coordinates $(a,b)$ for an aspect and its opposite
relation.  The restriction of $J$ is

$$
\begin{pmatrix}
0&-1\\
1&0
\end{pmatrix},
\qquad
(a,b)\longmapsto(-b,a).
$$

The projective ratio $z=a/b$ is therefore sent to

$$
z\longmapsto-\frac1z.
$$

The earlier AEG inversion is recovered on all three pair charts from one
six-dimensional operator.  Its characteristic polynomial is

$$
\chi_J(\lambda)=(\lambda^2+1)^3.
$$

The matrix is only a coordinate shadow.  The proposed spectral carrier is
$W$ together with its three aspect--opposite-relation planes and the global
orientation action; the six-by-six matrix alone forgets why those planes are
paired.

## Time-space exchange and chirality

Let $P_{TS}$ exchange $T$ and $S$.  Its action must also be transported to
oriented relations:

$$
SR\mapsto-RT,\qquad
RT\mapsto-SR,\qquad
TS\mapsto-TS.
$$

Since a transposition reverses total orientation,

$$
P_{TS}\Omega P_{TS}^{-1}=-\Omega.
$$

It follows that

$$
P_{TS}JP_{TS}^{-1}
=
-J
=
J^{-1}.
$$

This gives the desired precise statement:

> Exchanging time and space changes the common aspect chirality from the
> forward orientation action to its reverse.  Projectivization sees the same
> negative-inverse chart, while the oriented six-dimensional carrier retains
> the sign.

More generally, for every permutation $\pi$ of the three aspects,

$$
P_\pi J P_\pi^{-1}
=
\operatorname{sgn}(\pi)J.
$$

Cyclic permutations preserve chirality; transpositions reverse it.

## The previous scalar trichotomy reappears as signature

Allow diagonal aspect squares

$$
T^2=\varepsilon_T,\qquad
S^2=\varepsilon_S,\qquad
R^2=\varepsilon_R.
$$

Then

$$
\Omega^2
=
-\varepsilon_T\varepsilon_S\varepsilon_R.
$$

The complex, split, and dual alternatives are therefore not lost.  They
reappear as three possible states of the aspect pairing:

| product $\varepsilon_T\varepsilon_S\varepsilon_R$ | $\Omega^2$ | type |
|---:|---:|---|
| positive | $-1$ | complex / elliptic |
| negative | $+1$ | split / hyperbolic |
| zero | $0$ | dual / parabolic degeneration |

The AEG order-four lift supports the first row under the same-carrier bridge
hypothesis from the preceding calibration.  It does not by itself derive the
positive aspect pairing.

This distinction is important.  If temporal, spatial, and relational aspects
were assigned a physical Lorentzian signature with exactly one negative
square, the same construction would be split rather than complex.  Semantic
temporality in program geometry must not be silently identified with a
negative metric direction in physical spacetime.

## Checked program calibration

The file tests/python/test_three_aspect_chirality_carrier.py contains three
finite Adva functions on the ordered Real chart

$$
(T,S,R,SR,RT,TS).
$$

They realize:

1. the orientation action
   $$
   J(t,s,r,sr,rt,ts)=(-sr,-rt,-ts,t,s,r);
   $$
2. its inverse $J^{-1}=-J$;
3. the time-space exchange
   $$
   P_{TS}(t,s,r,sr,rt,ts)
   =
   (s,t,r,-rt,-sr,-ts).
   $$

Each port is consumed exactly once, and Rust checks the graph, types, ordered
frontier, and linear use.  A test-local exact geometric-product oracle
derives rather than assumes the sign table.  The tests verify:

- $J^2=-I$ and $J^{-1}=-J$;
- $P_{TS}JP_{TS}^{-1}=-J$;
- the orientation-character law for all six aspect permutations;
- the three invariant aspect--opposite-relation planes;
- the exact characteristic polynomial $(\lambda^2+1)^3$;
- complex, split, and dual behavior for positive, negative, and degenerate
  aspect-pairing products.

Python and SymPy remain research adapters over the Rust-checked Real programs.
They do not create stable program identities or semantic cells.

## What this does and does not explain

The calibration supports a stronger version of the original intuition:

> The six components need not be six scalar coordinates.  They can be three
> pairs in which a primitive aspect is completed by the oriented relation of
> the other two.  A single total-orientation expression exchanges the two
> members of every pair.

It also gives one concrete sense in which polynomial-like and matrix-like can
be the same object.  The expression $\Omega=TSR$ is compositional and
factorized; its left action is the matrix-like shadow $J$.  The action is not
the ontology from which the expression is reconstructed.  Both are
presentations of one grade-aware expression operation.

Several boundaries remain.

1. The bivector $SR$ is an oriented composite relation, not yet a proved
   internal-Hom object $[S,R]$.
2. Anticommutation and the quadratic pairing are assumptions of this
   calibration.  They have not been derived from causal cuts, occurrence
   sharing, or coherence cells.
3. The identification of this six-dimensional lift with the AEG homogeneous
   carrier remains conditional.
4. No stable Clifford type, exterior grade, complex scalar, spectrum, bundle,
   manifold, or physical spacetime signature is added to Adva.

## Next theoretical obligation

The next step should not be a larger coordinate experiment.  It should ask
whether the program calculus itself produces the grade structure:

- primitive aspects from one-dimensional directed generation;
- oriented pair relations from interchange of two independent constructions;
- the total orientation expression from coherent three-way composition;
- the sign change from exchanging two construction orders.

If those four ingredients can be derived from checked cuts and their
interchange cells, then $\Omega^2=-1$ and the complex three-pair carrier would
be consequences of program geometry.  If they cannot, the present structure
remains an illuminating external model rather than the intrinsic mechanism.
