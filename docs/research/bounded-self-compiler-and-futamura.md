# A bounded self compiler and the Futamura dependency ladder

Authored by ChatGPT (OpenAI), submitted through Mingli Yuan's GitHub account as
an authorized proxy. Neither account ownership nor this attribution is review or
a correctness guarantee. The finite checks, counterexamples and residuals below
are the evidence. Date: 2026-09-15.

## What is being constructed

The existing PSC0 compiler lowers finite acyclic Real/Bool programs. M6 also names
a crossing `compile`; that name does not implement compilation. The new experiment
implements a compiler for a **separate structured Adva research subset** with
integer, Boolean, tree and stack registers, generic primitives, `Seq`, `If`, and
`While`. Its entire compiler source is an ordinary program in that same subset.
This is a bounded source-to-bytecode compiler, not a compiler for every Adva
surface or a change to stable PSC0 semantics.

The [compiler source](../../programs/bounded-self-compiler/compiler.source.adva)
contains no embedded prebuilt compiler and no host `compile` callback. Its
[authoring script](../../experiments/bounded_self_compiler/author.py) creates the
readable structured source; it is not involved in native compilation. An external
Python seed emits instructions and patches addresses. In contrast, the Adva
compiler traverses encoded source with explicit stacks, counts block sizes,
computes branch targets and constructs instruction data. The codec only changes
representation; it cannot resolve addresses or generate control flow.

The compiler has 35 registers and lowers to 257 generic instructions. Its data
wire input includes the program name, register declarations and source body.
Names and declarations pass through as data. A native compilation returns the
complete encoded target module. A structural decoder produces target JSON;
Rust then admits its types, indices, shapes and capacities before running it.
Well-formed source construction is an explicit external frontend boundary;
passing an arbitrary data tree to the compiler is not native source admission.
The admitted target must have in-range jump destinations and a terminal final
instruction. The fixture/compiler sources use an explicit final terminal
primitive outside their structured controls. No implicit terminal instruction
is appended: a source ending directly with a structured branch can be refused
if its generated exit target falls past the code, even if that jump would be
unreachable. General source-language admission/completeness remains a residual.

The [v1 research machine ADR](../adr/bounded-self-compiler-research.md) adds four
generic operations and explicit finite capacity limits. The v0 VM, arithmetic
interpreter and their recorded source-bound profiles stay byte-for-byte frozen.
The v1 capacity is fixed per profile: it is neither infinite storage nor an
argument for Turing completeness.

## Integration with the later v0 capacity work

Main `4027933` also contains the [v0 capacity preflight](self-interpretation-capacity-preflight.md)
and [subset scaling preflight](self-interpretation-scaling-preflight.md), received
on 2026-09-16 before integrating this compiler. Their unchanged v0 ceilings and
partial object-grammar results remain valid. This compiler uses the explicitly
separate v1 profile to cross the measured capacity barriers; it does not claim
that the old v0 machine could already run this compiler.

| Quantity | Frozen v0 limit | Separate v1 limit | This compiler |
| --- | ---: | ---: | ---: |
| Registers | 16 | 64 | 35 |
| Target instructions | 128 | 2,048 | 257 |
| Input data nodes | 127 | 16,384 | 1,354 |
| Input data depth | 12 | 48 | 26 |
| Largest input node arity | 8 | 2,048 | 35 |
| Lifetime instructions | 2,048 | 200,000 | 34,135 per self compilation |

These are fixed finite profile bounds and one received compiler, not a universal
machine claim or a full self interpreter. The v0 partial meta interpreter does
not cover the full structured v1 source language required by the next Futamura
step.

## The bootstrap check and its limits

Let `S` be compiler source and `C0` the external seed compiler. The intended chain
is:

```
C0(S) = C1
C1(S) = C2
C2(S) = C3
```

Equality here is canonical target-module byte equality, including register
declarations and code. Compiler execution on `S` is native data-machine v1
execution. This equality is necessary evidence of closure, but alone it could
also hold for a wrong compiler. Consequently every stage has a separate
[structural receiver](../../experiments/bounded_self_compiler/checker.py) that
checks all primitive leaves, block intervals, generated branches and loop back
edges without invoking the seed or Adva compiler. Its receipt binds the source
and target with SHA-256 and lists the block correspondence.

