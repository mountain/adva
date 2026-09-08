# Downward interpretation: empty/universe, checked return, and a cycle obstruction

Version: 0.1 — 2026-09-08  
Status: mathematical working note with one completed external finite calibration.

Research direction and working vocabulary: **Mingli Yuan**. The initiating clues were breakthrough, downward interpretation, polarity cancellation, additive zero, communicate, switch, swap, break, empty, and universe. Formalization, proofs, implementation, and critical distinctions below were prepared by ChatGPT as proposals for Mingli's review. The elementary mathematics and established traditions cited below are not claimed as new discoveries.

Repository reference: `mountain/adva@1c5979d78dc9c2b79b633ea492c38fe09090f221`. This is a standalone research artifact. It neither modifies that repository nor installs new Adva operations.

## 中文提要

本轮得到一个可执行的最小下行构造：上行表达必须保留原问题，以及将上层候选接回原问题的关系；下行计算寻找这条关系中的具体见证，并在原问题一侧验收。`empty/universe` 描述孔的最小语法内容与合法填法族之间的读法，仍不足以自动构造见证。

在 F7 中，把 `2*x²+6=t` 上行改写为 `2*y+6=t`，会得到一个确定的 y。返回时需要解 `x²=y`：t=1 有两个填法 1、6；t=5 得到 y=3，但没有任何填法。所有七个 t 均已逐点核验。成功回答存在性后，未访问位置仍保留；空候选、无解证明、义务完成、资源耗尽分别记录。

另一个关键结果是闭圈障碍：三条局部关系 `x=y, y=z, z≠x` 每条都可实现，却不能共同实现。沿圈复合是 `H(x)=x+1`（F2），没有不动点。保持语义的坐标切换只会共轭 H，不能凭换坐标制造不动点。这个结果支持把“局部接口归零”和“整圈相容”分开，也为 `break` 暴露开放接口、`communicate` 提供新的边界条件留下了明确的研究位置。

验证范围：689 个至多 3×3 的二值关系，37,477 组子集配对，10,108 次闭包检查；七个算术目标；五个有限返回过程；八个篡改控制全部拒绝。它们检验本笔记的有限模型，不证明 adva 已完成通用解释、内生突破或三机全局闭合。

## 1. The actual inherited boundary

Research 0079 already contains a closer starting point than the earlier conversation's bare equation `Models(empty)=universe`: an aperture has minimal syntactic content while its filling fibre contains all admissible fillings visible in the declared carrier. It distinguishes an absent aperture, a grounded aperture with an empty fibre, and a fibre with several fillings. Closing a multivalued fibre requires explicit selection and retains alternatives and history.

Research 0132 defines a checked coordinate switch, separately from judgment and target revision. Research 0133 distinguishes execution stopping from existence, complete enumeration, and uniqueness judgments. Research 0135 requires frame changes to retain accumulated fuel. Research 0091 gives stronger conditions for endogenous scope breakthrough, including internally generated proposals and later effective reuse.

These distinctions determine this note's scope. The experiment supplies its feature map externally, performs no vocabulary discovery, creates no native semantic identities, and does not claim an endogenous breakthrough. Its purpose is to specify and pressure-test a return interface that a future breakthrough mechanism could be required to carry.

Two earlier conversational compressions need correction:

1. Empty constraints admitting a whole domain is one precise mathematical reading. It does not uniquely determine an interpretation relation or a decoder.
2. Reversing roles can reverse a relation. It does not supply an inverse function, recover discarded history, or establish that a semantic obligation has been met.

## 2. One relation, two directions of reading

Fix a declared domain X of possible objects or fillings, a set Q of questions or tests, and a relation R contained in X×Q. Write x R q when x satisfies q. This Boolean relation describes satisfaction; evidence for an incidence must be carried separately in a computational realization.

For A contained in X and B contained in Q, define

$$
A^{\uparrow}=\{q\in Q:\forall x\in A,\ xRq\},\qquad
B^{\downarrow}=\{x\in X:\forall q\in B,\ xRq\}.
$$

Then

