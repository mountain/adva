# PR #232 双图接收合同独立审查

审查日：2026-11-10（北京时间）  
审查者：Codex（OpenAI）。这是一次重新读取源文件的独立审查，不代表独立团队、不同模型、形式化证明或明理本人的技术背书。  
固定对象：`mountain/adva@2d5b6c18a7446d4f0aa3834c521cd7ad57a600a8`。读取时 PR #232 为 Open / Draft，head 正是该提交。

**结论：保留 `PassedFiniteStructuralContractReview`，但应修订 C 的定义及 A–D 的绑定规则，才能把它当作明确的目标接收合同。** 这不是一个已经实现的接收器误收漏洞；当前材料没有执行真实接收。主要缺口在于：有序端点对、两侧分别存在、某个具名跨图关系成立，是三个不同层次的陈述。v0 没有明确选择最后两者中的哪一种。

## 1. 审查范围与证据等级

本轮读取 11 月 9 日合同、检查器、测试、执行合同和结果记录；只读查看历史 A–D 定义、11 月 2 日后继实现与 native `OccurrencePath` 类型以校准含义。未读取 `canonical-request-20261031.json`，未读取实际 diagram 字节，未重跑 430 条引用清点、原生 helper 测试或历史 13 项套件，未调用原生接收器，未向 GitHub 写入内容。

| 层次 | 本轮确立的内容 | 不得外推为 |
| --- | --- | --- |
| 源码事实 | v0 检查左右声明副本的自洽；比较说明仅作字符串检查 | 实际端点存在、diagram 合法或关系成立 |
| 直接推导 | 全元组左右相等不适合规范案例，因为 role 已不同 | 跨图关系不可能存在 |
| 有限执行 | 原检查器接受规范文档和 6 个同步改写变体 | 原检查器发生原生误收 |
| 有限数学模型 | 16 个具名案例区分定位、数值关系、指定关系、证据缺失和记录失败 | 真实 Adva 语义或 Rust 认证 |
| 接口建议 | `adapter-obligation-v1-proposed.json` 明确同侧绑定与跨侧判定 | 已实现、已编译或原生验证通过 |

历史结果和历史来源文件保持原样；本审查不升级 0090、0092、M6、`free`、`Close` 或算术普遍性主张。

## 2. 发现一：完整元组相等、同侧声明相等与关系成立被同一句话遮蔽

v0 的 `comparison` 写为 `exact tuple equality after each independent native admission`。检查器实际执行：

```text
relation.left  == expected_selector(ordered_diagrams[0])
relation.right == expected_selector(ordered_diagrams[1])
```

`expected_selector` 只从同一份输入 JSON 中复制字段。它没有导入任何图，没有从 native occurrence 表读取实际端点，也没有求值某个关系谓词。随后代码只检查 `comparison` 是否等于规定字符串。

至少有三种读法，必须选择并命名：

1. **左右完整元组相等**：规范案例必不成立，因为 `left != right`；其 digest、source、occurrence 和 path 也不同。
2. **每侧实际端点与请求中该侧预期元组相等**：这是正确而必要的绑定检查；必须从实际导入结果取出实际端点。当前 Python 检查只覆盖其“声明副本一致”的弱版本。
3. **两个正确绑定的端点满足具名关系 R**：需要单独定义 R、参数、量词、适用域和证据；不能由前两步自动得到。

修订中使用以下两个不同判断：

\[
\operatorname{Bind}_s:\quad
\operatorname{ActualTuple}(\widehat D_s,o_s)=\operatorname{ExpectedTuple}_s(r),
\qquad s\in\{L,R\},
\]

\[
\operatorname{Rel}:\quad
R_{\rho,\Gamma}(\widehat D_L,o_L,\widehat D_R,o_R;w).
\]

这里 `r` 为独立固定的请求，`D̂_s` 为原生检查后的图，`ρ` 为固定关系规则，`Γ` 为保留的前提，`w` 为该规则需要的证据。`Bind_L` 与 `Bind_R` 不是 `R` 的证明。

