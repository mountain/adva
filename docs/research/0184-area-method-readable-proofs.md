# 0184 — 消点法：面积法内核生成可读证明，逐步可复核（张景中可读机器证明的一轮有界试跑）

- Status: bounded, external exact computation
- Contract: `experiments/zhang_area_method/contract.json`
- Checker: `experiments/zhang_area_method/calibration.py`
- Retained evidence: `experiments/zhang_area_method/evidence.json`
- Run: `ExternalExactPass`, 22 acceptance checks true, 985 assertions, 6.98 s, no subprocess
- Claim: `adva.bounded-experiment.zhang-area-method.v0`

## 1. 这一轮要问什么

0183 检验的是**例证法**：用有限个实例认证一个恒等式，产物是"网格上处处为零"。这一轮问的是同一批资料里的另一半——**消点法（面积法）**，它的产物不是恒等判定，而是**可读的推理步骤**：按构造逆序消去被构造的点，每一步由一条具名引理给出，最后只剩自由点的量，用域运算判定。

方法的可执行定义取自 Narboux 对 Chou–Gao–Zhang《Machine Proofs in Geometry》的面积法 Coq 形式化（来源与取回情况见 0183 §2.5 与 `adva-library/zhang-jingzhong-finite-example-point-elimination-external-reference-v0.md` §2.5）：只允许三种几何量、构造必须写成构造序列、消点按构造的逆序、每步都有消去引理。

## 2. 内核是什么

- **构造**：`on_line_d`（定比点）、`is_midpoint`、`inter_ll`（两线交点）、`affine_comb`（仿射组合）。
- **三种量**（`evidence.json` 的 `geometry_semantics` 逐条给出定义）：
  - `S(A,B,C)` = 齐次三元组的 3×3 行列式，即**二倍有向面积**——取二倍是为了让所有引理系数保持整数；
  - `R(A,B,C,D)` = 使 `B − A = λ(D − C)` 的有向 λ，按 `dot(B−A,D−C)/|D−C|²` 计算，**仅当 AB ∥ CD 时**才是有向距离之比；
  - `Py(A,B,C) = AB² + BC² − CA²`。
- **14 条具名引理**（`on_line_d_area`、`on_line_d_pyth`、`midpoint_area`、`midpoint_pyth`、`inter_ll_area`、`inter_ll_pyth`、`ratio_area`、`ratio_complement_area`、`ratio_as_pythagoras`、`area_swap`、`area_cyclic`、`pyth_swap_ends`、`affine_comb_area`、`affine_comb_pyth`）：每条都**两次**验证——一次作为**多项式恒等式**精确验证（`n1*d2 − n2*d1 == 0`，不是抽样），一次在 40 个定种子有理实例上核对（14 × 40 = 560 次，全部吻合）。
- **每一步都是可读的**：保留的步骤记下所用引理、被消去的点、被改写子项的位置、以及改写前后的表达式字符串。六条证明共 **136 步**（`menelaus` 另有 3 步辅助改写）。

## 3. 证明与结果

| 命题 | 结果 | 消去步数 |
| --- | --- | ---: |
| 三中线共点（`S(G,C,M_ab) = 0`） | Proved | 27 |
| 重心分中线 2∶1（`R(A,G,A,M_bc) = 2/3`） | Proved | 22 |
| Ceva（有理参数 r_D=1/3, r_E=2/5, r_F=3/4） | Proved | 27 |
| Menelaus（有向乘积 = −1） | Proved | 43 |
| Apollonius 的勾股差形式 | Proved | 5 |
| 平行四边形对边之比 `R(A,B,D,C) = 1` | Proved | 12 |

**每一步都被独立复核**，而且是两条互不相同的路子（`replay_verdict`）：首先把轨迹序列化成 JSON 再重新解析，检查记录的位置上确实是记录的子项、按引理名重新推导右端、并把重排后的结果与记录的"改写后"字符串比较（结构复现 136/136）；然后**另外**把改写前后的子项串重新解析，在实际构造里按精确有理函数求值并比较——这一步**完全不用改写代码**（语义复核 136/136）。也就是说，轨迹不是被信任的，而是被重算的。

`R` 这类量还额外核对了它成立的前提：用到 `R` 的三条证明都检查了相应线段**确实平行**（`ratio_parallelism_verified`，平行残差恒为零）。

## 4. Unknown 才是这一轮最有价值的部分

内核只有两种结局：`Proved` 与 `Unknown`。**没有 `disproved`。** 四条 `Unknown` 各自说明理由：

1. **Pappus** —— `Unknown: construction not implemented`。Pappus 需要对边交点（含由 `on_parallel` / `on_inter_parallel_parallel` 产生的**无穷远点**），本内核不实现。这正是 0181/0182 用吴法做过的同一个命题：**同一命题，三种方法，能否做到是不同的**。
2. **`pyth_middle_argument`** —— `Py(A,M,B) = −Py(A,B,A)/4`（M 为 AB 中点）。这是一个**真命题**（两边都等于 −|AB|²/2），但因为被消去的点 M 恰好落在 `Py` 的**中间**参数位置，内核不实现该情形，于是报 `Unknown`；独立实例检查在同一条目里记录了它在 12/12 个精确实例上成立。这是"**Unknown 不是否证**"最干净的一个具体例证：内核做不到，而命题为真。
3. **`centroid_ratio_3_1_falsified`** —— 故意写成 3∶1 的假命题。消去跑完后残差是**非零常数 −7/3**，内核报 `Unknown`（不是 disproved）；另在显式有理见证 A=(0,0), B=(1,0), C=(0,1) 上取值 −7/3 且非退化条件全部成立，**该假命题在这一点上被否证**——并且这一否证被明确记为"控制项，不是内核结局"。
4. **`ceva_rational_wrong_parameter_falsified`** —— 参数改成 r_F=1/2 的假命题，残差是非零有理函数；在同一见证上取值为 **2/11**（可以手算核对）。

