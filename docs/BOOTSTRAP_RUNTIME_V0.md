# Adva bootstrap runtime v0

This is a packaging and CLI boundary over existing Rust implementations. It is
not a new interpreter, proof rule, native `free`, self-hosted compiler, or a
public release. Direction: Mingli Yuan; implementation: ChatGPT/Codex.

## Supported first path

The initial tested target is Linux x86_64 with Rust **1.94.0**, a host C linker,
GNU coreutils, Bash, and locked Cargo dependencies. Python 3 is optional for
packaging and report inspection; the executable and Rust library loader do not
depend on Python. Other targets need their own build and filesystem validation.
Hard links are required for no-overwrite report publication.

From an authorized checkout, initialize `adva-library` at the parent gitlink;
do not update it to an unrelated latest branch. The bootstrap input list pins
library commit `7496a5c893fadf5d72fd29cf7ad5a63f42586b4b` and the actual files.
The repository currently uses an SSH submodule URL, so access to both private
repositories must already be configured. No visibility or license is changed.

```sh
git submodule update --init adva-library
rustup toolchain install 1.94.0 --profile minimal
bash scripts/bootstrap-build.sh /tmp/adva-bootstrap-build-01
python3 scripts/check_bootstrap.py /tmp/adva-bootstrap-build-01
```

Choose a new output directory. The script verifies `bootstrap/inputs.sha256`,
builds in an empty target directory (600-second host bound), copies a runtime
bundle, and invokes four bounded commands from outside the source directory.
Each command has a 30-second host bound. Build logs, failures and partial output
remain on failure; there is no automatic retry or fuel renewal. A timeout may
prevent a final command report. Finite library fuel counts existing logical
checks, not wall time, CPU instructions, or terminal report I/O.

The bundle contains `bin/adva`, `library/stability`, `programs/arithmetic.adva`,
and reports. This is the epoch-library subset; it does not include or execute
the entire mathematical/documentary catalog. `build-target` is retained build
work, not required to run the copied binary. Dependency downloads can occur
during build. An offline source release additionally needs vendored dependencies
and their license material; this version does not claim an offline bootstrap.

## Native commands

These are **research v0** interfaces:

```sh
bin/adva library check --path library --epoch 1 --output check.json
bin/adva library reuse --path library --epoch 1 --word 0 --input 2 --output reuse.json
```

`--path` names the library root; the supported store is its `stability/`
directory. Epochs are 0..3, input integers are -8..8, and `--fuel` is 0..50000
(default 50000). Word ordinals are snapshot-local. A library check rederives
the stored snapshot and parent chain through `load_library_v0`; reuse invokes
`reuse_library_word_v0` and its exact integer/nonzero checks. It does not run
arbitrary `.adva` documents. A different schema is refused by the existing loader.

Use optional `--expect-digest HEX` to bind an independently selected canonical
snapshot BLAKE3 digest. `check.json` records that digest; its prior selection is
the caller's responsibility. Omitting the option performs internal consistency
checking only. A digest neither authenticates an author nor turns supplied
observation assumptions into world facts. This CLI does not repair historical
receipt anchors or change the disclosure API.

| Outcome | JSON status | Exit |
| --- | --- | ---: |
| Snapshot and ancestry rechecked | `SnapshotChecked` | 0 |
| Scoped word instantiated with guards checked | `ReuseChecked` | 0 |
| Invalid input, guard, schema, pin or missing snapshot | `Rejected` | 2 |
| Shared library fuel exhausted | `Unknown` | 2 |

Valid requests retain structured failure reports. Invalid CLI options, unsafe
destinations and host publication failures can stop before a report exists.
Outputs must be fresh and outside the library; they never update an epoch.
Full selected snapshots and scoped witness nodes accompany successful checks.
Snapshot ancestry is rechecked from disk, not authenticated by this command.

## Acceptance and arithmetic boundary

The arithmetic program evaluates `2 + 3 * 4` to `14` through the existing f64
native-run profile. The separate library reuse instantiates the exact integer
doubling witness at `x=2`, yielding `['4', '4']`. At `x=0` this witness's retained
nonzero condition refuses reuse; the polynomial identity itself still holds at
zero. No f64 output of zero or one is promoted to an exact arithmetic proof.

`check_bootstrap.py` checks report status, values, shared snapshot, zero refusal,
and unchanged library file hashes. This is saved-report protocol inspection;
only Rust did semantic checking. The source/input digest list is integrity data,
not an independently trusted or signed build certificate. Reproduction means a
clean build and the declared behavior; identical machine-code bytes across
hosts/toolchains have not been established.

## Source bundle without private submodule fetching

An authorized collaborator may create the minimal source bundle locally:

```sh
python3 scripts/package_bootstrap.py /tmp/adva-bootstrap-source.tar.gz
mkdir /tmp/adva-source-test
tar -xzf /tmp/adva-bootstrap-source.tar.gz -C /tmp/adva-source-test
cd /tmp/adva-source-test/adva-bootstrap
bash scripts/bootstrap-build.sh /tmp/adva-from-archive-01
python3 scripts/check_bootstrap.py /tmp/adva-from-archive-01
```

The source package contains all pinned native build inputs and both required
epoch files, not Git metadata, the full repository, or all research tests. Its
creation grants no redistribution permission; the existing license applies.
The `library_cli` and `native_run_cli` integration tests are included and need no
private library connection. The current `Cargo.lock` and all existing checker
sources remain byte-identical; changing them can intentionally invalidate
historical checker bindings and requires a separate compatibility decision.

## Relation to the Quine

Research 0164 is a finite source-byte relay through a research observer. It can
later be an additional integration fixture. It is not a prerequisite for this
bootstrap, does not construct a general compiler, and is not re-run by these
scripts. General self-interpretation and observer specialization keep their
existing agenda dependencies. Runtime reports and validation evidence for this
change are recorded separately in `bootstrap/VALIDATION.md`.
