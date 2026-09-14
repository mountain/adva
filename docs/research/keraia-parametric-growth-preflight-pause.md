# Keraia parametric-growth preflight: paused before a mathematical verdict

Status: bounded failed preflight, 2026-09-14. Base main:
`3f81373ef9766a5ca0e9df3b9bed4bb6b6e493ac`. This record introduces no
research word, certificate or mathematical claim.

Authored by ChatGPT (OpenAI). Mingli Yuan supplied the research direction and
his GitHub account is the submission proxy. The account is not evidence of
review, endorsement or correctness.

## Frozen question

The preceding Keraia run certifies exact complete-frame cycles, but deliberately
leaves

[
  D_3D_3,qquad D_3=\lambda x.((x x)x),
]

as `UnknownFuel`: its head repeats while its ordered argument stack grows.
The frozen question was whether a receiver-selected natural-number template

[
  F_r(n)=(P_r,D_r^n,c)
  quad\longmapstoquad
  F_r(n+r-2)
]

could check the concrete (r=3) premise and reuse the same rule at (r=4).
The intended certificate must check a finite, positive-length pure macro with
an opaque ordered stack prefix; it must preserve control, cursor, interpreter
profile and cost, contain no read or return, and have a strictly positive exact
integer stack increment. This would be a conditional induction over the
declared machine semantics, not a general nontermination procedure.

The complete frozen scope, negative controls and limits are retained in
[`contract.json`](../../experiments/keraia_growth_certificate/contract.json).
There are no search candidates. Each child permits at most 100,000 counted host
operations, 128 semantic steps, 30 seconds wall time and 256 MiB address space.
Only one implementation correction and replay was permitted.

## What actually ran

The first child stopped before the checker because the local isolated staging
directory did not have the repository-relative sibling modules on its import
path. The failure is retained under `evidence/attempt-1`. The one permitted
correction added the downloaded upstream module directories to the local
`PYTHONPATH`; no mathematical field or acceptance condition changed.

The corrected launch entered the checker and then stopped after 122 counted
host operations: the draft receiver called a nonexistent `oracle.named`
function. The upstream oracle intentionally exposes named compilation and
substitution but no de-Bruijn-to-named conversion under that name. This is an
implementation error in the new draft, not evidence for or against the
parametric recurrence. It is retained under `evidence/attempt-2`.

The first and second launches took about 40.65 ms and 49.81 ms respectively.
The highest measured child RSS upper bound was 13,568 KiB (13.25 MiB). Research,
reading, authoring, network and later storage time were not measured. No
candidate was searched, no suffix cylinder was removed from the unresolved
mass and no comparison with the previous five-million-unit campaign is made.

## Verdict and residual

The verdict is **Unknown / paused due to implementation failure**. In
particular:

- the old `UnknownFuel` classification remains authoritative;
- no new vocabulary is formed or proposed for promotion;
- no Keraia cylinder, Omega bound, Q4/M6 cell, native operation or universality
  result follows;
- the draft source is retained only to make the failed attempt reproducible.

The smallest continuation is to replace the nonexistent call with an explicit,
locally checked de-Bruijn-to-named conversion equivalent to the conversion
already present in the prior cycle receiver, review that single change, and
run one newly contracted finite attempt. It must not reuse the exhausted
correction allowance of this run.
