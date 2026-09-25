# 0237 — Singularity surgery: opposite chirality, a raised flux, and two roles that fail when swapped

**Date**: 2026-09-25 · **Contract**: `experiments/three_cycle_supplement_v1/contract.json`
(sha256 `157838642e9097ea4a1a1c7461db9e548affb0c6f3af7b830816f37f22b74f5a`) ·
**Checker**: `calibration.py` · **Evidence**: `evidence.json`
(sha256 `255e5044ab51162b4fc221b7b9324ff27d569ea08a0915f098b8f4a2161c2270`) ·
**Paired test**: `tests/python/test_three_cycle_supplement.py`

**Status**: one bounded external exact calibration in Python with declared `sympy`
for resultants, Groebner bases and Sturm counts. It inherits the frozen parent
contract (`three_cycle_chain_v1/contract.json`, `a3dc2e8d...`) and supplement one
(`contract-supplement-1.json`, `e125ee49...`) byte for byte and edits neither. No
native certificate, no stable API, no `ValueType`, no `OperationSpec`, no IR version,
no Seal, no library admission, no transport, no terminology home, no physical claim
and no data read or used.

中文摘要：把"奇点消除手术"写成可判定的构造并精确执行。奇异迹＝判别式碰撞点
$(-2,7019/8)$（在 B1 分支 $q=256p^2+76p+43/8$ 上，$D=0$ 精确验证）＋年缝（第 0 侧，
时向耦合 $31/512$ 为最大）。切除颈圈后边界恰有**两个连通分量**（24 格：外侧 $r=+1$、
内侧 $r=-1$）；两条螺旋手性相反（$\sigma_{\text{外}}=+1$、$\sigma_{\text{内}}=-1$），
颈圈通量**术前 0 → 术后 2，严格增大且全部归因**；外侧障碍被**写出并消解**，内侧在
**24 步内抵达、预算 36**。资源**无创造**（分层总和仍是 $9/8$），逐层封热；
**记忆层三年恒为深层**。投影作为映射被检验（认同两侧、把螺旋对读成单一旋转方向、
或把侧投进旋转方向的余域，全部被否决）。**两条控制未能判别，照实保留**（见 §5），
而"相反手性是否**必要**"记为 **Undecided**——因为通量增量是
$w\cdot n_{\text{phase}}\cdot(\sigma_O-\sigma_I)$，**声明的相位倾角与手性做了一样多的功**。

## 1. Excision and the two sides

The declared singular locus is two things at once: the discriminant collision on the
B1 branch at `(p,q) = (-2, 7019/8)`, where the cleared resultant
`-(8p+1)^6(8q+1)^2(64q+17)^2(2048p^2+608p-8q+43)` vanishes exactly (degree 12, 52
terms, factor multiplicities 6/2/2/1), and the annual seam at side 0, where the
declared coupling is `-31/512, -15/512, 0×10`. On the declared carrier `Z × Z_12` the
collar is the seam circle of 12 cells with radial extent 1, orientation sign +1 and
declared normal `(1,1)`; excising it leaves a boundary with **exactly two connected
components**, the outer side `r = +1` and the inner side `r = -1`, disjoint and not
identical, which is what replaces the singular carrier.

## 2. The two spirals and the raised flux

`S_σ(r,k) = (r + 1/12, k + σ mod 12)` is a rotation compounded with a radial advance
on each side — pure rotation and pure radial advance are rejected by the declared
condition. The chirality pair is `σ_outer = +1`, `σ_inner = -1`. With the pairing
`B(u,v) = u_r v_r + u_k v_k` and resource `(1/12, +1)` resp. `(1/12, -1)` per turn
(terms 13/12 and 11/12), the collar flux is **0 before and 2 after**: strictly
greater, rise 2, **attributed 2, unattributed 0**.

## 3. The two roles

