# Triadic Conflict Apertures and Third-Domain Completion

Status: working typing rule, finite calibration, and coherence obligations
following
[0079](0079-typed-hole-open-close-calibration-v0.md),
[0081](0081-relative-halt-exploration-threaded-compactification.md), and
[0082](0082-threaded-finite-logic-adequacy.md).

This note checks a proposal by Mingli Yuan:

> When two lines with distinct tri-domain identities compete for one linear
> source, the conflict should open a hole in the unique remaining domain.
> The hole must then admit the grammar of a correctly typed filling line.

The proposal is coherent under a precise typing gate.  It gives a principled
way to replace the assumed Cartesian pairing condition of note 0082 by a
third-domain completion obligation.  It does not make every conflicted pair a
conjunction witness automatically.  Opening the hole records an unresolved
obligation; only a certified third-domain filling closes a triangular cell
that can witness conjunction.

No stable connective, aperture type, Rust API, or natural-deduction rule is
introduced here.

---

## 0. Verdict

Let

\[
D=\{K,X,t\}.
\]

Suppose two lines \(\ell_d\) and \(m_e\):

1. have distinct domain identities \(d\ne e\);
2. consume the same linear source;
3. have distinct occurrence identities;
4. have the same wire type; and
5. retain their ordered boundary ports.

Then there is a unique remaining domain

\[
\mu(d,e)
=
D\setminus\{d,e\}.
\]

The conflict may be objectified as an aperture

\[
H_{\mu(d,e)}
\left(
s;
p_{\ell_d},
p_{m_e};
R
\right),
\]

where \(s\) is the shared source and \(R\) retains occurrence, order,
provenance, and unresolved resource evidence.

A filler is not an arbitrary line bearing the remaining-domain label.  It is
a pair \(\kappa=(n_{\mu(d,e)},\chi)\), where \(n_{\mu(d,e)}\) is a
remaining-domain line and \(\chi\) certifies a linear common lift

\[
\kappa:
s\multimap_{\mu(d,e)}
\left(A\boxtimes_{\mu(d,e)}B\right)
\]

with boundary projections

\[
p_A\circ n_{\mu(d,e)}\simeq_Q\ell_d,
\qquad
p_B\circ n_{\mu(d,e)}\simeq_Q m_e,
\qquad
\operatorname{use}_s(n_{\mu(d,e)})=1.
\]

Equivalently,

\[
\operatorname{Fill}_{\mu(d,e)}
\left(
H_{\mu(d,e)}
\right)
=
\left\{
(n,\chi):
\chi\text{ certifies the oriented linear closure}
\right\}.
\]

Any such pair closes the aperture and produces a triangular cell

\[
\operatorname{Cell}_\triangle
(\ell_d,m_e,\kappa).
\]

The cell, not the bare open aperture, is the proof-relevant conjunction
witness.

---

## 1. Typed lines and the opening rule

The minimal line record is

\[
\ell
=
\left(
\operatorname{label},
\delta(\ell),
\sigma(\ell),
\omega(\ell),
\tau(\ell)
\right),
\]

where:

- \(\delta(\ell)\in D\) is the tri-domain identity;
- \(\sigma(\ell)\) is the source identity;
- \(\omega(\ell)\) is the occurrence identity; and
- \(\tau(\ell)\) is the wire type.

The ordered pair also carries an orientation

\[
\varepsilon(d,e)
=
\begin{cases}
\mathrm{forward},
&(d,e)\in\{(K,X),(X,t),(t,K)\},\\
\mathrm{reverse},
&\text{otherwise}.
\end{cases}
\]

The opening rule is:

\[
\boxed{
\frac{
\delta(\ell)=d
\quad
\delta(m)=e
\quad
d\ne e
\quad
\sigma(\ell)=\sigma(m)
\quad
\omega(\ell)\ne\omega(m)
\quad
\tau(\ell)=\tau(m)
}{
\ell,m
\leadsto
H^{\varepsilon(d,e)}_{\mu(d,e)}(\ell,m)
}
}
\tag{Open-\(\triangle\)}
\]

This rule does not apply when:

- the sources are distinct, because the lines pair directly;
- the domain identities are equal, because no unique remaining domain is
  selected;
- the occurrence identities are equal, because the record aliases one
  occurrence rather than presenting two competing uses; or
