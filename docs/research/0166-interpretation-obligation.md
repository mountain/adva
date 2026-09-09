# Research 0166: Interpretation obligations beyond byte pairing

Date: 2026-09-09. Status: completed finite external calibration over fresh
Rust-rechecked library reuse. Direction: Mingli Yuan; formulation,
implementation and measurement: ChatGPT/Codex. Base main:
`6d2717cf330072c789fab1f816756c3a3a227433`; library:
`c9161549eaf667946e1830282261d4aa200cc3a4`.

## Question, objects and boundary

The newly registered `meaning-interpretation-v0.md` proposes a mechanism,
an interpretation and a third record binding their versions. That file is
`proposed-document`; catalog membership does not check its prose. The referenced
AEG mechanism and dual-pair receipt were not accessible in this run. This is a
new, smaller calibration of the proposed relation, not a replay or validation
of those unavailable artifacts, receipt ancestry or geometric hypotheses.

Can a correctly byte-bound interpretation still fail an explicit question about
the mechanism? Freeze:

- **Mechanism M:** existing native `library reuse`, epoch 1, word 0; snapshot
  digest `4480fa1e8b60ab945879f8644820ab8ef242dceaf494470bedb9b68b5fd976ee`.
  Its selected expressions are `2*x` and `x+x`. Rust reloads ancestry and
  scoped witnesses and checks nonzero obligations for every fresh input.
- **Interpretation I:** one of two supplied external ASTs, `add(x,x)` or
  `mul(x,x)`. The grammar has `x`, binary `add` and binary `mul`, interpreted
  over Python integers. It does not implement Adva sharing or natural language.
- **Question Q:** do the two ordered native guarded values equal the AST's
  prediction, for every input in the explicitly supplied finite scope?
- **Third record B:** schema plus separate hashes of M, I and Q. Q includes
  the observation relation, arithmetic domain, quantifier and exact inputs.
  None of M or I embeds B, avoiding a self-hash cycle.

Old scope is `{2}`, target scope `{2,3}`, fresh reuse scope `{-3}`. Native
guarded reuse admits the existing bounded integer range with zero excluded;
zero is tested separately as a refusal. No division, inversion or product-one
normalization is inferred from the outputs. Ordinary native `run` with f64 is
not used in this experiment. Supplied observations in the epoch remain
assumptions, and observation equality never identifies two programs/histories.

The [contract](../../experiments/interpretation_obligation/contract.json), SHA256
`c496984fa1d578f83561f3fd5441b27dec67d6408e296bbf3800adafa9d26b94`, was saved before
execution. It bounds the run to 20 wall seconds, 10 CPU seconds, 256 MiB address
space per process, 2 MiB per output file, 1 MiB total retained bytes, four native
calls (three seconds each) and at most 4,000 aggregate granted library units.
There are two supplied candidates and zero search nodes; this is no discovery
of an unknown difficult identity. One correction replay was allowed, none used.

## Actual results

Four actual Rust CLI invocations ran at `2`, `3`, `-3` and `0`. The first three
were `ReuseChecked`, with values `[4,4]`, `[6,6]` and `[-6,-6]`. Zero was
`Rejected` by the retained nonzero condition, with the native report saved.

| Case | Byte binding | Finite relation result |
| --- | --- | --- |
| Square interpretation, old scope `{2}` | Pass | `MatchedFiniteScope` |
| Doubling interpretation, target `{2,3}` | Pass | `MatchedFiniteScope` |
| Square interpretation, target `{2,3}`, new matching pins | Pass | `Counterexample`: at 3, `[6,6] != [9,9]` |
| Change interpretation without updating binding | Fail | `RejectedBinding` |
| Target `{2,3}`, omit the record at 3 | Pass | `UnknownCoverage`, missing input 3 |
| Duplicate the input-2 record | Pass | `RejectedEvidence` |
| Doubling, fresh scope `{-3}` | Pass | `MatchedFiniteScope` |
| Square, fresh scope `{-3}` | Pass | `Counterexample`: `[-6,-6] != [9,9]` |
| Try to admit zero in the scoped relation | Pass | `RejectedScope` |
| Repin an unsupported AST constructor | Pass | `RejectedSyntax` |
| Alter a returned input coordinate | Pass | `RejectedEvidence` |

