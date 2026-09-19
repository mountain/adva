# Iota 共轭、对偶与 Zot 程序自接合

2026-09-19。研究与新增代码：ChatGPT（OpenAI）。本包是独立参考实验；读取现有仓库材料，没有启动三计算机，没有更改或推送仓库。

**已经实现纯 Iota 的复共轭、乘以虚单位、二阶表转置和伴随。** 共轭可以先做起来；把它接到任意程序的左右对偶，还需要一个保留应用、边界和观察的表示映射。当前不能把两件事直接等同。

## 1. 核对了哪些刚提交的材料

| 来源 | 本次读取版本 | 与问题直接相关的内容 |
| --- | --- | --- |
| `mountain/adva-iota` | `a9540b4d93076674ce2ea954ad7b08b1bb86fff5` | `frame_v1/materials/frame.md`、`algebra.py`、`check.py`、`frames.json`；唯一源组合子是 Iota，虚单位由复结构 J 表示 |
| `mountain/adva-machine` | `25818eb259dd8a16c50214e825a8b3af3d641333` | 9 月 19 日收到的 carrier matrix 材料；从 wedge / contraction 构造六维载体上的 Omega |
| `mountain/adva` | 当前检索最新 `e98592b7dc0c3fabba3fa897a491c78f5c55c45e` | 既有 Iota frame 接收文档与上游定义一致 |

