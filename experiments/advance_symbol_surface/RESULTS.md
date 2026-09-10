# 符号表述的首次原生载入

日期：2026-09-10。状态：`VariationObserved`，一轮有限执行完成。
主仓基线 `91f57d01f94fcd1a2f58cfb59832c263e99315d4`，库版本
`f0312ca4a109e8ca26cc01cb678750ad889c95be`。用户要求通过 adva.py 再前进一步。

最新库交接的明确问题是：PR 170 的原始文档外壳能否通过现有只读 Rust
加载器，并保留九项开放义务。本轮执行了：

```sh
timeout 190s python3 python/adva/adva.py advance \
  --profile symbol-surface-load-v0 \
  --output target/advance-symbol-surface-20260910-01
```

主仓和库中八份源文件逐字节一致。三个外部 payload 的 SHA256 绑定通过，
17 条目的目录及 key-words 检查通过，文档性 swap 对照通过。原文件与历史
NotRun 记录没有被改写。

本轮从当前固定 Rust 源码离线构建 `adva-python`，把新产生的共享库复制到
输出目录后直接加载。没有调用以前安装的扩展，也没有修改 Rust 语义代码。
实际证书来自已有 `load_adva_document_json -> load_adva_document_v0`。

| 项目 | 新观测 |
| --- | --- |
| 原生文档载入 | NativeEnvelopeLoaded |
| 选中入口 / 帧 | inspect / 0 |
| 持久化帧状态 | ready |
| verify 形式判定 | conditional |
| 剩余前沿坐标 | 9，逐项与原记录一致 |
| 已记录 history/result/evidence 输出 | 0 |
| 数学义务解除 | 0 |
| 算术求值 / 证明重放 / 游戏步数 | 0 / 0 / 0 |

Rust 证书的 schema/version、规范表、引用解析及机制形式四个检查字段全部为
checked。原文档、库副本、原样重放的完整载入产物一致。文档摘要为：

`blake3:0b5a4579e5e8b92e7149b09aea82c3e40c1a782a4f01b9925cca33e6f811d7a6`

四个原生负例分别拒绝未知 carrier 99、漏声明的 hole 8、只记录一个输出、
未知 entrypoint。八次调用及所有错误原文保存在 `native-load.json` 和 `cases/`。

另一个正对照把相同外壳放入没有任何外部 payload 的目录。Rust 仍然返回相同
载入产物。这精确展示了当前边界：原生加载器解析文档内的 carrier 引用，
把 `sha256:...` 当作结构坐标字符串；它没有打开、认证或解释所引用的内容。
外层 payload 字节检查单独拒绝了只增加一个空格的内容变更。内容摘要匹配
同样不构成数学证明。

本轮的增量是：此前的 `Native loading: NotRun` 现在有了具体 Rust 载入证书，
未完成状态也经过了原生形式检查。九个文档坐标仍只索引外部注释，不是九个
数学任务的原生编码。i、pi、负一、Cantor、定理应用和游戏的执行状态均保持
原样。没有新增知识纪元、原生 free/drop、Rust Seal 或已完成的学习声明。

| 费用 | 实测 |
| --- | ---: |
| 墙钟，最终报告写入前 | 8.601042 秒 |
| 子进程 CPU 总计 | 7.793590 秒 |
| 监督子进程调用，含构建 | 7 |
| 一个受限子进程内的 Rust 加载调用 | 8 |
| 通过的固定对照 | 8 |
| 留存字节，最终报告前 | 10,854,950 |
| 重试 / 预算续期 | 0 / 0 |

费用不含编写代码、工程测试、运行后只读摘要复核和本文整理。最终报告写入后
还有截止检查，本轮没有超时附录；没有声称测得整体峰值内存。留存量包含
10,593,128 字节的实际原生共享库。

随提交保留的完整材料：

- [总回执](evidence/run-01/report.json)
- [完整原生结果、八次调用及对照](evidence/run-01/native-load.json)
- [原生载入证书与 transition](evidence/run-01/cases/original.json)
- [冻结合同](evidence/run-01/contract.json)
- [本轮对库交接的答复](reply.json)

总回执 SHA256：`51694ca9400e5561591832bb9909ae62cbb8ef38274c8b98ba86420e674fd614`。
其 53 份清单文件的长度与 SHA256 均在运行后复核，实际运行的五份 Python
源码副本与当前实现逐字节一致。相关 109 项工程测试及新增文件 Ruff 检查
通过；这些检查不记作另一轮研究执行。用户随后要求提交远端，因此把全部
54 份原始文件归档至 `evidence/run-01/`，原生共享库无损 gzip 压缩，其余
文件逐字节保留。原始共 10,867,233 字节，归档存储 2,314,022 字节（均不含
新增 manifest）。manifest 同时登记存储与原始字节摘要；`verify_evidence.py`
复核全部材料和已记录结果，不执行共享库。原 target 目录与历史合同不变。
