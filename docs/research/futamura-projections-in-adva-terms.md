# The Futamura projections in Adva's terms, with a first executed instance

Status: completed bounded construction, executed calibration and theory statement,
2026-09-16. Base: `4027933`. The executed record is retained under
`experiments/futamura_first_projection/evidence/attempt-1`.

Direction: Mingli Yuan. Design, construction, execution and record:
deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through Mingli Yuan's
GitHub account (`mountain`) as an authorized proxy; not his authorship, review,
endorsement or guarantee. No independent human review.

## 1. What the agenda asked for, and what was missing

`docs/RESEARCH_ENGINEERING_AGENDA.md` already carries the Futamura projections as
the classical calibration of the specialization track (§1.1), states the progression
toward them (§1.5), and names the target inside the arithmetic-expression track:
"compile one fixed static expression into an ordinary Adva program as a baseline,
while explicitly recording that this is compilation rather than interpretation"
(§4 staged plan step 1), with the exit condition "residual execution agrees under a
declared observer while source-to-residual correspondence and forgotten structure
remain explicit", and finally "test the first Futamura-style
interpreter-specialization observation" (§4 phase 2).

The agenda also states what was missing: "These equations are a conceptual
calibration, not current Adva claims. A future Adva formulation must state the exact
program identities, observation policies, residuals, and certificates under which an
equivalence symbol is justified." Two prerequisites have since arrived — finite
tagged data with bounded control, and an arithmetic interpreter written as a program
over it (`programs/bounded-interpreter/interpreter.adva`) — so that calibration can
now be run instead of described. This note states the projections in this
repository's terms and records the first executed instance.

## 2. The projections stated in this repository's terms

Let `M` be the research data machine at a declared profile: fixed source bytes, a
declared profile digest, hard bounds (128 program instructions, 16 registers, 127
data nodes, depth 12, node arity 8, stack 256, lifetime fuel 2048), and a run record
that retains every executed instruction with a digest of the resulting state.

- An **object program** is finite tagged data in a declared encoding `repr`. For the
  arithmetic object language that encoding is the existing one: tag 0 literal with an
  integer field, tag 1 addition with two fields, tag 2 multiplication with two fields.
- An **interpreter** `I` is a program of `M` that takes `repr(p)` as data and returns
  the object-level result. `I` exists and is unchanged.
- A **specializer** `mix` is a program of `M` that takes interpreter and program as
  data and returns residual program data. `mix` must be a *program*, not a host
  function; a host-side transformation would relocate the projection out of the
  language and prove nothing about `M`.
- The **observation policy** `Q` must be declared before execution. Here it is: the
  run status and the returned integer value. The execution trace is deliberately
  *not* part of `Q`, because specialization changes the trace by design; a
  correctness condition demanding trace equality would forbid specialization
  outright. This is the point the agenda's research question 5 asks to fix.
