# Threaded Natural Deduction and the Entailment Triangle Cell

Status: research-local ordered implicational natural-deduction fixture,
finite soundness calibration, replayable bounded-search audit, and promotion
boundary following
[0081](0081-relative-halt-exploration-threaded-compactification.md),
[0082](0082-threaded-finite-logic-adequacy.md), and
[0083](0083-triadic-conflict-aperture-completion.md).

No stable Adva formula, context, proof term, entailment-cell type, search
operation, certificate, logical symbol, or Rust API is introduced here.
The executable companion is a self-contained Python research test. Its local
identifiers are test coordinates and are not Rust-owned `SourceId`,
`OccurrenceId`, or `ProofObject` values.

This note records the first explicitly proof-theoretic step proposed by
Mingli Yuan:

> Proof construction, model space, and fair exploration should form a
> triadic entailment cell. A successful proof must close the three readings
> coherently; a countermodel, resource conflict, and open search frontier must
> remain different outcomes.

The main correction is that two different triangular cells are now in view:

1. an **entailment coherence cell** compares a proof construction, its model
   interpretation, and a checked search history; and
2. the **linear-conflict completion cell** of note 0083 resolves two actual
   occurrences competing for one linear source.

They are not identified. Talking about the same entailment task or formula is
shared provenance, not shared resource consumption.

---

## 0. Executive result

Fix one entailment task

\[
q=(\Gamma\Rightarrow A;\mathcal L,\Sigma,Q).
\]

The three meta-level readings are

\[
K_q=\operatorname{Der}_K(\Gamma,A),
\qquad
X_q=\operatorname{Val}_{H_7}(\Gamma,A),
\qquad
t_q=\operatorname{SearchTrace}_K(q)
\times\operatorname{ModelScan}_{H_7}(q).
\]

Thus \(t_q\) is a paired audit object, not merely the event that first found a
proof. The first positive cell has boundary

\[
\begin{array}{ccc}
&\tau\in t_q&\\
{\scriptstyle\operatorname{extract}_K}\swarrow
&&
\searrow{\scriptstyle\operatorname{direct}_X}\\
\pi\in K_q
&\xrightarrow{\operatorname{sound}_{H_7}}&
e\in X_q^+ .
\end{array}
\]

Its filler asserts that:

1. the proof-search trace replays and extracts exactly \(\pi\);
2. recursive rule soundness erases \(\pi\) to one seven-bit sequent-support
   mask;
3. the exhaustive model scan yields a second mask; and
4. the two masks agree.

The two computations use the same declared Boolean interpretation. They are
structurally different certificate constructions, not independent semantic
implementations.

The first proof calculus is deliberately smaller than ordinary natural
deduction. It has:

- singleton assumption;
- ordered right linear-implication introduction;
- source-disjoint right linear-implication elimination; and
- no implicit weakening, contraction, or exchange.

For this fragment, structural induction first proves soundness over all eight
Boolean valuations and then restricts to \(H_7\):

\[
\boxed{
\Gamma\vdash_K A
\Longrightarrow
\lvert\Gamma\rvert\models_{2^3}\lvert A\rvert
\Longrightarrow
\lvert\Gamma\rvert\models_{H_7}\lvert A\rvert.
}
\tag{S}
\]

Boolean entailment does not imply \(\mathrm{TND}_0\) derivability. The Boolean
model forgets resources, while the proof calculus preserves them.

A checked countermodel instead closes a negative \(X\)-\(t\) cell:

\[
\operatorname{Cex}_{H_7}(q)
=
\sum_{h\in H_7}
[h\models\Gamma]
\times
[h\not\models A].
\]

Under theorem (S), positive proofs and countermodels are orthogonal:

\[
\operatorname{Der}_K(q)
\times
\operatorname{Cex}_{H_7}(q)
\longrightarrow
\mathbf 0.
\]

Budget exhaustion with work remaining is `Frontier`; exhaustion of both
finite declared lists is `SearchExhausted`. Neither is falsehood,
non-derivability, nor an `Omega`-type boundary.

---

## 1. Two layers of proof theory

