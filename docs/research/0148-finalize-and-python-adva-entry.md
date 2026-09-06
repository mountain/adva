# Research 0148: Finalize preparation and enter through Python adva.py

Preparation status: **Finalized for the finite implementation below**.
This closes the preparation scope agreed with Mingli Yuan after Research
0147. It does not claim that all research obligations are solved. No further
unbounded mathematical task is a prerequisite for ending this preparation.

## Fixed sequence and distinct tasks

The current finite implementation sequence is:

1. Read the retained prime candidate from Research 0147.
2. Ask the Rust research verifier to check the finite certificate.
3. Let `python/adva/adva.py` validate the transport and save the result.

The original six-stage learn protocol is a separate task: formation,
forward p-to-2p, matched reversal, composition, concrete nonzero guards,
and Seal. Its six subsequent requested free slots retain their missing
adapter and NotRun status. Prime verification neither replaces these six
stages nor supplies their guards, histories or free implementation. No call
to that old task is made in this run.

The working relationship proposed by Mingli is retained with precise scope:

| Word | Reading in this task | Remaining boundary |
| --- | --- | --- |
| `equal` | Exact N=product(P)+1 and N=q*k | Primality and outside-list membership are additional obligations; value equality creates no EquationCell |
| `breakthrough` | One checked extension from P to P union {q} | A proposed workflow reading, not a new native primitive or unbounded search |
| `free` | A task-relative permission requires its own contract | This adapter allows only retaining its finite certificate, never native free |
| `finalize` | Freeze the preparation scope, versions, exit criteria and implementation order | The full Universe(Prime) proof checker stays a separate unimplemented obligation |

## Implemented boundary

### Placement of specification and compile

Mingli asks whether these two existing engineering concepts fit without
opening another unbounded task. They do, with explicit domains:

| Concept | Place in this finite method | What it does not certify |
| --- | --- | --- |
| `specification` | The versioned task contract: input types, witness relations, accepted outcomes, resource caps and allowed action | Writing a specification does not make its proposition true or its implementation correct |
| `compile` at the tool boundary | Cargo turns the Rust verifier implementation into the executable selected by Python; source and binary hashes are retained | Successful compilation does not establish primality, full Universe(Prime), or conformance to every semantic requirement |
| Existing native Adva compilation | PSC0 source is lowered by the Rust kernel to checked diagrams with its existing compilation/graft certificates | This is a different input/output relation from compiling the host Rust checker; no Nat/Prime lowering is added here |

The specification constrains both the implementation and acceptance of its
results. Build the tool under its declared toolchain assumptions, invoke it
on a bounded request, then inspect the checked result against that same
specification. There is no new compiler language, optimizer, proof compiler,
generic specification solver or builtin in this step. These names organize
the existing task, rather than requiring another research prerequisite.

[ADR 0036](../adr/0036-bounded-prime-verifier-and-python-entry.md) records the
new version-zero request/result boundary. `adva-prime-verify` is a separate
research binary in `adva-witness`, with a small exact-integer verifier.
It changes no Lisp operation registry, Real realization, stable IR, semantic
identity, old witness guard or existing library version.

The request contains `primes`, `n`, `q`, `k` and `fuel`. Rust rechecks all
input primes, the product-plus-one equation, factor equation, nonmembership
and every divisor needed for q's primality. Explicit fuel bounds the
checks; exhaustion preserves the checked prefix. Divisor zero remainders
are permitted. They are not sent through the older nonzero-expression
guard. The public API rejects oversized list/schema lengths before cloning
the request; the CLI additionally caps input at 16 KiB before decoding.

Python performs no prime arithmetic. It snapshots the exact request, makes
at most one native call under a three-second bound, checks the returned
schema, input echo, status/exit-code agreement, fuel and limited capability,
then preserves raw native bytes, hashes and diagnostics. Output paths must
be fresh. The selected executable is a trusted local input; its path and
hash do not authenticate an arbitrary substitute.

The request and result are data until the selected checker actually runs.
Successful JSON parsing or a saved success string is not a Rust judgment.
The current CLI's source types are exact bounded unsigned integers; BigInt
remains available in the repository for a future enlarged profile, but is
not needed for values at most 65535.

