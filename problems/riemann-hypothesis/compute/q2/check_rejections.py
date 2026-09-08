#!/usr/bin/env python3
"""Exercise missing coverage, false margins, and corrupted coefficient rejection.

These tests attack the certificate interfaces. They do not prove the
transcendental enclosures or replace complete arithmetic regeneration.
"""
import argparse
import copy
import json
from pathlib import Path
import tempfile
from verify_analytic import ball, check_barrier, check_matrix
from verify_finite import c_rows, digest, rust_rows

def rejected(label,action):
    try:
        action()
    except (ValueError,StopIteration):
        print('PASS rejected '+label)
    else:
        raise RuntimeError('accepted invalid evidence: '+label)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('upstream',type=Path);p.add_argument('original',type=Path)
    p.add_argument('independent',type=Path);args=p.parse_args()
    original=(args.upstream/'barrier/certificates/barrier_target_closed.log').read_text()
    check_barrier(args.upstream/'barrier/certificates/barrier_target_closed.log')
    with tempfile.TemporaryDirectory(prefix='rh-q2-rejections-') as name:
        root=Path(name); path=root/'prisms.txt'
        rows=original.splitlines(keepends=True)
        prism_positions=[i for i,s in enumerate(rows) if s.startswith('Prism(')]
        first=prism_positions[0]; second=prism_positions[1]
        variants=[]
        altered=rows[:];del altered[prism_positions[-1]];variants.append(('missing final prism',altered))
        altered=rows[:];altered[second]=altered[second].replace('Prism(2)','Prism(1)');variants.append(('duplicate prism index',altered))
        altered=rows[:];start=altered[second].split(' t=[',1)[1].split(',',1)[0]
        altered[second]=altered[second].replace(' t=['+start+',',' t=[0,',1);variants.append(('time seam gap',altered))
        altered=rows[:];a,b=altered[first].split(' winding=',1);_,b=b.split(' min_mesh=',1)
        altered[first]=a+' winding=1 min_mesh='+b;variants.append(('nonzero winding',altered))
        altered=rows[:];altered[first]=altered[first].replace('Dt=52726','Dt=52726000',1);variants.append(('false time allowance',altered))
        altered=rows[:];a,b=altered[first].split(' min_mesh=',1);_,b=b.split(' Dz=',1)
        altered[first]=a+' min_mesh=0 Dz='+b;variants.append(('nonpositive boundary modulus',altered))
        altered=rows[:];altered[-2]='RESULT: INCOMPLETE\n';variants.append(('missing completion marker',altered))
        for label,lines in variants:
            path.write_text(''.join(lines));rejected(label,lambda:check_barrier(path))
        for value in ('[1 +/- -1]','nan','[+/- inf]'):
            rejected('invalid ball '+value,lambda:ball(value))
        cdir=root/'finite';cdir.mkdir()
        manifest=json.loads((args.original/'progress.json').read_text())
        source=args.original/'N690988-690988.txt';text=source.read_text()
        for label,changed in [
            ('finite floor below error',text.replace('0.000000791366','0.000000000000')),
            ('finite wrong index',text.replace('N 690988 ','N 690989 ')),
            ('finite missing completion',text[:text.index('TIMING')])]:
            cp=cdir/source.name;cp.write_text(changed)
            record=copy.deepcopy(manifest);record['segments'][0]['sha256']=digest(cp)
            (cdir/'progress.json').write_text(json.dumps(record))
            # Hashes have been updated, so rejection must use content gates.
            rejected(label,lambda:list(c_rows(cdir)))
        rdir=root/'independent';rdir.mkdir()
        record=json.loads((args.independent/'manifest.json').read_text())
        for run in record['runs']:
            for suffix in ('.txt','.stderr.txt'):
                (rdir/(run['name']+suffix)).symlink_to((args.independent/(run['name']+suffix)).resolve())
        name=record['runs'][1]['name']+'.txt';rp=rdir/name;rp.unlink()
        text=(args.independent/name).read_text().replace('N 690989 LOWER12','N 690988 LOWER12',1)
        rp.write_text(text);record['runs'][1]['stdout_sha256']=digest(rp)
        (rdir/'manifest.json').write_text(json.dumps(record))
        rejected('independent duplicate index with matching hash',lambda:list(rust_rows(rdir)))
        mdir=root/'matrix';(mdir/'barrier').mkdir(parents=True)
        source=args.upstream/'barrier/certificates/storedsum_interval_regenerated.txt'
        target=mdir/'barrier/storedsum_interval_regenerated.txt'
        rows=source.read_text().splitlines()
        target.write_text('\n'.join(rows[:-1])+'\n')
        rejected('truncated coefficient matrix',lambda:check_matrix(args.upstream,mdir))
        row=rows[1].split(',');row[0]='[0 +/- 1e-30]';rows[1]=','.join(row)
        target.write_text('\n'.join(rows)+'\n')
        rejected('coefficient outside serialization ball',lambda:check_matrix(args.upstream,mdir))
    print('PASS 16 malformed-certificate rejection cases')

if __name__=='__main__': main()
