# Research 0167: The iota-lang substrate is a compile-failing, never-executed machine

Date: 2026-09-10. Status: bounded local audit; reconnection is compile-complete
and behaviourally negative. No claim entry is registered in `claims.toml`; no
native admission, no new epoch, no language equivalence.
Direction: Mingli Yuan. Audit, reconnection and record: assistant.

## 1. What was asked

Research 0161 recorded iota-lang as the Substrate side of one checked finite
projection and reported its state as "parser and definitions only, no running
loop". 0161 also took its ι encodings from the iota-lang definitions but
reimplemented the reducer in Python (`docs/research/0161-evidence/reducer.py`),
so the substrate was never executed as an independent implementation.

This note closes that gap as far as it can be closed: it establishes exactly
what state the iota-lang checkout is in, whether a reconnection to a running
machine is a wiring repair or a design repair, and which part of the recorded
test contract the recorded rules can and cannot reproduce.

## 2. Provenance and scope

| Item | Value |
| --- | --- |
| Checkout | `/Users/mingli/Adva/iota-lang` |
| HEAD | `a1865e6d70d55a0d9457b33570e533463818d7d6` ("add tests") |
| Working tree | clean (0 modified paths) |
| Language resources | `src/main/resources/iota/lang/iota.iota`, `.../ski.iota` |
| Java sources | 20 files, 755 lines under `src/main/java` |
| Java tests | 2 files, 171 lines under `src/tests/java` |
| Toolchain used | OpenJDK 26.0.1 (`javac --release 17`) |
| Licence | MIT, Copyright (c) 2021 Mingli Yuan |

`SKITest.java` pins at
`c9b84b9206daa10c5977e22f90bc30ba9cbe016c038ad1036644d8025a58e133`, 17 `@Test`
methods. That file is treated here as the recorded behavioural contract: it is
the only place in the repository where the machine's expected results are
written down.

Two artefacts were produced and are committed:

1. `experiments/iota_lang/` — a reconnected machine, staged under the audit so
   that the checkout is not modified;
2. `docs/research/0167-evidence/replay.jsonl` — the replay of all 17 recorded
   cases, sha256 `e1bb323b8fe677342b7de8cf0da65eb90426088fb9602a12485249edb306c0a4`.

The frozen contract for this run is: one checkout at the pin above, one
Java toolchain, 17 transcribed cases, both execution modes, step cap 100000 per
case, no network, no dependency resolution, no write into the checkout.

## 3. The recorded sources do not compile

```
javac --release 17 -proc:none -d <tmp> $(find src/main/java -name '*.java')
```

fails with 83 `error:` lines (67 diagnostics). The failure is not a missing
classpath; the referenced symbols do not exist anywhere in the repository or in
its history:

| Referenced | Declared? | Where |
| --- | --- | --- |
| `org.rekex.*` (6 packages) | external | `Parser.java` only; the declared dependency was never resolved |
| `ski.lang.cons.$.cons` | **no** — no `package ski` in any commit | `SKIMachine.java:5` |
| `ski.lang.ski.$.Combinator.iota` | **no** | `IotaMachine.java` (5 sites) |
| `iota.lang.Combinator.s` | **no** — no `package iota.lang` | `LISPMachine.onDes` |
| `DualStack.lppeek()` | **no** — never defined in any commit | `IotaMachine.onSwap`, `onCirc` |
| `Symbol.value()` | **no** | every rule condition |

`git log --all --name-status` over `src/main/resources` shows that only two
`.iota` files have ever existed, and that the two migration commits (`e62f000`,
`63bcfb6`) only *renamed* them (`iota/anno/*.iota` ↔ `iota/lang/*.iota`). No
module named `ski`, `cons`, `iota.lang` or `iota.lang.iota.$` was ever authored
in this repository, and no generator exists that could produce one: the `.iota`
files are Clojure-shaped (`(ns iota.lang.ski)` + `defn`), while the rekex
`Parser` accepts `<>`/`()`/`[]` with uppercase constants. The `$.Combinator.i`
enum-member access has no authoring source in either notation.

The same holds for the utility layer, and it did so from the beginning:
`DualStack` instantiates `Applicative<T>` and `Concatenative<T>` with `new`,
which raises `Applicative is abstract; cannot be instantiated` — and the file's
first committed version already had that line. So the repository has never been
in a compiling state at any commit.

**First finding: the reconnection is not a build-configuration problem.**
Nothing is missing from the build; the machine was written against a module and
symbol layer that does not exist in this repository and never did.

## 4. Reconnecting it is not only wiring

