# Bootstrap Zero Rebased: The Six-Port Whole-Cut Kernel

Status: syntax-theory correction and replacement baseline after notes 0095--0100.
This note records the argument that began with the question "why six?" and
reorganizes Bootstrap Zero around one finite whole-cut presentation. It does
not modify the stable Adva language or semantic API.

Notes 0095--0100 remain useful factor-placement records. They are not erased.
Their inventory is now insufficient because it treats several constructions
as adjacent syntax atoms that the later argument relates through one common
finite carrier.

---

## 0. Boundary of the correction

This note remains before semantics. It introduces no evaluator, denotation,
truth relation, transition system, halting predicate, physical energy,
analytic derivative, surreal option recursion, or stable implementation.

Its claim is narrower:

> Under an explicit triadic sustained-threading contract, six is the least
> number of distinct port occurrences in the open stratum, and the line,
> circle, cut, threading, braid, collision, and multi-hole views must be
> presentations of one finite typed ledger.

The qualification is essential. Six is not asserted to be the dimension of
nature, the least carrier for every topology, or the number of independent
braid strands.

---

## 1. The conditional minimality of six

Let the domain-role alphabet be

\[
\mathsf D=\{K,X,t\}.
\]

The triadic cycle has the three unordered role interfaces

\[
KX,\qquad Xt,\qquad tK.
\tag{RoleEdges}
\]

Fix the following formation contract.

1. **Triadic cyclicity.** Each of the three role interfaces occurs once in the
   minimal cycle.
2. **Binary cutting.** A cut creates two distinct, named, cooriented boundary
   ports before any collision quotient.
3. **No silent break.** Every created port is used by a through channel or is
   retained as an explicitly named open hole or residual.
4. **Positive occupancy.** Every port of the minimal closed carrier receives
   at least one degree occurrence.
5. **No implicit contraction.** Sharing, collision, merge, and forgetting do
   not identify two occurrences during the initial allocation.
6. **Carrier duality.** The line and circle readings use the same occurrence
   ledger rather than recounting or manufacturing occurrences.

For a cyclic carrier with \(m\) cuts, binary cutting creates \(2m\) ports. If
\(n\) degree occurrences positively occupy those ports, then

\[
n\geq 2m.
\tag{PortBound}
\]

### Finite minimality theorem

For the triadic carrier, \(m=3\), so

\[
n\geq 6.
\]

Equality is attained by assigning exactly one degree occurrence to each
port. Hence

\[
\boxed{n_{\min}=6}
\tag{SixMinimal}
\]

under the six stated conditions.

The proof is finite counting: the three cuts have disjoint two-element port
fibres in the open stratum, giving six distinct ports; positive occupancy
requires one occurrence per port; the one-per-port allocation is a witness.

This theorem deliberately exposes its failure modes. If a role edge is
removed, a cut is not binary, an empty port is allowed, contraction precedes
allocation, or the topology is not the triadic cycle, another minimum may
result. Variable topology and other \(F_n\) carriers remain visible.

### Collision does not refute the count

A later collision may identify locations while retaining occurrence members
and their multiplicities. Thus

\[
1+1+1+1+1+1
\longrightarrow
2+1+2+1
\longrightarrow
3+3
\tag{CollisionStrata}
\]

changes distinguishable loci but not the degree ledger. Six is the open-stratum
minimum; collided forms are boundary strata of the same presented carrier.

---

## 2. One whole-cut cell, not independent line and circle atoms

The public glyph

```text
<L|R>
```

must be read as one whole-cut cell. The separator is not an operation applied
to two already independent sides. A cut simultaneously presents two local
sides, a continuation skeleton, and the boundary data from which closure may
be formed.

The minimal carrier is a finite record

\[
\mathbb W_6=
(\mathsf D,C,P,O,M,\gamma,H,R),
\tag{WholeSix}
\]

where:

- \(C\) is the three-cut ledger over the role edges;
- \(P\) is the six-port ledger, with two named sides per cut;
- \(O\) is the six distinct initial occurrences and their source lineage;
- \(M\) is a complete through matching or an explicit open-port account;
- \(\gamma\) is a cyclic order on the same ports;
- \(H\) is an ordered hole and alternative ledger; and
- \(R\) is an explicit residual ledger.

The line and circle are two checked projections:

\[
\mathsf{line}:\mathbb W_6\to\mathsf{LineView}_6,
\qquad
\mathsf{circle}:\mathbb W_6\to\mathsf{CircleView}_6.
\tag{CarrierViews}
\]

The line view reads the six occurrences as the endpoints of three continued
through channels. The circle view reads those same occurrences in cyclic
boundary order. Neither projection may rename, copy, discard, or recreate an
occurrence.

