# Research 0259: Henkin witness completion and projective process-neighborhood duality

Date: 2026-10-08. Status: original mathematical synthesis with elementary
conditional arguments and a proposed native bridge. No new experiment,
native witness operation, higher-cell faithfulness theorem, or universality
claim is supplied.

Research direction: **Mingli Yuan**. Formalization, source comparison,
mathematical review, and this note: **Codex (OpenAI)**, submitted through
Mingli Yuan's GitHub account (`mountain`) as an authorized proxy. Account
use is not his authorship, review, endorsement, or a correctness guarantee.
The original contribution is offered under Unknown v0.3.

Inspected repository: `mountain/adva@e16134412b2ab4ca88d9d013743e06bcd6e06baf`.
This note continues [Research 0258](0258-henkin-completion-galois-closure-and-observer-separation.md)
and the 2026-10-08 discussion of Henkin completion, the Scott axioms, and
the August 2026 process-neighborhood working draft. It records a connection
between methods, not an identification of their formal systems.

## 1. The shared problem

An open requirement should acquire a compatible witness whose semantic
reading can be checked. A distinction that matters to the task should
survive that reading. Three obligations therefore remain separate:

1. **Realization:** a compatible requirement has a common witness.
2. **Separation:** the declared observations recover the required distinctions.
3. **Extension compatibility:** new witnesses and comparison cells respect
   the selected old judgments, source data, and coherence relations.

Henkin construction supplies a classical model for the first obligation
and, through completeness, separating models for formula equivalence
classes. Process-neighborhood duality specifies how a witness reading
transports along a process. A reconstruction theorem would connect those
readings to the intensional distinctions of programs and rewrites.

Here a required predicate is a constraint selected for a task. The word
"required" does not assert that the predicate is positive in the
Gödel-Scott sense. That interpretation requires a separate typed
positivity predicate and additional axioms.

## 2. What the Henkin analogy permits

In classical first-order logic, fresh witness constants and the appropriate
witness axioms can extend a consistent theory without adding consequences
in its old language. The construction must retain freshness, scope, and
the consistency argument; adding an arbitrary named object is insufficient.
An ensuing maximal consistent completion chooses among previously
undecided old-language sentences. It preserves consistency and extends
the theory, but need not be conservative over that original theory.

For higher-order logic, a Henkin general model uses restricted function
domains that still interpret the specified terms and satisfy their closure
conditions. An arbitrary set of finite probes is not automatically such
a domain. General-model completeness does not assert model existence in
full higher-order semantics.

Adva's computation grammar remains separate from these logical semantics.
Research 0087, section 10.1, offers well-formed terms as a possible witness
stock for a later interpretation. It supplies neither the satisfaction
lemma nor the consistency-preserving extension theorem. In particular,
an input hole, a logical existential requirement, and an observer aperture
cannot be identified solely because each invites a filling.

## 3. A witness-sensitive process-neighborhood interface

Fix a context `Gamma`, a history carrier `H_Gamma`, an observer domain
`Phi_Gamma`, and a declared groupoid-valued pairing

\[
\rho_\Gamma:\mathscr H_\Gamma\times\Phi_\Gamma\longrightarrow\mathbf{Gpd}.
\]

An object of `rho_Gamma(h, phi)` is a witness of the observation `phi` at
the particular history `h`. Its morphisms are the comparisons admitted by
this interpretation. A proposition's truth value and this groupoid of
witnesses are different semantic layers.

For a typed process `D: Gamma -> A`, suppose the interpretation provides

\[
D_*:\mathscr H_\Gamma\to\mathscr H_A,
\qquad D^*:\Phi_A\to\Phi_\Gamma,
\]

and the process-neighborhood comparison

\[
\rho_A(D_*h,\psi)\simeq\rho_\Gamma(h,D^*\psi).
\tag{PD}
\]

