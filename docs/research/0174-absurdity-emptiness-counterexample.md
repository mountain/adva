# 0174 — 物理上下界不能清空 Absurdity：一条待带入学习的反例

Status: research note, not a claim, not a trial, and not a proof. It records one
instruction from the direction verbatim, reconstructs the operation that
instruction proposes, and records why that operation cannot be executed as
stated. There is no checker, no evidence file, no executed run and no frozen
contract behind this note; nothing here asserts a physical fact, a bound, or an
epistemic emptiness as a repository claim.

The companion documentary registration on the library side is
[`adva-library/knowledge-boundary/absurdity-emptiness-counterexample-v0.adva`](../../adva-library/knowledge-boundary/absurdity-emptiness-counterexample-v0.adva)
(catalog key `logic-absurdity-emptiness-counterexample`, home `logic`). The two
files have one home each and do not copy each other: this note is the research
record, that document is the knowledge-boundary registration.

## 0. 这份记录做什么

明理要求在 adva 主线和 adva-library 同时登记一项操作，**作为以后的反例带入学习**。
这份记录做四件事：

1. 把指令**逐字**引入，用字不改；
2. 把「Abserdity 为空」这句话拆成三个不同的词，因为它是三个东西共用一个拼写；
3. 把被提议的操作重构成一个形状，并先写出它的**最强形式**；
4. 逐条记下它为什么现在不能执行，以及它怎样才能变成一次**合法的有界学习**。

第 3、4 节的关系是这份记录的要点：**这不是一个被驳回的命题，而是一个以后应当被一眼认出的形状。** 它要学的不是"物理不能说清空 Absurdity"，而是"用哪一种推理会以为说清了"。

## 1. 指令原文（逐字，用字不改）

> 目前国际最为公认的单位制、对应的物理常数和测量关系与理论，我们对宇宙各种时间、空间、物质组织形态范围的上限与下限估计，来做归谬学习，直到证明 adva 主线 Abserdity 为空。

出处：苑明理，2026-09-13，要求同时登记于 adva 主线与 adva-library。

原文用字为「**Abserdity**」，本记录按原样保留，不作拼写更正。本记录把它读作 ADR 0028 与
[`crates/adva-witness/src/closure_transport.rs`](../../crates/adva-witness/src/closure_transport.rs)
中保留的认知类 `Absurdity`——这是**一种读法**，不是对原文的改写，也不是对作者意图的断言。

## 2. 先分开三个同形的词

`absurdity` 在本仓库的记录里至少有三个不同的用法。混用它们，是这条反例的第一个入口。

| 用法 | 出处 | 承载 | 能否成为一个精确命题 |
| --- | --- | --- | --- |
| 保留的认知类 `Absurdity` | ADR 0028；`closure_transport.rs`；Research 0118 | 同一类型、同一 scope、同一 verifier 版本下，一个 claim **与它的否定**同时被验证 | 可以 |
| 猜想刚性意义上的「荒谬」 | Research 0172 §5 | 一句审美与修辞判断（`z = i − e` 没有可调的余地） | 不可以；它是散文 |
| 叙事见证意义上的「荒谬」 | `programs/bootstrap-0/second-absurdity-witness.adva`、`third-absurdity-euler-cut-witness.adva`；Research 0005 / 0006 | 一个故事结构，用于见证人类反复出现的荒谬 | 不可以；它不对应任何检查 |

「Abserdity 为空」只有**第一种**读法可以写成一个精确命题。本记录以第一种为主，另外两种作为**保留残余**登记：它们仍然存在，仍然可被引用，且随时可能被误当成同一个东西——Research 0118 已经写明区分它们的理由（"A single counterexample only separates one universal identity candidate"），ADR 0028 也写明 `absurdity` 只能由一个"在同一 scope、同一解释、同一 verifier 版本下同时验证一个 claim 及其否定"的未来方法引入。

## 3. 被提议的操作，与它的最强形式

### 3.1 操作的四步

1. 采用国际最为公认的单位制与其定义常数（BIPM《SI 手册》第 9 版，2019 修订），以及由它导出的测量关系与理论（相对论、量子力学、标准宇宙学）；
2. 取我们对时间、空间、物质组织形态范围的**上限与下限估计**；
3. 在这些范围之内做**归谬学习**；
4. 终止条件：**直到证明 Absurdity 为空**。

### 3.2 输入的形状（外部参考，本仓库未复核）

下表只说明"被提议操作的输入长什么样"。**每一行都是外部参考，不是本仓库的 claim**；本记录没有复核任何一位数字，也没有 pin 任何一份外部文档。任何一位数字有误都不改变第 4 节的结论，因为第 4 节针对的是**这些量能承担什么角色**，而不是它们的取值。

