# Learning a rational fourteen-point Pascal configuration

A bounded external experiment, authored by ChatGPT (OpenAI) and submitted
through Mingli Yuan's GitHub account as an authorized proxy. The account owner
supplies the research direction; account use is not technical review.
Original code and prose are contributed under Unknown v0.3.

**Result:** a simple polygon with fourteen distinct rational vertices satisfies
the declared five-point and four-point circle/Pascal bindings exactly.
The four-point circle center also lies **exactly on the five-point circle**.
The current fit moves a labelled point by RMS **1.429139 original edge lengths**.
This is an existence witness with substantial deformation, not a closest fit or
a new aperiodic monotile. The full exact coordinates are in
[`evidence/candidate.json`](evidence/candidate.json).

## What is constrained

The seed comes from Smith, Myers, Kaplan and Goodman-Strauss,
[*A chiral aperiodic monotile*](https://arxiv.org/abs/2305.17743), Figure 1.1,
and the [authors' coordinate implementation](https://cs.uwaterloo.ca/~csk/spectre/spectre.js).
The supplied figure was converted into an explicitly supplied coordinate seed,
not a pixel loss. Number its boundary points from 0 through 13. The two groups
consume all fourteen finite labels:

| Circle | Circle vertices | Degenerate six-slot sequence | Required opposite-side intersections |
| --- | --- | --- | --- |
| Red | 1, 3, 5, 7, 9 | 1, 1, 3, 5, 7, 9 | 11, one infinity point, 13 |
| Blue | 2, 4, 8, 12 | 2, 2, 4, 8, 8, 12 | 0, 6, 10 |

Repeated adjacent vertices mean the actual tangent of that circle. For slots
`a,b,c,d,e,f`, the intersections are `ab ∩ de`, `bc ∩ ef`, `cd ∩ fa`.
The checker computes them, checks their distinctness and collinearity, and
checks that they equal the assigned existing vertices. The circle membership
counts must be exactly five and four among all fourteen vertices. The user's
additional relation couples the two circles:

`|O_blue - O_red|^2 = r_red^2`.

This is an exact acceptance requirement, not a soft fitting penalty. Write
complex coordinates `red = C + q*r` and `blue = C + q*k + s*b`, where `r,b`
are local Pascal points and `k` is a rational unit-circle point. Then the blue
center `C+q*k` lies on the red circle of center `C` and squared radius `|q|^2`.
Only `C,q,s` and the circle-chart parameters are rationalized; the blue center
is always reconstructed from them.

This distinction is necessary: Pascal collinearity is already automatic for
properly constructed intersections of six points on a conic. What fails at the
source is **binding those intersections to specified other Tile vertices**.
The original point 10 is on the blue circle, in addition to its four true
corners; it must leave that circle to serve as an external Pascal intersection.
A five-point degeneration usually has eight projective points. Here one
intersection is explicitly at infinity, leaving seven finite red points.
The blue construction has seven finite points. Infinity is not counted as
one of the fourteen rational affine vertices.

We preserve labels and boundary adjacency, exact circle/Pascal and center-incidence constraints,
distinctness and a simple final polygon. We release the original edge lengths,
angles, circle centers/radii and the straight angle at point 10. There is no
claim that the original tiling or aperiodicity survives. No continuous feasible
path from the original Tile to this result was computed or proved.

## How the experiment uses Adva

This is the repository's **external finite-learning route**. Native `learn`
does not currently expose a generic Euclidean constrained optimizer.
The producer reuses `cross` and `det3` from
`experiments/knowledge_geometry/acceleration_direction.py`; it pins the existing
Pascal task/witness bytes and the library revision. It follows Research 0131's
proposal, independent check, judgment, update and retention discipline, under
the frozen `contract_v1.json` Research 0129 resource contract.

A rational circle chart makes incidence exact by construction. A seven-angle
C++ proposer uses annealing, a coupled complex least-squares fit and a crossing
penalty to reduce displacement from the supplied seed. Its first start uses
the original circle angles; its second uses an explicitly retained, earlier
learned rational witness. The initial source angles are projected into the
constrained parameter family, so the optimizer's first feasible proposal is
not asserted to be the unmodified source polygon. Twelve starts and all their
iterations belong to one fixed budget, not automatic restarts after exhaustion.

Floating parameters are rationalized, then **all points are reconstructed**
with `Fraction`. Rounding the resulting coordinates would destroy exactness.
A separate checker process, with separately written line/intersection/determinant
formulas, accepts or rejects the reconstruction. It imports no producer or
optimizer. It also rejects zero projective vectors, coincident lines, collapsed
points, crossings, unintended circle members and false bindings. Passing the
checker is an external arithmetic result, not a Rust semantic certificate,
Q4/M6 admission, a native communication operation or a Seal. No core, lock,
submodule or geometry-catalog obligation is changed.

## Reproduce the exact result

Python 3.11+ standard library is sufficient for verification:

```sh
python experiments/pascal_circle_learning/check.py experiments/pascal_circle_learning/evidence/candidate.json
python experiments/pascal_circle_learning/duality.py experiments/pascal_circle_learning/evidence/candidate.json
python -m unittest discover -s tests/python -p 'test_pascal_circle*.py' -v
```

The frozen bounded search additionally requires a C++17 compiler (`g++`).
Explicit external inputs and run outputs must stay outside the repository:

```sh
python experiments/pascal_circle_learning/run.py --seed /absolute/external/seed.json --output /absolute/external/new-run
python experiments/pascal_circle_learning/run.py --seed /absolute/external/seed.json --output /absolute/external/zero-run --fuel 0
```

The seed is a JSON object with schema
`adva.external.pascal-circle-seed.v0` and `points`: fourteen finite two-coordinate
arrays in label order. Bibliographic and exact-algebraic metadata may accompany
it. The full source seed, source image, paper and author implementation are
not embedded or downloaded by this experiment. An absent input produces an
explicit unavailable/Unknown result. Public witness verification needs no
external seed. Numerical search replay requires the independently obtained
seed matching the retained digest; its full derivation is described in
[`MATHEMATICS.md`](MATHEMATICS.md).

The stored exact witness proves existence regardless of platform-dependent
floating search behavior. The search has no cross-platform bitwise promise.
Budget exhaustion or unsuccessful rationalization means `Unknown`, never a
proof of nonexistence. Numeric proposer, rejected exact attempts and independent
acceptance outcomes are retained in the run output.

## Evidence and limits

The fixed proposal run spent **48,012 numeric evaluations and one exact
candidate check**, within a budget of 50,000. The first simple proposal had
RMS 1.56726; the retained exact result has RMS 1.4291391728 and minimum pair
distance 0.0420363403. All **26 named exact checks** pass. The separately enforced minimum-distance guard uses exact squared distance.
The recorded v1 run took 1.079 seconds before final serialization, including
compilation and checking. These figures are
measurements of this instance, not formal bounds on an entire search family.
The supplied original seed has RMS zero relative to itself but fails the
requested bindings; fitting improvement is measured among feasible proposals.

The independently derived displacement lower bound is approximately 0.422342485
for this fixed labelling, even before imposing all circle constraints. The
current result is far above that lower bound. Binding choices and the strong
circle shrinkage in this candidate warrant further study; they were not
silently varied during this run. The theorem that every rational-coordinate
configuration can be scaled to integer coordinates does not make the original
Tile shape rational while preserving its angles.

See [`MATHEMATICS.md`](MATHEMATICS.md) for the rational construction, the
unchanged-Tile obstruction and exact lower-bound derivation; `contract_v1.json`
for the frozen scope and resource limits; `evidence/` for the reviewed witness,
check result and measured execution record. Publication provenance is recorded
separately under `governance/publication/records/`.

## Correction retained from the first experiment

The initial v0 model allowed the two circle similarities to vary independently.
Its witness passed 25 checks, but it did not constrain the four-point center
to the five-point circle. After the user explicitly required that relation,
the same witness was checked under v1: precisely the added center-incidence
check fails. Its previous Verified judgment was scoped to the incomplete v0
profile and cannot answer the completed request. The old witness and its new
Refuted judgment are retained as a regression control. Earlier references to
26 checks for v0 were a counting error; v0 had 25, and v1 adds the 26th.

The discovery pilot, initial source-fitting pilot and the center-constrained
successor each have a distinct declared finite contract. Their costs are
listed together in `evidence/development-history.json`; the final run's 50,000
limit is not claimed to cover all earlier development. There is no automatic
continuation after a spent run budget. The unexecuted v0 packaged replay was
cancelled when the new condition arrived.

## Self-duality diagnosis

For each accepted seven-finite-point group, take the six bound hexagon-side
lines and the Pascal line. Neither resulting seven-point/seven-line incidence
structure is combinatorially self-dual. A local neighboring-degree obstruction
already proves this; a separate finite diagnosis checks all 10,080 candidate
point-to-line bijections and agrees. Circle polarity also leaves these line
sets, because some circle-point tangents are absent. This is not a rejection
of another proposed completion or pairing of points and lines. Such a proposal
needs explicit sets and a correspondence. `duality.py` replays the exact
incidence diagnosis without moving any accepted point or running an optimizer.
See the final section of `MATHEMATICS.md` and `evidence/duality-diagnosis.json`.
