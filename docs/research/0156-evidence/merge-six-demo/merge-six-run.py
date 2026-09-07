"""真实 6 方 merge 排演（0156 Phase 0 机制端到端）：
key-issue x6 → §14 次序 → merge 步骤入 lineage 链 → 锚点 → 六方签名 → 复核。

注意: 私钥种子只写入 AEG 工作区，绝不进入仓库。
"""

import json
import shutil
import sys
from pathlib import Path

REPO = Path("/Users/mingli/Adva/adva")
OUT = Path("/Users/mingli/Adva/AEG/.merge-six")
sys.path.insert(0, str(REPO / "python" / "adva"))
import lineage as L  # noqa: E402


def merge_order(parties):
    nodes = {p["id"]: {"value": p["value"], "members": [p["id"]]} for p in parties}
    steps = []
    rank = 0
    while len(nodes) > 1:
        pairs = [(a, b) for a in sorted(nodes) for b in sorted(nodes) if a < b]
        residual, left, right = min(
            (abs(nodes[a]["value"] - nodes[b]["value"]), a, b) for a, b in pairs)
        rank += 1
        assertion = "Verified" if nodes[left]["value"] == nodes[right]["value"] else "Rejected"
        steps.append({"order_rank": rank, "order_score": residual,
                      "left": nodes[left]["members"], "right": nodes[right]["members"],
                      "value_assertion": assertion})
        merged = f"merged-{rank}"
        nodes[merged] = {"value": nodes[left]["value"],
                         "members": nodes[left]["members"] + nodes[right]["members"]}
        del nodes[left], nodes[right]
    return steps


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "keys").mkdir(parents=True)
    records_dir = OUT / "lineage" / "arithmetic" / "records"
    records_dir.mkdir(parents=True)

    parties = [{"id": f"P{i}", "value": 14.0} for i in range(1, 7)]
    keys = {}
    key_records = []
    for party in parties:
        report = L.key_issue(purpose="anchor-signing",
                             home=f"merge-six/{party['id']}",
                             policy_version="v0",
                             private_out=OUT / "keys" / f"{party['id']}.seed")
        assert report["status"] == "Issued", report
        seed = (OUT / "keys" / f"{party['id']}.seed").read_text().strip()
        keys[party["id"]] = {"seed": seed,
                             "pubkey_hex": report["record"]["pubkey_hex"],
                             "key_id": report["record"]["key_id"]}
        key_records.append(report["record"])
        (OUT / f"key-issue-{party['id']}.json").write_bytes(
            L.canonical_bytes(report["record"]))
    print("key-issue: 6/6 Issued")

    steps = merge_order(parties)
    merge_steps = []
    for step in steps:
        merge_steps.append(step)
        print(f"rank={step['order_rank']} score={step['order_score']} "
              f"{'+'.join(step['left'])} ⋈ {'+'.join(step['right'])} → {step['value_assertion']}")

    # merge 步骤作为 lineage 链记录
    for seq, step in enumerate(steps, 1):
        body = {
            "schema": L.RECORD_SCHEMA, "version": 0, "package": "arithmetic",
            "seq": seq,
            "proposition": f"merge({' + '.join(step['left'])}, {' + '.join(step['right'])}): values equal",
            "environment": {"values": "[14, 14]",
                            "order_score": int(step["order_score"]),
                            "order_rank": step["order_rank"]},
            "checker": {"id": "merge-residual-v0", "version": "0"},
            "verdict": step["value_assertion"], "residual": None,
            "cites_same_home": [seq - 1] if seq > 1 else [],
            "cites_cross": [], "budget_consumed": {"units": 1},
            "secret_slot": None,
        }
        body["digest"] = L.sha256_hex(L.canonical_bytes(body))
        (records_dir / f"{seq:06d}.json").write_bytes(L.canonical_bytes(body))
    print("lineage records: 5 merge steps written")

    # 锚点
    report = L.lineage_update(OUT, "arithmetic", 0,
                              OUT / "lineage" / "anchors" / "0000.json")
    assert report["status"] == "CheckpointBuilt", report
    anchor_path = Path(report["anchor"]["path"])
    anchor = json.loads(anchor_path.read_bytes())

    # 六方在锚点哈希上的真实签名
    message = {"purpose": "anchor-signing",
               "anchor_sha256": L.anchor_hash(anchor)}
    signature_requests = []
    for party in parties:
        pid = party["id"]
        sig = L.sign_ed25519(keys[pid]["seed"], message)
        anchor["signatures"].append({"key_id": keys[pid]["key_id"],
                                     "pubkey_hex": keys[pid]["pubkey_hex"],
                                     "signature_hex": sig})
        request = {"schema": L.SIGNATURE_REQUEST_SCHEMA, "version": 0,
                   "key_id": keys[pid]["key_id"],
                   "pubkey_hex": keys[pid]["pubkey_hex"],
                   "message": message, "signature_hex": sig}
        signature_requests.append(request)
        (OUT / f"signature-request-{pid}.json").write_bytes(L.canonical_bytes(request))
    anchor_path.write_bytes(L.canonical_bytes(anchor))  # self_sha256 不变(签名被排除)
    L.validate_anchor(anchor)
    print("anchor signed by 6 parties; validate_anchor OK")

    # 签名复核 x6
    verified = 0
    for party in parties:
        rep = L.verify("signature", OUT / f"signature-request-{party['id']}.json")
        assert rep["status"] == "Verified", rep
        verified += 1
    print(f"signature verify: {verified}/6 Verified")

    # 链完整性
    rep = L.tamper_check(OUT, anchor_path)
    assert rep["status"] == "Intact", rep
    print("tamper-check:", rep["status"])

    # 负控制: 篡改 merge 记录 3
    tampered = OUT.parent / ".merge-six-tampered"
    if tampered.exists():
        shutil.rmtree(tampered)
    shutil.copytree(OUT, tampered)
    path = tampered / "lineage" / "arithmetic" / "records" / "000003.json"
    text = json.loads(path.read_bytes())
    text["proposition"] = "merge: values equal (tampered)"
    path.write_bytes(L.canonical_bytes(text))
    rep = L.tamper_check(tampered, tampered / "lineage" / "anchors" / "0000.json")
    divergence = rep["packages"]["arithmetic"]["first_divergence"]
    print("negative control:", rep["status"], "at seq", divergence["seq"])
    assert rep["status"] == "Tampered" and divergence["seq"] == 3

    summary = {
        "schema": "adva.merge-six.rehearsal.v0",
        "version": 0,
        "note": "real Ed25519 keys and signatures, synthetic parties; "
                "private seeds retained in AEG workspace only, never in the repository",
        "parties": [{"id": p["id"], "value": p["value"],
                     "key_id": keys[p["id"]]["key_id"]} for p in parties],
        "merge_steps": merge_steps,
        "anchor_self_sha256": L.anchor_hash(anchor),
        "signatures_verified": verified,
        "tamper_check": "Intact",
        "negative_control": {"status": "Tampered", "seq": 3},
        "files": {"public": sorted(
            p.name for p in OUT.iterdir() if p.is_file()) +
            ["lineage/anchors/0000.json", "lineage/arithmetic/records/*"]},
    }
    (OUT / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print("\nsummary:", OUT / "summary.json")
    print("私钥种子位置(不进仓库):", OUT / "keys/")


if __name__ == "__main__":
    main()
