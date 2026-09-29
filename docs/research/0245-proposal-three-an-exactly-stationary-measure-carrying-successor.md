# 0245 — Proposal three: an exactly stationary measure-carrying successor

**Date:** 2026-09-29. **Status:** external exact finite calibration, proposal only.
**Contract/checker/evidence:** `experiments/space_proposal_v3_transfer_v1/`.
**Paired test:** `tests/python/test_space_proposal_v3_transfer.py`.

This implements section 5 of
[`mountain/adva`, Research 0244](0244-proposal-three-the-pyritohedral-constellation-the-entry-window-and-a-transport-defect-disclosed.md)
at commit `e617f65ef5129d1888d892e77cabdfd6e5de7786`. The contract pins fourteen
source files by SHA-256. The old checker, contract, evidence, tests and note
remain byte-for-byte unchanged. This is a separately named successor, not a
repair of the historical payload or a promotion of its old claims.

中文摘要：保留原来的二十个顶点、三十条边、8+12 轨道、十对对径、手性备选、
进窗条件与能级表，只替换输运机制。新转移逐步双随机，实际携带的均匀测度
逐步精确平稳，顶点质量散度为零。不变排程的总环流为零；两组破缺排程在
梯度反号时分别给出 ±1/10、±3/80，精确相消。这里非零的是**有向环流**，
不是有限顶点坐标的净位移：任何单值端点差在平稳测度下的平均值都为零。
旧权重、旧残差与失败的 placement 对照都保留在原处。

## 1. Fixed boundary and the additional declaration

The parent is replayed and its **entire payload** compared with its frozen
evidence. Its S1, S2, S5, S6, S7, S8 and S9 section digests are retained as the
unchanged boundary: constellation orbits, antipodal pairing, chiral alternative,
two-region addressing, W1–W4, level/task assignment, stage one and the old
overreach controls. The three four-step schedules and gradients `{-1,0,1}` are
also unchanged. No graph edge is added, removed or redirected out of its old
component. Every old edge retains positive transition probability both ways.

There is one new modelling declaration: the oriented square

\[
(-1,-1,-1)\to(-1,-1,1)\to(-1,1,1)\to(-1,1,-1)\to(-1,-1,-1)
\]

and the **oppositely oriented antipodal square** carry the bias. Both lie in the
existing eight-vertex cube orbit. The twelve-vertex orbit keeps its symmetric
transfer. This declared orientation is not derived from the placement field,
nor does it replace the constellation's point group or assert physical chirality.

## 2. Transfer and measure

Use the row convention: `P[i][j]` moves mass from `i` to `j`, and
\(\mu_{s+1}=\mu_sP_s\). Let \(A\) be the unchanged 3-regular adjacency matrix,
\(R\) the existing antipodal permutation, and \(K\) the skew current with `+1`
on the declared square's forward edges and `−1` on its reverse edges. Set

\[
B=\tfrac14(I+A),\qquad C=K-RKR,\qquad
P_s(g)=B+\frac{a_sg}{16}C,\qquad u_i=\frac1{20}.
\]

Each closed square contributes one incoming and one outgoing current at each
of its vertices. Consequently

\[
C^{\mathsf T}=-C,\quad C\mathbf1=0,\quad
\mathbf1^{\mathsf T}C=0,\quad RCR=-C.
\]

The two squares are disjoint and \(C\) has sixteen nonzero ordered entries,
each of magnitude one. Since \(|a_s|\le1/2\), supported off-diagonal rates
are between \(7/32\) and \(9/32\); the diagonal remains \(1/4\).
Both marginals of \(P_s\) are exactly one. Thus every step is doubly stochastic,
\(uP_s=u\), and vertex mass divergence is exactly zero. The checker actually
propagates the state, retains all five states for each four-step case, and
does not reset or renormalize it. Tests also propagate a nonuniform point mass
to detect a hidden reset or transpose.

The observation is the fixed skew edge observable \(D=C\):

\[
J_s=\sum_{i,j}\mu_s(i)P_s(i,j)C_{ij}.
\]

