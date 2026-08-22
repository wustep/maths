#!/usr/bin/env python3
"""Independent topological check of the schemes this search reports.

Nothing here looks at a triangulation or a sign vector: it parses the
bracket strings and applies the classical congruences for real plane
curves of degree 2k = 8 (k = 4, k^2 = 16).

  Rokhlin (M-curves):                 p - n = k^2      (mod 8)
  Gudkov-Krakhnov-Kharlamov (M-1):    p - n = k^2 +- 1 (mod 8)

with p the number of even-depth ovals and n the number of odd-depth
ovals.  An M-curve of degree 8 has 22 ovals, so a failure here would mean
the sweep had produced a scheme that no real degree-8 curve can have --
i.e. a bug in the evaluator.  It is a check, not a search.
"""
import json
import sys


def parse(s):
    """bracket string -> list of oval depths"""
    s = s.strip()
    assert s.startswith("<") and s.endswith(">"), s
    depths = []

    def body(t, d):
        # t is the inside of a <...>; groups separated by " u "
        if t == "0" or t == "":
            return
        for g in split_top(t):
            g = g.strip()
            if "<" in g:
                mult = int(g[:g.index("<")])
                inner = g[g.index("<") + 1:-1]
                for _ in range(mult):
                    depths.append(d)
                    body(inner, d + 1)
            else:
                for _ in range(int(g)):
                    depths.append(d)

    def split_top(t):
        out, lvl, cur = [], 0, ""
        i = 0
        while i < len(t):
            c = t[i]
            if c == "<":
                lvl += 1
            elif c == ">":
                lvl -= 1
            if lvl == 0 and t[i:i + 3] == " u ":
                out.append(cur)
                cur = ""
                i += 3
                continue
            cur += c
            i += 1
        out.append(cur)
        return out

    body(s[1:-1], 0)
    return depths


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else \
        "certs/census_span_classification.json"
    d = json.load(open(src))
    schemes = d["distinct_M_schemes"]
    k2 = 16
    bad = []
    for s in schemes:
        dep = parse(s)
        p = sum(1 for x in dep if x % 2 == 0)
        n = len(dep) - p
        if len(dep) != 22:
            bad.append((s, f"{len(dep)} ovals, not 22"))
        elif (p - n - k2) % 8:
            bad.append((s, f"p-n = {p-n}, not = 16 mod 8"))
    print(f"{len(schemes)} M-schemes, {len(schemes)-len(bad)} satisfy "
          f"22 ovals and Rokhlin's congruence p-n = k^2 (mod 8)")
    for s, why in bad:
        print("  FAIL", s, why)

    new = json.load(open("certs/new_schemes.json"))
    print(f"\n{len(new)} certified schemes outside the census:")
    for c in new:
        dep = parse(c["scheme"])
        p = sum(1 for x in dep if x % 2 == 0)
        n = len(dep) - p
        tag = ""
        if len(dep) == 21:
            tag = ("GKK ok" if (p - n - k2) % 8 in (1, 7) else "GKK FAIL")
        elif len(dep) == 22:
            tag = ("Rokhlin ok" if (p - n - k2) % 8 == 0 else "Rokhlin FAIL")
        print(f"  {c['scheme']:24s} ovals={len(dep):2d} p-n={p-n:3d} {tag}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
