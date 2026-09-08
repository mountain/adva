"""有界推进循环（bounded advance loop）：直到 breakthrough 扩权或周期上限。

纪律（Research 0129 §4 / 0139）：
- 循环有界：max_cycles 上限，每周期预算显式，耗尽报 Unknown 并停止；
- breakthrough 扩权只来自授权标记文件（人类输入），循环**不自行扩权**；
- 每周期修订合同记录在案；无自动加油、无静默闭环；
- 全部见证保留（归档不删除）。

授权标记格式（由人类/授权方写入）：
  AEG/.breakthrough-auth.json = {"authorized_length": 35}
"""

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/Users/mingli/Adva/adva")
CAMPAIGN = Path("/Users/mingli/Adva/AEG/.campaign")
BREAK = Path("/Users/mingli/Adva/AEG/.breakthrough")
AUTH = Path("/Users/mingli/Adva/AEG/.breakthrough-auth.json")
BIN = REPO / "target/debug/adva-labs-search"
MAX_CYCLES = 3          # 有界：本演示周期上限
PIPELINE_ROUNDS = 100   # 每周期流水线遍数（已授权模式）
CURRENT_LENGTH = 31     # 已完成的 breakthrough 最大族长
ITERATIONS = 10_000
SEED = 1


def archive_previous(cycle):
    target = CAMPAIGN / f"archive-cycle{cycle}"
    target.mkdir(exist_ok=True)
    moved = 0
    for name in ("round-*", "summary.json"):
        for path in list(CAMPAIGN.glob(name)):
            shutil.move(str(path), target)
            moved += 1
    return moved


def run_pipeline(cycle):
    """100 遍六槽流水线（learn→run→free 阻塞），返回汇总。"""
    sys.path.insert(0, str(CAMPAIGN))
    spec = __import__("importlib.util").util.spec_from_file_location(
        "driver", CAMPAIGN / "driver.py")
    driver = __import__("importlib.util").util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    import io
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        driver.main()
    summary = json.loads((CAMPAIGN / "summary.json").read_text())
    return summary["aggregates"]


def read_auth():
    if not AUTH.is_file():
        return None
    value = json.loads(AUTH.read_text())
    length = value.get("authorized_length")
    if isinstance(length, int) and length > CURRENT_LENGTH:
        return length
    return None


def run_breakthrough_until(authorized):
    """从 CURRENT+1 滚到 authorized（每步修订合同 + 复核 + 负控制）。"""
    global CURRENT_LENGTH
    rows = []
    for length in range(CURRENT_LENGTH + 1, authorized + 1):
        run = length - 19
        contract = json.loads(json.dumps(
            json.load(open(BREAK / f"contract-run{run - 1}.json",
                           encoding="utf-8"))))
        contract["revision"] = {"reason": "advance loop: authorized extension",
                                "changed": f"length {length - 1} -> {length}",
                                "unchanged": "checker, seed 1, iterations 10000, workers 1, budgets"}
        contract["1_question_and_level"]["input_family"] = \
            f"All length-{length} binary sequences over {{-1, +1}}"
        contract["6_resources_and_exit"]["length"] = length
        contract["6_resources_and_exit"]["continuation_count"] = run
        contract["continuation_of"] = f"run {run - 1} (length {length - 1})"
        (BREAK / f"contract-run{run}.json").write_text(
            json.dumps(contract, indent=2), encoding="utf-8")
        subprocess.run([str(BIN), "search", "--length", str(length),
                        "--iterations", str(ITERATIONS), "--seed", str(SEED),
                        "--workers", "1", "--output",
                        str(BREAK / f"run{run}-report.json")],
                       capture_output=True, text=True, timeout=120)
        verify = subprocess.run([str(BIN), "verify",
                                 str(BREAK / f"run{run}-report.json")],
                                capture_output=True, text=True, timeout=30)
        report = json.loads((BREAK / f"run{run}-report.json").read_text())
        tampered = dict(report)
        tampered["best"] = dict(report["best"], energy=report["best"]["energy"] + 1)
        (BREAK / f"run{run}-tampered.json").write_text(json.dumps(tampered))
        neg = subprocess.run([str(BIN), "verify",
                              str(BREAK / f"run{run}-tampered.json")],
                             capture_output=True, text=True, timeout=30)
        rows.append({"run": run, "length": length,
                     "energy": report["best"]["energy"],
                     "merit": report["best"]["merit_factor"],
                     "verify_exit": verify.returncode,
                     "tamper_rejected": "mismatch" in neg.stderr})
        CURRENT_LENGTH = length
        print(f"  breakthrough run{run} (length {length}): energy="
              f"{report['best']['energy']} verify={verify.returncode} "
              f"neg={'mismatch' in neg.stderr}", flush=True)
    return rows


def main():
    cycle_log = []
    authorized = read_auth()
    for cycle in range(1, MAX_CYCLES + 1):
        print(f"=== cycle {cycle}/{MAX_CYCLES} ===", flush=True)
        moved = archive_previous(cycle)
        started = time.monotonic()
        aggregates = run_pipeline(cycle)
        wall = round(time.monotonic() - started, 1)
        cycle_log.append({"cycle": cycle, "pipeline": aggregates,
                          "wall_s": wall, "archived_files": moved})
        print(f"  pipeline: learn={aggregates['learn_completed']}/100 "
              f"free={aggregates['free_adapter_unavailable']}/100 ({wall}s)",
              flush=True)
        authorized = read_auth() or authorized
        if authorized is not None:
            print(f"  breakthrough 扩权: authorized_length={authorized}",
                  flush=True)
            rows = run_breakthrough_until(authorized)
            summary = {
                "schema": "adva.bounded-advance-loop.summary.v0",
                "version": 0,
                "status": "Completed",
                "reason": f"breakthrough authorized to length {authorized} "
                          "and completed within the declared cycles",
                "cycles": cycle_log,
                "breakthrough": rows,
            }
            (CAMPAIGN / "advance-loop-summary.json").write_text(
                json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
            print("loop status: Completed")
            return summary
    summary = {
        "schema": "adva.bounded-advance-loop.summary.v0",
        "version": 0,
        "status": "Unknown",
        "reason": "no breakthrough authorization within the declared "
                  f"{MAX_CYCLES} cycles; stopped by the cycle bound, not by "
                  "an authorization",
        "cycles": cycle_log,
        "breakthrough": [],
        "continuation": "write AEG/.breakthrough-auth.json with "
                        "{\"authorized_length\": N} and rerun",
    }
    (CAMPAIGN / "advance-loop-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print("loop status: Unknown (cycle bound reached without authorization)")
    return summary


if __name__ == "__main__":
    main()
