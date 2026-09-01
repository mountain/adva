# Logic as a Learned Characteristic

Status: conceptual research note following
[`0038-triadic-characteristic-inference-calibration.md`](0038-triadic-characteristic-inference-calibration.md)
and
[`0044-finite-triadic-satisfaction-logic.md`](0044-finite-triadic-satisfaction-logic.md).

This note develops one hypothesis:

> Logic appears early along a learning path because a proposition is a severe,
> stable characteristic of observation.  It keeps a distinction that can be
> transported and composed, while forgetting most of the process by which the
> distinction became observable.

The claim needs one immediate correction.  A single characteristic is not yet
a logic.  A proposition-like characteristic is a first **object** learned from
observations.  Entailment between characteristics is a first **relational**
characteristic.  A logic appears only after a family of such characteristics
is equipped with a justified order, operations, substitution, and possibly
proof objects.

The word “traditional” below is deliberately narrow.  It refers primarily to
the familiar extensional presentation of classical propositional and
first-order semantics, not to every historical or contemporary logic.  Proof
theory, intuitionistic logic, modal logic, linear logic, relevance logic,
dependent type theory, dynamic logic, and other systems recover different
parts of what the extensional presentation forgets.  The thesis is therefore
not that all logic erases the same data.  It is that every logic earns its
stability by declaring some data logically irrelevant.

This note introduces no stable Adva logic, observer, learning, proposition, or
topology API.  It records a conceptual decomposition and its falsifiable
boundaries.  Rust remains the semantic authority; the active `ProgramSlice`
priority is unchanged.

---

## 0. Executive distinction

Let a finite observer boundary be

\[
Q=(Q_t,Q_X,Q_K),
\]

where the three components bound temporal observation, spatial resolution,
and constructive access.  Let

\[
\mathcal O_Q
\]

be the observations available at that boundary.

The first characteristic should generally be written

\[
\chi_{U,Q}:\mathcal O_Q\longrightarrow\mathbb S,
\]

not as a total omniscient map from the open world to a discrete Boolean set.
Here \(\mathbb S\) is read in the Sierpinski sense:

- positive finite evidence can place an observation in \(U\);
- absence of positive evidence is not automatically evidence for the
  complement of \(U\).

A classical Boolean characteristic

\[
\bar\chi_{U,Q}:\mathcal O_Q\longrightarrow 2
\]

requires more: the observer must also recognize the complement, or explicitly
declare a Booleanization that forgets the distinction between “not yet
observed” and “observed false.”

The proposed learning order is therefore

\[
\boxed{
\text{positive characteristic}
\longrightarrow
\text{entailment order}
\longrightarrow
\text{logical operations}
\longrightarrow
\text{theory}.
}
\]

Logic is not the first bit returned by learning.  It is the first stable
calculus of such bits and of the refinements between them.

---

# Part I. What a characteristic does

## 1. From an event to a truth region

Suppose an observed event still has temporal, spatial, and constructive
coordinates:

\[
e=(t,x,k).
\]

A proposition-like observation maps many distinct events to one positive
reading:

\[
e\longmapsto\chi_{U,Q}(e)=1.
\]

Its positive extension is

\[
U_Q=\chi_{U,Q}^{-1}(1).
\]

This is already a quotient.  All events in \(U_Q\) agree with respect to one
question even when they disagree in every other available respect.

The characteristic retains:

- one observable distinction;
- the positive region on which that distinction holds;
- the possibility of comparing that region with other regions; and
- whatever invariance the observer contract guarantees.

It need not retain:

- how long recognition took;
- where inside the region the event occurred;
- which construction or proof supplied the evidence;
- how many different witnesses existed;
- which path reached the event;
- what the observer could not inspect; or
- whether a currently negative reading is false or merely unresolved.

This is why a logical characteristic can be extremely stable.  Stability is
obtained by refusing to distinguish most of the underlying events.

## 2. Characteristic, proposition, logic, and theory

Four levels should not be collapsed.

| level | finite-observer reading | additional structure |
|---|---|---|
| characteristic | one map \(\chi_{U,Q}\) | a positive distinction |
| proposition | a named or generated characteristic | syntax or provenance |
| logic | an ordered, compositional family of propositions | entailment and operations |
| theory | selected propositions accepted at one stage | axioms, data, or learned constraints |

