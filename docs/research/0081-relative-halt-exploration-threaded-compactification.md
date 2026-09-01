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

The finite many-sorted syntax, capture-avoiding substitution, quantifier
fibres, and structural-induction adequacy theorem requested by this staging
are supplied in
[0082](0082-threaded-finite-logic-adequacy.md).  They remain research-local
and do not yet provide natural deduction or stable kernel types.

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

### 2.4 Working bivalent reading: true is a line, false is an empty hole

The proposed geometric reading of a Boolean value is local to a proposition
at a world.  Let \(H_A\) be the typed aperture posed by proposition \(A\), and
let

\[
\operatorname{Fill}_Q(H_A;h)
\]

be the fibre of admitted compatible threads at halt world \(h\).  Then the
first proof-relevant interpretation is

\[
\boxed{
\begin{aligned}
h\Vdash A
&\Longleftrightarrow
\operatorname{Fill}_Q(H_A;h)\text{ is inhabited},\\
h\Vdash \neg A
&\Longleftarrow
\operatorname{Fill}_Q(H_A;h)\text{ is certified empty}.
\end{aligned}
}
\]

An inhabitant is a line or thread that fills the typed hole.  Falsehood is
not the visual presence of a hole, but an exhaustiveness certificate that no
admitted thread can fill it.  A hole for which no line has yet been found and
whose fibre has not been exhausted is **Undecided**, not false.  The absence
of an aperture is a fourth structural situation and must not be confused with
an aperture having an empty fibre.

On the finite carrier \(H_7\), exhaustive enumeration makes this reading
bivalent pointwise:

\[
\operatorname{Fill}(H_A;h)
=
\begin{cases}
\{\text{a typed membership line}\},&h\in\llbracket A\rrbracket,\\
\varnothing,&h\notin\llbracket A\rrbracket.
\end{cases}
\]

Thus every pair \((A,h)\) has value true or false in the completed finite
model.  During a non-exhaustive search the observation may still be true,
false, or undecided.  This is not a third truth value: it is a statement
about the authority of the current search certificate.

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

At the present finite extensional level, the first candidate connectives are
operations on proposition supports:

\[
\llbracket A\land B\rrbracket
=
\llbracket A\rrbracket\cap\llbracket B\rrbracket,
\qquad
\llbracket A\lor B\rrbracket
=
\llbracket A\rrbracket\cup\llbracket B\rrbracket.
\]

This is the Boolean shadow that must be explained by, rather than silently
identified with, a later proof-relevant semantics.

### 3.1 Filling fibres and their Boolean shadow

For a proposition \(A\), define its support by forgetting every distinction
except whether its filling fibre is inhabited:

\[
\operatorname{Supp}_Q(A)
=
\left\{
h\in H_7:
\operatorname{Fill}_Q(A;h)\ne\varnothing
\right\}.
\]

This support map is a deliberate abstraction.  It forgets the number of
threads, their occurrences, histories, resources, port order, residuals, and
the difference between alternative witnesses.

The proposed fibre constructors are:

- \(A\land B\) requires compatible witness pairing and trace synchronization,
  so its filling is a compatibility-restricted product;
- \(A\lor B\) requires a retained branch tag and branch provenance, so its
  filling is a tagged sum;
- \(A\Rightarrow B\) requires a checked transformer from every admitted
  \(A\)-thread to a \(B\)-thread and later a discharge rule; and
- \(A^\star\) or \(\neg A\) requires outcome dualization to be well defined
  under admissible contexts, rather than mere failure to find an
  \(A\)-thread.

Schematically, before any term calculus is claimed,

\[
\begin{aligned}
\operatorname{Fill}(A\land B)
&\simeq
\operatorname{Fill}(A)\times_{\mathrm{compat}}
\operatorname{Fill}(B),\\
\operatorname{Fill}(A\lor B)
&\simeq
\operatorname{Fill}(A)+\operatorname{Fill}(B),\\
\operatorname{Fill}(A\Rightarrow B)
&\subseteq
\bigl(\operatorname{Fill}(A)\to\operatorname{Fill}(B)\bigr).
\end{aligned}
\]