The receiver is a Python research checker, not a native transformation
certificate. Instruction positions and AST paths are research coordinates, not
`SourceId`, `OccurrenceId`, or `GraftTrace`. Rust remains the native execution and
target-admission authority. Native receiving fully reconstructs prior execution
from independently supplied program, input and original lifetime fuel.

A separately implemented direct AST evaluator runs fixture control structurally,
without lowering. It checks terminal data/rejection and the ordered primitive
register states against the generated target. A source `If` or `While` corresponds
to several target instructions, so full history and instruction fuel are **not**
asserted equal. Compiler, target, receiving and host resource costs are counted
separately. Exhaustion leaves the corresponding computation Unknown; it is not
proof of source divergence or a correctness counterexample.

The [successor frozen contract](../../experiments/bounded_self_compiler/contract-v1.json)
allows exactly one primary/fresh full attempt. Each process has at most 48 native
launches, 200,000 lifetime instructions per run, 2,000,000 reference work units,
600 wall seconds, 540 aggregate CPU seconds, 1 GiB address space and 256 MiB of
artifacts. Checking and continuation replay consume these same process budgets.
Builds, unit tests and later receiving regressions are separate finite checks.

The complete retained outcomes are in
[execution.json](../../experiments/bounded_self_compiler/evidence/attempt-2/execution.json)
and [results.json](../../experiments/bounded_self_compiler/evidence/attempt-2/results.json).
The [failed first full attempt](../../experiments/bounded_self_compiler/evidence/attempt-1/execution.json)
stopped after 34 native calls when the mutation visitor incorrectly received the
module envelope instead of its body (`KeyError: kind`). Its archive and frozen
sources remain historical. `contract-v1.json` allocates one replacement pair with
the same family and resource limits, after a separately bounded mutation preflight.
The fix changes the campaign entry into its mutation helper; neither the Adva
compiler nor Rust VM changes. The original attempt is not reported as passed.

## Executed result

The successor attempt passed in both fresh processes. Each process made 46 native
CLI calls, received 24 structural compilation receipts and checked the same ten
fixtures. `C1`, `C2` and `C3` have identical canonical target bytes. Each native
self compilation used **34,135 instructions**; each stage receipt contains 266
source blocks. Two full native receptions plus prefix reception during resume
verified **68,287 prior steps per process**. This count covers successful native
receptions, not an asserted exact total of work inside refused receptions.

The independent Python receiver checked **146 fixture state transitions**, and
the direct source observer matched **99 ordered primitive events** per process.
The compiler source itself was also evaluated directly on the literal fixture,
matching the native compiler output after 76 primitive source events. Eight
fixtures returned and two rejected (overflow and negative dynamic index).
`9007199254740993 + 2` returned `9007199254740995` exactly. A 17-step prefix followed
by continuation matched the uninterrupted complete trace and final state.

Changing a branch-construction tag in compiler source changed the generated
compiler; running that compiler on an `If` fixture produced instruction data the
structural decoder refused. A separately altered target branch failed block
correspondence. Changed original fuel, input and trace were refused; zero-fuel
and bounded-loop runs exhausted their fixed budgets; static type errors and
output overwriting were refused. These controls establish the reported finite
behavior, not an unrestricted compiler theorem.

| Process | Wall seconds | CPU seconds including native children |
| --- | ---: | ---: |
| primary | 59.078 | 57.926 |
| fresh | 54.186 | 54.158 |

The supervisor used 116.240 wall seconds including the two campaigns and archive
receiving; source snapshot copying occurs before that timer starts, despite the retained
JSON key containing the words `including_freeze`. The actual code boundary
governs this timing statement. Per-process
costs begin at `Trial` construction, include source/data writes, native runs,
checking and continuation, and end before writing the final cost record. The
archives contain all 267 files per process (about 33.09 MB uncompressed each).
Independent implementations here share one assistant author and do not imply
independent human review. No speedup comparison was performed.

## Bringing in all three Futamura projections

The project's [research agenda](../RESEARCH_ENGINEERING_AGENDA.md) already names
the Futamura route. This experiment supplies a self-compiling substrate; it does
not retroactively turn that agenda into an executed specializer.

Use `T` for the implementation/residual language and `L` for an object language.
Let `I_L` be an interpreter written in `T`, with the convention
`I_L(p, x) = observation of L-program p on dynamic input x`. A specializer `mix`
written in `T` consumes a `T` program and its static argument, returning a `T`
residual program for the remaining dynamic argument. Its correctness condition is