The existing finite semantics and the threaded proof calculus should not be
forced into one undifferentiated logic.

### 1.1 The classical \(H_7\) support layer

Let

\[
D=\{K,X,t\},
\qquad
H_7=\{h_S:\varnothing\ne S\subseteq D\}.
\]

Each \(h_S\) is the valuation

\[
h_S(P_d)=1
\Longleftrightarrow
d\in S.
\]

Excluding the all-false valuation is enforced by the background formula

\[
T_{H_7}:=P_K\lor P_X\lor P_t.
\]

Hence \(H_7\)-validity is not unrestricted three-atom classical validity.
For example,

\[
\models_{H_7}T_{H_7},
\qquad
\not\models_{\mathrm{CPL}}T_{H_7}.
\]

Fix any standard sound-and-complete classical natural-deduction calculus
\(\mathrm{CND}_{\mathrm{CPL}}^{\mathrm{cl}}\), for example intuitionistic
natural deduction plus reductio ad absurdum. Let

\[
\mathrm{CND}_{H_7}^{\mathrm{cl}}
=
\mathrm{CND}_{\mathrm{CPL}}^{\mathrm{cl}}+T_{H_7},
\]

where the context is Cartesian and \(T_{H_7}\) is a separate background
assumption, not the classical control rule. Before applying classical
completeness, erase the threaded syntax:

\[
\lvert P_d\rvert=P_d,
\qquad
\lvert A\multimap_RB\rvert
=
\lvert A\rvert\to\lvert B\rvert,
\]

and let \(\lvert\Gamma\rvert\) forget source, occurrence, domain, order, and
multiplicity authority while retaining the erased formulae. Standard
classical propositional completeness then yields the relative corollary

\[
\boxed{
\lvert\Gamma\rvert\models_{H_7}\lvert A\rvert
\Longleftrightarrow
\lvert\Gamma\rvert,T_{H_7}
\vdash_{\mathrm{CND}_{\mathrm{CPL}}^{\mathrm{cl}}}\lvert A\rvert.
}
\tag{C}
\]

Indeed,

\[
\lvert\Gamma\rvert\models_{H_7}\lvert A\rvert
\Longleftrightarrow
\lvert\Gamma\rvert,T_{H_7}
\models_{\mathrm{CPL}}\lvert A\rvert,
\]

and theorem (C) follows from the ordinary soundness and completeness theorem
for classical propositional logic.

This is a theorem about the proof-irrelevant support shadow. It assumes the
ordinary structural rules and classical control. The current fibre semantics
does not yet provide proof-relevant continuations, choice certificates, or a
uniform interpretation of classical control.

### 1.2 The threaded construction layer

The first proof-relevant calculus is an ordered linear fragment
\(\mathrm{TND}_0\). In V0, raw contexts are strictly associative finite ordered
sequences: tuple concatenation installs associativity definitionally but does
not install exchange. The proof tree separately retains the bracketing of rule
composition. Associativity of future 0083 filled-cell composition is not
derived from raw tuple associativity.

This layer does not inherit theorem (C). Ordinary Boolean completeness is not
resource-sensitive completeness.

The intended long-term relation is therefore

\[
\mathrm{TND}_0
\xrightarrow{\text{forget resources}}
\mathrm{CND}_{H_7}^{\mathrm{cl}},
\]

not an equality of calculi.

---

## 2. Formulae, identities, and judgments

The executable fragment uses

\[
A,B::=P_K\mid P_X\mid P_t\mid A\multimap_R B.
\]

This restriction makes the grade invariant total on the executable proof
language. \(T_{H_7}\) and ordinary classical connectives live in the erased
support language; no proof-relevant tensor, additive, or bottom constructor is
claimed here.

An open assumption occurrence is

\[
a=
(x:A;
\operatorname{ProvId}p,
\operatorname{ResourceSourceId}s,
\operatorname{OccurrenceId}o,
\operatorname{ScopeId}u,
\operatorname{DomainId}d).
\]

