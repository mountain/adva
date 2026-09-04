# Transition-Frame Relation Path Adapter

Status: bounded executable research V0; no execution or CLI promotion

This note implements the first persistent-carrier adapter for the typed
`Q4`/`M6` relation profiles of note 0111. It does not modify
`AdvaDocumentV0`.

## 1. Source of a path word

For one stored transition frame

\[
(S,M,O)\xrightarrow{\mu}(H,R,E),
\]

the relation generator is the edge mechanism

\[
\mu\in\{\mathsf{compute},\mathsf{verify},\mathsf{learn}\}.
\]

The method carrier `M` remains an input. It is not the edge label. This is
necessary for two differently ordered paths to share the same labelled input
boundary.

Each path step retains:

```text
FrameRelationStepV0 := {
  frame: FrameIdV0,
  mechanism: MechanismV0,
  input: FrameInputV0,
  output: RecordedFrameOutputV0
}
```

`FrameIdV0` is a document-local storage occurrence. It is not an IR node,
source, or occurrence identity.

## 2. Exact three-port handoff

Let one recorded output be `(H,R,E)` and the next input be `(S,M,O)`. The
adapter requires equality of the underlying carrier sets and derives the
unique permutation

\[
\rho:\{H,R,E\}\xrightarrow{\cong}\{S,M,O\}.
\]

For example,

```text
H -> object
R -> subject
E -> method
```

is retained literally as a `FrameHandoffRouteV0`. No conventional wiring is
assumed. A partial reuse, external carrier, repeated target, ready output, or
repeated frame occurrence is rejected.

This is not yet `join`. It recognizes an already present full handoff in one
validated document and neither searches for nor constructs a route.

## 3. Parallel path boundary

Two derived frame paths may form a relation only if

\[
\operatorname{start}(p)=\operatorname{start}(q)
\]

as exact `subject/method/object` triples, and

\[
\operatorname{end}(p)=\operatorname{end}(q)
\]

as exact `history/result/evidence` triples.

Their mechanism words are then passed to the existing relation checker:

```text
Q4: compute verify
    verify compute

M6: compute verify compute
    verify compute verify
```

Other distinct mechanism pairs can occupy `a` and `b`; the displayed pair is
the executable calibration.

The returned `FrameRelationCellV0` retains:

- the validated document digest;
- both raw frame paths and every frame ID;
- every derived handoff permutation;
- the two mechanism words;
- the open or directionally filled relation state; and
- a `FrameRelationCertificateV0` limited to graph formation.

## 4. Refusal surface

Rust tests reject:

1. an invalid neutral document;
2. an empty, unknown, or repeated frame path;
3. a ready frame without recorded outputs;
4. an adjacent pair that does not reuse all three carrier coordinates;
5. unequal labelled starting or ending boundaries; and
6. a mechanism history that is not the selected `Q4` or `M6` word.

The positive fixtures derive one `Q4` diamond and one `M6` boundary from
complete neutral document graphs. They also verify a non-identity handoff
permutation and retained relation residuals.

## 5. Remaining gap

The adapter proves no execution provenance: a recorded output is still only a
persistent reference. It also provides no bridge from `FrameIdV0` to
`NodeId`/`OccurrenceId`, no relation-witness replay, no relation-cell
composition, no `TO24` filler, and no feedback.

The next safe CLI step is therefore read-only inspection of these derived
paths. A mutating `join` command must wait for a result artifact that can
distinguish:

```text
already connected / connectable with a supplied route / open residual
```

and must never manufacture carrier identity from equal cache content.
