# 未并入 main 的分支清单（inventory of branches not yet in main）

日期：2026-09-12。执行：deepseek-v4-flash-vision-exp（DeepSeek Harness），经 Mingli Yuan
的账号代理提交。工具：[`scripts/unmerged_branch_inventory.py`](../../scripts/unmerged_branch_inventory.py)；
机器可读结果：[`unmerged-branches.json`](unmerged-branches.json)。

## 0. 为什么有这份清单

本仓库的实践是**完成的工作直接落 main**，所以"分支上还压着提交"通常意味着那条线尚未完成、
或约定分开、或**已被别的路径吸收**。三者外观相同，需要判定而不是猜。2026-09-12 的一轮
合并里，正是因为没有这个判定，一条分支搬走同一产物造出的**第二个 home** 差点被并进来；
另一条分支的两条笔记既没进索引也没计数，"干净合并"掩盖了记录漂移。这份清单把判定做成
可重复执行的一步。

## 1. 判定规则（两个独立信号，都打印出来）

1. **补丁等价性**：`git cherry main <branch> <base>`。标记 `-` 表示等价补丁已在 main；
   `+` 表示不在。这能抓到**换了一条路到达**的工作（rebase、重新署名的提交）。
2. **文件状态**：对分支相对 merge-base 改动的每一个文件，主线现在是
   **逐字节相同 / 不同 / 根本没有**。

判定：

| 判定 | 含义 | 依据 |
|---|---|---|
| `absorbed` | 内容已在 main | 无 `+` 补丁，或改动文件在 main 上全部逐字节相同 |
| `superseded` | 只会有"改现有文件"，主线已另有更新的版本 | 有 `+` 补丁，且所有改动文件在 main 上都存在但不同 |
| `unmerged` | 会**新增主线没有的路径** | 有 `+` 补丁，且至少一个改动文件在 main 上不存在 |
| `empty` | 相对 main 没有任何内容改动 | 改动文件为 0 |

`absorbed` **不等于"什么都没发生"**，只是"内容已在 main"；`superseded` **不等于"作废"**，
它说的是"这条线想改的文件，主线已经有一个更新的版本"——差异是否值得并入属于编辑判断。

## 2. 当前结论（59 条未并入 main 的分支）

- `absorbed` **32** 条
- `superseded` **24** 条
- `unmerged` **2** 条
- `empty` **1** 条

### 2.1 确未并入（2 条）——逐条已查

| 分支 | 会新增 | 处置 |
|---|---|---|
| `research/affine-boundary-jet-faithfulness` | `0003-affine-boundary-two-jet-faithfulness.md`、其 claim、扩展的测试 | **已并入**（`25e746d`）：主线 0002 与 0004 之间**恰好空着 0003**，且 claims 里零处提到 two-jet |
| `research/0041-elliptic-isogeny-triadic-characteristics` | `0041-elliptic-isogenies-as-triadic-characteristics.md`、`test_elliptic_isogeny_triadic_characteristics.py` | **未并入，留给作者**：主线已有**同号同题**的 `0041-elliptic-isogeny-triadic-characteristics.md`（447 行）与 `test_elliptic_isogeny_characteristics.py`；分支是另一稿（876 行），两份**仅 64 行重合**，既非子集也非超集。机械合并会造出两条同号同题的笔记 |
| `research/learn-only-six-call-preflight-2026-09-06` | `docs/research/checkpoints/2026-09-06-learn-only-six-call-preflight.md` | **未并入，需一次 home 决定**：主线**没有** `docs/research/checkpoints/` 这个目录；主线同类记录是顶层编号笔记或其证据目录。采用日期式 `checkpoints/` 会引入本仓库尚无的新约定（并会使 README 的"支撑目录"计数 +1） |

### 2.2 空分支（1 条）

`feat/rust-python-kernel-bootstrap`：领先 1 个提交，但相对 main **零文件改动**，即一个不含内容
的合并提交。并入它只会增加一个空合并。