The entailment problem separately carries \(\operatorname{TaskId}q\).
`TaskId`, `ProvId`, `ResourceSourceId`, `OccurrenceId`, `ScopeId`,
and `BinderId` are tagged nominal types. They are pairwise distinct sorts;
this is not a claim that their underlying display strings must have unequal
characters.

- `TaskId` identifies the whole \(K\)-\(X\)-\(t\) entailment audit.
- `ProvId` identifies the historical or evidential origin of one hypothesis;
  different hypotheses in one task may have different provenance.
- `ResourceSourceId` identifies a resource that may be consumed only under a
  declared source law.
- `(ScopeId, OccurrenceId)` identifies one globally fresh use position in the
  V0 proof tree.
- `BinderId` records the discharge that changed one use from open to bound.

The executable V0 chooses the simple global-freshness discipline: premise
ledgers must be disjoint even for already discharged uses. Future substitution
may add explicit alpha-freshening; it is not performed implicitly here.

There are also three different triples which must not be identified:

1. the meta-level proof/model/search vertices \(K_q,X_q,t_q\);
2. the Boolean coordinates \(P_K,P_X,P_t\); and
3. the resource `DomainId` values used by note 0083.

An explicit calibration map among these sorts is deferred. In particular, a
hypothesis whose formula is \(P_K\) may carry resource domain \(X\) in a test
without asserting \(P_K=X\). The companion represents Boolean coordinates and
resource domains by distinct runtime enum types, even though both display the
labels \(K,X,t\).

The judgment form is

\[
\Gamma\vdash_K M:A\;\blacktriangleright\;\Lambda,
\]

where \(\Gamma\) is an ordered open context and \(\Lambda\) is an audit
ledger containing every resource use, including its full hypothesis,
open/discharged status, binder, order, and residual data. Discharge changes
status; it never deletes resource identity. The executable V0 keeps these
data in the proof tree and frozen records; it does not allocate stable Adva
semantic identities.

---

## 3. The first ordered natural-deduction rules

### 3.1 Assumption

\[
\frac{\ }{
x:A[s,o,d]\vdash_K x_o:A
}
\;(\mathrm{Ax}).
\]

The context is exactly the singleton occurrence. There is no rule

\[
\Gamma,x:A\vdash x:A
\]

with an unused \(\Gamma\). Such a rule would install weakening silently.

### 3.2 Right linear-implication introduction

\[
\frac{
\Gamma\circ x:A[s,o,d]
\vdash_K M:B
}{
\Gamma
\vdash_K
\lambda^R x_o.M:A\multimap_R B
}
\;(\multimap_R I).
\]

The discharged occurrence must be the right boundary occurrence and must be
open exactly once. Discharge does not erase its history; it changes a free
resource obligation into a bound audit record.

Discharging an interior occurrence would require an exchange or braid
certificate. No such structural rule is assumed here.

### 3.3 Right linear-implication elimination

\[
\frac{
\Gamma\vdash_K F:A\multimap_R B
\qquad
\Delta\vdash_K N:A
\qquad
\operatorname{Src}(\Lambda_F)
\cap
\operatorname{Src}(\Lambda_N)=\varnothing
}{
\Gamma\circ\Delta
\vdash_K
\operatorname{app}^R(F,N):B
}
\;(\multimap_R E).
\]

All scoped occurrence identifiers and binder identifiers in the two complete
ledgers must also be disjoint, including already discharged uses. The
conclusion preserves left-to-right open-context order.

The recursive proof checker reconstructs the conclusion, ordered context,
principal occurrence, binder, complete resource ledger, and premise relation.
It additionally checks

\[
\operatorname{Open}(\Lambda_\pi)=\Gamma_\pi.
\]

Stored dataclass fields alone are not proof authority. This blocks a
contraction from being hidden behind an earlier discharge.

### 3.4 Structural rules are obligations

The absent structural rules have explicit future certificate shapes:

| rule | required evidence |
|---|---|
| weakening | `DropCert(s)` |
| contraction | `CopyCert(s -> s_1,s_2)` |
| exchange | ordered braid or swap certificate |
| filled-cell associativity | ledger- and residual-preserving associator |

