# Simplex contraction, Pascal certificates, and Calabi's scalar reduction

Date: 2026-09-09.
Status: discussion synthesis and research proposal; no new computational run,
Metamath proof, native operation, or catalog admission.
Direction and questions: Mingli Yuan / 苑明理.
Literature checking, formalization, and boundary review: ChatGPT.

## 1. Question and repository checkpoint

Can finite exploration stop by shrinking a simplex below an observer's
resolution, while preserving the truth of a Pascal proof obligation?
Can Calabi's reduction from a metric problem to a scalar potential suggest
a faithful reduction of the actual search variables?

This note records the conversation before further implementation. It is
based on adva main 7cf1d0ccd69cf5fa1fecf0c1328f1c3aa6a6c237, whose library
gitlink is 6016248224d968e9ce1323477ecc21bc8c29d443.

Relevant existing material:

- [Research 0128](0128-acceleration-direction-pascal-incidence.md):
  the classical Pascal polynomial identity, an external exact checker,
  projective covariance, and conditional reuse costs.
- [Research 0129](0129-bounded-breakthrough-trusted-boundaries.md):
  protected obligations, finite fuel, independent acceptance, and scoped Unknown.
- [Research 0130](0130-prefix-coverage-gated-close.md): the registered finite
  prefix-coverage experiment. Coverage is necessary before feature closure;
  interval width alone does not suffice.