- the wire types differ, because no source-preserving pairing is typed.

These cases remain explicit rather than being forced through the triadic
rule.

---

## 2. The three domain-pair cases

The unique-complement rule gives:

| competing line domains | aperture domain | first operational reading |
|---|---|---|
| \(K,X\) | \(t\) | order or schedule the construction--placement conflict |
| \(X,t\) | \(K\) | construct a mediator, duplicator, or authorized share |
| \(t,K\) | \(X\) | separate occurrences by placement, context, or neighborhood |

These operational readings are working hypotheses, not definitions of the
three domains.  The exact invariant is only that the filler has the unique
remaining domain identity and discharges the retained conflict without
silently merging occurrences or copying a linear source.

The table realizes the tri-domain principle:

\[
\boxed{
\text{two distinct domain identities}
\quad\Longrightarrow\quad
\text{an obligation in the opposite domain}.
}
\]

---

## 3. Closing is stronger than opening

The closing rule is:

\[
\boxed{
\frac{
H_{\mu(d,e)}(\ell,m)
\quad
\kappa:
\operatorname{Fill}_{\mu(d,e)}
\left(H_{\mu(d,e)}(\ell,m)\right)
}{
\operatorname{Cell}_\triangle(\ell,m,\kappa)
}
}
\tag{Close-\(\triangle\)}
\]

The filler must match:

1. the exact aperture identity;
2. the remaining domain;
3. the source and wire type;
4. the ordered boundary ports and their orientation;
5. projections back to the two original line occurrences;
6. exactly one linear use of the shared source; and
7. the declared operational role or a more general certified resolution
   predicate.

A line from either already occupied domain cannot fill the hole merely by
being present.  A filler for another source, another port order, another
aperture, or a filler that uses the source twice also cannot close it.

The triangular common-lift presentation is already a strong finite
calibration hypothesis.  In a general process category the two uses form a
span from the shared source, and a resolution may require a diamond or cospan

\[
\ell:s\to A,
\qquad
m:s\to B,
\qquad
A\xrightarrow{n_k}W\xleftarrow{p_k}B,
\]

together with a commuting-cell certificate.  It compresses to one triangular
filler only when the relevant third-domain transport or comparison permits
that representation.  The tri-domain principle alone does not prove this
compression.

Nor can an ordinary extra line repair a pair that already violates a
downward-closed linear feasibility predicate.  The closure certificate must
authorize a copy/share, schedule the uses, spatially separate them, or supply
another semantics-preserving rewrite.  A third color without such an effect
is not a filler.

This preserves the distinction:

\[
\boxed{
\text{conflict observed}
\ne
\text{aperture opened}
\ne
\text{aperture filled}
\ne
\text{closed conjunction witness}.
}
\]

If no filler has yet been found, the aperture is open and the conjunction is
undecided at the search level.  If the finite filling fibre is certified
empty, that candidate pair is refuted.  If another pair of lines closes, the
overall conjunction can still be inhabited.

---

## 4. Conjunction with triadic compatibility fibres

For two lines define the compatibility fibre:

\[
\mathcal C(\ell,m)
=
\begin{cases}
\mathbf 1,
&
\text{the sources pair directly},
\\
\operatorname{Fill}_{\mu(d,e)}
\left(H_{\mu(d,e)}(\ell,m)\right),
&
\text{a typed distinct-domain conflict opens},
\\
\mathbf 0,
&
\text{the pair is ill typed or has an unhandled conflict}.
\end{cases}
\]

The triadically resolved conjunction is:

\[
\boxed{
\operatorname{Fill}(A\land_\triangle B)
=
\sum_{\ell\in\operatorname{Fill}(A)}
\sum_{m\in\operatorname{Fill}(B)}
\mathcal C(\ell,m).
}
\tag{\(\triangle\)-and}
\]

An inhabitant is either:

- a direct compatible pair; or
- a pair together with a certified third-domain filler.

This gives the exact support inclusion:

\[
\operatorname{Supp}(A\land_\triangle B)
\subseteq
\operatorname{Supp}(A)\cap\operatorname{Supp}(B).
\]

Equality follows from the **triadic completion condition**:

