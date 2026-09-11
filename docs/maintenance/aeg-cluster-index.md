# AEG 集群索引（`~/AEG`）

日期：2026-09-11。维护：deepseek-v4-flash（DeepSeek Harness），经 Mingli Yuan 的
账号代理。**同一份索引同时存放在两处**——工作现场的 `~/AEG/README.md` 与主仓的
本文件；上一轮的教训正是"地图只存在于一个即将退休的仓里"，所以不再只放一处。

## 1. 这个目录是什么

`~/AEG` 是 **Human 层（Surface）的工作现场**：算术表达式几何（AEG）及其相关研究、
论文、实验与模型训练的本地项目簇。规模 **7.7 GB / 30 个条目 / 23 个 git 仓**。

它接替了 `/Users/mingli/Adva/AEG`（那个仓已在本日备份到
`git@github.com:mountain/adva-aeg.git`，其试验树已迁入 `adva/trials`）。
这次接替是六仓设计提案**决策点 5** 的答案。

## 2. 与 adva / adva-library 的分工（一句话规则）

| 角色 | 在哪里 |
|---|---|
| 工作现场：跑试验、开新线 | `~/AEG`（这里） |
| 记录归宿：试验树、收据账本、feed | `adva/trials`（ADR 0046） |
| 知识准入 | `adva-library`（目录学 + math-check） |

结果从现场回到记录，走三仓公理 2「跨仓即引用」：**字节 pin 的收据 / 证据登记**；
成为知识则另走 `adva-library` 的目录学准入。**不要让新线在这里长出第二套 ledger/feed**，
那会把刚完成的迁移重新拆开。

## 3. 项目清单（实测）

构成：**23 个 git 仓**（下表全部）、**4 个非 git 目录**（见 §5）。体积为 `du -sh`。

| 项目 | 体积 | 最后提交 | 分支 / 远端 | 未提交 | 最近在做什么 |
|---|---|---|---|---|---|
| aeg-lm | 1.8G | 2026-08-20 | `autoresearch/r0-information-computation` / ✓ | 0 | R0-long 训练动态、240M 验证检查点 |
| optaeg | 995M | 2025-11-21 | main / ✓ | **28** | OptAEGV5、MNIST 层初始化重构 |
| aeg-ad | 896M | 2026-03-02 | main / ✓ | 5 | 几何优化器、FashionMNIST、benchmark |
| cayley | 804M | 2025-07-21 | main / ✓ | **28** | Poincaré 圆盘可视化与赋值函数 |
| gru | 622M | — | **非 git** | — | 见 §5 |
| gassim | 609M | 2025-09-06 | main / ✓ | 0 | GasSim 硬球气体仿真 v0.0.6 |
| autoresearch-macos | 605M | 2026-03-07 | master / ✓ | 1 | macOS MPS 超参调优 |
| brain | 477M | **无任何提交** | 分离 HEAD / **无远端** | **15** | 见 §4，最易丢 |
| aeg-gas-calc | 237M | 2025-09-07 | main / ✓ | 5 | experiment 001 |
| topological-flow | 211M | 2025-11-21 | main / ✓ | 6 | Topological Flow Solver |
| moc | 154M | — | **非 git** | — | 见 §5 |
| three-body | 185M | 2026-08-17 | main / ✓ | 0 | 三体过程分析：新分析语言的多基准压力测试 |
| aeg-invitation | 91M | 2025-12-11 | main / ✓ | 5 | 《An invitation to arithmetic expression geometry》(LaTeX) |
| dags | 67M | — | **非 git** | — | 见 §5 |
| aeg-paper | 39M | 2026-08-16 | main / ✓ | 4 | 《Arithmetic Expression Geometry》论文 |
| process-geometry | 30M | 2026-08-27 | main / ✓ | 0 | Process Geometry（adva 的 AGENTS.md 把它列为理论与回归判据来源） |
| aeg-lean | 27M | 2023-08-09 | main / ✓ | 3 | 算术表达式的 threadlike 定义 |
| autoresearch2 | 2.4M | 2026-03-10 | master / ✓ | **34** | 训练分片守卫 |
| aeg-topological-order | 2.6M | 2026-08-22 | main / ✓ | 0 | R(2,2) 定理闭合审计 |
| knottingham | 1.8M | 2025-10-30 | main / ✓ | 1 | 固定 wheel 版本、SVG 导出 |
| aeg-shakespeare | 1.7M | 2026-08-22 | main / ✓ | 0 | Release 0.0.2、语义核心拆分 |
| knot-alexander | 1.5M | 2025-11-20 | main / ✓ | 12 | Borromean 环与挠结构分析 |
| pcrg-paper | 1.2M | 2026-06-22 | main / ✓ | 1 | 有限域二值化的认知群解读 |
| aeg-multiplication | 1.1M | 2026-08-19 | `agent/bootstrap-representation-search` / ✓ | 0 | 预注册与 append-only errata |
| math-notes | 408K | 2025-06-01 | main / ✓ | 5 | 数学笔记 |
| thermal | 204K | — | **非 git** | — | 见 §5 |
| lorenz | 136K | 2025-08-28 | main / ✓ | 0 | 初提交 |

