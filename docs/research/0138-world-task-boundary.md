# Research 0138: World as the counterpart of open, at a task boundary

Date: 2026-09-06. Status: native bounded experiment completed; operational vocabulary remains Proposed.
Base: main `57c1d04bcfe51b82f6e559a61ca02e668f630b5a`.

## User-defined placement and one-step objective

Mingli named the third task position World and defined it as the counterpart
of open. The third position retains two expressions: `Subject seek Object`
and `Machine obligate Human`. The preceding proposals retain
`Universe Human Obligation` and `Human explore Universe`, motivated by his
readings of different intellectual traditions. They are working formulations,
not imported religious propositions, physical laws, or formal-system axioms.

This step asks how to put a single arithmetic question and a task review
assignment into the same inspectable record without identifying them.
The working name and counterpart placement are user-defined. The operational
task interpretation proposed here still needs validation. World is not
identified with Universe, and the word does not mean an open question closed.

Research 0122 on main already separates arithmetic trust-policy checks from
actual external consent and custody. Its fixed quorum program is not reused
as an arbitrary task former. Drafts 130--137 remain unmerged contextual work;
in particular, draft 136 supplies one exact arithmetic round trip and draft
137 exposes absent self-interpreter interfaces. Draft 137's final CI now
passes. This independent branch depends on main's witness kernel, not those
draft implementations. No paused unknown-syntax-building work is resumed.

## Minimal World task record

| Field | Meaning |
| --- | --- |
| open | The exact unanswered arithmetic goal and retained gaps |
| Subject / Object | Requesting role and sought witness; neither is silently identified with Human or Universe |
| Machine / Human | Solver role and review role, separately bound |
| Boundary | Candidate domain, arithmetic definition and acceptance rule |
| Resource | Finite candidate allowance and external execution caps |
| Agreement input | An externally assumed, task-scoped review arrangement |
| Witness / Residual | Native proof, search prefix, remaining candidates and pending review |

These role references are research-local labels, not native SourceId values.
The display label is separate from the task binding. The binding includes the
goal, domain, resource contract and role references, so retasking cannot reuse
an unrelated agreement merely by retaining a display name.

The operative split is:

1. Seek produces an arithmetic candidate or a bounded residual.
2. The native checker validates a candidate independently of the agreement.
3. A separate task rule may derive a pending witness-review assignment from
   a matching externally supplied agreement assumption.

The third step does not establish that any real person has agreed, reviewed
the result or incurred a duty. In particular, a MachineProposal is not an
ExternalAssumption input. The origin tag itself is not authentication: a
deployment would still have to justify who supplies and verifies that input.
This is an inspectable protocol assumption, not a solved consent mechanism.

## Frozen arithmetic and native evidence

The main task asks for x in {1,2,3} satisfying x+1=3, in ascending candidate
order with two candidate units. Its witness is x=2. With only one unit, the
checked prefix is x=1 and the result must retain Unknown with {2,3} remaining.
A new goal x+1=4 reuses the same fixed procedure with three units, yielding
x=3. Only these three searches run: 2+1+3=6 candidate visits.

The checker uses existing ExactExprV0 integer constants and addition. For a
successful candidate it records an ArithmeticTransition from x+1 to goal,
with equal actual/declared three-role boundaries; all retained concrete
nonzero guards are checked. Exact normalized equality gives M=1 and native
Seal may succeed. Both proof nodes are retained. No f64 oracle or new exact
scalar type is introduced. The arithmetic seal is not a Human review receipt.

The remaining fixed checks reuse those results: missing agreement, a machine
proposal used as agreement, a stale agreement after retasking, a display-only
rename, and an incorrect candidate x=1 for goal3. There are eight case groups
in total and no search beyond the frozen three candidate lists. Every outcome
keeps task_closed=false because Human review is not supplied or simulated.
This is an explicit conservative policy in the example, not a derived
complete closure rule. The checks establish that the fixed cases respect
that policy; they do not learn when an arbitrary World task should close.

## Boundary findings this experiment can and cannot support

An arithmetic witness may be valid while no review assignment can yet be
derived. Conversely, an agreement cannot make a wrong arithmetic candidate
valid. This separation is the useful connection between the two expressions
in the World position. It prevents a successful calculation or an exhausted
budget from manufacturing an obligation to accept a claim or provide fuel.

Missing agreement is a task-formation gap; incorrect mathematics is a checker
failure; pending Human review is a remaining task action. They are not the
same open condition. Native nonzero obligations are also distinct from these
research-local task obligations.

Rename only changes the presentation label in this fixture. A changed goal
requires a new matching task-bound agreement input. Search and verification
costs remain recorded. No copied prefix is declared globally replay-proof,
and no private signature, personal identity or actual consent is inferred.