With \(\mu_s=u\), symmetry of \(B\) cancels its contribution and
\(\sum_{i,j}C_{ij}^2=16\), giving

\[
J_s=\frac{a_sg}{20},\qquad
\mathcal T(g)=\frac{g}{20}\sum_{s=0}^3a_s.
\]

This is a measure-weighted current on transitions. The independent receiving
test recomputes it as
\(\sum_{i<j}[\mu_iP_{ij}-\mu_jP_{ji}]C_{ij}\), not as the old weight sum.

## 3. Zero and exact reversal

For the invariant schedule, \(a_{s+2}=-a_s\). Since \(RBR=B\) and \(RCR=-C\),
the **full transition field**, not only its summed flow, obeys

\[
P_{s+2}(Ri,Rj)=P_s(i,j).
\]

The measure is antipodal-even and the observable antipodal-odd, hence
\(J_{s+2}=-J_s\) and \(\mathcal T=0\). Every one of the matrix entries is
checked against this identity. Double stochasticity alone does not imply the
schedule symmetry or zero circulation; the broken schedule is a negative control.

For every admitted amplitude, reversing the gradient gives
\(P_s(-g)=P_s(g)^{\mathsf T}=RP_s(g)R\). The measure stays the same and the
observable is skew, so \(J_s(-g)=-J_s(g)\) and
\(\mathcal T(-g)=-\mathcal T(g)\) exactly.

| Schedule | Per-step current at `g=+1` | Total at `+1` | Total at `−1` |
|---|---|---:|---:|
| Invariant `(1/2,−1/2,−1/2,1/2)` | `1/40,−1/40,−1/40,1/40` | 0 | 0 |
| Broken uniform `(1/2,1/2,1/2,1/2)` | `1/40,1/40,1/40,1/40` | 1/10 | −1/10 |
| Broken shifted `(1/2,1/4,−1/4,1/4)` | `1/40,1/80,−1/80,1/80` | 3/80 | −3/80 |

All three schedules at `g=0` reduce to \(B\) and have zero current.
The old values `∓15/2` are not expected to survive a change of transfer,
measure normalization and observable; they remain frozen in Research 0244.

## 4. Independent reference and falsification

The independent reference is
[`mountain/adva`, Research 0242](0242-a-spatiotemporal-ratchet-net-transport-needs-both-asymmetries.md),
with `experiments/spatiotemporal_ratchet_v1/{contract.json,calibration.py,evidence.json}`
pinned at the same base commit above. Its original paired test is run unchanged.
The successor re-executes R1–R4 at all three gradient signs using that checker's
own periodic-measure solver and transfer. R1–R3 remain zero; R4 at `+1` remains

\[
-\frac{2395373021828541}{130893752065903472383},
\]

with exact opposite at `−1`. This reference validates measure-carrying reasoning;
it is not a numerical oracle for the twenty-vertex model. In particular, 0242's
R4 periodic measure is **nonuniform**. Its column-stochastic convention is
explicitly transposed at the comparison boundary. Offered to the successor as
a uniform-stationary candidate, its first step is rejected with drift `±1/96`.

Eleven executed negative controls have accepted companions:

| Candidate or claim | Exact reason for refusal |
|---|---|
| One unbalanced edge added, compensated on its source diagonal | Rows sum to one, but column residuals are `±1/64` and uniform drift is `±1/1280` |
| Transpose of that candidate | Uniform measure is fixed, but rows fail by `±1/64`; it cannot transport arbitrary source mass conservatively |
| A signed matrix with both marginals one | Negative diagonal entries `−1/4` are not probabilities |
| Frozen weights added to the symmetric base | Neither stochastic marginal is correct |
| The same frozen-weight candidate with its diagonal normalized | Nonnegative and row-stochastic, but uniform drift reaches `3/160` |
| 0242 R4 asserted uniform-stationary | Uniform drift `±1/96`; its proper periodic-measure calculation remains valid |
| Double stochasticity alone asserted to imply invariant zero | Broken uniform case is doubly stochastic and carries `1/10` |
| Gradient sign asserted irrelevant | Broken uniform totals differ: `±1/10` |
| Nonzero endpoint displacement asserted | All twenty indicator-gradient observables give zero |
| Amplitude `3/4` | Exceeds the unchanged `1/2` declaration |
| Gradient `2` | Outside the declared three values |

