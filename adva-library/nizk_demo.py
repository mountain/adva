#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
非交互式零知识证明（NIZK）Python 演示
====================================

Demo 1: Groth16 zk-SNARK —— zksnake（纯 Python 实现，BN254 曲线）
    证明「我知道秘密 x，使得公开的 y = x³ + x + 5」，其中 x = 3, y = 35。
    验证者只能看到公开值 y 和证明 proof，全程拿不到 x。

Demo 2: Schnorr NIZK —— 仅用 Python 标准库从零实现（Fiat-Shamir 变换）
    证明「我知道离散对数 x = dlog_g(h) mod q」，不泄露 x。

──────────── 安装速览（完整的分版本说明见 INSTALL.md）────────────
路径 A（本 demo 默认，Python 3.8–3.14 通用，使用 vendor 内的纯 Python zksnake）:
    python3 -m venv .venv-zkp
    source .venv-zkp/bin/activate          # Windows: .venv-zkp\\Scripts\\activate
    pip install -r requirements.txt
    python nizk_demo.py

路径 B（新版 zksnake，PyPI 预编译 wheel，Python 3.9–3.13）:
    pip install zksnake                     # 注意: 新版 API 与本 demo 不同

路径 C（零依赖，任何 Python >= 3.6，无需安装）:
    python nizk_demo.py --stdlib-only       # 只运行 Demo 2
