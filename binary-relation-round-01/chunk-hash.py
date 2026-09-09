"""Chunk-hash shared-segment detection between two binaries (bounded)."""
import hashlib, json, sys
def chunk(path, size=64):
    h = {}
    with open(path, 'rb') as f:
        data = f.read()
    for i in range(0, max(0, len(data) - size + 1)):
        h.setdefault(hashlib.sha256(data[i:i+size]).hexdigest(), []).append(i)
    return h, len(data)
a, la = chunk(sys.argv[1])
b, lb = chunk(sys.argv[2])
common = {k: (a[k], b[k]) for k in a if k in b}
sizes = sorted({len(v[0]) + len(v[1]) for v in common.values()})
print(json.dumps({
    "size_P": la, "size_Q": lb,
    "chunk_size": 64,
    "common_chunks": len(common),
    "total_shared_offsets": sum(len(v[0]) + len(v[1]) for v in common.values()),
    "P_covered_bytes": sum(len(v[0]) for v in common.values()) * 64,
    "largest_shared_runs": sizes[-5:] if sizes else [],
    "relation_hint": "embedding-candidate" if len(common) > 0.5 * (la // 64) else "shared-fragments-or-none"
}, indent=2))
