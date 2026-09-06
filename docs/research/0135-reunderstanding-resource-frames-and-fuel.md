# Research 0135: Reunderstanding, resource frames, and cumulative fuel

Status: proposed engineering vocabulary with an external bounded calibration,
2026-09-06. Mingli Yuan supplied the direction and names. His next Task is
explicitly reserved for the next conversation; this experiment does not
invent or execute that task. The assistant supplied the accounting model,
implementation and tests; a second agent reviewed the conceptual boundary
and then read the code without running additional experiments.

## 1. Direction and dependency boundary

Mingli's proposed turning point is `reunderstanding`: resources on a different
substrate can be given another interpretation, inducing a boundary `switch`
inside a `frame`. A finite vocabulary permits `rename`, while shared fuel
and interface conditions constrain continued work. `retask` will follow when
Mingli supplies the next Task.

We use `reinterpret` as the standard spelling and retain `reinteprete` as the
user's original spelling. This orthographic convention creates no new
semantic operation. `free` is provisionally read as freedom to select among
admissible transformations, not zero cost, unrestricted reordering, an inverse
law, or a free mathematical construction already established.

The fixed main commit is
`57c1d04bcfe51b82f6e559a61ca02e668f630b5a`. At preflight, #130--#134 were
unmerged draft proposals. AGENTS.md, the research agenda, claims.toml and
Research 0129 remain authoritative constraints. Research 0134's distinction
between phase return and local close motivates this follow-up, but no code
or claim from that draft is imported as merged authority. Native interpreter,
specializer, resource semantics and identity allocation are not introduced.

The new question is intentionally narrower than interpreting an arbitrary
real substrate: can a fixed finite representation change and lexical rename
preserve an explicit common resource boundary, including spent fuel?

## 2. Proposed organization

| Term | Proposed role | Input and output | Required boundary / residual |
| --- | --- | --- | --- |
| `substrate` | carrier with available representations and operations | declared representation and capacities | no equivalence between actual physical carriers assumed |
| `resource` | typed availability and cost account | quantities, units, scope and history | storage units and work units are distinct |
| `frame` | the current interpretation contract | types, units, name bindings, resource rules and obligations | changing a frame requires an explicit correspondence |
| `reunderstanding` | propose another useful reading | current frame and an intended use to a candidate interpretation and obligations | usefulness and human interpretation remain to be established |
| `reinterpret` | express the old/new reading relation | two frames and a mapping to a preservation claim or residual | only checked relations authorize a switch |
| `switch` | commit an admitted frame change | mapping, witness and budget to a new frame and history event | inexact or invalid mapping leaves the active frame unchanged |
| `rename` | change local names while retaining their bindings | finite role/name bijection to another bijection | collisions or reconstructed resource accounts are rejected |
| `retask` | assign resources and evidence to a new explicit task | supplied Task plus frame and old evidence to new obligations | not executed; Task is AwaitingUserTask |

All general names remain Proposed. The executable part is a fixed external
calibration of rename, representation switch and resource accounting. It is
not a general reunderstanding algorithm or a native Adva vocabulary extension.

In the earlier syntax/semantics/pragmatics organization, rename concerns
bindings in syntax; reinterpret states a relation between readings; retask
changes the use and acceptance question. `frame` records their joint boundary.
These roles overlap and do not establish a one-to-one mathematical identity.

## 3. Frozen finite model

The contract is [0135-resource-reinterpretation-contract.json](0135-resource-reinterpretation-contract.json),
SHA256
`a72f59cddddde17c8650d8fa615106df4600b713392f44848b6cde78ba77cbc2`.
It was written before the first run. There is one fixed transition model and
one deliberately unsafe control, with no adaptive search or larger rerun.

The common resource is a natural-number bit capacity, at most 24. An octet
cell has declared width 8; a nibble cell has declared width 4. A frame stores
the cell count and substrate name. An exact conversion must satisfy

\[
 n_{\mathrm{old}} w_{\mathrm{old}}
 = n_{\mathrm{new}} w_{\mathrm{new}}
 = B.
\]

This is a representation of one capacity, not a transfer or allocation of
real storage. Multiplying unit widths supplies the complete imported
arithmetic justification. There is no conversion of storage bits into CPU
time, energy, authority or task-solving power.

