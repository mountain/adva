"""Receive retained bootstrap evidence; no native campaign is launched."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tarfile
from checker import receive_compilation
from language import decode_target, encode_source, seed_compile, canonical
from reference import Budget, receive, source_execute
from runtime import ROOT, HERE, profile, sha

EVIDENCE=HERE/'evidence/attempt-2'

def read_archive(name):
    with tarfile.open(EVIDENCE/(name+'.tar.gz'),'r:gz') as bundle:
        members=bundle.getmembers()
        assert len(members)<=500 and sum(m.size for m in members)<=268435456
        assert all(m.isfile() and Path(m.name).name==m.name and m.size<=67108864 for m in members)
        return {m.name:bundle.extractfile(m).read() for m in members}


def bound_sources():
    execution=json.loads((EVIDENCE/'execution.json').read_text())
    assert execution['status']=='Passed' and execution['deterministic_results_equal']
    manifest=json.loads((EVIDENCE/'source-manifest.json').read_text())
    frozen={'crates/adva-witness/src/data_machine_v1.rs',
            'programs/bounded-self-compiler/compiler.source.adva',
            'experiments/bounded_self_compiler/contract.json',
            'experiments/bounded_self_compiler/contract-v1.json',
            'experiments/bounded_self_compiler/language.py',
            'experiments/bounded_self_compiler/checker.py',
            'experiments/bounded_self_compiler/reference.py'}
    for name,digest in manifest.items():
        assert sha(EVIDENCE/'sources'/name)==digest
        if name in frozen:assert sha(ROOT/name)==digest
    for row in execution['processes']:
        assert row['exit_code']==0 and not row['timed_out']
        assert sha(EVIDENCE/row['archive']['path'])==row['archive']['sha256']
    assert json.loads((EVIDENCE/'results.json').read_text())['profile']==profile()


def stages_and_correspondence():
    files=read_archive('primary');budget=Budget()
    source=json.loads(files['compiler.source.adva'])
    stages=[json.loads(files['compiler.'+name+'.adva']) for name in ('c1','c2','c3')]
    assert canonical(stages[0])==canonical(stages[1])==canonical(stages[2])
    assert stages[0]==seed_compile(source)
    for stage in ('c1','c2'):
        report=json.loads(files['self-'+stage+'.run.adva'])
        assert report['input']==encode_source(source) and report['program']==stages[0]
        assert decode_target(report['state']['phase']['value'])==stages[0]
    summary=json.loads(files['summary.json'])
    for name in summary['receipts']:
        expected=json.loads(files[name+'.receipt.json'])
        if name in ('c1','c2','c3'):s=source;t=stages[0]
        elif name=='changed-source':
            s=json.loads(files['mutant.source.adva'])
            t=decode_target(json.loads(files['changed-source.run.adva'])['state']['phase']['value'])
        else:
            s=json.loads(files[name.rsplit('-',1)[0]+'.source.adva'])
            t=decode_target(json.loads(files[name+'.run.adva'])['state']['phase']['value'])
        assert receive_compilation(s,t,budget)==expected
    bad=json.loads(files['mutated-target.adva'])
    try:receive_compilation(source,bad,budget)
    except ValueError:pass
    else:raise AssertionError('branch mutation accepted')


def fixture_semantics():
    files=read_archive('primary');summary=json.loads(files['summary.json']);budget=Budget()
    edges=0;primitives=0
    for row in summary['fixtures']:
        name=row['name'];prefix=name+'-execute'
        report=json.loads(files[prefix+'.run.adva']);program=json.loads(files[prefix+'.program.adva'])
        data=json.loads(files[prefix+'.input.json']);source=json.loads(files[name+'.source.adva'])
        receive(report,program,data,2048,summary['profile'],budget)
        phase,events=source_execute(source,data,budget)
        assert phase==report['state']['phase']==row['phase']
        assert len(events)==row['primitive_events']
        edges+=report['state']['spent'];primitives+=len(events)
    assert edges==summary['independent_fixture_edges']
    assert primitives==summary['fixture_primitive_events']


def lineage_and_mutations():
    files=read_archive('primary')
    whole=json.loads(files['self-c2.run.adva']);prefix=json.loads(files['prefix.run.adva'])
    resumed=json.loads(files['resumed.run.adva'])
    assert prefix['state']['spent']==17 and prefix['status']=='Suspended'
    assert resumed['trace']==whole['trace'] and resumed['state']==whole['state']
    assert resumed['fuel']==prefix['fuel']==whole['fuel']==200000
    receive(prefix,json.loads(files['prefix.program.adva']),json.loads(files['prefix.input.json']),
            200000,profile(),Budget())
    for name in ('changed-fuel','changed-input','changed-trace','static-type'):
        assert name+'.run.adva' not in files
        assert files[name+'.stderr.txt']
    mutant=json.loads(files['mutant-execute.run.adva'])
    try:decode_target(mutant['state']['phase']['value'])
    except ValueError:pass
    else:raise AssertionError('malformed generated code accepted')
    assert json.loads(files['zero-fuel.run.adva'])['status']=='FuelExhausted'
    assert json.loads(files['loop-fuel.run.adva'])['state']['spent']==23


def fresh_and_failures():
    primary=read_archive('primary');fresh=read_archive('fresh')
    assert primary.keys()==fresh.keys()
    for name in primary:
        if name=='cost.json' or name.endswith(('.stdout.txt','.stderr.txt')):continue
        assert primary[name]==fresh[name],name
    for files in (primary,fresh):
        cost=json.loads(files['cost.json']);assert cost['status']=='Passed'
        assert len(cost['native_calls'])<=48
        assert cost['wall_seconds']<600 and cost['cpu_seconds_including_native']<540
    failure=json.loads((HERE/'evidence/attempt-1/execution.json').read_text())
    assert failure['status']=='Failed' and len(failure['processes'])==1
    row=failure['processes'][0]
    assert sha(HERE/'evidence/attempt-1'/row['archive']['path'])==row['archive']['sha256']
    old=(HERE/'contract.json').read_bytes();new=json.loads((HERE/'contract-v1.json').read_text())
    assert new['supersedes']['sha256']==hashlib.sha256(old).hexdigest()
    original=json.loads(old)
    for key in ('family','machine_limits','campaign_limits'):assert new[key]==original[key]

CHECKS={'sources':bound_sources,'stages':stages_and_correspondence,'fixtures':fixture_semantics,
        'lineage':lineage_and_mutations,'fresh':fresh_and_failures}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('check',choices=[*CHECKS,'all']);a=p.parse_args()
    for name,check in CHECKS.items():
        if a.check in (name,'all'):check();print(name+': received')
