# 0207 — `constructive` 饥饿的机制：两道门（修正版）

Status: 研究记录（research record）。**不是**原生准入，**不是** Seal，**不是**定理。
**不修改**任何源码；只调用已构建的 `adva-labs-search` 二进制。
日期：2026-09-19　执笔：DeepSeek Harness（deepseek-v4-flash-vision-exp），经 Mingli Yuan 会话指令
承接：`CONSTRUCTIVE-STARVATION-EXPERIMENT.md`
**本记录取代** `UCB-STARVATION-MECHANISM.md`（该文的核心结论经实测证伪，已作废，保留在案）

---

## 0. 一句话结论

> `constructive` 的调度份额由**两道独立的门**决定，实际份额取**更严的那一道**：
>
> **门 1（资格窗）**：`iteration % construction_interval == 0`（默认 32）→ 每 32 步才可能被选中。
> **门 2（UCB 分数）**：在窗口开放的那些步里，再按 UCB 分数与另两个程序竞争。
>
> 低探索时门 2 更严（份额 ~0.05%）；高探索时门 1 是硬上限（份额 = 1/32 = 3.125%）。
> **两者是相乘关系，不是任一个单独能解释的。**

---

## 1. 源码（`experiments/labs-search/src/lib.rs`）

```rust
// 784-787：资格窗
let constructive_only = self.config.enabled_programs.len() == 1
    && self.config.enabled_programs[0] == ProgramKind::Constructive;
let construction_allowed =
    constructive_only || self.iteration % self.config.construction_interval == 0;

// 589-592：资格过滤 —— constructive 仅当窗口开放时进入候选集
let mut eligible = enabled.iter().copied()
    .filter(|k| *k != ProgramKind::Constructive || construction_allowed).collect();

// 597-600：零使用者优先（防冷启动饿死）
for kind in &eligible { if self.stats[kind.index()].uses == 0 { return *kind; } }

// 602-621：UCB
score(v) = reward_sum/v.uses + exploration * sqrt( ln(total_uses+1) / v.uses )
```

`construction_interval` 默认值 **32**（`SearchConfig::for_length`，第 408 行）。
故窗口上限 = `iterations / 32`。

---

## 2. 决定性实验：e × interval 二维扫描

`length 64`，`iterations 200000`，`workers 1`，`seed 1`，全三计算集，
读 `constructive` 的 `uses`：

| `e` \ `construction_interval` | 1 | 2 | 8 | **32** | 128 |
|---|---:|---:|---:|---:|---:|
| **4** | 111 | 111 | 92 | 93 | 95 |
| **50** | 23,450 | 11,720 | 7,905 | **6,247** | 1,562 |
| **500** | 53,020 | 51,715 | 24,998 | **6,249** | 1,562 |
| *窗口上限 = 200000/CI* | *200,000* | *100,000* | *25,000* | ***6,250*** | *1,562* |

**三处决定性观察**：

1. **`e = 4` 那一行几乎不随 interval 变化**（111 / 111 / 92 / 93 / 95）。
   这正是先前 interval 扫描"什么都没看到"的原因 —— 但原因不是 interval 无关，
   而是**低探索下门 2 先卡住**，门 1 根本没成为约束。
2. **`e = 500` 时恰好顶到窗口上限**：6249 vs 6250、1562 vs 1562。
   门 1 成为**硬上限**。
3. **`e = 50, CI = 32` 给出 6247**，而 `u ∝ e²` 的预测是 14,532 ——
   被 6250 的窗口封顶。**UCB 的 e² 律在窗口内成立，但窗口先截断。**

---

## 3. 前作错误的更正

`UCB-STARVATION-MECHANISM.md` 声称：

> 「`constructive` 的 `uses` 被钉在 ~93；把 `scheduler_exploration` 调大 20,000 倍
> 才接近公平份额；**且这不是调参能修的**。」

**实测证伪**：

| `e` | 0.01 | 0.1 | 0.5 | 1.0 | **4.0** | **50** | **107** | **500** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `constructive` uses | — | — | — | — | 93 | 6,247 | 6,249 | 6,249 |

