# 0209 — `constructive` 的零贡献：测量假象，而非退化

## 0. 结论

> `constructive` 在组合中 `best_updates = 0`，**既不是作用退化，也不是调度饥饿，
> 也不是能力天花板，而是测量假象**。
>
> `best_updates` 只计"改进**全局最优**"的次数。`constructive` 的候选能量下限
> （约 392）高于另两个程序可达到的水平（364–380），所以它**永远不可能**改进全局最优 ——
> 无论给它多少额度。与此同时它**持续被接受**（6,249 次使用中 40–63 次接受），
> 通过改变 `current` 影响整条搜索轨迹。

**判定依据**（同额度、只改上下文）：

| seed | `constructive` 单独（6,250 次） | 组合内（6,249 次） |
|---|---:|---:|
| 1 / 2 / 3 / 4 / 5 | **18 / 19 / 14 / 13 / 14** 次 best_updates | **0 / 0 / 0 / 0 / 0** |

额度差 1 次，结果差 78 次。**上下文决定，而非额度。**

---

## 1. 三种错误归因，依次被测量推翻

| # | 归因 | 被什么推翻 |
|---|---|---|
| 1 | **作用退化**（恒等，不做任何事） | 单独运行 4 种子 **82 次 best_updates**（20/24/16/22）。恒等作用不可能做出 82 次。 |
| 2 | **调度饥饿**（额度被压到 ~93 次） | 把额度提到 **6,249**（`--scheduler-exploration 500`，顶到资格窗上限），单独运行 78 次、组合内仍 0。**额度相同，结果相反。** |
| 3 | **能力天花板**（它到不了那个水平） | 部分成立但**不是原因**：它单独能到 392，而组合里另两个到 364–380，故它**永不可能**赢得全局最优。但这正说明零是**定义**的结果，不是能力不足的结果。 |

**真正的原因在第 3 条的另一面**：`best_updates` 这个量测的是"谁改进了全局最优"，
而 `constructive` 的贡献方式**不经过这个通道**。

---

## 2. 源码依据

```rust
// src/lib.rs:814-821
let mut best_gain = 0;
if proposal.candidate.energy < self.best.energy {
    best_gain = self.best.energy - proposal.candidate.energy;   // 只在与全局最优比较时才非零
    self.best = proposal.candidate.clone();
} else { self.stagnation += 1; }
...
self.scheduler.update(kind, accepted, current_gain, best_gain);
```

`best_gain > 0` 要求候选**严格优于全局最优**。`constructive` 达不到那个水平，
于是 `best_updates` 恒为 0 —— **这是定义的推论，不是测量发现**。

接受判据（第 988-1002 行）显示它并非不活动：

```rust
if proposal_energy <= self.current.energy { return true; }   // 改进 current 即被接受
let base_scale = (self.current.energy / length.max(1) / 4).max(1);
let cap = base_scale * stagnation_boost * 4;                 // 上坡容差 ∝ current.energy
if delta > cap { return false; }
```

`cap ∝ current.energy` —— 这解释了接受率为何随情境变化：

| 情境 | `constructive` uses | accepted | 接受率 | `current` |
|---|---:|---:|---:|---:|
| `constructive` 单独（6,250 步） | 6,250 | 127 | **2.03%** | 564 |
| `constructive` 单独（200k 步） | 200,000 | 3,329 | 1.66% | 576 |
| `spatial,constructive` | 6,249 | 63 | 1.01% | 380 |
| 全三计算集 | 6,249 | **40** | 0.64% | 532 |

**接受从未停止**（组合内 40–63 次），只是每次只改 `current`，不改 `best`。

---

## 3. 消融：零贡献不等于无影响

**预测**（由"它从不改进全局最优"推出）：去掉 `constructive` 不会使结果变差。

**检验**（`length 64`，200,000 步，7 种子）：

