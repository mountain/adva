# Beta-History Local Confluence and Audit 2-Cells

Status: research-local critical-pair theorem, ordered-substitution
composition boundary, and executable audit-square calibration following
[0084](0084-threaded-natural-deduction-entailment-cell.md),
[0085](0085-ordered-substitution-cut-beta-ledger-boundary.md), and
[0086](0086-contextual-beta-ledger-transport-strong-normalization.md).

No stable Adva proof identity, proof version, beta-history type, transport
composition, 2-cell, coherence quotient, logical symbol, or Rust API is
introduced here.  The word **beta** continues to mean contraction of a
principal right-implication detour in a finite checked
\(\mathrm{TND}_0\) natural-deduction proof tree:

\[
\operatorname E
\bigl(\operatorname I_x^b(\pi),\sigma\bigr)
\longrightarrow_\beta
\operatorname{Sub}_x(\pi,\sigma).
\]

There is still no term AST or evaluator.  The results below are not a
runtime lambda-calculus Church--Rosser theorem, an unrestricted cut-
elimination theorem, or a coherence theorem for a future nonlinear logic.
The executable companion is
`test_threaded_beta_confluence_calibration.py`.  Its frozen cell and history
types remain Python research coordinates rather than promoted Adva objects.

---

## 0. Executive result

For the current finite, unfolded, linear one-hole proof trees, two beta-like
redex positions in one checked proof have exactly four prefix relations:

1. the positions are equal;
2. neither position is a prefix of the other;
3. the first is a strict prefix of the second; or
4. the second is a strict prefix of the first.

Equal positions contract deterministically.  Non-prefix positions form an
independent Peiffer square.  A redex strictly inside an outer detour lies
either in the outer body or in the outer argument.  In the body case one
must additionally distinguish an off-spine redex from a redex whose subtree
contains the outer substitution target.  The latter splits according to
whether that target lies in the inner body or the inner argument.

The required equations are:

- independent-redex interchange;
- distinct-hole substitution interchange `SC-body`;
- nested graft associativity `SC-arg`; and
- functoriality in the grafted replacement `GraftNat`.

Under the exact V0 checkedness and freshness conditions, every competing
one-step pair has a common endpoint after at most one residual contraction
on each side.  Thus the underlying proof-tree relation satisfies a
**one-step strong diamond**, and hence local confluence.

This strong diamond depends essentially on linearity:

- the discharged target is one unique assumption leaf;
- its replacement is grafted exactly once;
- no other subtree is duplicated or erased;
- the proof representation has no sharing; and
- contraction only removes the outer elimination, introduction, and target
  leaf while preserving every other resource authority.

Together with strong normalization from note 0086, local confluence gives
global confluence of the underlying beta proof-tree relation by Newman's
lemma.  Every fixed starting proof therefore has one exact structural beta
normal form.

That endpoint theorem does **not** identify two beta histories.  Four levels
must remain separate:

\[
\begin{array}{c}
\text{proof endpoint}\\
\downarrow\ {\scriptstyle\text{retains more audit structure}}\\
\text{composite boundary transport}\\
\downarrow\ {\scriptstyle\text{retains more audit structure}}\\
\text{history}\\
\downarrow\ {\scriptstyle\text{retains more audit structure}}\\
\text{history 2-cell}
\end{array}
\]

The arrows describe increasing retained audit structure.  They are not an
order relation among four notions of equality.

The present note specifies an explicit join-cell whose two histories replay
to one endpoint and have the same canonical composite boundary summary.  The
companion fixture realizes the independent and nested nondegenerate cells.
The same-position case is calibrated by two one-event routes rather than an
identity-cell datatype.  The result does not prove uniqueness of a cell,
equality of histories, higher coherence among three or more competing
reductions, or the validity of any observer quotient.

---

## 1. Dependency boundary and notation

Note 0085 supplies ordered one-hole substitution

\[
\operatorname{Sub}_x(\pi,\sigma)
\]

under strict V0 freshness.  Note 0086 supplies deterministic contextual
contraction at an input-relative premise-index path:

\[
D\Longrightarrow_{\beta,p}^{\tau}D'.
\]

The certificate \(\tau\) relates heterogeneous complete ledgers by a
survivor partial bijection.  It is not ledger equality.

Write

\[
p\preceq q
\]

