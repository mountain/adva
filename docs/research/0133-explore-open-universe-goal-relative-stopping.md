# Research 0133: Explore, open, universe and goal-relative stopping

Status: external finite arithmetic calibration; proposed vocabulary organization.
No native language primitive, universal grammar or general acceleration claim.

## Origin and relation to prior work

On 2026-09-06 Mingli Yuan proposed turning the engineering orientation from
the stopping-oriented names `halt`, `null`, `empty` toward `explore`, `open`,
`universe`. The assistant proposed retaining the earlier distinctions internally
while testing different completion goals on one finite open equation. Mingli
authorized this calibration. The meanings below are operational proposals,
not a claim that the complete intended language has been recovered.

The inspected main was `57c1d04bcfe51b82f6e559a61ca02e668f630b5a`.
Drafts #130, #131 and #132 remained open, at heads
`f5357fff7fc1d93f1bfbaa184f26ac46b1f5da19`,
`834fcb88db886272234ec6d8b7c068db5d354a51`, and
`6e4052686f835991120fbcb4888b28553ec56ad2` respectively.
This is a self-contained branch from main, importing none of their code or
claim entries. Their experiments were not repeated.

Research 0090 and draft #130 motivate the distinction between finite evidence
and full coverage. Draft #132 supplies the familiar quadratic and the need to
retain alternatives across structural changes. Here the added question is
goal-dependent stopping: existence, complete enumeration, and uniqueness require
different evidence even on the same domain and equation. The scope remains
external under AGENTS.md and Research 0129. No stable semantics, M6 filler,
0092 word promotion or paused unknown-syntax-building inquiry is advanced.

The run contract was written before execution:
[`0133-goal-relative-exploration-contract.json`](0133-goal-relative-exploration-contract.json),
SHA-256 `5b4717c3f85847184b35a0115c2d546a4a0fc9ea2d7b206585ae6c3760771d7d`.

## The same open equation, three questions

Let U be the explicitly declared seven-element field F7, with canonical
representatives 0 through 6. The typed open position is x in

```text
h(x) = (2*x+0)*x+6
h(?) = 1
```

The model returns the value vector `[6,1,0,3,3,0,1]` on ascending inputs.
The solution set is `{1,6}`. It is deliberately a simple known equation;
there is no mathematical discovery or difficult synthesis claim.

| Goal | Statement / answer type | Sufficient evidence in this checker |
|---|---|---|
| exists | Is there an x satisfying the equation? Boolean | One witness for true; complete negative coverage for false |
| all | Return exactly the satisfying subset of U | Check every member of U; partial findings are not a complete set |
| unique | Is there exactly one satisfying x? Boolean | Two distinct witnesses for false; full coverage for true or for the zero-solution false case |

The checker admits explicit finite coverage, not alternative symbolic proofs.
Consequently, its seven-point requirement for some answers is a property of
this chosen proof interface, not a lower bound for every mathematical method.
For example, an algebraic uniqueness proof may avoid literal enumeration, but
would require its own admitted proof and scope rules.

The producer's execution stop is stored separately from the checked judgment.
Every call is finite; stopping due to fuel need not decide its question. Even
after a question is decided, unvisited positions remain recorded.

## Main results and scheduling distinction

Both policies use the same equation, ascending schedule, maximum fuel seven,
independent scalar checker and result format. The goal-aware policy stops at
the first existence witness or the second distinct uniqueness witness. The
exhaustive policy continues through the declared domain.

| Goal | Goal-aware evaluated inputs | Exhaustive evaluated inputs | Checked answer |
|---|---:|---:|---|
| exists | 2 | 7 | true, witness x=1 |
| all | 7 | 7 | [1,6] |
| unique | 7 | 7 | false, witnesses x=1 and x=6 |

After the two-point existence run, positions 2 through 6 remain unvisited,
including the other actual solution. Thus question completion does not imply
that the open position has only one possible filling.

A separate frozen schedule `[6,1,0,2,3,4,5]`, with fuel two, refutes uniqueness
after exactly two evaluations. The other five positions remain unvisited.
That is a complete answer to the uniqueness question, not a claim that all
solutions have been enumerated. Schedule changes can affect when sufficient
evidence appears without changing the universe or the mathematical answer.

## Unknown, missing and empty