### 2.3 被取代（24 条）

这些分支的 `+` 补丁数不为零，但**没有任何文件是主线所缺的**——它们想改的文件主线都已存在，
只是版本不同或更新。其中体量最大的几条：

| 分支 | 领先 | 未入主线的补丁 | 改动文件 | 相同 | 不同 | 缺失 | 最后提交 |
|---|---:|---:|---:|---:|---:|---:|---|
| `codex/program-process-core` | 2 | 2 | 20 | 1 | 19 | 0 | 2026-08-30 |
| `feature/compiler-graft-trace` | 17 | 17 | 13 | 5 | 8 | 0 | 2026-08-30 |
| `research/expression-coefficient-cut-contraction` | 1 | 1 | 1 | 0 | 1 | 0 | 2026-08-30 |
| `research/whole-cut-program-cell` | 15 | 15 | 6 | 5 | 1 | 0 | 2026-08-30 |
| `research/causal-cut-chirality-cube` | 6 | 6 | 3 | 1 | 2 | 0 | 2026-08-30 |
| `research/e0-dual-cut-surgery` | 5 | 5 | 4 | 1 | 3 | 0 | 2026-08-30 |
| `research/surreal-cut-objectification-no-go` | 4 | 4 | 4 | 2 | 2 | 0 | 2026-08-30 |
| `research/occurrence-affine-cut-lift` | 6 | 6 | 3 | 2 | 1 | 0 | 2026-08-30 |
| `research/three-aspect-scalar-trichotomy` | 7 | 7 | 3 | 2 | 1 | 0 | 2026-08-30 |
| `research/three-aspect-chirality-carrier` | 4 | 4 | 3 | 2 | 1 | 0 | 2026-08-30 |
| `feature/exact-slice-composition` | 4 | 4 | 13 | 2 | 11 | 0 | 2026-08-31 |
| `feature/read-only-program-slices-python` | 2 | 2 | 12 | 2 | 10 | 0 | 2026-08-31 |

（完整 59 行见表尾附录与 JSON。）

## 3. 已吸收（32 条）

这些分支的改动文件在 main 上**逐字节相同**，或根本没有 `+` 补丁：内容已经在 main 里，
不再需要动作。典型是 2026-08-30～09-08 那一批单提交试点线。

## 4. 复现

```sh
python3 scripts/unmerged_branch_inventory.py --json docs/maintenance/unmerged-branches.json
```

## 5. 边界

本清单判定的是**内容是否已在 main**，不是"这条线是否正确、是否值得保留"。它不删除任何分支、
不改写任何历史，也不裁定 `superseded` 那些差异该不该并入。判定依赖 `git cherry` 的补丁等价
与文件字节两级信号；**重命名过的内容可能被判为 `unmerged`**，所以每一条 `unmerged` 都必须
人工看内容再动（本次两条都看过，见 §2.1）。手工重写、格式转换或跨文件搬移过的内容，
两级信号都可能失手，这是本清单已知的残余。

## 附录：全部 59 行

