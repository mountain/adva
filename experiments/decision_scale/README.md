# Common positive loss scale preserves a finite decision

Status: external bounded experiment, 2026-09-17. Profile
`adva.research.decision-scale.v0`. This continues the now-merged finite decision
work from PR #187 at `af399692cb953821cac21f8870764ea26761f789`.

Authored by ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy;
account use is not his authorship, review or correctness guarantee. Original
code, prose, fixtures and measurements are contributed under Unknown v0.3.
No external source text, code or data is incorporated.

## The mathematical condition

Fix the complete finite prior, observation kernel, action set and their roles.
For a **single positive** rational factor alpha, request

\[
L'(s,a)=\alpha L(s,a),\qquad c'=\alpha c,\qquad \alpha>0.
\]

Every conditional and prior expected loss then scales by alpha. Since positive
multiplication preserves order and equality, it preserves the entire argmin
set, including every tie. Thus

\[
R'_0=\alpha R_0,\quad R'_1=\alpha R_1,\quad
V'=\alpha V,\quad V'_{\rm net}=\alpha V_{\rm net}.
\]

All observation masses, posteriors and acquisition minimizers stay unchanged.
A zero-probability observation still has no defined conditional law, risk or
action set in this profile. The identities follow directly by distributing a
common factor through finite sums and minima; the experiment is a bounded
implementation check of this argument, not a formal proof-kernel artifact.

If the operation represents a change of unit for the *same* loss quantity,
then one new unit equals `1/alpha` old units. Merely changing a unit label does
not establish this correspondence. It is a declared premise, not a physical
measurement or an economic preference theorem. The profile handles linear
positive scaling only, without offsets or state-dependent factors.

## Frozen receiving boundary

The [contract](contract.json) was prepared before execution. It accepts a
receiver-selected request containing exactly `source`, `factor`, `target_unit`
and `step`. The source is the existing finite-decision context; the target is
derived by scaling every loss and the observation cost, changing the unit label,
and appending the step to history. All other fields remain fixed.

The factor has positive canonical numerator and denominator at most 16. Both
endpoints must fit the unchanged decision profile (rational components at most
64, history length at most four) and probability profile (joint components at
most 1024). Positive arithmetic may exceed these implementation bounds; that is
`InvalidContext` for this interface, not a counterexample to scale invariance.

The receiver performs five distinct checks:

1. Validate the complete expected request and derived target domain.
2. Bind the candidate request, then validate its source decision against the
   selected source, including the source's probability receipt.
3. Validate target decision arithmetic against its own supplied context,
   including its probability receipt. Record **self-consistency only**.
4. Check that the complete target context is exactly the requested target.
5. Check scaling of risks and values, unchanged probability claims, all tie
   sets and all null events. Only then return `AcceptedDecisionScale`.

The third check deliberately has less authority than transport acceptance.
Ten controls have two arithmetically valid endpoints yet fail the fourth check.
The output records `endpoint_arithmetic_checked` separately from acceptance.
Every refusal retains the expected request and has an empty semantic delta.

The cumulative work budget includes both decision receivers and both probability
receivers. The campaign cap is 40 children and 30 seconds; each child has three
seconds, 128 MiB address space, bounded wire/output bytes and 10,000 defined work
units. No checker source, dependency lock, native semantic identity, library
entry or older evidence is modified.

## Results and two useful counterexamples

Seven transports passed: low cost with factor 3/2, high cost with factor 2,
conditional tie with factor 1/2, asymmetric reuse with factor 2/3, null event
with factor 3/2, acquisition tie with factor 2, and the inverse low-cost change
with factor 2/3. All complete tie sets and null events were preserved.

For the low-cost example, the net value changes from 1/8 to 3/16 and the choice
remains `observe`. For the high-cost example, common scaling by two changes
net value from -1/8 to -1/4 and the choice remains `skip`.

