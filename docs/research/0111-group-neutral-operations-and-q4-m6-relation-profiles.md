# Group-Neutral Operations and Typed `Q4`/`M6` Relation Profiles

Status: bounded Rust formation calibration; no CLI or persistence promotion

This note corrects the braid-centered reading that arose while considering
`join` as a CLI primitive. It continues the neutral carrier and transition
frame work of notes 0109 and 0110 without modifying the `.adva` version-zero
document schema.

## 1. The correction

`Q4` and `M6` are sibling relation boundaries, not two instances of one
undifferentiated braid operation:

\[
\chi_{a,b}:ab\Rightarrow ba,
\qquad \partial\chi=Q_4,
\]

\[
\beta_{a,b}:aba\Rightarrow bab,
\qquad \partial\beta=M_6.
\]

The three readings retained by the current calibration are:

| relation | boundary | raw process lift | finite Coxeter shadow |
|---|---:|---|---|
| interchange | `Q4` | trace monoid | Klein four group |
| braid | `M6` | positive braid monoid | symmetric group `S3` |

The raw process lift is deliberately a monoid. General Adva steps need not be
invertible. Passing to `Z^2`, `B3`, or another group completion would require a
separate view contract and proof obligation.

The full symmetry group of a square presentation is also not stored in the
`Q4` profile. Presentation rotation or reflection can change orientation,
roles, and witness direction even while preserving an unlabeled polygon.

## 2. Common substrate

The common structure is a path-and-relation calculus:

\[
x\xrightarrow{p}y,
\qquad
p\xRightarrow{w}q,
\qquad
x\xrightarrow{q}y.
\]

One-dimensional paths retain their ordered histories. A two-dimensional
relation cell records an obligation or an explicit filler between parallel
paths. Group, monoid, Coxeter, geometric, proof, and execution readings are
views of this carrier rather than fields silently placed on every program.

This supports the existing finite `S4` calibration without identifying its
faces:

\[
\langle s_1,s_3\rangle\cong C_2\times C_2
\quad\leadsto\quad Q_4,
\]

\[
\langle s_1,s_2\rangle\cong S_3
\quad\leadsto\quad M_6.
\]

Their coexistence in `TO24` is evidence for a shared coherence envelope, not
a proof that one local group governs both relations.

## 3. Operational layers

The candidate CLI vocabulary is partitioned before any command is exposed:

| layer | candidate words | narrow meaning |
|---|---|---|
| carrier | `join`, `cut`, `close` | glue, select a boundary, close a zero residual |
| traversal | `step`, `run` | one admitted step, finite repetition |
| relation | `interchange`, `braid`, `transport` | form/fill `Q4`, form/fill `M6`, read one oriented filler |
| observation | `check`, `inspect` | validate or present without executing |

In particular:

- `join` is not group multiplication and does not require conjugacy;
- `cut` is not intrinsically the opening of a closed braid;
- `run` is not intrinsically braid motion;
- `transport` becomes conjugacy only under an additional braid/group view.

## 4. Rust calibration

`adva_witness::RelationCellV0` contains:

```text
RelationProfileV0
left raw RelationPathV0
right raw RelationPathV0
RelationFillingV0
```

`RelationProfileV0` prevents the `Q4` and `M6` shadows from being exchanged.
The checker admits exactly:

```text
interchange: ab  => ba,  a != b
braid:       aba => bab, a != b
```

An open relation contains a nonempty residual cache reference and cannot be
read as transport. A filled relation records `left_to_right` or
`right_to_left`, a witness cache reference, and an optional retained residual.
Transport follows only that declared orientation. It never manufactures an
inverse.

The returned `RelationFormationCertificateV0` checks formation only. Cache
references are not replayed, authenticated, or promoted to semantic identity.

## 5. Deferred obligations

This calibration does not yet provide:

1. endpoint and occurrence ledgers for general relation paths;
2. semantic checking of an interchange or braid witness;
3. horizontal or vertical composition of relation cells;
4. whiskering, identities, associators, or a `TO24` three-cell;
5. a group completion or inverse-execution rule;
6. `join`, `cut`, `close`, `step`, or `run` commands;
7. relation-cell storage inside `.adva` documents;
8. feedback, infinite execution, or conjugacy as a generic judgment.

The next engineering gate is a typed endpoint/occurrence adapter from checked
Adva frames to `RelationPathV0`. Until that exists, generator labels remain
research coordinates and relation cells cannot rewrite or execute stored
programs.