A machine-local reconnection was staged under `experiments/iota_lang/`: the
recorded machines are kept rule for rule, and are connected to one interning
site for symbol identity (`Symbols`, one instance per token) plus a concrete
`Cons` carrying the public `left`/`right` fields that the rule bodies read.
Rule *order* is also made deterministic — the recorded `LISPMachine` reflects
over `getFields()` and dereferences `@rule` unconditionally, which throws
`NullPointerException` on every non-rule field — so rules are now collected
from the class chain, superclass first, in declaration order. With that, the
machine compiles and runs; `SKITest` cannot be executed at all as recorded, so
the 17 cases were transcribed into a driver that compares result token strings.

Compiling is where the good news ends. Two rules are arithmetically
inconsistent with the rest of the class, and the inconsistency is provable from
the recorded snapshot strings themselves:

- `onCons` pushes head-then-tail (`state.lpush(c.left); state.rpush(c.right)`),
  which splits `(x y)` into the state `x|y`. But `rvrt` fires only when
  `llen() == 2 && rlen() == 0`, `wrap2` and `wrap3` fire only when
  `llen() == 0`, and `swap` reads the head from the left stack. With that push
  order the pair-rebuilding rules are **unreachable**, and `(x y)` stops at
  `x|y` with no rule applicable.
- `onS` pushes `(y z)` then `z`, leaving the right stack `(y z)z`, while
  `wrap3` reads that stack as `[third, second, first]` and would rebuild
  `(x (y z))` — not the `((x z) (y z))` the test asserts.

Both were kept as recorded in the audit, and are documented in the staged
source. Their effect is visible in the frozen transcript: the machine reaches
states such as `ιs|(ι ι)k`, `x|z(y z)` and `x|yy` in which no rule fires.

The frozen transcript also shows one concrete mechanism behind the dead ends.
`S` is the only evaluator rule whose first argument is consumed as a *raw
token* on the left stack (`onS` pops `lpeek` itself), while `K` and `I` reduce
a term that the `cons` rule has already marshalled. So when `S`'s first
argument is not itself a reducible term, the machine transfers that token to
the left stack and then stops:

| term | last reachable state | recorded expectation |
| --- | --- | --- |
| `(((s k) x) y)` (`testFalse`) | `(x y)` computed, then re-split to `x\|y` with no rule applicable | `y` |
| `(((s x) y) z)` (`testS`) | `x\|z(y z)`, no rule applicable | `((x z) (y z))` |

A raw argument to `S` therefore yields a stall rather than a wrong value. That
is a stronger statement than "two expectations disagree": on the recorded rules
`S` cannot be applied to a constant combinator at all, which is exactly what
`testFalse`, `testKSKS`, `testKKKSKS` and `testSKK` require. And what the
machine computes for `S K x y` is `(x y)`, the standard value, while the
recorded test asserts `y` — a mistake in the contract rather than a difference
of rule semantics.

**Second finding: the recorded rule set has no operand-marshalling model.**
This is the same defect class AGENTS.md names for this repository: a machine
with more than one representation of the same state needs one invariant that
all rules respect, and here the left/right convention is only implicit and only
partly consistent.

## 5. The negative result is not a stopping bug

The recorded loop stops as soon as the left stack is empty (`halted()`), which
is not a normal form: after an `I`, `K` or `S` reduction the head routinely
moves to the right stack and the left stack empties while the term is still
mid-reduction. That alone could explain failures — so the driver replays every
case twice:

- `recorded`: the recorded loop and halt condition;
- `strict-halt`: a bounded diagnostic requiring an empty left stack *and*
  exactly one right-stack term before reading a result.

```
mode           cases  expected value read  errored  ever reached expected value
recorded          17                    0       17                            4
strict-halt       17                    0       17                            5
```

Not one of the 17 cases ever produces a readable result in either mode: every
case ends in `no rule applies at state ...` or `peek on empty stack`. Neither
mode counts as a pass. The two modes differ in exactly one case — `testSKK`
reaches its expected `(x y)` under the stricter loop and not under the recorded
one — so the halt condition accounts for one case and cannot account for the
other sixteen.

The `ever reached` column is the sharper measurement. The driver records, for
every round, the two stack heads as real terms rather than as reconstructed
strings, and asks whether the expected value was ever *transiently* the top of
either stack:

| case | expected | reached at round | what happens instead |
| --- | --- | --- | --- |
| `testI` | `x` | 1 | recorded loop keeps reducing on the emptied stack |
| `testK` | `x` | 2 | recorded loop keeps reducing on the emptied stack |
| `testFalse` | `y` | 1 | machine computes `(x y)`, re-splits it, dead-ends at `x\|y` |
| `testIota2` | `x` | 1 | machine dead-ends at `ιs\|xk` |
| `testSKK` | `(x y)` | strict loop only | machine computes `(x y)`, then fails on the emptied stack |

