"""Shared path and census helpers for the q1 searches.

Every q1 driver is meant to be launched from this folder or from
``compute/``; we always chdir to the parent ``compute/`` so the
existing archive, ``certs/``, and Haas tables resolve.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def boot():
    os.chdir(ROOT)
    return ROOT


def known_schemes():
    ks = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    assert len(ks) == 2367, len(ks)
    for c in json.load(open("certs/new_schemes.json")):
        ks.add(c["scheme"])
    extra = os.path.join(HERE, "certs", "new_schemes.json")
    if os.path.exists(extra):
        for c in json.load(open(extra)):
            ks.add(c["scheme"])
    return ks


def census_schemes():
    ks = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    assert len(ks) == 2367
    return ks
