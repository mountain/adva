# Three-clock calibration and the boundary of a transported history

Status: bounded external research, 2026-09-17. Main was `c91f6ec` when this
contract was frozen. This continuation is based on draft PR #198 at
`1cdc2c1f99f6219d921374d1ae056fe7f4669910`; the preceding reversible-memory
campaign is preserved byte for byte. The new profile explicitly reuses its
producer and independent receiver, with source digests pinned. It is not a
native Adva operation or an executed library exchange.

Authored by ChatGPT (OpenAI), submitted through Mingli Yuan's authorized
account proxy. Account use does not make Mingli the author, reviewer or
guarantor. Original first-party code, exposition and synthetic evidence are
contributed under Unknown v0.3. No external paper text, page image, source
code or dataset is incorporated.

## Question and scope

Does an exactly consistent three-clock calibration preserve the complete
finite records needed by a history-conditioned dynamics judgment? Can that
transport succeed while the proposed effective Markov law still fails?

There are three ordered clocks A,B,C, three positive affine comparison maps,
and H+1 identified events, H=1..3. A's event times are strictly increasing
rationals. The event index is exactly the system-state index S_0,...,S_H
in the supplied reversible-bit context. The environment has one through
three bits. That joint probability law is supplied, not inferred from
observations or certified as a physical preparation.

All slopes and offsets have canonical rational encodings; positive slopes
preserve this finite event order. These scalar clock comparisons include no
space coordinates, signal protocol, proper-time measurement or spacetime
metric. They cannot establish relativistic synchronization, locality or
thermal equilibrium. The full frozen grammar and budgets are in
[contract.json](contract.json).

## Two independent calibration obligations

Let f_AB(t)=a_AB t+b_AB, with analogous maps on B->C and C->A. Compose in
that order, retaining the orientation:

    f_CA(f_BC(f_AB(t))) = R t + D
    R = a_CA a_BC a_AB
    D = a_CA (a_BC b_AB + b_BC) + b_CA.

The finite receiving labels are ClockConsistent for R=1,D=0;
RateConsistent for R=1,D!=0; and ClockInconsistent for R!=1. RateConsistent
means only that this affine loop returns the original rate scale. It is not
an assertion about an actual physical equilibrium. In particular it does not
erase the offset D.

If R=1,D=0, choose A's parameter as t, B's as f_AB(t), and C's as
f_BC(f_AB(t)). All three comparison maps then agree with those assignments.
Conversely a common parameter reproducing every edge implies loop identity.
This argument concerns the declared affine model, not arbitrary curved
spacetime or a physically supplied clock network.

Examples use edges represented as (slope,offset):

| Edges A->B, B->C, C->A | Loop | Meaning |
| --- | --- | --- |
| (2,1), (3,-2), (1/6,-1/6) | t | Full affine consistency |
| (2,1), (3,-2), (1/6,5/6) | t+1 | Rate agrees but offset survives |
| (2,1), (3,-2), (1/3,-1/3) | 2t | The event at zero is fixed; the map is not identity |

For separately changed charts g_i(t)=s_i t+o_i, s_i>0, each edge changes to
g_j composed with f_ij composed with g_i inverse. The loop at A is conjugated:

    R' = R,    D' = s_A D + (1-R)o_A.

Thus full consistency is chart invariant. If R=1, a nonzero D cannot be
removed by a positive change of A's scale. If R!=1, the offset alone is not
invariant. A fixed event is not a replacement for checking both coefficients.

## Why the dynamics result must travel separately

For each positive system history h ending before a requested transition,
let M(h) be its probability and F(h) the probability of that history followed
by a flip. A supplied homogeneous flip law q requires

    F(h) - q M(h) = 0

for every positive h. Zero-mass histories have no asserted conditional
probability. The prior receiving profile checks these quantities from the
complete finite initial law and ordered reversible gates.

Our elementary transport statement is: if event identities, all their state
records, the probability space and event order are preserved, an invertible
change of their time labels does not change which microstates realize h or a
flip extension. Therefore both M(h) and F(h), and hence their residual, are
unchanged. No fitted Markov assumption is needed to transport a counterexample.

That is why the new top-level VerifiedTransport can legitimately contain
dynamics_outcome=Counterexample. A consistent clock triangle cannot change
the outcome of the independent dynamics check. Reusing one fair environment
bit with a fair initial system gives S_2=S_0: one-time and adjacent-pair laws
agree with the fair flip kernel, while the history (0,0) has zero flip-extension
mass instead of 1/8. Complete calibration preserves this failure.

A new three-bit even-parity ensemble has all two-coordinate marginals
uniform. With S_0=0 and sequential bit use, its first two observed steps
agree with independent fair noise. At step three S_3=0; the history (0,0,0)
has mass 1/4 and flip-extension mass zero instead of 1/8. The constraint
excludes half the environment states. It is not a vanishing-measure
collision-set model or a hard-sphere simulation.

The kernel is indexed by the same identified events, not by a unit numeric
clock interval. Under t_B=a t_A+b, a fixed duration and its numerical endpoint
must also be transported. Reusing the same numerical timestamp or a fixed
continuous-time generator without its transformation is a different question.
Deleting earlier observations changes the conditioning information and is
not an invertible clock relabeling.

