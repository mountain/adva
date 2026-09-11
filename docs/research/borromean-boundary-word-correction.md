# Boundary words repair the triple-intersection inference

Date: 2026-09-11. Direction and question: Mingli Yuan / 苑明理.
Analysis, implementation, visual observation and writing: ChatGPT (OpenAI),
submitted through Mingli Yuan's GitHub account as an authorized proxy.
Account use is not endorsement, review or a correctness guarantee.

Status: executed external exact finite calibration, using an imported theorem.
Base main: `cb5f62d6a0c468c47b0c8dd46ce0424d52256890`.

## Result

The golden-rectangle configuration has a unit Milnor triple linking number
under the declared surface orientation. The missing term in the earlier
argument is now computed. A second configuration has the same triple-point
count and zero pairwise linking numbers, but zero triple linking number:

| configuration | pairwise linking | boundary term m | triple points t | mu = m - t |
| --- | --- | ---: | ---: | ---: |
| Original three golden rectangles | all zero | 0 | 1 | -1 |
| Uniform scale by two | all zero | 0 | 1 | -1 |
| Common translation by (1,2,3) | all zero | 0 | 1 | -1 |
| Same cyclic arrangement, aspect ratio two | all zero | 0 | 1 | -1 |
| Concentric orthogonal squares, half-widths 3,2,1 | all zero | 1 | 1 | 0 |
| Third golden component separated at y=10 | all zero | 0 | 0 | 0 |

Thus the original geometric intuition survives with a corrected justification.
The raw triple-point count is insufficient even in this small family. The
rational aspect-ratio example also shows that a unit invariant here is not
evidence of uniqueness of the golden ratio. No isotopy between the examples
is computed and no uniqueness theorem about the arrangement is claimed.

## The imported theorem and the missing hypothesis

Mellor and Melvin, *A geometric interpretation of Milnor's triple linking
numbers*, Algebraic & Geometric Topology 3 (2003), 557-568, define the boundary
term in section 2 and prove on page 561 that

\[
\bar\mu_{ijk}=m_{ijk}(F)-t_{ijk}(F)\pmod\delta,
\qquad \delta=\gcd(\operatorname{lk}_{ij},\operatorname{lk}_{jk},\operatorname{lk}_{ki}).
\]

Source: <https://arxiv.org/pdf/math/0110001>.

Here t counts oriented triple intersections. For each component L_k, walk
its oriented boundary and record a signed letter i for each crossing of F_i.
If w_k is this word, then m is the cyclic sum of the degree-two coefficients:

\[
m_{ijk}=\epsilon_{ij}(w_k)+\epsilon_{jk}(w_i)+\epsilon_{ki}(w_j).
\]

When all pairwise linking numbers vanish, the formula gives an integer.
Pairwise vanishing alone does not remove m for an arbitrary surface system.
The simplification to -t requires the corresponding boundary term to vanish.
The theorem is imported as mathematics; this work neither reproves it nor
formalizes it in a proof assistant.

The predecessor's
[golden-ratio record](golden-ratio-receipts-and-source-boundaries.md), section 9,
and `borromean_checks` did not compute this term. Their geometric data and
historical evidence are preserved. This note supersedes that inference, not
the source bytes or the recorded run. Similarly, the earlier claim that the
abelianized presentation's H1 = Z^3 recovers pairwise linking numbers is not
valid: link-component meridians give this abelian group for every three-component
link. Pairwise linking requires the peripheral/longitude information or the
separate signed intersection calculation; the latter is retained here.

## Exact source-to-surface boundary

The new checker reads the literal `rectangles` assignment in
`golden_rectangle_checks` from the byte-pinned predecessor source using a
restricted AST decoder. It never executes that module. Only the constants
ZERO, ONE and PHI and literal tuple/dictionary data are admitted. Its own
quadratic-field arithmetic uses exact rational pairs a+b sqrt(5), independent
of the predecessor's class. The full constructed inputs are retained.

Writing phi=(1+sqrt(5))/2, the original surfaces are

- F_z: z=0, |x|<=1, |y|<=phi;
- F_x: x=0, |y|<=1, |z|<=phi;
- F_y: y=0, |z|<=1, |x|<=phi.

This run explicitly chooses normals (+e_z,+e_x,+e_y) and component order
(z0,x0,y0), and constructs each boundary by the right-hand convention. The
resulting words, with i=z0, j=x0 and k=y0, are

\[
w_i=kk^{-1},\qquad w_j=ii^{-1},\qquad w_k=jj^{-1}.
\]

All three relevant degree-two coefficients vanish. The normals have positive
determinant and the origin is the unique interior triple point. Consequently
m=0, t=1 and mu=-1. The sign is tied to this declared ordering/orientation;
it is not a retroactive sign convention for the predecessor's report.

