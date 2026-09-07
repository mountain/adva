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
