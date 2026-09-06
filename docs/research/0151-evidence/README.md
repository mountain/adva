# Research 0151 execution evidence

Executed on 2026-09-06: one trial **Completed**, followed by one separate
read-only replay **Completed**. The three conditional stages each returned
`FeedbackVerified`; their arithmetic evidence is only `AcceptedPair`.
General vocabulary promotion remains `CertificateObstruction`.

## What changed

Let `r0` denote the disk-loaded seed with retained alternatives `2*x` and
`x+x`. The generator, which cannot access task observations, produced:

| Stage | Selected proposal | Polynomial shadow | Enabled / disabled candidates | Accepted pairs, enabled / disabled / macro |
| --- | --- | --- | --- | --- |
| 0 | `r1(x) := r0(r0(x))` | `4*x` | 14 / 10 | 1 / 0 / 1 |
| 1 | `r2(x) := r1(r0(x))` | `8*x` | 22 / 14 | 2 / 0 / 2 |
| 2 | `r3(x) := r2(r1(x))` | `32*x` | 34 / 22 | 2 / 0 / 2 |

These spellings explain serialized ordinal references; they are not new
native Lisp words. All proposal trees use at most three surface nodes. The
ordinary-macro control has the same enabled candidate counts, traces and
logical cost vectors. Disabled searches completely examine their declared
families and return `Open`, not unrestricted unrepresentability.

Each saved stage was reloaded and fully regenerated before continuation.
The final recipe book contains one checked seed and three composite proposal
definitions. Stage 1 and stage 2 retain both successful composition orders,
even where their expanded arithmetic artifacts coincide. Ordinals retain
derivation order; artifact digests never become program identities.

The selected pairs have expanded node counts `[5,7]`, `[7,15]`, `[11,63]` and
named-variable occurrence counts `[1,4]`, `[1,8]`, `[1,32]`. These are
arithmetic syntax counts, NOT SourceId/OccurrenceId or native sharing.
Polynomial equality and the nonzero calibration guards are freshly checked;
both complete expression trees and native research witness nodes are saved.

## What the control means

The local feedback hypothesis survives: including a saved recipe changes
bounded generation and permits a later accepted proposal that explicitly
references it. Merely storing a renamed old result would not pass ablation.

The stronger claim does **not** follow. The ordinary-macro arm deliberately
uses the same arithmetic definition/expansion engine, stripped of any claim
that a witnessed name is a primitive. It is a representational control, not
an independently implemented checker or performance baseline. It has exactly
the same candidates and costs. This experiment therefore demonstrates
**no advantage over ordinary compositional macros**, no new arithmetic law,
no intrinsic self-interpreter and no completed language-formation step.

The run stops after the contracted three stages. More repeated compositions
would not by themselves repair the missing all-fillings coverage/invariance
or native explicit-copy/source/occurrence correspondence. A subsequent trial
needs a new finite contract targeting one of those obligations, rather than
silently increasing this run's depth or replenishing its account.

## Costs and artifacts

The trial spent **32,592 / 50,000** shared units:

| Item | Units |
| --- | ---: |
| Prepaid three checkpoints and final report | 4 |
| Initial checked seed load | 201 |
| Stage 0, three searches plus comparison | 958 |
| Stage 0 disk reload and replay | 1,163 |
| Stage 1, three searches plus comparison | 2,980 |
| Stages 0–1 disk reload and replay | 4,147 |
| Stage 2, three searches plus comparison | 9,494 |
| Stages 0–2 disk reload and replay | 13,645 |

Enabled and ordinary-macro search costs are respectively 379, 1,299 and
4,097 units at the three stages. These include definition inspection,
generation, expansion and checking, not only compressed notation. Costs
increase; this is not a measured acceleration. Full vectors are in
[run.json](run.json). There are 186 production candidate visits across the
nine searches; replay visits are separately charged, not counted as discoveries.

The separate [replay.json](replay.json) spent **13,649 / 50,000** units in its
explicit audit account, without changing or continuing the live journal.
It reconstructed the same four definitions. Neither account is a global
anti-fork resource mechanism.

Measured native wall time / peak RSS:

- Trial: 0.23 seconds / 6,784 KiB, [native-cost.txt](native-cost.txt).
- Separate replay: 0.08 seconds / 6,336 KiB, [replay-cost.txt](replay-cost.txt).

Supervisor limits were 60 seconds, 512 MiB virtual memory and 1 MiB per file.
The three actual journal files are 81,544, 194,757 and 577,777 bytes; the trial
and replay reports are 6,944 and 2,232 bytes. No pending files remain.

The knowledge snapshots `epoch-0000.json` and `epoch-0001.json`, previous
0149/0150 checker sources, contracts and reports, and Cargo.lock retain their
preflight SHA256 values. No epoch 2 was published; all new recipes live in
the [separate exploration journal](../../../adva-library/exploration/0151/).

## Verification and replay command

One focused invocation passed all 12 new example tests. The 211 workspace
tests and workspace/all-target/all-feature Clippy with warnings denied passed.
The new Rust source passes rustfmt, and `git diff --check` passes. No Python
code, stable operation or IR schema changed. Existing unrelated repository
issues remain: whole-workspace rustfmt has the previously known line in
`prime_certificate.rs`, and the old claim registry has one dangling dependency.

The actual trial command was:

```sh
ulimit -v 524288
ulimit -f 1024
timeout 60s /usr/bin/time -v -o docs/research/0151-evidence/native-cost.txt \
  target/debug/examples/library_generation run adva-library/stability \
  adva-library/exploration/0151 docs/research/0151-evidence/run.json
```

Do not rerun against these occupied output paths. To audit the existing
journal, build the pinned source/dependencies, select a **new** report path,
and run the read-only mode under the same supervisor limits:

```sh
cargo build --locked -p adva-witness --example library_generation
timeout 60s target/debug/examples/library_generation replay \
  adva-library/stability adva-library/exploration/0151 NEW-REPLAY-REPORT.json
```

Source/checker drift, changed observations, altered definitions, forged
candidate status, wrong expansion/guards/certificates or incomplete traces
must fail complete replay. Unknown files remain diagnostic, not an admitted
recipe book. There is no automatic resume, repair or overwrite operation.

## Frozen SHA256

| Artifact | SHA256 |
| --- | --- |
| `library_generation.rs` | `c8efda18b1615042a5e0910d00dba57d557babc0b08a62b164ee177bf8269efe` |
| Research 0151 contract | `4a79594ead81c6676a8e1b923a5d1e847c280aef441d1d7f3fce2c2b944ddfb4` |
| `stage-0000.json` | `27ac1392e2b158a06deaf12311cc14e85d08cd1088fcc04f8e85a5324b93c64c` |
| `stage-0001.json` | `d2842b50ab0c82ef54b168f57d48e157fee83a6598a90ad41d4ca175d80f1e6a` |
| `stage-0002.json` | `eed760dffeb7d4e9f61b8a9f702ce9f104ab5d97ddd9bb286b9e2001994d3598` |
| `run.json` | `06d2593dde77b38f947236334ebbb9f59afeac0769d5c06bd404ba2ae12bcd5a` |
| `replay.json` | `c23c637dc62fe4935923762563802a4b660ef500302e008c6bd703406fe8a7d6` |
