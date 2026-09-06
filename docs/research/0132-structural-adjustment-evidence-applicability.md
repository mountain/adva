# Research 0132: Structural adjustment and evidence applicability

Status: external finite arithmetic calibration; proposed working meanings for
`switch`, `reorganize`, `revise`, and `judge`. No native semantic operation or
general language-completeness claim.

## Origin and scope

On 2026-09-06 Mingli Yuan corrected the earlier compression of `switch` into
`judge`: a finite learner needs words for structural adjustment as well as
judgment. He requested execution of a small F7 calibration connecting those
adjustments to evidence reuse and revision. The operational definitions and
implementation below were constructed by the assistant in response.

The inspected main was `57c1d04bcfe51b82f6e559a61ca02e668f630b5a`.
Open drafts were #130 (`f5357fff7fc1d93f1bfbaa184f26ac46b1f5da19`) and
#131 (`834fcb88db886272234ec6d8b7c068db5d354a51`). This change branches from
main, reads their recorded boundaries, and imports neither draft's code nor
claim entries. Research 0131 supplies the motivating arithmetic example;
the present fixture is self-contained and does not rerun its search.

Research 0118 already implements local closure transport and challenge
propagation in a different Rust research carrier. This note does not rediscover
that capability. Its added calibration is the explicit difference between
coordinate transport of an observation, expression reorganization, and a
changed target value, with a pending-versus-committed adjustment boundary.
The independent scope follows AGENTS.md, the research agenda and Research 0129.
The paused unknown-syntax-building inquiry remains paused. Arithmetic universality,
the opposite hypothesized arithmetic truth, general M6 coherence, native
specialization and 0092 vocabulary promotion remain open.

The pre-execution contract is
[`0132-structural-adjustment-run-contract.json`](0132-structural-adjustment-run-contract.json),
SHA-256 `a26b331839a7788bc5eee4b70bfb308a286549cd6c6fcc5b1f3d42f9031d4feb`.

## Frozen question

Can an externally supplied finite adjustment recipe retain an old true
observation, relocate it when coordinates change, retain its value under an
equivalent reorganization, and refuse its unchanged use for a revised target?
Can insufficient verification fuel leave the active state unchanged?

All scalars and input coordinates are canonical elements of F7. For one
coefficient triple and parameters s,d, with d nonzero, use

```text
f(x) = a*x^2 + b*x + c
h(x) = f(x+s)
e(x) = a*x^2 + (2*a*s+b)*x + (a*s^2+b*s+c)
k(x) = e(x)+d
```

The recipe is supplied, not discovered. There is no search. Each instance
checks all seven values in each of three relations:

1. the input-coordinate relation between f and h;
2. equality of the shifted expression and e;
3. the difference d between e and the revised target k.

There are also three scalar-observation rows: the source observation, a
blind-copy control, and a stale-value control. Thus each full instance has
exactly 24 obligations. The first observation is f(0)=c. Since -s+s=0 in F7,
the transported observation is h(-s)=c. Reorganization preserves e(-s)=c.
Revision requires a new statement k(-s)=c+d, rather than copying c.

This is a finite elementary consequence of substitution and distributivity.
It needs no manifold, physical theory, general inverse-program procedure or
new logical axiom. The coordinate translation here is bijective. No analogous
invertibility is asserted for arbitrary switches or revisions.

## Main witness

Choose (a,b,c)=(2,3,1), s=1 and d=1.

| Stage | Expression / observation | Evidence applicability |
|---|---|---|
| Source | f(0)=1 | True in the source task |
| switch | h(x)=f(x+1), h(6)=1 | Transport the coordinate 0 to 6 |
| reorganize | e(x)=2*x^2+6, e(6)=1 | Same scalar value, distinct expression record |
| revise | k(x)=2*x^2, k(6)=2 | New target and newly derived observation |

Two retained negative controls distinguish applicability from truth:

- Blind copying f(0)=1 into h(0)=1 fails: h(0)=6.
- Copying e(6)=1 into k(6)=1 fails: k(6)=2.

Neither failure makes f(0)=1 or e(6)=1 false in its original task. All old
observations and the ordered history remain. The receipt records four
distinct task/expression content coordinates and appends the three adjustment
events. Such hashes are external record references, not native occurrence
identities, provenance authentication or geometric cells.

