"""Bounded documentary citations; shared historical numbers remain valid.

Authored by Codex (OpenAI), through Mingli Yuan's authorized account proxy.
Original contribution under Unknown v0.3.
"""
import copy
import hashlib
import json
import re
from pathlib import Path

import unittest

ROOT = Path(__file__).resolve().parents[2]


def validate(data):
    assert data['schema'] == 'adva.research-reference-identity.v1'
    assert re.fullmatch(r'[0-9a-f]{40}', data['audit_commit'])
    paths = set()
    for note in data['notes']:
        assert note['repository'] == 'mountain/adva'
        assert re.fullmatch(r'docs/research/[0-9]{4}-[a-z0-9-]+\.md', note['path'])
        assert note['path'] not in paths
        paths.add(note['path'])
        assert note['commit'] == data['audit_commit']
        assert re.fullmatch(r'[0-9a-f]{40}', note['introduced_by'])
        assert hashlib.sha256((ROOT / note['path']).read_bytes()).hexdigest() == note['sha256']
    for ref in data['resolutions']:
        assert ref['target'] in paths
        assert ref['source_commit'] == data['audit_commit']
        assert re.fullmatch(r'(docs/research|governance/publication/records)/[a-z0-9-]+\.(md|json)', ref['source_path'])
        raw = (ROOT / ref['source_path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == ref['source_sha256']
        assert type(ref['line']) is int and ref['line'] > 0
        assert raw.decode().splitlines()[ref['line'] - 1] == ref['text']
        assert ref['basis'].strip()


def table():
    return json.loads((ROOT / 'docs/research-reference-identities.json').read_text())


class ReferenceIdentityTests(unittest.TestCase):
    def test_pinned_reference_table_and_shared_number(self):
        data = table()
        validate(data)
        self.assertEqual(len([n for n in data['notes'] if '/0259-' in n['path']]), 2)
        self.assertEqual(len(data['resolutions']), 4)
        self.assertIn('RESEARCH_REFERENCE_IDENTITY.md',
                      (ROOT / 'docs/research/README.md').read_text())

    def test_reject_invalid_new_citations(self):
        for mutation in ['bare', 'commit', 'bytes', 'locator', 'duplicate']:
            with self.subTest(mutation=mutation):
                data = copy.deepcopy(table())
                if mutation == 'bare':
                    data['resolutions'][0]['target'] = 'Research 0259'
                elif mutation == 'commit':
                    data['notes'][0]['commit'] = 'main'
                elif mutation == 'bytes':
                    data['notes'][0]['sha256'] = '0' * 64
                elif mutation == 'locator':
                    data['resolutions'][0]['line'] += 1
                else:
                    data['notes'].append(copy.deepcopy(data['notes'][0]))
                with self.assertRaises(AssertionError):
                    validate(data)
