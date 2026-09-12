# Research 0168: switch, swap and the braid group are not iota's problem

Date: 2026-09-10. Status: bounded assessment; **no executable artefact and no
new claim**. It answers one direction question asked by Mingli Yuan: could
`switch`, `swap` and the braid group be handled more easily by an iota-lang
substrate. The answer is no, for one mathematical reason and three engineering
reasons, both recorded below with their evidence.
Base: `mountain/adva@d423ea8`.

## 1. The question

Direction: "考察一下 switch\swap 和辫子群是不是可以用 iota-lang 来更容易的
解决，即便数学上能，工程怎么引进，仍需要慎重考虑."

The question has three layers and they must not be merged: whether a substrate
*can express* these structures, whether it *decides* them, and whether importing
it *helps the engineering*. This note separates them, because the answer differs
per layer and only the third is a matter of taste.

## 2. What adva already holds

| Structure | Where | What is actually there |
| --- | --- | --- |
| `swap` | `crates/adva-lisp/src/operation.rs:391` (evaluator), `:193` (spec), `crates/adva-lisp/src/validate.rs:490` (lineage) | 2 in / 2 out, `LineageRule::Swap`, output lineage is `[in1, in0]`, evaluator returns the two values exchanged |
| switch | `docs/research/0160-faithful-switch-and-reverse-observer-search.md` | **not a primitive.** "Switch" there names a *representation switch*: whether two independently computed representations agree, and what a coarser observation lost. Local faithfulness remains Open |
| `Q4` interchange | `crates/adva-witness/src/relation.rs`, `docs/research/0111-...md` | profile fixed to `ab => ba`, trace-monoid process lift, Klein-four Coxeter shadow |
| `M6` braid | same | profile fixed to `aba => bab`, positive-braid-monoid lift, `S3` shadow; raw paths are never identified |
| braid as transport | `docs/research/0057-typed-vacua-constant-boundary-braids.md` | the fixed three-colour boundary carries a nontrivial pure-braid transport layer; three visible colour rotations return to the original boundary but leave a central full twist in the exact lift |
| braid coupled to computation | `docs/research/0058-checked-gate-braid-composition.md` | crossings move complete coloured ports while the gate reads only their colours and values, so every pure braid lies in a contextual kernel of the finite computation: "the braid layer is a transport sidecar, not yet a computationally coupled substrate" |

Two facts about `swap` matter for the assessment and are easy to miss.

1. `swap` is **involutive**: `swap . swap = id`. It is therefore an order-two
   element, and as a permutation of two ports it satisfies the Yang–Baxter
   relation trivially. Adva does not need a substrate to *represent* braid
   generators: it already has one, as an exact 2-in/2-out operation whose
   lineage rule is `[in1, in0]` and whose registry completeness is tested
   (`crates/adva-lisp/tests/operation_registry.rs:119`).
2. The braid relation as adva records it is a **formation** obligation over two
   still-distinct raw paths, not an equality: `RelationCellV0` keeps both paths
   and never identifies them.

## 3. The mathematical objection

The braid group word problem is **decidable**, and well engineered: Garside
normal form, Birman–Ko–Lee, Dehornoy ordering. This is what makes braid
computation in adva exact and terminating.

The equational theory of combinatory logic is **undecidable**. Combinatory logic
and the untyped lambda calculus are equivalent under bracket abstraction, and
the equational theory of the latter is undecidable. Iota is a one-rule complete
basis for SKI, so it inherits that theory exactly.

Therefore:

> Reducing "are these two braid words equal?" to "are these two iota terms
> equal?" replaces a decidable problem with an undecidable one. This is not an
> engineering risk; it is a direction error.

There is a second, independent objection, and it is the one that connects to
0161. Iota's reward is **convergence**: `ι x => x S K` exists to drive a term to
a unique normal form. A braid records **divergence**: distinct routes that reach
the same boundary. The 0161 calibration already measured this on the substrate
itself — the ι encoding expands to η-expanded SKI, so the two sides agree *by
value* and not *by syntax*. A machine whose purpose is to erase routes cannot
carry routes, and the whole content of `B_n` is which route was taken.

