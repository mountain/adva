#!/usr/bin/env python3
"""Round-04 benchmark: direct baseline B, index formation F, reuse R.

One baseline, one index build, one reuse query, one stale-rule control.
All stages itemized; unallocated remainder reported. Writes:
  - index-04.json            (the isolated saved index artifact)
  - index-04-mutated.json    (synthetic metadata-mismatch copy, refused)
  - reuse-measure-04.json    (raw measurements)
"""
import hashlib
import json
import subprocess
import sys
import time
import resource

sys.path.insert(0, "/Users/mingli/Adva/AEG/trials/bounded-exchange-round-01")
import reuse_rules as R  # noqa: E402

BASE = "/Users/mingli/Adva/AEG/trials/bounded-exchange-round-01"
SRC = {
    "left": "/Users/mingli/Adva/AEG/trials/unrelated-pair-round-01/cookbook-layer.txt",
    "right": "/Users/mingli/Adva/AEG/trials/unrelated-pair-round-01/irs-layer.txt",
}


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    with open(path, "rb") as f:
        return sha_bytes(f.read())


def now():
    return time.perf_counter()


def projection_for(text):
    lines = R.filtered_lines(text)
    toks = R.content_tokens(text)
    freq, rank, fd, order = R.build_freq_rank(toks)
    loc, span = R.context_from_lines(lines)
    return {"frequency": freq, "rank": rank, "locator": loc,
            "context": span, "content_tokens": len(toks)}


def main():
    t_start = now()
    # ---- shared setup (reported, excluded from B/F/R totals) ----
    t_setup = now()
    rule_pin = sha_file(R.__file__)
    stoplist_pin = sha_bytes("\n".join(sorted(R.STOP)).encode())
    texts = {k: open(v, encoding="utf-8").read() for k, v in SRC.items()}
    source_pins = {k: sha_bytes(t.encode()) for k, t in texts.items()}
    t_shared_setup = now() - t_setup

    # ---- B: one direct baseline, complete projection ----
    b_stages = {}
    t = now()
    lines = {k: R.filtered_lines(v) for k, v in texts.items()}
    b_stages["lines"] = now() - t
    t = now()
    toks = {k: R.content_tokens(v) for k, v in texts.items()}
    b_stages["tokenize"] = now() - t
    t = now()
    proj_B = {}
    for side in ("left", "right"):
        f, rk, fd, order = R.build_freq_rank(toks[side])
        loc, span = R.context_from_lines(lines[side])
        proj_B[side] = {"frequency": f, "rank": rk, "locator": loc,
                        "context": span, "content_tokens": len(toks[side])}
    b_stages["rank_and_context"] = now() - t
    t = now()
    b_serialized = json.dumps(proj_B)
    b_stages["serialize"] = now() - t
    B = sum(b_stages.values())

    # ---- F: fresh index build in an isolated artifact ----
    f_stages = {}
    t = now()
    toks_f = {k: R.content_tokens(v) for k, v in texts.items()}
    f_stages["tokenize"] = now() - t
    t = now()
    index_sides = {}
    for side in ("left", "right"):
        fd = {}
        for tk in toks_f[side]:
            fd[tk] = fd.get(tk, 0) + 1
        order = sorted(fd, key=lambda w: -fd[w])
        rank = {w: i + 1 for i, w in enumerate(order)}
        word_lines = {}
        for lineno, ln in enumerate(lines[side], 1):
            for tk in R.TOKEN.findall(ln):
                tk = tk.lower()
                if tk not in R.STOP and not tk.isdigit():
                    word_lines.setdefault(tk, []).append(lineno)
        index_sides[side] = {
            "lines": lines[side],
            "tokens": {w: {"freq": fd[w], "rank": rank[w],
                           "lines": word_lines.get(w, [])}
                       for w in fd},
        }
    f_stages["build"] = now() - t
    t = now()
    index = {
        "kind": "bounded-exchange-word-index-v1",
        "source_sha256": source_pins,
        "rule_sha256": rule_pin,
        "stoplist_sha256": stoplist_pin,
        "sides": index_sides,
    }
    serialized = json.dumps(index)
    f_stages["serialize"] = now() - t
    t = now()
    index_path = BASE + "/index-04.json"
    with open(index_path, "w") as f:
        f.write(serialized)
    f_stages["write"] = now() - t
    t = now()
    index_pin = sha_file(index_path)
    f_stages["pin"] = now() - t
    t = now()
    reloaded = json.load(open(index_path))
    assert reloaded["sides"]["left"]["tokens"][R.TARGET]["freq"] == proj_B["left"]["frequency"]
    assert reloaded["sides"]["right"]["tokens"][R.TARGET]["rank"] == proj_B["right"]["rank"]
    f_stages["validate"] = now() - t
    F = sum(f_stages.values())

    # ---- stale-rule control: synthetic mutated copy must be refused ----
    t = now()
    mutated = dict(index)
    mutated["rule_sha256"] = "0" * 64
    mutated_path = BASE + "/index-04-mutated.json"
    with open(mutated_path, "w") as f:
        json.dump(mutated, f)
    cp = subprocess.run([sys.executable, BASE + "/reuse_query.py", mutated_path],
                        capture_output=True, text=True, timeout=30)
    control = {
        "refused": cp.returncode != 0 or '"refused": true' in cp.stdout,
        "exit_code": cp.returncode,
        "seconds": now() - t,
    }

    # ---- R: fresh-process reload, verify, query, serialize ----
    t = now()
    cp = subprocess.run([sys.executable, BASE + "/reuse_query.py", index_path],
                        capture_output=True, text=True, timeout=30)
    r_total = now() - t
    r_report = json.loads(cp.stdout)
    proj_R = r_report["projection"]
    R_cost = r_report["total_seconds"]

    # ---- comparison and accounting ----
    equal = proj_B == proj_R
    amortize = None
    if B > R_cost:
        amortize = {"formula": "floor(F/(B-R))+1",
                    "N_star": int(F // (B - R_cost)) + 1,
                    "B": B, "F": F, "R": R_cost}
    report = {
        "schema": "aeg.bounded-exchange.reuse-measure-04",
        "rule_pin": rule_pin,
        "stoplist_pin": stoplist_pin,
        "source_pins": source_pins,
        "index_pin": index_pin,
        "index_size_bytes": len(serialized.encode()),
        "baseline": {"projection": proj_B, "stages": b_stages,
                     "B_seconds": B},
        "formation": {"stages": f_stages, "F_seconds": F},
        "reuse": {"stages": r_report["stage_seconds"],
                  "R_seconds": R_cost,
                  "wall_subprocess_seconds": r_total,
                  "peak_memory_bytes": r_report["peak_memory_bytes"]},
        "stale_rule_control": control,
        "result_comparison": {"baseline_equals_reloaded": equal},
        "amortization": amortize,
        "shared_setup_seconds": t_shared_setup,
        "total_wall_seconds": now() - t_start,
        "unallocated_seconds": (now() - t_start) - t_shared_setup - B - F - r_total,
        "builder_peak_memory_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "cache_assumptions": ("R runs in a fresh interpreter right after F; OS page "
                              "cache is warm; warm-cache is not a cold-start claim"),
    }
    with open(BASE + "/reuse-measure-04.json", "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(json.dumps({k: report[k] for k in
          ("baseline", "formation", "reuse", "stale_rule_control",
           "result_comparison", "amortization", "index_size_bytes",
           "shared_setup_seconds", "total_wall_seconds",
           "unallocated_seconds")}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