The existing working words suffice for this small step: divide separates the
two judgments; observe records their outcomes; break retains an unfinished
prefix; learn names the proposed correction of the task model. The example
does not implement an Adva-internal learner, general obligate primitive,
self-interpreter, free object, or closure of World or Universe.

## Reproduction and budget

The frozen contract is `0138-world-task-run-contract.json`.

```sh
cargo build --release -p adva-witness --example world_task_boundary
mkdir -p target/world-task
timeout 30 target/release/examples/world_task_boundary \
  --output target/world-task/world-task.json
```

CI applies a 30-second process limit, 256 MiB virtual-memory limit, bounded
file output and a ten-minute job timeout. The artifact basename is explicitly
world-task.json, with create-new writes; no recursive extension is generated.
One necessary implementation correction was permitted; none was needed for
native compilation or execution. The local environment has no Rust toolchain.
CI formatted the source, passed example clippy, built it and executed the
frozen cases once. The ordinary initial CI failed its formatting gate; this
follow-up retains the exact executed rustfmt output and changes the dedicated
workflow to check formatting. With retained evidence present, that workflow
does not repeat the research execution. No additional search is authorized
by a timeout. Use a fresh output directory for manual reproduction: an
existing world-task.json is deliberately not overwritten.

This step helps Mingli and later agents see which task obligation is attached
to which goal, assumption and evidence. It does not yet establish value on
Jiamin's real task. The next smallest continuation is one explicitly supplied
review response or changed task requirement, with its source and scope
retained, and a check of precisely which obligation it discharges or reopens.


## Retained native result

The [native job](https://github.com/mountain/adva/actions/runs/34032876417)
succeeded on 2026-09-06. Its starting head was
`9bfa9ac4274091a1754aa9e8710d332aa4c11f08`; CI applied rustfmt before building.
The final example is exactly that executed formatted source, whose digest is
recorded in `0138-world-task-cost.json`.

| Fixed case | Arithmetic | Assumed agreement | Remaining action |
| --- | --- | --- | --- |
| Main, x+1=3, fuel2 | Verified x=2 | Conditionally applicable | Human review pending |
| Short fuel1 | Unknown; checked x=1, remaining {2,3} | Conditionally applicable | Arithmetic witness still absent |
| Reuse, x+1=4, fuel3 | Verified x=3 | Conditionally applicable | Human review pending |
| Missing agreement | Verified | Missing | Scoped review assignment absent |
| Machine proposal | Verified | Rejected as imported agreement | External assumption absent |
| Retask with old agreement | Verified | Binding rejected | Matching agreement absent |
| Display rename | Same verified witness | Same applicable assumption | Human review pending |
| Wrong x=1 for goal3 | Rejected; native Seal refused | Conditionally applicable | Valid arithmetic witness absent |

All eight groups passed their fixed checks. Complete native proof nodes,
exact inputs, search prefixes, assumptions and judgments are retained in
`0138-world-task-witness.json` (109446 bytes, without a final newline).
SHA-256: `5db5990535f3cbf00c371204faa02caab92a2b6a9e109eb0d86ecd17d0330279`.
The file digest matches the native CI output. It is an integrity check, not
a semantic source identity. No agreement-origin tag is authentication.

There were six candidate visits and fourteen counted native proof-check
units: six candidate derivations, seven saved-witness replays and one forced
Seal-refusal check. A unit is not every internal kernel invocation. Search
and construction took 87023 ns; verification and case recording 196245 ns;
serialization 148483 ns; file creation, write and sync 1194868 ns. The sum of
these measured phases is 1.626619 ms, excluding startup, top-level evidence
packaging, stdout, teardown, engineering, compilation and network time.
The fresh goal4 reuse used three of the six candidate visits; separate reuse
time was not measured.

The outer native-command measurement recorded a peak resident set of 3852
KiB (about 3.76 MiB). This covers the timed timeout/native-command process
tree, not the compiler or full CI host. Its displayed 0.00-second times are
rounded. Cargo reported 29.44 seconds for the lint/dev build and 55.08 seconds
for the release build. Full research time, per-phase peak memory and isolated
word-formation cost were not measured. The machine-readable cost record and
raw host measurement are saved alongside the witness. No with/without-word
cost comparison was run and no acceleration or added expression power is
claimed.

This result calibrates one proposed World/open interface. It supplies no
general closure criterion, evidence of real agreement, native learn
implementation, self-interpreter or proof of universal grammar reliability.
No additional working word is required for this finite step.

The example's witness replay reconstructs retained in-memory proof nodes in
the native store. It does not yet expose an importer that reads this saved
task JSON and validates it independently. The JSON is complete audit output;
deserialization alone would not authorize a task or certificate. A standalone
stored-task replay interface remains an engineering obligation.