The tagged sum gives the expected support law directly:

\[
\operatorname{Supp}_Q(A\lor B)
=
\operatorname{Supp}_Q(A)\cup\operatorname{Supp}_Q(B).
\]

Conjunction is more delicate:

\[
\operatorname{Supp}_Q(A\land B)
\subseteq
\operatorname{Supp}_Q(A)\cap\operatorname{Supp}_Q(B).
\]

Equality holds only when simultaneous inhabitation guarantees at least one
compatible pair:

\[
\forall h,\quad
\operatorname{Fill}_Q(A;h)\ne\varnothing
\land
\operatorname{Fill}_Q(B;h)\ne\varnothing
\Longrightarrow
\operatorname{Fill}_Q(A;h)
\times_{\mathrm{compat}}
\operatorname{Fill}_Q(B;h)
\ne\varnothing.
\]

This **compatible-pair completeness** can fail when two individually valid
threads consume the same linear source, disagree on an occurrence, or have
incompatible residual obligations.  In that case support intersection
over-approximates proof-relevant conjunction.

### 3.2 Truth, falsehood, implication, and negation

The unit and empty fibres are the candidates for truth and falsehood:

\[
\operatorname{Fill}_Q(\top;h)\simeq\mathbf 1,
\qquad
\operatorname{Fill}_Q(\bot;h)\simeq\mathbf 0.
\]

The unit contains a canonical identity thread.  The empty fibre belongs to a
declared aperture and carries an exhaustiveness certificate; it is not the
absence of an aperture.

An implication witness is an admissible total transformer:

\[
\operatorname{Fill}_Q(A\Rightarrow B;h)
=
\operatorname{Adm}_Q
\left(
\operatorname{Fill}_Q(A;h),
\operatorname{Fill}_Q(B;h)
\right).
\]

It must map every admitted \(A\)-thread to a \(B\)-thread while preserving the
declared type, source, occurrence, resource, and residual laws.  Consequently,

\[
\operatorname{Supp}_Q(A\Rightarrow B)
\subseteq
\bigl(H_7\setminus\operatorname{Supp}_Q(A)\bigr)
\cup
\operatorname{Supp}_Q(B).
\]

Equality requires **transformer completeness**: whenever the source is
certifiably empty or the target is inhabited, the grammar must provide an
admissible transformer.  Restricted resource or provenance laws may make the
inclusion strict even when the classical truth table says the implication is
true.

Negation is then defined rather than guessed:

\[
\neg A:=A\Rightarrow\bot.
\]

Its support is the Boolean complement only when certified empty fibres admit
the required refuter and the search is exhaustive:

\[
\operatorname{Supp}_Q(\neg A)
=
H_7\setminus\operatorname{Supp}_Q(A).
\]

The current \(H_7\) oracle assigns one canonical membership line to every
true proposition--world pair, makes those lines mutually compatible, and
enumerates every false pair exhaustively.  It therefore realizes the Boolean
equalities by construction.  This is a calibration fixture, not yet a theorem
about general Adva threads.

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
therefore remained semantic candidates until a finite predicate fixture
checked substitution and binding.  Note 0082 now supplies that first finite
fixture and proves its semantic adequacy under explicit Cartesian and
exhaustiveness hypotheses.  Stable observer-indexed quantifiers remain open.

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

In the line--hole reading, their proof-relevant candidates are dependent sum
and dependent product:

\[
\operatorname{Fill}(\exists x\,A(x))
\simeq
\sum_{x\in D_Q}\operatorname{Fill}(A(x)),
\qquad
\operatorname{Fill}(\forall x\,A(x))
\simeq
\prod_{x\in D_Q}\operatorname{Fill}(A(x)).
\]

