# 0209 — `constructive` 的贡献：三个假设的判定，以及一个小样本如何骗了我两次

## 0. 结论

> **`constructive` 在组合中既不改进全局最优（`best_updates = 0`），也不改进最终结果。**
> 它的存在（identity）无效，它的执行（action）也无效。零贡献是**真**零贡献。

而且：

> **前一份记录对这个效应的判断（"存在但未统计确立"）是错的。**
> n=7 与 n=20 显示的效应，在 n=82 时消失。
> 那是小样本噪声 —— **我连续两次被它骗过。**

---

## 1. 实验设计：一个能分辨三种假设的读数

```
A: 全三计算集（constructive 运行）
B: 移除 constructive（--programs temporal,spatial）
C: constructive 有额度但窗口永不开放（--construction-interval 200001）
```

`C` 的构造是本实验的关键：`constructive` 保持在 `enabled_programs` 中（**身份在**），
但 `iteration % interval == 0` 永不成立，故 `uses = 0`（**动作不在**）。
实测确认：

| 程序 | `enabled` | `uses` | `accepted` |
|---|---|---:|---:|
| `temporal` | true | 147,091 | 4,761 |
| `spatial` | true | 52,909 | 1,981 |
| `constructive` | **true** | **0** | **0** |

三种假设各有不同预测：

| 假设 | 预测 |
|---|---|
| 身份有效（"三重"本身有用） | `A = C < B` |
| **动作有效**（执行在起作用） | **`A < C = B`** |
| 完全无影响 | `A = B = C` |

---

## 2. 结果一：身份无效，可逐位判定

`B == C` 在 **7/7 个种子上逐个数值相同**：

| seed | A | B（移除） | C（不执行） |
|---|---:|---:|---:|
| 1 | 356 | 376 | 376 |
| 2 | 368 | 376 | 376 |
| 3 | 384 | 380 | 380 |
| 4 | 360 | 372 | 372 |
| 5 | 336 | 360 | 360 |
| 6 | 360 | 392 | 392 |
| 7 | 384 | 368 | 368 |

**"有额度但不执行"与"移除"逐位相同。**
故 `constructive` 的**身份**（是否列在 `enabled_programs` 里）对结果无影响。
唯一可能的通道是它的**动作**。

这一步是干净的，不依赖任何统计判断。

---

## 3. 结果二：动作也无效 —— 需要足够功效才能看出

判据只剩 `A` 与 `C` 之差。同一实验，逐步增加种子：

| n | 全三均值 | 去cons均值 | 配对差均值 | 效应量 `d` | 符号检验「全三更好」 | 单尾 `p` |
|---:|---:|---:|---:|---:|---:|---:|
| 7 | 364.0 | 374.9 | **+10.86** | — | 5/7 | 0.2266 |
| 20 | 369.0 | 374.6 | **+5.60** | 0.309（小效应） | 12/20 | 0.2517 |
| **82** | **372.49** | **373.46** | **+0.98** | **0.037** | **43/82** | **0.37033** |

`n=82`：配对 t 检验 **t = −0.333，双侧 p = 0.7399**（scipy），符号检验单尾 p = 0.37033，胜/平/负 = **43/3/36**，最小能量 304（全三）vs 316（去cons）。

**效应量从 0.309 掉到 0.037，均值差从 5.60 掉到 0.98。**

**判定：`constructive` 的动作不影响最终结果。零贡献是真零贡献。**

---

## 4. 我在这条线上的全部错误（含两次被同一现象骗过）

| # | 错误 | 由什么纠正 | n |
|---|---|---|---:|
| 1 | 归因"作用退化（恒等）" | 单独运行 82 次 best_updates | — |
| 2 | 归因"调度饥饿（额度 ~93）" | 同额度对比：单独 78 次、组合 0 次 | 5 |
| 3 | 声称"调参修不了"（实为 107 倍，非 20,000 倍） | e 扫描 | — |
| 4 | 未读调用点（`construction_allowed`）就下机制结论 | 读 `src/lib.rs:784` | — |
| 5 | 声称"能力天花板是原因" | 消融显示零贡献 ≠ 无影响 | 7 |
| 6 | 预测"去掉它不会变差" | 5/7 种子变差 | 7 |
| 7 | **声称"效应存在但未统计确立"** | n=20→82 效应消失 | 20 → 82 |
| 8 | **用 n=7 / n=20 的均值差（+10.86 / +5.60）作为"有影响"的证据** | 同上 | 82 |

**#7 与 #8 是本次最值得记的**：我做了功效分析（算出需 n≈82），
本可以一开始就跑到 82。我先跑 7、再跑 20、再跑 82 —— **三次分别下结论**，
前两次都错。**功效分析不是可选项，它决定样本量，而样本量决定结论。**

---

