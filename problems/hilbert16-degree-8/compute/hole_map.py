#!/usr/bin/env python3
"""Where the published census is thin, in the two-nest family.

Prints, for each oval count, which schemes <a u 1<b> u 1<c>> are in the
replayed 2,367, which are ours (certs/new_schemes.json), and which are in
neither.  Every scheme this search found outside the census sits in a run of
'.'s in one of these rows, which is what "the census misses the neighbours of
its own M-curves" looks like concretely.  A '-' next to several '.'s and 'N's
is a target, not a claim: nothing here says a '-' is unrealizable.
"""
import json
import sys


def scheme(a, b, c):
    parts = ([str(a)] if a else []) + [f"1<{b}>", f"1<{c}>"]
    return "<" + " u ".join(parts) + ">"


def main():
    census = {l.strip() for l in open("census_schemes.txt") if l.strip()}
    new = {x["scheme"] for x in json.load(open("certs/new_schemes.json"))}
    print("family <a u 1<b> u 1<c>> with b <= c;  . = in the 2,367, "
          "N = certified here, - = neither")
    targets = []
    for tot in (22, 21, 20, 19):
        print(f"\n--- {tot} ovals   (b along the row, b = 1..8)")
        for a in range(0, 9):
            row = []
            for b in range(1, 9):
                c = tot - 2 - a - b
                if c < b:
                    row.append(" ")
                    continue
                s = scheme(a, b, c)
                if s in census:
                    row.append(".")
                elif s in new:
                    row.append("N")
                else:
                    row.append("-")
                    targets.append((tot, a, b, c, s))
            if any(x != " " for x in row):
                print(f"  a={a:2d}: " + " ".join(row))
    # a hole is interesting when both its neighbours in b are realized
    hot = []
    for tot, a, b, c, s in targets:
        left = scheme(a, b - 1, c + 1) if b > 1 else None
        right = scheme(a, b + 1, c - 1) if c > b + 1 else None
        ok = lambda x: x is not None and (x in census or x in new)
        if ok(left) and ok(right):
            hot.append(s)
    print(f"\nholes with both b-neighbours realized ({len(hot)}):")
    for s in hot:
        print("   ", s)


if __name__ == "__main__":
    main()
