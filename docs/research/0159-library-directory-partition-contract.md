# Research 0159：adva-library 目录分割工程合同

日期：2026-09-08。状态：`proposed-document`，供评审；不改变任何检查器、不授予任何原生权限、不修改增长义务。
起草：assistant（基于与明理的边界讨论）；评审人：Mingli Yuan。
合同数据文件：`docs/research/0159-library-directory-partition-contract.json`
（schema `adva.library-directory-partition.contract.research`）。

## 1. 中文交接

adva-library 自 2026-09-06 起持续生长：Pascal 原件、phase-runner 编排输入、
0150 纪元、0151 期刊、math 目录学、validation 验收与 vendor 依赖已各自建立
规则，但这些规则散落在 ADR 0042、Research 0139/0154、`math/constraints/`
与各 README 中。本文把既有规则收拢为一份可检查的目录分割合同，并按合同
自身的 admission 程序登记为 math 目录学条目（logic 主题，
`logic-directory-partition-contract`，proposed-document）。

核心立场：**目录分割不是模块系统、不是知识分类法，而是"检查器分层"**——
每个目录对应一种不同权威的准入检查器；文件放在哪个目录，就声明接受哪种
检查；位置本身不授予任何权限。动态的 learn/run/free 合同定义数据如何在
层间运输；本目录合同定义每层可以保留什么、谁有权检查。两者合起来才是
完整的工程边界。

## 2. 六层模型

| 层 | 目录 | 检查器（权威来源） | 允许的证据状态 |
| --- | --- | --- | --- |
| 原样层 | 根（pascal 对、index.json） | 字节摘要 pin | proposed-document |
| 编排层 | phase-runner/ + learn-free-six.contract.json | 有界子进程监督器；输出只作字节 | 运输记录（不解释） |
| 快照层 | stability/ | Rust load_library_v0 全父链重放 | checked-research-snapshot |
| 期刊层 | exploration/ | 全阶段再生回放比对 | replayable-proposal-journal |
| 目录学层 | math/ | adva.py math-check（schema/一居/字节 pin） | 多状态；native_admission 恒 not-granted |
| 验证层 | validation/ | 安装运行冒烟 + 版本 pin | 验收记录（非密码审计） |
| 依赖层 | vendor/ | 精确 commit pin | 外部源码，不改写 |
| 夹具层 | knowledge-boundary/、prime-universe/ | 各自实验合同 | 各自声明 |

六层检查器权威递增、互不替代：math-check 通过不等于 Rust 重查通过；
字节 pin 成功不等于证明成立。目录分割的全部意义是让这些"不"字变得可检查。

## 3. 三条公理

1. **位置不授权**（location grants nothing）：条目必须显式登记；目录名不是
   语义身份，topics 不映射 compute/verify/learn 或 Rust/Lean/Metamath。
2. **跨目录即引用**（cross-directory is documentary, never derivational）：
   一居制；跨主题引用是文档视图，不是推导父、隐式导入或权限转让。
3. **晋升需新合同**（promotion requires a new contract）：journal→epoch、
   proposed→native、documentary→Seal 每步都需新的有界版本化合同；禁止
   就地改写旧 pin。

## 4. 与 0157/0158 的连接

- 0158 的"下行解释"是几何祖先规则的一般化：每个条目都要有可检查的回程
  纤维（downward chain），否则只是外部引用。
- 0158 的 drop 是 0157 free 谓词的机器侧一半：drop ≈ F2（前沿闭合后的释放
  动作，receipt 保留全部见证）；F1 账户终态与 F3 人类接受仍独立。
- 本地 AEG 点号目录（.breakthrough、.campaign 等）是"没有 drop 的活帧"：
  运行与检查已完成，但帧未释放到仓库内指定归宿（docs/research/0NNN-evidence/）。
  本合同 cross_directory_rules 第 5 条即补这条规则；本次提交执行第一次归档
  （Run 8–11 补入 0129-evidence，advance-loop 登记为 0160 证据）。

## 5. 工程推进路线

1. 归档未入仓推进（本次完成：Run 8–11、0160；merge-six keys/、.rust-run100、
   archive-run2..5 待按合同分类）；
2. free 谓词工程化（0157 评审 → acceptance schema → learn-free-six 合同 v1 →
   原生 free 的 Rust 设计门；drop 作为 F2 候选进入该门）；
3. drop 桥（0158 continuation：一个具体 thread/dual 对 + 一条保持性声明 +
   一个有限合同）；
4. math catalog 提案准入命令（加法式，显式评审，新版本号）；
5. 治理修复（0158 编号冲突、.gitmodules 与 vendor 未跟踪产物）。

## 6. 本次登记（admission 记录）

按合同 admission_procedure：declare（本条目与目录表）→ check（math-check
目录学一致性，CatalogConsistent）→ accept（本次为文档登记，任务未声明人类
接受）→ commit（加法式，历史 pin 不变）。math-check 通过只允许浏览声明引用，
不授予原生准入。

## 7. 明确不做

- 不注册新原生命令（free/drop 无原生实现，本文件不注册）；
- 不改变 learn-free-six.contract.json 的 free 阶段（仍 AdapterUnavailable/NotRun）；
- 不修改增长义务与 documentary seal（保持 Open / NotIssued）；
- 不修改任何检查器；本文件是 proposed-document，不是已接受的 ADR。
