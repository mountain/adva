# 0239 — The rounded ending: a conjunction that nets nothing, and a one-way commitment that sealing may not touch

**Date**: 2026-09-25 · **Contract**: `experiments/three_cycle_supplement_v2/contract.json`
(sha256 `823eedfaa492d0524c901793b580d5f02b67d7cf739f26781e326aa667d1e990`) ·
**Checker**: `calibration.py` (sha256 `8d7a7f05...0aa6c578`) · **Evidence**: `evidence.json`
(sha256 `6fb838efba636c62bd956349c7fe8c941841238147d92cfbefd7e721cc5e48c9`) ·
**Paired test**: `tests/python/test_three_cycle_supplement_v2.py`

**Status**: one bounded external exact calibration in Python with declared `sympy` used
only for rational-interval real-root isolation and one specialised discriminant. It
inherits the frozen parent chain, supplement one and the surgery contract byte for
byte and edits none of them. No native certificate, no stable API, no Seal, no
admission, no transport, no terminology home, no physical claim, no forecast, no
skill claim, **no magnitude for any physical quantity**, and no data read or used.

中文摘要：收尾改成**圆融**——两条终止条件**合取且各自全量**：可封分量在返回不动点精确闭合
（残差 `0` 于 $\mathbb{Q}(w)$，$w$ 为 $h^3+8h^2+64h-320$ 的唯一实根），承诺分量**越出链尾、写出
而不消解**（四个声明位置携带、`discharged: false`、量级 `none_declared`）。四条禁令各带
**必须失败**的对照：二选一、净额化、妨碍判定、折中（容差 0）。易的既濟／未濟降为对照族
（对角 81 点＝当位、补集 6,480 点、全不当位 1,296 点）。起头二分：可重置
（错位 5 日＋步余数 $2/9$＝486 赞）与**不可重置承诺**（重置必须被拒）。中间 5 点双循环
（生 $+1$、克 $+2$，5 素故皆为生成元；模 4 的合数对照被拒）。天文余数：链长 1095 日，
对 260／2920／18980 余 55／1095／1095，**一条都不闭合**。单向储库：阈值 **1** 开、**1/4** 关，
增量 1/8 与 1/16，回路不回到初态，**滞后**在控制量 1/2 处两支不同；**父链的一阶弛豫储库在
单调性与滞后检验上失败**。**封热对不可封源被拒**（承诺项只记账、不可封，且不得抵消违规）。
4×2 分类表每格**三选一**（待纠正 1 格／必须保留结构 2 格／显式不可量化 5 格），
**全表不给量级**。误差侧第四项 `committed-but-unquantified` 每缝分记、不融合。

## 1. The rounded ending and its four prohibitions

The two terminal conditions are a conjunction and **both hold in full**: the sealable
residual is exactly `("0","0","0")` as an element of `Q(w)`, where `w` is the unique
real root of `h^3+8h^2+64h-320` (derivative discriminant `-512`; value `-29` at 3 and
`128` at 4), and the identity `512(E(h)-h) = h(h^3+8h^2+64h-320)` is checked at `w` and
at `w+1/4`, the displaced state carrying the residual
`62497/131072 - 487/8192·w - 13/4096·w²` and **not** closing. The committed component
is `CarriedOutAndWrittenOut` at four declared positions with `discharged: false` and
magnitude `none_declared`. The two residual records have **different types**, so
netting is impossible rather than merely forbidden.

Four prohibitions are each rejected by an executed control: an either-or terminal; a
netting terminal (fused 0 against the separate 1/4 and 1/4); an obstructing terminal
where satisfying one condition flips the other's verdict; and both compromise
terminals (residual equal to a non-zero tolerance, and a non-zero tolerance with zero
residual) against the exact terminal with tolerance 0. The Yi pair is demoted to the
contrast family: forced-closed, forced-open and either-or readings on the address
carrier (diagonal 81 points, complement 6,480, every coordinate out of position 1,296,
some in position 5,184) are all rejected.

## 2. Beginning, middle, and the astronomical remainders

The beginning is split. **Resetable**: the phase misalignment of 5 days (365 = 18·20+5,
the Wayeb position) and the step-carry remainder `2/9` (6 of 27 steps, 486 zan at 81
zan per step); both reset to zero. **Non-resetable**: the one-way commitment state,
whose reset is **rejected** and whose state is left unchanged, together with the
misdeclaration-by-class and no-write-out controls.

