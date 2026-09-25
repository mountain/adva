# 0243 — The geometry foundation: shared items, the corrected pairing, and the spacetime-group clause

**Date**: 2026-09-25 · **Contract**: `experiments/geometry_foundation_v1/contract.json`
(sha256 `1e07f9a04a9d6d60073a5cb3f726df7d38554608f4d023383314fbff83217750`) ·
**Supplement**: `contract-supplement-1.json`
(sha256 `1540a1290d805bf031fd6734fba1701267e7ce1e67a19a6d52a7e1b1dce7c7ab`) ·
**Checker**: `calibration.py` (sha256 `f108bc02...f06fe9`) · **Evidence**: `evidence.json`
(sha256 `ecd9dbe122ac96732f37ccc44798cf8fec3d58d074adbeab204f408e2c8974a6`) ·
**Paired test**: `tests/python/test_geometry_foundation.py`

**Status**: `PROPOSAL ONLY - 提议性方案`. One bounded exact calibration of the shared geometric
basis of proposals one to three, plus a supplement carrying the spacetime-group clause.
It authorizes nothing, decides nothing, asserts no physical effect, gives no magnitude for
any physical quantity and uses no data. No native certificate, no stable API, no Seal, no
admission, no transport, no terminology home.

中文摘要：把三个提议**共用的几何**各写一次并精确算出：光斑下限 $\theta_\odot L$（含半影直径形式）、
étendue 上限（每模恰 $1\,\mu W$）、**更正后的** L2 可用分数（遮蔽 **0.850952…**、可用 **0.149047…**，
被作废的 0.787261… 按摘要引用而不修改）、图案尺度、对称性约束、工作区域／时刻算法、消融能级分配，
并把**配对规则**做成"混配即抛错"的规则（故意错配被否决，错**恰好 2 倍／4 倍**）。另有两处**更正**写进
supplement：① 非手性阿基米德多面体的**完整**点群（$T_d$ 24、$O_h$ 48）含 12／24 个非正常元素，
**不在 $\mathrm{SO}(3)$ 里**，只在旋转部分上成立，所以与相对论时空匹配的是 **$\mathrm{O}(3)$（旋转＋宇称）**
$\subset \mathrm{O}(3,1)$；② "地面图案继承点群"是**错的对象**——时空对称性才该声明：**（星座＋排程）在
「空间操作＋时间平移」下不变 ⇒ 净输运恰为 0**，**该不变性缺失 ⇒ 定向输运**，方向由相位梯度写定。

## 1. What the run establishes exactly

Thirty declared constants drive every shared item, each computed once and referenced rather
than repeated:

- **Pairing rules as rules.** A mixed pairing raises `PairingViolation`; the deliberately
  mis-paired control (the Earth's angular radius against the Sun's angular diameter) is
  rejected with the exact factor **2** in the ratio and **4** in the fraction, while
  radius-with-radius and diameter-with-diameter are accepted and give **the same** ratio —
  so the rule is about like-with-like and not about a preferred kind. Handing a *radius* to
  the penumbra-diameter form is rejected too, short by exactly `theta_sun_radius * L`.
- **Corrected usable fraction at the second Lagrange point**: ratio `0.922470...`, occulted
  `0.850952...`, usable `0.149047...`, the two summing to exactly one; the superseded
  `0.787261...` is recomputed by the mis-paired rule, asserted equal to the earlier run's own
  retained value read at digest `10e639d3...` (cited, not edited), and the difference is
  exactly **three quarters** of the corrected occulted fraction.
- **Spot floors** `3720.373...`, `332843.242...`, `13812901.467...` m at the three declared
  distances, each with its penumbra diameter beside it, the third exceeding the Earth's
  diameter; **étendue ceiling** exactly one microwatt per mode; **pattern scale** equal to the
  floor by reference, with finer structure washed out by the extended source and coarser
  interference structure excluded because it would need an aperture below the declared
  coherence length (the declared aperture is forty times it).
- **Symmetry**: three declared Archimedean solids with declared vertex sets and groups built
  by exact integer matrix closure — truncated tetrahedron `T_d(24)` with rotation part `T(12)`,
  cuboctahedron and truncated octahedron both `O_h(48)` with rotation part `O(24)` — each
  vertex set verified invariant, each rotation element verified to have determinant exactly
  `+1`. The run reports, rather than smoothing over, that the **full** groups contain improper
  elements and so are **not** inside SO(3). Controls reject putting the time direction into
  the point group (with an exact witness rotation) and claiming an arbitrary placement
  invariant.
