# Walkthrough — A 14-vertex degree sequence with a checkable deck

- Problem: `problems/graph-reconstruction-next-order` (P39)
- Date: 2026-08-17
- Argument status: certified full-deck reconstruction for one n=14
  degree sequence (and a second sequence hashing)
- Problem status: open. The Kelly–Ulam conjecture is not proved. McKay’s
  all-graphs frontier is still n=13.

## 0. What was actually missing

McKay (arXiv:2102.01942v4 / AJC 83, 2022) already did every graph on at
most 13 vertices, and at n=14 the three degree windows [0,5], [5,6],
[6,7]. Complements give [7,8] and [8,13] for free. The first open window
at the next order is therefore **graphs with a vertex of degree ≤4 and a
vertex of degree ≥6**.

That window is not a one-quest enumeration. `geng -d4 -D6 14 0/100` was
still running after eight minutes. The missing degree of freedom was not
“run McKay’s parent-child loop on all of n=14”. It was a *recognisable
subclass* of the leftover whose membership is a full-deck invariant and
whose list fits on this machine.

## 1. Named false starts

- **All of n=14.** OEIS A000088: about 2.90×10^16 unlabelled graphs.
  McKay’s n=13 run was already 5.05×10^13 graphs and 1.5 CPU-years. We
  did not start this.

- **The whole (4,6) and (5,7) windows.** These are the first McKay-style
  triples not in Theorem 3.1(h). 1/100 generation slices did not return
  a `>Z` line. That is a size reading, not a reconstruction statement.

- **LSB vertex deletion.** First `deckrecon` packed G−v as if nauty stored
  vertex 0 in the low bit. K3 and P3 received the same deck hash. n=4
  “found” four collisions. nauty packs vertex 0 at the high bit.
  `ISELEMENT` / `ADDONEEDGE` fixed it. After the fix, n=2 is the only
  full-deck collision (K2 and 2K1) and n=3 is the only reduced-deck
  collision (P3 and K2+K1), which is exactly the classical picture.

- **Unpruned 2-factor search.** A first `add_twofactor` walked every
  {0,2}-subgraph of the 9-regular complement of a 4-regular 14-vertex
  graph. It never finished the first parent. The support has to be
  *chosen first* (a k-subset) and then a 2-factor of that subset
  enumerated.

- **Split / chordal / claw-free as the first target.** `geng -S 14`
  produces 67,997,750 split graphs, and Hammer–Simeone says split-ness
  is a degree-sequence predicate, so this is a legal class. It is just
  larger than the biregular slices. Chordal and claw-free generation
  were still running at 15+ minutes with `-q`, and neither property is
  a degree-sequence predicate, so uniqueness inside the class would not
  by itself be reconstructibility.

- **O’Shea–Wilkins 2023.** A claimed general proof with a 2024
  corrigendum; 2026 status pages do not accept it. Unused.

## 2. The useful failure

The 1/100 slices of `-d4 -D6` taught the right scale: the *interval*
[4,6] is dominated by the already-settled nearly-regular pieces [4,5]
and [5,6]. The new graphs are those that actually attain both ends.
Among those, the ones with *no* degree 5 are rare enough to list,
because their extra edges cannot touch the degree-4 vertices.

That is a structural fact, not a search heuristic. Once it is seen,
generation becomes “4-regular plus a 2-factor of the complement on the
degree-6 set”, and `geng -d4 -D4 14` is eight seconds.

## 3. The click

Let G be 14-vertex with degrees 4 or 6 only, and let S be the set of
degree-6 vertices, |S|=s≥3. Every extra edge beyond a 4-regular spanning
subgraph has both ends in S (otherwise a degree-4 vertex would rise to
5). Those extra edges form a 2-regular graph on S, hence a disjoint
union of cycles of length at least 3.

The smallest case is s=3: S induces a triangle of non-edges of a
4-regular graph. There is only one 2-regular graph on three vertices.
The construction is exhaustive for the degree sequence 4^11 6^3.

Kelly’s lemma gives the degree of the deleted vertex on each card, so
the degree sequence of G is a function of the full deck. A hypomorphic
mate of such a G has the same sequence, hence is another graph on the
same list. Unique decks on the list are reconstructibility.

