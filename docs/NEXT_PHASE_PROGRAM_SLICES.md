# Next-Phase Task Brief: Exact Graft Frames and Program Slices

Status: approved next-phase handoff after PR #23. This document is written so
that an implementation agent can begin without reconstructing the preceding
theoretical discussion from conversation history.

The task is structural. Do not add numerical experiments, matrix APIs,
complex scalars, process exponentials, resolvents, or spectra in this phase.
Longer-term directions are preserved in `RESEARCH_ENGINEERING_AGENDA.md`; they
do not widen this task.

## 1. Mission

Extend the finite Rust semantic kernel so that it can represent and certify:

1. the nested program-substitution frames produced by typed calls; and
2. the exact open program between two certified causal cuts of one unchanged
   checked diagram.

The intended common object is a finite `ProgramSlice`. K, C, and F are three
readings of that object:

- K: graft frames, ordered holes, and substitution nesting;
- C: event dependency and causal development;
- F: lower/upper cuts and reverse boundary organization.

Do not implement K, C, and F as three duplicated semantic stores.

## 2. Mandatory reading before design or code

Read each file completely, in this order:

1. `AGENTS.md`
2. `README.md`
3. `docs/ARCHITECTURE.md`
4. `docs/SEMANTIC_SCOPE.md`
5. `docs/PROGRAM_PROCESS_CORE.md`
6. `docs/TECHNICAL_REPORT_PROGRAM_PROCESS_CORE.md`
7. `docs/claims.toml`
8. `docs/adr/0001-rust-semantic-authority.md`
9. `docs/adr/0004-frontier-before-compiled-presentations.md`
10. `docs/adr/0005-checked-diagram-import.md`
11. `docs/adr/0006-program-process-before-projections.md`

Then inspect at minimum:

- `crates/adva-ir/src/term.rs`
- `crates/adva-ir/src/diagram.rs`
- `crates/adva-ir/src/process.rs`
- `crates/adva-ir/src/certificate.rs`
- `crates/adva-lisp/src/compile.rs`
- `crates/adva-lisp/src/process.rs`
- `crates/adva-lisp/src/validate.rs`
- `crates/adva-lisp/tests/process.rs`
- the Python causal-cut facade and tests.

Do not infer semantic authority from Python research fixtures.

## 3. Baseline facts that must not be reopened silently

- The native object is an open finite program, not a value or matrix.
- Function inputs are ordered holes.
- `ProgramTerm::Call` is finite typed simultaneous substitution.
- Sharing and discard are explicit program operations.
- Rust is the sole semantic authority.
- Source and occurrence identities are explicit and must survive unchanged.
- A causal past is a downward-closed node set.
- A causal cut is derived from exact crossing wires.
- Scalar evaluation is an observation and currently realizes `Real` as `f64`.
- Structural judgments must not depend on evaluation, floating-point equality,
  tolerances, or analytic truncation.
- The current JSON IR remains version 1 unless a separate, explicit versioning
  decision is approved.
- Current matrix-like and expression-valued backward constructions are bounded
  research witnesses, not stable ontology.

## 4. Target definitions

The exact field names remain a design decision, but the following information
must be representable.

### 4.1 GraftTrace

Compilation should produce a deterministic companion trace containing a root
frame and nested call frames.

Each `GraftFrame` needs enough information to distinguish:

- deterministic frame identity and scope path;
- parent/child nesting;
- caller and callee;
- ordered callee holes;
- the argument-producing region bound to each hole;
- the instantiated callee-body region;
- entry wires and exit wires;
- the corresponding call history event;
- nested calls inside arguments and inside the callee body.

Do not collapse argument regions and callee-body regions into one unlabelled
node set.

The first implementation should accompany `CompilationArtifact`; it should
not reinterpret stored `adva.ir` version 1 diagrams.

### 4.2 ProgramSlice

For one validated diagram `P` and downward-closed node sets `U <= V`, a
`ProgramSlice(P, U, V)` must retain:

- lower cut `cut(P, U)`;
- upper cut `cut(P, V)`;
- original events in the set difference \(V\setminus U\);
- lower-boundary wires consumed inside the slice;
- upper-boundary wires produced inside the slice;
- through-wires crossing both cuts unchanged;
- internal events whose effects do not reach the upper frontier;
- exact original identities and lineage;
- intersecting graft frames or explicit links to the graft trace.

Represent the slice as an identity-preserving view of the original diagram.
Do not lower it again as a fresh program during the exact phase.

### 4.3 Slice composition

