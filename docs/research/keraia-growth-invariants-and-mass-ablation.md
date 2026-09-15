# Keraia growth invariants and same-cut mass ablation

Status: executed bounded external calibration and a conditional stack-locality
argument, 2026-09-15. Base: `75fa3a9d3aa0ac762d5c28f3aecbf1fd86c96e88`.

Direction: Mingli Yuan. Implementation, argument and review: ChatGPT (OpenAI),
submitted through his account as authorized proxy; not his authorship, review,
endorsement or guarantee. Both implementations were reviewed by the same
assistant. Different kernels are a cross-check, not independent human review.

## Question and inherited boundary

The previous [cycle experiment](keraia-cycle-certificates-and-halting-mass-bounds.md)
left growing states unresolved because no complete execution frame recurred.
Can a finite received invariant exclude some such suffix cylinders, and how much
uncertainty does it remove when depth, fuel and accepted-code weights stay fixed?

This retains `keraia.appendix-b.cbn-whnf.read.v0`, its step convention and both
existing compilers. Evaluation does not descend under a returned lambda.
Uncapped reduction is the semantic object of the divergence argument; finite
execution/discovery still stops at its explicit resource limits. No historical
JavaScript is executed and optimal prefix universality is not transferred.

Contract and implementation: `experiments/keraia_growth_mass/`. Original sources
were frozen before one fixture preflight, one primary campaign and one fresh
process. All three passed; there was no failed or corrected research campaign.

## The invariant and why its finite check suffices

Write a frame as `(C, B, cursor, profile, cost)`, with the stack **bottom-first**.
The candidate supplies a trace from a receiver-reconstructed initial frame,
plus a segment from frame j to frame k. The receiver requires:

1. Positive segment length and no read or return inside it.
2. The same closed control term and input cursor at j and k.
3. The final stack is `B ++ W`, where B is the stack at j and W is nonempty.
4. Every intermediate stack preserves B as its bottom prefix. No beta step
   pops when the stack height equals the height of B, even if a later step
   would reconstruct identical bottom bytes.
5. All supplied source bits have been consumed. Receiver-selected source,
   original search fuel, profile and cost convention agree exactly; integer
   fields cannot be replaced by Boolean or floating-point values.

The receiver compiles the source with the string-marking compiler and checks
**every** edge using named capture-avoiding substitution. It does not use the
proposer's beta or stepping functions. Decoding a receipt is not acceptance.

**Conditional proof.** On the segment, write every stack as `B ++ T_i`.
Application pushes its fixed argument onto T_i. Beta consumes only a top item
of T_i, because condition 4 prohibits consuming B. These transitions depend on
C_i and T_i, not on B. By induction on the finite segment, replacing B by any
other stack D gives exactly the same control/cursor trace and replaces the
endpoint stack by `D ++ W`. No read/return boundary is crossed.

Take successively `D = B`, `B ++ W`, `B ++ W ++ W`, and so on. At every period
boundary the control is the same and another nonempty W has been appended.
Thus the underlying reduction cannot return and its stack is unbounded. Each
period retains its original positive semantic cost. A finite memory/fuel limit
still interrupts an actual run; that interruption is not the proof.

The finite stem can include reads, but their bits are already fixed in the
supplied prefix. Appending any suffix therefore preserves the stem and the
read-free pumping segment. The entire source cylinder is nonhalting, with
measure `2^(-source length)` under fair input bits.

For `A = lambda x. (x x) x`, the 19-bit source `1110011000110011000` represents
`A A`. Three internal steps take `(A A, B)` to `(A A, B ++ [A])`. Full-state
recurrence fails; the protected-stack invariant succeeds. This is a sufficient
stack-locality argument, not a general termination decision procedure or a new
native Q4 cell.

## Same-cut comparison

Both arms receive the **same** unchanged demanded-prefix traversal, at fuel
128. One arm admits only exact-cycle certificates; the other additionally
admits received growth certificates. Every accepted code is checked by the
named oracle for status, consumed position, ordered reads and weak-head value.
The terminal codes are checked as a disjoint exact Kraft partition.

