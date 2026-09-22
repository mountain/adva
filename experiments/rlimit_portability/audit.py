"""Read-only inventory of RLIMIT_AS references; categories are reviewed, not inferred safety proofs."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

GUARDED = {
    'python/adva/adva.py': 'prime_check rejects non-Linux before Popen(_limits); the verifier-search dispatch is separate',
    'python/adva/operator_receipt.py': 'run rejects non-Linux before input processing and Popen(limits)',
    'experiments/judgment_distinction/calibration.py': 'main rejects non-Linux before installing limits',
    'experiments/borromean_surface_audit/check.py': 'main rejects non-Linux; contract requires Linux',
    'experiments/borromean_longitude_audit/check.py': 'run rejects non-Linux with Exhausted before install',
    'experiments/sharkovsky_interval_extension/check.py': 'install rejects non-Linux with Exhausted',
    'experiments/triadic_period_bridge/check.py': 'install rejects non-Linux with Exhausted',
}
CONDITIONAL = {
    'python/adva/quine_relay.py', 'experiments/phase_runner/run_six.py',
    'experiments/pascal_commutator_certificate/run.py',
}
RECORDED = {
    'experiments/golden_ratio/calibration.py',
    'experiments/li_yorke_period_three/replay.py',
    'experiments/reflexive_lattice_gate/calibration.py',
}
NOTES = {
    'python/adva/verifier_search.py': 'Supervisor.call reaches child_limits without a platform gate. run catches SubprocessError as Blocked; dependencies may fail first. search_campaign reuses the pinned child_limits. Do not weaken or re-pin.',
    'experiments/execution_performance/run.py': 'Linux scheduler affinity is an additional portability blocker; an AS guard alone is insufficient.',
    'experiments/murphy/run.py': 'Only Python children install AS; outer handler reports Failed on preexec refusal. Non-Python children do not execute this AS call.',
    'experiments/representation_residual/run.py': 'AS call is in the optional native-backend branch, not the pure Python portion.',
    'experiments/frame_covariance/run.py': 'main installs AS before trial. New separate portable replay bypasses only main; source/contract/evidence unchanged.',
}


def inventory():
    rows = []
    paths = sorted([*ROOT.joinpath('experiments').rglob('*.py'), *ROOT.joinpath('python/adva').rglob('*.py')])
    for path in paths:
        name = str(path.relative_to(ROOT))
        if name.startswith('experiments/rlimit_portability/'):
            continue
        raw = path.read_bytes()
        text = raw.decode()
        if 'RLIMIT_AS' not in text:
            continue
        frozen = ('evidence' in path.parts or 'run-01' in path.parts or 'before-' in path.name)
        if frozen:
            category, reason = 'historical-source', 'Frozen source snapshot; preserve bytes. Legacy invocation can still refuse AS; snapshot presence is not a live-path bug.'
        elif name in GUARDED:
            category, reason = 'linux-required-entry', GUARDED[name]
        elif name in CONDITIONAL:
            category, reason = 'linux-only-install', 'AS installation is platform guarded. Does not imply every advertised memory bound is enforced on Darwin.'
        elif name in RECORDED:
            category, reason = 'refusal-recorded', 'ValueError/OSError is caught at installation and refusal is recorded. No Darwin memory guarantee follows.'
        elif name == 'experiments/numeric_boundary_audit/audit.py':
            category, reason = 'mock-only', 'RLIMIT_AS belongs to a mock resource namespace; no real AS installation here.'
        else:
            category, reason = 'unguarded-installation', NOTES.get(name, 'No Darwin platform guard or local refusal-recording around this installation. Reaching it on a refusing host aborts the limiter; an outer handler may classify failure. Preserve contract until separately scoped.')
        tree = ast.parse(text)
        sites = []
        for node in ast.walk(tree):
            if (isinstance(node, ast.Attribute) and node.attr == 'RLIMIT_AS') or (isinstance(node, ast.Constant) and node.value == 'RLIMIT_AS'):
                owners = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.lineno <= node.lineno <= n.end_lineno]
                owner = min(owners, key=lambda n: n.end_lineno-n.lineno).name if owners else '<module>'
                sites.append({'line':node.lineno,'function':owner})
        rows.append({'path':name,'sha256':hashlib.sha256(raw).hexdigest(), 'category':category,
                     'sites': sorted(sites,key=lambda x:x['line']), 'reason':reason})
    return {'schema':'adva.engineering.rlimit-as-inventory.v1',
            'scope':'All Python source files under experiments/ and python/adva/ containing RLIMIT_AS; archives are not unpacked. One row per file, all AST reference sites listed. Static reachability review, not a Darwin execution claim.',
            'counts':dict(sorted(Counter(r['category'] for r in rows).items())), 'files':rows}


if __name__ == '__main__':
    print(json.dumps(inventory(), indent=2, sort_keys=True))