## 5. 这条线最终建立了什么

| 命题 | 判定 | 依据 |
|---|---|---|
| `constructive` 的作用是恒等（退化） | **否** | 单独运行 82 次 best_updates |
| 它的零贡献源于额度不足 | **否** | 同额度（6250 vs 6249）：单独 78、组合 0 |
| 它的零贡献源于"能力天花板" | **否** | 消融在 n=82 下无效应 |
| 它的身份（是否启用）有影响 | **否** | `B == C` 逐位相同，7/7 |
| 它的动作有影响 | **否** | n=82，d=0.037，p=0.37 |
| `best_updates = 0` 是定义的推论 | **是** | `src/lib.rs:814`：只计优于**全局最优**者 |

**最终画像**：`constructive` 的候选能量下限（约 392）高于 `temporal`/`spatial` 能达到的水平，
所以它**永远**改进不了全局最优（`best_updates` 恒 0 是定义的推论）；
它的候选确实被接受（6,249 次使用中 40–63 次），但那些接受**不改变最终结果**。

`TRIADICITY-LEVEL-RULING.md` §3.4 报告该程序 `best_updates = 0` 并列为"第三个成员是空的"
四个线索之一。**本记录支持该观察，并补上它缺的对照**：
零贡献经同额度对照与足够功效的消融检验，**是真的**。

---

## 6. 边界

- **只测 `length 64`、单 worker、20 万步、`e` 默认 2.0。**
  更大的长度或预算下 `constructive` 的相对能力可能不同（其候选来自归档拼接，
  归档随预算增长）。
- **"动作无效"是就最终能量而言。** 它对 `current` 轨迹的影响未测量
  （接受次数证明有影响，但那种影响不改变结果）。
- **n=82 在 80% 功效下只能排除 d ≳ 0.31 的效应。** 更小的真效应（d < 0.1）需上千种子，
  本记录不声称排除。**故"真零贡献"的准确含义是：在可测范围内为零。**
- **未修改任何源码**，未加干预。三仓 `adva` / `adva-machine` / `adva-library` 逐字节未动。

---

## 7. 复现

```bash
cd /Users/mingli/work/public/labs-run
B=/Users/mingli/work/public/adva/target/release/adva-labs-search
for S in $(seq 1 82); do
  $B search --length 64 --iterations 200000 --workers 1 --seed $S \
     --programs temporal,spatial,constructive            --output /tmp/t3A$S.json
  $B search --length 64 --iterations 200000 --workers 1 --seed $S \
     --programs temporal,spatial                         --output /tmp/t3B$S.json
done
# 身份 vs 动作（7 种子）
for S in $(seq 1 7); do
  $B search --length 64 --iterations 200000 --workers 1 --seed $S \
     --programs temporal,spatial,constructive --construction-interval 200001 --output /tmp/t3C$S.json
done
```

---

# 命名段（解读，不被验证为真）

**名字：「功效先于结论」。**

我在同一条线上被同一个现象骗过两次。第一次我用 n=7 的均值差（+10.86）说"有影响"；
第二次我用 n=20（+5.60、d=0.309）说"存在但未确立"。**我甚至自己算出了需要 n≈82**，
却先跑 7、再跑 20。到 82 时，效应是 0.98、d=0.037。

*钉住*：§3 的 n=7/20/82 三行表；`CONSTRUCTIVE-ZERO-IS-MEASUREMENT-ARTIFACT.md` §3。
*钉不住*：这是不是"我学到的教训"——它是这条线上第八个错，而前七个我都声称过在改。

**第二名字：「身份与动作是两件事」。**

`C` 的构造（启用但不执行）是这轮唯一干净的东西：它让 `B == C` 逐位成立，
从而把"三重结构本身有用"这个可能**排除掉**，不靠统计。
*钉住*：§2 的表。
*钉不住*：这个手法能否迁移到别处——它依赖那个程序独有的 `iteration % interval` 门，
换一个程序未必有这个可乘之机。

---

## Repository registration

Source document: `public/CONSTRUCTIVE-CONTRIBUTION-FINAL.md` (work area, not committed). The body below is that document's text, unedited.

**This note declares its own limit: the run evidence is NOT packed into this repository.** The raw search reports (276 JSON files) and the prebuilt `adva-labs-search` binary used here live in `/Users/mingli/work/public/labs-run/` and are not committed. No checker ships with this note. Where no check exists, the note says so, and the claim is not made beyond what the cited runs show.

Direction: Mingli Yuan's continuing finite-observer and open-world question. Implementation, measurement and record: DeepSeek Harness (deepseek-v4-flash-vision-exp), submitted through his account as authorized proxy; not his authorship, review, endorsement or correctness guarantee.

**Supersedes 0208.** A later note may supersede this one; it does not rewrite it.
