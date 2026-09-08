# Downward interpretation and Mingli's drop route

Date: 2026-09-08  
Status: external finite research calibration; intended thread duality **Open**.  
Research direction and route: **Mingli Yuan**. Formalization, implementation,
and this handoff: ChatGPT.

## 中文交接

本记录保存明理从 `empty universe`、极性抵消与加法归零，推进到
Substrate / Engineering / Machine、Knowledge / Language、
`(switch swap break)`、Surface / thread / cut / drop 的工作路线。
原始表述及其中的拼写保存在路线笔记中；这里的具体解释与有限模型由
ChatGPT 提出，保留各自的假设、验证范围和未完成项。

这次完成了三个外部校准：下行见证返回；有明确解释配置的接口验收与
drop；以及把 Research 0101 的 thread 分解落实到有限线性收回模型。
它们为路线提供了可复核的构造。真实 thread 的对偶、所需保留的观察，
以及与原生 Adva 载体之间的检查桥仍为 Open。

明理已授权本轮提交并合入主线。本次交接保存已完成工作和开放问题，
无需在本轮补充 thread；未来继续时从下述边界接起。

## What is preserved

Repository inspection and all run contracts were pinned to
`1c5979d78dc9c2b79b633ea492c38fe09090f221`.
The two reports were written before repository publication. Their statements
that no repository file had been modified describe that authoring stage.
This handoff imports those reports and their evidence without retroactively
changing the experimental sources, contracts, or observed outputs.

| Record | Scope | Result |
| --- | --- | --- |
| [Downward interpretation](0158-evidence/downward-interpretation-v0/downward-interpretation-v0.md) | Satisfaction relations, concrete return fibres, indexed obligations, cycle obstruction | 689 relations, 37,477 subset pairs, 10,108 closure checks; all seven F7 targets; five return runs; eight corrupted receipts rejected |
| [Mingli's route](0158-evidence/mingli-drop-route-v0/mingli-drop-route-v0.md) | Supplied interpretation of `(switch swap break)`, checked cut/drop, logic as mathematical data | 11 expected case outcomes; five corrupted receipts rejected; 256 Boolean implication masks checked, 81 valid and 175 invalid |
| [Retraction supplement](0158-evidence/mingli-drop-route-v0/retraction-evidence.json) | Explicit linear realization over F7², with a nonlinear counterexample | All 49 vectors and seven nonlinear inputs checked; thread/dual identification remains Open |

Sources, frozen contracts, complete outputs, SHA-256 manifests, and reproduction
instructions are in [0158-evidence](0158-evidence/README.md). Each calibration
was executed once under its own finite contract. The retraction supplement has
a separate contract and does not rewrite the earlier run. These are finite
implementation checks alongside the reports' mathematical arguments.

## The downward connection

An upper candidate needs an explicit relation back to the original question.
For `y = x²` in F7, solving `2y + 6 = t` does not itself construct an `x`.
At `t = 1`, the return fibre has `x = 1, 6`; at `t = 5`, the upper answer
`y = 3` has an empty return fibre. Empty constraints, an empty fibre, a
discharged obligation, and exhausted fuel therefore remain distinct.

The supplied engineering profile gives the expression `(switch swap break)`
a precise local meaning: inspect the two endpoint positions, swap intact
records when needed, and break the routing loop once aligned. A separate
check tests the offered root against the original request. Only a successful
check permits `drop` to release the live frame; source records, result,
evidence, history, and spent fuel remain in its receipt. Missing interpretation,
missing thread, and insufficient fuel have explicit outcomes. The spelling
alone does not establish a Lisp interpretation or a native Adva operation.

The route also treats a candidate logic as a mathematical object examined by
a fixed checker. This extends the documentary direction in
[ADR 0042](../adr/0042-math-topic-catalog-without-semantic-authority.md).
The proposed logic cannot select a replacement checker that simply accepts it.
Objectifying logic and releasing a checked frame are two concrete readings
along the route; no equivalence between their operators has been established.

## A precise additive connection, with its assumption

[Research 0101](0101-six-port-whole-cut-theory.md) already factors a thread as
`T_ij = g_j r_i`, through a common generative skeleton `B`, with
`r_i g_i = 1_B` supplied at the appropriate witnessed level. In an explicit
external vector-space realization where these are linear maps and equalities,
write `e = gr`. Then

$$
e^2=e,\qquad r(1-e)=r-rgr=0,\qquad x=g(rx)+(1-e)x.
$$

Thus retraction annihilates one component while a retained residual makes
reconstruction possible. The F7² fixture takes `g_0(b)=(b,0)`,
`r_0(x,y)=x`, `g_1(b)=(0,b)`, and `r_1(x,y)=y`.
Its thread `T_01(x,y)=(0,x)` differs from the swap `(y,x)`, and the reverse
thread round trip is the projector `e_0`, not the identity on the whole space.

Additivity is essential to the cancellation equation. A nonlinear split
retraction with `r(x)=x²` on F7 and a chosen section of its image still has
`rg=1` and an idempotent `gr`, but at `x=6` it gives `e(x)=1` and
`r(x-e(x))=4`, not zero. A split pair alone therefore cannot authorize the
linear residual formula. Neither this complement nor the illustrative
receiving interface has been identified with Mingli's intended thread dual.

## Preserved boundary and continuation

| Obligation | Current status |
| --- | --- |
| Actual thread and the relation defining its dual | Open; illustrative roots do not fill this slot |
| Observation and residual that the intended cut/drop must preserve | Open beyond the explicit fixtures |
| Approved additive realization of the intended carrier | Open; the F7² model is externally supplied |
| Native validation, lineage, and transformation certificate | Not issued by these Python experiments |
| Math growth obligation | Existing pinned obligation remains Open; native Seal remains NotIssued |

This publication adds research records and external calibration sources.
Rust semantic authority, the OperationSpec registry, JSON IR, math catalog,
growth pins, and the completed earlier campaign remain unchanged. Native
changes would require their existing design and validation gates. Value
equality, scalar zero, or a successful fixture does not authorize history
erasure, a general duality, endogenous breakthrough, or a physical energy law.

A future continuation can start with a concrete thread/dual pair and one
preservation claim, then declare one finite contract that checks the claimed
pairing and retained observation. Existing failures and costs must remain
visible. The present records stop at their declared outcomes; this handoff
does not restart a search or reset experimental fuel.