The common lift of note 0083 consumes a shared source once and supplies two
coherent projections. It is not a `CopyCert` and does not derive contraction.

---

## 4. Erased Boolean model space \(X\)

For \(h_S\in H_7\), define

\[
\begin{aligned}
h_S\models P_d
&\Longleftrightarrow d\in S,\\
h_S\models A\multimap_R B
&\Longleftrightarrow
h_S\not\models A\text{ or }h_S\models B.
\end{aligned}
\]

Material implication appears only after resource information is forgotten.
This is a soundness target, not yet a faithful model of ordered linear proof
identity.

For an ordered context,

\[
h\models\Gamma
\Longleftrightarrow
\forall(x:A)\in\Gamma,\quad h\models A.
\]

The support-level entailment certificate records

\[
\operatorname{PremMod}(q)
=
\{h\in H_7:h\models\Gamma\},
\]

\[
\operatorname{Cex}(q)
=
\{h\in\operatorname{PremMod}(q):h\not\models A\}.
\]

It is positive precisely when \(\operatorname{Cex}(q)=\varnothing\).

---

## 5. Local soundness cells

For a checked derivation \(\pi:\Gamma\vdash_K A\), define a soundness cell

\[
\sigma_\pi:
\prod_{h\in 2^D}
([h\models\lvert\Gamma\rvert]\to[h\models\lvert A\rvert]).
\]

### 5.1 Assumption case

If \(\pi=\mathrm{Ax}(x)\), the only premise and conclusion have the same
formula. The cell is the identity transport.

### 5.2 Introduction case

Assume the induction hypothesis for

\[
\pi:\Gamma,x:A\vdash_K B.
\]

At one world \(h\):

- if \(h\not\models A\), material \(A\multimap_RB\) is true; and
- if \(h\models A\), the induction hypothesis sends satisfaction of
  \(\Gamma,x:A\) to satisfaction of \(B\).

Thus

\[
\lvert\Gamma\rvert
\models_{2^D}
\lvert A\multimap_RB\rvert.
\]

### 5.3 Elimination case

Assume

\[
\Gamma\models A\multimap_RB,
\qquad
\Delta\models A.
\]

At a world satisfying \(\Gamma\circ\Delta\), the first entailment cannot use
the false-antecedent branch, because the second provides \(A\). Therefore the
world satisfies \(B\).

### 5.4 Soundness theorem

Structural induction on the checked proof tree proves:

\[
\boxed{
\Gamma\vdash_{\mathrm{TND}_0}A
\Longrightarrow
\lvert\Gamma\rvert\models_{2^D}\lvert A\rvert
\Longrightarrow
\lvert\Gamma\rvert\models_{H_7}\lvert A\rvert.
}
\]

The first implication is the rule theorem. The second is only restriction to a
subspace. Thus \(H_7\) is a calibration frame, not the cause of soundness.
This theorem says nothing about completeness, normalization, or the proof
identity forgotten by the Boolean semantics.

---

## 6. Positive and negative entailment cells

### 6.1 Positive cell

A bounded trace returning a candidate proof closes a positive cell only after:

1. the trace replays from its exact initial state under the declared scheduler;
2. its terminal index extracts exactly the claimed proof;
3. the proof, full ledger, open context, and conclusion recursively check in
   \(K\) and exactly match the task;
4. structural soundness builds a world obligation at every point of \(2^D\);
5. a separate exhaustive scan records every premise and conclusion truth
   value on \(H_7\); and
6. both routes yield the same seven-bit sequent-support mask.

The V0 cell type is schematically

\[
\begin{aligned}
\operatorname{EntailCell}^+(q,\tau)
:={}&
\sum_\pi
\operatorname{Trace}^+_K(q,\tau,\pi)
\\
&\times
\operatorname{Check}_K(\pi:q)
\\
&\times
\operatorname{RuleSound}_{2^D}(\pi)
\\
&\times
\operatorname{ModelScan}_{H_7}(q)
\\
&\times
[\operatorname{Cex}_{H_7}(q)=\varnothing]
\\
&\times
\bigl[
\operatorname{Mask}_{H_7}(\operatorname{RuleSound}(\pi))
=
\operatorname{Mask}_{H_7}(\operatorname{ModelScan}(q))
\bigr].
\end{aligned}
\]

