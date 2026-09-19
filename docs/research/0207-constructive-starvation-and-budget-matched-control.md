# 0207 — 可判定实验：`constructive` 的零贡献是作用退化，还是调度饥饿？

Status: 研究记录（research record）。**不是**原生准入，**不是** Seal，**不是**定理。
本记录**不修改** `adva`、`adva-machine`、`adva-library`。全部实测在工作区内完成。
日期：2026-09-19　执笔：DeepSeek Harness（deepseek-v4-flash-vision-exp），经 Mingli Yuan 会话指令

---

## 0. 一句话结论

> **`constructive` 的作用不是恒等。** 它单独运行时在 4 个种子上共做出 **82 次 best_updates**。
> 它在三计算集中零贡献的原因，是**调度饥饿**（373 次调度 / 20 万步），**不是作用退化**。

这**反驳**了 `TRIADICITY-LEVEL-RULING.md` §8.2 提出的解释路径，但**不反驳**该文的分层裁定本身。

---

## 1. 被检验的假设

`TRIADICITY-LEVEL-RULING.md` 裁定「三元性属于载体，不属于作用」，并观察到
labs-search 的 `constructive` 在 75 次三计算集运行中 `best_updates = 0`。
该文 §8.2 提出下一步：

> 用"作用层退化"解释 `constructive` 为何从不改进纪录，并设计一个**非恒等**的 constructive
> 作用（例如按 reward 加权的拼接），检验能否翻案。

**先检验更前置的一步**：`constructive` 的作用**是否**退化（恒等）？
若它本就非恒等，则无需设计新作用，解释方向应当改换。

判定依据（在机制自身词汇内）：

| 情形 | 单独运行 `constructive` 时的预期 |
|---|---|
| 作用恒等（退化） | `best_updates = 0` —— 恒等作用不改变任何候选 |
| 作用非恒等 | `best_updates > 0` |

这与 `direction_ruling_probe.py` 的 (B) 段同构：那里用「改变数值的作用 vs 恒等作用」判定
三个事件；这里用「单独运行时能否更新纪录」判定 constructive 的作用。

---

## 2. 实验设计

固定：`length 64`，`iterations 200000`，`workers 1`，`scheduler-exploration 4.0`，
其余取默认（`initial_population 8`、`move_samples 32`、`construction_interval 32`、
`archive_size 16`、`recent_flip_window 8`），取 `e=4.0` 是因为原记录显示该值下
`constructive` 获得最多调度机会。

四组配置 × 4 个种子（seed 1–4），单一变量为 `--programs`：

1. `constructive` —— 单独运行
2. `temporal` —— 单独运行
3. `spatial` —— 单独运行
4. `temporal,spatial,constructive` —— 全三计算集（复现原始设定）

---

## 3. 结果

### 3.1 单独运行：`constructive` 做出实质贡献

| seed | `best_updates` | `accepted` | `improving_accepts` | `cumulative_best_gain` | 最终 best energy |
|---|---:|---:|---:|---:|---:|
| 1 | **20** | 3329 | 2933 | 1100 | 392 |
| 2 | **24** | — | — | — | 412 |
| 3 | **16** | — | — | — | 408 |
| 4 | **22** | — | — | — | 408 |
| **合计** | **82** | | | | |

`constructive` 单独运行 20 万步，**82 次改进全局纪录**，`mean_scheduler_reward = 1.32`。

**作用非恒等。** 若它是恒等，`best_updates` 必须恒为 0。

### 3.2 三计算集中：它被饿死

| seed | 全集中 `constructive` 的 `uses` | `accepted` | `best_updates` |
|---|---:|---:|---:|
| 1 | 93 | 0 | 0 |
| 2 | 92 | 0 | 0 |
| 3 | 89 | 0 | 0 |
| 4 | 99 | 0 | 0 |
| **合计** | **373 / 800,000 步 = 0.047%** | **0** | **0** |

同一 seed、同一长度、同一预算下，`constructive` 从 200,000 次调度降到 ~90 次。
**它没有机会贡献，而不是没有能力贡献。**

