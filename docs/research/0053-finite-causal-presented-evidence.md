# Finite Causal Evidence over Context Presentations

Status: exploratory finite calibration following
[`0052-finite-state-transport-proof-no-go.md`](0052-finite-state-transport-proof-no-go.md).

The executable fixture is
[`tests/python/test_triadic_causal_presented_evidence.py`](../../tests/python/test_triadic_causal_presented_evidence.py).

The preceding no-go established that programs acting on world states cannot
serve directly as proof-relevant entailments.  This note introduces the first
separate evidence layer without importing arbitrary host-language functions.

The central restriction is causal:

> An evidence transformation may continue an existing checked context by
> appending future steps.  It may not erase, replace, or insert events in the
> already recorded past.

This produces the first exact separation between extensional inclusion and
evidence transport.

The sixteen transformations of the finite triadic machine determine sixteen
**context presentations**.  Several presentations have the same spatial
support but retain different program effects.  For a presentation \(m\), its
evidence fibre contains every finite context word that denotes \(m\), together
with its complete run from a supporting initial state.

A causal evidence continuation from presentation \(m\) to presentation \(n\)
is a suffix word \(d\) satisfying

\[
m;d=n
\]

and

\[
P_m\subseteq P_n.
\]

It maps a witness word \(w\) to \(wd\).  The old trace remains a literal
prefix of the new trace.

Exact enumeration gives:

| comparison among 16 presentations | count |
|---|---:|
| extensional support inclusions | 72 |
| inclusions with causal evidence continuation | 60 |
| inclusions with no causal continuation | 12 |
| lifted strict inclusions | 16 |
| lifted equal-support comparisons | 44 |

All twelve failures are attempts to remove a temporal-opening effect from an
already presented history.  Constructive flipping behaves differently: it is
reachable in both directions, although a round trip retains a nonempty
\(KK\) evidence history.

This is the first finite result in the current line where

\[
P_m\subseteq P_n
\]

does not automatically lift to the admitted evidence grammar.

The evidence objects, suffix grammar, and search remain research-local Python
objects over the Rust-checked scalar machine from note 0051.  This note adds no
stable evidence, realizer, proof, context, category, natural-deduction, or
three-computer API; it does not modify `claims.toml`; and it does not change
the active `ProgramSlice` priority.

---

## 0. Executive construction

Let

\[
S_0=\{0,1\}^3
\]

and let

\[
M=\langle T,X,K\rangle
\]

be the sixteen-element transformation monoid already computed.  The spatial
atom is

\[
A_X=\{(t,x,k)\mid x=1\}.
\]

Each transformation \(m\in M\) presents the predicate

\[
P_m=m^{-1}(A_X).
\]

Only five distinct supports occur, but the sixteen presentations are not
identified.

For an initial state \(s\in P_m\), define the evidence fibre

\[
E_m(s)
=
\bigl\{
(w,\rho_w(s))
\mid
\llbracket w\rrbracket=m
\bigr\},
\]

where \(w\) is a finite context word and \(\rho_w(s)\) is its full run trace.

The total presented evidence carrier is

\[
E_m=\coprod_{s\in P_m}E_m(s),
\]

with base projection

\[
\pi_m:E_m\longrightarrow P_m,
\qquad
\pi_m(w,\rho_w(s))=s.
\]

For a suffix \(d\) with \(m;d=n\) and \(P_m\subseteq P_n\), define

\[
\tau_d:E_m\longrightarrow E_n
\]

by

\[
\tau_d(w,\rho_w(s))
=
(wd,\rho_{wd}(s)).
\]

Then

\[
\pi_n\circ\tau_d=\pi_m.
\]

The initial world state is unchanged.  The certificate is extended forward in
time.

---

# Part I. Why presentations must not be quotiented too early

## 1. Five supports, sixteen presentations

The sixteen transformations generate only the five spatial supports

\[
x,
\qquad
t\wedge k,
\qquad
t\wedge\neg k,
\qquad
k,
\qquad
\neg k.
\]

For example, the contexts

\[
\varepsilon,
\qquad
T,
\qquad
K,
\qquad
TK
\]

