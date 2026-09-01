# Relative Halt Semantics, Entailment Search, and Thread-Respecting Compactification

Status: working synthesis and finite calibration specification following
[0033](0033-omega-type-computational-boundary.md),
[0036](0036-triangular-symbolic-interpretation-learning-calculus.md),
[0044](0044-finite-triadic-satisfaction-logic.md),
[0045](0045-logic-as-learned-characteristic.md),
[0046](0046-proposal-for-logic-on-a-3-form.md),
[0059](0059-tri-bracket-eigen-normalization-logic.md),
[0060](0060-checked-bracket-observer-bridge.md),
[0066](0066-self-dual-characteristic-completion-calculus.md),
[0079](0079-typed-hole-open-close-calibration-v0.md), and
[0080](0080-finite-surface-universal-lift-imagination.md).

This note records a proposal initiated by Mingli Yuan:

> The seven nonempty triadic stopping forms should be examined as the finite
> base of a propositional logic.  Quantifiers should be introduced only after
> the connective layer is understood.  Exploration is processual: its growing
> frontier should meet the universal hyperbolic boundary, while any
> compactification induced by a finite vocabulary must preserve the grammar
> of threads and apertures.

The proposal is sharpened below by separating exact stable faces, relative
machine halts, propositions, semantic entailment, future predicate logic,
proof search, finite-word boundaries, permanent cusps, and operational
apertures.  Exploration is not promoted here to an object-language modality.
Its first formal role is certificate search for an entailment question inside
one fixed logic.  Natural deduction, dynamic modalities, and fixed-point
operators remain downstream.  No stable logical symbol, quantifier,
compactification type, Rust API, or semantic right to forget is introduced
here.

---

## 0. Executive correction and result

Let

\[
D=\{K,X,t\}.
\]

The first tri-cell of note 0059 has seven nonempty exact stable faces

\[
\mathsf{Face}_7
=
\mathcal P(D)\setminus\{\varnothing\}.
\]

They are not yet seven truth values or seven machine halts.  A candidate
**exact relative halt mode** is

\[
\boxed{
\operatorname{ExactHalt}_{S,Q}(M)
\Longleftrightarrow
\operatorname{Stable}(\operatorname{surface}_Q M)=S
\land
\operatorname{Quiescent}_Q(M),
\qquad
\varnothing\ne S\subseteq D.
}
\]

This yields seven mutually exclusive terminal worlds when the declared
observer projection is representable and the machine is quiescent.  The
current checked result establishes only the face classifier and the need for
quiescence; it has not installed these seven modes as a universal machine
semantics.

The proposed logical architecture is

\[
\boxed{
\text{seven exact halt worlds}
\to
\text{generated propositions and semantic connectives}
\to
\text{semantic entailment}
\to
\text{predicate syntax, substitution, and candidate quantifiers}
\to
\text{later proof calculus and entailment search}
\to
\text{thread-respecting search-boundary geometry}.
}
\]

The principal compactification claim is also conditional:

> A finite typed vocabulary supplies a finitely branching word or path
> system whose infinite admissible continuations have an end boundary.  A
> hyperbolic realization may identify that symbolic boundary with part of a
> visual or Gromov boundary only after a checked coding or quasi-isometry
> theorem.  The compactification must retain permanent typed cusps,
> operational aperture circles, thread endpoints and cyclic orders, pairing
> choices, holonomy, and residual evidence.

Universality is therefore not a completed scalar output.  It is the coherent
unbounded unfolding of finite certified words and threads.

---

## 1. Contingency enters through an aperture, not as inspected content

Let \(a\) be a contingent historical event relative to the current observer
and vocabulary.  Contingent here means not derivable or canonically selected
inside the current grammar; it does not by itself mean probabilistically
random.

The universal grammar may retain an opaque identity and provenance for
\(a\), but its active behavior must factor through declared observation:

\[
a
\longmapsto
\bigl([a]_Q,R_Q(a)\bigr),
\]

\[
\mathcal E_{Q,B}(a)
=
\left(
\overline{\mathcal E}_{Q,B}([a]_Q),
R_Q(a)
\right).
\]

The residual records the distinctions that the active quotient does not use.
If two events are equivalent under all admitted contexts and tests, active
evolution must respect that equivalence:

\[
a\sim_Q b
\Longrightarrow
\operatorname{Step}_Q(C[a])
\sim_Q
\operatorname{Step}_Q(C[b]).
\]