So five cases do compute the documented value on the way through, and the
recorded machine has no normal-form test that recognises it. Removing the
spurious reductions is not sufficient either: the twelve `testS`-class and
`testII`-class cases never touch their expected value at all, because the `S`
rule (above) and the pair family cannot reach them.

Repairing this is a design decision, not a bug fix: a machine that both
computes a value and then destroys it has one stop condition and one operand
convention to choose, and the recorded sources fix neither.

A further contract defect is visible in the same place as `onS`: `testFalse` is
`(((S K) x) y)` and `testKSKS` is `(((K S) K) S)`, i.e. the recorded tests use
`S` and `K` both as combinators and as ordinary operands of each other, while
the rule conditions recognise them only in head position. No rule is recorded
that reconciles the two roles.

Two further observations from transcription, which are contract defects rather
than machine defects:

- `SKITest` reads `cons`, `variable`, `i`, `k`, `s`, `iota` without declaring
  them anywhere in the file or in the classpath; `testII` … `testIIIIII` build
  `cons(cons(hi, hi), hi)` from one value, so all five have the *same* term
  `((ι ι) (ι ι))` but five different expect-strings, none of which is that
  term. The recorded expect-strings are unreachable for the recorded terms
  regardless of rule semantics.

**Third finding: iota-lang is a language whose machine was never executed.**
The three symptoms 0161 recorded — parser and definitions present, no running
loop, no equivalence claim — now have one cause.

## 6. Reproduction

```
experiments/iota_lang/run.sh /Users/mingli/Adva/iota-lang <fresh-output.jsonl>
```

The script compiles the staged machine into a temporary directory, replays the
17 cases in both modes, and writes the header (checkout, HEAD, dirty count,
`SKITest` digest, `@Test` count, toolchain), one line per case, and two
summaries. It refuses to overwrite an existing output path and writes nothing
into the iota-lang checkout. For step-level stack effects:

```
javac -d <tmp> $(find experiments/iota_lang/java -name '*.java')
java -cp <tmp> iota.Probe "(i x)" 6
```

## 7. What this does not establish

**Substrate-side only (direction, 2026-09-10).** This line of work stays on the
iota-lang side. Nothing here is connected into adva: no Rust type, operation,
certificate or `ProgramTerm`, no adapter, no comparison harness, no change to
the 0161 projection or to its Python reducer. The audit lives in adva's
repository only because that is where the evidence discipline and the archive
home are; that is a storage location, not an admission. Any future adva-side
integration needs its own explicit decision and its own bounded, versioned
contract, and is not authorized by this note.

- No equivalence, refinement or simulation between iota-lang and adva is
  claimed, in either direction. The 0161 projection is untouched and is still a
  finite projection onto an external definition, not onto a running substrate.
- A repaired machine that reproduces 17 recorded strings would still not be a
  proof of the SKI or iota calculus, of ι's universality, or of Church-Rosser
  behaviour. Term rewriting here is bounded by a fuel cap and is not a
  confluence proof.
- The staged machine is an audit artefact under `experiments/`. It is not the
  iota-lang repository and carries no authority over it. Applying the same
  patch upstream is a separate, deliberate change to that repository.
- The rule-order defect (`getFields()` reflection) and the identity defect
  (`==` on non-interned symbols) were repaired only as far as needed to make a
  run possible; no claim is made that the repaired order is the intended one.
  The staged order is the recorded declaration order, superclass first.
- No `claims.toml` entry, no native operation, no Seal, no epoch and no
  directory-catalog change accompanies this note.

## 8. Consequence for the plan

0161's recorded next step was "make iota-lang run, then upgrade the projection
from rewriting the definition to comparing two independent implementations".
By the direction of 2026-09-10 the second half is **not** in scope: this line
continues on the substrate side only, and the projection upgrade stays blocked
until it is separately authorized. This audit shows the first half is larger
than a wiring task, and that its content is a design decision rather than a
repair: the machine needs one explicit
operand convention, a halt condition that agrees with it, and a test contract
whose expectations are consistent with each other. Until that decision is made
and recorded, there is no substrate to compare against, and any byte-frontier
agreement between adva and a *repaired* iota machine would be evidence about
the repair, not about iota-lang.

The three options for the substrate itself, with what each would buy (all of
them iota-lang-side work, none of them an adva change):

1. **Design the machine** — fix the operand convention, the halt condition and
   the loop, then re-derive the 17 cases and record the ones that survive.
   Largest work, and the only one that yields a substrate with a defensible
   semantics.
2. **Shrink the contract** — reduce iota-lang to the one rule that *is* fully
   recorded and consistent as far as it goes (`ι x => x S K` plus the ι-only
   cases), discard the SKI and pair layers that never ran, and record the
   substrate as iota-only. Smallest work; also the most honest description of
   what exists today.
