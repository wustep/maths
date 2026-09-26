"""q12 encodings. Leftover one-flip of the three q11 followup certificates."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
Q11 = ROOT / 'q11'
Q10 = ROOT / 'q10'
Q9 = ROOT / 'q9'
Q8 = ROOT / 'q8'
sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location('q11common', Q11 / 'common.py')
q11c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q11c)

PTS = q11c.PTS
tree_code = q11c.tree_code
scheme_code = q11c.scheme_code
code_scheme = q11c.code_scheme
triangulation = q11c.triangulation
digest = q11c.digest
unpack = q11c.unpack
flips = q11c.flips
write_task = q11c.write_task
task_tris = q11c.task_tris
atomic_json = q11c.atomic_json
canon = q11c.canon
parse_pcom = q11c.parse_pcom
seeds = q11c.seeds  # published M-certificates plus seventeen parent additions

# Three q11 followup certificates that were never used as one-flip seeds.
FOLLOWUP_SCHEMES = [
    '<1 u 1<1> u 1<4> u 1<10>>',
    '<1<1> u 1<4> u 1<9>>',
    '<1<1> u 1<3> u 1<10>>',
]
N_LEFTOVER = 93
LEFTOVER_PLAN_SHA = '544498c92d5c94d04a0c087f8c6424080120da7420c4108a07a15691c744c912'
LEFTOVER_SEEDS_SHA = 'feeeb688c1a2aeb816e503c399fce369972d7c024c70a6de0008d66b6b42e394'


def q11_schemes():
    certs = json.loads((Q11 / 'certs/new_schemes.json').read_text())
    out = {canon(c['scheme']) for c in certs}
    assert len(out) == 8
    assert set(FOLLOWUP_SCHEMES) <= out
    return out


def baseline():
    """Published 2,367 plus seventeen plus q8 plus nine q9 plus thirteen q10 plus eight q11."""
    prior = q11c.baseline()
    extra = q11_schemes()
    assert extra.isdisjoint(prior)
    out = prior | extra
    assert len(out) == 2415
    return out


def leftover_seeds():
    by = {canon(c['scheme']): c for c in json.loads((Q11 / 'certs/new_schemes.json').read_text())}
    out = []
    for s in FOLLOWUP_SCHEMES:
        c = by[s]
        out.append(dict(
            source='q11 followup: ' + s,
            scheme=s,
            triangles=triangulation(c['triangles']),
            heights=c['heights'],
            signs=c['signs'],
        ))
    assert [c['scheme'] for c in out] == FOLLOWUP_SCHEMES
    return out


def leftover_plan():
    out = []
    for i, c in enumerate(leftover_seeds()):
        for removed, added, tris in flips(unpack(c)[0]):
            out.append(dict(seed=i, removed=removed, added=added,
                            triangulation_sha256=digest(tris)))
    return out


def cert_seeds(path, source_prefix='certificate: '):
    out = []
    for c in json.loads(Path(path).read_text()):
        out.append(dict(
            source=source_prefix + c['scheme'],
            scheme=canon(c['scheme']),
            triangles=triangulation(c['triangles']),
            heights=c['heights'],
            signs=c['signs'],
        ))
    return out


def cert_plan(path, source_prefix='certificate: '):
    out = []
    for i, c in enumerate(cert_seeds(path, source_prefix=source_prefix)):
        for removed, added, tris in flips(unpack(c)[0]):
            out.append(dict(seed=i, removed=removed, added=added,
                            triangulation_sha256=digest(tris)))
    return out


def source_hashes():
    paths = ['q12/ball.c', 'q12/common.py', 'q12/search.py', 'tcore.h',
             'fastcx.py', 'export_span.py', 'haas.py', 'notation.py',
             'replay_census.py', 'tcurve.py', 'data/deg8.pcoms.txz',
             'certs/new_schemes.json', 'census_schemes.txt',
             'q8/certs/new_schemes.json', 'q9/certs/new_schemes.json',
             'q10/certs/new_schemes.json', 'q11/certs/new_schemes.json']
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
