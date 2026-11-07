#!/usr/bin/env python3
"""Reference integrity only. Never invoke Rust or load a request payload.

Original review tooling by Codex (OpenAI), contributed under Unknown v0.3.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess


class Invalid(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Invalid(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(path):
    p = PurePosixPath(path)
    require(not p.is_absolute() and '..' not in p.parts and str(p) == path,
            'noncanonical relative path')
    return p


def validate(contract, manifest, refs, reader, revision):
    """reader supplies committed bytes, not working-tree or external payloads."""
    require(revision == contract['machine_revision'], 'wrong machine revision')
    expected = contract['source_paths']
    require([r['path'] for r in manifest] == expected, 'source roster differs')
    require(len(expected) == len(set(expected)), 'duplicate source')
    require(len(manifest) <= contract['limits']['source_files'], 'source file cap')
    data = {}
    total = 0
    for row in manifest:
        path = row['path']
        safe_path(path)
        require(row['mode'] == '100644', 'source must be regular tracked file')
        raw = reader(path)
        total += len(raw)
        require(len(raw) <= contract['limits']['single_source_bytes'], 'single file cap')
        require(total <= contract['limits']['total_source_bytes'], 'source byte cap')
        require(len(raw) == row['bytes'], 'source size differs')
        require(digest(raw) == row['sha256'], 'source hash differs')
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require(blob == row['git_blob'], 'git blob differs')
        require(len(raw.splitlines()) == row['lines'], 'line count differs')
        raw.decode('utf-8', errors='strict')
        data[path] = raw
    require([r['id'] for r in refs] == contract['reference_ids'], 'reference roster differs')
    require(len(refs) <= contract['limits']['references'], 'reference cap')
    for ref in refs:
        require(ref['path'] in data, 'reference outside selected scope')
        a, b = ref['first_line'], ref['last_line']
        lines = data[ref['path']].splitlines(keepends=True)
        require(type(a) is int and type(b) is int and 1 <= a <= b <= len(lines),
                'invalid line interval')
        require(digest(b''.join(lines[a-1:b])) == ref['range_sha256'], 'range hash differs')
        url = f"https://github.com/mountain/adva-machine/blob/{revision}/{ref['path']}#L{a}-L{b}"
        require(ref['url'] == url, 'reference URL differs')
    return {'source_files':len(manifest), 'source_bytes':total, 'references':len(refs)}


class GitReader:
    def __init__(self, machine, revision, single_cap):
        self.machine = str(Path(machine).resolve())
        self.revision = revision
        self.single_cap = single_cap

    def git(self, *args):
        return subprocess.check_output(['git','-C',self.machine,*args], timeout=3,
                                       stderr=subprocess.PIPE)

    def __call__(self, path):
        safe_path(path)
        entry = self.git('ls-tree',self.revision,'--',path).decode().strip()
        fields = entry.split(None,3)
        require(len(fields) == 4 and fields[0] == '100644' and
                fields[1] == 'blob' and fields[3] == path, 'not a regular pinned blob')
        size = int(self.git('cat-file','-s',fields[2]))
        require(size <= self.single_cap, 'pre-read source cap')
        raw = self.git('cat-file','blob',fields[2])
        require(len(raw) == size, 'truncated git blob')
        return raw


def load_bundle(directory, expected_contract_sha256):
    require(re.fullmatch('[0-9a-f]{64}', expected_contract_sha256) is not None,
            'expected independent contract digest required')
    raw = (directory/'contract.json').read_bytes()
    require(digest(raw) == expected_contract_sha256, 'contract pin mismatch')
    contract = json.loads(raw)
    for name, pin in contract['artifact_pins'].items():
        safe_path(name)
        data = (directory/name).read_bytes()
        require(len(data) == pin['bytes'] and digest(data) == pin['sha256'],
                f'bound artifact mismatch: {name}')
    def read(name): return json.loads((directory/name).read_bytes())
    return contract, read('source-manifest.json'), read('references.json')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--machine', required=True)
    parser.add_argument('--contract-sha256', required=True)
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    contract, manifest, refs = load_bundle(directory, args.contract_sha256)
    reader = GitReader(args.machine, contract['machine_revision'],
                       contract['limits']['single_source_bytes'])
    revision = reader.git('rev-parse','HEAD').decode().strip()
    result = validate(contract, manifest, refs, reader, revision)
    print(json.dumps({'status':'ReferenceIntegrityVerified',**result,
          'semantic_verdict_proved_by_this_tool':False,
          'opaque_request_reads':0,'native_executions':0},sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (Invalid, OSError, UnicodeError, ValueError, subprocess.SubprocessError) as error:
        print(json.dumps({'status':'UnknownOrInvalidEvidence','reason':str(error)}))
        raise SystemExit(1)