$$
\varnothing_Q^{\downarrow}=X,\qquad
\varnothing_X^{\uparrow}=Q.
$$

The subscripts matter: these are empty sets on different sides. This equation is a statement about a relation and universal quantification. It is not an equality between an empty collection and a nonempty collection on one side.

**Proposition 1 — antitone correspondence.**

$$
B\subseteq A^{\uparrow}\quad\Longleftrightarrow\quad
A\subseteq B^{\downarrow}.
$$

**Proof.** Both sides state that xRq for every pair (x,q) in A×B. Consequently each derivation reverses inclusion. Also A is contained in A↑↓; applying the two order reversals shows that ↑↓ is monotone. The adjunction gives A↑↓↑=A↑, hence ↑↓ is idempotent. The dual argument applies to ↓↑. These are elementary relation-induced Galois closure laws. ∎

This formalizes a two-sided reading, but no particular R is selected by the extreme-value equations. Many inequivalent relations have exactly these same empty/universe laws. Recovering the intended R remains a substantive task.

### Four different emptiness claims

| Expression | Meaning | What would justify it? |
| --- | --- | --- |
| An unfilled typed placeholder | No filling has yet been selected | A declared aperture and its admissible carrier |
| Pending obligations = empty | The fixed local requirements have been discharged | Receipts bound to those requirements |
| Filling fibre = empty | No admissible filling exists in this scope | An applicable proof, or checked exhaustive finite coverage |
| Discovered candidates = empty | No candidate has been found so far | A search observation; this alone decides no existence question |

There is also a useful unit check. An assignment to zero holes has exactly one empty tuple, so the empty product of filling sets is `{()}`. An empty family of candidates is the empty set. Neither convention can be changed by dropping its type. Likewise, a universally quantified assertion over an empty fibre can be true without supplying any witness.

## 3. Downward interpretation needs a filling relation and a witness

Let an upward feature map be

$$
\alpha:X\longrightarrow Y.
$$

Reversing its graph yields a relation whose value at y is

$$
\operatorname{Fill}_{\alpha}(y)=\{x\in X:\alpha(x)=y\}.
$$

This is a legitimate return interface even when α is many-to-one. It may be empty, singleton, or multivalued. Computing its members, or selecting one with a certificate, is additional work.

**Proposition 2 — exact reconstruction requires retained distinctions.** If α(x₁)=α(x₂) for distinct x₁,x₂, there is no function d:Y→X with d∘α=id_X.

**Proof.** Such a d would have to assign both x₁ and x₂ to their common feature. ∎

To reconstruct the original x, retain a residual r(x) such that x↦(α(x),r(x)) is injective. Within a fibre of size k, r must distinguish at least k cases; a fixed-length binary residual therefore needs at least ceil(log₂ k) bits. This bound concerns reconstruction of the original input. Selecting a fresh valid member is a different task and need not recover the original branch. Neither task identifies native process histories.

### A minimal constructive return contract

Let p:X→{false,true} be the original predicate and p′:Y→{false,true} the transformed predicate. A sufficient return package consists of:

- the original problem and its frame;
- an abstract witness y with evidence for p′(y);
- a concrete candidate x;
- a checked link α(x)=y;
- a preservation argument p′(α(x)) ⇒ p(x), in the declared scope;
- the retained alternatives, process history, and cost record.

**Proposition 3 — checked descent.** Under those premises, p(x) holds.

**Proof.** Substitute α(x)=y in p′(y), then apply the preservation implication. ∎

A checker can instead recheck p(x) directly. Retaining the link still matters if the result is claimed to be a return of this particular upstream candidate rather than an independently found answer.

The executable operation is thus a bounded search/check over a proof-relevant fibre, schematically

$$
\operatorname{Lift}_{C}(y)
=\sum_{x\in X_C}
\operatorname{Evidence}(\alpha(x)=y)
\times\operatorname{Evidence}(p_C(x)).
$$

This notation specifies obligations; it does not implement an unrestricted proof search. The finite calibration below uses exact arithmetic evidence. An abstract witness with no concrete filling is a return obstruction, not permission to remove the original obligation.

### Return paths compose in reverse order

