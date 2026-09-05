# WholeCut6 to M6 Alternating-Pairing Bridge

Status: syntax-only bridge following
[note 0101](0101-six-port-whole-cut-theory.md),
[note 0102](0102-bootstrap-zero-whole-cut-grammar.md), and
[note 0103](0103-cell-carrier-view-relation-machines.md). Its executable
companion is `test_bootstrap_zero_whole_cut_m6_bridge.py`.

This note closes one precise gap: it states when the three atomic whole-cut
pairings and three sustained through pairings of one checked `WholeCut6`
carrier present the boundary of an `M6` relation machine. It introduces no
braid filler, braid equation, proof identity, stable Rust or Python type,
interpreter semantics, or claim that every six-port object is an `M6`.

---

## 0. Result

Let the authoritative port occurrence ledger be

\[
P=\{p_0,p_1,p_2,p_3,p_4,p_5\}.
\]

The three `WholeCutCell` records induce a fixed-point-free involution
\(\kappa:P\to P\), pairing the two ports of each atomic cut. A closed
`ThroughAccount` induces a second fixed-point-free involution
\(\tau:P\to P\), pairing the two ports of each through channel.

The bridge exists when:

1. both pairings are total on the same six-port ledger;
2. no cut pair is also a through pair;
3. the graph
   \[
   G=(P,E_\kappa\cup E_\tau)
   \]
   is connected; and
4. the declared `circle-order` is a rotation or reversal of this incidence
   cycle.

Each vertex of \(G\) then has one \(\kappa\)-edge and one \(\tau\)-edge.
A connected two-regular graph on six vertices is \(C_6\), and its edge kinds
alternate. Choosing a root and orientation gives two length-three paths
between opposite vertices:

\[
\kappa\tau\kappa
\qquad\text{and}\qquad
\tau\kappa\tau.
\]

Therefore the checked incidence data presents the open braid-shaped boundary

\[
\boxed{
\mathsf{bridge}(\mathbb W_6)
=
M_6^\partial[
\kappa\tau\kappa
\Rightarrow
\tau\kappa\tau].
}
\tag{WholeM6}
\]

This is a finite graph theorem under explicit formation hypotheses. Cardinality
six alone is insufficient.

---

## 1. Three typed ledgers

The bridge keeps three name classes disjoint.

### 1.1 Port ledger

Each source port retains

\[
p=(\mathsf{PortName},\mathsf{SourceName},
   \mathsf{OccurrenceName},A,m).
\]

It remains the authority for source lineage, value type, occurrence identity,
and multiplicity.

### 1.2 State presentation

For each port \(p\), the bridge creates a view-local state name

\[
s[p]:=\mathsf{state}[\mathsf{name}(p)].
\]

The state presentation reuses the complete source occurrence payload:

\[
\mathsf{occurrence}(s[p])=\mathsf{occurrence}(p),
\]

but the typed names remain different:

\[
\mathsf{name}(s[p])\ne\mathsf{name}(p).
\]

The bridge therefore creates no new semantic occurrence. It creates a typed
state presentation of an existing port occurrence.

### 1.3 Boundary-step ledger

Every cut pair and through pair produces one boundary-step occurrence:

\[
e_c:
s[p_L]\leftrightarrow s[p_R],
\qquad
e_h:
s[p_s]\leftrightarrow s[p_t].
\]

A step has its own name and records its origin cell or channel. It is neither
a port nor a state. The chosen boundary path may traverse the native
coorientation or its converse; that presentation direction is explicit and
does not mutate the source `WholeCutCell` or `ThroughChannel`.

Thus the bridge has exactly:

\[
6\text{ port occurrences},
\qquad
6\text{ state presentations},
\qquad
6\text{ boundary-step occurrences},
\]

with total, injective maps between the relevant ledgers rather than raw name
identification.

---

## 2. Circle order becomes incidence-bearing

The earlier executable `circle-order` check required only that it recount the
six authoritative ports. That was too weak: an arbitrary permutation of six
ports need not follow either cut or through incidence.

The refined formation judgment requires every consecutive cyclic pair in

\[
(p_0,p_1,p_2,p_3,p_4,p_5)
\]

to be exactly one member of

\[
E_\kappa\cup E_\tau,
\]

with every pairing edge used once. The resulting edge-kind word must alternate:

\[
\kappa,\tau,\kappa,\tau,\kappa,\tau
\]

up to rotation and reversal.

This strengthening changes no occurrence identity. It prevents a merely
recounted ledger from being mistaken for a geometric circle.

An open whole-cut carrier with named holes remains valid raw syntax, but it
cannot project to a closed `CircleView` or an `M6` relation boundary until
the missing through account is supplied explicitly.

