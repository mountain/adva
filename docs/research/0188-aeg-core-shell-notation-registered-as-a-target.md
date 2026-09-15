# 0188 — AEG 核壳记号：作为目标点先行登记

Status: research note, not a claim, not a trial, not a proof. It escorts one
terminology registration — [`docs/terminology/aeg-core-shell-notation-v0.json`](../terminology/aeg-core-shell-notation-v0.json)
— and records why the notation was registered before anything executes. There is
no checker, no evidence file, no frozen contract and no executed run behind this
note. The source discussion is [`苑明理方案提议一.md`](../../苑明理方案提议一.md)
(sha256 `30fde8bd…`), a proposal, not a check.

## 0. 这一步在做什么

苑明理与 Gemini 的讨论提出了一套重构方案（算术表达式几何 + 信息论驱动的区间计算）。
讨论之后他决定：**先登记记号，因为那是我们要去的目标点**；执行放在后面。这份记录把
登记本身、它与既有 home 的关系、以及三处必须写下来的收紧记在案。

这一步**不**做：不实现核壳、不改任何检查器、不引入 Posit、不动原生 Rust、不声称任何精度
或收敛。

## 1. 为什么"缺的机制"值得先有一个名字

起因是清单 `docs/maintenance/FLOAT_APERTURES.md` 的两个结论：开口的本质是**声明与执行之间
的缝隙**；而我们今天只有两种形态——精确（拒绝一切浮点，于是本质数值化的计算做不了）或浮点
（未声明的漂移）。缺的是第三种：**未解决的那部分被携带、而不是被舍入抹平**。

讨论稿把这种形态的记号给了出来。先登记它的理由是：**没有名字，就没有可以声明的切分**；
而有名字之后，"核在哪、壳在哪、方向是什么、何时才允许坍缩"才成为可以写进合同的东西。

## 2. 登记了什么

| 记号 | 名字 | 一句话 | 登记里的 witness |
|---|---|---|---|
| `[]` | closed-core | 在声明的精确域内、不含任何壳项、绝不舍入的那部分 | `TargetOnly` |
| `()` | open-shell | 声明的预算没解决的余项，**被携带**而非被舍入 | `TargetOnly` |
| `<>` | modal-tension | 与残差一同携带的**逼近方向** | `ImportedClassicalExample` |
| `[< >]` | projective-duality | 把比值携带为一对，使求逆成为换位、核内不做标量除法 | `ExecutedExternalFiniteEvidence` |
| `(> <)` | centripetal-balance | 终局：壳空才允许坍缩，否则 `Unknown` 且壳被保留 | `TargetOnly` |
| `1 = (> <) [< >] < [] () >` | unit-specification | 单位元的**规范图**（不是等式） | `TargetOnly` |

六条术语共带 **24 条 `does_not_imply` 边界**。这份文件的 `authority` 明确写着
`native_admission: NotGranted`、`numeric_acceptance_authority: false`、
`diagram_admission: false`、`stable_keywords_added: []`。

## 3. 它标注既有 home，而不是新建 home

这是登记时最要紧的一步，也是我读完原生代码后改变的理解：提案里被当作"新"的几件东西，
**原生侧已经有一半**。

| 提案要素 | 既有 home | 实际内容 |
|---|---|---|
| 射影齐次对 `[N:D]`，求逆=换位 | `crates/adva-witness/src/arithmetic.rs` `MultiplicativeResidualV0` | **精确的 `after / before` 多项式对**（`PolynomialV0`，系数 `BigInt`），`identity()` 就是 `1/1` |
| 残差不得被标量求和抵消 | `crates/adva-witness/src/trace_arithmetic.rs` `ThreeSideAdditiveResidualV0` | 注释原文：不同侧的坐标**永不通过标量求和相互抵消** |
| 拒绝要带类型 | `crates/adva-witness/src/closure_transport.rs` `RejectionResidualV0` | 拒绝本身是一个有类型的残余 |
| 分配律作为可传输的无损边 | 同上，`closure_transport.rs` | 有一个 **frozen distributivity identity**，候选不是它就拒绝 |
| 残差 / 燃料 / 标架 / 作用域 | `docs/terminology/golden-ratio-receipt-v0.json` | receipt 字段已含 `fuel_used / frame / residual / claim_scope`，kind 已含 **`unknown-tail`** 与 **`finite-precision-stop`** |

所以本登记**不**为 residual、fuel、frame、bracket 造第二个 home：它只给这些既有字段补上
"哪一部分是核、哪一部分是壳、方向与对偶怎么记"的**结构名字**。同一份 JSON 里
`related_homes` 列出了这六处，且每个路径都已核对存在。

## 4. 三处符号占用（已作为显式声明登记）

