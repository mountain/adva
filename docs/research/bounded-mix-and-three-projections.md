# Bounded input-binding mix and three code-producing projections

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized GitHub account
proxy. This does not imply his authorship, review or correctness guarantee.

## Question and boundary

Can an ordinary Adva program bind another program's static input, accept its own
implementation, and produce executable residuals, compilers and a compiler
generator? The [implementation](../../experiments/bounded_mix/README.md) is a
**conservative input-binding specializer**. It does not evaluate static arithmetic
or remove interpreter dispatch. The experiment checks the finite code-producing
equations; a general optimizing `mix` and unrestricted projection laws remain Open.

This follows the [structured bootstrap](bounded-self-compiler-and-futamura.md),
whose hand-written compiler and `C1 = C2 = C3` did not themselves implement the
second projection. The previous CI repair completed successfully before this
continuation: [main CI at 5274e9b](https://github.com/mountain/adva/actions/runs/35071935752).

The executable `mix` has 41 registers and 238 instructions. The existing Adva
self compiler compiled its structured source in 14,407 native instructions.
An independent receiver checked the complete source-to-target correspondence;
Rust replayed that compilation. Python provides source authoring, wire encoding,
loading and structural receiving. It performs no specialization during the
native runs. Rust remains the admission, execution and replay authority.

## Construction and observed equations

An admitted source program `q` expects a node tagged 42 containing `[s, d]`.
`mix` receives the same pair representation with `[wire(q), s]`. It emits an
ordinary program that receives `d`, constructs literal `s` with generic
instructions, builds the pair, and then executes the relocated original body.
Each original `input` reads the bound pair; every jump and branch destination
moves by the prefix length. All other instructions remain unchanged.

Sixteen scratch registers are appended to at most 48 source registers. Source
register names cannot start with `mix_`. Twelve depth-indexed stacks construct
static data: a node at depth 11 is refused, while an integer may occupy that
depth. The receiver recursively checks the literal prefix and every body
instruction; the Adva producer uses iterative work stacks. Their common author
does not constitute independent human review.

Write `emit(P, x)` for decoding the returned wire data from running `P` on `x`,
and `run(P, x).phase` for its terminal observation. Brackets abbreviate the
tag-42 pair. The checked construction is:

```
r     = emit(mix, [wire(I), p])
c     = emit(mix, [wire(mix), wire(I)])
cogen = emit(mix, [wire(mix), wire(mix)])

emit(c, p)             = r
emit(cogen, wire(I))    = c
run(r, d).phase        = run(I, [p, d]).phase
```

The first two equalities compare complete canonical target code, including
register declarations and control flow. The last compares exact returned data
or rejection reasons. Source and residual instruction counts are deliberately
different. The fixture family has two different interpreter implementations:
affine arithmetic with two coefficient programs, and tagged add/multiply/reject
with three programs. Branches, loops, repeated input and uninitialized-register
refusal have additional v1 controls.

This input-binding construction can preserve an admitted body without executing
it during specialization. Consequently it can be self-applied before there is a
complete Adva self interpreter. Specializing such a full interpreter remains a
separate, unmet dependency. This baseline also does not demonstrate that a
binding-time analysis can classify and evaluate `mix`'s own computation.

## Retained v1 obstruction and separate v2 continuation

The [original contract](../../experiments/bounded_mix/contract.json) declared a
six-call preflight and one campaign of at most 72 native calls, 1,200 wall seconds,
1,080 aggregate CPU seconds, 1 GiB address space and 256 MiB artifacts. Checking
and replay count within the campaign. Each run has at most 200,000 lifetime
instructions; no retry or automatic refuelling is permitted.

The preflight passed in 32.240 wall seconds. The v1 campaign completed 67 native
calls in 237.929 wall seconds and 231.898 aggregate CPU seconds. It received five
first/second code equalities, 18 terminal pairs and 16 structural receipts.
The generated affine and tagged compilers contain 656 and 791 instructions.

Third generation really ran, and was **rejected at instruction 58,551** with
`node arity exceeds 2048`. It did not return an admitted compiler generator.
An independent prediction gave 3,959 instructions, including a 3,721-instruction
literal prefix. Both the instruction vector and its encoded node exceed v1's
2,048 limit. The failed execution, prediction and residual are retained in
[`v1-attempt-01`](../../experiments/bounded_mix/evidence/v1-attempt-01/summary.json).

The [successor contract](../../experiments/bounded_mix/contract-v1.json) pins that
obstruction and its predecessor by digest. It permits one new 48-call campaign
with the same time, memory, artifact and per-run fuel limits. The
[v2 ADR](../adr/bounded-mix-self-application.md) preserves v0/v1 and changes only
version/profile markers plus instruction count and node/field arity to 4,096.
All 23 operations and the other capacities are unchanged. V2 uses exactly the
received mix body with explicit schema selection; the wire format contains no
profile marker. A v1 checkpoint cannot be resumed under v2.

The v2 campaign **passed all 48 native calls**, taking 439.802 wall seconds and
438.924 aggregate CPU seconds. The returned compiler generator
has 3,959 instructions and 57 registers, passed native admission, and generated
both interpreters' compilers. Two complete second/third code equalities and five
first/second code equalities passed. Ten terminal pairs agree, including checked
integer overflow and explicit rejection of the unsupported object tag.
Native receiving replayed 90,036 prior steps across generation, compiler runs and
the 17-step continuation. See the
[summary](../../experiments/bounded_mix/evidence/v2-attempt-01/summary.json) and
[cost record](../../experiments/bounded_mix/evidence/v2-attempt-01/cost.json).

The 57-register generated programs fit native execution's 64-register bound,
but exceed mix's 48-register source boundary. Thus these three constructions do
not establish closure under arbitrary further specialization.

Changing mix's actual pair-tag emission from 42 to 43 changed the generated code;
the structural receiver refused it, and the mutated residual returned the changed
tag. Changed fuel, a foreign v1 checkpoint, malformed input, zero fuel and a
4,097-field node exercised distinct refusal/exhaustion controls. These are actual
executed controls, not predictions from the independent construction.

Each completed run is retained in a complete archive with per-member sizes and
SHA-256 digests, checked before redundant loose files are removed. Source
snapshots, every program/input, stdout/stderr, complete native traces, final
states, receipts and failures remain recoverable. Regression tests recheck the
archives, code-producing equalities, receipts, controls, profile boundaries and
fixed costs. They do not launch a new research campaign. The historical source
snapshots precede post-run documentation and archive-checking code.

## Interpretation and remaining work

The residual retains interpretation and adds literal construction. For example,
the successful affine case takes 12 original instructions and 25 residual
instructions. This result supplies no execution-speed advantage over the Rust
VM and does not change the [earlier performance comparison](execution-performance-comparison.md).
The emitted compiler generator is a program that binds an interpreter into the
existing specializer; its name does not establish efficient compiler generation.

The next optimizing boundary needs explicit binding-time analysis, residual
environments, checked static evaluation and dynamic control-flow residualization.
It must preserve overflow and rejection behavior, terminate or return Unknown
under a fixed budget, and handle its own implementation before an optimizing
second/third projection claim is made. A full interpreter, loader boundaries,
native transformation certificates and an unrestricted correctness theorem remain
open. No `SourceId`, `OccurrenceId`, stable PSC0 operation or native `Seal` is
created by the external structural receipts.

An initial host import collision selected an older experiment's `fixtures`
module. Package-qualified imports fixed it before native execution. The v1
capacity refusal is a distinct, retained native outcome. Neither is erased or
counted as a successful third projection.

During integration, one pytest command named the nonexistent
`test_research_index.py` and collected no tests. Correcting it to
`test_research_index_consistency.py` produced 49 passing related tests. This was
a test-command error and did not repeat either finite campaign.

Integration checks passed `cargo fmt --check`, workspace Clippy with warnings
denied, the Rust workspace tests, and a subsequent v2 CLI regression executing
an actual emitted residual, replaying it, preserving continuation fuel and
refusing output overwrite. The archive/source/receipt regressions are separate
from the finite research runs and are not included in their recorded timing.