| 分支 | 领先 | 未入主线的补丁 | 改动文件 | 相同 | 不同 | 缺失 | 最后提交 |
|---|---:|---:|---:|---:|---:|---:|---|
| `codex/program-process-core` | 2 | 2 | 20 | 1 | 19 | 0 | 2026-08-30 |
| `feature/compiler-graft-trace` | 17 | 17 | 13 | 5 | 8 | 0 | 2026-08-30 |
| `research/expression-coefficient-cut-contraction` | 1 | 1 | 1 | 0 | 1 | 0 | 2026-08-30 |
| `research/whole-cut-program-cell` | 15 | 15 | 6 | 5 | 1 | 0 | 2026-08-30 |
| `research/causal-cut-chirality-cube` | 6 | 6 | 3 | 1 | 2 | 0 | 2026-08-30 |
| `research/e0-dual-cut-surgery` | 5 | 5 | 4 | 1 | 3 | 0 | 2026-08-30 |
| `research/surreal-cut-objectification-no-go` | 4 | 4 | 4 | 2 | 2 | 0 | 2026-08-30 |
| `research/occurrence-affine-cut-lift` | 6 | 6 | 3 | 2 | 1 | 0 | 2026-08-30 |
| `research/three-aspect-scalar-trichotomy` | 7 | 7 | 3 | 2 | 1 | 0 | 2026-08-30 |
| `research/three-aspect-chirality-carrier` | 4 | 4 | 3 | 2 | 1 | 0 | 2026-08-30 |
| `feature/exact-slice-composition` | 4 | 4 | 13 | 2 | 11 | 0 | 2026-08-31 |
| `feature/read-only-program-slices-python` | 2 | 2 | 12 | 2 | 10 | 0 | 2026-08-31 |
| `feature/exhaustive-independent-slices` | 2 | 2 | 8 | 1 | 7 | 0 | 2026-08-31 |
| `feature/exact-program-slice` | 5 | 5 | 15 | 3 | 12 | 0 | 2026-08-31 |
| `feat/triadic-observer-transition-v0` | 2 | 2 | 14 | 7 | 7 | 0 | 2026-09-01 |
| `research/tnd0-focused-proof-completion` | 9 | 6 | 5 | 4 | 1 | 0 | 2026-09-02 |
| `research/relative-halt-threaded-compactification` | 32 | 32 | 11 | 7 | 4 | 0 | 2026-09-02 |
| `docs/leibniz-open-characteristic-notes` | 9 | 9 | 5 | 3 | 2 | 0 | 2026-09-02 |
| `research/typed-hole-open-close-v0` | 3 | 3 | 10 | 4 | 6 | 0 | 2026-09-02 |
| `research/beta-ledger-transport-subject-reduction` | 5 | 5 | 5 | 1 | 4 | 0 | 2026-09-02 |
| `research/beta-local-confluence-coherence` | 7 | 6 | 6 | 4 | 2 | 0 | 2026-09-02 |
| `research/0095-bootstrap-zero-geometric-threading-syntax` | 30 | 30 | 13 | 12 | 1 | 0 | 2026-09-03 |
| `research/0109-neutral-carrier-mechanism-frontiers` | 6 | 6 | 20 | 6 | 14 | 0 | 2026-09-04 |
| `research/problem-formation-value-seeking-v0` | 25 | 25 | 19 | 13 | 6 | 0 | 2026-09-05 |

