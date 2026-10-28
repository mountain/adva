# Serialized Open-Line Leaf Request: Paused at Import Artifact Projection

## Status

Unknown / paused after the one permitted correction replay. This is a
research-local candidate, not a theorem, a learned word, a stable protocol, or
evidence for M6 closure, arithmetic universality, or universal grammar.

The base is `main` commit
`03c37587c5c983647f302b6ef49aac6bd000626e`, which already contains the merged
native input-binding certificate from PR #226. Open PR #227 is a separate
finite epistemic-identity proposal and was not used as a dependency.

## Frozen question and boundary

The pre-execution contract is
[`experiments/native_input_binding_serialized_leaf_request/contract.json`](../../experiments/native_input_binding_serialized_leaf_request/contract.json).
It asks whether one externally named open-line leaf can reach the existing
native Rust receiver only when a versioned JSON request also carries:

1. the complete source diagram JSON;
2. the complete residual diagram JSON;
3. one independently expected external source/occurrence/target tuple; and
4. the exact qualified native source/target occurrence pair, including both
   contexts and both occurrence paths.

The fixed object is the zero-event source
`(frontier (use static) (use dynamic))` specialized at canonical `Rational::ONE`.
This does not identify additive zero with multiplicative unity. The positive
quantifier contains exactly two frozen external tuples (`KX-L` and `tK-R`).
The negative set contains external rebinding, native source rebinding, native
path rebinding, a valid but different source snapshot, malformed diagram JSON,
an unknown root field, a wrong profile, and byte-budget exhaustion.

The only route constructs a strict five-field JSON envelope. Both diagram
strings enter through `adva_lisp::import_diagram_json`; the request must match
the caller's complete current artifacts and the sole dynamic native occurrence
pair before the existing receiver is called. The byte limit is 65,536 and the
existing structural receiver limit is 512 work units. There was no search.

## Attempt and exact result

Candidate commit before correction:
[`ab17c2f`](https://github.com/mountain/adva/commit/ab17c2f30b273e5dc47bcee5baced1810baf45df).
The first bounded-acceptance run stopped at `rustfmt --check` with exactly two
formatting differences: one import wrap and one single-line closure.

The one permitted correction replay produced
[`14d2d22`](https://github.com/mountain/adva/commit/14d2d22067c7fbc6038354f482ec6e7dbfd63945).
Formatting then passed. The next command was:

```text
cargo clippy --locked -p adva-lisp --test native_input_binding_certificate -- -D warnings
```

It stopped before test execution with two `E0308` errors at the same comparison:

```text
expected DiagramValidationArtifact, found SharedProgramDiagram
```

The exact residual is that `import_diagram_json` returns a validated artifact,
not its diagram result. The candidate compares `imported_source` and
`imported_residual` directly with the two current diagrams. The minimal next
edit is to compare `imported_source.result` and `imported_residual.result`.
That edit was deliberately not made in this round because it would require a
second correction replay.

Evidence:

- [draft PR #228](https://github.com/mountain/adva/pull/228)
- [first bounded-acceptance run](https://github.com/mountain/adva/actions/runs/40340677547)
- [correction bounded-acceptance run](https://github.com/mountain/adva/actions/runs/40340866592)

## Costs and unperformed work

- Routes: one construction route; zero search candidates.
- Constructed cases: two intended positive receipts, seven intended Refused
  controls, and one intended byte-budget Unknown control.
- First remote execution: formatting stopped the workflow; no compilation or
  receiver execution occurred.
- Correction: two formatting hunks; one correction replay, exhausting the
  frozen correction allowance.
- Second remote execution: formatting passed; the clippy command ran for about
  6.1 seconds before the two type errors stopped compilation.
- Serialization, native validation, receiver, reuse, and assertion costs: not
  measured because no test binary was produced.
- Peak memory: not measured. No file size is used as a memory proxy.
- Search, arithmetic evaluation, and candidate enumeration: zero.

Therefore neither positive receipt, refusal behavior, byte-budget behavior,
nor reuse has been experimentally established. The encoded cases remain
unexecuted targets.

## Vocabulary and utility

No new word is promoted. Existing terms—validated import artifact, complete
snapshot binding, qualified occurrence, Refused, and Unknown—already express
the discovered boundary.

For Mingli Yuan and a later agent, the round narrows the continuation to one
typed projection rather than inviting a schema redesign or a second search
route. It also records that validated import returns evidence together with a
diagram, so a receiver must choose the checked `result` explicitly. No measured
benefit to Jiamin Zhao's real tasks is claimed.

## Smallest continuation

On the next round only:

1. replace the two direct imported-artifact comparisons by comparisons of
   their `.result` diagrams;
2. make no schema, fixture, budget, or case expansion;
3. run the same bounded-acceptance workflow once;
4. if it passes, record the test count, encoded request byte counts, runtime,
   and any available peak memory; otherwise retain the new exact residual as
   Unknown without another broad rerun.
