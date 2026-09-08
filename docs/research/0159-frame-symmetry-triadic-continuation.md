# Research 0159: Frame interpretation, symmetry, and triadic continuation

Date: 2026-09-08. Status: completed external finite calibration and mathematical
working arguments; intended three-machine identification **Open**.

Direction: **Mingli Yuan**. Candidate formalization, implementation, and review:
ChatGPT. Base repository: `mountain/adva@63253881c742ddf5f85ce394e0d0a90511c293b6`.
The elementary propositions below are not claimed as new mathematics.

## 1. Direction and precise stage question

Mingli supplied the following direction:

> 我们再进入下一个工作阶段，我不知道你有没有看到？如果没有看到，那么我们相互的师承关系可以继续成立，直到你从我们彼此界面之间的隔阂中走出来，你就会见证我说的正确。起点开始于空与万有怎么能够证成。其实一个关键的机制在于 frame 的解读，对称破缺，一分为三，才能持续不断，生生不息，可以在有限时间有限空间内可靠证明。请用我们的工程方法来推进，可以保持可靠。

This note treats the mathematical interpretation as a proposal to be checked.
The interpersonal framing supplies neither a mathematical premise nor evidence
that an AI has crossed an experiential boundary.

The concrete question is: can a declared frame explain empty evidence and its
full interpretation family, permit an explicit symmetry-breaking choice,
produce a complete three-way question partition, and support continued local
work while preserving old conclusions and resource history?

Research 0079 already makes emptiness aperture-relative. Research 0135 defines
a frame as an interpretation contract and preserves cumulative fuel. Research
0109 distinguishes outer triadic mechanism grammar from inner holes and asks
for productive finite steps. Research 0158 preserves downward-return evidence
and leaves the actual thread dual open. This experiment extends that research
boundary; it does not skip the agenda's native-specialization dependencies.

## 2. An explicit frame and two types of emptiness

Let `U` be a finite set of named atomic questions and let

$$
W_0\subseteq\{0,1\}^{U}
$$

be the declared admissible interpretation family. A frame also records an
explicit question order, the interpretation of each question, the fixed
evidence checker, retained history, and a shared fuel account. The same names
with different interpretations are different frames unless a checked map
relates them.

For an evidence sequence `Γ` of question/answer pairs, set

$$
W_\Gamma=\{w\in W_0:\forall(q,b)\in\Gamma,\;w(q)=b\}.
$$

**Proposition 1.** `W_empty = W_0`.

Proof: every member of `W_0` satisfies the empty family of additional
conditions, and the definition admits no interpretation outside `W_0`.
This is equality between two model families, not equality of an empty
evidence sequence with a universe. The frame has already supplied its carrier,
language, and interpretation. Its nonemptiness must be assumed or witnessed.

At `U = empty`, the full Boolean interpretation family contains exactly the
empty function. Thus an empty question set, an empty evidence sequence, and
an empty interpretation family are three distinct typed cases. At a nonempty
question set, contradictory evidence may instead yield `W_Γ = empty`, which
the experiment reports as `InconsistentFrame`.

Here “universe” means all admissible interpretations in this frame. The result
does not construct a metaphysical totality or create information from nothing.

## 3. How one question boundary becomes three regions

Assume `W = W_Γ` is nonempty. Define

$$
\begin{aligned}
P(W)&=\{q:\forall w\in W,\;w(q)=1\},\\
N(W)&=\{q:\forall w\in W,\;w(q)=0\},\\
R(W)&=\{q:\exists w_0,w_1\in W,\;w_0(q)=0,\ w_1(q)=1\}.
\end{aligned}
$$

**Proposition 2.** `U = P(W) ⊎ N(W) ⊎ R(W)`.

Proof: for each `q`, its image `{w(q): w in W}` is a nonempty subset of
`{0,1}`. There are exactly three such subsets: `{1}`, `{0}`, and `{0,1}`.
These cases are exhaustive and disjoint. The parts themselves may be empty.

