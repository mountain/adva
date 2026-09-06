# Research 0134: Three engineering turns, revision, and local close

Status: external bounded experiment and proposed vocabulary calibration,
2026-09-06. Requested by Mingli Yuan; the assistant supplied the finite model,
implementation and checks. No native operation or general grammar theorem.

## Question and repository boundary

Can an observer revise an already answered existence question into a
nonuniqueness question, reuse a checked observation, traverse specification,
syntax and interpretation, and close only the new obligation?

The fixed base is `57c1d04bcfe51b82f6e559a61ca02e668f630b5a`. At preflight,
PRs #130, #131, #132 and #133 were open drafts, not merged results. This note
follows their discussion but imports no code or native certificates from them.
Research 0129 and the research agenda govern the run. Native semantic changes,
intrinsic compilation, general observer specialization and self-application
remain subject to their existing dependencies.

Research 0132 distinguishes evidence from its applicability to a changed
task. Research 0133 distinguishes goal-relative stopping from complete
enumeration. This experiment adds a concrete nine-instruction lowering,
compiler conformance checks, a revised-goal continuation receipt, and a
three-turn counterexample to unconditional closure. It does not repeat their
full experiment families. Old observations are reconstructed and charged in
this standalone fixture; they are not imported or authenticated PR #133
certificates.

The frozen input is [0134-three-turn-revise-contract.json](0134-three-turn-revise-contract.json).
Its SHA256 is
`e88d4ce8730d269cd3e3ee2677db1335fcb6ed52c15214a7d9fea45cf9f112b2`.
The contract was saved before any trial execution.

## A typed, deliberately small engineering triangle

The source form is an exact coefficient triple over F7:

`[a,b,c]` denotes `a*x*x+b*x+c (mod 7)`.

The external compiler lowers it to exactly nine stack instructions:

`CONST a; X; MUL; CONST b; ADD; X; MUL; CONST c; ADD`.

The stack interpreter computes `(a*x+b)*x+c (mod 7)`. The independent
scalar oracle uses expanded powers. All seven source/target outputs must
agree in this checker, even when the observation task needs only two inputs.
This is a small external compiler/interpreter calibration, not an Adva
program or a native tagged-data, case/fold or recursive evaluator.

| Turn | Boundary | Changed | Preserved | Remaining obligation |
| --- | --- | --- | --- | --- |
| 1 | specification to syntax | exists v1 becomes nonunique v2; expanded syntax becomes stack syntax | arithmetic domain, polynomial, old existence claim | compilation conformance, imported observation validity, new goal judgment |
| 2 | syntax to interpretation | explicitly budgeted continuation observations | v2 binding and old history | evaluate the new goal from accepted observations |
| 3 | interpretation to specification | knowledge and prescribed next action | old truth and unvisited positions | second witness if missing; otherwise none for this goal |

These are engineering roles, not equalities between compilation/syntax,
interpretation/semantics and specification/pragmatics. Formal specification
does not itself verify human intent, institutional acceptance or physical
appropriateness. The receipt's labels are descriptive external strings, not
SourceId, OccurrenceId, native process identities or authenticated provenance.

## Frozen arithmetic and outcomes

The original question is `exists x in F7: f(x)=rhs`. The revised question is
`exists distinct x,y in F7: f(x)=f(y)=rhs`. There is no complete-enumeration
goal in this run. `continue` names the bounded action, not a quantifier.

| Case | Old checked observation | New observations | Revised result | Residual |
| --- | --- | --- | --- | --- |
| main: `2*x*x+6=1` | `f(1)=1` | `f(6)=1` | Close: nonuniqueness True | five unvisited positions |
| fresh: `x*x+2*x+3=3` | `f(0)=3` | `f(5)=3` | Close: nonuniqueness True | five unvisited positions |
| main, zero fuel | `f(1)=1` | none | Unknown | second distinct witness; schedule `[6]` |
| main, nonwitness | `f(1)=1` | `f(2)=0` | Unknown | second distinct witness; scheduled portion exhausted |
| main, one unit over `[2,6]` | `f(1)=1` | `f(2)=0` | Unknown | cursor 1; remaining schedule `[6]` |