\[
\operatorname{Obs}(\llbracket \operatorname{mix}(q,s)\rrbracket_T(d))
=\operatorname{Obs}(\llbracket q\rrbracket_T(s,d)).
\]

This is a conditional semantic law over the admitted inputs and declared
observer. Refusal, effects, resource exhaustion and residual costs must be
specified; equality of a few answers does not establish the unrestricted law.
The returned residual must come with a checkable correspondence receipt.

| Construction | Executable expression | Required meaning |
| --- | --- | --- |
| First projection | `p_T = mix(I_L, p_L)` | Specialize an interpreter to one object program; run the residual on `x`. |
| Second projection | `compiler_L = mix(mix, I_L)` | Specialize the specializer to an interpreter; the result accepts object programs and emits residuals. |
| Third projection | `cogen = mix(mix, mix)` | Specialize the specializer to itself; the result accepts interpreters and emits compilers. |

The corresponding equations, under the same observer and representation
conventions, are:

\[
\begin{aligned}
\llbracket p_T\rrbracket_T(x)
&\simeq \llbracket I_L\rrbracket_T(p_L,x),\\
\llbracket compiler_L\rrbracket_T(p_L)
&\simeq \operatorname{mix}(I_L,p_L),\\
\llbracket cogen\rrbracket_T(I_L)
&\simeq \operatorname{mix}(\operatorname{mix},I_L).
\end{aligned}
\]

For code-producing equations, `simeq` first needs a declared code observer:
byte equality is one strong choice; certified equivalence of residual behavior
is another. Neither code equality nor state hashing allocates native identities.
The second and third equations are well-typed only if `mix` can process its own
implementation language, data representation and static/dynamic binding pattern.
A specializer implemented in Python is not automatically self-applicable through
a compiler implemented in Adva. Self compilation and specializer self-application
are distinct closure requirements.

The type discipline and diagrammatic account above follow Williams and Perugini,
[*Revisiting the Futamura Projections: A Diagrammatic Approach*](https://arxiv.org/abs/1611.09906),
including [its full discussion of self-application](https://arxiv.org/html/1611.09906v3).
Futamura's original result is cited by the agenda as
[*Partial Evaluation of Computation Process—An Approach to a Compiler-Compiler*](https://doi.org/10.1023/A:1010095604496).
The present experiment does not claim to reproduce an unrestricted theorem from
either reference.

## Executable status and next missing contracts

| Component | Status at this experiment | Evidence needed for the next boundary |
| --- | --- | --- |
| Typed data and bounded control | Native research v1 implementation | Retained execution, receiving and refusal controls. |
| Self-compiling structured compiler | Passed in the declared finite bootstrap experiment | Stage equality plus block, execution and mutation checks. |
| Interpreter for the complete structured subset, written in that subset | Open | The existing arithmetic interpreter has a smaller object grammar; the independent Python AST oracle is not an Adva implementation. |
| Correct binding-time specializer `mix` | Open | Static/dynamic value representation, residual construction, effect/error policy, bounded termination and correspondence receipts. |
| First projection | Open as a `mix` execution | Specialize a declared interpreter, then compare residual and unspecialized observations and actual costs. |
| Second projection | Open | `mix` must accept its own source and correctly residualize its dynamic program input. A hand-written compiler is not this projection. |
| Third projection | Open | Receive `mix(mix,mix)` and test the generated compilers on multiple independently declared interpreters. |

This ladder makes additional language implementations potentially cheaper:
provide a semantics-preserving interpreter in the admitted implementation subset,
then use a verified specializer and eventually a compiler generator. It does not
make an arbitrary language or its foreign-function, I/O, concurrency, memory and
undefined-behavior rules automatically available. Those are explicit semantic
interfaces. It also provides no automatic speed advantage: residual size,
specialization time, compile time, execution time and receiving overhead need
separate finite measurements.

A useful next concrete contract is therefore an Adva interpreter for this exact
structured subset, followed by a bounded `mix` with explicit static/dynamic data
and residual-control receipts. The current compiler can already compile programs
in that subset, including a future interpreter or specializer written within its
finite limits; claiming the projections waits for those actual executions.