For `U <= V <= W`, define composition from the two adjacent slices without
recompilation, new semantic IDs, numerical evaluation, or tolerance.

The result must agree with the directly derived `ProgramSlice(P, U, W)` under
a canonical exact comparison.

## 5. Required laws and certificates

At minimum, implement or explicitly reject the following obligations.

### 5.1 Identity

`slice(P, U, U)` has no events, has the same lower and upper cut, and preserves
all through-wire identities.

### 5.2 Event conservation

For `U <= V <= W`, the event sets of `slice(U,V)` and `slice(V,W)` are disjoint
and their union is exactly the event set of `slice(U,W)`.

### 5.3 Boundary agreement

The upper cut of `slice(U,V)` is exactly the lower cut of `slice(V,W)`.

### 5.4 Exact composition

Composing adjacent slices yields the direct outer slice with the same original
nodes, endpoints, sources, occurrences, paths, histories, and lineage.

### 5.5 Associativity

For `U <= V <= W <= X`, the two parenthesizations of three slice compositions
must produce the same canonical exact result.

### 5.6 Structural operations

Copy and discard must remain explicit events. Composition must not turn copy
into aliasing or erase a discarded internal event merely because it has no
upper-boundary value.

### 5.7 Certificates

Every public semantic analysis or composition returns result plus certificate.
Certificates should state only checked finite facts, including as applicable:

- diagram integrity;
- lower and upper past closure;
- past inclusion;
- event partition;
- boundary agreement;
- original-ID preservation;
- lineage preservation;
- graft-frame consistency;
- exact composition.

Do not use a boolean to stand for an unrestricted theorem.

## 6. Work packages and dependency order

### WP0: red-team the definitions

Before stable types are chosen, write minimal examples for every fixture in
section 7. Determine:

- whether `GraftFrame` regions are nested, disjoint, or may overlap;
- whether every frame has canonical entry and exit causal pasts;
- whether every syntax frame induces one program slice;
- whether arbitrary cuts correspond to no syntax frame;
- whether equal frontier snapshots can hide different completed histories.

Record counterexamples. Do not repair a failed conjecture by silently
weakening a test.

The bounded E0 dual-cut calibration in
`docs/research/0020-e0-dual-cut-surgery.md` is a WP0 companion result.  On one
declared planar fork-recombine embedding it identifies every Rust-certified
cut with a decorated mod-two dual cycle and every enabled event with one
dual-face boundary surgery.  It also gives two constraints for WP1--WP3:

- a bare terminal cycle cannot replace the event content of a slice, as an
  internal constant followed by discard can leave the same frontier; and
- the desired expression-level `P S P*` factorization cannot be tested until
  ordered argument regions and callee-body boundaries are present in the
  graft trace.

This research witness does not satisfy the phase exit condition, define a
canonical E0 grid, or authorize a stable dual-cycle or `P*` API.

### WP1: compiler-emitted graft trace

Add IR-level companion result and certificate types, then make Rust lowering
emit deterministic nested frame data.

Requirements:

- frame IDs are derived from stable compilation paths, never addresses;
- argument order follows the declared hole order;
- child frames retain their exact parent and region role;
- call stack failure cannot leave a partially authorized artifact;
- existing compilation behavior and diagram semantics remain unchanged.

At the end of WP1, decide whether the trace is sufficient. Do not yet change
the serialized diagram schema.

### WP2: exact program-slice analysis

Add an API tentatively named

```text
analyze_program_slice(diagram, lower_completed, upper_completed)
```

It must validate the diagram, validate both causal pasts, validate inclusion,
and derive the complete slice data without evaluation.

Reuse the existing causal-cut implementation rather than duplicating frontier
logic.

### WP3: exact slice composition

Add a composition operation or verifier for adjacent same-diagram slices. The
operation must retain original identities and return a certificate.

Prefer a canonical view/union construction over materialization as a new
diagram. If a materialized diagram is also useful, keep it a later compiled
presentation with an explicit identity map.

### WP4: exhaustive finite tests

Build hand-written fixtures and, where practical, exhaust all downward-closed
sets and nested triples in small checked diagrams.

Tests must compare exact Rust data. They must not call scalar evaluation as an
oracle for structural composition.

### WP5: read-only Python facade

Only after the Rust API and tests are stable, expose typed read-only adapters
for inspection. Python must not reconstruct slices, frames, or certificates.

### WP6: claims, ADR, and promotion decision

Update `claims.toml` with exact finite claims and precise counterexample
boundaries. Add an ADR if a new stable artifact boundary is introduced.

