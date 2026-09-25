# 0240 — A proposal-only optical scheme, its three derived bounds, and one erratum the run itself cannot repair

**Date**: 2026-09-25 · **Contract**: `experiments/optical_imbalance_proposal_v1/contract.json`
(sha256 `116913a9369e43666d80cf65a6877164f186fd813955a4d1c05f39777496fa4f`) ·
**Checker**: `calibration.py` (sha256 `49034f1b...9277597`) · **Evidence**: `evidence.json`
(sha256 `10e639d3843b29dbad0d815d8599ea5c2ff7c391b1eb1f1a3a8a422036538624`) ·
**Paired test**: `tests/python/test_optical_imbalance_proposal.py`

**Status**: `PROPOSAL ONLY - 提议性方案`. One bounded external exact calibration of a proposed
scheme. It authorizes nothing, decides nothing, deploys nothing, asserts no physical
effect and uses no data. No native certificate, no stable API, no Seal, no admission,
no transport, no terminology home.

中文摘要：把"用反射镜出功率、光纤出相位、末级衍射定图案"的提议写成精确算术标定，
并把三类内容分栏：**推导出的界**（无源光斑下限、单模光纤 étendue 上限、L2 可用通量分数）、
**声明约定**（平台距离、面密度、目标面积与通量、年发射率等 23 个精确常量）、
**仅属提议的记账**（`authorization/decision/deployment/governance` 全为 none/unaddressed）。
六个"过度外推"控制全部产生否决（各带一个被接受的对照），父契约两条禁令（不许净额化、
承诺不可封）照旧适用且**终止问题记为 Unaddressed**。**本笔记同时登记一处勘误**：
payload 里 L2 可用通量分数的推导把**地球角半径**与**日面角直径**相除（差一个 2 倍），
正确值应为约 **0.149**（遮蔽 ≈0.851）而不是 payload 的 0.787；该错误**不被静默修正**，
保留原样并在此登记，受其影响的下游量需在后续一轮重算。

## 1. What the run establishes exactly

Twenty-three declared constants (each with a unit and each marked declared, not measured
here, not read from data) drive three bounds computed in exact rational arithmetic:

- **Passive spot floor** `theta_sun * L`: near-Earth `≈3720.37 m`, geostationary
  `≈332843.24 m`, second Lagrange point `≈13812901.47 m`. The L2 floor **exceeds the
  Earth's diameter** by about 1071 km. The historically reported case of a 20 m mirror
  producing a spot of about 5 km at the declared 400 km is consistent with the floor,
  both with and without the aperture term, and the excess over the floor is attributed
  to nothing.
- **Fibre power ceiling** `B * lambda^2`, exactly one microwatt per mode: a gigawatt
  needs exactly 10^15 fibres and a megawatt exactly 10^12; the declared network of 10^6
  fibres can carry at most one watt, i.e. 10^-12 of the required power. This bound, not
  style, is what forces mirrors to carry power and fibres to carry phase.
- **Second Lagrange point geometry**: the derived umbra length is less than the declared
  distance, so the Earth is in the **antumbra** and the Sun appears annular there — a
  derived result, not an assertion.

The division of labour, the two deployment modes (L2 night-side addition; near-Earth
relay chain) with **separate, un-netted accounts**, and the declared-target arithmetic
(patch, flux, intercepting area, areal mass, launch-years, mirror count) are all reported
as arithmetic on **declared proposal inputs** with delivery efficiency declared as 1, so
every area is a lower bound. Every one of the six overreach controls produced a rejection
with an accepted companion: a passive pattern finer than the floor, more than the
étendue ceiling through one mode (or fibres as a power channel), the coherent fraction
treated as the whole power, a usable fraction above the derived one, an asymmetric pattern
without a declared blaze direction, and a target reached by loosening the derivation
rather than the declaration. Both inherited prohibitions are executed against rejected
controls: no netting of the two modes' accounts, and no sealing of a component that is by
definition a leak. The termination problem is recorded as `Unaddressed`, with
`governance: unaddressed`, and this run does not attempt to solve it.

## 2. The erratum, registered rather than repaired

The payload's `l2_usable_fraction` divides the Earth's angular **radius** by the Sun's
angular **diameter**: it uses `theta_earth = 6371/1500000` rad against
`theta_sun = 1546000/167886523` rad, whose ratio is `0.4612`, and reports the unusable
fraction as that ratio squared, `≈0.2127`, hence a usable fraction of `≈0.7873`. The
comparison must pair like with like: with both as radii, `theta_earth/theta_sun ≈ 0.9225`,
so the **occulted** area fraction is `≈0.851` and the **usable** fraction is `≈0.149`.
The run itself flags the radius-versus-diameter convention as its first `Undecided` item,
but flags it for the spot-floor bound and does not notice that the *same* convention
mismatch corrupts the usable fraction, because the two quantities were declared
separately.

Consequences, recorded rather than silently fixed: the **spot floor is unaffected** (a
penumbra *diameter* is `D + theta_sun(full size) * L`, so the declared pairing is right
there); the **usable fraction, the usable flux, and everything downstream of it for mode
A** (intercepting area, areal mass, launch-years) **inherit the error**, as does
overreach control 4, which rejects a claimed usable fraction above `0.7873` instead of
above the correct `≈0.149`. Nothing in the payload or the checker is edited here: the
frozen evidence keeps its digest, this note registers the correction, and a follow-up run
with its own contract must recompute the affected quantities and re-issue the control.
Also retained, not repaired: the contract's prose "of order a trillion fibres" for a
gigawatt is three orders away from the exact `10^15` at the declared radiance, and the
one control that **failed to discriminate** — the same target reached by loosening the
declared areal density cannot be distinguished, by arithmetic alone, from a
re-derivation, so what the six controls actually separate is the derived bounds (which
may not be substituted) from the declared inputs (which may be re-declared).

## 3. Boundary

Nothing here is a physical claim: no effect on any atmosphere, ocean, cloud, surface,
weather or climate is asserted or estimated, and the target figures are proposal
arithmetic. `authorization`, `decision` and `deployment` are all `none`, `governance` is
`unaddressed`, `physical_effect_asserted` is `none`, and `data_used` is `none`; the
document states in its own payload that it is a 提议性方案 and that it authorizes,
decides and deploys nothing. The derived bounds rest on declared constants carried as
exact rationals; the *form* of each bound is not a declaration, while a different
declaration of the constants is a different run. No Rust source, `Cargo.toml`,
`Cargo.lock`, `docs/` or `.github/` file was touched and no parent contract was edited,
so the advance-surface base commit does not move.

Authored and checked by deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted
through Mingli Yuan's authorized account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee. One agent wrote the contract, the checker
and this note; there is no independent reviewer. The erratum in section 2 was found by
the parent session while reading the run's own report, not by the run.