when \(p\) is a prefix of \(q\), \(p\prec q\) for strict prefix, and

\[
p\perp q
\quad:\Longleftrightarrow\quad
p\npreceq q\ \text{ and }\ q\npreceq p.
\]

Path concatenation is written by juxtaposition.  Thus \(p(0,0)u\) is the
global path obtained by entering the function premise of an elimination,
the body premise of its introduction, and then following \(u\).

For a proof \(D\) with a redex at \(p\), write

\[
\beta_p(D)
\]

for the proof endpoint computed by contextual contraction after erasing the
audit event label.  This notation does not erase the transport when an audit
statement is being made; it only separates the proof result from the
certificate that witnesses it.

---

## 2. Four levels of equality and coherence

The local-confluence statement has four observers with different claims.

- **Proof endpoint.**  The final checked `NDProof` values are structurally
  equal.  Stable nominal proof identity is not claimed.
- **Composite boundary transport.**  The fixture's frozen composite records
  are equal.  They encode the same survivor partial bijection from the
  initial ledger to the final ledger, but not equality of intermediate block
  motions.
- **History.**  Both ordered event sequences replay with their intermediate
  proofs, but the sequences are not equal.
- **History 2-cell.**  A frozen square replays the two nondegenerate routes.
  Uniqueness, composition laws, and higher coherence are not claimed.

### 2.1 Proof endpoint

The current `NDProof` fixture has structural dataclass equality and no
`ProofNodeId`.  The common endpoint theorem is therefore an equality of the
entire reconstructed proof, including its complete ordered ledger.  It is
stronger than equality of conclusion and open context.

### 2.2 Composite boundary transport

Each beta step retires one scoped occurrence, its source authority, and its
binder authority.  Every other `ResourceUse` survives with the same complete
payload.  Mathematically, two steps induce a composite by matching survivor
occurrence keys through the intermediate proof.  For a two-step history

\[
D\xRightarrow{\tau_1}D_1\xRightarrow{\tau_2}J,
\]

the composite boundary transport is the induced partial bijection between
\(\Lambda_D\) and \(\Lambda_J\).  It forgets which crossing happened first.

The executable `CompositeBoundaryTransport` is a canonical extensional
summary recomputed directly from the source, endpoint, and retired authority
set.  Exact equality of two such frozen summaries is calibrated.  The fixture
does not yet expose binary composition of two step transports or prove unit
and associativity laws for such an operation.

In particular, the fixture does not compute this record by composing the two
0086 transports along each route.  Equality of canonical source-to-endpoint
summaries is not equality of \(\tau_2\circ\tau_1\) values in a promoted
transport category, because no such binary operation or equality is defined.

### 2.3 History

The executable `BetaHistory` retains event labels, retired authorities, and
selected input-relative paths.  Its enclosing `BetaRoute` retains the
intermediate proofs.  Replay recomputes the local transports, ancestor frames,
and substitution traces rather than storing them in the history.  Opposite
sides of a critical-pair square normally have different histories even when
their endpoints and composite boundary transports agree.

### 2.4 History 2-cell

A 2-cell records that two replayable histories with a common source have an
exact common endpoint and the same canonical composite boundary summary.  It
relates histories; it does not collapse them.  The cell is external
transformation
history and is not appended to the current proof ledger.

The fixture implements `InterchangeCell` and `NestedCoherenceCell`.  It does
not implement a same-position identity cell: that case compares two
one-event `BetaRoute` values with equal endpoints and composites but unequal
event-labelled histories.

Event identifiers must be exact nonempty `BetaEventId` values and injective
within each fixture history.  The two event identifiers of a nondegenerate
cell must be distinct.  These are local rejection conditions, not a global
allocation theorem.  The same identifier may still be constructed elsewhere,
and no cross-history namespace, freshness service, or promoted event identity
exists.

---

## 3. Exhaustive path classification

Let \(p,q\) be valid redex positions in the same finite proof tree.  Prefix
order on finite tuples gives the disjoint exhaustive classification

\[
p=q,
\qquad
p\perp q,
\qquad
p\prec q,
\qquad
q\prec p.
\tag{Path4}
\]

No fifth overlap case exists.  A proof-tree occurrence is either the same
node, lies strictly above the other, lies strictly below it, or lies in a
different subtree.

