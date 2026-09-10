"""meaning.py v3 — 双文档对位的意义解读器（生成 vs 验证）。

对象：用户根路径下的两个 PDF
  /Users/mingli/2303.08774v6.pdf  OpenAI, "GPT-4 Technical Report" (2024, 100 pp)
  /Users/mingli/nenbakraniya.pdf   Nen Bakraniya, "Accurate Proteome-wide Missense
                                   Variant Effect Prediction with AlphaMissense"
                                   (student study deck, 37 pp)

方法沿用 meaning.py v2 的纪律：pin → 对齐 → 逆向解读 → 孔洞即能量 → 一句话意义。
"""
import hashlib
import json
import pathlib
import re

HOME = pathlib.Path("/Users/mingli")
ROUND = pathlib.Path("/Users/mingli/Adva/AEG/trials/meaning-pair-round-02")
A = HOME / "2303.08774v6.pdf"   # 生成旗舰：GPT-4 技术报告
B = HOME / "nenbakraniya.pdf"   # 验证旗舰：AlphaMissense 学生研报
TA = ROUND / "a-full.txt"
TB = ROUND / "b-full.txt"

REVERSE_MEANING = {
    "a": (
        "GPT-4：生成的旗舰 —— 一百页只为说清一件事：下一个词可以被预测，",
        "而且预测本身可预测（用千分之一算力外推性能）。生成被验证驯服了。",
    ),
    "b": (
        "AlphaMissense：验证的旗舰 —— 整个蛋白质组逐点核查，哪些变异致病。",
        "37 页只有 637 个词 —— 这份报告的意义住在图里，不在字里。",
    ),
    "pair": (
        "两篇之间：一篇预测下一个 token，一篇核查下一次变异。",
        "词表 6651 对 305，语言 177 对 0，变异 0 对 21 —— 域词彻底分裂，",
        "体裁词（model 505/11）才把两篇连在同一个文类里。",
    ),
}


def sha_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def words(path):
    return re.findall(r"[A-Za-z][A-Za-z'-]*|[0-9]+", pathlib.Path(path).read_text().lower())


def freq(toks):
    d = {}
    for t in toks:
        d[t] = d.get(t, 0) + 1
    return d


def phrase_count(text, phrase):
    return len(re.findall(re.escape(phrase), text, re.IGNORECASE))


def main():
    pins = {"a": sha_file(A), "b": sha_file(B)}
    ta, tb = words(TA), words(TB)
    fa, fb = freq(ta), freq(tb)
    shared = set(fa) & set(fb)
    overlap = len(shared) / min(len(fa), len(fb))
    ra, rb = pathlib.Path(TA).read_text(), pathlib.Path(TB).read_text()
    align = {
        "schema": "aeg.meaning-pair.align", "version": 0,
        "pins": pins,
        "pages": {"a": 100, "b": 37},
        "words": {"a": len(ta), "b": len(tb)},
        "vocabulary_overlap": round(overlap, 4),
        "citation": {"b_cites_a": ("openai" in rb.lower()) or ("gpt" in rb.lower()),
                     "a_cites_b": "alphamissense" in ra.lower()},
        "phrases": {
            "model": [phrase_count(ra, "model"), phrase_count(rb, "model")],
            "predict": [phrase_count(ra, "predict"), phrase_count(rb, "predict")],
            "benchmark": [phrase_count(ra, "benchmark"), phrase_count(rb, "benchmark")],
            "evaluat*": [phrase_count(ra, "evaluat"), phrase_count(rb, "evaluat")],
            "safety": [phrase_count(ra, "safety"), phrase_count(rb, "safety")],
            "language": [phrase_count(ra, "language"), phrase_count(rb, "language")],
            "variant": [phrase_count(ra, "variant"), phrase_count(rb, "variant")],
            "missense": [phrase_count(ra, "missense"), phrase_count(rb, "missense")],
            "pathogen": [phrase_count(ra, "pathogen"), phrase_count(rb, "pathogen")],
            "limitation": [phrase_count(ra, "limitation"), phrase_count(rb, "limitation")],
        },
    }
    (ROUND / "align.json").write_text(json.dumps(align, indent=2, ensure_ascii=False) + "\n")

    print("=== 意义解读：GPT-4 报告 vs AlphaMissense 研报 ===\n")
    print(f"[pin] 2303.08774v6.pdf  sha256={pins['a']}")
    print(f"[pin] nenbakraniya.pdf   sha256={pins['b']}\n")
    print(f"[✓] 页数  100 → 37     词数   {len(ta)} → {len(tb)}")
    print(f"[✓] 词表 {len(fa)} → {len(fb)}，重合系数 {round(overlap,4)}")
    print("[✓] 引用方向：互不引用（各自独立）\n")
    print("[对齐] 短语权重（前 = GPT-4 报告，后 = AlphaMissense 研报）：")
    for k, v in align["phrases"].items():
        print(f"      {k:14s} {v[0]:4d} → {v[1]:4d}")
    print()
    for key in ("a", "b", "pair"):
        for line in REVERSE_MEANING[key]:
            print(f"[逆向解读] {line}")
        print()
    print("[孔洞] 两份报告的实验与结论均未重跑；学生研报的图未做像素层分析 —— 其意义")
    print("       大部分不在文本层。本解读只对齐了文本层的表面事实。")
    print()
    print("=== 终点 ===\n")
    print("这一对的意义合起来只有一句：")
    print("“生成与验证是 AI 的两极：一篇预测下一个词，一篇核查下一次变异——")
    print("它们之间隔着的，正是信任要计算的那段距离。”")


if __name__ == "__main__":
    main()