- [Pinned Pascal task](https://github.com/mountain/adva-library/blob/6016248224d968e9ce1323477ecc21bc8c29d443/pascal-task.adva)
  and [witness](https://github.com/mountain/adva-library/blob/6016248224d968e9ce1323477ecc21bc8c29d443/pascal-witness.adva).
- [Contemporary Yau-Calabi narrative mapping](https://github.com/mountain/adva-library/blob/6016248224d968e9ce1323477ecc21bc8c29d443/meaning-yau-calabi-mapping-v0.md):
  already recorded on main as a proposed documentary analogy.

At this checkpoint PRs #161, #163, and #166 remain unmerged proposals.
This note does not depend on their implementations.

The pinned Pascal task SHA-256 is
60d3ca374486239afb82bbe31d821a4d0c02ef947ccf62557753e85137087a5d;
the witness SHA-256 is
f20338add39c292db6bac482a2c9265353d6a5a1a5189cc2823398ddc29fe448.
These are integrity references, not authentication.

The existing math growth obligation remains Open / native Seal NotIssued.
This is a docs/research handoff, not a new geometry catalog entry or a
cross-topic derivation parent. The original Pascal bytes, library gitlink,
claim registry, and runtime are unchanged.

## 2. What shrinking establishes

For a simplex with vertices v_0,...,v_d, uniform shrinking is

\[
v_i' = v_0+\sigma(v_i-v_0),\qquad 0<\sigma<1.
\]

In a fixed norm and coordinate presentation, each pairwise difference is
multiplied by sigma. After m consecutive uniform shrinks,

\[
D_m=\sigma^mD_0.
\]

For D_0 > epsilon > 0, taking

\[
m\ge\left\lceil
\frac{\log(D_0/\epsilon)}{\log(1/\sigma)}
\right\rceil
\]

ensures D_m <= epsilon. This elementary estimate counts uniform shrinks,
not all Nelder-Mead iterations. Intervening reflection or expansion invalidates
that simple whole-run formula. Exact rational shrinking also grows coordinate
bit lengths; a geometric step count is not a constant-cost arithmetic model.

Standard Nelder-Mead is a heuristic optimizer. McKinnon [1] constructs
strictly convex, differentiable two-variable examples on which it converges
to a nonstationary point. Small diameter therefore does not imply a root,
an optimum, or a proof.

A further distinction is observer-relative. For the grid observer
Q_epsilon(x)=floor(x/epsilon), the interval
[epsilon-epsilon/4, epsilon+epsilon/4] has width epsilon/2 but contains
two observed values, 0 and 1. Diameter below a cell width does not guarantee
membership in one cell.

Finally, a search simplex is not automatically an enclosure of every
admissible solution. Any discarded region needs a justification, a retained
alternative, or an explicit loss of coverage. Shrinking cannot discharge that
obligation by itself.

## 3. A projective scaling counterexample

In projective geometry, [v]=[lambda v] for nonzero lambda.
For three homogeneous representatives,

\[
\det(\lambda X,\lambda Y,\lambda Z)=\lambda^3\det(X,Y,Z).
\]

Take X=(1,0,0), Y=(0,1,0), Z=(0,0,1).
Their determinant is 1. With lambda=1/1024, it becomes 1/1073741824,
but the projective points are unchanged and remain noncollinear.
This is a control for a proposed incidence checker, not a counterexample
to Pascal under its conic assumptions.

A numerical objective based on an unnormalized determinant can therefore
improve merely by changing representatives. Before interpreting shrinkage,
fix a chart or a gauge with its domain, nonzero conditions, observable,
and metric. One chart may not cover the full task; changing charts requires
an explicit transition and retained history. Normalization does not by
itself repair missing coverage.

## 4. When a small residual can certify exact zero

There is a conditional arithmetic bridge:

\[
R=N/D,\quad N\in\mathbb Z,\quad D\in\mathbb Z,\quad 0<D\le B.
\]

If a rigorous bound establishes |R|<1/B, then N=0 and R=0.
For N nonzero, |N|>=1 and hence |R|>=1/D>=1/B.

Required inputs are the exact expression, a proved denominator bound,
all definedness conditions, and a certified strict residual bound.
A floating-point value, an interval merely containing zero, or a small
simplex supplies none of these automatically.

Without a denominator bound, nonzero rationals can approach zero arbitrarily
closely. For a polynomial with integer coefficients, certified coefficientwise
absolute bounds strictly below 1 also imply a zero polynomial; small values
at a few sample points do not.

The rational criterion establishes one specified residual's equality.
A universal Pascal claim still needs a symbolic identity or an appropriate
universal argument, together with the geometric assumptions.

## 5. Two meanings of three-dimensional Pascal

### 5.1 Three-dimensional vector representation of the plane theorem

A projective plane point is a nonzero vector in K^3 modulo nonzero scale.
The conic xz-y^2=0 is a quadratic cone in the vector presentation.
Three projective points are collinear exactly when their three representative
vectors are linearly dependent. Their rays then lie in a plane through the
origin. The projective dimension is still two.

The normalized library task already uses this representation. Over Q,
let d,e,f be pairwise distinct and different from 0 and 1, and take

\[
A=(1,0,0),\ B=(0,0,1),\ C=(1,1,1),\
D=(1,d,d^2),\ E=(1,e,e^2),\ F=(1,f,f^2).
\]

Its three opposite-side intersections have representatives

\[
X=(1,0,-de),\quad Y=(1,1,e+f-ef),\quad
Z=(1+d-f,d,df).
\]

The common line is

\[
\ell=(de,-(de+e+f-ef),1).
\]

The third residual is the following identity in Z[d,e,f]:

\[
de(1+d-f)-d(de+e+f-ef)+df
=de+d^2e-def-d^2e-de-df+def+df=0.
\]

The other two dot products also vanish directly. The line is nonzero because
its third coefficient is 1; X and Y have first coordinate 1, and Z has
second coordinate d != 0. The original witness also retains conic membership,
endpoint incidences, intersection incidences, and negative controls.

These are existing arithmetic constructions, not a newly discovered theorem
or a newly executed proof. Their translation into Metamath remains to be
constructed and checked. General conic inputs additionally need the
normalization/transport lemma and its invertibility conditions.

Research 0128 provides a broader, classical identity F=G: a six-by-six
conic-membership determinant equals the opposite-side incidence determinant.
Its stored 720-term polynomial certificate is an alternative existing
algebraic route, not a reason to repeat numerical search.

### 5.2 A genuine projective three-space extension

Caminata and Schaffler [2, Theorem A] give a higher-dimensional Pascal
generalization. In P^3, seven points on a twisted cubic are the relevant
configuration. For example, the curve has parametrization

\[
[s:t]\longmapsto[s^3:s^2t:st^2:t^3].
\]

For seven points in general linear position on that curve, the points

\[
U=P_1P_2\cap P_4P_5P_7,\quad
V=P_2P_3\cap P_5P_6P_7,\quad
W=P_3P_4\cap P_1P_6P_7,\quad P_7
\]

are coplanar. Here two labels denote a line and three denote a plane.
The cited characterization requires the analogous condition for each choice
of six labels. Its stated field framework is algebraically closed;
a new rational or real implementation must specify its own hypotheses.

P^3 uses four homogeneous coordinates. It must not be conflated with the
three-coordinate lift of P^2, or with the dimension of an optimizer's
parameter simplex. This extension is a literature reference only; no new
seven-point experiment or proof obligation is activated here.

## 6. Calabi: preserve the structure, reduce the unknown

The primary bibliography matching the discussed subject is:

Eugenio Calabi, On Kähler Manifolds with Vanishing Canonical Class,
in Algebraic Geometry and Topology: A Symposium in Honor of Solomon
Lefschetz, Princeton University Press, 1957, pp. 78-89 [3].
The publisher's 2015 electronic edition is not the original publication date.
Calabi's earlier 1954 ICM note, The space of Kähler metrics, vol. II,
pp. 206-207, is a precursor. The quoted reminiscence alone does not identify
which edition or early text Yau physically encountered.

Calabi's pp. 79-80 discuss recovering the Ricci tensor from the volume
density and prescribing the Ricci form in a fixed Kähler class.
Proposition 1 is accompanied by an explicit acknowledgment that the
existence proof was incomplete. Yau's full proof appeared in [4].
The original publisher PDF was located but not successfully retrieved during
the lookup; searchable original-text transcription and bibliographic sources
were consulted. No archival PDF attachment is claimed.

In modern notation, let M be a compact connected Kähler manifold without
boundary, of complex dimension n, with fixed complex structure and
background Kähler form omega. Within its fixed Kähler class write

\[
\omega_\varphi=\omega+i\partial\bar\partial\varphi>0.
\]

For a prescribed smooth positive volume form mu with

\[
\int_M\mu=\int_M\omega^n/n!,
\]

the equation is

\[
(\omega+i\partial\bar\partial\varphi)^n/n!=\mu.
\]

Equivalently, write n! mu=e^F omega^n.
The unknown phi is one real-valued function, modulo an additive constant;
it is not one real number or a finite vector. This is a fully nonlinear
second-order complex Monge-Ampère PDE, elliptic on the positive-definite
branch. Fixing the complex structure and Kähler class, and retaining
positivity and volume compatibility, are essential.

Locally the Ricci form is

\[
\rho(\omega_\varphi)=-i\partial\bar\partial\log\det(g_{\varphi,j\bar k}).
\]

Prescribing a volume density whose induced Ricci form is zero therefore
gives a Ricci-flat solution. On a compact Kähler manifold with c_1(M)=0
in real cohomology, the Calabi-Yau theorem yields a unique Ricci-flat
Kähler metric in each Kähler class.

The contemporary narrative mapping needs two explicit interpretation guards:

1. The Ricci form itself depends on the metric. Its cohomology class
   [rho]=2*pi*c_1(M) is the invariant. Vanishing class is not pointwise
   vanishing of the original metric's Ricci tensor.
2. A^0=I and reciprocal spectra in a finite matrix model are algebraic
   facts in that model; they do not prove the PDE existence theorem or
   identify an Adva space with a Calabi-Yau manifold. A scalar determinant
   alone does not faithfully encode a matrix.

The transferable research question is conditional: can we identify a
sufficient reduced representation, prove its decoding/faithfulness boundary,
and solve the remaining obligations more cheaply? Calabi's scalar
potential is a motivation, not an already available Adva encoding.
A finite discretization would additionally require approximation,
positivity, convergence, and error certificates. None is supplied here.

## 7. Proposed next step and stopping boundary

First inspect one concrete Metamath task and its resource-exhaustion log.
The conversation reports repeated exhaustion, but this submission does not
diagnose whether search, expression expansion, transport, or verification
caused it.

Then freeze one proof target: the displayed Z[d,e,f] identity, expressed
using the actual target database's available algebraic lemmas.
Build an explicit derivation and send it to an independent verifier.
Do not assume a Python zero residual is already a Metamath proof.

Proposed limits for that future trial: one primary algebraic route, at most
one alternative route, 30 seconds per subprocess, 100000 proof-search nodes
if any search is used, 256 MiB per child process, 2 MiB retained evidence,
and five minutes total including checking and saving. These are proposed
limits, not an installed supervisor. Confirm the actual enforceable bounds
and database pins before execution; otherwise retain a preflight Unknown.
No full database rebuild or general Pascal search is required by this target.

Success is one accepted, task-bound proof plus a rejected altered-residual
control. Full Pascal, geometric normalization, native import, source/history
transport, and human acceptance remain separate obligations. Reuse should
include a fresh valid rational instance while keeping the symbolic proof
as the universal algebraic evidence.

Nelder-Mead may later order admissible candidates in a declared finite
parameter model. It cannot override coverage or independent verification.
No new vocabulary is promoted in this note: explore, verify,
coverage-gated-close, and acceleration-direction retain their previous scope.
In particular, numerical shrink is not native contraction; additive zero
does not prove a multiplicative inverse or erase an execution history.

## 8. Evidence and cost status

This submission records mathematical derivations, literature references,
and an implementation proposal. Search candidates executed: 0.
New Nelder-Mead runs: 0. New Metamath runs: 0.
Existing benchmark and Pascal replay measurements were not rerun and are
not reported as fresh measurements. No new runtime, peak-memory, or speedup
measurement is available. Documentation/source checks are not theorem
verification.

The useful outcome is a sharper separation of geometric localization,
observer-relative indistinguishability, exact equality, and proof admission.
The next smallest engineering obligation is a single exact algebraic proof
export, after inspecting the actual verifier boundary.

## References

1. K. I. M. McKinnon, Convergence of the Nelder-Mead Simplex Method to a
   Nonstationary Point, SIAM Journal on Optimization 9(1), 148-158 (1998).
   [DOI](https://doi.org/10.1137/S1052623496303482).
2. Alessio Caminata and Luca Schaffler, A Pascal's Theorem for rational normal
   curves, arXiv:1903.00460v2 (2021), Theorem A.
   [Paper](https://arxiv.org/abs/1903.00460).
3. Eugenio Calabi, On Kähler Manifolds with Vanishing Canonical Class (1957),
   pp. 78-89.
   [Publisher](https://doi.org/10.1515/9781400879915-006).
4. Shing-Tung Yau, On the Ricci Curvature of a Compact Kähler Manifold and
   the Complex Monge-Ampère Equation, I, Communications on Pure and Applied
   Mathematics 31(3), 339-411 (1978).
   [Publisher](https://doi.org/10.1002/cpa.3160310304).
