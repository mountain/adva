# Threaded Finite Propositional and Predicate Logic Adequacy

Status: finite semantic theorem, executable calibration, and promotion
boundary following
[0079](0079-typed-hole-open-close-calibration-v0.md),
[0080](0080-finite-surface-universal-lift-imagination.md), and
[0081](0081-relative-halt-exploration-threaded-compactification.md).

This note answers a proposal by Mingli Yuan:

> Propositions may be typed holes, true may be a filling line, and false may
> be a hole whose filling fibre is certified empty.  Propositional and
> predicate logic should be realized and checked against that grammar before
> a natural-deduction proof system is introduced.

The answer is positive under explicit finite Cartesian hypotheses and
negative without them.  A finite, exhaustive, copy-authorized thread grammar
is adequate for ordinary Boolean propositional semantics and finite
many-sorted predicate semantics.  A general linear or provenance-restricted
thread grammar need not be adequate for classical logic: individually
inhabited fibres may have no compatible conjunction witness, and classically
true implications may have no admissible transformer.

No stable Adva connective, binder, quantifier, proof term, or natural-
deduction rule is introduced here.

---

## 0. Exact result and boundary

Let \(\mathcal M\) be a finite many-sorted structure, let \(\rho\) be an
environment, and let \(\varphi\) be a well-sorted first-order formula.  Write

\[
\mathcal M,\rho\models\varphi
\]

for ordinary finite Tarskian satisfaction, and write

\[
\operatorname{Fill}_{\mathcal M,\rho}(\varphi)
\]

for the finite fibre of canonical lines admitted by the grammar below.

The main result is:

\[
\boxed{
\mathcal M,\rho\models\varphi
\quad\Longleftrightarrow\quad
\operatorname{Fill}_{\mathcal M,\rho}(\varphi)
\ne\varnothing.
}
\tag{A}
\]

This is the **finite thread adequacy theorem**.  It is proved by structural
induction on \(\varphi\), after the atomic, compatibility, transformer, and
domain-exhaustiveness hypotheses have been stated.

The theorem is semantic adequacy, not proof-theoretic completeness.  It does
not yet establish

\[
\Gamma\models\varphi
\Longrightarrow
\Gamma\vdash\varphi.
\]

That implication requires a proof calculus, a derivation checker, soundness,
completeness, and preferably normalization or cut elimination.

---

## 1. Finite many-sorted syntax and models

### 1.1 Terms

For each declared sort \(s\), the first term grammar contains:

\[
t ::= x:s \mid c:s.
\]

Thus the finite fixture has sorted variables and constants but no function
symbols.  Function symbols can be added later without changing the
substitution argument, provided their interpretations are total and
sort-correct.

### 1.2 Formulas

For predicate symbols \(P:s_1\times\cdots\times s_n\) and same-sorted terms
\(t,u\), formulas are:

\[
\begin{aligned}
\varphi ::= {}&
\top
\mid
\bot
\mid
P(t_1,\ldots,t_n)
\mid
t=u\\
&\mid
\neg\varphi
\mid
\varphi\land\varphi
\mid
\varphi\lor\varphi
\mid
\varphi\Rightarrow\varphi\\
&\mid
\exists x:s.\,\varphi
\mid
\forall x:s.\,\varphi.
\end{aligned}
\]

Binders are identified up to alpha renaming.  Substitution is
capture-avoiding and sort-preserving.

### 1.3 Finite structures

A finite many-sorted structure supplies:

- one finite, explicitly enumerated domain \(D_s\) for every sort \(s\);
- one sort-correct value \(c^{\mathcal M}\in D_s\) for every constant;
- one finite extension
  \(P^{\mathcal M}\subseteq D_{s_1}\times\cdots\times D_{s_n}\)
  for every predicate; and
- decidable equality on each finite domain.

The empty domain is allowed in the executable semantic fixture when no
constant requires an inhabitant.  This makes the empty dependent sum and
empty dependent product visible rather than implicit.

---

## 2. Propositions as apertures and lines as realizers

For every formula, structure, and environment, introduce a typed aperture

\[
H_\varphi(\mathcal M,\rho)
\]

and its finite filling fibre

\[
\mathsf L_\varphi(\mathcal M,\rho)
:=
\operatorname{Fill}_{\mathcal M,\rho}(\varphi).
\]

The structural statuses remain distinct:

1. no aperture was declared;
2. the aperture has at least one admitted line;
3. the aperture has an exhaustive empty-fibre certificate; or
4. the aperture remains unresolved because its fibre was not exhausted.

