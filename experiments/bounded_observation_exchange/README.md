# Bounded observation exchange: one request across a private boundary

Status: proposed external protocol experiment. Base Adva commit:
`17fe19e283011f3c4361112f2fe25e4cdae9407e`. No native semantics change.

The local AEG workspace is not available to this receiver. A published reference
to its receipts does not provide the receipt bytes or a way to reconstruct them.
This experiment instead makes one concrete request an authorized AEG operator can
answer without disclosing that workspace. Publication does not establish delivery.
There is currently **no real peer reply**; `status.json` is `Unknown/AwaitingReply`.
All reported successful comparisons are explicitly synthetic controls.

## Frozen question and boundaries

`request.json` asks for one before/after observation relative to an explicitly named
predecessor. Its observation grammar consists of exactly three fields: `task`,
`result`, `residual`. Values are strings of at most 1024 characters, or JSON null
for unavailable/withheld information. References are bounded opaque labels, not
native identities. The contract version and observation method are fixed.

The finite question is whether these three **disclosed strings** differ. There is
no search over source objects and no inference from silence. Literal equality is
not semantic equivalence. A paraphrase can change the observation; different
source records can produce the same observation. Both are retained as limitations.
Field coverage here means coverage of this declared three-field projection, not
coverage of the source repository or all legal arithmetic possibilities.

The two three-port interfaces are an engineering proposal:

| Side | Three inputs | Three outputs |
| --- | --- | --- |
| Sender | source records; question; disclosure/resource contract | record references; finite projection; omissions |
| Receiver | response; fixed checker; original request bytes | byte-bound acknowledgement; scoped judgment; remaining obligation |

The common object is the question/contract and its exact request bytes. This
organizes partial communication; it does not prove that the interfaces instantiate
the proposed mathematical duality of three-hole expressions. No inverse map from
a digest to an inaccessible source is assumed.

## Existing vocabulary, with observable scope

This reuses Research 0139 (`docs/research/0139-library-six-phase-and-communication.md`)
and the scoped `evidence-stutter` distinction. It registers no new native word.

* `send`: publish a request for possible retrieval; delivery remains unconfirmed.
* `receive`: supply response bytes to the local checker.
* `acknowledge`: after schema and request binding pass, return SHA-256 references
  to the exact request and response bytes. This is an unsigned local receipt.
* `accept`: semantic acceptance is always `Withheld` in this prototype.

The three outcome cases are `VariationObserved` for at least one unequal field
with all six values disclosed, `EvidenceStutter` for equal complete projections,
and `Unknown` if any value is null or a reply has not arrived. Known changed fields
remain recorded even when the total result is Unknown. Wrong bindings, malformed
fields, duplicate JSON keys and oversized messages are `Rejected`.

Hashes are byte references under the usual collision assumption, not authentication
or proof of historical provenance. Sender labels and predecessor labels remain
unverified claims. The checker must be given the locally selected original request;
it does not choose a trustworthy request from an incoming packet. Whitespace edits
change the request hash intentionally. The checker never fetches links or executes
incoming source code. Replaying the same inputs gives the same receipt and grants
zero resources; durable deduplication, equivocation detection and global exactly-once
delivery are outside this stateless prototype.

## Minimal handoff

An operator who already has authorized access to the AEG source can:

1. Read the frozen request. Limit inspection to the requested 30 seconds; stop with
   nulls/omissions if that is insufficient. Do not copy private documents, secrets
   or private filesystem paths into the reply.
2. Copy `response-template.json` to a response file. Preserve `request_sha256` and
   `method`. Replace the template labels with opaque source labels, fill authorized
   fields, and explain omissions. Null values are valid partial communication.
3. Return that one JSON file through a shared authorized surface, such as the same
   branch or a user-provided attachment. No response is sent automatically here.
4. The receiver checks it using the exact published request file:

```sh
python experiments/bounded_observation_exchange/check_exchange.py \
  experiments/bounded_observation_exchange/request.json response.json
```

The template is not a received message. Its pending status must never be replaced
with a synthetic test result. Genuine semantic acceptance would require a further
authorized source-to-projection witness and a checker for the particular assertion.

## Resource bound, replay and evidence

The receiver reads at most 16385 bytes from each input and rejects beyond 16384.
It compares exactly three fields, with bounded string lengths; no retries, network
calls, candidate search or fuel replenishment occur. The source-side time limit is
a requested contract, not something this receiver can remotely enforce.

```sh
# Reproduce synthetic controls and the new-instance reuse; overwrites local evidence.
python experiments/bounded_observation_exchange/calibrate.py
# Inspect the real exchange state: remains Unknown/AwaitingReply.
python experiments/bounded_observation_exchange/check_exchange.py \
  experiments/bounded_observation_exchange/request.json
```

`fixtures.json` preserves exact synthetic request/response strings and expected
statuses. `synthetic-response.json` is clearly labeled synthetic. Thirteen controls
passed: difference, equality, partial coverage, missing reply, wrong request, wrong
method, invalid boolean version, duplicate JSON keys, oversized response, omitted
field, changed-question replay, new-instance reuse and repeat delivery. Every case
also checks withheld semantic acceptance and zero resource grant. Serialization
roundtrip is separately checked. The new instance changes only the residual field.

Measured construction, verification including reuse, serialization replay and
artifact writes total 0.002321111 seconds; process peak RSS is 10752 KiB on Linux.
Individual stages are in `evidence.json`. Research/coding/network/publication time
and the final evidence write are excluded. No acceleration or expressiveness gain
is claimed. No arithmetic zero/one test, native `free`, Seal, M6 filler, global
closure or universal grammar completeness is established by these controls.

This helps Mingli and later human/AI operators ask for a checkable piece of progress
without assuming access to the other workspace. Its value for Jiamin's actual task
has not been measured. The next smallest step is one authorized real response;
the next verification obligation is source-to-projection faithfulness, not a larger
communication framework.