Suppose a second feature β:Y→Z is used. Returning z requires a witnessed pair β(y)=z followed by α(x)=y. The combined link is (β∘α)(x)=z, with both intermediate witnesses retained. Predicate preservation composes by implication. Returning through two levels therefore follows the reversed sequence of upward interfaces.

The abstract feature (β∘α)(x) alone does not select x. The finite cost of both lifts and both checks belongs to the same return record. Relational composition that forgets its intermediate witness can serve as a set-level description, but is insufficient as the full computational receipt.

## 4. Concrete arithmetic return in F7

Use the same polynomial family as the existing goal-relative calibration:

$$
f(x)=2x^2+6\pmod 7,\qquad f(x)=t.
$$

The supplied upward feature is y=x². In the new expression,

$$
2y+6=t,\qquad y=4(t-6)\pmod7,
$$

because 2·4=1 in F7. This gives an abstract answer for every t. Returning it requires an x in the square fibre.

| t | Abstract y | Complete concrete fibre | Return result |
| --- | --- | --- | --- |
| 0 | 4 | {2,5} | Two valid fillings |
| 1 | 1 | {1,6} | Two valid fillings |
| 2 | 5 | empty | No lift in F7 |
| 3 | 2 | {3,4} | Two valid fillings |
| 4 | 6 | empty | No lift in F7 |
| 5 | 3 | empty | No lift in F7 |
| 6 | 0 | {0} | One valid filling |

For t=1, selecting x=1 proves existence; x=6 remains an alternative. The abstract y=1 cannot determine which of those two inputs was originally used. One branch bit suffices to restore that distinction. The calibration explicitly checks reconstruction of all seven inputs from a square value and its branch index.

For t=5, the abstract calculation is valid: y=3 solves 2y+6=5 in F7. But no square in F7 equals 3. The missing domain restriction is

$$
y\in\alpha(X)=\{0,1,2,4\}.
$$

Retaining this restriction at the upper level, or checking the fibre during return, prevents a spurious success. Computing an exact image restriction can itself be expensive in other problems. This small example establishes no search speedup.

The preserved equality f=β∘α, where β(y)=2y+6, is not by itself an abstract-witness existence theorem: it says what happens to concrete inputs and says nothing about whether an arbitrary y has a preimage.

### Quantifier direction check

For a predicate set P contained in X, define the existential and universal readings of a fibre:

$$
\exists_\alpha(P)=\{y:\exists x\in\alpha^{-1}(y),\ x\in P\},
$$
$$
\forall_\alpha(P)=\{y:\forall x\in\alpha^{-1}(y),\ x\in P\}.
$$

They satisfy the complement duality

$$
\forall_\alpha(P)=Y\setminus\exists_\alpha(X\setminus P).
$$

At y=3, the fibre is empty. Even the predicate false holds universally over that fibre; no existential witness follows. A point-level return therefore requires an inhabited fibre in addition to an applicable universal preservation property. This is exactly where an untyped empty/universe shortcut can fail.

## 5. Polarity cancellation has to be indexed and checked

Three mathematical operations must retain their own types:

| Operation | Its exact action | What it does not establish |
| --- | --- | --- |
| Relation transpose | Exchange the two positions in each incidence | Complementation, functional inversion, or historical reversal |
| Boolean complement | Exchange a subset with its relative complement | A witness in either subset |
| Additive inverse | Negate an element of an additive group | Satisfaction of a semantic interface |

A useful external accounting model is the free abelian group on a declared finite set I of obligation occurrences. Each request contributes −e_i; an accepted response for that very occurrence contributes +e_i. The complete boundary balance is a vector

$$
b=\sum_i(n_i^{\rm accepted}-n_i^{\rm requested})e_i.
$$

With exactly one registered request per i, no duplicate accepted response, and acceptance gated by the appropriate checker, b=0 is equivalent to discharge of those registered obligations. The proof is componentwise: every coefficient is −1 or 0 and is zero precisely when that request has its accepted response.

