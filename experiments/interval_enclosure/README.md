# Rational expression enclosures, directed rounding and retained domain gaps

Status: bounded external research, 2026-09-17. PR #194 was merged after all
eight checks passed; baseline is `afd929ed37198bbab1c7f338aba449f83616b7cc`.
This advances priority 4 of the [applied-mathematics roadmap](../../docs/research/applied-mathematics-contract-roadmap.md).

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
not his review, endorsement or correctness guarantee. Original first-party
code, exposition and synthetic data under Unknown v0.3. Another ChatGPT agent
statically reviewed the mathematics and scripts, without institutional review.

## What this receiving contract adds

The existing Feigenbaum campaign already uses rational interval arithmetic and
outward rounding, while the Sharkovsky experiment concerns piecewise-affine
extensions. They are methodological references; neither is a caller-bound
generic expression receipt. Their code, campaigns and evidence remain unchanged
and are not rerun or imported here.

This separate receiver fixes the expression, variable boxes, evaluation order,
rounding policy, epsilon and history before checking the candidate trace. Every
node reports both its `tight` primitive interval and its propagated `enclosure`.
Here `tight` refers to that primitive applied to the already propagated child
intervals; it does **not** mean the globally sharp range of the original expression.

At most two named variables and seven ordered acyclic nodes are admitted, with
depth at most four. Every node is reachable from the final node. Repeated named
variables and references mean the same value. Node indices are external syntax,
not native Adva sharing or source identities. The mathematical domain is all
rational valuations in the declared closed boxes; finite endpoint encoding
limits do not enumerate that domain or define a finite field.

## Exact enclosure and rounding rules

For intervals [a,b] and [c,d], addition yields [a+c,b+d] and subtraction
[a−d,b−c]. Multiplication takes the smallest and largest endpoint products.
Division is multiplication by [1/d,1/c], only when [c,d] excludes zero. This
reciprocal formula applies to positive and negative denominator intervals.

The producer uses four-corner enumeration. The independent receiver uses
monotonicity on the nine pairs of negative/crossing/positive sign classes,
and reciprocal multiplication for division. Both use Python Fraction but import
neither one another nor the legacy interval implementations.

In `exact-rational` mode no rounding occurs. In `outward-grid` mode grid N
means spacing 1/N, with N in {1,2,4,8,16,32,64}. At **every leaf and operation**,
including input boxes and constants, the interval [l,u] becomes

    [ floor(N*l)/N, ceil(N*u)/N ].

The receiver derives these bounds using signed integer division with remainder.
Truncation toward zero is not a lower-bound rule. The producer independently
uses Fraction floor/ceil. For example, [1/3,2/3] at spacing 1/8 becomes
[1/4,3/4], and [−2/3,−1/3] becomes [−3/4,−1/4]. Four finite counterexamples
replace one bound by inward rounding: each excludes an original legal endpoint.
These are actual unsoundness witnesses, not merely differing output formats.

Soundness follows by induction over the finite node order. Each primitive
interval contains the result of every allowed pair of operand values; outward
rounding only enlarges it. Shared-variable dependencies may make the set of
actual operand pairs smaller than that rectangle, which preserves inclusion
but loses sharpness. Exclusion of denominator zero supplies the required
division domain at every completed step. This elementary argument is supplied
as original exposition, not as a proof-kernel artifact. Sample checking alone
would not establish the universal enclosure property.

## Exact zero, exact one and epsilon are different judgments

| Enclosure | Zero classification | One classification |
| --- | --- | --- |
| [0,0] | ExactZero | ExcludesOne |
| [1,1] | StrictPositive | ExactOne |
| [1/64,1/64] | StrictPositive | ExcludesOne |
| [−1/64,1/64] | ZeroUndetermined | ExcludesOne |
| [1/2,2] | StrictPositive | OneUndetermined |

The receiver separately checks whether the entire enclosure is inside
[−epsilon,epsilon]. With epsilon=1/16, both small intervals in the table meet
this magnitude bound, but neither is classified as `ExactZero`. A complete
verified enclosure may therefore retain an unresolved equality or sign question.
An interval containing zero does not establish existence of a zero in the
original expression's image.

For x∈[1,2], the natural interval trace of x−x yields [−1,1], and x/x yields
[1/2,2]. Algebraically their values are exactly zero and one respectively
(the latter has nonzero x). Candidates that silently replace those trace nodes
by [0,0] or [1,1] are refused **as violations of the selected interpreter**.
Those narrower intervals are mathematically correct. This experiment does not
refute the identities or claim the interval interpreter has recovered dependency.
A separately justified rewrite or dependency-aware receiving profile is still
needed to accept those shortcuts as part of this process.

## A blocked denominator is not necessarily a real pole

At the first division whose propagated denominator contains zero, the receiver
checks and retains exactly the preceding trace, records the node and denominator,
and returns `UnknownDomain`. It returns no accepted root result or semantic delta.
It cannot skip that operation because a later multiplication happens to be zero.

The frozen examples distinguish five situations:

| Expression and original box | Why the interval interpreter pauses |
| --- | --- |
| 1/x, x∈[−1,1] | Denominator crosses zero |
| 0/x, x∈[0,1] | Zero numerator does not make division by zero defined |
| x/(x−x+1), x∈[1,2] | Dependency loss gives denominator [0,2] |
| 1/x, x∈[1/64,1/32], spacing 1/16 | Outward rounding changes denominator to [0,1/16] |
| 0·(1/x), x∈[−1,1] | The earlier division still has an unresolved domain |