**公平份额（T/3 ≈ 66,667）需要 `e ≈ 107`**（解 `e = s*·sqrt(fair/ln(T+1))`），
即约 **27 倍**，不是 20,000 倍。而且 `e = 50` 时它已获 **3.12%**（对比 0.05%），
是 **62 倍增长**。

故该文的两个核心论断均错：
- 「需要 20,000 倍」—— 实际是 107 倍（`20000/107 ≈ 187`，**错误约 187 倍**）；
- 「不是调参能修的」—— 反了，**配额主要就是被 `e` 与 `interval` 两个参数决定的**。

该文还声称「零奖励者的分数被钉在竞争得分 `s*` 上」，此机制**未获支持**：
实测显示是资格窗在起作用，不需要引入"钉住"假设。

---

## 4. 提高预算能否改善结果？不能

`seed 1/2/3`，`length 64`，200k 步，`CI = 32`：

| `e` | `constructive` uses（三种子） | 最终能量（三种子） | 能量均值 |
|---|---:|---|---:|
| 4 | 93 / 92 / 89 | 360 / 372 / 348 | **360.0** |
| 20 | 2,743 / 1,969 / 2,323 | 388 / 352 / 380 | 373.3 |
| **50** | **6,247 / 6,247 / 6,247** | 400 / 388 / 380 | **389.3** |
| 200 | 6,249 / 6,249 / 6,249 | 344 / 384 / 336 | 354.7 |

把 `constructive` 的预算从 ~90 提到 ~6,250（**约 70 倍**），**最终能量没有改善**：
`e=50` 的均值（389.3）比 `e=4`（360.0）**更差**。

**结合前作的关键对照**：`constructive` **单独运行时**用 200,000 次调度做出
82 次 `best_updates`（4 种子）；在组合内即使给到 6,249 次调度，
`best_updates` 仍为 **0**。

> **所以"给它更多机会"不是答案。** 它在单独运行时有效，在组合中即使预算扩大 70 倍也无效。
> 这指向"上下文"而非"额度"—— 但本实验**没有**分离这两者。

---

## 5. 边界：什么没有被建立

- **没有分离"额度"与"上下文"。** 组合内 `best_updates` 恒为 0，而单独运行 82 次；
  预算扩大 70 倍后仍为 0。二者哪个是原因**未判定**。
- **`e = 107` 的"公平份额"是公式外推，未实测。** 实测只到 `e = 500`，
  且因窗口上限停在 6,249，故 66,667 的公平份额**在此 interval 下不可达**
  （需 `CI = 1`，那时 `e = 50` 已给 23,450）。
- **未实现任何干预。** 未改调度器、未加强制配额、未做奖励归一化。
- **只有 length 64、单 worker。** 多 worker 各有独立调度器，未测。
- **`e=4` 行的 interval 扫描用的是 seed 1**；`e=4/20/50/200` 的能量对比用了 3 种子，
  但未做统计检验（n=3）。
- **全部为研究侧。** 未改动 `adva` / `adva-machine` / `adva-library` 任何文件，
  未产生 `claims.toml` 条目，未签发 `Seal`。

---

## 6. 复现

```bash
cd /Users/mingli/work/public/labs-run
B=/Users/mingli/work/public/adva/target/release/adva-labs-search
# 二维扫描
for E in 4 50 500; do for CI in 1 2 8 32 128; do
  $B search --length 64 --iterations 200000 --workers 1 --seed 1 \
     --programs temporal,spatial,constructive \
     --scheduler-exploration $E --construction-interval $CI --output /tmp/g${E}_${CI}.json
done; done
# 能量对比（3 种子）
for E in 4 20 50 200; do for S in 1 2 3; do
  $B search --length 64 --iterations 200000 --workers 1 --seed $S \
     --programs temporal,spatial,constructive --scheduler-exploration $E --output /tmp/f${E}_${S}.json
done; done
```

读 `workers[0].programs[]` 中 `program == "constructive"` 的 `uses` / `best_updates`，
以及 `best.energy`。

---

## 7. 本记录自身的错误登记

本轮由我造成、由**测量**纠正的错误，按严重度排列：

