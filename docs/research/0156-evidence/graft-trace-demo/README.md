# GraftTrace 计算证据（2026-09-07）

状态：研究本地证据。这是一份**编译期结构证书**，不是语义证明；
不使用仓库 crate 之外的任何新代码入库，未注册新原生词。

## 背景

六方 merge 讨论中比较了 Presentation（公开构造+证据+披露边界）与
GraftTrace（编译期嵌套替换伴随证书）两种结构。为确认 GraftTrace 的
可计算性与输入条件，执行本实验。

## 关键发现

`adva run` 的运行轮廓**只接受单定义、无 import、无调用的程序**：

```
adva: profile requires one definition and no imports   (exit 2, state Rejected)
```

因此含函数调用的程序无法经 run 传输编译——GraftTrace 只能通过完整编译
API（parse_module → link_modules → compile_function）计算。这也解释了
`programs/native-run/arithmetic.adva`（无调用）为何不携带 GraftTrace。

## 方法与产出

- `driver/`：独立 cargo 项目，path 依赖仓库 `crates/adva-lisp`；
  程序 `quadruple(x) = double(double(x))`（双模块 + import + 两次嵌套 call）；
- `graft-result.json`：完整 GraftTrace（3 帧：root → root-body →
  root-body/call-argument-0，含 caller/callee、洞绑定、entry_wire、lineage）；
- `graft-certificate.json`：证书 `certified: true`，7 项检查全部 `checked`
  （diagram_integrity、deterministic_frame_ids、parent_child_nesting、
  ordered_hole_bindings、argument_body_regions、boundary_maps、
  call_history_links）；
- `run-record.json`：执行记录与文件摘要。

复现：`cd driver && CARGO_TARGET_DIR=$PWD/target cargo run --offline`

## merge-order-rehearsal/

0156 第 14 节（排序分数条目）工作示例的**合成排演**（不是已执行的 merge
证据）：`rehearse.py` 实现 min-residual-first + party 序号 tie-break；
`all-agree.json` 演示全残差 0 时次序退化为固定序列；
`one-tampered.json` 演示篡改方（P4=15）被排到最后一步且值一致断言 Rejected。
