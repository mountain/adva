# Continuation binding after implementation failure

Status: executed finite external calibration, 2026-09-16. Base main
`8fdedde5d893e1242048bc6052445dbdb2c4670e`, after merging PR #185.

Authored and checked by ChatGPT (OpenAI), through Mingli Yuan's authorized
account proxy; account use is not his authorship, review or correctness claim.
All added prose, code, fixtures and generated evidence are project-original,
contributed under Unknown v0.3. No external content is incorporated.

## Correction of scope and question

Research 0205 calibrated supplied failure labels; it did not crash and restart
a checker. Its preservation result carries the object digest, history and
unresolved set, not a serialized complete object. The sentence about a repaired
continuation refers to equality between projections in one process. It must
not be cited as end-to-end recovery evidence. Its published experiment timing
covers the retained primary/replay pair only; a subsequent integration replay
was also invoked, without retained separate timing. The full integration cost
is therefore unavailable. Frozen evidence and the historical report remain
unchanged; this note records the narrower reading.

The new question is whether a later candidate can be checked across fresh
processes against the receiver's exact original object/history/unresolved
triple and actual failure parent, without silently renewing an allowance.
The [contract](../../experiments/continuation_binding/contract.json) fixes two
finite binary-word machines, exact integer stages, schemas, trust boundary,
negative controls and resources before execution. No candidate search occurs.

## Executed sequence

For widths two and three, the supervisor saves the complete canonical state
before dispatch. A worker then actually exits with code 17 before producing
a candidate. The supervisor observes that exit and retains a failure record
with no semantic delta. It does not claim to diagnose arbitrary exit causes.
The checkpoint and parent are loaded back from files and sent to a new worker.
That worker proposes the supplied delayed event. A third, fresh process checks
the proposal and eleven mutations against separately supplied receiver-local
expected checkpoint and parent bytes.

The receiver compares the complete state string, recomputes its parent binding,
checks exact fields and types, then independently checks membership in the
bound finite machine and unresolved set. It does not trust the sender's
successful label. The reference source is the declared local fixture, not an
authenticated external principal. Digests are byte references, not native
semantic identities or signatures.

The protocol allowance starts at four abstract attempt units, drops to three
after the observed failure and two after the successful retry. These units
are a finite protocol model, not Adva fuel or CPU units. Host resource usage
is measured separately. No loop or automatic resource renewal is implemented.

## Results and evidence

Both `10@5` and the fresh width-three reuse `110@7` return `Counterexample`.
All 22 negative controls return `InvalidEvidence`: changed object, history or
unresolved set; wrong parent; renewed allowance; wrong or Boolean stage;
additional or missing field; non-object input; and malformed JSON. Every
output retains the complete original state and parent. Refusals add no
semantic facts. The receiver performs no external acceptance side effect.

Six child processes completed in one campaign, including two intentional
failures. No implementation correction or extra research replay was needed.
The [result](../../experiments/continuation_binding/evidence/attempt-1/result.json)
and adjacent files retain every request, candidate, receiver result, stderr,
failure parent and checkpoint. The contract is copied into the evidence.

The complete campaign took **0.863020904 seconds**. The highest child RSS was
**11,008 KiB (10.75 MiB)**. The metrics file reports cumulative child RSS
high-water marks, not independent memory measurements for each stage.
Construction, serialization, startup, checking and reuse share this total;
their individual costs are not measured. There are zero search candidates,
24 receiver cases, and six subprocesses; no instruction-level work count is
claimed. Authoring, reading, Git and publication checks are outside the total.

Each child has a ten-second wall limit, five CPU seconds, 128 MiB address-space
limit and one-MiB regular-file output limit. The campaign has a 90-second outer
deadline. Requests are fixed and bounded; this is not a hostile-input service.
Unexpected child exits stop the campaign and leave existing raw files. A
supervisor failure while recording is not claimed recoverable.

Replay into a new directory from repository root:

```sh
timeout 90s python -B -S experiments/continuation_binding/run.py /tmp/adva-continuation-new
```

## Relation and remaining obligations

This implements one external research receiving condition motivated by the
[communication framework](../COMMUNICATION_FRAMEWORK.md), not a native exchange
or its complete conformance profile. Source, failure history and unresolved
obligations stay explicit. There is no library migration or dependency upgrade.
It extends the finite failure-kind claim without adding a word. Arithmetic
universality and hypothesized arithmetic truth remain hypotheses; this does
not test additive zero or multiplicative one, issue `Close/free`, or fill M6.

The useful distinction for Mingli and later agents is concrete: restarting a
tool does not authorize replacing the question or funding a new task. Jiamin's
real decision workflow has not been tested. This is neither a learning theorem
nor measured acceleration.

The next minimal step is a separately contracted receiver ledger: redelivering
the same accepted continuation must refer to the prior disposition, while a
conflicting payload at that coordinate must be refused. This stateless checker
does not promise exactly-once acceptance, durable transactions, concurrency
safety, adversarial authentication, arbitrary crash recovery or faithful
interpretation of a human's intent.