Only after the evidence is complete should the project decide whether graft
frames belong in a future `adva.ir` version 2.

## 7. Mandatory fixtures

The test suite must cover all of the following.

1. **Identity-only program**
   - no operation events;
   - nonempty boundary;
   - identity slice retains through wires.

2. **Explicit copy**
   - one source produces distinct child occurrences;
   - child lineage remains distinct across cuts and composition.

3. **Explicit discard**
   - a slice contains an event with no upper-frontier wire;
   - the event is not erased from the slice.

4. **Internal constant**
   - zero-input event appears inside a slice;
   - enabling and event partition remain exact.

5. **Independent diamond**
   - two events are simultaneously enabled;
   - alternative schedules retain distinct step histories;
   - the containing slice retains the common partial order.

6. **Through wire**
   - one wire appears unchanged at lower and upper cuts while other events
     execute.

7. **Nested calls**
   - caller, argument subprogram, callee body, and nested child call can be
     distinguished in the graft trace.

8. **Ordered multi-output frontier**
   - hole binding and boundary ordering survive slicing and composition.

9. **Equal frontier, different event past**
   - demonstrate explicitly why a frontier snapshot does not identify a
     process interval.

10. **Equal value, different program**
    - existing K2-style examples remain distinct under frames and slices.

## 8. Floating-point and truncation acceptance rule

This phase must pass with structural tests that do not evaluate any `Real`
value.

It is acceptable for the existing full test suite to continue testing `f64`
evaluation. It is not acceptable for new frame, cut, slice, or composition
tests to use:

- approximate equality;
- an epsilon;
- numerical Jacobians;
- matrix multiplication;
- a finite series approximation;
- a convergence threshold.

If implementation appears to require one of these, stop and report the hidden
observation assumption. Do not embed it in the core.

Future analytic work must introduce explicit observation and truncation
policies with remainder certificates. It is outside this task.

## 9. Decisions that require a separate approval

Stop and request review before doing any of the following:

- changing the meaning or schema version of stored diagrams;
- adding local binders, recursion, or cyclic programs;
- making `GraftTrace` or `ProgramSlice` depend on Python;
- creating a stable probe or `D*`/pullback API;
- introducing matrix, vector, covector, algebraic-module, or manifold ontology;
- adding a foundational complex scalar type;
- adding process exponential, resolvent, eigenvalue, or spectrum types;
- identifying programs from equal values, frontiers, gradients, or numerical
  observations;
- deriving an equation or coherence cell from successful tests.

## 10. Expected deliverables

The phase is complete only when it contains:

1. a written definition and counterexample analysis;
2. Rust `GraftTrace`/`GraftFrame` companion artifacts with certificates;
3. Rust `ProgramSlice` analysis with certificates;
4. exact adjacent-slice composition or an explicit counterexample showing why
   the proposed law must be weakened;
5. mandatory fixture tests;
6. exhaustive nested-cut tests on at least one nontrivial small diagram;
7. read-only Python exposure, if and only if the Rust interface has stabilized;
8. updated architecture, semantic scope, claims, and ADR documentation;
9. passing format, Clippy, Rust tests, and Python version-matrix CI;
10. a final report separating established facts, bounded evidence,
    counterexamples, and remaining conjectures.

## 11. Acceptance criteria

The implementation is accepted when:

- every semantic identity originates in Rust;
- no structural judgment depends on values or floating point;
- slices retain internal discarded events;
- through-wires are explicit;
- copy lineages remain distinct and source-related;
- nested composition is exact on original IDs;
- associativity is tested on nested quadruples;
- graft frames distinguish ordered arguments from callee bodies;
- existing `adva.ir` version 1 semantics remain unchanged;
- all new public results carry certificates;
- claims state finite scope and no-go boundaries;
- CI is green.

## 12. First mathematical checkpoint

The first checkpoint is not "prove time-space duality." It is:

> For one validated finite program and nested causal pasts, can exact program
> slices be composed while preserving every original semantic identity and
> every internal event?

Only after that checkpoint passes should the project ask:

> Which grafting frames correspond to which program slices, and does nesting
> reverse exactly, faithfully, or only partially?

The answer may be a theorem, a restricted theorem, or a finite
counterexample. All three outcomes are useful if recorded precisely.

## 13. Required completion report format

The implementing agent's final report must include:

- baseline commit and PR;
- exact files and public APIs changed;
- laws implemented;
- counterexamples found;
- whether the original scope/cut intuition survived unchanged, weakened, or
  failed;
- why no numerical tolerance was needed;
- CI run and result;
- the single highest-priority remaining obligation.
