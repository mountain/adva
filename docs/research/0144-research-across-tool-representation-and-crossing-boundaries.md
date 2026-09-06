# Research 0144: direction and order across tool, representation, and crossing boundaries

Status: proposed engineering organization and completed bounded external calibration.
One frozen invocation completed on 2026-09-06. No repository-wide
relocation, native free implementation, or stable language change occurs here.

Inspected main: `24d7275971cfd61fabc3270ac2a71b79df377598`.
Open draft #142: `2407780f21c428c7a801234e8bb2e27185093900`.
Open draft #143: `cd5730119757ff8247e54b641dfc1aca4b112e22`, based on #142.
This work is stacked explicitly on #143; neither draft is a merged main result.

## 1. Origin, question, and direction

On 2026-09-06, Mingli Yuan (苑明理) identified the previous ModelGap as a
frontier. He requested a study of safe direction selection and implementation
order across three work surfaces: tools, representations, and crossings. He
proposed organizing implementation paths as Rust, Python and Adva machines,
keeping a balanced three-part structure inside each, and locating the meaning
of operations while names and file contents remain changeable. He proposed
`research` as a name if the procedure obtains a witness.

We retain his statement that research concerns boundaries as the methodological
focus of this project, not as a proved definition excluding other research.
His naming and motivation are attributed here; the finite operational model,
implementation and interpretations below are the assistant's proposal.

ModelGap says that the declared candidates do not explain a checked observation.
It exposes a frontier of that model family. It does not by itself establish
whether to repair a tool, reinterpret an observation, expand a candidate family,
or retask. Those actions change different obligations and can be jointly needed.

The main question is:

> Can a finite observer revise this ModelGap without deleting old refutations,
> erasing an unresolved capability, resetting fuel, or mistaking a new question
> for a solution of the old question?

The calibrated answer is external and task-relative. The layout and native
implementation sections are engineering proposals with their own acceptance
gates. Neither a successful small revision nor three directories establishes
universal grammar reliability, native semantic authority, or acceleration.

## 2. Three surfaces are work views, not three intrinsic kinds

| Surface | Changes considered | What must be checked | Typical useful next direction |
|---|---|---|---|
| Tool | Paths, entry points, package layout, runtime and adapters | Resolved dependencies, supported contract, executable capability, resource bounds and report status | Repair discovery, packaging or execution while retaining the question |
| Representation | Names, encodings, source programs and observation presentation | A directed source/target correspondence, the intended observer, domains, histories and residuals | Translate or revise an ambiguous representation and recheck applicability |
| Crossing | Candidate families, questions, accepted actions and task boundaries | Conservation or explicit replacement of obligations, evidence applicability, new checks and cumulative history | Form a new bounded contract and test one proposed transition |

These are related views of the same step. They are not a disjoint classification
of every error. In particular, a ModelGap can be caused by a bad observation
interface as well as an inadequate model family. A diagnosis is a proposal
until the relevant evidence rules out alternatives.

Research 0109 already supplies the neutral organization:

`(subject, method, object) --compute/verify/learn--> (history, result, evidence)`.

Positions are not intrinsic types. Rust, Python and Adva are implementation
substrates and surfaces, not respectively K, t and X. The construction,
history and observation readings remain relevant to each entire mechanism.
File counts, three-stage cycles and matching labels do not discharge any
obligation. Research 0134 already retains three-turn cycles that remain Unknown.

## 3. Proposed tool layout and a migration order

The [machine-readable migration plan](0144-layout-migration-plan.json) records
the inspected paths and consumers. Its inventory is targeted, not a claim that
every path reference in every repository blob has been enumerated.

