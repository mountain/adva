# Failure Frontiers and Observer-Relative Closure

Status: working research synthesis. This note records a proposal initiated by
Mingli Yuan and connects it to
[0066](0066-self-dual-characteristic-completion-calculus.md),
[0079](0079-typed-hole-open-close-calibration-v0.md),
[0080](0080-finite-surface-universal-lift-imagination.md), and
[0088](0088-historical-distributivity-character-v0.md).

The proposal is motivated by Gold-style identification in the limit, PAC
learning, prefix-free halting probability, and the exact finite Omega
approximations of Calude and Dinneen. It introduces no stable API, semantic
type, right-to-forget judgment, open logic, probability semantics, or
universality claim.

The central conclusion is:

> Failure is first a structured residual aperture on a prefix boundary.
> A scalar error is only an observer-relative measure or bound on that
> aperture. Closure need not remove the aperture; it must prove that the
> remaining legal fillings cannot alter the requested feature.

---

## 0. Executive result

Let

\[
T=2^{<\omega}
\]

be the binary prefix tree, with Cantor boundary

\[
\partial T=2^\omega.
\]

A finite prefix \(p\) determines the cylinder

\[
[p]=\{x\in2^\omega:p\prec x\},
\qquad
\lambda([p])=2^{-|p|}.
\]

For a universal prefix-free machine \(U\), define the effectively open halting
region

\[
\mathcal H_U
=
\bigcup_{U(p)\downarrow}[p].
\]

Its measure is

\[
\Omega_U
=
\lambda(\mathcal H_U)
=
\sum_{U(p)\downarrow}2^{-|p|}.
\]

This separates four levels that must not be identified:

| level | object |
|---|---|
| native boundary | infinite paths \(2^\omega\) |
| open region | the c.e. open halting set \(\mathcal H_U\) |
| measured feature | \(\Omega_U=\lambda(\mathcal H_U)\) |
| coordinate presentation | a real-number or hyperbolic-boundary chart for \(\Omega_U\) |

The map

\[
\mathcal H_U\longmapsto\lambda(\mathcal H_U)
\]

forgets which programs halt, where their cylinders lie, how they halt, and
which proofs or simulations established the result. Its fibres are large.
Therefore \(\Omega_U\) is a one-dimensional characteristic of the halting
geometry, not the complete geometry.

A finite observer should instead retain a sandwich aperture

\[
\boxed{
L_t\subseteq X\subseteq U_t,
\qquad
A_t=\operatorname{Frontier}(U_t\setminus L_t),
}
\]

where \(L_t\) is the witnessed lower region, \(U_t\) is a certified possible
upper region, and \(A_t\) is a prefix-free unresolved frontier.

The local three-form is

\[
\boxed{
\operatorname{Must}
\mid
\operatorname{Unknown}
\mid
\operatorname{May}.
}
\]

---

## 1. Four different failures

The word failure is too coarse unless its role is recorded.

| failure | meaning | required response |
|---|---|---|
| semantic failure | the current hypothesis is false | counterexample or witnessed residual |
| epistemic failure | the observer does not yet know which completion is true | retain an unresolved frontier |
| certificate failure | the claim may be true but the bound or invariance proof is absent | refuse closure |
| implementation failure | a simulator, filter, or proof checker may have misclassified a case | distrust the transition or add a separate risk model |

For a true object \(L\) and current hypothesis \(H_t\), the extensional
difference is

\[
R_t^+=L\setminus H_t,
\qquad
R_t^-=H_t\setminus L.
\]

A finite observer generally does not possess these exact sets. It possesses
witnessed subsets and a cover of what remains possible. The honest finite
record is therefore closer to

\[
\mathcal F_t=
\left(
W_t^+,
W_t^-,
A_t,
\operatorname{CoverCert}_t,
\mu_t,
g_t,
Q_t,
M_t,
\operatorname{Trace}_t
\right),
\]

where:

- \(W_t^+\subseteq R_t^+\) and \(W_t^-\subseteq R_t^-\) are witnessed
  residuals;
- \(A_t\) is a finite or finitely presented prefix-free unknown frontier;
- \(\operatorname{CoverCert}_t\) states what unresolved cases are covered by
  \(A_t\);
- \(\mu_t\) is the declared observer measure;
- \(g_t\) is an exact mass or certified upper bound;
- \(Q_t\) is the observation policy;
- \(M_t\) is the closure modality; and
- \(\operatorname{Trace}_t\) retains refinement, witness, pruning, and
  implementation history.

Implementation risk does not belong silently inside \(W_t^-\). A heuristic
nonhalting classification is not a negative proof.

---