- The **source-to-residual correspondence** is a retained rule plus the residual
  bytes, and the **forgotten structure** is named explicitly (here: tree shape,
  literals, and the interpreter's evaluation order).

The projections then read, for a declared finite family of `(p, x)` pairs:

1. `mix(I, p)` is a residual program whose execution under `Q` equals interpreting
   `p`: for all declared `x`, `Q(run(mix(I,p), x)) = Q(run(I, ⟨repr(p), x⟩))`.
2. `mix(mix, I)` is a compiler for `I`.
3. `mix(mix, mix)` is a compiler generator.

Each projection additionally needs four things this note makes explicit, because
without them the `≃` is decorative: an **admitted representation** of the programs
involved, a **specializer expressible in the language it specializes**, a
**separately budgeted interpretation and specialization cost**, and a **loader** that
turns emitted program data back into an executable program.

## 3. The executed instance: projection 1 for a fully static family

The source family is the 129 frozen regular arithmetic trees retained by the bounded
interpreter campaign. Each source program is the entire input to the interpreter, so
the static/dynamic boundary is total: nothing is dynamic, every residual is a
constant.

The compiler `C` is built from `I` by a declared rule and the rule is checked
instruction by instruction rather than asserted:

| Quantity | Value |
| --- | --- |
| `I` instructions | 51 |
| `C` instructions | 62 |
| `C` body identical to `I`, except the final `return` | yes, for all 50 other instructions |
| That `return` becomes | `jump 51` into the appended epilogue |
| Emission epilogue | 11 instructions |
| Registers added | 5 (so `C` uses the declared maximum of 16) |

The epilogue folds the completed value into residual program data in a declared
encodings `R`: a program node (tag 7) whose fields are instruction nodes — tag 0
`constant value dst`, tag 2 `box_integer src dst`, tag 1 `return src`. Because this
profile has no loader instruction, the checker instantiates that data into a program
file; that host step is a declared boundary of the result, not part of the claim
about in-language compilation.

Executed over the whole family, three ways:

| Quantity | Value |
| --- | --- |
| Trees | 129 (the frozen family, unchanged) |
| Interpreted run | value and status; 24 to 136 native steps, 15,966 in total |
| Compiled run | 35 to 147 native steps, 17,385 in total |
| Residual | 3 instructions for every case; 3 native steps |
| Value agreement | interpreted = directly executed residual = independent recursive oracle, 129 of 129 |
| Interpreted side versus the frozen archive | one run compared byte for byte: identical |
| One-shot compile then run | 17,772 steps against 15,966 for interpreting once |
| Reuse | two uses of a residual already beat interpreting twice, in 129 of 129 cases |

Two of these numbers are the substance rather than the bookkeeping. The interpreted
total of 15,966 steps equals the total the frozen campaign itself recorded for the
same family, and one interpreted run is byte-identical to that campaign's retained
artifact: the interpretation half of this calibration is the frozen evidence, not a
re-implementation. And the one-shot total is *worse* than interpreting once —
17,772 against 15,966 — because the compile cost is counted; compilation pays only on
reuse, and the per-case break-even is two uses for every one of the 129 trees. Both
facts are recorded rather than hidden, because a projection that reports only the
residual's 3 steps would be reporting the part that flatters it.

## 4. Why projections 2 and 3 are blocked today, and by what

The second projection needs `mix(mix, I)`: the specializer applied to itself, which
requires the specializer to be a program in the language it specializes. Three
measured facts stand in the way, and none of them is a matter of effort:

1. **The data bound.** The inspectable encoding of the 51-instruction object
   interpreter needs 169 nodes against a declared 127, and the only encoding that
   fits — packing operands into one integer — needs an unpacking operation that the
   19-variant vocabulary does not provide
   ([capacity preflight](self-interpretation-capacity-preflight.md)).
2. **The program bound.** A meta program with 19 opcode cases over one object
   instruction is 295 instructions against 128, before any real body, register file or
   provenance ([scaling preflight](self-interpretation-scaling-preflight.md)). The
   compiler itself shows the shape of the gap: 62 instructions using 17 opcode kinds,
   while the object language it compiles has 3 tags over trees. A compiler written in
   the machine's own 19-op instruction language, for that same instruction language,
   is what self-hosting needs and what the bound refuses.
3. **The loader.** Emitted program data becomes an executable program only through a
   host step today. The language has no instruction that loads a program from data,
   so even a perfect in-language compiler would still hand its output to something
   outside `M`.

Consequences for the open choice in agenda §12/§13/§14 are therefore sharpened rather
than changed: a separately scoped extension that wants projections 2 and 3 must move
the program instruction bound (with the 295-instruction floor as its reference), and
either the data node bound or the operation vocabulary, and the fuel bound; a checked
translation between the carrier and the program/process boundary moves none of them.
Projection 1, by contrast, needs none of that — it is available now, in the form
recorded here.

## 5. The promotion gates of §1.6, against this work

| Gate | Status here |
| --- | --- |
| input/static/dynamic boundaries are typed | satisfied for the declared family: the static boundary is total and declared |
| residual program identities are fresh and explicit | satisfied: every residual is retained as data with a declared encoding |
| the source-to-residual correspondence is certified | partially: the construction rule and the instruction-level relation are checked; there is no certificate object of the kind the stable API would require |
| forgotten process information is recorded | satisfied: named in the contract and in this note |
| correctness is observation-relative, not inferred from a few values | satisfied: `Q` is declared, the trace is excluded on purpose, and all 129 cases are checked against a third implementation |
| copy and discard cannot be introduced implicitly | satisfied in the letter — the epilogue's copies are explicit instructions — but the emitted residual is a copy-free constant, so this gate is barely exercised |
| failure and unknown conditions are representable | not satisfied: the residual has no failure or unknown path, and no residual can express one |

This is why nothing here is promoted: the gates that concern failure, unknown and
certificate objects are exactly the ones a stable specializer would need, and this
calibration does not supply them.

## 6. What this does not establish

- No stable specializer, no general partial evaluator, no new operation, no bound
  change, no IR-versioning decision.
- `C` is not obtained by applying a specializer to `I`. It is a compiler constructed
  from `I` by a declared rule, and what is checked is the commuting square for the
  residuals it emits. Deriving `C` from `I` mechanized is projection 2, and section 4
  is the measurement that says it does not fit today.
- The static boundary is total, so the residuals are constants. A residual with
  dynamic inputs, and therefore any claim about residual *code quality*, is not
  attempted.
- The step counts are steps of the research data machine, not wall-clock numbers for
  real hardware, and they include no claim of a speedup in any engineering sense.
- Projections 2 and 3 are blocked by declared bounds in one profile, not refuted.
  Widening them, or adding an unpacking or loading operation, is a separately scoped
  decision with its own ADR and its own price.

## 7. Files

- Contract, checker, compiler and record:
  `experiments/futamura_first_projection/` — `contract.json`, `check.py`,
  `evidence/attempt-1/compiler.adva`, `evidence/attempt-1/residuals/` (129 emitted
  residuals), `evidence/attempt-1/results.json`, and `attempt.tar.gz` holding the 1,161
  raw programs, inputs and runs of the 387 launches with every member digest verified
  before the loose copies were removed.
- The receiving regression is
  `tests/python/test_futamura_first_projection.py`; it reads the record, rebuilds the
  compiler from the frozen interpreter and re-checks the relationship, and launches no
  run.
- Registered as `adva.bounded-experiment.futamura-first-projection.v0`; recorded in
  agenda section 15.