## Receiving and coverage

The caller binds the question, history, clock labels, three edges, complete
event list and complete micro-request. The receiver checks the loop by affine
matrices; the producer uses scalar composition. It checks exact ordered event
records, including the return reading, before invoking the source-pinned
reversible-memory receiver on the independently bound nested request.

A correct consecutive event prefix retains its missing event IDs as
UnknownCoverage. A missing initial event, reordered records, changed labels,
false clock coefficients or changed embedded question are evidence refusals.
Already verified clock/event components survive a later dynamics refusal;
independently checked counterexamples survive a later calibration or coverage
obstruction. A failed implementation does not create a physical counterexample.
The output records both levels; neither level grants native free or Close.

## Relation to Zhao and Deng-Hani-Ma

Zhao Zheng (赵峥), Pei Shouyong and Liu Liao, *Transitivity of clock rate
synchronization being equivalent to the zeroth law of thermodynamics*,
Acta Physica Sinica 48 (1999), 2004-2010,
https://doi.org/10.7498/aps.48.2004, give an argument conditioned on the
Planck-spectrum property of equilibrium radiation. The abstract explicitly
distinguishes clock-rate synchronization from the stronger construction of
simultaneity surfaces. The affine checks above preserve a related distinction
in a toy model; they do not reproduce that physical equivalence or supply its
radiation premise. The paper's full proof has not been audited in this round.

Yu Deng, Zaher Hani and Xiao Ma (马骁), *Long time derivation of the Boltzmann
equation from hard sphere dynamics*, arXiv:2408.07818v3,
https://arxiv.org/abs/2408.07818v3, extend the rarefied hard-sphere kinetic
derivation to long intervals on which the limiting solution exists. Their
cumulant method retains full collision histories and controls their size;
the cutting algorithm serves estimates rather than authorizing arbitrary
erasure of correlations. We use that as methodological guidance: a successful
change of description does not, by itself, justify a memoryless effective law.
Their singular limit, time-dependent estimates and collision geometry are
not obtained by this finite experiment. Microscopic inversion, clock
consistency and a justified effective law remain three separate obligations.

## Reproduction and remaining obligations

Run from the repository root:

```sh
python3 -B -S experiments/clock_history/run.py --output /tmp/adva-clock-history-new
```

The campaign has at most 32 receiver calls, 100000 counted work units and
30 seconds, whichever limit comes first. Each child has a 3-second and
128-MiB address-space limit. These are finite computation bounds, not a
quantification over arbitrary physical histories. No search is performed.

The first campaign passes 536 assertions in 32 fresh receiving processes:
five VerifiedTransport, two CalibrationObstruction, two UnknownCoverage,
16 InvalidEvidence and seven InvalidContext. Two complete transports retain
Counterexample as their dynamics outcome (repeated bit and three-bit parity).
Both nonidentity clock loops also retain the independently checked parity
counterexample. A missing terminal event retains that counterexample;
a missing final micro row retains a source UnknownCoverage. A false final
micro claim retains all three verified source rows and the counterexample.

The source distribution, event times, clock labels and rational noise rate
are changed in the positive-chart reuse instance. Additional exact controls
check loop conjugation, positive-order preservation and all three two-bit
projections of the parity ensemble. These controls do not establish that
actual observers can prepare or observe that complete ensemble.

| Measured component | Cost |
| --- | --- |
| Whole campaign before final summary serialization | 6.870948309 s |
| Context and candidate construction | 0.016152116 s |
| Receiving subprocesses | 6.419092879 s |
| Timed serialization before the final summary | 0.091500046 s |
| Exact algebra/distribution controls | 0.001981608 s |
| New-instance construction, subset of construction | 0.001727876 s |
| New-instance receiving, subset of receiving | 0.234912079 s |
| Counted receiver / clock producer-control / imported producer work | 4522 / 174 / 1040 |
| Total counted work | 5736 |
| Highest child RSS / supervisor RSS | 12032 / 15104 KiB |
| Verified archive packaging and inventory | 0.072014716 s |

The phase rows are not an exhaustive partition of wall time; repeated budget
inventory checks, process setup, mutation construction and supervision are
included in the whole campaign. RSS is a per-process high-water measure,
not simultaneous aggregate memory. Research, source reading, code authoring,
review and network publication time were not separately measured. Final
summary serialization is outside the recorded campaign phase snapshot.
No search, failed campaign or corrective replay occurred. Static preflight
and another ChatGPT agent's review preceded execution; no code was changed
after the successful campaign.

[evidence/execution.json](evidence/execution.json) records every case and
source digest. [evidence/manifest.json](evidence/manifest.json) inventories all
163 files in the original archive, including exact inputs, outputs and
commands. Each member was extracted and hash-checked. Stored success flags
do not replace replaying the receiving checks.

No vocabulary word is promoted. The next narrow question is an approximate
version that keeps calibration error and conditional-dynamics error separate,
with an explicit finite horizon and transported observation window. Relating
the clock comparison to a physically specified thermal equilibrium is another
obligation. Neither thermodynamic singularity exclusion nor Wick continuation
is tested. Practical value for Jiamin's task and a speedup remain unmeasured.
