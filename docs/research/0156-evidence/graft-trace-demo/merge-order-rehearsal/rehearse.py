"""§14 六方合并次序排演（合成数据；不是已执行的 merge 证据）。

规则实现：min-residual-first；残差并列按 party 序号字典序 tie-break；
每个合并步骤记录 order_score/order_rank/值一致断言。
"""

import json
from itertools import combinations
from pathlib import Path

OUT = Path("/Users/mingli/Adva/AEG/.merge-rehearsal")


def norm(value):
    """归一化到同一精确表示后比较；本例直接用数值。"""
    return value


def rehearse(parties):
    nodes = {p["id"]: {"value": p["value"], "members": [p["id"]]} for p in parties}
    steps = []
    rank = 0
    while len(nodes) > 1:
        pairs = list(combinations(sorted(nodes), 2))
        best = min(
            (abs(norm(nodes[a]["value"]) - norm(nodes[b]["value"])), a, b)
            for a, b in pairs
        )
        residual, left, right = best
        rank += 1
        value_l, value_r = nodes[left]["value"], nodes[right]["value"]
        assertion = "Verified" if norm(value_l) == norm(value_r) else "Rejected"
        steps.append({
            "order_rank": rank,
            "order_score": residual,
            "left": nodes[left]["members"],
            "right": nodes[right]["members"],
            "left_value": value_l,
            "right_value": value_r,
            "value_assertion": assertion,
            "tie_break": "party-index lexicographic (fixed, replayable)",
        })
        merged_id = f"merged-{rank}"
        nodes[merged_id] = {"value": value_l,
                            "members": nodes[left]["members"] + nodes[right]["members"]}
        del nodes[left]
        del nodes[right]
    return steps


def run_scenario(name, values):
    parties = [{"id": f"P{i}", "value": values[i - 1]} for i in range(1, 7)]
    steps = rehearse(parties)
    record = {
        "schema": "adva.merge-order.rehearsal.v0",
        "version": 0,
        "scenario": name,
        "parties": parties,
        "note": "synthetic rehearsal of 0156 section 14; not executed merge evidence",
        "steps": steps,
    }
    OUT.mkdir(exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    print(f"=== 场景 {name} ===")
    for step in steps:
        print(f"rank={step['order_rank']} score={step['order_score']} "
              f"{'+'.join(step['left'])} ⋈ {'+'.join(step['right'])} "
              f"值 {step['left_value']} vs {step['right_value']} → {step['value_assertion']}")
    return steps


if __name__ == "__main__":
    run_scenario("all-agree", [14.0] * 6)
    print()
    run_scenario("one-tampered", [14.0, 14.0, 14.0, 15.0, 14.0, 14.0])