The executable `PositionRelation` compresses `(Path4)` to the trichotomy
`same`, `independent`, and `nested`.  In the nested case its `outer_path` and
`inner_path` fields retain which of the two strict-prefix orientations holds.
Thus the implementation loses no case even though its discriminator has
three values.

The classification is input-relative.  Note 0086 deliberately does not make
a path into a stable node name, so each nontrivial case below computes the
residual path in the corresponding result proof.

---

## 4. Equal positions

If \(p=q\), deterministic replay of note 0086 gives

\[
\beta_p(D)=\beta_q(D).
\]

The local peak is joined with zero additional steps.

This does not imply equality of the full certificates.  Contracting the same
source at the same path with two different research-local `BetaEventId`
values produces the same proof result but distinct frozen transport records.
Even this degenerate peak therefore demonstrates why proof endpoint equality
must be stated before audit-history coherence.

---

## 5. Independent positions and the Peiffer square

Suppose \(p\perp q\).  Contraction at \(p\) replaces only the subtree rooted
at \(p\) and rebuilds its ancestors without changing premise arities.
Therefore the redex at \(q\) remains at path \(q\).  Symmetrically, the
residual of \(p\) after contracting \(q\) is still \(p\).

The square is

\[
\begin{array}{ccc}
D & \xrightarrow{\ \beta_p\ } & D_p \\
{\scriptstyle\beta_q}\downarrow &&
\downarrow{\scriptstyle\beta_q} \\
D_q & \xrightarrow{\ \beta_p\ } & J_{p,q}.
\end{array}
\tag{Peiffer}
\]

The endpoint equation is exact:

\[
\boxed{
\beta_q(\beta_p(D))
=
\beta_p(\beta_q(D)).
}
\tag{Ind}
\]

### Proof

Induct on the longest common prefix of \(p\) and \(q\).  At their first
divergence the common ancestor must have two premises, hence it is a right-
implication elimination.  One redex is in its function premise and the other
is in its argument premise.  Contracting either side leaves the other premise
unchanged.  Deterministic rebuilding therefore gives the same final

\[
\operatorname E(D_f',D_a').
\]

Rebuild the common outer introduction and elimination frames.  The original
proof was globally checked; each contraction removes authority but introduces
none, so neither rebuilding order can create an occurrence, source, or binder
collision.  This proves the exact proof and ledger equation. \(\square\)

At the boundary-transport level, both composites retire the same two distinct
target authorities and send every other occurrence key to its unique position
in \(\Lambda_{J_{p,q}}\).  Hence their composite survivor partial bijections
are extensionally equal.  The two histories are still not equal: their first
positions, intermediate proofs, and ancestor frames differ.  The Peiffer
2-cell records this commuting square.

---

## 6. Strict nesting: outer redex shape and residual paths

It suffices to treat \(p\prec q\); the case \(q\prec p\) is obtained by
exchanging the names of the two positions.

Let the redex at \(p\) be

\[
R=
\operatorname E
\bigl(\operatorname I_x^b(\pi),\sigma\bigr),
\tag{Outer}
\]

and let \(r\) be the relative path in \(\pi\) from its root to the unique
open target assumption leaf \(x\), as reconstructed by the substitution
trace.  Outer contraction gives

\[
R\longrightarrow_\beta
\operatorname{Sub}_x(\pi,\sigma).
\]

The strict descendant redex has only two top-level locations:

- in the outer body \(\pi\), its path changes from \(p(0,0)u\) to \(pu\);
- in the outer argument \(\sigma\), its path changes from \(p(1)v\) to
  \(prv\).

There is no redex at \(p(0)\), because that node is the outer introduction,
not an elimination.  Any redex below that node is in its unique body premise
and therefore has prefix \(p(0,0)\).  Principal occurrences and binder fields
are not proof children and contribute no further cases.

If the inner redex is contracted first, the outer redex remains at \(p\).
Contextual beta preserves the changed premise's exact conclusion and ordered
open context, and it removes no authority belonging to the other redex.

---

## 7. Nested redex in the outer body

Assume

\[
q=p(0,0)u
\]

and let

\[
\pi\longrightarrow_{\beta,u}\pi_u.
\]

The desired common endpoint is

\[
J_{\mathrm{body}}
=
\operatorname{Sub}_x(\pi_u,\sigma).
\tag{JB}
\]

