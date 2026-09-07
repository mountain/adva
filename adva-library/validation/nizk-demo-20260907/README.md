# NIZK demo 安装与运行验收：2026-09-07

结论：Linux x86_64、CPython 3.11.15 下，未修改的完整 demo 和零依赖模式
均完成一次运行，六项正反例控制符合预期；`pip check` 通过。
这是安装与运行冒烟检查，不是密码算法形式化验证、安全审计或原生证明。

本目录整理并提交此前保存在本机 `target/nizk-demo-20260907.u3nnfn/`
中的运行记录。提交时核对了原始输出、源码摘要、vendor HEAD 和依赖状态，
没有再次启动 demo，没有把历史结果冒充成新一轮实验。

## 验收对象与结果

- 父检出版本：`d9ebd85c2dd47f2de9075e11b86c5014127d4758`。
- 脚本：[`../../nizk_demo.py`](../../nizk_demo.py)，SHA-256
  `04e389b09ca24d164da9a8679eb61d094507d94cdb17f3baf448620551852e62`。
- 原始依赖声明：[`../../requirements.txt`](../../requirements.txt)，SHA-256
  `8907b16ec495b4ebf4b2b9530baf1cdeeaeae954d4997852dae5e302cea65861`。
- 外部源码：`https://github.com/Merricx/zksnake.git`，精确提交
  `fc9a81b3862643aef352b9aa49b67793593bede0`，位于
  `adva-library/vendor/zksnake-py`；不是 PyPI 同名新版的 Rust 内核。
- 独立环境：`adva-library/.venv-zkp`，未改动主 `.venv`。

| 运行模式 | 控制 | 观察结果 |
|---|---|---|
| 完整 demo | Groth16：原公开值 y=35 | 接受 |
| 完整 demo | 同一证明改用公开值 y=36 | 拒绝 |
| 完整 demo | Schnorr：原公开值 h | 接受 |
| 完整 demo | Schnorr：随机替换为 h_fake | 拒绝 |
| `-S --stdlib-only` | Schnorr：原公开值 h | 接受 |
| `-S --stdlib-only` | Schnorr：随机替换为 h_fake | 拒绝 |

两次退出码均为 0；另行核对了上述完整结果行、无异常通过标记或 traceback，
以及零依赖模式没有 Demo 1。脚本只打印控制结果，**退出 0 本身不足以验收**。
随机替换的反例只说明本次样本被拒绝，不保证每次随机选择都与原值不同，
更不证明所有伪造都被拒绝。

Groth16 正例报告 setup 0.281 秒、prove 0.096 秒、verify 1.591 秒。
这些是脚本报告的单项操作时间，不是整轮时间、性能保证或跨平台基准。

## 提交的证据

- [`report.json`](report.json)：版本、控制结果、执行限制和未覆盖的验证层。
- [`full-demo.excerpt.txt`](full-demo.excerpt.txt)、
  [`stdlib-demo.excerpt.txt`](stdlib-demo.excerpt.txt)：按白名单逐行保留的
  demo 标题、耗时与验收结果；保留原行文本和顺序。
- [`dependencies.json`](dependencies.json)：从 pip 安装报告提取的环境、
  13 个已下载 wheel 的来源、版本和 SHA-256，不包含完整包说明元数据。
- [`installed-versions.txt`](installed-versions.txt)：原环境版本清单，
  包括 bootstrap 工具 pip 24.0 和 setuptools 79.0.1。
- [`requirements-linux-py311.lock`](requirements-linux-py311.lock)：依据实际
  下载的 wheel 生成的哈希锁定清单；仅适用于对应平台和 Python ABI。
  原安装使用原始 requirements，并未另建环境验证这个后生成的锁文件。

原始日志包含 demo 主动打印的测试秘密；发布摘录省略秘密、随机群参数、
公开值和证明数值，也省略未经本次验收支持的隐私说明。原始日志与完整
pip 报告仅留在本机忽略目录，其摘要记入报告，未提交虚拟环境、密钥或
生产数据。摘要用于追溯字节版本，不是签名、语义身份或安全证明。

因此这些摘录支持审阅本次控制结果，但不能独立重放原来的随机证明。
重跑将生成新的随机参数和证明，预期相同的是控制判定，不是逐字节输出。

