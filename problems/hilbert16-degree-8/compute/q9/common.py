"""q9 encodings. Reuse q8 plan/seeds; the baseline includes the q8 scheme."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
Q8 = ROOT / 'q8'
sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location('q8common', Q8 / 'common.py')
q8c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(q8c)

PTS = q8c.PTS
tree_code = q8c.tree_code
scheme_code = q8c.scheme_code
code_scheme = q8c.code_scheme
triangulation = q8c.triangulation
digest = q8c.digest
unpack = q8c.unpack
flips = q8c.flips
write_task = q8c.write_task
plan = q8c.plan
seeds = q8c.seeds
task_tris = q8c.task_tris
atomic_json = q8c.atomic_json
canon = q8c.canon
parse_pcom = q8c.parse_pcom
Q8_SCHEME = '<3 u 1<3> u 1<12>>'
Q8_PLAN_SHA = '57b02fc3bcd778ce8af7b20f54e57f67ae0597218c5b27f8ac9924fc00ca7fc2'
Q8_SEEDS_SHA = '7e6a53d838592345d56be42df2a9520ce6f9ef0a9620137ae2e7c23f3569096e'
REMAINING_START = 82
REMAINING_STOP = 1190


def q8_schemes():
    certs = json.loads((Q8 / 'certs/new_schemes.json').read_text())
    out = {canon(c['scheme']) for c in certs}
    assert out == {Q8_SCHEME}
    return out


def baseline():
    """Published 2,367 plus seventeen parent additions plus the q8 scheme."""
    prior = q8c.baseline()
    extra = q8_schemes()
    assert extra.isdisjoint(prior)
    out = prior | extra
    assert len(out) == 2385
    return out


def q8_certificates():
    return json.loads((Q8 / 'certs/new_schemes.json').read_text())


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


def extra_seeds():
    """One-flip neighbourhood of the q8 certificate, a new finite domain."""
    out = cert_seeds(Q8 / 'certs/new_schemes.json', source_prefix='q8 addition: ')
    assert len(out) == 1
    return out


def extra_plan():
    return cert_plan(Q8 / 'certs/new_schemes.json', source_prefix='q8 addition: ')


def cert_plan(path, source_prefix='certificate: '):
    out = []
    for i, c in enumerate(cert_seeds(path, source_prefix=source_prefix)):
        for removed, added, tris in flips(unpack(c)[0]):
            out.append(dict(seed=i, removed=removed, added=added,
                            triangulation_sha256=digest(tris)))
    return out


def source_hashes():
    paths = ['q9/ball.c', 'q9/common.py', 'q9/search.py', 'tcore.h',
             'fastcx.py', 'export_span.py', 'haas.py', 'notation.py',
             'replay_census.py', 'tcurve.py', 'data/deg8.pcoms.txz',
             'certs/new_schemes.json', 'census_schemes.txt',
             'q8/certs/new_schemes.json']
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
