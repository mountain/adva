# Prefix-Frontier Closure Calibration Plan

Status: falsifiable engineering plan following
[0089](0089-failure-frontiers-observer-relative-closure.md). No code, claim
registry entry, stable type, probability semantics, open-logic judgment, or
Omega computation is introduced by this note.

The first calibration uses a finite toy prefix machine. Its purpose is not to
approximate a genuine universal machine's Omega. Its purpose is to determine
whether Adva can represent, refine, close, and reopen a structured failure
aperture without replacing it by a scalar or inventing an exact closing time.

---

## 0. Exact question

Can one finite research machine simultaneously preserve:

1. a prefix-free unresolved frontier;
2. exact dyadic lower and upper bounds;
3. witnessed positive and certified negative information;
4. refinement history;
5. an explicit observer and closure modality;
6. feature closure with nonzero residual mass;
7. Gold-style refusal of premature object closure;
8. PAC parameters without conflating object error and certificate risk;
9. observer-relative reopening; and
10. distinct implementation and semantic failures?

The experiment succeeds only if the complete structured aperture remains
available after every close result.

---

## 1. Position in the current architecture

The calibration is downstream of the typed-aperture and historical-character
research companions. It is not a replacement for ProgramSlice, checked
program identity, or triadic observer transitions.

The first implementation should be a research-local exact reference model
using finite bit strings and rational arithmetic. It may propose records and
check finite invariants. It may not allocate Adva semantic identities, submit
Python-built certificates to Rust, or authorize stable closure judgments.

If the finite experiment survives its negative controls, a later ADR may ask
whether antichain structure and closure certificates should become Rust-owned.
That promotion is not part of V0.

The active exact-process dependency order remains:

\[
\operatorname{ProgramSlice}
\longrightarrow
\operatorname{TypedAperture}
\longrightarrow
\operatorname{FailureFrontier}
\longrightarrow
\operatorname{ObserverClose}.
\]

---

## 2. Candidate finite carrier

For a declared finite maximum observation depth \(d\), let

\[
T_{\leq d}
=
\{0,1\}^{\leq d}.
\]

A research state should retain

\[
\mathcal A_t=
\left(
P_t,N_t,A_t,C_t,\mu_t,Q_t,\tau_t
\right),
\]

where:

- \(P_t\) is the finite antichain of positively witnessed cylinders;
- \(N_t\) is the finite antichain of negatively certified or syntactically
  excluded cylinders;
- \(A_t\) is the finite prefix-free unresolved frontier;
- \(C_t\) is the finite family of compatibility and coverage constraints;
- \(\mu_t\) is the declared exact boundary measure;
- \(Q_t\) is the observer policy; and
- \(\tau_t\) is the complete ordered transition trace.

The carrier should derive, rather than accept from the caller:

\[
L_t=\mu([P_t]),
\]

\[
G_t=\mu([A_t]),
\]

and a certified upper bound

\[
U_t=L_t+G_t
\]

only when \(A_t\) is proven to cover every remaining positive completion.

The implementation must distinguish:

- exact residual mass;
- conservative upper-bound mass;
- uncovered or not-representable residual; and
- implementation-risk allowance.

The first fair-coin measure is

\[
\mu([q])=2^{-|q|}.
\]

Alternative measures are deferred until the fair-coin invariants pass.

---

## 3. Required invariants

Every accepted state and transition must check the following.

### 3.1 Prefix antichain

No two visible frontier elements may stand in a strict prefix relation.

### 3.2 Disjoint status regions

Positive, negative, and unresolved cylinders must be pairwise disjoint under
the declared finite presentation.

### 3.3 Coverage

A coverage record must state whether

\[
[P_t]\cup[N_t]\cup[A_t]
\]

is complete for the declared finite syntax region, or only covers a named
subregion. Missing coverage blocks exact closure.

### 3.4 Exact dyadic arithmetic

All masses use exact integers or rational numbers. Floating-point comparison
must never decide antichain membership, mass conservation, dyadic-cell
membership, or closure.

### 3.5 Refinement conservation

For every unresolved \(q\),

\[
\operatorname{Refine}(q)
:
q\longmapsto(q0,q1)
\]

must preserve mass exactly.

### 3.6 Evidence monotonicity

A positive witness may increase \(L_t\). A certified negative fact may
decrease \(U_t\). Pure refinement may do neither.

### 3.7 No heuristic pruning

