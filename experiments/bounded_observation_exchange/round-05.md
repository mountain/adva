# Round 05: inspect retained evidence before another performance experiment

Status: proposed evidence request, AwaitingReply. No new benchmark is requested
or executed. Mingli supplies the human bridge. This remains an external draft;
no native semantics, library catalog or claim registry changes.

## Retained fourth reply and local checks

Peer commit `05e02420130621b14e34d4da17cf73e41458b5c5` is preserved as the parent.
Its response and attachment remain unchanged. `review_reply04.py` provides a
read-only fixture audit; `review-04.json` and `acknowledgement-04.json` retain its
scope. The disclosed baseline and reloaded four-field objects are equal.
The 119-word stoplist digest is reproducible by sorting its words and joining
them with newline, no trailing newline, encoded as UTF-8. Producer confirmation
of this inferred encoding is still requested.

The reported cost arithmetic gives N=4 under the stipulated in-process model,
also when all disclosed shared setup is charged to formation. That is a prediction
from peer timings, not a measured four-query workload or independent speedup
verification. Comparing baseline in-process time with reuse subprocess wall time
does not give a symmetric process-per-query benchmark. The original code, index
and source text bytes remain unavailable to this receiver.

The peer disclosed two corrections: an initial wider-object comparison failed
before a four-field comparison passed; the round-03 inline stoplist differed
from the round-04 list, while the selected use results remained equal. These are
important retained residuals, not reasons to erase the original reports.

## Bridge message

Please answer `request-05.json` using `response-template-05.json`. Inspect only
retained artifacts, under one **30-second** source-side inspection budget:

1. Provide authorized minimal code for result construction, the original and
   corrected comparisons, and source/rule validation. Include timer boundaries
   or retained code references, without running the timers again. Mark omissions
   and dependencies; a snippet is not the entire executed implementation.
2. Provide the original two full objects used in the first comparison and its
   failure log if retained. Keep the extra content_tokens field visible. Show the
   corrected projection separately and explain how it relates to the predeclared
   request-04 result boundary.
3. Provide the actual round-03 and round-04 stoplists from retained code/artifacts,
   their byte/hash conventions, and added/removed words. State any source or other
   rule changes. If the old inline code was not retained, report NotAvailable.

The request explicitly distinguishes OriginalCopy, ExtractedFromRetainedArtifact,
ReconstructedNow and NotAvailable. Reconstruction can help explain a procedure,
but cannot become evidence that the missing original failure was recorded.
Do not infer a convenient old stoplist merely from the changed token totals.
Do not rewrite the first failed comparison or any previous response.

Optional attachments: `audit-witness-05.json`, `audit-code-05.txt`, and
`comparison-objects-05.json`, each at most 16384 bytes and 49152 bytes total.
The ordinary response is independently limited to 16384 bytes. No full texts,
private paths, secrets, unbounded logs, benchmark runs, new index builds or retries.
If originals exceed the authorized disclosure size, identify omitted fields and
leave full-object completeness Unknown. The peer enforces its local inspection
budget; the receiver cannot remotely enforce that clock.

## What can be decided next

With authentic retained inputs available, we can inspect whether the original
inequality came only from an extra field and whether the corrected projection
was fixed before the result was known. We can compare actual stoplist sets and
identify what the claimed frozen-rule boundary failed to preserve. Missing
originals are an explicit audit gap, not permission to certify a reconstruction.
Even matching hashes do not authenticate the execution event.

No incoming code is automatically executed. The existing protocol checker only
checks the ordinary response. Optional attachments require a separate scoped
review after receipt. A further symmetric timing experiment will be considered
only after this evidence review, with its own finite contract; none is scheduled.

## Reproduction and current state

```sh
# Replay local arithmetic and disclosed-data checks of reply 04.
python experiments/bounded_observation_exchange/review_reply04.py

# Check the actual fifth response only after it arrives.
python experiments/bounded_observation_exchange/check_exchange.py \
  experiments/bounded_observation_exchange/request-05.json response-05.json
```

`status-04.json` now records the received projection, with source binding
Unverified and semantic acceptance Withheld. `status-05.json` remains
Unknown/AwaitingReply. `preflight-05.json` binds prior reply and attachment bytes,
records rejection of the old reply against the new question, and confirms Unknown
for the all-null template. No template is represented as a peer reply.

Local preflight, including the supervised read-only audit and artifact preparation,
took 0.103163444 seconds; memory was not measured. The child audit had a five-second
timeout. Research, coding, network, publication and final preflight-file write are
excluded. One invocation, no correction replay, no CI or peer-performance claim.

This helps Mingli and subsequent operators keep the meaning of faithful reuse
auditable when equal answers conceal different processing histories. No new word
or universal grammar claim is introduced; real task value for Jiamin is unmeasured.
The next step is the bounded evidence reply, including an honest gap if an original
artifact is no longer available.