\[
\boxed{
\begin{aligned}
\operatorname{Fill}(A)\ne\varnothing
\land
\operatorname{Fill}(B)\ne\varnothing
\quad\Longrightarrow\quad
\exists\ell,m,\ 
\mathcal C(\ell,m)\ne\varnothing.
\end{aligned}
}
\tag{A2-\(\triangle\)}
\]

Thus the Cartesian pair-completeness hypothesis A2 of note 0082 can be
replaced by A2-\(\triangle\).  Classical conjunction is recovered when every
required third-domain aperture can be filled.  When some apertures remain
open or are refuted, the proof-relevant connective remains resource
sensitive.

---

## 5. The conjunction witness is a cell

Two boundary lines plus a third-domain filling line naturally form a
triangular two-dimensional object:

\[
\operatorname{Cell}_\triangle(\ell_d,m_e,\kappa_{\mu(d,e)}).
\]

Calling this object merely another line would erase which conflict was
resolved and how.  If the proof language requires a one-dimensional named
witness, it needs an explicit abstraction:

\[
\operatorname{Cell}_\triangle(\ell,m,\kappa)
\xrightarrow{\operatorname{Abstract}_Q}
p:A\land_\triangle B,
\qquad
R_p=
(\ell,m,\kappa,\text{ports},\text{source},\text{history}).
\]

The residual makes reopening possible under observer refinement.  This is
the precise point where abstraction and controlled forgetting enter the
logical grammar: they name a closed cell without deleting the evidence that
made closure valid.

---

## 6. Symmetry, orientation, and coherence laws

### 6.1 Oriented symmetry

Swapping the two boundary lines preserves the remaining domain but reverses
the ordered ports:

\[
H_{\mu(d,e)}(\ell,m)^\star
\cong
H_{\mu(e,d)}(m,\ell).
\]

A filler must transport across this duality.  Treating the two port orders as
literally identical would erase orientation information.

### 6.2 Source conservation

Opening and closing retain the shared source identity and both occurrence
identities.  A \(K\)-filler interpreted as a duplicator must carry an explicit
copy or share certificate; it cannot silently create a second linear use.

### 6.3 Observer naturality

If observer refinement reveals that the lines did not share a source, or
reveals an additional distinction in the filler, the closed cell must either
transport naturally or reopen with the relevant residual.

### 6.4 Associativity remains open

For three lines, the parenthesizations

\[
(A\land_\triangle B)\land_\triangle C,
\qquad
A\land_\triangle(B\land_\triangle C)
\]

may open and fill apertures in different orders.  Associativity requires a
checked isomorphism between the resulting glued cell complexes that preserves
sources, occurrences, port order, fillers, and residuals.

The binary opening rule alone does not provide this associator.

### 6.5 Three-way conflict remains open

If \(K\)-, \(X\)-, and \(t\)-lines all compete for one source, independent
pairwise completion can reuse the same linear evidence circularly.  The
correct object may be one primitive three-way aperture or a higher cell,
rather than three unrelated binary holes.

This is the principal obstruction to promoting
\(\land_\triangle\) as a stable associative connective.

A capacity-two source gives a decisive counterexample: every pair among
three lines can be jointly admissible while the triple is not.  Pairwise
filled apertures therefore do not imply a globally filled three-way
aperture.  At capacity one, three lines may even cite one another circularly
as fillers unless the closure certificates carry a grounded progress order.

### 6.6 Same-domain contraction is a separate law

The complement rule has no value on \((d,d)\).  In particular, it cannot
derive the classical diagonal

\[
A\longrightarrow A\land A.
\]

Classical contraction therefore still needs an explicit copy/share
certificate or a separate same-domain aperture law.  Third-domain completion
alone is insufficient for ordinary Cartesian logic.

### 6.7 The remaining-domain operation is not a connective

The partial color operation

\[
(d,e)\longmapsto D\setminus\{d,e\}
\]

for \(d\ne e\) has no total associative extension on exactly three domain
colors that preserves this rule.  It should remain the typing of an oriented
horn or triangular cell, not be mistaken for the value operation of a binary
logical connective.  Compound proofs must retain bracketed cell complexes
and an explicit associator, or introduce a richer grading.

---

## 7. Relation to truth, failure, and exploration

The triadic rule refines the earlier line--hole interpretation:

\[
\begin{array}{c|c}
\text{state} & \text{logical authority}\\
\hline
\text{direct pair or closed triangular cell}
&
\text{conjunction witness}
\\
\text{typed aperture with unresolved filling fibre}
&
\text{open search obligation}
\\
\text{certified empty filling fibre for one pair}
&
\text{that pair is refuted}
\\
\text{every candidate pair certified empty}
&
\text{conjunction false in the completed finite model}
\end{array}
\]

Exploration can search the remaining-domain filling fibre.  Its outcomes are:

\[
\operatorname{Fill}(\kappa),
\qquad
\operatorname{EmptyCertificate},
\qquad
\operatorname{Frontier}(\operatorname{continue}).
\]

The search process does not itself define the connective.  It tries to
inhabit the compatibility fibre already declared by the grammar.

---

## 8. Finite executable calibration

The companion test
**tests/python/test_triadic_conflict_aperture_calibration.py** checks:

1. all six ordered distinct-domain pairs select one unique remaining domain
   and the expected forward or reverse orientation;
2. an open aperture is not yet a conjunction witness;
3. only a filler for the exact aperture, remaining domain, orientation, and
   role closes the triangular cell;
4. the filler projections recover both original line occurrences;
5. a bare third-domain line without a closure certificate is rejected;
6. a filler using the shared source twice is rejected;
7. distinct sources pair directly without an aperture, including same-domain
   lines;
8. same-source, same-domain conflicts and occurrence aliases remain explicit
   obstructions; and
9. swapping the boundary lines dualizes orientation and ports while
   preserving the hole domain.

The fixture uses the provisional operational roles:

\[
K\mapsto\text{construct-mediator},
\quad
X\mapsto\text{separate-placement},
\quad
t\mapsto\text{order-schedule}.
\]

These labels are calibration data, not stable ontology.

---

## 9. Decisive falsifiers

The proposal must be weakened or rejected if:

1. a line cannot be assigned one auditable domain identity at the conflict;
2. two distinct identities do not select a unique remaining domain;
3. the opened aperture loses source or occurrence identity;
4. a wrong-domain line can close the aperture;
5. a filler does not project back to the two boundary lines;
6. a bare third-color line closes without a cell certificate;
7. opening alone is reported as a proof of conjunction;
8. a filler silently copies, merges, or discards a linear source;
9. swapping boundary lines erases orientation rather than dualizing it;
10. observer refinement cannot reopen an invalidated closure;
11. the two conjunction parenthesizations have no coherent comparison; or
12. pairwise treatment of a three-way conflict duplicates evidence.

Items 11 and 12 are currently open theorem obligations.  The finite binary
calibration does not settle them.

---

## 10. Promotion boundary and next step

This note establishes:

- a unique remaining-domain opening rule for two distinct domain lines;
- a typed third-domain closing rule;
- a compatibility-fibre semantics for resource-sensitive conjunction;
- a condition under which classical support intersection is recovered;
- a proof-relevant distinction between open aperture and closed cell; and
- a finite executable calibration of all three domain-pair cases.

It does not establish:

- that every Adva line has one canonical tri-domain identity;
- that every typed aperture is fillable;
- an associative or commutative conjunction in the kernel;
- a coherent resolution of three-way source conflict;
- natural-deduction introduction and elimination rules;
- normalization or cut elimination; or
- a geometric realization of the triangular cell in a hyperbolic surface.

The next decisive fixture should use three lines sharing one source and
compare the two binary closure orders.  If the resulting cell complexes admit
a source- and residual-preserving associator, A2-\(\triangle\) becomes a
credible basis for conjunction introduction.  If not, the primitive logical
constructor should be ternary or explicitly ordered rather than an ordinary
binary conjunction.

## Conservative conclusion

The proposal works as a typed completion mechanism.  Two distinct domain
lines competing for one linear source determine a unique aperture in the
remaining domain.  A matching third-domain line closes a triangular cell,
and that closed cell can witness conjunction after an explicit abstraction.

The key correction is that opening is not success.  It reifies incompatibility
as a new typed obligation.  The earlier classical pairing hypothesis is
recovered only when these third-domain obligations are fillable coherently.
The unresolved mathematical issue is no longer the binary domain assignment;
it is the associativity and higher coherence of glued triangular cells.
