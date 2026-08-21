# Priority — unresolved

Table 5.1 of arXiv:2511.02542 is explicitly "the best **as far as the authors
know**". That is not the same as a priority claim, and the covering-codes
length tables are scattered across a literature that is badly indexed. Treat
$\ell_2(10,2) \le 50$ as **new until a human confirms otherwise**, and do not
post anything until every box below is ticked.

None of these can be done from inside this repo. All of them need a person.

## Checklist

- [ ] **Lobstein's online covering-radius bibliography.** The standing
      bibliography maintained by Antoine Lobstein (Télécom Paris / CNRS) is the
      canonical index for this area. Search it for $\ell_2(10,2)$, for
      $[50,40]$ and $[51,41]$ binary codes, and for any post-2003 entry citing
      Kaikkonen–Rosendahl. Also check the associated online length tables for
      $\ell_2(r,2)$ if a current copy is reachable.
- [ ] **ACCT proceedings, Davydov–Drozhzhina-Labinskaya lineage.** The
      Algebraic and Combinatorial Coding Theory workshop volumes (Bulgaria,
      biennial since 1988) are the single most likely place a 50 is already
      hiding: covering-code length records have appeared there for decades, the
      volumes are poorly indexed, many are not on MathSciNet, and several are
      not online at all. Work backwards from the Davydov and
      Drozhzhina-Labinskaya papers and forwards through anything citing them.
      This is the box most likely to fail.
- [ ] **Cohen, Honkala, Litsyn, Lobstein, _Covering Codes_ (North-Holland,
      1997).** Check the $\ell_2(r,2)$ length tables in Chapter 5 / the
      appendix tables, and check the supplement/errata. Note that
      arXiv:2511.02542 marks the Kaikkonen–Rosendahl result with $\bullet$
      precisely because it is *not* in this book, so the book predates the 51 —
      but it may still record constructions worth comparing.
- [ ] **Kaikkonen–Rosendahl 2003 itself** (IEEE Trans. Inform. Theory 49(7), 1809-1812,
      doi:10.1109/TIT.2003.813508). Read what they actually claim and whether they or anyone citing
      them note a better length at $r = 10$.
- [ ] **Lower bounds on $\ell_2(10,2)$.** Is anything known beyond the
      sphere-covering bound of 45? Check the excess/counting-bound literature
      for radius-2 binary codes and any exhaustive search results for small $r$.
      If a lower bound of 50 exists somewhere, this result is *optimal* and the
      note should say so; if a lower bound of 46–49 exists, the note should
      quote it instead of 45.
- [ ] **Search for the matrix directly.** The 50 columns as a set are a
      specific object. Try the integer sequence and the $[50,40]$ parameters
      against any saturating-set / covering-code databases that turn up in the
      searches above.
- [ ] **Email the authors** (draft below) with the matrix and the verifier
      **before** posting to arXiv or anywhere else. They maintain the table,
      they did the $p(H_{KR}) = 11$ computer search, and they are the people
      most likely to know in one reading whether a 50 already exists.

## Draft email

Send after the first six boxes, whatever they turn up — the authors' answer is
useful either way. Attach `data/H_r10_n50.txt`, `data/partition_p10.json`, and
a tarball of `verify/` and `run_all.sh`.