Two additional frozen ordinary uncached baselines compute both old and new
witness positions from scratch. There are seven records in total. Schedules
are externally supplied test inputs, not discovered policies or an optimal
search order. No continuation is automatically launched from a residual.

Every record has exactly three turns and returns to the specification role.
Four records close their revised goal; three remain Unknown. In every record
v1 and v2 are different specifications. Thus phase return does not imply
state identity or local close. A single old existence witness never supports
the new nonuniqueness verdict on its own.

The elementary conditional argument is explicit: compiler conformance gives
`VM(code,z)=f(z)` on the declared domain. Verified distinct observations x,y
with values rhs therefore establish the revised existential statement. This
is ordinary scoped arithmetic reasoning, not a novel theorem. The full-domain
compiler check is sufficient here, not a claim that all possible correct
compilers must prove conformance by enumeration.

## Proposed words and their operational boundaries

| Word | Input and output | Admission / witness | Rejection or residual |
| --- | --- | --- | --- |
| `revise` | old specification and evidence to new version plus applicability obligations | explicit unchanged arithmetic scope and v1/v2 distinction | changed polynomial/domain or stale completion fails this fixture's checker; a more general revision is not implemented |
| `continue` | retained observations, finite order and new fuel to additional observations, cursor and stop reason | exact schedule prefix, charged work, checked scalar values | fuel or schedule exhaustion leaves the second-witness obligation Unknown |
| `learn` | checked observations and a goal to updated judgment and prescribed next action | two distinct witnesses change Unknown to True and cancel further uniqueness testing | a nonwitness only updates the frontier; no theorem or general rule is learned |
| `close` | a versioned question and checked sufficient evidence to local completion | only the v2 nonuniqueness goal is closed here | three turn labels, v1 Close, duplicate witnesses or missing evidence cannot close v2 |

All words remain Proposed as general engineering vocabulary. There is a
concrete external calibration for these narrow roles, not native commands.
The fresh instance reuses the same recipe. Expansion and replay are given
below. Each receipt explicitly records changed, preserved, inapplicable and
owed fields, and retains both question versions.

**Critical observation boundary:** the compiler verifier sees all seven
function values and can itself solve the finite equation. The learner's
separate observation table is an imposed interface restriction; the complete
artifact also exposes the compiler rows. Consequently this is a test of
evidence routing and task-relative judgment, not evidence that the whole
system acquired information absent from its earlier computation. No hidden
information security or intrinsic world-structure learning is claimed.

The `learn` action policy is supplied by the author. It produces a next-action
record but does not execute a scheduler. Pending `[2,6]` retains a cursor for
later work; this run does not implement a general persistent resume API.

## Independent checks and correction

The producer uses a stack VM. The checker independently computes polynomial
values by expanded powers; it checks code shape without calling the compiler,
executes the target on every domain value, and independently derives the
goal verdict. Compiler rows do not by themselves authorize the VM.

Receipt-label assembly is shared between producer and checker. Independence
therefore concerns scalar meaning and goal judgment, not two independently
implemented protocol state machines. Python arithmetic, JSON and the small
checker are trusted host infrastructure; no Rust semantic certificate is
created. Source/target value agreement never identifies their histories.

Eight targeted tests cover replay and fresh reuse, equal-length cycles with
different outcomes, stale goal completion, changed scope, mutated compiler,
incomplete compilation coverage, changed history, duplicate witnesses,
altered scalar values, false fuel/cursors, false learner actions and deleted
residuals. Boolean field inputs are rejected.

Initial construction and all eight tests passed. Review then identified that
Python's `False == 0` / `True == 1` could admit falsely typed frontier entries
or query fuel metadata. One correction strengthened these boundaries and
added controls; one correction build/replay and test pass followed. The
arithmetic witness bytes and hash remained unchanged. No additional repair
or search route was attempted.

## Costs and enforceable limits