This is also why AGENTS.md forbids contraction, memoization, CSE or a cell on
the strength of value equality: value agreement is exactly the observation that
would discard the braid.

## 4. Where iota *could* stand, and why it does not help here

Three roles were considered.

1. **Iota as an encoding target** — compile a normal-form algorithm into ι.
   Coherent in principle, because ι is a complete basis. But it makes the
   problem undecidable (§3) and buys nothing adva's exact Artin action does not
   already do.
2. **Iota as a minimal, portable reference interpreter** — a tiny substrate an
   independent party could reimplement. This is the only role with real value,
   and it is not a braid-specific one: it belongs to the checker question, not
   the braid question.
3. **Iota as the value-level semantics of a braid** — incoherent: it collapses
   precisely the distinctions the braid layer exists to keep.

The per-structure verdict follows.

| Structure | Can iota express it | Does that decide it | Does it help |
| --- | --- | --- | --- |
| `swap` | yes (everything is expressible) | not needed — swap is already exact, typed, involutive | no; 2-in/2-out typed boundary would become untyped term application, i.e. strictly less information |
| switch (0160) | **the question cannot be stated** | — | no; it is a representation/observation/objectification question, and iota has no representations, no observations and no quotients |
| braid group | yes, but only up to iota's equality | no — and worse, undecidable after the translation | no; see §3 |

## 5. Engineering cost of importing it

Even if §3 were absent, the import is not cheap.

- **It does not exist yet.** The iota-lang checkout does not compile at any
  commit (research 0167), and the DualMachine written to complete it passes 9 of
  29 cases with one structural defect outstanding. Depending on it moves risk
  from design to infrastructure.
- **Toolchain, measured on the machine this assessment was made on.**
  `lein`, `clojure`, `clj`, `mvn` and `gradle` are all **absent**. Clojure
  itself is in the local Maven repository, but the two declared dependencies
  are not: `org/rekex/rekex-parser` and `org/junit/jupiter` have **never been
  resolved**, which is consistent with 0167 section 3 finding the rekex
  import unresolved in every commit. So the import is not "call a library":
  it is "install a JVM toolchain, resolve two never-resolved dependencies, and
  fix a repository that has never compiled".
- **Placement.** adva is Rust authority plus a Python adapter. Iota is Java
  (a Clojure shell around `src/main/java`). Under ADR 0001 the Rust side is the
  sole semantic authority and the versioned JSON IR is the interchange
  boundary; a third implementation language has no place on that boundary that
  is not a new subprocess contract.
- **The migration would rebuild what already works.** Adva's braid correctness
  comes *from* carrying identity and history: `SourceId`, `OccurrenceId`,
  lineages and explicit residuals. Iota has no identity mechanism at all (0167
  §4: its machine compares tokens, and its rules were never consistent about
  which frame owned which operand). Any bridge would therefore have to carry
  identity outside iota, in a sidecar — which is a rewrite of the existing
  apparatus with an extra language on top.

## 6. What the braid layer actually lacks

If the goal is to move the braid layer from a transport sidecar to something
computation reads, the missing primitive is named in 0058 and it is not a
language: crossings move complete coloured ports while the gate reads only
their colours and values, so what is missing is an observer that **reads the
port itself** rather than its colour and value. That is an extension of adva's
reading policy, not a change of substrate.

