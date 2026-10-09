"""Three-point successor calibration, original contribution under Unknown v0.3.

Authored by Codex (OpenAI) through Mingli Yuan's authorized account proxy;
not his authorship, review or endorsement. Eight analyses and 23 receiver calls.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / 'experiments/program_positivity'
SUCCESSOR = ENGINE / 'three_point'


def load(name):
    key = 'adva_three_point_' + name
    spec = importlib.util.spec_from_file_location(key, ENGINE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


meta, verifier = load('meta'), load('verifier')


def query(report, name='pair'):
    return next(q for q in report['queries'] if q['name'] == name)


class ThreePointCalibration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads((SUCCESSOR / 'cases.json').read_text())
        cls.reports = {name: meta.analyze(r) for name, r in cls.cases.items()}

    def test_observation_equivalence_preserves_three_indexed_trials(self):
        r = self.reports['basic']
        self.assertEqual(r['n'], 3)
        self.assertEqual(r['full_mask'], 7)
        self.assertEqual([t['outputs']['y'] for t in r['trace']], ['1', '1', '4'])
        self.assertEqual([t['observations'] for t in r['trace']],
                         [{'large': False}, {'large': False}, {'large': True}])
        self.assertEqual(r['regions'], {'all': 7, 'empty': 0, 'large': 4, 'pair': 3})
        # Exact full-powerset models, including unnamed regions that distinguish
        # observationally equal points. No quotient is licensed by equal outputs.
        self.assertEqual({tuple(m['positive_masks']) for m in r['models']},
                         {(1, 3, 5, 7), (2, 3, 6, 7), (4, 5, 6, 7), (3, 5, 6, 7)})
        self.assertEqual(query(r)['classification'], 'Underdetermined')
        self.assertEqual(query(r)['positive_model_count'], 3)
        self.assertEqual(query(r)['negative_model_count'], 1)
        self.assertIn(3, r['models'][query(r)['positive_witness']]['positive_masks'])
        self.assertNotIn(3, r['models'][query(r)['negative_witness']]['positive_masks'])

    def test_policies_change_models_and_decisions(self):
        joint = self.reports['joint']
        self.assertEqual(len(joint['models']), 3)
        self.assertEqual(query(joint)['classification'], 'Underdetermined')
        self.assertEqual(query(joint)['positive_model_count'], 2)
        self.assertEqual(query(joint)['negative_model_count'], 1)
        for i, name in enumerate(('marked_zero', 'marked_one', 'marked_two')):
            r = self.reports[name]
            self.assertEqual(len(r['models']), 1)
            self.assertEqual(r['models'][0]['realizers'], [i])
            self.assertEqual(query(r)['classification'],
                             'ForcedPositive' if i < 2 else 'ForcedNegative')
        self.assertNotEqual(self.reports['marked_zero']['models'], self.reports['marked_one']['models'])
        self.assertEqual(self.reports['marked_zero']['queries'], self.reports['marked_one']['queries'])
        conflict = self.reports['marked_conflict']
        self.assertEqual(conflict['status'], 'Analyzed')
        self.assertEqual(conflict['census'], {'candidate_count': 16, 'surviving_count': 0, 'complete': True})
        self.assertTrue(all(q['classification'] == 'Inconsistent' for q in conflict['queries']))
        self.assertTrue(query(conflict)['inhabited']['value'])
        permitted = self.reports['joint_negative_pair']
        self.assertEqual(permitted['models'][0]['realizers'], [2])
        self.assertEqual(query(permitted)['classification'], 'ForcedNegative')

    def test_partial_enumeration_is_unknown_not_inconsistent(self):
        r = self.reports['partial_fuel']
        self.assertEqual(r['status'], 'Unknown')
        self.assertEqual(r['failure']['code'], 'fuel')
        self.assertEqual(r['n'], 3)
        self.assertEqual(len(r['trace']), 3)
        self.assertEqual(r['regions']['pair'], 3)
        self.assertGreater(r['census']['candidate_count'], 0)
        self.assertLess(r['census']['candidate_count'], 16)
        self.assertFalse(r['census']['complete'])
        self.assertEqual(r['models'], [])
        self.assertTrue(all(q['classification'] == 'Unknown' and
                            q['positive_witness'] is None and q['negative_witness'] is None
                            for q in r['queries']))
        self.assertLessEqual(r['fuel']['used'], 200)

    def test_independent_receiver_checks_every_case(self):
        for name, r in self.reports.items():
            with self.subTest(case=name):
                self.assertEqual(verifier.verify(self.cases[name], r)['status'],
                                 'NoClaim' if name == 'partial_fuel' else 'Verified')

    def test_receiver_rejects_complete_claim_mutations(self):
        base = self.reports['basic']
        mutations = []
        def change(label, edit):
            r = copy.deepcopy(base)
            edit(r)
            mutations.append((label, r))
        change('omit_model_with_consistent_count', lambda r: (r['models'].pop(), r['census'].update(surviving_count=3)))
        change('duplicate_model', lambda r: r['models'].__setitem__(1, copy.deepcopy(r['models'][0])))
        change('false_common_realizer', lambda r: next(m for m in r['models'] if not m['realizers']).update(realizers=[0]))
        change('same_positive_negative_witness', lambda r: query(r).update(negative_witness=query(r)['positive_witness']))
        change('ambiguity_as_unknown', lambda r: query(r).update(classification='Unknown'))
        change('ambiguity_as_inconsistent', lambda r: query(r).update(classification='Inconsistent'))
        change('wrong_region', lambda r: r['regions'].update(pair=1))
        change('wrong_observation', lambda r: r['trace'][1]['observations'].update(large=True))
        change('wrong_output', lambda r: r['trace'][0]['outputs'].update(y='-1'))
        for label, r in mutations:
            with self.subTest(mutation=label):
                self.assertEqual(verifier.verify(self.cases['basic'], r)['status'], 'Rejected')
        r = copy.deepcopy(self.reports['marked_zero'])
        r['models'][0] = copy.deepcopy(self.reports['marked_two']['models'][0])
        self.assertEqual(verifier.verify(self.cases['marked_zero'], r)['status'], 'Rejected')
        r = copy.deepcopy(self.reports['marked_conflict'])
        query(r).update(classification='Unknown')
        self.assertEqual(verifier.verify(self.cases['marked_conflict'], r)['status'], 'Rejected')

    def test_receiver_rejects_leaking_unknown_claims(self):
        for field in ('classification', 'model', 'witness', 'complete'):
            r = copy.deepcopy(self.reports['partial_fuel'])
            if field == 'classification':
                query(r).update(classification='Inconsistent')
            elif field == 'model':
                r['models'] = [copy.deepcopy(self.reports['basic']['models'][0])]
            elif field == 'witness':
                query(r).update(positive_witness=0)
            else:
                r['census']['complete'] = True
            with self.subTest(mutation=field):
                self.assertEqual(verifier.verify(self.cases['partial_fuel'], r)['status'], 'Rejected')


if __name__ == '__main__':
    unittest.main()