顶层还有几份散落文件：`aeg-paper.zip`（28.7 MB）、`doctor.pdf`、
`pendulum-am-canonicalization-and-observable-quotient.md`、
`pendulum-am-representation-demo.html`、`一些微分方程求解方法的缘分-卢燚.pptx`。

## 4. 风险项（未备份或未纳管）

1. **`brain`**：477 MB，git 已初始化但**没有任何提交**，分离 HEAD，15 处未提交，
   **无远端** → 这是整个集群里最容易丢的一块。
2. **未提交较多**：`autoresearch2` 34、`cayley` 28、`optaeg` 28、`knot-alexander` 12、
   `topological-flow` 6、`aeg-ad`/`aeg-gas-calc`/`aeg-invitation`/`math-notes` 各 5、
   `aeg-paper` 4、`aeg-lean` 3。
3. 远端状态：除 `brain` 外，其余 git 仓都有 `origin` ✓（已核）。

## 5. 四个非 git 目录

`dags`（67M，含 `generate_hierarchy_catalog.py`、`build_h.sh`）、
`gru`（622M，含 `lorenz.py`、`pyproject.toml`）、
`moc`（154M，含 `main.py`、`pyproject.toml`）、
`thermal`（204K，HTML 页面 + `pyproject.toml`）。
它们**不在任何版本控制之下**；若其中有什么要保留，应各自 `git init` 或并入相邻仓。

## 6. 与本次交接相关的文件

- `_adva-bridge/three-repo-split-proposal.md`、`_adva-bridge/six-repo-design-proposal.md`
  ——2026-09-08 两份提案的**副本**（原件仍在 `Adva/AEG`，其仓已备份到
  `mountain/adva-aeg`；退休步骤执行后原件随该仓归档）。
- 决策记录：`adva/docs/adr/0046-trials-home-in-adva.md`。
- 已退休仓的备份：`git@github.com:mountain/adva-aeg.git`（private，首次推送 tip `dc639c6`，
  56 提交 / 9,922 对象 / 58.57 MiB）。

## 7. 待办

1. `brain` 补远端（或先建立首个提交），四个非 git 目录决定去留（§4、§5）。
2. `/Users/mingli/Adva/AEG` 的退休：目录旁移 + 在原路径留一个只含
   `trials -> /Users/mingli/Adva/adva/trials` 的 stub，使 17 个硬编码根路径的试验脚本
   继续可跑，**不动任何试验字节**。
3. 两份提案在退休后的归属：其历史留在 `mountain/adva-aeg`；本目录的副本是工作地图。