The middle carries a five-point structure with two directed cycles on the same five
points: generation `[0,1,2,3,4]` and overcoming `[0,2,4,1,3]`, both of order 5, both
generators because five is prime, differing at all five points, with overcoming equal
to generation applied twice. Rejecting one cycle, identifying the two, the zero step
and a composite-modulus primality reading are each rejected.

The chain is `3 × 365 = 1095` integer days. The remainders are **55** against 260,
**1095** against 2920 and **1095** against 18980; the chain **closes none** of them,
with `2920 = 8·365`, `18980 = 52·365 = 73·260` and `365 = 18·20+5` recorded beside it.
A third-degree harmonic is 7 functions and all harmonics to degree 3 number 16, neither
equal to three, and the index map is injective with no collisions, so the "three is not
a degree" reading is asserted and both identifying readings are rejected, the numerical
coincidence `5 = 2·2+1` being recorded and **not** used.

## 3. The one-way reservoir, and what sealing may not do

Thresholds open at 1 and close at 1/4, with increments 1/8 open and 1/16 closed. On the
declared control loop `0, 1/2, 1, 1/2, 0` the branch reads `closed, closed, open, open,
closed`, the increments `1/16, 1/16, 1/8, 1/8, 1/16`, and the states `1/16, 1/8, 1/4,
3/8, 7/16`: non-decreasing, strictly increasing, and **the loop does not restore the
state**. The hysteresis is exact at control `1/2` — the thaw path is closed and the
refreeze path open, with increments 1/16 against 1/8 — and **the parent chain's
declared first-order relaxation fails both the monotonicity and the hysteresis
controls**, which is the evidence that the one-way shape is doing work.

Sealing is **refused** for the committed component: it is accounted and never sealed,
and a declared layer-wise violation (mixed +1/64, thermocline 0, deep −1/64, total 0) is
reported as a violation **not cancelled by the total**.

## 4. The four-by-two classification, without magnitudes

Eight cells, each carrying exactly one declaration: aerosols north
`structure_to_be_preserved` and south `explicitly_unquantified`; low cloud south
`structure_to_be_preserved` and north `explicitly_unquantified`; water vapour south
`correction_to_be_made` (the correction declared as a path, with no amount) and north
`explicitly_unquantified`; wildfire north and south both `explicitly_unquantified`, as a
ratchet rather than a reversible quantity. The accounts are one correction, two
structures and five unquantified. **Every cell is `magnitude = none_declared`**, no
numeric leaf sits under the cell or committed-component records, and no payload key
names a value, amount, rate, flux, forcing, sign or timing. Four controls are executed:
a structure cell treated as a correctable perturbation, a ratchet cell treated as
reversible, a symmetric north-south treatment, and any fusion of the correction account
with the structure account are each rejected.

## 5. Controls, the ones that failed, and what is not decided

Fifteen control groups discriminated. **Two controls failed to discriminate and are
retained**: the declared year-length control of the astronomical remainders, because the
same verdict holds for 365, 360 and 364-day years (55/1095/1095 against 40/1080/1080
and 52/1092/1092), so it cannot separate the declarations; and the monotonicity control
of the one-way reservoir, because with both increments set equal the state is still
non-decreasing, so only the hysteresis control tests the threshold branch. Three further
failures are **carried forward by citation and not repaired**: note 0238's
drift/iterability control and note 0237's radial-normal flux control and its
arrival-step-count-under-chirality control.

Five items are recorded as `Undecided` with their reasons and retained data: whether
"none in position" names the complement of the diagonal (6,480) or the points with every
coordinate out of position (1,296, the other 5,184 being in some coordinates), both
exact counts retained and neither substituted; which side is the sealing side, since the
contract names only the north side as the cold-injecting side and the south-side
correspondence used in the wildfire note is declared and used for nothing else; whether
the four-by-two placements are canonical, every unplaced cell being
`explicitly_unquantified` rather than invented; whether another one-way shape would also
pass the falsifiable pair; and whether the committed state can be given a magnitude,
which is nowhere attempted.

## 6. Boundary

Nothing here is a physical claim: no magnitude, sign or timing is asserted for
aerosols, low cloud, water vapour, wildfire or the committed component, and the
four-by-two table is a declared classification and not a result about the atmosphere.
Observational verification is **Unavailable**, `xue_study_data_used` is false, and the
parent's data-authenticity reservation is carried verbatim and un-narrowed. No Rust
source, `Cargo.toml`, `Cargo.lock`, `docs/` or `.github/` file was touched and no parent
contract was edited, so the advance-surface base commit does not move.

Authored and checked by deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted
through Mingli Yuan's authorized account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee. One agent wrote the contract, the checker
and this note; there is no independent reviewer.
