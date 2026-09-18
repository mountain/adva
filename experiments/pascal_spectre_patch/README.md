# Curved contacts, an unfillable corner, and a rational sphere lift

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy.
Original contribution under Unknown v0.3. Account use is not Mingli's technical
review or a correctness guarantee. This is an external bounded experiment;
no native Adva operation, catalog admission or dependency change is made.

**The previous rational Pascal-circle witness cannot tile the plane.**
It has a rigorously unfillable reflex corner. Adding the centrally symmetric
S-curves used in this experiment preserves its corner angles and therefore
preserves that obstruction. Exact local curved contacts and a sphere lift
remain possible; neither removes the obstruction.

The finite run obtained **four congruent curved tiles with three exact shared
seams and no overlapping interiors**, at `epsilon=1/100000`. It checked all
1,378 pairs of the 53 distinct edge control hulls. There were three transform
proposals and 2,602 budgeted checks, taking approximately 0.12 seconds; no
budget continuation occurred. The first two amplitude certificates failed and
remain in the report. These failures concern a sufficient hull condition,
not necessarily actual curve intersections.

The fixed input is the first-party witness in
`../pascal_circle_learning/evidence/candidate.json`, SHA-256
`5d805463d69e0d5e2b248f09077e8a8bbaa09021938961c819383dae0960190c`.
All of its rational, two-circle, Pascal, circle-center and simplicity conditions
remain valid. Those conditions never implied tilability. This continuation
adds a new negative result without changing the old candidate or its evidence.

## Spectre-inspired curve choice

