# Research 0158: An opening equation is not an anchored-content guarantee

Date: 2026-09-07. Status: completed bounded external counterexample calibration;
one research-only context gate, not a production cryptographic repair.

Motivation: Mingli Yuan's requirement that finite arithmetic evidence survive
representation changes and private-boundary crossings. This specific challenge,
formalization and proposed word are the assistant's contribution for review.

## Source state and problem formation

Inspected main: `1c5979d78dc9c2b79b633ea492c38fe09090f221`; no open PRs.
Research 0149–0157 and the stopped LABS series are now on main. The former
blanket description that all native work is NotRun is obsolete: later records
retain native/library and Rust/Lean/Metamath executions in another environment.
This run does not reproduce those campaigns. The length-20–43 LABS series is
explicitly closed by the user and is not resumed. Research 0157's free predicate
remains a proposal, and the free adapter remains unavailable in its records.

This environment has Python but no cargo/rustc. Rather than repeat a missing
backend check, this study follows the new documentary disclosure boundary in
0156. The latest source explicitly says that the second generator's discrete
log is known, while the disclosure checker accepts a complete commitment and
opening supplied in the same request. These facts form two separate questions:

1. Does knowing an opening imply a computationally binding commitment?
2. Does a valid request opening establish its connection to an earlier anchor?

Neither implication follows merely from the word `Verified`. This is a concrete
challenge to conditional evidence reuse, related to 0118/0122 and the
question-indexed distinction in 0142, not a new universal-grammar theorem.
The two words in 0123 remain Proposed. No 0090 coverage obligation is discharged,
no 0092 all-fillings promotion occurs, and unknown-syntax-building is not resumed.

The [contract](0158-disclosure-binding-contract.json) was saved before execution.
Its hash is `5ca302509d68bb53ba24166db02ce2ca3f12611be53d2a8a36afc2dd1ff26ddb`.
The unchanged `python/adva/lineage.py` hash is
`199363208f0fa541b533df2ed3f30f53dc9ffa13f2e6e49dbe7fed0748067882`.

## Route 1: the conditional finite arithmetic boundary

Write the commitment relation as

    C = g^m h^b mod p,       h = g^a,       ord(g) = r.

If a is known and invertible modulo r, then a different message m' admits

    b' = b + (m - m') a^(-1) mod r.