For the concentric squares, the half-widths are 3 in z=0, 2 in x=0 and 1
in y=0. They instead give

\[
w_i=1,\qquad w_j=ii^{-1},\qquad w_k=iji^{-1}j^{-1}.
\]

The coefficient of X_i X_j is one. Thus m=1 cancels the same t=1. This is an
explicit counterexample to using pairwise-zero plus unit raw triple count as
a sufficient admission rule. Zero mu is not asserted to classify an arbitrary
link as the unlink.

The checker enumerates all four boundary edges against both other surfaces.
Signed events retain edge ordinal, exact edge parameter, crossed surface and
coordinates, in traversal order. It rejects boundary contacts, event ties,
relevant coplanar edges and crossings at polygon vertices. Convex rectangles
are embedded disks; their remaining finite intersections are transverse and
away from corners, so the PL corners can be rounded locally without changing
the recorded intersection system. No tolerance decides incidence.

An additional source-level weakness was visible in the old endpoint check:
`on_boundary` could succeed merely because an endpoint satisfies a rectangle's
plane equation. Plane membership is not polygon-boundary membership. This
checker requires the free-coordinate bounds explicitly, including strict
interiority for a boundary-surface crossing. It leaves the old pinned routine
unchanged rather than silently replacing its historical meaning.

## Validation and costs

The [contract](../../experiments/borromean_surface_audit/contract.json) was
written before execution. The two attempts both passed, with no correction
attempt and no increase in its budget:

- 22 fixed cases: six configurations, seven other normal-sign assignments,
  five other component orders and four refusals;
- every fixture serialized and decoded, then judged again: 44 judgments per
  process;
- signed ordered-pair coefficients checked against a separately implemented
  degree-two noncommutative Magnus product, plus cyclic basepoint controls;
- pairwise linking sums checked in both directions, and normals checked
  against the oriented polygon boundaries;
- the missing component returns UnknownCoverage; boundary contact, nonzero
  pairwise linking and an invalid normal are refused;
- first process: 597 assertions, 27,725 counted work units, 0.103420 seconds
  including report publication, 25,368 KiB peak RSS;
- fresh-process comparison: 598 assertions, 27,726 work units, 0.110753
  seconds including report publication, 25,388 KiB peak RSS.

Linux address-space and CPU limits were installed; each process had an outer
eight-second timeout and its own seven-second alarm. The shared session used
two of three allowed attempts. Source/contract SHA256 values and full fixture
inputs/results are retained. These are external Python checks sharing one
theorem and field model, not independent proof kernels. No speedup is claimed.
Research, authoring, network, visual reading and integration costs are excluded.

From a checkout containing the predecessor at the pinned bytes, choose fresh
paths:

```sh
timeout 8s python -B -S experiments/borromean_surface_audit/check.py \
  --output /tmp/borromean-surfaces-first.json
timeout 8s python -B -S experiments/borromean_surface_audit/check.py \
  --compare /tmp/borromean-surfaces-first.json \
  --output /tmp/borromean-surfaces-replay.json
```

See [attempt-01.json](../../experiments/borromean_surface_audit/attempt-01.json),
[replay-01.json](../../experiments/borromean_surface_audit/replay-01.json), and
[execution.json](../../experiments/borromean_surface_audit/execution.json).

## What visual inspection contributed

The current ChatGPT assistant inspected two exact source images, after their
Git blob hashes were checked. This is a new observation, separate from the
predecessor agent's historical statement that it had not read the images.

The 500x463 rectangle plate mixes three colored filled regions, white vertex
markers and a red polyhedral edge network. Occlusion and the absence of
orientation arrows expose an ambiguity that matters for the proof: surfaces,
link boundaries and auxiliary polyhedron edges cannot be treated as one
object. The 500x338 spiral plate shows why close visual resemblance also
requires a declared comparison; no error magnitude was read from its pixels.

The [visual observation](../../experiments/borromean_surface_audit/visual-observation.json)
records exact image identities, resolution, observations, proposed meanings and
unresolved details. It supplies no mathematical certificate, pixel-derived
coordinates, source authentication or new image licence. The original images
remain in the pinned public library and are not duplicated here.

## Remaining boundary and next step

The complement/longitude extraction in `experiments/golden_ratio/queue.json`
remains Open. This surface route supplies the missing term in its own right;
it is not that route's independent cross-check and does not close its queue
item. No native import, geometry-library admission, Seal, free or new word is
introduced. A unit triple invariant does not prove ambient isotopy to a
particular drawing, general representation completeness or a physical claim.

The next useful step is to compare a correctly constructed preferred longitude
against this full surface answer on both the golden and concentric-square
fixtures. The second fixture is now essential: matching only the familiar
unit example would not detect the omitted boundary term.