| 输入 | 值 / 量级 | 性质 | 本仓库是否复核 |
| --- | --- | --- | --- |
| 七个定义常数（s, m, kg, A, K, mol, cd） | ΔνCs = 9 192 631 770 Hz；c = 299 792 458 m/s；h = 6.626 070 15 × 10⁻³⁴ J·s；e = 1.602 176 634 × 10⁻¹⁹ C；k = 1.380 649 × 10⁻²³ J/K；N_A = 6.022 140 76 × 10²³ mol⁻¹；K_cd = 683 lm/W | 定义：精确、无不确定度 | 否 |
| 牛顿常数 G | 6.674 30(15) × 10⁻¹¹ m³ kg⁻¹ s⁻² | CODATA 推荐值：有不确定度，非定义 | 否 |
| 普朗克时间 t_P | 5.391 247(60) × 10⁻⁴⁴ s | 由 ħ, G, c 组合而成，不是测量结果 | 否 |
| 普朗克长度 l_P | 1.616 255(18) × 10⁻³⁵ m | 同上；该尺度以下理论框架自身失效 | 否 |
| 宇宙年龄 | 13.797(23) Gyr ≈ 4.35 × 10¹⁷ s | Planck 2018，ΛCDM 拟合 | 否 |
| 粒子视界共动半径 | ≈ 46.5 Gly ≈ 4.4 × 10²⁶ m | 观测 + ΛCDM；是"可观测"而不是"整体" | 否 |
| 哈勃半径 c/H₀ | ≈ 1.3 × 10²⁶ m | 依赖 H₀ 的测量分歧 | 否 |
| 加速膨胀下的事件视界 | 可达区域有限 | ΛCDM；"能到的"与"存在的"不同 | 否 |
| 质子寿命下界 | ≳ 10³⁴ yr 量级 | 一个**下界**（Super-Kamiokande，p → e⁺π⁰） | 否 |
| 不确定关系 | Δx Δp ≥ ħ/2；ΔE Δt ≥ ħ/2 | 理论（量子力学的公理化内容） | 否 |
| 全宇宙信息量与运算次数 | ≲ 10⁹⁰ bit、≲ 10¹²⁰ 次基本运算；Bekenstein–Hawking / 全息界 S ≲ A/(4 l_P²) ~ 10¹²² k_B | 量级估计（Lloyd 2002 一类） | 否 |
| 普通物质粒子数 | ~10⁸⁰ | 量级估计（重子数） | 否 |

### 3.3 最强形式（steelman）

一条反例记录必须先写出对手最强的形式，否则驳倒的只是稻草人。把第 3.1 节展开到最强：

> 如果宇宙的总信息量与总运算次数有限（上表最后几行），那么任何物理上可实现的观察者所能提出的 claim 总数也有限；于是"归谬学习"在原则上**可以被穷尽**；穷尽之后，如果没有任何同一 scope 的 claim + 否定对被验证，那么 `Absurdity` 类就是空的。因此，"Absurdity 为空"不是信念，而是一个**有限穷尽的结论**。

第 4 节针对的就是这个形式。

## 4. 反例的形状：八条

**D1 — scope 被替换。** `Absurdity` 的成员资格是"在一个**声明的** scope、解释与 verifier 版本下，一个 claim 及其否定同时被验证"（ADR 0028）。物理宇宙不是这样一个 scope：它没有声明、没有 verifier 版本、也没有被冻结的解释。用物理范围去限制一个由声明定义的类，是把**被量化的域**换掉了，而不是把它限制得更紧。

**D2 — 单位不匹配最多只能到 `incommensurate`。** ADR 0028 的表里，`incommensurate` 的判据是"类型化单位不匹配；真与假都不断言"。SI 量、测量关系与宇宙学估计进入本仓库时正是这种身份；Research 0118 已经用两个实例记录过同样的拒绝（多项式证书提交给 M6 ordered-holonomy 与 shared-truth 单位 → 两次类型化拒绝，两个 target hole 保留）。**物理材料连 `separation` 都到不了**，更不必说 `absurdity`；它最多是一份被声明为不匹配的导入。

**D3 — 有限枚举推不出全称否定。** "Absurdity 为空"是关于**一切**声明 scope、解释与 verifier 版本的全称命题，而其中后两者是**开放未来**的对象：每个新 note、新版本都可以引入新的 scope。AGENTS.md 的规则是"搜索穷尽产生 `Unknown`，绝不是不存在的证明"。物理上界可以限制**这个宇宙已经发生的**运算次数，限制不了"某方法下不可验证"这件事的类成员资格。

**D4 — 经验估计是模型依赖的偶然事实，不能当归谬的必要前提。** 13.797 Gyr 是 ΛCDM 拟合的结果并带有不确定度；t_P 以下理论框架自身失效；H₀ 至今有测量分歧。归谬需要**必然**前提，而这里的前提是"目前最好的估计"。用偶然事实做归谬前提，得到的不是矛盾，而是"当前模型下看起来如此"。

**D5 — 上下界本身是观察者相对的。** 视界、光锥、可达区域都是"相对于某个观察者的过去"而言的；而本仓库的 `Probe`、`ObservationPolicy`、`TypedFrontier` 是**语义对象**，不是物理视界。把物理视界当作本仓库的观察者孔径，是一种 forbidden conflation（把两类不同的东西认成同一个）。

