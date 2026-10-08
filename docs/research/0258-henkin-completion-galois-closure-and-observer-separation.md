# Research 0258: Henkin completion, Galois closure, and observer separation

Date: 2026-10-08. Status: original research synthesis with a reproduced
external finite calibration; the correspondence to native Adva halt words
remains **Open**.

Research direction and the proposed connection: **Mingli Yuan**.
Formalization, source audit, experimental replay, and this note: **Codex
(OpenAI)**. Submitted through Mingli Yuan's GitHub account (`mountain`) as
an authorized proxy. Account use is not his authorship, review, endorsement,
or a correctness guarantee. Original contributions are offered under
Unknown v0.3; classical completeness is not claimed as new mathematics.

Inspected base: `mountain/adva@6d7ab990021f201d189c92be5d3729b3a9d4bf42`.
The initiating conversation was the 2026-10-08 discussion of faithfulness,
Galois connections, and the construction of triadic halt words. The account
below is a source-grounded synthesis, not a verbatim transcript.

## 1. The intuition and its precise scope

Mingli proposed that the construction behind Adva's triadic halt words and
the Hintikka/Henkin completeness methods may share the technique used in
faithfulness arguments. The useful common mechanism is:

1. state an open obligation or a distinction that must survive;
2. extend it with admissible, checkable witnesses;
3. obtain a compatible completed object;
4. read that object through observations that retain the required distinction.

**Completion and separation are distinct obligations.** Existence of a valid
completion does not make its observation injective. Conversely, an injective
encoding does not show that each consistent request has a realizable
completion. Their strongest connection is constructive: realize each
consistent distinguishing request and verify its semantic reading.

The conversation initially asked about Galois-group faithfulness. Research
0160 concerns braid/Burau representations, not a Galois-group theorem.
Relation-induced Galois connections occur in Research 0158's downward
interpretation supplement. These are different uses of the name Galois.
This note establishes no result about the faithfulness of a Galois group.

## 2. What the existing Adva record actually supplies

All paths in this table are in `mountain/adva` at the inspected base.

| Source | Existing content | Boundary retained here |
| --- | --- | --- |
| `docs/research/0066-self-dual-characteristic-completion-calculus.md`, sections 1 and 7–9 | A Hintikka/Henkin calibration and a proposed proof/learning bridge | Its finite oracle is not a general tableau or native model-extraction theorem |
| `docs/research/0087-typed-three-domain-threaded-multihole-calculus.md`, section 10.1 | Well-formed computation terms as a future Henkin term stock; partial multi-hole configurations as candidate extensions | Constructor completeness is not logical completeness; the logic remains outside the computation grammar |
| `docs/research/0079-typed-hole-open-close-calibration-v0.md`, sections 2.4–2.5 | Grounded apertures, admissible filling fibres, and limits of fixed-language completion | Witness addition is not arbitrary concept invention; selecting a filling retains alternatives and history |
| `docs/research/0158-evidence/downward-interpretation-v0/downward-interpretation-v0.md`, sections 2–3 | Antitone Galois closure and a witnessed return fibre | Closure does not supply an inverse decoder or recover discarded distinctions |
| `docs/research/0160-faithful-switch-and-reverse-observer-search.md`, sections 3–5 | Compatible representations, separating observations, and the obstruction to recovering collisions by postprocessing | Compatibility is weaker than faithfulness; observation equality is not a native proof or coherence cell |
| `ontology/semantics/triadic-halt-circle-closure.md` | Seven nonempty halt-domain sets of one shared typed run | Only `H_KXt` closes the three machine-domain holes; semantic promotion still needs global compatibility |

Research 0101/0102's seven partition types of six ports must not be silently
identified with these seven halt words. Their grammar records formation and
retention obligations before a separate halting judgment. A selection
declaration alone does not fill a native hole or construct a circle.

For a shared run `r`, the working machine rule is

\[
\mathsf{HaltSet}(r)=\{K,X,t\}
\quad\Longleftrightarrow\quad
\mathsf{CircleClosed}(r).
\]

This rule does not identify halting with logical validity. It excludes fuel
exhaustion and three unrelated terminal traces. A global semantic closure
must retain compatible connectors, sources, occurrences, and residual
certificates; closing the three domain holes does not erase finer residuals.

## 3. The classical bridge: completeness gives separating models

For sets of sentences in a fixed classical first-order language with a sound and
strongly complete proof system, let

\[
\operatorname{Mod}(\Gamma)=\{M:M\models\Gamma\},\qquad
\operatorname{Th}(\mathscr M)=
\{\varphi\text{ a sentence}:\forall M\in\mathscr M,\ M\models\varphi\}.
\]