- **Work-region and work-time calculus**: a declared constellation of four platforms over a
  twelve-step window, per-platform-per-region duty exactly `1/4`, per-region duty exactly `1`
  under the relay, sweep returning after four steps; single-platform sustained coverage is
  rejected as exactly four times wrong, and choosing a region in flight is rejected because
  the table computed in advance assigns it elsewhere.
- **Ablation-level assignment**: six declared tasks onto four declared levels (2/2/1/1), every
  assignment to a level and never to a platform; routing to a platform and using a level
  outside the declared set are both rejected.
- **Stage one is calibration**: 4096 declared units carried identically through compute,
  aggregate and distribute (index sums identical at all three stages, 64 units per declared
  recipient); then launches 1..8 with a cumulative network 1, 3, 6, 10, 15, 21, 28, 36, so
  **learning enters at the first step**; the topology-broken control (a merge losing exactly
  one unit) and the learning-delayed control (zero learning units at the first step) are both
  rejected.
- **Declared obligations** (safety, topology, controllable impact, bounded and tolerated
  error) each with an executed violating control that is rejected; proposal-only bookkeeping
  with authorization, decision, deployment and physical effect all `none`, governance
  `unaddressed`, and the termination problem `Unaddressed` and unsolved.

**One control failed to discriminate and is retained**: a declaration whose *kind* label is
wrong but whose kinds match cannot be caught by the kind rule, and is caught only by a
different rule (the exact bracket for `0.851`). Eight items are `Undecided`, including whether
"subgroup of SO(3)" means the full group or its rotation part.

## 2. The spacetime-group clause (the supplement)

Two corrections are recorded in `contract-supplement-1.json` rather than by editing the
frozen contract. First, the symmetry that matches relativistic spacetime on the
constellation's side is **O(3)** — rotations together with parity — embedded in the full
Lorentz group **O(3,1)**, because the full point groups of the achiral solids computed here
contain improper elements; parity is exactly the element that pairs antipodal platforms, which
is what makes the sunlit and unsunlit sides structural. Second, the ground **pattern**'s
symmetry is the *wrong object* for a transport goal: a pattern symmetric in space and
unchanging in time has no direction and drives no net transport. The object to declare is the
**spacetime symmetry of the (constellation, schedule) pair**:

- if that pair is invariant under any operation of the form *spatial operation combined with a
  time translation*, the net transport over a period is **exactly zero** — the mechanism is
  the one already executed in the ratchet run of note 0242, where a reflection composed with a
  half-period shift makes the per-step flows pair exactly;
- **directed transport requires that invariance to be broken**, i.e. a non-symmorphic
  spacetime element to be absent; the direction is then written by the declared phase
  gradient, not by the pattern's shape;
- the point group's remaining role is to constrain **which schedules are compatible with the
  declared placement**: a schedule invariant under a subgroup gives a standing pattern and
  transports nothing, while one carrying a phase gradient gives a travelling pattern.

The supplement requires the zero and the non-zero to be **produced** (each as an executed
rejection or an executed result), and requires the rejections of a falsely claimed invariance,
of a claimed direction not following the gradient's sign, of a direction fixed by pattern
shape alone, and of identifying an achiral solid's full point group with a subgroup of SO(3).

## 3. Boundary

Nothing here is a physical claim: no magnitude, sign or timing is asserted for any physical
quantity, no pattern is projected onto any real surface, and nothing is ablated, melted, moved
or heated. `authorization`, `decision`, `deployment` and `physical_effect_asserted` are `none`,
`governance` is `unaddressed`, observational verification is `Unavailable`, no data was read or
used, and the termination problem is `Unaddressed` and not solved. The run's one failed control,
its eight `Undecided` items and its rotation-part finding all remain in force. No Rust source,
`Cargo.toml`, `Cargo.lock`, `docs/` or `.github/` file was touched and no parent contract was
edited, so the advance-surface base commit does not move.

Authored and checked by deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through
Mingli Yuan's authorized account proxy. Account use is not his authorship, review, endorsement
or correctness guarantee. One agent wrote the contract, the checker and this note; there is no
independent reviewer.