### 3.3 三组单独运行的对比（同预算）

| 程序 | seed1 | seed2 | seed3 | seed4 | 4 种子合计 best_updates |
|---|---:|---:|---:|---:|---:|
| `spatial` | 356 (17) | 396 (13) | **352 (20)** | 400 (17) | 67 |
| `temporal` | 380 (21) | — | — | — | 21（仅 seed1 测得） |
| `constructive` | 392 (20) | 412 (24) | 408 (16) | 408 (22) | **82** |
| 全三计算集 | **360** | **372** | **348** | **336** | — |

（括号内为 `best_updates`；能量越低越好）

**两点观察**：

1. **`constructive` 单独运行是三者中 `best_updates` 最多的**（4 种子 82 次，对比 `spatial` 的 67 次）。
2. **全三计算集在 4 个种子中有 3 个不劣于任何单独程序**（seed 2: 372 vs 396/412；
   seed 3: 348 vs 352/408；seed 4: 336 vs 400/408），**但在 seed 1 上更差**
   （组合 360 vs spatial 单独 **356**）。
   所以"组合有增益"**只在 3/4 个种子上成立，不是普遍成立**。

---

## 4. 裁定

| 命题 | 判定 | 依据 |
|---|---|---|
| `constructive` 的作用是恒等（退化） | **否** | 单独运行 82 次 best_updates |
| 它的零贡献源于作用退化 | **否** | 同上；且它在组合内只有 0.047% 的调度份额 |
| 它的零贡献源于调度饥饿 | **是（有支持）** | 同预算下 200,000 → ~90 次调度 |
| 全三计算集相对最优单程序有增益 | **3/4 种子成立，非普遍** | seed 1 上 360 > 356（spatial 单独更优） |

**对 `TRIADICITY-LEVEL-RULING.md` 的影响**：

- 该文的**分层裁定本身不受影响** —— 载体 vs 作用的分层是在手性立方上做的，
  证据是 81/81 矩阵单位律与「恰有一个恒等事件」，与这里无关。
- 该文 §8.2 提出的**解释路径（作用层退化）被本实验反驳**。
  `labs-search` 的第三个程序提供的是**另一类**退化：调度饥饿，
  而非手性立方那种「作用恰为恒等」。
- 该文把两处「第三个成员是空的」并列观察（手性立方的 `id`、labs 的 `constructive`），
  **本实验说明它们的机制不同**，不应归为同一个「作用层退化」。

**饥饿的机制（推断，未直接测量）**：UCB 冷启动。`constructive` 早期接受率低
（其候选来自归档拼接，初期归档小），奖励信号弱 → 被 UCB 压低 → 得不到新数据 →
奖励估计无法更新。形成自锁，与 `scheduler_exploration` 无关（原记录已证与该参数无关）。

---

## 5. 边界：什么没有被建立

- **没有设计新的非恒等 constructive 作用。** 本实验证明无需如此：现有作用已非恒等。
  原计划的那一步（按 reward 加权重写拼接）**未执行**。
- **没有证明"调度饥饿"是唯一原因。** 只证明它在同预算下仅获 ~90 次调度，
  且其在组合内的 `accepted = 0`（组合内 0 接受 vs 单独运行 3329 接受）
  同时受调度量和上下文影响，二者未分离。
- **未测 `e` 取其他值的情形。** 固定 `e = 4.0`；原记录显示 `e` 是 `uses` 的杆杆，
  本实验没有重扫该轴。
- **未测长度 64 以外的情形**，未测多 worker。
- **`temporal` 只有 seed 1 的数据**（其余种子的该项未采集），故其 4 种子合计不完整。
- **未触及 `free`。** labs 循环中 `free` 全程 `AdapterUnavailable`，与本实验无关。
- **全部为研究侧**：只调用已构建的 `adva-labs-search` 二进制，未改任何源码，
  未产生 `claims.toml` 条目，未签发 `Seal`。

---

## 6. 复现

