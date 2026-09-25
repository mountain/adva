# 0238 — Three chained annual cycles: every cycle closes, the remainder is counted in steps, and the drift control fails to discriminate

**Date**: 2026-09-25 · **Contract**: `experiments/three_cycle_chain_v1/contract.json`
(sha256 `a3dc2e8d86e45139484fceed571ef99ea3b63f18748c6f1c82bb031a3305a965`) ·
**Checker**: `calibration.py` (sha256 `37180ea0...6975bd77`) · **Evidence**: `evidence.json`
(sha256 `f78fdf205bb03cfd65f6992ac9e1a97de8a28a71a9ac4e61c009fb08e2397c65`) ·
**Paired test**: `tests/python/test_three_cycle_chain.py`

**Status**: one bounded external exact calibration in Python. Supplement one
(`contract-supplement-1.json`) is not folded in here; the surgery run
(`three_cycle_supplement_v1`, note 0237) inherits both contracts. No native
certificate, no stable API, no Seal, no admission, no transport, no terminology
home, no physical claim, no forecast, no skill claim, no data read or used.

中文摘要：三个年周期（C1＝2026-12→2027-12、C2、C3）精确链接。缝态取闭合三次
$h^3+8h^2+64h-320$ 的实出口 $w=3.2035072879526181\ldots$ 作为 $\mathbb{Q}(w)$ 的精确元素；
**C1、C2、C3 各自 `ClosedByFixedPoint`**，缺陷与漂移**恒为 0**；累积读数
$E^3-h=h(h^3+8h^2+64h-320)Q$，$Q$ 为 60 次、系数**全正**、Sturm 计数 0 ⇒ **不存在真正的实三周期轨道**。
步数：9 步/周期 × 3 ＝ 27 基础步、末尾余数 **6**、合计 33（余数 $2/9$＝486 赞）；
末尾块 **2 步**被接受，**1 步与 3 步都被规则拒绝**。角色分型：下/中/上 ＝ 思/福/禍，
**9 条条件、9 条禍对照全部执行、0 条失败**。快慢：fast＝slow＝$w/2$、**慢分量每缝漂移 0**；
声明储库弛豫系数 $1/30$（时常数 30）、淡水项 $29w/60$、稳态 $w/2$。封热界 0，
声明漏链 $3/1000$ 被检出。**两条要记住的负面结果**：漂移控制**未能判别**
（闭合是逐点条件，C1 闭合则 C2/C3 不可能漂移——按失败控制记录，并给出反事实漂移值）；
"一个实出口"必须与整个闭合读法的两个实根（$h=0$ 平凡出口 ＋ $w$）分清。

## 1. The chain and its closure

The seam state is the real exit `w` of `h³ + 8h² + 64h − 320`, isolated by an exact
rational bracket inside `(3,4)` (Sturm count 1; the derivative minimum is `128/3 > 0`
at `h = −8/3`), carried as an exact element of `Q(w)` with coordinates
`a + b·w + c·w²`. **C1, C2 and C3 are each `ClosedByFixedPoint`**: entry equals exit
equals `w`, closure defect and drift exactly zero. The cumulative reading is

$$E^3 - h = h\,\bigl(h^3+8h^2+64h-320\bigr)\,Q,$$

with `Q` of degree 60, **all coefficients positive** and **Sturm count 0**: there is
**no genuine real period-3 orbit**, and the real fixed points of `E³` are exactly `0`
and `w`.

The contract's phrase "the closure amplitude with one real exit" needed
disambiguating and the run does it: the **nontrivial closure branch** has **one** real
exit, while the **whole closure reading** `E(h) = h` has **two** real roots — `h = 0`,
which is trivial because `E(0) = 0` identically, and the closure amplitude `w`.

## 2. Steps, remainder, and the role typing

