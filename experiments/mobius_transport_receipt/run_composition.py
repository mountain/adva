"""Two-child supervisor with fresh replay and measured checkpoint comparison."""
import argparse
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output-dir', required=True)
    args = ap.parse_args()
    root = Path(args.output_dir)
    root.mkdir(parents=True, exist_ok=True)
    report_path = root/'execution.json'
    if report_path.exists() or any((root/n).exists() for n in ('primary.json', 'replay.json')):
        raise SystemExit('Refusing to overwrite existing evidence')
    started = time.perf_counter()
    ledger, payloads = [], []
    for name in ('primary', 'replay'):
        begin = time.perf_counter()
        cmd = [sys.executable, '-B', '-S', str(Path(__file__).with_name('compose.py')), '--output', str(root/(name+'.json'))]
        try:
            run = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            entry = {'name': name, 'elapsed_ms_through_child_exit': 1000*(time.perf_counter()-begin),
                     'returncode': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr}
        except subprocess.TimeoutExpired:
            ledger.append({'name': name, 'status': 'UnknownResource', 'reason': 'outer timeout'})
            break
        ledger.append(entry)
        if run.returncode != 0:
            break
        with (root/(name+'.json')).open() as f:
            payload = json.load(f)
        payloads.append(payload)
        if payload.get('status') != 'Passed':
            break
    compare_start = time.perf_counter()
    body = lambda x: {k:v for k,v in x.items() if k != 'cost'}
    equal = len(payloads) == 2 and all(p.get('status') == 'Passed' for p in payloads) and body(payloads[0]) == body(payloads[1])
    # Exercise comparison against one changed semantic field without a new run.
    changed_rejected = False
    if equal:
        changed = json.loads(json.dumps(body(payloads[1])))
        changed['cases'][0]['result']['history']['route_ids'].reverse()
        changed_rejected = changed != body(payloads[0])
    comparison_ms = 1000*(time.perf_counter()-compare_start)
    report = {'status': 'Passed' if equal and changed_rejected else 'UnknownOrInvalidEvidence',
              'invocations': ledger, 'same_non_timing_evidence': equal,
              'changed_ordered_history_rejected': changed_rejected,
              'comparison_ms': comparison_ms,
              'elapsed_through_comparison_ms': 1000*(time.perf_counter()-started),
              'supervisor_peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              'child_peak_rss_kib': resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
              'corrections': 0, 'remote_save_and_final_supervisor_write_cost': 'not measured'}
    report_path.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))

if __name__ == '__main__':
    main()
