# Focused Normal Forms, Subformula Property, and Decidable Derivability

Status: research-local object-level theorem and executable calibration
following
[0084](0084-threaded-natural-deduction-entailment-cell.md),
[0085](0085-ordered-substitution-cut-beta-ledger-boundary.md),
[0086](0086-contextual-beta-ledger-transport-strong-normalization.md), and
[0093](0093-beta-history-local-confluence-audit-2-cells.md)

This note closes the next object-level boundary of the finite
\(\mathrm{TND}_0\) fragment.  It identifies the formula-and-proof skeleton as
the associative, empty-antecedent, right-residual fragment of ordered linear
natural deduction; characterizes beta-normal proofs by mutually inductive
normal and neutral forms; proves the beta-normal subformula property and
canonical-form lemmas; and derives a terminating, sound, and complete focused
decision procedure for derivability.

The word **beta** continues to mean the proof-level contraction

\[
\operatorname E
  \bigl(\operatorname I_x^b(\pi),\sigma\bigr)
\longrightarrow_\beta
\operatorname{Sub}_x(\pi,\sigma)
\]

from notes 0085--0093.  This note introduces no eta reduction or equality.
It uses eta-shaped expansion only as a type-directed, derivability-preserving
discipline for selecting focused proof presentations.  In particular,

\[
f
\qquad\text{and}\qquad
\lambda^R x.\operatorname{app}^R(f,x)
\]

are not identified here.

No stable Adva logical symbol, proof-term AST, focused-search API, failure
certificate, alpha-renaming operation, quotient, or Rust type is introduced.
All erasure, decoration, normal-form, and search constructions in this note
are research-local specifications over the checked Python proof trees.

---

## 0. Executive result

Let the formula skeleton be

\[
A,B ::= p \mid A\multimap_R B,
\qquad
p\in\{P_K,P_X,P_t\},
\]

and let a context be a finite ordered word, including the empty word.  After
erasing nominal audit data, the rules of \(\mathrm{TND}_0\) are exactly

\[
\frac{\ }{x:A\vdash x:A}\;(\mathrm{Ax}),
\]

\[
\frac{\Gamma\circ x:A\vdash M:B}
     {\Gamma\vdash\lambda^R x.M:A\multimap_R B}
\;(\multimap_R I),
\]

and

\[
\frac{\Gamma\vdash F:A\multimap_R B
\qquad
\Delta\vdash N:A}
{\Gamma\circ\Delta\vdash\operatorname{app}^R(F,N):B}
\;(\multimap_R E).
\]

Under the usual Lambek notation, \(A\multimap_R B\) has the orientation
\(B/A\), because it is characterized by the right-residuation pattern

\[
\Gamma\circ A\vdash B
\quad\Longleftrightarrow\quad
\Gamma\vdash B/A.
\]

The contexts are associative words, and the rules do not install exchange,
weakening, or contraction.  Empty contexts are admitted.  The skeleton is
therefore the natural-deduction presentation of the right-division fragment
of the associative empty-antecedent Lambek calculus, commonly written the
\(L^*\) \(/\)-fragment, rather than Lambek's original
nonempty-antecedent \(L\).

The exact checked calculus is not definitionally identical to that
skeleton.  It additionally retains task, provenance, source, occurrence,
scope, binder, domain, status, and ledger data.  The relation is instead
expressed by two theorems:

\[
\boxed{
\text{checked decoration}
\xrightarrow{\ \operatorname{erase}\ }
\text{right-residual skeleton}
}
\tag{Erase}
\]

and

\[
\boxed{
\text{right-residual derivation}
\xrightarrow{\ \operatorname{decorate}_{\mathrm{fresh}}\ }
\text{some checked decoration}.
}
\tag{Lift}
\]

Consequently, at the level of existence of a proof,

\[
\Gamma\vdash_{\mathrm{TND}^{\mathrm{sk}}_0}A
\quad\Longleftrightarrow\quad
\text{some fresh checked decoration of }\Gamma\vdash A\text{ exists}.
\tag{Der-Eq}
\]

This is not equality of proof objects.  The lift is deliberately
noncanonical: there are many globally fresh nominal decorations of one
skeleton proof.

Every beta-normal skeleton proof has one of the mutually inductive shapes

\[
\begin{aligned}
N&::=\lambda^R x.N\mid R,\\
R&::=x\mid\operatorname{app}^R(R,N).
\end{aligned}
\tag{NN}
\]

It follows that every formula occurring in a beta-normal derivation is a
subformula of its conclusion or of one of its open assumptions.  Closed
normal proofs of atomic formulae do not exist; closed normal proofs of
right-implication formulae end in introduction; and atomic normal proofs are
neutral spines headed by the leftmost open assumption.

A type-directed long-form operation then chooses an introduction at every
right-implication goal without declaring eta equality.  Reading those long
forms backwards gives a finite focused search.  If the goal is an
implication, search introduces its argument at the right boundary.  If the
goal is atomic, search must focus on the leftmost assumption, follow its
unique right-residual spine, and partition the remaining context into
contiguous argument blocks.  Empty blocks are allowed because the calculus
admits closed arguments.

The total number of \(\multimap_R\) occurrences in a sequent strictly
decreases along every recursive search call.  Formula comparison and the
set of contiguous partitions are finite.  Search therefore returns either:

1. a well-typed focused skeleton derivation with a fresh checked lift; or
2. a complete finite failure tree covering every possible focused branch.

Soundness and completeness yield

\[
\boxed{
\operatorname{Focus}(\Gamma,A)=\operatorname{success}
\quad\Longleftrightarrow\quad
\Gamma\vdash_{\mathrm{TND}^{\mathrm{sk}}_0}A.
}
\tag{Focus-Dec}
\]

Thus derivability in the present finite right-residual fragment is
decidable.  A complete focused failure proves nonderivability in this
fragment.  It is neither a Boolean countermodel nor an \(\Omega\)-boundary.

---

## 1. Dependency boundary

The proof uses four earlier results.

1. Note 0084 defines checked \(\mathrm{Ax}\),
   \(\multimap_R I\), and \(\multimap_R E\), ordered contexts, and the
   complete resource ledger.
