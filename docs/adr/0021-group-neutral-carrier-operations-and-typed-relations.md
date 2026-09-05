# ADR 0021: Keep Carrier Operations Group-Neutral and Type Relation Cells

Status: accepted for the research companion

## Context

The candidate CLI vocabulary introduced `join`, `cut`, `close`, `step`, and
`run` while the existing Bootstrap Zero research uses two different local
relation boundaries:

\[
Q_4:\;ab\Rightarrow ba,
\qquad
M_6:\;aba\Rightarrow bab.
\]

Treating both relations as braid-group operations would erase an important
distinction. `Q4` is an interchange boundary. Before inverses it has a trace
monoid presentation; its finite Coxeter shadow is the Klein four group.
`M6` is a braid boundary. Before inverses it has a positive braid-monoid
presentation; its finite Coxeter shadow is `S3`. The geometric automorphism
group of a displayed square is another view and is not the `Q4` process
algebra.

Adva mechanisms may also be partial and noninvertible. Therefore no group can
serve as the ontology of every carrier operation.

## Decision

1. Carrier operations remain group-neutral:
   - `join` glues explicit routed boundaries;
   - `cut` selects an input/output observation boundary;
   - `close` is a future checked zero-residual closure operation.
2. Traversal remains distinct from gluing:
   - `step` advances one admitted transition;
   - `run` is a future finite repetition policy over steps.
3. Relation operations inhabit a proof-relevant layer:
   - `interchange` forms or fills `Q4`;
   - `braid` forms or fills `M6`;
   - `transport` reads one explicitly oriented filler.
4. `transport` is the generic word. Conjugacy is a braid-view interpretation,
   not the meaning of every cut change or relation filler.
5. The research Rust layer records a coherent triple:

   ```text
   boundary shape / process lift / finite Coxeter shadow
   ```

   with the initial exact profiles:

   ```text
   Q4 / trace monoid          / Klein four
   M6 / positive braid monoid / S3
   ```
6. Raw left and right paths remain distinct after formation. An open boundary
   must retain an explicit residual reference. A filled boundary cites one
   directional witness; it never obtains the reverse direction implicitly.
7. `AdvaDocumentV0` and `adva.ir` version one remain unchanged. Relation cells
   are independent research artifacts until their composition, identity, and
   persistence obligations are understood.

## Consequences

`join` can remain a CLI candidate without being confused with group
multiplication, braid closure, or conjugacy. `run` can range over `Q4`, `M6`,
and future relation families because its kernel meaning is finite traversal,
not braid motion.

The present Rust checker verifies only relation-profile coherence, the exact
`ab/ba` or `aba/bab` word shape, distinct raw paths, and explicit
witness/residual references. It does not replay a witness, establish program
equality, implement a group, construct a `TO24` coherence filler, or authorize
feedback.

## Rejected alternatives

- **Use the braid group as the common kernel.** This misclassifies independent
  interchange and assumes inverses unavailable to general Adva mechanisms.
- **Store only polygon shape.** A square or hexagon does not determine its
  process lift or the observation that produced its finite state space.
- **Call every cut change conjugacy.** This is valid only under an admitted
  braid/group view and would overstate the generic transport judgment.
- **Extend `.adva` V0 immediately.** The CLI and relation-composition semantics
  are still candidates; changing the document schema would make a research
  distinction look stable.
