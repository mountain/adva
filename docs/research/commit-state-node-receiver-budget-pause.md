# Cross-language commit-state receiving pauses at the frozen work boundary

Date: 2026-09-22. Status: **Unknown / paused bounded experiment**; no new word
and no revision of the Proposed `commit-state-reconcile` record.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
not his review, endorsement or correctness guarantee. Original code, prose and
synthetic controls are contributed under Unknown v0.3. The only input bytes are
the project's already admitted, merged snapshot archive.

## Dependency and frozen question

PR 203 merged at `d6b9e93aa8f063cc2dd3fedafaa71bb4292ed545`.
Current main was `79f6353511d736ae743b109f1c573b652eff170a` and had no
open pull request. Later main changes repaired terminology checks, recorded an
unrelated boundary-gluing distinction, classified resource-limit sites and
reconciled the six-query plan; none changed the snapshot relation.

The previous residual was that both projection builders and the pair receiver
used Python. This round froze the narrower question: can a Node.js receiver,
using no external package, Python semantic process, SQLite file or ledger path,
recover the same common projection and three-way result from the already
archived bytes?

The accepted JSON domain was frozen before execution: ASCII strings, unique
keys, null, booleans, arrays and JavaScript safe integers. Exact rationals remain
integer pairs. Decimal/exponent numbers, unsafe integers and non-ASCII strings
are unsupported at this boundary and must return `UnknownCommitState` rather
than being coerced. The planned campaign contained four valid pairs, the six
inherited refusals and four parser controls. Limits included 14 child processes,
three seconds and 10,000 counted work units per child, 100,000 total units,
262,144 bytes per input, 32 MiB Node old-space, 30 seconds campaign wall and one
implementation correction replay.

## Implemented boundary

`receive_pair.mjs` contains an original recursive JSON parser with duplicate-key,
depth, UTF-8, ASCII and safe-integer checks. Canonical objects sort ASCII keys;
snapshot files, body digests, receiver-selected pins, builder provenance and the
projection digest are checked independently. The only imports are `node:fs`,
`node:crypto` and `node:perf_hooks`. There is no subprocess or SQLite import and
the interface accepts only request, left-snapshot and right-snapshot paths.

The Python supervisor extracts only selected JSON members from the earlier
archive; it extracts no `.sqlite3` member. Archived Python response bytes are
comparison records, not invoked semantic code. A positive case must match their
outcome, state, allowance, stored result, projection digest, both provenance
maps and all no-authority flags.

## Executed result and retained failures

The first attempt stopped on the first case before emitting a semantic report.
The strict canonicalizer correctly rejected the report's floating
`wall_seconds` field. This was an implementation-layer mismatch between the
input grammar and diagnostic output, not evidence about commit state. The
failure is retained.

The sole permitted correction changed that diagnostic to an integer
`wall_nanoseconds` field without changing input grammar, judgment or limits.
The replay then established one positive finite result:

- the symmetric empty pair returned `ProvenUncommittedLedger`;
- its projection digest was
  `aac5e73ad70cc3183c4028c586fdcb2853d1df7ed63f4f2d61332005dbd568b3`,
  exactly matching the archived Python response;
- allowance `(grant=3, spent=2, remaining=1)`, state, both builder-provenance
  maps and every no-authority field also matched;
- the receiver used 6,841 units and 15,399,480 internal nanoseconds; its fresh
  process took 0.068292519 seconds and reported 44,360 KiB peak RSS.

The next valid case, symmetric committed, parsed enough material to reach
10,001 units and returned `UnknownCommitState` with
`Error: receiver:work-limit`. Its internal time was 15,086,386 nanoseconds.
Because the frozen expected outcome was `StoredCommitted`, the supervisor
stopped immediately. The two asymmetric cases, six inherited refusal cases and
four parser controls are **NotRun**, not failures and not implied successes.

Thus the result is not a completed cross-language receiver. It is a positive
empty-state reuse plus a precise resource obstruction for the larger committed
state. The obstruction may reflect token-level metering rather than essential
semantic cost, but the frozen contract does not permit changing that judgment
after seeing the result.

## Actual cost

Attempt zero used 0.092639492 seconds; attempt one used 0.159376474 seconds.
Their sum was **0.252015966 seconds**, excluding reading, coding and publication.
The replay supervisor accounts 6,841 accepted work units. The two emitted replay
reports expose **16,842 attempted units** when the stopped committed call's
10,001 units are also counted. Search candidates were zero and the one permitted
correction replay was consumed.

Highest child-process RSS across both attempts was **45,300 KiB (44.238 MiB)**;
highest supervisor RSS was **13,008 KiB (12.703 MiB)**. The 32 MiB V8 old-space
flag is not a total process-memory cap. The evidence package contains 26 files
and 524,525 expanded bytes; packing and full member-hash verification took
0.027289219 seconds. Archive SHA-256 is
`34885fef6444d6d6c53f9f221890d5d96c4f0461d8c0d8dab25b6b5b2ecf5622`.

## Vocabulary, usefulness and residual

**New or revised vocabulary: zero.** The partial run does not justify a new
version of `commit-state-reconcile`. It helps Mingli and later agents by showing
that one genuine cross-language projection comparison is possible and by
locating the next failure in explicit resource accounting rather than in a
silently changed semantic result. Benefit for Jiamin's real task remains
unmeasured.

The retained execution envelope still lists `commit-state-reconcile` under its
planned `revised_vocabulary` field. Because the campaign did not complete and
no terminology file changed, that field is a reporting defect, not a revision;
this note and the repository diff preserve the authoritative status.

The evidence does not establish authentication, hostile replacement defense,
power-loss recovery, original arithmetic truth, native communicate/accept,
Close/free/Seal, M6 closure, Research 0090 coverage, Research 0092 vocabulary
lifting or Research 0123 arithmetic universality. Additive zero and
multiplicative unit domains are unchanged.

The next minimum is **not** to rerun this contract with a larger number. First
freeze a revised metering relation: compare token-count charging with a
byte-block or structural-node charge on the two already selected symmetric
cases, prove that each input component is charged exactly once, and set the next
cap from that calibration before executing the remaining cases. The present
attempt stays paused and reproducible.