2. Note 0085 proves ordered one-hole proof substitution under the strict
   V0 freshness conditions.
3. Note 0086 proves contextual beta subject reduction and strong
   normalization for every finite checked proof tree.
4. Note 0093 proves local and global confluence of the beta proof-tree
   relation and one exact beta-normal endpoint for every fixed checked
   starting proof.

The new dependency graph is

\[
\begin{array}{c}
\text{checked rules}
\longrightarrow
\text{skeleton erasure and fresh lift}
\\[1mm]
\text{beta strong normalization}
\longrightarrow
\text{normal/neutral existence}
\\[1mm]
\text{normal/neutral characterization}
\longrightarrow
\text{subformula and canonical forms}
\\[1mm]
\text{canonical forms}
+
\text{long-form admissibility}
\longrightarrow
\text{focused completeness}
\\[1mm]
\text{focused soundness}
+
\text{focused completeness}
+
\text{termination}
\longrightarrow
\text{decidable derivability}.
\end{array}
\tag{Deps}
\]

Beta confluence is useful for the surrounding normalization theory, but
focused derivability does not require the stronger claim that all proofs of
one sequent are equal.  They generally are not.

The following results are not dependencies of this note:

- an eta reduction, eta equality, or beta-eta confluence theorem;
- an explicit sequent calculus with cuts or Gentzen cut elimination;
- transport composition or coherence between beta histories;
- completeness for Boolean, resource, categorical, or geometric semantics;
- any proof-relevant quantifier rule; and
- any unbounded scheduler or compactification.

---

## 2. The formula-and-proof skeleton

### 2.1 Formulae and ordered contexts

The skeleton retains the existing formula constructors and forgets no
logical connective, because the checked fragment already contains only the
three atomic coordinates and right linear implication:

\[
A,B ::= P_K\mid P_X\mid P_t\mid A\multimap_R B.
\]

For the metatheorems, the atomic signature may be any finite decidable set.
The three-coordinate signature is retained in the executable calibration.

A skeleton context is a word

\[
\Gamma=x_1:A_1,\ldots,x_n:A_n.
\]

The displayed variables are local occurrence positions, not retained
nominal authorities.  The executable skeleton stores the formula word
\((A_1,\ldots,A_n)\); equal formulae at two positions remain two distinct
linear positions.

Concatenation is strictly associative at this syntactic level and has the
empty word as unit.  No permutation, deletion, or duplication of entries is
implicit.

The right-spine decomposition of a formula is unique:

\[
F =
A_1\multimap_R
 \bigl(A_2\multimap_R
  \cdots
   (A_k\multimap_R q)\cdots\bigr),
\tag{Spine}
\]

where \(q\) is atomic and \(k\geq0\).  Write

\[
\operatorname{spine}(F)=([A_1,\ldots,A_k],q).
\]

This decomposition is syntactic.  It uses no associativity equation for
\(\multimap_R\).

### 2.2 Skeleton proof terms

The proof-term skeleton is

\[
M,N ::= x
\mid\lambda^R x.M
\mid\operatorname{app}^R(M,N).
\]

The three typing rules are precisely those displayed in Section 0.  The
introduction premise must end in the discharged right-boundary occurrence.
The elimination conclusion concatenates the function context before the
argument context.  These two orientations are the reason that
\(\multimap_R\) is the right residual.

There is no general rule

\[
\Gamma,x:A,\Delta\vdash x:A
\]

and no rule that changes \(\Gamma,\Delta\) into \(\Delta,\Gamma\).  The only
assumption rule has singleton context.  Each open assumption is consequently
used exactly once.

### 2.3 Exact Lambek classification

At the skeleton level the calculus has:

- associative ordered contexts;
- a single right division \(B/A\);
- no product formula;
- no left division;
- no exchange, weakening, or contraction; and
- an admitted empty antecedent.

It is therefore safer to call it the **natural-deduction presentation of the
associative \(L^*\) right-division fragment** than to call it either full
Lambek calculus or ordinary intuitionistic linear logic.  Equivalence with a
future Gentzen \(L^*\) sequent presentation additionally requires
translations involving the right-division left rule and explicit cut; it is
not asserted here.

Because there is no formula-level product or unit, the most direct
proof-relevant algebraic target would be a nonsymmetric right-closed
multicategory rather than a monoidal category whose tensor is already
internal to the formula language.  No such semantic completeness theorem is
claimed in this note.

---

## 3. Erasure of checked decorations

### 3.1 Erasure operation

For a recursively checked \(\mathrm{TND}_0\) proof \(D\), define
\(|D|\) by structural recursion.

- An audited assumption becomes the corresponding skeleton variable.
- An audited introduction becomes \(\lambda^R x.|D_0|\).
- An audited elimination becomes
  \(\operatorname{app}^R(|D_1|,|D_2|)\).

Erasure removes:

- task and provenance identities;
- resource-source and domain identities;
- occurrence and scope identities;
- binder identities;
- open and discharged ledger status;
- complete ledger records; and
- cached checker fields.

It retains:

- every formula;
- the ordered open context;
- the proof-tree constructor;
- the forced right-boundary discharge constructor and its formula; and
- the function-before-argument orientation.

In particular, context erasure is the word map

\[
\left|
 h_1:A_1,\ldots,h_n:A_n
\right|
=
(A_1,\ldots,A_n).
\]

It preserves order, multiplicity, and the empty word; it is not a set or
multiset projection.

Erasure is an observer declared only for the object-level derivability
theorem.  It does not assert that the removed records are meaningless to an
audit observer.

### 3.2 Theorem 3.1: erasure soundness

If

\[
D:
\Gamma\vdash_K A\blacktriangleright\Lambda
\]

passes the recursive \(\mathrm{TND}_0\) checker, then

\[
|\Gamma|\vdash |D|:|A|
\]

is a well-formed right-residual skeleton derivation.

#### Proof

Proceed by structural induction on the checked proof tree.

For an assumption, recursive checking requires a singleton open context, so
the skeleton \(\mathrm{Ax}\) rule applies.

