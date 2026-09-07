# Research 0156 Phase 0 实施证据

日期：2026-09-07。状态：`phase-0-evidence`，记录性证据，不是原生准入，
不发原生 Seal，不做任何数学语义判断。

实现位置：`python/adva/lineage.py`（纯标准库核心）+ `python/adva/adva.py`
新增 `lineage-update` / `tamper-check` / `verify` / `key-issue` 四个命令；
验收测试 `tests/python/test_lineage.py`（19 项，2026-09-07 全部通过，
含篡改定位、预算耗尽、锚点链、CLI 退出码控制）。

## 演示数据（合成示例，不是原生 witness 内容）

`demo/lineage/arithmetic/records/` 三条演示性算术发现记录，形态引用实际材料：

| 记录 | 内容 | 判定 |
| --- | --- | --- |
| 000001 | k27 风格：mul(x, y) == const(1)，Q 上精确有理数 | Rejected（残差 -1/18014398509481984） |
| 000002 | prime-universe 风格：2*3*5+1 == 31 | Verified |
| 000003 | 篡改控制（平移 y） | Rejected（残差 1） |

## 实际 CLI 运行（报告在 `reports/`）

| 命令 | 报告 | 状态 | 退出码 |
| --- | --- | --- | ---: |
| lineage-update（构建检查点与锚点） | update-report.json | CheckpointBuilt | 0 |
| tamper-check（干净状态） | tamper-intact.json | Intact | 0 |
| tamper-check（篡改仿真，改记录 2 一个字节） | tamper-tampered.json | Tampered（定位 seq 2） | 2 |
| tamper-check（锚点缺失） | tamper-missing-anchor.json | Unknown（保留原因） | 3 |
| verify --kind inclusion（合法路径） | inclusion-verified.json | Verified | 0 |
| verify --kind inclusion（伪造摘要） | inclusion-rejected.json | Rejected | 2 |
| verify --kind signature（可选后端存在） | signature-verified.json | Verified | 0 |
| verify --kind signature（纯标准库 `python -S`） | signature-unknown-stdlib.json | Unknown（后端缺失，不降级） | 3 |
| key-issue（anchor-signing，后端存在） | key-issue-issued.json | Issued | 0 |
| key-issue（未声明用途域） | key-issue-blocked.json | Blocked | 2 |

`tampered/` 是篡改仿真后的完整副本；`key-issue-record.json` 只含公钥记录，
私钥种子只写入过 /tmp 并已删除（Research 0155 第 6.2 节纪律）。

## 边界

- 本实现只做**文档性完整性**（字节、链、检查点、锚点）；记录通过形状校验
  不等于命题被检查为真，`native_admission` 不适用；
- Phase 1–3（披露边界 NIZK、谓词 SNARK、IVC）未实现，`secret_slot` 必须缺席；
- Ed25519 仅在可选 `cryptography` 包可导入时可用；缺失时报告 Unknown 并保留
  原因，绝不降级为"只查哈希"；
- 锚点仍是信任根：攻破全部锚点副本的边界见提案 5.4 节。

## 复现

```sh
python3 python/adva/adva.py lineage-update --root docs/research/0156-evidence/demo \
    --package arithmetic --global-seq 0 \
    --anchor-out docs/research/0156-evidence/demo/lineage/anchors/0000.json
python3 python/adva/adva.py tamper-check --root docs/research/0156-evidence/demo \
    --anchor docs/research/0156-evidence/demo/lineage/anchors/0000.json
python3 -m pytest tests/python/test_lineage.py -q
```
