# Cube-root conjugation and polar covariance

Date: 2026-09-10. Direction: Mingli Yuan; formalization and finite external
calibration: ChatGPT. Status: bounded external exact evidence, not native
Adva semantics. Main read: `60b37d8a4c155994acc7207f2feecc1da7cc6441`.
Library read: `bc92ddce3053d6afc7df39dabeecf00a5ae0db07`.

## The incoming question

The library's new `logic-reflexive-duality-conservation` entry proposes six
readings of `{1,w,w^2}` and its real-part signs `(+, -, -)`. Its section 2.5
connects conjugation, lattice reflexivity and PR #175. This is a productive
question input, not a proved identification. The present note supplies an
exact relation and a counterexample to equality, without editing that pinned
document or attributing its interpretations to established physics.

Since the preceding merge, main has also advanced the library pointer and
catalog expectations to 21 entries, and added a historical toolchain merge
receipt. Open PR #176 consolidates the numerical audit; #177 proposes the
k28 closure record; #172 remains a separate native symbol-surface proposal.
These are unmerged proposals, not new verified dependencies of this experiment.
No native pairing replay for #175 was found in those updates. This environment
still lacks Rust/Cargo and the installed Adva extension; that obligation is
retained, and the old pairing experiment was not rerun.

## Freeze the types before calculation

Write `w^2+w+1=0`, choosing the upper-half-plane primitive cube root when
embedding into C. Exact arithmetic stores `a+b*w` as `(a,b)` over Q, with

\[
(a,b)(c,d)=(ac-bd,ad+bc-bd),\qquad
\overline{(a,b)}=(a-b,-b).
\]

The triangle is a real convex hull in the coordinate plane:

\[
P=\operatorname{conv}\{(1,0),(0,1),(-1,-1)\}.
\]

Its vertices sum to zero and are non-collinear, so their positive barycentric
average puts the origin strictly inside. The primal lattice is `M=Z^2` in
the basis `(1,w)`. A dual coefficient pair is a covector in `N=Hom(M,Z)`,
with pairing `x^T y`. The Euclidean metric in the primal basis is instead

\[
G=\begin{pmatrix}1&-1/2\\-1/2&1\end{pmatrix}.
\]

These two coordinate roles are not interchangeable. If `z` denotes a physical
Euclidean vector in primal coordinates and `y` its pairing covector, then
`y=Gz`, so converting a dual-coordinate polar to Euclidean primal coordinates
requires `z=G^{-1}y`.

The frozen contract is `experiments/cube_root_polar/contract.json`. This is a
new **two-dimensional triangle profile**, not a silent extension of #175's
centrally symmetric three-dimensional profile. The triangle is not centrally
symmetric. We use `x^T y <= 1`; the alternative `x^T y >= -1` convention
negates the polar. That sign matters here, although both sets are lattice
polytopes in their declared dual coordinates.

## Three exact conclusions

### 1. A positive paired-lattice example

The inequalities `y1<=1`, `y2<=1`, `-y1-y2<=1` give

\[
Q=P^\circ=\operatorname{conv}\{(1,1),(1,-2),(-2,1)\}.
\]

All primal vertices are integral in M, all polar vertices are integral in N,
and the origin is interior. Thus this is a reflexive lattice triangle in
the declared sense. Exact active-pair enumeration recovers these three
vertices and its bipolar. Completeness follows because each vertex of the
bounded full-dimensional two-dimensional polar has two independent active
constraints; all pairs are checked.

This positive example does not repair the previous fixed TO24 obstruction:
the object, dimension and lattice contract have changed explicitly.

### 2. Conjugation is not the polar construction

The conjugation matrix and its action are

\[
C=\begin{pmatrix}1&-1\\0&-1\end{pmatrix},\quad C^2=I,\quad CP=P.
\]

But in the **same primal coordinate type** the Euclidean polar is

\[
G^{-1}Q=\operatorname{conv}\{(2,2),(0,-2),(-2,0)\}=-2P\ne CP.
\]

Thus complex conjugation preserves this triangle, while its Euclidean polar
is the triangle multiplied by minus two. We do not compare P directly to a
covector-coordinate list as if they had the same geometric interpretation.
Both operations have involutive aspects, but that does not identify them.
The lattice property is called **reflexivity / 自反性**, not geometric
reflection / 反射. Neither operation by itself constitutes mirror symmetry.

### 3. A compatible relation does hold

For invertible A and the declared pairing,

\[
(AP)^\circ=A^{-T}P^\circ.
\]

Indeed `y in (AP)^circ` iff `(Ax)^T y<=1` for every x in P, iff
`A^T y in P^circ`. This proves the relation with its full quantifier; a
finite numerical test is not its proof.