The third expression is actually x: its denominator is identically one. The
fourth original denominator is strictly positive. Thus `UnknownDomain` is not
a proof of an actual pole or mathematical impossibility. A separately selected
spacing 1/64 completes the positive-denominator example and yields [32,64].
The original box and expression are unchanged between those coarse/fine cases;
no automatic grid refinement or renewal of fuel is performed.

## Exact interface

The [frozen contract](contract.json) specifies all fields and budgets. A request
has `question`, `variables`, `nodes`, `mode`, `grid`, `epsilon`, `history`, and
`scope`. Variables have `name` and a rational interval. Nodes are `var`, `const`,
or binary `add`, `sub`, `mul`, `div` with earlier integer references. History
has one to four entries; scope is `all-rational-valuations-in-box`.

A candidate has `profile`, the exact selected `request`, `trace`, and `result`.
Profile is `adva.research.interval-enclosure.v0`. A completed result reports
its interval, zero/one classifications and the separate epsilon-bound Boolean.
A domain pause reports the blocked node and denominator. Each trace entry binds
its index, primitive interval and propagated enclosure.

The protocol requires the canonical result of the selected algorithm, not an
arbitrary enclosure that happens to be sound. Malformed input or substituted
context is `InvalidContext` or `InvalidEvidence`, not a mathematical counterexample.
Budget exhaustion is `UnknownBudget`. On a raw JSON parsing failure there is no
decoded expected request; the exact input bytes remain in the evidence. Verified
prefixes can remain as diagnostics after a later refusal, without accepting a root.

No probability distribution, sampling confidence, physical measurement error or
binary64 error model is inferred from a box or an outward-rounded rational grid.
The meaning of an input box is supplied by the caller.

## Execution, evidence and replay

The first campaign passed **641 assertions in 53 fresh receiving processes**:
20 `VerifiedEnclosure`, five `UnknownDomain`, 18 `InvalidEvidence` and ten
`InvalidContext`. It covers all nine sign-pair multiplication branches,
positive/negative grid reuse, exact zero/one, negative division, nested
operations, five domain pauses, four inward-rounding counterexamples,
dependency-policy controls and malformed inputs. Direct rational evaluation
records 135 sample valuations; these include actual undefined points and
well-defined points behind interval-domain obstructions. Samples are controls,
not universal proofs. There was no failed campaign or corrective replay.

Measured campaign wall time was **9.240999519 seconds**. Counted work was
1,226 receiver units, 162 producer units and 406 direct-point units, with zero
search candidates. Instrumented construction took 0.017214706 s, receiving
8.850439376 s, serialization 0.116571300 s and independent point observations
0.027040363 s. The fresh negative-box reuse receiver took 0.128829211 s within
that receiving total. Some copying/setup/bookkeeping is included only in total
campaign wall time. Highest child RSS was 10,752 KiB (10.5 MiB), supervisor RSS
13,184 KiB (12.875 MiB), not an aggregate system peak. Archive construction
additionally took 0.080224338 s. Final report/manifest writing, research, static
review, network and CI costs were not separately measured. No speedup or
expression-power increase is claimed.

[execution.json](evidence/execution.json) records all results, costs and source
hashes. [rounding-counterexamples.json](evidence/rounding-counterexamples.json)
gives the four exact excluded endpoints. [manifest.json](evidence/manifest.json)
inventories **293 exact files** inside [attempt-1.tar.gz](evidence/attempt-1.tar.gz):
requests, candidates, raw process outputs, commands, finite point observations,
contract and counterexamples. The archive is 21,236 bytes, SHA-256
`6aaab0b2d7696ef3b9d799dd159599915b8af1d49a2d846ee03555aecba2afd2`.
File size is storage cost, not peak memory. All incorporated material is original
code, exposition or synthetic evidence; no external research expression is
included. Stored command paths require substitution after extraction.

Run from repository root using a fresh output path:

```sh
python3 -B -S experiments/interval_enclosure/run.py --output /tmp/adva-interval-fresh
```

The supervisor uses at most 53 fresh receivers and 30 wall seconds. Each child
has 3 wall/CPU seconds, 128 MiB address space, 32 KiB per input and 10,000 counted
work units. Receiver intermediate integers and endpoints are bounded to 512 bits;
the producer and direct-point evaluator each have 10,000 counted work units,
and aggregate counted work is capped at 100,000. Input rational components are
at most 64. Limits are not a hostile-service certification. CI adds an outer
35-second timeout and preserves outputs on failure.

To receive one preserved domain-gap example independently:

```sh
mkdir /tmp/adva-interval-evidence
tar -xzf experiments/interval_enclosure/evidence/attempt-1.tar.gz -C /tmp/adva-interval-evidence
python3 -B -S experiments/interval_enclosure/receive.py \
  --expected /tmp/adva-interval-evidence/attempt-1/valid/dependency-domain/expected.json \
  --candidate /tmp/adva-interval-evidence/attempt-1/valid/dependency-domain/candidate.json
```

## Remaining obligations

This helps people and agents retain what an approximate calculation does and
does not establish, and reject rounding in the wrong direction before relying
on its boundary. The dependency obstruction is useful even when the original
expression is perfectly well-defined. No measured practical benefit for Mingli
or Jiamin has been established; no native operation, `Close`, `free`, M6 filler,
universal grammar, learned theorem or acceleration follows.

General interval functions, transcendental operations, binary64 error bounds,
dependency-aware rewrites and native import remain open. The next roadmap task
is priority 5: a bounded optimization problem with separately checked feasibility,
lower bound and gap. A small residual, contracted search region or matching mean
must not substitute for that optimality certificate. The older ledger-holder-exit
obligation remains a separate engineering task.
