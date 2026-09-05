# Typed Vacua and Constant-Boundary Braids: A Three-Bracket Calibration

Status: bounded research calibration following
[`0049-triadic-universal-computation-form-plan.md`](0049-triadic-universal-computation-form-plan.md)
and the cellular annulus / torus Dehn-twist calibration in
[note 0048](0048-cellular-annulus-nodal-torus-dehn-twist.md).

The executable fixture is
`tests/python/test_tri_bracket_braid_transport.py`.

This note tests the proposal that the three empty pairs

```text
{}[]()
```

form a permanently available three-colored boundary and that nontrivial run
history may be carried by braids over that boundary.  The bounded result is:

> The fixed three-color boundary supports a nontrivial pure-braid transport
> layer.  Three visible color rotations return to the original boundary but
> leave a central full twist in the exact lift.  Three opposite-pair winding
> readings recover only the abelianized shadow and can forget global schedule
> order.  Braid transport alone cannot realize the nontrivial idempotent
> updates already present in the finite triadic program experiments.

This is a transport and no-go calibration, not a universal-computation
result.  It adds no stable bracket, vacuum, braid, scheduler, code-as-data,
interpreter, state, logic, or three-computer API; does not modify
`claims.toml`; and does not change Rust semantic authority or the active
`ProgramSlice` priority.

---

## 0. Executive separation

The proposal becomes nontrivial only after separating four layers:

| layer | provisional object | role |
|---|---|---|
| glyph | `{}`, `[]`, `()` | finite surface notation |
| type | `K`, `X`, `t` | construction, spatial, and temporal colors |
| boundary | \(\Omega_{\partial}=K\otimes X\otimes t\) | invariant external interface |
| run | \(p:\Omega_{\partial}\to\Omega_{\partial}\) | history-bearing endomorphism |

The tensor notation is mathematical shorthand.  It does not assert that the
current Adva frontier implements a tensor product.

A fixed boundary does not imply a fixed internal state, a fixed filling, or
an identity program.  In particular,

\[
p:\Omega_{\partial}\to\Omega_{\partial}
\]

does not imply

\[
p=1_{\Omega_{\partial}}.
\]

This distinction is the first way in which one visible form can carry many
program histories.

## 1. Three typed vacua, not three monoidal units

Use the provisional correspondence

\[
{}\leftrightarrow K,
\qquad
[]\leftrightarrow X,
\qquad
()\leftrightarrow t.
\]

The three pairs are typed vacuum generators.  They are not three copies of
the monoidal unit.  The unit is the empty word

\[
\mathbb I=\varepsilon.
\]

If all three pairs were declared to be the same unit object, monoidal
coherence would canonically identify them and braiding with the unit would be
trivial.  The distinction needed by the proposal would disappear.

A more detailed future semantics may use three preparations

\[
\epsilon_K:\mathbb I\to K,
\qquad
\epsilon_X:\mathbb I\to X,
\qquad
\epsilon_t:\mathbb I\to t.
\]

The present fixture does not interpret these preparations.  It checks only
the typed boundary and its transport histories.

## 2. The strict flat grammar used here

This first fixture chooses the strictest no-nesting reading:

```text
atom ::= {} | [] | ()
word ::= empty | atom word
```

Every accepted pair is empty and atomic.  Mixed forms such as `{[]}`, `[()]`,
and `({})` are rejected.  Same-color nesting such as `{{}}` is also excluded
from this transport calibration.

The last exclusion is stronger than the conjecture that only mixed nesting
is forbidden.  It is deliberate: it isolates the question of whether a flat,
constant boundary can already carry nontrivial run history.  A later code
grammar may add typed same-color constructors

\[
b_D:D\to D
\]

without adding any mixed constructor \(D\to D'\) for \(D\ne D'\).

The public boundary is the one word

\[
\boxed{\Omega_{\partial}={}[]()}. 
\]

Permuted color words occur only as typed intermediate objects while a braid
is being composed.  They are not additional public machine boundaries.

## 3. The colored braid groupoid

Let

\[
O=\{K,X,t\}.
\]

The free braided monoidal category on \(O\) has color words \(O^*\) as
objects and color-preserving braids as morphisms.  Juxtaposition is the
monoidal product and vertical stacking is sequential composition.

