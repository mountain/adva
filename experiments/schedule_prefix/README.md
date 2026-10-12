# Enabled-prefix coverage without erasing schedule history

Date: 2026-10-12. Status: executed bounded comparison; no stable API or vocabulary
promotion. Codex (OpenAI), submitted through Mingli Yuan's authorized account
proxy, not his authorship, review or endorsement. Project-original contribution
under Unknown v0.3. Software dependencies retain their own licenses; only their
manifest/lock coordinates, not dependency source or binaries, are published.

## Question, dependencies and frozen scope

Research 0265 ended with an explicit next step: compare enabled-prefix coverage
with exhaustive permutation coverage on the same native diagrams before raising
the four-event bound. This report executes that step and adds one fresh reuse
instance of the same size: two independent two-event chains.

Inspected main: `mountain/adva@7a8fb500c32e414f170a780f5e5f93161ca76b2e`, including
merged PR #215's personal-library placement and public continuity records.
The sole open research PR found was #214 at
`f6dd486ca13ac7c8e8c149057fe9f5c5e73d8e36`; its CI 983, publication, machine
dependency and bootstrap checks had all passed, but it was still draft/unmerged.
That head, already containing main, is this experiment's base. The latest main
does not yet contain Research 0262–0265. The older source/cut/slice authority in
Rust is merged; the quotient-query gate and these calibrations are proposals.

Reviewed constraints: `AGENTS.md`, `PUBLICATION_BOUNDARY.md`, the knowledge/machine
boundary, `RESEARCH_ENGINEERING_AGENDA.md`, `claims.toml`, Research 0090/0092,
0123/0129 and 0262–0265. Their relevant source bytes did not change since the
preceding inspection. Research 0090's coverage prerequisite is used; 0092's
full-filler closure and vocabulary promotion are not inferred. Research 0123's
`arithmetic-universality` and `hypothesized-arithmetic-truth` remain hypotheses.
Exact finite node sets are the arithmetic domain here; additive-zero and
multiplicative-unit constructions are neither identified nor extended.

The [contract](contract.json), written before execution, freezes one route,
four specified diagrams, at most four native events, 24 permutations, 65 prefix
records, 20 process launches, 100,000 counted units, 10 seconds per runtime
process and 180 seconds for build. No hard memory cap is claimed. Input files
are capped at one MiB. Runtime counters exclude native internal instructions;
the finite grammar and supervisor timeout are separate bounds. Only one
implementation correction replay was available; none was used.

Inputs are exact diagram JSON and receiver-selected BLAKE3 bindings. The three
old diagrams are read from the unchanged
`mountain/adva@37cd7993b99bdc678a1af6d6f27f734c3d6bf5fa/experiments/schedule_receiving/evidence/attempt-1/bundle.json`.
The fresh diagram is compiled by Rust from the original two-chain module in
`src/main.rs`; its source and exported input are retained. These are trusted
fixture bindings, not proof of sender identity or consent.

## Construction, receiving and the finite argument

The depth-first producer records each legal **word prefix**, its canonical
completed cut and all enabled outgoing events with full Rust CausalStep
artifacts. It tests every unused event through `advance_causal_cut`.

A separate invocation runs a breadth-first receiver. After native diagram
import it rederives the cut and full outgoing step list at each reachable word
prefix. Missing records or a missing child block coverage; duplicated prefixes,
changed cuts/steps, wrong bindings and unreachable records are refused. Producer
telemetry is not used to justify acceptance. The receiver independently obtains
the complete legal-word set by the permutation baseline and compares exact sets.
The routines share the native Rust kernel and enabled-step helper; this is
separated traversal/control logic, not independent semantic-kernel validation.

**Coverage argument, conditional on the existing native DAG/step semantics.**
The root represents the empty legal word. At any legal prefix, its legal next
letters are exactly the unused enabled events. The receiver requires every one
and no different one, so induction on prefix length includes every legal word.
Each branch increases length by one; the finite DAG is exhausted after at most
its node count. Comparing complete words to full permutations is a second
finite oracle for the four declared diagrams. This is not a proof of universal
grammar, unbounded learning, global M6 closure or native `free`.

## Results: coverage succeeds; end-to-end speedup is not established

| Fixture | Events | Legal words | Prefix records | Baseline native attempts | Prefix producer attempts | Prefix verifier attempts |
|---|---:|---:|---:|---:|---:|---:|
| diamond | 3 | 2 | 7 | 12 | 9 | 9 |
| three independent | 3 | 6 | 16 | 18 | 15 | 15 |
| delayed diamond | 4 | 2 | 9 | 42 | 16 | 16 |
| fresh two chains | 4 | 6 | 19 | 50 | 24 | 24 |

All four exact word sets agree. Whole-fibre queries descend; first-event
queries retain an explicit `NonSaturated` pair in each case. The new two-chain
instance has six legal interleavings, rather than just the two block orders.

The counted unit is one native advance attempt, one prefix record visit or one
complete permutation candidate, with the components retained separately:

| Fixture | Permutation baseline units | Prefix construction + verification units | Construction ms | Prefix verification ms | Baseline ms |
|---|---:|---:|---:|---:|---:|
| diamond | 18 | 16 + 16 = 32 | 2.385 | 1.947 | 0.911 |
| three independent | 24 | 31 + 31 = 62 | 8.497 | 6.773 | 3.200 |
| delayed diamond | 66 | 25 + 25 = 50 | 3.018 | 2.592 | 2.540 |
| fresh two chains | 74 | 43 + 43 = 86 | 6.979 | 6.312 | 3.747 |

