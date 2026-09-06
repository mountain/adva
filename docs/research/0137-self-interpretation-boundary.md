# Research 0137: Forming the self-interpretation boundary

Date: 2026-09-06. Status: completed native capability audit; self interpretation Unknown.
Base: main `57c1d04bcfe51b82f6e559a61ca02e668f630b5a`.

## Motivation and current evidence

Mingli proposes a directed interpretation cycle with fixed entry `adva.adva`,
a normalized self reading that may become learn, and a boundary forbidding
the production of `adva.adva.adva`. He asks how representation, rename, forget,
divide, break, breakthrough, free and Universe belong in this process.

Draft PR 136 produced a native six-call p -> 2p -> p arithmetic witness.
Its final head `4cbbfebfead3918b4da46920d55708d10f3baee8` now passes all
three workflows. It remains unmerged. Its learn.adva is a Transition record,
not an interpreter or a learned method. This independent branch uses main's
Lisp compiler and observer APIs; it does not import draft 136 as a dependency.
Other drafts 130--135 are contextual finite calibrations, not merged results.

The agenda already puts finite tagged data and case/fold semantics before a
bounded arithmetic evaluator, and representable specialization before
self-application. This audit checks the first missing interfaces; it does
not authorize a stable grammar extension or bypass that dependency order.

## Frozen native question

Run exactly the seven source texts described by
`0137-self-interpretation-run-contract.json`: one named-composition module,
four rejected language interfaces, and two history-distinguishing programs.
No expression search or additional route is needed. The current native
ValueType admits Real and Bool; the builtin registry is authoritative.

The example uses `parse_module`, `link_modules`, `compile_function`,
`evaluate`, and `observe_history`. It can show that def/call express composite
words, that selected runtime-code and control proposals are rejected, and
that equal values can conceal distinct histories. It does not establish that
no alternative encoding could ever work. These are concrete interface gaps,
not an impossibility theorem about self interpretation.

The fixture in `programs/self-boundary/words.lisp` names five finite functions:
forward, reverse, self, observe and learn. Self is a finite composition,
reverse(forward(x)); learn calls observe on that composition. These names test
ordinary user-defined vocabulary. They are not recursive self interpretation,
a general observation operator, a newly synthesized learning method, or a
native CLI dispatch. The Rust wrapper remains external orchestration.

The numeric readings use the existing f64 realization at 2 and 3, with scale
factors 2 and 1/2. These values are exactly representable. This is not a new
exact-integer interpreter or the arithmetic witness kernel's M=1 judgment.
The history distinction is structural and does not rely on a float tolerance.

## What a genuine self interpreter must provide

Let L be a declared typed sublanguage, repr its finite program representation,
Q the selected observations, and I an interpreter whose own code belongs to L.
A future target is an observation-preserving interpretation relation:

\[
 Q(run_L(I,\langle repr(p),x\rangle,F_I))
 = Q(run_L(p,x,F_p)).
\]

Specify the admissible p and x, result/status types, source correspondence,
and sufficient interpreter fuel separately from direct execution fuel.
Matching Unknown outcomes is not evidence of successful interpretation.
Applying I to its own representation additionally needs a well-typed input
encoding within the declared size/depth boundary. A loader that selects a
hard-coded Rust function by JSON schema does not satisfy this condition.

Three capabilities need definitions before more vocabulary can solve this:

1. **Representation:** finite typed program data, with explicit encoding and
   validation. Quote is one possible surface name, not a required spelling.
2. **Construction and structural inspection:** construct syntax and inspect
   its tagged cases. Existing generate/divide ideas can name these directions;
   their input/output types and coverage obligations must be stated.
3. **Bounded control:** a step/continue protocol with state, residual, fuel
   and explicit suspension. It must not be implemented by ignoring the
   current prohibition on recursive PSC0 compilation.

