# Q4--M6 Juxtaposition and Proof-Carrying Search for Low-Resource Go

Status: exploratory research note. This note proposes a falsifiable application
of the `cell -> carrier -> views` architecture. It adds no stable Adva syntax,
Go rules engine, game-value interpreter, certified quotient, or claim that
`Q4` and `M6` suffice for strong full-board play.

This note continues:

- [note 0103](0103-cell-carrier-view-relation-machines.md), which introduces
  dimension-indexed relation cells, the `Q4` interchange boundary, the `M6`
  braid boundary, and open view contracts; and
- [note 0104](0104-whole-cut-six-to-m6-boundary-bridge.md), which derives one
  open `M6` boundary from the six-port whole-cut incidence ledger without
  manufacturing a filler.

The application question is deliberately narrow:

> Can certified local `Q4` interchange and candidate `M6` braid
> reorganization quotient redundant Go histories cheaply enough to support an
> exact or hybrid low-resource player?

The strongest present answer is conditional. `Q4` has a mature analogue in
independence-based partial-order reduction and in the decomposition of Go
endgames into local games. `M6` is a plausible extension for overlapping but
coherently reorganizable histories; no general Go braid law is known or
assumed here.

---

## 0. Notation gate: `Q4`, not `D4`

The current Bootstrap Zero notation is:

\[
Q_4=\partial\chi_{a,b}
\qquad\text{for}\qquad
\chi_{a,b}:ab\Rightarrow ba,
\]

where `Q4` names a four-occurrence square relation boundary. By contrast,
\(D_4\) conventionally names the dihedral symmetry group of a square (with
order conventions varying across the literature). They are related but not
interchangeable:

- `Q4` is a cell boundary;
- `D4` may act on presentations of that boundary by rotations and reflections.

Accordingly this note studies `Q4--M6` juxtaposition. It retains a possible
`D4` symmetry view as a separate extension. Such a view may canonicalize
rotated or reflected local Go patterns, but only after checking player color,
turn, edge/corner location, ko state, and scoring conventions. A color swap may
induce negation of a game value rather than raw equality.

---

## 1. Historical anchor and scope

Partizan combinatorial game theory was motivated in part by the decomposition
of late Go endgames into sums of local games. Berlekamp and Wolfe subsequently
developed this connection into a precise theory of values, temperature,
cooling, sente, and gote. Their results concern positions whose interactions
can be controlled well enough for local game analysis; they do not make
general full-board Go a direct surreal-number calculation.

Martin Mueller's decomposition search supplied an algorithmic precedent: use
independent local subgames and combinatorial-game structure to avoid a large
traditional minimax expansion. The proposed `Q4--M6` layer should therefore be
judged against two established baselines:

1. local combinatorial-game decomposition of Go endgames; and
2. partial-order reduction of commuting transitions in concurrent systems.

The prospective contribution is not the observation that independent Go
regions can be analyzed separately. It is the stronger engineering proposal
that independence and limited interference be represented by explicit,
proof-relevant relation cells over one authoritative history ledger, so that
every search reduction remains auditable.

---

## 2. Core hypothesis

Let raw search generate typed legal histories from a Go position \(S\). Instead
of treating all move sequences as unrelated branches, attach local relation
cells when two histories have compatible typed boundaries:

\[
\mathsf{Hist}(S)
\big/
\langle
ab\overset{Q_4}{\sim}ba,
\quad
aba\overset{M_6}{\sim}bab
\rangle.
\tag{HistoryQuotientCandidate}
\]

This expression is only a target. A relation may enter the quotient only when
it carries a sufficient certificate. Open boundaries remain distinct search
histories.

The intended division of labor is:

| structure | intended Go role | present confidence |
|---|---|---|
| `Q4` | certified interchange of independent local processes | strong candidate with established analogues |
| `M6` | certified reorganization of overlapping, order-sensitive processes | research conjecture |
| open boundary | interaction not yet certified | hard residual retained for search |
| Conway sum | composition of certified independent local games | established late-endgame model |
| temperature | urgency among decomposed local games | established late-endgame tool |