**历史证据没有承诺更强的 R。** 11 月 2 日后继实现固定两个不同的期望元组，分别检查它们是否存在于 source/residual 的 occurrence 集合中。它没有检验一般的值等价、过程等价、运输定律或 M6。因此，不能因为本次提出更强的需求，就把旧后继判为“未通过自己已经承诺的强语义”。

若目标仅是复现这个旧结果，精确定义 `PinnedPairMembershipV1` 即可；其结论只能是“指定端点分别定位成功”。若目标是 source-to-residual transport 或另一种关系，则应选择 `CertifiedRelationV1` 并提供相应 checker。当前无法仅凭 v0 推断调用者要求哪一种，修订稿保留 `selected_relation: null` 和 `Unknown/TargetRelationUnderspecified`。

## 3. 发现二：身份须完整限定，不能靠删字段恢复跨图相等

| 字段 | 同侧绑定要求 | 跨侧关系规则 |
| --- | --- | --- |
| diagram role / slot | 与请求中的位置严格一致 | 左右角色始终分开，顺序不交换 |
| serialized digest | 对实际送入 importer 的同一字节串重算并核对 | 可以相同或不同；不能单独推出语义同一，也不应强制不等 |
| native context | 保留请求中的 context，或给出可验证的无损推导 | 不得因 ID 拼写相同而合并函数或模块作用域 |
| source ID | 与实际 occurrence 的 source 完整核对 | 可由具名映射关联；同值不替换来源 |
| occurrence ID | 在本侧 checked diagram 中定位并核对 | 即使字符串相同，也保留各自的图与 context 限定 |
| occurrence path | 与同一 occurrence 记录的原生路径精确一致 | 两侧路径可相同或不同；相同不产生跨图关系 |

因此，不能把修复写成“忽略 role/digest/source/path 后再比较”，也不能写成“不同 source 一律拒绝”。一个合法的运输关系通常关联两个不同端点。真正必须拒绝的是：**在调用者已经固定的请求下，以另一个同值端点替换原本指定的端点。** 若调用者另行发起只要求值相等的新请求，正确接收器可在保留两端身份的条件下接受该较弱结论。

原生 `SourceId` 与 `OccurrenceId` 是语义结构中的显式标识；JSON 中出现相同字符串、相同 digest 或 Python 对象相等都不能替代原生判定。

## 4. 发现三：v0 的 path 类型不能直接当成原生 OccurrencePath

原生类型为 `OccurrencePath(pub Vec<u32>)`，根路径是 `[]`。历史后继从 `occurrence.path.0` 导出该数组，并核对 `context`、`source`、`occurrence`、`path` 四项的**同一记录**。该后继中两个指定端点的 path 都是 `[]`，source、occurrence 和 context 各不相同。

v0 却把 path 写为 `"output/0"` 与 `"input/0"`，要求任何非空字符串，没有规定它们与原生 occurrence 路径、边界端口或 wire 的对应。v0 还未显式承载旧请求的 context。

这并不证明所有转换都不可能：context 可能从导入图中推导；某个端口也可能经 native WireRef 关联到 occurrence。但这些都需要明确、受检的映射，不能通过给字符串起名来获得。建议：

- 将 `occurrence_path` 固定为原生 `Array<u32>`，允许 `[]`，拒绝布尔值、负数、越界数字与隐式文本转换。
- 若确实需要 input/output port，新增独立的 `BoundaryPort` 类型，检查 port → WireRef → occurrence 的原生关联。
- 通过 occurrence identity 定位记录，并联合核对 source/path/context；不能只以 path 查找，因为不同来源的根路径都可能是 `[]`。
- 禁止“source 在集合中、occurrence 在集合中、path 在集合中”这种分项存在性代替同一 occurrence 的元组存在性。

## 5. A–D 承载能力逐项判断

