# From a Fixed Alphabet to Historical Primitives

Status: philosophical synthesis initiated by Mingli Yuan's finite-observer and
open/close-hole questions. The constructions in this note are working
hypotheses. They are not implemented operations, Rust judgments, registered
claims, or a statement of Leibniz's own view.

This note depends on the historical reconstruction in
[0001](0001-leibniz-universal-characteristic.md).

---

## 0. The question inherited from finite learning

A finite learner receives a finite history \(D\) through an observation
language \(Q\). Even perfect reasoning within that language determines at most
a fibre of compatible structures:

\[
\mathcal H_Q(D)
=
\{W\mid \operatorname{Obs}_Q(W)=D\}.
\]

Experience constrains this fibre; deduction derives consequences inside a
declared representation. Neither operation alone explains who creates a new
question, a new feature language, a new intermediate object, or a refined
observer.

Human imagination appears to cross that boundary by proposing something that
is not yet an observed fact and is not derivable in the old vocabulary. A
formal account must permit novelty without treating every arbitrary string as
a meaningful invention.

## 1. What the Leibnizian architecture contributes

The useful inheritance is a separation of functions.

| Leibnizian function | open-logic reading | mandatory qualification |
|---|---|---|
| characteristic | structure-bearing public representation | no representation is globally final |
| calculus | certificate-bearing manipulation and judgment | a calculus cannot invent its own missing vocabulary by proof alone |
| analysis | expose conditions and unresolved components | decomposition need not terminate in absolute atoms |
| synthesis | combine components into candidate constructions | candidates may be contradictory or unrepresentable |
| encyclopaedia | accumulated external memory for discovery | records must retain provenance, failure, and observer scope |
| art of discovery | change the space in which a problem can be posed | novelty still requires later judgment |

The correspondence is interpretive. It does not identify these historical
functions with Adva's three domains or with current program types.

## 2. The decisive departure: no absolute alphabet

Leibniz's early programme begins with an alphabet of primitive thoughts. The
open-logic proposal instead begins with a finite, versioned signature
\(\Sigma_Q\) available to observer \(Q\).

A new primitive is not assumed to be metaphysically atomic. It is produced by
a history:

\[
\Sigma_Q
\xrightarrow{\operatorname{Open}_Q}
(\Sigma_Q,h)
\xrightarrow{\operatorname{Explore}_Q}
(e,\pi?,R,H)
\xrightarrow{\operatorname{Seal}_{Q,\pi}}
\Sigma_Q\cup\{\sigma_h\}.
\]

Here:

- \(h\) is a fresh typed hole together with an explicit obligation;
- \(e\) is a candidate filling or construction;
- \(\pi\) is a scoped certificate when closure succeeds;
- \(R\) is unresolved or deliberately hidden residual structure;
- \(H\) is the analysis, synthesis, observation, and failure history; and
- \(\sigma_h\) is a reusable character for the sealed construction.

The proposed character has the conceptual payload

\[
\sigma_h=(e,\pi,R,H).
\]

It may be manipulated without expanding \(e\) on every use, just as
Leibnizian symbolic cognition allows blind thought. But the expansion and its
authority remain recoverable.

The governing intuition is:

> Every primitive is a hole that was once sealed.

This is a research principle, not an established theorem. Some primitives may
remain externally stipulated at a given version boundary. The claim is that
new internal primitives should enter through an auditable sealing history
rather than silent declaration.

## 3. Opening a hole

An open hole is not merely an unbound variable, an empty object, a singular
middle point, or missing input data. It must record at least:

- a typed boundary or interface;
- the observer and language under which the absence was detected;
- the obligation that would count as a filling;
- the process or residual that exposed the absence; and
- the distinction between unknown, inconsistent, unrepresentable, and
  resource-exhausted states.

Opening can occur in several ways:

1. **analysis** decomposes a familiar object and exposes an unresolved
   condition;
2. **counterexample** breaks an earlier closure and leaves a new obligation;
3. **residual activation** makes previously hidden process structure relevant;
4. **observer refinement** introduces distinctions unavailable to the old
   language; or
5. **constructive imagination** proposes a new interface, comparison, or
   representation whose consequences are not yet known.

The fifth case is the hardest. A machine has not displayed imagination merely
because it enumerates terms in a fixed grammar. It must be able to propose a
change of typed vocabulary or observation while retaining a falsification
handle.

## 4. Sealing is not erasure

Sealing a hole is observer-relative certification, not global identity. In
general,

\[
\operatorname{Seal}_Q(\operatorname{Open}_Q(S))
\neq S.
\]

The left side must retain new information: at minimum a certificate, a history,
a residual, or an outstanding obligation. If open and seal are implemented as
inverse edits, the system has only created and deleted a placeholder.

A sealed character authorizes a particular future use under a declared scope.
It does not automatically authorize:

- equality of the original processes;
- contraction of distinct occurrences;
- provenance hiding;
- a stable right to forget;
- transfer to every observer;
- an equation or coherence cell; or
- a claim that the represented structure is intrinsic to the world.

## 5. Reopening and observer refinement