all generate the same current spatial support \(x\).  They do not have the
same transformation:

- \(\varepsilon\) preserves every coordinate;
- \(T\) opens the temporal gate;
- \(K\) flips construction; and
- \(TK\) performs both effects.

Support equality has forgotten what the program did outside the selected
spatial observation.

## 2. Why a presented predicate is not just its support

A presented predicate retains at least:

- the extensional support \(P_m\);
- the context transformation \(m\);
- a concrete finite word realizing \(m\);
- the complete run trace from the initial state; and
- the checked histories of the scalar programs used by the context.

Two presentations may therefore have equal support while their evidence
fibres contain different histories and endpoints.

The support map

\[
Q:E_m\longmapsto P_m
\]

is an observer forgetting map.  Treating it as equality would reproduce the
extensional collapse identified in the preceding notes.

## 3. Finite types with open evidence

The semantic presentation index \(m\) belongs to the finite monoid \(M\), but
the evidence fibre \(E_m(s)\) is not finite.  Context loops produce arbitrarily
long words denoting the same transformation.

For example,

\[
K^2=1
\]

as a state transformation.  Both

\[
\varepsilon
\]

and

\[
KK
\]

belong to the identity presentation, but their evidence histories differ.

This gives a concrete finite-expression/open-interpretation form:

- finitely many semantic evidence types;
- finite evidence objects one at a time;
- unboundedly many possible evidence histories; and
- a finite quotient used to decide type-level reachability without erasing
  the returned witness word.

---

# Part II. The causal continuation grammar

## 4. One admitted operation: append a suffix

Given evidence

\[
e=(w,\rho_w(s))\in E_m(s),
\]

the grammar permits

\[
e\longmapsto e;d
\]

for a finite suffix \(d\).  The resulting word is \(wd\).

This operation is constructive:

1. retain the input evidence object;
2. execute the declared suffix from its final state;
3. append the new states and program histories; and
4. return the longer certificate.

It does not inspect a support table and synthesize an unrelated target witness.

## 5. The two typing conditions

The suffix must satisfy a presentation boundary:

\[
\llbracket wd\rrbracket
=
\llbracket w\rrbracket;\llbracket d\rrbracket
=n.
\]

It must also be total on the source evidence support:

\[
P_m\subseteq P_n.
\]

The second condition ensures that every source evidence state remains a valid
base state for the target presented predicate.

Together they define

\[
m\xRightarrow{d}_{\mathrm{ev}}n.
\]

## 6. What is deliberately forbidden

The first grammar does not allow a transformer to:

- delete an event from \(w\);
- replace the existing prefix by another context;
- insert a new event before an already executed event;
- choose an arbitrary target witness from a support table;
- identify two histories because their current spatial values agree; or
- call a host function that reconstructs evidence from scratch.

These restrictions are not claimed to be the final proof theory.  They isolate
the most conservative evidence operation already justified by sequential
execution: future continuation.

## 7. Exact finite decision procedure

Although evidence words are unbounded, existence of a suffix is decided in the
finite monoid.

For a source presentation \(m\):

1. place \(m\) in a queue;
2. right-compose each discovered presentation by \(T,X,K\);
3. retain the first word reaching every new transformation;
4. stop when the finite queue is empty; and
5. accept target \(n\) exactly when it is reachable and
   \(P_m\subseteq P_n\).

The search computes the complete right action

\[
mM=\{m;d\mid d\in M\}.
\]

It returns a shortest concrete suffix word.  Search exhaustion is conclusive
because all longer words denote one of the already enumerated monoid elements.

---

# Part III. Exact lifting result

## 8. Seventy-two extensional comparisons

Among the sixteen presented predicates, exactly 72 ordered pairs satisfy

\[
P_m\subseteq P_n.
\]

This count treats two different presentations with equal support as two
different objects.  It is therefore larger than the inclusion count among the
five distinct direct supports.

## 9. Sixty causal lifts

Exactly 60 of those 72 inclusions admit a suffix continuation:

\[
n\in mM.
\]

They split into:

