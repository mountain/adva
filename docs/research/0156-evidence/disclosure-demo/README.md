# 披露边界演示（0156 Phase 1，2026-09-07）

状态：研究本地证据；隐藏内容为合成样例 `{"answer": 14}`。

## 流程

1. 记录 `lineage/arithmetic/records/000001.json` 的 `secret_slot` 只含
   Pedersen 承诺（钉住群参数 q/g/h）与 Schnorr NIZK（Fiat-Shamir）——
   隐藏内容与盲因子**从未进入链**，链上可见的只有承诺与证明；
2. `lineage-update` → 锚点 `lineage/anchors/0000.json`；
3. `tamper-check` → `tamper-intact.json`（Intact）；
4. 披露：`verify --kind disclosure` 用 `disclosure-request.json`
   （content + blinding + 承诺 + 证明）→ `disclosure-verified.json`
   （Verified，退出 0）——披露后任何人可直接验证开箱，无需 ZKP；
5. 负控制：`disclosure-bad.json`（content 改为 {"answer": 15}）→
   `disclosure-rejected.json`（Rejected，退出 2）。

## 边界

- 群参数为钉住的 128 位安全素数子群（研究规模，非生产规模）；第二生成元
  离散对数已知（NUMS 派生），已文档化——仅适用于披露边界的承诺方程；
- 承诺证明证明"存在开箱"，不证明内容满足任何语义谓词（Phase 2 谓词
  SNARK 未实现）；
- 全部披露路径为纯标准库（`python -S` 可用），无第三方依赖。
