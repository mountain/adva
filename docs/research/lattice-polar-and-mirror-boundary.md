# Lattice-polar admission: Goldberg refinement, quotients, and mirror boundaries

Date: 2026-09-10. Direction and motivating questions: Mingli Yuan / 苑明理.
Formalization, literature checking and implementation: ChatGPT.
Status: Adva research terminology with an executed external exact-arithmetic
calibration. No stable keyword, Rust semantic type, native filler, or mirror
construction is introduced.

Base: `0e4be5f81f59cd208b14bd21ea8a3250e8f7f289`.
Pinned library: `b99d9c7295e9d3a4a0d77f8a7e7e6db7deee4364`.
The open PR #172 concerns native symbol-surface loading; this experiment
does not depend on it. Existing main results are not replayed as new evidence.

## 1. Why this belongs to Adva terminology

Mingli's question relates the repeated refinement of the Q4/M6 geometric
carrier to finite observers, Universal, Yau's Euler-number-six construction,
and mirror symmetry. Unlike the preceding golden-ratio atlas, this record
places the distinctions inside Adva's research vocabulary and its claim
registry. The entry point is
[the versioned terminology contract](../terminology/geometry-boundaries-v0.json).
It separates a named direction, its typed interpretation, an external check,
and native admission. JSON labels do not install language operations.

The existing dependencies are [0103](0103-cell-carrier-view-relation-machines.md),
[0111](0111-group-neutral-operations-and-q4-m6-relation-profiles.md),
[0129](0129-bounded-breakthrough-trusted-boundaries.md), and
[the simplex/Calabi boundary note](simplex-contraction-pascal-calabi-reduction.md).
The geometry track of the research agenda permits theorem/counterexample
work without adding a stable geometry API.

The main new result is a negative admission theorem: the centered standard
TO24 cannot be a reflexive lattice polytope for *any* compatible full-rank
lattice. A nonintegral primal-polar pairing is a short certificate. A change
of linear coordinates or uniform scale, with the dual frame transported
correctly, cannot remove it. This does not exclude different realizations of
the same combinatorial polyhedron or other Calabi-Yau constructions.

## 2. Prior facts and their separate types

The finite S4 calibration in 0103 realizes TO24 as a truncated octahedron
with 24 vertices, 36 edges, six Q4 squares and eight M6 hexagons. Q4 denotes
an interchange boundary ab => ba; M6 denotes aba => bab. The raw histories
remain different, and the higher filler is not manufactured by the polygon.
The finite Coxeter shadows are C2 x C2 and S3, respectively. Neither is the
whole symmetry group of an unlabelled presentation. A signed braid lift
retains information forgotten by the finite permutation shadow.

In Goldberg notation this geometry is the octahedral variant GP_IV(1,1),
not the pentagon/hexagon icosahedral family. For GP_IV(m,n), put
T=m*m+m*n+n*n. Then V=8T, E=12T, F=4T+2; there are six quadrilaterals
and 4(T-1) hexagons. The numerical sequence m=n=2^k increases the face
count, but does not itself supply a nested cell map, a metric normalization,
or a typed Adva refinement. These are separate construction targets.

For any cubic cell decomposition of the sphere, 3V=2E, sum(j*f_j)=2E,
and V-E+F=2 imply sum((6-j)*f_j)=12. With only quadrilateral/hexagonal
faces, f_4=6. This is a combinatorial curvature budget; it is not a
Calabi-Yau Euler number. The polyhedral boundary has Euler number 2; the
filled convex body has Euler number 1. Subdivision preserves these numbers.

In the classical compact Calabi-Yau threefold setting with h^(1,0)=h^(2,0)=0,
chi=2(h^(1,1)-h^(2,1)). A Tian-Yau construction described in [3] starts
with a complete intersection in P3 x P3 of bidegrees (1,1),(3,0),(0,3),
Euler number -18, and a free Z3 action. Its quotient has Euler number -6
and Hodge numbers (6,9). The quotient formula chi(X/G)=chi(X)/|G| here
uses a free finite action; fixed points require separate analysis. The
three-generation interpretation requires the specified heterotic model and
bundle assumptions. It is not a theorem about every CY or about M6.

Mirror symmetry exchanges complex-structure and complexified Kähler data
in appropriate mirror pairs. The exchanged Hodge numbers imply opposite
Euler numbers in this threefold setting, but those numbers alone do not
prove mirror symmetry [4]. Spatial reflection, complex conjugation, group
quotient, polar duality, and mirror symmetry remain separate operations.
Ricci-flatness does not mean vanishing full curvature; c1=0 does not imply
c3=0. Geometric symmetry groups and metric holonomy have different roles.

## 3. A genuine combinatorial bridge and its gate

Batyrev's construction [5] starts with a lattice M, its dual N, and a
full-dimensional lattice polytope containing zero in its interior. Its polar
must also have lattice vertices in N. Under the stated regularity and
crepant-resolution conditions, a d-dimensional reflexive polytope supplies
families of complex (d-1)-dimensional Calabi-Yau hypersurfaces in toric
varieties, and dual polytopes give mirror candidates with proved Hodge
relations. A three-dimensional polytope supplies K3 surfaces in this
construction; a Calabi-Yau threefold requires dimension four.