Failure of this law means that the grammar inspected undeclared history, the
observer was too coarse, or a supposedly forgotten distinction was still a
live dependency.

A contingent beginning creates a typed aperture and an obligation.  It is not
already a failure.  A failure requires a witness that one candidate cannot
close, lift, represent, continue, or satisfy that obligation under the
declared grammar.

---

## 2. Three readings of the seven faces

### 2.1 Seven positive surface requests

For every nonempty \(S\subseteq D\), note 0059 defines

\[
\operatorname{Sat}_S(p)
\Longleftrightarrow
S\subseteq\operatorname{Stable}(p).
\]

These predicates overlap.  They form seven nonempty positive conjunctions of
the three atoms \(P_K,P_X,P_t\).  Their exact conjunction law is

\[
\operatorname{Sat}_S\land\operatorname{Sat}_T
=
\operatorname{Sat}_{S\cup T}.
\]

Disjunction does not remain inside this seven-element family.  For example,

\[
\operatorname{Sat}_{\{K\}}
\lor
\operatorname{Sat}_{\{X\}}
\]

is not one face request \(\operatorname{Sat}_U\).  Thus the seven requests are
not a propositional algebra.

### 2.2 Seven mutually exclusive terminal worlds

Let

\[
H_7=\{h_S:\varnothing\ne S\subseteq D\},
\]

where \(h_S\) records an `ExactHalt` at face \(S\).  Define the three atomic
supports

\[
P_d
=
\{h_S\in H_7:d\in S\},
\qquad d\in D.
\]

An extensional proposition is a subset of \(H_7\).  Ordinary set
intersection, union, and relative complement then provide a finite Boolean
calibration.  The three atomic supports distinguish every terminal world:

\[
\{h_S\}
=
\bigcap_{d\in S}P_d
\cap
\bigcap_{d\notin S}(H_7\setminus P_d).
\]

Consequently their Boolean closure is the complete powerset

\[
\mathcal P(H_7),
\qquad
|\mathcal P(H_7)|=2^7=128.
\]

This is an extensional finite result, not yet a proof-relevant logic.
Conjunction still needs synchronized witnesses, disjunction needs tagged
alternatives, implication needs a checked transformer, and negation needs an
admissible dual or countercertificate.

### 2.3 Why the seven faces should not be scalar truth values yet

If a scalar value is identified directly with a nonempty subset of \(D\), the
family is not closed under intersection or complement:

\[
\{K\}\cap\{X\}=\varnothing,
\qquad
D\setminus D=\varnothing.
\]

Adding the eighth face \(\varnothing\) repairs set-theoretic closure, but that
face must not be called exploration, divergence, falsehood, or `Unknown`.
Those are independent execution or epistemic axes.  An entirely stable
surface can still have an enabled gate and fail quiescence, while fuel may be
exhausted on a represented nonempty face.

The recommended first semantics therefore treats the seven exact halts as
worlds and propositions as supports over them.

---

## 3. Which process words may become connectives

The current vocabulary must remain sorted.

| word | proposed logical role |
|---|---|
| `Success` | scoped satisfaction judgment with certificate and residual |
| `Failure` or `Refuted` | witnessed candidate or obligation failure; not negation |
| `Undecided` | budgeted metalanguage result with frontier and continuation |
| `Open` | typed outstanding obligation |
| `Seal` | certified program action that internalizes a filling |
| `Reopen` | dynamic transition under refined observation or activated residual |
| `Abstract` | quotient or name formation under contextual congruence |
| `Forget` | observer map with replayable residual |
| `Generate` | candidate constructor; witness formation requires predicate syntax |
| `Explore` | entailment-certificate search; logic revision stays in the metalanguage |
| `Thread` | semantic transport now; proof term only after a calculus is chosen |
| `Lift` | reconstruction or instantiation in a finer or universal carrier |

The first candidate connectives are induced semantically from operations on
proposition supports:

\[
\llbracket A\land B\rrbracket
=
\llbracket A\rrbracket\cap\llbracket B\rrbracket,
\qquad
\llbracket A\lor B\rrbracket
=
\llbracket A\rrbracket\cup\llbracket B\rrbracket.
\]

That extensional semantics comes before a proof calculus.  A later
proof-relevant presentation would additionally require:

- \(A\land B\) requires compatible witness pairing and trace synchronization;
- \(A\lor B\) requires a retained branch tag and branch provenance;
- \(A\Rightarrow B\) requires a checked hypothetical transformer and a
  discharge rule;
- \(A^\star\) or \(\neg A\) requires outcome dualization to be well defined
  under admissible contexts.

`Failure(A)` does not by itself construct \(\neg A\).  Failure to find a
certificate constructs neither falsehood nor divergence.

A proposed semantic connective must first pass:

1. extensional well-definedness on the admitted proposition supports;
2. contextual congruence under the frozen observer and norm; and
3. naturality, or an explicit reopening witness, under observer refinement.

Only later may a natural-deduction or other proof-theoretic presentation add:

4. proof- or construction-relevant term formers;
5. introduction, elimination, and discharge rules;
6. residual and resource preservation; and
7. soundness, relative completeness, and normalization obligations.

---

## 4. Predicate logic must precede proof-theoretic quantifiers

The finite halt-world carrier calibrates propositional semantics only.  A
predicate language additionally needs at least:

- typed variables and terms;
- arities and interpretations of predicates;
- capture-avoiding substitution;
- binders, free-variable support, and alpha equivalence;
- equality or an explicit decision not to include it;
- observer-indexed domains and their refinement maps; and
- a distinction between an empty fibre and an incompletely explored fibre.

None of these is supplied by the 128-proposition calculation.  Quantifiers
therefore remain semantic candidates until one finite predicate fixture has
checked substitution and binding.

Let a fine observer refine a coarse observer through

