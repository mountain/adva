#!/usr/bin/env python3
"""Witness computation for bounded exchange request-02.

Recomputes the exact old/new rule scores and the top-25 heads for the
tax-instructions/cookbook pair, plus the excluded-common-word evidence.
"""
import json
import re
import sys

STOP = set("""a an the and or but if then else for of to in on at by with from as is are was were be been being
am do does did done have has had having will would shall should can could may might must not no nor
this that these those it its i you your he she they them we us our his her their there here what which who whom
when where why how all any each every some such more most much many few other own same so than too very just
also only into upon per via about above after again against between below under over before during while until
because although though since once""".split())

TOKEN = re.compile(r"[A-Za-z][A-Za-z'-]*|[0-9]+")

LEFT = "/Users/mingli/Adva/AEG/trials/unrelated-pair-round-01/cookbook-layer.txt"
RIGHT = "/Users/mingli/Adva/AEG/trials/unrelated-pair-round-01/irs-layer.txt"


def tokens(path):
    return [t.lower() for t in TOKEN.findall(open(path).read())]


def freq(toks):
    d = {}
    for t in toks:
        d[t] = d.get(t, 0) + 1
    return d


def rank_map(f):
    # stable sort by -freq: ties keep first-occurrence order
    order = sorted(f, key=lambda w: -f[w])
    return {w: i + 1 for i, w in enumerate(order)}


def overlap(fa, fb):
    sa, sb = set(fa), set(fb)
    return len(sa & sb) / min(len(sa), len(sb))


def main():
    lt, rt = tokens(LEFT), tokens(RIGHT)
    lf, rf = freq(lt), freq(rt)
    # old rule 1: naive
    naive = overlap(lf, rf)
    # old rule 2: stopword-filtered content
    lc = {w: c for w, c in lf.items() if w not in STOP and not w.isdigit()}
    rc = {w: c for w, c in rf.items() if w not in STOP and not w.isdigit()}
    content = overlap(lc, rc)
    # new rule: top-25 content heads
    lhead = sorted(lc, key=lambda w: -lc[w])[:25]
    rhead = sorted(rc, key=lambda w: -rc[w])[:25]
    head_int = sorted(set(lhead) & set(rhead))
    lrank, rrank = rank_map(lc), rank_map(rc)
    shared_content = set(lc) & set(rc)

    # dropped examples: shared under old content rule, absent from new head
    candidates = [
        ("line", "form line / recipe line: homograph, sense not judged"),
        ("return", "tax return / return to the kettle: homograph, sense not judged"),
        ("see", "cross-reference verb in both"),
        ("use", "generic verb in both"),
        ("take", "generic verb in both"),
        ("half", "measure word in cookbook head; rare in tax text"),
        ("check", "payment/verification in tax; rare in cookbook"),
        ("person", "generic noun in both"),
    ]
    dropped = []
    for w, note in candidates:
        if w not in shared_content:
            print("WARN: not shared:", w)
            continue
        dropped.append({
            "word": w,
            "old_membership_evidence": (
                f"naive-shared and content-shared; cookbook freq {lc[w]} rank "
                f"{lrank[w]}; irs freq {rc[w]} rank {rrank[w]}"),
            "new_exclusion_reason": (
                "absent from the top-25 head intersection: "
                + ("cookbook rank > 25" if lrank[w] > 25 else "cookbook in head")
                + "; " + ("irs rank > 25" if rrank[w] > 25 else "irs in head")
                + ". Mechanical rank exclusion; relevance only stipulated. "
                + note),
        })
    report = {
        "schema": "aeg.bounded-exchange.witness-02",
        "scores": {
            "naive_vocabulary_overlap": round(naive, 4),
            "stopword_filtered_content_overlap": round(content, 4),
            "head_intersection_fraction": f"{len(head_int)}/25",
        },
        "vocab_sizes": {
            "cookbook_naive": len(lf), "irs_naive": len(rf),
            "cookbook_content": len(lc), "irs_content": len(rc),
            "shared_naive": len(set(lf) & set(rf)),
            "shared_content": len(shared_content),
        },
        "heads": {"cookbook": lhead, "irs": rhead},
        "dropped_examples": dropped,
    }
    out = "/Users/mingli/Adva/AEG/trials/bounded-exchange-round-01/witness-02.json"
    with open(out, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(json.dumps(report, indent=2, ensure_ascii=False)[:2400])


if __name__ == "__main__":
    sys.exit(main())
