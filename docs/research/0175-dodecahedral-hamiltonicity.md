# 0175 — 十二面体图的哈密顿圈：精确计数，与一条被声明的 Icosian 式规则

Date: 2026-09-13. Direction and question: Mingli Yuan. Formalization, checker,
execution and writing: deepseek-v4-flash-vision-exp (DeepSeek Harness),
submitted through his account as an authorized proxy; he has not reviewed or
endorsed it, and his name is not evidence for any content here.

Status: **bounded external exact calibration**, one run inside a frozen contract,
with one retained deviation. It introduces no stable API, no native type, no
library admission, no `docs/claims.toml` entry and no Seal.

Base: `f6d0d12`. Contract:
[`contract.json`](../../experiments/dodecahedral_hamiltonicity/contract.json).
Checker and evidence:
[`checker.py`](../../experiments/dodecahedral_hamiltonicity/checker.py),
[`evidence.json`](../../experiments/dodecahedral_hamiltonicity/evidence.json).

## 0. 这份记录从哪里来

问题最初以 "Icosian game"（哈密顿 1857 年的二十面体游戏）提出。先说检索结果，因为它是这份记录的起点：

- `Icosian` 在 `adva` 与 `adva-library` 中**零命中**，在全部 39 份会话记录中也只出现在提出该问题的这一轮；
- 本仓库既有的 `Hamiltonian` **全部是物理/谱意义**的哈密顿量（`0106-ontological-programming-type-barriers.md`：`does not define a physical Hamiltonian`；`0106-three-hole-conjugate-m6-projective-lift.md`：`a phase, Hamiltonian, or time parameter`），process-geometry 侧也是力学意义（`dΩ = T dH`）。**图论意义上的哈密顿路/圈，此前从未被检查过**；
- 与十二面体相邻的材料是 **golden-ratio 线**：`adva-library/golden-ratio/plates/dodecahedron-vertices.webp` 与 `docs/research/golden-ratio-receipts-and-source-boundaries.md` 已执行过"十二顶点二十面体之对偶"的坐标、面心、内切球半径、正五边形对角比 φ、内接立方体与八面体等检查——**唯独没有哈密顿性质**。

所以这里做的是一件**新事**，而不是某条旧结论的延续；它唯一引用的既有材料，是那套已经执行过的二十面体顶点与面。

## 1. 问题与冻结契约

**问题**：由两个互相独立的构造得到的十二面体图 `G`（20 顶点、30 棱），在预先声明的等价关系下有多少个哈密顿圈？加入一条**本仓库自己声明的** Icosian 式局部规则后还剩多少？声明的控制组能否把判据证成非空判据？

六项契约按 `0129` §3 冻结在 `contract.json` 中，要点：**十二面体图的哈密顿圈数不从文献导入、也不预设**——它是运行输出；若日后与文献比较，比较写在运行之后，不一致记为残余。

## 2. 两个构造与接口检验

- **G1**：标准十二面体坐标（`(±1,±1,±1)`、`(0,±1/φ,±φ)`、`(±1/φ,±φ,0)`、`(±φ,0,±1/φ)`），邻接 = 精确算出的**最小平方距离**（`8 - 4φ`，即棱长 `2/φ`）。
- **G2**：**已执行过**的十二顶点二十面体之**对偶**：取其 20 个面，邻接 = 共享一条棱；每个二十面体顶点周围的 5 个三角形给出对偶图的一个五边形面。

**接口检验（全部精确、无浮点）**：

| 检查 | 结果 |
|---|---|
| 两构造规模 | 各 20 顶点、30 棱、3-正则、连通、围长 5 |
| 二十面体本身 | 12 顶点、30 棱、20 面 |
| 同构见证 | 回溯搜索给出**显式双射**并逐棱验证；无同构则停 |
| 面系统 | 两个构造各有 **12 个五边形面**，每条棱恰在 2 个面中（`Σ = 60 = 2E`） |
| 独立几何复核 | 20 个**三角形顶点和**按最小距离构成的图也同构于 `G1`（20 顶点 30 棱） |

## 3. 结果

| 量 | G1 | G2 |
|---|---:|---:|
| 哈密顿圈（定向、固定起点） | **60** | 60 |
| 哈密顿圈（无向无根） | **30** | 30 |
| 恒等式 `定向 = 2 × 无向` | 成立 | 成立 |
| 满足"存在连续 5 顶点恰为一个面"的圈 | **30 / 30** | 30 / 30 |
| 每个面被"连续 5 顶点"命中的次数 | 12 个面各 **10** | 相同 |
| 每条圈的命中段数分布 | **恰好 4 段**（直方图 `{4: 30}`） | 相同 |
| 命中总次数 | 120 | 120 |