\[
q:\mathcal O_{Q'}\longrightarrow\mathcal O_Q.
\]

Inverse image gives reindexing

\[
q^*:\mathcal L_Q\longrightarrow\mathcal L_{Q'}.
\]

Where a later predicate family is closed under the required operations,
candidate semantic quantifiers are adjoints:

\[
\boxed{
\exists_q\dashv q^*\dashv\forall_q.
}
\]

The left adjoint reports that at least one fine lift satisfies the predicate.
The right adjoint reports that every compatible fine lift satisfies it.  The
residual fibre is therefore the semantic carrier of the quantifier, not
discarded implementation detail.

The same pattern applies to coordinate projections of the typed 3-form

\[
\Lambda_Q\subseteq\mathcal T_Q\times\mathcal X_Q\times\mathcal K_Q.
\]

It suggests six typed quantifiers:

\[
(\exists_t,\forall_t),
\qquad
(\exists_X,\forall_X),
\qquad
(\exists_K,\forall_K).
\]

Their first readings are:

- \(\exists_K\): some construction or witness completes an opposite
  time--space section;
- \(\exists_X\): some placement, filling, sheet, or possible world is
  compatible;
- \(\exists_t\): some history or finite run realizes the section;
- the corresponding universal quantifiers require every admitted member of
  the declared fibre.

An unenumerated or pending fibre is not an empty fibre.  Vacuous truth is
licensed only after exact exhaustiveness, not after fuel exhaustion.
Beck--Chevalley, Frobenius, and substitution laws remain open.  Quantifier
introduction, elimination, eigenvariable, and witness-discharge rules belong
to the still-later natural-deduction layer.

---

## 5. Exploration first searches an entailment question

For one fixed observer, language, interpretation, and norm, semantic
entailment and proof-theoretic derivability must be written separately:

\[
\Gamma\models_Q\varphi,
\qquad
\Gamma\vdash_Q\varphi.
\]

The first quantifies over admitted models or halt worlds.  The second requires
a selected proof calculus.  Exploration is initially the process that seeks
finite evidence connecting the two; it is not itself a connective,
quantifier, or truth value.

Once a proof system and an independent model semantics both exist, the
intended result type is

\[
\boxed{
\operatorname{Explore}_{Q,N,\Sigma,B}
(\Gamma\Rightarrow\varphi)
\Downarrow
\begin{cases}
\operatorname{Derivation}(\pi),\\
\operatorname{Countermodel}(M,w_M),\\
\operatorname{Frontier}(F,R,\operatorname{continue}).
\end{cases}
}
\]

The cases have different authority:

- `Derivation` is checked evidence for \(\Gamma\vdash_Q\varphi\);
- `Countermodel` is checked evidence for
  \(\Gamma\not\models_Q\varphi\);
- `Frontier` records that the bounded search has established neither result.

Budget and scheduler affect which certificate is found, not the definition of
\(\models_Q\) or \(\vdash_Q\).  If exploration changes the observer,
vocabulary, interpretation, or rule set, it performs a metalanguage update

\[
(\mathcal L_Q,\models_Q)
\longrightarrow
(\mathcal L_{Q'},\models_{Q'}),
\]

not a derivation inside one unchanged logic.  The update must transport old
claims or reopen them from residual evidence.

### 5.1 The present finite entailment calibration

Before a proof calculus exists, the seven halt worlds already support a
complete finite semantic decision procedure.  For a finite premise family
\(\Gamma\subseteq\mathcal P(H_7)\), let

\[
\operatorname{Mod}(\Gamma)
=
\bigcap_{A\in\Gamma}\llbracket A\rrbracket,
\]

with \(\operatorname{Mod}(\varnothing)=H_7\).  Then

\[
\Gamma\models_{H_7}\varphi
\Longleftrightarrow
\operatorname{Mod}(\Gamma)
\subseteq
\llbracket\varphi\rrbracket.
\]

A failed inclusion returns the exact finite countermodel support

\[
\operatorname{Mod}(\Gamma)
\setminus
\llbracket\varphi\rrbracket.
\]

This is semantic entailment only.  It supplies no proof term and proves no
soundness or completeness theorem for natural deduction.

### 5.2 Deferred process interpretations

Dynamic modalities and fixed points may later describe a chosen proof-search
transition system.  In particular, finite proof reachability may admit a
least-fixed-point reading, while indefinitely fair open branches may admit a
greatest-fixed-point reading.  Those are downstream hypotheses, not part of
the present propositional or predicate grammar.

Likewise, the imagination operations from note 0080 remain metalanguage
search constructors:

\[
J_K=\operatorname{FreshWitness},
\qquad
J_X=\operatorname{Split},
\qquad
J_t=\operatorname{FairExtend}.
\]

They may later schedule witness search, model branching, and fair rule
application.  Until predicate syntax and a proof calculus exist, they do not
implement existential introduction, possible-world semantics, or proof
completeness.

---

## 6. Finite vocabulary and symbolic compactification

Let \(A_n\) be one finite typed vocabulary and let

\[
L_n\subseteq A_n^*
\]

be a prefix-closed language of admitted finite exploration or thread words.
Its infinite admissible boundary is

\[
\partial L_n
=
\left\{
\alpha\in A_n^\omega:
\alpha_{\le m}\in L_n
\text{ for every }m
\right\}.
\]

Because the alphabet is finite, \(A_n^\omega\) is compact in the product
topology.  If admissibility is closed under limits of finite prefixes,
\(\partial L_n\) is a closed compact subspace.  Equivalently, a locally
finite prefix tree has a compact end compactification under the standard
hypotheses.

This is the first exact relation between a finite vocabulary and
compactification:

\[
\boxed{
\text{finite branching of admitted words}
\Longrightarrow
\text{a compact space of coherent infinite continuations}.
}
\]

A finite prefix-free frontier \(F_{n,B}\) determines a finite union of
cylinder neighborhoods on that boundary.  Under a declared binary
self-delimiting code its current open mass is

\[
\varepsilon_{n,B}
=
\sum_{u\in F_{n,B}}2^{-|u|}.
\]

This is a measure of unresolved cylinders, not a count of failures or a
probability of falsehood.  In a universal prefix-free interpreter, the
positive halting mass is enumerable from below while no general finite
certificate proves that the remaining boundary has been exhausted.

### 6.1 Vocabulary refinement

An open learner has a tower of finite vocabularies rather than one final
alphabet.  If refinement maps have compatible forgetting projections

\[
q_{n+1,n}:\overline L_{n+1}\longrightarrow\overline L_n,
\]

one may ask for an inverse-limit carrier

\[
\overline L_\infty
=
\varprojlim_n\overline L_n.
\]

Compactness follows only under the usual nonemptiness, compactness, and
compatibility hypotheses.  Vocabulary creation may make the transition a
correspondence rather than a total map, and an inverse limit can be empty.
The residual must record precisely where refinement, forgetting, and new
primitive formation fail to commute.

### 6.2 Hyperbolic realization is an additional theorem

A finite alphabet does not imply that its rewrite graph is hyperbolic.  To
obtain a map

\[
\partial L_n\longrightarrow\partial\mathbb H^2_{\mathrm{AM}},
\]

one still needs a checked symbolic coding, convergence theorem,
quasi-isometric embedding, convergence-group action, or equivalent boundary
extension result.  Without that bridge, the word boundary and the hyperbolic
ideal circle are related hypotheses rather than identical objects.

---

## 7. A thread-respecting hyperbolic bordification

The compactification must distinguish at least five boundary notions:

1. the visual boundary \(\partial\mathbb H^2_{\mathrm{AM}}\) upstairs;
2. the three permanent typed cusp ends \(K,X,t\) of the marked quotient;
3. horocyclic boundary circles used to truncate those cusps for finite
   interfaces;
4. operational Failure apertures opened by witnessed obstructions; and
5. the finite unresolved search frontier, which is a cylinder cover rather
   than the completed ideal boundary.

Ordinary conformal compactification fills a cusp by a point.  That can erase
approach direction, cyclic order of ports, and thread incidence.  The first
appropriate candidate is instead a marked horocyclic bordification or real
oriented blow-up of each typed puncture.  It replaces a cusp point by a
labelled boundary circle of approach directions while keeping operational
apertures as separately typed circles.

The proposed decorated record is

\[
\overline{\mathcal O}^{\mathrm{thr}}_{P,Q}
=
\left(
\overline\Sigma^{\mathrm{or}}_{P,Q},
\Omega_{\mathrm{perm}},
H_{\mathrm{op}},
\mathsf{Ports},
W,
\Gamma_P,
\rho_P,
\mathfrak m_P,
R_P
\right),
\]

where:

- \(\overline\Sigma^{\mathrm{or}}_{P,Q}\) is the oriented or horocyclic
  bordified carrier;
- \(\Omega_{\mathrm{perm}}=\{K,X,t\}\) contains the permanent typed ends;
- \(H_{\mathrm{op}}\) is the finite family of operational apertures;
- `Ports` retains types, orientations, occurrence identities, and cyclic
  boundary order;
- \(W\) is the typed thread or ribbon graph;
- \(\Gamma_P\) records deck and identification data;
- \(\rho_P\) records monodromy or holonomy;
- \(\mathfrak m_P\) retains chart, observer, basepoint, and vocabulary
  markings; and
- \(R_P\) retains forgotten history, alternatives, schedules, and unresolved
  obligations.

This is a bordification of a decorated process carrier, not merely a compact
topological space.

### 7.1 Grammar-conservativity laws

An admissible compactification must satisfy at least the following laws.

**C0. Boundary-sort separation.**  No permanent cusp is silently converted
into an operational aperture, and no finite frontier is declared to be the
entire ideal boundary.

**C1. Endpoint conservation.**  Every finite thread endpoint remains attached
to its typed port unless an explicit gate, pairing, cap, or seal discharges
it.

**C2. Cyclic-order and occurrence preservation.**  Distinct port orders,
source occurrences, or pairing choices are not identified without an
authorized quotient and residual.

**C3. Seal compatibility.**  For a certified seal,

\[
\operatorname{Comp}^{\mathrm{thr}}
\bigl(\operatorname{Seal}_{H,\kappa}(W)\bigr)
\cong
\operatorname{Seal}_{\operatorname{Comp}(H),\operatorname{Comp}(\kappa)}
\bigl(\operatorname{Comp}^{\mathrm{thr}}(W)\bigr).
\]

No such equation is available for an uncertified filling.

**C4. Holonomy preservation.**  A compactification may turn an infinite
approach into a boundary mark, but it cannot turn nontrivial monodromy into a
contractible cap.  A defect closure retains its defect.

**C5. Successful-lift preservation.**  A thread sealed downstairs may lift
upstairs from \(\widetilde p\) to \(g\widetilde p\).  Its iterates and ideal
endpoints remain part of the generative semantics even though the downstairs
obligation is closed.

**C6. Reopening naturality.**  Observer refinement and `Reopen` commute with
compactification up to a typed residual or produce an explicit obstruction.

**C7. Frontier honesty.**  Budget exhaustion retains the finite antichain,
scheduler, vocabulary version, and continuation.  Compactification does not
turn an unresolved cylinder into a failed branch or a completed point.

**C8. Finite presentation.**  The finite observer stores generators,
relations, markings, port data, and residual programs.  It does not store a
completed uncountable boundary extensionally.

---

## 8. Three kinds of open thread

The phrase "a thread that has not successfully closed" must be separated into
three cases.

### 8.1 Finite unmatched thread

An endpoint on an operational aperture represents a pending typed obligation.
It can be sealed only by explicit compatible pairing, gate, or patch data.

### 8.2 Infinite exploration ray

After a fixed search calculus and fairness policy exist, an infinite fair
branch may have every finite prefix admitted but no finite closure
certificate.  It belongs to the end boundary of that search tree.  It may
encode genuine nontermination, perpetual revision, or simply an unresolved
run; those readings require additional evidence.  The present propositional
calibration has no such branch semantics.

### 8.3 Lift of a successful sealed thread

A closed thread downstairs may represent \(g\in\Gamma_P\).  A chosen lift
satisfies

\[
\widetilde p
\longrightarrow
g\widetilde p
\longrightarrow
g^2\widetilde p
\longrightarrow\cdots.
\]

This path may converge to an ideal boundary point.  It is open upstairs
because it is generative, not because the downstairs closure failed.

Hence

\[
\boxed{
\text{finite unresolved openness}
\ne
\text{infinite fair continuation}
\ne
\text{unbounded lift of a successful character}.
}
\]

The three permanent cusp labels give typed asymptotic readings:

- \(K\): fresh witness, construction, and vocabulary growth;
- \(X\): branching, placement, filling, and possible-world growth;
- \(t\): fair continuation, causal depth, and historical growth.

This marking is a working semantics.  A theorem must still identify the
corresponding parabolic orbits or cusp directions in a concrete
\(\mathbb H^2_{\mathrm{AM}}\) realization.

---

## 9. Finite calibration sequence

The first executable oracle is finite and requires no hyperbolic numerical
model.  Later stages must preserve the semantic/proof-theoretic separation.

### 9.1 Exact-halt and propositional fixture

1. enumerate the seven nonempty exact faces;
2. attach both quiescent and active machine records to every face;
3. verify that only the quiescent records inhabit `ExactHalt`;
4. generate the three atomic supports \(P_K,P_X,P_t\);
5. verify that their extensional Boolean closure has 128 propositions;
6. verify the positive conjunction law for all seven `Sat` requests;
7. provide an exact counterexample showing that a disjunction of requests is
   not one request; and
8. verify that face intersection leaves the seven-element scalar carrier.

The accompanying test implements this stage.

### 9.2 Finite semantic-entailment fixture

For finite premise supports \(\Gamma\) and conclusion support \(P\):

1. compute the common model support \(\operatorname{Mod}(\Gamma)\);
2. decide entailment by support inclusion;
3. return every counterexample world when inclusion fails;
4. keep inconsistency and empty-model support explicit; and
5. introduce no derivation or proof-search trace.

This remains a model-theoretic calibration.

The accompanying test now implements this finite semantic stage as well.

### 9.3 Predicate-language prerequisites and fibre diagnostic

Before calling any operation a quantifier, specify one finite typed predicate
language with terms, variables, substitution, free-variable support, binders,
and observer-indexed domains.

Only then use one coarse aperture with two fine filling histories.  One
filling receives a scoped closure certificate and the other retains an
obstruction.  The semantic fibre diagnostic should verify:

- existential projection has at least one compatible fine lift;
- universal projection does not contain the coarse point;
- dropping the obstructed residual changes the universal result and is
  rejected; and
- fuel exhaustion is distinct from an empty fibre.

This checks only the candidate adjunction semantics.  Introduction,
elimination, eigenvariable, and witness-discharge rules remain undefined.

### 9.4 Deferred proof-search fixture

Only after a proof calculus and independent model evaluator exist, use a
finite entailment task containing:

- one checked derivation branch;
- one independently checked countermodel branch;
- one budget-exhausted frontier.

Verify that the search returns typed orthogonal outcomes and never turns the
budget-exhausted branch into falsehood.  Dynamic modalities and least/greatest
fixed-point approximants may be studied only after this result is stable.

### 9.5 Threaded compactification fixture

Use a finite typed prefix tree with three permanent end labels, one
operational aperture, two alternative port pairings, and two histories with
the same coarse endpoint but distinct holonomy.  Verify that the proposed
boundary serializer retains:

- permanent versus operational boundary sorts;
- port types and cyclic order;
- both pairing alternatives;
- the holonomy distinction;
- the finite frontier as cylinders; and
- a successful sealed loop separately from its unbounded lifted ray.

This fixture calibrates the grammar of compactification.  It does not prove a
boundary equivalence with \(\partial\mathbb H^2\).

---

## 10. Decisive falsifiers

The proposal must be weakened or rejected if any of the following persists:

1. exact stable faces cannot be combined with quiescence into a compositional
   relative halt record;
2. the three atomic supports fail to distinguish the seven terminal worlds;
3. a proposed connective depends on representative history after the
   declared residual quotient;
4. conjunction, disjunction, implication, or duality requires silent copy,
   discard, branch erasure, or source identification;
5. semantic entailment is identified with derivability before a proof system
   and soundness theorem exist;
6. exploration changes the observer, vocabulary, or rules while reporting a
   derivation in the old logic;
7. quantifier rules, natural deduction, dynamic modalities, or fixed points
   are promoted before predicate syntax and semantic substitution laws;
8. finite vocabulary is taken to imply hyperbolicity without a geometric
   coding result;
9. compactification identifies permanent cusps with Failure apertures;
10. a cusp filled as a point erases thread direction, port order, pairing, or
    holonomy;
11. an unresolved finite frontier is promoted to the completed ideal
    boundary;
12. a successful sealed loop loses its nontrivial lifted continuation;
13. vocabulary refinement has no compatible map or correspondence between
    finite compacta; or
14. the compactified object cannot reopen from retained residual evidence.

---

## 11. Promotion boundary

Even a successful finite calibration establishes at most:

- seven observer-relative exact halt worlds in one declared carrier;
- one finite generated extensional proposition algebra;
- one decidable finite semantic-entailment relation with exact
  countermodels;
- semantic and proof-relevant obligations for future connective constructors;
- one syntax for a thread-respecting finite bordification record.

It does not establish:

- a seven-valued logic;
- a predicate language with checked substitution;
- a complete natural-deduction calculus;
- stable quantifiers or a hyperdoctrine;
- a general modal \(\mu\)-calculus for Adva;
- a universal machine;
- a canonical equivalence between the symbolic end boundary and
  \(\partial\mathbb H^2_{\mathrm{AM}}\);
- a theorem that the three bracket sorts are geometric cusps;
- a final compactification of every changing vocabulary; or
- authority to fill a permanent cusp, erase a thread, or forget a residual.

---

## 12. Immediate implementation order

1. retain the completed exact-halt and 128-proposition finite oracle without
   adding stable semantic types;
2. add finite semantic entailment and exact countermodel extraction over the
   seven halt worlds;
3. define one finite typed predicate language with variables, terms, binders,
   and capture-avoiding substitution;
4. test candidate existential/universal fibre semantics and the required
   substitution laws;
5. only then select natural deduction, sequent calculus, tableau, or another
   proof presentation and state soundness and relative-completeness targets;
6. define exploration as certificate search for that fixed entailment task;
7. separately define a research-local threaded-bordification record and test
   boundary-sort, port, pairing, holonomy, seal, lift, and reopen laws; and
8. only then choose a symbolic-to-hyperbolic coding and test whether it
   extends continuously to boundaries.

The first geometric target should not be a numerical compactification of an
arbitrary program space.  It should be one finite typed word system whose
end compactification and one marked hyperbolic realization can be compared
without losing any thread or aperture evidence.

## Conservative conclusion

The seven nonempty triadic faces supply a finite terminal-world carrier after
quiescence is added.  They do not by themselves supply seven truth values.
Propositions live over those worlds, and semantic entailment is finite support
inclusion.  Predicate terms, substitution, and fibre semantics must be built
before quantifiers are admitted.  Natural deduction comes later.  Exploration
first searches for a derivation, countermodel, or honest frontier in one fixed
entailment problem; dynamic and coinductive readings remain possible future
semantics for a mature search calculus.

A finite vocabulary gives compactness first at the level of coherent infinite
words or ends.  Hyperbolic compactification is a further representation
theorem.  The appropriate geometric object is not a bare surface with cusp
points filled in, but a marked thread-respecting bordification that retains
typed cusp directions, operational apertures, port orders, pairing choices,
holonomy, residuals, and the distinction between unresolved rays and
unbounded lifts of successful characters.

The resulting working principle is

\[
\boxed{
\text{finite language}
\to
\text{compact end space},
\qquad
\text{certified thread grammar}
\to
\text{admissible compactification},
\qquad
\text{exploration}
\to
\text{derivation, countermodel, or retained frontier}.
}
\]
