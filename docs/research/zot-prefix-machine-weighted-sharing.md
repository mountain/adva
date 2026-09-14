# Zot weighted sharing and the prefix-Keraia boundary

Status: external bounded implementation and parser/counting calibration,
2026-09-13. Research evidence, not native Adva semantics.

Authored by **ChatGPT (OpenAI)**. Submitted through Mingli Yuan's GitHub
account (mountain) as an authorized proxy. Mingli supplied the research
direction and the suggestion to consider Keraia. Account use implies neither
personal authorship nor technical review or endorsement.

The measured result is a reduction in repeated Zot evaluation with unchanged
finite probability accounting. The next target for a genuine Chaitin-machine
experiment is the **prefix version of Keraia**, exposing its input effects.

## Execution and provenance

Files: [experiments/zot_prefix_machine](../../experiments/zot_prefix_machine/).

Adva base: `215d652a10a090cd369cc184617b8f15d21e4814`.
Zot: mountain/zot at `2317e468551c4393fa1b6c9ec4d343a961c14770`.
The unchanged vendored source has Git blob identity
`43fcf74c885fd3abc90a2c8e5f88e177952ecbcf`, independently confirmed by
GitHub's tree response. Its original MIT license is retained.

The terminal could not initialize. The committed JavaScript machine and
checker bodies ran in the available V8 isolate. No Node process, QuickJS
executable, Rust build, Python suite or full repository CI ran on this host.
The thin Node replay wrapper was checked with mocked filesystem/path/process
interfaces; this is not a real Node filesystem or CLI test.

Replay from a checkout to a fresh destination:

~~~sh
node experiments/zot_prefix_machine/run.cjs > /tmp/zot-keraia-replay.json
~~~

Each invocation executes the fixed families once under their budgets, with
no retry or widening loop. Timing observations will differ.

## Machine and probability

The pinned Zot source applies the current continuation to each bit's
combinator and then applies an output driver. Host return is not lambda
normal-form termination. Its raw return domain is not prefix-free:
both `0` and `00` return.

This calibration defines a new wrapper:

\[
E(w)=1^{|w|}0w,\qquad \mu(E(w))=2^{-(2|w|+1)}.
\]

The unary header determines exactly how many payload bits follow. Different
lengths disagree at the shorter delimiter; equal lengths have equal code
length. Thus the codes are prefix-free. The length-n layer has mass
\(2^{-(n+1)}\); all layers beyond N have mass \(2^{-(N+1)}\).

Accept only if the pinned call-by-value computation returns and every emitted
item is a literal binary character. Returned non-bit output and type errors
are rejected by this **new observation wrapper**. Its corresponding partial
machine can be defined to loop on rejection. This does not assert that the
original Zot program fails to return. Resource limits produce Unknown.

The wrapper changes the machine and its distribution. Its convenient length
tail does not establish optimal prefix universality, algorithmic randomness,
or computed bits of Chaitin's Omega.

The explicit machine defunctionalizes closures with their captured arguments
and retains application, argument and output frames. It preserves
left-to-right call-by-value evaluation. One CEK transition is the semantic
time unit, including a boundary's Done transition. Parsing, phase bookkeeping,
interning and prebuilding the fixed driver are outside this clock but inside
measured host work. A word shares its 4096-step allowance across all boundaries.
A cache hit debits the original boundary's transition cost.

A trusted local checkpoint retains control, stack, output, step count and the
complete closure arena. Mid-evaluation serialization and restoration were
checked. This is not an untrusted import or native identity boundary.

## Measured sharing

All 1023 binary payloads of length zero through nine retain separate ledger
rows and exact code weights.

| Policy | Actual CEK transitions | Cache entries | Initial wall time |
| --- | ---: | ---: | ---: |
| Direct word replay | 125845 | 0 | 96 ms |
| Literal-prefix boundary cache | 33737 | 2045 | 30 ms |
| Exact-closure boundary cache | 13349 | 930 | 17 ms |

The last key contains complete closure syntax, captured values and the next
action, including finalization. It uses neither a tag alone nor scalar
observation or algebraic equality. Pure boundary evaluation permits reuse
while copying the output sequence and charging the original cost per caller.