**十二面体图的哈密顿圈数是 30（无向无根）**，两个独立构造一致，且有显式同构见证。这正是文献里常见的那个值——但本记录**不**把它当作从文献导入的事实：它是运行输出，文献值只是事后一致。

## 4. 那条"被声明的规则"是空的

契约里声明的规则（**本仓库的类比，不是历史规则**："圈中存在连续 5 个顶点恰好构成某个五边形面"）**没有筛掉任何圈**：30 个圈全部满足，而且每条圈**恰好**命中 4 段、12 个面命中次数完全均匀（各 10）。

这是一个**要点**，不是附注：在这种十二面体图与这条局部规则下，"五顶点成面"是**每条哈密顿圈的普遍特征**，因此它不构成选择规则。所以它不能用来复刻历史游戏的筛选效果；历史规则究竟是什么，本记录不主张（见第 7 节）。

## 5. 控制组

| 控制 | 结果 | 期望来源 |
|---|---:|---|
| `C3` / `C5` | 1 / 1 | 一行计数论证（唯一循环序） |
| `K4` | 3 | 一行计数论证 `(4-1)!/2` |
| 立方体图 `Q3` | 6 | **计算值**，DFS 与独立位掩码 DP 一致（未与文献比较） |
| Petersen | 0 | **文献导入**的经典事实，运行后比较、一致 |
| 割点"领结"图 | 0 | 一行割点引理 |

正负两侧都在：既有"必须非零"的正控制，也有"必须为零"的负控制，因此判据不是"凡来皆是"或"凡来皆否"的机器。

## 6. 成本与预算

| 项 | 声明上界 | 实际 |
|---|---:|---:|
| 搜索节点 | 2×10⁷ | **25 501** |
| 墙钟 | 60 s | **0.008 s** |
| 保留产物 | 1 MiB | 22 974 B（`evidence.json`） |
| 子进程 | 1 | 0（检查器自身进程内完成） |

无续跑、无重试、无燃料重置。

## 7. 偏差与残余（必须保留）

1. **契约偏差**：契约的控制组点名了 **Herschel 图**，但运行时**没有取到它的棱表**，因此未使用；改用一个**可一行论证**的割点图作为负控制。偏差已在 `contract.json` 的 `deviation_note`、`evidence.json` 与本记录中登记，**不是静默修补**。
2. **历史规则未取源**：Hamilton 的 Icosian game 的**确切规则**本记录不主张；契约里那条局部规则明确是本仓库的类比。要复刻历史游戏需要单独取源并另行登记。
3. **双曲紧化那一半是 preflight 阻塞项**：契约里把它登记为"没有接口说明、照 `0129` §3 不启动"，因此本记录**不**主张"双曲紧化之后哈密顿性如何"。它与 `0072`（普通紧化不升维，`H² ∪ S¹_∞ ≅ D²`；三维提升走单位切丛）**没有**任何被检查过的联系。
4. `Q3` 的计数与文献值未比较；比较若做，须写在运行之后，不一致记为残余。
5. 三个中间失败在过程中发生并被修掉（面序走查在 5-循环上取错候选、`visited` 的闭包作用域、面在搬运时被排序破坏了循环序）。它们**未进入**任何提交的产物——最终产物是 `Checked`，`evidence.json` 由最终版检查器重跑生成。

## 8. 不主张

- 不主张任何关于正十二面体、二十面体或 Goldberg 族的**几何**命题；这里只数了图上的圈。
- 不主张哈密顿性与**物理哈密顿量**有任何关系；两者同名不同物，本记录不混用。
- 不主张与 `0072` / `0079` / `0081` / `0082` / `0099` 的双曲紧化线有任何联系（见第 7 节第 3 条）。
- 不新增稳定 API、原生类型、库准入或 Seal；不写 `docs/claims.toml`。
- 有限范围仅限：契约声明的两个图、声明的等价关系、声明的规则与控制组。

## 9. 复现

```sh
python3 experiments/dodecahedral_hamiltonicity/checker.py   # 打印并重写 evidence.json
pytest tests/python/test_dodecahedral_hamiltonicity.py -q   # 在临时副本里重跑并比对
```

## 10. 署名

问题与方向：苑明理（2026-09-13）。契约、检查器、运行与本文：deepseek-v4-flash-vision-exp（DeepSeek Harness），经其账号作为授权代理提交；他未审阅、未背书，其姓名不构成对任何内容的证据。此处权威是执行的检查与保留的残余。
