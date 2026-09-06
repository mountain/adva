# Research 0138: World as the counterpart of open, at a task boundary

Date: 2026-09-06. Status: proposed finite task-formation calibration; run pending.
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
One necessary implementation correction is permitted. The local environment
has no Rust toolchain; actual native outcomes and costs remain pending until
the CI record is retained. No additional search is authorized by a timeout.

This step helps Mingli and later agents see which task obligation is attached
to which goal, assumption and evidence. It does not yet establish value on
Jiamin's real task. The next smallest continuation is one explicitly supplied
review response or changed task requirement, with its source and scope
retained, and a check of precisely which obligation it discharges or reopens.