Three main-equation runs use fuel two. Existence is verified, while complete
enumeration and uniqueness remain Unknown despite having found one solution.
A zero-fuel existence run has an empty discovered list but remains Unknown,
with the entire domain unvisited.

For the distinct equation `2*x^2+6=2`, all seven inputs are checked and none
satisfies it. The checked complete-set answer is `[]`; existence and uniqueness
are both false in this declared finite domain. This absence result comes from
the checker recomputing complete coverage, not from trusting raw search
exhaustion, elapsed time or a producer status.

Missing input is different again. A None equation is rejected with the external
label `MissingInput` before exploration starts. An omitted equation is not a
verified empty solution set. The JSON null used for an Unknown answer is also
interpreted with its explicit status and goal, not as a universal null object.

These cases give narrow working distinctions:

- `halt`: an actual finite execution stop, with its reason recorded;
- `null`: a possible missing-field representation whose meaning requires a type;
- `empty`: an empty specified collection, with a separate obligation if it is
  claimed to contain all solutions.

They are not removed or identified with the new three names.

## New-instance reuse and positive uniqueness

The same goal rules, evaluator and verifier are reused without changes for
`x^2+2*x+3=3`. Its solutions are `[0,5]`; ascending existence checks one input,
complete enumeration checks seven, and non-uniqueness checks six.

A positive-uniqueness control uses `x^2=0`. The witness at x=0 settles existence
after one input, but this checker verifies uniqueness only after all seven
inputs. A six-input version of that uniqueness query remains Unknown in the
targeted tests. There is no inference from one witness to uniqueness.

The generated artifact contains 20 fixed runs: the three goals on four equations,
three exhaustive main-equation controls, three fuel-two main-equation controls,
zero-fuel existence and the reordered two-witness uniqueness control.
This is a finite reuse test of supplied goal policies, not a learned general
stopping theorem or a universal exploration mechanism.

## Operational word contracts

| Word | Concrete role / input-output boundary | Conditions and refusal | Replay and residual |
|---|---|---|---|
| `explore` | A formed query, finite schedule and fuel -> visited rows, discoveries, stop reason and proposed judgment | Fixed admitted goal, canonical task and complete schedule declaration; invalid inputs rejected, inadequate evidence remains Unknown | Replay each visited value and derive the judgment; keep every unvisited position |
| `open` | The explicitly typed x-position in the declared equation | A filling must satisfy that equation in F7; a found filling does not establish uniqueness | Keep equation, type, goal and remaining positions; no identification of syntax holes with native apertures or logical Omega |
| `universe` | The explicit domain U against which coverage and quantifiers are read | Require exactly 0 through 6 in this fixture; reject omitted or duplicate schedule positions | Reconstruct coverage and preserve domain binding; this U is not the physical open world |

The new orientation is an interface proposal: explore an open question within
a declared universe and budget. It is not the pointwise renaming
`halt=explore`, `null=open`, `empty=universe`. No such equality is asserted.

`judge` reads the verified goal-specific evidence. `switch` or `reorganize` may
later change a schedule or view under an explicit contract; the reordered
fixture changes only the supplied schedule. `revise` can change the question,
but the old completion status cannot simply be copied to the new goal.
`word-formation` and `syntax-formation` remain proposed higher-level roles;
no new native primitive is introduced by these Python function names.

The three-domain reading remains provisional: time concerns finite exploration
and stopping, construction concerns the typed open equation and its fillings,
space concerns declared positions and coverage. These are interacting views,
not a proof of three intrinsic wire types or a physical three-world model.

## Checker boundary and tests

The producer uses nested Horner evaluation. The checker independently computes
expanded powers modulo seven, verifies the exact schedule prefix, distinct
positions, fuel, stopping policy, discoveries and unvisited positions, then
reconstructs the goal judgment. It does not trust the producer's verdict.
Canonical encoding distinguishes booleans from integers in evidence comparisons.

Within this finite specification, one checked positive row establishes
existence; two different positive input positions refute exact uniqueness;
and verified coverage permits counting all satisfying positions. These are
elementary scope-bound arguments. The Python interpreter and implementation
are not formally verified, and their hashes are not authentication or native
semantic identities.

Eight targeted tests replay the committed artifact and check:

1. exact outcomes and comparable candidate counts;
2. question completion while alternatives remain;
3. rejection of uniqueness inferred from one witness;
4. non-uniqueness from two distinct witnesses without full coverage;
5. verified empty answers versus zero-fuel Unknown and missing input;
6. positive uniqueness and an insufficient six-input prefix;
7. false complete answers, omitted rows, corrupted values and goal drift;
8. fresh-equation reuse and malformed domains/scalars.

All passed. There were no correction replays, broad repository test reruns or
CI-wait loops. The existing Python CI can collect these fixture-replay tests.
Process-wide limits are set only in the standalone CLI or the standalone test
harness, not by tests inside the shared pytest process.

All scalar zeros remain ordinary field values. No division is used. This
calibration supplies no native additive formation residual A, multiplicative
transport residual M, source/occurrence equality or M6 filler.

## Resource use and limited acceleration evidence

Standalone limits are five seconds CPU and wall time, 256 MiB address space,
128 KiB artifact size, 1,000 scalar evaluations/checks and 20,000 metadata
items. The outer command also has a five-second timeout. Every individual run
has at most seven candidate evaluations. There is no automatic continuation,
scope enlargement or fuel reset.

On Linux and Python 3.12.13:

| Measurement | Observed value |
|---|---:|
| Build including evaluation and initial verification | 1.817639 ms |
| Initial verification within build | 1.101834 ms |
| Serialization | 0.125174 ms |
| Parse | 0.103062 ms |
| Artifact replay | 1.224234 ms |
| Witness-file save | 0.201928 ms |
| Total measured elapsed | 3.601237 ms |
| Producer evaluations | 95 |
| Checker evaluations, initial verification plus replay | 190 |
| Metadata items | 1,185 |
| Main process peak RSS | 10,880 KiB (10.625 MiB) |
| Artifact size | 11,559 bytes |

The test harness including discovery took 4.371503 ms, with 6 producer and 112
checker evaluations, 553 metadata items and 13,952 KiB (13.625 MiB) peak RSS.
Main and test processes together performed 403 scalar evaluations/checks under
their separate limits. Counts are not machine-instruction counts. Build timing
nests its subphases; do not sum nested timings.

The two-versus-seven existence comparison demonstrates fewer evaluations under
the frozen policy and budget. It does not establish a novel speedup: ordinary
early-stopping code can do exactly this, and an algebraic solver may use another
proof interface. In this one-shot run, the goal-aware main existence call took
0.082893 ms while the exhaustive call took 0.026189 ms. No elapsed-time benefit
was observed for that comparison; call order and fixed overhead were not
controlled as a benchmark. No optimality or portable timing conclusion follows.

Reported timings exclude imports, interpreter startup, design, source retrieval,
network persistence and cost-report writing. They include task construction
inside the measured build, goal-policy execution, verification and witness
handling. Human naming effort, physical energy and customer-use value were not
measured. Artifact size is not peak memory. Hard process interruption may leave
no checkpoint or output; only the observed candidate-fuel records were saved
and replayed.

## Reproduction and next step

From the repository root, Linux with Python 3.11 or later:

```console
timeout 5s python -m experiments.goal_exploration.calibration --check examples/verified_witness/goal-exploration-f7.json
timeout 5s python -m experiments.goal_exploration.calibration --output /tmp/goal-exploration-f7.json --cost-output /tmp/goal-exploration-f7-cost.json
timeout 5s python -m unittest discover -s tests/python -p test_goal_exploration.py -v
```

Witness SHA-256:
`e5148db4d2ae975122ca492663faf9cbe68bac03002ee85a059e3c9b57c0efdb`.

Artifacts:

- `experiments/goal_exploration/calibration.py`
- `tests/python/test_goal_exploration.py`
- `examples/verified_witness/goal-exploration-f7.json`
- `examples/verified_witness/goal-exploration-f7-cost.json`
- `examples/verified_witness/goal-exploration-f7-validation.json`

This helps Mingli and subsequent agents distinguish what question has been
answered from whether a run halted, an input is missing, a result is empty,
or alternative fillings remain. It supplies no validation of Jiamin's concrete
use case or the whole vocabulary's completeness.

The next smallest continuation is a goal revision from verified existence to
complete enumeration: retain the already checked observations, reopen the new
goal, and investigate avoiding duplicate evaluation without inheriting the old
completion status. This fixture does not yet implement such incremental reuse.
It can be studied without another vocabulary word or a harder arithmetic task.
