"""Archive a completed finite run, verifying every byte before removing raw copies."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile


def digest(raw):return hashlib.sha256(raw).hexdigest()


def retain(root):
    root=Path(root)
    cost=json.loads((root/'cost.json').read_text())
    assert cost['status'] in ('Passed','Failed','PassedWithThirdCapacityObstruction')
    destination=root/'complete.tar.gz'
    if destination.exists() or (root/'retention.json').exists():
        raise FileExistsError('retained run already archived')
    paths=sorted(p for p in root.iterdir() if p.is_file())
    assert len(paths)<=600 and sum(p.stat().st_size for p in paths)<=256*1024**2
    manifest={p.name:{'sha256':digest(p.read_bytes()),'bytes':p.stat().st_size} for p in paths}
    with tarfile.open(destination,'x:gz') as bundle:
        for p in paths:bundle.add(p,arcname=p.name,recursive=False)
    with tarfile.open(destination,'r:gz') as bundle:
        assert set(bundle.getnames())==set(manifest)
        for member in bundle.getmembers():
            assert member.isfile() and Path(member.name).name==member.name
            raw=bundle.extractfile(member).read()
            assert len(raw)==manifest[member.name]['bytes'] and digest(raw)==manifest[member.name]['sha256']
    record={'schema':'adva.mix.retention.v0','archive':'complete.tar.gz',
            'archive_sha256':digest(destination.read_bytes()),'files':manifest,
            'uncompressed_bytes':sum(r['bytes'] for r in manifest.values()),'all_members_verified':True}
    (root/'retention.json').write_text(json.dumps(record,indent=2)+'\n')
    keep={'cost.json','summary.json','source-manifest.json','mix.program.adva',
          'capacity-preflight.json','third-capacity-obstruction.json'}
    for p in paths:
        assert digest(p.read_bytes())==manifest[p.name]['sha256']
        if p.name not in keep and not p.name.endswith('.target.adva'):p.unlink()
    print(json.dumps({'files':len(paths),'uncompressed_bytes':record['uncompressed_bytes'],
                      'archive_bytes':destination.stat().st_size}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory');a=p.parse_args();retain(a.directory)
