# 0242 — A spatiotemporal ratchet: net transport needs both asymmetries, and the standing wave transports nothing

**Date**: 2026-09-25 · **Contract**: `experiments/spatiotemporal_ratchet_v1/contract.json`
(sha256 `9c495906eee86e6bfaa5eb39c88ea8b7cc9048f86bec574e458e413626a9963c`) ·
**Checker**: `calibration.py` · **Evidence**: `evidence.json`
(sha256 `26cf72d7927f29c87bdb765ce66453ead0d0aafdec54498656d09bd605a91666`) ·
**Paired test**: `tests/python/test_spatiotemporal_ratchet.py`

**Status**: `PROPOSAL ONLY - 提议性方案`, one bounded exact calibration of a **declared discrete
model**. It authorizes nothing, decides nothing, gives **no magnitude, sign or timing for any
physical quantity**, and uses no data. Nothing is ablated, melted, moved or heated: the wider
programme's "singular point" appears **only** as a declared pinning site, that is as a declared
spatial asymmetry.

中文摘要：把"联动创造安全范围下的时空不平衡"写成可判伪的离散模型并精确求解。环 $N=6$，
声明的反射 $R(i)=-i$，两个声明势（对称的 $U_{\rm sym}$ 与非对称的 $U_{\rm asym}$，后者的唯一
最小点是声明的**钉扎位**），门函数只读斜率符号，相位梯度 $g\in\{-1,0,+1\}$，四步声明排程
$|\nu_s|\le1/2$（每步声明能量 $\le2$）。结论四条，全部精确：**空间对称＋时间对称 ⇒ 输运恰为 0**；
**空间非对称＋时间对称 ⇒ 恰为 0**；**空间对称＋时间非对称 ⇒ 恰为 0**（每步流量 $=\frac38\nu_s$，
故输运 $=\frac38\cdot$排程均值 $=0$）；**两者兼有 ⇒ 非零**
$\mp\frac{2395373021828541}{130893752065903472383}$，**相位梯度反号时方向精确反向、两向之和恰为 0**。
驻波 $g=0$ 输运为 0 且退化为均匀扩散。连通性不变、每步声明能量 $2,1,1,2\le2$（恰触界）。
七条控制全部被否决（各带一个被接受的对照）；**一条控制未能判别并保留**：把声明势整体乘 3
给出**完全相同**的门、转移与输运——因为门只读斜率符号，势的幅度从不进入转移。

## 1. The declared model

A ring of six sites with adjacent pairs, the declared reflection `R(i) = (−i) mod 6`, two declared
integer potentials — `U_sym = (2,0,1,2,1,0)`, invariant under `R`, and `U_asym = (3,0,1,2,3,2)`,
not invariant, with a unique minimal site that is the **declared pinning site** — one declared gate
array read leftward at the reflected site, a declared phase gradient `g ∈ {−1,0,+1}` whose sign fixes
the declared direction, a declared transfer whose amplitudes are `¼(1 ± ν_s g G)`, a declared
four-step schedule with declared bound `|ν_s| ≤ 1/2` and declared step energy `4|ν_s| ≤ 2`, the
declared periodic measure (the measure the transfer reproduces after one period, with uniqueness
checked by the exact rank of `P − I`), and the declared transport as the net displacement over
exactly one period.

## 2. The four required zeros and the one non-zero

| Item | Configuration | Exact transport |
|---|---|---|
| **R1** | symmetric potential, time-symmetric drive | **0** (measure uniform; flows `3/16, 0, −3/16, 0` pair exactly) |
| **R2** | asymmetric potential, time-symmetric drive | **0** (measure not uniform; flows pair exactly; transfer field invariant) |
| **R3** | symmetric potential, time-asymmetric drive | **0** (every per-step flow is exactly `(3/8)·ν_s`, so the transport is `(3/8)·` the schedule mean, which is zero) |
| **R4** | both asymmetries | `−2395373021828541/130893752065903472383` at `g = +1`, exactly its negative at `g = −1`, **exact sum zero**; the `g = −1` measure is the exact reflection of the `g = +1` measure; the uniform-reference cross-check reads `±1/32768` |
| **R5** | standing wave `g = 0` | **0**, with the transfer collapsing to uniform diffusion at every site and step |
| **R6** | topology and bound | connectivity unchanged (six sites reached; edge set preserved; every edge positive in both directions); step energies `2, 1, 1, 2` against the declared bound 2, reached exactly |

Every one of the zeros is produced as an **executed rejection** of the corresponding claim, not as a
remark: the claims that the symmetric forcing transports, that spatial asymmetry alone transports, that
temporal asymmetry alone transports, that transport is independent of the gradient's sign, and that the
standing wave transports are each rejected with an accepted companion. The pair control is decisive:
the *same* asymmetric potential gives exactly zero with the time-symmetric schedule and a non-zero
value with the time-asymmetric one.

## 3. Controls, including the one that failed

Seven controls were executed and **all seven rejected** with accepted companions: the three symmetric
cases, the gradient-sign independence, the standing wave, the schedule crossing the declared step
energy bound (claimed 2, derived 3), and the schedule changing the declared connectivity (claimed 0,
derived 1/8). **One control failed to discriminate and is retained rather than repaired**: rescaling
the declared potential by the declared factor 3 leaves the gate array, the transfer and the transport
identical, because the gates read only the *slopes'* signs and the potential's magnitudes never enter
the transfer. The limitation is recorded in the payload and as an `Undecided` item, and no
magnitude-carrying gate rule is decided here.

Six further items are `Undecided` with retained data: whether the declared gate rule is the intended
relation between potential and transfer; whether the gradient should take values beyond `{−1,0,+1}`;
whether the uniform reference measure should be *the* transport measure (only the periodic measure's
zero follows from the checked invariance of the transfer field); whether the declared time symmetry
should be read as the antisymmetric rocking used here or as a palindromic schedule (the palindromic
reading is **not** decided); whether the step energy should be called an energy at all; and whether the
zeros persist for another ring, period, step size or gate value.

Three failures of the implementation itself are on the record rather than hidden: a connectivity
candidate that *adds* a non-declared edge rather than dropping one (the assertion was corrected to
compare adjacency sets), a sign-vacuous duplicate reflection assertion, and a paired test that
composed the period transfer in the wrong matrix order — the independent recomputation disagreed with
the checker on R2 alone, which is how the test bug was found.

## 4. Boundary

Nothing here is a physical claim: no material is transported, nothing is ablated, melted, moved or
heated, no magnitude, sign or timing is asserted for any physical quantity, and no data is read or
used. The model is declared, and a different ring, potential, drive, period or gate rule is a different
run: the zeros under a symmetric forcing are statements about **this** declared model and are not a
theorem about any physical system. `authorization`, `decision`, `deployment` and
`physical_effect_asserted` are `none`, `governance` is `unaddressed`, and the termination problem is
recorded as `Unaddressed` and not solved. No Rust source, `Cargo.toml`, `Cargo.lock`, `docs/` or
`.github/` file was touched and no parent contract was edited, so the advance-surface base commit does
not move.

Authored and checked by deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted through Mingli
Yuan's authorized account proxy. Account use is not his authorship, review, endorsement or correctness
guarantee. One agent wrote the contract, the checker and this note; there is no independent reviewer.