**D6 — 推理方向被反转。** AGENTS.md：Rust 是类型、项、图、来源、发生、历史、单元、观察者、演算与证书的唯一权威；外部材料不创造、也不识别语义身份。`docs/SEMANTIC_SCOPE.md` 明确把"曲率、质量、时空的物理解释"排在稳定 API 之外。从物理事实推出认知类为空，等于让外部学科成为本仓库语义的权威——这正好是被禁止的方向。

**D7 — 终止条件没有有限停点。** "直到证明……为空"没有数值化的资源边界、没有停点、没有残余。Research 0129 §3.6 要求试验在启动前写死搜索量、耗时、内存、保留产物大小与续跑次数的上界，并说明每个上界如何被强制执行；§3.5 要求检查器与负控制先于搜索冻结。本操作一项都没有，且它的"直到"是无限的，因此它不是一次有界试验，而是一个不会停的过程。

**D8 — "当前方法不发射"被换成了"该类为空"。** `closure_transport.rs` 的注释写明：`Absurdity` 保留给未来的同 scope 矛盾证明，**并且被第一版方法有意地永不发射**。"版本零从不发射 `Absurdity`"是关于一个冻结实现的事实，已经记录在案；"`Absurdity` 为空"是关于所有方法的命题。把前者读成后者，是这条反例最容易被重演的一次偷换。

## 5. 识别清单（这就是"带入学习"的用法）

以后任何一次学习，如果出现下列任一形状，就应当认出它是这条反例的重演：

1. 用一个外部学科的**全域估计**去关闭本仓库的一个**认知类**（D1、D6）；
2. 把模型依赖的、带不确定度的**估计**当作归谬的**必然前提**（D4）；
3. 把"没找到"当作"不存在"，把穷尽当作 `Unknown` 之外的结论（D3）；
4. 用一个没有数值边界、没有停点、没有残余的**无限过程**当作证明手段（D7）；
5. 把"当前实现不发射 X"当作"X 为空"（D8）；
6. 同一个拼写被当成同一个东西（§2；这是 D1 的入口）。

## 6. 它怎样才能变成一次合法的有界学习

如果以后确实要做这件事，按 Research 0129 §3 的六项写契约，并且至少要做下面这些替换：

1. **把"宇宙范围"换成声明的有限 scope**：一族有限的、精确的候选 claim 与它们的否定，连同被冻结的解释与 verifier 版本；
2. **物理量只作为声明的外部假设进入**，逐条标明来源、版本、不确定度与引入理由，并在记录里保持 `incommensurate` 身份——它可以是前提，但不能是一次"关闭"；
3. **终止条件必须是有限的**：要么找到一个真正的同 scope claim + 否定对（此时 `Absurdity` **有实例**，不是空），要么耗尽并报 `Unknown`，并保留残余；
4. **检查器与负控制先冻结**：负控制必须能把一个"什么都判为空"的检查器暴露出来（Research 0173 §3 的坐标镜面控制就是这种形状的例子：判据不把一个有限的群判成无穷）；
5. **结论只对声明的有限 scope 有效**，不能上升为对类的全称结论；
6. **不自动续燃料、不自动放宽范围**；续跑需要新的有限契约。

还有一条更小、更可能真正推进问题的方向可以直接说：让 `Absurdity` 从"永不发射"变成"有实例"或"有不可能性证明"的唯一入口，是在**已有**的 `ClosureFindingClassV0` 上找一对真正的同 scope claim + 否定，而不是去丈量宇宙。本记录不执行这件事，也不声称它一定能做成。

## 7. 这份记录不主张什么

- **不主张 `Absurdity` 为空**。那是被提议的结论；本记录没有给出它的证明，也没有给出任何检查。
- **同样不主张 `Absurdity` 非空**。本记录没有给出任何 claim + 否定对。"没找到"不是"不存在"，这正是 D3。
- **不主张任何物理数值是本仓库的 claim**。§3.2 的每一行都是外部参考，未经本仓库复核、未经 pin、未经检查。
- **不发起任何试验**。按 Research 0129，试验需要先写出六项冻结契约；本记录没有写，也不代替它。Research 0129 §1 已经记录过一件同类的事：过早引入物理解释没有解决当时的问题。
- **不改写原文用字**，也不替作者认领任何哲学读法。
- **与 `docs/claims.toml` 中任何既有 claim 无依赖关系**；无原生 witness、无库准入、无 Seal、无 release。

## 8. 出处与署名

第 1 节的指令原文作者为苑明理（Mingli Yuan），2026-09-13 口述并要求同时登记于 adva 主线与 adva-library；著作权归其本人，逐字引用，用字不改。本记录的整理、词义区分、最强形式的重构与第 4–6 节的判断，以及 adva-library 一侧的登记文件，由 deepseek-v4-flash-vision-exp（DeepSeek Harness）完成，经其账号作为授权代理提交；他未审阅、未背书，其姓名不构成对任何内容的证据。此处权威是执行的检查与保留的残余——而本记录没有执行检查，所以它只登记形状，不登记结论。
