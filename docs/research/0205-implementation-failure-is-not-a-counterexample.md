# 0205 — Implementation failure is not a counterexample

Status: executed bounded external calibration, 2026-09-16. Base main:
`c3081ab7efe65ed064535e8d9bf79ae3dc65238e`. This continues the remaining
failure-kind control named by Research 0090 and Research 0204. It adds no stable
operation or new vocabulary.

Direction: Mingli Yuan's finite-observer and open-world question. Implementation,
argument and review: ChatGPT (OpenAI), submitted through his account as an
authorized proxy; not his authorship, review, endorsement or correctness
guarantee.

All prose, code, fixtures and generated evidence in this contribution are
project-original and contributed under Unknown v0.3. No external content is
incorporated.

## Question and frozen boundary

Research 0204 showed that observation timeout is not negative evidence. Its
smallest continuation asks whether a verifier implementation failure can be
distinguished from a semantic counterexample without losing the object being
checked, the observation history or the unresolved complement.

The input is one exact finite snapshot and one producer receipt. A snapshot
contains a binary-word machine, the observed integer stage, its positive history,
the proposed complete domain and the unresolved finite syntax. Canonical JSON
digests bind the object, history and unresolved set separately. The receiver is
a checker, not a searcher. It accepts either:

1. a `semantic-candidate` naming one program and reveal stage; or
2. an `implementation-failure` naming a phase and one bounded failure code, with
   no semantic conclusion and no candidate.

The width-two primary instance is the previous machine

\[
  M=\{00\mapsto1,10\mapsto5\},
\]

observed at stage one under the false complete-domain proposal \(\{00\}\). The
fresh reuse is width three,

\[
  M'=\{000\mapsto2,110\mapsto7\},
\]

observed at stage two under the proposal \(\{000\}\). Exact types, fixtures,
acceptance conditions and limits are frozen in
`experiments/failure_kind_boundary/contract.json`. There is no candidate search.

Each child process permits at most 100,000 counted host operations, 30 seconds
wall time, 25 CPU seconds, 256 MiB address space and 1 MiB output. One primary
and one deterministic fresh-process replay are allowed.

## Result

For each family, three injected failures — unavailable load interface, exhausted
execution budget and internal serialization error — return
`ImplementationFailure`. Each result repeats exactly the input object digest,
history and history digest, unresolved set and unresolved digest. Its semantic
delta has no accepted or rejected program.

The delayed event is handled differently. The receiver checks that the word is
in the declared syntax, the stage is an exact nonnegative integer, the event
belongs to the same bound machine, it occurs after the observed stage, it is
outside the proposal and remains in the preserved unresolved set. The two valid
events, `10@5` and `110@7`, therefore return `Counterexample`. A repaired
continuation starts from the exact snapshot retained by each injected failure
and accepts the same independently checked witness.

The distinction is consequently evidence-directed rather than label-directed:
an implementation crash neither creates nor erases a semantic counterexample.
A valid witness may later refute the proposal, but the crash alone says nothing
about the proposal's truth.

Twenty negative controls are refused across the two families. They attempt to
relabel a failure as a counterexample, attach a semantic conclusion or candidate
to a failure, fabricate the event stage, reuse an already visible event, change
the object/history/unresolved binding, substitute a Boolean stage and use a
semantic result name as an implementation failure code.

The primary and replay each pass 48 counted assertions and use 342 counted host
work units. Their deterministic evidence is equal. No research run failed and
no correction replay was used.

## What the finite check establishes

Let \(S=(O,H,U)\) be the bound object, history and unresolved state. The receiver
accepts an implementation-failure receipt only when its three bindings equal
those of \(S\), its failure kind belongs to the declared finite grammar and it
contains no semantic claim. Its output carries the same \(S\) and an empty
semantic delta. Thus preservation follows directly by construction and is
checked in all six failure cases.

For a semantic candidate \((p,t)\), the receiver checks the finite conjunction

\[
 p\in U,\quad M(p)=t,\quad t>t_{\mathrm{observed}},\quad
 p\notin D_{\mathrm{proposed}}.
\]

Both retained candidates satisfy it. Every altered candidate used by the
controls fails at least one conjunct or one context binding. This is a finite
receiver argument for the declared carrier, not a theorem that arbitrary host
failures are detectable or that unrestricted semantic counterexamples are
decidable.

## Costs, replay and use

The primary child took about 33.22 ms and the replay about 37.46 ms; supervisor
wall time was about 71.61 ms. The two children used 684 counted work units in
total. The highest recorded child RSS high-water mark was 11,648 KiB (11.375
MiB), and supervisor RSS was 10,112 KiB. These are process high-water marks, not
incremental memory. Reading, authoring, source retrieval, network and repository
integration time are not measured.

Search cost is exactly zero candidates. Construction, receiver validation and
JSON serialization occur inside each child process but were not timed
independently; only their combined wall/CPU and counted-work totals above are
available. The width-three reuse likewise shares that run and has no separate
wall or memory measurement. The retained evidence exposes each result count but
does not justify allocating the aggregate time among those phases.

Python byte compilation, JSON parsing, TOML parsing, deterministic replay and
the staged whitespace check passed. The identified-withdrawal scanner checked
4,389 staged-tree blobs, 9,192 expanded members and 377,120,743 bytes and found
no withdrawn copy. Its additional `--history` mode did not finish in this
partial clone: lazy object retrieval lost its local network proxy after about
nine minutes and the run was stopped. The parent main already records a fresh-
clone check over all 184 branch refs before this contribution; that earlier
record is not restated as a check of the new commit. The new staged payload is
project-original and was covered by the completed staged-tree scan.

Reproduce into a new directory:

```console
timeout 65s python -B -S experiments/failure_kind_boundary/supervise.py \
  --output-dir /tmp/adva-failure-kind-new
```

For Mingli and later agents, this gives a checked status discipline: tool failure
keeps the question open and preserves the continuation point; it cannot be
reported as mathematical refutation. For Jiamin, the analogous potential value
is that a failed analysis does not silently remove an action or alternative from
the decision space. That practical value has not been tested.

No new word is needed. Existing `ImplementationFailure`, `Counterexample` and
`InvalidEvidence` outcomes already express the necessary separation. This does
not implement failure detection for arbitrary tools, a native Adva receiver,
`Close`, `free`, M6 filling, arithmetic universality, learning, acceleration or
social trust.

The smallest continuation is not another status name. It is an end-to-end
continuation receipt that binds a later successful check to the exact preserved
object/history/unresolved triple, so a retry cannot silently substitute a new
question.