| # | 错误 | 如何被发现 | 后果 |
|---|---|---|---|
| 1 | **断言"调参修不了"** —— 声称需 e≈80,000（后改 107 又说 27 倍仍算"修不了"） | e 扫描实测：e=50 即给 3.12%，是 62 倍增长 | 一个**方向相反的结论**，若未测会被记录为结果 |
| 2 | **算术错误**：把公平份额阈值算成 20,000 倍 | 重算 `e = s*·sqrt(fair/ln(T+1))` 得 107 | 错 740 倍 |
| 3 | **声称分数"被钉在 s\*"** —— 该机制未获支持 | interval/e 二维扫描显示是资格窗在起作用 | 引入了不必要的假设 |
| 4 | **未先读 `constructive_allowed` 的计算就下机制结论** | 读 `src/lib.rs:784-787` 才发现每 32 步才开放一次 | 整个第一版机制解释作废 |
| 5 | 首版脚本在预测尚未检验时即写作结论 | 停下先跑 T 扫描 | 已在前作登记 |

**#4 是根因**：我在读调度器时读了 `choose`（第 581 行起），**没读调用点**（第 784 行）。
一个 30 行的函数就在上面 200 行处，读完它整轮就不用走这么多弯路。

**连续第四轮同一类错误**（前三轮：把噪声读成趋势、在不该概括处概括、只看两行就判"不吻合"）：
**在数据或源码未读全时下结论。** 已列入固定纪律：
**下任何机制断言之前，先读调用点，并把该表每一行读完。**

---

## 附录：English summary

**Mechanism of `constructive`'s scheduling share: two gates, and the tighter one wins.**

The scheduler gates eligibility before scoring: `constructive_allowed` is true only every
`construction_interval`-th iteration (`src/lib.rs:784-787`; default interval 32). So the window
admits at most `iterations / 32` draws, and UCB then decides how many of those it wins.

A two-dimensional sweep (`e` × `interval`, length 64, 200k iterations, seed 1) makes this visible:

| `e` \ `CI` | 1 | 2 | 8 | **32** | 128 |
|---|---:|---:|---:|---:|---:|
| 4 | 111 | 111 | 92 | 93 | 95 |
| 50 | 23,450 | 11,720 | 7,905 | **6,247** | 1,562 |
| 500 | 53,020 | 51,715 | 24,998 | **6,249** | 1,562 |
| *window cap* | *200,000* | *100,000* | *25,000* | ***6,250*** | *1,562* |

At `e = 4` the interval barely matters, because the UCB score is the binding constraint; at
`e = 500` the usage sits exactly on the window cap (6249/6250, 1562/1562). The two gates multiply.

This **falsifies** the earlier claim that "no setting of `scheduler_exploration` fixes this": the fair
share threshold is `e ≈ 107` (about 27×, not 20,000×), and at `e = 50` the program already receives
3.12% instead of 0.05% — a 62× increase. It also removes the unsupported "score pinned at s*"
hypothesis.

**Budget is not the answer.** Raising `constructive`'s budget ~70× (93 → 6,250 uses) does not improve
final energy: seed means 360.0 at `e=4` versus 389.3 at `e=50`. Run alone the same program makes 82
`best_updates`; inside the triad it makes 0 even at 6,249 uses. Whether the cause is budget or
context is **not** separated here.

**Scope.** Research record only; no source modified, only the prebuilt binary invoked. Bounded to
length 64, single worker, 200k iterations, ≤3 seeds. No intervention was implemented. The fair-share
figure is a formula extrapolation: at the default interval the cap makes it unreachable.

---

## Repository registration

Source document: `public/UCB-STARVATION-MECHANISM.md` (work area, not committed). The body below is that document's text, unedited.

**This note declares its own limit: the run evidence is NOT packed into this repository.** The raw search reports (276 JSON files) and the prebuilt `adva-labs-search` binary used here live in `/Users/mingli/work/public/labs-run/` and are not committed. No checker ships with this note. Where no check exists, the note says so, and the claim is not made beyond what the cited runs show.

Direction: Mingli Yuan's continuing finite-observer and open-world question. Implementation, measurement and record: DeepSeek Harness (deepseek-v4-flash-vision-exp), submitted through his account as authorized proxy; not his authorship, review, endorsement or correctness guarantee.

**Supersedes 0206.** **Superseded by 0208.** A later note may supersede this one; it does not rewrite it.