`Q4` and `M6` are therefore not move-selection policies. They are local
certificates that change the shape of the search space. A policy or exact game
solver must still select among inequivalent classes.

---

## 3. The Go carrier

A raw Go board diagram is not a sufficient carrier. A legal-state carrier must
include every coordinate capable of changing future legality or payoff:

\[
\mathcal G=
(B,\tau,R,K,H,C,M,O),
\tag{GoCarrier}
\]

where:

- \(B\) is the stone placement;
- \(\tau\) is the player to move;
- \(R\) is the exact ruleset and scoring convention;
- \(K\) is simple-ko or superko state;
- \(H\) is the retained position and move-history ledger needed by
  \(R\);
- \(C\) records captures, prisoners, passes, and other score-relevant state;
- \(M\) is the typed legal-move occurrence ledger; and
- \(O\) records open local regions and unresolved interaction residuals.

A move is a typed one-cell occurrence

\[
m:S_{\tau}\longrightarrow S'_{\bar\tau}.
\tag{PlyCell}
\]

Two equal stone diagrams need not be the same carrier state. Under history-
sensitive ko rules they may expose different legal moves. Any reduction that
forgets this distinction before certification is unsound.

---

## 4. Why raw plies do not form the intended `Q4`

Go alternates turns. If \(a\) and \(b\) are untyped board coordinates, the two
words \(ab\) and \(ba\) generally place different colors at those coordinates.
They do not define parallel paths from one typed source.

The first implementation should therefore use **turn-preserving local
macros**. A macro contains a bounded local exchange or response protocol and
returns the same global turn polarity:

\[
\alpha:S_{\tau}\longrightarrow S^{\alpha}_{\tau}.
\tag{TurnPreservingMacro}
\]

The simplest such macro consumes an even number of raw plies. More refined
versions may expose a partizan local-game interface instead of forcing a fixed
reply sequence, but that is a later extension.

An alternative asynchronous semantics could separate local events from the
global turn scheduler. It may eventually be more expressive, but it introduces
additional scheduling and fairness obligations. It should not be the first
calibration.

---

## 5. `Q4` as an independence certificate

Let \(\alpha\) and \(\beta\) be compatible turn-preserving macros. A strong
Go interchange cell has boundary

\[
S\xrightarrow{\alpha}S_{\alpha}
 \xrightarrow{\beta}S_{\alpha\beta},
\]

\[
S\xrightarrow{\beta}S_{\beta}
 \xrightarrow{\alpha}S_{\beta\alpha},
\]

and filler

\[
\chi_{\alpha,\beta}:
\alpha\beta\Rightarrow\beta\alpha.
\tag{GoQ4}
\]

### 5.1 Strong exact filler

A strong filler requires equality of the complete terminal carrier records:

\[
S_{\alpha\beta}=S_{\beta\alpha}.
\tag{ExactDiamond}
\]

It must also certify that every intermediate move is legal. This form is safe
for exact quotient search.

### 5.2 View-relative filler

A weaker view may observe only

\[
V(S_{\alpha\beta})=V(S_{\beta\alpha}).
\tag{ObservedDiamond}
\]

Such a cell is useful for analysis but does not by itself authorize minimax
pruning. It additionally needs a value-sufficiency or future-bisimulation
witness showing that the forgotten coordinates cannot change any continuation
relevant to the chosen task.

### 5.3 Ideal reduction

If two local processes of lengths \(m\) and \(n\) are independent, raw search
may enumerate

\[
\binom{m+n}{m}
\]

interleavings. Adjacent `Q4` interchange cells can place those words in one
Mazurkiewicz-style trace class. In the ideal case the solver explores one
representative and verifies the interchange certificates instead of expanding
every scheduling permutation.

The actual saving is net of certification cost. It must be measured, not
assumed.

---

## 6. `M6` as a certified interference cell

`Q4` expresses independence. Many Go processes are not independent: they may
share liberties, ko threats, sente obligations, cutting points, or external
support. The proposed `M6` experiment asks whether some such overlapping
processes nevertheless admit a coherent braid-shaped reorganization:

\[
\beta_{\alpha,\beta}:
\alpha\beta\alpha
\Rightarrow
\beta\alpha\beta.
\tag{GoM6}
\]