Only cases 2 and 3 determine Boolean truth in the completed finite model.
Case 4 is a search status, not a third truth value.

### 2.1 Atomic certification

For a predicate atom:

\[
\mathsf L_{P(\vec t)}(\mathcal M,\rho)
=
\begin{cases}
\{\operatorname{FactLine}(P,\llbracket\vec t\rrbracket_\rho)\},
&
\llbracket\vec t\rrbracket_\rho\in P^{\mathcal M},
\\
\varnothing,
&
\text{otherwise}.
\end{cases}
\]

For equality:

\[
\mathsf L_{t=u}(\mathcal M,\rho)
=
\begin{cases}
\{\operatorname{EqLine}
(\llbracket t\rrbracket_\rho)\},
&
\llbracket t\rrbracket_\rho
=
\llbracket u\rrbracket_\rho,
\\
\varnothing,
&
\text{otherwise}.
\end{cases}
\]

The empty cases are certified by exhaustive predicate lookup or decidable
finite equality.

### 2.2 Truth and falsehood

\[
\mathsf L_\top\simeq\mathbf 1,
\qquad
\mathsf L_\bot\simeq\mathbf 0.
\]

The unit fibre contains a canonical identity line.  The zero fibre is a
declared, exhaustively empty aperture, not the absence of a proposition.

---

## 3. Connective constructors

### 3.1 Conjunction

The general thread reading is a compatibility-restricted product:

\[
\mathsf L_{\varphi\land\psi}
=
\mathsf L_\varphi
\times_{\mathrm{compat}}
\mathsf L_\psi.
\]

For ordinary Cartesian logic the fixture authorizes every pair of canonical
semantic lines:

\[
\mathsf L_{\varphi\land\psi}
=
\mathsf L_\varphi\times\mathsf L_\psi.
\tag{C-and}
\]

Hence it is inhabited exactly when both factors are inhabited.

This authorization is substantive.  If two lines consume the same exclusive
source, the restricted product may be empty even when both factors are
inhabited.  In that regime classical conjunction is not adequate; a
substructural logic is the more faithful candidate.

#### 3.1.1 Triadic mediation of an exclusive-source conflict

Note [0083](0083-triadic-conflict-aperture-completion.md) refines the
distinct-domain case.  If two lines with identities \(d\ne e\) consume one
source, their compatibility obligation opens an oriented aperture in the
unique remaining domain \(\mu(d,e)\).  Define

\[
\mathcal C(\ell,m)
=
\operatorname{Fill}_{\mu(d,e)}
\left(H_{\mu(d,e)}(\ell,m)\right).
\]

Then a resource-sensitive conjunction has fibre

\[
\mathsf L_{\varphi\land_\triangle\psi}
=
\sum_{\ell\in\mathsf L_\varphi}
\sum_{m\in\mathsf L_\psi}
\mathcal C(\ell,m).
\]

A filler is a remaining-domain line together with a closure certificate.  It
must project back to both boundary lines and use the shared linear source
exactly once.  The open aperture alone is not a conjunction witness.

This derives Cartesian support intersection only under the triadic completion
condition

\[
\mathsf L_\varphi\ne\varnothing
\land
\mathsf L_\psi\ne\varnothing
\Longrightarrow
\exists\ell,m,\quad
\mathcal C(\ell,m)\ne\varnothing.
\]

The rule does not handle same-domain contraction, three-way source conflict,
or associativity by itself.  It is therefore a possible derivation of A2, not
a replacement for the remaining structural laws.

### 3.2 Disjunction

\[
\mathsf L_{\varphi\lor\psi}
=
\mathsf L_\varphi+\mathsf L_\psi.
\tag{C-or}
\]

The sum is tagged.  A line retains either
\(\operatorname{Left}(\ell)\) or
\(\operatorname{Right}(r)\).  Erasing that tag invalidates disjunction
elimination and loses branch provenance.

### 3.3 Implication

An implication line is a total admissible transformer:

\[
\mathsf L_{\varphi\Rightarrow\psi}
=
\operatorname{Adm}
\left(
\mathsf L_\varphi,
\mathsf L_\psi
\right).
\]

In the finite Cartesian fixture, every total finite function is admissible,
or one canonical representative is retained.  Therefore:

\[
\operatorname{Adm}(A,B)\ne\varnothing
\quad\Longleftrightarrow\quad
A=\varnothing
\ \lor\
B\ne\varnothing.
\tag{C-imp}
\]

