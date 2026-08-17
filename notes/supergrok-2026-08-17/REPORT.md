# SuperGrok 2026-08-17

Weekly SuperGrok pool, `grok-4.6` xhigh. No Extra Usage purchase.

## Finished

### P15 Chowla cosine — `problems/chowla-cosine`

Verified: for every n ≥ 1 and every n-element set of positive integers,

    min_x  ∑_{a ∈ A} cos(a x)  ≤  − n^{1/7} / 18.

Replay: `cd problems/chowla-cosine && ./compute/run_all.sh` (exit 0).

This names the constant in Bedert §7's polynomial bound. It does **not** beat Bedert v3's exponent `n^{1/5−o(1)}`. Soft spot: the Young/split constants 3 and 14 in `compute/CONSTANTS.md`.

### P07 Sidon second term — `problems/sidon-second-term`

Verified Hou–Zhao arXiv:2607.01169v2 (C < 0.9435) independently, then the same eight kernels at L=6:

    F(N) ≤ √N + 0.94349251 N^{1/4} + O(1)

with √(ab) = 0.9434925085, which is 8.22×10^{-8} below Hou–Zhao's exact γ0. Replay:

```
python3 problems/sidon-second-term/compute/verify_houzhao.py
python3 problems/sidon-second-term/compute/verify_certificate.py problems/sidon-second-term/compute/certs/hz_kernels_L6.json --beat 0.94349259
python3 problems/sidon-second-term/compute/verify_beat_hz.py
```

Does **not** change the four-decimal statement 0.9435. Same lemma, longer boundary. Residue if the bar is a new method or a 0.9434-level constant.


### P29 unit-distance 509 — `problems/unit-distance-509`

No smaller 5-chromatic unit-distance graph. Independently rebuilt Parts 509: n=509, m=2442, field Q(√3,√5,√11). Cadical 4-coloring UNSAT with drat-trim `s VERIFIED`. Vertex-critical (509/509 deletions 4-colorable). 1-for-2 swaps on degree-4 pairs against the radius-2.55 lattice/ρ reserve: 0 hits. A 514-vertex swap graph is also critical and does not beat 509. Published record still 509.

Replay of the exact rebuild: `python3 problems/unit-distance-509/compute/verify_graph.py 509_parts.vtx`.

### Landau 4 — `problems/landau-n2-plus-1`

Extended the certified prefix. At N=10^6: 54110 primes n^2+1, matching Wolf / OEIS A083844 π_q(10^{12})=54110. True Ω=2 composites: 147612. Iwaniec P2s: 201722. Bateman–Horn ratio 1.00260. No new prime. Infinitude still open.

Replay: `python3 compute/sieve_n2p1.py --n-max 1000000` then `python3 compute/verify.py`.


### P16 cosine zeros — `problems/cosine-zeros`

Verified: for {0,1}-cosine sums, Z(N) ≥ log log N / (200 log log log N) whenever the right-hand side is ≥ 4. Replay `cd problems/cosine-zeros && ./compute/run_all.sh` (exit 0). Names the constant in Bedert's (log log N)^{1-o(1)}. Does **not** beat the exponent or the O((N log N)^{2/3}) barrier.

### P14 two-squares gap — `problems/two-squares-gap`

Claim: G(n) < 2√2 n^{1/4} − 3 for 2 ≤ n ≤ 1.024e15 except {3,6,21,91}. Independently checked the stored m≤250 witnesses: 15993/15993, 0 bad (`verify_a3_cert.py a3_cert_m250.json`). Did not re-run the m≤8000 search. Does **not** prove Green's 1/10. Beats Jameson's published additive −2 on that range.

### P20 Ulam sequence — `problems/ulam-sequence`

Independently certified the L=22 word `2313131131313131311313` has F2=9690750 and C_F < 1.442 by integer comparison, beating Clément–Steinerberger 1.454. nwords matches the closed admissible-language count 4316282880. Did not re-enumerate 4.3e9 words. Density still open.

### P08 long-gap dilate — `problems/long-gap-dilate`

No certified \(C>2\). Independently replayed Shakan on listed sets (`verify.py`, 104 reports, 0 failures) and every SAT witness through \(p=71\) (`verify_sat_witnesses.py`, 0 failures). For \(17\le p\le 71\) and \(n=\mathrm{round}\sqrt p\), \(G(p,n)\ge 2.1\sqrt p\) with a checked witness. Isolated small-\(p\) table, not a universal constant. Record still Shakan's 2.

### P09 thin cyclic bases — `problems/thin-cyclic-bases`