The old singleton-scope agreement remains true. It was never a certificate for
`{2,3}`, all integers or all interpretations. The target counterexample therefore
does not overturn an earlier truth: it refutes an unwarranted scope expansion.
The checker conservatively requires full selected coverage before classifying
the whole finite relation; it does not optimize counterexample search.

Within the same target data and fixed budget, byte binding alone passes both
candidate descriptions. The added relation check distinguishes them. Calling
both byte passes semantic successes would produce one false acceptance out of
these two candidates. That is a conditional diagnostic of the incorrect
promotion rule, not a population error rate or an empirical speedup claim.

All eleven expected cases passed, as did JSON serialization and same-checker
comparison replay. The source snapshots and executable were hash-checked before
and after. The executable was the retained bootstrap build from #160, whose
reference SHA256 matched. No build or source modification occurred in this run.

## Proposed working term: interpretation-obligation

Status: **Proposed**, an external research relation rather than an Adva word
admitted by the native grammar.

- **Action:** attach a falsifiable behavioral obligation to a version-bound
  mechanism/interpretation pair.
- **Inputs:** M, I, Q, B and fresh native observation records for Q's finite
  input scope, under a trusted supplied executable and explicit checker rules.
- **Outputs:** finite matches, a retained counterexample, coverage/native
  Unknown, or typed binding/syntax/scope/evidence refusal.
- **Applicable conditions:** the interpretation has stipulated finite syntax;
  its observation is commensurate with the selected native values; guards,
  input coordinates, checker revision and snapshot selection are retained.
- **Witness and reuse:** target `2x` versus `x*x` at 3, then a distinct input
  -3 under the same rule. The term is not justified by merely naming it.
- **Expansion:** check separate pins, validate the scoped interpretation,
  require coverage and native successful responses, evaluate the AST, compare
  each ordered result and retain the first mismatch plus all comparisons.
- **Refusal:** repinning cannot discharge the behavioral obligation; unknown
  syntax, omitted records, duplicate coordinates and unmet guards cannot count
  as success. Parsing saved JSON alone grants no native authority.
- **Residual:** no arbitrary-prose semantics, faithful universal representation,
  independent executable authentication, repaired receipt ancestry, geometric
  duality, native free or evidence of human acceptance/customer benefit.

## Costs, evidence and next step

The sole invocation completed before checkpoint in **37.112084 ms**. Breakdown:
native calls and associated report handling 20.318916 ms; binding and relation
checks 1.540593 ms; serialization and same-checker replay 1.817698 ms. The
remaining time includes startup/preflight/hash checks and report preparation.
These intervals do not isolate naming/authoring cost or final checkpoint I/O.
Authoring and network retrieval were not metered. No acceleration claim is made.

Native library checks spent **815** units across four separately capped calls;
their budgets do not reset within a call or authorize more than four calls.
Linux peak RSS was **12,416 KiB** for the Python process and **12,160 KiB** for
the largest reported child, not simultaneous aggregate memory. The final
retained run directory contains **107,436 bytes**; file size is not memory use.

Exact invocation, reports, bindings, comparisons and the runtime source are in
[the experiment](../../experiments/interpretation_obligation/README.md) and
[the result](../../experiments/interpretation_obligation/run-01/report.json).
The original binary was
`b77954194eaffb085d2dbf823d92b942ccf0fffcd7cb99dee8868e8ad5adc598`; its build
provenance remains `bootstrap/VALIDATION.md`. A reproducer must supply a trusted
build; recording a new binary hash does not authenticate it.

This helps Mingli and later agents distinguish a correctly registered explanation
from an explanation that survives a declared test. It does not establish the
truth of the eight prose readings or their benefit to Jiamin's actual task.

Next minimum step: choose one sentence from the paired interpretation that
already has an available receipt, translate it into one explicit scoped
predicate, and preserve that sentence-to-predicate translation as a proposed
mapping for human review. Do not generalize the checker to arbitrary prose or
begin the Teichmuller/Calabi-Yau identification in the same step.