The three roles are `cell`, `fuel`, `task`; active names are exactly `a,b,c`.
All six bijections are tested on each substrate. Frame names may change,
while the account's externally declared fixture label and its accumulated
debits persist. This label is not a native SourceId, a generated semantic
identity, an authenticated resource entitlement or an implemented durable
account service.

Each rename costs one model fuel unit. A switch costs two, declared as one
proposal unit and one verification unit. These are abstract fixed charges,
not measurements of host work. A spend action occurs only in the reset
control. With enough fuel, cost is deducted before candidate validation:
rejection and inexact conversion still retain their debit. With insufficient
fuel, the action is Unknown and unexecuted. Host preflight and checker work
remain separately measured and bounded.

The budget invariant is

\[
 \mathrm{spent}+\mathrm{remaining}=\mathrm{grant},
 \qquad\mathrm{remaining}\geq0.
\]

No name change creates a new grant. No rejected attempt refunds its checking
charge. No switch resets prior expenditure. The finite positive charges
bound the number of admitted actions in this model; they do not prove
unrestricted program termination or a universal resource conversion law.

## 4. Results and counterexamples

There are twenty fixed traces:

- two four-action round trips at capacities 24 and 16, each with grant 8;
- twelve one-step renames, covering all six bijections on both substrates;
- six controls: colliding names, forged width, inexact conversion, zero fuel,
  cycling between naming frames, and spend/rename/spend.

The 24-bit route goes from three octets to six nibbles and back. The fresh
16-bit instance uses two octets and four nibbles with the same recipe. Each
round trip restores its initial representation and naming map, but spends
six fuel and retains four events. Thus returning to the same frame is not
identity of the complete resource/history state.

| Proposal | Checked result | Retained consequence |
| --- | --- | --- |
| 3 octets to 6 nibbles | Committed | 24 bits preserved; switch costs 2 |
| 6 nibbles relabelled as 6 octets | Rejected | proposed 48 bits exceeds the declared 24; old frame and paid cost remain |
| 3 nibbles to 1 octet | Unknown | 4 bits are unrepresented; active 12-bit frame unchanged |
| cell and fuel both named `a` | Rejected | role distinction retained; rename cost still paid |
| rename with zero fuel | Unknown | no frame change; candidate remains pending |
| two funded renames followed by a third | Unknown at the third | two units spent, zero remaining; finite names do not refill fuel |

Inexact conversion here could be made representable by introducing an
explicit residual-bearing target frame. That grammar extension is not made
in this run; the residual remains available for a later proposal.

**Budget-reset counterexample:** use grant 3 and the same three-name
vocabulary for both implementations. Spend 2, then rename at cost 1, then
request another spend of 1.

| Point | Shared-account checker | Deliberately unsafe name-keyed accounts |
| --- | --- | --- |
| after spend 2 | 1 remains | 1 remains |
| after rename cost 1 | 0 remains | the new name receives a fresh grant of 3 |
| another spend 1 | Unknown; total spent stays 3 | accepted; total spent becomes 4 |

The unsafe implementation is included only as a replayable counterexample,
not as an authorized transition policy. A finite vocabulary plus finite local
allowances does not imply conservation of the shared budget. Binding the
account independently of its display name is the decisive condition in this
model. No performance advantage is asserted for the checked version.

## 5. Verification, persistence and correction

The producer proposes exact cell counts by integer division. A separate
checker reconstructs the frozen action sequence and checks target capacity
by multiplication. It independently accumulates debits and compares each
complete event, final frame, account label, Task marker and pending cursor.
Strict canonical JSON comparison distinguishes Boolean values from integers.

The source instances and static width/cost declarations are shared trusted
inputs. The checker is not an independent formal proof assistant. It accepts
only the frozen input family; the producer by itself is not an arbitrary-input
safe interpreter. In particular, complete role-key validation is supplied by
the frozen query binding and checker, not by an unrestricted front-end parser.

Seven targeted tests cover artifact replay, fresh reuse, all bijections,
collisions, width forgery, inexact residuals, name-based refills, zero fuel,
cycling, history/account/scope mutations, injected tasks and Boolean metadata.
All passed. A read-only second-agent review found no issue overturning the
resource result, but identified the same pending-cursor ambiguity found in
the main review.

