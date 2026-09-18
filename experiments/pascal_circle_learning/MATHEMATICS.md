# A rational Pascal-circle learning chart with coupled centers

This note records original calculations for a bounded **external geometry
calibration**. It does not establish a native Adva learning operation, a native
Pascal import, a geometry-library successor, or a `Seal`.

Authored and independently recalculated by ChatGPT (OpenAI), through Mingli
Yuan's authorized GitHub account proxy. Account use is not Mingli's technical
review or a correctness guarantee. The original exposition and calculations
are contributed under Unknown v0.3. No source figure, source code, paper text,
or complete external vertex table is incorporated here.

## 1. Reference and exact question

The external reference is Smith, Myers, Kaplan and Goodman-Strauss,
[*A chiral aperiodic monotile*](https://arxiv.org/abs/2305.17743), with the
[authors' resource page](https://cs.uwaterloo.ca/~csk/spectre/). An explicitly
supplied external seed uses the fourteen boundary labels `p0` through `p13`
in the authors' application order. The straight-edge midpoint is `p10`.
Source coordinates and images remain outside this repository.

The experiment asks for fourteen **new**, distinct rational affine points,
with the same labelled polygon-edge order, satisfying these roles:

| Group | Circle points | Additional finite points | Additional projective point |
| --- | --- | --- | --- |
| Red | `p1,p3,p5,p7,p9` | `p11,p13` | One point at infinity |
| Blue | `p2,p4,p8,p12` | `p0,p6,p10` | None |

Each group has seven finite points. Together they cover fourteen labels;
the red point at infinity is additional and is not a polygon vertex.
The circles must contain exactly their declared five and four points among
the fourteen labels. The polygon must be simple and have nonzero area.
The revised profile additionally requires the blue circle center to lie
exactly on the red circle:

\[
\|O_B-O_R\|^2=r_R^2.
\]

This is a hard algebraic condition, not a soft objective penalty. A witness
for the earlier profile without it does not satisfy the complete request.

The source tiling theorem is not an assumption about these new polygons.
Original edge lengths, angles, circle sizes and tiling properties are released.

## 2. Specified incidence, not an identically satisfied residual

For a cyclic six-slot list `(a,b,c,d,e,f)`, form

\[
X=ab\cap de,\qquad Y=bc\cap ef,\qquad Z=cd\cap fa.
\]

Adjacent repeated entries mean the tangent at that point. Merely minimizing
the collinearity determinant of `X,Y,Z` cannot learn the desired association:
Pascal already makes that determinant zero for a nonsingular conic. The
nontrivial requirement is equality with **specified polygon labels**.

The producer uses the following fixed constructive chart:

| Group | Six slots | X | Y | Z |
| --- | --- | --- | --- | --- |
| Red | `(p1,p1,p3,p5,p7,p9)` | `p11` | infinity | `p13` |
| Blue | `(p2,p2,p4,p8,p8,p12)` | `p0` | `p6` | `p10` |

Writing the five red circle points as `(a,b,c,d,e)` gives

\[
p_{11}=t_a\cap cd,\qquad ab\parallel de,
\qquad p_{13}=bc\cap ea.
\]

Writing the four blue circle points as `(a,b,c,d)` gives

\[
p_0=t_a\cap t_c,\qquad p_6=ab\cap cd,
\qquad p_{10}=bc\cap da.
\]

Here `t_a` means a tangent, not the rational parameter introduced below.
Parallel lines must be distinct. Coincident lines do not define a projective
intersection and are rejected.

The independent checker validates the supplied six-slot lists, repetition
patterns, declared circle memberships and intersection identities. Its
admissible presentation is broader than the producer's one fixed ordering;
this does not authorize changing a frozen producer chart during a run.

## 3. Why the external seed fails these identities

Let `s = sqrt(3)` and use the external seed's unit-edge coordinate frame.
Independent exact arithmetic gives the two circle facts

\[
O_R=(2,1),\quad r_R^2=2;
\qquad O_B=((3-s)/2,(3-s)/2),\quad r_B^2=3.
\]

These source circles satisfy `||O_B-O_R||^2=2=r_R^2`. The center condition
is therefore an existing source relation to preserve, unlike the designated
Pascal intersection identities that the source fails.

The original blue circle also contains the straight-edge midpoint `p10`.
For the four-point construction above, each pair of opposite sides has no
common circle endpoint. Its finite intersection cannot lie on the circle:
a chord line meets a nonsingular circle at its two endpoints, and a tangent
meets it only at its tangency point. Thus making `p10` a nondegenerate Pascal
intersection **requires** it to leave the blue circle. Allowing the formerly
straight polygon edge to bend is a necessary relaxation.

For the frozen red six-slot ordering, direct calculation on the source gives

\[
X_R=(1+2s,-2s),\qquad
Y_R=[1:s-2:0],\qquad
Z_R=((s-1)/2,-(3+s)/2).
\]

These finite intersections are not the assigned source points `p11,p13`.
There is a particularly small certificate of the first failure: the tangent
at source `p1` is `x+y=1`, whereas source `p11` satisfies `x+y=2`.

For the frozen blue ordering the actual source intersections are

\[
X_B=(3,0),\quad Y_B=(2+s/2,3/2),
\quad Z_B=(3/2+s,-3s/2),
\]

and they are not source `p0,p6,p10`. Independently, the assigned source triple
itself has the exact homogeneous determinant

\[
\det\begin{pmatrix}
p_{0x}&p_{0y}&1\\
p_{6x}&p_{6y}&1\\
p_{10x}&p_{10y}&1
\end{pmatrix}=3+3\sqrt3\ne0.
\]

Consequently the original labelled shape cannot already satisfy this profile.
The fact that some other Pascal triple is collinear does not repair these
failed point identities.

## 4. Rational construction

Use the unit-circle parametrization

\[
P(t)=\left(\frac{1-t^2}{1+t^2},\frac{2t}{1+t^2}\right),
\qquad t\in\mathbb Q.
\]

Its chord between parameters `u,v` has equation

\[
(1-uv)x+(u+v)y=1+uv.
\]

Choose four red parameters `t_a,t_b,t_c,t_d`, and define

\[
A=1-t_at_b,\quad B=t_a+t_b,\quad
t_e=\frac{B-A t_d}{A+B t_d}.
\]

This makes the chord normals for `ab` and `de` proportional. The checker
additionally requires distinct chords, so their intersection is a genuine
point at infinity. The denominator-zero chart case is rejected; this
rejection is a limitation of the selected chart, not a nonexistence theorem.

All four blue parameters are free, subject to the exact nondegeneracy checks.
Tangents have rational coefficients, and nonparallel rational lines have
rational affine intersections. Thus all fourteen constructed finite points
are rational before any numerical optimization is used.

An uncoupled seven-point group can undergo a rational similarity

\[
(x,y)\longmapsto
(\alpha x-\beta y+c_x,\ \beta x+\alpha y+c_y).
\]

Its circle center is `(c_x,c_y)` and radius squared is
`alpha^2+beta^2 > 0`. The radius itself need not be rational. Similarities
preserve the circle, tangent and parallel-line relations.

For the **revised coupled profile**, identify the plane with complex numbers.
Let `r_i` and `b_i` denote the red and blue unit-chart points, including their
computed finite Pascal intersections. Choose rational complex numbers
`C,q,sigma`, with `q` and `sigma` nonzero, and a rational unit-circle point
`k=P(t_k)`. Set

\[
z_i=C+q r_i\quad(i\text{ red}),\qquad
z_i=C+q k+\sigma b_i\quad(i\text{ blue}).
\]

The resulting circles have

\[
O_R=C,\quad r_R^2=|q|^2,\qquad
O_B=C+qk,\quad r_B^2=|\sigma|^2.
\]

Consequently `|O_B-O_R|^2=|q|^2|k|^2=|q|^2` exactly. Both similarities preserve
all the previously specified Pascal bindings. Every finite point is rational
whenever the parameters are rational.

This coupling introduces no additional restriction on the rational fixed-role
problem beyond the stated condition and chart exclusions. Indeed, three
noncollinear rational points determine a rational circle center. For any
accepted rational configuration, choose `q=p1-O_R` and `sigma=p2-O_B` and set
`k=(O_B-O_R)/q`. These are rational complex numbers, and the center condition
gives `|k|=1`. Normalizing each circle by its chosen multiplier gives rational
unit-circle points. They have rational half-angle parameters unless they
equal the omitted point `(-1,0)` of this finite chart. Antipodal/chart-pole
cases require another chart or a projective parameter; rejection here must
not be presented as a theorem about their impossibility.

Final rationalization applies to these parameters, **then reconstructs all
points**. Rounding fourteen independently calculated point coordinates would
generally destroy the exact incidence equations and is not permitted.
In particular, rationalize `C,q,sigma,t_k` and derive `O_B=C+qk`; rounding the
blue center independently would destroy the new center condition.

## 5. Rational coordinates require geometric relaxation

If two nonzero rational direction vectors have a non-right angle `theta`,
then

\[
\tan\theta=\frac{\det(u,v)}{u\cdot v}\in\mathbb Q.
\]

The source polygon has `60`-degree turns, whose tangent is irrational.
Therefore no placement with all rational vertex coordinates can preserve
all those angles. This obstruction is independent of the choice of global
Euclidean frame; changing only translation, rotation or scale is insufficient.

In the specific source coordinate frame, the original blue circle has no
rational affine points at all. Its equation is

\[
x^2+y^2-(3-s)(x+y)+3-3s=0.
\]

For rational `x,y`, separating the rational and irrational parts forces
`x+y=3` and `x^2+y^2=6`; hence `x,y=(3 +/- sqrt(3))/2`, a contradiction.
This frame-specific observation is supplementary to the angle obstruction.
Allowing circle positions, radii and internal circle-point angles to change
removes these obstacles, as the rational chart and checked witness demonstrate.

## 6. A necessary displacement bound

Any accepted blue group must make `p0,p6,p10` collinear. Let `S` be the
uncorrected centered scatter matrix of these three **source** points. Exact
calculation gives

\[
S=\begin{pmatrix}
6+3s/2&3/2\\3/2&2+s/2
\end{pmatrix},\qquad
\operatorname{tr}S=8+2s,\quad\det S=12+6s.
\]

The minimum total squared distance from the three source points to any line
is the smaller eigenvalue

\[
\lambda_{\min}=4+\sqrt3-\sqrt{7+2\sqrt3}.
\]

For any three new collinear positions, their displacement from the source is
at least this best-line-fitting error: for their common line, perpendicular
projection is the closest possible choice of each point. Other vertices
contribute nonnegative squared displacement. Therefore, with original edge
length one,

\[
\mathrm{RMS}_{14}\ge
\sqrt{\frac{4+\sqrt3-\sqrt{7+2\sqrt3}}{14}}
\approx0.4223424848.
\]

This is a lower bound, not an attained optimum. It already rules out an
arbitrarily small correction of the source under these label bindings.
Adding the center condition cannot weaken this necessary lower bound.

## 7. What is learned and what is projected

The numerical objective is labelled squared distance to the supplied source,
with topology and collision handling during proposal generation. Hard
acceptance remains exact circle/incidence checking and polygon simplicity.

For unit-circle angles, the red parallel constraint reads
`theta_e = theta_a + theta_b - theta_d (mod 2*pi)`. Independent similarities
absorb one common rotation for each group, so fixing `theta_a=0` on each
circle leaves six angular proposal variables. The coupled model adds the
angle of `k`, for seven nonlinear angular variables in total.

For fixed chart points and `k`, solve jointly for the three complex unknowns
`(C,q,sigma)`. The design rows are `[1,r_i,0]` for a red point and `[1,k,b_i]`
for a blue point. Complex least squares thus reduces to a `3`-by-`3` Hermitian
normal system, or an equivalent real six-variable linear least-squares
problem. The columns have full rank whenever two red `r_i` differ and a blue
`b_i` is nonzero: a vanishing linear combination on the red rows first forces
the constant and red coefficients to vanish, and a blue row forces the last
coefficient to vanish. Numerical ill-conditioning and zero fitted multipliers
still require explicit rejection; algebraic rank is not a numerical guarantee.

In the source-normalized chart, the exact source values are

\[
C=2+i,\quad q=-1-i,\quad
\sigma=\sqrt3/2-3i/2,\quad
k=\sqrt3/2-i/2.
\]

Thus the source direction for `k` has angle `-pi/6`, with half-angle parameter
`sqrt(3)-2`. The six relative source angles are red
`(pi/3,2*pi/3,pi)` and blue `(pi/3,pi/2,7*pi/6)`. These are initialization
facts, not final rational parameters. The source red antipode also illustrates
why a finite half-angle chart must distinguish a pole from nonexistence.

Seven angular plus six real linear variables give thirteen real parameters,
one fewer than the previous two-independent-circle family, as expected for
the additional scalar center-incidence equation.

The source supplies the first angular initialization. It is then projected
into the constructive family: dependent circle parameters, designated
intersection labels and fitted similarities are reconstructed. **That first
model configuration is not the original fourteen-point seed.** Optimizing
distance to the original seed does not mean starting an exactly feasible
continuous deformation at the original seed, which fails the role identities.

Moreover, preserving the polygon's labelled boundary order and checking its
final simplicity do not prove preservation of circle-point cyclic order or
simplicity throughout an interpolating path. Distinct points cannot exchange
their circular order along a continuous path that keeps them on one circle.
This experiment does not certify such a path. The result is an accepted
endpoint proposed by a finite external learner.

## 8. Historical prototype and its new exact refutation

The separately frozen scratch refinement used 48,012 numerical evaluations
and one exact candidate check. Its rational candidate has SHA-256

`0946ee3bbc34954ce65b0c8e4c639c5bf3f5deee06995e2c0bddec3b96f63c20`.

This identifies a witness for the **earlier, incomplete profile only**.
It satisfies the old circle, Pascal and simple-polygon conditions, but its
center-incidence residual is

\[
|O_B-O_R|^2-r_R^2=
\frac{4953785174725775491947473498653600891906191}
{1971641960762104222935249718375464007993600}
\approx2.5125176240472054\ne0.
\]

Its verdict under the complete revised request is therefore **Refuted**.
The old profile's `Verified` status must remain labelled with its old scope;
it cannot be transferred to the new run. Retaining this failed candidate is
part of the audit trail, not evidence for accepting the full request.

The measured labelled RMS is `1.2705417653647195` source-edge units, and the
minimum point separation is `0.06371747919919145`. The red circle becomes
much smaller than its source counterpart; this is a substantial deformation,
not a recovered Tile or a proven minimum-displacement solution. The hoped-for
RMS range `0.5` to `1.0` was not reached by this finite refinement.

The earlier checker reported **25** named checks: three global checks and
eleven per circle. Earlier working updates said 26; counting the actual
result fields corrected that reporting error. The revised profile now really
has **26** named checks: the previous 25 plus center incidence. On this old
candidate, center incidence is the one newly failing condition.

A second audit used only independent `Fraction` arithmetic, importing neither
the repository producer nor its checker. It reconstructed each circle from
three submitted points, verified exact memberships and all six specified
intersection identities, checked all 77 pairs of nonadjacent closed polygon
edges, and found all fourteen consecutive triples noncollinear. Its signed
area is positive, approximately `2.186471924781006`.
The same independently implemented audit was extended to reconstruct the
center relation and confirmed the nonzero residual above. A newly generated
candidate requires a fresh exact audit against all conditions.

## 9. Accepted witness for the complete coupled profile

A separately frozen successor run produced a candidate with SHA-256

`5d805463d69e0d5e2b248f09077e8a8bbaa09021938961c819383dae0960190c`.

Its compact exact parameter certificate is:

| Parameter tuple | Exact values |
| --- | --- |
| Red `(t_a,t_b,t_c,t_d)` | `(0,-35/82,-9238/6819,18598/9327)` |
| Blue `(t_a,t_b,t_c,t_d)` | `(0,8830/1279,10990/9143,-14509/5374)` |
| Center direction `t_k` | `-648/3451` |
| Red multiplier `q` | `-1872/7795 - (1579/7887)i` |
| Common origin `C` | `16365/9121 + (7104/8045)i` |
| Blue multiplier `sigma` | `-1213/9723 - (5803/9670)i` |

The center direction is particularly explicit:

\[
k=\frac{11489497-4472496i}{12329305},\qquad |k|^2=1.
\]

Thus `O_B-O_R=qk`, and the independently reconstructed circles satisfy

\[
|O_B-O_R|^2=r_R^2=
\frac{369483769180321}{3779687729097225},\qquad
r_B^2=\frac{3321092389243861}{8840025538388100}.
\]

The center-incidence residual is **exactly zero**. The red infinite
intersection is

\[
Y_R=[1:-1641476723/492524770:0].
\]

All 26 named independent-checker conditions passed. A second implementation
using only `Fraction` arithmetic again reconstructed circle centers from
three candidate points, rather than trusting the submitted centers, and
verified the complete incidence, exact circle cardinality and center
relation. It checked all 77 nonadjacent closed-edge pairs, all fourteen
consecutive triples and positive signed area. It imported neither producer
nor repository checker.

| Measurement | Result |
| --- | ---: |
| Labelled RMS displacement from the supplied source | `1.4291391728319605` |
| Minimum pair distance | `0.04203634031829899` |
| Signed area | approximately `2.33464576113791` |
| Numerical proposals in this formal run | `48012` |
| Exact candidate checks in this formal run | `1` |
| Total proposal/check fuel spent | `48013` of `50000` |
| Formal invocation wall time before final serialization | approximately `1.0792` seconds |
| Numerical proposal phase wall time | approximately `0.1155` seconds |

The recorded wall time includes compilation and the first independent
candidate check. It excludes earlier separately bounded prototypes, later
auditing and report preparation. It is not a claim about total development
time. The logged source-angle projection initially had approximate RMS
`1.65199` and seven numerical crossing detections; that was an unaccepted
proposal, not the original seed itself. The accepted rational endpoint
removes the crossings and lowers the source-distance objective within the
declared finite search. No optimum is certified.

## 10. Remaining claims and limits

The historical witness establishes existence only for the older profile.
The new independently audited witness establishes a rational simple-polygon
endpoint for the complete coupled-circle profile. Parameterization alone
would not have established its polygon simplicity; that property was checked
on the explicit rational witness. No result here establishes global optimality,
an unrestricted learner, a continuous feasible path from the original seed,
or any periodic or aperiodic tiling property of the learned polygon.

Numerical search is only a proposer. The independent checker establishes the
declared finite endpoint conditions with exact arithmetic. Exhausting any
finite search budget remains `Unknown`, not proof that another chart, binding
or a smaller displacement is impossible. Changing an intersection-to-label
assignment changes this experiment and requires a separately declared finite
contract.

## 11. Bounded diagnosis of a proposed seven-point self-duality

The successful coupled-circle run did not require an additional optimization
condition. A later question about self-duality was examined as a separate,
read-only incidence diagnosis, without moving the accepted points or running
another geometry search.

For each side, choose its seven finite points and the six lines from the
bound six-slot sequence, plus its Pascal line. Denote those lines by
`l0,...,l5,l6`, in that order. The red seven-point set excludes its Pascal
point at infinity; including that point would give eight points against
seven lines, so these particular sets could not be interchanged bijectively.

For the seven-point sets, equal numbers of points and lines are not enough
for combinatorial self-duality. Incidence must be preserved under a point-line
interchange. The exact candidate gives short obstructions:

| Side | Existing local incidence type | Missing dual type |
| --- | --- | --- |
| Red | `l4=de` has degree two, and both its incident points have degree two. | No degree-two point is incident to two degree-two lines. |
| Blue | `X=p0` has degree three and lies on both degree-two tangent lines `l0,l3`. | No degree-three line contains two degree-two points. |

An incidence isomorphism preserves degree and neighboring degree types.
Therefore neither selected seven-point/seven-line structure is
combinatorially self-dual. In particular neither has an involutive
self-duality. These obstructions concern the specified line sets; a proposed
different choice or completion of points and lines is a different question.

For corroboration, a contract fixed before execution allowed at most `7!`
point-to-line bijections per side, `10080` total, and ten seconds, with zero
automatic continuation. Exact `Fraction` incidence was computed from the
accepted rational candidate. All `10080` bijections were checked in about
`0.017` seconds; general and involutive self-duality counts were both zero
on both sides. The retained diagnosis contains the exact incidence matrices,
line coefficients, candidate digest and permutation count.

Circle polarity is a separate geometric notion. It sends a point on the
circle to that point's own tangent. The present red line set lacks tangents
at `p3,p5,p7,p9`; the blue set lacks tangents at `p4,p12`. Thus neither finite
line set is closed under its circle's natural polarity either. The accepted
circle-center condition does not repair that missing closure.

This diagnosis neither defines nor rules out a larger completed self-dual
configuration or a different projective correlation. Such a proposal needs
an explicit point set, line set and duality map before it can become a new
constraint. No claim about arbitrary projective polarities is made here.