| Declared source | Alteration actually supplied | Source / target net value | Source / target choice |
| --- | --- | --- | --- |
| High cost | Double loss, leave cost unchanged | -1/8 / 1/8 | skip / observe |
| Low cost | Quadruple cost, leave loss unchanged | 1/8 / -1/4 | observe / skip |

Both endpoint calculations are independently checked and valid for their own
questions. Both proposed transports are rejected: a partial rescaling changes
the question and can reverse the acquisition choice. Unchanged probabilities
alone do not protect a decision.

The forward-inverse case restores all numerical and unit fields. It retains
the original two history entries plus the two transport steps. Identity of the
final numbers does not cancel process history. The producer checks the exact
handoff between these two fixed cases; no general receipt-composition protocol
or native inverse is claimed.

The complete campaign returns **7 `AcceptedDecisionScale`, 27 `InvalidEvidence`,
6 `InvalidContext`**, with 193 supervisor assertions. The 27 evidence controls
cover erased history, a changed factor request, wrong risks, partial scaling,
changed action roles, a missing tie, an invented null posterior and an extra
native-free field. Six context controls cover zero, negative, Boolean and
noncanonical factors, target arithmetic overflow of the profile limit, and a
fifth history record. No correction or retry was needed.

## Actual cost and exact evidence

| Measurement | Result |
| --- | --- |
| Campaign through verification | 8.077904954 seconds |
| Candidate construction, including all control generation | 0.039730314 seconds |
| Input serialization | 0.162178887 seconds |
| Receiving, including startup and all ancestor checks | 7.694067609 seconds |
| Summed receiver work units | 9,298 |
| Highest child RSS | 11,776 KiB = 11.5 MiB |
| Supervisor RSS | 14,464 KiB = 14.125 MiB |
| Fresh receiver processes | 40 |

Reuse is included, not separately timed. Other supervisor overhead accounts
for the difference between the phase totals and campaign time. Final report
serialization/writing, archiving, research, authoring and publication are
excluded. RSS measures process memory, not file size. This is no speedup claim.
The existing producer enumerates four policies when constructing each endpoint;
there is no unbounded search or automatic fuel renewal.

[evidence/manifest.json](evidence/manifest.json) inventories every member of the
retained `attempt-1.tar.gz`, including exact expected requests, candidate
receipts, outputs, empty stderr files, source hashes and measurements. The
source and target implementations share Python/Fraction; receiving is separate
code and process, not an independently formalized arithmetic kernel.

Replay from the repository root using the Python standard library on Linux:

```sh
timeout 35s python3 -B -S experiments/decision_scale/run.py --output /tmp/adva-decision-scale-new
tar -xzf experiments/decision_scale/evidence/attempt-1.tar.gz -C /tmp
python3 -B -S experiments/decision_scale/receive.py --expected /tmp/attempt-1/high-cost/valid/expected.json --candidate /tmp/attempt-1/high-cost/valid/candidate.json
```

Use a fresh output directory. Inspect the JSON `outcome`, not merely process
exit zero. CI runs the same declared campaign and keeps its own evidence;
elapsed time and RSS are not replay invariants.

## Contribution and residual

No new vocabulary is needed. This gives a checked use of scale, loss, cost and
history: a representation change must transport *every quantity that enters the
comparison*. It helps Mingli and later agents detect a decision that changed
because only part of its numerical presentation was converted.

It does not establish human loss preferences, physical unit compatibility,
native Adva transport, `free`, M6 closure, universal grammar, persistent learning
or measured value for Jiamin's real task. Numerical scale invariance is compatible
with the broader intuition of stable interpretation across representations;
the necessary common scale and fixed decision contract are the actual reason
this instance works.

The next compact step is a bounded composition receipt: bind the exact
intermediate context and the ordered two-step history, then compare its numerical
effect with the product factor. A direct product factor must not erase the two
steps or authorize a mismatched intermediate unit contract.
