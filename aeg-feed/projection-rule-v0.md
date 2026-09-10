# Projection rule v0 (public, path-free)

The deterministic mapping used by the AEG-side projector to turn a pair of
receipts into a bounded-exchange response. A receiver holding the feed
bytes can re-derive the three projected strings and check excerpt equality.

## Inputs

- Two receipts from the feed (`receipts/receipt-NN.json`), one for `before`
  and one for `after`.
- A frozen request file (any request using `declared-field-projection-v1`).

## Mapping (per receipt)

| projected field | source fields | rule |
| --- | --- | --- |
| `task` | `delta.kind`, `delta.description` | `"{kind}: {description}"`, truncated to 1024 chars, trailing `...` if cut |
| `result` | `status`, `evidence` (top-level keys) | `"{status}; evidence keys: {k1}, {k2}, ..."` (keys sorted), truncated to 1024 |
| `residual` | `documented_holes` | `"documented_holes: {h1} | {h2} | ..."`, or `"documented_holes: none declared"`, truncated to 1024 |

Truncation marker: a string longer than 1024 characters is cut at 1021
characters and the last three characters are replaced by `...`.

## Response shape

Standard `declared-field-projection-v1` response: `before.record_ref` and
`after.record_ref` are the opaque labels `receipt-NN`; `request_sha256` is
the SHA-256 of the exact request bytes; `sender_claim` is fixed as
"AEG operator mechanical projection; label unauthenticated"; `omissions`
is fixed as "Mechanical projection of receipt fields; no semantic
acceptance; witness carries byte pointers."

## Witness shape

`aeg.projection-witness` v0: both receipt pins (`receipt_sha256`),
feed paths (`receipts/receipt-NN.json`), the request and response pins,
the JSON pointers for each projected field, and the verbatim excerpts
(`delta_kind`, `delta_description`, `status`, `documented_holes`).

## Verification a receiver can perform alone

1. `python3 aeg-feed/feed_check.py aeg-feed` → FeedConsistent.
2. For each side, load `receipts/receipt-NN.json` and check that the
   excerpts in the witness equal the receipt's field values verbatim.
3. Apply the mapping rule to those values and check the result equals the
   corresponding projected string in the response.
4. Check `request_sha256` equals the SHA-256 of the request bytes it holds.

Step 3 is exact, not approximate: the mapping is total over the declared
fields and uses no local state. Interpretation beyond literal equality is
not part of this rule.

## Limits

- The rule projects the declared fields only; it does not extract meaning,
  judge relevance or verify any mathematics.
- `evidence` may contain nested objects; only its top-level keys appear in
  `result`, as names, not as values.
- Receipts with missing `delta`/`status`/`documented_holes` fields project
  to the strings `unknown: ` / `Unknown; evidence keys: ` / the
  none-declared form — the rule never invents content.
