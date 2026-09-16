# Knowledge and machine repositories: preserving dependency continuity

Direction from Mingli Yuan, 2026-09-16. Authored by ChatGPT (OpenAI), through
his authorized account proxy; account use is not technical review or a
correctness guarantee. English is the primary documentation language.

## Decision

Repository boundaries may change; dependency and evidence chains must remain
continuous. `mountain/adva` develops knowledge through questions, hypotheses,
constructions, executable research programs, experiments and retained evidence.
`mountain/adva-machine` owns the Adva specification and Rust/Python toolchains,
including bounded Adva-written compiler/specializer work and machine conformance.
The eventual organization of `adva-library` remains open.

This supports exploration in an endlessly open universe. A finite successful
check retains its assumptions and unresolved questions. It does not close the
research programme or promote proposed arithmetic hypotheses to established truth.

Both repositories currently retain the inherited implementation and history.
The first migration introduces an external, fixed-version consumer route. It
does not remove the old Rust workspace, public Python package, research tools,
historical source paths or existing CI. There is no requirement to update old
evidence to whichever machine version is newest.

## Ownership and dependency map

| Current area | Maintenance destination | Dependency that must survive |
| --- | --- | --- |
| Language/IR specifications, native Rust crates and machine profiles | `adva-machine` | Research claims cite a fixed specification/profile; native admission remains mandatory |
| Rust-backed Python facade, machine adapters and conformance | `adva-machine` | Package imports, executable identity, error behavior and supported subsets |
| Compiler, bootstrap, mix and projection implementation experiments | `adva-machine` | Source-to-target correspondence, frozen profile and complete evidence |
| Research questions, philosophy, hypotheses, task-specific programs and experiments | `adva` | Explicit machine/library versions, assumptions, budgets, witnesses and residuals |
| Delivered constructions, catalogs and checked snapshots | `adva-library`, split undecided | One home per entry, byte pins, declared authority and original receiving contracts |
| Historical contracts, source snapshots and evidence | Their retained history | Original commit, relative paths, source fingerprints and replay instructions |

These are maintenance responsibilities, not instructions to move all files with
the same extension. Research-specific Rust may remain with research. Python
supervisors are not automatically machine code. A documentary reference is not
a runtime dependency or an implicit import. Machine test fixtures may depend on
a pinned library without requiring a live checkout of the knowledge repository.

Confirmed migration edges include:

- `pyproject.toml` builds `crates/adva-python/Cargo.toml`; Python consumers cannot
  survive removal of that path until they use a separately received package.
- Existing CI builds the local workspace and launches `target/*/adva`.
- `scripts/check_frozen_library_ci.py` binds the 0150 snapshots to historical
  commit `caabb28b95bb7484680b8d0039fd5a571de421d6`; its live receiver must still
  reject the stale fingerprint. This pilot does not replace that receiver.
- Phase-runner inputs are confined to their contract directory. A later path
  migration must preserve that group, not weaken the containment check.
- The symbol-surface successor binds native source paths and a base commit.
  Those source boundaries and predecessor contracts remain unchanged.
- The library's relative documentary links still refer to the inherited parent
  layout. Redirecting every historical reference would alter retained context.

This is a selected dependency inventory, not an exhaustive migration audit.

## First executable consumer

[`dependencies/adva-machine.lock.json`](../dependencies/adva-machine.lock.json)
pins the machine commit, specification catalog, machine's library lock, library
commit, native fixture and knowledge-side inputs. The machine and knowledge
library pins must agree. An existing dependency checkout must have the exact
revision and no tracked or untracked changes outside Git-ignored files.

[`scripts/check_machine_dependency.py`](../scripts/check_machine_dependency.py)
fetches the exact machine commit and its library when no checkout is supplied.
It builds that machine in a new target directory, retains compiler versions and
build logs, and invokes its existing commands. It does not build this knowledge
repository's Cargo workspace or import its Python package.

Four finite checks cover two existing research examples:

1. Receive the library's `phase-runner/run-program.adva` through Rust `adva run`.
   Compare **every report field except `phase_seconds`** with retained Research
   0140 evidence, including the program, source/occurrence history, compilation,
   certificates, numerical result and resource account. This is the original
   PSC0 `f64` example, not an exact-rational theorem or a six-phase run.
2. Run the knowledge repository's unchanged bounded arithmetic interpreter via
   `adva.machine.request.v0` on `data-machine-v0`: return integer 14 in 134 steps.
3. Supply an unsupported object tag and retain the native rejection.
4. Stop the same interpreter at quantum 17 with original lifetime fuel 2048;
   retain `Suspended` as an open outcome, without resuming or renewing fuel.

All three data-machine cases pass through fresh Rust trace replay. They do not
equate their instruction accounting with PSC0 AST-admission units. Every output
directory must be new. Failures keep partial evidence and return nonzero; there
is no automatic fallback to the local implementation or retry with a new pin.
Build/fetch time is recorded separately from execution. Child commands have
deadlines; this trusted engineering check is not a hostile-program sandbox.

## Reproduction

From a checkout of this repository, with Git, stable Rust and Python 3.11+:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install blake3==1.0.9
.venv/bin/python scripts/check_machine_dependency.py \
  --output target/machine-dependency-01
```

An initialized knowledge-side library submodule is not needed for this route:
the checker compares its committed gitlink, then receives the library through
the machine's pinned submodule. Only that library is fetched, not its unrelated
vendor submodules. To use an existing exact machine checkout, add
`--machine /absolute/path/to/adva-machine`. A later machine HEAD is refused;
use a separate checkout at the locked commit instead of moving an active branch.

The report and full artifacts are under `OUTPUT/evidence/`; fetched source and
build products stay outside that evidence directory. Its SHA-256 inventory
checks integrity, not authorship or native truth. Reproduction executes the
native checks again; it does not merely accept a stored success flag.
The [dedicated CI job](../.github/workflows/machine-dependency.yml) runs this
route from a clean checkout and uploads the evidence even after a failure.
The [first retained run](../dependencies/README.md) passed all four checks;
its source acquisition, fresh build, raw artifacts and native replay receipts
are committed with the dependency boundary.

## Subsequent gates

1. Keep this consumer check passing while expanding the actual dependency map.
2. Migrate one research caller or package consumer at a time. Carry refusal,
   provenance, input, budget and historical replay obligations with it.
3. Establish a versioned Python package consumption route before retiring the
   inherited `maturin` build or changing imports.
4. Retire duplicate implementation paths only after every live consumer has a
   received replacement. Keep old commits and frozen replay paths addressable.

An upgrade creates a reviewed successor lock and new evidence; earlier locks
remain in Git history and retained run bundles. A mismatch is a failed gate,
not permission to relax a fingerprint, change a historical witness, or grant
the library a missing import capability. General optimizing mix and general
second/third projection capabilities remain open under their own contracts.
