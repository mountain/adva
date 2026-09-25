# 0236 — Two addresses at once, three time conditions, and what the closure changes

**Date**: 2026-09-25 · **Contract**: `experiments/two_address_exchange_v1/contract.json` ·
**Checker**: `calibration.py` · **Evidence**: `evidence.json` ·
**Paired test**: `tests/python/test_exchange_two_address.py`

**Status**: one bounded external exact calibration in Python with declared `sympy`
for resultants, Groebner bases and Sturm counts. No native certificate, no stable
API, no `ValueType`, no `OperationSpec`, no IR version, no Seal, no library
admission, no transport, no terminology home, no physical claim, no forecast and no
meteorological or reanalysis data. Notes 0228, 0233, 0234 and 0235 are cited, not
edited.

中文摘要：把 0228 的两个地址 $(a,b)$ **同时**用起来（$e(a,b)_i=3a_i+b_i$，6,561 点双射，
任一地址单独都不足以恢复细点；互度＝除法/余数对＋两套 81 值观察与其字符基），
并按三条声明的时间条件计算：**T1** 末尾**恰两个**格外状态（用九/用六、踦/贏 的结构位置，
一条放在中间、或放三个都必须被规则拒绝）；**T2** 三退出句＝**終養始**，闭合读作返回映射
不动点，$p=q=0$ 时非平凡分支恰为三次 $h^3+8h^2+64h-320=0$：**一个实出口**
$3.2035072879526181\ldots$ ＋一对共轭出口，与 0235 的水平 1 读法（**两个实分支**）并列且
断言 $1\neq2$；**T3** 穿越点三候选分别精算：年缝（第 0 侧）$2+\sqrt{8\sqrt{17}-20}$、
互度对角 $81$ 点的 $8$、谱穿越 $k=3c$ 的 $81$ 对（振幅 1）。三条硬控制全部执行：0228 §3
两点见证**自己**产生不可能性、§7 挤压被判退化、0235 恒等环复现。基线比较给出严格次序
$1<3.2035\ldots<5.6034\ldots$；"时间条件是否改变可达性"记 **NotDecided** 并给出理由。

## 1. Two addresses simultaneously

`e(a,b)_i = 3a_i + b_i` is exhausted over all 6,561 points: a bijection onto
`{0..8}^4`, every fixed-`a` and fixed-`b` fibre exactly 81, the pair recovering the
fine point and **neither address alone** doing so. Both readings of 0228 §2 are kept
apart — nested spatial (coarse cell / child) and ordered state (source / target) —
rather than identified by counting. The mutual measuring is the declared inverse
pair `a = floor(z/3)`, `b = z mod 3`, checked at every point, together with the two
81-valued observations `q_block`, `q_phase` and their character bases: the base-nine
carrier has 6,561 characters and 65 distinct Laplacian eigenvalues, the ternary base
has 9 distinct eigenvalues `3j` with multiplicity `C(8,j)2^j`, and the two spectra
meet exactly on `{0,3,6,9,12}` with the multiplicities reported beside them.

The mutual-measuring diagonal `a = b` is the 81 points `z = 4a` with every
coordinate in `{0,4,8}`, where `q_block = q_phase`. **It is not closed under the
declared translations**, so no time iteration is declared on it: closing only there
would repeat a spatial pattern in time, which is the extrusion of 0228 §7.

## 2. T1 — the factor-two extra block at the end

The twelve phases carry fourteen states: an extra block of **exactly two**
(`yong-9`, `yong-6`) at the declared end index 12, the structural position of
用九/用六 in Yi and of 踦/贏, the intercalary remainder, in Taixuan. Both negative
controls are **rejected by the declared rule and asserted, not narrated**: a block
starting at an interior index is refused with "the block must start at the declared
end of the twelve-phase cycle, index 12, not index 6", and a third extra state is
refused with "the block must hold exactly two extra states, not 3".

## 3. T2 — 終養始 as closure, and the change it makes

Read as periodic closure, the clause makes the end feed the beginning, so the
closure is the fixed point of the annual return. `h = 0` is always an exit because
`E_{p,q}(0) = 0` identically; the nontrivial branch is the exact quotient by `h`,
degree three with a `(p,q)`-free constant term, and at `p = q = 0`

$$512\bigl(E(h)-h\bigr)=h\bigl(h^3+8h^2+64h-320\bigr).$$

Its derivative has discriminant `−512`, so the cubic is strictly increasing: **one
real exit** `h* = 3.2035072879526181...`, isolated in `(3,4)` by exact rational
intervals and given in closed form by the depressed cubic
`y^3 + 128y/3 − 12224/27 = 0`, `y = h + 8/3`, whose resolvent roots are real and are
squared exactly in `Q(√4281)`; and **one conjugate pair of exits**,
`−5.6017536439763091 ± 8.2771295362453176 i`, certified non-real by the quotient
conic `h^2 + 11h + 935/4` with exact discriminant `−814`.