| lifted comparison | count |
|---|---:|
| equal-support | 44 |
| strict-support | 16 |
| total | 60 |

The shortest suffix lengths are:

| suffix length | causal lifts |
|---:|---:|
| 0 | 16 |
| 1 | 24 |
| 2 | 12 |
| 3 | 6 |
| 4 | 2 |

The sixteen empty suffixes are evidence identities.

## 10. Twelve inclusions do not lift

The complete failure set is:

| source presentations | unreachable equal-support targets |
|---|---|
| \(T, TK\) | \(\varepsilon, K\) |
| \(XT, XTK\) | \(X, XK\) |
| \(KXT, KXTK\) | \(KX, KXK\) |

Expanding the Cartesian pairs gives exactly twelve failures.

Every row has the same structure: the source presentation has already opened
the temporal gate after some prefix, while the target presentation lacks that
effect.  No admitted generator restores an arbitrary original temporal bit.

Therefore

\[
P_m=P_n
\]

for these pairs, but

\[
m\not\xRightarrow{d}_{\mathrm{ev}}n
\]

for every finite suffix \(d\).

This is the first exact support equality without evidence transport in the
declared grammar.

---

# Part IV. Temporal irreversibility and constructive return

## 11. The temporal gate gives an evidence arrow

The empty and temporal presentations have the same spatial support:

\[
P_{\varepsilon}=P_T=\{x=1\}.
\]

There is a forward continuation

\[
\varepsilon\xRightarrow{T}_{\mathrm{ev}}T.
\]

There is no reverse suffix:

\[
T\not\xRightarrow{}_{\mathrm{ev}}\varepsilon.
\]

The reason is operational, not extensional.  Once \(T\) has replaced the
temporal coordinate by one, the current generator set has no instruction that
recovers its previous value uniformly.

## 12. The same arrow appears after spatial observation

Likewise,

\[
P_X=P_{XT}=\{t=1\wedge k=1\}.
\]

Appending \(T\) gives

\[
X\xRightarrow{T}_{\mathrm{ev}}XT,
\]

but no suffix removes the later temporal opening:

\[
XT\not\xRightarrow{}_{\mathrm{ev}}X.
\]

The spatial observer forgets the difference, while causal evidence retains
its direction.

## 13. Construction is bidirectionally reachable

The constructive flip satisfies

\[
K^2=1.
\]

Hence

\[
\varepsilon\xRightarrow{K}_{\mathrm{ev}}K
\]

and

\[
K\xRightarrow{K}_{\mathrm{ev}}\varepsilon.
\]

Similarly,

\[
X\xRightarrow{K}_{\mathrm{ev}}XK
\]

and

\[
XK\xRightarrow{K}_{\mathrm{ev}}X.
\]

This is bidirectional reachability of presentation types.  It is not strict
proof-level inversion.  Composing the two continuations appends \(KK\), so the
resulting evidence history is nonempty even though its state transformation is
the identity.

Any later equation identifying that loop with empty evidence would require a
separate checked evidence cell.  State equality alone does not authorize it.

---

# Part V. Strict inclusion can lift causally

## 14. The initial false intuition

The previous no-go might suggest that the inclusion

\[
t\wedge k\subseteq k
\]

cannot lift because the canonical contexts are

\[
X
\quad\text{and}\quad
TX,
\]

and changing \(X\) into \(TX\) appears to require inserting \(T\) before the
past spatial step.

That conclusion would incorrectly require the target evidence to use its
canonical shortest word.

## 15. The target presentation accepts noncanonical histories

Start with an \(X\)-evidence word and append \(TX\):

\[
X\longmapsto XTX.
\]

The complete transformation of \(XTX\) is the same as that of \(TX\):

\[
\llbracket XTX\rrbracket
=
\llbracket TX\rrbracket.
\]

Therefore

\[
X\xRightarrow{TX}_{\mathrm{ev}}TX.
\]

The original \(X\)-trace remains the prefix of the new certificate.  No event
is inserted into its past.

This gives a genuine causal lift of the strict inclusion

\[
P_X=t\wedge k
\subsetneq
k=P_{TX}.
\]

