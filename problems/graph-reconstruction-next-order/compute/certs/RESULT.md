# Certificate summary

Date: 2026-08-17
Machine: 8-core, nauty 2.9.1, `compute/deckrecon.c`

## Replay (not a dent; verifies the tester)

All graphs on n≤10 vertices have unique reduced decks for n≥4, unique
full decks for n≥3. n=2 is the classical K2 / 2K1 pair. n=3 reduced decks
identify P3 with K2+K1 (set reconstruction starts at n=4).

n=10: 12,005,168 graphs (OEIS A000088), 0 full-deck SHA-256 collisions,
0 reduced-deck collisions. 2,401 graphs rehashed with `labelg`: 0 mismatches.
See `n10_unique.txt`, `sample_n10.txt`.

## Dent: n=14, degree sequence 4^11 6^3

Construction: every 4-regular 14-vertex graph, plus every triangle in
the complement. The three degree-6 vertices must induce a triangle of
extra edges (the only 2-factor on three vertices).

| item | value |
|------|------:|
| 4-regular parents (`geng -d4 -D4 14`) | 88,193 |
| of which connected | 88,168 |
| labelled overlays (all parents) | 18,785,786 |
| unlabelled, complete census | **8,571,837** |
| unlabelled, connected parents only | 8,571,676 |
| extra from 25 disconnected parents | 161 |
| degree sequences (`degcheck`) | 1, namely [4]^11[6]^3 |
| full-deck SHA-256 collisions (complete) | **0** |
| reduced-deck SHA-256 collisions (complete) | **0** |
| `labelg` samples, complete list | 17,143, 0 mismatches |
| `labelg` samples, connected-parent list | 21,429, 0 mismatches |

Files: `bireg46_s3all.g6`, `bireg46_s3all_unique.txt`,
`bireg46_s3all_degseq.txt`, `sample_bireg46_s3all.txt`; connected-parent
twins without `all` in the name.

The degree sequence is reconstructible from the full deck (Kelly). Any
hypomorphic mate would have the same sequence and would appear in the
complete list. Therefore every 14-vertex graph of degree sequence
4^11 6^3 is reconstructible from its full deck.

This class is not in McKay, Theorem 3.1 (Australas. J. Combin. 83 (2022);
arXiv:2102.01942v4). It has δ=4 and Δ=6, so it sits in the n=14 residue
after (0,5;14), (5,6;14) and (6,7;14).

## In progress / residue

- Degree sequence 4^10 6^4 from connected 4-regular parents:
  41,538,279 unlabelled graphs, all of that sequence
  (`bireg46_s4.g6`, `bireg46_s4_degseq.txt`). Uniqueness is
  `bireg46_s4_unique.txt` if present.
- Split graphs n=14: 67,997,750 counted, not uniqueness-tested
  (`split14_count.txt`).
