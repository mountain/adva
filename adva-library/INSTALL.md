# NIZK Demo 分版本安装说明

本说明覆盖 `nizk_demo.py` 的全部安装路径，按 Python 版本给出结论与命令。
下表及第 6 节原有「**实测**」结论来自 macOS arm64，Homebrew Python 3.14.6 / 3.13；
另有 2026-09-07 的 [Linux x86_64 / Python 3.11.15 验收记录](validation/nizk-demo-20260907/README.md)，
覆盖路径 A 和 C，附依赖版本、wheel 摘要和脱敏结果摘录。
其余结论依据撰写时查询的 PyPI 元数据（`requires_python` 与 wheel 标签）。

---

## 1. 总览：Python 版本 × 安装路径

| Python 版本 | 路径 A：纯 Python zksnake（本 demo 默认） | 路径 B：新版 zksnake（PyPI，Rust 内核） | 路径 C：零依赖 Schnorr | zksk |
|---|---|---|---|---|
| **3.6 / 3.7** | ✗（需 ≥3.8） | ✗（需 ≥3.9） | ✓ 仅 Demo 2 | 可能可用（未实测） |
| **3.8** | ✓（pyproject 声明 ≥3.8；本机未实测） | ✗ | ✓ | 可能可用（未实测） |
| **3.9** | ✓ | ✓ 有 wheel（Windows/Linux 全平台；macOS 仅 arm64） | ✓ | 可能可用（未实测） |
| **3.10** | ✓ | ✓ 有 wheel（Windows/Linux；macOS 无 wheel → 需 Rust） | ✓ | 可能可用（未实测） |
| **3.11** | ✓ | ✓ 有 wheel | ✓ | 可能可用（未实测） |
| **3.12** | ✓ | ✓ 有 wheel | ✓ | 存疑（petlib 老代码，3.12 起 distutils 已移除） |
| **3.13** | ✓ **实测跑通** | ✓ 有 wheel | ✓ **实测跑通** | ✗ **实测安装失败** |
| **3.14** | ✓ **实测跑通（推荐）** | ✗ 无 wheel → 需 Rust 源码构建 | ✓ **实测跑通** | ✗ **实测安装失败** |

依赖解析说明：`requirements.txt` 中 `joblib>=1.4.0` 会按 Python 版本自动解析
（3.8/3.9 → joblib 1.4.2；3.10+ → 1.5.0/1.6.0），`py_ecc` 8.0.0 为纯 Python wheel（要求 ≥3.8,<4）。

---

## 2. 路径 A：纯 Python zksnake（推荐，Python 3.8–3.14 通用）