The boundary contains six state occurrences and retains both raw histories.
The two histories must have common typed endpoints, but endpoint agreement
alone is not enough: the filler must be stable under the continuations for
which it is used.

Candidate empirical sources include:

- transfer of sente between weakly coupled endgame regions;
- local exchanges sharing one external liberty or cutting resource;
- bounded ko-threat reorganizations;
- attack--defence macros whose order changes intermediate states but not the
  certified continuation class; and
- symmetry-related tactical templates with an explicitly transported player
  polarity.

These are search locations, not examples already proved to satisfy the braid
relation. The first experiment may find that useful `M6` cells are rare or
that their certificates cost more than the search they remove. That would be
a valid negative result.

No global equation

\[
\alpha\beta\alpha=\beta\alpha\beta
\]

is admitted in the Go language. Every filler is local, ruleset-indexed,
history-indexed, and task-indexed.

---

## 7. Juxtaposing `Q4` and `M6`

For a local pair of operation families, the relation detector should return a
typed trichotomy rather than force an equation:

\[
\mathsf{classify}(\alpha,\beta;S)=
\begin{cases}
\mathsf{Interchange}(\chi), & \text{a certified `Q4` filler exists},\\
\mathsf{Braid}(\beta), & \text{a certified `M6` filler exists},\\
\mathsf{Open}(r), & \text{the interaction remains residual}.
\end{cases}
\tag{RelationTrichotomy}
\]

The alternatives need not be globally exclusive under every view. A coarse
view may see a `Q4` where the exact view retains an open boundary. Therefore
each result names its view contract and the authority it grants.

The `TO24` envelope from note 0103 already demonstrates that square and
hexagonal relation faces can coexist over a shared finite state graph. It does
not prove that Go positions assemble into that envelope. The Go experiment
asks a more modest question: whether useful finite carriers exhibit enough
certified `Q4` and `M6` faces to reduce search.

---

## 8. Cell--carrier--views organization

The prospective spine is

\[
\mathsf{GoMacroCells}
\xrightarrow{\mathsf{assemble}_{\rho}}
\mathsf{GoSearchCarrier}
\xrightarrow{V_\nu}
\mathsf{GoView}_{\nu}.
\tag{GoCCV}
\]

One carrier may contain many move cells and many relation cells. It may emit
local views for one cell, paired views for two cells, and joint views for the
complete search component. All views reuse one occurrence ledger.

| view | retained coordinates | use |
|---|---|---|
| board | stones, turn, rules, ko state | exact legality |
| group/liberty | connected groups, liberties, captures | local dependency candidates |
| thread | ordered move and macro occurrences | audit history |
| relation | `Q4`/`M6` boundaries and fillers | certified reduction |
| logic | obligations, countercases, witness checks | proof-carrying search |
| decomposition | local components and coupling graph | Conway sum candidate |
| Conway | local partizan game presentations | endgame value |
| temperature | urgency and cooling data | global move choice among local games |
| search | representatives, backtracking points, residual frontier | solver control |
| observer | scope, resolution, and budget | bounded analysis |
| residual | unclassified interaction and omitted depth | honest incompleteness |

The Conway and temperature views are interpreters, not raw projections. They
require their own adequacy conditions. A relation view may justify a search
quotient without yet supplying a surreal or combinatorial-game value.

---

## 9. Sound quotient obligations

