# ADR 0024: Admit a Three-Sided Trace-Arithmetic Calibration

Status: accepted for one executable research calibration

## Context

The first bounded reveal retains two distinct `M6` paths and one open semantic
filler. That single residual is too coarse for studying semantic drift. Equal
storage endpoints do not show that two interpretations point to the same
truth, and a trace name or digest supplies neither time nor space constraints.

The next experiment needs arithmetic coordinates on time, space, and
construction without choosing a unique threading order or turning a lossy
projection into path equality.

## Decision

1. Add `adva trace-arithmetic REVEAL_WITNESS --output CALIBRATION`. It consumes
   a completed persisted reveal witness, not the source program.
2. Retain the exact two frame paths and give each a BLAKE3 digest. Derive time
   counts, exact spatial endpoints, and a construction projection containing
   mechanism incidence plus the still-authoritative ordered word.
3. Compute `left - right` in separate typed residual records. Coordinates from
   different sides cannot cancel through one scalar total.
4. Record `T = chi_T(S,C)`, `S = chi_S(C,T)`, and `C = chi_C(T,S)`, but keep all
   three open until explicit characteristic-map witnesses exist. Equality of a
   direct projection is not such a witness.
5. Compute a diagnostic commutative product weight and the exact `right / left`
   residual. This shadow forgets order; it is not process semantics or a braid
   quotient.
6. Keep the truth fiber open with no shared truth coordinate. Neither matching
   projections nor an arithmetic hash may fill it.
7. Save the self-checking result as
   `adva.trace-arithmetic-calibration.research` version zero with the common
   `.adva` suffix.

## First result

For `compute verify compute` versus `verify compute verify`, the time residual
and exact endpoint residual are zero. The construction residual is
`compute = +1`, `verify = -1`, with zero learn, length, and alternation
components. The commutative weights are `compute^2 verify` and
`compute verify^2`, so the naive multiplicative residual is not one.

The experiment exposes five independently named open obligations: three
cross-side characteristic maps, multiplicative holonomy, and a shared truth
coordinate. It does not close the original semantic filler.

The first output is retained at
`programs/bootstrap-0/first-trace-arithmetic.adva`. Its artifact digest is
`blake3:09be4633b0cbef2e9d8a29f2e6b7b2ea1a1bf7e3f715655d411b42f18af3d407`.
CI must reproduce the exact bytes.

## Consequences

Persisted witnesses can now be reused without reloading their source program.
An explicit collision test shows that equal mechanism incidence, length, and
alternation counts do not identify ordered words.

Carrier IDs remain document-local storage coordinates, BLAKE3 digests remain
content coordinates rather than signatures, and external truth still requires
an observation anchor outside this formation experiment.
