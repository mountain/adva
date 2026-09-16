# Pinned research dependencies

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
not his technical review or correctness guarantee.

`adva-machine.lock.json` starts the knowledge repository's external toolchain
consumer route. It pins machine `e62d88dcc83fc4967260866518029942b9631b71` and
library `73a6af4ac4ed8225366d3c16794e309cff15f51d`. It does not require either
repository's current `main` to stay at that revision. See the
[boundary decision and reproduction commands](../docs/KNOWLEDGE_MACHINE_BOUNDARY.md).

## Received run: continuity-01

The [report](evidence/continuity-01/report.json) records an executed run on
2026-09-16. The checker fetched the exact public machine commit into a new
checkout, fetched its library, and built a fresh release executable without
building the knowledge repository's workspace. The build took 154.66 wall
seconds on this host; compiler versions and command logs are retained.

| Check | Result | Boundary |
| --- | --- | --- |
| Library arithmetic subject | Passed; value 14 | Every native report field except phase timings matches retained Research 0140 evidence, including history and certificates |
| Arithmetic tree interpreter | Returned integer 14; 134 instructions | Native v0 replay passed |
| Unsupported object tag | Rejected; 21 instructions | Native v0 replay passed; command exit 2 is required |
| Quantum 17 | Suspended; 17 instructions | Native v0 replay passed; lifetime fuel remains 2048 |

There were ten native invocations: one PSC0 fixture execution plus admission,
execution and receiving for each of three v0 cases. The data-machine cases
executed 172 instructions and separately replayed 172 instructions. These are
engineering continuity observations, not a performance comparison, exact
rational theorem, general library importer or full repository migration.

The complete run includes the exact checker, dependency lock, input requests,
historical comparison artifact, raw native artifacts, replay receipts, build
and command logs, and an integrity manifest. Absolute paths and the original
base-commit field remain as recorded. The checker and lock were new working
files at execution time: their retained snapshots and digests identify the
executed version; the base commit alone does not describe those additions.

An initial targeted test invocation passed eight new migration-boundary tests
and seven existing contract-chain tests. A later broader test command used a
nonexistent test filename and collected no tests; that invocation is not counted
as validation. The corrected selection passed 673 tests: dependency migration,
retained evidence, the existing native contract chain, research index, math
catalog and catalog key words. The catalog check also remained
`CatalogConsistent`, with the geometry obligation open and no native admission.

SHA-256 identifies retained bytes, not native semantic authority. The checker
does not authorize a stored report by reading its `Passed` field: a new run
builds the pinned machine and performs native execution/replay again. These
artifacts do not update earlier research evidence or release its obligations.

## Public-checkout correction

The first [CI run](https://github.com/mountain/adva/actions/runs/35085965622)
failed during library acquisition, before any build or native execution. The
historical machine `.gitmodules` uses an SSH URL. Local SSH access had hidden
this environmental dependency; the new hosted runner had no corresponding key.
The complete [failed receipt](evidence/ci-01-failed/report.json), checker, lock
and command logs are retained without rewriting the successful local run.

The acquisition command now supplies the lock's public HTTPS library URL through
Git's per-invocation submodule configuration. The machine revision, gitlink,
library commit, specification and input byte pins are unchanged. The workflow
disables SSH explicitly, so this route must work using public HTTPS access.
A successor run, `continuity-02`, checks the corrected acquisition path with
`GIT_SSH_COMMAND=false`; it retains its own checker and complete evidence.
Its [report](evidence/continuity-02/report.json) passed all four checks after a
155.72-second fresh build. The expanded regression selection passed 675 tests,
including both successful runs and the preserved failed acquisition.

## Unknown v0.3 dependency successor

The current lock advances the machine and library together for Unknown v0.3.
Its `previous_lock` records the exact earlier lock and digest under `locks/`.
The original two successful runs and failed CI receipt remain bound to that
earlier machine/library pair. The native source profiles, knowledge inputs,
historical comparison artifact and finite execution budgets are unchanged.
The license revision's voluntary commitments do not retroactively change the
meaning or permissions of earlier artifacts.

The [continuity-03 report](evidence/continuity-03/report.json) receives this new
pair after a fresh public HTTPS checkout and a 158.47-second release build,
with SSH disabled. All four checks passed: the complete historical PSC0 observer
and returned/rejected/suspended data-machine executions with fresh Rust replay.
The three data-machine cases retain 172 executed and separately replayed steps;
all ten native calls are accounted for. The checker itself is unchanged.
The complete successor run is retained alongside, not in place of, its predecessors.

## Publication withdrawal successor

The active pins now use publication-clean history. The machine successor is
retained on `maintenance/publication-clean-consumer-20260916`; it preserves the
implementation previously pinned at `0c1e972d6b2b955b0a5361f755cf2560ce44a248`.
Its Cargo inputs, Rust/Python sources, specification, programs and experiment
sources are byte-identical. Its new library lock preserves its predecessor,
and the knowledge lock likewise preserves the complete prior lock and receipt
chain. Historical evidence is not relabelled as a run of the new commit.

An exact-tree local rehearsal rebuilt this successor and passed the library
arithmetic observer plus Returned, Rejected and Suspended native replay cases.
The final public pins are independently checked by the dependency-continuity
workflow. The main branch of the machine remains free to advance independently.
The eight removed golden-ratio inputs are outside this native execution chain;
full historical calibration with those inputs remains unavailable publicly.