关键原文：[Iota frame](https://github.com/mountain/adva-iota/blob/a9540b4d93076674ce2ea954ad7b08b1bb86fff5/frame_v1/materials/frame.md)、[frame 代数代码](https://github.com/mountain/adva-iota/blob/a9540b4d93076674ce2ea954ad7b08b1bb86fff5/frame_v1/materials/algebra.py)、[carrier 规范](https://github.com/mountain/adva-machine/blob/25818eb259dd8a16c50214e825a8b3af3d641333/spec/framework/carrier-matrix-v0.md)、[carrier 检查代码](https://github.com/mountain/adva-machine/blob/25818eb259dd8a16c50214e825a8b3af3d641333/knowledge/received/carrier-matrix-machine-2026-09-19-v1/materials/check.py)。各文件的 Git blob 记录在 `source-review.json`。

现有 `conjugate(t,a,inverse)` 计算的是换基相似变换 `t*a*inverse`。它给这次工作提供了运输框架，但还不是对数值做复共轭的函数。历史 `DUALMACHINE.md` 的双栈也有已记录的 S/Iota 缺陷，不能作为一般对偶定理使用。

符号分开使用：

| 符号 | 本报告中的意义 |
| --- | --- |
| \(\iota\) | 源组合子，\(\iota f=fSK\) |
| \(I\) | 恒等组合子或对应空间的恒等算子，依上下文标明 |
| \(i\)、\(J\) | 虚单位及其实坐标表示，\(J^2=-I\) |
| `.iota` 文件中的 ASCII `i` | 只编码源组合子 \(\iota\)，不编码虚单位 |
| carrier 文档的 \(\iota_j\) | 外代数收缩；与源组合子 \(\iota\) 是不同对象 |

## 2. 一个只用 Iota 的可执行共轭

先声明坐标表示，不改变用户教给我们的 Adva 列表结构。下面的四槽积只是本实验内部的坐标载体：

\[
Z(p,q,r,s)=\lambda k.k\,p\,q\,r\,s,
\qquad \operatorname{read}(Z)=(p-q)+i(r-s).
\]

槽位可先保留为任意符号；如果读成数值，假定它们来自允许减法的同一标量域。我们没有给解释器增加加减法、复数或矩阵原语。

\[
\begin{aligned}
C Z(p,q,r,s)&=Z(p,q,s,r),\\
J Z(p,q,r,s)&=Z(s,r,p,q),\\
N Z(p,q,r,s)&=Z(q,p,s,r).
\end{aligned}
\]

三个闭合 lambda 程序分别是：

```text
C = λz. z (λp q r s k. k p q s r)
J = λz. z (λp q r s k. k s r p q)
N = λz. z (λp q r s k. k q p s r)
```

它们用无 eta 优化的 S/K/I 括号抽象编译，再把所有 S/K/I 展开成 Iota。因此输出文件只有 `i` 和 `*`；`*AB` 表示应用，整串必须完整读完。没有声称最短编码。

| 程序 | 作用 | 纯 Iota 字符数，不含末尾换行 |
| --- | --- | ---: |
| `evidence/C.iota` | 复共轭 | 743 |
| `evidence/J.iota` | 乘以 i | 671 |
| `evidence/N.iota` | 整体取负 | 725 |
| `adjoint_evidence/transpose2.iota` | 2×2 表转置 | 743 |
| `adjoint_evidence/conjugate2.iota` | 2×2 表逐项共轭 | 3,809 |
| `adjoint_evidence/adjoint2.iota` | 2×2 表共轭转置 | 3,791 |

对任意四个形式槽位，编译后的程序经完整 beta 归约满足：

\[
\boxed{C^2=I,\qquad J^2=N,\qquad J^4=I,\qquad CJC=NJ=-J.}
\]

这些是所声明的构造子元组上的等式，不是对任意未类型化 lambda 项都声称同一性质。另一个直接按 Iota/S/K 规则重写的解释器，独立核对了 C、J、N 的输出槽位顺序。

例如 `Z(2,0,3,0)` 读为 `2+3i`；C 输出 `Z(2,0,0,3)`，读为 `2-3i`；J 输出 `Z(0,3,2,0)`，读为 `-3+2i`。这里的数字只用于说明读法，程序执行的是精确槽位交换。

## 3. 转置与共轭组合成伴随

用另一个四槽积表示表 \(M=\left(\begin{smallmatrix}a&b\\c&d\end{smallmatrix}\right)\)，其中每项都是上一节的复坐标。

\[
T(M)=\begin{pmatrix}a&c\\b&d\end{pmatrix},\qquad
\overline M=\begin{pmatrix}Ca&Cb\\Cc&Cd\end{pmatrix},\qquad
M^\dagger=T(\overline M).
\]

已把三个操作分别编译成纯 Iota，并在 16 个形式槽位上验证：\(T^2=I\)、逐项共轭平方为 I、转置与逐项共轭可交换、\((M^\dagger)^\dagger=M\)，以及全部输出槽位与公式一致。

因此，“对偶和共轭可以结合”在这个明确的线性载体上有可运行实例：矩阵转置表示对偶映射的坐标形式，共轭转置给出标准 Hermitian 配对下的伴随。尚未把一般 Adva 程序规定为矩阵，也没有给本纯 Iota 原型增加完整矩阵乘法库。

## 4. 新 carrier 材料中的共轭来自哪里

原材料已经给出 \(W=\Lambda^1E\oplus\Lambda^2E\)。在它声明的有符号基

\[
(e_1,e_2,e_3,e_{23},-e_{13},e_{12})
\]

上，按代码实际执行的 `c_2(c_1(c_0 .))` 顺序，独立重建得到

\[
\Omega=\begin{pmatrix}0&I_3\\-I_3&0\end{pmatrix},\qquad
\Omega^2=-I_6.
\]

这个符号约定使 \(\Omega=-J_{\rm canonical}\)，必须保留，不能把两者悄悄混同。

现在取外代数分级算子 \(\Gamma v=(-1)^{\deg v}v\)，定义

\[
\boxed{C=-\Gamma\vert_W=
\begin{pmatrix}I_3&0\\0&-I_3\end{pmatrix}.}
\]

由于每个 wedge 和 contraction 都翻转奇偶分级，\(\Gamma\) 与每个 \(c_j\) 反交换，也与三个 \(c_j\) 的乘积反交换。因此

\[
C^2=I_6,\qquad C\Omega C=-\Omega.
\]

本次还在原声明的 cube 上，从 enabled edges 重新计算配对 \(dx_i(g_j)\)，再重建 wedge、contraction 和 Omega；未调用原仓库的检查器。由此，在这个明确分级的载体上，复结构和共轭能共同构造出来。其 \(\Lambda^1\) 分量是选择的实部，\(\Lambda^2\) 分量是对应虚部。

只给出 \(J^2=-I\) 还不能唯一选定 C：C 和 -C 都满足平方为 I 且与 J 反交换；还需要实部选择或等价的分级/配对信息。这里恰好由已有 carrier 提供了该选择。单纯再乘一个 i 也不是共轭：\(J J J^{-1}=J\)，不会得到 -J。

## 5. 已有十二个 frame 的运输检查

对上游四个 process 家族、每个家族的 identity/scaled/mixed 三张图表，读取其已保存矩阵，以精确有理数检验新的扩展：

\[
C'=TCT^{-1},\quad J'=TJT^{-1},\quad
G'=T^{-\mathsf T}GT^{-1},\quad O'=OT^{-1}.
\]

十二张图表均满足 \(C'^2=I\)、\(C'J'C'=-J'\)、\(C'^{\mathsf T}G'C'=G'\)，观察也与源图表一致。对现有实 H，检查了 \(CHC=H\)。在 \(A=-JH\) 上，得到 \(CAC=-A\)，并精确核对了到 12 阶的

\[
C\frac{A^k}{k!}C=(-1)^k\frac{A^k}{k!}.
\]

这对应原定义下 \(C U(t) C=U(-t)\) 的系数关系；没有把事件时钟或程序归约历史解释成可逆时间，也没有把 12 阶截断说成完整指数的数值计算。

对度量伴随 \(M^\sharp=G^{-1}M^{\mathsf T}G\)，核对了 H 自伴随、J 反自伴随、伴随平方为恒等，以及用一对确实不交换的算子检验

\[
(XY)^\sharp=Y^\sharp X^\sharp.
\]

反例有实际区分力：mixed 图表若不运输 C，会破坏 \(CJC=-J\)；scaled 图表若仍用旧欧氏度量，会给出错误的 J 伴随；乘积取伴随而不倒转次序也会失败。

这些是对现存 frame 坐标的新增外部检查，不是重跑它们的旧 process 接收、运行或认证流程。

## 6. `0001011011` 的自接合实际结果

保持此前的对象定义：125 是原 Zot 机器的转换次数；对应的程序值 P 用 823 字符 Iota 表示，不是一个“125 字符 Iota 程序”。

为避免把组合子参数与复共轭混名，在此令

\[
\begin{aligned}
L(c)&=\lambda l\,R.R(\lambda r.c(lr)),\\
\mathrm{One}&=\lambda c\,h.h(L(c)),\\
D&=\lambda r.S(\mathrm{One}(\iota r)),\\
A_P&=L(L(D)),\qquad P=\lambda h.hA_P.
\end{aligned}
\]

用户确认的同一 P 两种角色自接合按普通应用计算：

\[
PP\longrightarrow P A_P\longrightarrow A_P A_P.
\]

结果有限：`evidence/PP.iota` 为 1,647 字符；独立的最左最外组合子重写共 **1,808 步**，其中 Iota 822 步、S 549 步、K 437 步，峰值 7,627 个树节点。重写器同时使用 \(\iota f\to fSK\)、S 和 K 的标准规则；故这里不是 1,808 个仅用 Iota 单一原语计数的步骤，也不能与 Zot 的 125 次 CEK 转换直接比较。

该结果经 lambda 展开后的完整 beta 正规形有 84 个 AST 节点；P 的有 49 个。两者正规形不同。因此已确认的自接合没有发散，也没有得到 \(PP=_\beta P\)。这里只用 beta 等价作判断，没有给出一般观察等价或 beta-eta 等价结论。

全部 1,808 条归约的规则、位置、节点数和结果摘要保存在 `evidence/PP-trace.json`；完整 lambda 正规形在 `evidence/result.json`。初始纯 Iota 项和两种归约算法都在包内，可重新生成。

## 7. 还差哪座桥，才能说这是 P 的共轭/对偶

现在的 C 操作的是已声明的坐标。P 则是一般的程序/continuation。不能直接假定 \(C\circ P\circ C\) 就是一个仍处于同一坐标载体的算子。

本次给 P 输入符号元组就能看见这个差别：

\[
P Z(p,q,r,s)=A_P p q r s
\longrightarrow q\,(\lambda x.L(D)(p x))\,r\,s.
\]

其头是任意输入槽位 q，未呈现为四槽坐标构造子。因此我们没有建立 P 的坐标端映射性质，也没有声称刚生成的伴随程序就是 \(P^\dagger\)。

直接镜像应用树也不能解决语义对偶。设 M 递归交换左右子树并固定 Iota 叶子，则 M 在原始树上确实是对合；但它不保持标准 beta 等价。记 \(K_\iota,S_\iota\) 为标准 Iota 编码：

\[
K_\iota=_\beta (K_\iota K_\iota)S_\iota,
\quad M(K_\iota)=_\beta I,
\quad M((K_\iota K_\iota)S_\iota)=_\beta SK\ne_\beta I.
\]

所以，用户所说的左右展开若要形成语义对偶，应连同求值规则、端口和配对一起运输，不能只翻转括号。若只定义系数共轭并固定所有 Iota 源叶子，那么纯 P 自然不变；这是系数层的固定性，尚未说明程序层自对偶。

下一步的明确对象是一个作用在“右展开程序—左展开数据”接合处的表示映射：验证它运输应用、保留接口顺序，并使配对在换基下保持一致。本包给这座桥两端提供了可运行的例子，而没有把缺失的映射当成已经证明。

## 8. 复现与证据边界

需要 Python 3.10+（使用 `int.bit_count`），无需第三方包。在解压后的本目录执行，每次输出目录必须不存在：

```sh
python3 research.py --output /tmp/iota-conjugation-fresh
python3 adjoint.py --base /tmp/iota-conjugation-fresh --output /tmp/iota-adjoint-fresh
```

第一项记录 400 个通过断言，第二项记录 16 个通过断言；它们是本次有限范围内的检查，不是 416 次独立验证。第一项实测约 17 秒，重跑耗时因机器而异。预算耗尽时保留 Unknown/失败记录，不据此宣布发散。

两份精确上游输入保存在 `inputs/`，原始字节的 SHA-256 和 Git blob 已核对；它们仍属于各自来源，原项目注明 Unknown v0.3。新增代码由 ChatGPT（OpenAI）编写。`SHA256SUMS` 覆盖打包文件。

一个初版镜像反例选错了见证：K 与 I K 的镜像恰好都是 I，因此那个反例没有区分力。失败结果和当时脚本保留在 `attempts/adjoint-control-v0/`；改用 K 与 (K K) S 后得到上述有效反例。没有删掉失败记录或修改待检验的等价要求。

三计算机原生执行次数为零。未声称 Adva 原生接纳、P 的一般矩阵表示、所有输入为空、不可逆归约可被复共轭倒放，或任何物理黑洞/奇点结论。
