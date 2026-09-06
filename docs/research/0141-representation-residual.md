# Research 0141: a representation question across three machine roles

Status: finite experiment proposed; execution records are added only after running.
Dependency: draft #140 at `e008c8f70e44d31d44d15f615260003ea02bb562`.
Main remains `57c1d04bcfe51b82f6e559a61ca02e668f630b5a`; #140 is not merged.

## Question formation

On 2026-09-06 Mingli Yuan asked to turn the Real floating-point limitation
into an Adva representation question using the three-machine methodology,
and pass the finite question to Python for execution and analysis.
Research 0123 keeps arithmetic-universality and hypothesized-arithmetic-truth
as proposed directions. This experiment tests one necessary preservation
condition for those directions; it does not prove either hypothesis. It does
not discharge Research 0090 coverage or enable Research 0092 vocabulary lifting.

The issue exposed by native `Real` is whether finite scalar execution preserves
the question we intended to ask. Freeze the question as: for the eight named
instances in `programs/representation-residual/representation-question.adva`,
does binary64 evaluation preserve **exact zero and exact one**, and where is
any discrepancy introduced? There are three seed families, one new product
reuse instance, and four controls. No candidate search is performed.

The file is an explicitly proposed research question envelope read by the
Python experiment. It is not a registered native Adva program schema. Its
arithmetic cases are rendered as actual `adva.run.program.research` programs,
which the existing Rust executable can compile and execute. This separates
the present executable language from the still external question/checker layer.

| Research role | Retained object | Boundary obligation |
|---|---|---|
| Construction K | Rational input intention and finite expression tree | Preserve exact inputs before conversion; do not identify equal-valued sources |
| Time t | Specified operation order and rounding trace | Retain the original Rust history; reassociation is a different program |
| Space X | Finite binary64 observation and its exact-value fibre | A displayed zero/one must not silently become an exact predicate judgment |

These roles organize the research. They are not an invocation of native
`TriadicObserverTransitionV0`. That API requires a checked ProgramSlice and an
explicit policy on three input-source fibres. Assigning K/X/t to three scalar
variables just to satisfy its arity would not justify the present interpretation.
No physical spacetime interpretation is imported.

## The two necessary comparisons

Let rho round a rational to binary64 and iota embed a finite binary64 scalar
as its exact rational value. For one expression E and intended input q, retain:

```
v_intended = eval_Q(E, q)
v_quantized = eval_Q(E, iota(rho(q)))
v_observed = iota(eval_64(E, rho(q)))
input_residual = v_quantized - v_intended
operation_residual = v_observed - v_quantized
total_residual = input_residual + operation_residual
```

Also compare `rho(v_intended)` with `eval_64(E,rho(q))`. Their equality tests
compatibility of rounded evaluation, but it does not establish reflection of
the intended exact predicate. For example, both paths may return 1 even when
the exact product is `1 - 2^-54`. The exact-value fibre at observed 1 contains
points on both sides of the predicate "is exactly one".

All exact computations here are external Python Fraction oracles over the
declared finite add/multiply grammar. Python creates no SourceId, OccurrenceId,
ProgramSlice, semantic history or native certificate. A supplied success flag
is not an independent check: native comparisons are based on fresh executions
of the unchanged executable and the original envelope is retained.

## Frozen witnesses and controls

1. Input alias: `(2^53+1) + (-2^53)` has exact result 1. Conversion can already
   erase the low bit before the addition executes.
2. Ordered absorption: `(2^53+1) + (-2^53)` with **three separate exactly
   representable inputs** and the specified left-associated addition also
   loses one, this time during execution. The right-associated program is a
   control with the same number of arithmetic operations and a different history.
3. Multiplication: `(1+2^-27)(1-2^-27)` has exact result `1-2^-54`, but its
   binary64 observation is 1. Both inputs are exactly representable and nonzero.
   The `k=28` instance is reuse; `k=26` is an exact-result control.
4. Additional controls: distinct inputs below the precision boundary and an
   explicit zero input. The latter must retain its failed nonzero guard even
   when zero is the correct scalar result.

These are familiar floating-point phenomena used to calibrate Adva's boundary,
not newly discovered mathematical results. Preliminary independent design review
replayed six cases with Fraction; its timing/memory were not measured. The
frozen main suite and its costs are recorded separately.

## Proposed working term: representation-residual

Purpose: turn a hidden representation loss into a question that a later checker
can consume. Input: exact intention, representation profile, ordered expression,
pointwise native run where available, target predicate and domain guards.
Output: input/operation residuals, retained native report, external oracle trace,
predicate decision, guard status and remaining obligations.

Applicability: the frozen finite add/multiply grammar and rational inputs within
the explicit bit/step/time limits. Replay by executing the command below against
the retained question. A nonzero residual refutes the asserted exact equality;
a missing checker or exhausted budget yields Unknown. An unchanged representation
must be retested on the reserved new product instance before claiming reuse.

Rejection conditions: unknown grammar/profile, nonfinite values, mismatching
native input conversion or result, exhausted budget, invalid saved run binding,
or a failed required nonzero guard. Raw float-only zero/one classification and
the exact-oracle gate use the same frozen cases and resource cap. Costs include
the oracle and representation record; this does not claim acceleration.

Status remains **Proposed as an external diagnostic vocabulary**. It is neither
a new stable builtin nor a learned theorem, M1 certificate, Seal, or universal
grammar result. Scalar zero is not additive formation A0; scalar one is not
guarded multiplicative transport M1. A zero residual at one input does not
establish identity over a domain, equality of histories, or an M6 filler.

## Replay and resource boundary

```
python3 experiments/representation_residual/run.py \
  --question programs/representation-residual/representation-question.adva \
  --output-dir target/representation-residual \
  --backend /absolute/path/to/adva
```

Without `--backend`, the script performs external arithmetic comparisons and
explicitly reports native execution as NotRun. Use a new output directory.
The suite permits eight cases, 128 mathematical AST steps, 256-bit Fraction
components, 30 seconds total, and at most five seconds per native invocation.
Each native program keeps #140's fuel of 16; each case invokes it at most once.
Native calls are additionally bounded by the workflow's outer process limits.
There is no retry loop, fuel reset, or broadening of the candidate family.

## Remaining obligations

The exact oracle does not implement exact Rational semantics inside Adva.
The research question schema and interpretation of the three roles still need
their own native boundary if promoted. Rounding fibres are only exhibited by
finite witnesses here; no interval coverage theorem is claimed. Actual value
for Jiamin's practical task, general error-aware compilation, and safe
reassociation certificates remain open.

## Execution checkpoint

The local external-only suite completed eight cases with two falsezero and two
falseone observations; the exact oracle gate accepted none of those four.
The recorded product-k28 reuse exhibits residual 1/2^56. See
`0141-local-preflight/report.json`. Native execution there is explicitly NotRun.
Two separate negative controls retained a wrong expected value and a lowered
budget; both were visibly refused (`0141-local-preflight/negative-controls.json`).
The final native byte-binding adjustment is tracked separately from these
local measurements. One CI execution will compare the unchanged Rust binary
against the same frozen cases; until that record is attached it is NotRun.

The local attempt to materialize the earlier native artifact returned HTTP403.
No download escalation or toolchain installation was attempted. The CI bridge
uses the already tested artifact with source-hash checks, and retains its
identity and all new native reports. The native artifact is an expiring build
convenience; the source-based replay command remains the durable route.
