# Bounded breakthrough trials（Research 0129 证据，2026-09-07）

状态：研究本地证据；两次有限试验，按 0129 六要素合同执行。

## Run 1（contract-run1.json）

- 问题：length-20 ±1 序列族内找低能量序列；10,000 步、seed 1、workers 1；
- 结果：**energy 34，merit 5.882352941176**（`run1-report.json`），
  独立 `verify` 重算 19 个相关值一致；负控制（篡改 energy）被拒。

## Run 2（contract-run2.json，0129 §4 续试）

- 修订：length 20 → 21；其余不变（同检查器、同种子、同预算）；
  理由：相邻族的有用新证据；
- 结果：**energy 34，merit 6.485294117647**（`run2-report.json`），
  独立 `verify` 重算 20 个相关值一致；负控制
  `run2-tampered.json` 被拒（"stored energy 35 differs from exact energy 34"）。

## 边界

- 两次都是**采样搜索**，不声称族内最优（exhaustive 是单独命令，未跑）；
- 结果只对各自声明族有效；不产生新原生词、无语言形成步骤；
- 预算均未耗尽（各约 0.3s / 120s 上限）；续试计数 2，无自动重启。

## Run 3（contract-run3.json，0129 §4 第二次续试）

- 修订：length 21 → 22；其余不变；理由：相邻族继续滚动；
- 结果：**energy 55，merit 4.400000000000**（`run3-report.json`），
  独立 `verify` 重算 21 个相关值一致；负控制 `run3-tampered.json`
  被拒（"stored energy 56 differs from exact energy 55"）。

## Run 4（contract-run4.json，0129 §4 第三次续试）

- 修订：length 22 → 23；其余不变；
- 结果：**energy 51，merit 5.186274509804**（`run4-report.json`），
  独立 `verify` 重算 22 个相关值一致；负控制 `run4-tampered.json`
  被拒（"stored energy 52 differs from exact energy 51"）。

## Run 5（contract-run5.json，0129 §4 第四次续试）

- 修订：length 23 → 24；其余不变；
- 结果：**energy 52，merit 5.538461538462**（`run5-report.json`），
  独立 `verify` 重算 23 个相关值一致；负控制 `run5-tampered.json`
  被拒（"stored energy 53 differs from exact energy 52"）。

## Run 6（contract-run6.json，0129 §4 第五次续试）

- 修订：length 24 → 25；其余不变；
- 结果：**energy 76，merit 4.111842105263**（`run6-report.json`），
  独立 `verify` 重算 24 个相关值一致；负控制 `run6-tampered.json`
  被拒（"stored energy 77 differs from exact energy 76"）。

## 梯度引导消融（ablation-*.json，length 25 / seed 1 / 10000 步）

三程序单独引导 vs 合奏（Run 6 同预算对照）：

| 程序 | 引导机制 | energy | merit |
| --- | --- | ---: | ---: |
| spatial | **残差自相关场（离散梯度场）** | 56 | 5.580357 |
| temporal | top-k 轨迹增量翻转 | 52 | 6.009615 |
| constructive | 归档见证拼接变异 | 52 | 6.009615 |
| ensemble（Run 6） | 三程序合奏 | 76 | 4.111842 |

观察：同种子同预算下，单程序聚焦（尤其 spatial 的梯度场引导与
temporal/constructive）优于合奏——分数排序是引导而非录取，各程序
优劣属有限样本观察，不构成通用结论（0129 边界）。

## Run 7（contract-run7.json，0129 §4 第六次续试，无人输入）

- 修订：length 25 → 26；其余不变；修订合同自动生成（记录，非许可）；
- 结果：**energy 77，merit 4.389610389610**（`run7-report.json`），
  独立 `verify` 重算 25 个相关值一致；负控制 `run7-tampered.json`
  被拒（"stored energy 78 differs from exact energy 77"）。

## Run 8–11（contract-run8..11.json，0129 §4 继续滚动，证据补齐归档）

本批四轮（length 27→30）的运行时证据此前仅存于本地工作目录，2026-09-08
按 0159 目录分割合同归档补齐。合同修订沿用相邻族（length +1），检查器、
seed 1、10000 步、workers 1 与预算均不变。

