# Research 0145: preservation contracts and finite splitting

Status: bounded external calibration completed on 2026-09-06.
No native free, directory migration, stable splitter or new builtin is added.

Inspected main: `24d7275971cfd61fabc3270ac2a71b79df377598`.
Dependency: unmerged draft #144, `d2f7208e42e2f9682e0af169feacf3389c04efe6`,
which is stacked on drafts #143 and #142. Their research results remain draft
dependencies rather than merged main capabilities.

## 1. Origin and the question being formed

Mingli Yuan (苑明理) observed that splitting cannot continue indefinitely and
asked what must remain fixed when representations change. He then authorized
the next step: turn a preservation criterion and a resource-decrease rule into
a concrete bounded contract. The motivation and terminology are his; this
finite model, implementation and operational interpretation are the assistant's
proposal.

Research 0144 kept a ModelGap's old refutations and capability residual visible
while admitting an external candidate revision. It did not implement a general
splitter or a general representation-equivalence checker. This note supplies
one narrower next piece: a worklist whose coverage, representation judgment and
resource account remain checkable at each committed boundary.

The question is whether such a worklist can split and check a fixed finite
family without losing an obligation, duplicating a budget, changing its
meaning after seeing the result, or treating an exhausted search as completion.

This is a **new calibration contract**, not an automatic refill of the 0144
task's remaining 467 units. The inherited evidence and ledger stay bound to
their old task. Every budget used below is explicitly declared for this new
experiment, including audits and serialization.

## 2. What remains fixed when the representation changes

| Fixed field or relation | Concrete interpretation here |
|---|---|
| Problem and quantifier | For every input in the declared seven-point set, compare the two declared programs |
| Arithmetic and observation | Exact integer value equality; no floating tolerance and no after-the-fact observer choice |
| Source/target relation | Expanded and Horner representations with explicit coefficients, operation versions and identity input/output correspondence |
| Checking authority | Frozen external checker and Python exact integers; no native identity or certificate is produced |
| Evidence scope | Question version, input set, both representations and coefficients; display names alone are excluded from binding |
| History and residuals | Separate operation traces, ordered work events, checked points and all pending blocks |
| Resources and stop | A single case ledger, protected checking/save reserve and shared invocation meter; no per-child balance |

A representation may change bytes without changing its values under the
specified observer. The required preservation relation is fixed **before**
checking that change. If the problem, observer or permitted action changes,
the old judgment must be checked for applicability to the new question.

Changing a display name preserves this fixture's binding. This does not cover
renaming an imported module, variable binding, file path or operation selector:
those can change resolution and require the separate migration obligations in
0144. A hash binds bytes; it is not a semantic identity or an equivalence proof.

Histories need not become equal when values agree. We retain the expanded
program's five arithmetic operations and the Horner program's four operations
separately. Their numerical agreement cannot identify native sources,
occurrences, diagrams, equation cells or M6 fillers.

## 3. Fixed arithmetic and the finite frontier

The arithmetic domain is the integers Z, not the finite field F7. The finite
observation set is:

`D = {-3, -2, -1, 0, 1, 2, 3}`.

The source expression is `a*x*x + b*x + c`; the target is `(a*x+b)*x+c`.
The main coefficients are `(2,3,1)`, and the new-instance coefficients are
`(-1,2,3)`. Source and target forms are supplied, not discovered by a learner.
Strict integer types exclude booleans. Declared coefficients are bounded and
intermediate values must fit the specified 128-bit bound.

Expanded/Horner correspondence is elementary arithmetic. Research 0134 already
calibrated a finite compiler/interpreter relation using these forms. The new
claim here concerns **coverage, evidence applicability and shared accounting
across splitting and representation change**, not a new compilation theorem.
No polynomial extrapolation beyond the declared observation set is needed.

Let V be the checked points, and P an ordered family of nonempty pending
blocks. Every committed successful or suspended boundary must retain:

`D = V disjoint-union (disjoint-union of all blocks in P)`.

A successful split replaces one pending block B with exactly two nonempty,
disjoint proper subblocks whose union is B. The fixture uses a deterministic
midpoint split and preserves the order of the remaining queue. Global coverage
is checked as well as the local parent/child relation: a locally valid split
does not justify losing or duplicating another queue element.

A point enters V only after the declared exact comparison has passed. A
counterexample remains associated with its input and the rest of the frontier;
it is not counted as a verified equality. Invalid split proposals leave the
last valid frontier unchanged, although the attempted work is charged.

## 4. Two finite descent arguments

There are two complementary constraints, with different scopes.

For a fixed atom set D, define

`Phi(P) = sum over B in P of (|B|-1)`.

A valid binary split decreases Phi by one. Initially Phi is six, so there
can be at most six valid splits. More generally, replacing a block by k
nonempty disjoint subblocks decreases Phi by k-1. This proof needs a fixed
finite atom set and complete disjoint coverage; it says nothing about an
arbitrary refinement that introduces new obligations or new atoms.

For the successful work path, define

`Psi(P) = sum over B in P of (2*|B|-1)`.

Each valid binary split or successful singleton check decreases Psi by one.
Initially Psi is thirteen. A completed run therefore needs at most six splits
and seven successful leaf checks. A refutation stops immediately; it does not
need to lower Psi by pretending the false equality was checked true.

Display changes, repeated checking, rejected proposals and representation
changes need not lower Phi. Their work still requires fuel. Every admitted
work attempt costs at least one unit from the shared case account. Thus
structural descent controls valid refinements of this fixed problem, while
resource descent controls the other operations and attempted changes.

Neither argument guarantees useful progress. A split can be legal and cost
more than direct checking. This experiment makes no speedup or optimal-direction
claim, and does not recursively introduce new languages or tasks.

## 5. One ledger and a reserve, not balances copied to children

For a case with E work units, its total allowance is E+64. Sixty-four units
are reserved for final independent checking and checkpoint serialization.
Work cannot consume that reserve. The reserve is part of the same total:
checking and saving spend it; they do not obtain a second budget.

Pending nodes contain problem blocks, not fuel balances. A split cannot give
each child its parent's remaining fuel. The account is shared by the entire
worklist. Main and fresh cases have E=13; the zero-work case has E=0; the
partial case has E=4. A zero-work case still has explicitly budgeted checking
and save capacity, rather than an unexplained free checkpoint.

All cases, proposed operations, final checks and selected serialized replays
also share one invocation meter capped at 2000 units. The three receipt-audit
cases have explicit audit allowances; they do not install a fresh balance into
the receipt being audited. Source-history costs and current audit costs must
be reported separately.

The two serialized reconstruction checks likewise have explicit finite audit
allowances inside the same invocation meter. They recheck the saved transitions;
they do not grant fresh work to the original task. Display-name acceptance is
a statement of evidence applicability, not permission to start another run.
If the one allowed implementation correction is necessary, both invocations
must be retained and their total work cannot exceed 4000 charged units.

Charges are declared work/checking batches over bounded data, not individual
machine instructions. Input size, arity, atom count, integer size, CPU, wall
time and address space provide additional finite limits. Checkpointing is
best-effort under ordinary budget exhaustion; hardware failure, abrupt process
termination or filesystem failure can still prevent publication.

## 6. Frozen checks and outcomes

The [contract](0145-finite-split-contract.json) was written before execution.
It fixes twelve cases, one route, seven atoms, split arity two, depth at most
six, thirteen work steps per full case, 256 KiB files, five seconds wall/CPU,
256 MiB address space and at most one necessary implementation-repair replay.

