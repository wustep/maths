# Research log — Sets with no unique sum mod p

## 2026-08-16

- [OEIS A398173](https://oeis.org/A398173) — 14 terms through p=47: 3,4,5,7,7,8,9,10,11,11,12,13,13,13.
- [Bedert, arXiv:2303.15134](https://arxiv.org/abs/2303.15134); [Cao–Yuan, arXiv:2608.06728](https://arxiv.org/abs/2608.06728).
- q1 used the wrong predicate (r=1 rather than r∉{1,2}); memory commit `77d43c5`.
- q2 recoded; recovered `green_m_p.csv` matches A398173 through p=47.
