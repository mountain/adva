# Research 0154: math catalog engineering and task-loop capability audit

Date: 2026-09-06. Scope: documentary organization, bounded integrity checks
and inspection of existing executable research. No new mathematical search,
logical calculus, native geometry import, Seal or loop operator is introduced.

## Requested constraints

Mingli Yuan proposes arithmetic, geometry and logic inside `math/`, with logic
as explicit research content rather than an unexamined authority. He further
requires directory separation during future growth and geometry to start
from Pascal, recorded as an obligation with seal. ADR 0042 and the pinned
`math/constraints/` files distinguish the documentary checkpoint from the
existing Rust Seal. The obligation remains Open.

The implementation gives each catalog entry one home and partitions topic
views into owned entries and references. Geometry candidate chains must reach
the pinned Pascal root through earlier same-home parents. Existing unrelated
geometric material may remain reference, not a derived successor. No checksum
or status field grants mathematical truth or native admission. The read-only
standard-library CLI is `python3 python/adva/adva.py math-check`.

The initial catalog now has ten entries. The first eight-entry draft omitted
two relevant capabilities, found during the requested task-loop audit: the
existing external Pascal incidence program and existing finite logical
procedures. They are now indexed with their original, limited authority.

## Can propositions define computational tasks?

Yes, in declared finite fragments. A proposition alone is not a task loop:
it does not specify an input representation, candidate construction, a
decision procedure, next-state policy or termination condition. A task needs
at least the following independent coordinates:

- home directory, theory/version and explicit interpretation;
- input domain, preconditions and question/acceptance predicate;
- admissible construction or search steps and their checker;
- retained state, history, evidence and residual obligations;
- next-task rule, finite fuel/time/memory/I/O budget, and terminal outcomes.

The intended external control structure is:

```text
declared proposition and assumptions
  -> finite task/input
  -> construct or search
  -> check result and side conditions
  -> retain evidence, history and unresolved obligations
  -> stop, or choose the next same-home task within the remaining budget
```

That is a task-level iteration design, not an implemented stable Adva loop.
It need not grow the knowledge library: repeated execution, proof search and
admission of a new reusable word are separate events. A theorem check passing
does not establish global progress or justify deleting an earlier path.

## Existing mechanisms, checked in this audit

| Domain | Concrete existing task | Executable level | Still missing |
| --- | --- | --- | --- |
| arithmetic | Construct an expression path to a fixed target and check every selected edge | Rust research search with Lean/Metamath supervision; Research 0153 retains 100 rounds | A general proposition-to-task interface; native program/knowledge promotion |
| geometry | Six ordered homogeneous points: compare conic determinant with Pascal incidence computation and separately check geometric side conditions | External Python exact calculation, symbolic witness/replay and 320-input fixed workload in Research 0128 | Native Pascal import, certificate-bearing coordinate/derivation bridge and native geometry admission |
| logic | Evaluate a formula in an explicit finite model; separately search/check ordered right-implication proofs | Test-local finite satisfaction and TND0 focused proof procedures in Research 0082/0084/0094 | Unified task transport, a promoted Rust logical carrier/checker and native iteration |

These are not equally strong or the same kind of loop. The arithmetic campaign
already has a bounded orchestration entry. Geometry has a batch calculation
and witness-checking script. Logic has finite evaluators and proof-search
fixtures, not a production task CLI. The focused procedure and ordinary finite
Boolean satisfaction belong to distinct declared logical fragments.

The geometry script is
`experiments/knowledge_geometry/acceleration_direction.py`. Its two routes
compare the same exact scalar, but a zero scalar alone does not make repeated
or degenerate points a valid Pascal instance. The native run profile still
uses f64 and cannot substitute for these exact arithmetic obligations.

`python/adva/research.py::ResearchMachineV0` already packages finite replay
epochs over Rust-checked program cuts/slices. It repeats a declared schedule
and checks its chosen boundary condition. It neither consumes these math
catalog propositions nor defines recursive PSC0 semantics, a self-growing
library or a general feedback operator.

## What can and cannot be sealed

The directory/Pascal obligation can be fixed as a documentary checkpoint.
That records what future work must satisfy; it does not record that the work
has succeeded. Native `WitnessProofV0::Seal` requires the existing Rust
formation and multiplicative closure judgments, with retained nonzero
obligations. It is not a generic constructor for sealing any English or JSON
task statement. No native Seal is created in this engineering phase.

Search exhaustion remains Unknown at the task boundary. Finite model
evaluation can compute truth in its explicit model; a failed proof search
does not thereby refute a formula in every interpretation. A general theorem
also needs more than testing a finite list of numerical instances.

## Validation scope

The capability audit ran the four existing test files for Pascal acceleration,
finite logic adequacy, natural deduction and focused proof completion:
**53 tests passed**. This was engineering regression, not a fresh benchmark,
new theorem campaign or execution of the proposed Pascal three-human meeting.
The **81 catalog tests** separately exercise shape/integrity, one-home membership,
the fixed open obligation, Pascal ancestry, rejection controls, resource
exhaustion, no-clobber output and denial of native admission.

The complete Python regression passes **787 tests plus three subtests**.
The outer prime entry still passes its five frozen cases, using five native
calls and 258/5120 fuel. Ruff passes for the new checker and tests. The direct
standard-library math CLI returns `CatalogConsistent`: ten entries, 41 files,
41 reference occurrences, 1,814,303 bytes read, no subprocesses, Open growth
obligation and native Seal NotIssued. These are metadata/regression results,
not new native arithmetic, geometry or logic theorems.

Historical Research 0149--0153 materials and old library snapshots remain
unchanged. Only the additive outer CLI changes its previous hash; historical
0153 runtime pins continue to refer to commit `5d956de`. A new common task-loop
runner would require its own versioned contract and bounded engineering
decision. The current implementation does not silently add that runner.