```bash
cd /Users/mingli/work/public/labs-run
B=/Users/mingli/work/public/adva/target/release/adva-labs-search
for S in 1 2 3 4; do
  for P in constructive spatial temporal,spatial,constructive; do
    $B search --length 64 --iterations 200000 --workers 1 --seed $S \
       --programs $P --scheduler-exploration 4.0 --output /tmp/s${S}-$(echo $P|tr ',' '_').json
  done
done
```

读 `workers[0].programs[]` 中 `program == "constructive"` 的 `uses` / `accepted` / `best_updates`。

---

## 7. 本记录自身的错误登记

| # | 错误 | 如何被发现 |
|---|---|---|
| 1 | 首轮把 `temporal` 的单程序对照漏采 3 个种子，导致其合计不可比 | 汇总时发现该行只有 seed 1 |
| 2 | 未先读 `--programs` 的可用取值就写第一版对照脚本 | 先读 `search --help` 后才修正 |
| 3 | **声称"全三计算集在每个种子上都优于任何单独程序"** —— 只看了 `best_updates` 大就下结论，未逐种子比对最终能量 | 写记录后逐数字核实，发现 seed 1 上组合 360 而 spatial 单独 356，**组合更差**。已改为"3/4 种子成立" |

（#3 与 `TRIADICITY-LEVEL-RULING.md` §6 的 #4「把噪声读成单调趋势」是同类错误：
在不该概括的地方下了概括。§0 的主结论未受影响。）

---

## 附录：English summary

**Decisive experiment: is `constructive`'s zero contribution action degeneracy or scheduling starvation?**

The ruling document proposed explaining `constructive`'s zero record-setting by action-layer
degeneracy. Before designing a non-identity replacement, this experiment tested the antecedent:
*is* its action degenerate?

Single-variable design, `length 64`, 200k iterations, 1 worker, `e = 4.0`, seeds 1–4, varying only
`--programs` across {`constructive`}, {`temporal`}, {`spatial`}, and the full triadic set.

**Result.** Run alone, `constructive` makes **82 best_updates across 4 seeds**
(20/24/16/22), with 3329 accepted moves and `cumulative_best_gain = 1100` at seed 1 — the highest
`best_updates` of the three programs tested (spatial: 67 over 4 seeds). Inside the full triadic set
it receives **373 scheduling uses out of 800,000 steps (0.047%)** and makes **zero**
best_updates.

Regarding the full triadic set: it is no worse than every single program in 3 of the 4 seeds, but in
seed 1 it is worse (360) than `spatial` alone (356), so the combination's advantage is not general.

**Verdict.** Its action is **not** the identity, and degeneracy is **not** the explanation; the
observed behaviour is **scheduling starvation**. The ruling document's layering (triadicity belongs
to the index structure, not to the actions) is unaffected, since its evidence comes from the
chirality cube (81/81 matrix-unit law, exactly one identity event). But its §8.2 explanatory path is
refuted, and the two "empty third member" observations — the cube's `id` and labs' `constructive` —
have **different** mechanisms and should not be grouped as one action-layer degeneracy.

**Scope.** Research record only. No source modified; only the prebuilt `adva-labs-search` binary was
invoked. No native admission, no Seal, no `claims.toml` entry. Bounded to length 64, `e = 4.0`,
200k steps, seeds 1–4. `temporal` alone was collected for seed 1 only. No non-identity constructive
action was designed, because the experiment showed none was needed.

---

## Repository registration

Source document: `public/CONSTRUCTIVE-STARVATION-EXPERIMENT.md` (work area, not committed). The body below is that document's text, unedited.

**This note declares its own limit: the run evidence is NOT packed into this repository.** The raw search reports (276 JSON files) and the prebuilt `adva-labs-search` binary used here live in `/Users/mingli/work/public/labs-run/` and are not committed. No checker ships with this note. Where no check exists, the note says so, and the claim is not made beyond what the cited runs show.

Direction: Mingli Yuan's continuing finite-observer and open-world question. Implementation, measurement and record: DeepSeek Harness (deepseek-v4-flash-vision-exp), submitted through his account as authorized proxy; not his authorship, review, endorsement or correctness guarantee.

**Superseded by 0208.** A later note may supersede this one; it does not rewrite it.