| Existing location | Proposed location | Compatibility condition |
|---|---|---|
| `crates/*` | `rust/crates/*` | Root virtual Cargo workspace and path dependencies updated together |
| `experiments/labs-search` | `rust/experiments/labs-search` | Retain this existing Rust workspace member |
| `python/adva/*` | Retain | Preserve the public package and `adva._native` binding |
| `tests/python/*` | Later: `python/tests/*` | Update pytest and test-relative discovery |
| Python research scripts | Gradually: `python/experiments/*` | Resolve imports, roots, data dependencies and historical replay first |
| `programs/*` | `adva/programs/*` | Update execution commands, workflow inputs and selectors |
| `adva-library/*` | `adva/library/*` | Move contract and relative inputs as a unit |
| `.adva` examples | Selected: `adva/examples/*` | Preserve actual schema and execution status |
| `docs/`, `schemas/`, `ontology/`, root manifests | Retain shared roots | Shared contracts and governance are not a fourth machine |

Keeping the root Cargo virtual workspace preserves root-level Cargo commands
and the present target directory convention. Moving all manifests at once is
unnecessary. The mixed `experiments/` directory cannot be migrated solely by
filename suffix because experiments contain code, data, evidence and recipes.

There is already a `python/adva` package, including `research.py` and
`ResearchMachineV0`. The root `pyproject.toml` binds its native extension as
`adva._native`. If the user wants the spelling `adva.py`, a package-internal
`python/adva/adva.py` can be a thin future facade, with `__main__.py` exposing
`python -m adva`. This is a proposal, not an installed command. A competing
top-level `python/adva.py` would create avoidable discovery ambiguity; we do
not claim that it necessarily shadows the package in every Python launch mode.

The phase runner deliberately confines input paths to the contract directory.
Moving library inputs must preserve that grouping; weakening the check to
permit `../../` is not a migration technique. Other scripts depend on
`__file__.parents[...]`, `target/debug/adva`, and fixed `programs/` locations.
Historical 0142/0143 checker paths and source digests need a separately retained
migration record. Old evidence stays bound to its old commit.

The implementation sequence is:

1. Freeze common contract fields, the path-resolution map, supported capabilities,
   and representative replay commands. Complete this boundary study first.
2. Make one pure Rust path migration, preserving the root workspace and updating
   maturin plus affected workflow paths; require one native build and binding
   import acceptance. This gate is NotRun in the current environment.
3. Move each Adva program/library group with its relative input structure;
   validate decoding and one existing native replay at the new locations.
4. Move Python experiments and tests in dependency groups; add a thin entry
   facade only when it dispatches existing supported operations without gaining
   semantic authority. Preserve diagnostic report statuses.
5. Introduce native free in its own research-layer change, with the checked
   task boundary below. It must not be hidden inside a path-only change.

The ordering is based on dependencies and rollback clarity, not a theorem
that every project must migrate Rust before Adva before Python. A failed gate
leaves the previous runnable layout available. Whole-repository relocation is
not attempted in this research branch because native acceptance cannot be
verified here: Python is available, but adva/cargo/rustc are absent.

## 4. Balanced internal organization and where meaning lives

Each machine can expose the same three responsibilities without duplicating
the implementation or the authority of the other machines:

| Responsibility | Rust | Python | Adva surface |
|---|---|---|---|
| Present | Parse/validate versioned native inputs and exact boundaries | Form tasks, package resources and propose representations | Express supported programs, tasks and method selections |
| Operate | Compile, evaluate and check native semantic relations | Coordinate bounded tools and external experiments; request Rust judgments | Compose only operations the current interpreter actually implements |
| Account | Return checked artifacts, history and typed residuals | Retain costs, provenance, failures and replay inputs | Carry explicit named outputs and witnesses under their actual schemas |

This is interface balance, not three equal implementations of a semantic kernel.
No requirement to divide every source file into three equal sections follows.
The Rust operation registry and validation boundary remain authoritative for
native types, identities, terms, diagrams, histories and certificates. Python
may provide external exact arithmetic without silently converting it into a
Rust witness. A `.adva` suffix alone does not identify an executable format.

For this design, the meaning of an operation is anchored by its versioned
input/output relation and the interpreting/checking rules, including the
scope, observation policy, ordered history and declared side conditions.
Its pragmatic direction is the action the task contract permits and the
acceptance criterion of that task. Human intent and institutional acceptance
are separate when a task actually requires them.

