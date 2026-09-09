# Research 0162：有界推进循环（bounded advance loop）证据登记

日期：2026-09-08（运行 2026-09-07）。状态：bounded evidence registration。
编号注：已推送为 0162，并被远端 0163（evidence stutter audit）正式引用；0161 为远端留白空号。
循环状态 **Unknown**。循环设计：assistant；运行与授权边界：按 Research 0129
§4 / 0139 纪律。

## 中文说明

`.advance-loop.py`（入仓为 `0162-evidence/driver.py`，字节保留）执行三个
有界周期，每周期 100 遍六槽流水线（learn→run→free，合成后端）。循环自身
不扩权：breakthrough 只来自人类授权标记文件 `AEG/.breakthrough-auth.json`
（`{"authorized_length": N}`）。标记文件不存在 → 三周期耗尽停止，状态
**Unknown**，reason 为 cycle bound。

| 周期 | learn | run | free | 启动数 | 墙钟 |
| --- | --- | --- | --- | ---: | ---: |
| 1 | 100/100 Completed | 100/100 Completed | 100 AdapterUnavailable | 1200 | 36.2 s |
| 2 | 100/100 Completed | 100/100 Completed | 100 AdapterUnavailable | 1200 | 40.2 s |
| 3 | 100/100 Completed | 100/100 Completed | 100 AdapterUnavailable | 1200 | 41.7 s |

全部退出码 0；breakthrough 列表为空；free 阶段无适配器（0157 候选谓词未
批准，0139 阻塞保留）。续跑需人类写入授权标记文件后重跑；本次登记不重启。

## 证据目录

`docs/research/0162-evidence/`：

- `advance-loop-summary.json`：循环汇总（schema adva.bounded-advance-loop.summary.v0）；
- `driver.py`：循环驱动原样保留；
- `archive-cycle1/`：循环启动前归档的上一轮 100 遍输出（基线，非循环周期）；
- `archive-cycle2/`、`archive-cycle3/`：第 1、2 周期输出；
- `final-rounds/`：第 3 周期输出（循环停止时未再归档，连同其 summary.json 原样保留）。

## 边界

合成后端（synthetic child）不等于原生 learn/run；六槽报告槽位不等于六次
成功；不产生新纪元、不改变增长义务、不登记 math catalog 条目（0129 风格
证据）。`archive-run1..5`（早前 100 遍战役归档）仍在本机 AEG：其中 run-01
已入仓为 0153-evidence/run-01，run2..5 的入仓决策待后续合同修订。