| seed | 全三 | 去掉 `constructive` | 仅 `constructive` | |
|---|---:|---:|---:|---|
| 1 | **356** | 376 | 392 | 全三更好 |
| 2 | **368** | 376 | 412 | 全三更好 |
| 3 | 384 | **380** | 408 | 全三更差 |
| 4 | **360** | 372 | 408 | 全三更好 |
| 5 | **336** | 360 | 428 | 全三更好 |
| 6 | **360** | 392 | 416 | 全三更好 |
| 7 | 384 | **368** | 392 | 全三更差 |
| **均值** | **364.0** | 374.9 | 408.0 | 5/7 |

**配对差（去掉 − 全三）= [20, 8, −4, 12, 24, 32, −16]，均值 +10.86。**

**但符号检验 `k=5/7, 单尾 p = 0.2266` —— 不显著。**

故本记录的判定是：

- **已建立**：`best_updates = 0` 不等于零贡献。去掉它平均使结果变差 10.9，
  但这个效应在 n=7 下**未被统计确立**。
- **未建立**：`constructive` 究竟通过什么通道贡献（改 `current` → 影响另两个程序的
  提议？还是别的）。本实验只证明"存在影响"，未指出路径。

**与邻座的结论一致**：`TRIADICITY-LEVEL-RULING.md` §3.4 报告配对消融为
`NotSupported`（W4 L1 / W3 L2），本实验得到 W5 L2。两次独立测量给出同类结果 ——
**都指向"移除它有时更好，但证据不足以支持'三重优于二'"**。

---

## 4. 这份记录推翻的各条（含我自己的）

| 来源 | 原结论 | 现状 |
|---|---|---|
| 本会话 · 第一份 | 零贡献 = 调度饥饿 | **推翻**（同额度下单独运行 78 次） |
| 本会话 · 第二份 | 两道门（资格窗 × UCB）决定份额 | **测量保留**（二维表为真），**归因推翻**（份额不是零贡献的原因） |
| 本会话 · 第二份 | "提高预算不能改善结果" | **保留**：预算扩 70 倍，能量均值 360.0 → 389.3 |
| 本会话 · 第二份 | "参数不是答案" | **修正为**：参数决定份额，份额**不是**决定因素；决定因素是 `best_updates` 的定义 |
| `TRIADICITY-LEVEL-RULING.md` §8.2 | 用"作用退化"解释零贡献 | **推翻**（第一份已推翻，本记录给出替代） |
| `TRIADICITY-LEVEL-RULING.md` §3.4 | `constructive` 零贡献（可能被读作无影响） | **部分推翻**：零 `best_updates` 是度量假象，消融显示有影响（未显著） |

---

## 5. 边界

- **效应未统计确立。** n=7，符号检验 p=0.2266。要确立需要更多种子。
- **未指出贡献路径。** 只知"有影响"，不知经由什么。
- **`best_updates = 0` 是定义推论**：`constructive` 的能量下限高于另两者，故必然为 0。
  本记录把这个推论**测出来了**（下限 392 vs 对手 364–380），但它不是发现。
- **只有 `length 64`、单 worker、200k 步。** 未测其他长度与多 worker。
- **未修改任何源码。** 未加干预，未改度量。
- 三仓 `adva` / `adva-machine` / `adva-library` 逐字节未动。

---

## 6. 复现

```bash
cd /Users/mingli/work/public/labs-run
B=/Users/mingli/work/public/adva/target/release/adva-labs-search
# 同额度、只改上下文
for S in 1 2 3 4 5; do
  $B search --length 64 --iterations 6250   --workers 1 --seed $S --programs constructive --output /tmp/A$S.json
  $B search --length 64 --iterations 200000 --workers 1 --seed $S \
     --programs temporal,spatial,constructive --scheduler-exploration 500 --output /tmp/B$S.json
done
# 消融
for S in 1 2 3 4 5 6 7; do
  $B search --length 64 --iterations 200000 --workers 1 --seed $S --programs temporal,spatial,constructive --output /tmp/ab7_a$S.json
  $B search --length 64 --iterations 200000 --workers 1 --seed $S --programs temporal,spatial --output /tmp/ab7_b$S.json
  $B search --length 64 --iterations 200000 --workers 1 --seed $S --programs constructive --output /tmp/ab7_c$S.json
done
```