For an introduction, recursive checking proves that the selected occurrence
is the unique open right-boundary occurrence of the premise and that its
formula is the implication domain.  After erasure, this is exactly the
\(\multimap_R I\) premise.

For an elimination, recursive checking proves the premise formula match and
the exact left-to-right concatenation of the two open contexts.  Source,
occurrence, scope, and binder disjointness disappear under erasure, while the
skeleton \(\multimap_R E\) premises and conclusion remain.  This completes
the induction.  \(\square\)

Erasure also commutes with the underlying proof result of checked
substitution and beta contraction:

\[
\left|\operatorname{Sub}_x(D,E)\right|
=
\operatorname{Sub}_x(|D|,|E|)
\tag{Erase-Sub}
\]

and

\[
D\longrightarrow_\beta D'
\quad\Longrightarrow\quad
|D|\longrightarrow_\beta|D'|.
\tag{Erase-Beta}
\]

These equations concern proof-tree endpoints.  They do not erase the
substitution or beta certificate from an audit history by fiat.

---

## 4. Fresh decoration lifting

### 4.1 Decoration policy

Let \(d\) be a finite skeleton derivation.  Its proof tree has finitely many
assumption leaves and introduction nodes.  A boundary decoration assigns
checked, pairwise compatible hypothesis occurrences to the ordered open
context positions of \(d\).  Equal formulae at two positions still receive
two distinct occurrences.

Retain the supplied authorities on those open positions.  For every internal
leaf that will be discharged, choose one globally fresh occurrence, source,
scope, and provenance identity.  Choose one globally fresh binder identity
for every introduction node and any admitted domain for each fresh source.

All new choices are disjoint within their nominal sort from the boundary and
from identities already reserved for the task.  Tagged identities of
different sorts need not have different display strings.  Allocation is by
proof-tree occurrence, not by structural equality of subproofs.  Repeated
closed arguments therefore receive disjoint internal authorities.  A
discharged leaf retains its leaf authorities and receives the binder of the
unique introduction that discharges it.  Introduction changes status; it
does not allocate a second copy of the leaf.

Because all leaf source identities are distinct, no shared-source aperture
or source-transfer premise is required.  Because all occurrence, scope, and
binder identities are globally fresh, premise ledgers satisfy the strict V0
disjointness checks.

### 4.2 Theorem 4.1: fresh-decoration lifting

For every finite skeleton derivation

\[
d:\Gamma\vdash A
\]

every valid ordered boundary decoration \(\widehat\Gamma\) of \(\Gamma\),
and every finite set \(S\) of already reserved nominal identities disjoint
from that boundary, there exists a checked decorated derivation

\[
\widehat d:
\widehat\Gamma\vdash_K A
\blacktriangleright\widehat\Lambda
\]

whose newly allocated internal identities are disjoint from both
\(\widehat\Gamma\) and \(S\), and such that

\[
|\widehat d|=d.
\]

#### Proof

Proceed by structural induction on \(d\).

For \(\mathrm{Ax}\), use the supplied boundary occurrence when it is open.
For an assumption internal to a surrounding implication introduction,
allocate one fresh tuple of leaf authorities and build the checked singleton
assumption.

For \(\multimap_R I\), extend the supplied conclusion boundary by one fresh
occurrence of the displayed domain formula, then decorate the premise
recursively.  Allocate a fresh binder, verify that the new occurrence is the
right-boundary leaf, and change exactly that record from open to discharged.

For \(\multimap_R E\), split the supplied boundary decoration at the exact
skeleton context boundary, partition an infinite supply of fresh identities
into two disjoint finite supplies, decorate both premises recursively, and
invoke the checked elimination constructor.  Their complete ledgers and
source sets are disjoint by construction, and their open contexts concatenate
in the skeleton order.

Finiteness of \(d\) ensures that only finitely many fresh identities are
required.  Structural erasure returns the original constructor at every
node.  \(\square\)

### 4.3 Corollary 4.2: derivability equivalence

For every skeleton sequent \(\Gamma\vdash A\) and every valid boundary
decoration \(\widehat\Gamma\) of \(\Gamma\),

\[
\Gamma\vdash_{\mathrm{TND}^{\mathrm{sk}}_0}A
\quad\Longleftrightarrow\quad
\text{some checked proof with exact open context }\widehat\Gamma
\text{ derives }A.
\]

This is an existential theorem over decorations.  It does not say:

- that decorations are unique;
- that two decorations are alpha-equal;
- that nominal identities may be ignored by every observer;
- that a derivation using an intentionally shared source can be replaced by
  a fresh-source derivation without changing its audit meaning; or
- that erasure is faithful on proof histories.

---

## 5. Beta-normal and neutral proofs

### 5.1 Mutually inductive judgments

Write

\[
\Gamma\vdash_{\mathrm{ne}}R:A
\]

for a neutral proof and

\[
\Gamma\vdash_{\mathrm{nf}}N:A
\]

for a beta-normal proof.

Neutral proofs are generated by

\[
\frac{\ }{x:A\vdash_{\mathrm{ne}}x:A}
\]

and

\[
\frac{\Gamma\vdash_{\mathrm{ne}}R:A\multimap_R B
\qquad
\Delta\vdash_{\mathrm{nf}}N:A}
{\Gamma\circ\Delta
\vdash_{\mathrm{ne}}\operatorname{app}^R(R,N):B}.
\]

Normal proofs are generated by

\[
\frac{\Gamma\vdash_{\mathrm{ne}}R:A}
{\Gamma\vdash_{\mathrm{nf}}R:A}
\]

and

\[
\frac{\Gamma\circ x:A\vdash_{\mathrm{nf}}N:B}
{\Gamma\vdash_{\mathrm{nf}}
\lambda^R x.N:A\multimap_R B}.
\]

The grammar retains ordered context splitting in every neutral application.
It does not merely classify untyped tree shapes.

### 5.2 Theorem 5.1: normal/neutral characterization

A well-typed skeleton proof is beta-normal if and only if it is generated by
the mutually inductive judgments above.

#### Proof

Every generated proof is beta-normal: the function premise of every
application is neutral and hence cannot begin with an introduction.