Here the correct dual action of conjugation is

\[
C^{-T}=C^T=\begin{pmatrix}1&0\\-1&-1\end{pmatrix},
\qquad \langle Cx,C^{-T}y\rangle=\langle x,y\rangle.
\]

All nine primal/polar vertex pairings pass. Applying C directly to both
coordinate types fails in **8/9** pairs. For example `x=(1,0)`, `y=(1,1)`
pair to one, while `Cx=(1,0)`, `Cy=(0,-1)` pair to zero. The correct
dual transform gives `(1,-2)` and restores one.

A new fixture uses the unimodular shear
`A=((1,1),(0,1))`, giving vertices `(-2,-1),(1,0),(1,1)` and polar vertices
`(-2,3),(1,-3),(1,0)`. The same checker again proves the finite bipolar
and paired-lattice conditions and checks conjugation/polar covariance.
Correct transport passes all nine pairs; the same wrong-direction control
again fails in eight. In this fixture conjugation does change the primal
vertex set, so the check is not relying only on the original triangle's
conjugation symmetry.

## What the zero, one and signs do and do not express

The exact identities `1+w+w^2=0` and `1*w*w^2=1` both hold. The checker also
checks conjugation multiplicativity on all 81 pairs from `{-1,0,1}^2`.
These are algebraic checks, not trajectories, attraction or repulsion laws.
Dynamics would additionally need a state space, evolution rule and a defined
quantity with a proved conservation law.

Real-part observation gives `(1,-1/2,-1/2)`. It identifies w and w^2 and
does not preserve multiplication:

\[
\Re(w^2)=-1/2\ne\Re(w)^2=1/4.
\]

The three signs therefore lose a distinction and cannot carry this complex
multiplication as a faithful ring representation. They are also not a metric
signature: the actual Gram matrix has positive leading entry and determinant
3/4 and is positive definite. `det(C)=-1` records orientation reversal;
`det(C)*det(C^{-1})=1` follows from invertibility and is not an energy law.

## Adva terminology and invocation

No new word or native keyword is introduced. Existing `lattice-polar` gains
the explicitly named `cube-root-polar-covariance.v0` external profile, linked
from `docs/terminology/geometry-boundaries-v0.json`. Existing `mirror` retains
its stronger construction obligations. No reserved `D*` is implemented by C
or its transpose, and no native triadic observer is inferred from three roots.

The proposed use order is:

1. `problem-formation`: ask equality versus compatibility of the operations.
2. `representation`: fix basis, primal/dual roles, origin, pairing and metric.
3. `lattice-polar`: perform the separately bounded triangle profile.
4. `judge`: retain the exact covariance and reject conjugation=polarity.
5. `revise`: replace the proposed equality with the typed compatibility law.

The new profile's full input, output, refusal, replay and residual boundaries
are in the terminology record. Profile status remains Proposed and evidence
status ExternalExactPass. This is a bounded oracle, not an untrusted import
checker or a native learning result. The library entry and gitlink, Pascal
growth obligation and previous claims/evidence are preserved.

## Execution and next step

Replay from repository root with a fresh path:

```bash
python3 -S experiments/cube_root_polar/replay.py --output /tmp/cube-root-polar-fresh.json
```

One successful run; no correction replay. There are 18 active-constraint pairs
and 142 assertions including the codec status check. Exact construction and
checking took 1.720 ms, including 0.174 ms for formation/ring checks, 0.582 ms
for the first fixture and 0.851 ms for reuse. Codec work took 0.435 ms, writing
0.092 ms; sampled process high-water RSS was **11,008 KiB (10.75 MiB)**.
The 7,631-byte report size is not a memory estimate. Research, code formation
and network time were not measured; no speedup claim is made.

The run enforces one route, 30 wall seconds, 25 CPU seconds, 256 MiB address
space, 24 active pairs, 1,000 assertions and a 1 MiB output limit. Exhaustion
or check failure exits nonzero and does not admit partial results. Exact
coordinates, pairings, counts and code/contract pins are in `evidence.json`;
timing and final RSS are in `execution-cost.json` in the same experiment.
JSON replay is codec checking, not an independent mathematical verifier.

This supports Mingli's intuition that the two sides can communicate through
an explicit boundary relation. It refutes direct identification of the two
operations in this smallest example. It helps subsequent implementers select
the correct dual coordinates and prevents a positive example in a new object
from overwriting TO24's negative witness. Jiamin's real-task benefit remains
unmeasured.

The next engineering step remains one native-required replay of
`experiments/pairing_transport/replay.py` from the merged #175 work. A later
native version of this triangle profile must separately bind its two
coordinate types, Gram interpretation and retained program history. No
Calabi-Yau, mirror, physical-force or universality claim follows yet.
