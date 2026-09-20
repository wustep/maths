"""q10 encodings. Leftover one-flip of the four q9 followup certificates."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
Q9 = ROOT / 'q9'
Q8 = ROOT / 'q8'
sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location('q9common', Q9 / 'common.py')
q9c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q9c)

PTS = q9c.PTS
tree_code = q9c.tree_code
scheme_code = q9c.scheme_code
code_scheme = q9c.code_scheme
triangulation = q9c.triangulation
digest = q9c.digest
unpack = q9c.unpack
flips = q9c.flips
write_task = q9c.write_task
task_tris = q9c.task_tris
atomic_json = q9c.atomic_json
canon = q9c.canon
parse_pcom = q9c.parse_pcom
seeds = q9c.seeds  # published M-certificates plus seventeen parent additions

# Four q9 followup certificates that were never used as one-flip seeds.
FOLLOWUP_SCHEMES = [
    '<2 u 1<1> u 1<2> u 1<9>>',
    '<4 u 1<1> u 1<3> u 1<9>>',
    '<3 u 1<1> u 1<3> u 1<9>>',
    '<2 u 1<1> u 1<3> u 1<9>>',
]
LEFTOVER_PLAN_SHA = 'be9520910264e4bcdba6c03618384023d544804e4999a42516a391210e9bd320'
LEFTOVER_SEEDS_SHA = '6fc3cbb36c765248e22abf1a7cc9783224c7dce60dfbca375c055046369c96a4'


def q9_schemes():
    certs = json.loads((Q9 / 'certs/new_schemes.json').read_text())
    out = {canon(c['scheme']) for c in certs}
    assert len(out) == 9
    assert set(FOLLOWUP_SCHEMES) <= out
    return out


def baseline():
    """Published 2,367 plus seventeen plus q8 plus the nine q9 schemes."""
    prior = q9c.baseline()
    extra = q9_schemes()
    assert extra.isdisjoint(prior)
    out = prior | extra
    assert len(out) == 2394
    return out


def leftover_seeds():
    by = {canon(c['scheme']): c for c in json.loads((Q9 / 'certs/new_schemes.json').read_text())}
    out = []
    for s in FOLLOWUP_SCHEMES:
        c = by[s]
        out.append(dict(
            source='q9 followup: ' + s,
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
    paths = ['q10/ball.c', 'q10/common.py', 'q10/search.py', 'tcore.h',
             'fastcx.py', 'export_span.py', 'haas.py', 'notation.py',
             'replay_census.py', 'tcurve.py', 'data/deg8.pcoms.txz',
             'certs/new_schemes.json', 'census_schemes.txt',
             'q8/certs/new_schemes.json', 'q9/certs/new_schemes.json']
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
