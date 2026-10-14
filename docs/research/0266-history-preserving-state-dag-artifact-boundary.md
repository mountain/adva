# Research 0266: history-preserving state-DAG artifact boundary

Date: 2026-10-13. Status: bounded artifact-level result; native receiver remains
Unknown. Codex (OpenAI), submitted through Mingli Yuan's authorized account
proxy, not his authorship, review or endorsement. Project-original contribution
under Unknown v0.3.

## Frozen question and dependency state

Research 0265 and the later enabled-prefix comparison left one narrow question:
can equal exact completed cuts share transition facts without deleting the
distinct schedule histories that reach them? This round freezes the same four
diagrams, their exact `NodeId` words, cuts and serialized causal steps, at most
four events, 24 terminal paths, 17 states, one MiB per input and 100,000 counted
units. The candidate grammar is one transition record per exact cut plus **all**
labelled root-to-terminal paths through the resulting DAG. Success requires the
same complete word sets, the same first-event counter-pairs, and refusal of
missing or changed coverage.

Inspected main was `7a8fb500c32e414f170a780f5e5f93161ca76b2e`, including
merged PR #215. Draft PR #214 at
`8a41d515da0275ef8a716ccac1b1b92a080e0c8a` was the only open PR and contained
Research 0262--0265 plus the enabled-prefix comparison; those results are not
yet on main. Its Rust, Python 3.11/3.12, publication, machine-dependency and
bootstrap jobs passed. Python 3.13 failed when an older continuation Node
receiver exceeded its five-second test timeout; that log did not implicate this
research package, so it was neither reclassified as mathematics nor used to
justify a rerun.

The dependency reading remains unchanged. Research 0090 requires complete
coverage before closure; this experiment starts only from the frozen complete
prefix receipts. It does not satisfy Research 0092's global filler requirement.
Research 0123's `arithmetic-universality` and
`hypothesized-arithmetic-truth` remain hypotheses. No additive-zero,
multiplicative-unit, invertibility, noncommutative order or M6 claim is changed.

The pre-execution [contract](../../experiments/schedule_state_dag/contract.json)
also froze a Rust producer/receiver. The current host contained Python but no
Rust compiler or Cargo executable. Two failed tool-discovery commands did no
mathematical work. Rather than fabricate native output, the run narrowed to a
second route: fold the already Rust-verified complete prefix receipts and check
the resulting artifact with separately invoked Python logic. The Rust source is
retained as an **unexecuted proposal**, not evidence.

## Finite construction and argument

For every prefix record, the artifact constructor uses its exact completed cut
as a state key and copies each enabled edge's event, next completed cut and full
serialized causal step. If two prefixes have the same cut, their complete edge
lists must agree byte-for-byte after canonical JSON encoding; disagreement is
an implementation obstruction. The receiver independently derives the expected
state projection from the complete prefix receipt, checks exact binding and
coverage, then enumerates every labelled root-to-terminal path in the state DAG.

The finite preservation argument is elementary but useful. Map a legal prefix
to the path obtained by reading its event labels from the empty cut. Every
enabled edge is retained, so induction on prefix length gives a path for every
legal prefix. Conversely every stored edge came from a verified enabled prefix
edge, so every labelled path is legal. Merging endpoints with equal cuts does
not merge the paths that reach them. Thus complete words are in bijection with
labelled root-to-terminal paths, conditional on the frozen prefix receipt and
its earlier native checking. This is not an independent proof of the native
step semantics.

## Result: storage shares; full receiving does not yet become cheaper

| Fixture | Prefix records | DAG states | State reduction | Legal words | Formation units | Artifact receiving units | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| diamond | 7 | 5 | 2 | 2 | 13 | 30 | 43 |
| three independent | 16 | 8 | 8 | 6 | 31 | 67 | 98 |
| delayed diamond | 9 | 6 | 3 | 2 | 17 | 38 | 55 |
| two independent chains | 19 | 9 | 10 | 6 | 37 | 77 | 114 |

All four reconstructed word sets equal the earlier complete prefix results:
`2, 6, 2, 6`. In particular, the two diamond orders and all six interleavings of
the two chains remain present after state sharing. The first-event query therefore
retains a `NonSaturated` pair, while the whole-fibre query still descends.

The result separates storage from receiving cost. State records fall by
`2, 8, 3, 10`, but this receiver must reread the complete prefix reference,
compare every DAG state and edge, and expand every path. Its formation plus
receiving totals are `43, 98, 55, 114` units. The earlier native prefix
construction plus receiving totals were `32, 62, 50, 86`. Under these declared
units, **none** of the four artifact-level state-DAG totals is smaller. A lower
state count is therefore not evidence of lower end-to-end verification cost.

Six controls passed. Removing an edge or reachable state returns
`UnknownCoverage`; changing a next cut, duplicating a state or adding an
unreachable state returns `InvalidEvidence`; changing the diagram binding
returns `InvalidContext`. Missing material never becomes a negative theorem or
a closure certificate.

## Costs, correction and replay

The first artifact execution classified all ten cases correctly but omitted a
summed-unit field on early refusal paths. Its complete output is retained under
`evidence/prior-telemetry-incomplete`. One permitted implementation correction
added the total before every return and replayed the identical cases; no
mathematical classification changed.

The corrected run used 424 counted artifact units: 310 across the four valid
formation/receiving pairs and 114 across six controls. Including the retained
first run gives 848 reconstructed units. The first and corrected runs took
0.007480 and 0.012934 seconds respectively. Corrected supervisor peak RSS was
10,496 KiB; no child processes were launched. JSON serialization was included
in wall time but not separately timed. Native internal work, Rust build cost and
native receiver memory are missing because that route did not execute. There
was no candidate search.

Exact corrected outputs are in
[`evidence/attempt-1`](../../experiments/schedule_state_dag/evidence/attempt-1),
including four canonical DAGs, per-case counters, source hashes and a complete
manifest. Reproduce the artifact result from repository root with:

```sh
python experiments/schedule_state_dag/analyze.py /tmp/adva-state-dag-NEW
python tests/python/test_schedule_state_dag_evidence.py
```

The unexecuted native route is declared by `Cargo.toml`, `src/main.rs` and
`run.py`. In an environment with Rust/Cargo it is intended to run as:

```sh
python experiments/schedule_state_dag/run.py /tmp/adva-state-dag-native-NEW
```

Until that command produces and independently receives native evidence, its
status is `Unknown`, not failed mathematics and not successful validation.

## Vocabulary, use and residual

New vocabulary: **zero**. “History-preserving state DAG” is a descriptive name
for this standard finite construction, not a promoted Adva word. Existing
coverage, obstruction and quotient-query language already states the boundary.

This helps Mingli and later agents share exact transition facts without
mistaking an equal present cut for an equal history. It also prevents an
attractive storage reduction from being reported as a solver or verifier
speedup. Jiamin's real-task benefit remains unmeasured.

The smallest continuation is now fixed: run the retained native receiver on
the same four inputs, require the same state counts, word sets, counter-pairs
and six refusal classes, and compare native transition revalidation plus path
expansion against the old prefix receiver. Do not raise the four-event bound.
Shared-kernel defects, malicious inputs, authentication, arbitrary diagrams,
global M6 closure, native `free` and universal grammar remain open.