The polytope encodes construction data: its boundary is not the CY itself.
High symmetry, rational vertices, or the equation (P^o)^o=P do not establish
the lattice condition. Ordinary Goldberg refinement is not automatically
a crepant subdivision of a toric fan.

We use the convention P^o={y:<x,y><=1 for every x in P}. Batyrev uses
the equivalent negative-polar convention <x,y>>=-1. Negation converts the
conventions; all tested polytopes are centrally symmetric, so their polar
vertex sets agree under this conversion. No sign conversion is implicit
for future nonsymmetric inputs.

## 4. Frozen arithmetic problem and result

The [run contract](../../experiments/lattice_polar/contract.json) was written
before execution. Coordinates are exact rationals, origin fixed at zero,
pairing the declared primal-dual dot product. One route enumerates every
triple of primal constraints, solves its active equalities exactly, and
retains feasible polar vertices. Full dimension and central symmetry imply
an interior origin; hence the polar is bounded. Every vertex has three
independent active normals, so complete triple enumeration covers every
polar vertex. The same procedure checks the bipolar.

The primary input is P=conv(signed permutations of (0,1,2)). Its exact
halfspace representation is

    |x_i| <= 2,          |x_1|+|x_2|+|x_3| <= 3.

The computed polar vertices are the six signed e_i/2 and the eight
(+/-1,+/-1,+/-1)/3. All 14 occur, and the bipolar recovers precisely the
24 supplied vertices. Supporting-face incidence independently recovers
the 6 squares, 8 hexagons, 36 edges, and vertex pattern (4,6,6).

### Lattice-pairing obstruction theorem

If P is a lattice polytope in M and P^o is a lattice polytope in
N=Hom(M,Z), every primal-polar vertex pairing is an integer. But

    v=(1,2,0) in Vert(P), y=(1/2,0,0) in Vert(P^o), <v,y>=1/2.

This contradicts integrality. Thus *no such M exists for this fixed P and
origin*. The certificate does not enumerate possible lattices. It is a
necessary-condition argument over all of them. For invertible A,
<Av,A^(-T)y>=<v,y>; for positive scale s, <sv,y/s>=<v,y>. The same
obstruction persists under these changes. This analytic proof, not a finite
lattice search, supplies the universal quantifier. Neither translations of
the origin nor shape changes were tested or included in the theorem.

### Positive controls and new-instance reuse

The unit cube has polar conv(+/-e_i), and both vertex sets are integral
in the declared standard lattices. The unchanged checker is reused on the
sheared cube A(x,y,z)=(x+y,y,z), a unimodular change of basis. Its polar
agrees with A^(-T) applied to the old polar. Applying A on both sides is
explicitly rejected as the wrong dual-coordinate transport.

A new scale, 2P, has polar P^o/2 and retains the same nonintegral pairing.
Geometric shrinking of polar coordinates does not repair the lattice gate.
This is a concrete rejection of the proposed shortcut through small scale,
not a refutation of observer-relative approximation in its own task domain.

The remaining controls reject a forged polar point (1,0,0), return
UnknownCoverage for an incomplete coverage flag, and show that residual
1/2 < epsilon=3/4 still does not establish integrality. The control with a
missing flag tests result policy only; it does not make this tool an
untrusted-certificate validator. Enumeration evidence is generated internally.

## 5. Adva vocabulary placement and proposed invocation order

These are research interpretations, not changes to existing native names:

| Term/profile | Input and output | What it can establish now |
| --- | --- | --- |
| refine | covered carrier, normalization, observation policy -> finer carrier plus coarse-read map | Proposed; no new refinement executed |
| quotient | carrier and checked group action -> orbit carrier plus stabilizer/fibre record | Proposed; no new quotient executed |
| lattice-polar | rational vertex data, origin, primal-dual lattice frame -> polar, bidual, lattice judgment, residual | Executed external finite profile in this record |
| mirror | two CY constructions and a declared mirror comparison -> checked invariant correspondences plus remaining obligations | Proposed; no mirror constructed |

`lattice-polar` does not overwrite the project's polarity operation or the
reserved D* observer pullback. Its narrow implementation composes candidate
polar construction and `judge`; it deliberately exposes two independent
judgments: rational biduality and lattice admissibility. `ReflexiveInDeclaredLattice`
does not authorize `mirror`. `NoCompatibleReflexiveLattice` is a mathematical
obstruction for one fixed centered object, not a general impossibility verdict.

The proposed calling discipline is:

1. `problem-formation`: specify the object and target guarantee.
2. `representation`: freeze origin, lattice pair, coordinates and pairing.
3. `lattice-polar`: construct and check the finite data.
4. `judge`: return the exact lattice result or a scoped Unknown.
5. `revise`: change the question explicitly if an obstruction requires a
   different shape/dimension; retain the old certificate and charge new fuel.