---

## 3. Relation-cell presentation

Choose the first cycle state as source and the opposite state as target. The
two halves of the circle produce:

\[
D_\kappa:
s_0\xrightarrow\kappa s_1
\xrightarrow\tau s_2
\xrightarrow\kappa s_3,
\]

\[
D_\tau:
s_0\xrightarrow\tau s_5
\xrightarrow\kappa s_4
\xrightarrow\tau s_3.
\]

Their union is the same alternating six-cycle. The relation boundary is

\[
\mathsf{RelBoundary}
[D_\kappa\Rightarrow D_\tau].
\]

The orientation is a presentation choice. Rotating the declared circle chooses
another source; reversing it exchanges native and converse step readings. No
such choice renames or duplicates the underlying port occurrences.

The present adapter returns

\[
M_6^\partial
\]

with an empty filler ledger. It does not infer

\[
\beta:D_\kappa\Longrightarrow D_\tau
\]

from incidence or from the equality of endpoint states.

---

## 4. Logic view

Applying the proof-relevant logic view gives one open obligation:

\[
V_{\mathsf{logic}}
(\mathsf{bridge}(\mathbb W_6))
=
\left(
D_\kappa
\overset{?}{\Longrightarrow}
D_\tau
\right).
\]

It retains:

- all six source occurrences;
- all six typed state presentations;
- all six step occurrences and their origins;
- both ordered histories;
- their common typed source and target; and
- the absence of a filler.

This establishes that logic view is defined on the bridged `M6` boundary. It
does not establish the braid rule as a valid logical transformation.

A later filler must say which calculus admits it and provide an independently
checkable witness. Proof irrelevance would be a further forgetting view.

---

## 5. Zero and noncollapse

The alternating cycle gives a nonempty returning word:

\[
(\kappa\tau)^3
\]

in the finite Coxeter shadow. Endpoint return may be observed as identity, but
the written six-step history is not the empty word.

At the relation level the proposed filler would witness

\[
[\kappa\tau\kappa]
-
[\tau\kappa\tau]
=0.
\]

The bridge supplies the two terms and their common boundary. It does not supply
the equality. Thus the implementation respects the separation:

\[
\text{returning endpoint}
\ne
\text{empty history}
\ne
\text{witnessed zero}.
\]

This is the finite form of the larger rule that a view may send a history to
zero without authorizing its deletion from the carrier.

---

## 6. Negative boundaries

The adapter rejects:

1. six ports whose through pairing repeats a cut pairing;
2. six ports whose two matchings do not form one connected cycle;
3. a `circle-order` that merely enumerates the ledger but ignores incidence;
4. a missing through edge disguised as closure;
5. port/state/step name reuse;
6. loss or modification of source, occurrence, type, or multiplicity payload;
7. a source or target thread whose step boundaries do not replay; and
8. any bridge that manufactures a braid filler.

These failures are formation errors, not semantic countermodels.

---

## 7. Executable calibration

The companion test:

- strengthens the original `WholeCut6` validator so a closed circle order
  must be induced by the two matchings;
- derives the six boundary steps from exactly three cells and three channels;
- obtains the words `cut-thread-cut` and `thread-cut-thread`;
- reuses every authoritative occurrence exactly once;
- records distinct port, state, and step names;
- records each step's cell or channel origin and native/converse presentation;
- projects the result through the logic view as one open braid obligation;
- rejects nonalternating, incidence-free, and open-hole pseudo-carriers; and
- retains an empty filler ledger.

These checks are exhaustive for the presented six-element matching fixture,
not for every future topology or arity.

---

## 8. What has and has not been closed

### Established in this research fixture

- the exact two-matching criterion for the canonical closed `WholeCut6`;
- the induced connected alternating \(C_6\);
- the typed port-to-state presentation map;
- the cell/channel-to-step origin map;
- the two length-three boundary threads;
- the open `M6` relation boundary; and
- its proof-relevant logic-view obligation.

### Still open

- an admissible braid filler in the Bootstrap Zero proof language;
- transport of signed `over/under` histories through the finite Coxeter view;
- rotation and reversal coherence between alternate rooted presentations;
- composition of `Q4` and `M6` relation cells;
- the proposed `TO24` three-dimensional filler;
- stable Rust authority, certificates, serialization, and public syntax; and
- any arithmetic, surreal, geometric, learning, or physical interpreter.

The next narrow task is no longer to identify the six-cycle. It is to state
the smallest typed rule that may fill one bridged `M6^\partial`, together
with the countercase showing when the same endpoint data is insufficient.

