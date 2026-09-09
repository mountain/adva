"""验证合一的逆行解读：从 receipt-08 沿 predecessor 哈希链走回起点。
每步校验 pin；链被切断处与悬空收据如实显示（孔洞即下一轮能量）。
"""
import hashlib, json, pathlib

ROOT = pathlib.Path('/Users/mingli/Adva/AEG')
START = ROOT/'trials/binary-relation-round-01/evidence-pdf-01/receipt-08.json'

REVERSE_MEANING = {
    1: "第一个诚实的“无进展”，也是进展（EvidenceStutter 是测量的起点）。",
    2: "一百次原生运行只差计时字段 —— 重复不是学习；边界是被测出来的。",
    3: "变异必须落在声明的载波上 —— 行动之前，先定义自己测量什么。",
    4: "一个公式在两种语言里给出同一个答案 —— 同一问题可以被两个世界分别确认。",
    5: "全部 256 字节在基底语言上成立 —— “显式、可检查、有界”被做成了 256 个可重跑的事实。",
    6: "对方的 advance 步骤用我们的收据当前驱 —— 信任在双方之间传递，不靠说服，靠 pin。",
    7: "两个二进制在同一字节前沿上一致 —— “信任可计算”第一次有了机器层的实例。",
    8: "两份文档字节层几乎无关，却共享同一论点母句 —— 意义不藏在字节里，藏在问题里。",
}

def all_receipts():
    found = {}
    import itertools as _it
    for p in _it.chain(ROOT.glob('trials/*/receipt-*.json'), ROOT.glob('trials/*/*/receipt-*.json')):
        try:
            found[hashlib.sha256(p.read_bytes()).hexdigest()] = p
        except OSError:
            pass
    return found

def main():
    by_sha = all_receipts()
    chain, seen = [], set()
    cur = json.loads(START.read_text(encoding='utf-8'))
    p = START
    while True:
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        chain.append((cur.get('round'), cur, p, sha))
        seen.add(sha)
        pred = cur.get('predecessor_sha256')
        if not pred:
            break
        if pred not in by_sha:
            print(f"[孔洞] 前驱 {pred[:12]}… 不在仓内 —— 链在此断开（保留为能量）\n")
            break
        p = by_sha[pred]
        cur = json.loads(p.read_text(encoding='utf-8'))

    print("=== 逆行运转：从合一结果走回起点 ===\n")
    for round_no, rec, path, sha in reversed(chain):
        print(f"[✓] receipt-{round_no:02d}  {rec.get('status','?'):<20} sha={sha[:16]}…")
        print(f"    逆行解读：{REVERSE_MEANING.get(round_no, '')}\n")

    orphans = [ (json.loads(v.read_text(encoding='utf-8')).get('round'), v)
                for v in by_sha.values() if v not in (x[2] for x in chain) ]
    if orphans:
        print("=== 悬空收据（未被前驱链引用，如实保留）===\n")
        for round_no, v in sorted(orphans, key=lambda x: x[0] if x[0] else 0):
            sha = hashlib.sha256(v.read_bytes()).hexdigest()
            print(f"[悬空] receipt-{round_no or '?'}  sha={sha[:16]}…  逆行解读：{REVERSE_MEANING.get(round_no, '')}")
        print("\n（精化轮重写收据时切断了 01→02→03 链并令 04 悬空；修复与否留作下一轮。）")

    print("=== 终点 ===\n")
    print("全部收据的意义合起来只有一句：")
    print("“信任不需要被相信，只需要被重跑。”")
    print("这就是把验证合一结果逆行运转得到的意义解读。")

if __name__ == '__main__':
    main()