For the boundary \(KXt\), the elementary crossings have typed targets:

\[
\sigma_1:KXt\longrightarrow XKt,
\]

\[
\sigma_2:KXt\longrightarrow KtX.
\]

Neither generator is by itself an endomorphism of \(KXt\).  If the three
distinct colors must return to their original endpoint types, the endomorphism
group is the pure braid group

\[
\operatorname{End}(\Omega_{\partial})\cong P_3,
\]

not the whole uncolored braid group \(B_3\).

Three useful pure generators are

\[
A_{12}=\sigma_1^2,
\qquad
A_{23}=\sigma_2^2,
\qquad
A_{13}=\sigma_2\sigma_1^2\sigma_2^{-1}.
\]

The fixture represents endpoint colors explicitly and uses the standard
faithful Artin action

\[
B_3\hookrightarrow\operatorname{Aut}(F_3)
\]

for exact braid equality.  Free-group words are reduced using signed integer
generators; no floating-point or sampled geometric oracle is involved.

This Python model is an independent research oracle.  It does not create an
Adva `SourceId`, `OccurrenceId`, program identity, or semantic certificate.

## 4. Braid coherence is not free exchange

The elementary generators satisfy

\[
\boxed{
\sigma_1\sigma_2\sigma_1
=
\sigma_2\sigma_1\sigma_2.
}
\]

They do not satisfy \(\sigma_i^2=1\).  Replacing the crossings by ordinary
swaps would quotient the braid group to the symmetric group \(S_3\) and erase
over-crossing versus under-crossing history.

Thus three different notions remain separate:

1. no mixed nesting is a typing restriction;
2. juxtaposition is composition at the object boundary; and
3. braid coherence is a checked equality between two transport histories.

None implies unconditional exchange of arbitrary program updates.

## 5. Three rotations and one central residual

Let

\[
r=\sigma_1\sigma_2,
\qquad
\Delta=\sigma_1\sigma_2\sigma_1.
\]

On endpoint colors, \(r\) is a three-cycle.  Therefore the coarse endpoint
observer sees

\[
r^3=1.
\]

In the braid lift, however,

\[
\boxed{
r^3=(\sigma_1\sigma_2)^3=\Delta^2\ne 1.
}
\]

The full twist \(\Delta^2\) is central.  The fixture checks exact commutation
with both generators and proves nonidentity through the faithful Artin action.

This gives a minimal form of the proposed invariant machine:

> the three visible types return to the same positions while the run retains
> an integer-like holonomy that the endpoint state does not show.

There is a precise projective shadow.  Under

\[
\sigma_1\longmapsto
\begin{pmatrix}1&1\\0&1\end{pmatrix},
\qquad
\sigma_2\longmapsto
\begin{pmatrix}1&0\\-1&1\end{pmatrix},
\]

the braid relation holds and \((\sigma_1\sigma_2)^3\) maps to \(-I\).  It is
therefore invisible after projectivizing to \(PSL_2(\mathbb Z)\), although the
Artin lift remains nontrivial.

This connects, without identifying, two earlier observations:

- the Legendre calibration has a braid relation and a central sign in its
  lifted monodromy; and
- the cellular-annulus calibration closes on finite vertices while retaining
  unbounded winding in paths and homology.

The present full twist is not declared to be an Adva residual, energy,
characteristic, or universal \(\Omega\).  It is one exact candidate carrier
for history that a coarse observer forgets.

## 6. Three opposite-pair winding shadows

For a pure braid, forget one strand and measure the signed winding of the
remaining pair.  This gives three integer readings:

\[
\lambda_t:P_3\to\mathbb Z,
\qquad
\lambda_X:P_3\to\mathbb Z,
\qquad
\lambda_K:P_3\to\mathbb Z.
\]

The subscript names the omitted color.  The three pure generators have

| pure braid | \(\lambda_t\) | \(\lambda_X\) | \(\lambda_K\) |
|---|---:|---:|---:|
| \(A_{12}\) | 1 | 0 | 0 |
| \(A_{13}\) | 0 | 1 | 0 |
| \(A_{23}\) | 0 | 0 | 1 |

Together these readings are the abelianization shadow

\[
P_3\longrightarrow\mathbb Z^3.
\]

They do not recover global order.  The fixture constructs

