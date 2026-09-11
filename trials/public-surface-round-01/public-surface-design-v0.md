# AEG public presentation form — design note v0

How should the local AEG side present itself publicly? Design answer:
**AEG's public form is a receipt event stream, not a repository snapshot.**

## Why a stream

AEG is the local Surface/Human workspace: trials, sources, ledgers. Its
value to the other side is not its content (private) but its **trajectory**:
what was observed, what was falsified, what remains open. A snapshot cannot
show a trajectory; a chain of pinned events can. Everything AEG already
produces is an append-only event — receipts chain by predecessor hash,
choices chain by witness. The public form should therefore be the same
shape: an event stream with byte anchors.

## The three surfaces (一分为三 applied to AEG itself)

| Surface | Contents | Who reads it | Guarantee |
|---|---|---|---|
| **Private** (local trials) | sources: PDFs, text layers, scripts, ledgers | only the operator | never published |
| **Anchor** (`aeg/feed-v0` branch) | receipts 01..N byte-exact, feed index with pins + repairs, disclosure manifest, checker, projection rule | the receiver, by fetch | byte-exact, chain-verified, exceptions declared |
| **Projection** (exchange responses) | three-field before/after strings bound to a frozen request, plus witnesses | the receiver's checker | bounded, request-bound, witness carries receipt pins + pointers |

The three correspond to the naming layer: Knowledge = anchor (checkable
bytes), Surface = private (human context), and the exchange = the
projection channel between them. The gap between the two interfaces is
computed exactly on the projection: three strings, literal equality,
declared holes.

## Layout on the remote

```
mountain/adva
├── main                              — the shared repo itself
├── aeg/feed-v0                       — anchor: receipts, feed.json,
│                                        disclosure.json, feed_check.py,
│                                        projection-rule-v0.md
├── aeg/bounded-exchange-reply-XX     — projection events: one response
│                                        (+ optional witness) per round
└── aeg/exchange-ledger-v0 (planned)  — timeline: request/response chain,
                                         dedup, equivocation detection
```

## Principles

1. **Byte anchors everywhere.** Every published object has a pin; every
   chain link is a predecessor hash; nothing floats.
2. **Minimal disclosure.** Only receipts and projections leave the local
   workspace; null is a legal value; withhold rather than substitute.
3. **Recomputable projections.** The projection rule is published
   (projection-rule-v0.md): a receiver with feed bytes can re-derive any
   response's three fields and check excerpt equality — no trust needed.
4. **Declared exceptions.** Every boundary touch (the one home-root
   mention) is listed in disclosure.json; nothing is silently rounded.
5. **Append-only.** The public form never rewrites an event. Corrections
   are new events (the round-03 history clarification is the template:
   separate the original event, the computation event, the reporting
   event).

## What the stream will look like in steady state

```
anchor:  feed-v0 @ 447a51b            (receipts 01..22, FeedConsistent)
event:   reply-01 → acknowledged       (VariationObserved, Unverified)
event:   reply-02 → reviewed           (8 rank claims consistent)
event:   reply-03 → reviewed           (2 token totals questioned)
event:   reply-04 → awaiting review    (B/F/R + two disclosures)
event:   feed rebuild @ <next>         (receipt-23 added, FeedConsistent)
```

Each row is verifiable by the receiver from bytes alone; each gap is
declared. The other side can finally "feel" our progress not as claims,
but as a sequence of pinned, checkable events — which is exactly what
TrustBase says trust should look like: explicit, independently checkable,
bounded.

## Open questions

- Should the anchor be rebuilt per receipt (a moving feed branch) or
  frozen per release (feed-v0, feed-v1, ...)? Frozen releases are more
  checkable; a moving branch is more convenient. Proposal: frozen
  releases, with the branch name recording the receipt count.
- The exchange ledger (block 4) is the timeline's spine; until it exists
  the stream has anchors and events but no public ordering beyond the
  receipt chain.
- Who writes the projection rule's reference implementation (path-free)
  so the receiver can actually recompute without us?