3. **Keep it as reference material** — leave iota-lang as the definition source
   it currently is, state that explicitly in the 0161 line, and stop describing
   it as a language implementation in the six-repo proposal until it runs.

This note takes no position among the three; it supplies the evidence they
share.

## 9. 中文交接

- **事实**：iota-lang 在 `a1865e6`（工作树干净）下**任何一个提交都无法编译**。
  引用的 `ski.lang.cons.$`、`ski.lang.ski.$.Combinator`、`iota.lang.Combinator.s`、
  `DualStack.lppeek()`、`Symbol.value()` 全仓全历史都不存在，也从来没有对应的
  作者源或生成器；`DualStack` 从第一个提交起就在 `new` 两个函数式接口。
- **复现**：`javac --release 17` 得到 83 行 `error:`（67 条诊断）。
- **重连不是接线问题**：我把机器按规则逐条接到单一符号内部化点后可以编译并运行，
  但 17 个记录用例**双模式都是 0 次合法读出**；`onCons` 与
  `rvrt`/`wrap2`/`wrap3` 的栈约定互相矛盾（成对重建规则不可达），`onS` 的右栈
  顺序与 `wrap3` 相反，`onKr` 缺右栈为空的守卫（原记录里该守卫存在，重连中丢过一次，
  已补回并记入本次运行）。
- **不是停机太早，但停机条件确实吃掉一例**：严格停机变体（左空且右恰一项）只在
  `testSKK` 上改变结论，其余完全相同；逐轮记录两个栈顶真值后可以看到，
  **记录循环 4/17、严格循环 5/17 个用例在归约途中确实算出了文档期望值**
  （`testI`、`testK`、`testFalse`、`testIota2`，加上严格循环下的 `testSKK`），
  机器却没有识别正规形的判据。另外 12 个 `S` 类与 `ι` 类用例连期望值都没碰到。
  所以缺口一半在停机条件、一半在规则代数，两者都要选，而记录里都没选。
- **契约本身也有缺陷**：`testII`…`testIIIIII` 的项全等而期望串互不相同；`testFalse`
  与 `testS` 的算符顺序要求互相矛盾。
- **结论**：iota-lang 目前不是"能跑的基底语言"，而是一台**从未被执行的机器**。
  0161 记录的"只有解析器与定义、无运行闭环"由此得到单一成因解释。
- **边界**：本记录不声称任何语言等价、不声称 ι/SKI 演算、不是证明、不登记
  `claims.toml`、不动目录学、不改 iota-lang 仓（修复实例按审计工件放在
  `experiments/iota_lang/`）。
- **产出**：`experiments/iota_lang/`（重连机器 + 重放驱动 + 追踪探针 + `run.sh`）、
  `docs/research/0167-evidence/replay.jsonl`（本次运行原始记录，sha256
  `bfa1dc5f…bdfec1`）。

## 10. DualMachine version 0 (same day, substrate-side only)

After this audit the completion line was started on the iota-lang side, using
the direction of 2026-09-10 to keep it there. The specification is
[`experiments/iota_lang/DUALMACHINE.md`](../../experiments/iota_lang/DUALMACHINE.md);
the run is `experiments/iota_lang/run-dual.sh`; the evidence is
[`0167-evidence/dualmachine-v0.jsonl`](0167-evidence/dualmachine-v0.jsonl).

The design decision recorded there: `()` is a **time frame** whose head decides
everything that happens to the rest, `[]` is a **space frame** that orders and
collects and which no rule consumes, and `<L R>` is neither — it is a judgement
over a typed middle object (research 0070) and version 0 refuses it in every
position with a named reason rather than evaluating it. All 29 cases measured;
9 pass.

Three findings from building it, which are the substance rather than detail:

1. **Value move.** A head with no rule is not stuck, it is a value. Without
   that rule the machine cannot return `(x y)`, whose normal form is itself.
2. **Spine flattening.** `(a b c)` is right-nested, so a machine that
   re-marshals one bracket at a time never has `S`'s three arguments together —
   which is why the recorded `onS` rule could never fire at all.
3. **Frame ownership.** Arguments must belong to a frame explicitly; delimiting
   by depth on one shared stack is not enough once frames nest.

The remaining defect is one and it is structural: `S` and `iota` produce pending
applications as parts, and a closing frame assembles its parts without
evaluating them, so 14 of the 17 recorded cases cannot reach their expectation.
The fix is named in the specification and requires no change to any rule. No
failure was tuned away to make a case pass, and the suite keeps the two recorded
cases whose expectations are themselves inconsistent (`testFalse`, and the five
`testII`-family cases that share one term).

This remains substrate-side. Nothing in the DualMachine line is connected into
adva, and the boundary recorded in section 7 is unchanged.