本 demo 的 Demo 1（Groth16）使用 [zksnake](https://github.com/Merricx/zksnake)
GitHub 仓库的**纯 Python 版本**（提交 `fc9a81b`，已检出在 `vendor/zksnake-py/`）。
其 PyPI 发行版已改为 Rust 内核（见路径 B），故不用 `pip install zksnake`。

### 2.1 获取 Python（按需选择）

| 环境 | 命令 |
|---|---|
| macOS（Homebrew） | `brew install python@3.14` 或 `brew install python@3.13` |
| macOS/Linux（pyenv） | `pyenv install 3.11`（可装任意 3.8–3.14 版本） |
| Linux（Debian/Ubuntu） | `sudo apt install python3 python3-venv python3-pip` |
| Windows | 从 [python.org](https://www.python.org/downloads/) 安装 3.8–3.14 任一版本 |

### 2.2 获取纯 Python 版 zksnake（确认源码存在后才可跳过）

以下命令从 `adva-library` 目录执行。demo 实际导入的是 `vendor/zksnake-py/src`。
仓库目前缺少 `.gitmodules`；只有 Git 引用或空目录不代表源码已恢复，
不能假定 clone 主仓库后即可跳过此步。仅在目标目录不存在或为空时克隆；
若已有源码，先检查 HEAD 和本地改动，不要覆盖已有工作。

```bash
git clone https://github.com/Merricx/zksnake.git vendor/zksnake-py
git -C vendor/zksnake-py checkout --detach fc9a81b3862643aef352b9aa49b67793593bede0
git -C vendor/zksnake-py rev-parse HEAD
```

### 2.3 创建虚拟环境并安装依赖

**macOS / Linux**

```bash
python3 -m venv .venv-zkp
source .venv-zkp/bin/activate
pip install -r requirements.txt
python nizk_demo.py
```

**Windows（PowerShell / CMD）**

```powershell
py -3.13 -m venv .venv-zkp        # 换成你安装的版本号，如 -3.14
.venv-zkp\Scripts\activate
pip install -r requirements.txt
python nizk_demo.py
```

### 2.4 预期输出与耗时参考

| Python 版本 | setup | prove | verify | 结果 |
|---|---|---|---|---|
| 3.14.6（实测） | 0.37s | 0.09s | 0.25s | 正确 ✓ / 伪造 ✗ |
| 3.13（实测） | 0.64s | 0.09s | 0.17s | 正确 ✓ / 伪造 ✗ |

---

## 3. 路径 B：新版 zksnake（PyPI 预编译 wheel，Python 3.9–3.13）

新版 zksnake 用 Rust（arkworks）重写了内核，`pip install zksnake` 在有预编译
wheel 的平台可开箱即用，性能远高于纯 Python 版。

```bash
pip install zksnake
```

**wheel 覆盖矩阵（zksnake 0.1.0，撰写时查询）**

| 平台 | Python 3.9 | 3.10 | 3.11 | 3.12 | 3.13 | 3.14 |
|---|---|---|---|---|---|---|
| Linux x86_64（manylinux） | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| macOS arm64（Apple Silicon） | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ |
| macOS x86_64（Intel） | ✗ | ✗ | ✓ | ✓ | ✓ | ✗ |
| Windows（win_amd64 / win32） | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |

**无 wheel 的场景**（上表 ✗，含全部 3.14）需要 Rust 工具链从源码构建：

```bash
# macOS/Linux: 安装 Rust 后重试 pip
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
pip install zksnake
```

**注意**：新版是 Rust 内核 + Python 绑定，API 与纯 Python 版不同。本 demo 脚本
针对纯 Python 版 API 编写；若改用新版，需按其文档改写调用方式。

---

## 4. 路径 C：零依赖（仅 Demo 2，任何 Python ≥ 3.6）

Demo 2（Schnorr NIZK，Fiat-Shamir 变换）只用 Python 标准库
（`hashlib`、`random`），**不需要安装任何东西、不需要网络**：

```bash
python nizk_demo.py --stdlib-only
```

适合 Python 3.6–3.7、3.14 无 wheel、或离线/沙箱环境。

---

## 5. 其他 Python ZKP 库的版本适配（速查）

| 库 | 安装方式 | 适用 Python | 备注 |
|---|---|---|---|
| [zksk](https://pypi.org/project/zksk/) | `pip install zksk` | 建议 ≤3.11 | 依赖链 zksk→bplib→petlib（C 扩展）；**3.13/3.14 实测编译失败**；3.12 未实测但风险高（petlib 为 2018 年代码） |
| [pysnark](https://github.com/meilof/pysnark) | `pip install git+https://github.com/meilof/pysnark` | 3.8+（实测 3.14 可导入） | 纯 Python 电路 DSL；**生成证明需外部后端**（libsnark 封装或 snarkjs CLI），本仓库 `vendor/pysnark` 已备好 |
| [pybulletproofs](https://pypi.org/project/pybulletproofs/) | `pip install pybulletproofs` | 3.8–3.10（仅 Linux x86_64 有 wheel） | Bulletproofs 范围证明；其他平台/版本需 Rust 源码构建 |
| [groth16-zorch](https://pypi.org/project/groth16-zorch/) | `pip install groth16-zorch` | 3.9+ | 基于 zorch 张量库，需 PyTorch |
| [zkpy](https://pypi.org/project/zkpy/) | `pip install zkpy` | 3.8+ | 封装 circom 电路工具链，需另装 circom + snarkjs 可执行文件 |
| [zokrates-pycrypto](https://pypi.org/project/zokrates-pycrypto/) | `pip install zokrates-pycrypto` | 3.8+ | ZoKrates 生态辅助库，需另装 ZoKrates CLI |

---

## 6. 本机实测记录（macOS arm64，Homebrew）

### Python 3.14.6
- **路径 A**：完整跑通（setup 0.37s / prove 0.09s / verify 0.25s；Schnorr prove 48μs / verify 41μs）
- **新版 zksnake**：无 cp314 wheel，pip 走 Rust 源码构建；本机开发沙箱阻止了 cargo
  缓存写入而中断（**普通环境无此限制**，装好 Rust 即可构建）
- **zksk**：`bplib`（→`petlib`）C 扩展构建失败
- **pysnark**：导入成功、可建电路；后端缺失外部二进制

### Python 3.13
- **路径 A**：完整跑通（setup 0.64s / prove 0.09s / verify 0.17s；Schnorr 55μs / 42μs）
- **zksk**：构建失败（同上）

### 其他版本
结论来自 PyPI 元数据（`requires_python`、wheel 标签），未逐版本实测。

---

## 7. 常见问题（FAQ）

- **pip 缓存权限警告**（Homebrew 环境常见，无害）：`pip install --no-cache-dir ...`
- **joblib/py_ecc 版本**：无需手动指定，pip 会按 Python 版本自动选合适版本
- **Apple Silicon + Python 3.10 想装新版 zksnake**：无 arm64 cp310 wheel → 改用路径 A
- **离线环境**：使用路径 C；或预先下载依赖做本地 wheel 安装
- **conda 用户**：`conda create -n zkp python=3.11` 后可完全按路径 A 操作