Note 0082 implements these formulas for finite explicitly enumerated domains
and proves that fibre inhabitation matches Tarskian satisfaction.  They become
proof-theoretic quantifiers only after introduction, elimination,
eigenvariable, and witness-discharge rules are fixed.

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
Finite capture-avoiding substitution and its fibre naturality are established
in note 0082.  Observer-refinement substitution, Beck--Chevalley, Frobenius,
and stable reindexing laws remain open.  Quantifier introduction,
elimination, eigenvariable, and witness-discharge rules belong to the
still-later natural-deduction layer.

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

**C1a. Filling-status separation.**  The compactification must distinguish an
absent aperture, an aperture with a witnessed line, an exhaustively empty
filling fibre, and an unresolved fibre.  No limit operation may turn the last
case into falsehood merely by hiding its frontier.

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
   not one request;
8. verify that face intersection leaves the seven-element scalar carrier;
9. represent an inhabited fibre as true, an exhaustively empty fibre as
   false, and a non-exhausted empty observation as undecided; and
10. verify pointwise bivalence for all \(128\times7\) proposition--world
    pairs in the exhaustively enumerated finite carrier.

The accompanying test implements this stage.

### 9.2 Finite connective-fibre fixture

Use finite thread records with explicit exclusive-source sets:

1. verify that a conjunction contains only compatible thread pairs;
2. exhibit two inhabited fibres whose conjunction is empty because their
   only threads consume the same exclusive source;
3. verify that disjunction retains a left or right provenance tag;
4. accept an implication graph only when it maps every thread in an
   exhaustively enumerated source fibre to an admitted target thread;
5. reject partial and ill-typed implication graphs; and
6. accept vacuous implication from a certified empty source while rejecting
   the same claim for a merely unresolved source.

This fixture deliberately exhibits where the proof-relevant support laws can
be stricter than the Boolean truth tables.  It does not define stable Adva
connectives or natural-deduction rules.

The accompanying test now implements this finite diagnostic.

### 9.3 Finite semantic-entailment fixture

For finite premise supports \(\Gamma\) and conclusion support \(P\):

1. compute the common model support \(\operatorname{Mod}(\Gamma)\);
2. decide entailment by support inclusion;
3. return every counterexample world when inclusion fails;
4. keep inconsistency and empty-model support explicit; and
5. introduce no derivation or proof-search trace.

This remains a model-theoretic calibration.

The accompanying test now implements this finite semantic stage as well.

### 9.4 Predicate-language prerequisites and fibre diagnostic

Note 0082 now specifies one finite typed predicate language with terms,
variables, equality, capture-avoiding substitution, free-variable support,
binders, and explicitly enumerated domains.  It checks dependent-sum and
dependent-product quantifier fibres against finite Tarskian semantics.

The remaining observer-indexed diagnostic uses one coarse aperture with two
fine filling histories.  One
filling receives a scoped closure certificate and the other retains an
obstruction.  The semantic fibre diagnostic should verify:

- existential projection has at least one compatible fine lift;
- universal projection does not contain the coarse point;
- dropping the obstructed residual changes the universal result and is
  rejected; and
- fuel exhaustion is distinct from an empty fibre.

This checks only the candidate adjunction semantics.  Introduction,
elimination, eigenvariable, and witness-discharge rules remain undefined.

### 9.5 Deferred proof-search fixture

Only after a proof calculus and independent model evaluator exist, use a
finite entailment task containing:

- one checked derivation branch;
- one independently checked countermodel branch;
- one budget-exhausted frontier.

Verify that the search returns typed orthogonal outcomes and never turns the
budget-exhausted branch into falsehood.  Dynamic modalities and least/greatest
fixed-point approximants may be studied only after this result is stable.

### 9.6 Threaded compactification fixture

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
4. a bare unfilled aperture is called false without an empty-fibre
   certificate, or absence of an aperture is confused with an empty fibre;
5. support intersection is promoted to proof-relevant conjunction even when
   its only witness pairs are incompatible;
6. classical implication is asserted without a total admissible transformer,
   or vacuity is inferred from a non-exhausted source fibre;
7. conjunction, disjunction, implication, or duality requires silent copy,
   discard, branch erasure, or source identification;