Let \(Q\preceq Q'\) mean that \(Q'\) can observe distinctions hidden from
\(Q\). A closure certified under \(Q\) may fail to transport to \(Q'\). Reopening
has the conceptual form

\[
\operatorname{Reopen}_{Q\to Q'}
(\sigma_h)
\longrightarrow
(h',e,\pi,R,H,\omega),
\]

where \(\omega\) explains why the old certificate is insufficient, why a
residual became visible, or why a new obligation has appeared.

Reopening is not arbitrary revocation. It must point to retained evidence. This
is why the exploration record is semantic fuel rather than archival decoration:
a later observer may find the route by which a supposedly primitive character
can be opened again.

No global final observer is assumed. Stability is local and versioned:

\[
(Q_0,\Sigma_0)
\to
(Q_1,\Sigma_1)
\to
(Q_2,\Sigma_2)
\to\cdots .
\]

The sequence may contain refinement, branching, incompatible local languages,
and returns to earlier residuals. It need not converge to one complete
signature.

## 6. Imagination, experience, and reason

The proposed division of labour is:

\[
\begin{aligned}
\text{imagination} &:\quad
  \text{open or reshape a typed possibility space},\\
\text{experience} &:\quad
  \text{constrain, separate, or refute candidates},\\
\text{reason} &:\quad
  \text{derive consequences and check certificates},\\
\text{objectification} &:\quad
  \text{seal a construction as a reusable character},\\
\text{memory} &:\quad
  \text{preserve the path by which it may later reopen}.
\end{aligned}
\]

Imagination is therefore not a truth-preserving inference rule. Its output is a
candidate language extension together with obligations and expected
observations. Reliability comes later from experience and reason.

This answers finite learning only in a qualified sense. The learner never
escapes finitude absolutely. It can exceed any one fixed finite observer by
changing the observer and preserving the transitions between finite states.

### 6.1 Current bounded aperture calibration

[Open PR 91](https://github.com/mountain/adva/pull/91) independently implements
a first research-only aperture layer over unchanged Rust-grounded through
artifacts. Its passed test matrix supports a deliberately weaker result:

- an existing finite through relation can be read as a filling fibre;
- a unique filling can be selected without deleting the residual;
- a multivalued fibre refuses implicit close and retains unselected fillings;
- a grounded empty filling fibre remains distinct from no aperture; and
- reopening re-exposes the same aperture while retaining close/reopen trace.

This is genuine evidence for the claims that close is not erasure and reopen is
not historical inversion. It does not yet support the historical-alphabet
construction above. The companion creates no new hole type or vocabulary,
does not objectify a sealed span as a reusable primitive, and does not reopen a
closure because a refined observer \(Q'\) exposed a formerly hidden residual.
Those remain the next stronger hypotheses.

## 7. Relationship to the three-domain programme

It would be premature to assign characteristic, calculus, and discovery
one-to-one to construction, space, and time. Leibniz's distinction is
functional; Adva's triadic domains are proposed observer readings over exact
program fibres.

A safer hypothesis is that every domain may admit typed opening and sealing,

\[
\operatorname{Open}_d,\operatorname{Seal}_d,
\qquad d\in\{K,X,t\},
\]

while the characteristic supplies shared interface notation and the calculus
checks transports or closures. Domain cycling must retain the complete carrier
and its residual; a finite circular relation is not automatically a closed
execution.

The relation between the three typed hole families, projective duality, and
the empty/universal pair remains open. No identification should be made until
their input boundaries, dual actions, and closure certificates are stated.

## 8. A Leibnizian core with an anti-Leibnizian boundary

The synthesis can be summarized as follows.

Inside a declared finite observer, adopt the Leibnizian discipline:

- make concepts public in compositional characters;
- calculate by explicit rules;
- distinguish proof, refutation, and invalid representation;
- organize knowledge so that discoveries can be reproduced.

At the boundary between observers, reject a divine completed language:

- do not assume a final alphabet;
- do not identify finite closure with universal truth;
- do not erase the history compressed into a character;
- permit certified reopening under a refined context.

This yields a candidate **open universal characteristic**: universal not
because one finite language already contains everything, but because the
system has a disciplined way to extend, compare, seal, and reopen finite
languages.

## 9. Nonclaims and red-team questions

This note does not establish that:

- every semantic primitive can be generated by sealing a prior hole;
- the proposed operations form a category, adjunction, modality, or
  cobordism theory;
- \(\operatorname{Open}_d\) and \(\operatorname{Seal}_d\) exist in current
  Adva code;
- the three domains provide a complete ontology of imagination;
- historical retention is sufficient for safe reopening; or
- an open characteristic yields complete logic or universal computation.

The main red-team questions are:

1. What prevents arbitrary vocabulary mutation from being called imagination?
2. Who is authorized to declare that a hole has been sealed?
3. Which parts of a certificate transport under observer refinement?
4. Can residuals grow without bound and make every sealed primitive unusable?
5. When are two differently generated characters comparable?
6. Can a history be compressed while preserving all future reopening routes?
7. Is "start as a hole" a typed construction, or only a metaphor for missing
   initial conditions?

The next note turns these questions into bounded experiments.
