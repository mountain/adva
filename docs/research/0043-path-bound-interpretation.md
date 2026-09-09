# A finite Surface phrase bound to an oriented Legendre path

Date: 2026-09-09. Direction: Mingli Yuan; implementation: ChatGPT/Codex.
Status: Proposed external research; no native admission.
Base: `6d31e377d4a5c8cd16045996cbe9cb840e0c7bae`.
Library pin: `d6765f7ff3875bc79c8bdaa4fdbe8a70737d5c72`.

## 1. What the parallel work changed

The library commit changes the Surface naming entry from `wenyan` to two
declared languages: Wenyan for the human interface and `scale-marked cyclic`
for the mechanism-side working language. It cites the now-merged #164
research commit. The catalog digest was updated; the entry remains
`proposed-document`. This is a documentary refinement, not an implemented
translator, a new theorem or witnessed human acceptance.

The library's meaning-interpretation document still labels the H2/Teichmuller/
Calabi-Yau identification as a hypothesis. The new naming entry does not
prove it. A read attempt at the referenced `mountain/AEG` repository returned
404; that could reflect naming or access. This round does not claim to have
inspected the AEG mechanism, Wenyan implementation, or its receipt bytes.

Main includes #164, with exact scale-aware recovery and transported input
swaps. Drafts #161 and #163 remain unmerged. The former's distinction between
a mechanism and its stipulated interpretation is relevant context but is not
an admitted dependency. No library catalog, pinned Pascal material, math
growth obligation, claim registry or native code is changed here.

The next useful question is whether an interface instruction agrees with
an independently supplied path and a declared algebraic action. This also
implements the narrow next step explicitly left open by #164.

## 2. Frozen question, domain and interpretation

The four interface strings are exactly:

```
绕零孔 正行 1 周
绕零孔 逆行 1 周
绕零孔 正行 2 周
绕零孔 逆行 2 周
```

Their stipulated meanings are winding +1, -1, +2 and -2 respectively. This is
a four-entry experimental grammar, not a claim to interpret Chinese prose
or to execute the Wenyan language. `闭合` alone is deliberately unsupported:
it does not specify endpoint, action, history or observer-level closure.

Here `零孔` names the removed geometric parameter value lambda=0. It is not
an Adva input hole, an Omega point, a proof obligation or a human subject.

An independent input supplies a based, closed rational polygon in

```
D = { lambda in C : 0 < |lambda| < 1/2 }.
```

It also supplies an oriented integral homology basis B in SL(2,Z). Columns
of B are new basis vectors expressed in the fixed reference basis. The
imported convention from Research 0043 is

```
A = M0 = ((1,2),(0,1))
positive = counterclockwise
M_reference = A^w = ((1,2*w),(0,1))
M_B = B^-1 M_reference B.
```

This round imports the identification of A with Legendre local monodromy;
it does not derive it from elliptic integrals or solve the Picard-Fuchs
equation. What is newly checked is the agreement of the phrase, concrete
polygon winding, basis convention and claimed matrix. Missing basis returns
UnknownBasis rather than guessing an orientation.

## 3. Exact path checker

All coordinates are Fractions; no floating-point angles or tolerances enter.
Every vertex has nonzero squared norm strictly below 1/4. Convexity of the
disk ensures every line segment remains inside it. A segment hits the origin
exactly when its endpoint cross product is zero and their dot product is
nonpositive; such a segment is refused.

The checker counts signed crossings of the positive real ray using a
half-open endpoint convention. For an upward crossing with a_y <= 0 < b_y,
cross(a,b)>0 contributes +1; the downward counterpart contributes -1. This
is the usual winding number for a polygon avoiding the origin. Horizontal
edges and repeated ray vertices do not receive spurious contributions.

The punctured disk has fundamental group Z; once basepoint, orientation and
the monodromy representation are fixed, its loop class is determined by w.
Consequently A^w is sufficient in this local domain. This argument explains
the scope; finite testing alone is not the justification for arbitrary local
polygon homotopy invariance.

Acceptance also checks the change-of-basis square on the fixed reference
charge q=(0,1):

```
B (M_B (B^-1 q)) = A^w q.
```

The complete input polygon and phrase remain in the receipt. Subdivision
may preserve the matrix while changing the recorded path. No matrix equality
authorizes deletion or semantic identification of these histories.

## 4. A directly inspectable witness

Take the rational diamond

```
1/8 -> i/8 -> -1/8 -> -i/8 -> 1/8.
```

It lies in D, avoids zero, and has winding +1. Its starting and ending
parameters agree. Nevertheless

```
A (0,1) = (2,1) != (0,1).
```

Reversing the polygon gives winding -1 and A^-1, sending (0,1) to (-2,1).
The same positive interface phrase paired with that reversed path is refused.
Thus endpoint closure does not imply identity of transported homology.

For fresh reuse, a nonsymmetric polygon with six listed vertices and a new
basis B=((1,2),(1,3)) is accepted. This changes both the geometry of the
polygon and its coordinate presentation; it is not another radius of the
same diamond.

## 5. Why the local boundary is necessary