## 有限运行约定与重跑

以下整理自原执行前约定，不增加原记录的运行次数：仅两次启动，无重试、
无自动续跑；每次 30 秒墙钟时间、2 秒强制停止宽限、20 CPU 秒、1 GiB
地址空间、1 MiB 单文件写入、128 个文件描述符。使用上游选项
`ZKSNAKE_PARALLEL_CPU=1` 避免默认 joblib worker 池。
两个 demo 合计最多 60 秒运行加 4 秒停止宽限、40 CPU 秒。
原准备步骤另限源码获取 120 秒、建环境 30 秒、pip 安装 180 秒，
pip 重试为 0；这些不是 demo 计时的一部分。检查与记录整理也不计入
上述 demo 操作耗时。发布的每份日志和报告小于 64 KiB。

从项目根目录，在确认源码摘要和 vendor 提交相符、依赖已安装后，可手动
执行以下两条命令。每次重跑是单独的有限验收，不覆盖本目录的历史证据：

```sh
timeout --kill-after=2s 30s \
  prlimit --cpu=20 --as=1073741824 --fsize=1048576 --nofile=128 -- \
  env ZKSNAKE_PARALLEL_CPU=1 PYTHONDONTWRITEBYTECODE=1 \
  adva-library/.venv-zkp/bin/python -u adva-library/nizk_demo.py

timeout --kill-after=2s 30s \
  prlimit --cpu=20 --as=1073741824 --fsize=1048576 --nofile=128 -- \
  env ZKSNAKE_PARALLEL_CPU=1 PYTHONDONTWRITEBYTECODE=1 \
  adva-library/.venv-zkp/bin/python -S -u adva-library/nizk_demo.py --stdlib-only
```

必须同时检查退出码和 `report.json` 中 `expected_control_lines` 的原样输出；
完整模式应有四条，零依赖模式应有两条且无 Demo 1。不能只搜索“通过”。
超时或资源耗尽记为 Unknown，不解释为算法不成立，也不自动重置预算；
控制结果不符则验收失败。保留失败与部分输出。上述 Linux 进程限制不是
对抗恶意程序的安全沙箱，也不是对所有检查及记录工作的总资源上界。

如需在匹配的 Linux x86_64 / CPython 3.11 新隔离环境中按已观察的 wheel
安装，可使用以下命令；这是复现说明，不是已经完成的第二次安装记录：

```sh
timeout --kill-after=2s 180s \
  adva-library/.venv-zkp/bin/python -m pip install \
  --disable-pip-version-check --retries 0 --timeout 30 \
  --only-binary=:all: --require-hashes \
  -r adva-library/validation/nizk-demo-20260907/requirements-linux-py311.lock

adva-library/.venv-zkp/bin/python -m pip check
```

虚拟环境创建和 vendor 恢复步骤见 [`../../INSTALL.md`](../../INSTALL.md)。
本次只恢复了 demo 使用的纯 Python vendor；仓库缺少 `.gitmodules`
的问题仍在，其他三个 vendor 引用没有安装，也未被本报告验证。

## 保持的边界与残余

Schnorr 使用 `random`、玩具群参数、概率素性测试并主动打印见证；其素数
搜索没有内部步数上限，所以运行依赖外部时间限制。Groth16 使用本地
演示 setup，不是经过审计的可信设置仪式。公开的小样例本身也可能暴露
见证。这些限制没有在提交验证记录时被修复，不得用于真实秘密。

没有执行 Lean 或 Metamath 密码学证明，没有验证 Python/Rust 实现精化、
互操作、知识可靠性、零知识性质、侧信道或生产安全性。demo 的编译是
外部库中的 R1CS 到 QAP，不是 adva 原生编译或语义准入。

本次未改动 demo、requirements 或 vendor 源码；未实现 Research 0156 的
ArithmeticLineage、tamper-check、key-issue 或 verify 命令；未增加数学
目录条目、改变 Pascal 根或签发原生证书。几何义务仍 Open，native Seal
仍 NotIssued。`adva.py` 的外围入口地位不变，没有新增绕过它的原生接口。