| Depth | Accepted mass, both arms | Cycle-only nonhalting | Additional growth exclusion | Unresolved after growth |
|---:|---|---|---|---|
| 15 | 13039/16384 | 1/32768 | **0** | 6689/32768 |
| 19 | 428713/524288 | 37/524288 | **19/524288** | 95519/524288 |

Depth 15 reproduces the earlier partition exactly. Its extra exclusion is
zero; extending the search depth is not itself credited to the invariant.

At depth 19 the exact-cycle arm has unresolved mass `95538/524288`; the growth
arm has `95519/524288`. The invariant therefore removes exactly `19/524288`,
about **0.003624 percentage points**: uncertainty moves from **18.222427%** to
**18.218803%**. The added mass is 13 cylinders: two of length 17 and eleven of
length 19. Their individual sources and complete certificates are retained.

The resulting bound for this declared profile is:

\[
\frac{428713}{524288} \le H_{\mathrm{profile}}
\le \frac{65529}{65536}.
\]

Before adding growth certificates, the upper bound at that same cut was
`524251/524288`. The accepted lower bound does not change between the two arms.

There are 26 runtime-fuel frontiers at depth 19. Exact cycles certify 13 and
growth certifies the remaining 13. The remaining 95,519 terminal cylinders are
3,141 pending-input cylinders and 92,378 incomplete-syntax cylinders, all at
length 19. About **96.71%** of the remaining mass is incomplete syntax. No
runtime-fuel frontier remains in this finite cut, but that does not imply that
all divergent programs, or even all deeper fuel frontiers, can be certified.

## Boundary controls and receiving-only review

The fixtures include a protected reader argument below the pump, delayed
growth, a demanded read selecting growth or identity, and both discarded and
lambda-hidden growth. The last two halt under this weak-head profile.

A 33-bit selector has exact *conditional* halting mass one half after its
program is fixed. Its growth branch contributes global mass `2^-34`, not one
half; this fixture is outside the depth-19 ledger and is not added to it.

Fifteen receipt/context controls are refused. One is an actual four-edge
execution of A A whose selected segment has repeated control and a growing
endpoint stack but consumes and then rebuilds the alleged protected bottom.
This shows the endpoint-only criterion is insufficient as a certificate rule.
Seven finite suffix-extension controls retain the original 128 spent steps,
unchanged cursor and no input reads.

The later receiving-only regression disables the proposer, primary pure-step,
primary beta and candidate microstep functions. All 17 saved growth certificates
(13 search results and four fixtures) still verify. It additionally refuses a
Boolean false in place of the valid zero entry, floating-point 128 in place of
integer fuel, and the actual bottom-consuming trace. This review has its own
2-million-work/10-second bound and launches no new search.

## Cost, reproduction and limits

Each full process passed **132,141 assertions**, using **5,305,156** counted
host-work units. The preflight used 32,504 units; the three-child total was
**10,642,816**, below the declared 162-million aggregate allowance. Primary and
fresh child wall times were about 4.58 and 4.63 seconds; primary peak RSS was
101,036 KiB. Host time/RSS are excluded from deterministic comparison, while
work counts, ordered ledgers, certificates and all mathematical outputs agree.

The traversal visits 14,395 nodes at depth 15 and 202,005 at depth 19. This is
not a new direct enumeration of all overlapping bit strings, and certification
is applied after frontier collection. No online-pruning speedup is measured.
Costs cover the declared executions/checks, not authoring, CI or network work.

Read the retained run under `experiments/keraia_growth_mass/evidence/attempt-1`.
For an explicitly budgeted reproduction into a **new** directory:

```sh
timeout 140s prlimit --as=536870912 --cpu=130 -- \
  python -B -S experiments/keraia_growth_mass/supervise.py \
  --output-dir /tmp/keraia-growth-new-run
```

This provides no general halting tail bound, optimal-machine Omega value,
convergence-rate theorem, native certificate, library admission or Seal. The
independent receiving code checks finite premises of the stated conditional
argument; the general induction is not formalized in the Rust kernel.

The acceleration intuition gains a concrete but small extension: a received
invariant can exclude whole input cylinders even when exact states never
repeat. In this cut, the next bottleneck is the incomplete syntax frontier;
repeating the same runtime-cycle search cannot resolve it. Any further work
needs a new finite contract addressing that frontier or a broader invariant.