An interpreter may then be written using those facilities and compared with
the Rust reference implementation. Only after that comparison includes the
interpreter's own program can self interpretation be claimed. Even then,
learn requires an evidenced change that affects a later observation, method
selection, generated candidate or retained residual. Renaming an unchanged
cycle, or obtaining a scalar M=1, does not itself supply that change.

## Fixed entry, changing state, and representation

The proposed file arrangement separates four roles:

| Stable path | Role | Current status |
| --- | --- | --- |
| adva.adva | Versioned interpreter program | Construction target; not generated by this audit |
| state.adva | Current bounded execution state | Proposed |
| trace.adva | Retained transitions and residuals | Proposed for this interpreter |
| learn.adva | A validated resulting method or witness, with explicit type | PR 136 currently supplies the witness reading only |

Repeated interpretation changes state and appends bounded trace data, not
the entry's suffix. The proposed writer must accept explicit fixed roles;
it must never derive output by appending `.adva` to its input path. A full
trace store also needs a finite capacity and a suspend/export policy.
The audit itself emits only `self-boundary.json`; it does not create a dummy
adva.adva and misrepresent that file as an interpreter.

Rename has two different cases. A display alias may refer to the same pinned
program. A changed program representation requires explicit name/binding and
source correspondence, preserved observations and retained cost. A filename
or hash is not a semantic SourceId; renaming cannot reset fuel, erase a
failure, or promote a witness schema into a callable method schema.

## Forget, divide, break, and breakthrough

For a proposed summary q:H -> S, current observation preservation asks for
Q = Qbar composed with q. If two histories have the same q but differ under a
protected observer, q is insufficient for that observer. The native example
uses the same qualified function name and input port in two separate checked
compilations: id(x) and neg(neg(x)) have equal scalar observations but different
retained histories. Their equality does not authorize an identity cell.

If q is noninjective, no function can reconstruct every original history from
q alone. A residual may retain the discarded distinction, but its storage and
replay still cost resources. For continuing computation, preservation of the
current value is weaker than preservation of future permitted actions:
equal summaries must support compatible next steps, guards, costs and
observations. A change of Q can require reopening the forget judgment.

| Working word | Proposed operational boundary |
| --- | --- |
| forget | Declare what is omitted and which observers remain valid; retain the necessary residual or refuse |
| divide | Split an obligation into typed parts with coverage, resource allocation and recombination conditions; not automatically arithmetic division |
| break | Suspend this attempt with its frontier, cause and remaining fuel; it does not erase the obstruction |
| breakthrough | Existing bounded attempt to repair one exposed obligation; never a promise of positive closure |

These roles do not require four more stable primitives. Existing observation,
boundary, residual, continuation and verification facilities should carry
them where those facilities are actually implemented.

## Free and Universe: a useful calibration, not an identification

One mathematical reading worth considering is the classical free--forgetful
adjunction. For the one-sort monoid example, assigning meanings to generators
extends uniquely to a homomorphism from the free monoid of finite words:

\[
 Hom_{Mon}(F(X),M) \cong Hom_{Set}(X,U(M)).
\]

This connects compositional interpretation with a universal mapping property.
It is formalized in the primary mathlib sources as
[MonCat.adj](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Algebra/Category/MonCat/Adjunctions.html)
and [FreeMonoid.lift](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Algebra/FreeMonoid/Basic.html)
(consulted 2026-09-06). Adva's typed directional vocabulary would need its own
declared carriers and composable morphisms before importing any such property.

Three distinctions matter. U forgets specified algebraic structure while
retaining the underlying carrier; it is not the deletion of execution history.
An adjunction is not a pair of inverse programs. And finite words over a
finite nonempty alphabet form an infinite set: words of length at most N
are generally not closed under concatenation. The N=2 words aa and bb already
concatenate beyond the bound. A finite runner must refuse or suspend at that
boundary, not silently truncate and claim the full universal property.