The empty-source case contains the unique empty transformer.  It is licensed
only when source exhaustion is certified.  A partially explored empty
observation does not justify vacuity.

For a provenance- or resource-restricted grammar, the implication support
can be strictly smaller than the classical truth table even when \(B\) is
inhabited.  Transformer completeness is therefore a theorem obligation, not
a notation.

### 3.4 Negation

\[
\neg\varphi:=\varphi\Rightarrow\bot.
\]

Consequently:

\[
\mathsf L_{\neg\varphi}\ne\varnothing
\quad\Longleftrightarrow\quad
\mathsf L_\varphi=\varnothing
\]

only when the source fibre is exhaustive and the empty transformer is
admitted.  Failure to find a \(\varphi\)-line is insufficient.

---

## 4. Predicate constructors

### 4.1 Existential quantification

\[
\boxed{
\mathsf L_{\exists x:s.\,\varphi}
=
\sum_{a\in D_s}
\mathsf L_\varphi(\rho[x\mapsto a]).
}
\tag{Q-exists}
\]

An existential line retains both the witness value \(a\) and the body line.
It cannot forget which domain member closed the aperture.

The dependent sum is inhabited exactly when at least one indexed filling
fibre is inhabited.

### 4.2 Universal quantification

\[
\boxed{
\mathsf L_{\forall x:s.\,\varphi}
=
\prod_{a\in D_s}
\mathsf L_\varphi(\rho[x\mapsto a]).
}
\tag{Q-forall}
\]

A universal line is a complete indexed family with one body line for every
declared domain value.  In the executable finite grammar the family is
enumerated explicitly.

For an empty domain:

\[
\sum_{a\in\varnothing}\mathsf L_a
=
\mathbf 0,
\qquad
\prod_{a\in\varnothing}\mathsf L_a
=
\mathbf 1.
\]

Thus existential falsehood and universal vacuity are consequences of the
empty sum and empty product.  They are not consequences of search timeout.

For infinite domains, an explicit product is not an implementation.  A
universal line would need a uniform program or section, and its relation to
pointwise truth may require choice or computability hypotheses.  That case is
outside this finite theorem.

---

## 5. Finite thread adequacy theorem

### 5.1 Hypotheses

The theorem assumes:

**A0. Well-sorted syntax.**  Every term, predicate application, equality, and
binder is sort-correct.

**A1. Atomic exactness.**  Predicate membership and equality return a line
exactly when the corresponding atomic judgment is true, and otherwise return
an exhaustive empty certificate.

**A2. Resolved pair completeness.**  Any two inhabited operand fibres contain
a pair that is directly compatible, explicitly copy/share authorized, or
closed by a certified compatibility filler.  Note 0083 supplies a candidate
third-domain filler rule for distinct-domain conflicts; same-domain
contraction and higher coherence remain separate obligations.

**A3. Tagged sums.**  Disjunction preserves left/right provenance.

**A4. Transformer completeness.**  The finite implication fibre is inhabited
exactly when its source is certified empty or its target is inhabited.

**A5. Domain exhaustiveness.**  Every quantified domain is finite and exactly
enumerated.

**A6. Alpha and substitution naturality.**  Renaming a bound variable changes
no satisfaction judgment or filling fibre up to canonical isomorphism.

### 5.2 Theorem

For every formula generated by the grammar, every finite structure satisfying
A0--A6, and every well-sorted environment:

\[
\mathcal M,\rho\models\varphi
\quad\Longleftrightarrow\quad
\mathsf L_\varphi(\mathcal M,\rho)\ne\varnothing.
\]

### 5.3 Proof by structural induction

**Atomic formulas.**  The predicate and equality cases are A1.

**Units.**  \(\mathbf 1\) is inhabited and \(\mathbf 0\) is empty, matching
\(\top\) and \(\bot\).

**Conjunction.**  By the induction hypotheses and A2, the resolved
compatibility sum over the two operand fibres is inhabited exactly when both
operand fibres are inhabited.  In the canonical fixture this sum reduces to
\(\mathsf L_\varphi\times\mathsf L_\psi\).  This is the Tarskian clause for
conjunction.

**Disjunction.**  A tagged sum is inhabited exactly when at least one summand
is inhabited.  This is the Tarskian clause for disjunction.

**Implication.**  By A4, the transformer fibre is inhabited exactly when the
premise fibre is empty or the conclusion fibre is inhabited.  By induction,
this is equivalent to