This corrects the weaker formulation in which `Line` and `Circle` were merely
two neighboring value constructors. They remain distinguished value shapes,
but their six-port instances are now required to descend from one ledger.

---

## 3. Duality, polarity, and conjugation

Three syntactic categories of reversal must remain separate.

| constructor | changes | line reading | circle reading |
|---|---|---|---|
| `dual` \(D\) | carrier presentation | internal flow to boundary order | boundary order to internal flow |
| `polarity` \(P\) | local coorientation | left/right sign | inside/outside sign |
| `conjugate` \(J\) | motion orientation | forward/backward | clockwise/counterclockwise |

`L`/`R`, incidence polarity `+`/`-`, and motion orientation
`forward`/`reverse` are therefore three disjoint alphabets. A local
coorientation witness relates the two sides of one cut to opposite polarity
marks; there is no permanent global equation `L = +`.

Duality transports polarity and conjugation between carrier readings. The
transport must be explicit:

\[
D\circ P\;\Rightarrow\;P_D\circ D,
\qquad
D\circ J\;\Rightarrow\;J_D\circ D.
\tag{TransportWitnesses}
\]

The arrows are named coherence witnesses, not raw definitional equalities.
Their exact signs depend on the chosen local coorientation. Bootstrap Zero
must not identify duality with additive inverse, polarity reversal, or motion
reversal.

A cut presents both polar sides at once. A later additive observation may
assign cancelling signs, but the raw syntax retains both sides.

---

## 4. Cut, generation, retraction, and traversal

The richer cut grammar contains a split pair

\[
B\xrightarrow{g}E\xrightarrow{r}B
\tag{SplitPair}
\]

and an explicit split witness whose typed boundary is

\[
r\circ g\Rightarrow 1_B.
\tag{SplitWitness}
\]

The other composite is retained as a named projector presentation

\[
e:=g\circ r:E\to E.
\tag{ProjectorPresentation}
\]

Bootstrap Zero does not equate \(e\) with \(1_E\). Repeating the projector may
later receive an idempotence witness, but raw occurrences and residuals remain
present.

The two directions have different grammatical roles:

- `generate` includes cutting, distinction, and expansion;
- `retract` includes merge, forgetting, and return to a generative skeleton.

Merge, forgetting, dissipation, and retraction are not synonyms. Merge is a
local incidence operation. Retraction has the split boundary above.
Forgetting declares a retained fibre and residual. Dissipation would require
a later grading along history.

Traversal is derived rather than primitive. Given two presentations over one
compatible skeleton,

\[
B\xrightarrow{g_i}E_i\xrightarrow{r_i}B,
\qquad
B\xrightarrow{g_j}E_j\xrightarrow{r_j}B,
\]

define its factorization record by

\[
\boxed{T_{i\to j}:=g_j\circ r_i.}
\tag{TraversalFactorization}
\]

A thread therefore preserves enough structure to regenerate the next local
presentation; it need not preserve every local distinction.

---

## 5. Braid history and collision strata

Six port occurrences do not imply six independent strands. In the minimal
closed matching there are three through channels. After choosing a linear
cut, ordinary three-strand braid words supply a routing presentation. On the
circle, a cyclic rotation and three local gap positions supply the annular or
affine reading.

The raw braid layer retains:

- complete typed incidence records;
- crossing sign separately from incidence polarity;
- written word order;
- endpoint return separately from raw-word identity; and
- a formal inverse spelling separately from a cancellation equation.

The collision layer is new. A collision record

\[
\mathsf{collide}[\xi;p_1,\ldots,p_k\Rightarrow\lambda]
\tag{Collision}
\]

places several compatible ports at one locus \(\lambda\) while retaining the
ordered or multiset member ledger. It may reduce the number of loci, but it
cannot silently delete an occurrence or its multiplicity.

Opposite polarities at one locus are not the empty syntax object. Any later
cancellation is an interpreter result with an explicit witness.

Bootstrap Zero needs typed raw braid and collision formation. It does not yet
choose a full inverse-braid, singular-braid, tangle, cactus, or compactification
equational theory. Those are visible extension choices.

---

## 6. Holes, addition, multiplication, and history

Three composition forms remain distinct.

1. \(A\oplus B\): parallel juxtaposition or additive allocation;
2. \(A\otimes B\): structural substitution of a complete inner presentation
   into each declared outer hole;
3. \(g\circ f\): ordered historical composition of compatible morphisms.

Under a later finite-count observation,

\[
|F_m\oplus F_n|=m+n,
\qquad
|F_m\otimes F_n|=mn.
\]

These equalities explain the arithmetic shadow; they are not Bootstrap Zero
evaluation rules. In particular,

\[
6=3\times2
\]

records three cuts with two ports each, while