[Smith, Myers, Kaplan and Goodman-Strauss, Lemma 2.1](https://arxiv.org/html/2305.17743v2)
replace the original Tile(1,1) edges with centrally symmetric nonstraight
S-curves, or use a more general alternating construction. Their preservation
of tilings depends on the original tile geometry. It is not a theorem about
an arbitrary fourteen-sided polygon.

For each directed edge `A -> B`, set `d=B-A` and let `J` rotate by 90 degrees.
Our explicit original curve is

\[
\gamma(t)=A+td+\epsilon t^2(1-t)^2(2t-1)Jd,\qquad 0\le t\le1.
\]

It has rational coefficients, the original endpoints and endpoint tangent
directions. Its midpoint half-turn satisfies
`gamma(1-t)=A+B-gamma(t)` identically. Consequently the half-turn copy along
the same edge has exactly the same boundary arc in reverse order, not just
nearby sampled pixels. This applies a Spectre construction technique; we do
not call the resulting non-tiling shape a Spectre.

The curve's six degree-five Bernstein controls are
`A, A+d/5, A+2d/5-epsilon*Jd/10, A+3d/5+epsilon*Jd/10, A+4d/5, B`.
A control-hull certificate checks entire curves. Once shared arcs are identified,
other edge hulls must be disjoint except at their common endpoints. Every
intermediate amplitude from zero to the accepted amplitude stays inside the
same hulls. Thus the starting straight patch deforms without edge crossings,
with consistent shared seams and unchanged local tangent sectors. The resulting
Jordan regions keep disjoint interiors. Floating samples are used for drawing,
not for this certificate.

## A strict local obstruction to any full-plane tiling

The input has

\[
\alpha_4\approx359.996908454^\circ,\quad
\delta=360^\circ-\alpha_4\approx0.003091546^\circ,
\quad\min_i\alpha_i=\alpha_8\approx0.256420136^\circ.
\]

Every available corner is larger than the remaining wedge at `p4`. A smooth
edge interior contributes 180 degrees, also too large. No neighboring congruent
copy can fill the wedge without overlapping the original copy. This argument
allows reflections and non-edge-to-edge contacts. Local finiteness follows
from the positive fixed tile area and bounded diameter; infinitely many
congruent tiles cannot evade the local contradiction by accumulating there.

The decimal angles only illustrate the result. `obstruction.py` compares
rational cross products and dot products, proving the strict inequalities
exactly. `TILING_OBSTRUCTION.md` gives the full proof. The conclusion applies to this particular candidate
and to regular simple curved boundaries preserving these tangent angles;
it does not exclude all configurations satisfying the earlier circle/Pascal
constraints, or curves that deliberately change the endpoint tangents.

## Stereographic lifting: exact but not a change of intrinsic dimension

We use inverse stereographic projection

\[
\Phi(x,y)=\frac{(2x,2y,x^2+y^2-1)}{1+x^2+y^2}.
\]

It maps every rational planar point to a rational point on the unit sphere,
with inverse `(x,y)=(X/(1-Z),Y/(1-Z))`. The sphere equation follows from
`4r^2+(r^2-1)^2=(r^2+1)^2`. The experiment checks rational patch vertices and
rational curve parameters exactly.

The map is a bijection from the plane onto the sphere minus one point, so it
preserves incidences, overlaps and gaps. It cannot convert a non-tiling into
a tiling. The target is still an intrinsically two-dimensional surface. Its
pulled-back metric is `4(dx^2+dy^2)/(1+x^2+y^2)^2`; plane congruence does not
usually become sphere congruence. The retained sorted multisets of all fourteen
adjacent-vertex chord lengths differ across tiles. Therefore the spherical
copies are not all congruent, even allowing a relabelling of vertices. The
336 rational point checks supplement the general algebraic identity; they
are not a sampling-based proof of the whole projected boundary.
Circle incidence survives, but a Euclidean circle center does not generally
become the center of the image circle.

## The relevant higher-dimensional route already exists

[Baake, Gähler, Mazáč and Sadun](https://arxiv.org/html/2411.15503v2)
give a four-real-dimensional cut-and-project description related to Spectre
tilings: two physical dimensions and two internal dimensions, with fractal
windows. Precisely, their Theorem 9 identifies CASPr control points as a
full-density subset of a five-color regular model set; Corollary 11 relates
Spectre tilings by mutual local derivability to a reprojected five-color Meyer
set. Their argument uses the established Spectre tiling space and substitution
structure. It does not admit arbitrary changes to fourteen boundary vertices.

For a new candidate, the next useful learning constraints are compatible edge
pairings and completable vertex neighborhoods. A necessary early filter is to
exclude a largest reflex angle whose complement is smaller than every corner.
After finding extendable neighborhoods, one needs global extension or a
substitution structure, then a return module, star map and acceptance windows.
Local seam coincidence and a sphere drawing do not supply these certificates.

## Replay and evidence

From the repository root (Python standard library for checks):

```sh
python experiments/pascal_spectre_patch/patch.py --output /tmp/pascal-patch.json
python experiments/pascal_spectre_patch/obstruction.py
python -m unittest discover -s tests/python -p 'test_pascal_spectre_*.py' -v
```

To draw the retained result, with NumPy and Matplotlib installed:

```sh
python experiments/pascal_spectre_patch/plot.py --report experiments/pascal_spectre_patch/evidence/patch.json --output /tmp/pascal-patch.png
```

The main diagram uses the actual accepted curve amplitude. Its maximum normal
displacement is only `epsilon/(25*sqrt(5))`, about `1.78885e-7` times its edge
length. The normalized curve inset exaggerates normal displacement 100,000
times and is explicitly labelled; that exaggeration was not certified.

The input is already public first-party material; no source paper, external
figure, original Spectre implementation or external vertex table is imported.
`contract.json` was frozen before the patch run. `evidence/patch.json` retains
all three successful attachments, the two failed amplitude certificates, exact
transforms, sphere coordinates and resource counts. `evidence/obstruction.json`
retains an independent rational angle certificate and confirms that all
fourteen squared edge lengths are distinct. `evidence/validation.json` records
the eight executed controls and the separate proof review.

No unrestricted search was performed. A failed control-hull sufficient test
only withholds that certificate; the angle obstruction independently proves
non-tilability for this candidate. A successful small patch proves exactly
its recorded seams and disjointness, without claiming a complete vertex corona.
