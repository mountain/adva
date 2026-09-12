# trials 迁移记录（migration record）

日期：2026-09-11。执行：deepseek-v4-flash（DeepSeek Harness），经 Mingli Yuan 的
账号代理提交。决策记录见 [ADR 0046](../docs/adr/0046-trials-home-in-adva.md)。

本目录此前是本地 AEG 仓（`/Users/mingli/Adva/AEG`）的一部分。按 M1 方案，它现在
以**保留历史**的方式迁入 adva 主仓，成为试验树的**唯一工作归宿**。

## 迁移方式与逐字节核验

```sh
git clone --no-hardlinks /Users/mingli/Adva/AEG /tmp/aeg-split
cd /tmp/aeg-split && git subtree split -P trials -b trials-only   # 头 71b25ef17a7ac257ddac736f08d488cfafaa0ca7
cd /Users/mingli/Adva/adva && git subtree add --prefix trials /tmp/aeg-split trials-only
```

| 项 | 值 |
|---|---|
| 随迁提交 | **47**（AEG 共 55 个提交，其中 8 个与 trials 无关） |
| 文件数 | **397**（`git ls-tree -r HEAD trials`） |
| 跟踪体积 | 63.64 MiB（工作树 64 MB） |
| 逐条比对 | `git ls-tree -r main trials`（AEG）与 `git ls-tree -r HEAD trials`（adva）**397 条完全相同**：模式、类型、blob 哈希、路径逐条一致 |
| 新增对象 | **522 个**（343 blob + 179 树/提交），压缩后 **52.47 MiB** |

## 迁移时在 AEG 中尚未提交的 6 个文件

它们当时是 untracked，任何基于 git 的导入都会静默漏掉，因此按字节带过来并在此登记
（AEG 里的对应文件至今仍是 untracked）：

| 文件（`bounded-exchange-round-01/`） | SHA-256 |
|---|---|
| `audit-code-05.txt` | `0bdcb56f4bbb3e503fbc0db40022d1768fa7150ea030ab0ee6614911c0d74cc3` |
| `audit-witness-05.json` | `4bb96e31a9ffcdb590c0df33efc4feb8b41b3bc481efbb46b28884f1f244d45c` |
| `comparison-objects-05.json` | `75bc3c1b124bc07d7e0c9658842079e3f0ff897c65ace20600425ca57c99e6c8` |
| `request-05.json` | `b7d908d71edc5ca1338dfd1b54517a6b528f811c05108f618e719c03273e91aa` |
| `response-05.json` | `837e042bace7972c95be81748346eb78de6bc80e54d94fdd8c1e39c5edb8f6ed` |
| `response-template-05.json` | `9da916a3d13e2786baa7d927ba13251288be79cd8fd2034ac0bcacea9b0704c0` |

## 没有随迁的内容（仍在 AEG，且 AEG 至今没有远端）

- `.campaign/`：**41,418 文件 / 57.61 MiB**（与主仓 `docs/research/0162-evidence/`
  很可能大面积重复，尚未去重）；
- `.rust-run100/`（101 文件）、`.breakthrough/`（81）、`.stage-runphase/`（58）、
  `.merge-six*/`、`.stage-*/`、`.graft-*` 等点目录；
- `math/`、`stability/`、`knowledge-boundary/`：adva-library 的**旧副本**（目录同名）；
- 顶层的 `three-repo-split-proposal.md`、`six-repo-design-proposal.md`。

## 一个未处理的耦合：17 个硬编码路径

`trials/` 里有 **17 个文件**把仓库根写成常量，例如：

```python
ROOT = pathlib.Path('/Users/mingli/Adva/AEG')      # receipt-ledger/ledger_check.py
AEG  = pathlib.Path("/Users/mingli/Adva/AEG")      # aeg-tools/project_receipt.py, aeg-feed/build_feed.py
```

凡引用 `ROOT/"trials"/...` 的脚本，只要 `/Users/mingli/Adva/AEG/trials` 仍指向本树，
就能**就地复跑**。计划（尚未执行，见 ADR 0046 的待办）：AEG 退休时让该路径保留为
一个只含 `trials ->` 符号链接的目录，从而**不修改任何试验字节**。其余相对引用为 0，
trials 内的脚本不 import 顶层模块（只依赖标准库）。

## 第三方工件与许可

| 文件 | 体积 | 记录 |
|---|---|---|
| `unrelated-pair-round-01/irs-1040-instructions.pdf` | 4.23 MiB | 美国国税局 1040 填报说明；美国政府作品 |
| `burau-boundary-pair-round-01/2607.05283v1.pdf` | 2.70 MiB | arXiv 预印本 2607.05283；许可按其页面，本条不裁定 |
| `meaning-pair-round-02/pixels/*.png` | ≈ 48 MiB | 该 trial 自产的像素层分析输出 |

未确认的部分如实记为 Unknown，不做推定——与 `resources/our-attitudes/` 里那张
Hilbert 墓石照片同一条纪律。

## 边界

进入本仓**不授予任何语义身份**：trials 仍是 Human 层的试验与收据，不是推导父、
不是检查权威、不产生目录学条目。本次迁移没有改动任何检查器、`math-check`、
`claims.toml` 或试验字节本身。

## 2026-09-12：`aeg/feed-v0` 线的归并（同一 home 的重复副本）

分支 `aeg/feed-v0`（6 个提交，2026-09-10）把 `trials/aeg-feed/` **整体搬到仓库根** `aeg-feed/`
并称之为公开锚点，与主线在 `trials/` 下的继续推进形成了同一产物的两个 home。按其做法，
本目录不再是唯一工作归宿，这与 [ADR 0046](../docs/adr/0046-trials-home-in-adva.md) 相悖。

合并前逐文件核对（这是删除前必须做的安全步骤）：

- 根副本 34 个文件中 **33 个与本目录逐字节相同**；
- 唯一不同的是 `feed.json`：根副本 30 条，本目录 31 条，即**主线更新**；
- **没有任何文件只存在于根副本**；
- 本目录另有 `receipts/receipt-31.json` 与生成器 `build_feed.py`，根副本没有。

因此按其历史并入、结果归一到既有 home：分支的提交进入主线历史，根目录的重复副本删除，
`trials/aeg-feed/` 保持为唯一 home。**没有内容被丢弃**，被删掉的每一个字节都仍然存在于
本目录中。此后若要改变 feed 的位置，应作为一次显式的 home 迁移并同时更新本文件与 ADR，
而不是由一条分支的改名默默完成。