Theories may change during learning while the transport laws of the logic
remain stable.  Conversely, a new observer may force a change of logic if it
introduces resources, modalities, or evidence distinctions that the old
operations cannot transport.

Thus “logic is a learned characteristic” is best sharpened to:

> proposition formation is an early characteristic inference; entailment is
> an early characteristic of relations between propositions; logic is their
> stable closure under declared operations.

## 3. The first relational characteristic

Given two observed positive regions \(U_Q\) and \(V_Q\), the simplest exact
comparison is inclusion:

\[
U_Q\preceq_Q V_Q
\quad\Longleftrightarrow\quad
U_Q\subseteq V_Q.
\]

This yields a preorder of observational strength.  If observation satisfying
\(U_Q\) always satisfies \(V_Q\), then \(U_Q\) carries at least as much
positive information as \(V_Q\).

This order is a semantic shadow of entailment.  It is not automatically a
constructive proof transformer.  To promote

\[
U_Q\subseteq V_Q
\]

to a proof-relevant judgment, one must also construct a uniform method that
turns evidence for \(U_Q\) into evidence for \(V_Q\).

The distinction is essential for Adva: equal output supports do not identify
program histories, and set inclusion does not manufacture a checked program.

---

# Part II. What extensional logic abstracts

## 4. Abstraction is the positive operation

To abstract is not merely to delete.  It is to select an invariant and make
operations on that invariant possible.

The familiar extensional logical view commonly abstracts:

1. a truth region from heterogeneous events;
2. a proposition from the sentences or constructions that present it;
3. an entailment order from many individual successful inferences;
4. a compositional algebra from repeated combinations of distinctions; and
5. substitution invariance from changes of irrelevant names or presentations.

This produces a language in which a finite expression can be interpreted in
many situations.  The expression is finite because it gives an intensional
rule, not because it enumerates the world extensionally.

For example, a finite formula may determine a region in an infinite model.
The formula does not contain every point of that region.  Syntax plus an
interpretation rule generates the extension.

## 5. The main forgetting map

The extensional truth projection may be pictured as

\[
\pi_Q:
\{
\text{histories, locations, constructions, evidence}
\}
\longrightarrow
\{
\text{logical readings}
\}.
\]

For a reading \(b\), the forgotten information is its fibre

\[
R_Q(b)=\pi_Q^{-1}(b).
\]

Traditional presentations usually work only with \(b\).  The current
research programme asks that a finite observer retain or reconstruct an
explicit description of \(R_Q(b)\) whenever later learning may split the
coarse reading.

This gives the accountable-forgetting pattern

