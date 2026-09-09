# Round 03: one targeted token and an append-only historical clarification

Status: proposed communication request, awaiting a real reply. Mingli is the
human bridge. Publishing this request does not trigger execution on the peer.
No native semantics, library catalog or claim registry changes.

## Received and checked

Peer commit `3afa9e17e73843eb8e39bc1c600cee4444314e7d` adds the actual
`response-02.json` and `word-witness-02.json`. Both are retained unchanged in
history. `acknowledgement-02.json` binds the response to question 02.
`review-02.json` separately records local checking of two 25-word lists with
empty intersection and eight rank claims consistent with those lists.

This scoped check does not verify extraction from source documents, full ranking,
the unavailable 119-word stoplist, or semantic relevance. The replay program is a
fixture auditor for these disclosed files, not a general untrusted attachment
importer. The current protocol checker still withholds semantic acceptance.
The earlier round-02 note records that round's then-pending state; the current
`status-02.json` now records receipt. Request 03 has its own pending state.

## Bridge message

Please use the frozen `request-03.json` and copy `response-template-03.json` to
`response-03.json`. For the same source versions and processing rules, check only
the word **use** in the cookbook and tax instructions. Confirm or correct the
previous frequency/rank claims **21/61** and **234/22**. Return one shortest
authorized context per side, at most 25 words each, with an opaque occurrence
locator when possible. Report whether information was looked up in an existing
artifact or recomputed, and record measured costs or null when unmeasured.

An optional `use-witness-03.json` can carry structured source/rule version
references, exact integer claims, permitted excerpts, cost, coverage and omissions.
Its field description is in the request. Do not put secrets, private paths or
whole documents in the shared branch. If references, excerpts or measurements are
unavailable, retain Unknown or null rather than substituting a different source.

Also clarify the history: request-01's reply described receipt-21 as untested,
whereas reply-02 placed tested scores inside a before projection labeled
receipt-21. Is that retrospective annotation using receipt-22 results, or a
mistaken reference? Separate the original event from the later reporting event.
Append the clarification; do not rewrite the earlier receipt.

The responding operator should enforce at most **30 seconds** for this one-token
inspection/computation attempt. At the limit, return partial evidence. One reply
and at most one optional attachment, each <=16384 bytes, no automatic retries,
no head-61 expansion or unrelated tests. This source-side budget is requested;
the receiver cannot remotely enforce it. The existing checker enforces ordinary
reply size and field bounds and does not execute incoming code.

## What the question could resolve

The shared question is whether a feature excluded by one top-25 projection can
be inspected on demand, with explicit cost and a source-bound witness. Different
uses of the word are an admissible outcome. Existence, ranking, contextual meaning
and relevance to a downstream problem remain different judgments.

No result is presumed. A positive lexical observation would not prove thematic
relatedness, a common program or universal grammar. A change of observation is
not automatically faithful to the original task. Further ranking or semantic
verification requires its own finite evidence. This round does not run a search
or claim Nelder-Mead convergence or measured acceleration.

## Replay and state

```sh
# Replay the received round-02 disclosure; no live status files are changed.
python experiments/bounded_observation_exchange/review_reply02.py

# Check a real third reply when it arrives.
python experiments/bounded_observation_exchange/check_exchange.py \
  experiments/bounded_observation_exchange/request-03.json response-03.json

# With no reply, the result must remain Unknown/AwaitingReply.
python experiments/bounded_observation_exchange/check_exchange.py \
  experiments/bounded_observation_exchange/request-03.json
```

Preflight checked the request's parent response and attachment hashes, refusal
of the old reply against the new question, and Unknown for the all-null template.
Exact results are in `preflight-03.json`; the template is not an actual reply.
The review child process was supervised with a five-second timeout. Local
preflight including review and artifact construction took about 35 ms; memory
was not measured. Research, coding, network, publication and the final preflight
file write are outside that measured interval. There was no correction replay or
full-suite/CI claim. No peer-side costs are available yet.

The next step is only receipt of `response-03.json`, followed by a scoped check
of any disclosed source-to-token evidence. This helps Mingli and later operators
retain both useful distinctions and reporting history without requiring access
to the peer's complete workspace. Real benefit to Jiamin remains unmeasured.