The commuting claim is extensional. The structural recursion and the direct
scan are different certificate constructions, but both intentionally call the
same declared formula interpretation. The fixture therefore checks internal
coherence; it is not an independent validation of that interpretation. It
also does not identify proof-relevant certificates or quotient distinct
derivations.

### 6.2 Negative countermodel cell

A negative cell retains the complete task and replayable trace:

\[
c=(q,\tau,h,\eta_\Gamma,\nu_A,[h\in H_7]),
\]

where the full premise truth vector \(\eta_\Gamma\) and conclusion-false
certificate \(\nu_A\) are independently recomputed. It has no positive \(K\)
vertex. Under soundness, it instead induces

\[
\operatorname{Der}_K(q)\to\mathbf 0.
\]

For example,

\[
P_K,\;P_X\multimap_RP_K
\not\models_{H_7}P_X
\]

has countermodels \(h_{\{K\}}\) and \(h_{\{K,t\}}\).

A checked proof for \(q\) and a checked countermodel for \(q\) cannot coexist
under theorem (S). The finite runner stops at its first terminal certificate;
it does not yet implement a separate `KernelSemanticConflict` result type.

---

## 7. Bounded search prefixes in \(t\)

The executable companion alternates between:

- a finite declared list of candidate proof objects; and
- a declared finite, duplicate-free subplan drawn from \(H_7\), defaulting to
  the ordered enumeration of all seven halt worlds.

Its result is

\[
\operatorname{ProofFound}(i)
\mid
\operatorname{CountermodelFound}(j)
\mid
\operatorname{Frontier}
\mid
\operatorname{SearchExhausted}.
\]

Every result sits inside

\[
\operatorname{SearchTrace}
(S_0,b,S_1,\operatorname{events},\operatorname{result}).
\]

Events carry a branch and an integer coordinate. Replay recomputes the unique
alternating transition, acceptance predicate, final cursor, and result from
\(S_0\) and budget \(b\). A bare proof or an empty event tuple has no search
authority.

The alternation test establishes only a finite scheduling invariant. It does
not prove an infinite scheduler fair.

A later fair enumerator must satisfy at least

\[
\forall c\text{ finite and continuously admissible},
\quad
\exists n,\ c\text{ is inspected by stage }n.
\]

Fairness would guarantee discovery of an existing finite certificate. It
would not guarantee that every logic has a proof or a finite countermodel.

`Frontier` means that the budget ended while at least one declared coordinate
remains. `SearchExhausted` means that both finite declared lists ended without
a certificate. The latter does not prove non-derivability because the
candidate list is not a complete proof enumerator. Neither result has truth,
refutation, proof, or `Omega` authority.

---

## 8. Resource conflict opens a different horn

When \((\multimap_RE)\) tries to combine two complete resource ledgers, six
cases remain separate:

1. disjoint source, scoped occurrence, and binder identities: concatenate the
   ledgers and their open ordered contexts;
2. repeated scoped occurrence or binder identity: reject an alias;
3. one shared source carrying different formulae: reject a canonical
   source-type mismatch;
4. more than one shared source: reject a multiple-conflict boundary;
5. one shared source carrying the same formula and the same domain identity:
   reject the current same-domain linear conflict; or
6. one shared source carrying the same canonical formula/type but distinct
   domain identities: expose an oriented remaining-domain boundary diagnostic
   shaped for note 0083.

In the last case,

\[
H_{\mu(d,e)}^\varepsilon,
\qquad
\mu(d,e)=D\setminus\{d,e\},
\]

is returned instead of a derivation. The executable
`ApertureBoundaryDiagnostic` retains an aperture identity, canonical source
and formula, left/right ports with full provenance, required filler role,
orientation, and residual ledger. It is sufficient to verify that the correct
third-domain boundary and its domain-specific role were selected.