Each standalone process is limited to 5 seconds wall/CPU, 256 MiB address
space, 2,000 charged scalar evaluations/checks, 30,000 metadata checks and a
128 KiB artifact. Each record visits at most two new candidates. Fixed loops,
cooperative checks, process resource limits, an alarm and outer `timeout`
enforce these bounds. Unit tests do not install global limits on import;
their recorded standalone harness did install the same process limits.
Hard interruption can prevent a checkpoint and is not reported as success.

| Final measured item | Cost |
| --- | --- |
| construction plus initial verification | 0.890192 ms |
| serialization | 0.115150 ms |
| parse | 0.110693 ms |
| replay verification | 0.609338 ms |
| witness write | 0.099336 ms |
| main total including intervening bookkeeping | 1.865990 ms |
| main scalar work | 64 producer evaluations + 226 checker evaluations/checks |
| main metadata checks | 865 |
| main peak process RSS | 11,008 KiB = 10.75 MiB |
| targeted tests, including discovery | 8.132855 ms; 8 passed |
| test work | 426 checker evaluations/checks; 1,690 metadata checks |
| test peak process RSS | 14,200 KiB = 13.8671875 MiB |

Including the initial run and the one correction, recorded main/test work
totals 1,416 scalar evaluations/checks and 17.923512 ms. These are separate
bounded processes, not one merged measurement. The prior measurements are
retained in the validation artifact. Imports/startup, research, coding,
network and cost-report writes are excluded. Peak RSS is a Linux process
measurement, not artifact size. Research and publication wall time is not
instrumented by this harness and is not part of the millisecond totals.

The paired cached run executes one new candidate; the ordinary baseline
executes two under the same two-observation total ceiling. Both construct
the old observation and check compilation and witnesses, so this is not
free precomputation. Main cached/uncached build-and-check times were
0.149961/0.094188 ms; fresh were 0.325620/0.090183 ms. These are single-shot
measurements and include verification. Ordinary caching can achieve the same
candidate-count reduction. No elapsed-time gain, novel acceleration or
expression-power increase is demonstrated; naming and verification costs
are included rather than amortized away.

## Reproduction and evidence

From repository root, with Python 3.11 or later:

```sh
timeout 5s python -m experiments.revise_cycle.calibration --check examples/verified_witness/three-turn-revise-f7.json
timeout 5s python -m experiments.revise_cycle.calibration --output /tmp/three-turn-revise-f7.json --cost-output /tmp/three-turn-revise-f7-cost.json
timeout 5s python -m unittest discover -s tests/python -p test_revise_cycle.py -v
```

Canonical witness: `examples/verified_witness/three-turn-revise-f7.json`,
11,952 bytes, SHA256
`17f528489aace95984db2121190f5b9735a9bbd5670289653e45f8e91cf91814`.
Cost and validation records have the same prefix with `-cost.json` and
`-validation.json`. The local workspace was an exported subset of the repo;
the full Rust/Python suite was not run and CI status was not observed.

## Residuals and next handoff

The result supports conditional local close after a checked three-turn
process, and refutes turn-count-only closure in this finite model. It does
not prove a three-turn identity law. `I` and the user's proposed duality with
`identity` remain unassigned here. The agenda already uses I as a conventional
interpreter symbol; that usage does not establish the proposed duality.

There is no physical interpretation, M6 filler, interpreter self-application,
universal grammar completeness, new syntax formation, native A=0 or M=1
claim. No division occurs; zero is an ordinary external field value, not a
bridge to the native ZeroFault rules. `unknown-syntax-building` stays paused.

This helps Mingli and subsequent agents distinguish a completed route from
a completed obligation, and gives implementers a reviewable boundary for
reusing evidence after a goal change. Actual usefulness to Jiamin's work,
social trust and institutional requirements have not been measured.

Next minimal step: specify the observation interface for I, and explicitly
choose which equality `identity` would denote. Then test a round trip that
preserves observed values while retaining a changed history. Do not enlarge
the grammar or assert a duality before this choice is made.