Thus forward execution and backward observation read the same witness.
The projective realization of this interface uses inverse images of
neighborhoods under the chronological arithmetic action. Witness transport
additionally needs the declared proof-relevant pairing; an equality of
ordinary inverse-image subsets alone does not provide proof transport.

For a finite family `Psi = {psi_1, ..., psi_m}`, first define independent
witnesses at one fixed history by

\[
W_A(k;\Psi)=\prod_{i=1}^m\rho_A(k,\psi_i).
\]

This product uses a common history. It does not impose any extra relations
among its certificates. Requirements involving shared evidence or higher
coherence need a separately specified compatible diagram and its homotopy
limit, or another carrier with an explicit invariance argument, instead.

An empty proof fibre only says that no witness occurs in that fibre.
It is not a certificate of logical falsity unless the interpretation
includes and proves the relevant adequacy theorem. Signed constraints
must use their declared negative certificates. In Research 0258's finite
Boolean interpretation, `e not in I` is an exact negative observation;
that fact does not extend automatically to arbitrary proof fibres.

## 4. Conditional witness transport and the missing lift

**Proposition 1 (fixed-history witness transport).** For a finite family,
the comparisons (PD) induce an equivalence

\[
W_A(D_*h;\Psi)\simeq W_\Gamma(h;D^*\Psi).
\tag{WT}
\]

**Proof.** Take the finite product of the given equivalences. This proves
the pointwise statement. A functorial comparison requires their declared
naturality. For a compatible witness diagram, a coherent equivalence of
the diagrams induces the comparison of their homotopy limits. Pointwise
equivalences alone do not preserve arbitrary strict limits. Neither
coherence nor compatibility is obtained by dropping that data. End of proof.

Consequently a source history witnessing the pulled-back requirements
produces a target history witnessing the original requirements. The
converse for an arbitrary target history is an additional lifting problem.
It holds for a target witness at `k` if a source history `h` with
`D_*h` isomorphic to `k` is provided and witness transport along that
isomorphism is part of the interpretation. A general converse requires
appropriate essential surjectivity or a weaker lift for the particular
requirements at issue.

**Hand counterexample.** Let the source carrier be `{s}`, the target
carrier `{a,b}`, and `D_*(s)=a`. Use discrete truth fibres, with `psi`
true exactly at `b`, and interpret `D^*` by inverse image. The pairing
law holds, and `psi` has a target witness, but its pullback has none.
This is a mathematical example, not an executed native experiment.

The quantified realization goal is

\[
\mathsf{Compatible}_Q(\Psi)
\Longrightarrow \exists h\; W_Q(h;\Psi)\ne\varnothing,
\tag{HR}
\]

with the compatible version of `W` when needed. `Compatible_Q` must have
an independent definition; defining it as the right-hand side makes (HR)
tautological. A Henkin-style theorem would construct the witness and prove
its reading. The pairing law by itself does not establish (HR).

An extension of histories needs its own compatibility argument. Suppose
a declared forgetting process `r` satisfies `r_*h'=h`, and its pairing
law identifies `rho_new(h', r^*phi)` with `rho_old(h, phi)` for the retained
old observers. Then those particular old witness spaces are preserved.
An arbitrary history extension supplies neither this projection nor the
pairing law. This pointwise preservation also does not show that every old
history has a lift through `r_*`.

For finite independent requirements at a single fixed `h`, nonempty
individual fibres do yield a nonempty product. The failure to avoid is
the different quantifier exchange

\[
\forall\psi\in\Psi\;\exists h_\psi\text{ witnessing }\psi
\quad\not\Longrightarrow\quad
\exists h\;\forall\psi\in\Psi\text{ witnessing }\psi.
\]

For example, each of `{a,b}`, `{a,c}`, and `{b,c}` is inhabited in
`{a,b,c}`, while their common intersection is empty.

## 5. Realization does not repair a fixed observation

Work at explicitly selected equivalence classes, such as rewrite
2-cells modulo the admitted invertible 3-coherence. Let `S` be the old
set of classes, `O:S -> V` the observation, and `j:S -> S'` an extension.