## 5. 自证伪：三条控制，两条被抓、一条没抓

- 把 `on_line_d_area` 的第二项系数**翻符号**：被三个互相独立的检查同时抓住（引理自身的符号验证、目标消不下去、复盘的语义逐步检查），复盘在第 3 步首次报出"改写前后的子项作为精确有理函数不相等"。
- 把 `midpoint_area` 的仿射系数用错（把中点当 (1/3)Q + (2/3)R）：同样被三处抓住，复盘在第 2 步首次报出。
- **把消去顺序改成按构造顺序（而非逆序）：没有被抓住。** 在那组构型下这些引理恰好是合流的，目标仍然在 7 步内关闭。这条**阴性结果被原样保留**，并把"必须被抓"的验收只施加于前两条故意破坏的引理。

把没抓住的控制留在记录里，比让它消失更有价值：它说明本内核的"抓到"来自引理本身的精确性与复盘的逐步语义检查，而不是来自顺序这类约定。

## 6. 残留与不作声明

- 这是**外部精确计算**（Python + `fractions.Fraction`），不是原生证书：没有 Rust witness、没有 Seal、没有几何目录准入，Pascal 生根的生长义务仍然 Open。
- **没有解除任何非退化条件**：关闭的目标只在所记录的分母不 vanish 的开集上成立；每条证明都记下了自己的非退化条件（例如 `medians_concurrent` 记下两处分母，并精确验证它们不恒为零），但这只是记录，不是解除。这与 0181/0182 的处境相同，也与 0183 §5.5 里"图卡分母 = 吴法首位"的观察相呼应。
- **没有跑任何吴法式交叉核对**（无 Gröbner、无特征链、无伪余式）：引理本身就是全部判定过程。
- 未实现的构造与情形已在 `what_is_not_implemented` 里逐条列出：`on_line`（比值自由的点）、`on_parallel(_d)`、`on_inter_line_parallel`、`on_inter_parallel_parallel`、`on_perp(_d)`、`on_inter_line_perp`、`is_circumcenter`、`is_orthocenter`、`is_centroid`（作为构造子）、以及 `Py` 中间参数含被消去点的情形。
- 本机**没有 sympy**，可选的符号交叉核对因此未运行，并被如实记为不存在；没有任何证书步骤依赖它。
- 所有算术都是 `Fraction`，且每次有理函数求值与数值求值都过一道运行期守卫（值不是 `Fraction` 就抛 `TypeError`），因此浮点数**不可能静默混入**证书步骤（`floats_in_certified_steps: 0`）。
- 本轮不涉及费根堡、Arakelov、镜对称或本仓自身的几何生长线。

## 7. 复现与确定性

```
cd experiments/zhang_area_method
python3 calibration.py        # 重写 evidence.json，退出码 0
```

只用标准库即可运行（本机 `python3` 3.14.6）。两次同参运行除单个 `cost` 键外**逐字节一致**；checker 自己声明的正文摘要 `aeb642b15042c4587e398f007ecf2c444f0104b0940c7bad6ed51e11448531f8` 我用它文档化的算法（去掉 `cost` 后 `json.dumps(indent=2, sort_keys=True)` 取 sha256）**独立复算吻合**。成本：985 条断言、6.98 秒、27 075 次多项式乘法、7 283 次项求值。

## 8. 出处与核查方式

本轮由本会话委派的一个子代理实现（只写 `experiments/zhang_area_method/` 三个文件，未触碰其他路径，未运行任何改变状态的 git 命令）。交付后我做的是**核查而不是采信**：把它复制到临时目录独立复跑，比对除 `cost` 外的全部字节、按它文档化的方法重算自证摘要、逐项读取 22 条验收结果与四类 `Unknown` 的理由、确认 `disproved` 这一结局在内核中不存在、确认阴性控制被保留。上述数字都来自这次独立复跑与最终保留的证据文件。

## 9. 与 0181/0182/0183 并列看

同一批平面关联命题，三种产物：

| 轮次 | 方法 | 产物 | 非退化条件 | 已知代价 |
| --- | --- | --- | --- | --- |
| 0181 / 0182 | 吴法（伪除） | 多项式余式为零 | 必须记录首位系数（0182：120 项 6 次） | 展开是全部代价（720 项 8 次，整轮 32.9 秒） |
| 0183 | 例证法（有限实例） | 网格上处处为零 | 恒等式形式**不需要**；带假设的命题靠图卡，图卡分母 = 吴法首位 | 729 至 15625 次求值，整轮 9.7 秒 |
| 0184 | 消点法（面积法） | **136 步可读推理**，每步可重算 | 记录但未解除 | 6.98 秒，27 075 次多项式乘法，且在 Pappus 上停住 |

三条路各自的强项不同：吴法给出最一般的多项式表述，例证法把判定换成求值，消点法给出人能读、能逐步核对的过程——而消点法在本内核里恰好停在了吴法能做到的 Pappus 上。