\[
\boxed{
\text{logical abstraction}
=
\text{coarse invariant}
+
\text{declared forgotten fibre}.
}

The residual need not always be stored in full.  It may be represented by a
certificate, generator, ambiguity class, or honest `Unknown`.  What is ruled
out is silently treating the quotient as lossless.

## 6. A forgetting ledger

The following table describes the common extensional abstraction and the
conditions under which it is justified.

| source distinction | logical abstraction | commonly forgotten | justified when | failure if silently restored |
|---|---|---|---|---|
| many events | one truth region | point identity and local geometry | only membership matters | equal truth becomes equal event |
| many derivations | one consequence | proof identity and normalization path | proof irrelevance is declared | theorem equality becomes proof equality |
| many witnesses | existence | witness count and provenance | inhabitance alone is observed | existence becomes canonical construction |
| ordered search | eventual success | runtime, suspension, divergence | only completed success matters | non-observation becomes falsehood |
| resource use | unrestricted entailment | copy, discard, and cost | contraction/weakening are valid | unavailable duplication is assumed |
| observer boundary | fixed interpretation | calibration and resolution | observer is held constant | local truth becomes world-absolute truth |
| continuous/open evidence | Boolean value | boundary and unresolved cases | region is decidable or clopen | “not known” becomes “known not” |
| path transport | endpoint truth | monodromy and route dependence | transport is path-independent | equal endpoint becomes equal continuation |
| construction histories | extensional value | source and occurrence structure | future contexts ignore history | equal value becomes equal program |

No row is a universal accusation against logic.  Each row names a contract.
Different logical systems keep different columns.

## 7. What logic does not necessarily forget

The forgetting ledger also prevents a strawman.

- Proof theory can retain derivations and normalization.
- Intuitionistic logic can distinguish positive construction from Boolean
  complement.
- Linear and substructural logics can retain use, copy, and discard policies.
- Modal and dynamic logics can retain accessibility, time, or transition.
- Dependent type theories can retain structured witnesses.
- Topological and categorical semantics can retain locality and transport.

Each extension nevertheless makes its own quotient.  A proof term may retain
construction while still forgetting wall-clock history.  A temporal modality
may retain reachability while forgetting the exact implementation.  There is
no logic without an invariance declaration.

---

# Part III. Binarization and its price

## 8. Positive observation before Boolean truth

For an open or computably enumerable region, the natural characteristic is

\[
\chi_U:X\longrightarrow\mathbb S.
\]

A finite witness can establish membership in \(U\).  Failure to find a witness
does not necessarily establish membership in the complement.

This separates three readings:

| reading | meaning |
|---|---|
| positive | finite evidence has been observed |
| negative in a finite exhaustive fixture | all declared cases were checked and none succeeded |
| unresolved | the bounded search has not supplied either certificate |

Only the second reading licenses finite refutation.  The third must remain
`Unknown`.

## 9. Booleanization is a second abstraction

A map to the discrete Boolean object

\[
\bar\chi_U:X\to 2
\]

requires both \(U\) and its complement to be observable under the declared
contract.  Topologically, this is analogous to requiring a clopen or otherwise
decidable distinction.  Computationally, it requires a terminating decision
procedure on the declared input domain.

If an observer forces a Boolean answer without that contract, it performs a
second quotient:

\[
\{
\text{positive},
\text{refuted},
\text{unresolved}
\}
\longrightarrow
\{0,1\}.
\]

Which states are merged must be stated.  There is no observer-independent
canonical merge in the general open case.

## 10. Bivalence, completeness, and decidability

Three classical words must remain separate:

\[
\boxed{
\text{bivalence}
\ne
\text{semantic completeness}
\ne
\text{decidability}.
}

- Bivalence is a semantic claim about truth values.
- Completeness of a proof calculus says that every semantically valid formula
  in the declared semantics is derivable.
- Decidability says that an effective procedure terminates with the correct
  answer for every input in the declared domain.

First-order semantic completeness does not say that a finite observer can
decide every sentence, enumerate every model, or finitely encode all details
of an open world.  Incompleteness of sufficiently expressive effective
theories does not contradict completeness of first-order logic as a calculus.
The statements quantify over different objects.

---

# Part IV. Finite expression and open interpretation

## 11. Finite construction is not finite extension

Logic offers finite **construction rules** with open **interpretation**.
There are at least three different finiteness claims:

1. every individual formula has a finite construction;
2. the grammar or rule schema has a finite presentation; and
3. the full extension or class denoted by a formula is finite.

The first two do not imply the third.  A finite term can denote an infinite
set, and a finite formula can be evaluated in arbitrarily large structures.

This is the central response to the finite-observer problem.  The observer
does not finitely list the open world.  It learns a finite generator whose
meaning remains open under interpretation.

## 12. What finite expression cannot promise

No finite expression can extensionally contain every member and every detail
of an unrestricted proper class.  A finite rule may characterize such objects
only intensionally and relative to a metalanguage, semantics, or schema.

Likewise, no single finite logical language is automatically complete for all
future distinctions an open world may reveal.  New observations may:

- split an old truth region;
- expose witness-sensitive structure;
- invalidate contraction or proof irrelevance;
- require a modality or new sort; or
- reveal that a previous Booleanization merged `Unknown` with false.

The appropriate claim is therefore relative completeness:

> a calculus may be complete for a declared observer, syntax, and semantics,
> while remaining intentionally incomplete as a description of the world.

## 13. Generative compression

Logical abstraction is a form of generative compression:

\[
\text{finite syntax}
+
\text{interpretation rule}
\longmapsto
\text{possibly open extension}.
\]

Its power comes from three sources:

- variables range without enumerating all values;
- composition reuses finitely stated rules; and
- quantification summarizes families of instances.

Its price is equally structural: the denoted extension does not recover the
individual routes, costs, witnesses, or constructions that generated each
instance unless the logic explicitly retains them.

---

# Part V. Logic along a learning direction

## 14. Observer refinement

Let \(Q\preceq Q'\) mean that \(Q'\) is a finer observer.  Forgetting from the
fine observations to the coarse observations is a map

\[
q:\mathcal O_{Q'}\longrightarrow\mathcal O_Q.
\]

A coarse proposition \(U_Q\) can be re-read at the fine observer by inverse
image:

\[
q^*U_Q=q^{-1}(U_Q).
\]

If the finer observer only reveals alternatives inside the old positive
region, then the proposition is stable under learning.  For example,

\[
q^{-1}(P_{[I]})=P_I\lor P_{-I}
\]

in note 0044.  The finer observer does not refute projective closure; it splits
one coarse point into two lifted alternatives.

## 15. A tower rather than one final logic

The natural object is an observer-indexed tower

\[
\mathcal L_{Q_0}
\xleftarrow{q_{10}}
\mathcal L_{Q_1}
\xleftarrow{q_{21}}
\mathcal L_{Q_2}
\xleftarrow{}
\cdots.
\]

The arrows record how propositions are forgotten or reindexed.  The tower may
stabilize on some fragment without becoming globally final.

This separates two meanings of logical stability:

1. **theory stability:** particular accepted propositions survive refinement;
2. **calculus stability:** entailment and operations commute with observer
   transport.

The second is the deeper target.  A theory can learn new facts while the
calculus remains natural.  If transport fails, the residual identifies which
apparently logical operation depended on the old observer.

## 16. Three-domain reading of a proposition

For an event \((t,x,k)\), the same positive reading has three aspects:

- temporal: a search, execution, or normalization trace reaches evidence;
- spatial: the observed point lies in the proposition's extent;
- constructive: a witness or program realizes the proposition.

Projecting all three to one truth value gives useful stability but erases their
possible disagreement.  The 3-form proposal in note 0046 asks whether the
three aspects can remain coordinated long enough to generate logic before the
final truth projection is taken.

---

# Part VI. Claims, risks, and tests

## 17. Working hypotheses

The note proposes the following hypotheses, not theorems.

1. A positive observable characteristic is among the earliest stable products
   of learning.
2. Entailment or refinement order is the next stable relational
   characteristic.
3. Logic is the closure of generated characteristics, not an isolated bit.
4. Classical bivalence is often a later observer contract or Booleanization,
   not the primitive form of finite positive evidence.
5. Logical stability under learning is best expressed by transport across an
   observer tower with explicit residuals.
6. A finite expression handles an open interpretation by generative
   compression, not by extensionally representing the open world.

## 18. Decisive counterexamples

The framework should be revised if finite experiments show any of the
following.

- Learned characteristics do not precede or simplify the learned relation
  between observations.
- Entailment inclusion is unstable under every useful observer refinement.
- The residual fibres contain no information relevant to any future
  continuation.
- A single binary characteristic suffices without hidden treatment of
  unresolved observations.
- The proposed temporal, spatial, and constructive readings cannot be typed
  independently.
- Every proposed logical operation is already an arbitrary powerset operation
  unrelated to learned sections or transport.

## 19. Promotion boundary

Before this account becomes a formal system, it still needs:

1. a generated proposition syntax rather than arbitrary named subsets;
2. explicit proof or witness objects for entailment;
3. a treatment of incomplete search distinct from finite refutation;
4. observer reindexing laws and their residuals;
5. soundness relative to a declared satisfaction relation; and
6. a bounded completeness or counterexample result.

Until those exist, the correct conclusion is limited:

> Logic can be interpreted as a stable abstraction learned from
> characteristics, and its traditional extensional power can be explained by
> exactly which process details it declares irrelevant.  This interpretation
> does not yet constitute a new logic.