**Proposition 2 (collision persists under a preserving extension).**
Suppose `j` is injective on the old classes and
`O':S' -> V` satisfies `O' j = O`. If `alpha != beta` but
`O(alpha)=O(beta)`, then `O'` still fails to separate these old classes.

**Proof.** Injectivity gives `j(alpha) != j(beta)`, whereas

\[
O'(j\alpha)=O(\alpha)=O(\beta)=O'(j\beta).
\]

End of proof. Higher-categorical versions must replace these sets and
equalities with their stated quotient and coherent comparison; this note
does not silently promote the elementary argument to every such version.

Thus witness completion can resolve missing realization while the old
observer still loses information. Repairing that loss requires additional
observations, or a justified change to the distinctions demanded by the
task. If the extension identifies the old classes instead, it has changed
the separation contract and fails the injectivity assumption above.

## 6. Objectification as a separate coherent witness

For `f:X -> Y`, let

\[
S_f=\delta_Yf,\qquad R_f=(f\otimes f)\delta_X.
\]

They describe computing once and sharing its result, and sharing the
input before computing twice. A task-level comparison may exist between
their observations. A certified objectification additionally needs a
declared invertible cell and its required coherence.

For a process `f` whose interpretation creates a fresh result source per
execution, the two output occurrences of `S_f` share one result source,
while those of `R_f` have two distinct result sources. Equal scalar
values do not supply a source-preserving cell. The example depends on
that declared source policy; it does not apply to every `f`, such as
identity routing. This is a mathematical constraint, not a new native
execution.

Let `Obj_Q(f)` be the groupoid of admitted coherent witnesses and define
the comparison to observed equivalences schematically as

\[
\Lambda_{Q,f}:\mathsf{Obj}_Q(f)\longrightarrow
\mathsf{Eqv}_Q(S_f,R_f).
\]

The exact carriers remain part of the future construction. At the
groupoid level the following obligations are distinct:

| Obligation | Precise question |
| --- | --- |
| Existence | Is `Obj_Q(f)` nonempty? |
| Chosen witness | Is a concrete object and its coherence supplied? |
| Object separation | Is `pi_0 Lambda` injective? |
| Faithfulness | Are morphisms between fixed witness objects distinguished? |
| Fullness | Can comparisons between their images be lifted? |
| Essential surjectivity | Does every observed equivalence have a lift up to isomorphism? |
| Canonical lift | Is each relevant homotopy fibre contractible? |

The last row retains the comparison isomorphism with the chosen observed
equivalence. It is not a bare set fibre and is not the assertion that
the entire source groupoid is contractible.

Fix the syntax, source rules, coherence, and admission policy. If observer
refinement only adds constraints and there is a compatible forgetting
functor `Obj_Q'(f) -> Obj_Q(f)` on admitted witness groupoids, an existing
fine-level witness can be sent to the coarser level. This proves monotonicity
of witness existence. Forgetting on observations alone does not establish
that functor. Neither contractibility nor canonicity follows from existence
monotonicity. Likewise, absence of an admitted lift does not imply absence
of an observed equivalence.

## 7. The role and limits of universality

The working draft proposes three distinct universal targets:

| Construction | Data required of an interpretation |
| --- | --- |
| Free higher sharing syntax | Interpret the generators and satisfy the specified relations |
| History observer completion | Interpret representables and satisfy the chosen enrichment and colimit hypotheses |
| Free task-relative objectification | Interpret the old calculus and provide all specified coherent objectification witnesses |

These properties specify how an interpretation extends from those data.
They do not prove that the data exist or that every extension is faithful.
In particular, freely adjoining an objectification symbol does not show
that a given source-preserving semantics can interpret it.