## 2. Prefix-free residual geometry

If unresolved prefixes are stored without normalization, a parent and its
child may be counted twice. The visible unknown frontier must therefore be a
prefix-free antichain \(A_t\). Its Kraft capacity is

\[
\kappa(A_t)
=
\sum_{q\in A_t}2^{-|q|}.
\]

Three distinctions are mandatory:

\[
\text{residual set}
\ne
\text{prefix cover}
\ne
\text{Kraft capacity}.
\]

In general, if the unresolved residual is \(R_t\),

\[
R_t\subseteq[A_t]
=
\bigcup_{q\in A_t}[q],
\qquad
\mu(R_t)\leq\kappa(A_t).
\]

Equality requires an exact partition or coverage certificate. Consequently,
the phrase "error is the Kraft mass of the hole" is valid only after the
measure, cover, and equality or upper-bound status have been declared.

Two frontiers may have equal Kraft capacity but different branch locations,
shapes, refinement histories, and interactions with later observations. This
fibre under the scalar mass is a natural location for retained history,
holonomy, and eventually curvature hypotheses.

---

## 3. Refinement is not evidence

Replacing an unresolved prefix \(q\) by its children satisfies

\[
2^{-|q|}
=
2^{-|q0|}
+
2^{-|q1|}.
\]

Thus

\[
\operatorname{Refine}(q)
:
\{q\}
\longmapsto
\{q0,q1\}
\]

changes spatial resolution without decreasing total uncertainty.

Only evidence may move or remove mass:

- a positive witness moves a certified region from Unknown to Must;
- a negative proof or syntactic impossibility certificate removes a certified
  region from May;
- an observer refinement changes which distinctions are visible;
- a heuristic classification remains provisional and cannot authorize exact
  pruning.

This gives an exact interpretation of the earlier thread and patch language.
An unresolved prefix is simultaneously:

1. a boundary cylinder, hence an aperture;
2. a finite path, hence an unfinished thread; and
3. a family of infinite extensions, hence its possible fillings.

Therefore

\[
\boxed{
\text{aperture}
=
\text{unresolved extension space},
\qquad
\text{thread}
=
\text{one selected extension}.
}
\]

Merely drawing more thread does not close the aperture. A closure witness must
show why the remaining extensions no longer matter to the declared question.

---

## 4. Completion space and the closure judgment

Let the finite evidence and constraints determine

\[
\operatorname{Fill}(\mathcal F_t)
=
\left\{
X:
L_t\subseteq X\subseteq U_t,\;
X\models C_t
\right\}.
\]

For an observer \(Q\) and feature map \(\chi_Q\), define feature closure by

\[
\boxed{
\operatorname{FeatureClose}_Q(\mathcal F_t,y)
\iff
\chi_Q\left(\operatorname{Fill}(\mathcal F_t)\right)
=
\{y\}.
}
\]

Equivalently,

\[
\forall X_1,X_2\in\operatorname{Fill}(\mathcal F_t),
\qquad
\chi_Q(X_1)=\chi_Q(X_2)=y.
\]

The aperture may remain nonempty. What closes is the observer-relative
question.

This yields the principle:

\[
\boxed{
\text{the world remains open while a feature becomes closed}.
}
\]