Conversely, inspect the root constructor of a beta-normal proof.  An
assumption is neutral.  An introduction has a beta-normal body and is normal
by induction.  An elimination has beta-normal premises.  Its function
premise cannot be an introduction, because that would form the principal
beta redex.  Repeating the same inversion down the function premise reaches
an assumption head, so the function is neutral; the argument is normal by
induction.  \(\square\)

### 5.3 Corollary 5.2: existence of normal forms

Every finite skeleton derivation has a beta-normal derivation of the same
sequent.

#### Proof

Freshly decorate the skeleton derivation by Theorem 4.1, apply strong
normalization from note 0086, erase the checked beta-normal endpoint, and use
Theorem 5.1.  Subject reduction preserves the exact skeleton sequent.
\(\square\)

Confluence from note 0093 additionally gives one beta-normal endpoint for
each fixed checked source.  This does not make all normal proofs of one
sequent equal.

---

## 6. Beta-normal subformula property

Write \(C\preceq A\) when \(C\) is a syntactic subformula of \(A\), including
\(A\) itself.

### 6.1 Lemma 6.1: neutral-spine subformula lemma

If

\[
\Gamma\vdash_{\mathrm{ne}}R:C,
\]

then the conclusion \(C\), every eliminated domain along the neutral spine,
and every formula occurring in that spine are subformulae of formulae in
\(\Gamma\).  Formulae internal to a normal argument are subformulae of that
argument's open assumptions or of its argument type, and hence of
\(\Gamma\) or of the head-assumption formula.

#### Proof

Use induction on the neutral derivation.

For an assumption, the conclusion is the only context formula.

For an application, the induction hypothesis places
\(A\multimap_R B\), and therefore both \(A\) and \(B\), under a
head-assumption formula in the function context.  The normal-argument
induction places its internal formulae under \(A\) or under its own ordered
context.  Both premise contexts occur unchanged in the conclusion context.
\(\square\)

### 6.2 Theorem 6.2: beta-normal subformula property

If

\[
\Gamma\vdash_{\mathrm{nf}}N:A,
\]

then every formula occurrence in the normal derivation is a subformula of
\(A\) or of a formula in \(\Gamma\).

#### Proof

Proceed by induction on the normal derivation.

The neutral case follows from Lemma 6.1.

For an introduction with conclusion \(B\multimap_R C\), the premise has
boundary \(\Gamma,x:B\vdash C\).  By induction, each premise formula is a
subformula of \(C\), of \(B\), or of a formula in \(\Gamma\).  Both \(B\)
and \(C\) are subformulae of the displayed conclusion.  \(\square\)

The theorem includes formulas on discharged assumption leaves.  Their
ledger records remain in the checked proof tree, but their formulae are
controlled by the implication that discharged them.

### 6.3 Boundary of the theorem

The theorem is about beta-normal proofs in the right-residual fragment.  It
does not yet cover:

- maximal segments created by disjunction or existential elimination;
- commuting or permutative conversions;
- explicit cuts;
- formulae inside a term language for quantifiers;
- source-transfer or aperture-filling evidence; or
- proof-history certificates attached outside the current proof tree.

---

## 7. Canonical forms

### 7.1 Theorem 7.1: closed atomic impossibility

There is no beta-normal skeleton proof

\[
\varnothing\vdash_{\mathrm{nf}}N:p
\]

for an atomic \(p\).

#### Proof

An atomic normal proof cannot end in introduction, so it is neutral.
Every neutral proof has an assumption head and therefore a nonempty open
context.  \(\square\)

### 7.2 Theorem 7.2: closed implication introduction

If

\[
\varnothing\vdash_{\mathrm{nf}}N:A\multimap_R B,
\]

then \(N\) ends in \(\multimap_R I\).

#### Proof

If \(N\) were neutral, it would have an open assumption head.  The context
is empty, so this is impossible.  \(\square\)

### 7.3 Theorem 7.3: atomic head order

If

\[
x_1:F_1,\ldots,x_n:F_n
\vdash_{\mathrm{nf}}N:p
\]

with atomic \(p\), then \(n>0\), \(N\) is neutral, and its head is
\(x_1:F_1\).

#### Proof

The proof is neutral because the conclusion is atomic.  A neutral
application concatenates the function context before every argument
context.  Its assumption head is therefore the first entry of the complete
open context.  \(\square\)

The last theorem is the key focusing fact.  Search does not guess an
arbitrary head assumption.  Ordered elimination forces the leftmost one.

Canonicity is a shape theorem.  It does not say that a sequent has at most
one proof, nor that two proofs with the same outer constructor are equal.

---

## 8. Long focused presentations without eta equality

### 8.1 Long normal and neutral forms

Define type-directed long normal and long neutral judgments mutually.

At an atomic goal, a long normal proof is a long neutral proof:

\[
\frac{\Gamma\vdash_{\mathrm{lne}}R:p}
{\Gamma\vdash_{\mathrm{ln}}R:p}.
\]

At an implication goal, a long normal proof introduces:

\[
\frac{\Gamma\circ x:A\vdash_{\mathrm{ln}}L:B}
{\Gamma\vdash_{\mathrm{ln}}
\lambda^R x.L:A\multimap_R B}.
\]

Long neutral proofs have an assumption head and accept long normal
arguments:

\[
\frac{\ }{x:A\vdash_{\mathrm{lne}}x:A}
\]

and

\[
\frac{\Gamma\vdash_{\mathrm{lne}}R:A\multimap_R B
\qquad
\Delta\vdash_{\mathrm{ln}}L:A}
{\Gamma\circ\Delta
\vdash_{\mathrm{lne}}\operatorname{app}^R(R,L):B}.
\]

Thus a neutral proof of function type may occur as an intermediate spine,
but a completed long normal proof of function type is always an
introduction.

**Skeleton right-invertibility lemma.**  At the level of derivability,

\[
\Gamma\vdash A\multimap_R B
\quad\Longleftrightarrow\quad
\Gamma,A\vdash B.
\tag{Right-Inv}
\]