In a fixed strict or semistrict three-dimensional presentation, the full
representable history assignment `Y(A)=C(-,A)` recovers its actions by
evaluation at the source identity. That supplies a separation upper bound.
Relating it to groupoid-valued observers requires an explicit enrichment
and truncation policy. Restricting to five kinds of observers does not
itself yield a finite probe set: finite coverage is relative to a fixed
carrier or a declared size bound.

The open question whether universality should be called a positive
property must first fix a common domain of structures and a predicate
`U(x)` on that domain. `P(U)` is then an additional positivity judgment.
A universal mapping property alone supplies neither that judgment nor
a common realizer of all the other proposed positive properties. This
note adopts no Gödel-Scott positivity axiom for native Adva.

## 8. The next native bridge and retained residual

Research 0258 checks abstract finite posets: compatible signed requests
have the least witness `down(P)`, and event-membership probes separate
different ideals. Its 242-poset calibration contains no extraction of
native events, proof transport, or Peiffer 3-cells.

The narrow successor is to fix one Rust-checked finite acyclic diagram
`D`, its source and occurrence identities, and its causal order, using
[Research 0005](0005-causal-cut-alexandrov-topology.md) as the carrier reference.
Restrict to legal causal prefixes executing each node at most once and
quotient only by swaps of independent events. The proposed obligations are:

1. legal prefix classes correspond to the declared completed pasts;
2. compatible ideal requests have a legal prefix realization;
3. checked event-membership probes satisfy the intended reading;
4. source-decorated frontier transport agrees along two legal routes, or
   returns a retained invariant residual.

The fourth obligation must not be called an implemented higher filler.
Fixed-diagram membership separation also does not prove cross-diagram
reconstruction, general 2-cell separation, or 3-cell faithfulness. Rust
remains the authority for identities and certificates; Python calibration
cannot authorize these judgments. This is a research target in the existing
agenda, not the installation of a stable operation or a new run contract.

## 9. Sources, review, and publication scope

- Leon Henkin, *The Completeness of the First-Order Functional Calculus*,
  JSL 14(3), 1949, 159-166, [DOI 10.2307/2267044](https://doi.org/10.2307/2267044).
  The first-order calibration continues the reading recorded in 0258.
- Leon Henkin, *Completeness in the Theory of Types*, JSL 15(2), 1950,
  81-91, [DOI 10.2307/2266967](https://doi.org/10.2307/2266967).
  The publisher's abstract and domain-closure notes were inspected for the
  general-model boundary; this is not a claim of a new proof of completeness.
- *Projective Process--Neighborhood Duality: History-Augmented Chu
  Semantics, Proof Geometry, Task-Relative Objectification, Faithfulness,
  and Universality*, author field: Characteristica / Process Geometry
  Research Notes, August 2026, working draft v0.2. The actual supplied file
  is `projective_process_neighborhood_calculus_working_draft_v2.tex`,
  Library identifier `libfile_ec88e6a4ceb481918df757ef5a94cdd9`. Its 2702-line
  source was retrieved in this conversation. Relevant parts are sections
  15, 21-28, and 30-36. The file is a research input outside this repository;
  this note publishes original arguments and bibliographic identification,
  not its source text or a translation. Its conditional reconstruction and
  higher universal properties remain conditional or proposed.
- Christoph Benzmüller and Dana Scott, *Notes on Gödel's and Scott's
  variants of the ontological argument*, Monatshefte für Mathematik 208,
  2025, 569-611, [DOI 10.1007/s00605-025-02078-x](https://doi.org/10.1007/s00605-025-02078-x).
  The article was consulted for the higher-order general-model setting;
  its axioms are not installed by this note.

Propositions 1 and 2 are original elementary arguments under their explicit
assumptions. Mathematical review checked the quantifiers, compatibility
conditions, target-image restriction, and distinct lifting obligations.
The hand examples were reasoned through, not machine-executed. No new
semantic checker or experiment was run for this note. Repository index,
admission digests, and publication-boundary checks concern document
integration and byte integrity, not mathematical or native admission.