Those invariants are premises. Merely asserting a matching label on a false payload cannot enter an accepted response. Nor may different obligation coordinates be collapsed into one scalar: the vector (1,−1) has scalar sum zero while both coordinates remain nonzero. Over a finite field, modular count cancellation would introduce additional false zeros; the obligation ledger here uses integer counts.

Even a legitimately zero boundary retains its witness history. A process can have no exposed interface at a chosen cut and still have performed work or contain a nontrivial internal cycle. This external ledger is not Adva's native additive formation residual, a new chain-complex theorem, or an authorization to identify histories.

## 6. A three-sided obstruction and its exact invariant

Take x,y,z in F2 and require

$$
x=y,\qquad y=z,\qquad z\ne x.
$$

Every pair relation is nonempty and gives a total bijective transfer. Every two of the equations can also be satisfied. Their joint solution set is empty.

**Proposition 4 — loop existence is a fixed-point condition.** For deterministic interface maps f₀₁, f₁₂, f₂₀, compatible assignments around the loop are in bijection with fixed points of

$$
H=f_{20}\circ f_{12}\circ f_{01}.
$$

**Proof.** Any compatible assignment has x₁=f₀₁(x₀), x₂=f₁₂(x₁), and x₀=f₂₀(x₂), hence H(x₀)=x₀. Conversely, a fixed x₀ defines x₁ and x₂ by the first two maps and satisfies the third. ∎

In the example, f₀₁ and f₁₂ are identities and f₂₀ flips the bit, so

$$
H(x)=x+1,\qquad H(x)-x=1\quad\text{in F2}.
$$

No fixed point exists. This is an exact finite loop obstruction; no geometric holonomy of Q4/M6 has been established by this example. The similarity is a calibration target whose native interfaces remain to be constructed.

**Proposition 5 — a faithful coordinate switch cannot remove this obstruction.** For bijective coordinate changes s_i on the three carriers, define transformed edge maps f′_ij=s_j∘f_ij∘s_i⁻¹. Then