## 4. The argument, in the order it was found

1. Fetch McKay v4 and the 2026 status page. All-graphs record is n=13.
   Interval graphs are now reconstructible for all n≥3
   (arXiv:2504.02353v2); that does not move n=14.

2. Complement + Theorem 3.1(h) leaves (δ,Δ) pairs that escape [0,5],
   [5,6], [6,7], [7,8], [8,13]. The first tight pair is (4,6).

3. Write `deckrecon`: nauty-canonical cards, SHA-256 of the sorted
   (resp. uniqued) graph6 strings. Replay n=2 through n=10 against
   OEIS A000088. Independent checker: Python deletes vertices, `labelg`
   canonicalises, same SHA-256. 2,401 n=10 samples: 0 mismatches.

4. Count 4-regular n=14: 88,193 (88,168 connected). 5-regular n=14:
   3,459,386, already inside McKay’s (0,5;14).

5. Overlay complement triangles, `shortg`. Connected 4-regular parents
   give 18,780,938 labelled overlays and **8,571,676** unlabelled
   graphs. All 8,571,676 have sequence [4]^11[6]^3 (`degcheck`).

6. Hash every deck. 8,571,676 distinct full-deck SHA-256s, 8,571,676
   distinct reduced-deck SHA-256s. 21,429 samples through `labelg`: 0
   mismatches.

7. Repeat from *all* 88,193 four-regular parents (the 25 disconnected
   ones included). Unlabelled count rises by 161, to **8,571,837**,
   still a single degree sequence. Hash the complete list: 8,571,837
   distinct full-deck SHA-256s, 8,571,837 distinct reduced-deck
   SHA-256s. 17,143 `labelg` samples: 0 mismatches. That is the
   complete set of 14-vertex graphs of sequence 4^11 6^3.

8. Same construction with support 4 (a complementary C4): 127,456,264
   labelled overlays from the connected 4-regulars, **41,538,279**
   unlabelled graphs, all of sequence [4]^10[6]^4. Hashing in
   progress; uniqueness is incomplete until `certs/bireg46_s4_unique.txt`
   exists.

## 5. Computer search

- `certs/bireg46_s3.g6` — 8,571,676 graphs from connected 4-regular
  parents; `certs/bireg46_s3_unique.txt`; `certs/sample_bireg46_s3.txt`
  (21,429 lines) for `verify_labelg.py`.
- `certs/bireg46_s3all.g6` — complete 8,571,837; uniqueness
  `certs/bireg46_s3all_unique.txt` (0 collisions; 17,143 `labelg`
  matches).
- `certs/bireg46_s3_degseq.txt`, `certs/bireg46_s3all_degseq.txt`.
- `certs/bireg46_s4.g6` — 41,538,279 graphs, sequence 4^10 6^4, from
  connected 4-regular parents. Complete parents and uniqueness are the
  next leftover.
- `certs/n10_unique.txt` — McKay n=10 replay.
- `certs/split14_count.txt` — 67,997,750 split graphs on 14 vertices,
  not uniqueness-tested.
- The (4,6) *interval* (degrees 4,5,6 all allowed) and all other n=14
  leftover pairs are untouched.

## 6. What is proved vs still open

**Proved here.** Every simple graph on 14 vertices with degree sequence
4,4,4,4,4,4,4,4,4,4,4,6,6,6 is reconstructible from its full deck. The
list is finite, generated by a complete construction, independently
hashed, and sampled against a second canonical-labelling path.

**Also checked, not needed for the conjecture.** Those graphs have
unique *reduced* decks among themselves. Set-reconstruction against a
graph that has a degree-5 vertex is not claimed: the reduced deck
determines min and max degree (Manvel / McKay Lemma 2.2) but not the
absence of intermediate degrees.

**Open.** The reconstruction conjecture. All of n=14. McKay’s next
windows (0,6;14), (4,6;14) as an interval, (5,7;14), split graphs at
n=14, support-4 uniqueness, supports s≥5.

We did not beat McKay’s all-graphs n=13 record. We added a certified
line at n=14 that his Theorem 3.1 does not contain.