After inner-first reduction, the outer residual is at \(p\).  After outer-
first reduction, the inner residual is at \(pu\).  Establishing that its
contraction yields `(JB)` requires three subcases.

### 7.1 Off-spine body redex

If the inner path \(u\) and the outer target-leaf path \(r\) are independent,

\[
u\perp r,
\]

then substitution descends along the target spine and reuses the inner-redex
subtree unchanged.  Conversely, inner contraction does not change the target
spine.  Ordinary proof-context interchange gives

\[
\beta_u(\operatorname{Sub}_x(\pi,\sigma))
=
\operatorname{Sub}_x(\pi_u,\sigma).
\tag{OffSpine}
\]

No nested substitution-composition equation is needed in this subcase.

Because \(r\) ends at an assumption leaf and \(u\) selects an elimination,
the only non-independent alternative is \(u\prec r\).  Neither \(r=u\) nor
\(r\prec u\) is possible.

### 7.2 Target in the inner body: `SC-body`

Suppose the redex at \(u\) is

\[
\operatorname E
\bigl(\operatorname I_y^c(\theta),\rho\bigr)
\]

and the outer target \(x\) occurs in \(\theta\).  Its path has the form

\[
r=u(0,0)a.
\]

Inner-first then outer-first yields, inside the surrounding body context,

\[
\operatorname{Sub}_x
\bigl(\operatorname{Sub}_y(\theta,\rho),\sigma\bigr).
\]

Outer-first then inner-first yields

\[
\operatorname{Sub}_y
\bigl(\operatorname{Sub}_x(\theta,\sigma),\rho\bigr).
\]

The required distinct-hole interchange is

\[
\boxed{
\operatorname{Sub}_x
\bigl(\operatorname{Sub}_y(\theta,\rho),\sigma\bigr)
=
\operatorname{Sub}_y
\bigl(\operatorname{Sub}_x(\theta,\sigma),\rho\bigr).
}
\tag{SC-body}
\]

Here \(x\ne y\), the open occurrence \(x\) occurs exactly once in
\(\theta\), and it does not occur in \(\rho\).  All complete occurrence,
source, and binder identities of \(\theta,\rho,\sigma\), except for the
declared holes before their consumption, satisfy one joint V0 freshness
interface.

### 7.3 Target in the inner argument: `SC-arg`

If the outer target \(x\) instead occurs in the inner argument \(\rho\), then

\[
r=u(1)a.
\]

The required nested graft associativity is

\[
\boxed{
\operatorname{Sub}_x
\bigl(\operatorname{Sub}_y(\theta,\rho),\sigma\bigr)
=
\operatorname{Sub}_y
\bigl(\theta,\operatorname{Sub}_x(\rho,\sigma)\bigr).
}
\tag{SC-arg}
\]

Now \(x\) occurs exactly once in \(\rho\) and does not occur in
\(\theta\).  The same joint V0 freshness conditions apply.

Linearity makes these subcases exhaustive: the one open occurrence \(x\)
cannot be present in both premises of the inner elimination.

---

## 8. Nested redex in the outer argument

Assume

\[
q=p(1)v,
\qquad
\sigma\longrightarrow_{\beta,v}\sigma_v.
\]

The inner-first branch leaves the outer redex at \(p\) and reaches

\[
J_{\mathrm{arg}}
=
\operatorname{Sub}_x(\pi,\sigma_v).
\tag{JA}
\]

The outer-first branch grafts \(\sigma\) exactly once at the target-leaf path
\(r\).  Therefore the inner redex has the single residual path \(rv\) in the
contractum, globally \(prv\).  The necessary naturality equation is

\[
\boxed{
\beta_{rv}
\bigl(\operatorname{Sub}_x(\pi,\sigma)\bigr)
=
\operatorname{Sub}_x(\pi,\sigma_v).
}
\tag{GraftNat}
\]

This is functoriality of ordered substitution in its replacement proof.  It
is not an assertion that substitution certificates are equal.  On the left,
the inner event is replayed after grafting and has different ancestors and a
different global path; on the right, it is replayed before the outer event.

If a future calculus duplicates or discards the replacement, the one redex
at \(v\) may have several residuals or none.  `GraftNat` and the one-step
strong diamond are therefore specifically linear results.

---

## 9. Ordered substitution-composition lemma

The two equations used above should be packaged as one strengthened theorem,
not reproved ad hoc inside local confluence.