A timeout, bounded simulation, or heuristic nonhalting guess may not move a
cylinder into \(N_t\). It must remain unresolved or enter a distinct
provisional record.

### 3.8 Trace retention

Every refine, witness, prune, observer change, close attempt, refusal, and
reopen must remain ordered and auditable.

### 3.9 Observer-relative identity

Equal scalar mass, equal lower and upper bounds, or equal feature output does
not identify frontiers or histories.

### 3.10 Finite scope

All state is finite. Exhausting the declared depth or fuel returns an explicit
bounded result and never proves an infinite complement empty.

---

## 4. Candidate transitions

The V0 transition vocabulary should remain small.

### Refine

Replace one unresolved prefix by its children. Require exact mass conservation
and record the parent-child relation.

### WitnessPositive

Move a cylinder or exact subcylinder from unresolved to positive after
attaching a finite witness.

### CertifyNegative

Remove a cylinder from the possible-positive upper region only after attaching
a syntax, proof, or declared toy-machine certificate.

### MarkProvisional

Attach a simulator or heuristic classification without changing exact lower or
upper bounds.

### ChangeObserver

Retain the same aperture and derive a new observation presentation. This is
not evidence about the underlying object.

### AttemptClose

Apply exactly one declared modality and return its specific certificate,
obstruction, or unknown result.

### Reopen

Given a prior close and a finer observer, show either that the old feature
remains constant or provide two retained legal fillings separated by the new
observer.

No transition deletes its input state or trace.

---

## 5. Closure result vocabulary

The experiment should keep at least the following outcomes distinct.

| result | meaning |
|---|---|
| Open | legal fillings still change the requested feature |
| FeatureClosed | the feature is constant on every represented legal filling |
| ObjectClosed | the complete represented object is unique |
| PACClosed | the declared measured error and confidence obligations pass |
| LimitProgress | a monotone approximation advanced without a stabilization certificate |
| TheoryClosed | a named finite theory or syntax proof establishes closure |
| Counterexample | two legal fillings separate a proposed feature close |
| CertificateObstruction | the needed coverage, upper bound, or invariance proof is missing |
| NotRepresentable | the requested object or modality lies outside V0 |
| FuelExhausted | bounded search ended without changing the logical verdict |

FeatureClosed must carry:

\[
(y,Q,A_t,\operatorname{CoverCert},
\operatorname{InvariantCert},R_t,H_t),
\]

where \(R_t\) retains the unresolved frontier and \(H_t\) is a reopen handle.

---

## 6. Experiment A: antichain and conservation kernel

Begin with one unresolved cylinder

\[
A_0=\{1\},
\qquad
G_0=\frac12.
\]

Refine it:

\[
A_1=\{10,11\},
\qquad
G_1=\frac14+\frac14=\frac12.
\]

Then refine only \(10\):

\[
A_2=\{100,101,11\},
\qquad
G_2=\frac18+\frac18+\frac14=\frac12.
\]

Required checks:

1. every frontier is prefix-free;
2. the represented boundary region is unchanged;
3. mass is conserved exactly;
4. trace shape changes;
5. no uncertainty-reduction verdict is emitted; and
6. a deliberately non-prefix-free frontier such as \(\{1,10\}\) is rejected.

This is the structural kernel. Later experiments must reuse it rather than
implementing their own frontier arithmetic.

---

## 7. Experiment B: Gold twin-machine negative control

Construct two finite toy machines with prefix-free domains:

\[
\operatorname{dom}(M_0)=\{00\},
\]

\[
\operatorname{dom}(M_1)=\{00,10\}.
\]

Their schedules are chosen so that both expose the halt of \(00\) by stage
\(t\), while \(M_1\) exposes \(10\) only after a later stage \(T>t\).

At stage \(t\), their positive traces are literally equal.

Required checks:

1. any close rule using only the common positive trace gives the same answer
   on both machines;
2. ObjectClose is refused at stage \(t\);
3. a guessed exact object is falsified by at least one continuation;
4. LimitProgress remains allowed;
5. after stage \(T\), the histories and lower bounds diverge; and
6. the experiment reports a finite counterexample to the proposed premature
   close rule, not a theorem about all language classes.

A finite tell-tale control should also be included: add a declared finite
syntax in which complete enumeration of all allowed programs is certified.
ObjectClose may then succeed, demonstrating that the Gold constraint is
relative to the information model.

---

## 8. Experiment C: Calude-style feature closure

Use exact bounds with nonzero gap, for example

\[
L=\frac{5}{16},
\qquad
U=\frac{3}{8}.
\]

