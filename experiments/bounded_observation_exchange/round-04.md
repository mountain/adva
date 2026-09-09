# Round 04: version-bound reuse of one observation

Status: proposed peer request, AwaitingReply. The receiver has no original text
layers, complete stoplist or peer index. No index benchmark was run here. Mingli
supplies the bridge; publication is not delivery or consent.

## Retained third reply

Peer commit `06dcd45b0b6e30f06da33162bf88b620b0d0a42d` is retained as the parent.
`response-03.json` and `use-witness-03.json` are not rewritten. Local fixture replay
in `review_reply03.py` confirms question binding, consistency of reported 21/61
and 234/22 with the prior claims, and that the disclosed excerpts each contain
the target with the requested bounded context. It does not verify the source
frequencies, global ranking, shortest-context selection or contextual meaning.
`acknowledgement-03.json` and `review-03.json` record that scope.

The peer reports recomputation over 49510 content tokens, total 0.040119 seconds,
with no memory measurement. The two named stages sum to 0.019499 seconds; the
remaining 0.020620 seconds is not separately itemized. This is not evidence of an
incorrect total, but it prevents complete stage attribution. These are peer
measurements, not independently observed local timings.

The append-only history clarification states that the unrelated-pair scores
were first computed at round 22 and retrospectively annotated under a round-21
proposal label. It is retained as a clarification, not an authenticated copy of
the unavailable original receipts. Original event, computation event and later
reporting event should remain distinguishable.

## Single next question for the bridge

Please use `request-04.json`, copy `response-template-04.json` to
`response-04.json`, and inspect the SAME two source text layers under the SAME
rules for the SAME word, **use**. Can a saved-and-reloaded index return the same
frequency, rank, occurrence locator and short context as direct computation?
What does forming that reusable record cost, and what does reusing it cost?

The finite order is:

1. Pin exact source text-layer bytes and rule/code/stoplist versions. State hash
   scope and encoding. Disclose the stoplist and minimal reproduction code only
   when authorized; otherwise retain independent source replay as unavailable.
2. Execute one direct baseline, B, for the complete declared result projection.
3. Build one fresh index in an isolated artifact, verify it and save it. Count all
   formation, pinning, validation and serialization work in F, with shared setup
   explicitly allocated. Do not overwrite a live index.
4. Discard builder state, load the saved index, check source/rule bindings, then
   execute one reuse query. Count loading, validation, lookup, context recovery
   and serialization in R. Report warm-cache assumptions honestly.
5. Compare complete result projections. Stop on mismatch. If available within the
   same budget, change a requested rule reference in a synthetic metadata copy
   and check that the stale index is refused. Do not modify actual source files.

**Budget:** one overall 30-second source-side execution attempt, including
verification, serialization and the one optional metadata control. One baseline,
one index build, one reuse query, no retries. If implementation is unavailable,
return Proposed/NotRun with the missing step; do not turn this into an unbounded
indexing project. An ordinary reply and optional `reuse-witness-04.json` are each
limited to 16384 bytes. No full documents, private paths or secrets are requested.

Source freshness is part of the result contract. A saved digest alone does not
prove that a current mutable file still has those bytes. Either reuse the
explicitly immutable pinned snapshot or charge fresh source/rule hashing to R.
Metadata mismatch refusal does not by itself prove index contents are correct.

## Honest interpretation of cost

For N identical queries on the same version, the declared accounting model is:

    direct total = N * B
    indexed total = F + N * R

If all required costs are counted, B > R, and F >= 0, the first integer N with
strict predicted savings is floor(F/(B-R)) + 1. If B <= R, these measurements do
not establish positive amortization. Unmeasured inputs prevent the calculation.
Use the same timing boundary and result guarantee on both routes. Rebuilding
after source/rule changes must be charged separately. Index byte size and process
peak memory are different measurements.

One sample per route is a bounded calibration, not a robust speedup claim. The
warm OS cache and runtime environment can affect the numbers. Do not repeat the
benchmark just to obtain a favorable ratio. A slower route is a useful negative
result. Program/word-formation labor not measured must be disclosed separately.

The common question remains source-bound observation reuse, not whether a noun
and verb share one meaning or whether the documents are thematically related.
The arithmetic sets from round 02 are not claimed to model this text pipeline.
No new vocabulary, stable API, native identity, free/Seal, global convergence or
universal grammar claim is introduced.

## Replay and continuation

```sh
# Read-only audit of the received third reply.
python experiments/bounded_observation_exchange/review_reply03.py

# Use the existing protocol checker when the real fourth reply arrives.
python experiments/bounded_observation_exchange/check_exchange.py \
  experiments/bounded_observation_exchange/request-04.json response-04.json
```

The existing checker validates only the ordinary three-string projection. Any
structured reuse witness will need a separate, explicit equality and cost review;
its availability is not pre-accepted. `status-03.json` now records receipt with
source binding Unverified and semantic acceptance Withheld. `status-04.json`
remains Unknown/AwaitingReply. Calibration scripts must not overwrite live state.

Preflight binds the third response and attachment bytes, rejects an old response
under question 04, and confirms Unknown for the empty fourth template. The local
fixture-audit subprocess had a five-second timeout. Preflight including artifact
construction took 0.057846132 seconds; memory was not measured. The final
preflight-file write, research/coding, network and publication are excluded.
One invocation; no correction replay and no CI or peer performance claim.

This helps Mingli and subsequent operators distinguish an actually reusable
observation from a short answer that hides repeated full-source computation.
It may identify a useful engineering boundary; benefit for Jiamin's real task
remains unmeasured. The next step is receipt and review of the finite benchmark,
or a concrete NotRun/Unknown obligation if that is the honest outcome.
