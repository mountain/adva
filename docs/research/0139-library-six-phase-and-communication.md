# Research 0139: Library inputs, bounded phase reports and communication

Date: 2026-09-06. Status: orchestration implementation and proposed interface
design; no new native free, run or breakthrough semantics.

## Question and current evidence

Mingli asks to place pascal-task.adva and pascal-witness.adva in adva-library,
run learn six times and report, then free six times and report, and introduce
contract, seal and Seal at breakthrough. He also identifies a communication
gap among the three Human/World/Machine participants.

Main is `57c1d04bcfe51b82f6e559a61ca02e668f630b5a`. Drafts #130--138 were still
unmerged when inspected. This branch adds no semantic types or native words
and depends on main for its Python harness tests only. A real use of the
specific learn adapter requires the separately declared #136 source; that
dependency is not merged implicitly.

The native CLI contains reveal, trace-arithmetic, frontier, learn and verify.
There is no free, run or breakthrough command. Draft #136 implements a
particular method behind learn, with six stages: formation/Unit, forward,
endpoint-matched reverse, Compose, nonzero guards and native Seal. It retains
free_status=Proposed. Its saved learn.adva is a transition/replay record, not a
new executable method. Its final frontier is terminal. A zero fault at stage
five preserves one unspent unit and refuses the next successful seal.

Historical CI success of that method is prior evidence. It is not a native
execution performed by this new Python runner. The local runtime does not
currently provide adva/cargo/rustc. No toolchain installation or CI experiment
is requested to conceal the missing free contract.

## Boundary and deliverable

The Pascal pair is copied without changing bytes into `adva-library/` and
indexed with attribution, declared types, provenance and integrity hashes.
The connected account did not expose a separate repository named
mountain/adva-library. This directory is a provisional reviewable placement,
not a new repository, stable module system or native loader.

The Python program is a supervisor for external executable calls. It does not
interpret Pascal research JSON, derive Adva semantic identities, synthesize
free, or manufacture a Rust Seal by emitting a same-named JSON field.
The Pascal task and the fixed learn roundtrip remain different questions.

The runnable contract is frozen before invocation. It has exactly two phases,
learn and free, each with six requested slots. It specifies the method,
resource account, schemas, command argument vector, and caps of 30 seconds
per call, 180 seconds per phase, 128 KiB per captured artifact/log file and
256 MiB child virtual memory on the supported POSIX boundary. No shell,
automatic retries, output overwrite or seventh call is part of the contract.
The second phase cannot silently refill the first phase's terminal account.

The initial free adapter is null. The runner preserves that fact as NotRun
instead of launching six unknown commands. This is an engineering gap report,
not completion of free. When a first-phase error or guard refusal occurs,
later dependent actions retain their unexecuted status.

Two native output writes are not a transaction. If a transition file exists
while its next frontier is absent or invalid, the supervisor retains the
partial files, records the discrepancy and stops. A successful process exit
alone is insufficient even for protocol completion. Python's schema and
byte checks do not replace Rust semantic replay.

At call completion, the supervisor also cleans up the created process group,
including descendants whose direct parent has already exited. Cleanup errors
must preserve the launch record as an error. Deliberately detached processes
are outside this supervisor's containment; this is not a cgroup sandbox or a
general security boundary for arbitrary hostile executables.

## What 'no errors' can require

Expected cases such as missing implementation, refused guards, malformed
output and timeout should produce structured outcomes rather than an
uncaught crash. The six slots report requested work, actual launches and
uncompleted steps separately. Failed execution is not renamed success.
Fatal I/O or process/environment failures are possible: if saving a report
fails, the runner must surface that failure and must not claim a durable
continuation record exists.

Meaningful supervisor tests use explicitly synthetic child processes. They
check process sequencing, timeout, partial output and missing-backend behavior.
Synthetic subprocess success is not evidence that Adva learn or free ran.
No broad arithmetic search or with/without-word speed comparison is made.

## The missing free definition

The current strongest accepted arithmetic result is a guarded local M=1
roundtrip with retained history. A task-relative interpretation of free still
needs its own input/output and acceptance contract. The proposed next question
is whether a checked witness discharges all required obligations of a declared
finite task boundary. Coverage of those obligations must itself be justified;
an empty recorded list is not proof that nothing is missing.