\[
\beta_L=A_{12}A_{23},
\qquad
\beta_R=A_{23}A_{12}.
\]

Then

\[
(\lambda_t,\lambda_X,\lambda_K)(\beta_L)
=
(\lambda_t,\lambda_X,\lambda_K)(\beta_R)
=(1,0,1),
\]

but

\[
\beta_L\ne\beta_R.
\]

The commutator

\[
c=A_{12}A_{23}A_{12}^{-1}A_{23}^{-1}
\]

is even sharper:

\[
(\lambda_t,\lambda_X,\lambda_K)(c)=(0,0,0),
\qquad
c\ne1.
\]

Pairwise readings do not even detect centrality.  The full twist and the
noncentral word

\[
A_{12}A_{23}A_{13}
\]

both have shadow \((1,1,1)\), but the two braids are unequal and only the
full twist commutes with both elementary generators.

Therefore three complete pairwise winding readings may still forget a
noncommuting three-strand history.  This is an exact topological analogue of
the schedule and pairwise-marginal residuals in the finite triadic
experiments.  It does not identify the winding maps with the existing
opposite-pair sections; that comparison remains a future interpretation map.

## 7. The braid-only no-go

Every braid-group action is invertible.  If an action element \(e\) were
idempotent,

\[
e^2=e,
\]

then multiplication by \(e^{-1}\) would give

\[
e=1.
\]

Hence a braid group or groupoid action has no nonidentity idempotent update.

The finite triadic context experiments supply concrete incompatible
operations:

\[
T(t,x,k)=(1,x,k),
\]

\[
X(t,x,k)=(t,t\wedge k,k).
\]

They satisfy

\[
T^2=T,
\qquad
X^2=X,
\]

but neither is the identity and neither is injective.  On the eight-state
Boolean core each has image rank four.  The fixture recomputes these facts and
performs a bounded exact enumeration of Artin braid actions as a regression
witness for the general cancellation proof.

Therefore the existing updates cannot be identified with braid crossings.
At most, braid is the reversible group of units or the structural routing
layer inside a larger computation system.  A noninvertible quotient of the
positive braid monoid could contain idempotents, but it is no longer a braid
group action and must be named and tested separately.

Two further capacity bounds are immediate:

1. if only final endpoint permutations are observed, the state space has at
   most six elements; and
2. if the three colors must return to fixed positions and crossing history is
   discarded, the endpoint observer has only one state.

Keeping the full braid class avoids those finite bounds, but then the history
is an additional unbounded state carrier.  It is not contained in the three
empty glyphs alone.

## 8. Position inside the universal-computation plan

The research plan requires

\[
(\mathfrak F_Q;U_t,U_X,U_K;p_t,p_X,p_K;\sigma;\operatorname{Cal}_0).
\]

This calibration contributes only a candidate structural part of \(\sigma\):

- typed routing between the three positions;
- exact coherence between alternative crossing decompositions;
- a lift-sensitive schedule history; and
- three coarse pairwise observations with an explicit residual kernel.

It does not supply:

- a code carrier;
- any of the three interpreters;
- independently injected programs;
- startup calibration;
- tests or conditional branches;
- explicit copy or discard;
- growing storage; or
- a simulation theorem for a known universal machine.

The appropriate larger research container is provisionally

\[
\mathcal C_3
=
\operatorname{FreeBrMonCat}
\langle
K,X,t;
g_\alpha:w_\alpha\to w'_\alpha
\mid\mathcal R
\rangle,
\]

or a braided colored PROP when the computational generators have multiple
inputs and outputs.  Braiding supplies reversible transport; the
\(g_\alpha\) supply local, potentially noninvertible computation.  Copy,
discard, tests, and branches must remain explicit generators or checked
derived operations.

## 9. What the fixture establishes

Within its declared finite syntax and exact algebra, the fixture establishes:

1. three distinct typed vacuum atoms and a distinct empty word;
2. rejection of all bracket nesting in the strict flat calibration;
3. the fixed external boundary `{}[]()`;
4. typed intermediate color permutations;
5. pure-braid return to the original endpoint colors;
6. the exact \(B_3\) relation and inverse laws through the Artin action;
7. nontrivial central holonomy after three visible rotations;
8. projective loss of the central lift;
9. three exact opposite-pair winding readings;
10. equal pairwise shadows with unequal global histories;
11. a nontrivial commutator invisible to all three winding readings;
12. equal nonzero winding shadows with different centrality; and
13. incompatibility between invertible braid transport and nontrivial
    idempotent updates.

