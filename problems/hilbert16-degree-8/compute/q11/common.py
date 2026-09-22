"""q11 encodings. Leftover one-flip of the seven q10 followup certificates."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
Q10 = ROOT / 'q10'
Q9 = ROOT / 'q9'
Q8 = ROOT / 'q8'
sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location('q10common', Q10 / 'common.py')
q10c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q10c)

PTS = q10c.PTS
tree_code = q10c.tree_code
scheme_code = q10c.scheme_code
code_scheme = q10c.code_scheme
triangulation = q10c.triangulation
digest = q10c.digest
unpack = q10c.unpack
flips = q10c.flips
write_task = q10c.write_task
task_tris = q10c.task_tris
atomic_json = q10c.atomic_json
canon = q10c.canon
parse_pcom = q10c.parse_pcom
seeds = q10c.seeds  # published M-certificates plus seventeen parent additions

# Seven q10 followup certificates that were never used as one-flip seeds.
FOLLOWUP_SCHEMES = [
    '<1 u 1<1> u 1<2> u 1<10>>',
    '<1<1> u 1<2> u 1<9>>',
    '<2 u 1<1> u 1<2> u 1<10>>',
    '<3 u 1<1> u 1<2> u 1<10>>',
    '<4 u 2<1> u 1<10>>',
    '<1 u 1<1> u 1<4> u 1<9>>',
    '<2 u 1<1> u 1<5> u 1<9>>',
]
N_LEFTOVER = 205
LEFTOVER_PLAN_SHA = '43c0f0d9227d1672f9521e9d3cc7cb8d9a04113be47a827a60826614ee10b31a'
LEFTOVER_SEEDS_SHA = 'e26a39f33497b13fa34e7d6a1176e613cf72328440acb3db1ae6588170b5fb60'


def q10_schemes():
    certs = json.loads((Q10 / 'certs/new_schemes.json').read_text())
    out = {canon(c['scheme']) for c in certs}
    assert len(out) == 13
    assert set(FOLLOWUP_SCHEMES) <= out
    return out


def baseline():
    """Published 2,367 plus seventeen plus q8 plus nine q9 plus thirteen q10."""
    prior = q10c.baseline()
    extra = q10_schemes()
    assert extra.isdisjoint(prior)
    out = prior | extra
    assert len(out) == 2407
    return out


def leftover_seeds():
    by = {canon(c['scheme']): c for c in json.loads((Q10 / 'certs/new_schemes.json').read_text())}
    out = []
    for s in FOLLOWUP_SCHEMES:
        c = by[s]
        out.append(dict(
            source='q10 followup: ' + s,
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
    paths = ['q11/ball.c', 'q11/common.py', 'q11/search.py', 'tcore.h',
             'fastcx.py', 'export_span.py', 'haas.py', 'notation.py',
             'replay_census.py', 'tcurve.py', 'data/deg8.pcoms.txz',
             'certs/new_schemes.json', 'census_schemes.txt',
             'q8/certs/new_schemes.json', 'q9/certs/new_schemes.json',
             'q10/certs/new_schemes.json']
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