## Fresh-instance reuse

The second instance uses (a,b,c)=(1,2,3), s=2 and d=2 with the identical recipe
digest and unmodified implementation. It produces

```text
f(0)=3
h(5)=3
e(x)=x^2+6*x+4, e(5)=3
k(x)=x^2+6*x+6, k(5)=5
```

The blind copy to h(0)=3 is refuted by h(0)=4; copying the old value 3 to k(5)
is refuted by 5. All 24 obligations receive fresh checking. This witnesses
reuse of one externally supplied recipe on different parameters. It does not
prove that a learner invented the recipe or that the labels cause the result.

## Operational vocabulary contracts

| Word | Input and output / relation | Admission and refusal | Replay and residual |
|---|---|---|---|
| `switch` | Source expression/observation and declared shift s -> target coordinate reading and transported observation | Require the exact map direction and its seven input relations; reject a wrong inverse observation location | Retain map, both tasks, values and source history; no arbitrary-role or noninvertible switch theorem |
| `reorganize` | Shifted expression -> expanded expression with a checked equality relation | Require coefficients and every domain row; reject changed coefficients or missing rows | Retain both expression records and the equality evidence; no identification of their histories |
| `revise` | Expression and nonzero d -> new target, applicability record and new observation | Check the revision relation and old-value counterexample; a proposal alone cannot commit the new target | Keep old truths bound to their old tasks; no general repair or reality revision mechanism |
| `judge` | Proposal, exact source state, finite fuel and fixed checker -> AcceptedAdjustment or Unknown, with a receipt | Full acceptance requires all 24 obligations; malformed evidence is rejected; incomplete checking cannot change the active state | Retain source digest, proposal, checked-prefix count and remaining obligations; no independent oracle of truth or user intent |

The former switch/judge substitution is therefore corrected: judge is the
evidence-and-budget gate; switch is one kind of action it can admit. Reorganization
and revision are not reduced to coordinate switching. Their chosen scalar
realizations here do not establish that this is a complete or irredundant
vocabulary for every finite learner.

`syntax-formation` and `word-formation` remain documentary proposals. The recipe
can expand into the equations and row checks above; it introduces no parser
syntax or irreducible primitive. No extra word is claimed beyond the clarified
roles of these four working names.

## Verification and atomic acceptance

The producer constructs the proposal with nested Horner evaluation. The
checker independently reconstructs scalar rows with expanded powers and
checks header coefficients using another algebraic arrangement. It rejects
noncanonical field inputs (including Python booleans), wrong task or recipe
bindings, altered expression definitions, and incomplete row lists.

The active state is accepted as an input only when it matches the declared
source state. The checked source observation is the first arithmetic row.
After all obligations pass, the result appends transported, reorganized and
revised observations with explicit source-to-target history. The original
state is never mutated.

Two attempts with fuel 0 and 2 respectively retain Unknown/fuel_exhausted.
Their active state is exactly the original state. The proposed chain and
remaining row indices remain available for review, but are not an accepted
transformation. This implementation provides no incremental resume API;
fresh admission would require a new bounded invocation and checking again.

The deterministic artifact is serialized, parsed and replayed against the
arithmetic specification and reconstructed receipts. Producer and checker
use different scalar evaluation algorithms, but receipt/state assembly is
shared code. Tests separately assert expected observation values, histories,
pending-state preservation and mutation rejection. This is not a formally
verified Python interpreter or two fully independent state-machine checkers.

All scalar zeros are retained normally in these field equalities. No ratio
is used, so no division-by-zero claim is manufactured. These equalities are
not native formation residual A=0 or execution residual M=1 from Research
0107, and do not change that kernel's concrete zero-fault discipline.

## Resource contract and observed costs

The standalone process enforces a five-second wall alarm and CPU limit,
256 MiB address-space limit, 128 KiB artifact size and 20,000 metadata-item
limit. The outer command has an additional five-second timeout. There are
no recursive programs, searches, automatic continuations or fuel resets.

