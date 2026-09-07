# 真实 6 方 merge 排演（0156 机制端到端，2026-09-07）

状态：研究本地证据；合成参与方（P1–P6 非真实人类）；私钥种子**只存在于
AEG 工作区**，本目录仅含公钥记录与签名，符合 Research 0155 第 6.2 节纪律。

## 排演内容（merge-six-run.py 可复现）

1. `key-issue` ×6：六方各签发一把真实 Ed25519 密钥（用途 anchor-signing，
   home=merge-six/Pi；公钥记录 `key-issue-P*.json`）；
2. §14 次序：六方数值均 14.0 → 全残差 0 → tie-break 固定次序
   P1⋈P2 → P3⋈P4 → P5⋈P6 → M1⋈M2 → M3⋈M4，五步全部 Verified；
3. merge 步骤入 lineage 链：五条记录（`order_score`/`order_rank` 记入
   environment，记录 schema v0 暂无专用字段——见 README 末节）；
4. 锚点 + 六方真实签名：锚点 `self_sha256` 上六份 Ed25519 签名
   （`signature-request-P*.json`，含公钥、消息、签名）；
5. 复核：`verify --kind signature` 6/6 Verified；`tamper-check` Intact；
6. 负控制：篡改第 3 条记录 → `tamper-report.json` 定位 seq 3、Tampered。

## 文件清单（公开部分）

- `key-issue-P1..P6.json`：公钥签发记录（无私钥）
- `signature-request-P1..P6.json`：锚点签名请求（可逐一 verify）
- `lineage/`：五条 merge 记录 + 六方签名锚点
- `summary.json` / `tamper-report.json`：排演汇总与负控制报告
- `merge-six-run.py`：复现脚本

## 排演暴露的设计点

1. lineage 记录 schema v0 无 `order_score`/`order_rank` 专用字段——本次
   记入 `environment`；若 §14 需要独立字段，应作为 schema v1 的设计决策；
2. key-issue 目前仅注册 `anchor-signing` 用途域；merge 专属用途域
   （如 `merge-signing`）是待定扩展。

## 追加：真实两侧 merge（merge-two-sides.py）

Rust 侧（`target/debug/adva run arithmetic.adva`，f64 值 14.0）与 Python 侧
（精确整数 2+3*4 = 14）按 §14.4 预言合并：

- 归一化残差 |norm(14.0) − norm(14)| = **0**（§14.4 第二例的实测确认）；
- merge 记录为链上 **seq 6**（环境含两侧证据 sha256、order_score=0、
  order_rank=6，见 `lineage/arithmetic/records/000006.json`）；
- 新锚点 **0001.json**（global_seq 1）链向前锚点 0000；
- 两侧各签一把新密钥（`key-issue-{python,rust}-side.json`），
  `signature-request-{python,rust}-side.json` 复核 2/2 Verified；
- `tamper-check` Intact 且 `prev-anchor chain: True`；
- 两侧证据文件：`rust-side/result.adva`、`python-side/presentation.json`；
- 汇总：`summary-two-sides.json`。

私钥种子（`python-side-seed.key`、`rust-side-seed.key`）仅存于 AEG 工作区。