### Theorem 9.1: linear ordered two-hole composition

Let the displayed substitutions be well typed and let every input proof be
checked.  Assume each declared target is one exact open context and ledger
hole, distinct declared targets have distinct full nominal identities, and
all non-target occurrence, source, and binder identities satisfy one joint
V0 freshness condition.

Then:

1. when \(x\) and \(y\) are distinct holes of \(\theta\), with \(x\) absent
   from \(\rho\), equation `(SC-body)` holds as exact checked-proof equality;
2. when \(y\) is a hole of \(\theta\) and \(x\) is a hole of its replacement
   \(\rho\), equation `(SC-arg)` holds as exact checked-proof equality; and
3. substitution is compatible with a contextual beta step in its replacement
   by `(GraftNat)`.

The corresponding ordered ledger identities are

\[
\operatorname{splice}_x
\bigl(
  \operatorname{splice}_y(\Lambda_\theta,\Lambda_\rho),
  \Lambda_\sigma
\bigr)
=
\operatorname{splice}_y
\bigl(
  \operatorname{splice}_x(\Lambda_\theta,\Lambda_\sigma),
  \Lambda_\rho
\bigr)
\tag{LSC-body}
\]

in the distinct-hole case, and

\[
\operatorname{splice}_x
\bigl(
  \operatorname{splice}_y(\Lambda_\theta,\Lambda_\rho),
  \Lambda_\sigma
\bigr)
=
\operatorname{splice}_y
\bigl(
  \Lambda_\theta,
  \operatorname{splice}_x(\Lambda_\rho,\Lambda_\sigma)
\bigr)
\tag{LSC-arg}
\]

in the nested-replacement case.

These are ordered tuple-splice equations, not multiset equalities.  Their
proof uses the discharge--splice law already isolated in note 0085:

\[
D_{y,c}
\bigl(
  \operatorname{splice}_x(\Lambda,\Lambda_\sigma)
\bigr)
=
\operatorname{splice}_x
\bigl(D_{y,c}(\Lambda),\Lambda_\sigma\bigr),
\qquad x\ne y.
\tag{DS}
\]

### Proof

Induct on the first proof containing the relevant hole or holes.  At an
assumption, the equation is the corresponding identity or one tuple-splice
calculation.  Under implication introduction, use `(DS)` and rebuild with the
same principal occurrence and binder.  Under elimination, linearity places
each target in exactly one premise; apply the induction hypothesis in that
premise and reuse the other.  Deterministic elimination reconstruction and
joint freshness give the same proof, context, and complete ledger on both
sides.  `GraftNat` is the analogous induction following the unique target
spine and then the contextual path inside the once-grafted replacement.
\(\square\)

This theorem needs proof-tree trace equations in a promoted certificate:
which target spine was followed, which sibling was reused, and how a path
inside a replacement becomes \(rv\).  Exact proof equality alone does not
retain those audit facts.

---

## 10. One-step strong diamond and local confluence

### Theorem 10.1: strong diamond for beta-like \(\mathrm{TND}_0\)

Let \(D\) be a finite checked \(\mathrm{TND}_0\) proof.  Suppose

\[
D\longrightarrow_{\beta,p}D_p,
\qquad
D\longrightarrow_{\beta,q}D_q.
\]

Then either \(D_p=D_q\), or there is a checked proof \(J\) such that

\[
D_p\longrightarrow_\beta J,
\qquad
D_q\longrightarrow_\beta J.
\]

Moreover, when a completion step is required, its residual position is
exactly the one listed in Sections 5--8.

### Proof

Apply `(Path4)`.

- If \(p=q\), deterministic contraction gives \(D_p=D_q\).
- If \(p\perp q\), use the Peiffer square `(Ind)`; the residual positions are
  unchanged.
- If \(p\prec q\), expose the outer redex `(Outer)`.  A body descendant has
  path \(p(0,0)u\) and residual \(pu\).  Use `(OffSpine)`, `(SC-body)`, or
  `(SC-arg)` according to the unique position of the outer target.  An
  argument descendant has path \(p(1)v\) and residual \(prv\); use
  `(GraftNat)`.
- If \(q\prec p\), use the symmetric argument.

Checked-ledger uniqueness makes the two retired targets distinct.  A beta
step removes exactly its own target authority and preserves the other redex.
Thus every stated residual is a checked redex, and each branch reaches the
displayed exact endpoint in at most one additional contraction. \(\square\)

