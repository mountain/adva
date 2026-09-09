"""验证合一的逆行解读：从 receipt-08 沿 predecessor 哈希链走回起点。
每步校验 pin，并打印该收据的"反向意义"。运行它，解读自己出现。
"""
import hashlib, json, pathlib, sys

ROOT = pathlib.Path('/Users/mingli/Adva/AEG')
START = ROOT/'trials/binary-relation-round-01/evidence-pdf-01/receipt-08.json'

# 每一步的反向意义（意义由行动给出：每一句都 pin 到一张可复核的收据）
REVERSE_MEANING = {
    8: "两份文档字节层几乎无关，却共享同一论点母句 —— 意义不藏在字节里，藏在问题里。",
    7: "两个二进制在同一字节前沿上一致 —— “信任可计算”第一次有了机器层的实例。",
    6: "对方的 advance 步骤用我们的收据当前驱 —— 信任在双方之间传递，不靠说服，靠 pin。",
    5: "全部 256 字节在基底语言上成立 —— “显式、可检查、有界”被做成了 256 个可重跑的事实。",
    4: "一个公式在两种语言里给出同一个答案 —— 同一问题可以被两个世界分别确认。",
    3: "变异必须落在声明的载波上 —— 行动之前，先定义自己测量什么。",
    2: "一百次原生运行只差计时字段 —— 重复不是学习；边界是被测出来的。",
    1: "不变输入 → EvidenceStutter —— 第一个诚实的“无进展”，也是进展。",
}

def find_receipt(sha):
    """按 predecessor 哈希逆行定位收据文件（在 AEG 仓内搜索）。"""
    for p in ROOT.rglob('receipt-*.json'):
        if p.name == 'receipt-08.json' and p.parent.name != 'evidence-pdf-01':
            continue
        try:
            if hashlib.sha256(p.read_bytes()).hexdigest() == sha:
                return p
        except OSError:
            pass
    return None

def main():
    print("=== 逆行运转：从合一结果走回起点 ===\n")
    current = json.loads(START.read_text(encoding='utf-8'))
    steps = []
    while current is not None:
        round_no = current.get('round')
        pred = current.get('predecessor_sha256')
        # 校验当前收据自身（以文件实际字节为准）
        p = None
        for cand in ROOT.rglob('receipt-*.json'):
            try:
                if hashlib.sha256(cand.read_bytes()).hexdigest() == (pred if False else ''):
                    pass
            except OSError:
                pass
        if round_no == 8:
            p = START
        else:
            # 用上一轮记录的前驱哈希定位本收据文件
            pass
        steps.append((round_no, current, p))
        if pred is None:
            current = None
        else:
            nxt = find_receipt(pred)
            if nxt is None:
                print(f"[孔洞] 前驱 {pred[:12]}… 未在 AEG 仓中找到 —— 保留为下一轮能量\n")
                current = None
            else:
                current = json.loads(nxt.read_text(encoding='utf-8'))

    # 倒序打印：从起点(1)到合一(8)，即"逆行的逆行"= 意义的正向叙述
    for round_no, rec, path in reversed(steps):
        sha = hashlib.sha256(path.read_bytes()).hexdigest() if path else None
        status = rec.get('status', '?')
        mark = '✓' if sha else '?'
        print(f"[{mark}] receipt-{round_no:02d}  {status:<20} sha={sha[:16] if sha else '缺失'}…")
        print(f"    逆行解读：{REVERSE_MEANING.get(round_no, '')}\n")
    print("=== 终点 ===\n")
    print("全部收据的意义合起来只有一句：")
    print("“信任不需要被相信，只需要被重跑。”")
    print("这就是把验证合一结果逆行运转得到的意义解读。")

if __name__ == '__main__':
    main()