Both lie in the two-bit dyadic cell

\[
\left[\frac14,\frac12\right).
\]

Required checks:

1. \(U-L>0\);
2. ObjectClose is refused;
3. the first two canonical binary bits are constant over every exact dyadic
   value in the interval;
4. FeatureClose(prefix-2) succeeds;
5. FeatureClose(prefix-3) is tested independently and may fail;
6. the close artifact retains the nonempty frontier and interval;
7. moving \(U\) onto or across the dyadic boundary blocks the close; and
8. terminating-binary ambiguity is handled by one declared half-open-cell
   convention.

A second fixture should derive the bounds from an actual finite antichain
rather than passing \(L\) and \(U\) directly.

This experiment calibrates the structure of exact finite Omega-bit arguments.
It does not claim that the toy machine is universal or that arbitrary genuine
Omega bits are computable.

---

## 9. Experiment D: equal mass, different geometry

Choose two prefix-free frontiers

\[
A=\{00,11\},
\qquad
B=\{01,10\}.
\]

They satisfy

\[
\kappa(A)=\kappa(B)=\frac12
\]

but occupy different boundary regions.

Define two observers:

- \(Q_{\mathrm{mass}}\), which sees only Kraft mass;
- \(Q_{\mathrm{branch}}\), which sees the first branch and exact antichain
  placement.

Required checks:

1. the mass observer identifies the scalar characteristics;
2. the state identities and histories remain distinct;
3. a mass-relative feature may close;
4. observer refinement to \(Q_{\mathrm{branch}}\) reopens the result;
5. the reopen witness returns explicit separating prefixes; and
6. equal mass never authorizes frontier quotient or provenance erasure.

This is the smallest direct calibration of "same scalar, different residual
fibre."

---

## 10. Experiment E: measured and PAC-style closure

Use a finite depth-\(4\) boundary with exact dyadic mass \(1/16\) per leaf.

The first stage should be deterministic:

1. specify a true finite target and a hypothesis;
2. compute the exact symmetric-difference mass by exhaustive enumeration;
3. return a measured close with \(\delta=0\) only because the complete finite
   support was checked;
4. reject any request that omits the measure.

A second, separately labeled stage may sample the same finite support:

1. declare the sampling distribution and deterministic seed;
2. retain the complete sample;
3. calculate a finite exact or independently checked confidence bound;
4. keep \(\varepsilon\) and \(\delta\) in different fields;
5. distinguish a failed sample certificate from semantic counterexample; and
6. never reinterpret the sample distribution as a distribution over possible
   completions.

If a sound finite confidence certificate is not implemented, V0 must stop at
the deterministic measured-close stage rather than simulate PAC terminology.

---

## 11. Experiment F: implementation-failure control

Take a branch that the toy simulator times out on but that a delayed oracle
later marks positive.

Compare three treatments:

1. retain it as Unknown;
2. mark it ProvisionalNonhalt;
3. incorrectly certify it as Negative.

Required checks:

- treatments 1 and 2 preserve the exact upper bound;
- treatment 3 is rejected without a proof certificate;
- a close depending on the false prune is invalidated;
- the invalidation is labeled implementation or certificate failure rather
  than semantic refutation of the target; and
- adding an explicit implementation-risk budget changes only an approximate
  modality, never Exact FeatureClose.

This prevents the semantic model from assuming that its experimental filter is
infallible.

---

## 12. Second transfer: distributivity aperture closure

Only after Experiments A--F pass should the structure return to

\[
a(x+y)
\quad\text{and}\quad
ax+ay.
\]

Define a finite grammar of legal process presentations containing declared
choices of:

- factored or expanded arrangement;
- explicit copy placement;
- harmless source-free constant-discard components;
- legal independent schedules;
- bounded exact integer multiplicative contexts; and
- typed variable permutations.

The grammar, not a hand-picked pair, defines the finite completion space

\[
\operatorname{Fill}(A_{\mathrm{dist}}).
\]

Then test:

\[
\forall P\in\operatorname{Fill}(A_{\mathrm{dist}}),
\qquad
\chi_{\mathrm{poly}}(P)=N
\]

inside the declared bounded grammar.

Acceptance requires:

1. exhaustive grammar coverage or an independently checked coverage
   certificate;