符号冲突在本仓库不是假想风险——语料里的 `ι` 曾有四个含义。登记前查了，查出三处：

1. **`{}[]()` 已有含义**：`docs/SEMANTIC_SCOPE.md` 里，`HoleOpenCloseMachineV0` 把"三个局部三角
   接口"README 为这个 presentation。同一个 `[]` 与 `()`，不同的 home，不得互相替换；孔径那
   一侧保留它自己的 0079 号笔记。
2. **iota-lang 的 `Parser` 接受 `<>`/`()`/`[]`**（记在 0167 的 iota-lang 重连审计里）：那是外部
   基底的语法形式，不是本记号的一种读法。
3. **"bracket" 在 `golden-ratio-receipt-v0.json` 里已是负载词**，专指**已产出值的数值区间**
   （"a seeded bracket may not be reported as tail coverage"）。所以 `()` 壳**不是**数值 bracket；
   如果壳将来变成有界区间，它继承那一套纪律，而不是另立一套。

## 5. 三处收紧（写进 `does_not_imply`，不留在讨论里）

1. **`Expr ≅ [[a,b],[c,d]]` 过宽。** 单变量 Möbius 片段与"单个比值提升为对儿"成立；多子表达的
   一般有理表达式不是 Möbius 映射。诚实的形式就是原生已有的**多项式对**。而且：继续复合要通分，
   **次数会涨**，而讨论稿自己也指出理想在除法下失效——所以射影提升把决策从"舍入"**搬到**
   "声明次数/理想的截断"。这是好得多的位置（代数化、可声明），但**不是免费的午餐**，必须明说。
2. **"上下文残差作为仿射上同调"是仿射算术/Taylor 模型的一阶传播的改述。** `d(1/z) = −dz/z²`
   就是一阶传播律。它真正的新意是 **custody**——残差外挂在标架上、绝不与核混淆——而那恰是原生
   `ThreeSideAdditiveResidualV0` 已强制的事。**不要指望它解决讨论稿自己诊断出的非线性耦合。**
3. **`1 = (> <) [< >] < [] () >` 是规范图，不是等式**；`lim` 那条收敛条件是散文穿了一件极限的
   外衣。有限版本必须写清"燃料耗尽时怎么办"：**耗尽只产出 `Unknown` 并保留壳，绝不允许静默
   收敛**。Posit/Unum 至多是**调度器**，因为本仓库的规矩是启发式永不凌驾于受保护的义务；它
   不能成为任何判定的权威。

## 6. 这一步不成立什么

- 不成立任何精度、界、收敛或正确性；六条术语里五条的 witness 是 `TargetOnly`，
  唯一带 `ExecutedExternalFiniteEvidence` 的那条（`[< >]`）指的是**既有原生实现**，而它
  不含预算也不含壳——正是记号仍然缺的那部分。
- 不成立"原生应当照此改动"。没有原生改动，也没有提出改动。
- 不成立任何测度上的改进：`docs/maintenance/FLOAT_APERTURES.md` 列出的开口**一个都没有被关闭**。
- 不成立对讨论稿其余内容的背书：信息论分辨率、Posit 位分配、对 `1.0` 的对数对称，本登记
  一条都没有采纳为机制，也没有反驳。

## 7. 下一级 rung，与待定的问题

若继续，最小可检验的一步是**在声明的一段表达式语法上实现核/壳**，并让分配律成为**可检验的
恒等式传输**（`a(b+c)` 与 `ab+ac` 必须产出**相等的核与相等的壳**，而不是"在 epsilon 内接近"）——
这一条正好能检验讨论稿诊断的"分母污染"会不会发生、以什么形态被携带。

待定的三件事（登记文件 `residual` 里逐条留存）：

1. 壳的第一形态：**符号未展开式**，还是**有界数值区间**？我倾向先做符号未展开——有界区间一上来
   就把我们要躲开的舍入重新引回来，而且会立刻撞上 `golden-ratio-receipt` 那套既有 bracket 纪律。
2. 核的次数/理想预算与它的截断规则。
3. 终局条件的有限形式，以及"拒绝"是否算作一种壳。

这三件事定了，才有资格谈合同、检查器与证据。

## 8. 出处与署名

方向与决定：苑明理（Mingli Yuan）。讨论稿由 Gemini 参与成形，经他放入本仓库；本步把它
**原样提交**，不改一字，使登记文件里的指针可解析。登记文件、本记录与那份清单
（`FLOAT_APERTURES.md`）由 deepseek-v4-flash-vision-exp（DeepSeek Harness）完成，经他的账号
作为授权代理提交；他未审阅、未背书，其姓名不构成对任何内容的证据。此处权威是文件的字段与
已核对的路径，不是任何人。