Let \(h\sim h'\) be generated by certified local relation cells. Exact search
may quotient by \(\sim\) only if it is a congruence for the task-relevant game
transition system.

At minimum, related histories must satisfy:

1. **Typed legality:** both histories begin and end at compatible typed states.
2. **Ruleset identity:** both use the same rules and scoring contract.
3. **History sufficiency:** all ko and repetition information needed by future
   legality is retained.
4. **Payoff preservation:** terminal scores and winner judgments agree.
5. **Continuation correspondence:** every legal continuation on one side has a
   related continuation on the other.
6. **Player-polarity preservation:** corresponding continuations belong to the
   same player.
7. **Whiskering stability:** the relation remains valid inside every admitted
   surrounding local context.
8. **Occurrence preservation:** quotienting a search representative does not
   erase the raw histories or their provenance.

A bisimulation certificate is sufficient but may be expensive. More local
independence criteria can be used if a theorem proves that they imply these
global obligations for the selected rules fragment.

For the first finite experiment, canonical representatives should be selected
over an explicitly enumerated relation graph. The implementation should not
orient `Q4` and `M6` equations into a presumed confluent rewrite system. Once
both commuting and braid relations are admitted, normalization and critical
pairs become separate proof obligations.

---

## 10. Relation to combinatorial-game decomposition

If the board is certified to decompose into independent local games
\(G_1,\ldots,G_k\), the global late endgame can be presented as the disjunctive
sum

\[
G=G_1+\cdots+G_k.
\tag{GoSum}
\]

This is the established domain in which Conway-style values and thermographs
are effective. The proposed contribution of `Q4` is to make part of the
independence argument explicit:

\[
\text{local components}
\quad+\quad
\text{certified interchange}
\quad\Longrightarrow\quad
\text{decomposition candidate}.
\]

The implication is not automatic. `Q4` cells among currently enumerated
macros may fail to detect a future long-range interaction. A certified
decomposition therefore also needs a scope-closure condition stating that no
legal continuation crosses the proposed component boundary.

The `M6` layer targets the region between clean independence and unrestricted
global coupling. If it succeeds, some interactions currently left to residual
minimax search may admit a finite coherent presentation. It does not turn a
coupled game into an ordinary Conway sum unless an additional interpreter
proves that reduction.

---

## 11. A low-resource solver architecture

The proposed solver is hybrid and proof-carrying:

1. **Legal-state kernel.** Generate exact moves under a fixed ruleset and
   retain all history needed for ko legality.
2. **Local-scope detector.** Propose groups, liberties, boundaries, and regions
   that may support local macros.
3. **Macro assembler.** Build bounded turn-preserving local processes with
   explicit input and output states.
4. **Relation prover.** Search first for strong `Q4` diamonds, then for bounded
   `M6` hexagons; retain failed candidates as counterexamples or residuals.
5. **Relation graph.** Store raw histories, relation boundaries, fillers, and
   open obligations without deleting provenance.
6. **Certified quotient.** Explore one representative per authorized relation
   class and retain backtracking points where independence fails.
7. **Local game interpreter.** On certified decomposed regions, calculate
   combinatorial-game values and temperatures.
8. **Residual solver.** Apply bounded minimax, alpha--beta, MCTS, or a learned
   policy only to unresolved coupled components.
9. **Verifier.** Replay the selected principal variation and every reduction
   certificate against the exact legal-state kernel.

The principal resource hypothesis is:

\[
C_{\mathrm{relation}}
+C_{\mathrm{quotient}}
+C_{\mathrm{residual}}
<
C_{\mathrm{raw\ search}}.
\tag{ResourceHypothesis}
\]

No asymptotic complexity improvement is claimed. The expected gain is
structural and instance-dependent: repeated independent or coherently related
histories are certified once and reused.

---

## 12. Prefix and Omega views

Search histories may be encoded by self-delimiting prefix words. If \(P_s\) is
the finite prefix-free set of histories certified as solved at stage \(s\), the
direct measure readout is

\[
\Omega_s=\sum_{p\in P_s}2^{-|p|}.
\tag{SolvedPrefixMass}
\]

This quantity can report how much of a chosen encoded search space has been
closed by certificates. It is not a win probability and is not Chaitin's
Omega unless a particular universal prefix-free machine and its halting domain
have been declared.

Relation quotienting introduces an accounting hazard. Two distinct codes may
be related by a `Q4` or `M6` filler while still occupying two distinct prefix
cylinders. A quotient view must therefore push their weights forward and
retain multiplicity; it may not count one representative and silently erase
the other cylinder.

The unresolved prefix frontier is an `Omega`-shaped boundary in the project's
broader vocabulary: it records legal continuations not closed by the finite
observer. It remains a residual view and must not be used as a manufactured
game value.

---

## 13. Minimal falsifiable experiment

The first experiment should test search compression, not playing strength.

### 13.1 Rules and corpus

- use a fixed small-board ruleset, initially on selected \(5\times5\) or
  \(7\times7\) positions;
- begin with a no-ko fragment or retain complete positional-superko history;
- include separated late-endgame regions, shared-liberty counterexamples,
  edge and corner symmetries, simple sente/gote interactions, and bounded ko
  examples in a later stratum;
- use exact bounded minimax as the reference oracle.

### 13.2 Calibration stages

1. enumerate the bounded raw game graph;
2. assemble turn-preserving macros;
3. enumerate exact `Q4` diamonds;
4. verify that quotienting by certified `Q4` preserves root value and the set
   of optimal moves;
5. enumerate candidate `M6` boundaries without assuming fillers;
6. certify any valid `M6` cells by full continuation checks within the bound;
7. repeat the quotient comparison with `Q4` and `M6` juxtaposed; and
8. measure certificate construction, verification, memory, and search costs
   separately.

### 13.3 Required negative tests

- two macros touch disjoint coordinates but share a group liberty;
- two paths end in the same stone diagram but have different superko histories;
- a view-relative `Q4` hides a score-relevant capture;
- a proposed `M6` agrees at its endpoint but admits different continuations;
- symmetry maps a corner position to an edge position without preserving the
  board boundary; and
- relation certification costs more than exploring the removed branches.

### 13.4 Metrics

Record at least:

\[
\rho_N=\frac{N_{\mathrm{raw}}}{N_{\mathrm{quotient}}},
\qquad
\rho_M=\frac{M_{\mathrm{raw}}}{M_{\mathrm{quotient}}},
\qquad
\rho_T=\frac{T_{\mathrm{raw}}}
{T_{\mathrm{certify}}+T_{\mathrm{quotient}}+T_{\mathrm{solve}}}.
\]

Also report:

- `Q4` and `M6` coverage rates;
- filler verification cost;
- residual component sizes;
- exact agreement of root outcome, score, and optimal move set; and
- the proportion of apparent relations rejected by history-aware checking.

The experiment succeeds as a structural calibration if it preserves exact
answers and obtains reproducible net reduction on at least one nontrivial
position family. It need not yet defeat human or neural Go players.

---

## 14. Theorem and conjecture ledger

### Theorem targets

**T1 -- Exact `Q4` quotient soundness.** If every `Q4` filler is a typed
payoff-preserving bisimulation congruence, quotient minimax has the same root
value and optimal move classes as raw minimax.

**T2 -- Independent-interleaving reduction.** Under a declared macro
independence relation, adjacent `Q4` cells generate the corresponding trace
equivalence, so one representative per trace class suffices for every
trace-invariant objective.

**T3 -- Certified local-sum adequacy.** If local scopes are continuation-
closed and mutually independent, the exact Go subgame equals their partizan
disjunctive sum under the declared game interpreter.

**T4 -- Relation-view ledger preservation.** Every quotient and game view
retains a total map from raw move and history occurrences to representatives,
fibres, and residuals.

### Research conjectures

**C1 -- Endgame `Q4` abundance.** Practical separated late-endgame positions
contain enough certified interchange cells for net search reduction.

**C2 -- Useful Go `M6` cells.** Some recurring weakly coupled Go interactions
admit local braid fillers that remove histories not removable by independence
alone.

**C3 -- Hybrid advantage.** Certified relation reduction plus local game
evaluation requires substantially less search than raw minimax on selected
small-board and endgame families.

**C4 -- Learnable candidate discovery.** A lightweight learned model can
propose relation candidates while a small exact verifier preserves soundness.

None of C1--C4 belongs to Bootstrap Zero's hard syntax kernel.

---

## 15. Red-team boundary

Several failure modes could invalidate the practical proposal without
invalidating the `Q4/M6` syntax.

1. **Certification equivalence.** Proving independence may require nearly the
   same search as solving the position.
2. **Sparse relations.** Realistic Go positions may contain few exact `Q4`
   cells and essentially no reusable `M6` fillers.
3. **Nonlocal influence.** A locally invisible ladder, ko threat, invasion, or
   score interaction may defeat scope closure.
4. **History explosion.** Correct superko state may remove much of the expected
   quotient.
5. **Macro bias.** A poor macro language may manufacture apparent simplicity
   or miss strategically important responses.
6. **Normalization difficulty.** Combined interchange and braid relations may
   lack a cheap canonical form.
7. **Endgame confinement.** The method may be valuable only after the board has
   already decomposed, with little impact on opening or middle-game play.
8. **View unsoundness.** Equality in a liberty, geometry, or score view may not
   preserve game value.
9. **Full-board overclaim.** Local compression does not overcome the known
   combinatorial hardness of generalized Go.

The correct negative result is not "`Q4` or `M6` is false." It is that a
particular Go view supplies too few cheap, sound fillers to improve the chosen
solver.

---

## 16. Relationship to finite observers

At every stage the solver is a finite observer. It sees a bounded subgraph,
uses a finite macro vocabulary, verifies a finite family of relation cells,
and leaves the remaining frontier open:

\[
\mathcal G_0\to\mathcal G_1\to\cdots\to\mathcal G_s.
\]

The epistemic statuses are separate:

| status | meaning |
|---|---|
| filled `Q4` | independence is certified under a named contract |
| filled `M6` | braid reorganization is certified under a named contract |
| open relation | candidate boundary exists but has no filler |
| absent relation | the current vocabulary has not even proposed the boundary |
| residual search | no authorized quotient is available |

This separation prevents finite failure from becoming a false global
negative. It also prevents a heuristic success from becoming a fabricated
proof.

---

## 17. Promotion discipline

The proposal should advance through four independently reviewable layers:

1. **Research note:** the present conceptual and falsification boundary.
2. **Executable calibration:** self-contained small-board fixtures outside the
   stable semantic API.
3. **Certified research types:** exact carrier, relation, and quotient
   certificates after the finite theorems are proved.
4. **Optional application engine:** local CGT and residual-search interpreters,
   still separate from Bootstrap Zero syntax.

No Go-specific constructor should enter the stable Adva object language merely
because the experiment is successful. The reusable promotion target is a
general proof-carrying relation-reduced game/search carrier.

---

## 18. References and external calibration

- Elwyn Berlekamp and David Wolfe, *Mathematical Go: Chilling Gets the Last
  Point*. Project page:
  <https://math.berkeley.edu/~berlek/cgt/gobook.html>.
- Martin Mueller, "Decomposition Search: A Combinatorial Games Approach to
  Game Tree Search, with Applications to Solving Go Endgames," IJCAI 1999:
  <https://www.ijcai.org/Proceedings/99-1/Papers/083.pdf>.
- Edmund M. Clarke, Orna Grumberg, Marius Minea, and Doron Peled, "State Space
  Reduction Using Partial Order Techniques":
  <https://www.cs.cmu.edu/~emc/papers/Invited%20Journal%20Articles/State%20Space%20Reduction%20using%20Partial%20Order%20Techniques2.pdf>.
- Matthew Earnshaw and Paweł Sobociński, "String Diagrammatic Trace Theory":
  <https://arxiv.org/abs/2306.16341>.
- Martin Mueller, *Computer Go as a Sum of Local Games: An Application of
  Combinatorial Game Theory*, ETH Zurich dissertation, listed at:
  <https://webdocs.cs.ualberta.ca/~mmueller/cgt/decomposition-search.html>.

These sources support the historical, local-decomposition, and commuting-trace
calibrations. They do not establish the proposed Go `M6` conjecture.

---

## 19. Present conclusion

The research direction is credible in a restricted form:

> Use `Q4` to certify and quotient independent local Go processes; search for
> `M6` fillers among weakly coupled histories; apply Conway values and
> temperature only after local-game adequacy is established; and leave every
> uncertified interaction in an explicit residual solver.

The likely first success is not a generally strong low-compute Go player. It
is an exact small-board or late-endgame solver that explores histories modulo
auditable local relations and demonstrates a measurable reduction over raw
search. If that finite result survives the negative tests, the same
architecture can be tested in other mathematical games and multi-agent search
systems.