This diagnostic is not yet an accepted 0083 filler or a context-merge proof
rule. Such a promotion still requires substitution transport, proof-tree
bracketing coherence, filled-cell associativity, and preservation of every
residual ledger. Therefore:

A source-formula mismatch may later trigger an explicit vocabulary-extension
or typed-transport operator. In \(\mathrm{TND}_0\) it is only an obstruction:
it is neither the remaining-domain aperture nor \(\Omega\).

\[
\boxed{
\text{entailment coherence cell}
\ne
\text{shared-source conflict completion cell}.
}
\]

They may later be related by a theorem; they are not related by naming both
of them triangles.

---

## 9. Exact failure of threaded completeness

The Boolean shadow validates weakening-like sequents. For example,

\[
P_K\models_{H_7}P_X\multimap_RP_K.
\]

But the strict calculus has no derivation

\[
P_K\vdash_{\mathrm{TND}_0}P_X\multimap_RP_K,
\]

because \((\multimap_RI)\) would introduce a \(P_X\) resource that the body
does not consume.

This non-derivability also has a simple grade invariant. Let \(G\) be the free
abelian group generated by \(e_K,e_X,e_t\), and define

\[
g(P_d)=e_d,
\qquad
g(A\multimap_RB)=g(B)-g(A),
\qquad
g(\Gamma)=\sum_{x:A\in\Gamma}g(A).
\]

Each rule of \(\mathrm{TND}_0\) preserves

\[
g(\Gamma)=g(A).
\]

However,

\[
g(P_K)=e_K,
\qquad
g(P_X\multimap_RP_K)=e_K-e_X.
\]

The grades differ, so the sequent is not derivable.

Consequently,

\[
\boxed{
\operatorname{Cex}_{H_7}(q)=\varnothing
\centernot\Longrightarrow
\operatorname{Der}_{\mathrm{TND}_0}(q)\ne\varnothing.
}
\]

This is not a counterexample to classical completeness. It is evidence that
the resource-preserving calculus and its proof-irrelevant Boolean shadow have
different completeness questions.

---

## 10. Quantifiers are not promoted yet

Note 0082 has finite predicate terms, capture-avoiding substitution, and
dependent-sum/product semantics. Natural-deduction quantifier rules still
need:

- a proof-level substitution or cut theorem;
- eigenvariable and freshness conditions;
- source- and occurrence-preserving term substitution;
- witness retention for \(\exists I\);
- discharge and branch uniformity for \(\exists E\); and
- a distinction between one fixed finite structure and validity over all
  finite structures.

Fixed finite model checking is decidable. It does not imply that pure logic
proves every sentence true in one structure. Validity over all unbounded
finite first-order structures also has the Trakhtenbrot obstruction and must
not be advertised as a future total proof procedure.

Quantifier proof rules therefore follow proof substitution; they do not
precede it.

---

## 11. The status of \(\Omega\)

There is no genuine `Omega` result in the finite \(H_7\) calibration:

- all seven worlds can be inspected;
- a finite countermodel is a completed negative result;
- a resource boundary diagnostic is a typed request for later filler evidence;
- a bounded frontier may reflect an incomplete candidate list; and
- finite-plan exhaustion may reflect an incomplete candidate list; and
- the strict proof calculus is intentionally incomplete for the Boolean
  shadow.

An infinite fair chain under fixed language, rules, observer, and residual
would provide at most a candidate ray for a future compactification. A genuine
calculus-relative boundary still needs ray equivalence, scheduler invariance,
a declared compactification scheme, and a proof that no finite certificate
already closes the ray. Numerical Chaitin \(\Omega_U\) additionally requires a
fixed universal prefix-free machine, self-delimiting program codes, and Kraft
weights.

Thus

\[
\operatorname{Frontier}
\ne
\operatorname{SearchExhausted}
\ne
H_d
\ne
\Omega_t
\ne
\Omega_U.
\]

---

## 12. Executable calibration

The companion
**tests/python/test_threaded_natural_deduction_calibration.py** checks:

1. \(T_{H_7}=P_K\lor P_X\lor P_t\) holds on exactly the seven nonempty
   Boolean worlds and fails on the all-false valuation;