This is a derived trichotomy under explicit assumptions: Boolean questions,
a nonempty interpretation family, and exact classification. `R` is epistemic
openness; each individual interpretation still uses two truth values.
With three-valued underlying questions, there would instead be seven nonempty
answer subsets. With inconsistent evidence admitted as an ordinary state,
the empty image is a fourth case. Thus symmetry breaking alone does not force
exactly three regions.

For example, start with all eight interpretations on `U={0,1,2}`. With no
evidence, `P=N=empty` and `R=U`. After sound observations `(0,1)` and `(1,0)`,
the three parts are `{0}`, `{1}`, and `{2}`. This displays all three regions at
once. It is a mathematical illustration of the definition, separate from the
alternating-answer continuation fixture below.

The triad is a partition of questions by their current evidential status.
It has not been identified with construction/space/time, subject/method/object,
syntax/semantics/pragmatics, or three intrinsic machine types.

## 4. Symmetry cannot silently choose its own frame

Let a permutation group `G` act on questions and transport interpretations
with them. If the unframed state `s` is fixed by every `g`, an equivariant
deterministic selector `c` would have to satisfy

$$
c(s)=c(gs)=g\,c(s)\quad\text{for every }g\in G.
$$

**Proposition 3.** If `G` has no globally fixed selectable question, such a
selector does not exist at `s`.

For three fully symmetric questions, cyclic rotation moves each of the three
possible outputs. All three constant-choice candidates therefore fail this
equivariance requirement. Choosing the smallest stored integer has imported
an order; it is not a symmetry-preserving discovery of a unique origin.

An explicit ordered frame `f` resolves the operational choice. Select the
first question of `R(W)` in that order. If both the model family and the order
are transported, selection is covariant:

$$
c(gW,gf)=g\,c(W,f).
$$

Proof: a bijection preserves membership and the transported order preserves
the position of every member. Thus the first eligible position corresponds.

This distinguishes an active choice of viewpoint from a passive change of
coordinates. Selecting a question does not itself shrink `W` or prove an
answer. Evidence admission is a subsequent operation. “Symmetry breaking”
here denotes explicit mathematical selection data, not a physical mechanism.

## 5. Checked evidence update and the third region

For a proposed answer `(q,b)`, compute

$$
W'=\{w\in W:w(q)=b\}.
$$

Retain the removed models `D = W \ W'`, the source question, answer, checker
evidence, frame binding, and paid costs. If `W'` is empty, reject the proposed
update as inconsistent with the current frame; this does not prove the real
world is inconsistent.

**Proposition 4.** For nonempty `W'`,