Side O writes the obstruction out and discharges it: the record names the collision,
its parameter `q = 7019/8`, the vanishing factor value 0, the collar normal and the
boundary object, and the discharge is a condition on that record — **Discharged**.
Side I reaches its declared target `(r=1, k=0)` from `(-1,0)` in **24 steps against a
budget of 36**, with the excised cell at step 12 reported.

## 4. Resources, sealing, memory

The carried remainder (fast 1/4; layers mixed 1/8, thermocline 1/4, deep 1/2; total
7/8) is split by shares derived from the flux terms (13/24 and 11/24), and per-layer
sums equal the carried content exactly, so **no resource is created** by the surgery.
The layer-wise sealing bound is zero and the post-surgery drift is zero in all three
layers. The seam redistribution conserves 7/8 every seam, and **the layer holding the
carried memory is the deep layer at C1, C2 and C3 — stable**.

## 5. Controls, including the two that failed to discriminate

Chirality: the declared pair is accepted by the declared condition
`σ_outer = -σ_inner`, and the same-chirality pair is **rejected by the rule, not by a
count**. The reversed opposite pair `(-1,+1)` passes the condition but **lowers** the
flux to `-2`, which is reported rather than hidden. An unattributed rise is produced
and flagged: a declared non-helical extra introduction of `(1/8,0)` gives flux 17/8
with **1/8 unattributed**. Roles: an unwritten obstruction, an implicit obstruction
and a disagreeing record are each rejected; an over-budget arrival (radial advance
1/24, 48 steps, excess 12) is rejected; and swapping the roles fails **both** sides'
conditions. Conservation: a layer-wise violation whose total is conserved is reported
as a violation (`cancelled_by_the_total: false`), and the zero-redistribution control
is reported as the layer structure doing no work. Projection: the declared map is
accepted as a map, and three alternatives — identifying the two sides, reading the
pair as one rotation sense, and putting a side into the rotation-sense codomain — are
rejected. Inherited controls still run: under a declared change of observation
composition the mechanism readings are **unchanged** while the composition-only term
moves by exactly 3/256, and the fused reading is rejected as an artefact; the three
uncertainty terms appear separately at every seam and a fused figure (11/256) is
rejected; and the purely atmospheric chain **loses** the carried memory at the seam
(0) while the chain with the declared slow component keeps it (7/8), so the split does
work.

**Two controls failed to discriminate and are retained, not repaired.** First, with a
radial normal `(1,0)` the flux rise is zero for every chirality pair, so that control
cannot separate the declared pair from the same-chirality pair: the rise is a declared
consequence of the phase tilt as much as of the chirality. Second, both declared
chirality signs arrive in 24 steps at the declared target, so the arrival condition
does not discriminate handedness.

## 6. What is not decided

Whether opposite chirality is **necessary** rather than merely declared is recorded as
`Undecided`, with its reason in the payload: the rise is
`w · n_phase · (σ_O − σ_I)`, so the declared tilt does as much work as the chirality,
and the radial-normal case gives rise zero for every pair; the retained partial data
are the fluxes `2 / 0 / −2` for `(+1,−1) / (+1,+1) / (−1,+1)`. Also undecided: whether
the declared collar and its normal are canonical (rise 2 with tilt 1, 0 with tilt 0),
whether the declared projection is the only one, and whether the arrival path must
avoid the excised collar at every step.

## 7. Boundary

Nothing here is a physical claim: cold, heat, wind, ocean, plateau and forecast exist
only as declared projection labels, and no cold or heat quantity is asserted anywhere.
No data was read or used; the observational verification is recorded as
**Unavailable** with the parent contract's authenticity reservation carried verbatim
and un-narrowed. No Rust source, `Cargo.toml`, `Cargo.lock`, `docs/`, `.github/` or
parent contract was touched, so the advance-surface base commit does not move. Ruff is
absent from the project virtual environment; the host's ruff 0.15.7 reports nothing on
the two new Python files.

Authored and checked by deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted
through Mingli Yuan's authorized account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee. One agent wrote the contract, the
checker and this note; there is no independent reviewer.