| 义务 | v0 已有声明 | 仍缺少的可执行语义 |
| --- | --- | --- |
| A：原请求或无损版本等价物 | request schema、request/context 的 SHA-256 字段 | 独立信任锚、准确的哈希字节域、注册 decoder、从冻结请求提取两图/端点/目标关系的映射；版本等价物的受检无损对应 |
| B：两图原生检查 | 两个有序 slot，各标记 RequiredNotImplemented | 真实供给图字节通过 native importer；证书绑定实际返回对象、版本和 context；不得替换为接收方生成的图 |
| C：限定端点关系 | 两侧完整声明元组及顺序 | 实际端点联合解析与绑定；明确 C 只是定位，还是具名 R；后一种必须有适用 checker 与证据 |
| D：同路接收结果 | Accepted/Refused/Unknown 及文字 residual | 同一请求—context—检查器—有序图对—目标关系的收据绑定；检查状态、证据、预算、允许用途；记录失败路径 |

v0 使用重复数字 digest 和假想 source 标签，本来就是不含真实字节的接口示意；本审查不把这种示意本身当作错误。问题是：示意尚未给出未来实现必需的派生与绑定规则，故“结构足以列出义务”不能读成“语义足以实现义务”。

`Accepted.requires` 列出 `D-recorded-receiver-outcome` 可视为工程义务，不必将它批评为逻辑循环；但应明确执行顺序：完成 A–C → 构造无自哈希的 receipt body → 成功记录 → 返回 Accepted 与 receipt 引用。若记录失败，返回 `Unknown/ReceiptPersistenceFailure`，不得声称存在持久接收证书。

## 6. 最小反例与有限执行

### 6.1 原检查器上的七次直接调用

以原始 `verify.py` 和 v0 文档的已核验 SHA-256 为输入，不修改原检查器。每项从规范文档独立复制：

| 探针 | 改动 | 实际结果 |
| --- | --- | --- |
| S00 | 规范文档 | StructurallyCompleteProposedInterface |
| S01 | 同时把左 slot 和 relation.left 的 path 改为 missing/999 | 同上 |
| S02 | 同时更换两处 source ID | 同上 |
| S03 | 同时更换两处 occurrence ID | 同上 |
| S04 | 同时更换两处左图 digest | 同上 |
| S05 | 只更换 request digest，不重新派生端点 | 同上 |
| S06 | request schema 改为未注册字符串 | 同上 |

这些是“声明自洽不蕴含真实绑定”的见证。S01–S04 保持了两份声明相等；S05–S06 保持了检查器所要求的字符串/摘要形状。由于没有读取任何实际图，探针不是对某个真实接收器的攻击成功记录。

原套件的 `test_05` 是删除名为 wrong-path 的控制条目；`test_06` 是把 same-value-different-origin 控制的 expected 字符串改为 Accepted。它们不提交错误路径，也不构造同值异源图。这两个测试在原有声明层范围内合理，后续原生测试必须使用实际不同对象。

### 6.2 一个可写在纸上的反例

取左侧端点 `a/u/[]`，右图有两个端点 `b/v/[]` 与 `d/z/[1]`，三者的观察值都为 1，局部图像都是同一个点。显式固定关系：

\[
R=\{(a/u/[],\;b/v/[])\}.
\]

则：

- 左右完整身份不等，但第一对属于 R；完整元组相等会错拒。
- 第二个右端点确实存在，且同值、同局部图像，但 `(a/u/[], d/z/[1])` 不属于 R；值相等或两侧成员资格会错收该指定关系。
- 拼接 `source=d, occurrence=v, path=[]`：每个分项都在右图中出现，但没有这个联合元组。
- 若仅知道局部图像相同，而目标是未定义或缺证据的运输/M6，则正确状态是 Unknown；不能仅因找不到 witness 就声称 Refused 意味着不存在。

这里的 R 是人为明确指定的有限数学关系，**不是从 native Adva 推导出的运输关系**。它足以否定“成员资格/同值一般能证明任意目标关系”的推论。