The generic gate is also exercised on test-side matrices, including malformed
and floating-point input; the tests do not merely trust retained rejection flags.

## 5. Residual and interpretation

The numerical defects of the **new** transfer are discharged: row residual,
column residual, actual uniform drift and mass divergence are identically zero
at every step. The following residuals remain:

- **Circulation, not coordinate displacement.** For any single-valued vertex
  function \(f\), stationarity forces
  \(\sum_{ij}u_iP_{ij}(f(j)-f(i))=(uP-u)f=0\). This also means zero net mass
  crossing any cut, including the sunward/anti-sunward cut. The nonzero observable
  above is not an endpoint gradient: its integral around the square is four.
  It counts signed path circulation, analogous to 0242's unwrapped ring current.
  No nonzero Euclidean displacement or material transfer is established.
- **Declared orientation and placement residual.** The cycle is an additional
  choice. The old failed placement-discrimination control is not repaired, nor
  is its purported alternative silently changed. The full old edge-sum pairing
  count of 24 is not promoted to a transfer-field symmetry-group result; only
  the explicitly checked antipodal/half-period identity is used here.
- **Disconnected graph and nonuniqueness.** The unchanged graph has components
  of sizes `8,4,4,4`. Uniform stationarity is exact but not unique: component
  masses can vary. The successor does not assert global mixing or convergence
  to uniform from every initial state.
- **A correction to the old prose, without rewriting it.** Direct evaluation
  finds endpoint-even weights on **18 of 30** old undirected edges, not all
  thirty. The blanket “exact-even” description in 0244 is too broad. Its actual
  divergence defect and frozen numbers remain as recorded; the successor's
  admission rests on both exact stochastic marginals, never on that phrase.
- **Scope.** One finite declared model, no observational data or physical
  magnitude, no physical effect, authorization, decision or deployment.
  Governance and general termination remain `Unaddressed`. Native admission
  is `NotGranted`; native execution and native transport are `NotRun`. No
  Rust semantics, stable API, catalog, dependency lock or native `Seal` changes.

## 6. Reproduction and contribution

```sh
python experiments/space_proposal_v3_transfer_v1/calibration.py --output /tmp/new-transfer.json
pytest -q tests/python/test_space_proposal_v3_transfer.py tests/python/test_space_proposal_v3.py tests/python/test_spatiotemporal_ratchet.py tests/python/test_geometry_foundation.py
```

Executed on Python 3.12.14: **71 tests passed**, covering the successor, the
unchanged 0244 and 0242 tests, and the shared geometry tests. Fresh and relocated
replays equal the retained evidence byte-for-byte; overwrite and changed-parent
refusals pass. The retained successor evidence SHA-256 is
`125e78cbf6a9aa5af222cee3432977ec4bc31c2f7d81b3c0a8070f40609797a2`.
The full repository suite and Rust suite were not run for this additive external
experiment; no native code or dependency lock changed.

The checker refuses an existing output path. Its contract fixes a 60-second wall
limit, 30-second CPU limit, 1 MiB output limit, twenty vertices, four steps, nine
schedule/gradient cases and no child processes, automatic retries or search.
Resource exhaustion is not a pass. Evidence is deterministic, exact rational,
host-path independent, with the checker and contract hashes retained.

Authored, implemented and checked by **ChatGPT (OpenAI)**, through Mingli Yuan's
GitHub account as an authorized submission proxy. Project-original contribution
under Unknown v0.3; no third-party content imported. Mingli supplied the repair
direction. Account use is not his authorship, independent review, endorsement or
correctness guarantee. There was no independent reviewer; independent here means
separate reference implementation and test-side recomputation.
