#!/usr/bin/env python3
"""Real-scheme bracket notation: parse and canonicalize.

Handles this folder's ASCII form  <18 u 1<3>>  and the
dmg-lab/CombinatorialPatchworking form  <18v1<3>>  (and filenames,
where <> is rendered ()).  A scheme is a forest of ovals; an oval is
the tuple of its children's encodings, sorted; J marks a pseudoline.
"""


def parse(s):
    """Return (forest, has_J) where forest is the canonical tuple."""
    s = s.strip().replace("(", "<").replace(")", ">")
    pos = 0

    def peek():
        return s[pos] if pos < len(s) else ""

    def parse_body():
        nonlocal pos
        forest = []
        has_j = False
        while True:
            while pos < len(s) and s[pos] in " uv⊔":
                pos += 1
            ch = peek()
            if ch == "J":
                pos += 1
                has_j = True
            elif ch.isdigit():
                num = 0
                while pos < len(s) and s[pos].isdigit():
                    num = num * 10 + int(s[pos])
                    pos += 1
                if peek() == "<":
                    pos += 1
                    inner, ij = parse_body()
                    if ij:
                        raise ValueError("J inside an oval")
                    if peek() != ">":
                        raise ValueError(f"expected > at {pos} in {s!r}")
                    pos += 1
                    forest.extend([tuple(sorted(inner))] * num)
                else:
                    forest.extend([()] * num)
            elif ch == "<":
                pos += 1
                inner, ij = parse_body()
                if ij:
                    has_j = True
                if peek() != ">":
                    raise ValueError(f"expected > at {pos} in {s!r}")
                pos += 1
                if pos <= len(s) and (pos == len(s) or True):
                    # outermost brackets: treat inner as the forest
                    if forest:
                        raise ValueError(f"unexpected < at {pos} in {s!r}")
                    forest = list(inner)
            else:
                break
        return forest, has_j

    forest, has_j = parse_body()
    if pos != len(s):
        raise ValueError(f"trailing junk at {pos} in {s!r}")
    return tuple(sorted(forest)), has_j


def render(forest, has_j=False):
    def rend(forest):
        forest = sorted(forest)
        groups = []
        i = 0
        while i < len(forest):
            j = i
            while j < len(forest) and forest[j] == forest[i]:
                j += 1
            mult = j - i
            if forest[i] == ():
                groups.append(str(mult))
            else:
                groups.append(f"{mult}<{rend(list(forest[i]))}>")
            i = j
        return " u ".join(groups) if groups else "0"

    body = rend(list(forest))
    if has_j:
        body = f"J u {body}" if body != "0" else "J"
    return f"<{body}>"


def canon(s):
    """Canonical form of any bracket-notation string."""
    forest, has_j = parse(s)
    return render(forest, has_j)


def stats(s):
    """(#ovals, p, n) with p = ovals at even depth, n = odd depth."""
    forest, _ = parse(s)

    def walk(forest, depth):
        o = p = n = 0
        for oval in forest:
            o += 1
            if depth % 2 == 0:
                p += 1
            else:
                n += 1
            so, sp, sn = walk(oval, depth + 1)
            o, p, n = o + so, p + sp, n + sn
        return o, p, n

    return walk(forest, 0)


if __name__ == "__main__":
    tests = [
        ("<18v1<3>>", "<18 u 1<3>>", (22, 19, 3)),
        ("(18v1(3))", "<18 u 1<3>>", (22, 19, 3)),
        ("<1v1<9>v1<10>>", "<1 u 1<9> u 1<10>>", (22, 3, 19)),
        ("<4v1<2v1<14>>>", "<4 u 1<2 u 1<14>>>", (22, 19, 3)),
        ("<16v3<1>>", "<16 u 3<1>>", (22, 19, 3)),
        ("<1<1<1<1>>>>", "<1<1<1<1>>>>", (4, 2, 2)),
        ("<J u 15>", "<J u 15>", (15, 15, 0)),
        ("<0>", "<0>", (0, 0, 0)),
    ]
    for src, want, wstats in tests:
        got = canon(src)
        assert got == want, (src, got, want)
        assert stats(src) == wstats, (src, stats(src), wstats)
    print("notation tests pass")
