# Research 0265: receiving schedule fibres with complete coverage

Date: 2026-10-12. Status: bounded executed research, not a stable API.
Authored by Codex (OpenAI), through Mingli Yuan's authorized account proxy;
not his technical review or endorsement. Project-original, Unknown v0.3.

## Question and dependency boundary

Can another process recover the Research 0264 quotient judgment from archived
native diagrams, slices and schedule steps, without compiling the source again?
The additional obligation is coverage: receiving some valid schedules cannot
establish that the query descends on **all** legal schedules.

Main was `1b9bd090b2c4710916b6a0ccca0ad88fb7d323bd`; the inspected and extended
draft PR #214 was `56e3fbc1bc36835c9174b69e3fe079bd8944b935`. Research 0262's
finite-set proof and 0263/0264 native calibrations remain unmerged proposals
at this checkpoint. Research 0123's arithmetic-universality and
hypothesized-arithmetic-truth remain hypotheses. No arithmetic field, additive
zero, multiplicative unit, identity contraction or M6 filler is introduced.

This follows Research 0090's coverage discipline and the agenda's exact-slice
dependency. It supplies no Research 0092 vocabulary-promotion or full-filler
closure. The fixed communication and kernel/package boundary documents remain
documentary constraints; this is not execution of general native `communicate`.

The frozen [contract](../../experiments/schedule_receiving/contract.json)
selects one route, three fixtures, 1–4 events, at most 24 permutations per
receive, 16 receiver launches, 100,000 counted units, 10 seconds and 256 MiB
address space per runtime child, and at most one implementation correction.
Compilation has a separate 240-second timeout and no memory cap. The arithmetic
domain is exact finite sets of native NodeId values; query grammar is only
`all` and `first(event)`. No optimization or unbounded search is attempted.

## Receiving procedure

The research-local Rust producer compiles three original functions once and
exports the full diagram JSON, the certified whole ProgramSlice, and every
schedule's word, full CausalStep artifacts and final ideal. The fresh reuse
fixture adds a final negation after the diamond's join, hence four events.

The separate Rust receiver has no parser/linker/compiler call. It:

1. checks the caller-selected diagram-byte and canonical-slice BLAKE3 bindings;
2. calls `import_diagram_json`, retaining the existing semantic authority;
3. rederives and compares the **entire** whole-slice artifact;
4. advances each supplied word and compares every full step, including its
   certificate and both frontiers, before accepting its final ideal;
5. enumerates every permutation of this diagram's nodes, checks enabledness
   through Rust, and compares the complete legal set with the supplied words;
6. evaluates the caller's query only after that coverage equality succeeds.

A successful certificate string is never accepted by itself. Candidate JSON
does not allocate a new source, occurrence or history. All native judgments
are rederived by the existing Rust kernel. The producer and receiver share
that kernel: separation of processes and generation logic is **not** an
independent implementation of native semantics.

The input request is an external expectation supplied by the receiving caller.
The campaign derives its original expectations from the producer; this is a
trusted fixture experiment, not authentication of an adversarial producer.
Changing both the caller's contract and the archive changes the question.
Hashes give exact bindings, not authorship, consent or physical meaning.

## Results

| Fixture | Events | Legal schedules | Permutations checked per complete receive | `all` | `first(event)` |
|---|---:|---:|---:|---|---|
| diamond | 3 | 2 | 6 | Descends | NonSaturated |
| three independent | 3 | 6 | 6 | Descends | NonSaturated |
| delayed diamond, new reuse | 4 | 2 | 24 | Descends | NonSaturated |

For each obstruction, the retained pair has the same final ideal but different
first events; both full native paths are archived. The eight controls return:

| Changed input | Outcome |
|---|---|
| another valid diagram under the original expectation | InvalidContext |
| another whole slice | InvalidContext |
| changed intermediate completed cut | InvalidEvidence |
| reversed word with unchanged steps | InvalidEvidence |
| omitted second diamond schedule | UnknownCoverage |
| duplicated schedule | InvalidEvidence |
| changed final ideal | InvalidEvidence |
| unsupported query grammar | InvalidEvidence |

