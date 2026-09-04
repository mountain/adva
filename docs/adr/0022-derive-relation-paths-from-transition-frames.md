# ADR 0022: Derive Relation Paths from Mechanism-Labelled Transition Frames

Status: accepted for the research companion

## Context

ADR 0021 separates carrier operations, finite traversal, and proof-relevant
relations. Its initial `RelationPathV0` uses research generator labels and
therefore cannot yet show that a relation belongs to a particular neutral
`.adva` document.

The persistent document already distinguishes:

- neutral carrier coordinates;
- `subject/method/object` input slots;
- `compute/verify/learn` mechanism labels on transition frames;
- `history/result/evidence` output slots; and
- document-local `FrameIdV0` coordinates.

An adapter must not reinterpret the `method` input carrier as an edge label.
Doing so would collapse one of the three inputs into the mechanism and make
two paths such as `compute verify` and `verify compute` appear to have
different starting states merely because their first edge differs.

## Decision

1. A stored relation generator is derived from `FrameMechanismV0`:

   ```text
   compute | verify | learn
   ```

   The `method` carrier remains an ordinary member of the input triple.
2. `FrameIdV0` identifies each document-local step occurrence. Reusing one
   frame ID within a finite path is rejected because V0 has no event
   re-enabling or feedback semantics.
3. Every admitted step must have a complete recorded output triple. A ready
   frame supplies no endpoint for a subsequent structural path.
4. Adjacent frames compose only when the first frame's three recorded output
   carrier coordinates are reused exactly once by the second frame's three
   inputs. The derived output-to-input permutation is retained as
   `FrameHandoffRouteV0`.
5. Two frame paths form a relation candidate only when they have the same
   exact labelled input boundary and the same exact labelled recorded-output
   boundary.
6. The resulting artifact records the validated document digest, both complete
   frame paths, both handoff ledgers, the abstract `Q4` or `M6` relation cell,
   and a narrow formation certificate.
7. These coordinates remain document-local. `FrameIdV0` is not promoted to
   `adva_ir::OccurrenceId`, and shared carrier references do not prove shared
   semantic values or mechanism-output provenance.

## Consequences

`Q4` and `M6` paths can now be derived from persistent frame graphs without
accepting caller-written `a` and `b` labels. A `Q4` diamond may have exact
mechanism histories `compute verify` and `verify compute`; an `M6` boundary may
have `compute verify compute` and `verify compute verify`.

This adapter checks a full, already-recorded three-carrier handoff. It does not
implement `join`: no missing route is searched for, no carrier is copied or
discarded, and no output is generated. It also does not establish that the
recorded frames were executed or that the relation filler is semantically
valid.

## Rejected alternatives

- **Use the method carrier as the generator.** This confuses an input object
  with the edge mechanism and prevents common starting boundaries.
- **Compare artifact content instead of carrier coordinates.** Cache equality
  is not permission to identify document positions.
- **Infer partial handoffs.** A missing input or unused output is an open join
  problem and must remain outside this closed finite-path adapter.
- **Reuse a frame ID to represent iteration.** Iteration requires fresh event
  occurrence or explicit re-enabling semantics, neither of which exists in
  V0.
