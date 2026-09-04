# ADR 0023: Admit the First Bounded Named `M6` Reveal Run

Status: accepted for one executable research calibration

## Context

ADR 0020 deliberately withheld the first checked-in `.adva` program while the
neutral carrier document boundary was unsettled. ADRs 0021 and 0022 now supply
a bounded `M6` relation profile and derive its two paths from validated stored
transition frames.

The next question is whether six directed transports between time, space, and
construction can be named without making those names semantic identities. A
finite run must also distinguish completing the six-frame observation from
proving the semantic filler of the resulting relation.

## Decision

1. The first checked-in neutral program is
   `programs/bootstrap-0/reveal.adva`.
2. Its carrier table contains one local observer snapshot, one reveal-method
   carrier, one seed-witness carrier, intermediate recorded boundaries, and a
   common final `history/result/evidence` boundary.
3. Six entry-point names form an observer-local experimental vocabulary:

   ```text
   construction -> time          run
   time         -> space         reveal
   space        -> construction  name

   construction -> space         instantiate
   space        -> time          resume
   time         -> construction  compile
   ```

   Entry-point names remain selectors. The relation checker uses only resolved
   `FrameIdV0` coordinates, exact three-port handoffs, common endpoints, and
   `compute/verify/learn` frame mechanisms.
4. The forward frames derive `compute verify compute`; the conjugate frames
   derive `verify compute verify`. The existing positive-braid `M6` formation
   checker must accept the pair before a completed report is emitted.
5. The research CLI command

   ```text
   adva reveal PROGRAM --output WITNESS --fuel N
   ```

   observes at most six named frame occurrences. Insufficient fuel emits a
   structurally checked suspended witness rather than failure.
6. A full six-occurrence run emits a separate self-describing
   `adva.m6-reveal-witness.research` version-zero artifact with the common
   `.adva` suffix. It retains source digest, naming coordinates, fuel ledger,
   both frame paths, handoffs, relation certificate, and problem list.
7. The first complete formation remains an open relation. Its question list
   records `experiment:first:m6-semantic-filler-required`; no filler, reverse
   transport, or semantic equality is manufactured.
8. The actual first output is retained at
   `programs/bootstrap-0/first-reveal-witness.adva`. Its source digest is
   `blake3:ac29810342f62beae0ff84da6c3a7a431bd65807d0a13b4e5b35da4027bcb227`
   and its witness digest is
   `blake3:b03cee7f38c01f0a84fa3c71227955ce8c85ac01a844f8c47e74a06c45a0d007`.
   CI must reproduce the exact witness bytes.

## Consequences

The repository now has a reproducible first `.adva` program and a finite
command that saves its result as another `.adva` witness. Experimental names
can be changed without becoming frame or semantic identities. Fuel exhaustion
and an open semantic relation are represented by different fields. The first
observation is now an auditable repository object rather than an expected
result described only in prose.

This is a formation run over already recorded graph boundaries. It does not
prove that any stored output was produced by executing its mechanism. It also
does not load three independent files as one invocation, search a shared
knowledge base, schedule independent strands around a cut, establish the
six-direction interpretation of `M6`, or implement feedback.

## Superseded constraint

ADR 0020's decision not to check in the first `.adva` program is superseded by
this narrowly scoped calibration. Its format, validation, and provenance
limits remain in force.
