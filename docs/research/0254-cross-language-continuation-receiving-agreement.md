# Research 0254: Cross-language continuation receiving agreement

Status: **bounded finite implementation comparison**. This note adds no native
operation, framework `accept`, executable continuation permission, new fuel or
vocabulary word.

## Question and frozen boundary

[Research 0253](0253-terminal-resolution-continuation-tuple-gate.md) binds one
terminal-resolution receipt to one exact problem--history--budget tuple, but
its classification is produced by one Python receiver. The next declared
question was deliberately narrower than another semantic extension: does a
separately implemented Node receiver, given the exact same frozen bytes,
reproduce the three-way classification and byte-identical preserved tuple?

The [contract](../../experiments/continuation_resolution_crosscheck/contract.json)
freezes one route, ten Node processes, zero Python receiver and target
processes, one second per child, twenty outer seconds, 40,000 Node work units,
1,000 comparison units, zero search candidates and zero correction replays.
It pins the Research 0253 execution, Python receiver and new Node receiver by
SHA-256. The receiver uses only Node's `crypto` and `fs` modules. It parses and
validates the selected bytes itself rather than invoking or importing Python.

The comparison projection is intentionally small:

1. one of `ContinuationReady`, `UnknownContinuationState` and
   `InvalidEvidence`;
2. the canonical bytes of `preserved_continuation`, including `null`;
3. zero fuel and the false authority boundary;
4. distinct implementation-source coordinates.

Only a match on the first two under distinct source coordinates yields the
local result `ImplementationAgreement`. A missing implementation result,
identical source provenance, classification divergence or preserved-tuple
divergence yields `UnknownImplementationAgreement`. These are result labels,
not proposed framework words.

## Result

The sole execution passed 104 explicit supervisor checks. All ten inherited
cases agree:

| Inherited family | Count | Both implementations |
| --- | ---: | --- |
| exact Alpha completion and independent Gamma cancellation | 2 | `ContinuationReady` |
| parent or internal binding divergence | 5 | `UnknownContinuationState` |
| invalid parent or representation | 3 | `InvalidEvidence` |

For every case, the two preserved tuples encode to identical canonical bytes.
Every selected query, continuation and terminal-resolution receipt has the
same SHA-256 before and after the Node process. Every semantic fuel delta is
zero, all effect, retry, refund, mutation, native and `free` authority flags
are false, and no target starts.

Four comparison-only controls return `UnknownImplementationAgreement`:

- a copied Node projection with its classification changed;
- a copied ready projection with its retained budget changed;
- identical semantic results presented with the same source fingerprint;
- a missing second result.

The first two distinguish classification from the retained object. The third
prevents a copied implementation from being presented as two-implementation
agreement. The fourth preserves absence as unknown.

## Measured cost

The retained [execution](../../experiments/continuation_resolution_crosscheck/evidence/attempt-1/execution.json)
records:

- ten Node processes, zero Python receiver and target processes;
- 17,865 Node structural work units and 49 comparison units;
- 0.537914088999969 seconds summed Node-process wall time;
- 0.5481653790002383 seconds whole-run time;
- 0.0035979150002276583 seconds evidence serialization time;
- 35,452 KiB maximum child RSS and 12,160 KiB supervisor RSS;
- zero search candidates and zero correction replays.

The RSS values are process-category maxima, not concurrent aggregate memory;
the V8 old-space flag is not a total-process memory bound. Construction,
authoring and publication time are unmeasured. One later direct validation
loaded both test functions without pytest, ran one fresh ten-process replay,
checked Node syntax and Python byte compilation, and parsed 230 unique claims.
It took 0.7264199559999724 seconds; the fresh replay used another 17,865 Node
units, 0.5502297289986018 seconds of Node wall and 0.5636819829996966 seconds
whole-run wall, with 37,632 KiB child and 13,804 KiB supervisor RSS maxima.
Thus primary plus validation used twenty Node processes and 35,730 counted Node
units. Pytest itself was not run in this environment; no pytest result is
claimed. The publication-boundary history check then scanned 5,325 unique
blobs and 14,119 members in 9.340146699 seconds and found no identified
withdrawn copy.

## Meaning and residual

No new word is justified. Agreement between these two programs is useful
process evidence that the selected result is not an accidental Python-only
projection, but both implementations share the same written specification,
fixtures, host, SHA-256 library and comparison supervisor. Common-mode defects
remain possible. This is neither independent human review nor mathematical
truth, and disagreement would not be a semantic counterexample.

This helps Mingli and later agents hand the exact same finite question to a
second tool without losing the problem, ordered history, budget or unresolved
state. Its practical value for Jiamin's actual task remains unmeasured.

The experiment does not authenticate producers, contain hostile processes,
prove power-loss durability, establish distributed consistency or exactly-once
execution, or perform the continuation. It does not implement native
`communicate`, `accept`, `free` or `Close`, establish Research 0090 coverage or
Research 0092 promotion, close M6, prove hypothesized arithmetic truth or
establish arithmetic universality.

The next minimum step is a held-out transport test: a third process should
construct one new canonical problem--history--budget tuple and terminal receipt
without importing either receiver, then both receivers should classify those
bytes. The constructor must not supply the expected answer. Agreement remains
finite evidence; divergence remains unknown.

Authored by ChatGPT (OpenAI), contributed under Unknown v0.3 through Mingli
Yuan's authorized GitHub account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee.
