# Keraia read boundaries and weighted prefix search

Status: bounded external calibration, 2026-09-14, based on main
`4ebffc16cdec247f36496d8416ae5feef07f06b2`. Accepted evidence is
[`attempt-2`](../../experiments/keraia_read_machine/evidence/attempt-2/).
The earlier attempt and a receiver defect remain on the record.

Authored by ChatGPT (OpenAI). Mingli Yuan supplied the research direction;
his GitHub account is the authorized submission proxy, not evidence of human
authorship, review, endorsement or correctness. The assistant implemented
and reviewed both interpreters; their different representations are useful
cross-checks, not independent human review.

## Question and imported boundary

The [Zot calibration](zot-prefix-machine-weighted-sharing.md) left Keraia's
runtime input boundary open. The [Möbius composition review](mobius-transport-composition-boundary.md)
shows why a receiving context must be selected separately from a proposed
receipt. This step applies that discipline to explicit input position, cost
and continuation state; it imports no Möbius or native Q4 witness.

The source is Michael Stay, [Very simple Chaitin machines for concrete AIT](https://arxiv.org/abs/cs/0508056),
sections 8–9 and Appendix B, read as text and page images. The prefix variant
uses its first complete binary tree as program and subsequent bits as input;
residual leaves denote the reader. The article discusses normalization while
its appendix uses lazy functions. We therefore declare a separate weak-head
profile and do not silently equate those stopping criteria. The appendix was
read, not executed in this round; the new implementations are independently
written and do not vendor its JavaScript.

`keraia.appendix-b.cbn-whnf.read.v0` performs call-by-name weak-head reduction
with greedy variable marking. Applying `R` to an argument `x` consumes one
bit: `0` returns `K x`, `1` returns `I`. A bare `R` is already a returned
function. Evaluation does not descend under a returned lambda. Unread data
is `Overflow`; missing tree syntax, a demanded but unavailable input bit and
spent fuel are `NeedSyntax`, `NeedInput` and `UnknownFuel` respectively.

The finite family and budget were frozen before execution in
[`contract.json`](../../experiments/keraia_read_machine/contract.json).
All 4,095 binary strings of lengths 0–11 are checked at semantic fuel cuts
8, 32 and 128. There are 65 distinct complete program descriptions in that
family. Fifteen fixtures additionally cover identity, both printed K
encodings, one-bit reads, unread suffixes, a self-application loop, and
discarding that loop under call by name. Open-term substitution controls
check capture avoidance. These fixtures extend to 39 bits; they are not an
exhaustive longer-code search.

## Executable state and receiver

An immutable external de Bruijn term, ordered argument stack, absolute
cursor, profile and cost convention define a pure-segment boundary. A segment
stops before reading, on weak-head return, or when its allowance expires.
Application-spine push, beta contraction, primitive read and final return
each cost one semantic step. Waiting for input costs no step. Compilation,
term traversal and receipt inspection consume separately counted host work.

Before cache admission the receiver replays the exact segment and verifies
start, end, cost and stop reason with type-preserving comparison. Hits debit
the original semantic cost and retain the caller's source and read history.
The checker shares the primary transition kernel; it is an integrity check,
not a second derivation of that cost semantics. The independent named-term
oracle checks output, input order and consumed length at the largest cut;
its own reduction budget is 512 and is not called the same step count.

Prefix traversal branches only at missing syntax or demanded input. A
`NeedInput` branch receives a copied state and one bit, with all previous
steps still spent. A checkpoint retains control, stack, cursor, source,
history and remaining/original fuel. Restoration replays from source and
fuel independently supplied by the receiver. This validates event-frontier
checkpoints only; arbitrary mid-step restoration is not implemented.

For the paper's one-read example `11101001010011000`, the recorded frontier
has cursor 17, 3 steps spent and 125 of 128 left. Appending `1` returns `I`
after 5 total steps, identical to uninterrupted execution. Providing only
4 total steps remains `UnknownFuel` even with a warm cache. Changed profile,
cursor, trace, residual, fuel or receiving source is refused by the controls.

## Exact mass and measured work

All three fuel cuts give the same result. Direct execution and checked cache
agree on every ledger field. Resumable prefix search reproduces exactly the
same accepted-code ledger; it deliberately does not enumerate the rejected
suffix extensions of an already accepted code.

| Direct enumeration outcome | Number of code words |
|---|---:|
| `Halt` | 54 |
| `NeedInput` | 35 |
| `NeedSyntax` | 988 |
| `Overflow` | 3,018 |
| `UnknownFuel` | 0 |

The accepted codes and the search's 485 unresolved prefix cylinders are a
checked prefix antichain with exact Kraft partition

\[
\frac{1563}{2048}+\frac{23}{2048}+\frac{462}{2048}=1.
\]

The terms are accepted mass, pending-read mass and incomplete-syntax mass.
There are 23 pending-read and 462 incomplete-syntax frontier words, all of
length 11. The prefix traversal visits 1,077 nodes. Its terminal cylinders,
not the overlapping incomplete words in direct enumeration, are what the
mass calculation sums. For the eventual halting mass of this declared
profile the retained interval is only `[1563/2048, 1]`; unresolved mass is
`485/2048`, about 23.68%. About 95.26% of that residual is incomplete syntax.

| Method | Executed pure steps | Verification replay steps | Read steps | Total dispatch work |
|---|---:|---:|---:|---:|
| Direct enumeration | 4,002 | 0 | 744 | 4,746 |
| Checked segment cache | 112 | 112 | 744 | 968 |
| Resumable prefix search, no cache | 132 | 0 | 24 | 156 |

The cache has 71 entries and 3,780 hits. Including replay dispatches gives
4.90 times less dispatch work for the cache and 30.42 times less for prefix
search against this exhaustive baseline. These are evaluator dispatch
counts, not total host operations or algorithmic complexity bounds. The
baseline spends substantial work on unread suffixes that prefix search
never needs to visit.

Wall time gives a narrower conclusion. At fuel 128, the corrected primary
run measured 38.10 ms direct, 42.22 ms cache and 8.81 ms prefix search. The
fresh process measured 39.63, 41.78 and 7.95 ms respectively. Thus checked
cache alone was slower in these two measurements; prefix search was about
4.3–5.0 times faster. These short single-host observations are not a robust
benchmark. The full corrected campaign used 409,011 host-work units and
28,820 assertions per process, approximately 0.35 seconds and 22.2 MiB RSS.

Equal outputs do not merge probability events: `1001` and `11000` both return
`I`, but together contribute `1/16 + 1/32 = 3/32`. Keeping only the first
representative loses `1/32`. Receipts share computation; the per-code ledger
keeps each weight and provenance.

## Source discrepancy and retained implementation error

Under the declared greedy marking profile, the literal section-8 K encoding
`1100110101000` and Appendix-B encoding `11010100110010100` compile differently.
Applying each to `I` and `R` gives `R` and `I`, respectively, in both new
interpreters. The outer variable marker in the shorter encoding also marks
the apparent inner lambda marker. This is a discrepancy between literal
examples under this profile, not a refutation of the article's universality
result. Neither source example was silently replaced. Both codes and outputs
remain in `source_comparison` and `fixtures`.

Attempt 1 and its fresh replay passed 28,819 assertions each. Subsequent
review found that Python equality treats `True` as `1` and integer-valued
floats as integers. Four finite probes reproduced an evidence-boundary
failure: altered checkpoint step/cursor fields and altered receipt cursor/
variable-index fields were accepted. Their record is
[`type-boundary-red.json`](../../experiments/keraia_read_machine/evidence/attempt-1/type-boundary-red.json).
This initial passing campaign did not establish a strict type boundary.

The separately frozen [`correction-1.json`](../../experiments/keraia_read_machine/correction-1.json)
authorized one necessary correction within the same search family and
budgets. Receipt comparison now preserves types recursively; checkpoint
comparison uses canonical JSON with integer, float and Boolean distinctions.
All four bad cases are refused in attempt 2 and its fresh replay. Attempt 1's
exact source copies and all results remain intact. No scope expansion or
second correction was used.

The two campaigns each have one primary plus one conditional fresh process.
Each child is limited to 15 million work units, 45 wall seconds, 40 CPU
seconds and 512 MiB; the outer supervisor caps execution and evidence
comparison at 100 wall/95 CPU seconds. The four red probes had their own
20,000-work/5-second contract and used 60 work units. Total recorded child
work across both attempts and those probes was 1,611,874 units. No native
Rust tests or full repository suite were run for this external-only change.

## What this advances, and what remains open

The executed result is a resumable prefix interpreter whose accepted-code
weights survive checked computational reuse. It supports the practical
direction of removing repeated prefix execution before attempting more
expensive equivalence-based compression.

It does not yet establish a Q4/M6 transport or a commutativization of ACS.
One candidate next square would compare executing a demanded suffix directly
with first transporting a pure segment and then continuing that same suffix,
preserving ordered reads, total fuel and source weights. The current receiver
and one-bit continuation provide finite ingredients for that question;
general segment composition and a native Q4 witness are absent.

There is also no accelerated convergence result for Chaitin's halting
probability. The profile's relation to a fixed optimal prefix machine is
unproved; the 8/32/128 cuts already agree on this small family, so it contains
no slow halting tail to measure. Faster enumeration does not reduce the
unresolved interval at the same cut. A useful next finite contract would
need multi-read and delayed-return programs plus a justified residual-mass
bound or a direct comparison against a fixed optimal machine. The present
run stops here; it does not automatically enlarge the search.
