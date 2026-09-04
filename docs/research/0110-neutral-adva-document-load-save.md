# Neutral `.adva` document load/save boundary

Status: bounded executable research V0  
Date: 2026-09-04

## 1. Purpose

The neutral-carrier grammar distinguishes the input view

\[
(\mathsf{subject},\mathsf{method},\mathsf{object})
\]

from the persisted output view

\[
(\mathsf{history},\mathsf{result},\mathsf{evidence}).
\]

This note implements the missing boundary between them. It does not choose a
default cyclic wiring. Every reload states how each stored output slot becomes
one input slot.

## 2. Document

`AdvaDocumentV0` is a self-describing JSON container with exactly three
fields: a schema identifier, a version, and one output triple. The schema is
`adva.neutral-carrier.research` and the version is zero. Unknown fields are
rejected.

Every carrier retains its `ArtifactKeyV0` cache coordinate and canonical
`OpenFrontierV0`. The key is not an embedded program, source identity,
occurrence identity, proof, or model. Consequently the document is a checked
manifest, not yet a self-contained durable artifact store.

## 3. Save boundary

`save_adva_document_v0` performs the following finite operation:

1. require the exact `.adva` suffix;
2. check the schema-independent output carrier invariants;
3. encode the versioned document deterministically;
4. compute a BLAKE3 integrity digest over canonical compact JSON;
5. write and synchronize a temporary file in the destination directory;
6. rename it into place and synchronize the parent directory on Unix.

The returned receipt records the destination, digest, and byte count. A digest
is an integrity and cache coordinate only; it is not a signature or semantic
identity.

## 4. Load and relabelling boundary

A route is a pair

\[
\mathsf{OutputLabelV0}\longrightarrow\mathsf{InputLabelV0}.
\]

`ReloadPlanV0` contains exactly three routes. Validity requires both projections
to be bijective: each output appears once and each input appears once. Thus
the loader cannot introduce implicit copy, discard, weakening, or contraction.

`load_adva_document_v0` reads and revalidates the document before applying the
plan. Success returns the re-labelled `MechanismInputV0` and a certificate
containing the canonical route order, document digest, schema/version check,
frontier check, and exact-bijection check.

Route order in caller data has no semantics. The certificate canonicalizes it
by input order: subject, method, object.

## 5. Python boundary

`adva.persistence` provides `save_adva_document` and `load_adva_document`.
Python handles ergonomic mappings and paths. The native extension passes the
content to `adva-witness`; Python neither validates frontiers nor creates
semantic identities.

## 6. Tested refusal surface

Rust and Python tests cover:

- deterministic in-memory document round trip;
- explicit output-to-input permutation with exact carrier preservation;
- rejection of repeated output or input slots;
- rejection of wrong versions, empty artifact coordinates, noncanonical
  frontiers, and non-`.adva` paths;
- atomic replacement followed by full reload validation; and
- equality of save and load digests.

Tests use temporary directories only. No `.adva` program is added to the
repository, so the first authored program remains outside this implementation
change.

## 7. Remaining boundary

This work does not resolve a carrier key against a durable artifact store, prove
that stored outputs came from a successful mechanism, choose a default route,
execute the reloaded input, implement feedback, or unify this JSON container
with existing Lisp-source `.adva` files. Those require separate certificates
and format-dispatch decisions.
