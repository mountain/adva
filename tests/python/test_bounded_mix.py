"""Structural controls for the bounded binding relation; no research campaign."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.bounded_mix.author import source
from experiments.bounded_mix.receive import binding, receive, wire
from experiments.bounded_mix.fixtures import interpreters, controls
from experiments.bounded_self_compiler.language import seed_compile, decode_target, integer, node


def test_mix_is_ordinary_reproducible_source_in_its_target_grammar():
    s=json.loads((ROOT/'programs/bounded-mix/mix.source.adva').read_text())
    assert s==source()
    target=seed_compile(s)
    assert target==json.loads((ROOT/'programs/bounded-mix/mix.seed.adva').read_text())
    assert decode_target(wire(target))==target
    assert len(target['registers'])<=48


@pytest.mark.parametrize('mutation',['literal','input','jump','branch','scratch','declaration'])
def test_receiver_refuses_changed_correspondence(mutation):
    q=controls()[1][1]
    s=node(7,[integer(9007199254740993),node(9,[])])
    target,offset=binding(q,s)
    bad=deepcopy(target)
    if mutation=='literal':
        next(i for i in bad['code'][:offset] if i['op']=='constant')['value']+=1
    elif mutation=='input':
        bad['code'][offset]['src']-=1
    elif mutation=='jump':
        next(i for i in bad['code'][offset:] if i['op']=='jump')['target']-=offset
    elif mutation=='branch':
        next(i for i in bad['code'][offset:] if i['op']=='branch')['yes']+=1
    elif mutation=='scratch':
        bad['code'][0]['dst']-=1
    else:
        bad['registers'][-1]['kind']='data'
    with pytest.raises(ValueError,match='correspondence'):
        receive(q,s,bad)


def test_receiver_refuses_changed_source_and_static_argument():
    q=interpreters()[0][1];s=integer(7)
    target,_=binding(q,s)
    with pytest.raises(ValueError):receive(q,integer(9),target)
    changed=deepcopy(q)
    next(i for i in changed['code'] if i['op']=='multiply')['op']='add'
    with pytest.raises(ValueError):receive(changed,s,target)


def test_reserved_names_and_literal_depth_are_explicit_refusals():
    q=controls()[0][1]
    bad=deepcopy(q);bad['registers'][0]['name']='mix_A'
    with pytest.raises(ValueError,match='namespace'):binding(bad,integer(0))
    deep=integer(0)
    for _ in range(12):deep=node(0,[deep])
    with pytest.raises(ValueError,match='depth'):binding(q,deep)


def test_third_projection_capacity_obstruction_is_not_reported_as_execution():
    mix=seed_compile(source())
    target,offset=binding(mix,wire(mix))
    assert offset==3721 and len(target['code'])==3959
    assert len(target['code'])>2048
    assert len(target['registers'])==57


def test_v2_is_only_a_version_and_capacity_successor_of_frozen_v1():
    old=(ROOT/'crates/adva-witness/src/data_machine_v1.rs').read_text()
    new=(ROOT/'crates/adva-witness/src/data_machine_v2.rs').read_text()
    expected=old.replace('V1','V2').replace('_v1','_v2').replace('.v1','.v2')
    assert expected.count('2048')==6
    assert new==expected.replace('2048','4096')
    assert 'DATA_MACHINE_MAX_FUEL_V2: u32 = 200000' in new