The reverse direction is the introduction rule.  For the forward direction,
apply the given proof to the singleton assumption proof of \(A\).  This
creates a new derivation; it does not rewrite the original proof.  In a
checked lift, the new occurrence of \(A\) must have fresh source, occurrence,
scope, and later binder authority.  Thus right invertibility preserves the
formula sequent but not a fixed complete ledger.

### 8.2 Theorem 8.1: long-form admissibility

For every beta-normal skeleton proof

\[
\Gamma\vdash_{\mathrm{nf}}N:A
\]

there exists a long normal skeleton proof

\[
\Gamma\vdash_{\mathrm{ln}}\operatorname{Long}_A(N):A.
\]

#### Construction

Proceed by recursion on the goal type together with the normal/neutral
structure.

If the goal is atomic, recursively long-expand every normal argument in the
neutral spine.

If the goal is \(B\multimap_R C\) and \(N\) is already an introduction,
recursively long-expand its body at \(C\).

If the goal is \(B\multimap_R C\) and \(N\) is neutral, choose a fresh
skeleton variable \(x:B\), form the well-typed proof

\[
\Gamma,x:B\vdash\operatorname{app}^R(N,x):C,
\]

long-expand it at \(C\), and introduce \(x\):

\[
\Gamma\vdash
\lambda^R x.
\operatorname{Long}_C
 \bigl(\operatorname{app}^R(N,x)\bigr)
:B\multimap_R C.
\]

When \(B\) is itself an implication, the occurrence \(x:B\) is
long-expanded inside its argument position by the same recursive operation.
Its open context remains the singleton \(x:B\), so the outer application
still places it immediately to the right of \(\Gamma\).

The recursion terminates by the goal type and the finite normal tree.
\(\square\)

The operation is type directed.  It does not repeatedly expand arbitrary
neutral subterms in function position; unrestricted expansion could recreate
beta redexes and would not supply the termination argument used here.

### 8.3 Why this is not eta

The construction proves only

\[
\Gamma\vdash N:A
\quad\Longrightarrow\quad
\Gamma\vdash\operatorname{Long}_A(N):A.
\]

It does not prove

\[
N=\operatorname{Long}_A(N),
\qquad
N\longrightarrow_\eta\operatorname{Long}_A(N),
\]

or the converse reduction.

For example, from

\[
f:A\multimap_R B\vdash f:A\multimap_R B
\]

the focused discipline constructs

\[
f:A\multimap_R B
\vdash
\lambda^R x.\operatorname{app}^R(f,x)
:A\multimap_R B.
\]

The second proof contains a newly introduced and discharged assumption use.
Its decorated ledger is not literally the ledger of the first proof.
Declaring them equal requires a future alpha/eta observer and transport
theorem.

---

## 9. Focused search

### 9.1 Search judgments

Let

\[
\operatorname{Search}(\Gamma,A)
\]

operate on the finite skeleton context and formula.  It returns either a
long normal proof or a replayable complete failure tree.

The search rules are syntax directed.

**Right phase.**  If \(A=B\multimap_R C\), append one fresh skeleton
assumption at the right boundary and search the body:

\[
\operatorname{Search}(\Gamma,B\multimap_R C)
=
\lambda^R x.
\operatorname{Search}(\Gamma\circ x:B,C).
\tag{Focus-R}
\]

The rule is deterministic up to the spelling of the fresh bound variable.
An implementation may use a de Bruijn position or a path-derived local name
so that search itself does not depend on global nominal allocation.

**Atomic phase.**  Let the goal be atomic \(p\).

- If \(\Gamma\) is empty, fail.
- Otherwise write \(\Gamma=x:F\circ\Delta\).
- Compute the unique
  \(\operatorname{spine}(F)=([A_1,\ldots,A_k],q)\).
- If \(q\neq p\), fail.
- Enumerate every contiguous ordered weak partition

  \[
  \Delta=\Delta_1\circ\cdots\circ\Delta_k.
  \tag{Part}
  \]

- For one partition, recursively search

  \[
  \operatorname{Search}(\Delta_i,A_i)
  \qquad(1\leq i\leq k).
  \]

  If all calls succeed, return

  \[
  \operatorname{app}^R
   \bigl(\cdots
    \operatorname{app}^R
     (\operatorname{app}^R(x,L_1),L_2)
    \cdots,L_k\bigr).
  \tag{Focus-A}
  \]

A weak partition allows empty blocks.  This is necessary because an argument
may have a closed proof.  For \(k=0\), the unique zero-block partition exists
only when \(\Delta\) is empty.

### 9.2 Lemma 9.1: neutral-spine inversion

Suppose

\[
x:F\circ\Delta
\vdash_{\mathrm{lne}}R:p
\]

with atomic \(p\), and

\[
\operatorname{spine}(F)=([A_1,\ldots,A_k],q).
\]

Then:

1. \(q=p\);
2. the neutral proof applies the head \(x\) exactly \(k\) times;
3. there is a contiguous ordered weak partition
   \(\Delta=\Delta_1\circ\cdots\circ\Delta_k\); and
4. each argument is a long normal proof
   \(\Delta_i\vdash_{\mathrm{ln}}L_i:A_i\).

#### Proof

By Theorem 7.3 the head is \(x\).  Repeated inversion of the long-neutral
application rule follows the unique result side of \(F\).  Since the final
goal is atomic, the entire right spine must be consumed, and its terminal
atom must be \(p\).  Every application concatenates its argument context
after all preceding contexts, producing exactly the displayed contiguous
partition.  \(\square\)

The lemma is exhaustive.  There is no additional head choice or
noncontiguous allocation hidden from focused search.

---

## 10. Soundness and completeness of focusing

### 10.1 Theorem 10.1: focused soundness

If

\[
\operatorname{Search}(\Gamma,A)
\]

returns a long normal proof \(L\), then

\[
\Gamma\vdash_{\mathrm{ln}}L:A,
\]

and hence \(\Gamma\vdash A\) in the skeleton calculus.

#### Proof

Induct over the successful search record.  A right-phase record applies the
checked skeleton introduction rule to its recursively verified child.  An
atomic-phase record verifies the unique head spine, the exact ordered
partition, every recursive argument proof, and then replays the neutral
elimination spine.  The partition covers the entire suffix exactly once, so
no weakening, contraction, or exchange is introduced.  \(\square\)