One arithmetic row check compares a complete scalar relation/observation
record with its recomputed specification. It is not one field operation or
CPU instruction. Build/admission checks 24+24+0+2=50 rows; artifact replay
checks another 50, exactly the declared 100-row run limit. The test process
has a separate 100-row allowance. Metadata and serialization costs are
bounded separately and remain in elapsed time. Untrusted JSON is byte-bounded
before parsing; the module is an external research fixture, not a hardened
public service for adversarial arbitrary syntax.

Observed on Linux, Python 3.12.13:

| Phase or resource | Result |
|---|---:|
| Construct two proposals | 0.148058 ms |
| Main-instance verification and state construction | 0.370606 ms |
| Fresh-instance verification and state construction | 0.371317 ms |
| Zero/two-fuel pending checks | 0.240535 ms |
| Build total, including those phases | 1.156214 ms |
| Serialization | 0.087559 ms |
| Parsing | 0.086938 ms |
| Artifact replay | 1.029367 ms |
| Witness-file save | 0.119836 ms |
| Total measured elapsed | 2.583027 ms |
| Main process peak RSS | 10,880 KiB (10.625 MiB) |
| Artifact bytes | 11,257 |
| Main checked rows / metadata items | 100 / 362 |

Eight targeted tests passed. The measured test harness, including discovery,
took 6.473901 ms, checked 54 rows and 388 metadata items, with process peak RSS
14,080 KiB (13.75 MiB). There were no implementation correction replays. The
main run and test harness together performed 154 row checks under their two
declared budgets. No whole-repository suite or CI-wait loop was run.

Do not sum nested build timings. These one-shot observations exclude imports,
interpreter startup, design, source retrieval, network persistence and writing
the cost report. Artifact size is not peak memory. No physical energy,
incremental-verification speedup or customer-use cost has been measured.
In particular, these timings must not be compared as speedup against the
different search workload in 0131.

The candidate-fuel pending receipts were successfully saved and replayed.
Resource exceptions report Unknown when caught, but hard process interruption
does not guarantee a checkpoint or even an output record. That limitation is
retained rather than read as a proof of perpetual continuation.

## Replay and retained evidence

From the repository root, on Linux with Python 3.11 or later:

```console
timeout 5s python -m experiments.structural_adjustment.calibration --check examples/verified_witness/structural-adjustment-f7.json
timeout 5s python -m experiments.structural_adjustment.calibration --output /tmp/structural-adjustment-f7.json --cost-output /tmp/structural-adjustment-f7-cost.json
timeout 5s python -m unittest discover -s tests/python -p test_structural_adjustment.py -v
```

Witness SHA-256:
`a059c66e040fbe1dc832a54864d3eee9fb29db5aa5f46717e4f6356f2ddc3cde`.

The eight tests replay the committed fixture and check coordinate direction,
the blind-copy counterexample, expression/history distinction, preservation of
old truths under target revision, fresh-instance reuse, pending-state rejection
of forged acceptance, missing/tampered rows and stale state, and malformed
fields/budgets. Tests do not change process-wide resource limits in a shared
pytest process. The measured standalone test harness applies its own limits.

Files:

- `experiments/structural_adjustment/calibration.py`
- `tests/python/test_structural_adjustment.py`
- `examples/verified_witness/structural-adjustment-f7.json`
- `examples/verified_witness/structural-adjustment-f7-cost.json`
- `examples/verified_witness/structural-adjustment-f7-validation.json`

## Result and smallest continuation

The result supports Mingli's structural distinction in one explicit finite
setting: judging an adjustment and performing it are different responsibilities;
evidence can move with a checked coordinate relation, survive an equivalent
expression change, or require a new value after target revision. A true old
statement need not be erased when its use for a new task is refuted.

This gives Mingli and subsequent agents a replayable example for reviewing
word meanings and prevents blind migration of constraints. It has not been
validated against Jiamin's practical task or human interpretation needs.

The next smallest cost question is a two-branch dependency fixture in which
one declared revision affects only one branch. Compare whole-task checking
with checking the affected branch plus the dependency and reuse evidence,
including all formation, validation and persistence costs. The present
implementation rechecks all obligations; selective verification and its
advantage, if any, remain unimplemented. No harder arithmetic search or new
vocabulary is needed before that comparison.
