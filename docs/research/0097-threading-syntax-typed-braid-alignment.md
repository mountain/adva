# Threading Syntax and Typed Braid Alignment

Status: syntax-only continuation of
[note 0057](0057-typed-vacua-constant-boundary-braids.md),
[note 0058](0058-checked-gate-braid-composition.md),
[note 0059](0059-tri-bracket-eigen-normalization-logic.md),
[note 0071](0071-figure-eight-through-characteristic.md),
[note 0079](0079-typed-hole-open-close-calibration-v0.md),
[note 0095](0095-bootstrap-zero-geometric-threading-syntax.md), and
[note 0096](0096-boolean-triangle-placement-language-alignment.md).

This note aligns the threading fragment of Bootstrap Zero with the repository's
earlier braid discussion.  It adds one raw routing constructor,

```text
crossing[xi; r; over]
crossing[xi; r; under]
```

and a derived grammar of finite braid blocks.  It adds no Artin equation,
group quotient, knot invariant, gate naturality law, evaluator, or public API.

---

## 0. Recovered result

The earlier notes establish six constraints that the small language must not
erase.

1. The public three-shell boundary is fixed, while a single colored crossing
   normally has a permuted typed frontier as its target.
2. Positive and negative crossings have the same endpoint permutation but
   retain different over/under histories.
3. Endpoint return does not erase a pure braid word or a full twist.
4. A symmetric swap is a quotient of signed braid data, not its synonym.
5. Braid transport is reversible; an ordinary computational gate may copy,
   discard, merge, or otherwise be noninvertible.
6. A through relation, even when closed, does not by itself specify a knot.
   Closure pairing, embedding, orientation, and retained history are separate
   data.

The immediate syntax result is conservative: retain signed adjacent crossings
as named atoms and postpone every equation between their words.

---

## 1. The gap in the first Bootstrap Zero draft

Note 0095 already separated four notions:

- the ordered domain word in
  \(\mathsf{Through}_{de}^{f}\);
- the interface side \(L/R\);
- the incidence polarity \(+/-\); and
- a function-level `swap` constructor.

None records whether one of two routed strands passes over or under the other.
Encoding that distinction with incidence polarity would confuse connection
orientation with crossing history.  Encoding it with the ordered domain word
would confuse a cell type with a local route.  Encoding it with `swap` would
discard the sign.

Bootstrap Zero therefore needs a fifth independent coordinate.

| Coordinate | Raw alphabet or form | What it records | What it does not record |
|---|---|---|---|
| Domain direction | \(de\) in \(\mathsf{Through}_{de}^{f}\) | ordered endpoint roles | crossing sign |
| Interface side | \(L,R\) | side of a through cell | inverse or converse |
| Incidence polarity | \(+,-\) | endpoint attachment orientation | over/under |
| Crossing sign | `over`, `under` | signed local routing history | a gate operation |
| Function swap | `function[swap]` | declared computational constructor | an Artin generator |

These coordinates can agree extensionally in a later interpretation.  They
remain distinct in raw syntax.

---

## 2. Signed routing atoms

Let a typed frontier be a finite ordered sequence of complete incidence
records:

\[
F=\langle \rho_1,\ldots,\rho_n\rangle,
\qquad
\rho=(i,s,o,A,d,p).
\]

The record retains the incidence name, source, occurrence, value type, domain
role, and incidence polarity.  For \(1\le r<n\), let \(s_rF\) exchange the
two complete records at positions \(r\) and \(r+1\), changing nothing inside
either record.

The new raw atom is

\[
u_{\mathsf{route}}
::=
\mathsf{crossing}[\xi;r;\eta],
\qquad
\eta::=\mathsf{over}\mid\mathsf{under}.
\tag{Crossing}
\]

Its formation rule is

\[
\frac{
  1\le r<|F|
  \qquad
  \eta\in\{\mathsf{over},\mathsf{under}\}
}{
  \Sigma;Q\vdash_{\mathsf{cross}}
  \mathsf{crossing}[\xi;r;\eta]:F\rightsquigarrow s_rF
}.
\tag{Cross-WF}
\]

The sign is read relative to the written input frontier: `over` means that
the strand initially at position \(r\) passes over the strand at \(r+1\), and
`under` means that it passes under.  This convention fixes which raw atom
corresponds to each signed generator without adding a geometric interpreter.

Thus the two signs have the same routed target:

\[
\operatorname{target}(\mathsf{crossing}[\xi;r;\mathsf{over}])
=
\operatorname{target}(\mathsf{crossing}[\xi;r;\mathsf{under}]),
\]

but are different raw atoms.  The shared endpoint permutation is not evidence
for raw equality.

The rule moves whole incidence records.  It never detaches a value from its
color, source, occurrence, role, or polarity; and it never copies or discards
an incidence.

---

## 3. Raw braid blocks

A braid block is a finite routing-only word:

\[
\beta::=\epsilon_\beta
\mid
\mathsf{crossing}[\xi;r;\eta]::\beta.
\tag{BraidWord}
\]