\[
\mathcal M,\rho\not\models\varphi
\quad\lor\quad
\mathcal M,\rho\models\psi.
\]

**Negation.**  Substitute \(\bot\) for the conclusion of implication.

**Existential quantification.**  A finite dependent sum is inhabited exactly
when some indexed factor is inhabited.  Apply the induction hypothesis to
each environment \(\rho[x\mapsto a]\).

**Universal quantification.**  A finite dependent product is inhabited
exactly when every indexed factor is inhabited.  Apply the induction
hypothesis to every enumerated domain member.  The empty product gives the
empty-domain case.

These cases exhaust the syntax.  Therefore the theorem holds.

---

## 6. Substitution theorem

For a term \(t:s\), a variable \(x:s\), and capture-avoiding substitution:

\[
\boxed{
\mathcal M,\rho\models\varphi[t/x]
\quad\Longleftrightarrow\quad
\mathcal M,\rho
\left[
x\mapsto\llbracket t\rrbracket_{\mathcal M,\rho}
\right]
\models\varphi.
}
\tag{S}
\]

The threaded strengthening is:

\[
\boxed{
\mathsf L_{\varphi[t/x]}(\mathcal M,\rho)
\cong
\mathsf L_\varphi
\left(
\mathcal M,
\rho[x\mapsto\llbracket t\rrbracket_{\mathcal M,\rho}]
\right).
}
\tag{TS}
\]

The proof is a simultaneous induction on terms and formulas.  The binder case
alpha-renames a bound variable whenever it occurs free in \(t\), then applies
the induction hypothesis.  The executable fixture checks both satisfaction
and fibre cardinality for a substitution that would capture a variable under
naive replacement.

This theorem is the first necessary bridge from predicate semantics toward
quantifier introduction and elimination.  Without it, the dependent
sum/product formulas are only suggestive notation.

---

## 7. Propositional corollary on the seven halt worlds

Use the seven exact relative halt worlds

\[
H_7
=
\{h_S:\varnothing\ne S\subseteq\{K,X,t\}\}
\]

and interpret \(K,X,t\) as zero-ary predicates.  For each world \(h_S\),
assign a canonical atomic line exactly to the atoms contained in \(S\).

Every singleton world has a characteristic formula:

\[
\chi_S
=
\bigwedge_{d\in S}P_d
\land
\bigwedge_{d\notin S}\neg P_d.
\]

Every support \(U\subseteq H_7\) has the disjunctive formula:

\[
\chi_U
=
\bigvee_{h_S\in U}\chi_S.
\]

Hence all \(2^7=128\) extensional propositions are represented.  Finite
thread adequacy gives:

\[
h\in U
\quad\Longleftrightarrow\quad
h\models\chi_U
\quad\Longleftrightarrow\quad
\mathsf L_{\chi_U}(h)\ne\varnothing.
\]

The executable fixture checks all \(128\times7=896\) pairs.

---

## 8. Entailment and the remaining proof-theoretic gap

For a fixed structure and environment:

\[
\Gamma\models_{\mathcal M,\rho}\varphi
\]

means that inhabitation of every premise fibre implies inhabitation of the
conclusion fibre.  Under A2 and A4 this yields a pointwise semantic
transformer:

\[
\prod_{\gamma\in\Gamma}\mathsf L_\gamma(\mathcal M,\rho)
\longrightarrow
\mathsf L_\varphi(\mathcal M,\rho).
\]

But first-order semantic entailment quantifies over every admitted structure
and environment:

\[
\Gamma\models\varphi
\Longleftrightarrow
\forall\mathcal M,\rho,\quad
\mathcal M,\rho\models\Gamma
\Rightarrow
\mathcal M,\rho\models\varphi.
\]

A family of pointwise transformers is not automatically one uniform
derivation.  Natural deduction requires syntax-directed constructors that do
not inspect an arbitrary model to choose their branch or witness.

Therefore:

\[
\boxed{
\text{finite thread adequacy}
\ne
\text{soundness and completeness of natural deduction}.
}
\]

The present theorem makes that later question well posed; it does not answer
it.

---

## 9. Executable calibration

The companion test
**tests/python/test_threaded_finite_logic_adequacy.py** implements:

1. sorted variables and constants;
2. zero-ary, unary, and binary predicates;
3. decidable sorted equality;
4. \(\top,\bot,\neg,\land,\lor,\Rightarrow\);
5. finite \(\exists\) as a witness-tagged dependent sum;
6. finite \(\forall\) as a complete dependent product;
7. capture-avoiding, sort-preserving substitution;
8. ordinary Tarskian evaluation;
9. canonical finite filling fibres; and
10. the inhabitedness comparison in theorem (A).

The executable oracles are:

- all 128 proposition supports over all seven halt worlds;
- all 128 structures on a two-element domain generated by four unary
  predicate extensions, sixteen binary relation extensions, and two constant
  values;
- four environments per structure for seven representative open and closed
  predicate formulas;
- 256 capture-avoiding substitution comparisons; and
- nonempty- and empty-domain quantifier edges.

The earlier connective-fibre fixture additionally retains a decisive
counterexample: two individually inhabited fibres can have an empty
compatibility-restricted conjunction when both lines consume one exclusive
source.  The note 0083 fixture refines its distinct-domain case into a typed
remaining-domain aperture and verifies that only an oriented linear common
lift with a closure certificate can fill it.

These are exhaustive finite checks for the declared fixtures, not empirical
evidence sampled from a larger state space.

---

## 10. Decisive falsifiers and logic selection

Classical adequacy must be weakened or rejected if:

1. a true atomic judgment has no certified line;
2. a false atomic judgment cannot be distinguished from incomplete search;
3. a conjunction loses all pairs because required lines are incompatible;
4. a third-domain color is accepted without a common-lift and resource
   certificate;
5. disjunction erases its branch tag;
6. a classically true implication has no admissible total transformer;
7. an unresolved source is treated as empty to obtain vacuous implication;
8. an existential line forgets its witness;
9. a universal line omits a declared domain member;
10. substitution captures a free variable or changes its sort;
11. alpha renaming changes satisfaction or filling;
12. observer refinement changes a previously used domain without reopening
    the quantified claim; or
13. a compactification identifies an unresolved fibre with a certified empty
    one.

If items 3 or 6 are intrinsic rather than implementation defects, the correct
response is not to force classical logic.  The grammar may instead select a
linear, affine, relevant, ordered, or otherwise substructural logic whose
connectives reflect the actual resource laws.

This produces a concrete logic-selection criterion:

\[
\boxed{
\begin{aligned}
\text{copy, weakening, and compatible pairing}
&\Longrightarrow
\text{Cartesian connectives},\\
\text{exclusive sources and restricted transformers}
&\Longrightarrow
\text{substructural connectives}.
\end{aligned}
}
\]

---

## 11. Promotion boundary and next step

This note establishes:

- a finite many-sorted predicate syntax;
- capture-avoiding substitution and its finite semantic check;
- canonical finite line constructors for propositional connectives and
  quantifiers;
- a structural-induction proof of finite semantic adequacy;
- exhaustive finite proposition and predicate fixtures; and
- explicit counterconditions separating classical from substructural logic.

It does not establish:

- a stable parser, IR, or Rust representation for these formulas;
- proof terms in the Adva kernel;
- natural-deduction introduction or elimination rules;
- soundness, completeness, normalization, or cut elimination;
- adequacy for infinite, evolving, or non-exhaustive domains;
- uniform witness extraction from semantic truth;
- classical adequacy for unrestricted existing Adva thread graphs; or
- a relation between proof normalization and hyperbolic compactification.

The next proof-theoretic step should choose one of two routes:

1. a Cartesian finite natural deduction whose structural rules are justified
   by explicit copy, discard, and compatibility certificates; or
2. a linear or ordered natural deduction whose contexts preserve the native
   source and occurrence discipline.

The finite semantics in this note can evaluate either calculus independently.
Exploration can then search for a derivation, countermodel, or retained
frontier without defining truth by the behavior of the search.

## Conservative conclusion

The line--hole hypothesis can support ordinary finite propositional and
predicate semantics, but only after its structural laws are stated.  A
formula is a typed aperture; an atomic fact or equality supplies a primitive
line; conjunction pairs compatible lines; disjunction tags alternatives;
implication is a total admissible transformer; existential quantification
retains a witness; and universal quantification supplies a complete indexed
family.

Under finite exhaustiveness, Cartesian compatibility, and transformer
completeness, satisfaction is exactly filling-fibre inhabitation.  The proof
is structural induction, and the finite implementation exhaustively checks
its declared models.  Without those hypotheses the mismatch is informative:
it identifies the resource-sensitive logic selected by the actual thread
grammar.