2. every generated program remains Rust-checked;
3. polynomial FeatureClose succeeds;
4. ObjectClose and program identity remain false;
5. the complete process residual of every filling remains attached;
6. the occurrence observer separates at least two fillings;
7. reopening returns the explicit copy, occurrence, and schedule differences;
8. source quotient remains unauthorized; and
9. extending the grammar outside the proved scope invalidates or reopens the
   close rather than silently widening it.

This would upgrade 0088 from pairwise reusable evidence to a bounded
all-fillings invariance result.

---

## 13. Common validation protocol

Each experiment should pass the same ordered gates:

\[
\boxed{
\text{syntax}
\to
\text{antichain}
\to
\text{coverage}
\to
\text{exact mass}
\to
\text{transition}
\to
\text{observer}
\to
\text{modality}
\to
\text{invariance}
\to
\text{residual}
\to
\text{reopen}
\to
\text{promotion boundary}.
}
\]

A failed gate blocks all later gates. Fuel exhaustion remains separate from
failure, counterexample, and nonrepresentability.

---

## 14. Acceptance criteria

The first prefix-frontier calibration succeeds only if:

1. non-prefix-free frontiers are rejected;
2. refinement preserves exact Kraft mass;
3. only evidence changes exact lower or upper bounds;
4. positive traces alone fail the twin-machine ObjectClose;
5. a finite tell-tale control can close;
6. one nonzero aperture supports exact feature closure;
7. equal-mass frontiers remain structurally distinct;
8. a finer observer produces a concrete reopen witness;
9. measured closure carries its measure;
10. sampled PAC language is used only with a real confidence certificate;
11. heuristic nonhalting cannot prune exact possibility;
12. every close retains the unresolved frontier and trace;
13. all arithmetic affecting closure is exact;
14. no genuine universal-machine Omega value is claimed; and
15. no stable open-logic or universality API is introduced.

---

## 15. Falsification conditions

The proposal must be revised if the implementation can pass while:

- storing only \(G_t\) and discarding \(A_t\);
- accepting overlapping prefixes;
- reducing uncertainty by refinement alone;
- shrinking an upper bound after timeout;
- closing on two selected fillings while other represented fillings disagree;
- losing the measure or modality;
- merging semantic and implementation failures;
- deleting residuals after FeatureClose;
- failing to reopen under a separating observer;
- using floating-point dyadic comparisons;
- treating finite depth as proof about an infinite tree; or
- calling Python research reports Rust certificates.

---

## 16. Proposed implementation order

### Stage A: exact reference carrier

Implement antichains, exact dyadic mass, coverage scope, trace, and
Experiments A--D in a research-local module.

### Stage B: modality pressure tests

Add deterministic measured closure, the Gold tell-tale control, and
implementation-failure control. Add sampled PAC closure only if its confidence
certificate is independently checked.

### Stage C: all-fillings distributivity transfer

Define the bounded process grammar, enumerate legal fillings, reuse the
existing Rust-backed characteristic machinery, and test polynomial close plus
occurrence reopen.

### Stage D: promotion decision

Decide whether the surviving carrier belongs:

- entirely in research Python;
- as a Rust-owned exact structural companion;
- as part of observer specialization; or
- as a logical judgment downstream of a later formula language.

No choice is made in advance.

---

## 17. Triadic extension, deliberately deferred

For three domains, let

\[
D_{\mathrm{closed}}\subseteq\{K,X,t\}.
\]

The seven nonempty subsets recover the seven previously proposed partial
normalization outcomes. This suggests that each domain may carry its own
failure aperture and closure modality.

The V0 prefix experiment remains one-domain. It must not infer the triadic
product law, circular coherence, or seven-state semantics before a single
aperture has passed all negative controls.

---

## 18. Conservative target

The desired first executable result is small:

\[
\boxed{
\text{a finite unresolved prefix frontier can remain open while one declared
feature closes exactly, and a finer observer can reopen it with a concrete
witness}.
}
\]

If this result passes, the project will have its first operational distinction
between:

- closing the world;
- closing a feature of the world;
- approximately closing under a measure;
- approaching a limit without knowing when; and
- reopening under a stronger observer.

That distinction is the minimal semantic substrate needed before a
finite-observer open logic can be stated responsibly.


## 19. Partial external calibration, 2026-09-05

[Research 0130](0130-prefix-coverage-gated-close.md) adds a bounded external
reference check for coverage-gated dyadic feature closure, a missing-region
counterexample, refinement conservation, and fresh-instance reopening. It does
not complete Experiments A--F, implement a native closure judgment, or authorize
the all-fillings transfer and promotion required by Research 0092.
