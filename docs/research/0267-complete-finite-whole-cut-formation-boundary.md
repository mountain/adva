# Research 0267: complete finite WholeCut6 formation boundary

Date: 2026-10-14. Status: bounded research-local syntax-formation result.
Codex (OpenAI), submitted through Mingli Yuan's authorized account proxy, not
his authorship, review or endorsement. Project-original contribution under
Unknown v0.3.

## Frozen question and dependency state

Main was inspected at `8585c5b965b84422b802d50f11f375aea171bd27`.
There were no open pull requests. Merged PR #216 had already supplied the
source-bound distributivity record and recursive Hole/Use formation, while its
report left `HistoryComposition`, `BalancedZero`, and complete current
name/type boundaries open. The pre-execution
[contract](../../experiments/bootstrap_zero_complete_formation/contract.json)
therefore asks only whether those two constructors can enter the same finite
formation judgment without weakening the source, occurrence, type, name or
residual-ledger checks.

The objects are one research-local `WholeCut6` and one `AMTerm`. The grammar is
`Atom | Hole | Use | EmptyZero | PolarDual | Plus | Tensor | BalancedZero |
HistoryComposition`. Quantification is over every recursive position of each
supplied term, bounded by 256 visited nodes and depth 32, and over the current
declaration fields exercised by the frozen fixtures. The arithmetic domain is
empty: only syntax formation and exact nominal/type equality are checked.

This boundary does not change Research 0090's coverage requirement. It does not
supply Research 0092's full filler or vocabulary-promotion conditions. Research
0123's `arithmetic-universality` and `hypothesized-arithmetic-truth` remain
hypotheses. Additive zero and multiplicative unit retain separate domains; no
invertibility, cancellation, commutativity or numerical interpretation is
introduced here.

## Formation relation

`HistoryComposition(first, second)` is an ordered binary syntax constructor.
Formation requires both children to form recursively; swapping them produces a
different term. No inverse, cancellation or semantic history composition is
inferred.

`BalancedZero(positive, negative)` is admitted only when `negative` is exactly
`PolarDual(positive)`. The receiver visits the retained positive syntax once:
the negative component is a coordinated view of the same syntax, not a second
occurrence, implicit copy, additive zero proof or arithmetic cancellation.

WholeCut6 validation now also requires nonempty string names for the carrier,
cells, ports, cuts, types, sources, occurrences, channels, open-port fields,
circle order and residuals. The residual ledger must equal the ordered open-port
residual projection exactly. Hole names, types and ports are explicit. These
conditions make the input/output relation:

```text
(WholeCut6, AMTerm) -> FormationAccepted | ValueError(refusal boundary)
```

Within the finite budget, structural induction gives the limited theorem. Each
accepted leaf is either a named atom/empty form or is bound to an exact declared
hole or source occurrence. Every unary and binary constructor has accepted
children. `BalancedZero` additionally carries the exact dual-view equation and
`HistoryComposition` retains order. Therefore every accepted term has a finite
formed tree whose bound leaves retain the declared names, types and sources.
This is a formation theorem only, not an evaluation or equality theorem.

## Result and countercases

Fifteen new cases passed. A positive term combines both constructors over the
merged source-bound distributivity fixture. A second fixture with the fresh
prefix `formation-fresh-` reuses the relation successfully, while cross-source
occurrences are refused. Constructor order is observed and `BalancedZero` stays
distinct from ordinary `Plus`.

Four malformed-constructor controls reject a mismatched dual, a non-`PolarDual`
negative and invalid children in either history position. Nine WholeCut6
mutations reject an empty cell name, port name, port type or channel name; an
empty open residual; an extra or reordered residual; an empty hole type; and an
empty alternative type. The complete Bootstrap Zero suite passed 1,078 cases,
including the 1,063 merged cases and these 15 additions.

The result is deliberately not entered in `docs/claims.toml`: it is a local
test grammar result with no native checker, stable operation or broader
mathematical promotion.

## Cost and replay

There was one route, zero search candidates and zero semantic correction
replays. A first static lint preflight found one unused import, removed before
semantic execution. `/usr/bin/time` was unavailable, so targeted child memory
was recorded with Python resource accounting instead.

The complete suite took 1.90 seconds; its peak memory was not measured. The
targeted 15-case replay reported 0.08 seconds inside pytest and 0.336558176
seconds wall time including process launch, with child peak RSS 27,984 KiB.
Construction, receiving and fresh-reuse time were not separately exposed.
Serialization cost is zero inside this receiver. Lint time and memory were not
measured. Exact local outputs are retained in
[`execution.json`](../../experiments/bootstrap_zero_complete_formation/evidence/attempt-1/execution.json).

