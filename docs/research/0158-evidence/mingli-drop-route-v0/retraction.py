#!/usr/bin/env python3
import hashlib
import itertools
import json
from pathlib import Path
import resource
import signal
import time


def mv(matrix, vector):
    return tuple(sum(a*b for a,b in zip(row,vector)) % 7 for row in matrix)


def main():
    base=Path(__file__).parent
    raw=(base/'retraction-contract.json').read_bytes()
    c=json.loads(raw)
    lim=c['limits']
    resource.setrlimit(resource.RLIMIT_AS, (lim['memory_mib']*1024**2,)*2)
    resource.setrlimit(resource.RLIMIT_CPU, (lim['cpu_seconds'],)*2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (lim['max_output_bytes'],)*2)
    signal.alarm(lim['wall_seconds'])
    start=time.monotonic()
    e0=((1,0),(0,0)); e1=((0,0),(0,1))
    t01=((0,0),(1,0)); t10=((0,1),(0,0)); swap=((0,1),(1,0))
    rows=[]
    for x,y in itertools.product(range(7),repeat=2):
        v=(x,y)
        p=mv(e0,v); k=mv(e1,v)
        forward=mv(t01,v); reverse=mv(t10,forward)
        assert p==(x,0) and k==(0,y)
        assert mv(e0,p)==p and mv(e0,k)==(0,0)
        assert mv(e1,k)==k and mv(e1,p)==(0,0)
        assert tuple((a+b)%7 for a,b in zip(p,k))==v
        assert forward==(0,x) and reverse==p
        assert mv(t01,mv(t10,v))==k
        assert mv(t01,k)==(0,0)
        assert (mv(swap,v)==forward)==(y==0)
        rows.append({'input':v,'skeleton':x,'retained_residual':y,
                     'thread':forward,'round_trip':reverse})
    section={0:0,1:1,2:3,4:2}
    nonlinear=[]
    for x in range(7):
        feature=x*x%7
        selected=section[feature]
        assert selected*selected%7==feature
        projected_twice=section[(selected*selected)%7]
        assert projected_twice==selected
        residual=(x-selected)%7
        nonlinear.append({'x':x,'feature':feature,'e_x':selected,
                          'x_minus_e_x':residual,'r_of_residual':residual*residual%7})
    assert nonlinear[6]=={'x':6,'feature':1,'e_x':1,'x_minus_e_x':5,'r_of_residual':4}
    report={'status':'PassedFiniteRetractionCalibration','linear_rows':rows,
            'nonlinear_rows':nonlinear,'linear_rows_checked':49,'nonlinear_rows_checked':7,
            'nonlinear_counterexample':nonlinear[6],
            'swap_is_not_thread_counterexample':{'input':[0,1],'swap':[1,0],'thread':[0,0]},
            'native_dual_identification':'Open',
            'contract_sha256':hashlib.sha256(raw).hexdigest(),
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'costs':{'elapsed_before_checkpoint_seconds':time.monotonic()-start,
                     'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}
    data=(json.dumps(report,indent=2)+'\n').encode()
    assert len(data)<=lim['max_output_bytes']
    with (base/'retraction-evidence.json').open('xb') as f: f.write(data)
    signal.alarm(0)
    print(json.dumps({'status':report['status'],'linear_rows':49,'nonlinear_rows':7,
                      'counterexample':nonlinear[6],'costs':report['costs'],'output_bytes':len(data)}))


if __name__=='__main__':
    main()