### Corollary 10.2: proof-tree local confluence

The beta-like reduction relation on finite checked \(\mathrm{TND}_0\) proof
trees is locally confluent.

The theorem is stronger than the corollary because it supplies a one-step
join rather than an arbitrary finite join.  The strength is not expected to
survive unrestricted contraction, weakening, shared proof DAGs, recursion,
or future reductions that duplicate or erase beta redexes.

---

## 11. The explicit audit join cell

Proof-tree local confluence does not by itself audit competing histories.  A
research-local join cell for a peak should retain at least the following
data:

\[
\begin{array}{l}
\operatorname{BetaHistoryJoinCell}(D,p,q)=\\[2mm]
\quad(D,\ p,\ q,\ \operatorname{relation}(p,q),\\
\qquad \tau_p:D\to D_p,\quad \tau_q:D\to D_q,\\
\qquad q/p,\quad p/q,\\
\qquad \tau_{q/p}:D_p\to J,\quad
       \tau_{p/q}:D_q\to J,\\
\qquad \text{endpoint equality},\\
\qquad \text{canonical survivor-summary equality},\\
\qquad \text{retired-authority equality},\\
\qquad \text{case witness}).
\end{array}
\tag{CellData}
\]

In a promoted generic cell, a completion transport may be an identity
boundary when \(p=q\).  Its case witness would be one of:

- deterministic same-position replay;
- an independent Peiffer witness;
- an off-spine body witness;
- an `SC-body` certificate;
- an `SC-arg` certificate; or
- a `GraftNat` certificate.

The fixture uses two more concrete records.  `InterchangeCell` carries both
independent residual witnesses and routes.  `NestedCoherenceCell` carries one
of four `NestedShape` values, both residual witnesses, and both routes.  The
four shapes are outer argument, body off-spine, outer target in the inner
body, and outer target in the inner argument.  The same-position case has no
cell record in V0.

The 2-cell boundary is

\[
\boxed{
\tau_{q/p}\circ\tau_p
\quad\Longrightarrow\quad
\tau_{p/q}\circ\tau_q.
}
\tag{2Cell}
\]

Equation `(2Cell)` is the boundary required of a future promoted composition
law.  The fixture does not construct either displayed composite transport.
It replays both routes and compares their canonical source-to-endpoint
summaries.

### 11.1 Deterministic recomputation obligations

A promoted checker for `(CellData)` must recompute rather than trust:

1. checkedness of the common source;
2. the two original redex positions;
3. their prefix relation;
4. both first-step transports;
5. the appropriate residual positions;
6. both completion transports;
7. exact equality of the two final `NDProof` values;
8. equality of final open context and conclusion;
9. equality of the two retired occurrence/source/binder sets;
10. extensional equality of the composite survivor maps on every other
    occurrence key; and
11. the applicable Peiffer, substitution-composition, or graft-naturality
    witness.

The final ledger equality does not license skipping item 10.  It is checked
separately so the cell establishes that the same source authority reaches the
same final position along each history.

The executable replay constructors recompute items 1--10 and the applicable
independent or nested shape.  They replay every step through the 0086
transport checker.  The nested fixture validates the endpoint equations by
route replay; it does not yet package `SC-body`, `SC-arg`, or `GraftNat` as
standalone reusable algebraic certificate types.

These `_check_*` functions are deterministic recomputation using the same
constructors and algorithms that produced the values.  They reject a changed
field when recomputation no longer returns the same frozen record.  They are
not an independent verifier, a second implementation, a formal proof kernel,
or a tamper-proof security boundary.  Passing replay is evidence of internal
fixture consistency only.

### 11.2 Existence, not equality or unique coherence

Theorem 10.1 and the explicit residual formulas construct join data for every
local peak.  The fixture makes the two nondegenerate classes replayable and
calibrates the degenerate same-position endpoint separately.  This remains
an existence and replay result.  The two nondegenerate histories have
different event orders and input-relative paths.  Their routes have different
intermediate proofs, and replay reconstructs different step transports and
ancestor frames.

Nothing here proves:

- that two valid join cells with the same boundary are equal;
- a canonical choice among join cells;
- interchange among three or more independent events;
- Yang--Baxter, cube, pentagon, or other higher coherence;
- associativity or unitality of history composition as a promoted API; or
- invariance under event renaming, proof-node rebasing, or proof-version
  replacement.

