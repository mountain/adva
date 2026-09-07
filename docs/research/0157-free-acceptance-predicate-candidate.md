# Research 0157：自由接受谓词候选（free acceptance predicate candidate）

日期：2026-09-07。状态：`proposed-document`，候选提案供评审，不是执行报告。
本文不注册任何原生命令、不合成 free、不修改 learn-free-six 合同（其 free
阶段继续为 AdapterUnavailable/NotRun，obstruction 原样保留）。
起草：assistant；评审人：Mingli Yuan。

## 1. 阻塞现状（0139 三缺）

1. 任务相对的自由接受谓词未定义（`free_status=Proposed`）；
2. 原生 CLI 无 free 命令（只有 reveal/trace-arithmetic/frontier/learn/verify）；
3. 无版本化输入/输出适配器（合同 free 阶段 command_template 为 null）。

## 2. 候选谓词 FREE(subject, method, object)（供评审，非实现）

在一个有界任务上判定三件事，全部成立才 `FreeAccepted`：

- **F1 账户终态**：object 的燃料/单位账户到达声明终点，无未决义务；
  保留的 Rejected 残余与 Unknown 原因必须显式列出，不得被"接受"吞掉；
- **F2 前沿闭合**：subject 的 final frontier 满足 method 合同声明的完成
  条件（槽位账户终止、guard 状态可审计、无未消耗的成功封印被拒绝）；
- **F3 人类接受**：任务声明范围的人类接受记录存在（时间/地点/接受不再
  Unknown；对应 pascal-task 的 acceptance.human_task）。

输出 `FreeAccepted / Rejected / Unknown`，附原因与残余。语义判定必须由
原生检查器执行；Python 编排层只传递与记录（0139 边界）。

## 3. 候选命令面与接受记录（不注册）

```
adva free <subject.adva> <method.adva> <object.adva> --output <acceptance.adva>
```

接受记录 schema 候选：`adva.free-acceptance.v0`
{schema, version, task_key, frontier_binding, account_terminal,
human_acceptance, status, reason, residuals}。

## 4. 明确不做

- 不在编排层合成 free；不定义"learn 成功即 free"；
- 不接受空谓词或恒真谓词；F3 的人类接受不能用签名替代
  （签名认证来源，接受是任务语义，0155 三谓词分离）；
- 本候选不解除任何义务、不改变 0139/0156 的既有登记。