Universe should name a declared scope of objects or questions, for example
U_B at boundary B. It should not silently mean every open-world possibility,
all representation levels, or a proved universal ambient space. A proposed
operational free_(B,Q) may mean admissible transformations preserving Q and
the resource contract. This operational reading and an algebraic free object
are separate hypotheses until a correspondence is supplied.

## Reproduction, result and next step

```sh
cargo build --release -p adva-lisp --example observe_self_boundary
mkdir -p target/self-boundary
timeout 30 target/release/examples/observe_self_boundary \
  --output target/self-boundary/self-boundary.json
```

The dedicated CI additionally bounds virtual memory to 256 MiB and the job
to ten minutes. Existing output paths must be refused. Native execution
succeeded in the bounded run recorded below. Outputs retain source texts,
errors and history observations so a
later run can reconstruct the finite checks. Timings are observations, so
replay is a repetition of the checks rather than a byte-identical benchmark.

The next minimal engineering decision is a small typed Code representation
with three constructors (literal, add, multiply), a structural inspection
rule, and a fuel-bounded evaluator contract. First implement and compare that
evaluator in a research companion. Only then enlarge the admitted language
enough to express its own evaluator, with a separate typing and resource gate.
This order exposes what remains, rather than hiding the gap inside a host
dispatcher. It helps Mingli and later agents choose the actual next language
feature; practical value on Jiamin's task remains unmeasured.

## Native result and actual cost

[Draft PR 137](https://github.com/mountain/adva/pull/137) retains this independent
change. [Native run 34031716645](https://github.com/mountain/adva/actions/runs/34031716645),
job 101482337806, succeeded on source commit
`ac19f682d7785102434a4fc5b1425669d6bc4e55` after rustfmt. Clippy, release build
and all six audit groups passed. The separate ordinary formatting gate failed
on the first commit; the captured formatting is applied in the next commit.
No behavior fix or second research execution was required. Once the artifact
exists, the dedicated workflow skips another audit for formatting changes.

The exact native output is `0137-self-boundary-observation.json`, 12,561 bytes,
SHA-256 `4e4ec48a1ee7c85ff75a753c2df5375780102bc4d3ca7aec0552f63d6da66871`.
It contains all seven source texts, complete native history observations,
evaluation/compilation certificates and the exact four refusal messages.
Log extraction removed only a separately labelled stderr byte-count line
interleaved before the JSON; the saved bytes match the runner's SHA-256.
The [run archive](https://github.com/mountain/adva/actions/runs/34031716645/artifacts/9988835801)
also retains the outer GNU time report under seven-day retention.

Actual work: three successful compilations, one rejected compilation, three
rejected parses, eight compiled nodes, four evaluations and three history
observations. The named composition returned 2 and reused the same compiled
diagram to return 3. The two counterexample histories contain two and three
events respectively, although both scalar readings are 2. The self interpreter
status remains Unknown. These rejections do not justify an unrestricted
impossibility claim or a replacement of existing stable semantics.

| Component | Measured seconds |
| --- | --- |
| Native parse total | 0.000058879 |
| Native link total | 0.000008654 |
| Native compile total | 0.000125059 |
| First and counterexample evaluations | 0.000018718 |
| Fresh-input reuse evaluation | 0.000006069 |
| Native history observations | 0.000001492 |
| Evidence construction | 0.000061213 |
| Whole audit | 0.000304150 |
| Serialization | 0.000035804 |
| File write and sync | 0.010774428 |
| Outer supervised wall time, coarse GNU time reading | 0.01 |
| Clippy including its compilation | 7.31 |
| Release build | 19.78 |

Whole-audit time includes the listed inner work and is not added to it again.
The runner reports maximum RSS 3420 KiB for the supervised process and exit
status zero. This is not total CI memory or a file-size-derived estimate.
Outer timing precision is coarser than the internal measurements. Editing,
network and total research wall time were not measured. No speedup or
expression-power increase is inferred from these small timings.
