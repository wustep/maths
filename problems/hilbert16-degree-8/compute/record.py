#!/usr/bin/env python3
"""The published degree-8 record, as data.

Sources (fetched 2026-08-21, see RESEARCH.md):
  * Orevkov, "Classification of flexible M-curves of degree 8 up to
    isotopy", GAFA 12 (2002) 723-755: the 89 real schemes realizable
    by pseudo-holomorphic M-curves; 83 realized algebraically, six
    open (SIX_OPEN below).
  * Geiselmann-Joswig-Kastner-Mundinger-Pokutta-Spiegel-Wack-Zimmer,
    "Limits of Combinatorial Patchworking", arXiv:2602.06888 v3
    (2026), Table 1 and Section 5.3: 38 of the 89 realized as
    T-curves (bold in their Table 1; certificates in
    dmg-lab/CombinatorialPatchworking, replayed by replay_census.py);
    the 12 with (p,n) = (3,19) are impossible as T-curves (their
    Theorem 21); the remaining 39 are undecided as T-curves.

All schemes are stored in this folder's canonical ASCII notation
(notation.canon of the paper's bracket notation).
"""

from notation import canon, stats

# the six M-schemes whose ALGEBRAIC realizability is open (Orevkov)
SIX_OPEN = [canon(s) for s in [
    "<4v1<2v1<14>>>",      # (p,n) = (19,3), T-curve status open
    "<14v1<2v1<4>>>",      # (p,n) = (19,3), T-curve status open
    "<1v1<1>v1<18>>",      # (3,19), not a T-curve (Thm 21)
    "<1v1<4>v1<15>>",      # (3,19), not a T-curve (Thm 21)
    "<1v1<7>v1<12>>",      # (3,19), not a T-curve (Thm 21)
    "<1v1<9>v1<10>>",      # (3,19), not a T-curve (Thm 21)
]]

# Orevkov's Table 1 as reproduced (with two corrections) in
# arXiv:2602.06888 v3 Table 1.  T = realized as T-curve there.
M_SCHEMES = {}
_TABLE = [
    # (p,n) = (19,3): 20 schemes
    ("<18v1<3>>", True), ("<17v1<1>v1<2>>", True), ("<16v3<1>>", True),
    ("<1v1<2v1<17>>>", False), ("<2v1<2v1<16>>>", False),
    ("<3v1<2v1<15>>>", False), ("<4v1<2v1<14>>>", False),
    ("<5v1<2v1<13>>>", False), ("<6v1<2v1<12>>>", False),
    ("<7v1<2v1<11>>>", False), ("<8v1<2v1<10>>>", False),
    ("<9v1<2v1<9>>>", False), ("<10v1<2v1<8>>>", True),
    ("<11v1<2v1<7>>>", False), ("<12v1<2v1<6>>>", False),
    ("<13v1<2v1<5>>>", False), ("<14v1<2v1<4>>>", False),
    ("<15v1<2v1<3>>>", False), ("<16v1<2v1<2>>>", False),
    ("<17v1<2v1<1>>>", True),
    # (p,n) = (15,7): 19 schemes
    ("<14v1<7>>", True), ("<13v1<1>v1<6>>", True),
    ("<13v1<2>v1<5>>", True), ("<13v1<3>v1<4>>", True),
    ("<12v2<1>v1<5>>", True), ("<12v1<1>v2<3>>", True),
    ("<1v1<6v1<13>>>", False), ("<2v1<6v1<12>>>", False),
    ("<3v1<6v1<11>>>", False), ("<4v1<6v1<10>>>", False),
    ("<5v1<6v1<9>>>", False), ("<6v1<6v1<8>>>", True),
    ("<7v1<6v1<7>>>", False), ("<8v1<6v1<6>>>", False),
    ("<9v1<6v1<5>>>", True), ("<10v1<6v1<4>>>", True),
    ("<11v1<6v1<3>>>", True), ("<12v1<6v1<2>>>", False),
    ("<13v1<6v1<1>>>", True),
    # (p,n) = (11,11): 19 schemes
    ("<10v1<11>>", True), ("<9v1<1>v1<10>>", True),
    ("<9v1<2>v1<9>>", True), ("<9v1<3>v1<8>>", True),
    ("<9v1<4>v1<7>>", True), ("<9v1<5>v1<6>>", True),
    ("<8v2<1>v1<9>>", True), ("<8v1<1>v1<3>v1<7>>", True),
    ("<8v1<1>v2<5>>", True), ("<8v2<3>v1<5>>", True),
    ("<1v1<10v1<9>>>", False), ("<2v1<10v1<8>>>", False),
    ("<3v1<10v1<7>>>", False), ("<4v1<10v1<6>>>", False),
    ("<5v1<10v1<5>>>", True), ("<6v1<10v1<4>>>", True),
    ("<7v1<10v1<3>>>", True), ("<8v1<10v1<2>>>", False),
    ("<9v1<10v1<1>>>", True),
    # (p,n) = (7,15): 19 schemes
    ("<6v1<15>>", True), ("<5v1<1>v1<14>>", True),
    ("<5v1<2>v1<13>>", True), ("<5v1<3>v1<12>>", True),
    ("<5v1<4>v1<11>>", True), ("<5v1<5>v1<10>>", True),
    ("<5v1<6>v1<9>>", False), ("<5v1<7>v1<8>>", True),
    ("<4v2<1>v1<13>>", False), ("<4v1<1>v1<3>v1<11>>", False),
    ("<4v1<1>v1<5>v1<9>>", False), ("<4v1<1>v2<7>>", False),
    ("<4v1<3>v1<5>v1<7>>", False), ("<4v3<5>>", False),
    ("<1v1<14v1<5>>>", False), ("<2v1<14v1<4>>>", False),
    ("<3v1<14v1<3>>>", False), ("<4v1<14v1<2>>>", False),
    ("<5v1<14v1<1>>>", True),
    # (p,n) = (3,19): 12 schemes, none T-realizable (Thm 21)
    ("<2v1<19>>", False), ("<1v1<1>v1<18>>", False),
    ("<1v1<2>v1<17>>", False), ("<1v1<4>v1<15>>", False),
    ("<1v1<5>v1<14>>", False), ("<1v1<7>v1<12>>", False),
    ("<1v1<8>v1<11>>", False), ("<1v1<9>v1<10>>", False),
    ("<2<1>v1<17>>", False), ("<1<1>v1<7>v1<11>>", False),
    ("<1<5>v2<7>>", False), ("<1v1<18v1<1>>>", False),
]
for s, t in _TABLE:
    M_SCHEMES[canon(s)] = t