Let B1=((1,0),(-2,1)) be the second cusp matrix in the existing convention.
Then an exact multiplication gives

```
A B1 A^-1 B1^-1 = ((13,8),(8,5)) != I.
```

The formal commutator word has zero total exponent around both cusps. This
shows that the pair of abelian winding counts does not determine the global
action on the three-punctured sphere. The report stores the formal generator
word and left-to-right matrix product; no concrete global polygon is claimed
constructed or checked here. Column-vector applications use the corresponding
right-to-left composition order.

Thus one must not promote the local rule `w=0 => identity action` to all of
P1 minus {0,1,infinity}. Recovering the ordered nonabelian loop word is a
separate obligation. This is a scope counterexample, not a failure of exact
arithmetic and not a new monodromy theorem.

## 6. Relationship to the three-expression surface model

The preceding round's matrix L=(2I+C)/3 gives an exact possible bridge:
hold epsilon and two regular lambda coordinates fixed, let the third follow
the checked polygon, and recover z=epsilon^-1 L^-1 lambda along the path.
Because the map is linear, each polygon edge remains a line segment in these
input coordinates. This is a formula for a next construction, not an
executed three-machine path receipt in this round.

There is an important coverage change: the preceding test grid placed every
lambda in the positive real/imaginary quadrant, which cannot contain a loop
around zero. The present loop therefore leaves that old observation region.
Its acceptance comes from the new punctured-disk contract, not from reusing
the old grid's coverage certificate. The old finite evidence remains valid
in its original scope.

Likewise, the transported S3 input swaps of #164 are not these monodromy
loops. Surface language must distinguish changing an input order, changing
coordinates, and following a path that transports a homology charge.

## 7. Proposed working relation

`path-bound-interpretation` is a proposed composite relation, not a stable
primitive:

```
(phrase, concrete path, basepoint, domain, basis, imported convention)
    -> (measured winding, action, agreement/refusal, retained history).
```

Its role is to connect a small interface instruction to an independently
checkable geometric path and algebraic effect. A phrase alone, a matrix
alone, or equal endpoints is insufficient for this relation.

Required conditions: the exact grammar, rational local polygon, bounded
resource contract, explicit basis, and imported monodromy convention.
Witnesses: 36 baseline cases, fresh reuse, inverse-orientation and scope
counterexamples. Rejection conditions: unsupported phrase, wrong direction
or turns, missing/invalid basis, wrong claimed action, wrong basepoint, open
path, origin crossing, outside-domain path or exceeded bounds.
Expansion/replay: the four phrase entries, rational crossing algorithm and
matrix formula in run.py. Residuals: actual Wenyan integration, analytic
period derivation, global ordered path words, native identities, Surface
geometry and human acceptance. No speedup, universality or learned-theorem
claim is made. It proposes a precise relation for testing interface fidelity.

## 8. Evidence and cost

Before executing, the budget was made explicit about replay: at most 64
initial validation cases and 128 total checker calls including replay, a
single 30-second deadline, at most 32 vertices per polygon, 64-bit rational
input components and checked matrix entries. Temporary intermediate integer
maxima are not instrumented. There is one route, no fuel reset and no
execution correction or retry. Contract and script were saved before the run.

Run from the repository root on Linux with Python 3.11+ standard library:

```sh
timeout 30s python3 experiments/path_bound_interpretation/run.py /tmp/path-evidence.json
```

Observed results:

- 36 baseline cases: four phrases, three radii, three bases;
- one fresh asymmetric polygon with a fourth basis;
- 13 refusal controls, a subdivision/history control and the global
  commutator scope control;
- 52 initial checker calls and 37 serialization replay calls, 89 total;
- all 37 accepted paths close at their endpoints and have nonidentity
  matrices, exposing the endpoint-only rule's 37 false positives in this scope.

Measured construction: 0.201 ms; baseline checks: 2.982 ms; fresh reuse:
0.070 ms; controls: 0.628 ms; serialization: 0.695 ms; replay: 8.637 ms.
Elapsed before final report write: 13.716 ms; outer process wall: 82.504 ms.
Sampled process high-water RSS: 11,136 KiB on Linux (10.875 MiB), sampled
before final report writing. Authoring, network, analytic periods, temporary
integer maxima and final write cost were not separately measured.

`experiments/path_bound_interpretation/evidence.json` contains all accepted
input polygons, basepoints, bases, actions, charges, histories, control results,
digests and costs. Control construction is explicit in the fixed script.
Hashes bind bytes only; no signature or authentication is claimed. Replay
uses the same checker and is not independent verification of the checker.
The algebraic argument and explicit counterexamples provide separate grounds
for the declared local rule. No complete workspace, native or remote CI pass
is claimed.

## 9. Next smallest continuation

Connect one accepted polygon to the actual three-expression input ledger via
the displayed inverse L, retaining which input occurrences change at each
edge. Supply a new finite coverage contract for that extended input region.
Compare the input-side path and output-side path as whole ordered records,
then bind the existing local monodromy receipt. Do not infer global loop
identity from winding counts or relabel a path receipt as native free.