The satisfaction relation induces an antitone Galois connection:

\[
\mathscr M\subseteq\operatorname{Mod}(\Gamma)
\quad\Longleftrightarrow\quad
\Gamma\subseteq\operatorname{Th}(\mathscr M).
\]

Soundness and completeness identify the resulting theory closure with
syntactic consequence:

\[
\operatorname{Cn}_{\vdash}(\Gamma)
=\operatorname{Th}(\operatorname{Mod}(\Gamma)).
\]

This recovers the deductive closure, not the original presentation
`Gamma`. Different axiom sets can have the same models.

Henkin's classical construction extends the language with controlled witness
constants, extends consistency, constructs a model, and verifies the
semantic reading by induction on formulas. A saturated open Hintikka branch
is a related route to a model, under the declared saturation conditions.
Neither route is an algorithm deciding all first-order proof searches.

The separation consequence is especially close to the intuition. For
sentences `phi, psi` and a fixed theory `T`, if

\[
T\nvdash\varphi\leftrightarrow\psi,
\]

completeness gives a model of `T` where their truth values differ. Hence the
map from sentences **modulo `T`-provable equivalence** to their truth profiles
over all models of `T` is injective. It also reflects the entailment order.
One model need not separate all formulas. The whole separating model family,
the chosen quotient, and the semantic correctness argument matter.

