"""Finite matrix-free calibration; no native identities. ChatGPT/OpenAI."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'experiments/iota_dual_expansion'
spec = importlib.util.spec_from_file_location('dual_expansion', HERE / 'checker.py')
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def test_typed_grammars_reject_cross_domain_operands():
    with pytest.raises(TypeError):
        m.App(m.comb(1,1), m.I)
    with pytest.raises(TypeError):
        m.Comb(1,1,m.I,'c1')
    with pytest.raises(TypeError):
        m.Leaf('z')


def test_fresh_exact_payload():
    assert m.run() == json.loads((HERE / 'evidence.json').read_text())


def test_mirror_is_involution_but_not_a_rewrite_correspondence():
    term = m.App(m.I,m.Leaf('a'))
    assert m.mirror(m.mirror(term)) == term
    assert m.step(term) is not None
    assert m.step(m.mirror(term)) is None
    # Even the self-mirror two-leaf source loses its local rewrite under mirror.
    ii = m.App(m.I,m.I)
    assert m.mirror(ii) == ii
    assert m.mirror(m.root_step(ii)[1]) != m.root_step(ii)[1]


def test_equal_endpoints_do_not_identify_histories_or_schedule_cuts():
    bare = m.history(m.Leaf('a'))
    applied = m.history(m.App(m.App(m.I,m.I),m.Leaf('a')))
    assert bare['normal_form'] == applied['normal_form'] == 'a'
    assert len(bare['events']) == 0 and len(applied['events']) == 5
    assert len(bare['schedule_cuts']) == 1 and len(applied['schedule_cuts']) == 6


def test_pure_three_leaf_counterexample():
    left = m.history(m.build(1,2,m.I))
    right = m.history(m.build(2,2,m.I))
    assert (left['normal_form'],right['normal_form']) == ('i','@sk')
    assert (len(left['events']),len(right['events'])) == (5,6)


def test_one_and_three_actual_apertures():
    r = m.run()
    assert r['rows'][3]['right']['source'] == '@ia'
    assert r['three_role_binding']['port_leaves'] == ['a','b','c']
    assert r['controls'][-1]['normal_form'] == '@@a@@bskc'


@pytest.mark.skipif(sys.platform != 'linux', reason='contracted Linux memory limit')
def test_cli_replay_and_refuses_overwrite(tmp_path):
    out = tmp_path / 'fresh.json'
    cmd = [sys.executable,'-S',str(HERE/'checker.py'),'--output',str(out)]
    result = subprocess.run(cmd,capture_output=True,text=True,timeout=25)
    assert result.returncode == 0, result.stderr
    assert json.loads(out.read_text()) == m.run()
    original = out.read_bytes()
    result = subprocess.run(cmd,capture_output=True,text=True,timeout=25)
    assert result.returncode != 0 and out.read_bytes() == original


def test_source_pin_mutation_is_refused(monkeypatch):
    contract = json.loads((HERE/'contract.json').read_text())
    contract['pins'][next(iter(contract['pins']))] = '0' * 64
    old = m.json.loads
    monkeypatch.setattr(m.json,'loads',lambda value: contract if 'external-iota-dual' in value else old(value))
    with pytest.raises(ValueError,match='input pin mismatch'):
        m.run()