──────────────────────────────────────────────────────────────
"""
import os
import sys
import time
import random
import hashlib
import argparse

# 让 zksnake（纯 Python 版，vendor 内）可导入
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "vendor", "zksnake-py", "src"))


def section(title):
    print("\n" + "=" * 66)
    print(title)
    print("=" * 66)


# ---------------------------------------------------------------------------
# Demo 1: Groth16 zk-SNARK（zksnake）
# ---------------------------------------------------------------------------
def demo1_groth16():
    from zksnake.symbolic import Symbol
    from zksnake.r1cs import ConstraintSystem
    from zksnake.groth16 import Setup, Prover, Verifier

    secret_x = 3
    public_y = secret_x ** 3 + secret_x + 5          # 35

    # ---- 1. 把「y == x³ + x + 5」编译成 R1CS 约束系统 ----
    x, y, v1 = Symbol('x'), Symbol('y'), Symbol('v1')
    cs = ConstraintSystem(['x'], 'y')                # 公开输入: y；秘密输入: x
    cs.add(v1 == x * x)                              # 约束: v1 = x²
    cs.add(y - 5 - x == v1 * x)                      # 约束: y - 5 - x = v1·x ⟺ y = x³+x+5
    cs.set_public(y)
    qap = cs.compile()                               # 编译成 QAP（二次算术程序）

    # ---- 2. 可信设置: 生成证明密钥和验证密钥 ----
    t0 = time.perf_counter()
    prover_key, verifier_key = Setup(qap).generate()
    t_setup = time.perf_counter() - t0

    # ---- 3. 证明者: 用秘密 x 求解见证，生成证明 ----
    public_witness, private_witness = cs.solve({'x': secret_x}, public_y)
    t0 = time.perf_counter()
    proof = Prover(qap, prover_key).prove(public_witness, private_witness)
    t_prove = time.perf_counter() - t0

    # ---- 4. 验证者: 只看公开值和证明 ----
    t0 = time.perf_counter()
    ok = Verifier(verifier_key).verify(proof, public_witness)
    t_verify = time.perf_counter() - t0

    # ---- 5. 反例: 换成错误的公开值 y=36 再验证 ----
    bad_witness = [1, 36]                           # 声称 y=36，与约束矛盾（格式同 [1, y]）
    ok_bad = Verifier(verifier_key).verify(proof, bad_witness)

    print(f"秘密 x = {secret_x}，公开 y = {public_y}")
    print(f"setup 耗时:   {t_setup:.3f}s")
    print(f"prove 耗时:   {t_prove:.3f}s")
    print(f"verify 耗时:  {t_verify:.3f}s")
    print(f"正确公开值 y={public_y} 的验证结果: {'✓ 通过' if ok else '✗ 失败'}")
    print(f"伪造公开值 y=36     的验证结果: {'✓ 通过（异常!）' if ok_bad else '✗ 失败（符合预期）'}")
    print("\n证明内容（只是曲线上的 3 个点 A、B、C，不含秘密 x）:")
    print(f"  A = {proof.A}")
    print(f"  B = {proof.B}")
    print(f"  C = {proof.C}")
    print(f"  → 验证者除了「y={public_y} 的某个 x 确实存在」之外，无法得知 x")


# ---------------------------------------------------------------------------
# Demo 2: Schnorr NIZK（纯标准库，Fiat-Shamir 变换）
# ---------------------------------------------------------------------------
def is_prime(n, rounds=16):
    """Miller-Rabin 素性测试（演示用途，rounds=16）"""
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(rounds):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def find_safe_prime(bits=128):
    """寻找安全素数 q = 2r + 1（r 也是素数），使子群具有素数阶 r"""
    lo = 1 << (bits - 1)
    while True:
        r = random.getrandbits(bits) | (1 << (bits - 1)) | 1   # 随机奇数 r
        if is_prime(r) and is_prime(2 * r + 1):
            return 2 * r + 1, r


def demo2_schnorr():
    # ---- 1. 公共参数: 素数 q，素数阶 r 子群的生成元 g ----
    q, r = find_safe_prime()
    g0 = 2
    while pow(g0, 2, q) == 1 or pow(g0, r, q) == 1:   # 找 F_q* 的生成元
        g0 += 1
    g = pow(g0, 2, q)                                  # g 的阶为 r

    # ---- 2. 证明者持有秘密 x，公开承诺 h = g^x mod q ----
    x = random.randrange(1, r)                         # 秘密
    h = pow(g, x, q)                                   # 公开值

    def H(*items):
        """Fiat-Shamir 哈希：把交互挑战变成哈希输出的非交互挑战"""
        data = "|".join(str(i) for i in items).encode()
        return int.from_bytes(hashlib.sha256(data).digest(), "big") % r

    # ---- 3. 非交互式证明: (t, s) ----
    t0 = time.perf_counter()
    k = random.randrange(1, r)                         # 一次性随机数（保密!）
    t = pow(g, k, q)                                   # 承诺
    c = H(q, g, h, t)                                  # 挑战（哈希代替验证者提问）
    s = (k + c * x) % r                                # 响应
    t_prove = time.perf_counter() - t0

    # ---- 4. 验证者: 重算挑战并检查 g^s == t · h^c ----
    t0 = time.perf_counter()
    c2 = H(q, g, h, t)
    ok = (pow(g, s, q) == (t * pow(h, c2, q)) % q)
    t_verify = time.perf_counter() - t0

    # ---- 5. 伪造验证: 用错误的 s 或错误的 h ----
    h_fake = pow(g, random.randrange(1, r), q)         # 另一个公开值
    c3 = H(q, g, h_fake, t)
    ok_fake = (pow(g, s, q) == (t * pow(h_fake, c3, q)) % q)

    print(f"素数 q = {q}（{q.bit_length()} 位，子群阶 r = {r.bit_length()} 位）")
    print(f"秘密 x = {x}")
    print(f"公开 h = g^x mod q = {h}")
    print(f"prove 耗时:  {t_prove * 1e6:.0f} μs")
    print(f"verify 耗时: {t_verify * 1e6:.0f} μs")
    print(f"对正确公开值 h     的验证: {'✓ 通过' if ok else '✗ 失败'}")
    print(f"对伪造公开值 h_fake 的验证: {'✓ 通过（异常!）' if ok_fake else '✗ 失败（符合预期）'}")
    print(f"证明 (t, s) = ({t}, {s})")
    print(f"  → 从 (t, s) 反推 x 等价于破解离散对数问题；证明是非交互的、可离线验证的")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="非交互式零知识证明（NIZK）演示")
    parser.add_argument(
        "--stdlib-only", action="store_true",
        help="只运行 Demo 2（Schnorr NIZK）：零第三方依赖，任何 Python >= 3.6 可直接运行")
    args = parser.parse_args()

    print(f"当前 Python: {sys.version.split()[0]}（{sys.executable}）")

    if not args.stdlib_only:
        section("Demo 1: Groth16 zk-SNARK —— 证明 y = x³ + x + 5 的解存在（zksnake）")
        demo1_groth16()
    section("Demo 2: Schnorr NIZK —— 证明知道离散对数（纯标准库 + Fiat-Shamir）")
    demo2_schnorr()
    print()