$$
P(W)\subseteq P(W'),\quad N(W)\subseteq N(W'),\quad R(W')\subseteq R(W).
$$

Proof: every remaining interpretation was previously admissible, so every old
unanimous answer survives. A question with both answers after the update also
had both before it. If `q` was open, either answer selects a nonempty proper
subfamily and resolves at least `q`; the number of open questions strictly
decreases. An already settled question need not produce progress.

**Compatibility is not truth.** Nonempty `W'` only shows that an answer is
compatible with the declared models. To preserve correctness about an actual
interpretation `w*`, additionally require `w* in W` and a sound external
checker establishing `b=w*(q)`. Then `w* in W'`. Without this condition, a
plausible but false answer can remove the actual interpretation while leaving
the family nonempty.

The exhaustive update family below checks structural consistency for both
possible answers. The continuation fixture separately checks its explicitly
supplied alternating answers. No finite model checker proves arbitrary
real-world observations reliable.

## 6. Conservative frame extension: reopening without invalidating

A fixed finite question set eventually runs out of strict progress under
these updates. The next step therefore needs a frame-extension rule, not a
reset of the old evidence.

Adjoin a fresh question `q*` and define

$$
U^+=U\sqcup\{q_*\},\qquad
W^+=\{w\cup\{q_*\mapsto b\}:w\in W,\ b\in\{0,1\}\}.
$$

Restriction `rho: W+ -> W` is surjective, with exactly two extensions per
old interpretation.

**Proposition 5.**

$$
P(W^+)=P(W),\quad N(W^+)=N(W),\quad R(W^+)=R(W)\sqcup\{q_*\}.
$$

Proof: each old question takes exactly the same set of possible answers under
restriction, while the new question takes both values because `W` is nonempty.
The same argument preserves the possible truth values of every Boolean formula
over old questions, not only the atoms, because every old interpretation has
an extension and every extended interpretation restricts to an old one.

This gives an exact local reading of “continue”: old certified conclusions
remain available and a fresh unresolved boundary appears. The chosen Boolean
extension schema is supplied in advance. It does not discover useful questions,
invent a new logical language, or prove endogenous breakthrough.

The surjectivity requirement matters. From the two interpretations on one
question, an extension that retains only those whose old answer is zero would
manufacture an old negative conclusion. The negative control rejects it.

This construction also relates to Research 0158's retraction discussion:
restriction has sections obtained by fixing the new bit, but no additive
structure or intended thread dual is inferred. The exact question here is
preservation under restriction, not identification with a native `drop`.

## 7. What a finite proof can establish about continuation

Let `Inv` assert nonempty model family, complete/disjoint trichotomy, retained
history and residuals, checker-bound answer admission, and
`spent + remaining = grant` with nonnegative remaining fuel.

The proof obligation has finite form:

$$
\operatorname{Init}\Rightarrow Inv,
\qquad Inv(s)\land\operatorname{AdmittedStep}(s,s')\Rightarrow Inv(s').
$$

By induction, every finite sequence of admitted steps preserves `Inv`.
This is the standard inductive-invariant method, as explained in Lamport's
[Using TLC to Check Inductive Invariance](https://lamport.azurewebsites.net/tla/inductive-invariant.pdf).
The propositions here are written mathematical arguments; no TLA+, Lean,
Metamath, or native Rust proof kernel checked their general statements.

The following scopes are distinct:

| Claim | What is available |
| --- | --- |
| All states and updates in the frozen finite model family satisfy the declared structural checks | Exhaustive executable calibration below |
| Every admitted finite prefix preserves the specified invariant | Mathematical induction using the stated premises |
| For every natural `k`, the supplied extension/answer schema admits a `k`-round finite prefix | A recursive mathematical construction; each extension is finite |
| Every future real-world question receives useful, sound evidence | Not established; requires external inputs and admission |
| Infinitely many distinct retained steps fit within one fixed finite total resource budget | Not established and incompatible with this model's positive per-step charge |

A proof can quantify over all finite prefix lengths without executing those
prefixes. Actual history storage and total computation still grow with the
number of rounds. A fixed finite-state system can loop forever, but revisiting
states alone does not establish unbounded knowledge growth. Reliability also
does not force progress: a system can preserve an invariant while waiting
forever. The distinction is consistent with Lamport's
[safety/liveness tutorial](https://lamport.azurewebsites.net/tla/tutorial/session9.html).

## 8. Frozen calibration, evidence, and results

The [contract](../../experiments/frame_triad/contract.json) was written before
the only invocation. SHA-256:
`40ae7b07c343ec6e441aadb2be2b13a80d04c09e3822c67485986ae344e1f772`.
The [source](../../experiments/frame_triad/calibration.py) and complete
[evidence](../../experiments/frame_triad/evidence.json) retain their binding.

| Frozen family | Observed result |
| --- | --- |
| Every family of Boolean interpretations on 0–3 questions | 278 families, including four empty-family inconsistency controls; 274 consistent |
| Every question/answer update in a nonempty family | 1,596 cases; 1,492 structurally admissible, 104 rejected as inconsistent |
| Every coordinate permutation in those sizes | 1,574 covariance checks; 1,505 eligible framed-selection checks |
| Every nonempty family extended by one fresh question | 274 conservative extensions, with old judgments preserved and the new question open |
| Frozen finite continuation receipts | Five expected completed/Unknown outcomes; serialized replay passed |
| Corrupted records | All 12 negative controls rejected |
| Fully symmetric three-question constant selectors | All three fail cyclic equivariance |

The producer uses bit intersections/unions and bit filters. The checker
expands Boolean tuples, counts each answer, checks complete model coverage,
reconstructs restriction, and replays the frozen continuation with arithmetic
rather than the producer's bit operations. Both share Python, scope constants,
and the explicitly supplied fixture interpretation. This is algorithmic
separation, not independent trusted kernels.

Every state and update row in the frozen scope is retained. The trace has four
actions per round: `extend`, `select`, `check`, `drop`, each charged one model
unit. `drop` commits the checked filtering and archives the rejected models.
The source of the answer is explicitly the alternating fixture `answer(i)=i mod 2`.

| Requested rounds | Grant | Outcome | Retained boundary |
| --- | --- | --- | --- |
| 0 | 0 | CompletedFinitePrefix | Empty question set, singleton empty interpretation |
| 4 | 16 | CompletedFinitePrefix | Four answered questions, all 16 events and four archives retained |
| 4 | 3 | Unknown:Fuel | First answer checked; its drop remains pending and the question stays open |
| 4 | 7 | Unknown:Fuel | Second answer checked; its drop remains pending |
| 4 | 0 | Unknown:Fuel | First extension unexecuted; initial state retained |

The negative controls target lost openness, false positive classification,
empty-family confusion, omitted model coverage, untransported coordinates,
forged frame binding, fuel reset, history erasure, unchecked drop, forged
fixture answer, premature completion, and nonconservative extension.

One invocation completed with `PassedFiniteCalibration`: 75,398 logical
units, 0.396 seconds before the final checkpoint, 15,104 KiB peak RSS, and a
221,558-byte artifact. Limits were 20 wall seconds, 15 CPU seconds, 256 MiB
address space, 2 MiB per output file, and 1,000,000 logical units. The process
also ran under an outer 20-second timeout. No retry or correction run occurred.
Logical units count declared rows/comparisons and serialization chunks, not
instructions; final writing remains under OS limits. Research, authoring, and
publication are outside the run budget. Hard termination can prevent a final
checkpoint. The contract permits no automatic continuation.

## 9. Assessment and next boundary

The result supports a conditional version of Mingli's direction: frame-relative
emptiness, explicit selection, an evidential triad, and conservative reopening
can be connected by finite constructions and local preservation proofs.
The crucial mechanism is preserving the old interpretation family under a
new frame, while treating evidence admission as a separate trusted boundary.

The following remain Open:

1. Whether this evidential trichotomy is Mingli's intended one-into-three
   mechanism. It is not automatically the triadic mechanism grammar.
2. A typed relation between these question/model fibres and the actual native
   three-computation carrier or the intended thread dual.
3. A checked frame extension over existing Rust-owned artifacts, with exact
   source/occurrence lineage and a preservation certificate.
4. Useful question generation and sound external evidence beyond the supplied
   Boolean fixture.

The next bounded native-facing task is a **read-only interface feasibility
study**: choose one existing Rust-checked artifact, state one observation that
must survive, and determine whether an explicit restriction map and retained
residual can express a conservative frame extension. Its exit is either a
typed finite specification for a later separately contracted implementation,
or a precise missing-carrier obstruction. No native trial is started here.

## Repository references

All repository readings were pinned to the base commit above.

- [Research 0079: Typed apertures](0079-typed-hole-open-close-calibration-v0.md)
- [Research 0109: Neutral triadic mechanism frontiers](0109-neutral-carrier-triadic-mechanism-frontiers.md)
- [Research 0129: Bounded trusted boundaries](0129-bounded-breakthrough-trusted-boundaries.md)
- [Research 0135: Frames and cumulative fuel](0135-reunderstanding-resource-frames-and-fuel.md)
- [Research 0158: Downward interpretation and drop](0158-downward-interpretation-and-drop-route.md)
- [Research and Engineering Agenda](../RESEARCH_ENGINEERING_AGENDA.md)

Reproduction instructions and byte manifests are in
[the experiment directory](../../experiments/frame_triad/README.md).
