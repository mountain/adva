# Native input-binding correspondence certificate: finite PSC0 calibration

Date: 2026-10-14. Baseline: `cd10e3e31fa149a3039037fb4a55c67d610b8ce5`.
Status at authoring: implemented research checker and frozen regression family;
native Rust compilation and execution are **NotRun locally** because this host
has no Rust toolchain. Remote verification results must be recorded separately.
This document does not claim those checks have already passed.

Authored by Codex (OpenAI), through Mingli Yuan's GitHub account as an authorized
proxy. Account use is not his authorship, review, endorsement or correctness
guarantee. Original code, fixtures and prose are contributed under Unknown v0.3;
no third-party source, text or data is incorporated.

## Question, object and authority boundary

Issue [#26](https://github.com/mountain/adva/issues/26) needs a native
source-to-residual identity/certificate bridge beyond the executed research
data-machine `mix`. This calibration asks one smaller question:

> Can existing Rust PSC0 graft and slice judgments check a complete structural
> correspondence from a two-input source to a fresh-context residual whose
> first input is bound to one exact literal, preserving every body operation
> and accounting for all static lineage no longer exposed by the residual?

The source is a compiler-produced, call-free PSC0 function
`source(static: Real, dynamic: Real) -> (Real, Real)`. Its residual is a distinct
root function:

```lisp
(def residual
  (fn ((dynamic Real)) (outputs Real Real)
    (call source 7/3 (use dynamic))))
```

The compiler performs the existing finite simultaneous substitution. The
wrapper produces one constant event and a complete instance of the original
source body. The research receiver checks that instance rather than treating
the wrapper's call spelling or its certificate booleans as authority.

This is Rust-native research-specific checking, using the current local PSC0
compiler, operation registry, diagram validator, graft validator and slice
analyzer. It is **not** a stable `Specialize` operation or stable certificate
type. It does not change `ProgramTerm`, `adva.ir`, existing native certificate
definitions, source files, Cargo manifests or locks. It creates no `Seal`,
equation cell, semantic epoch, optimizing `mix` or arbitrary world-fibre
specializer. The fixed external `adva-machine` consumer lock is unchanged;
this experiment does not claim execution by that separately pinned consumer.

The implementation lives at
`experiments/native_input_binding_certificate/native_input_binding_certificate.rs`.
The dedicated CI job copies it temporarily to
`crates/adva-lisp/tests/native_input_binding_certificate.rs` in its own checkout
and runs the existing locked Rust workspace. That staging is an integration
test mechanism, not a tracked crate or schema modification. It avoids altering
the historical source boundary of the frozen symbol-surface contracts.

## Declared identities and the frozen question

A caller's `ExpectedRequest` fixes the complete source diagram snapshot, the
expected residual qualified root and the normalized static `Rational` before
receiving a proposed certificate. The proposal cannot repin that question.

Identity qualification contains the checked root `QualifiedName`, exact
`SourceId`, local `OccurrenceId` and `OccurrencePath`. Source and residual
roots must differ. Dynamic source IDs are mapped explicitly; dynamic
occurrences must have identical copy paths, distinct targets and complete
target coverage.

The compiler starts node and occurrence counters from zero on each compilation.
Both contexts can legitimately contain `occ:0`. Distinct contexts are therefore
essential: this experiment does **not** assert globally new local counters,
cryptographic identity, cross-recompilation semantic freshness or an epoch
allocator. Source identity is not inferred from a value, a hash or equality of
local indices. Complete source snapshots also distinguish different bodies
that deliberately retain the same root names and occurrence IDs.

Current parser literals use the exact operation `adva.builtin/constant@2` with
the normalized rational parameter. This version is frozen explicitly. The
historical `OperationRef::constant` helper names `constant@1`; equal rational
parameters do not authorize exchanging those operation declarations.

## Certificate fields and receiver obligations

`ResearchCertificate` is a private research object. It retains:

- complete source and residual diagram snapshots;
- the static rational and its original bound source;
- the dynamic source correspondence;
- a complete ordered source-event to residual-body-event map;
- a complete qualified occurrence correspondence, with `None` only for
  occurrences of the bound static source;
- every forgotten static occurrence and every original static `Source` or
  `Copy` history entry;
- the one introduced binding event.

The receiver first checks fixed finite graph sizes and validates both diagrams.
It revalidates both supplied graft traces through full native slice analysis.
It then requires exactly one source root frame and one residual root plus one
call frame, checks that the call is bound to the source function and boundary,
and checks the whole callee-body event region.

For every original body event, the exact `OperationRef`, output types, ordered
input wires, input positions and lineage projection must match its mapped
residual event. Ordered outputs are checked separately. No copy, discard or
internal constant event is removed. Residual occurrence coverage is injective
and exhaustive; source occurrence coverage is exhaustive, including static
descendants.

## Exact observation law and retained forgetting

Let `rho` substitute the declared literal wire for source input 0, map source
input 1 to residual input 0, map all original event IDs, and transport dynamic
occurrences by their explicit source/path correspondence. Static source
lineage is omitted by this declared observation and retained in the certificate's
static ledger.

The checked law is equality of exact decorated operation/wire structure and
history under `rho`. Its cut-level form is:

```text
rho(source full slice)
  = residual body slice after the literal-prefix event is complete
```

The receiver checks all exact lower/upper cut incidences, changed boundary
incidences, through wires, internal events and projected body history.
Each diagram orders cut vectors by its own producer order. Their exact
incidences, including consumer endpoints, are compared without assuming those
two vector orders coincide. Function output order remains protected.

Binding a sourced input to a source-free literal changes lineage. For a copy
of the static input, the original `Copy` ancestry rows disappear from the
residual's native lineage history, but the copy operation itself remains.
Every such ancestry row and all its static occurrences remain in the forgotten
ledger. Dynamic copy parents, children and ordered branch paths remain mapped.
The original static input boundary also remains in the complete source snapshot.
No right to erase provenance or to identify source and residual is inferred.

This observation law is structural. No evaluator, `f64`, tolerance or sampled
numeric agreement enters the receiver. It does **not** establish a new exact
rational runtime, numeric equivalence of all Real evaluations, a universal
observation law, or an observer-language synthesis theorem.

## Frozen finite validation family and controls

The main source body is:

```lisp
(frontier
  (add (copy (use static)))
  (add (copy (use dynamic)))
  (discard 1))
```

It has six original body events, three static and three dynamic occurrences,
two static source/copy history rows, and a hidden constant-discard component.
The positive family fixes static values `0`, `7/3` and `-5/2`. Two additional
fixtures bind an explicitly discarded static input and a zero-event ordered
two-input frontier. The latter tests mapped through wires without inventing
body events.

Ten Rust test functions exercise that family and these controls:

- missing or reordered body event correspondence;
- omitted static descendants or static source/copy history;
- incomplete occurrence coverage, forgotten dynamic occurrences, wrong target
  context and altered dynamic copy paths;
- a changed source body with the same local identities, even after the proposal
  repins its own snapshots;
- changed ordered outputs and reordered graft holes;
- an otherwise validated `constant@1` prefix substituted for `constant@2`;
- changed static data with a self-consistent proposed static parameter, against
  the caller's unchanged question;
- deleted hidden discard or dynamic copy structure;
- zero or insufficient positive verification allowance;
- an otherwise valid graph exceeding the declared size profile.

The test family is validation of a fixed construction, not a search campaign.
Proposal authoring and fixture compilation occur before the receiver's
verification-work accounting and are not represented as free native execution.

## Budget, outcomes and exit

The receiver admits at most 17 total nodes per diagram, 32 occurrences, 64
history rows, two inputs, two outputs and two input wires per node. A certified
residual has one introduced literal event and at most 16 source-body events.
The admitted fragment has a call-free source and exactly one residual call.
These are fixed finite fixture/admission limits, not a hostile-input sandbox
or a general byte-memory bound.

Each normal receiving instance is supplied 512 verification-work units. The
counter charges source/residual node, occurrence and history record counts,
five top-level kernel calls, and the receiver's occurrence, event, wire,
cut-incidence and history comparisons. A kernel invocation costs one unit in
this convention: that unit does not count its internal instructions, CPU time
or bit complexity. The fixed graph sizes bound the admitted kernel inputs.
Fixture compilation, formatting, build and remote job scheduling costs are
separate engineering costs.

The result is exactly one of `Certified`, `Refused` or `Unknown`. Altered or
missing correspondence and invalid native artifacts are refused. Size-profile
or verification-work exhaustion returns `Unknown`; no partially verified
certificate is returned and no allowance is renewed inside a receiving call.
The remote verification job has a 15-minute timeout; no automatic research
retry or expansion of the finite family is part of this contract.

## Reproduction and current validation record

In a fresh checkout with the existing Rust toolchain/dependencies:

```sh
test ! -e crates/adva-lisp/tests/native_input_binding_certificate.rs
cp experiments/native_input_binding_certificate/native_input_binding_certificate.rs \
  crates/adva-lisp/tests/native_input_binding_certificate.rs
cargo test --locked -p adva-lisp --test native_input_binding_certificate \
  --test process --test graft_trace --test diagram_validation
```

Use an isolated checkout; remove the temporary test when finished. The
dedicated workflow also applies Rust formatting to the staged test and checks
Clippy with warnings denied. Its input/formatted source digests and exact
formatted bytes are retained in the job log, so formatting is distinguishable
from executing unchanged input bytes.

Local status: static review only; Rust checks NotRun. Static preflight found
and corrected a literal-version assumption (`constant@1` helper versus the
parser's frozen `constant@2`) before any native execution. No failed native
attempt is concealed by that correction. An independently tasked Codex agent
reviewed the correspondence and negative controls, but shares the assistant
origin and is not independent human review.

The receiver and producer use different local paths for construction versus
verification, but share the same Rust compiler, operation registry, diagram
validator and graft/slice kernel. This is not independent implementation of
those trusted kernels or a proof-assistant formalization.

## Remaining issue boundary

A passing remote run would support this one finite, Rust-checked input-binding
correspondence result. It would not close the entire observer-conditioned
specialization issue, install a stable native transformation certificate, or
prove general partial evaluation or arbitrary world-fibre residualization.

The next smallest obligation is a separately scoped reusable receiving
interface, with independently bound source and request snapshots and a
reviewed persistent certificate boundary. Stable specifications and toolchain
development belong in `mountain/adva-machine`; research-specific witnesses may
remain here under the existing knowledge/machine boundary. No such promotion
or repository transfer is performed by this calibration.