\[
n_K+n_X+n_t=6
\]

records an additive distribution of the retained degree ledger.

The central coordination candidate is distributivity:

\[
A\otimes(B\oplus C)
\Rightarrow
(A\otimes B)\oplus(A\otimes C).
\tag{DistributivityWitness}
\]

It must be witnessed by exact hole bindings, occurrence production, and
thread ledgers. It is not an arithmetic equality in raw syntax.

### Zero is not raw collapse

The following must remain distinct raw forms:

\[
0_{\varnothing},
\qquad
0_{\varnothing}\otimes E,
\qquad
E\oplus E^{\#},
\tag{ZeroForms}
\]

where \(E^{\#}\) is a separately constructed polar-dual presentation. A later
interpreter may map more than one of them to a zero value. Bootstrap Zero
preserves their expression, occurrence, and history fibres.

Thus absorption and polar cancellation are possible extension witnesses, not
definitional equations of the object language.

---

## 7. The relative initiality of the six-port carrier

Let \(F_6\) be the freely named open-stratum six-port presentation satisfying
the minimal contract. Braid, collision, gluing, hole filling, and forgetting
may produce presentations

\[
q:F_6\to M.
\]

Existence of such a morphism does not make \(F_6\) an initial object in an
unmarked model category: several braid or collision histories may give
distinct maps to the same target.

In the category of presented models whose objects are pairs \((M,q)\), with
morphisms preserving the chosen presentation, \((F_6,1_{F_6})\) is initial by
construction. The correct claim is therefore relative initiality, not a
universal dimension claim.

Other \(F_n\), noncyclic connection graphs, nonbinary cuts, and continuous
degree carriers remain legitimate extension families.

---

## 8. What is hard, what is conditional, and what is deferred

| status | factors |
|---|---|
| hard kernel | typed names; three roles; whole cut; six-port open ledger; explicit holes and residuals; line/circle projections; distinct dual/polarity/conjugation alphabets; raw braid and collision records; `generate`, `retract`, and factored traversal; distinct `oplus`, `otimes`, and historical composition |
| coordination obligations | carrier-view occurrence preservation; split witness typing; dual transport witnesses; braid and collision ledger preservation; distributivity ledger; five interpreter-declaration projections |
| finite calibrations | seven unordered distributions of six among three roles when zero allocations are admitted; the 128 Boolean supports if they are predicates on those seven types; candidate ground and excited classes |
| deferred extensions | other arities and topologies; a chosen collision/braid quotient; characteristic grading and physical energy; multi-observer communication; proof and learning rules; Omega nonclosure; arithmetic and surreal semantics |

The seven distribution types follow from the partitions of six into at most
three nonnegative parts:

\[
(6,0,0),(5,1,0),(4,2,0),(3,3,0),
(4,1,1),(3,2,1),(2,2,2).
\]

Their relation to seven halting states or to \(2^7=128\) Boolean predicates is
not part of the minimality theorem. Those identifications need separate
judgments.

---

## 9. Visible extension discipline

Bootstrap Zero is intentionally open, but an extension must be visible. Each
extension declaration must state:

1. which new constructor or index family it adds;
2. which existing names and occurrence ledgers it consumes and returns;
3. whether it adds raw forms, formation rules, coherence witnesses, an
   interpreter, or semantic equations;
4. which old judgments it promises to preserve;
5. which counterexample or `Unknown` outcome prevents overclaiming; and
6. whether it is research-only or proposed for stable promotion.

The initial extension slots are:

```text
arity       topology       collision-theory
character   interpreter    equation
observer    proof          learning
omega       arithmetic     physical
```

An extension may populate a slot without changing the raw identity relation
of the hard kernel. Conservative extension is a proof obligation, not a label.

---

## 10. Revised Bootstrap Zero target

The target theorem is now:

> Every accepted six-port whole-cut package has one finite occurrence and
> multiplicity ledger. Its line, circle, three domain, thread-machine, and
> multi-hole add--multiply projections preserve that ledger; duality,
> polarity, conjugation, generation, retraction, braid, and collision remain
> typed and distinct; every hole, alternative, collision member, and residual
> is accounted for; and no semantic equality or physical interpretation is
> required.

The completion order is:

1. define and validate the six-port whole-cut carrier;
2. derive line and circle views from it;
3. type duality, polarity, conjugation, split pairs, and traversal;
4. add braid-preserving and collision-preserving ledgers;
5. coordinate holes, addition, multiplication, and historical composition;
6. derive the five interpreter declarations from the common carrier; and
7. prove the finite formation and preservation theorem with negative fixtures.

This is the corrected starting point for implementation. The earlier
circle/Omega/closure seam becomes one later calibration, not the first
foundation of Bootstrap Zero.