---

## 7. 我在这条线上的错误（连续第五轮，同一类）

| # | 错误 | 由什么纠正 |
|---|---|---|
| 1 | 归因"作用退化" | 单独运行 82 次 best_updates |
| 2 | 归因"调度饥饿" | 同额度对比（6250 vs 6249） |
| 3 | 声称"调参修不了"（实为 107 倍而非 20,000 倍） | e 扫描 |
| 4 | 未读调用点（`construction_allowed`）就下机制结论 | 读 `src/lib.rs:784` |
| 5 | **声称"能力天花板"是原因** | 消融显示零贡献 ≠ 无影响 |
| 6 | 预测"去掉它不会变差" | 5/7 种子变差 |

**共同点**：每一次我都在**一个通道**（`best_updates`、`uses`、`current`）里找原因，
而真相是**多个通道**，且我用作判据的那个通道**不承载**该程序的作用。

这与此前几轮（把噪声读成趋势、在不该概括处概括、只看两行就判"不吻合"、
没读调用点就下断言）是同一根：**把单一视角的读数当成对象的全部。**
已连续五轮，无法声称已改，只能登记。

---

## 附录：English summary

**`constructive`'s zero contribution is a measurement artifact, not degeneracy.**

Three successive attributions are each refuted by measurement.

1. *Action degeneracy* — refuted: run alone it makes 82 `best_updates` over 4 seeds.
2. *Scheduling starvation* — refuted by a budget-matched comparison: at ~6,250 uses it makes
   18/19/14/13/14 `best_updates` alone and **0** inside the triad, with the same seed, length, and
   quota. Quota differs by one use; outcome differs by 78 updates.
3. *Capability ceiling* — true but not the cause. Its energy floor (~392) lies above what the other
   two reach (364–380), so it can **never** win the global-best comparison, whatever its quota.

The real reason: `best_updates` counts only strict improvements to the **global best**
(`src/lib.rs:814-821`), and `constructive` contributes through the **`current`** state instead —
accepted 40–63 times out of 6,249 uses inside the triad. Its acceptance rate tracks
`cap ∝ current.energy` (2.03% → 0.64% as `current` falls), so it keeps contributing; it just never
enters the channel being counted.

**Ablation.** Seven seeds: full triad 364.0 mean energy versus 374.9 without `constructive`
(paired mean +10.86, 5/7 wins). A sign test gives **p = 0.2266**, so the effect is suggestive but
**not statistically established**. This is consistent with the neighbouring record's independent
ablation (`NotSupported`, W4 L1 / W3 L2); this run gives W5 L2.

**Scope.** Research record only; no source modified, only the prebuilt binary invoked. Length 64,
single worker, 200k steps, n=7. The contribution pathway is **not** identified — only the existence
of an effect. Three repositories byte-unchanged.

---

## Repository registration

Source document: `public/CONSTRUCTIVE-ZERO-IS-MEASUREMENT-ARTIFACT.md` (work area, not committed). The body below is that document's text, unedited.

**This note declares its own limit: the run evidence is NOT packed into this repository.** The raw search reports (276 JSON files) and the prebuilt `adva-labs-search` binary used here live in `/Users/mingli/work/public/labs-run/` and are not committed. No checker ships with this note. Where no check exists, the note says so, and the claim is not made beyond what the cited runs show.

Direction: Mingli Yuan's continuing finite-observer and open-world question. Implementation, measurement and record: DeepSeek Harness (deepseek-v4-flash-vision-exp), submitted through his account as authorized proxy; not his authorship, review, endorsement or correctness guarantee.

**Supersedes 0208.** **Superseded by 0210.** A later note may supersede this one; it does not rewrite it.