## Runnable entry and stopping behavior

```sh
cargo build -p adva-witness --bin adva-prime-verify
python3 python/adva/adva.py prime-check adva-library/prime-universe/requests/main.json --native target/debug/adva-prime-verify --output /tmp/adva-prime-main-new.json
```

The new direct-script entry needs only Python's standard library and the
Rust executable. The package initializer still imports PyO3 eagerly, so
`python -m adva.adva` without the installed extension is not promised.
There is no replacement root-level module or directory migration.

| Condition | Report and exit |
| --- | --- |
| Finite certificate verified | Completed / FiniteExtensionVerified, exit 0 |
| Native finite refusal | Completed / Blocked, exit 2 |
| Native checking fuel exhausted | Completed / Unknown, exit 3 |
| Native wall timeout | Unknown, exit 3, no granted action |
| Backend absent | NotRun / BackendUnavailable, exit 2, zero native invocations |
| Bad transport or process failure | ProtocolError or ExecutionError, exit 2 |

All native results retain `native_universe=NotImplemented` and
`native_free=NotGranted`. An arithmetic refusal is different from an absent
tool; neither silently becomes a successful continuation.

## Frozen verification and resource record

The [run contract](0148-finalize-python-entry-contract.json) fixes five
native-through-Python calls: main, fresh, composite successor, falsely prime
successor, and zero fuel. Requests are projections of the retained Research
0147 witnesses; no prime search or old calibration is rerun. Source-field
mapping is explicit: `N -> n`, `cofactor -> k`, with new finite checking fuel.
The original candidate evidence and original preparation records remain
unchanged.

There are six focused Rust unit-test groups, including empty input, malformed
integer fields, composite input, partial fuel and capability restrictions.
The dedicated workflow caps compilation at 240 seconds, focused tests at
60 seconds, each native call at three seconds and the entire job at six
minutes. The five calls allocate at most 5120 verification units. Host build,
test and runtime costs are separate from logical verification fuel. No
claim combines unmeasured unit-test fuel with the five-call ledger.

Local evidence: one missing-backend preflight completed as expected, with
zero native invocations, 33.786 ms including startup/save and a measured
12,160 KiB child peak RSS. The preflight's recorded source hash is the
earlier transport revision, before the final unsigned-64-bit input bound;
it is retained as such and not relabelled as a final-source execution.
No local Rust toolchain was available. The final-source native execution
status is recorded separately below.

Native CI evidence: **NotRun; workflow failed before any recorded step**.
The [single workflow attempt](https://github.com/mountain/adva/actions/runs/34052226236)
on source commit `f927549c451ed017e2b9ce10be22a6c3a940c8e7` completed
with failure at 2026-09-06T18:35:56Z. Its job had no assigned runner
(`runner_id=0`) and an empty step list. Compilation, six focused unit-test
groups and all five planned Python-to-Rust calls therefore remain NotRun;
their runtime and memory costs are unmeasured. This is not evidence of an
implementation failure or of mathematical rejection.

The [API evidence](0148-evidence/ci-preflight.json) retains the job response.
The connector does not allow the check-annotation endpoint, so the underlying
failure reason is Unknown; billing or quota is not inferred. No retry was
made. The frozen commands remain the next execution step when a suitable
executor is available. A correction replay is reserved for an actual
implementation error, which this run has not established.

The [source manifest](0148-evidence/source-manifest.json) identifies the saved
sources and evidence. It excludes itself to avoid a circular content hash.
No native binary exists in this run, so no binary hash or native memory
measurement is claimed. Total research and network wall time was not
instrumented; the local preflight measurement does not include those costs.

## Handoff

The preparation is closed at this specific boundary. The implemented tool
can support finite cooperative work once its compiled checker is available.
The immediate next obligation is the frozen native verification run. After
that succeeds, a possible semantic integration is an explicitly admitted
Adva result interface for this certificate, if selected as the next task. Native
free, the quantified Universe proof, global ledgers and philosophical value
judgments remain separate; none is required to keep expanding this preparation.

The repository remains private. Subject neutrality, the stated collaboration
direction and existing source/claim histories remain intact. No publication,
message to another person or automatic PR merge occurs in this step.