Independently replayed Bevan–Erskine–Lewis certificates through \(q=61\) (\(n=21594\), ratio \(1.660\)) and Haanpää's twelve cyclic table rows: all `A+A` covers (`verify.py` exit 0). No family with liminf strictly below \(\sqrt{8/3}\). Counting-optimal \(\sqrt2\) still open. Isolated Haanpää-scale tables are not an infinite-family dent.

### P33 union-closed — `problems/union-closed`

Independently replayed `compute/verify.py` (ALL_OK). On the \(\{b,1\}\) family, iid + Liu Example-4 mix at \(\beta=1/5\) has Gilmer ratio \(\ge 1.000077\) whenever the mean is \(\le 0.38285\) (5.1M mesh cells). Recovers Liu's Example-5 number \(0.382709087918735\). Same hypothesis class as Liu Theorem 13 (optimizer family, not every measure on \([0,1]\)). Not \(1/2\). Not a new reduction.

### P27 Cohn–Elkies planar — `problems/cohn-elkies`

Exact rational Laguerre–Gaussian from Cohn–Elkies Table 4 nodes. Independently replayed `compute/verify.py` (ALL CHECKS PASSED): R = 3627599/500000 = 7.255198, center density ≤ 0.2886751562026082, ratio to hexagonal 1.0000000748515987. Beats the printed Table 4 value 7.25520; meets Table 3 0.28868. Not a magic function (target 4π/√3). Green #42 still open.

### P30 kissing number 5d — `problems/kissing-5d`

Independently replayed `compute/verify_certificates.py` (exit 0). Restricted Delsarte: T_D5 bound 42 (excludes 43, 44); T_L5 bound 239925/5456 ≈ 43.9745 (excludes 44). Unrestricted range still 40 ≤ τ_5 ≤ 44. Restricted certificates, not the unrestricted kissing number.

### P05 affine {0,1,3} copies — `problems/affine-013`

Verified: for every finite S subset Z with |S|=n, Aaronson's T(S) = #{(x,y,z) in S^3 : x+2y=3z} satisfies T(S) <= ceil(n^2/2). Replay `python3 compute/verify_half.py` (ALL OK): sum identity through n=399, exhaustive fibres through n=7, 2360 random sets. Beats Aaronson's published 3/4. Interval still ~n^2/3. Conjecture 1/3 open.

### P17 random 0/1 polynomials — `problems/zero-one-polynomials`

Independently replayed `verify_fourier.py` (exit 0): BSKK N=2 theta = 0.00373556, published 0.003736 is a 4e-7 over-round. Stored census n=1..20 internally consistent (`verify_census.py`). 0/1-factor counts through n=16 sit under the rho^n majorant. Did not re-factor n=20. Unconditional p_n -> 1 still open.

### P34 1/3–2/3 posets — `problems/one-third-two-thirds`

Independently enumerated all 10! linear extensions of the stored covers of \(W_{10}\): e=187, pair 121:66, \(\delta=6/17<14/39\), still \(>1/3\). Width-3 via antichains {1,2,3} and {5,7,8}. Replay of the brute-force LE count, not of `verify_W10.py`'s DP. Did **not** re-run the 204M naturally labelled n=10 census, so uniqueness is their claim. All computed 3-chain boxes still \(\ge 1/3\); Olson–Sagan Q3.9 open. Unrestricted conjecture open.

### P37 Seymour second neighborhood — `problems/seymour-second-neighborhood`

Independently recomputed first/second neighbourhoods on seven stored n=8 certificates. All seven are Pisa (strong, \(\Delta=0\)). Three are irregular non-matchings: missing-degree \(3^2 2^6\), \(3^4 2^4\), \(3^6 2^2\). Also a non-tight 2-regular missing example. Headline witness `certs/n8_irregular_pisa.json` (ternary 145923119419): margins (0,-1,0,0,-1,-1,0,0). Did **not** re-run the 2.5B geng orientation census, so “exactly seven types” is their claim. Seymour still open. Eulerian \(n=2\delta+3\) tables do not beat Kaneko–Locke.

### P12 two smooth summands — `problems/two-smooth-summands`

Documented residue. Independently: split 649+131486110 realises F(131486759)=83; M is not a 73-smooth or 79-smooth sum (808372 / 727473 smooth integers through M-1); Jacobi(-M/q)=1 for the 21 odd primes q<=79. G(y) replayed through y=23, matching the stored A062241 values. Stored exception witnesses check: 3 for n^{1/2} (last 23), 16 for n^{2/5} (last 479), 76 for n^{1/3} (last 18191). Square-plus-remainder template holds on [2,5000] plus large spots. Did **not** re-run the C bitset covering [2,G(y)-1] for y>=31, so G(y) through 79 is their claim. Did not beat Balog 4/(9 sqrt(e)). Green #59 open.

### P38 Tuza triangles — `problems/tuza-triangle-packing-covering`