Nine steps per cycle over three cycles give 27 baseline steps, an end-block remainder
of **6** and a total of **33** (remainder `2/9`, i.e. 486 zan); the two declared step
readings agree on the remainder. The end block holds **exactly two** extra steps, and
a block of **one** and a block of **three** are both **rejected by rule and asserted**.
The three-by-three role typing is declared structure taken from the Taixuan zan
division — lower/middle/upper as deliberation/fortune/calamity, three each, with the
exit clause 終養始 at position 9 of the upper group — and **all nine conditions have
their calamity counterpart executed, with no failed control**.

## 3. Fast and slow, the declared reservoir, and sealing

The fast and slow components are each `w/2` at every seam and sum to `w`; the **slow
component's drift is exactly zero at every seam**, so it is conserved. The declared
slow reservoir has relaxation coefficient `1/30` (time constant 30), a freshwater
source term `29w/60` and steady value `w/2`, so it is **stationary at the chain's own
seam**; displacing it by 1/4 gives drifts `−1/120, −29/3600, −841/108000`, each a
factor 29/30 of the previous, while the open-ocean variant drifts
`−1/60, −29/1800, −841/54000` and is **not conserved**. The sealing bound is zero and
holds; a declared leaking chain `(1/1000, 1/500, 3/1000)` **is detected**, and the
leakage terms are constrained nonnegative precisely so that the sealing side cannot
cancel a violation (a signed term would: `1/1000 + (−1/1000) = 0`).

## 4. Controls: what discriminated, and what failed to

Memory **discriminated**: under a 1/4 displacement the primary slow response is
`(−1/120, 0, 0)` against the open ocean's `(0, −1/60, 0)`, exact and different.
Placement, leakage, remainder and the baselines all discriminated. The
**drift/iterability control FAILED and is retained as a failure, not repaired**: no
chain satisfying the declared rules can close in C1 and drift in C2/C3, because
closure is the pointwise condition `E(h) = h`, so `h₁ = h₀` forces `h₂ = h₁` and the
drift is identically zero. The detector's discriminating power is shown on the
counterfactual seam `w + 1/4`, whose three-cycle drifts are nonzero and exact. Readings
that do **not** discriminate are recorded too: the seam state and the closure status
are identical in the primary and the open-ocean variants, as are their three-cycle
seam residuals.

Baselines are reproduced and reported in an asserted exact order (no decimal is
compared anywhere): `J_inf = 1` at `(−2, 17/10)` with the level-one equation
`3285h⁴/512 − 219h³/64 − 19h²/20 + 3h/8 − 1 = 0` having **two** real branches in
`(−1,−1/2)` and `(1/2,1)`; the closure amplitude `3.2035072879526181...` with **one**
real exit; the level reading's largest amplitude `2 + sqrt(8√17 − 20)` with **two**
real branches, enclosed in `(11/2, 23/4)`; and the ordering
`1 < 3.2035072879526181... < 2 + sqrt(8√17 − 20)`.

## 5. Undecided

Whether a chain closing in C1 can drift in C2/C3 (impossible under the declared rules,
with the reason and the counterfactual data retained); a genuine real period-3 orbit
(none, with the degree-60 quotient and its Sturm count retained); the physical
magnitude and sign of the declared freshwater source term (a declared exact element,
never estimated or compared with any observation); and recovering the six historical
forecast maps as one annual program (not attempted; note 0233 records that those maps
failed composition).

## 6. Boundary

The chain is future and unverified: observational verification is **Unavailable** and
the contract's data-authenticity reservation is carried **verbatim**; no data was read
or used, and `xue_study_data_used` is false. The reservoir is a **declared model, not
a claim about the ocean**, and its 30-step time constant against a 3-step chain is a
retained mismatch. No physical, forecast or skill claim is made anywhere, and no Rust
source, `Cargo.toml`, `Cargo.lock`, `docs/` or `.github/` file was touched, so the
advance-surface base commit does not move.

Authored and checked by deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted
through Mingli Yuan's authorized account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee. One agent wrote the contract, the
checker and this note; there is no independent reviewer.