8. semantic entailment is identified with derivability before a proof system
   and soundness theorem exist;
9. exploration changes the observer, vocabulary, or rules while reporting a
   derivation in the old logic;
10. quantifier rules, natural deduction, dynamic modalities, or fixed points
   are promoted before predicate syntax and semantic substitution laws;
11. finite vocabulary is taken to imply hyperbolicity without a geometric
   coding result;
12. compactification identifies permanent cusps with Failure apertures;
13. a cusp filled as a point erases thread direction, port order, pairing, or
    holonomy;
14. an unresolved finite frontier is promoted to the completed ideal
    boundary;
15. a successful sealed loop loses its nontrivial lifted continuation;
16. vocabulary refinement has no compatible map or correspondence between
    finite compacta; or
17. the compactified object cannot reopen from retained residual evidence.

---

## 11. Promotion boundary

Even a successful finite calibration establishes at most:

- seven observer-relative exact halt worlds in one declared carrier;
- one finite generated extensional proposition algebra;
- one line--hole realization of pointwise bivalence on an exhaustively
  enumerated carrier, with undecided search kept outside the truth values;
- one finite connective-fibre diagnostic that preserves disjunction tags and
  exposes compatibility and transformer-completeness obligations;
- one research-local finite many-sorted predicate fixture with
  capture-avoiding substitution and semantic adequacy, recorded in note 0082;
- one decidable finite semantic-entailment relation with exact
  countermodels;
- semantic and proof-relevant obligations for future connective constructors;
- one syntax for a thread-respecting finite bordification record.

It does not establish:

- a seven-valued logic;
- a stable kernel predicate language or observer-refinement substitution law;
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
2. calibrate inhabited, exhaustively empty, and unresolved filling fibres;
3. calibrate compatible products, tagged sums, and exhaustive total
   transformers while recording every strictness counterexample;
4. add finite semantic entailment and exact countermodel extraction over the
   seven halt worlds;
5. retain the completed research-local finite typed predicate language with
   variables, terms, equality, binders, and capture-avoiding substitution;
6. retain its finite existential/universal fibre adequacy checks, then extend
   them to observer-refinement substitution laws;
7. only then select natural deduction, sequent calculus, tableau, or another
   proof presentation and state soundness and relative-completeness targets;
8. define exploration as certificate search for that fixed entailment task;
9. separately define a research-local threaded-bordification record and test
   boundary-sort, port, pairing, holonomy, seal, lift, and reopen laws; and
10. only then choose a symbolic-to-hyperbolic coding and test whether it
   extends continuously to boundaries.

The first geometric target should not be a numerical compactification of an
arbitrary program space.  It should be one finite typed word system whose
end compactification and one marked hyperbolic realization can be compared
without losing any thread or aperture evidence.

## Conservative conclusion

The seven nonempty triadic faces supply a finite terminal-world carrier after
quiescence is added.  They do not by themselves supply seven truth values.
Propositions pose typed holes over those worlds.  A compatible thread
witnesses truth; a certified empty filling fibre witnesses falsehood; a
non-exhausted hole is undecided rather than false.  On the exhaustively finite
carrier this recovers pointwise bivalence.  Connectives first act on filling
fibres: compatible product for conjunction, tagged sum for disjunction, and
admissible total transformation for implication.  Their Boolean truth tables
are support-level shadows and require explicit compatibility, transformer,
and empty-fibre completeness.  Semantic entailment is finite support
inclusion.  Note 0082 supplies the first finite predicate terms,
capture-avoiding substitution, dependent-sum and dependent-product
quantifiers, and a structural-induction proof that filling inhabitation
matches finite Tarskian satisfaction.  Stable observer-indexed quantifiers and
natural deduction come later.  Exploration first searches for a derivation,
countermodel, or honest frontier in one fixed entailment problem; dynamic and
coinductive readings remain possible future semantics for a mature search
calculus.

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
\text{line / certified empty hole}
\to
\text{true / false},
\qquad
\text{exploration}
\to
\text{derivation, countermodel, or retained frontier}.
}
\]