Independently checked all 1044 stored 7-vertex cores in `certs/c7_8reg_verified.json` (1002 template, 42 ILP): each (S,X) is a Puleo witness on the 9-vertex local graph (S edge-disjoint, |X|<=2|S|, every uv-through triangle hits X, S-edges off the hubs lie in X). 1044 distinct order-7 graph6 strings, matching the known count of unlabelled graphs on 7 vertices. The K7 core `F~~~w` is an STS(9) / affine plane of order 3: 12 triples, every pair once, |X|=22. Did **not** re-run geng, the n=8 WKE census, or the split n<=10 table. Does **not** prove Tuza for Delta<=8. Haxell 66/23 unchanged.

### P36 Caccetta–Häggkvist — `problems/caccetta-haggkvist-k3`

Independently replayed `verify_certificate.py` on the stored F4 flag-algebra certificate: c=0.34645, min eig(Q)=9.53e-9, worst F=-0.12343, all 32 coordinates < -0.05. Q is 8x8 PSD from the JSON alone. This is 5e-5 below the published HKN 0.3465 (a four-decimal rounding). Did **not** beat the 0.3388 personal communication. Did **not** independently replay drat-trim on the n=12,15,16,17 SAT proofs. n=18 d=6 remains UNKNOWN (residue). Conjecture 1/3 open.

### P31 projective plane of order 12 — `problems/projective-plane-order-twelve`

Residue. Independently replayed `replay_identities.py` (v=157, 12246 pairs, |det B|=13*12^78, Bruck–Ryser silent) and `classify_types.py` (all_ok; leftover Aut types: involutory elation, planar PG(2,3), generalized elation f in {1,4,7,10}). Independently verified both involution 2-MOLS (`verify_involution_mols.py`): Latin, pairwise orthogonal, L[r+6][c]=L[r][c]+6. Intercalate counts 108+108 (MacNeish) vs 90+78 (SAT), so not isotopic. Did **not** independently replay drat-trim on the mate-UNSAT proofs. t=3 kissat UNKNOWN is a timeout, not an exclusion. Published Aut still |G| in {1,2,3}. Plane still open.

### P41 R(5,5) — `problems/ramsey-r55`

Residue. Independently replayed `verify_mckay.py` on `refs/r55_42some.g6` (sha256 067902e853d87b49bcef0d1d4c0e3bbadd238ee18bc65341b079a3ca4780eccb): 328 lines, 328 ok, 328 complements also (5,5), 0 self-complementary, unique_fp=173, delta=19, Delta=22, no regular graphs. That is the published 656 (graph + complement). Independently replayed `py_circulant.py` 42 and 43: empty in the legal degree window. Did **not** independently replay the C Cayley census, extend_check, or involution SAT. Published record still 43 <= R(5,5) <= 46. Do not cite the folder as a bound.

### P39 graph reconstruction n=14 — `problems/graph-reconstruction-next-order`

SuperGrok claimed every 14-vertex graph of degree sequence 4^11 6^3 is reconstructible from its full deck (8,571,837 unlabelled graphs; 0 full-deck and 0 reduced-deck SHA-256 collisions). Independently: counted `bireg46_s3all.g6` = 8,571,837 lines and `bireg46_s3.g6` = 8,571,676; 200,000-prefix plus all 17,143 `labelg` samples are n=14 with sequence 4^11 6^3; `verify_labelg.py` on `sample_bireg46_s3all.txt`: checked=17143 mismatches=0. Also counted `bireg46_s4.g6` = 41,538,279; `labelg` samples checked=20769 mismatches=0. Did **not** independently re-sort the 8.5M (or 41M) deck hashes, re-run `geng`/`shortg`, or replay `degcheck` on the full lists. Uniqueness, and therefore reconstructibility, is their `deckrecon` sort. McKay all-graphs n=13 unchanged.

### P44 lonely runner 14 — `problems/lonely-runner-fourteen`

Incomplete (quota death, no WALKTHROUGH). Independently: `rk_inclusion.py --selftest` OK (k=10 at 103,107,109; k=12 at 149,151; k=13 at 173,179,181 and p>182). Family count 14^6-13^6-1=2,702,726. Two p=191 witnesses via `verify_witness.py`: v=(0..0,1,0) s=1 j=16 min_d=205; mixed v=(1,0,0,12,6,10,0,1,0,4,0,10,0) s=1 j=12 min_d=230. Did **not** replay leftover_csp / exhaustive rem>=4 salvage. LRC(13) open.

## Wrap

Weekly SuperGrok/Build pool returned 402 Payment Required (balance exhausted) on both live runs. Stopped launching. Did not buy Extra Usage. Local g6 lists for P39 are not in git (hundreds of MB).
