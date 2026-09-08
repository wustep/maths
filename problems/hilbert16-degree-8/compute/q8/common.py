"""Exact encodings and input helpers for q8; imports have no write effects."""
from pathlib import Path
import hashlib
import json
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from notation import parse, render, canon
from replay_census import parse_pcom
from tcurve import lattice_points

PTS = lattice_points(8)

def tree_code(tree):
    result = 1
    for child in sorted(tree_code(c) for c in tree):
        result = (result << child.bit_length()) | child
    return result << 1

def scheme_code(s):
    forest, pseudoline = parse(s)
    assert not pseudoline
    return tree_code(forest)

def code_scheme(code):
    bits = bin(int(code))[2:]
    pos = 0
    def node():
        nonlocal pos
        assert bits[pos] == '1'
        pos += 1
        children = []
        while bits[pos] != '0':
            children.append(node())
        pos += 1
        return tuple(sorted(children))
    forest = node()
    assert pos == len(bits)
    return render(forest)

def triangulation(tris):
    return tuple(sorted(tuple(sorted(tuple(p) for p in t)) for t in tris))

def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def unpack(c):
    return (triangulation(c['triangles']),
            {tuple(map(int, k.split(','))): int(v) for k, v in c['heights'].items()},
            {tuple(map(int, k.split(','))): int(v) for k, v in c['signs'].items()})

def baseline():
    a = {canon(c['scheme']) for c in json.loads((ROOT / 'certs/new_schemes.json').read_text())}
    b = set((ROOT / 'census_schemes.txt').read_text().splitlines())
    assert len(a) == 17 and len(b) == 2367 and not a & b
    return a | b

def seeds():
    out = []
    with tarfile.open(ROOT / 'data/deg8.pcoms.txz') as archive:
        for name in sorted(n for n in archive.getnames() if '/o22-' in n and n.endswith('.pcom')):
            tris, heights, signs, scheme = parse_pcom(archive.extractfile(name).read().decode())
            out.append(dict(source=name, scheme=canon(scheme), triangles=triangulation(tris),
                            heights={f'{x},{y}': int(h) for (x, y), h in heights.items()},
                            signs={f'{x},{y}': s for (x, y), s in signs.items()}))
    assert len(out) == 38
    for c in json.loads((ROOT / 'certs/new_schemes.json').read_text()):
        out.append(dict(c, source='parent addition: ' + c['scheme']))
    assert len(out) == 55
    return out

def flips(tris):
    """Every unimodular 2-2 flip, once, with the removed/added diagonals."""
    inc = {}
    for t in tris:
        for j in range(3):
            e = tuple(sorted((t[j], t[(j+1)%3])))
            inc.setdefault(e, []).append((t, t[(j+2)%3]))
    for (a, b), rows in sorted(inc.items()):
        if len(rows) != 2:
            continue
        (t, c), (u, d) = rows
        # A convex quadrilateral tiled by two primitive triangles is a
        # lattice parallelogram exactly when its other diagonal is flippable.
        if (a[0]+b[0], a[1]+b[1]) != (c[0]+d[0], c[1]+d[1]):
            continue
        new = [v for v in tris if v not in (t, u)] + [(a, c, d), (b, c, d)]
        yield (a, b), tuple(sorted((c, d))), triangulation(new)

def write_task(tris, signs, path, known=None):
    from fastcx import Complex
    from export_span import emit
    cx = Complex(8, tris)
    emit(cx, PTS, [], path)
    known = baseline() if known is None else known
    with open(path, 'a') as f:
        f.write('SEEDS 1\n' + ' '.join(str(signs[p]) for p in PTS) + '\n')
        f.write(f'KNOWN {len(known)}\n' + ' '.join(str(scheme_code(s)) for s in sorted(known)) + '\n')
    return cx