A close result must therefore retain the unresolved frontier and a reopen
handle. If a finer observer \(Q'\) separates two legal fillings, the prior
feature close reopens without becoming false at \(Q\).

---

## 5. Closure modalities

At least five modalities must remain distinct.

| modality | acceptance condition |
|---|---|
| ObjectClose | all legal fillings determine the same complete object under the declared identity |
| FeatureClose(Q) | all legal fillings have the same \(Q\)-feature |
| PACClose | object-level error is at most \(\varepsilon\) under a declared measure, with certificate failure probability at most \(\delta\) |
| LimitClose | a monotone approximation converges, but no certified stabilization stage is claimed |
| TheoryClose(T) | an explicit theory \(T\) proves the required upper bound, exclusion, or feature invariance |

No modality may be silently strengthened. In particular:

\[
\operatorname{LimitClose}
\not\Rightarrow
\operatorname{ObjectClose},
\]

and

\[
\operatorname{PACClose}_{\mu,\varepsilon,\delta}
\not\Rightarrow
\operatorname{FeatureClose}.
\]

PACClose must keep two probabilities separate:

- \(\varepsilon\) measures object-level error under the instance measure;
- \(\delta\) bounds failure of the statistical certificate or learning
  procedure.

A probability on instances must not be reinterpreted as a probability on
possible completions unless a second model explicitly supplies that measure.

---

## 6. Gold: convergence without an announced closing time

Gold's identification in the limit permits a learner to make finitely many
wrong conjectures and eventually stabilize. It does not generally require the
learner to know when stabilization has occurred. Under positive presentation,
an unseen positive example may appear arbitrarily late.

The corresponding open-logic constraint is

\[
\boxed{
\text{positive trace alone cannot authorize exact object closure}.
}
\]

This is class-relative. A finite tell-tale, finite elasticity condition, or
additional negative information may support stronger conclusions. The claim
must not be stated as an impossibility for every positive-data learning
problem.

Reference:

- E. Mark Gold,
  [Language Identification in the Limit](https://doi.org/10.1016/S0019-9958(67)91165-5),
  *Information and Control* 10 (1967), 447--474.

---

## 7. PAC: measured closure

PAC learning changes the requested judgment. It does not require recovery of
the complete target set. It requires a small symmetric difference under a
declared distribution, with high confidence:

\[
\mu(H_t\triangle L)\leq\varepsilon
\]

with confidence at least \(1-\delta\).

In the present vocabulary, this is not a point closure of the boundary. It is
a closure in a measure-relative quotient, with the low-mass residual retained.

Valiant's original 1984 formulation used positive examples, optional
membership queries, and important one-sided-error cases. The modern symmetric
PAC vocabulary is a later generalization. The structural lesson survives, but
the historical models must not be conflated.

Reference:

- Leslie G. Valiant,
  [A Theory of the Learnable](https://www.cs.princeton.edu/courses/archive/spring08/cos511/handouts/valiant.pdf),
  *Communications of the ACM* 27 (1984), 1134--1142.

---

## 8. Omega tails and feature closure

At time \(T\), the observed halting mass is

\[
\Omega_{U,T}
=
\sum_{U(p)\downarrow\text{ by }T}2^{-|p|}.
\]

For a sound simulator this produces only false negatives:

\[
\Omega_U
=
\underbrace{\Omega_{U,T}}_{\text{witnessed halting mass}}
+
\underbrace{\Delta_T}_{\text{unseen halting mass}}.
\]

The sequence is increasing,

\[
\Omega_{U,T}\uparrow\Omega_U,
\]

but in general has no computable convergence modulus.

The stronger finite structure is an interval

\[
L_t\leq\Omega_U\leq U_t,
\]

where \(U_t\) is justified by a prefix cover, machine syntax, nonhalting
proofs, or certified tail estimates.

To close the first \(n\) bits, it is unnecessary to prove \(L_t=U_t\). It is
enough to prove that the whole interval lies inside one canonical dyadic cell

\[
C_{n,k}
=
\left[
\frac{k}{2^n},
\frac{k+1}{2^n}
\right),
\]

subject to an explicit convention for dyadic boundary expansions.

Then

\[
\operatorname{prefix}_n(x)=k
\qquad
\text{for every }x\in[L_t,U_t].
\]

This is precisely FeatureClose(prefix-n) with a nonzero residual aperture.

Calude and Dinneen compute lower bounds by enumerating halting programs and
machine-specific upper bounds by covering all remaining possible halting
extensions of extendable prefixes. Their result obtains finitely many exact
bits for two presentations of one compact universal prefix-free machine. It
does not give a general procedure for arbitrarily many Omega bits or solve the
halting problem.

Reference:

- Cristian S. Calude and Michael J. Dinneen,
  [Exact Approximations of Omega Numbers](https://calude.net/cristianscalude/cristianAssets/pdf/approxcompactIJBC.pdf),
  *International Journal of Bifurcation and Chaos* 17 (2007), 1937--1954.

Calude and Stay add a computable prior on runtimes and derive effective
probability bounds for sufficiently late halting. The prior is part of the
judgment; there is no observer-free meaning of "most programs stop quickly."

Reference:

- Cristian S. Calude and Michael A. Stay,
  [Most Programs Stop Quickly or Never Halt](https://arxiv.org/abs/cs/0610153).

---

## 9. Hyperbolic boundary interpretation

The prefix tree is Gromov hyperbolic and its boundary is Cantor space.
Therefore the halting region is natively an open subset of a hyperbolic
boundary, while \(\Omega_U\) is its measure characteristic.

After choosing a chart, the real number \(\Omega_U\in(0,1)\) may itself be
drawn as an ideal boundary coordinate of \(\mathbb H^2\). This is a second
presentation, not the native construction.

Moreover, \(\Omega_U\) is generally not a classical cusp of
\(PSL_2(\mathbb Z)\). Modular cusps are rational points and infinity, whereas
an Omega number is machine-dependent, left computably enumerable, and
algorithmically random. Safer terms are:

- algorithmically inaccessible ideal point;
- random ideal endpoint; or
- non-effective boundary coordinate.

The machine subscript is mandatory:

\[
\Omega_U,
\quad\text{not an absolute }\Omega.
\]

Changing \(U\) changes the chart or coding presentation. A more invariant
research target may be a class of left-c.e. random boundary points, together
with their reducibility or Solovay structure.

---

## 10. Reading by the three computers

The construction can be distributed without treating the three readings as
independent programs:

| reading | role |
|---|---|
| construction \(K\) | supplies the prefix grammar, program tree, cylinders, and refinement rule |
| time \(C\) | executes finite histories and produces positive or negative evidence |
| frontier \(F\) | organizes boundary apertures, measures them, and tests observer-relative feature closure |

Thus

\[
(K\text{-prefix construction})
+
(C\text{-evidence history})
\longrightarrow
(F\text{-boundary characteristic}).
\]

The frontier feature is obtained from the opposite interaction of construction
and time. Its scalar randomness records the impossibility of recovering the
complete process geometry from the compressed feature.

---

## 11. Consequence for the current historical character

The implementation in 0088 establishes:

- one common exact polynomial characteristic for two checked programs;
- both complete process residuals;
- fresh typed finite reuse;
- an occurrence-observer reopen witness; and
- explicit refusal of program identity, equation cells, source quotient, and
  provenance erasure.

It does not yet supply:

- an unknown frontier \(A\);
- a legal completion space \(\operatorname{Fill}(A)\);
- a coverage certificate for all completions in scope;
- a closure modality; or
- an invariance certificate proving that every legal completion has the same
  characteristic.

The current result proves pairwise and finitely instantiated statements such
as

\[
\chi(P)=\chi(Q).
\]

It does not yet prove

\[
\forall X\in\operatorname{Fill}(A),
\qquad
\chi(X)=N.
\]

Therefore HistoricalCharacterV0 is presently a reusable marked witness, not a
complete observer-relative aperture closure.

The stronger proposed record is

\[
\boxed{
\operatorname{ApertureCharacter}
=
\left(
\chi,Q,L,U,A,
\operatorname{CoverCert},
\operatorname{InvariantCert},
\mu,M,R,H
\right).
}
\]

This record remains only a proposal. In particular, the completion space must
be finitely presented and independently checked before it can authorize any
close result.

---

## 12. Relationship to learning and proof

The new judgment sharpens the proposed duality.

Learning narrows or restructures the completion space:

\[
\operatorname{Fill}(\mathcal F_0)
\supseteq
\operatorname{Fill}(\mathcal F_1)
\supseteq
\cdots.
\]

Proof establishes that the requested feature is constant on the current
completion space:

\[
\chi_Q\left(\operatorname{Fill}(\mathcal F_t)\right)=\{y\}.
\]

They may share one characteristic kernel, but this is not yet strict
self-duality. Learning transforms evidence and constraints; proof supplies a
universal invariance certificate over the remaining legal fillings. A theorem
would still need an explicit contravariant construction or adjunction relating
these processes.

Imagination also receives a precise role. It generates or explores legal
fillings of an open frontier. It does not grant them truth. A feature may close
only when all admissible imagined fillings agree under the declared observer.

---

## 13. Red-team boundary

The proposal fails if it permits any of the following:

1. replacing the frontier by its Kraft mass;
2. calling a prefix cover the exact residual without a coverage certificate;
3. counting non-prefix-free cylinders additively;
4. treating refinement as uncertainty reduction;
5. pruning a branch on heuristic simulation alone;
6. converting Gold limit convergence into an announced exact closing time;
7. omitting \(\mu,\varepsilon,\delta\) from a probabilistic close;
8. mixing instance-space probability with probability over completions;
9. calling pairwise feature equality invariance over all legal fillings;
10. treating feature closure as program identity or an equation cell;
11. identifying an Omega coordinate with a classical modular cusp;
12. suppressing the machine subscript on \(\Omega_U\);
13. assigning a deck transformation to a lossy feature projection; or
14. inferring open-logic completeness or universal computation from a finite
    prefix experiment.

---

## 14. Conservative conclusion

The two source discussions support one coherent first judgment for a finite
observer's open logic:

\[
\boxed{
\text{close a feature exactly when every legal filling of the retained
failure aperture has the same observed feature}.
}
\]

The residual need not be empty. Its shape, measure, observer, modality, and
history remain attached. A finer observer may reopen the feature by separating
fillings that the former observer could not distinguish.

This is stronger than approximate agreement and weaker than complete-object
knowledge. It explains how a finite observer can reach stable vocabulary
without pretending that the open world has become finite or fully known.