The resolution chain is:

`locator -> resolved bytes/schema -> selected interpreter/operation version ->
checked relation -> scoped result and allowed action`.

No arrow follows from the preceding name alone. Changing a filename can change
relative imports or resource selection. Changing content requires new byte
binding and, when behavior changes, a new relation or contract. Two equal
scalar outputs cannot identify source histories. Replacing the checksum after
an edit establishes only the new bytes, not their correctness.

Research 0132 already distinguishes switch, reorganize, revise and judge.
The proposed organization preserves that distinction:

- `rename` changes presentation only when resolution and interpretation still
  satisfy their correspondence obligations.
- `reorganize` changes representation with a checked preservation relation.
- `revise` or `retask` creates a new question/candidate/action boundary; old
  evidence must be tested for applicability rather than copied as authority.
- `judge` selects whether one specified action has the required support.

## 5. A split must account for both sides and the interface

For a finite old obligation set O, declare a disjoint partition

`O = discharged ⊎ retained ⊎ replaced`.

Every discharged member requires an applicable check. Every replaced member
requires an explicit finite family of replacement obligations. Retained
obligations remain visible. Newly introduced interfaces and conditions must
also appear in the target ledger. Replacement is not discharge, and leaving
an obligation outside a new task does not retrospectively solve the old task.

The proposed transition records both boundary versions, the partition,
replacement mapping, newly checked facts, preserved counterexamples, new
residuals and resource consumption. A split is useful only with this account
of what is shared, changed and still owed at the interface.

This is an external obligation partition, not a native CausalCut, ProgramSlice,
linear hole split, independent subproblem decomposition or M6 filler. Native
cut/slice operations have their own checked diagram and incidence requirements.
There is no conservation theorem for a bare count of holes: refinement can
increase their number while making a question more precise.

## 6. Native free: proposed minimal semantics and dependencies

The first native implementation should be a Rust **research-layer task
admission judgment**, not a new stable Lisp builtin or an assertion that all
boundaries have closed. It should accept a checked source boundary, a versioned
target proposal, the correspondence and obligation ledger, relevant native
artifacts, a concrete requested action and bounded resources.

It would return either an action-scoped acceptance receipt, a refusal with a
counterexample/reason, or Unknown with remaining obligations. The receipt must
bind both boundaries and retain old evidence, new checks, histories and fuel.
An acceptance receipt does not itself execute the authorized action; execution
and checkpoint publication need an explicit subsequent protocol.

Acceptance must check the complete obligation set fixed by the supported
method, the availability of the requested capability, source/target evidence
applicability, all required typed arithmetic conditions and guards, and the
resource transition. A native task that requires A0/M1 must use the native
witness machinery; a successful Python scalar quotient cannot supply it.

Existing counterexamples constrain this design:

- In `free_roundtrip.rs`, stage four can already report symbolic A0/M1 while
  nonzero guards are NotRun; stage five checks them. Even the stage-six Seal
  retains `free_status = Proposed`.
- In `world_task_boundary.rs`, verified arithmetic and conditionally applicable
  agreement do not satisfy outstanding review: `task_closed` remains false.
- `run_six.py` may return exit status zero while its report is Incomplete.

Therefore availability, arithmetic truth, evidence applicability and task
permission remain separate judgments. Native schema/codec design, tests against
these guards, linking learn output to free input, and a bounded executor adapter
are still needed. A local fuel receipt is not a global anti-fork service.

The first implementation target is one existing guarded method and one
explicitly machine-checkable task acceptance predicate. Arbitrary program
rewrite, whole-task closure, human acceptance and open-world freedom stay out
of that first target. No native semantic code is added by this note.

## 7. Frozen finite calibration and research as a working word

The [contract](0144-boundary-research-contract.json) was saved before execution.
The [source](0144-source-model-gap.json) extracts the actual empty-survivor
ModelGap from draft #143, retaining the original report digest and source
commit. At its point, both supplied old predictions 1 and 2 are refuted by
`(1+2^-27)*(1-2^-27) = 1-2^-54`. Its remaining local fuel is 477, after 23 spent.