Sequential formation produces the judgment

\[
\Sigma;Q\vdash_{\mathsf{braid}}
\beta:F\rightsquigarrow F'.
\tag{Braid-WF}
\]

The endpoint action can be calculated by composing adjacent transpositions.
It is only a formation check.  No rewrite system is invoked.

A block with \(F'=F\) is **endpoint-pure**.  Endpoint-pure does not mean empty,
identity, or observationally invisible.  In particular, a double crossing and
a full twist remain written histories even when the frontier returns.

### 3.1 Formal inverse spelling

For a finite sequence \(\beta=a_1::\cdots::a_n\), define

\[
\operatorname{inv}_{\mathsf{syn}}(\beta)
=
\overline a_n::\cdots::\overline a_1,
\tag{FormalInverse}
\]

where the bar keeps the crossing name and gap and exchanges `over` with
`under`.  The empty word is fixed.

This gives a well-formed word in the reverse direction.  It does not add the
equation

\[
\beta::\operatorname{inv}_{\mathsf{syn}}(\beta)=\epsilon_\beta.
\]

Nor does Bootstrap Zero add the Artin relation

\[
\sigma_1\sigma_2\sigma_1
=
\sigma_2\sigma_1\sigma_2.
\]

Those are future equality or coherence judgments.  The two sides above are
well-formed, endpoint-compatible, and raw-syntactically different.

---

## 4. Braid blocks inside thread words

The thread language of note 0095 is mixed:

\[
u::=u_{\mathsf{route}}
\mid u_{\mathsf{tr}}
\mid u_{\mathsf{char}}
\mid u_{\mathsf{ori}}
\mid u_{\mathsf{read}},
\qquad
\tau::=\epsilon_\tau\mid u::\tau.
\]

A maximal contiguous sequence of routing atoms is a braid block.  Every other
thread atom is an explicit separator.  For example,

```text
crossing[x1;1;over]
:: crossing[x2;2;under]
:: function[kappa]
:: crossing[x3;1;over]
```

has two braid blocks separated by one gate atom.  No Bootstrap Zero rule moves
the function across a crossing.  Such a rule would require a typed naturality
or commutation witness and could fail for a gate that reads signed history.

This is the smallest mixed schedule that preserves both reversible transport
and possibly noninvertible computation without pretending they are the same
kind of step.

---

## 5. Braid vocabulary aligned with \(\mathcal G_0\)

| Braid-side notion | Bootstrap Zero syntax | Present status |
|---|---|---|
| Colored object | typed frontier \(F\) | explicit |
| Fixed public boundary | \(B_\partial:={}_K[]_X()_t\) under a policy | explicit |
| Positive generator | `crossing[xi;r;over]` | explicit raw atom |
| Negative generator | `crossing[xi;r;under]` | explicit raw atom |
| Endpoint permutation | \(F\mapsto s_rF\) | decidable formation data |
| Raw braid word | \(\beta\) | explicit finite syntax |
| Pure braid | \(\beta:F\rightsquigarrow F\) | endpoint-pure syntax |
| Formal inverse | \(\operatorname{inv}_{\mathsf{syn}}(\beta)\) | constructor, no equation |
| Artin equality | equality of braid words | absent; later coherence |
| Coxeter swap | unsigned adjacent exchange | not a crossing synonym |
| Gate | `function[kappa]` | non-routing thread atom |
| Mixed schedule | thread word \(\tau\) | ordered syntax |
| Winding shadow | `characteristic[chi]` if declared | tag only, not complete history |
| Full twist | retained endpoint-pure word | not collapsed |
| Through direction | \(\mathsf{Through}_{de}^{f}\) | independent of braid sign |
| Closed braid | circle plus explicit closure data | not inferred from a word |

The boundary row is schematic: the authoritative boundary is the complete
typed boundary record of note 0095.  A crossing may leave that public boundary
and land at a permuted typed frontier.  Public boundary endomorphisms are
therefore generally composite endpoint-pure blocks, not single generators.

---

## 6. Five prohibited conflations

### 6.1 Braid crossing is not function swap

Both crossing signs route the same adjacent endpoints.  A function called
`swap` is nevertheless a declared gate with its own block type.  The gate does
not acquire over/under history merely from its extensional permutation.

### 6.2 Formal inverse is not side reversal

The inverse spelling reverses a word and flips every crossing sign.  Exchanging
the \(L\) and \(R\) frontiers of a through cell is a different syntactic
operation and is not currently defined.

### 6.3 Formal inverse is not relation converse

For a relation-like cell \(\langle L\mid R\rangle\), converse would exchange
its endpoints.  It does not recover discarded data and is not an operational
reverse.  A braid inverse concerns only reversible routing history.

### 6.4 Conjugate tag is not braid conjugation

`conjugate[chi]` remains a thread tag.  Braid conjugation would require word
composition, formal inverse, and an explicit equality or quotient judgment.
The shared word “conjugate” supplies no coercion.

### 6.5 Endpoint return is not knot closure

An endpoint-pure word has matching source and target frontiers.  A closed
geometric object additionally needs a closure pairing and enough embedding,
orientation, and base-point data to state the intended equivalence.  A circle
shape in note 0095 checks finite incidence closure only; it does not silently
become a knot invariant.

---

## 7. Relation to the twenty Boolean archetypes

Note 0096 classifies the 128 three-variable Boolean supports into twenty
labeled archetypes modulo domain symmetry and complement.  Several labels
carry directed-edge or chiral placement information.  That organization can
suggest where an ordered route belongs, but it does not determine a braid
word.

There is no canonical function

\[
\{
\text{Boolean support masks}
\}
\longrightarrow
\{
\text{signed braid words}
\}.
\]

Distinct signed histories may have one endpoint permutation or one Boolean
shadow.  Conversely, a Boolean support may describe dependency or placement
without describing any crossing.  The safe alignment is therefore:

| Boolean placement label | Threading syntax it may constrain | Data still required |
|---|---|---|
| Vertex | selected domain role | typed incidence and occurrence |
| Symmetric edge | unordered dependency on two roles | route and any sign |
| Directed edge | ordered domain pair | crossing word, if one exists |
| Chiral triangle | cyclic orientation label | signed route and chronology |
| Complement partner | support-level polarity | no automatic braid inverse |

The triangle classification supplies placement labels; the braid fragment
preserves history that those labels can forget.

The syntax continuation in
[note 0098](0098-multihole-am-type-formation-constraints.md) uses pure
multi-hole addition and multiplication kernel shapes to test which formation
records are required once repeated source-use occurrences are included.  It
introduces no surreal or option semantics and does not identify Boolean
parity, hole order, the named negative-unit atom, or incidence polarity with
crossing sign.

---

## 8. Alignment with the five interpreter declarations

| Interpreter declaration | May later observe | Bootstrap Zero currently supplies |
|---|---|---|
| \(\mathcal I_t\) | temporal order or chronology | declared target sort only |
| \(\mathcal I_K\) | constructive organization | declared target sort only |
| \(\mathcal I_X\) | spatial embedding or crossing display | declared target sort only |
| \(\mathcal I_{\mathrm{thr}}\) | signed routing and gate schedule | finite mixed thread word |
| \(\mathcal I_{\mathrm{AM}}\) | add--multiply expression | independent AM grammar |

The threading interpreter is the natural eventual consumer of braid blocks,
but no interpreter clause exists yet.  The spatial interpreter is not granted
exclusive ownership of over/under syntax, and the temporal interpreter does
not manufacture chronology that the word failed to retain.

---

## 9. Closure and holonomy remain explicit

If a later program closes a braid block into a circle, the syntax must retain
at least:

1. the braid word or a certified quotient representative;
2. the closure pairing of exposed incidences;
3. the orientation of the resulting component; and
4. any base point required for a word rather than a conjugacy class.

Pairwise winding numbers or characteristic tags may be useful shadows, but
they need not determine the noncommuting global history.  The raw word is not
discarded merely because a later interpreter reports such a shadow.

---

## 10. Executable syntax calibration

The companion finite test checks only raw formation facts:

1. `over` and `under` have one routed frontier and distinct spellings;
2. crossings move complete incidence records;
3. invalid adjacent-gap indices are rejected;
4. a single crossing need not be a public-boundary endomorphism;
5. endpoint return does not empty a word;
6. the formal inverse restores endpoint routing without raw cancellation;
7. both Artin sides reach one endpoint frontier but remain different words;
8. crossing sign, incidence polarity, and through direction remain separate;
9. mixed words retain gates between maximal braid blocks; and
10. no tested operation copies, discards, or detaches an incidence field.

The test is an executable specification of these finite syntax distinctions,
not evidence for braid-group soundness or interpreter adequacy.

---

## 11. Bootstrap Zero obligations added

### B0.7 Signed-crossing separation

For every valid adjacent gap, the two signs have the same routed target and
different raw atoms.  Neither is incidence polarity or function swap.

### B0.8 Formal braid inverse formation

If \(\beta:F\rightsquigarrow F'\), then
\(\operatorname{inv}_{\mathsf{syn}}(\beta):F'\rightsquigarrow F\).  The
formation theorem introduces no word equation.

### B0.9 Mixed-word block preservation

The maximal braid-block decomposition of a finite thread word is decidable
and retains every non-routing separator in its written position.

---

## Conservative conclusion

The threading grammar now has enough syntax to remember a signed crossing:

\[
\boxed{
\mathsf{crossing}[\xi;r;\mathsf{over}]
\quad\text{or}\quad
\mathsf{crossing}[\xi;r;\mathsf{under}]
}
\]

It remembers no braid equation by fiat.  Ordered domain direction, L/R side,
incidence polarity, crossing sign, and function-level swap remain independent.
Raw braid blocks live inside mixed thread words, while gates remain explicit
separators.

This is enough to state the next problem honestly: which equalities or
coherences may later be admitted without erasing the computation that passes
through the braid?