| Case | Required interpretation |
|---|---|
| Main and fresh coefficients | Check every declared point and retain separate traces |
| Wrong target | Produce an exact counterexample and stop with Refuted |
| Missing child or overlapping children | Refuse the invalid partition without losing the old frontier |
| Copied child fuel | Refuse an attempt to create child balances |
| Display rename | Recheck the old receipt under the unchanged meaning scope |
| Changed scope with old receipt | Block unsupported evidence reuse; do not declare the new proposition false |
| Zero and partial work fuel | Unknown, with complete pending coverage and budgeted saved output |
| Self-child split | Refuse a proposal that does not properly refine its parent |
| Inconsistent final frontier | Refuse completion when the reported queue contradicts covered points |

The independent checker must reconstruct the event sequence, queue changes,
coverage, arithmetic and recorded work charges. It must not accept a success
label or sum of leaf counts as a substitute for those checks. The source and
target arithmetic share Python integers; independent traversal/checking is
not independent hardware or a formally verified Python runtime.

The main and partial-Unknown records are serialized and reconstructed under
the same invocation budget. No whole 0134, 0143 or 0144 suite is rerun.
There is no native call, path migration or automatic next iteration.

## 7. Executed witness and preserved Unknown

One invocation completed all twelve frozen expectations. Both selected
serialized reconstructions matched. There was no implementation-repair replay.
The complete [report](0145-evidence/report.json), [host costs](0145-evidence/host-cost.json),
[stdout](0145-evidence/stdout.txt), [stderr](0145-evidence/stderr.txt),
[resource inspection](0145-resource-inspection.json) and
[byte manifest](0145-evidence/manifest.json) are retained.

| Group | Count | Actual result |
|---|---:|---|
| Main, fresh coefficients, display-only receipt audit | 3 | FinitePreservationVerified |
| Invalid splits and invalid receipt reuse | 6 | Blocked |
| Wrong target constant | 1 | Refuted |
| Zero and partial work allowance | 2 | Unknown |

Main and fresh each perform six valid splits and seven point checks. The
display-name case performs an audit of the old thirteen-event receipt; it
does not run the old worklist again. The wrong target yields an exact
counterexample at x=-3: source value 10, target value 11. The counterexample
point remains pending rather than being counted as a verified equality.

After four work steps, the saved partial frontier is:

`checked = {-3}; pending = [{-2}, {-1}, {0,1,2,3}]`.

All seven atoms remain accounted for, exactly once. The work allowance is
exhausted even though reserved checking/save capacity remains. The zero-work
case saves the original seven-point block without executing a split or point
evaluation. Neither case automatically continues.

There is an important distinction in verification outcomes. The checker
**accepts** the primary receipts that correctly record a refused split, a
counterexample or Unknown. It **rejects** the two damaged/inapplicable audit
receipts. The frozen harness requires both the expected result and the right
checker decision; two unrelated uses of the label Blocked cannot make a test
pass accidentally.

The changed-scope audit removes one input from the new question and attempts
to reuse the unchanged receipt. Exact scope binding rejects that direct reuse.
This is a conservative applicability policy: a separately checked restriction
map could reuse a full-domain fact on a subset. No mathematical impossibility
of such transport or falsity of the smaller-domain statement is asserted.

At x=-1 the main source and target both yield zero. It is an ordinary integer
output in this external domain; it does not create a native formation A0
certificate or remove any nonzero guard from a native transport method.

## 8. Accounting, actual costs and reproduction

The twelve final case ledgers sum to **209 charged units**, exactly matching
the single global meter, below its 2000-unit cap. A bounded input/proposal
construction batch costs one reserved verification unit per case. Every work
attempt, final checker event/point batch, serialization and selected replay is
also accounted for. Fixed-size integer arithmetic within a point batch is not
counted as individual CPU instructions.

The construction batch is classified under the ledger's verification category;
this is an accounting convention, not a claim that the measured construction
phase consists only of verification. Execution, initial audit, replay and final
encoding retain distinct ledger snapshots. Main has 17 units after replay and
16 after the final encoding charge; the earlier snapshots are not rewritten.