One implementation correction was made: an Unknown event initially advanced
`next_action_index` past its uncompleted action. It now retains that action's
index. The event history still contains the attempt and its debit, if any.
One correction build/replay and test pass succeeded. No general resume API
is implemented: a later retry requires a revised finite run contract and
must retain prior debits. An inexact conversion additionally requires a
changed proposal or frame, rather than an automatic identical retry.

The Task is consistently `{status: AwaitingUserTask, content: null}`. This
typed absence is neither an empty solution set nor a completed task. The
next Task has not been guessed, renamed into existence or executed.

## 6. Resource measurements

Each standalone process is limited to 5 seconds CPU/wall, 256 MiB address
space, 2,000 charged arithmetic/transition rows and a 128 KiB artifact.
Each trace has at most four attempted actions. Resource limits, an alarm,
cooperative row/time checks and outer `timeout` enforce the finite run.
Unit test imports do not install process-wide limits; the recorded test
harness applied those limits to its own standalone process.

A host row is one produced or independently checked transition, or the
unsafe-control check. It is not a scalar machine instruction and not one
model fuel unit. Model fuel, host work and physical resources remain distinct.

| Final measurement | Cost |
| --- | --- |
| construction and initial check | 2.020878 ms |
| serialization | 0.197981 ms |
| parse | 0.269478 ms |
| replay | 1.386043 ms |
| witness write | 0.099837 ms |
| main total including bookkeeping | 4.016589 ms; 95 rows |
| main peak process RSS | 11,008 KiB = 10.75 MiB |
| seven tests including discovery | 7.341949 ms; 49 rows |
| test peak process RSS | 14,080 KiB = 13.75 MiB |

Main/fresh round-trip construction and checking took 0.322104/0.164292 ms.
These per-trace costs are included in the build total. Including the first
pass and the single correction pass gives 288 host rows and 23.016587 ms
across four bounded main/test processes. Initial measurements are retained
in the validation artifact.

The millisecond totals exclude imports/startup, design, dialogue, the
read-only conceptual/code review, network and cost-report writes. Research
wall time and model inference cost are not instrumented. Memory is Linux
process peak RSS, not artifact size. No hardware benchmark, learned
acceleration, increased expressive power or physical energy saving is claimed.

## 7. Evidence and reproduction

From repository root:

```sh
timeout 5s python -m experiments.resource_frame.calibration --check examples/verified_witness/resource-frame.json
timeout 5s python -m experiments.resource_frame.calibration --output /tmp/resource-frame.json --cost-output /tmp/resource-frame-cost.json
timeout 5s python -m unittest discover -s tests/python -p test_resource_frame.py -v
```

The witness `examples/verified_witness/resource-frame.json` is 22,607 bytes,
SHA256 `baeb1c092756823786a9952b71123d9c9718f8219b22be788590f34db5027e7f`.
The corresponding `-cost.json` and `-validation.json` retain final and prior
costs. The workspace was an exported repo subset. Full repository tests and
CI status were not observed. Hard process interruption can prevent a
checkpoint; no persistence or successful continuation is guaranteed then.

## 8. Handoff for the next Task

The reusable proposal is a boundary checklist for forming a task, not a
requirement that Mingli first formalize his whole problem:

1. Record the supplied problem awareness in its original wording.
2. Propose a finite Task version: intended decision, observable evidence and
   unresolved parts; keep the human reading distinct from formal validation.
3. Declare the substrate resources, units, shared budget and available
   vocabulary; identify which costs cannot yet be compared.
4. State the proposed reinterpretation and the exact common boundary it
   preserves, including history, prior expenditure and evidence scope.
5. Judge the translation witness, then switch and retask only within a finite
   contract; leave missing relations as explicit obligations.

`reunderstanding` is therefore a proposed source of candidate interpretations,
not an automatic permission to cross an unverified boundary. `rename` cannot
by itself guarantee boundary preservation. Neither `I`/`identity` duality nor
native resource conservation follows from this finite example. Arithmetic
A=0, M=1, native ZeroFault and M6 filling are not invoked; no division by a
possibly zero field element or noncommutative transport is smuggled in.

This result can help Mingli, Jiamin and subsequent agents avoid losing a
resource obligation when changing names or task frames. Actual usefulness
for Jiamin's next task remains untested. The next minimal step is to receive
that Task and propose its smallest typed frame, retaining whatever cannot yet
be expressed. No automatic continuation, retask, merge, or restart of the
paused unknown-syntax-building inquiry is performed.
