# From a finite probability receipt to a finite decision

Status: external bounded experiment, 2026-09-17. Profile
`adva.research.finite-decision.v0`. No new native keyword is installed.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
account use is not his authorship, review or correctness guarantee. All added
code, prose and synthetic fixtures are original contributions under Unknown v0.3.
No third-party source, dataset or illustration is incorporated.

## Question and frozen boundary

Can the previous probability receiver support a decision while retaining the
question, action meanings, losses, costs, ties and undefined conditions?

The [contract](contract.json) was written before execution. It fixes exactly
two states, two observations and two actions, a rational prior, a stochastic
observation-given-state kernel, nonnegative state-by-action losses and a
nonnegative observation cost in the same named loss unit. Roles and ordered
carriers are part of the question, not inferred from an untyped matrix.

Input rational components are bounded by 64. An additional inherited boundary
requires the derived joint probabilities to fit the unchanged parent profile's
1024 component cap. For example, prior `(1/61,60/61)` and kernel rows
`(1/59,58/59)` are valid probabilities but produce a denominator 3599: this
profile returns `InvalidContext`, not a mathematical refutation. This limitation
was identified by source review before the first run and recorded in the contract.

## Arithmetic and interpretation

Let states be s, observations o, actions a, prior p(s), kernel K(o|s), loss
L(s,a), and observation cost c. All expressions below use exact rationals.

\[
 P(s,o)=p(s)K(o\mid s),\quad
 q(o)=\sum_s P(s,o),\quad
 p(s\mid o)=P(s,o)/q(o)\quad(q(o)>0).
\]

For positive-mass observations, compare both conditional expected losses and
retain **every** minimizer. At mass zero, posterior, risks and conditional
minimizers are all `null`; a policy's arbitrary action there has no contribution
to the ex ante risk, but this does not define a conditional distribution.

\[
 R_0=\min_a\sum_s p(s)L(s,a),\quad
 R_1=\sum_{o:q(o)>0}q(o)\min_a\sum_s p(s\mid o)L(s,a),
 \qquad V=R_0-R_1,\quad V_{\rm net}=V-c.
\]

Under the declared unchanged action set and loss, V is nonnegative: constant
policies are among the four possible observation-to-action policies, so an
observer can ignore information. This elementary argument applies to this
finite model; the code checks the inequality on the supplied instances.
It does not imply that an actual information acquisition has nonnegative net
benefit. The acquisition choice is `observe`, `skip`, or the complete tie set
`[skip,observe]` according to the sign of V_net.

Probabilities alone do not prescribe a loss. Neither density normalization,
group identity nor the previously measured quadratic density energy supplies
the missing loss or cost interpretation. Here the loss unit is only a bound
label; no physical dimension conversion or human preference identification is
implemented. CPU time and work units are separate from c.

## Executable receiving chain

`run.py` constructs each candidate. It uses the existing project probability
producer for a four-atom joint receipt, then independently enumerates all four
deterministic policies to compute R1. `receive.py` reconstructs the joint context
from its own expected decision question, calls the unchanged probability
receiver's context and witness checks, and uses weighted conditional minima to
check R1. Both implementations share Python and `Fraction`; this is not a
formally independent trusted kernel.

Joint atoms use fixed positional IDs `s0:o0`, `s0:o1`, `s1:o0`, `s1:o1`, avoiding
collisions from arbitrary user labels. The complete original labels remain in
the outer expected context. The parent reference is uniformly 1/4, and its
observable is the state index. Its scope is probability checking, not the
meaning of a loss. The receiver binds all outer context fields, including loss,
unit, action order, kernel direction and history, before accepting decision use.

The two receiving layers share one cumulative 10,000-unit budget. Each fresh
process has a 3-second deadline, 128 MiB address-space cap, 3 CPU-second cap and
bounded output. The fixed campaign admits at most 48 children and 30 seconds.
This is an external research protocol, not native general `communicate`,
`accept`, a `Seal`, or an import of semantic identities.

## Retained result

One campaign completed without an implementation correction or retry:

| Instance | Risk without / with observation | Gross value | Cost | Net value | Acquisition minimizers |
| --- | --- | --- | --- | --- | --- |
| Symmetric channel, low cost | 1/2 / 1/4 | 1/4 | 1/8 | 1/8 | observe |
| Same channel, high cost | 1/2 / 1/4 | 1/4 | 3/8 | -1/8 | skip |
| Same probabilities, changed loss | 1/2 / 1/2 | 0 | 0 | 0 | skip, observe |
| Asymmetric new instance | 1 / 5/6 | 1/6 | 1/12 | 1/12 | observe |
| Impossible second observation | 1/2 / 1/2 | 0 | 0 | 0 | skip, observe |

The symmetric prior is `(1/2,1/2)` and the channel rows are `(3/4,1/4)` and
`(1/4,3/4)`. Initial losses are `[[0,1],[1,0]]`. Changing them to
`[[0,3],[1,0]]` leaves all probabilities and posteriors unchanged yet makes
the second conditional choice a tie and the information's decision value zero.
The new asymmetric instance uses prior `(2/3,1/3)`, rows `(3/4,1/4)` and
`(1/2,1/2)`, and losses `[[0,2],[3,0]]`. Full inputs, policy tables and outputs
are retained, rather than just these summaries.

Results: **5 `AcceptedFiniteDecision`, 41 `InvalidEvidence`, 2 `InvalidContext`**,
with 187 supervisor assertions. Refusal controls include altered loss, action
roles, question, unit, direction and history; a wrong parent; wrong posteriors
and net values; an omitted tied action; a fabricated zero-event posterior;
Boolean rationals; and an unsupported native-free assertion. The two invalid
contexts are a non-stochastic kernel and the inherited joint-denominator bound.
All refusals preserve the receiver-selected expected context and an empty
semantic delta. Recomputed alternative-context receipts were not separately
accepted under their own alternative contexts in this campaign.

The witness is [evidence/manifest.json](evidence/manifest.json) and its
`attempt-1.tar.gz` archive. The manifest gives each member's bytes and digest;
`attempt-1/result.json` records the source hashes, all five contexts, policy
enumerations, claims, outcomes and measured costs.

## Actual cost

| Measurement | Result |
| --- | --- |
| Campaign through verification | 9.280764753 seconds |
| Construction, including controls and parent candidates | 0.019077201 seconds |
| Per-case input serialization | 0.115696325 seconds |
| Child receiving, including process startup and parent checks | 8.975457398 seconds |
| Summed receiver work units | 3,786 |
| Highest child process RSS | 11,776 KiB = 11.5 MiB |
| Supervisor peak RSS | 13,824 KiB = 13.5 MiB |
| Fresh receiver processes | 48 |

Other supervisor overhead accounts for the difference between phase totals and
campaign time. Reuse is included, not separately timed. Final report encoding
and writing, evidence archiving, research, coding and publication are excluded.
RSS is process memory, not archive size or summed concurrent memory. Work units
count parsed rationals, comparisons and selected finite terms, not instructions.
The four policies are explicit finite enumeration, not an open-ended search.
There is no measured acceleration claim and no new vocabulary formation cost.

## Replay and residual

From the repository root, with Python standard library on Linux:

```sh
timeout 35s python3 -B -S experiments/finite_decision/run.py --output /tmp/adva-finite-decision-new
tar -xzf experiments/finite_decision/evidence/attempt-1.tar.gz -C /tmp
python3 -B -S experiments/finite_decision/receive.py --expected /tmp/attempt-1/low-cost/valid/expected.json --candidate /tmp/attempt-1/low-cost/valid/candidate.json
```

Use a fresh output directory. The dedicated CI executes the same fixed campaign
and retains its own artifacts. Elapsed time and RSS vary on replay. A receiver
result is returned in JSON even on refusal; automation must inspect `outcome`.

This proves no native Adva probability syntax, automatic learning of an unknown
model, authentication, universal grammar, physical energy, M6 closure, `free`,
human preference correctness or practical benefit to Jiamin's actual task.
No action is executed in the world. It gives Mingli and subsequent agents a
replayable way to ask what loss and observation cost justify a proposed choice.

The next minimal obligation is a checked positive rescaling of both loss and
cost: all risk quantities should scale together and both minimizer sets should
remain unchanged. Scaling only the loss can change acquisition choice and must
be kept as a changed problem. This would connect decision language to the first
units-and-scales contract without starting continuous probability or optimization.