Consequently `m + a*b - m' - a*b' = 0 mod r` and the two commitments agree.
This is elementary modular algebra, not a discovery about Pedersen schemes.
Correctness, hiding and computational binding are separate security properties;
see Metere and Dong, [Automated Cryptographic Analysis of the Pedersen Commitment
Scheme](https://arxiv.org/abs/1705.05897), sections 3–4, for a formal treatment.
Their security result does not certify this repository's implementation/setup.

Two public small-group witnesses use p=23, r=11, g=2, h=8 and a=3:

| First opening (m,b) | Different opening (m',b') | Same commitment |
| --- | --- | --- |
| (2,4) | (5,3) | 8 |
| (6,7) | (9,6) | 9 |

All blinding values satisfy the toy's nonzero bound. Inversion of zero is
explicitly rejected. Inversion here is of a nonzero exponent-field element,
not division of an unknown scalar; modular additive zero and multiplicative
group equality retain their different types. No native A0/M1 or M6 filler is
created, and equal commitment values do not identify the two opening histories.

**Scope limitation:** the numeric logarithm of the repository's pinned H was
not recovered or supplied in the inspected source. No discrete-log search ran.
These two witnesses are not two openings of a pinned-group repository record.
They establish the conditional failure mechanism behind the documented known-log
setup. The claim that known-log parameters suffice for a *binding* disclosure
must not be inferred from hiding or from the successful equation checks.

## Route 2: the unchanged repository verifier

The producer constructs two new synthetic one-record chains, for JSON answers
14 and 31. The fresh instance changes the proposed replacement to 37 (the main
replacement is 15). Blinding values and proof nonces are fixed public fixture
numbers, not real secrets. No key generation, signing, vendor code or external
service is used. Deterministic nonces here must never be used for real secrets.

The independent fixture producer computes canonical JSON hashes and proof
equations; the unchanged repository functions validate the records, anchors
and requests. Producer and checker share Python integer arithmetic. This is
not an independent-runtime or cryptographically verified implementation.

Each call explicitly supplies `anchor_path` to `lineage.verify('disclosure', ...)`.
In this source version that branch does not read the supplied anchor. Its narrow
equation-checking result may be correct even when the caller's proposed
historical interpretation is unsupported.

| Control, repeated on the fresh instance | Raw API | Proposed context gate |
| --- | --- | --- |
| Original request and pinned anchor | Verified | ContextBoundOpening |
| Change only content, retain old opening | Rejected | Rejected |
| Replace content, blinding, commitment and proof together | Verified | Rejected: AnchoredSlotMismatch |
| Supply a nonexistent anchor | Verified | Unknown: AnchorMissing |
| Supply a different, self-consistent anchor | Verified | Rejected: TrustedAnchorMismatch |

All ten expected pairs were observed, and all ten were repeated after serialized
input-index replay against the retained request bytes. Six raw Verified results do not support the claimed original
context; the added gate grants none of those six. **These are not six false
opening equations.** The comparison tests the invalid transfer from a narrow
API result to a stronger question; it does not establish that the narrow API
miscalculates or that a generic agent necessarily makes that transfer.

The entire replacement uses a *different* commitment, not two openings of one
pinned-group commitment. Original record and anchor bytes stay unchanged. This
is not evidence of tampering with real records, forging Ed25519 signatures or
breaking the hash chain. The synthetic anchors have no signatures. Their byte
hashes are trusted inputs to this fixture, not an authenticated trust root.

## Proposed word: anchor-bound-disclosure

| Field | Exact research meaning |
| --- | --- |
| Input | Frozen one-record root, expected anchor-byte hash, supplied anchor and disclosure request |
| Action | Check anchor availability and expected hash; replay the chain; compare the exact anchored secret_slot; check the opening |
| Output | ContextBoundOpening, Rejected, or Unknown with a reason |
| Conditions | Pinned checker, fixed package/sequence, quiescent local files, explicit trusted anchor hash and finite budget |
| Witness | Original and fresh fixtures plus six refused/unknown unsupported context transfers |
| Refusal | Missing/substituted anchor, substituted slot, non-intact chain or rejected opening |
| Expansion | `Study.context_gate` in the retained calibration; exact inputs and replay command below |
| Residual | Original-content binding NotEstablished; parameter security, authentication, concurrent filesystem safety, human acceptance and native free unresolved |

This is Proposed terminology and external research code. The exact-slot match
conservatively includes proof bytes: a regenerated proof for the same commitment
would need a separately scoped relaxation. No such transport is claimed here.
Crucially, this gate **does not repair known-log equivocation**. Two valid
openings of the same anchored slot could still pass. Context binding and
computational message binding are separate obligations, not alternate names.

No stable module or CLI was changed. No native capability is granted. The word
names a reusable check sequence, not a learned theorem or a new syntax primitive.

## Execution, correction and resource account

The optional `/usr/bin/time` launcher was absent: that preflight launched no
experiment. A Python supervisor then supplied the six-second hard timeout;
the child enforced a five-second alarm/CPU cap and 256 MiB address-space cap.

The first actual child stopped during fixture construction because a request
filename collided with `substituted-anchor.json`. Its source hash was
`f68c48627e4245f9659018cf0bcbe1db83734cd721f2cdca7d36514199c566cd`.
The sole repair puts request files in a `requests/` subdirectory. No arithmetic,
checker, expected result or budget was weakened. Partial `run-01` remains;
`run-02` is the single successful correction replay. There was no further run.

| Measured work | Cost |
| --- | ---: |
| Successful fixture and toy-witness formation | 2.826 ms |
| Initial ten raw API checks | 3.136 ms |
| Initial ten context-gate checks | 9.232 ms |
| Serialized input parse | 0.072 ms |
| Complete control replay, including both policies | 7.458 ms |
| Output serialization through report | 0.274 ms |
| Output writes through report | 0.640 ms |
| Successful child, outer wall including startup/exit | 103.834 ms |
| Failed child, outer wall | 143.217 ms |
| Both actual children, combined outer wall | 247.051 ms |
| Maximum measured child peak RSS across both runs | 15,516 KiB (15.152 MiB) |

The successful child records 48 top-level repository API calls. The failed
child did not save a counter; its traceback and source place it after four
fixture API calls, before any control evaluation. For conservative accounting,
reserve 16 calls for that failed construction: 48 measured + 16 reserved = the
64-call study cap. These units do not count every nested modular exponentiation
or Python instruction. All inputs and group sizes are frozen and small.

Two toy witnesses were constructed in each child; the successful child also
rechecked both after serialization. Search candidates, native invocations,
signing-key accesses and CI retries are zero. Fresh-instance reuse is included
in the formation and ten-case timings, not a separate additive cost. Timings
overlap: do not sum formation with its serialization/write components or replay
with its per-policy components. The successful output has 19 files / 20,631
bytes; file size is not RAM. Hash-manifest and final documentation persistence
costs are not separately instrumented. Research, naming, coding and network
costs are unmeasured and are not hidden in the millisecond figure.

The added gate took more measured time than the raw equation checker in this
one-shot sample. No acceleration, cost amortization or expression-power increase
is claimed. The benefit demonstrated is more accurately scoped acceptance.

## Reproduction and handoff

From the repository root, Python 3.11+ on Linux, use a fresh output path:

```sh
python3 experiments/disclosure_binding/calibration.py --output /tmp/adva-0158-fresh
```

The program itself enforces the frozen process limits and performs one serialized
replay. An outer supervisor should additionally impose a six-second timeout.
Hard termination may leave a partial directory; without the final report this
is Unknown, not a completed calibration. The script's source pin intentionally
refuses execution after an unreviewed lineage implementation change.

- [Complete input index](0158-evidence/run-02/inputs.json)
- [Results and raw checker reports](0158-evidence/run-02/report.json)
- [Measured host costs](0158-evidence/host-cost.json)
- [Retained failed invocation](0158-evidence/failed-invocation.json)
- [Artifact manifest](0158-evidence/manifest.json)

For Mingli and later agents, this prevents a valid opening from being promoted
to evidence about a particular earlier disclosure commitment without its
context. No benefit on Jiamin's actual task has yet been measured.

Next smallest step: decide whether the intended operation promises only an
opening equation, an anchored-slot opening, or original-content binding. The
first is implemented, the second has this finite external prototype, and the
third requires an independently reviewed parameter/setup and binding contract.
Do not silently replace group constants and reinterpret old anchors. Any repair
must use versioned parameters and retain old records' weaker status.
