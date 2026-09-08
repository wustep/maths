#!/usr/bin/env python3
"""Positive certificates, corrupted witnesses, and forced discovery controls."""
import argparse
import copy
from itertools import combinations
import json
import subprocess
import tarfile
from unittest.mock import patch

from common import (HERE, ROOT, PTS, baseline, canon, code_scheme, flips,
                    parse_pcom, scheme_code, seeds, unpack, write_task)
from tcurve import TCurve
from verify import both, build_rust, decode, rust_input, verify_new


def reject(fn, label):
    try:
        fn()
    except (AssertionError, ValueError, KeyError, IndexError):
        return
    raise AssertionError('accepted negative control: ' + label)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--full-baseline', action='store_true')
    args = ap.parse_args()
    exe = build_rust()
    seedlist = seeds()
    for cert in seedlist:
        both(cert, exe)
    print('PASS: Python and Rust agree on all 55 seed certificates', flush=True)

    # Archive TYPE and archive filename independently specify B.
    archive_schemes = set()
    with tarfile.open(ROOT / 'data/deg8.pcoms.txz') as archive:
        for member in archive.getmembers():
            if not member.name.endswith('.pcom'):
                continue
            tris, heights, signs, claimed = parse_pcom(archive.extractfile(member).read().decode())
            named = canon(member.name.rsplit('/', 1)[1][:-5])
            assert canon(claimed) == named
            archive_schemes.add(named)
            if args.full_baseline:
                cert = dict(triangles=tris, scheme=canon(claimed),
                            heights={f'{x},{y}': int(h) for (x,y),h in heights.items()},
                            signs={f'{x},{y}': s for (x,y),s in signs.items()})
                both(cert, exe)
    assert len(archive_schemes) == 2367
    assert archive_schemes == set((ROOT / 'census_schemes.txt').read_text().splitlines())
    assert len(baseline()) == 2384
    print('PASS: archive TYPE, filenames and replayed B agree' +
          ('; both verifiers accept all 2,384 baseline schemes' if args.full_baseline else ''),
          flush=True)

    # These are legitimate algebraic certificates, but neither is new.
    reject(lambda: verify_new(seedlist[0], exe), 'published scheme')
    reject(lambda: verify_new(seedlist[-1], exe), 'parent addition')
    bad = copy.deepcopy(seedlist[0])
    bad['scheme'] = '<4 u 1<2 u 1<14>>>'
    reject(lambda: both(bad, exe), 'forced open-nest answer')
    forced = subprocess.CompletedProcess([], 0,
                f'22 {scheme_code(bad["scheme"])}\n', '')
    with patch('verify.subprocess.run', return_value=forced):
        reject(lambda: both(seedlist[0], exe), 'independent checker disagreement')
    for mutation in ('sign', 'height', 'duplicate', 'point'):
        bad = copy.deepcopy(seedlist[0])
        if mutation == 'sign':
            bad['signs'][next(iter(bad['signs']))] = 0
        elif mutation == 'height':
            bad['heights'] = {k: 0 for k in bad['heights']}
        elif mutation == 'duplicate':
            bad['triangles'] = list(bad['triangles'])
            bad['triangles'][0] = bad['triangles'][1]
        else:
            bad['signs'].pop(next(iter(bad['signs'])))
        reject(lambda: both(bad, exe), mutation)

    # Exercise Rust rejection directly, so a Python early return cannot
    # hide a broken Rust geometry or input check.
    tris, heights, signs = decode(seedlist[0])
    valid = rust_input(tris, heights, signs)
    lines = valid.splitlines()
    damaged = []
    zero = lines.copy()
    for i in range(1,46):
        fields = zero[i].split(); fields[2] = '0'; zero[i] = ' '.join(fields)
    damaged.append(zero)
    duplicate = lines.copy(); duplicate[-1] = duplicate[-2]; damaged.append(duplicate)
    signzero = lines.copy(); fields = signzero[1].split(); fields[-1] = '0'
    signzero[1] = ' '.join(fields); damaged.append(signzero)
    duplicatepoint = lines.copy(); duplicatepoint[1] = duplicatepoint[2]; damaged.append(duplicatepoint)
    for badlines in damaged:
        p = subprocess.run([str(exe)], input='\n'.join(badlines)+'\n',
                           text=True, capture_output=True)
        assert p.returncode != 0, 'Rust accepted a damaged certificate'
    print('PASS: known schemes, false target, and malformed geometry/signs rejected', flush=True)

    ball = HERE / 'work/ball'
    subprocess.run(['cc', '-O3', '-std=c11', '-Wall', '-Wextra',
                    str(HERE / 'ball.c'), '-o', str(ball)], check=True)
    task = HERE / 'work/control.task'
    # Removing a known answer must make the search emit its exact signs.
    tris, _, signs = unpack(seedlist[0])
    write_task(tris, signs, task, known=set())
    p = subprocess.run([str(ball),str(task),'0'], check=True, capture_output=True,text=True)
    messages = [json.loads(s) for s in p.stdout.splitlines()]
    assert messages[0]['kind'] == 'witness'
    assert code_scheme(messages[0]['code']) == canon(seedlist[0]['scheme'])
    assert messages[0]['bits'] == sum(1<<i for i,p in enumerate(PTS) if signs[p]<0)
    write_task(tris, signs, task)
    p = subprocess.run([str(ball),str(task),'0'], check=True, capture_output=True,text=True)
    assert len(p.stdout.splitlines()) == 1, 'known scheme emitted as novel'

    # Exact trace coverage: all radii 0,1,2 changes on one changed mesh.
    # Independently compute every one of those topologies with Python.
    flipped = next(flips(tris))[2]
    write_task(flipped, signs, task)
    p = subprocess.run([str(ball),str(task),'2','trace'], check=True,capture_output=True,text=True)
    messages = [json.loads(s) for s in p.stdout.splitlines()]
    traces = [m for m in messages if m['kind']=='witness']
    bits0 = sum(1<<i for i,p in enumerate(PTS) if signs[p]<0)
    expected = {bits0 ^ sum(1<<i for i in c) for k in range(3)
                for c in combinations(range(45), k)}
    assert len(traces)==len(expected)==1036
    assert {m['bits'] for m in traces} == expected
    for m in traces:
        s = {p: (-1 if m['bits']>>i&1 else 1) for i,p in enumerate(PTS)}
        assert scheme_code(TCurve(8,flipped,s).scheme()) == m['code']
    print('PASS: forced discovery and exact 1,036-sign trace agree with Python', flush=True)


if __name__ == '__main__':
    main()
