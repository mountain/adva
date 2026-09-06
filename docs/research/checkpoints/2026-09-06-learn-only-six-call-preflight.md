# Checkpoint: learn-only six-call task preflight

Date: 2026-09-06. Status: blocked before execution; **0 of 6 learn calls
executed**. This is a handoff record, not a new experiment or claim.

## User boundary and task

Mingli requested a first task with explicit boundary, direction and resources,
using only the current Adva surface and six learn calls. Rust and Python are
not to be extended or used to supply a replacement solver. The intended
progression mentions difficult/measure, question/Question, and close/free.

Provisional problem awareness: can a finite learner produce a better bounded
question and an evidence-supported next action while preserving the existing
common boundary? This wording is a proposed interpretation, not a native
question type or a definition approved by Mingli for Question or free.

## Verified current interface

Main was checked at `57c1d04bcfe51b82f6e559a61ca02e668f630b5a`.
The current command is:

```console
adva learn subject.adva method.adva object.adva \
  --output transition.adva --frontier-output next-frontier.adva
```

The CLI has no general `learn --fuel` argument. Method schemas select
different existing algorithms. See
[`adva.rs`](https://github.com/mountain/adva/blob/57c1d04bcfe51b82f6e559a61ca02e668f630b5a/crates/adva-witness/src/bin/adva.rs).

- The inquiry/exploration route selects the first externally recorded
  candidate, keeps it Proposed, and preserves all five original obligations.
  It does not generate candidate content or close an obligation.
- The existing six-run hypothesis-formation route is the fixed GL(4,2)
  four-XOR magic-square experiment, already recorded in Research 0121.
  Replaying it would not instantiate this new question.
- The other learn routes can obtain specific bounded results, but their
  existing problem-formation, value-seeking and magic-square schemas do not
  provide an arbitrary question/Question/free interpreter.

Sources:
[Research 0115](https://github.com/mountain/adva/blob/57c1d04bcfe51b82f6e559a61ca02e668f630b5a/docs/research/0115-frontier-hypothesis-interface-experiment.md),
[Research 0121](https://github.com/mountain/adva/blob/57c1d04bcfe51b82f6e559a61ca02e668f630b5a/docs/research/0121-six-crossing-hypothesis-formation-search-word.md),
[`inquiry.rs`](https://github.com/mountain/adva/blob/57c1d04bcfe51b82f6e559a61ca02e668f630b5a/crates/adva-witness/src/inquiry.rs),
[`problem_value.rs`](https://github.com/mountain/adva/blob/57c1d04bcfe51b82f6e559a61ca02e668f630b5a/crates/adva-witness/src/problem_value.rs).
A read-only second-agent interface review agreed with these distinctions.

The neutral carrier grammar in Research 0109 admits open learning subjects
and finite filling proposals, but explicitly does not prove progress or
termination. The document graph in Research 0110 records routing without
being a general executor. Those broader structural interfaces must not be
mistaken for the current CLI's ability to run arbitrary new methods.

## Two distinct blockers

1. **Execution environment:** `command -v adva` and `command -v cargo`
   returned exit status 1 with no path. Bounded searches of the shared
   workspace and conventional tool locations found no usable executable.
   No native invocation, engine build, external arithmetic solver or fake
   six-error loop was launched.
2. **Interpretation/acceptance:** this task's distinction between
   `question` and `Question`, and the criterion for `free`, are not
   specified by a compatible existing method. Names can occur in candidate
   text without becoming types, proof rules or accepted states.

For the inquiry route specifically, accepted transitions copy the same five
open obligations. By iterating that preservation rule, six accepted calls
would still retain five open obligations. This is a source-level conditional
deduction, not the output of six runs in this session. It rules out obtaining
obligation closure merely by renaming the sixth Proposed candidate free.
It does not prove that every existing specialized learn route lacks witnesses.

## Retained six-call boundary

All six slots are NotRun. Native outputs, runtime, candidate counts and peak
memory are absent, not measured as zero. No mathematical difficulty estimate
can be inferred from an environment/interface obstruction.

If the inquiry route becomes the agreed calibration, its concrete admission
requirements are:

- one original frontier and a fixed exploration contract;
- six fresh resource snapshots with genuinely distinct candidate content;
- the preceding next-frontier as each subsequent subject;
- original question coordinates and all five obligations preserved;
- no interpreter extension, auxiliary solver, verify command or automatic
  seventh call;
- a shared maximum of six calls, 30 seconds per call, 180 seconds total native
  execution, 256 MiB per process and 1 MiB total retained outputs, enforced by
  a supervisor available before execution; no fuel renewal by renaming.

These are a proposed run ceiling and dependency checklist, **not an admitted
or executed run contract**. Six manually written candidates would be external
inputs; their registration must not be reported as six learned questions.
No snapshots are fabricated solely to reach the requested call count.

A minimal next question for Mingli's interpretation is: which observable
change in a proposed question and subsequent action should count as free,
while all existing obligations remain visible? Once that criterion can be
mapped to the current surface, an existing executable is needed to perform
the six native calls. Otherwise the result stays an explicit expression gap.

No Rust/Python code, native schema, builtin or mathematical claim was changed.
This checkpoint is saved alone on an isolated branch, without a duplicate
draft PR, automated continuation or merge. It does not restart the paused
unknown-syntax-building inquiry.
