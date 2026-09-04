# Neutral `.adva` document graph load/save boundary

Status: bounded executable research V0  
Date: 2026-09-04

## 1. Correction

The neutral-carrier grammar distinguishes the input view

\[
(\mathsf{subject},\mathsf{method},\mathsf{object})
\]

from the output view

\[
(\mathsf{history},\mathsf{result},\mathsf{evidence}).
\]

Carrier neutrality does not require mechanism absence from the document. It
requires only that mechanism is not an intrinsic carrier property. The
correct persistent shape is therefore a graph whose vertices are neutral
carriers and whose edges are mechanism-labelled transition frames.

## 2. Abstract document grammar

The research envelope is structurally:

```text
AdvaDocumentV0 := {
  schema, version,
  carriers: StoredCarrierV0*,
  frames: TransitionFrameV0*,
  entrypoints: EntryPointV0+
}

StoredCarrierV0 := { id, carrier: NeutralCarrierV0 }

TransitionFrameV0 := {
  id,
  input:  { subject: CarrierIdV0,
            method: CarrierIdV0,
            object: CarrierIdV0 },
  mechanism: Compute | Verify | Learn,
  output: { history: CarrierIdV0?,
            result: CarrierIdV0?,
            evidence: CarrierIdV0? }
}

EntryPointV0 := { name, frame: FrameIdV0 }
```

All three output references are absent for a ready frame or present for a
recorded frame. Mixed presence is invalid. The labels remain present as the
three output ports in both cases.

`CarrierIdV0` and `FrameIdV0` are canonical document-local coordinates. They
allocate no `SourceId`, `OccurrenceId`, value identity, proof identity, or
program identity.

## 3. Persistent substitution and reuse

There is no loader-local default wiring. A later frame expresses substitution
by referring to stored carrier coordinates in its labelled input positions.
For example, the structural relationship

\[
\mathsf{result}_{i}\mapsto\mathsf{subject}_{j},\qquad
\mathsf{evidence}_{i}\mapsto\mathsf{method}_{j},\qquad
\mathsf{history}_{i}\mapsto\mathsf{object}_{j}
\]

is represented by equal carrier coordinates at those six labelled positions.
Other permutations are equally explicit. The document does not infer one.

References within each three-slot input or recorded-output boundary must be
distinct. Reusing content in more than one same-frame slot requires separate
stored carrier positions rather than an implicit copy at the loader boundary.

Learning replacement carriers also use table references. The resolved
`FillPlanV0` is constructed only while loading and then checked by the existing
mechanism grammar.

## 4. Validation and load

`AdvaDocumentV0::from_json` rejects unknown fields and validates the whole
graph before any entry point can be selected:

1. exact schema and version;
2. strictly increasing carrier and frame coordinates;
3. strictly increasing, nonempty entry-point names;
4. nonempty artifact cache coordinates;
5. canonical open and declared-verification frontiers;
6. resolvable carrier and entry-frame references;
7. three distinct references at each input and recorded-output boundary;
8. all-ready or all-recorded output presence;
9. nonempty mechanism-specific witness/evidence coordinates; and
10. successful `MechanismFormV0::check` for every stored frame.

`load_adva_document_v0(path, entrypoint)` then resolves one selected frame to
the existing `MechanismFormV0`, its formation admission, and any complete
recorded `MechanismOutputV0`. Its certificate records the selected frame,
document digest, and the checked schema, table, reference, and mechanism-form
boundaries.

Loading a recorded frame does not establish output provenance. "Recorded" is
a persistence state, not an execution certificate.

## 5. Save

`save_adva_document_v0` accepts a complete validated `AdvaDocumentV0` rather
than constructing an output-only manifest. It:

1. requires the exact `.adva` suffix;
2. revalidates the complete graph;
3. encodes canonical pretty JSON;
4. computes a BLAKE3 integrity digest over canonical compact JSON;
5. writes and synchronizes a same-directory temporary file;
6. renames it into place and synchronizes the parent directory on Unix.

The digest is an integrity/cache coordinate, not a signature or semantic
identity.

## 6. Python boundary

`adva.persistence.save_adva_document(path, document)` accepts the complete
JSON-shaped graph. `load_adva_document(path, entrypoint)` returns the resolved
transition and Rust load certificate. Python does not validate references,
frontiers, mechanism forms, or allocate semantic identities.

## 7. Tested refusal surface

Rust and Python tests use temporary files only and cover:

- deterministic graph round trip and named entry-point selection;
- mechanism labels present on frames and absent from carriers;
- recorded output reuse by a later ready frame;
- learning replacement resolution through the carrier table;
- wrong versions, empty keys, noncanonical tables, unknown references,
  repeated boundary references, partial outputs, and wrong suffixes;
- atomic replacement and save/load digest agreement.

No `.adva` program is added to the repository. The first authored program
remains outside this implementation change.

## 8. Remaining boundary

The envelope does not embed or resolve artifact content, authenticate it,
execute a mechanism, prove that recorded outputs came from an execution,
mutate ready frames into recorded frames, schedule a cycle, implement
feedback, or unify its parser with Lisp-source `.adva` files. These require
separate result and certificate types.