The candidate revision supplies `1-2^-54` as a third prediction under a new
boundary. It does not discover the formula. The old candidate family and its
refutations remain historical facts. A correct candidate absent from the old
family cannot be obtained by filtering that family alone: adding one is a
different, versioned operation. This is the precise frontier crossing being
tested, not a proof that the best direction can be inferred automatically.

For this crossing study, 0144 establishes a new three-item research obligation
ledger: observation, model-gap and native-free. This is not an imported native
ledger or a replacement for all ten admission obligations of 0143. In 0143,
native-free was an unimplemented capability residual; the requested action
was an external checkpoint, not native execution. Observation
is checked, model-gap is replaced by candidate-v2, and native-free is retained.
The new candidate is independently checked with exact rational multiplication
and integer cross-multiplication. Only an external revised checkpoint can be
admitted. The native-free residual remains even in the successful case.

The source file's `subject` is the original pre-run input with 500 remaining
and zero spent. Continuation instead takes the 477/23 ledger and history from
`case.outcome`. These roles must not be confused. The new k30 source is a
synthetic calibration fixture with the same prescribed ledger, not a claim
that k30 was executed in the old 0143 ModelGap run. Point values and both old
refutations are independently reconstructed here; the entire old trace checker
and all 0143 gate policies are not reimplemented or rerun.

Twelve declared cases cover the valid revision, display-only rename, deletion
and overlap in the obligation ledger, stale boundary binding, changed candidate
content under a reused name, resource reset, zero fuel, native-free demand,
erased old refutations, fresh k30 reuse and changed-question stale evidence.
Two serialized reconstruction checks share the same invocation budget.
These tests do not execute a directory migration or establish compiler/runtime
equivalence. They are not a repeat of the complete 0142/0143 suites.

`research` is proposed as a workflow interpretation:

| Field | Proposed contract |
|---|---|
| Input | A retained frontier, one explicit direction proposal, trusted interfaces and finite resources |
| Action | Form the question; classify what changes; check the boundary obligations; run the admitted finite attempt |
| Output | A checked transition proposal or refusal/Unknown, with evidence, costs and next residual |
| Witness | The exact finite boundary revision and its refusal controls below |
| Refusal | Missing correspondence, lost obligation/refutation, unsupported capability, stale scope or exhausted resources |
| Expansion | Frozen contract, explicit transition ledger and reproducible checker command |
| Residual | Direction selection is supplied; layout migration and native free remain unimplemented here |

This does not introduce a new builtin, override `python/adva/research.py`, or
claim a newly learned theorem. The workflow should refine the existing research
machinery through explicit versioning if later promoted. The name helps people
and agents ask which boundary a proposed change is supposed to improve and
what evidence would justify it.

## 8. Executed witness, actual costs and replay

One invocation completed: all twelve expected outcomes and both serialized
reconstructions matched. No implementation repair replay, candidate search,
native invocation or directory migration ran. The full [report](0144-evidence/report.json),
[host measurements](0144-evidence/host-cost.json), [stdout](0144-evidence/stdout.txt),
[stderr](0144-evidence/stderr.txt), [resource inspection](0144-resource-inspection.json)
and [byte manifest](0144-evidence/manifest.json) are retained.

| Cases | Actual result | Remaining boundary |
|---|---|---|
| Main k27 revision and fresh k30 fixture | 2 TaskBoundarySatisfied | Only external-revised-checkpoint permitted; native-free remains |
| Display-only rename | 1 ModelGap | No new candidate or target boundary admitted |
| Invalid partition, missing residual/refutation, stale binding or evidence, changed prediction, resource reset, native-free demand | 8 Blocked | Old task and residuals retained; no action permitted |
| Zero-fuel proposal | 1 Unknown | No new action or resource state admitted |

