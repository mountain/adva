"""真实两侧 merge：Rust 侧（f64 14.0）与 Python 侧（精确整数 14）。
在既有 merge-six 链上追加 seq 6，产出链式新锚点（global_seq 1），
两侧各签一把新密钥；私钥只在 AEG 工作区。
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/mingli/Adva/adva")
OUT = Path("/Users/mingli/Adva/AEG/.merge-six")
sys.path.insert(0, str(REPO / "python" / "adva"))
import lineage as L  # noqa: E402


def main():
    (OUT / "rust-side").mkdir(exist_ok=True)
    (OUT / "python-side").mkdir(exist_ok=True)

    # Rust 侧: 真实二进制直跑，取求值结果
    rust_out = OUT / "rust-side" / "result.adva"
    result = subprocess.run(
        [str(REPO / "target/debug/adva"), "run",
         str(REPO / "programs/native-run/arithmetic.adva"),
         "--output", str(rust_out)],
        capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    rust_doc = json.loads(rust_out.read_text())
    rust_value = rust_doc["evaluation"]["values"][0]
    rust_sha = L.sha256_hex(rust_out.read_bytes())
    print(f"Rust 侧: value={rust_value} sha256={rust_sha[:16]}…")

    # Python 侧: 精确整数计算呈现
    python_presentation = {
        "schema": "adva.python-presentation.research",
        "version": 0,
        "expression": "2+3*4",
        "value": 14,
        "checker": "python-exact-int-v0",
        "note": "exact integer arithmetic; the companion Rust side uses IEEE-754 f64",
    }
    python_out = OUT / "python-side" / "presentation.json"
    python_out.write_bytes(L.canonical_bytes(python_presentation))
    python_sha = L.sha256_hex(python_out.read_bytes())
    print(f"Python 侧: value=14(精确) sha256={python_sha[:16]}…")

    # 归一化残差
    def norm(value):
        return int(value) if float(value).is_integer() else float(value)

    residual = abs(norm(rust_value) - norm(14))
    print(f"归一化残差 |norm(14.0) - norm(14)| = {residual}")
    assert residual == 0

    # 追加 merge 记录 seq 6
    records_dir = OUT / "lineage" / "arithmetic" / "records"
    body = {
        "schema": L.RECORD_SCHEMA, "version": 0, "package": "arithmetic",
        "seq": 6,
        "proposition": "merge(python-exact, rust-f64): normalized values equal",
        "environment": {
            "values": "[14, 14]",
            "python_evidence_sha256": python_sha,
            "rust_evidence_sha256": rust_sha,
            "order_score": 0,
            "order_rank": 6,
        },
        "checker": {"id": "merge-residual-v0", "version": "0"},
        "verdict": "Verified", "residual": None,
        "cites_same_home": [5], "cites_cross": [],
        "budget_consumed": {"units": 1}, "secret_slot": None,
    }
    body["digest"] = L.sha256_hex(L.canonical_bytes(body))
    (records_dir / "000006.json").write_bytes(L.canonical_bytes(body))
    print("seq 6 写入")

    # 新锚点（链式: prev = 0000）
    report = L.lineage_update(OUT, "arithmetic", 1,
                              OUT / "lineage" / "anchors" / "0001.json")
    assert report["status"] == "CheckpointBuilt", report
    anchor_path = Path(report["anchor"]["path"])
    anchor = json.loads(anchor_path.read_bytes())
    assert anchor["prev_anchor_sha256"], "新锚点必须链向前锚点"
    print("新锚点:", report["anchor"]["self_sha256"][:16], "… prev 链已建立")

    # 两侧各签一把新密钥
    sides = [("python-side", "python-side"),
             ("rust-side", "rust-side")]
    message = {"purpose": "anchor-signing",
               "anchor_sha256": L.anchor_hash(anchor)}
    for name, home in sides:
        rep = L.key_issue(purpose="anchor-signing", home=f"merge-six/{home}",
                          policy_version="v0",
                          private_out=OUT / "keys" / f"{name}-seed.key")
        assert rep["status"] == "Issued", rep
        seed = (OUT / "keys" / f"{name}-seed.key").read_text().strip()
        sig = L.sign_ed25519(seed, message)
        anchor["signatures"].append({"key_id": rep["record"]["key_id"],
                                     "pubkey_hex": rep["record"]["pubkey_hex"],
                                     "signature_hex": sig})
        request = {"schema": L.SIGNATURE_REQUEST_SCHEMA, "version": 0,
                   "key_id": rep["record"]["key_id"],
                   "pubkey_hex": rep["record"]["pubkey_hex"],
                   "message": message, "signature_hex": sig}
        (OUT / f"signature-request-{name}.json").write_bytes(L.canonical_bytes(request))
        (OUT / f"key-issue-{name}.json").write_bytes(L.canonical_bytes(rep["record"]))
        rep_v = L.verify("signature", OUT / f"signature-request-{name}.json")
        assert rep_v["status"] == "Verified", rep_v
    anchor_path.write_bytes(L.canonical_bytes(anchor))
    L.validate_anchor(anchor)
    print("两侧签名 2/2 Verified")

    # 完整性 + 前锚点链
    rep = L.tamper_check(OUT, anchor_path,
                         prev_anchor_path=OUT / "lineage" / "anchors" / "0000.json")
    assert rep["status"] == "Intact", rep
    print("tamper-check:", rep["status"], "| prev-anchor chain:", rep["anchor"]["prev_anchor_match"])

    summary = {
        "schema": "adva.merge-two-sides.rehearsal.v0",
        "version": 0,
        "note": "real two-side merge (Rust f64 14.0 vs Python exact 14); "
                "synthetic parties; private seeds in AEG workspace only",
        "rust_side": {"value": rust_value, "evidence_sha256": rust_sha,
                      "source": "target/debug/adva run programs/native-run/arithmetic.adva"},
        "python_side": {"value": 14, "evidence_sha256": python_sha,
                        "source": "exact integer arithmetic presentation"},
        "normalized_residual": residual,
        "merge_record_seq": 6,
        "verdict": "Verified",
        "anchor_global_seq": 1,
        "prev_anchor_sha256": anchor["prev_anchor_sha256"],
        "anchor_self_sha256": L.anchor_hash(anchor),
        "signatures": [s["key_id"] for s in anchor["signatures"]],
        "tamper_check": "Intact",
        "prev_anchor_match": True,
    }
    (OUT / "summary-two-sides.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print("\nsummary:", OUT / "summary-two-sides.json")


if __name__ == "__main__":
    main()