The finite semantic type is the target transformation \(TX\), not one
privileged spelling of it.

## 16. Why open evidence is necessary

If \(E_{TX}\) accepted only the canonical word \(TX\), the causal lift would
be rejected for a syntactic reason.  Allowing every finite word denoting the
target transformation admits \(XTX\) while still checking its type exactly.

Thus the evidence representation has the desired shape:

\[
\text{finite semantic index}
\quad+\quad
\text{open family of finite witnesses}.
\]

This is more faithful to the finite-representation problem than either an
arbitrary infinite powerset or a single canonical proof string.

---

# Part VI. Identity, cut, and the support observer

## 17. Evidence identity

For every presentation \(m\), the empty suffix gives

\[
\operatorname{id}_m:E_m\longrightarrow E_m.
\]

It leaves the evidence word and trace unchanged.

## 18. Evidence cut by suffix concatenation

If

\[
m\xRightarrow{d}_{\mathrm{ev}}n
\]

and

\[
n\xRightarrow{e}_{\mathrm{ev}}p,
\]

then

\[
m\xRightarrow{de}_{\mathrm{ev}}p.
\]

On evidence objects,

\[
(w\mapsto wd)\mapsto wde.
\]

The fixture exhaustively checks every composable pair among the 60 shortest
continuations.  Support inclusion, presentation typing, and trace-prefix
preservation survive composition.

This is the first candidate evidence-level identity and cut in the triadic
logic line.  It is still only the sequential fragment; no implication
introduction, discharge, tensor, sum, copy, or discard has been defined.

## 19. The support observer is not full

The support observer sends a presented evidence type to its extensional
predicate:

\[
Q(E_m)=P_m.
\]

It sees 72 inclusions among the sixteen presented objects.  Only 60 lift to
causal continuations.  Hence extensional support inclusion is not full with
respect to the admitted evidence morphisms.

The twelve missing lifts are not false inclusions.  They are distinctions that
the support observer has forgotten.

## 20. Forgetting target presentation restores every inclusion

Now let the target be only one of the five extensional propositions, accepting
evidence from any presentation with that support.  Across the sixteen source
presentations there are exactly 24 source-to-extensional-target inclusions.

Every one of the 24 has some causal continuation into at least one target
presentation.

Thus quotienting the codomain by presentation restores extensional lifting.
It does so by forgetting which target program effect and history must be
realized.

This makes the trade-off exact:

- retain presentation and expose twelve proof-relevant gaps; or
- forget presentation and recover all extensional inclusions.

---

# Part VII. Relation to the larger questions

## 21. A first finite evidence category

The current objects are the sixteen presentation-indexed evidence carriers
\(E_m\).  Morphism witnesses are concrete suffix words satisfying the two
typing conditions.  Empty suffixes provide identities and concatenation
provides composition.

There may be many witnesses between the same objects.  Indeed, loops such as
\(KK\) generate unbounded histories even when the object set is finite.

The fixture computes existence and one shortest witness through the finite
monoid.  It does not quotient the returned word.  This is a small
proof-relevant category candidate, not yet a natural-deduction system.

## 22. Consequence for finite representation

The finite-representation question now has a concrete answer at three levels:

1. the sixteen-element monoid finitely represents all context transformations;
2. each evidence object is a finite word and finite trace; and
3. the interpretation remains open because evidence histories have no fixed
   maximum length.

Completeness of type-level suffix reachability follows from the finite monoid.
It does not require enumerating every evidence word.

## 23. Consequence for temporal direction

The temporal update \(T\) is idempotent and irreversible in the selected
monoid.  Its effect is invisible to the current spatial support in several
presentations but remains ordered in evidence transport.

This supplies a finite arrow of time:

\[
E_{\varepsilon}\longrightarrow E_T
\]

without a reverse causal continuation.

The claim is relative to the declared instruction set.  Adding a temporal
restore instruction would change the right ideals and must recompute the
evidence category.

## 24. Consequence for the \(L/R\) problem

Suffix transport supplies an intrinsic direction without forcing every pair
of programs into one total order.  A context may extend another when it lies
in the appropriate right ideal and its support condition holds.

