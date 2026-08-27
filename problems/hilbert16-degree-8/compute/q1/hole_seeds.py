#!/usr/bin/env python3
"""List census certificates that neighbour a hole-map hole.

The four named hot holes only matched two archive files.  This walks
the <a u 1<b> u 1<c>> holes and prints every .pcom whose scheme is a
b-neighbour, so a later ball search can use the files that actually
exist.

usage: python3 q1/hole_seeds.py
"""
import json
import tarfile

from common import boot

boot()

from replay_census import ARCHIVE
from hole_map import scheme


def main():
    census = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    ours = {x["scheme"] for x in json.load(open("certs/new_schemes.json"))}
    known = census | ours
    tar = tarfile.open(ARCHIVE)
    names = [n for n in tar.getnames() if n.endswith(".pcom")]

    def neighbours(tot, a, b, c):
        out = []
        if b > 1:
            out.append(scheme(a, b - 1, c + 1))
        if c > b + 1:
            out.append(scheme(a, b + 1, c - 1))
        if a > 0:
            out.append(scheme(a - 1, b, c + 1))
            out.append(scheme(a - 1, b + 1, c))
        out.append(scheme(a + 1, b, c - 1))
        out.append(scheme(a + 1, b - 1, c) if b > 1 else None)
        return [s for s in out if s and s in known]

    holes = []
    for tot in (22, 21, 20, 19, 18):
        for a in range(0, 12):
            for b in range(1, 12):
                c = tot - 2 - a - b
                if c < b:
                    continue
                s = scheme(a, b, c)
                if s not in known:
                    holes.append((tot, a, b, c, s, neighbours(tot, a, b, c)))

    # map scheme string as written in TYPE-ish pcom path
    def path_of(sch):
        # archive: (5v1(5)v1(10)).pcom for <5 u 1<5> u 1<10>>
        body = sch[1:-1] if sch.startswith("<") and sch.endswith(">") else sch
        inner = (body.replace(" u ", "v")
                 .replace("<", "(").replace(">", ")").replace(" ", ""))
        hits = [n for n in names if n.endswith(f"({inner}).pcom")]
        return hits

    print(f"{len(holes)} holes in the two-nest family through 18 ovals")
    usable = []
    for tot, a, b, c, s, nbs in holes:
        files = []
        for nb in nbs:
            files.extend(path_of(nb))
        files = sorted(set(files))
        if files:
            usable.append((s, files))
            print(f"  {s}  neighbours={len(nbs)}  pcoms={len(files)}")
            for fn in files[:6]:
                print(f"     {fn}")
    print(f"{len(usable)} holes have at least one neighbour certificate")
    json.dump([{"hole": s, "pcoms": fs} for s, fs in usable],
              open("q1/certs/hole_neighbour_seeds.json", "w"), indent=1)
    print("wrote q1/certs/hole_neighbour_seeds.json")


if __name__ == "__main__":
    main()