### 6.3 十六个模型案例

完整输入、模型和逐项结果位于 `reproduce.py`、`audit-results.json`。16 项包含：不同身份的合法关系、错误路径、错误来源、元组拼接、同值但关系不成立、同图像缺证据、倒序、仅定位成功、单独的数值关系、数值不等、未定义关系、预算耗尽、外来收据、缺少右图检查、固定请求下替换端点、记录失败。

其中三个 Accepted 案例分别针对明确的关系、明确的成员资格、明确的数值等式。不同名字的结论没有相互转换。所有 Accepted/Refused/Unknown 均是**模型输出**，真实 native 结果仍为 NotRun。

## 7. 可直接审阅的接口修订

`adapter-obligation-v1-proposed.json` 是完整版本化合同草案，包含字段类型、A–D 规则、旧请求映射、两个不同关系分支、收据及错误语义，并列出 12 项待执行的原生控制。它是 JSON 合同文档，不是已实现的 JSON Schema validator 或 Rust API。

核心接口分离为：

| 类型 | 内容 |
| --- | --- |
| RequestBinding | 独立固定的原请求、context、profile；有序 QualifiedOccurrenceSelector 对；选定的关系 claim |
| PinnedPairMembershipV1 | 只证明两侧指定 occurrence 定位成功 |
| CertifiedRelationV1 | 关系 profile、参数、量词、适用域、证据及适用 checker |

同侧精确比较包含 slot、diagram digest、context、source ID、occurrence ID、native path。跨侧使用 SelectedRelation，不进行全元组相等。

最小迁移不是改旧文件后重跑 13 个标签测试，而是保留 v0，新增 v1：

1. 先固定目标究竟是 C0 定位，还是某个具名 R。若是 C0，声明其局限；若是 R，写出 checker 的确切判断。
2. 写出原冻结请求到该关系声明的保义映射。单纯附加一个新解释不能冒称已有请求的无损解码。
3. 由 Rust 实际导入两图并返回不可由输入自授的 checked handles/certificates；所有反序列化证书都需要验证。
4. 按实际 occurrence 记录做联合绑定，再执行目标关系 checker。
5. 把这一条 A–C 链的证据、版本和预算写进同一个结果记录。

`CertifiedRelationV1` 不是允许调用者任意选择 checker 的插件口：接收 context 必须事先固定受信 checker/profile，候选只携带待核验材料。调用者也不能在失败后把运输关系降为值相等。

## 8. Accepted / Refused / Unknown 的边界

| 情形 | 结果 | 所不声称的内容 |
| --- | --- | --- |
| 选定用途的 A–D 全部实际通过 | Accepted，绑定精确 claim 与用途 | 更强关系、所有图、身份合并或 M6 |
| 错图、错 context、错元组、错顺序、失效 guard 或提交的 witness 无效 | Refused，记录具体原因 | 目标关系在所有情形下不可能存在 |
| 完整有限关系判定器给出特定反例 | Refused，并保留该范围内的反例 | 无边界的数学否定 |
| 关系尚未定义、适用 checker/证据/原生检查不可用、预算耗尽 | Unknown，记录缺项及消耗 | 成功或不存在 |
| 必须的记录失败 | Unknown / ReceiptPersistenceFailure | 持久化 Accepted 已完成 |

一个已知不兼容/不允许的请求 profile 可被策略性 Refused；一个已允许但当前证据不足的判断是 Unknown。两者需用不同原因码。测试套件失败是实现验证失败，不能直接转写成任意真实请求的 Refused。

算术边界保持：加法零与乘法单位分别类型化；`A=B=0` 不能进行商消去；一般乘法载体还须满足该 profile 的可逆/有定义条件，非零不是所有代数域中的统一充分条件。数值等式不消除历史或来源义务。

## 9. 复现、成本与残余

在此包目录运行一次：

```sh
timeout 30s python3 -B reproduce.py > replay-results.json 2> replay-stderr.txt
```