| 分支 | 领先 | 未入主线的补丁 | 改动文件 | 相同 | 不同 | 缺失 | 最后提交 |
|---|---:|---:|---:|---:|---:|---:|---|
| `research/occurrence-backward-probe-pairing` | 1 | 0 | 3 | 1 | 2 | 0 | 2026-08-30 |
| `research/parameterized-optical-sensitivity` | 1 | 0 | 3 | 1 | 2 | 0 | 2026-08-30 |
| `research/optical-closure-observer-tower` | 1 | 0 | 3 | 1 | 2 | 0 | 2026-08-30 |
| `research/symbolic-probe-matrix-shadow` | 1 | 0 | 3 | 1 | 2 | 0 | 2026-08-30 |
| `codex/program-slice-handoff` | 1 | 0 | 4 | 0 | 4 | 0 | 2026-08-30 |
| `research/exponential-symbolic-cut-composition` | 1 | 0 | 3 | 1 | 2 | 0 | 2026-08-30 |
| `research/causal-line-six-state-filtrations` | 1 | 0 | 3 | 2 | 1 | 0 | 2026-08-30 |
| `research/expression-valued-backward-transport` | 1 | 0 | 3 | 1 | 2 | 0 | 2026-08-30 |
| `codex/research-engineering-agenda` | 1 | 0 | 5 | 0 | 5 | 0 | 2026-08-30 |
| `research/real-paraxial-optics-first-experiment` | 1 | 0 | 3 | 1 | 2 | 0 | 2026-08-30 |
| `research/symbolic-cut-composition` | 1 | 0 | 3 | 1 | 2 | 0 | 2026-08-30 |
| `research/ssa-intrinsic-compilation-agenda` | 1 | 0 | 1 | 0 | 1 | 0 | 2026-08-30 |
| `research/relational-ordered-two-hole-psp` | 1 | 0 | 6 | 2 | 4 | 0 | 2026-08-31 |
| `research/e0-mobius-cellular-edge-bridge` | 1 | 0 | 6 | 3 | 3 | 0 | 2026-08-31 |
| `research/e0-nested-decorated-surgery` | 1 | 0 | 6 | 1 | 5 | 0 | 2026-08-31 |
| `research/zero-event-scope-cut-incidence` | 1 | 0 | 6 | 2 | 4 | 0 | 2026-08-31 |
| `research/nonzero-ordered-frame-psp` | 1 | 0 | 6 | 2 | 4 | 0 | 2026-08-31 |
| `research/nested-frame-shared-surgery` | 1 | 0 | 6 | 2 | 4 | 0 | 2026-08-31 |
| `research/0033-omega-boundary` | 3 | 3 | 2 | 2 | 0 | 0 | 2026-08-31 |
| `research/checked-boundary-return-feedback-no-go` | 2 | 2 | 2 | 2 | 0 | 0 | 2026-09-01 |
| `research/0071-figure-eight-through-characteristic` | 2 | 2 | 2 | 2 | 0 | 0 | 2026-09-01 |
| `research/0072-pq-unit-tangent-through-geometry` | 2 | 2 | 2 | 2 | 0 | 0 | 2026-09-01 |
| `research/typed-surreal-through-forms` | 1 | 0 | 2 | 2 | 0 | 0 | 2026-09-01 |
| `research/0054-linear-synchronized-evidence-tensor` | 1 | 0 | 3 | 2 | 1 | 0 | 2026-09-01 |
| `research/0067-circular-three-form-interface-duality` | 3 | 3 | 6 | 6 | 0 | 0 | 2026-09-01 |
| `docs/universal-lift-threaded-imagination` | 1 | 0 | 1 | 1 | 0 | 0 | 2026-09-02 |
| `docs/encyclopaedia-demonstrativa` | 1 | 0 | 1 | 1 | 0 | 0 | 2026-09-02 |
| `research/typed-three-domain-threaded-multihole-syntax` | 1 | 0 | 2 | 1 | 1 | 0 | 2026-09-02 |
| `research/distributivity-historical-character-v0` | 1 | 0 | 10 | 6 | 4 | 0 | 2026-09-02 |
| `research/faithful-switch-reverse-observer-20260908` | 1 | 0 | 7 | 6 | 1 | 0 | 2026-09-08 |
| `research/frame-triad-continuation-20260908` | 1 | 0 | 7 | 6 | 1 | 0 | 2026-09-08 |
| `research/mingli-downward-drop-route-20260908` | 1 | 0 | 15 | 15 | 0 | 0 | 2026-09-08 |

| 分支 | 领先 | 未入主线的补丁 | 改动文件 | 相同 | 不同 | 缺失 | 最后提交 |
|---|---:|---:|---:|---:|---:|---:|---|
| `research/0041-elliptic-isogeny-triadic-characteristics` | 2 | 2 | 2 | 0 | 0 | 2 | 2026-09-01 |
| `research/learn-only-six-call-preflight-2026-09-06` | 1 | 1 | 1 | 0 | 0 | 1 | 2026-09-06 |

| 分支 | 领先 | 未入主线的补丁 | 改动文件 | 相同 | 不同 | 缺失 | 最后提交 |
|---|---:|---:|---:|---:|---:|---:|---|
| `feat/rust-python-kernel-bootstrap` | 1 | 0 | 0 | 0 | 0 | 0 | 2026-08-29 |