Both methods use the same diagrams, Rust authority, finite resource ceiling and
exact set-equality criterion. The proof-carrying tree additionally materializes
and compares full native step objects. Fewer enabledness probes alone therefore
do not establish a smaller full cost. Only one fixture reduces the declared
construction-plus-verification unit count. **None shows a construction-plus-
verification wall-time improvement in this run.** These are single fixed-order
measurements, not a randomized timing benchmark or an asymptotic conclusion.
The baseline timer runs on the already-imported diagram; the prefix receiver
timer includes its diagram import and receipt checks. Thus the timer columns
have explicit different preparation boundaries and are not an isolated data-
structure benchmark; no end-to-end speedup follows from their ratio.
The verified method's current implementation also executes the permutation
baseline for the comparison, so its actual campaign cost includes both columns.

## Counterexample: a shared state is not a disposable history

In the diamond, prefixes `[0,1]` and `[1,0]` have the same completed cut `[0,1]`.
Their full words `[0,1,2]` and `[1,0,2]` agree on the final ideal but disagree on
"event 0 happened first". Keeping just one record per completed cut loses one
of those histories. On its remaining singleton, every predicate would appear
constant, incorrectly suggesting descent for the original full question.

The deliberately lossy cut-dedup control retains only one complete word per
fixture, losing respectively **1, 5, 1 and 5** histories. Submitting the
collapsed diamond tree to the receiver yields `UnknownCoverage`, with a
concrete missing word prefix retained in the result.

This does not forbid sharing a state or caching its outgoing transitions.
A state DAG can retain all incoming paths and reconstruct all schedule words.
The invalid step is deleting route multiplicity merely because its present
state has an equal observation. State sharing and history erasure are different
operations; local image equality supplies neither path equality nor an M6 filler.

Eight frozen controls passed: missing edge, missing leaf and cut-dedup return
`UnknownCoverage`; wrong cut, altered step, duplicate prefix and unreachable
prefix return `InvalidEvidence`; a wrong tree binding returns `InvalidContext`.

## Evidence, total cost and reproduction

The sole campaign completed with 18 process launches (including build), 470
counted units across construction, verification, the permutation oracle and
controls, and no correction replay. Its 60 complete permutation candidates
are exhaustive finite coverage work, not a solver search for a theorem.

- build: 25.092 seconds, using an existing Cargo target cache and recompiling
  the path-dependent native crates; not a clean-build performance comparison;
- all runtime child wall times, including startup: 0.116096 seconds;
- supervisor JSON serialization/writes: 0.003380 seconds;
- total campaign wall time: 25.217713 seconds;
- maximum sampled native `VmHWM`: 5,536 KiB, read before final stdout encoding;
  final-output allocation is outside that sample;
- maximum child RSS including compilation: 483,300 KiB; supervisor: 12,544 KiB;
  these are separate high-water marks, not simultaneous aggregate memory.

Input decoding, diagram import, and in-process step serialization are included
in construction/verification timers but not individually split. The fresh Rust
module compilation costs are included in the `fresh` process measurement;
its internal instruction count is unmeasured. Human/AI authoring, source review,
network saving and archive audit are outside campaign timing. There is no claim
that file size measures peak memory. Exact outputs and per-process measurements
are in [execution.json](evidence/attempt-1/execution.json),
[results.json](evidence/attempt-1/results.json) and the surrounding 56-file
evidence directory. `manifest.json` covers every other file; `sources.json`
binds the five source/contract/lock files used for this campaign.

Reproduce from repository root with Python 3 and Rust/Cargo installed:

```sh
python experiments/schedule_prefix/run.py /tmp/adva-prefix-NEW
python tests/python/test_schedule_prefix_evidence.py
```

The output path must be new. A preexisting `CARGO_TARGET_DIR` is honored, and its
effect on build costs must be recorded. Direct interfaces after building are:

```sh
experiments/schedule_prefix/target/debug/schedule-prefix fresh
experiments/schedule_prefix/target/debug/schedule-prefix produce INPUT.json
experiments/schedule_prefix/target/debug/schedule-prefix verify INPUT.json TREE.json
```

`fresh` emits the new original diagram with its binding; `produce` emits the
complete tree and cost; `verify` emits acceptance/refusal, residual, exact legal
words, quotient counter-pairs and comparative costs. Use the supervisor for
timeouts and cumulative launch accounting. These host invocations are not a
new general Adva communication operation or an upgraded machine consumer lock.

## Vocabulary, use and next minimum step

New vocabulary: **zero**. This strengthens the coverage condition of the
already Proposed `quotient-query-gate`. It does not rename a known construction
as a learned theorem or claim social trust.

The result supports the intuition that generation can avoid many invalid
permutations. It does **not** support the stronger assumption that packaging
and independently receiving those witnesses is already cheaper. It helps Mingli
and later agents avoid deleting histories to obtain an attractive cost number.
Benefit for Jiamin's actual task remains unmeasured.

Next, on these same four small diagrams, test a checked state-DAG cache that
shares transition facts while preserving every incoming path. Require the same
word sets, counter-pairs and missing-branch refusals, and include cache formation,
receiving and expansion cost. Keep the four-event cap until that comparison is
complete. Shared-kernel defects, hostile-input hardening, authentication,
unbounded diagrams and general learner/closure claims remain open.
