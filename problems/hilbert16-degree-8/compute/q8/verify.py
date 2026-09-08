#!/usr/bin/env python3
"""Two independent geometry/topology checks and the exact q8 novelty gate."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import subprocess

from common import HERE, PTS, baseline, canon, code_scheme, triangulation
from tcurve import TCurve, check_convexity, validate_triangulation


def build_rust():
    exe = HERE / 'work/verify_regions'
    exe.parent.mkdir(exist_ok=True)
    subprocess.run(['rustc', '-O', '-C', 'overflow-checks=yes',
                    str(HERE / 'verify_regions.rs'), '-o', str(exe)], check=True)
    return exe


def decode(cert):
    assert cert.get('degree', 8) == 8
    assert len(cert['heights']) == len(cert['signs']) == 45, 'wrong domain size'
    tris = triangulation(cert['triangles'])
    heights = {tuple(map(int, k.split(','))): Fraction(v)
               for k,v in cert['heights'].items()}
    signs = {tuple(map(int, k.split(','))): v for k,v in cert['signs'].items()}
    assert set(heights) == set(PTS) == set(signs), 'lattice/sign domain mismatch'
    assert all(type(v) is int and v in (-1,1) for v in signs.values()), 'invalid sign'
    assert all(h.denominator == 1 and abs(h) <= 10**18 for h in heights.values())
    return tris, heights, signs


def rust_input(tris, heights, signs):
    idx = {p:i for i,p in enumerate(PTS)}
    lines = [f'8 45 {len(tris)}']
    lines += [f'{x} {y} {int(heights[x,y])} {signs[x,y]}' for x,y in PTS]
    lines += [' '.join(str(idx[p]) for p in t) for t in tris]
    return '\n'.join(lines) + '\n'


def both(cert, exe):
    tris, heights, signs = decode(cert)
    assert not validate_triangulation(8, tris), 'invalid triangulation'
    assert not check_convexity(8, tris, heights), 'strict lifting failed'
    got = canon(TCurve(8, tris, signs).scheme())
    p = subprocess.run([str(exe)], input=rust_input(tris, heights, signs),
                       capture_output=True, text=True)
    assert p.returncode == 0, 'Rust rejected certificate: ' + p.stderr[-500:]
    ovals, code = map(int, p.stdout.split())
    assert code_scheme(code) == got, f'independent topology disagreement: {got}'
    assert ovals == TCurve(8, tris, signs).counts()['ovals']
    assert got == canon(cert['scheme']), f'false claimed scheme: actual {got}'
    return got


def verify_new(cert, exe):
    got = both(cert, exe)
    assert got != '<>', 'empty scheme is not a new nonempty scheme'
    assert got not in baseline(), 'scheme already in B union A'
    return got


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('certificate', nargs='?', default=str(HERE / 'certs/new_schemes.json'))
    args = ap.parse_args()
    path = Path(args.certificate)
    if not path.exists():
        print('RESIDUE: no candidate certificate; q8 CLAIM is not established.')
        return 2
    certs = json.loads(path.read_text())
    assert isinstance(certs, list) and certs, 'empty certificate list is not success'
    exe = build_rust()
    found = {verify_new(cert, exe) for cert in certs}
    print(f'PASS: {len(found)} new nonempty schemes; count >= {2384+len(found)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
