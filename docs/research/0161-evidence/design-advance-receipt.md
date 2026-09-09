# AEG 试验轮 1：advance 收据 + ι/PSC0 关系（0163 的 next minimum step）

日期：2026-09-09。状态：bounded local trial（本地有界试验，非研究证据准入）。
依据：远端 0163 结论——"下一个最小步骤不是再跑 100 遍，而是定义一个
版本化 advance 收据：绑定前驱轮、要求被承认的 delta（问题/资源/观察/
已检查结果四类之一）；用不变输入测一次（必须 EvidenceStutter），用
独立检查过的新资源测一次（可 VariationObserved，但不声称学习）。"
关联：0164（PSC0 与 ι/SKI 基底）、ADR 0043、原始协议 pin/verify。

## 1. 研究线定义（下一步研究线 = 0163 处方 + 0164 桥）

- adva-lisp（crates/adva-lisp，PSC0）：内核有限 Lisp，程序图 + add/copy +
  Real frontier；0164 的 r 用 `(add (add (copy u)) v)` 编码字节。
- iota-lang：独立 Clojure 表达的 ι 组合子（ιx=xSK；SKI 全部可归约为 ι），
  目前只有解析器与定义，无运行闭环。
- 关系候选（本轮的记录，不声称等价）：ι/SKI 是"基底语言"（Substrate），
  PSC0 是"内核载体"（Knowledge 侧格式）；0164 的字节编码式是两者之间
  第一条可检查映射的候选投影源。

## 2. advance 收据 schema（v0，本地试验用）

{
  "schema": "aeg.advance-receipt.research",
  "version": 0,
  "round": N,
  "predecessor_sha256": "<上一轮收据/输入的 sha>",
  "delta": {"kind": "question|resource|observation|result",
            "admitted": true|false,
            "description": "..."},
  "status": "EvidenceStutter|VariationObserved|Rejected|Unknown",
  "evidence": ["<字节证据 pin 列表>"],
  "bounds": {...}
}

判定规则：无被承认 delta 且字节全等 → EvidenceStutter；有被承认 delta
且字节变异 → VariationObserved（不声称学习）；资源耗尽 → Unknown。

## 3. 本轮三个测量（全部本地、有界、可复核）

1. 离线 stutter（observation 类，不变输入）：对 0162 归档相邻轮字节做
   sha 比对——期望 EvidenceStutter；
2. 原生 stutter 复核：`.rust-run100/out-001..100.adva`（同一程序 100 次
   原生运行）sha 比对——期望 EvidenceStutter；
3. 原生变异（resource 类，新资源）：本地 adva 二进制跑两个不同 pinned
   程序（examples/arithmetic.adva vs programs/native-run/arithmetic.adva），
   输出字节比对——期望 VariationObserved（资源 delta 被承认）。

## 4. 边界与非目标

- 合成/原生运行都不构成 learn/free；不产生新纪元、不动目录学；
- 不声称 ι 与 PSC0 等价，只记录候选投影方向；
- 全部证据字节保留于本目录，收据 pin 之。

## 5. 修正记录（第一轮测量后的分类精化）

- 变异必须发生在"声明的语义载波"上；纯计时/元数据字段差异记为
  IncidentalVariation，不构成推进（实测：100 次原生运行只在
  compile/evaluate 等计时字段不同）。
- 资源 delta 被承认的前提：两端程序都由同一二进制独立准入（exit 0）。
- 状态词表：EvidenceStutter / VariationObserved / IncidentalVariation /
  Rejected / Unknown。
