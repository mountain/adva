"""Replay a fixed public placement inventory; no fetching, migration or admission.

Original analysis tool: Codex (OpenAI), Unknown v0.3, through Mingli Yuan's
account as authorized proxy; account ownership is not review or endorsement.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

SNAPSHOTS = {
    'mountain/adva': '8585c5b965b84422b802d50f11f375aea171bd27',
    'mountain/adva-library': '95d5f57eabdf89b4e42034f1e61880c9f75d9369',
    'mountain/adva-machine': '2b55219c5c20c4108e6c99d037c9a2b7b04f522e',
}
# Human-readable decisions are in RESEARCH_PLACEMENT_CANDIDATES_V2.md.
POLICIES = {
    'docs/philosophy/0001-': ('public-background', 'retain-public'),
    'docs/philosophy/0002-': ('public-hypothesis', 'retain-public'),
    'docs/philosophy/0003-': ('experiment-agenda', 'retain-public'),
    'docs/philosophy/0004-': ('personal-origin-pointer', 'personal-maintenance-already-placed'),
    'docs/philosophy/0005-': ('personal-origin-pointer', 'personal-maintenance-already-placed'),
    'docs/philosophy/0006-': ('personal-origin-pointer', 'personal-maintenance-already-placed'),
    'docs/philosophy/0007-': ('mixed-session-and-public-method', 'layered-reference-proposed-defer-retirement'),
    'docs/research/0077-': ('finite-evidence-and-premises', 'retain-public'),
    'docs/research/0078-': ('finite-evidence-and-premises', 'retain-public'),
    'docs/research/0079-': ('research-only-bridge-contract', 'retain-public'),
    'docs/research/0080-': ('public-hypothesis-and-premises', 'retain-public'),
    'docs/research/0120-': ('public-gate-proposal', 'retain-public'),
    'docs/research/0129-': ('bounded-trial-contract', 'retain-public'),
    'docs/research/0172-': ('conjecture-refutation-and-evidence', 'retain-public'),
    'docs/research/0174-': ('frozen-documentary-premise', 'retain-public'),
    'docs/research/absurdity-emptiness-record-freeze.md': ('freeze-contract', 'retain-public'),
    'programs/bootstrap-0/trust-continuity-session-witness.adva': ('public-documentary-witness', 'retain-public'),
    'docs/RESEARCH_ENGINEERING_AGENDA.md': ('public-dependency-plan', 'retain-public'),
    'docs/RESEARCH_REFERENCE_IDENTITY.md': ('reference-identity-interface', 'retain-public'),
    'docs/KNOWLEDGE_MACHINE_BOUNDARY.md': ('cross-repository-interface', 'retain-public'),
    'docs/COMMUNICATION_FRAMEWORK.md': ('communication-interface', 'retain-public'),
    'docs/claims.toml': ('claim-and-premise-interface', 'retain-public'),
}

def git(root, *args, acceptable=(0,)):
    p = subprocess.run(['git', '--no-lazy-fetch', '-c', 'protocol.allow=never',
                        '-C', str(root), *args], capture_output=True, timeout=60)
    if p.returncode not in acceptable:
        raise RuntimeError(f'Git unavailable/refused: {root}: {args}: {p.stderr.decode(errors="replace")}')
    return p.stdout


def inventory(roots):
    trees = {}
    for repo, rev in SNAPSHOTS.items():
        git(roots[repo], 'cat-file', '-e', rev + '^{commit}')
        rows = git(roots[repo], 'ls-tree', '-r', rev).decode().splitlines()
        trees[repo] = {row.split('\t', 1)[1]: row.split('\t', 1)[0].split()[2]
                       for row in rows if row.split()[1] == 'blob'}
    repo = 'mountain/adva'
    rev = SNAPSHOTS[repo]
    numbered = [p for p in trees[repo] if re.fullmatch(r'docs/research/[0-9]{4}-[^/]+\.md', p)]
    candidates = {}
    for prefix, policy in POLICIES.items():
        matches = [p for p in trees[repo] if p.startswith(prefix) and '/' not in p[len(prefix):]]
        if not matches:
            raise RuntimeError('Missing candidate: ' + prefix)
        candidates.update({p: policy for p in matches})
    occurrences = {}
    needles = []
    for path in candidates:
        needles.extend(['-e', Path(path).name])
    for other, other_rev in SNAPSHOTS.items():
        occurrences[other] = git(roots[other], 'grep', '-n', '-I', '-F', *needles,
                                 other_rev, '--', acceptable=(0, 1)).decode().splitlines()
    selected = sorted(set(numbered) | set(candidates))
    entries = []
    for path in selected:
        raw = git(roots[repo], 'show', rev + ':' + path)
        row = {'repository': repo, 'commit': rev, 'path': path,
               'git_blob': trees[repo][path], 'sha256': hashlib.sha256(raw).hexdigest(),
               'bytes': len(raw), 'history_url': f'https://github.com/{repo}/blob/{rev}/{path}'}
        if path in candidates:
            row['role'], row['decision'] = candidates[path]
            row['reference_occurrences'] = []
            for other, other_rev in SNAPSHOTS.items():
                # Literal filename occurrences include relative links and registry strings.
                # They are discovery evidence, not a semantic/runtime dependency proof.
                found = [line for line in occurrences[other]
                         if Path(path).name in line.split(':', 3)[3]]
                hits = set()
                for line in found:
                    _, file, lineno, _ = line.split(':', 3)
                    if other == repo and file == path:
                        continue
                    hits.add((file, int(lineno)))
                grouped = {}
                for file, line in sorted(hits):
                    grouped.setdefault(file, []).append(line)
                row['reference_occurrences'].extend(
                    {'repository': other, 'commit': other_rev, 'path': file, 'lines': lines}
                    for file, lines in sorted(grouped.items()))
        else:
            row['role'] = 'inventory-only-not-content-adjudicated'
            row['decision'] = 'defer-retain-current-public-home'
        entries.append(row)
    lock_paths = sorted(p for p in trees[repo] if p.startswith('dependencies/') and p.endswith('.json'))
    locks = []
    for path in lock_paths:
        raw = git(roots[repo], 'show', rev + ':' + path)
        locks.append({'path': path, 'git_blob': trees[repo][path], 'sha256': hashlib.sha256(raw).hexdigest()})
    return {'schema': 'adva.research-placement-inventory.v0.1', 'snapshots': SNAPSHOTS,
            'scope': {'numbered_notes': len(numbered), 'reviewed_files': len(candidates),
                      'cross_repository_search': 'literal filename occurrences in tracked text at three fixed trees',
                      'external_world_references': 'Unknown: repositories outside these three trees not exhaustively searched',
                      'dynamic_consumers': 'Unknown: literal occurrence search is not complete dependency analysis'},
            'authority': {'migration': 'NotExecuted', 'native_admission': 'NotGranted',
                          'KPB14_native_consumer_migration': 'NotEstablishedByThisInventory'},
            'dependency_records': locks, 'entries': entries}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--adva', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--library', type=Path, required=True)
    p.add_argument('--machine', type=Path, required=True)
    p.add_argument('--check', type=Path, help='compare to a retained inventory instead of writing')
    args = p.parse_args()
    roots = {'mountain/adva': args.adva, 'mountain/adva-library': args.library,
             'mountain/adva-machine': args.machine}
    try:
        result = inventory(roots)
        if args.check:
            if result != json.loads(args.check.read_text()):
                raise RuntimeError('Inventory differs from fixed public Git objects or declared policy')
            print('FixedPublicInventoryChecked; migration NotExecuted; native admission NotGranted')
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
    except (RuntimeError, subprocess.TimeoutExpired, OSError, ValueError) as error:
        p.exit(1, f'Unavailable/Rejected: {error}\n')


if __name__ == '__main__':
    main()