Those obligations appear only after nominal histories and cell composition
are defined.  They cannot be inferred from endpoint confluence.

---

## 12. Global proof-tree confluence and beta normal forms

Note 0086 proves strong normalization using

\[
\mu(D)=\operatorname{dchg}(\Lambda_D),
\qquad
D\to_\beta D'\Longrightarrow \mu(D')=\mu(D)-1.
\]

Theorem 10.1 supplies local confluence.  Newman's lemma therefore yields:

### Theorem 12.1: global proof-tree confluence

If

\[
D\longrightarrow_\beta^*P,
\qquad
D\longrightarrow_\beta^*Q,
\]

then there is a checked proof \(J\) such that

\[
P\longrightarrow_\beta^*J,
\qquad
Q\longrightarrow_\beta^*J.
\]

### Corollary 12.2: fixed-source unique beta normal form

Every finite checked \(\mathrm{TND}_0\) proof has one exact structural beta
normal form reachable from that proof.

The qualifier **fixed-source** is essential.  The corollary does not say that
all proofs of one sequent are equal, that beta-equivalent presentations have
stable nominal identity, or that semantic equality implies proof equality.
It also does not produce a unique normalized history.  Several distinct
histories may terminate at the same normal proof.

Newman's lemma is a theorem about a one-dimensional reduction relation.  It
does not manufacture audit 2-cells, prove equality of composite histories,
or supply higher-dimensional coherence.  Local cells must be explicitly
composed and their coherence proved separately if the audit layer is to be
promoted.

The executable companion compares leftmost and rightmost normalization on the
independent and four base nested peak families, including deep outer
whiskering.  Equal normal endpoints and composites support the corollary on
those fixtures.  They do not mechanize Newman's lemma, enumerate every finite
checked proof, or replace the mathematical local-confluence and strong-
normalization argument.

---

## 13. Observer quotients remain downstream

The present order of construction is

\[
\text{checked proof trees}
\longrightarrow
\text{checked beta transports}
\longrightarrow
\text{replayable history cells}
\longrightarrow
\text{possible observer quotient}.
\]

No arrow may be reversed by declaration.  Before quotienting histories or
proofs, a future observer must specify which of the following descend:

- conclusion and ordered open context;
- complete current ledger or a declared projection of it;
- survivor authority and retirement facts;
- provenance and event identity;
- residual positions or stable node identities;
- substitution and beta replay; and
- composition of 2-cells.

Proof endpoints that are equal need no quotient to be equal in the current
structural fixture.  Histories that reach those endpoints are not thereby
identified.  An observer-relative quotient is therefore a later theorem and
API decision, not part of local confluence.

---

## 14. Compactification and the absence of a new ray

For one finite starting proof \(D\), every beta history has length at most

\[
\mu(D)=\operatorname{dchg}(\Lambda_D).
\]

The proof tree has finitely many positions at every stage, so its beta
reduction tree is finitely branching and has bounded depth.  Adding a local
join cell between two already finite histories adds a two-dimensional audit
witness; it does not add a new beta transition, restore a retired record, or
extend either history by an unbounded one-dimensional tail.

Consequently the confluence and 2-cell analysis supplies no new infinite beta
ray, no \(\Omega\)-boundary, and no compactification claim.  A genuinely
unbounded history would require a later extension such as recursion,
nonlinear structural rules, an unbounded proof family, or another reduction
relation.  It cannot be inferred from multiple finite routes to the same
normal endpoint.

---

## 15. Executable calibration boundary

`test_threaded_beta_confluence_calibration.py` now supplies a self-contained
research fixture over the 0084--0086 operations.  It calibrates:

- validation of proof paths and the same/independent/nested trichotomy, with
  both nested orientations retained as outer and inner paths;
- deterministic same-position proof endpoints and composite summaries under
  distinct audit event labels, while the histories remain unequal;
- replayable `InterchangeCell` Peiffer squares for independent positions;
- replayable `NestedCoherenceCell` values for outer argument, body off-spine,
  outer target in the inner body, and outer target in the inner argument;
- the independent, ancestor, body-projection, and argument-graft residual
  classes, including a prefixed graft with nonempty \(r\) and \(v\);