$$
H'=s_0\circ H\circ s_0^{-1},\qquad
\operatorname{Fix}(H')=s_0(\operatorname{Fix}(H)).
$$

**Proof.** The intermediate coordinate changes cancel in the composite. The fixed-point equation is then transported by s₀. ∎

For invertible edges, reversing the whole traversal replaces H by H⁻¹; its fixed-point set is the same. This conclusion applies to a consistent reversal of all edges, not an arbitrary rewiring called swap.

The consequence is important for the vocabulary. A semantics-preserving switch can make an answer easier to express or find, but cannot turn a nonexistent compatible filling into an existing one. A genuine problem revision must declare what relation or constraint changes. Cutting a loop exposes an interface and can permit a finite return; the removed closure requirement must remain explicitly open. It cannot be silently counted as solved.

## 7. Proposed operational placement of the working words

These are scoped proposals, not new definitions imposed on Mingli's intended vocabulary and not native builtin specifications.

| Working word | Candidate role in the return construction | Required retained information |
| --- | --- | --- |
| empty | Minimal placeholder content, or an explicitly typed empty collection | Which collection, scope, and quantifier are meant |
| universe | The admissible carrier against which fillings and coverage are read | Domain and restrictions; not a completed physical universe |
| swap | Read a specified correspondence with its two positions exchanged | Original relation; multiplicity; this does not repurpose native wire swap |
| switch | Commit a checked change of frame or representation | Preservation evidence, old/new frame, prior expenditure |
| break | Exit this bounded computation with a typed result and return destination | Goal-specific evidence or Unknown, pending work, continuation cursor |
| communicate | Deliver a scoped result to an interface that can check and use it | Request binding, payload, witness, recipient interface, receipt, and context |
| breakthrough | Generate and try a scoped extension according to the stronger inherited requirements | A return interface is proposed as an additional usability obligation |

The successful local sequence is: form an explicit request; choose an admitted frame; construct an upstream candidate; resolve its return fibre; check the result at the original interface; record the discharge; return to the continuation. A failure or Unknown also returns a typed record but does not discharge a positive existence obligation.

The phrase “current time and space” can be represented minimally here by an occurrence of a request, its active frame, ordering, and finite resources. No measured spacetime semantics is inferred. Human communication also supplies intention and correction that the arithmetic checker cannot validate. The current dialogue provides such external input; no actual messages are sent by this experiment.

For an inconsistent closed cycle, a further structural reading of break is worth retaining: expose a boundary at which communication can supply information or initiate a justified revision. This reading still needs an explicit calculus. It is not derived merely from the usual programming-language statement `break`.

## 8. Relationship to established work

**Two-sided structure.** Pratt's Chu-space presentation makes a relation/matrix and its two orientations explicit; its transpose exchanges carrier and cocarrier. A Chu transform has two component maps constrained by an incidence equation. This is a useful vocabulary for asking which paired maps preserve an interface. The relation derivations in Section 2 and the actual evidence-return calculus are separate constructions; no equivalence to all of Chu theory is claimed. See [Pratt, Chu Spaces, 1999 lecture notes](https://ncatlab.org/nlab/files/Pratt-ChuSpaces.pdf), Chapter 1.

**Abstraction and return.** Cousot and Cousot's abstract interpretation supplies an established framework for relating more concrete and more abstract computations and accounting for loss of precision. The distinction between an abstract answer and an inhabited concrete fibre is compatible with that tradition. This note does not supply abstract fixpoint operators, widening, or a complete analyzer. See [Cousot and Cousot, POPL 1977](https://www.di.ens.fr/~cousot/COUSOTpapers/POPL77.shtml).

**Communication and proof reduction.** DeYoung, Caires, Pfenning, and Toninho relate linear-logic cut reduction to session-typed communication. A provider/use interface and checked continuation therefore have a precise prior theory to compare against. Applying that correspondence to Adva would require actual process typing and reduction rules; arithmetic token cancellation is insufficient. See [Cut Reduction in Linear Logic as Asynchronous Session-Typed Communication, CSL 2012](https://doi.org/10.4230/LIPIcs.CSL.2012.228).

The proposed contribution here is the specific alignment of these checks with Mingli's missing downward connection, together with an executable calibration and a small loop obstruction. Its broader novelty has not been evaluated.

## 9. Completed finite verification

The contract in `contract.json` was written before execution. One invocation of `calibration.py` completed with `PassedFiniteCalibration`; no repair execution or automatic continuation was used.

| Check | Observed result |
| --- | --- |
| Every binary relation with 0≤|X|,|Q|≤3 | 689 relations |
| Antitone correspondence against direct incidence inspection | 37,477 subset pairs passed |
| Extensivity and idempotence, both sides | 10,108 closure checks passed |
| Relation transpose twice | 689 round trips passed; relation equality only |
| All targets for the F7 equation | Seven targets; all seven source positions independently checked per target |
| Bounded return receipts | Five receipts accepted with their actual logical statuses |
| Corrupted receipt controls | Eight rejected |
| Serialized arithmetic and receipt replay | Passed |
| Three-way obstruction | All eight global Boolean assignments checked; no compatible triple |

The five return receipts are:

| Target | Candidate fuel | Visited x | Judgment | Unvisited x |
| --- | --- | --- | --- | --- |
| 1 | 7 | 0,1 | VerifiedExists, x=1 | 2,3,4,5,6 |
| 5 | 7 | 0,1,2,3,4,5,6 | RefutedExistsFiniteScope | none |
| 1 | 0 | none | Unknown | 0,1,2,3,4,5,6 |
| 1 | 1 | 0 | Unknown | 1,2,3,4,5,6 |
| 5 | 2 | 0,1 | Unknown | 2,3,4,5,6 |

The eight corruptions cover false arithmetic, stale target, stale frame, changed goal, omitted negative coverage, forged success with zero fuel, repeated position, and a Boolean masquerading as an integer position. The receipt checker evaluates squares by repeated addition and reconstructs original-equation satisfaction; the producer uses multiplication and an affine inverse. They share a Python runtime and scope constants. This is algorithmic separation, not two independently verified trusted kernels.

The relation checker implements derivations using intersections of row/column sets and compares them with direct pairwise incidence checks. The general propositions in this note have their own mathematical proofs. The finite truth tables are implementation calibration, not a proof about arbitrary cardinalities.

The round-trip fuel/history item in `countermodels` is an illustrative accounting record, not a newly executed frame-switch implementation. The branch reconstruction and Boolean-cycle checks are executable. Keeping this distinction prevents a hand-written record from being mistaken for a transition certificate.

### Costs and enforcement

The invocation had a 20-second external timeout and in-process wall alarm, a 15-second CPU limit, 256 MiB address-space limit, 1 MiB per-file size limit, and 2,000,000 declared logical work units. No native Adva command was invoked.

Observed: 53,198 logical units, approximately 0.061 seconds inside the process including its final checkpoint, 11,520 KiB peak RSS, and an 8,941-byte evidence file. These are one-run measurements, not a benchmark. Logical units count the specified loops and serialization operations, not machine instructions. The final output write is separately bounded by the OS limits. Research, source retrieval, source authoring, and remote saving are excluded from these execution measurements.

Hard process termination can prevent a final artifact; the successful observed invocation did preserve its evidence. There is no promised checkpoint under every possible operating-system failure.

## 10. Reproduction and next mathematical obligation

Use Python 3.11 or later on Linux, from the extracted directory:

```sh
timeout 20s python3 calibration.py --contract contract.json --output evidence-new.json
```

The output path must be new. The program records hashes of its source and contract. Those hashes bind this external record to its bytes; they are not authentication or native semantic identities. The runner consumes the supplied local contract and is not intended as a hardened service for untrusted contracts.

The smallest useful successor is a return adapter over one existing Rust-checked witness: retain the original request, a checked correspondence, explicit alternative fibres, and the evidence supplied at each downward step. Any actual semantic transformation remains subject to the Rust validation boundary and relevant operation/IR design rules.

For the three-machine theory, the next mathematical obligation is sharper: identify the actual three interface relations, compose them with witnesses retained, and test the resulting fixed-point or relational compatibility condition. A positive local port balance is insufficient. A negative result should locate the boundary to open or the assumption to revise.

This round supports the intuition that a two-sided interface can connect local completion to further continuation. The decisive missing data are the return fibre, its inhabitant or obstruction, and the compatibility of successive returns. Empty/universe names the two-sided possibility; a checked return makes one use of it concrete.

## Repository sources inspected

All links below are pinned to the inspected commit; their historical status statements refer to the dates inside those documents, not to current open-PR status.

- [AGENTS.md](https://github.com/mountain/adva/blob/1c5979d78dc9c2b79b633ea492c38fe09090f221/AGENTS.md)
- [Research and Engineering Agenda](https://github.com/mountain/adva/blob/1c5979d78dc9c2b79b633ea492c38fe09090f221/docs/RESEARCH_ENGINEERING_AGENDA.md)
- [0079: Typed apertures](https://github.com/mountain/adva/blob/1c5979d78dc9c2b79b633ea492c38fe09090f221/docs/research/0079-typed-hole-open-close-calibration-v0.md)
- [0091: Endogenous scope breakthrough](https://github.com/mountain/adva/blob/1c5979d78dc9c2b79b633ea492c38fe09090f221/docs/research/0091-endogenous-scope-breakthrough-and-venture-ledger.md)
- [0129: Trusted boundaries](https://github.com/mountain/adva/blob/1c5979d78dc9c2b79b633ea492c38fe09090f221/docs/research/0129-bounded-breakthrough-trusted-boundaries.md)
- [0132: Structural adjustment](https://github.com/mountain/adva/blob/1c5979d78dc9c2b79b633ea492c38fe09090f221/docs/research/0132-structural-adjustment-evidence-applicability.md)
- [0133: Goal-relative stopping](https://github.com/mountain/adva/blob/1c5979d78dc9c2b79b633ea492c38fe09090f221/docs/research/0133-explore-open-universe-goal-relative-stopping.md)
- [0135: Frames and fuel](https://github.com/mountain/adva/blob/1c5979d78dc9c2b79b633ea492c38fe09090f221/docs/research/0135-reunderstanding-resource-frames-and-fuel.md)
