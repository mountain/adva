"""逆行收据追踪器（机制侧，与库仓意义解读 v0 互为对偶）。
运行时：1) 沿前驱哈希逆行收据链并打印每步反向意义；
        2) 读取第三个对象 dual-pair-receipt.json，校验机制与解读双方的 pin；
        3) 打印终点句。任何断裂/缺失都如实显示为孔洞。
状态：bounded method；不授予原生准入；解读不被验证为真。
"""
import hashlib, json, itertools, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]          # AEG 仓根
HERE = pathlib.Path(__file__).resolve().parent
START = ROOT/'trials/binary-relation-round-01/evidence-pdf-01/receipt-08.json'
PAIR = HERE/'dual-pair-receipt.json'
LIB_CHECKOUT = ROOT.parent/'adva'                            # 约定：AEG 与 adva 同级
MD_REL = 'adva-library/meaning-interpretation-v0.md'

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

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def all_receipts():
    found = {}
    for p in itertools.chain(ROOT.glob('trials/*/receipt-*.json'),
                             ROOT.glob('trials/*/*/receipt-*.json')):
        try:
            found[sha(p)] = p
        except OSError:
            pass
    return found

def walk_chain():
    by_sha = all_receipts()
    chain, seen = [], set()
    cur = json.loads(START.read_text(encoding='utf-8'))
    p = START
    while True:
        h = sha(p)
        chain.append((cur.get('round'), cur, p, h))
        seen.add(h)
        pred = cur.get('predecessor_sha256')
        if not pred:
            break
        if pred not in by_sha:
            print(f"[孔洞] 前驱 {pred[:12]}… 不在仓内 —— 链在此断开（保留为能量）\n")
            break
        p = by_sha[pred]
        cur = json.loads(p.read_text(encoding='utf-8'))
    return chain, by_sha

def verify_dual_pair():
    print("=== 对偶对校验（第三个对象 = 泰西穆勒标记点）===\n")
    if not PAIR.exists():
        print("[孔洞] dual-pair-receipt.json 缺失\n")
        return
    pair = json.loads(PAIR.read_text(encoding='utf-8'))
    mech = pair['mechanism']
    interp = pair['interpretation']
    own = sha(pathlib.Path(__file__).resolve())
    ok_mech = own == mech['sha256']
    print(f"[{'✓' if ok_mech else '✗'}] 机制 pin：{own[:16]}… {'一致' if ok_mech else '不一致（机制被改动）'}")
    md_path = LIB_CHECKOUT/MD_REL
    if md_path.exists():
        md_h = sha(md_path)
        ok_md = md_h == interp['sha256']
        print(f"[{'✓' if ok_md else '✗'}] 解读 pin：{md_h[:16]}… {'一致' if ok_md else '不一致（解读被改动）'}")
    else:
        print(f"[未定位] 解读文件不在约定路径 {LIB_CHECKOUT}/{MD_REL}；记录的 pin：{interp['sha256'][:16]}…")
    print(f"    关系：{pair.get('relation', '')}\n")

def main():
    chain, by_sha = walk_chain()
    print("=== 逆行运转：从合一结果走回起点 ===\n")
    for round_no, rec, path, h in reversed(chain):
        print(f"[✓] receipt-{round_no:02d}  {rec.get('status','?'):<20} sha={h[:16]}…")
        print(f"    逆行解读：{REVERSE_MEANING.get(round_no, '')}\n")
    orphans = [(json.loads(v.read_text(encoding='utf-8')).get('round'), v)
               for v in by_sha.values() if v not in (x[2] for x in chain)]
    if orphans:
        print("=== 悬空收据（未被前驱链引用，如实保留）===\n")
        for round_no, v in sorted(orphans, key=lambda x: x[0] if x[0] else 0):
            print(f"[悬空] receipt-{round_no or '?'}  sha={sha(v)[:16]}…  逆行解读：{REVERSE_MEANING.get(round_no, '')}")
        print("\n（精化轮重写收据时切断了 01→02→03 链并令 04 悬空；修复与否留作下一轮。）")
    verify_dual_pair()
    print("=== 终点 ===\n")
    print("全部收据的意义合起来只有一句：")
    print("“信任不需要被相信，只需要被重跑。”")
    print("机制与解读互为解释；对偶对的标记在 dual-pair-receipt.json。")

if __name__ == '__main__':
    main()