The resulting relation combines:

- sequential order from word concatenation;
- algebraic reachability from the transformation monoid;
- observer compatibility from support inclusion; and
- construction history from the retained suffix witness.

This is a more precise local alternative to writing an unexplained
\(L\mid R\).  It does not yet solve the global reduction problem.

## 25. Consequence for startup calibration

A startup certificate may be continued by later calibration steps without
rewriting its earlier trace.  Two startup procedures can have the same coarse
calibrated support while failing to admit a causal certificate transformation
in one direction.

Thus calibration equality must specify whether it means:

- equal observed calibrated region;
- equal state transformation;
- mutually reachable presentation types; or
- equivalent evidence histories under a separately supplied cell.

The finite example shows these notions need not coincide.

## 26. Consequence for 3-form logic

The logic proposal now has a first non-extensional construction layer:

- temporal order appears as irreversible evidence extension;
- spatial truth appears as the observed target atom and its pullbacks;
- constructive difference appears in witness words and reversible flips; and
- support forgetting maps several evidence types to one proposition.

This is closer to a logic on a 3-form than support inclusion alone.  It remains
a sequential evidence fragment, not a complete logic.

---

# Part VIII. Verification and limits

## 27. What the fixture establishes

Within the declared finite machine and suffix-only evidence grammar, the
fixture establishes:

1. sixteen finite semantic presentation types with open finite-word evidence
   fibres;
2. exact validation of canonical evidence on every supporting core state;
3. a nonempty \(KK\) evidence history in the identity presentation;
4. exactly 72 extensional support inclusions among the presentations;
5. exactly 60 inclusions with a causal suffix continuation;
6. 44 equal-support and 16 strict-support causal lifts;
7. exactly twelve non-lifting inclusions;
8. the complete three-row classification of those twelve failures;
9. the exact shortest-suffix length distribution;
10. temporal forward reachability without reverse evidence erasure;
11. bidirectional constructive reachability with retained round-trip history;
12. a strict lift \(X\xRightarrow{TX}TX\) realized by the history \(XTX\);
13. evidence identity for all sixteen presentations;
14. exhaustive composition of every compatible pair among the sixty shortest
    continuations; and
15. restoration of all 24 source-to-extensional-target inclusions after
    forgetting target presentation.

## 28. What it does not establish

The fixture does not establish:

- a stable evidence or proof API;
- that suffix continuation is the complete notion of proof;
- a Rust-authoritative evidence carrier;
- equality or normalization of evidence words;
- a checked two-cell identifying \(KK\) with empty evidence;
- implication introduction or discharge;
- conjunction, disjunction, tensor, sum, copy, or discard rules;
- proof normalization or cut elimination;
- faithfulness, fullness, or completeness of a general categorical semantics;
- a universal three-computer language;
- a solution to the general \(L/R\) problem; or
- irreversibility under a larger instruction set.

The twelve negative results are exact only for the declared finite monoid and
the causal suffix grammar.  A future typed evidence rewrite could add new
morphisms, but it must state how it transforms or certifies the retained past.

## 29. Next gate

The next extension should not add arbitrary implication immediately.  It
should test one explicit composite evidence constructor while preserving
resource discipline.

A suitable progression is:

1. introduce a finite binary evidence product or sum as a research object;
2. keep pairing, projection, injection, case, copy, and discard distinct;
3. allow only constructors justified by typed program boundaries;
4. compute whether identity and suffix cut interact coherently with the new
   constructor;
5. search for the first support-valid judgment that still lacks an admitted
   composite evidence transformer; and
6. promote no stable connective until its resource and history laws are
   explicit.

## 30. Conservative conclusion

The first evidence-level result is:

> A finite family of context presentations can carry an open family of finite
> evidence histories.  Causal suffix continuation lifts most, but not all,
> extensional inclusions.  The missing lifts are precisely irreversible
> attempts to erase an already recorded temporal effect.

This is the sought separation that state transport could not provide.  It
retains finite computability, admits identity and sequential cut, and exposes
an evidence-sensitive arrow of time without claiming that a full natural
deduction has already been constructed.

