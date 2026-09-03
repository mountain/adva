# O1: Null = Universal

Status: proposed ontological axiom and natural-deduction requirement.

## Surface statement

\[
\boxed{\mathrm{Null}=\mathrm{Universal}.}
\tag{O1}
\]

The spelling and order above are authoritative for this proposal.

## Present status

O1 is not yet a theorem, stable definition, logical equality, program
operation, or registered exact claim. It is the first requirement posed by
the ontology path to a future natural-deduction system.

In particular, the equality sign is deliberately not resolved here as
definitional equality, propositional equality, mutual derivability, an
isomorphism, or observer-relative identification. Choosing among those
readings is part of the required theory.

## Minimal formation demand

A future calculus must first supply a common type or judgemental universe in
which both expressions are well formed. Schematically,

\[
\Gamma\vdash\mathrm{Null}:\mathsf{OntologicalForm},
\qquad
\Gamma\vdash\mathrm{Universal}:\mathsf{OntologicalForm}.
\]

It must then state a typed introduction rule for O1, for example only at the
level of an open requirement,

\[
\frac{}{
\Gamma\vdash
\mathrm{Null}=_{\mathsf O}\mathrm{Universal}
:\mathsf{OntologicalForm}
}.
\]

The symbol \(=_{\mathsf O}\) is a placeholder. This file does not authorize
ordinary untyped equality.

## Requirements on natural deduction

Any calculus realizing O1 must specify:

1. formation rules for \(\mathrm{Null}\), \(\mathrm{Universal}\), and their
   common type;
2. the exact strength of \(=_{\mathsf O}\);
3. introduction and elimination rules;
4. the substitutions and contexts in which O1 may be transported;
5. whether polarity reversal changes the presentation while retaining the
   same ontological word;
6. which residual distinguishes the two presentations before sealing;
7. a nontriviality argument or model showing that O1 does not collapse all
   judgements; and
8. a reopen rule retaining the proof, scope, and residual history used to seal
   the word.

## Nonclaims

O1 does not presently assert any of the following:

- the empty set equals a universal set;
- logical falsehood equals truth;
- \(0=1\);
- every initial object is a terminal object;
- every empty filling fibre is universally filled;
- a program hole, cut port, metavariable, logical obligation, observer
  aperture, singularity, and \(\Omega\) are identical;
- every two ontological words are equal; or
- Adva already implements the required natural-deduction rules.

Such consequences would require separately typed derivations. They must not
be imported from the surface spelling of O1.

## First proof obligations

Before O1 can become a certified semantic word, the ontology programme must
produce at least:

1. one precise typed reading of both sides;
2. one introduction rule and one elimination or substitution rule;
3. one nontrivial finite model or a decisive obstruction;
4. one example context in which the two presentations are interchangeable;
5. one negative context in which an untyped substitution is rejected; and
6. a closure certificate recording the residual forgotten by the
   identification.

Until those obligations are discharged, O1 remains open.