| Ledger | Initial | Work spent | Verification, including input construction | Serialization | Remaining |
|---|---:|---:|---:|---:|---:|
| Main, including selected replay and final report checkpoint | 77 | 13 | 45 | 3 | 16 |
| Fresh coefficients | 77 | 13 | 23 | 1 | 40 |
| Partial work, including selected replay | 68 | 4 | 15 | 2 | 47 |
| Zero work | 64 | 0 | 3 | 1 | 60 |
| Display-only audit | 64 | 0 | 23 | 1 | 40 |

The two serialized reconstructions spend the original main/partial cases'
remaining reserved budget. They do not obtain fresh grants or repeat the
producer's split execution. The three separate receipt audits use the audit
allocations declared for this invocation and leave the copied execution
ledger unchanged. The original 0144 task account is not consumed or refilled
by any of these independent calibration records.

| Measured component | Actual |
|---|---:|
| Construction and work | 1.622 ms |
| Initial independent verification | 2.579 ms |
| Case serialization | 0.502 ms |
| Selected serialized reconstructions, including their checking | 0.810 ms |
| Fresh case total, overlapping earlier component times | 0.666 ms |
| Supervised process wall, including startup and saved output | 50.139 ms |
| Process peak RSS at report measurement | 12032 KiB |
| Final supervised child peak RSS | 12160 KiB (11.875 MiB) |

Do not sum the overlapping fresh-case measurement with its constituent phases.
Research, implementation and network time remain Missing, not zero. The
43438-byte report is an artifact size, not a memory measurement. No elapsed-time
speedup, learned compiler or cost advantage is inferred from these measurements.

From this branch on Linux with Python 3.11 or later, choose a new output path:

```sh
timeout 5s python3 experiments/finite_split/calibration.py \
  --contract docs/research/0145-finite-split-contract.json \
  --output /tmp/adva-0145-replay.json
```

Require both `all_frozen_expectations_met` and `all_replays_match` to be true,
and inspect the checker decisions, event histories, residual queues and final
case ledgers. A process exit code alone is not a preservation certificate.
The tool refuses output overwrite. The contract is byte-bounded before
parsing, and its SHA-256 is pinned. It is a fixed research fixture rather than
a public service accepting arbitrary programs or arbitrary subdivisions.

The frozen contract SHA-256 is
`29c2db4ac3e23256a81a050a2466bc566fb735c5648443b16976b9a5c756ebfb`.
The executed runner SHA-256 is
`66824a1982bc7576c0ca53aa8f3e8ec5dde1c6db329b9ff931258d8278f06187`.
Five-second CPU/wall limits, 256 MiB address space, bounded data, fixed arity
and the shared meter apply to the invocation. A hard interruption can prevent
a valid report; outer process failure is retained separately and is not success.

## 9. Vocabulary, interpretation and next boundary

This refines `research` as a Proposed workflow: form the question and its
preservation relation, propose a bounded decomposition, check the relation and
ledger, and retain a result or precise residual. No new primitive, native
command or replacement for the existing ResearchMachineV0 is introduced.

It also sharpens the relationship between `reorganize`, `judge` and `learn`:
reorganization proposes a representation change, judgment tests its declared
meaning, and learning may retain a usable result. None of these words creates
fresh fuel or discharges a residual through naming alone.

The useful deliverable for Mingli and later agents is a checkable example of
what can remain invariant when representation changes and task boundaries
multiply. No actual customer task or benefit to Jiamin has been measured.

The next minimal study, if this one succeeds, is a separately budgeted resume
from the saved partial frontier with an explicit new allocation record and a
checked link to its predecessor. That would test continuation accounting;
this run must not silently refill or restart itself. Native free, generic
recursive splitting, observer specialization and 0090/0092 full-coverage
promotion retain their existing independent obligations.