Transition work falls by factors 9.427 against direct replay and 2.527
against literal-prefix reuse. These are finite interpreter-work ratios.
All policies use structural interning and still enumerate all 1023 codes.
Single fixed-order subsecond timings are not a robust benchmark or an
end-to-end asymptotic speed claim.

The three ordered ledgers agree on output, status, code weight and cost.
The independently instrumented original higher-order Zot source agrees on
all full-budget outputs and failure classifications: 945 accepted, 60 returned
non-bit outputs and 18 type errors. Its separate function-entry fuel is not
an independent CEK cost semantics. Both implementations share V8.

Warm caches were also compared with direct execution at
\(t=16,64,256,1024,4096\). At t=256 one payload remains Unknown; at t=1024
the entire finite family is classified.

For this wrapper alone, the exact interval at t=1024 is

\[
508608/524288\leq\Omega_{\rm wrapper}\leq509120/524288,
\]

or [0.9700927734375, 0.9710693359375]. Width 1/1024 is the unevaluated length
mass. Smaller time budgets also retain unresolved short-program mass.
This is an exact finite sum, not sampling or a confidence interval.

Negative controls preserve the output-changing adjacent-bit swap
`01000` -> `10000`, closure-tag equality with unequal captures, invalid frames,
deleted codes, changed weights and outputs, and a cached boundary whose
cost exceeds remaining fuel. Equal bit counts do not authorize reordering;
a representative's weight cannot replace its fibre's mass.

## Why prefix-Keraia