The omission is the important distinction. A one-element supplied family makes
every predicate appear constant if tested only on that family. The receiver
finds the missing legal word and refuses to close the quotient judgment.
This is complete coverage only for the admitted fixed diagrams, not for
unseen diagrams, unrestricted process histories or future observations.

No new word is needed. The Proposed `quotient-query-gate` is reused with an
explicit coverage precondition. There is no increased-expressivity or speedup
claim, no learned theorem and no practical-use claim for Jiamin.

## Costs and replay

The single campaign passed without an implementation correction replay:

- 14 receiver processes, one producer, one build invocation;
- 10 constructed receipts and 32 producer causal advances;
- 363 receiver work units (candidate permutations, attempted native advances,
  and query-pair comparisons; not internal kernel operations or CPU ticks);
- 44.788 seconds building, 0.02355 seconds producer process;
- 0.08938 seconds summed receiving processes, including startup;
- producer construction timers: 2.224 ms diamond, 7.766 ms independent-three,
  2.597 ms fresh delayed reuse (includes in-process object serialization);
- 7.140 ms supervisor JSON serialization/write time;
- 44.914 seconds total campaign wall time;
- 485,432 KiB maximum child RSS **including compilation**, not concurrent
  aggregate memory; 12,160 KiB supervisor RSS. Individual receiver peak RSS
  was not separately measured. File size is not used as memory evidence.

Toolchain installation, source reading, authoring, index repair and network
publication are outside campaign telemetry. Their complete timings are missing.
Rust formatting after execution changed presentation only; no second campaign
was launched. The package lock records dependency versions, without vendoring
their source or reassigning their licenses.

From repository root, with Rust/Cargo and Python available:

```sh
python experiments/schedule_receiving/run.py /tmp/adva-schedule-receive-NEW
python tests/python/test_schedule_receiving_evidence.py
```

The destination must be new. The supervisor preserves exact requests,
candidate archives, stdout, stderr, costs, outcomes and SHA-256 inventory in
[`evidence/attempt-1`](../../experiments/schedule_receiving/evidence/attempt-1/).
The receiver can also be invoked directly after building the separate package:

```sh
experiments/schedule_receiving/target/debug/receive ARCHIVE.json REQUEST.json
```

Use the supervisor for enforced runtime limits. The direct CLI has a one-MiB
input-file check and four-node profile cap, but no host wall-clock/address-space
limit of its own. The counter does not measure every decoder/kernel operation;
the time/address-space limits remain separate protections on trusted local files.

## Explicit corrections to the prior round

Research 0264 at the inspected head reported 22 advances, counting four for
the diamond. Its two words each contain **three** events, so the correct count
is **6 + 18 = 24**. This arithmetic correction does not change its 88 query
comparison units. The historical numbered note remains preserved.

The same head truncated `docs/research/README.md` after roughly 520 lines.
CI run 38147871974 had 17 failing Python index checks; its Rust job passed.
This continuation restores the complete index from the main Git object and
adds back 0262–0265. Eight complete-index checks and the 14 affected note/index
regression functions passed locally; this is not a rerun of the whole Python
suite. Missing `pytest` was handled by calling those plain test functions
directly. The previous CI failure remains visible rather than being described
as a passed integration.

## Residual and next minimum step

This helps Mingli and subsequent agents send a finite schedule question to a
new process without silently replacing a complete fibre by a convenient sample.
It provides a replayable counter-pair rather than identifying the two histories.
Its usefulness to Jiamin's actual decisions remains unmeasured.

Shared-kernel defects, parser behavior on arbitrary hostile bytes, authentication,
graft-provenance reconstruction and diagrams above four events remain outside
the executed result. The next minimum step is to replace factorial permutation
enumeration with a checked enabled-prefix tree on **these same three diagrams**,
compare the exact legal-word sets and total formation/checking costs, and refuse
any missing branch. Do not increase the event bound before this comparison.
