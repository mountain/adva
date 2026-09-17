# Two finite loss-scale transports need an exact middle

Status: external bounded experiment, 2026-09-17. This continuation starts from
merged PR #188, main commit `ee0dd321a792a2b17eaf6b2d42634171396d4727`.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
account use is not his authorship, review or correctness guarantee. Original
code, prose and synthetic evidence under Unknown v0.3. No third-party source
text, code, datasets or figures are incorporated.

## Question and finite statement

The previous receiver checks one common positive scaling of loss and
observation cost. This receiver checks exactly two ordered applications, using
the unchanged scale, decision and probability checkers as dependencies.

For positive factors a and b, the final numerical effect is

\[
L_2=baL_0,\qquad c_2=ba c_0,
\qquad H_2=H_0+[h_1,h_2].
\]

The scalar product records the numerical effect. It does not identify the two
step requests, intermediate units or ordered history with a one-step request.
Each checked step preserves all action and acquisition minimizers, ties and
null events under its fixed context. Composition additionally needs the same
complete intermediate context and receipt on both sides of the handoff.

## Frozen receiver and resources

The [contract](contract.json) was frozen before execution. A trusted request
contains the source context and exactly two ordered specifications, each with
factor, target unit and history step. The receiver derives both expected step
requests and checks source, intermediate and final domain limits before reading
any proposed acceptance into the candidate.

The candidate supplies two scale receipts and a summary. Both receipts are
checked under their own declared requests first, with local success recorded
only as diagnostic information. The receiver then binds their requests to the
expected ordered requests, checks that the first target and second source are
the same complete context and receipt, and verifies the product and final
context including both history entries. Refusal preserves the entire expected
request and an empty semantic delta.

There is one cumulative 10,000-work-unit budget across all parent checks. Each
child has three seconds, 128 MiB address space and bounded output; the campaign
has at most 40 children and 30 seconds. The new outer envelope admits 64 KiB
because it carries two receipts. Each embedded scale receipt's canonical JSON
is separately bounded by the old 32 KiB limit. This explicit envelope profile
does not change the old checker or its wire contract.

Inherited finite bounds remain: each step factor has reduced numerator and
denominator at most 16; endpoint rational components at most 64; joint
probability components at most 1024; endpoint history length at most four.
Consequently a source must leave room for both appended records. Product
summary components may be as large as 256. They are **not** used to bypass the
single-step factor limit.

The summary's `WithinFactorBound` or `OutsideFactorBound` describes just that
factor limit. It grants neither direct one-step execution nor native authority.
Unit correspondence is still a declared premise; physical unit compatibility
and human loss preferences are not established by this arithmetic.

## Executed witnesses

One campaign, without correction or replay, passed six compositions:

| Context | Factors | Product | Retained boundary |
| --- | --- | --- | --- |
| Nonidentity low-cost decision | 3/2, 2 | 3 | Both history steps remain |
| Forward and inverse | 3/2, 2/3 | 1 | Original numbers and unit return; history differs |
| Asymmetric fresh reuse | 2/3, 3/2 | 1 | Unequal prior and observation probabilities retained |
| Conditional and acquisition ties | 1/2, 2 | 1 | Complete minimizer sets retained |
| Null event | 2, 1/2 | 1 | Zero-event posterior, risks and actions remain null |
| Beyond the single-step factor profile | 8, 4 | 32 | Both steps fit; direct factor does not |

Four controls per family change the intermediate unit, rewrite middle history,
change the product summary, or reverse the two supplied links. In the **six
unit controls**, both scale receipts pass their own checks and the final
complete context is unchanged: the second step overwrites the intermediate
unit label with the requested final unit. Nevertheless the intermediate request
is wrong, and composition is refused. Final agreement cannot establish a
faithful handoff.

There are **25 evidence refusals after both local step checks passed**: the
24 family controls plus a Boolean product summary. Other evidence controls
remove a link, add a native-free field or falsify parent arithmetic. These local
checks are not acceptance for the receiver's requested composition.

Three unsupported composition requests cover a zero factor, insufficient
history capacity, and an out-of-profile intermediate loss. The last uses a
source loss of 8 and factors 16 and 1/16: the numerical path is
`8 -> 128 -> 8`. Original and final numbers fit, but intermediate 128 exceeds
64. The receiver refuses during preflight; it does not execute through that
boundary merely because the final number would return.

A separate child actually invokes the **unchanged one-step scale receiver**
with factor 32. It returns `InvalidContext`, while the admitted two-step path
8 then 4 passes the new composition profile. This shows a concrete difference
between these finite interfaces, not a theorem of universal expressivity or a
speed advantage. Neither checker replenishes fuel or changes its own bounds.

Total: **6 `AcceptedScaleComposition`, 28 `InvalidEvidence`, 4 `InvalidContext`**,
38 fresh child processes, and 184 supervisor assertions. The fourth invalid
context is the direct one-step probe; the other 37 children use the new receiver.
Every refusal retains the selected request, grants no native authority and
adds no semantic fact.

## Evidence and measured cost

The [manifest](evidence/manifest.json) inventories all members of
`attempt-1.tar.gz`. Each case retains the expected request, full candidate,
stdout and stderr. The result also records exact summaries, claims, outcomes,
all checker/producer source hashes and measurements.

| Measurement | Result |
| --- | --- |
| Campaign through verification | 7.817339579 seconds |
| Candidate construction and mutation generation | 0.075652728 seconds |
| Per-case input serialization | 0.226460221 seconds |
| Child startup, receiving and all ancestor checks | 7.370785964 seconds |
| Counted receiver work units | 27,612 |
| Highest child RSS | 11,924 KiB, about 11.64 MiB |
| Supervisor peak RSS | 15,660 KiB, about 15.29 MiB |

The phase gap is other supervisor overhead. Reuse is included but not separately
timed. Final report encoding/writing, archival, research and publication are
excluded. RSS is measured process memory, not archive size. The underlying
producer enumerates four deterministic decision policies per endpoint; there
is no open-ended search or general speedup claim. Python/Fraction are shared
trusted dependencies, despite separate producer and receiver code/processes.

Replay from the repository root with Python standard library on Linux:

```sh
timeout 35s python3 -B -S experiments/decision_scale_composition/run.py --output /tmp/adva-scale-composition-new
tar -xzf experiments/decision_scale_composition/evidence/attempt-1.tar.gz -C /tmp
python3 -B -S experiments/decision_scale_composition/receive.py --expected /tmp/attempt-1/nonidentity/valid/expected.json --candidate /tmp/attempt-1/nonidentity/valid/candidate.json
```

Choose a fresh output directory. The JSON outcome, not process exit zero,
indicates acceptance or refusal. CI replays the fixed campaign and retains its
own artifacts; measured time and memory need not be identical.

## Contribution and next boundary

No new vocabulary is introduced. The concrete contribution is a checked
two-step use of the existing scale/decision/probability boundary. It helps
Mingli and later agents distinguish an equal result, locally valid steps, and
a correctly connected process. The evidence supports that distinction without
establishing native composition, `free`, M6 closure, universal grammar, actual
learning or usefulness for Jiamin's real decision task.

The next minimal task is to define a bounded continuation checkpoint when a
chain reaches its history capacity: retain the accepted prefix and exact
remaining obligation, and refuse any retry that erases history or silently
renews resources. The present receiver stops at its declared two-step boundary;
it does not already provide such continuation or an unbounded compressed history.