Michael Stay's
[Very simple Chaitin machines for concrete AIT](https://arxiv.org/abs/cs/0508056)
distinguishes the original Keraia BEM in section 8 from the modified universal
Chaitin machine in section 9. The latter parses a first complete binary tree
as program, supplies the suffix as input, and substitutes a sequenced read
primitive R for remaining leaves. Incomplete syntax, underflow and overflow
are outside its halting domain. Appendix B's historical JavaScript is not
a verified portable implementation in Adva.

The inspected mountain/chaitin snapshot
`19f6928db83d36642da5c53691bdc59a8f6ca3b9` names Iota and Keraia in its README,
but Main.hs supplies a measured-tree/search scaffold, not a Keraia evaluator.

The new slot-count and recursive parsers agree on all 65535 binary strings
of length at most fifteen. The paper's example separates into program
`11101001010011000` (17 bits) and data `1`. A parser must preserve the suffix:
it cannot diagnose overflow before evaluation has had a chance to read it.

Underflow at a finite prefix is a **NeedInput search frontier**: extensions
may halt even when that exact input does not. Pruning the entire cylinder
would lose potential halting programs. A generic two-read protocol control
checks this and shows that interchanging labelled reads changes outputs on
fixed input `01`. This is not execution of Keraia's Interpret operator.
Possible symmetries of aggregate distributions still require a separate
probability and cost transport proof.

## Exact syntax mass and a second bottleneck

This calculation is derived from the tree grammar and independently checked;
it is not a Keraia halting calculation.

A full ordered binary tree with k internal nodes has \(2k+1\) bits and
\(C_k=\binom{2k}{k}/(k+1)\) possibilities. Thus

\[
P(L=2k+1)=C_k\,2^{-(2k+1)}.
\]

Start with one open slot. Bit 0 removes a slot; bit 1 adds one. Counting
uncompleted prefixes by slots yields an exact dynamic program. Completion
counts agree with an independent binomial Catalan formula at all depths
through 63 and exhaustive parsing through 15. It visits 1056 (depth, slots)
states through depth 63.

| Inspected bits | Mass with incomplete first program tree |
| ---: | ---: |
| 9 | 126 / 512 = 0.24609375 |
| 15 | 6435 / 32768 ≈ 0.196381 |
| 31 | 300540195 / 2147483648 ≈ 0.139950 |
| 63 | 916312070471295267 / 9223372036854775808 ≈ 0.099347 |

At depth \(2k+1\), residual mass is
\(\binom{2k+1}{k}/2^{2k+1}\), asymptotically \(1/\sqrt{\pi k}\);
the length tail has order \(N^{-1/2}\).
The grammar partitions fair-coin paths into completed tree cylinders and
unresolved prefixes. The DP counts that unresolved mass cheaply; it does not
decide which future descriptions and data halt.

This is a slow syntax tail before runtime and data consumption. It bounds
possible halting mass from descriptions longer than the cutoff, not the
whole residual: short descriptions can still need long data or computation.
It is not a lower bound on the actual contribution of long halting programs.

Equal slot counts preserve future syntax counts while forgetting application
structure. They cannot justify merging evaluator states.

## What Q4 would need to add

There is no Q4-specific optimization or native cell in this experiment.
Ordinary exact caching is the baseline a Q4 proposal must beat.

A prefix-Keraia state should expose control/closure, environment, continuation,
input cursor, output protocol, remaining semantic fuel and pending read.
The next bounded implementation should first check Interpret and
capture-avoiding substitution, fix lazy reduction and input sequencing,
and reproduce the paper's examples.

The useful candidate is sharing computation **between read boundaries**
when the full residual and cost can be transported. It is not unconditional
commutation of source bits or reads. A class C keeps mass
\(\sum_{p\in C}2^{-|p|}\); a time-bounded estimate also keeps each source's
cost. Preserving eventual halting alone does not preserve finite-time
acceptance.

Neither cache nor syntax DP supplies a computable general runtime tail.
They separate duplicate work from unresolved halting mass.

## Contracts, retained corrections and limits

Initial Zot pre-execution tree:
`9be0b6a5ef749abe141d24223222ec4871449957`.
Keraia boundary pre-execution tree:
`1b90a27e6786fea7e204ad4e776a496b88be3ba6`.
These identify immutable repository objects, not authentication or truth.

The initial Zot run consumed 665350 CEK transitions, 56317 oracle entries
and 555 ms through checkpoint. Caps: 8000000 transitions, 4000000 oracle
entries, 20 seconds, 100000 arena nodes, 4096 stack frames, 64 output items,
32768 cache entries and 2000000 retained ASCII bytes. These bound logical
structures; no OS RSS supervisor was available.

Keraia used 679554 counted operations in 121 ms, within 5000000 operations
and 10 seconds, completing 146 checks. No Keraia evaluator was run.

Retained corrections:

1. Two source/document assembly cells had template-delimiter syntax errors
   and were rejected before their bodies ran. They were corrected before use.
2. The first checkpoint test retained the arena count rather than its data.
   One separately declared regression retained the full arena and replayed
   the same family. The saved checkpoint then resumed with matching output,
   residual and total cost.
3. The outer regression wrapper compared JSON text across storage that
   reordered object keys. It produced a false negative despite identical
   deterministic data. The raw InvalidEvidence result remains in
   evidence-regression-raw.json. A separately budgeted structural comparator
   rechecked existing records, preserved array order, and passed changed-cost
   and swapped-row controls. It visited 21972 values in 9 ms, with no new
   search. The corrected verdict and its provenance are in evidence.json.

Rust remains the sole native authority. Closure IDs and DP coordinates are
external syntax, not SourceIds, occurrences or native sharing. No Q4 filler,
M6 coherence, geometry descendant, native Seal, universal Keraia evaluator,
or ACS/renormalization theorem is admitted. The Pascal obligation stays Open.

Integration refreshed onto main at 8a30d7d7d1c085651c200a9df63f06fd01d8912f after the Zhang finite-example work and catalog update landed. Their note, claims, tests and library pointer are preserved; the Zot/Keraia run inputs stay at their original pins.

## Real Node replay, 2026-09-14

The [Möbius integration review](../../experiments/mobius_transport_receipt/review-20260914/README.md)
executed the unchanged replay CLI with Node v24.19.0 under a separate finite
review contract. Both campaigns completed: all 38 Zot checks and 146
Keraia-boundary checks passed. All 1023 per-code ledgers, probability tables,
syntax counts and read controls match the retained V8 result. Raw output is
preserved in that review's `before/node.stdout`, with source hashes and the
invocation ledger. This closes the real-Node gap recorded above, while
QuickJS, full repository validation and the Keraia evaluator remain unrun or
unimplemented as stated. Authored by ChatGPT (OpenAI), submitted through
Mingli Yuan's account as authorized proxy; no human review is implied.