Beside it stands the level-one reading of note 0235, `E(h) = 1`, with `h^4 + 8h^3 +
64h^2 + 192h − 512 = 0` and **two** real branches, `1.6034490429...` and
`−5.6034490429...`, plus its conjugate pair. The run asserts `1 ≠ 2`, reports both
and substitutes neither: **the closure clause removes a real branch**, and the
scheme-one exchange question was posed on two.

## 4. T3 — the crossing point, three candidates, three amplitudes

1. **The year seam, side 0.** The time coupling of the declared shifted reference is
   `−31/512, −15/512` and ten zeros, so `max |d_m| = 31/512` sits at side 0, and the
   spatial amplitude there is `2 + sqrt(8 sqrt(17) − 20) = 5.6034490429...`,
   enclosed in `(5,6)` and attained on the negative branch. The run also corrected a
   modelling gap in the process: on a level-one branch the exact identity
   `8E = 6E_0 + E_0^2 + (h^2+4h−8E_0)(h^2/8 + 3h/4 + 3)` reduces the branch equation
   to `E_0^2 + 6E_0 − 8 = 0`, hence `E_0 = sqrt(17) − 3 = 1.1231056...` on side 1
   rather than the frozen level.
2. **The mutual-measuring diagonal.** 81 points, largest coordinate amplitude `8`,
   and as recorded above it carries no time iteration.
3. **The spectral crossing**, declared explicitly rather than dropped: a base-nine
   index and a ternary index cross when `k_i = 3c_i`, which is exactly **81 pairs in
   bijection**, with amplitude `1`. The intersection of the two Laplacian spectra is
   reported beside it as a separate quantity, because it is not the same thing.

## 5. Controls, the baseline, and what is not decided

The block-address witness of 0228 §3 fails any time iteration on the 81 coarse
labels **by itself**: the two points `(6,3,3,6)` and `(8,3,3,6)` share the block
`(2,1,1,2)` and take different blocks after `T_0`, and the label in question has 81
preimages and exactly two distinct successors, so no map `F` on the labels satisfies
`F(q_block(z)) = q_block(T_0 z)`. The 17,496 counted failures of the particular
equation are retained beside the witness, with the label step named. The extrusion
countermodel of 0228 §7 is reproduced, its period `(0,0,0,1)` verified as an exact
invariance of the extruded carrier and of its closure on the diagonal, and the
verdict is **Degenerate: not a time resource**. The identity-loop control of note
0235 is reproduced by exact rational continuation on both rectangles. The amplitude
floor of the first scheme is reproduced exactly: `J_inf = 1` at `(p,q) = (−2, 17/10)`,
off the discriminant variety.

The comparison is therefore an exact ordering, `1 < 3.2035072879526181... <
2 + sqrt(8 sqrt(17) − 20)`, between the first scheme's floor, the closure reading and
the level reading. **Whether the declared time conditions change what is reachable
is recorded as `NotDecided`**, with the reason: reachability needs a declared
protocol with a transition relation, whereas this run changes the equation of the
return and reports its algebraic consequences, and the first scheme's finding was
stated for the level reading only. Two further items are `Undecided` with retained
partial data: a crossing of the two Laplacian spectra as dynamic quantities (no
common carrier is declared) and a closed form for the realised closure root in a
field smaller than its splitting field.

Two draft errors made by the implementing agent are kept visible rather than
repaired in silence: a Cardano block with wrong depressed coefficients and then with
the resolvent roots treated as complex instead of real, and a first block-witness
counter that used the wrong label step and produced 20,412 instead of the declared
17,496.

## 6. Boundary

Nothing here is a statement about the atmosphere, the Tibetan Plateau, January, any
wind gap, any pressure centre or any forecast; the declared correspondence keeps its
data side Unavailable. The time direction is a declared order resource, not physical
time and not a causal or Lorentzian structure — 0228 §7 already records that even a
successful four-dimensional construction would not pick out physical time. No Rust
source, `Cargo.toml` or `Cargo.lock` changed, so the advance-surface base commit does
not move. Ruff is absent from the project virtual environment; the host's ruff 0.15.7
reports nothing on the two new Python files. Successive difference substitution is
not implemented.

Authored and checked by deepseek-v4-flash-vision-exp (DeepSeek Harness), submitted
through Mingli Yuan's authorized account proxy. Account use is not his authorship,
review, endorsement or correctness guarantee. One agent wrote the contract, the
checker and this note; there is no independent reviewer.