- exact common `NDProof` endpoints and equal frozen composite boundary
  summaries, rather than sequent equality alone;
- equality of retired authority sets and survivor partial bijections;
- exact per-step and two-step node, ledger, and discharged-use descent;
- whiskering through outer introduction and both elimination premises;
- deep alternating contexts without endpoint or residual-path drift;
- acceptance of a checked empty history as the exact identity route, while an
  unchecked source cannot obtain an identity route;
- rejection of duplicate event IDs, wrong exact nominal/container/index
  types, and forged corners, paths, authorities, survivor maps, histories,
  nested shapes, or residual witnesses; and
- leftmost and rightmost normalization with equal exact beta-normal endpoints
  and composites but unequal histories.

This is executable research calibration, not a promoted production API.  The
fixture replays representative constructors through the calibrated generated
depths, but it is not an exhaustive generator of all finite checked proofs.
Its direct composite summary is not a binary transport-composition API, and
its normalization comparisons do not mechanize Newman's lemma.
The empty route is a checked identity special case; without binary
composition it does not establish a promoted left- or right-unit law.

The finite factories and leftmost/rightmost strategy runs are examples that
exercise the declared cases.  No finite test collection proves Theorems 9.1,
10.1, or 12.1 universally.  Those remain mathematical arguments over all
finite checked trees in the stated linear fragment.  Likewise, the forged-
field cases calibrate deterministic rejection; they do not establish an
independent or adversarial verifier.

---

## 16. Established and deferred boundary

### Established at the research-local proof-tree level

- the four-way prefix classification `(Path4)`;
- exact residual paths for independent, body-nested, and argument-nested
  redexes;
- the independent Peiffer endpoint square;
- the ordered `SC-body`, `SC-arg`, and `GraftNat` obligations;
- a one-step strong diamond under the current linearity and freshness
  discipline;
- local confluence of beta-like finite \(\mathrm{TND}_0\) proof trees;
- global proof-tree confluence by strong normalization and Newman's lemma;
- one exact beta normal form for each fixed starting proof tree; and
- existence of a replay specification for one local history join cell.

### Executably calibrated by the Python fixture

- typed beta authorities, event-labelled histories, routes, residual
  witnesses, and canonical composite boundary summaries;
- checked empty histories and routes as exact identities, with unchecked
  identity sources rejected;
- exact nonempty typed event identifiers, route-local injectivity, and
  distinct cell-event identifiers, without global event allocation;
- same-position endpoint and composite equality with history inequality;
- replayable independent `InterchangeCell` values;
- replayable nested `NestedCoherenceCell` values for all four linear shapes;
- residual authority and path preservation through shallow and deep contexts;
- explicit outer-argument graft transport with nonempty \(r\) and \(v\);
- replay through introduction and both elimination-premise frames;
- exact endpoint and composite equality for both routes;
- exact two-event retirement and reduction measures;
- deterministic replay rejection of the forged fields listed in Section 15;
  and
- agreement of calibrated leftmost and rightmost beta-normal endpoints.

### Deferred

- a single promoted `BetaHistoryJoinCell` covering same-position identity
  cells together with independent and nested cells;
- standalone reusable certificates for `SC-body`, `SC-arg`, and `GraftNat`;
- stable nominal `ProofNodeId`, `ProofVersionId`, and globally allocated
  `BetaEventId` values;
- a promoted transport-composition operation and its unit and associativity
  laws;
- uniqueness or canonicality of audit 2-cells;
- coherence for cubes, braids, associators, or arbitrary finite histories;
- event renaming and proof-node rebasing theorems;
- any observer quotient identifying proofs, transports, histories, or cells;
- alpha-renaming, scope rebasing, source transfer, and aperture filling;
- shared DAGs, contraction, weakening, recursion, and other nonlinear rules;
- eta and commuting or permutative conversions;
- proof-relevant quantifiers and eigenvariable transport;
- explicit cuts and a full cut-elimination theorem;
- term syntax, capture-avoiding term substitution, evaluation contexts, and a
  runtime Church--Rosser theorem; and
- compactification or \(\Omega\) claims for genuinely unbounded histories.

The next audit obligation is not another proof-tree normalization theorem.
It is to promote the local replay vocabulary, define actual transport and
cell composition, and prove higher coherence without erasing the distinction
between current proof state, composite boundary action, ordered history, and
the cell that relates histories.
