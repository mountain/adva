# The compiler size curve and the bootstrapping budget

Status: completed bounded construction and measurement, with executed correctness at
every fitting shape, 2026-09-16. Base: `d5b5d0c`.

Direction: Mingli Yuan. Design, construction, execution and record:
deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through Mingli Yuan's
GitHub account (`mountain`) as an authorized proxy; not his authorship, review,
endorsement or guarantee. No independent human review.

## 1. What was missing

Four measurements of self-hosting work existed as isolated points: a two-opcode
compiler at 41 instructions
([dynamic-residual calibration](futamura-dynamic-residual-calibration.md)), a
four-opcode meta interpreter at 166, a nineteen-opcode ladder floor at 295
([scaling preflight](self-interpretation-scaling-preflight.md)), and a 127-node data
bound against a 169-node encoding
([capacity preflight](self-interpretation-capacity-preflight.md)). None of them said how
the cost *scales* — which of the three things a compiler must handle (opcodes, source
length, slots) actually consumes the bound.

This preflight measures that surface. A generated compiler, written in the research
data-machine language, lowers source programs of a declared subset of that same
machine's instruction language into machine programs. Each source instruction is
lowered by a declared rule — a slot lives in a data register and an integer register, so
one source instruction becomes one to three target instructions — the residual is
instantiated and executed directly, and the expected outcome comes from an independent
host-side reference implementation of the same declared semantics.

## 2. The curve

Compiler instructions against the declared bound of 128:

| Axis | Shape | Instructions | Fits |
| --- | --- | --- | --- |
| Opcodes | 2 opcodes, 2 slots, 3 instructions | 101 | yes |
| Opcodes | 3 opcodes, 2 slots, 3 instructions | 146 | no |
| Opcodes | 4 opcodes, 2 slots, 3 instructions | 194 | no |
| Opcodes | 5 opcodes, 2 slots, 3 instructions | 257 | no |
| Length | 2 opcodes, 2 slots, 1 instruction | 37 | yes |
| Length | 2 opcodes, 2 slots, 2 instructions | 69 | yes |
| Length | 2 opcodes, 2 slots, 3 instructions | 101 | yes |
| Opcodes | 3 opcodes, 2 slots, 2 instructions | 99 | yes |
| Slots | 2 opcodes, 2 slots, 2 instructions | 69 | yes |
| Slots | 2 opcodes, 3 slots, 2 instructions | 69 | yes |

The marginal costs are the useful part:

- **one more opcode** costs 45 to 63 instructions, because each opcode brings a dispatch
  case and its lowering body to every source position;
- **one more source instruction** costs 32 instructions, because the fetch, the whole
  dispatch and the bodies are emitted per position;
- **one more slot** costs nothing in compiler size, because slot indices travel as
  *data* in this design and are never baked into code. The slot term is free only
  because no register remapping happens; a compiler that renamed registers would pay it.

So the ceiling for this lowering compiler at three source instructions is **two
opcodes**: the third already needs 146 of the declared 128.

## 3. The full-language ceiling, submitted rather than assumed

A compiler for all nineteen declared opcodes over a single source instruction is
**201 instructions**. The twelve opcodes this preflight declares no lowering for are
charged the cheapest measured lowering, so 201 is a lower bound rather than an estimate.
It was submitted to the unchanged CLI and refused at admission, which places the
bootstrapping budget in one line: an in-language compiler for the machine's own
instruction language costs at least 201 instructions where 128 are allowed, before any
optimisation, register remapping, failure path or provenance.

## 4. Executed correctness at every fitting shape

For each shape that fits, the whole declared family of source programs was compiled,
each residual instantiated and executed directly, and compared with an independent
host-side reference implementation of the same declared semantics:

| Quantity | Value |
| --- | --- |
| Executed cases | 28 |
| Agreeing cases | 28 |
| Returned outcomes | 16, with values 3, 7 and 9 |
| Refused outcomes | 12, refused by both the residual and the reference |
| Residual sizes | 3, 4 and 6 instructions |
| CLI launches | 43 of 256 permitted |

Refusals are part of the result rather than an accident: a declared return slot that no
source position writes makes the residual refuse, and the reference refuses it too, so a
compiler that turned a refusal into a value would fail this check.

## 5. What this means for bootstrapping

The three constraints now have shapes rather than single numbers:

1. **Opcode count is the binding term.** Every opcode costs a dispatch case plus its
   lowering body *per source position*, so a compiler for a nineteen-opcode source
   language over even one instruction is over the bound. Self-hosting needs either a much
   larger instruction bound or a data-driven dispatch that does not repeat per position —
   and the latter is exactly what the machine cannot express, since control transfer
   targets and register operands are static indices.
2. **Source length is the second term**, at roughly 32 instructions per interpreted
   instruction, which is why the earlier meta interpreters broke at three object
   instructions.
3. **Slot count is free in code size but not in data**, because the slot bank is data.
   That is the one term an extension does not have to buy, as long as it does not
   require register remapping or indirect addressing.

None of this is a prohibition. It is the price list for the separately scoped extension
that projections two and three would need, and it is consistent with the two earlier
floors: 169 data nodes for an inspectable encoding, 295 instructions for a nineteen-case
ladder with placeholder bodies, and 201 instructions for a nineteen-opcode lowering
compiler.

## 6. What this does not establish

- The curve prices one declared lowering compiler with no optimisation. An optimising or
  remapping compiler pays more; a compiler with a different lowering might pay less.
- The slot term is free only under this design's convention that slot indices are data.
- No compiler was made self-applicable, and nothing here executes or refutes projections
  two and three: the ceiling is a measured refusal of one generated program.
- No wall-clock, throughput or residual-quality claim is made; the counts are machine
  instructions and executed steps of the research data machine.

## 7. Files

- Contract, checker and record: `experiments/compiler_size_curve/` — `contract.json`,
  `check.py`, `evidence/attempt-1/curve.json`, `evidence/attempt-1/ceiling-compiler.adva`,
  the generated compilers under `evidence/attempt-1/compilers/`, every emitted residual
  under `evidence/attempt-1/residuals/`, `evidence/attempt-1/results.json`, and
  `attempt.tar.gz` with the 128 raw programs, inputs and runs of the 43 launches, every
  member digest verified before the loose copies were removed.
- The receiving regression is `tests/python/test_compiler_size_curve.py`; it reads the
  record and regenerates the compilers and the ceiling program, and launches no run.
- Registered as `adva.bounded-experiment.compiler-size-curve.v0` and recorded in agenda
  section 17.