## 10. What it does not establish

The fixture does not establish:

- that the glyph-to-domain assignment is canonical;
- that same-color nesting must be forbidden;
- that every Adva program has a braid presentation;
- that every scheduler should satisfy a Yang--Baxter equation;
- that braid holonomy is observable in the current Adva state;
- that pairwise winding is the meaning of an opposite-pair section;
- that the finite \(T,X,K\) machine is a braid machine;
- a stable braided category or PROP implementation;
- U0 uniform programmability;
- Turing, component, coupled, or reflective universality; or
- mathematical novelty of the standard braid-group facts.

## 11. Decisive next experiment

The next falsifiable step is to add exactly one typed, noninvertible active
pair rewrite

\[
g_{DX}:D\otimes X\longrightarrow D\otimes X
\]

beside the reversible crossings.  It should be extracted from one existing
checked triadic update rather than invented only to satisfy a desired law.

The experiment must check:

1. exact source and target colors;
2. whether moving the gate through a third strand has a valid coherence law
   or a retained residual;
3. schedule order before and after the gate;
4. explicit copy, discard, and overwritten information;
5. whether three opposite-pair observations still miss a global history; and
6. whether the result is a group action, a noninvertible braid-like quotient,
   or a general braided rewriting system.

Only after that substrate exists should a U1 experiment encode a known
universal model, such as a fuel-bounded two-counter machine or a flat
interaction-net calculus.  Infinite history by itself is not a universality
proof.

## 12. Falsifiers

The braid hypothesis should be weakened or rejected if:

1. every declared observer identifies the full twist with identity and no
   later program can read the residual;
2. the actual typed crossings fail the braid coherence law;
3. preserving the fixed boundary requires implicit copy, discard, or source
   identification;
4. program composition cannot retain crossing source and occurrence history;
   or
5. all useful state must instead live in same-color nesting, making the flat
   braid layer merely decorative.

If the full twist is observable but no noninvertible gate composes coherently
with it, the correct result is a transport sidecar rather than a universal
machine substrate.

## Conservative conclusion

The three-bracket intuition survives its first exact test in a restricted
form:

> `{}[]()` can be a constant typed boundary while nontrivial process history
> lives in its pure-braid endomorphisms.  Three rotations close visibly but
> leave a central lift, and three pairwise winding observations still forget
> noncommuting global history.

The same test also fixes the boundary of the idea:

> braid is reversible transport, not the complete computation.  The existing
> nonidentity idempotent updates require a larger noninvertible rewriting
> structure, and universality still requires an explicit encoding and
> simulation theorem.

The immediate research target is therefore not “prove the three brackets are
universal.”  It is “compose one checked irreversible gate with this exact
three-color transport without erasing type, schedule, source, occurrence, or
residual history.”

## Mixed-nesting normalization follow-up

The partial-normalization logic follow-up is
[`0059-tri-bracket-eigen-normalization-logic.md`](0059-tri-bracket-eigen-normalization-logic.md).
It moves mixed nesting into raw syntax and makes flatness an eigenform property.
Its exhaustive first tri-cell shows that braid exchange preserves containment
edges and therefore cannot normalize the twenty-four nested presentations.  A
separate containment-splitting rewrite is required before braid transport can
calibrate the flat boundary.  That split remains a syntax-level oracle and is
not identified with a checked Adva gate.

## References

- André Joyal and Joachim Kock,
  [Weak units and homotopy 3-types](https://arxiv.org/abs/math/0602084),
  especially the free braided monoidal category on a set of colors.
- Alexander I. Suciu and He Wang,
  [The pure braid groups and their relatives](https://arxiv.org/abs/1602.05291),
  for pure braid structure and linking-number abelianization.
- Subhajit Datta,
  [The braid group \(B_3\) in the framework of continued
  fractions](https://arxiv.org/abs/2008.02262),
  for the central quotient and modular/projective description.
- Yves Lafont,
  [Interaction combinators](https://doi.org/10.1006/inco.1997.2643),
  for a universal flat local-rewrite calibration with three agent types.