Note 0058 already records this as the direction ("this does not refute a future
history-sensitive machine; it identifies the missing primitive that such a
machine must supply"), and 0160's faithfulness obligation points at the same
place from the representation side.

## 7. Checker soundness check (not an objection)

Before answering, the `M6` formation check was re-derived rather than trusted,
because a missing guard there would have made the whole "adva already handles
braids exactly" claim weaker.

The check is at `crates/adva-witness/src/relation.rs:606`. It requires the left
word to be `a b a` with `a != b`, the right word to start `b a`, *and* the third
right label to equal `b`. An out-of-tree probe (source and output retained in
[0168-evidence](0168-evidence/README.md)) confirms, with the rejection raised at
construction because `RelationCellV0::new` validates:

```
ACCEPTED  aba vs bab (the declared word): boundary_occurrences=6
REJECTED at new() aba vs ba-b3 (third label differs): InvalidBraidWord
REJECTED at new() aba vs ba-a (third label is a): InvalidBraidWord
```

My first reading of the guard was wrong — I judged the third conjunct absent
from a partial view of the condition — and the probe refuted it. The record
keeps both the first reading and the refutation, because an assessment that
only reports the conclusion cannot be checked. **The `M6` checker is sound for
the word-shape obligation it claims**; it checks formation of a braid cell and
explicit references only, and it does not replay the witness, which its own
documentation states.

## 8. What this note does not establish

- No new mathematics. Garside normal forms, the undecidability of the
  equational theory of combinatory logic, and the Yang–Baxter relation for
  order-two permutations are all classical.
- No claim that iota is useless. §4.2 records the one role with real value, and
  it is a checker role.
- No claim about whether adva's braid layer *should* be computationally coupled.
  That is a research direction (0058, 0160), not an assessment outcome.
- No change to any stable API, no `claims.toml` entry, no native operation, no
  Seal, no epoch, no directory-catalog change. The `M6` checker was read and
  probed, not modified.
- Nothing here authorizes an adva-side integration of iota-lang. The
  substrate-side-only boundary of research 0167 §7 stands unchanged.

## 9. 中文交接

- **问题**：switch / swap / 辫子群能否用 iota-lang 更容易地解决。
- **结论**：不能。数学上有一条方向性障碍，工程上还有三条代价。
- **数学障碍**：辫子群字问题**可判定**（Garside 正规形等）；组合子逻辑的
  等式理论**不可判定**（与无类型 λ 等价）。把辫子相等归约到 iota 项相等，
  是把可判定问题换成不可判定问题。第二条独立理由：ι 的回报是**收敛到唯一
  范式**，而辫子的内容是**不同路径到达同一边界**——0161 已实测两侧"按值相等、
  按语法不等"。用擦除路径的机器承载路径，方向就是错的。
- **逐项判定**：`swap` 已是精确、有类型、对合的 2 入 2 出原语，换成无类型项
  应用只会**信息更少**；`switch`（0160）问的是表示切换与观察损失，**在 iota
  里无法被陈述**；辫子群可编码但不可判定。
- **工程代价**：① iota-lang 在任何提交都编译不过，DualMachine 29 例 9 通过，
  依赖它等于把风险从设计搬到基础设施；② 本机实测 `lein`/`clojure`/`clj`/`mvn`/
  `gradle` **全部缺失**，且两个声明依赖（`rekex-parser`、`junit-jupiter`）在本地
  Maven 仓库**从未解析成功**——所以"引进"不是调用一个库，而是装一整套 JVM 工具链
  去修一个从未编译过的仓；③ adva 是 Rust 权威 + Python 适配，iota 是 Java，
  在 ADR 0001 的边界上无处安放；④ adva 辫子正确性**恰恰来自**携带身份与历史，
  而 iota 没有身份机制，桥必须把身份放在 iota 之外——等于重写现有装置再加一层语言。
- **辫子层真正缺什么**：0058 已指明——穿越移动完整端口，而门只读色与值，缺的是
  **读端口本身**的观察者。这是读取策略的扩展，不是换基底。
- **检查器复核**（非异议）：`M6` 的 `check_braid` 守卫**是完整的**，含
  `right_b_again != b`；我先前的误读被外部探针推翻，两者都留在记录里。
- **边界**：无新数学、不登记 `claims.toml`、不改任何稳定 API、未修改检查器；
  0167 的 substrate-side-only 边界不变。