Reference: Leon Henkin, *The Completeness of the First-Order Functional
Calculus*, JSL 14(3), 1949, 159–166,
[DOI: 10.2307/2267044](https://doi.org/10.2307/2267044).
The original proof was inspected for this calibration. No source text,
scan, translation, or external implementation is incorporated.

## 4. An exact finite analogue

Let `(E, <=)` be a finite event poset. Write `Down(E)` for its downward-closed
subsets, including the empty subset. Here **order ideal means downset**;
no directedness condition is imposed. Events and order relations in this
experiment are abstract inputs, not reconstructed Adva identities.

For positive requirements `P` and negative requirements `N`, define

\[
\operatorname{Sol}(P,N)=
\{I\in\operatorname{Down}(E):P\subseteq I,\ I\cap N=\varnothing\}.
\]

**Proposition 1 — canonical compatible completion.**

\[
\operatorname{Sol}(P,N)\ne\varnothing
\quad\Longleftrightarrow\quad
\downarrow P\cap N=\varnothing.
\]

When a solution exists, `down(P)` is its least member.

Proof: every downset containing `P` contains all predecessors of `P`, so a
negative event in `down(P)` blocks every solution. If there is no such event,
`down(P)` is itself a downset satisfying both requirements. Its containment
in every other solution proves minimality.

This is a finite propositional Horn calibration: each dependency `d <= e`
gives `x_e => x_d`. It has no existential quantifiers, fresh witness constants,
or maximal consistent first-order extension. It calibrates a saturation and
model-existence pattern, rather than implementing Henkin's full construction.

**Proposition 2 — completion supplies a countermodel.** If
`e` is not in `down(P)`, the canonical model `I=down(P)` satisfies every
positive requirement in `P` and makes `x_e` false. Thus the positive atomic
consequences of `P` under the dependency rules are exactly `down(P)`.

For clarity, there are two equivalent closure presentations here:

\[
\downarrow P\subseteq I\iff P\subseteq I,
\qquad I\in\operatorname{Down}(E),
\]

is the monotone adjunction of downward closure and inclusion. Alternatively,
define

\[
\operatorname{Mod}_+(P)=\{I\in\operatorname{Down}(E):P\subseteq I\},
\qquad
\operatorname{Th}_+(\mathscr I)=\bigcap_{I\in\mathscr I}I.
\]

The empty intersection is `E`. The antitone theory/model connection then has
`Th_+(Mod_+(P))=down(P)`: the least model belongs to the family and is contained
in every member. Raw `P` is not generally recoverable. On a chain
`e0 < eL`, the requirements `{eL}` and `{e0,eL}` have the same models.
Recovery applies to closed sets or closure-equivalence classes.

These propositions have the elementary proofs above. The finite replay below
calibrates the implementation; its bounded counts are not the proof of an
unrestricted Adva theorem.

## 5. Separation and the two retained negative controls

For each event define the membership observation

\[
q_e(I)=\mathbf 1_{e\in I},\qquad
\Phi(I)=(q_e(I))_{e\in E}.
\]

If `I != J`, an event in their symmetric difference separates them. Moreover,

\[
I\subseteq J\quad\Longleftrightarrow\quad
\forall e,\ q_e(I)\le q_e(J).
\]

Thus `Phi` is an injective extensional representation and an order embedding.
This separation uses set extensionality and access to every event. Its
nontrivial native obligation would be implementing the probes over checked
Adva evidence and identifying exactly which distinctions they preserve.

Take the fork `e0 < eL` and `e0 < eR`, with incomparable `eL,eR`:

| Control | Coarse answer | Exact answer |
| --- | --- | --- |
| `I={e0,eL}`, `J={e0,eR}` | Both have two events | `q_eL` separates them |
| `P={eL}`, `N={e0}` | `P` and `N` are disjoint | `down(P)` contains `e0`, so no compatible completion exists |

A Galois connection alone guarantees neither of these distinctions. A
deterministic recoding of the event count cannot repair the first collision;
the richer probe reads the retained event, not the count.

There is also a terminology trap. A poset is a thin category, so a functor
from it is automatically injective on each hom-set. This formal meaning of
*faithful* is too weak to express this experiment's result. The result here
is **object separation and order reflection**, not proof-relevant
faithfulness on Adva morphisms, equation cells, or coherence cells.

## 6. Frozen experiment and fresh replay

The supplied v0 files are retained byte-for-byte in
[`0258-evidence/`](0258-evidence/):

- [`henkin_faithfulness_finite_posets_v0.py`](0258-evidence/henkin_faithfulness_finite_posets_v0.py)
- [`henkin_faithfulness_finite_posets_v0.json`](0258-evidence/henkin_faithfulness_finite_posets_v0.json)
- [`replay.json`](0258-evidence/replay.json), recording source/report digests and this replay.

| `n` | All labeled posets | Signed constraint cases | Separated unordered ideal pairs |
| ---: | ---: | ---: | ---: |
| 1 | 1 | 4 | 1 |
| 2 | 3 | 48 | 12 |
| 3 | 19 | 1,216 | 214 |
| 4 | 219 | 56,064 | 5,970 |
| Total | **242** | **57,332** | **6,197** |

The source enumerates every pair orientation, rejects nontransitive orders,
enumerates all subsets and all signed constraints, and checks both existence
and the canonical least witness. Its expected poset counts are an additional
enumeration control. It checks separation of every distinct ideal pair and
the two concrete controls above.

Fresh ordinary and `python3 -O` executions each reproduced the retained JSON
**byte-for-byte**, including its source SHA-256 binding. Explicit `require`
checks remain active under `-O`. This is replay of the same algorithm; it is
not an independent verified kernel or a native Adva execution.

Reproduce from the repository root; the output must be a new path:

```sh
python3 docs/research/0258-evidence/henkin_faithfulness_finite_posets_v0.py --output /tmp/henkin-posets-fresh.json
cmp docs/research/0258-evidence/henkin_faithfulness_finite_posets_v0.json /tmp/henkin-posets-fresh.json
```

Only sizes 1 through 4 are executed. No performance, unrestricted search
termination, proof-assistant verification, event-trace reconstruction,
native observer implementability, or cell faithfulness is established.
The publication review is recorded in
[`research-0258-henkin-posets.json`](../../governance/publication/records/research-0258-henkin-posets.json).

## 7. The bridge still required for native triadic halt words

The next obligation is a correspondence theorem for **one declared native
finite carrier**, with its source and equality policy fixed:

1. Obtain events, precedence, source and occurrence identities from a
   Rust-checked carrier; do not reconstruct authority from Python masks.
2. Define which partial configurations or legal halt words map to downsets,
   and prove dependency closure for that map.
3. Prove realizability of the declared consistent requests by legal native
   configurations. A downset need not encode conflicts, exclusive choices,
   typing constraints, or global connector compatibility.
4. Implement membership probes with checked meanings and a replayable
   satisfaction lemma. Abstract access to a bit is not an observer certificate.
5. Fix the equivalence being separated. Equal event sets may still lose
   event order, construction history, aperture positions, sources,
   occurrences, alternatives, or cells. Retain these distinctions or justify
   a specific quotient.
6. Test a real coarse collision and a native separating witness, together
   with incompatible connectors, wrong-source labels, omitted prerequisites,
   and resource exhaustion that remains `Unknown`.

An ideal is one model in the analogue. The three domains may provide partial
readings of a shared candidate; they are not three arbitrary independent
models. In particular, three local satisfactions cannot replace a global
compatibility certificate.

The finite result supports the proposed shared **witness-and-separation
mechanism**. The decisive gap is the native realization and satisfaction
bridge, rather than the number of abstract cases checked. This note records
that gap without adding a stable operation, changing dependency locks,
registering a general completeness claim, or treating Git integration as
an executed Adva content exchange.