```text
To: alexander.davydov121@gmail.com
Cc: stefano.marcugini@unipg.it, fernanda.pambianco@unipg.it
Subject: A binary [50,40]_2 code of covering radius 2 — does this improve
         Table 5.1 row r=10 of arXiv:2511.02542?

Dear Professor Davydov, Professor Marcugini, Professor Pambianco,

I have what appears to be a binary [50,40]_2 code of covering radius 2,
i.e. l_2(10,2) <= 50, one below the Kaikkonen-Rosendahl [51,41]_2 2 code
that Table 5.1 of your paper "New upper bounds for binary linear covering
codes" (arXiv:2511.02542) lists for r = 10. Before doing anything further
with it I would like to ask whether this length is already known to you. Your
table is marked "best as far as the authors know", and the ACCT literature is
not something I can search exhaustively from outside.

The parity-check matrix is attached as 50 columns of F_2^10, written as
unsigned integers with bit i (least significant first) equal to row i+1:

  1 2 4 15 16 32 65 86 128 173 183 202 212 247 256 297 320 329 341 366
  373 381 391 403 438 460 479 491 502 559 576 608 653 734 742 754 771 777
  789 821 846 855 869 881 893 897 927 981 1003 1004

Verified facts, all by exhaustive enumeration over all 2^10 syndromes, from
the matrix text, by two independent programs in two languages:

  - F_2-rank 10; 50 distinct nonzero columns; minimum distance 3
  - {0} u S u (S+S) = F_2^10, i.e. 1024/1024 syndromes covered
  - covering radius exactly 2; covering density 319/256 = 1.24609375
    (against 1327/1024 = 1.29590 for H_KR)
  - deleting any single column leaves at least 9 syndromes uncovered, so the
    50-set is a minimal 1-saturating set in PG(9,2) — an LO code
  - exactly 10 linearly dependent triples

What may be of more interest than the single column: the matrix admits a
(2,0)-partition in the sense of your Definition 3.2 into p(H) = 10 subsets,
one fewer than the p(H_KR) = 11 you obtained by computer search in
Theorem 5.2. The blocks are

  {2,128,202,212,771,855,897,981}, {86}, {381,893,1003}, {183,297},
  {1,65,247,256,320,438,502,734}, {15,173,329,366,460,559,653,846},
  {4,16,391,491,742,754,869,881}, {479,1004}, {403},
  {32,341,373,576,608,777,789,821,927}.

Since your Theorem 5.7 family is seeded by C_KR at r = 10 — Phi(r) =
26*2^(r/2-4) - 1 is exactly 2^m(51+1) - 1 — substituting this code as C_0
appears to move the whole iteration. Condition (4.2) permits m = 4 and m = 5,
and I have applied Construction QM_2^2 directly and checked both results
exhaustively:

  r = 18, n = 815  (against Phi(18) = 831),  262144/262144,   density 1.26847
  r = 20, n = 1631 (against Phi(20) = 1663), 1048576/1048576, density 1.26924

Iterating gives n = 51*2^(r/2-5) - 1 for the reachable even r, with asymptotic
covering density 51^2/2^11 = 2601/2048 ~ 1.27002, against the 26^2/2^9 ~
1.32031 of your Theorem 5.7.

Two caveats I would rather state than have you find. First, only m = 4 and
m = 5 are exhaustively verified; everything beyond that inherits your
p(H_C) <= 2^(m+1) + 1 from (4.4) rather than computing partitions directly,
and I have not implemented the QM_3^2 and QM_5^2 analogues, so r = 22, 24, 26,
28, 42, 44 get no claim from this seed. (The r = 28 ingredient does seem to be
there: the columns 491, 734, 821 sum to zero and lie in three distinct blocks,
which is the analogue of your Theorem 5.2(ii).) Second, I make no optimality
claim — sphere-covering gives only l_2(10,2) >= 45.

For transparency: the matrix was found by simulated annealing seeded from
H_KR, run by an automated agent. The search method is not load-bearing — the
claim is a finite decidable statement about a fixed matrix, and the attached
verifiers re-derive every number above from the matrix text in about a second.

I would be grateful for a note on whether l_2(10,2) <= 50 is already in the
literature, particularly in the ACCT proceedings. If it is new and of interest
to you, I would be glad for you to use it however is most useful, including as
a corrigendum or extension to your own paper — I have no attachment to being
the one to publish it.

With thanks and best regards,
Stephen Wu
```

## Notes

- The claim to check is the *length*, not the matrix. Someone may have had a
  50-column example without publishing the matrix.
- The $p(H) = 10$ partition is a second, separable claim. Even if a 50 already
  exists, a 2-partition beating $p(H_{KR}) = 11$ may not.
- If any box turns up a prior $\ell_2(10,2) \le 50$: update `NOTE.md` §1 and §9,
  demote this to a re-verification with an independent witness and a smaller
  2-partition, and say so in the first paragraph rather than a footnote.
