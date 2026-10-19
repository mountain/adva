# Finite world structure identification v0

Status: executed research-local Rust experiment, not a stable learner API.
Baseline: `mountain/adva@8585c5b965b84422b802d50f11f375aea171bd27`.
This continues [Research 0263](0263-native-source-fibre-query-gate.md) and
[Issue #28](https://github.com/mountain/adva/issues/28).

Authored by Codex (OpenAI), through Mingli Yuan's GitHub account as an authorized
proxy. Account use is not his authorship, review, endorsement or correctness
guarantee. Code, fixture programs, evidence and prose are project-original
contributions under Unknown v0.3. No third-party content is incorporated;
existing external build dependencies retain their own licensing and locks.

## Frozen question and complete hypothesis family

Can a finite observer distinguish copy placement and an extra identity event
among **all** programs in one fixed finite grammar? This is a structural
question, with no numerical prediction or f64 evaluation involved.

The [run contract](../../experiments/finite_world_identification/contract.json)
fixes three ordered `Real` inputs `a,b,c`. Each input branch independently uses
`id(use input)` or `copy(use input)`. Optionally insert exactly one additional
`id` immediately before the first branch operation. No other terms are allowed.
Every candidate has the same namespace and root function name. Its output
boundary has the actual number of output wires. The observation does not read
the full candidate signature, body or name.

The three copy bits give eight placements; the padding bit gives two histories
per placement. The canonical enumeration coordinate is `key=2*copy_mask+pad`,
with keys 0 through 15. This key is not SourceId or semantic identity. The
implementation checks all 120 pairs have different full native diagrams.
There is no claim of coverage beyond these 16 programs or of syntax-independent
canonicalization of arbitrary PSC0 programs.

The hidden fixture is candidate **5**, copying `b` and padding `a`:

```lisp
(frontier (id (id (use a))) (copy (use b)) (id (use c)))
```

It has four operation nodes and source multiplicities `(1,2,1)`.
Candidate 4 omits the inner identity event, has three nodes and exactly the
same complete multiplicity observations. The hidden program is used only to
supply the observation question; the receiver never uses its key for selection.

## Native boundary and exact observer quotients

Rust generates source text, parses, links and compiles each candidate. The
receiver independently requires keys 0..15 exactly once in canonical order,
regenerates the artifact for each key under the caller-fixed grammar, and
compares the **complete** compilation artifact. Missing, duplicate or reordered
coverage yields `UnknownCoverage`; replacing a body's diagram under the same
key and root name yields `InvalidEvidence`.

The checked diagram is validated again and its transition from empty past to
complete past is certified with the existing Rust slice/triadic kernel. Counts
are read from exact lower source roots and upper source/occurrence incidences.
Occurrences remain the original slice members; copy events remain in history.
The exact compilation and graft companion, transition, complete slice and
source text are all retained in the [native evidence](../../experiments/finite_world_identification/evidence.json).
The slice has no graft intersections because this readout uses the ordinary
transition API; the separately regenerated compiler graft companion is retained.

Local counters and root names repeat across separately compiled worlds.
An occurrence is interpreted only within its candidate's complete native
snapshot, never identified with an occurrence in another candidate by local
counter, scalar value or hash equality.

For each checked world `W`, the readout is
`F(W)=(total upper incidences, a multiplicity, b multiplicity, c multiplicity,
full-slice operation-event count)`. Observational equivalence is exact equality
of the coordinates revealed by the question. `Q0` reads coordinate 0; `QA`
adds 1; `QAB` adds 2. `QABC` also reads 3. `QABH` instead adds coordinate 4 to
`QAB`. These are research projections, not a new stable ObservationPolicy or
active transformation. Reading operation-event count is an explicitly stronger
history observer, not information inferred for free from output observations.

The experiment computes **every class** in every quotient, checks disjoint
complete membership against a separate four-loop combinatorial oracle, and
receives each class under its exact observation. There are respectively
4, 6, 8, 8 and 16 classes under these five observers. The oracle supplies an
independent finite formula, not an independently implemented native kernel.

## Executed target and counterexample

| Observer | Observation from world 5 | Complete surviving keys | Node-minimal keys |
| --- | --- | --- | --- |
| Q0 | `(4)` | 2,3,4,5,8,9 | 2,4,8 |
| QA | `(4,1)` | 4,5,8,9 | 4,8 |
| QAB | `(4,1,2)` | 4,5 | 4 |
| QABC | `(4,1,2,1)` | 4,5 | 4 |
| QABH | `(4,1,2,4)` | 5 | 5 |

Thus new source observations remove copy-placement ambiguity but do not recover
the identity-padding history. All eight QABC classes still have two worlds.
The history observer separates that last pair; QABH identifies every one of
these 16 candidates uniquely. This is complete identification **conditional on
this grammar and access to that history observation**, not general recovery
from arbitrary incomplete observations or a universal theorem.

The minimality rule minimizes the number of operation nodes in the checked
native diagram. It is independent of source spelling length, key order and
prediction score. Every tie and every nonminimal survivor is retained. Under
QAB, it selects candidate 4 even though the hidden world is 5. This is a
checked counterexample to “the minimal fitting program is the actual world”.
No selected minimum becomes a rewrite, contraction or permission to erase id.

## Outcomes, controls, cost and retained failure

The research receiver returns `Complete` with **all** survivors and minima;
these may be multiple or empty. An empty class refutes compatibility only
inside the declared family. An unresolved pair is recorded as multiple
hypotheses, not unique recovery. Invalid question/evidence, incomplete coverage
and budget exhaustion remain distinct. `UnknownBudget` retains spent work,
the next unchecked key and matching candidates in the checked prefix, without
claiming the prefix is a complete class or granting resumable authority.

Six Rust test functions cover the complete quotients, target refinement,
wrong-minimum counterexample, omitted/duplicate/substituted candidates,
deleted history, changed occurrence path, wrong graft companion, invalid
questions, empty class, zero budget and allowance 31 versus required 32.
The receiver has no proposal-supplied observer features to trust. It recompiles
and rereads them. It is an in-process typed research receiver, not a hardened
arbitrary-JSON service or a new persistent certificate interface.

A complete receiving call charges 32 units: two bounded kernel bundles per
candidate. Kernel internals, arithmetic operations and comparisons are not
priced by those units. The six-test suite has a fixed upper bound of 1024
canonical compilations, with at most four nodes and nine occurrences per
candidate. The supervisor separately enforces 600 seconds for build, 120
seconds for testing, 4 GiB address space per process and 8 MiB per test-output
file. Build files have a separate 512 MiB cap. The retained native JSON cap
is 2 MiB. Timeout kills the child process group and reports `UnknownTimeout`;
no automatic scope expansion or research retry is performed. These trusted-host
limits are not a hostile-input sandbox, total-machine-memory cap or measured
peak RSS.

An initial engineering smoke run passed six tests before event-count refinement
and checked-prefix retention were added; it lacked the later resource supervisor
and is not the frozen run. The first supervised build then failed before tests:
its 8 MiB file limit also limited the linker output. One environmental correction
separated build/output limits without changing the candidate family. The failure
and corrected run are retained in [attempts.json](../../experiments/finite_world_identification/attempts.json).
The corrected run passed all six tests. A subsequent Rust execution matched
the complete frozen JSON byte for byte. Later implementation-only checks of
the supervisor and explicit hidden-observation assertion are recorded separately;
no historical evidence bytes are replaced. Full CI is a separate remote gate.

## Reproduce and dependency residual

```sh
python3 experiments/finite_world_identification/run.py --output /tmp/world-id-new
```

The output directory must not exist. The supervisor stages the research source
as an ephemeral adva-lisp integration test and removes it afterwards, retaining
logs, source/kernel/dependency SHA-256 bindings, native JSON and measured outer
wall time. Python performs only process supervision and exact byte comparison;
it never allocates semantic identities or supplies native judgments. Both Rust
producer and receiver share the compiler, validator and slice kernel. A defect
shared by those kernels remains possible; no independent human review is claimed.

Existing Rust identities and slices suffice for **this** read-only enumeration
and observer refinement. No specialization or executable residual is constructed,
so the experiment does not consume or claim the remaining interface from #26.
Turning observations into residual mechanisms, persisting portable correspondence
certificates, receiving them through a versioned machine-owned interface and
adopting that consumer remain #26 / KPB-14 successor work. PR #216's private
PSC0 input-binding certificate is relevant prior work, not automatically the
receiver for this 16-world family. No external machine/library pin changes.

Issue #28 therefore gains the complete-candidate experiment, exact hypothesis
classes, separating observations and explicit minimality counterexample; its
broader specialization dependency and general structure-learning scope remain
Open. A useful next experiment would test the same class calculation against
an independently supplied source-to-residual observation certificate, preserving
this full replay and the padded-world counterexample.
