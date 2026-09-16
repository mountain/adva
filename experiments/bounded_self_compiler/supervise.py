"""Freeze all semantic/experiment sources; one primary/fresh pair, full retention."""
import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import tarfile
import time
from runtime import ROOT, HERE, sha
from language import canonical

SOURCES = [
 'Cargo.toml','Cargo.lock','rust-toolchain.toml','crates/adva-witness/Cargo.toml',
 'crates/adva-witness/src/data_machine_v1.rs','crates/adva-witness/src/lib.rs',
 'crates/adva-witness/src/bin/adva.rs','crates/adva-witness/src/bin/support/data_machine_v1_cli.rs',
 'crates/adva-witness/src/bin/support/native_run_cli.rs',
 'programs/bounded-self-compiler/compiler.source.adva','programs/bounded-self-compiler/compiler.seed.adva',
 'programs/bounded-self-compiler/compiler.input.json','experiments/bounded_self_compiler/contract.json','experiments/bounded_self_compiler/contract-v1.json',
] + ['experiments/bounded_self_compiler/'+name+'.py' for name in
     ['author','language','checker','reference','fixtures','runtime','preflight','preflight_controls','preflight_mutation','compile','campaign','supervise']]


def save(path,value):
    with Path(path).open('xb') as f:f.write(canonical(value)+b'\n')


def archive(directory,destination):
    paths=sorted(p for p in directory.iterdir() if p.is_file())
    expected={p.name:sha(p) for p in paths}
    if sum(p.stat().st_size for p in paths)>268435456:raise RuntimeError('archive input budget')
    with destination.open('xb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0) as zipped:
            with tarfile.open(fileobj=zipped,mode='w|') as bundle:
                for p in paths:
                    data=p.read_bytes();info=tarfile.TarInfo(p.name);info.size=len(data);info.mode=0o644
                    bundle.addfile(info,io.BytesIO(data))
    with tarfile.open(destination,'r:gz') as bundle:
        actual={m.name:hashlib.sha256(bundle.extractfile(m).read()).hexdigest() for m in bundle.getmembers()}
    assert actual==expected
    return {'path':destination.name,'sha256':sha(destination),'files':len(paths),
            'uncompressed_bytes':sum(p.stat().st_size for p in paths),'bytes':destination.stat().st_size}


def main():
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    resource.setrlimit(resource.RLIMIT_AS,(1024**3,)*2)
    resource.setrlimit(resource.RLIMIT_CPU,(1140,)*2)
    manifest={}
    for name in SOURCES:
        dest=a.output/'sources'/name;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/name,dest);manifest[name]=sha(dest)
    save(a.output/'source-manifest.json',manifest)
    result={'status':'Failed','processes':[],'binary_sha256':sha(a.binary),
            'contract_sha256':manifest['experiments/bounded_self_compiler/contract-v1.json']}
    start=time.monotonic();previous=None
    try:
        for name in ('primary','fresh'):
            assert all(sha(ROOT/p)==digest for p,digest in manifest.items()),'frozen source changed'
            directory=a.output/('raw-'+name)
            command=[sys.executable,'-B',str(HERE/'campaign.py'),'--binary',str(a.binary.resolve()),'--output',str(directory.resolve())]
            child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
            timed_out=False
            try:stdout,stderr=child.communicate(timeout=610)
            except subprocess.TimeoutExpired:
                timed_out=True;os.killpg(child.pid,signal.SIGKILL);stdout,stderr=child.communicate()
            (a.output/(name+'.stdout.txt')).write_bytes(stdout);(a.output/(name+'.stderr.txt')).write_bytes(stderr)
            row={'name':name,'exit_code':child.returncode,'timed_out':timed_out}
            if directory.exists():row['archive']=archive(directory,a.output/(name+'.tar.gz'))
            result['processes'].append(row)
            if child.returncode!=0 or timed_out:raise RuntimeError(name+' stopped; retain failure without retry')
            summary=json.loads((directory/'summary.json').read_text())
            if previous is not None:assert previous==summary,'fresh deterministic result mismatch'
            previous=summary
            assert all(sha(ROOT/p)==digest for p,digest in manifest.items()),'frozen source changed'
            # Complete byte-verified archive is retained before removing only our raw directory.
            shutil.rmtree(directory)
        save(a.output/'results.json',previous)
        result['status']='Passed';result['deterministic_results_equal']=True
    except Exception as e:result['error']=str(e)
    finally:
        result['wall_seconds_including_freeze_receiving_archiving']=time.monotonic()-start
        save(a.output/'execution.json',result)
    print(json.dumps(result))
    if result['status']!='Passed':raise SystemExit(1)

if __name__=='__main__':main()