A useful candidate gate would include the old A/M and nonzero conditions,
literal endpoint/history obligations, the task's coverage certificate and the
explicit required discharges. It must also preserve human review where that
review belongs to the task. This is a proposal for Mingli's judgment, not a
definition silently installed in Python. One accepting and one rejecting or
Unknown instance should precede a six-step native free implementation.

## contract, seal and Seal

| Word | Proposed/current role | Timing and boundary |
| --- | --- | --- |
| contract | Versioned question, assumptions, resource caps, interfaces, checker and exit rule | Required before any actual trial; breakthrough may propose a new version with explicit changes |
| seal | Proposed verb for fixing a task-bound presentation/checkpoint version | Retains content and references; does not by itself validate mathematics or authenticate an author |
| Seal | Existing Rust WitnessProofV0 constructor | Native formation and multiplicative closure checks remain authoritative; concrete retained nonzero obligations are separately enforced by the bounded method |

Research #136 already uses Seal at its sixth learn stage. Thus it cannot be
treated as a completely new operation first appearing after twelve calls.
The intended future role can be refined at breakthrough without changing its
existing meaning. Neither seal nor Seal provides another person's consent.

The ordering is: an initial contract; bounded learn calls and report; a formed
free contract; bounded free calls and report; then, if a specific residual
justifies it, a bounded breakthrough proposal under a revised contract.
Checkpoints and communication may occur between stages. No stage consumes a
later contract retroactively. No breakthrough experiment runs in this record.

## Minimal communication proposal

| Word | Observable event | Does not establish |
| --- | --- | --- |
| send | Record an attempted dispatch of a particular presentation | Delivery |
| receive | Record the arriving message bytes and their source claim | Correctness or agreement |
| acknowledge | Refer back to the exact message/version received | Acceptance of its claims |
| accept | Record the explicitly scoped acceptance under the applicable contract | Acceptance of a changed task or all future obligations |

verify remains a distinct mathematical/protocol check and may be used before
accept. Each record binds task/version, sender, receiver, message reference,
presentation content, contract, parent event and the declared deadline/budget.
Three participant-local self references remain separate. Public messages carry
the declared Presentation; a secret remains governed by its disclosure scope.
No secret, actual identity or human agreement is fabricated by these fixtures.

Repeated reception of one identified message should reuse its receipt without
creating another acceptance or resource grant; proving a global exactly-once
protocol is a separate task. Missing reply is Unknown with a reason and
continuation condition, never implied consent. No messages are sent by this
proposal. A signature/provenance mechanism remains distinct from a key label.

## Next smallest continuation

Choose the task-relative free predicate and its accepting/refusing example.
Then provide a versioned native adapter that consumes a fresh declared budget
and refers to the preceding learn witness. Before adding networking, test one
local exchange in which reception is acknowledged but acceptance is withheld.
That would calibrate the communication distinction with no actual recipients.

No new consciousness, universal grammar, self-interpreter or social-trust claim
is entered in claims.toml. Prior Pascal identities and the existing native
roundtrip retain their original scopes.

## Recorded initial reports

The saved `0139-phase-runner-preflight/` reports were generated locally with
the committed default contract and no supplied backend. Environment inspection
found no adva, cargo or rustc on PATH. learn has six NotRun slots with
BackendUnavailable. free has six NotRun slots with LearnPhaseNotCompleted and
AdapterUnavailable. Both phases and the overall run have actual_launches=0.
The supervisor returned normally after saving these expected blocked outcomes.
That exit status is not a twelve-call success claim.

The report records 203360 ns for the pre-save orchestration interval. File
serialization/delivery, engineering time and peak memory were not measured in
this initial preflight. No native arithmetic or Pascal experiment was rerun.
The default reports remain valid after supervisor-only cleanup/validation
corrections because they launch no backend; they are not replayed to pad counts.

Eight supervisor regression test methods passed across the initial invocation
and targeted correction checks. They launched 18 synthetic backends and six
synthetic descendants, not native Adva processes. The measured invocation
durations were 0.428, 0.222 and 0.536 seconds. The version/hash and descendant
cleanup checks resolve concrete implementation risks; no native trial or
production preflight was repeated. The machine-readable validation record
retains final source and test digests.
