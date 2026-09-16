"""Finite subprocess and artifact accounting shared by the declared trials."""
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time
import blake3
from language import canonical

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def profile():
    h=blake3.blake3(b'adva.data-machine.transition.v1\0')
    h.update((ROOT/'crates/adva-witness/src/data_machine_v1.rs').read_bytes())
    h.update((ROOT/'Cargo.lock').read_bytes())
    return h.hexdigest()

class Trial:
    def __init__(self, binary, out, *, preflight=False):
        self.binary=Path(binary).resolve(); self.out=Path(out).resolve()
        self.out.mkdir(parents=True,exist_ok=False)
        self.wall=180 if preflight else 600
        self.cpu=160 if preflight else 540
        self.maximum=96*1024**2 if preflight else 256*1024**2
        self.start=time.monotonic(); self.calls=[]; self.bytes=0
        self.initial_cpu=self.used_cpu()
        resource.setrlimit(resource.RLIMIT_AS,(1024**3,)*2)
        resource.setrlimit(resource.RLIMIT_CPU,(self.cpu,)*2)
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('trial wall limit')))
        signal.alarm(self.wall)
    @staticmethod
    def used_cpu():
        return sum(r.ru_utime+r.ru_stime for r in [resource.getrusage(resource.RUSAGE_SELF),resource.getrusage(resource.RUSAGE_CHILDREN)])
    def remaining(self):
        if self.used_cpu()-self.initial_cpu >= self.cpu: raise TimeoutError('aggregate CPU limit')
        return max(0.001,self.wall-(time.monotonic()-self.start))
    def save(self,name,value):
        raw=value if isinstance(value,bytes) else canonical(value)+b'\n'
        if self.bytes+len(raw)>self.maximum: raise RuntimeError('artifact budget')
        path=self.out/name
        with path.open('xb') as f: f.write(raw)
        self.bytes+=len(raw)
        return path
    def native(self,name,program,data,*,fuel=200000,quantum=None,resume=None,check=None,refuse=False):
        if len(self.calls)>=48: raise RuntimeError('native launch budget')
        p=self.save(name+'.program.adva',program); d=self.save(name+'.input.json',data)
        output=self.out/(name+'.run.adva')
        cmd=[str(self.binary),'data-run-v1',str(p),'--input',str(d),'--fuel',str(fuel),
             '--quantum',str(fuel if quantum is None else quantum),'--output',str(output)]
        if resume: cmd+=['--resume',str(resume)]
        if check: cmd+=['--check',str(check)]
        cpu=max(1,int(self.cpu-(self.used_cpu()-self.initial_cpu)))
        space=min(64*1024**2,self.maximum-self.bytes)
        def limits():
            resource.setrlimit(resource.RLIMIT_CPU,(cpu,cpu))
            resource.setrlimit(resource.RLIMIT_FSIZE,(space,space))
        started=time.monotonic()
        result=subprocess.run(cmd,capture_output=True,timeout=self.remaining(),preexec_fn=limits)
        self.save(name+'.stdout.txt',result.stdout); self.save(name+'.stderr.txt',result.stderr)
        report=None
        if output.exists():
            self.bytes+=output.stat().st_size
            report=json.loads(output.read_bytes())
        self.calls.append({'name':name,'exit_code':result.returncode,
            'status':report.get('status','Verified') if report else 'Refused',
            'steps':report.get('state',{}).get('spent',0) if report else 0,
            'sha256':sha(output) if output.exists() else None,
            'wall_seconds':time.monotonic()-started})
        self.remaining()
        if self.bytes>self.maximum: raise RuntimeError('artifact budget')
        if refuse:
            assert result.returncode!=0 and report is None,(name,result.stderr)
        else:
            assert report is not None,(name,result.stderr)
            assert result.returncode==(1 if report.get('status')=='Rejected' else 0),(name,result.stderr)
        return report
    def finish(self,status,extra):
        signal.alarm(0)
        cost={'status':status,'wall_seconds':time.monotonic()-self.start,
              'cpu_seconds_including_native':self.used_cpu()-self.initial_cpu,
              'artifact_bytes_before_cost':self.bytes,'native_calls':self.calls,
              'binary_sha256':sha(self.binary),'profile':profile(),**extra}
        self.save('cost.json',cost)
        return cost