The main accepted step takes local remaining/spent fuel from **477/23 to
467/33**. It retains the original ModelGap event and both exact old refutations.
The new boundary has checked candidate-v2 and unresolved native-free. It does
not change the historical old task status to solved. Rename-only retains
ModelGap and consumes six local checking units. The zero-fuel proposal asks
for ledger 0/500; this does not establish that those 477 units were actually
spent. Its requested ledger is not installed, and the source stays 477/23.

Serialized reconstruction repeats the valid main revision and the deleted-
residual refusal, comparing the whole returned outcome including history and
resource records. Both match under the same global invocation budget. These
are different branches of one fixed calibration, not an implemented repeated
continuation service. The external source binding is a byte-derived reference,
not a native semantic identity or authentication mechanism.

| Measured component | Actual |
|---|---:|
| Global charged work, including reconstruction | 138 of 2000 units |
| Construction, including supplied proposal formation and source reconstruction | 2.268 ms |
| Twelve-case checking | 2.008 ms |
| Fresh-case checking, a subset of the previous row | 0.171 ms |
| Serialization and parse round trip | 2.081 ms |
| Two serialized reconstruction checks | 0.810 ms |
| Runner elapsed before final encode/write | 7.436 ms |
| Supervised process wall, including startup and saved report | 43.843 ms |
| Runner peak RSS at report time | 12672 KiB |
| Final supervised child peak RSS | 12928 KiB (12.625 MiB) |

Units are charges for declared fixed checks, arithmetic reads, construction
and serialization batches, not machine instructions. Global costs include
proposal and branch work; local fuel is the task ledger within a branch.
There is no global anti-fork account and no automatic refilling. Research,
coding and network costs were not instrumented and remain Missing. The
proposed name research causes no measured speedup or increase in expression
power. Peak RSS is a process measurement, not the 87346-byte report size.

The runner enforces five-second CPU/wall limits, a 256 MiB address-space
limit, 256 KiB input/report limits and one shared 2000-unit meter. It is a
fixed research calibration, not a hardened service for arbitrary programs.
A supervisor retains process failure separately; hard interruption can prevent
a valid report or checkpoint and is never interpreted as successful completion.

From this branch, on Linux with Python 3.11 or later, choose an output path
that does not already exist:

```sh
timeout 5s python3 experiments/boundary_research/calibration.py \
  --contract docs/research/0144-boundary-research-contract.json \
  --source docs/research/0144-source-model-gap.json \
  --output /tmp/adva-0144-replay.json
```

Require `all_expectations_met = true`, the case outcomes above, and both
`serialized_reconstruction[].matches = true`. Reading the report is necessary;
an exit code alone does not grant a task action. Clocks and RSS may differ.
The pinned contract SHA-256 is
`e11b9a87c868ca831ff82d4f6a61a07d6cf167d00cda9c6ce5362f5ed1bf971c`;
the executed runner SHA-256 is
`215c9cc8c082547a5d4ab4475546e73a7cccbaa8169bda2b37ecbef21ad3022d`.
No automatic next iteration follows this result.

## 9. Sources and remaining work

Repository sources inspected at the main commit above include AGENTS.md,
the research agenda, ARCHITECTURE.md, SEMANTIC_SCOPE.md, Research 0109,
0123, 0129, 0132, 0134, 0136, 0139, Cargo.toml, pyproject.toml,
the native guarded-roundtrip and world-task modules, and the phase-runner
and replay scripts identified in the migration plan. Draft #143 supplies the
ModelGap; its changes are not silently described as merged main features.

Arithmetic-universality and hypothesized-arithmetic-truth remain Proposed.
0090/0092 full-coverage gates, the paused unknown-syntax-building inquiry,
native M6 coherence and global grammar claims are unaffected.

The next concrete engineering change is the root-preserving Rust path migration,
after its native build/import gate can be executed. The next semantic change
is a separately reviewed Rust research admission type and one acceptance
predicate. A boundary record connecting both is required before calling the
combined operation native free. Actual usefulness for Jiamin's work has not
been measured in this finite calibration.