Replay from repository root:

```sh
python -m pytest -q tests/python/test_bootstrap_zero_complete_formation.py -p no:cacheprovider
python -m pytest -q 'tests/python/test_bootstrap_zero*.py' -p no:cacheprovider
python -m ruff check tests/python/test_bootstrap_zero_whole_cut_grammar.py tests/python/test_bootstrap_zero_distributivity_record.py tests/python/test_bootstrap_zero_complete_formation.py
python -m ruff format --check tests/python/test_bootstrap_zero_whole_cut_grammar.py tests/python/test_bootstrap_zero_distributivity_record.py tests/python/test_bootstrap_zero_complete_formation.py
```

## Vocabulary, use and residual

New vocabulary: **zero**. `BalancedZero` and `HistoryComposition` already
existed in the research model; this round admits them to the complete current
finite formation relation and sharpens their refusal boundaries. No claim of
greater universal expressivity or lower solution cost is made, so no
with/without-vocabulary speed comparison is inferred.

This helps Mingli and later agents construct the next syntax-only coordination
statement without silently treating a dual view as a copy, a history pair as
commutative, or an empty declaration as a mathematical object. Jiamin's actual
task benefit remains unmeasured.

The smallest continuation is a constructor-by-constructor syntax-only
coordination theorem over this exact accepted grammar and source-bound leaf
relation. Any later use for Research 0092 must first preserve Research 0090's
coverage gate and may yield only a paired witness or explicit gap until full
coverage is present. Arithmetic equality, history semantics, global M6 closure,
native `free`, stable API admission and universal grammar remain open.

## Independent PR #217 resource review

The original head `616aec1a13f1fe526920575502fa11411679b383` compares
negative and positive terms recursively before checking their descendants.
Two independently constructed 5,000-deep PolarDual chains produced
`RecursionError` on Python 3.12 (recursion limit 1,000); depth 600 instead
returned the formation-budget ValueError, but still compared before budgeting.
The explicit review contract extends the diagnostic fixture maximum from 600
to 5,000; it does not enlarge the accepted grammar.

The correction replaces dataclass term equality with an iterative ordered
field comparison. Formation visits retain the original 256-node cap and
root-zero depth 32. Dual comparison has a separate **cumulative** cap of 256
node pairs for the entire call, with absolute depth at most 32; nested
BalancedZero never resets that fuel. At most 256 formation nodes and 256
comparison pairs are processed (a pair reads two nodes). Equal separate trees
are accepted, so pointer sharing is not required and does not confer identity.
No term equality callback is invoked. The comparison can reject formerly
accepted terms when their aggregate comparison fuel is exhausted; this is an
explicit strengthened research-local receiving boundary.

This bounds structural work and auxiliary stacks for exact declared dataclass
constructors with ordinary string fields. String lengths, dictionary setup
from supplied WholeCut6 declarations, allocation before receiving, arbitrary
Python subclasses and malicious host objects are outside this resource
contract. Thus 256/32 is not a wall-time or total-input-byte guarantee.
The WholeCut6 validator covers the declared formation invariants and frozen
mutations; it is not a total decoder for arbitrary Python payloads.

The formation theorem is conditional on a valid WholeCut6 declaration and a
successfully accepted finite term under both budgets. Ordered children and
exact nominal source/type binding are preserved; the dual view registers no
second occurrence. This yields syntax well-formedness, not an evaluation law.
HistoryComposition order is raw constructor order, not a proved temporal
composition law. Cross-source uses are checked against the independently
supplied occurrence ledger.

For Research 0090/0092, still needed are: an explicit constructor-by-constructor
coordination interpretation and preservation proof; checked Rust program/type,
source/occurrence/history correspondence; complete declared filling-world
coverage and observer invariance; residual-preserving close/reopen witnesses;
and scoped generation, fair fuel, characteristic/promotion and reuse evidence.
Pairwise syntactic agreement cannot issue all-fillings FeatureClosed or prove
arithmetic cancellation, distributivity, invertibility or global M6 filling.

Authored by Codex (OpenAI), through Mingli Yuan's authorized GitHub account
proxy; not his authorship, review or endorsement. Original code, fixtures and
review prose contributed under Unknown v0.3; no external expression imported.

Review replay: 30 targeted cases passed (0.16 s pytest), full Bootstrap Zero
suite 1,093 passed (1.90 s), lint/format and publication history check passed.
Exact node threshold and wide-tree refusal are covered. The equality-callback
trap and deep mismatch controls directly distinguish the old implementation.
The original manifest and attempt-1 evidence remain historical byte pins at
the original head; use review-manifest.json for this correction.