脚本在检查前设置 CPU 10 秒、地址空间 256 MiB、普通文件输出 1 MiB 上限；外层 timeout 限制 30 秒。禁止自动扩展案例或搜索。输出文件应使用新名称，保留本次结果。断言不满足则失败退出，不能把截断输出当成功结果。

本次一个进程完成，无 correction replay；7 次结构调用、16 个模型案例通过其预先声明的期望。执行主逻辑到输出前为 2,579,174 ns；Linux `RUSAGE_SELF` 最大 RSS 11,136 KiB。stdout 61,745 字节，stderr 0 字节。输出前计时不包括序列化和写出；完整端到端峰值/时间没有另作精密测量。源码检索、报告撰写和打包不在这一模型运行计时内。

`audit-results.json` SHA-256：`54c779c58cf4618eb9010729ccd2d3000b04741669f4e288a9752717e17d9f5a`。

最终判断支持最初提出的边界疑问。真正关键的是**请求绑定的端点对、端点在图中的联合存在、端点间的指定关系**不能混为一个“相等”。下一步先确定 C 的精确命题；本轮交付足以审阅这项选择，不需要重跑库存或 helper 来回答它。Rust 接收器、真实双图控制、收据持久化与原目标是否能被接收均未完成。

## 10. 固定来源

- [S1：11 月 9 日 v0 草案，尤其 L40–61、L86–105](https://github.com/mountain/adva/blob/2d5b6c18a7446d4f0aa3834c521cd7ad57a600a8/experiments/native_input_binding_serialized_leaf_request/target-adapter-contract-review-20261109/adapter-obligation-v0.json#L40)
- [S2：检查器，尤其 expected_selector 与 L77–87](https://github.com/mountain/adva/blob/2d5b6c18a7446d4f0aa3834c521cd7ad57a600a8/experiments/native_input_binding_serialized_leaf_request/target-adapter-contract-review-20261109/verify.py#L31)
- [S3：测试 L45–55，仅改控制声明](https://github.com/mountain/adva/blob/2d5b6c18a7446d4f0aa3834c521cd7ad57a600a8/experiments/native_input_binding_serialized_leaf_request/target-adapter-contract-review-20261109/test_verify.py#L45)
- [S4：原 A–D 定义](https://github.com/mountain/adva/blob/2d5b6c18a7446d4f0aa3834c521cd7ad57a600a8/experiments/native_input_binding_serialized_leaf_request/machine-reference-ledger-notes-20261106.md)
- [S5：旧后继完整元组成员检查](https://github.com/mountain/adva/blob/2d5b6c18a7446d4f0aa3834c521cd7ad57a600a8/experiments/native_input_binding_certificate/native_input_binding_opaque_successor.rs#L34)
- [S6：原生 OccurrencePath 类型](https://github.com/mountain/adva/blob/2d5b6c18a7446d4f0aa3834c521cd7ad57a600a8/crates/adva-ir/src/ids.rs#L48)
- [S7：11 月 9 日结果与范围](https://github.com/mountain/adva/blob/2d5b6c18a7446d4f0aa3834c521cd7ad57a600a8/experiments/native_input_binding_serialized_leaf_request/target-adapter-contract-review-20261109/outcome.json)
- [S8：固定 Communication v1，目的/检查/接收/记录边界](https://github.com/mountain/adva-machine/blob/6c7f6515114e121cc2d4c0481bc416e81737a8c3/spec/framework/communication-v1.md)
- [S9：固定 Kernel/package v0.1，KPB-03、07–10](https://github.com/mountain/adva-machine/blob/acfc9806fe18a36d0f7194dcc196a380b2834adf/spec/framework/kernel-package-boundary-v0.1.md)

报告、修订方案及新探针为 Codex（OpenAI）原创，按 Unknown v0.3 提供。包内 upstream 文件保留原始字节；其 source URL 与摘要列于 `sources.json`。本轮无 GitHub 提交，未将账户使用、署名或信任作为正确性证据。