2. runtime closure of Boolean coordinates, resource domains, use status, and
   binder identity;
3. singleton assumption and discharge that retains a complete bound ledger;
4. successful right-boundary discharge after a nonempty ordered prefix;
5. ordered, source-disjoint implication elimination;
6. recursive per-rule soundness obligations over all eight Boolean worlds;
7. distinct nominal task, provenance, source, occurrence, scope, and binder
   identities;
8. rejection of a shared source assigned two different formula types;
9. a same-formula shared source in two domains exposing the typed third-domain
   boundary diagnostic;
10. rejection of occurrence aliases and same-domain source conflicts;
11. rejection of occurrence or source reuse hidden behind discharge;
12. replayable positive closure whose structural and direct \(H_7\) masks
    agree;
13. rejection of forged empty-event and wrong-coordinate proof traces;
14. replayable negative closure with a complete countermodel record;
15. rejection of the all-false world before \(H_7\) countermodel search;
16. separation of a resumable `Frontier` from finite `SearchExhausted`;
17. confirmation that exhausted finite inventory has no entailment authority;
18. branch, cursor, candidate, duplicate-world, and model-space invariants;
19. rejection of an unresolved shared source at the entailment boundary;
20. the grade witness separating Boolean validity from strict derivability;
    and
21. recursive rejection of a forged proof record.

The fixture is self-contained and does not import or reinterpret stable Adva
IR.

---

## 13. Proven, calibrated, and deferred

### Proven in the mathematical fragment

- local soundness of `Ax`, \(\multimap_RI\), and \(\multimap_RE\) under the
  Boolean interpretation on all eight valuations;
- structural-induction soundness of every checked \(\mathrm{TND}_0\)
  derivation, with \(H_7\) soundness as a restriction corollary;
- proof/countermodel orthogonality as a corollary of soundness;
- relative classical \(H_7\) completeness only after explicit erasure into
  \(\mathrm{CND}_{\mathrm{CPL}}^{\mathrm{cl}}+T_{H_7}\); and
- the grade obstruction separating strict linear derivability from Boolean
  semantic validity.

### Executably calibrated

- the ordered proof constructors, complete use ledger, and recursive checker;
- recursive per-rule Boolean obligations and exhaustive seven-world scan;
- bounded alternating inspection with replayable state transitions;
- positive support-mask coherence and negative countermodel closure;
- strict \(H_7\) membership, cursor, and context invariants;
- distinction between `Frontier` and `SearchExhausted`; and
- refusal to convert a typed resource boundary diagnostic into a proof.

### Deferred

- proof substitution and cut admissibility;
- \(\beta\)-subject reduction and normalization;
- left implication and its coherence with the right implication;
- tensor introduction and one-use elimination;
- certified context merge through 0083 fillers;
- weakening, contraction, exchange, and filled-cell associativity
  certificates;
- proof-relevant classical control;
- completeness of a resource model;
- quantifier introduction and elimination;
- an actually fair unbounded proof enumerator; and
- any `Omega` identification.

The next proof-theoretic target is not another connective. It is the
certificate-preserving substitution theorem

\[
\frac{
\Gamma\circ x:A\vdash_K M:B
\qquad
\Delta\vdash_K N:A
\qquad
\operatorname{Src}(\Lambda_M)
\cap
\operatorname{Src}(\Lambda_N)=\varnothing
\qquad
\operatorname{ScopedOcc}(\Lambda_M)
\cap
\operatorname{ScopedOcc}(\Lambda_N)=\varnothing
}{
\Gamma\circ\Delta
\vdash_K M[N/x]:B
},
\]

where \(\operatorname{ScopedOcc}\) consists of
\((\operatorname{ScopeId},\operatorname{OccurrenceId})\) pairs. The theorem
must specify how the audit record for \(x\) is transformed, require disjoint
binders or certified alpha-freshening, and preserve source, occurrence, order,
discharge, and residual data. Only after that theorem should
\(\beta\)-reduction, normalization, quantifier rules, and cut elimination be
promoted.