### 10.2 Theorem 10.2: focused completeness

If

\[
\Gamma\vdash A
\]

in the right-residual skeleton, then
\(\operatorname{Search}(\Gamma,A)\) has at least one successful branch.

#### Proof

By Corollary 5.2, normalize the derivation to a beta-normal proof.  By
Theorem 8.1, construct a long normal proof of the same sequent.

Proceed by induction on that long proof.  At an implication conclusion, its
last constructor is introduction, so the deterministic right phase follows
its premise.  At an atomic conclusion, Lemma 9.1 identifies the leftmost
head, the unique residual spine, and one of the finitely enumerated
contiguous partitions.  The induction hypothesis supplies success for every
argument block of that partition.  Search therefore visits a successful
branch.  \(\square\)

Completeness uses long-form **existence**, not eta equality.  Focused search
may return a different proof presentation from the beta-normal proof used to
establish its existence.

---

## 11. Termination

Let \(\#_R(A)\) be the number of \(\multimap_R\) occurrences in \(A\), and
define

\[
\mu(\Gamma\Rightarrow A)
=
\sum_{B\in\Gamma}\#_R(B)+\#_R(A).
\tag{Measure}
\]

### 11.1 Lemma 11.1: right-phase descent

The recursive call

\[
(\Gamma\Rightarrow B\multimap_R C)
\longmapsto
(\Gamma,B\Rightarrow C)
\]

decreases \(\mu\) by exactly one.

### 11.2 Lemma 11.2: atomic-phase descent

Suppose

\[
F=A_1\multimap_R\cdots\multimap_R A_k\multimap_R p.
\]

If \(k>0\), every recursive argument sequent

\[
\Delta_i\Rightarrow A_i
\]

has strictly smaller measure than

\[
F,\Delta\Rightarrow p.
\]

Indeed,

\[
\#_R(F)=k+\sum_{j=1}^k\#_R(A_j),
\]

and \(\Delta_i\) is one block of the partition of \(\Delta\).  At least the
outer spine connective leading to \(A_i\) is absent from the child measure.
If \(k=0\), the atomic phase makes no recursive call.

### 11.3 Theorem 11.3: search termination

Focused search terminates on every finite skeleton sequent.

#### Proof

Every recursive call strictly decreases the natural number \(\mu\).
Formula equality and spine decomposition are decidable.  A finite word has
finitely many contiguous weak \(k\)-partitions.  For \(n=|\Delta|\) and
\(k>0\), their number is

\[
\binom{n+k-1}{k-1}.
\]

Thus every node has finite branching and every branch has finite depth.
\(\square\)

The theorem proves termination of this syntax-directed search only.  It is
not a fairness theorem for an unbounded enumerator.

---

## 12. Complete finite failure

### 12.1 Failure constructors

A replayable focused failure tree should distinguish at least:

1. **AtomicEmpty**: an atomic goal with empty context;
2. **TerminalMismatch**: the leftmost head spine ends in \(q\neq p\);
3. **UnusedSuffix**: a zero-argument matching atomic head has a nonempty
   suffix;
4. **RightFailure**: the unique right-phase child has a complete failure;
5. **PartitionFailure**: for one displayed partition, at least one argument
   child has a complete failure; and
6. **AllPartitionsFailed**: every contiguous weak partition has an attached
   PartitionFailure.

Replay recomputes:

- the goal constructor;
- the leftmost context entry;
- its entire right spine;
- terminal-atom equality or inequality;
- the exact finite partition inventory;
- coverage and order of every block; and
- the selected failing child for every rejected partition.

An asserted empty list of candidates is not a failure certificate.

### 12.2 Theorem 12.1: failure soundness

If a complete failure tree for
\(\operatorname{Search}(\Gamma,A)\) replays, then

\[
\Gamma\nvdash A.
\]

#### Proof

Assume a derivation existed.  Focused completeness would supply a successful
focused branch.  The replayed failure tree covers the unique right child or
every atomic partition and rejects each by a recursively sound failure.
Hence no such branch exists, a contradiction.  \(\square\)

### 12.3 Theorem 12.2: failure completeness

If

\[
\Gamma\nvdash A,
\]

then terminating focused search constructs a complete replayable failure
tree.

#### Proof

Search has a finite tree by Theorem 11.3.  If any leaf-to-root branch
succeeded, focused soundness would yield a derivation.  Therefore every
branch fails.  Assemble the appropriate local failure constructor at each
node and retain all partition failures at atomic branching nodes.
\(\square\)

Complete focused failure is a negative theorem about the declared calculus.
It is not:

- a valuation making the conclusion false;
- a resource aperture awaiting an external filler;
- a proof that a larger connective language cannot derive the sequent;
- an exhausted arbitrary inventory of candidate proof trees; or
- an unresolved infinite exploration.

---

## 13. Decidable derivability

### 13.1 Theorem 13.1: skeleton decidability

There is a total decision procedure for

\[
\Gamma\vdash_{\mathrm{TND}^{\mathrm{sk}}_0}A.
\]

It returns either a long normal derivation or a complete failure tree.

#### Proof

Run focused search.  Termination is Theorem 11.3, positive correctness is
Theorems 10.1 and 10.2, and negative correctness is Theorems 12.1 and 12.2.
\(\square\)

### 13.2 Corollary 13.2: checked-\(\mathrm{TND}_0\) decidability

Existence of some fresh checked decoration of a skeleton sequent is
decidable.

On success, decorate the returned long proof using Theorem 4.1 and replay
the ordinary recursive checker.  On failure, Theorem 3.1 shows that any
checked proof would erase to a skeleton proof, contradicting the complete
failure certificate.

This corollary decides the existential fresh-decoration problem.  A separate
problem that fixes particular reused source identities or demands a
particular ledger may have additional audit constraints and is not reduced
to formula-skeleton search by this theorem.

### 13.3 Halting, success, and failure

For this focused object-level task:

- **success** is a replayable long normal derivation;
- **failure** is a replayable complete focused failure tree;
- **halting** follows from strict descent of \(\mu\); and
- **frontier** is an implementation state before the finite search tree has
  been completed.

There is no residual infinite ray under the fixed formula grammar, context,
and focused rules.  Therefore this decision procedure creates no new
\(\Omega\)-boundary.

### 13.4 Finite grammar-respecting compact search

The atomic vocabulary

\[
\{P_K,P_X,P_t\}
\]

is finite, but the recursively generated formula language is not.  Arbitrary
right-implication depth already gives infinitely many formulae.  Search is
finite for a different and more precise reason.

For one fixed finite sequent, the beta-normal subformula property supplies a
finite formula closure.  Focus never invents a formula outside that closure.
At an atomic goal it also preserves the threading grammar: it selects the
forced leftmost head and allocates the remaining word only through contiguous
ordered weak partitions.  It neither crosses two threads nor silently
exchanges, copies, or drops a context position.

This gives a grammar-respecting finite compact search space in the
operational sense:

\[
\text{finite subformula closure}
+
\text{finite ordered partitions}
+
\text{strict recursive descent}.
\]

Individual failed branches retain their typed open obligation.  A complete
failure report closes the metatheoretic question only after every permitted
branch has been covered.

This operational compactness is not a geometric or hyperbolic
compactification.  It adds no boundary point and supplies no \(\Omega\).
If formula depth or contexts grow without bound and their finite searches
form a compatible family, a genuine compactification would still require:

- a declared equivalence on rays or compatible prefixes;
- a topology or convergence structure on the family;
- continuity of the threading and opening operations;
- scheduler or presentation invariance; and
- a proof that no finite certificate already closes the proposed boundary.

None of those conclusions follows from a finite atomic vocabulary.

---

## 14. Minimal calibrating examples

### 14.1 Closed identity

\[
\varnothing\vdash A\multimap_R A.
\]

Right focusing appends \(x:A\) and reduces the task to

\[
x:A\vdash A.
\]

Atomic focusing selects the leftmost head \(x\), whose spine has no
arguments and ends in \(A\).  It returns

\[
\lambda^R x.x.
\]

### 14.2 Ordered application succeeds

\[
f:A\multimap_R B,\ x:A\vdash B.
\]

The atomic goal selects \(f\), whose spine is \([A]\) ending in \(B\).
The only successful partition gives the suffix \(x:A\) to that argument,
returning

\[
\operatorname{app}^R(f,x).
\]

### 14.3 Reversed order fails

\[
x:A,\ f:A\multimap_R B\nvdash B.
\]

The atomic goal must select the leftmost assumption \(x:A\).  Its spine ends
in \(A\), not \(B\), so TerminalMismatch closes the search.  Focusing may
not skip \(x\), exchange the assumptions, or use it before a function that
occurs to its right.

This sequent can be valid after forgetting order and linear resources under
ordinary material implication.  The focused failure is therefore not a
Boolean countermodel.

### 14.4 A closed argument requires an empty block

\[
f:(A\multimap_R A)\multimap_R P\vdash P.
\]

The head spine requires one argument of type \(A\multimap_R A\), while its
remaining context is empty.  The one-block weak partition assigns the empty
word to that argument.  Recursive right focusing constructs
\(\lambda^R x.x\), yielding

\[
\operatorname{app}^R
 \bigl(f,\lambda^R x.x\bigr).
\]

Forbidding empty blocks would make focused search incomplete for the present
empty-antecedent calculus.

### 14.5 Long presentation is not eta equality

The beta-normal assumption proof

\[
f:A\multimap_R B\vdash f:A\multimap_R B
\]

does not end in introduction.  Focused long-form construction instead uses

\[
f:A\multimap_R B
\vdash
\lambda^R x.\operatorname{app}^R(f,x)
:A\multimap_R B.
\]

Both prove the same sequent.  This note neither equates them nor supplies a
history cell between their decorated proof trees.

### 14.6 Focusing does not make proofs canonical

Let

\[
U=p\multimap_R p.
\]

The sequent

\[
h:U\multimap_R(U\multimap_R q),\ u:U\vdash q
\]

has at least two long focused proofs:

\[
h\,
 \bigl(\lambda^R x.\operatorname{app}^R(u,x)\bigr)\,
 \bigl(\lambda^R x.x\bigr)
\]

and

\[
h\,
 \bigl(\lambda^R x.x\bigr)\,
 \bigl(\lambda^R x.\operatorname{app}^R(u,x)\bigr).
\]

They arise from the two weak partitions that assign the one-element suffix
\((u:U)\) to the first or the second argument block.  Focus removes
irrelevant rule-order choices; it does not imply one proof per sequent, proof
equality, or a canonical audit history.  A deterministic implementation may
choose the first candidate while retaining that the mathematical search has
more than one successful branch.

---

## 15. Executable calibration

The self-contained companion
**test_threaded_focused_proof_completion_calibration.py** calibrates:

1. replayable formula-skeleton erasure and boundary-preserving fresh lifting;
2. preservation of distinct positions carrying equal formulae;
3. normal/neutral recognition and rejection of a principal beta detour;
4. beta-normal subformula collection on calibrated proof trees;
5. closed identity and open atomic identity;
6. long completion of an arrow assumption as a distinct beta-normal proof,
   not an asserted eta reduction;
7. order-sensitive focused success and failure;
8. weak contiguous partitions with a closed argument in an empty block;
9. all three ordered weak partitions of a two-argument spine;
10. distinct fresh authorities when one closed skeleton is used twice;
11. retention of two distinct focused proofs from two successful weak
    partitions;
12. the matching atomic head with an unused suffix;
13. complete empty-focus evidence for a closed atomic goal;
14. a typed complete-plan exhaustion result kept separate from semantic
    results;
15. replay rejection of omitted atomic attempts, forged plans, candidate
    indices, boundaries, skeletons, and unchecked lifts;
16. strict recursive descent using the residual-connective count; and
17. bounded generated-proof cross-checks through five proof nodes.

The fixture retains visited judgments, checked descents, flattened atomic
focus attempts, all generated candidates, and a typed
**FocusedSearchExhausted** result.  It deterministically recomputes the
complete finite search report.  It does not yet expose the six mathematical
failure constructors of Section 12 as a recursively nested reusable kernel.
In particular, an omitted partition is rejected by recomputing the whole
report, not by replaying a standalone **AllPartitionsFailed** value.

The fixture has twenty-one passing tests.  The repository-wide Python suite
has 154 passing tests at this revision.  Bounded generated-proof comparison is
calibration, not the proof of focused completeness.  The mathematical proof
is the normal-form inversion of Sections 8--10.

---

## 16. Learning checkpoints

These checkpoints are intended for a first manual pass through the argument.

### Checkpoint 1: identify the residual

Explain why

\[
\Gamma,A\vdash B
\quad\Longleftrightarrow\quad
\Gamma\vdash A\multimap_R B
\]

makes \(A\multimap_R B\) correspond to \(B/A\), and why elimination places
the proof of \(A\) to the right of the function context.

Then explain why allowing the empty context changes the classification from
the original Lambek \(L\) to an \(L^*\)-style fragment.

### Checkpoint 2: distinguish skeleton and decoration

Given one proof of

\[
\varnothing\vdash A\multimap_R A,
\]

list which data survive erasure and which fresh data must be supplied by a
decoration.  Explain why two decorations can erase to the same proof without
being the same audit object.

### Checkpoint 3: find the redex

Classify each of the following as normal or nonnormal:

\[
x,
\qquad
\lambda^R x.x,
\qquad
\operatorname{app}^R(f,x),
\qquad
\operatorname{app}^R(\lambda^R x.M,N).
\]

Explain why the function of a beta-normal application must be neutral.

### Checkpoint 4: prove the head-order lemma

Starting only from the ordered elimination rule, prove that an atomic normal
proof is headed by the leftmost open assumption.  Identify the exact point
where exchange would invalidate the argument.

### Checkpoint 5: replay focused search

Run the procedure by hand on:

\[
(A\multimap_R B),A\vdash B,
\]

\[
A,(A\multimap_R B)\vdash B,
\]

and

\[
((A\multimap_R A)\multimap_R P)\vdash P.
\]

For the last example, identify the empty argument block.

### Checkpoint 6: separate expansion from equality

Construct the long proof

\[
f:A\multimap_R B
\vdash
\lambda^R x.fx:A\multimap_R B
\]

from the assumption proof \(f:A\multimap_R B\vdash f:A\multimap_R B\).
State exactly what has been proved and why eta equality has not.

### Checkpoint 7: audit complete failure

For \(A,(A\multimap_R B)\vdash B\), write the TerminalMismatch record.
Explain why it proves nonderivability in this calculus but supplies no
Boolean valuation and no claim about a larger calculus.

---

## 17. Established and deferred boundary

### Established mathematically at the object-level skeleton

The explicit structural arguments above establish:

- the derivability-level classification as the natural-deduction
  presentation of an associative, empty-antecedent, right-residual ordered
  linear fragment;
- erasure from checked \(\mathrm{TND}_0\) proofs to skeleton derivations;
- boundary-preserving, finite-avoid fresh checked decorations for every
  finite skeleton derivation;
- derivability equivalence at every valid boundary under fresh internal
  decoration;
- mutual normal/neutral characterization of beta-normal proofs;
- the beta-normal subformula property;
- closed atomic impossibility, closed implication introduction, and
  leftmost-head canonicity;
- existence of type-directed long focused presentations without eta
  equality;
- a syntax-directed focused search;
- soundness and completeness of that search;
- possible nonuniqueness of successful focused proofs;
- strict termination by residual-connective count;
- replayable complete finite failure; and
- decidability of derivability in the declared fragment.

### Executably calibrated

The Python fixture calibrates the flattened deterministic subset listed in
Section 15, including erasure and lifting, normal and long-form recognition,
subformula checks, ordered weak partitions, complete-plan exhaustion,
descent, forgery rejection, and bounded generated-proof cross-checks.  It
does not yet promote the standalone recursively nested failure constructors
of Section 12 as an independent kernel.

### Not established

The note does not establish:

- Boolean completeness or equivalence with the \(H_7\) support layer;
- completeness for a resource, categorical, Kripke, phase, or geometric
  model;
- a free right-closed multicategory theorem;
- equality, uniqueness, or canonicality of arbitrary proofs of one sequent;
- alpha equivalence or canonical rebasing of nominal authorities;
- eta reduction, eta equality, beta-eta normalization, or beta-eta
  confluence;
- decidability of beta-eta proof equality;
- an explicit left rule, cut syntax, or Gentzen Hauptsatz;
- tensor, unit, left residual, additives, exponentials, or classical
  control;
- proof-relevant quantifiers or eigenvariable transport;
- actual composition of beta-ledger transports;
- equality, quotient, or higher coherence of beta histories;
- a fair unbounded proof enumerator; or
- compactification or \(\Omega\) for an infinite exploration.

In particular,

\[
\text{focused complete failure}
\neq
\text{Boolean countermodel}
\neq
\text{resource aperture}
\neq
\text{history obstruction}
\neq
\Omega.
\]

---

## Conservative conclusion

The present \(\mathrm{TND}_0\) object language is not yet a complete
propositional logic.  It is a precise and unusually tractable ordered
right-residual core.  Its beta reduction is already strongly normalizing and
confluent.  Normal and neutral forms expose the leftmost-head invariant;
the subformula property bounds every formula used by a normal proof; and
type-directed long presentation turns those facts into a finite focused
search.

For this fixed grammar, exploration therefore has a total proof-theoretic
meaning.  Success is a checked focused derivation.  Failure is a complete
finite tree showing that every permitted residual threading fails.  Both
halt.  Neither result requires forgetting ordered resources into Boolean
truth, and neither introduces an \(\Omega\)-boundary.

The next object-level choices remain explicit.  An eta theory must declare
which newly introduced bound audit data an observer may forget.  A Gentzen
theory must add explicit left and cut rules before claiming cut elimination.
A semantic completeness theorem must name its model class.  The separate
audit branch must compose transports and cells before identifying histories.
This note closes none of those boundaries by renaming them; it supplies the
decidable beta-normal core on which each can be built.