T_REALIZED = sorted(s for s, t in M_SCHEMES.items() if t)
IMPOSSIBLE_T = sorted(s for s in M_SCHEMES
                      if stats(s)[1:] == (3, 19))
UNDECIDED_T = sorted(s for s, t in M_SCHEMES.items()
                     if not t and stats(s)[1:] != (3, 19))


def selfcheck():
    assert len(M_SCHEMES) == 89, len(M_SCHEMES)
    assert len(T_REALIZED) == 38, len(T_REALIZED)
    assert len(IMPOSSIBLE_T) == 12, len(IMPOSSIBLE_T)
    assert len(UNDECIDED_T) == 39, len(UNDECIDED_T)
    for s in M_SCHEMES:
        o, p, n = stats(s)
        assert o == 22, (s, o)
        assert (p - n) % 8 == 0, (s, p, n)   # Gudkov-Rokhlin
    for s in SIX_OPEN:
        assert s in M_SCHEMES, s
        assert not M_SCHEMES[s], s
    bypn = {}
    for s in M_SCHEMES:
        bypn.setdefault(stats(s)[1:], []).append(s)
    counts = {k: (len(v), sum(M_SCHEMES[s] for s in v))
              for k, v in sorted(bypn.items())}
    # totals and bold counts of 2602.06888 v3 Table 1
    assert counts == {(3, 19): (12, 0), (7, 15): (19, 8),
                      (11, 11): (19, 14), (15, 7): (19, 11),
                      (19, 3): (20, 5)}, counts
    return counts


if __name__ == "__main__":
    print("per (p,n): {(p,n): (total, T-realized)}")
    print(selfcheck())
    # cross-check against the replayed census
    cens = {line.strip() for line in open("census_schemes.txt")}
    m_in_census = sorted(s for s in cens if stats(s)[0] == 22)
    assert m_in_census == T_REALIZED, "census 22-oval set != Table 1 bold"
    print(f"census 22-oval schemes == Table 1 bold set (38): OK")
    print(f"six open: {SIX_OPEN}")