No `mirror` or `free` step follows automatically. `coverage-gated-close`
can close only the declared finite arithmetic question once its evidence is
complete. A document with the word `Seal` cannot replace the Rust checker.

For future observer refinement, choose p_k:X_(k+1)->X_k and operation T_k.
The proposed transport condition is p_k T_(k+1)=T_k p_k, or a certified
error bound under a fixed observation metric. Geometric mesh diameter h
controls observable error only with a supplied continuity modulus, e.g.
Lh<epsilon. Coverage and task decision margins still matter. The target
`for every epsilon there exists an effective finite adequate level` remains
an approximation conjecture, not universal computation or complete grammar.

## 6. Execution, cost and limits

Reproduce from repository root with Python standard library on Linux:

```sh
python3 -S experiments/lattice_polar/calibration.py --output /tmp/lattice-polar-fresh.json
```

The output must not already exist. No network, input secrets, Rust build,
third-party numerical package or repository mutation occurs during replay.
Compare mathematical projections, not timing fields or byte hashes of the
whole fresh report. All exact input and output vertices appear in
[evidence.json](../../experiments/lattice_polar/evidence.json).

One successful run, zero correction replays: 4,928 constraint triples and
540 assertions; construction and checking 288.007 ms, including 0.327 ms
fixture formation. JSON serialization/parse replay took 0.540 ms; report
write took 0.101 ms as retained in execution-cost.json. Peak process RSS
was 11,264 KiB (11 MiB), sampled before final serialization. It is not
aggregate memory or file size. Research, authoring, network, final metadata
checks and interpretation acceptance were not timed as part of this run.

The budget was one route, at most 10,000 triples / 300,000 assertions,
30 seconds alarm, 25 CPU seconds, 256 MiB address space, 1 MiB per output,
2 MiB retained artifacts. The computation/serialization/write completed
under the same alarm. The exact script and contract hashes are in evidence.
The code plus constructive proof are inspectable, but Python replay uses
the same implementation, not an independent proof-assistant kernel.
No speedup or learned theorem discovery is claimed. The new-instance costs
are separately retained per fixture; there is no with/without-word benchmark.

## 7. Integration boundaries and next smallest step

Metadata review parsed the full claims TOML and found unique identifiers.
A whole-registry dependency assertion also exposed a pre-existing dangling
reference: adva.bounded-verified.symbolic-probe-matrix-shadow.v0 names
adva.exact.structural-forward-differential.v1, absent from the pinned
registry. This unrelated issue is retained and not repaired in this study;
no claim of whole-registry dependency closure is made. The new entry has no
dangling dependency. Its evidence/source hashes, terminology fields and
local artifact references pass the scoped metadata check. This review did
not rerun or correct the successful arithmetic experiment.

This registration is in Adva's own research terminology and claims, not a
new entry in the separately constrained mathematical library. The library
growth obligation, Pascal pins, current gitlink and catalog remain unchanged.
Q4/M6 remain documentary external geometry references there; this result
does not create a Pascal derivation parent or a native geometry successor.

The result supports Mingli's call to distinguish representations and their
boundaries. It rejects the shortcut from TO24 symmetry or rational duality
to Batyrev reflexivity. It does not refute a different combinatorial or
geometric realization, a higher-dimensional construction, or Universal.

The next minimal task is to bind one geometric frame to a checked Adva
diagram and specify what the external lattice judgment means for that frame,
retaining source/occurrence/history data. Its question is correspondence,
not an immediate CY search. Native vocabulary admission then needs a Rust
type/certificate design under the existing agenda. If instead the chosen
goal is a toric construction, explicitly open a separate shape/dimension
contract beginning with an already checked reflexive control; no silent
change of TO24 is permitted.

## References

1. Michael Goldberg, A Class of Multi-Symmetric Polyhedra, Tohoku Math. J.
   43 (1937), 104-108. https://www.jstage.jst.go.jp/article/tmj1911/43/0/43_0_104/_article
2. Brinkmann, Goetschalckx and Schein, Goldberg, Fuller, Caspar, Klug and
   Coxeter and a general approach to local symmetry-preserving operations
   (2017). https://arxiv.org/abs/1705.02848
3. Candelas, de la Ossa, He and Szendroi, Triadophilia: A Special Corner in
   the Landscape, section 1.1 and section 2 (2007/2008).
   https://arxiv.org/abs/0706.3134
4. Greene and Plesser, Mirror Manifolds: A Brief Review and Progress Report,
   sections 1-2 (1991). https://arxiv.org/abs/hep-th/9110014
5. Batyrev, Dual Polyhedra and Mirror Symmetry for Calabi-Yau Hypersurfaces
   in Toric Varieties (1993/1994), definitions and main construction.
   https://arxiv.org/abs/alg-geom/9310003

Classical results retain their attribution; the contextual vocabulary,
negative admission question, and finite implementation are this Adva study.