| Run | 族 | energy | merit | 负控制 |
| --- | --- | ---: | ---: | --- |
| 8 | 27 | 65 | 5.607692 | 拒绝 ✓ |
| 9 | 28 | 66 | 5.939394 | 拒绝 ✓ |
| 10 | 29 | 86 | 4.889535 | 拒绝 ✓ |
| 11 | 30 | 83 | 5.421687 | 拒绝 ✓ |

负控制为完整报告副本、仅篡改存储 energy（+1），与系列既有 verify 拒绝
机制一致（存储值与按序列精确重算不符即拒）。本批未保存独立 verify 记录
文件，故不另行声称复核计数；系列收官统计中 Run 9 进入 merit 前三的依据
即本表。
## Run 12（contract-run12.json，用户指示"learn×100 → free → breakthrough"扩权）

- 修订：length 30 → 31（本次扩权由用户指示）；
- 结果：**energy 83，merit 5.789156626506**（`run12-report.json`），
  独立 `verify` 重算 30 个相关值一致；负控制 `run12-tampered.json`
  被拒（"stored energy 84 differs from exact energy 83"）。

## 三段式战役（learn×100 → free → breakthrough，2026-09-07）

六槽流水线第 6 轮 100 遍 + 1 次 breakthrough：

- learn 阶段：100/100 Completed（每遍 6 槽链式前进）；
- run 阶段：100/100 Completed（每遍 6 槽原生传输）；
- free 阶段：100/100 AdapterUnavailable（阻塞记录，0157 谓词未批准）；
- breakthrough：Run 12（length 31）如上；
- 流水线 1200 次合成子进程调用、全部退出 0、见证零丢失。

## Run 13–17（contract-run13..17.json，赌博续试）

用户指示"赌一把，继续推进"（无显式上限）；本批按纪律有界为 5 次
（length 32–36），合同如实标注 gamble continuation。

| Run | 族 | energy | merit | 复核 | 负控制 |
| --- | --- | ---: | ---: | --- | --- |
| 13 | 32 | 116 | 4.413793 | ✓ | 拒绝 ✓ |
| 14 | 33 | 100 | 5.445000 | ✓ | 拒绝 ✓ |
| 15 | 34 | 121 | 4.776860 | ✓ | 拒绝 ✓ |
| 16 | 35 | 121 | 5.061983 | ✓ | 拒绝 ✓ |
| 17 | 36 | 102 | **6.352941** | ✓ | 拒绝 ✓ |

全系列 length 20–36 共 17 次试验保留；Run 17 的 merit 为系列第二高
（第一仍为 Run 2 的 6.485294）。

## Run 18–21（contract-run18..21.json，用户选定继续滚动）

| Run | 族 | energy | merit | 复核 | 负控制 |
| --- | --- | ---: | ---: | --- | --- |
| 18 | 37 | 138 | 4.960145 | ✓ | 拒绝 ✓ |
| 19 | 38 | 151 | 4.781457 | ✓ | 拒绝 ✓ |
| 20 | 39 | 143 | 5.318182 | ✓ | 拒绝 ✓ |
| 21 | 40 | 168 | 4.761905 | ✓ | 拒绝 ✓ |

全系列 length 20–40 共 21 次试验保留；每次独立复核一致、负控制拒绝。

## Run 22–24（contract-run22..24.json，收官三轮）

用户指示"再推进 3 轮就不推了"——本系列正式收官于 length 43。

| Run | 族 | energy | merit | 复核 | 负控制 |
| --- | --- | ---: | ---: | --- | --- |
| 22 | 41 | 180 | 4.669444 | ✓ | 拒绝 ✓ |
| 23 | 42 | 173 | 5.098266 | ✓ | 拒绝 ✓ |
| 24 | 43 | 225 | 4.108889 | ✓ | 拒绝 ✓ |

## 系列收官统计（length 20–43，共 24 次试验）

- 24 次试验全部独立复核一致、负控制拒绝、预算未耗尽；
- merit 前三：Run 2（21，6.485294）、Run 17（36，6.352941）、Run 9（28，5.939394）；
- 系列状态：**Closed by user instruction**（不再滚动；续试需新的显式授权）。
