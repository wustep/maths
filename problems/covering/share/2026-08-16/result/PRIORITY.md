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
- [ ] **Email the authors** with the matrix and the verifier
      **before** posting to arXiv or anywhere else. They maintain the table,
      they did the $p(H_{KR}) = 11$ computer search, and they are the people
      most likely to know in one reading whether a 50 already exists.


## Notes

- The claim to check is the *length*, not the matrix. Someone may have had a
  50-column example without publishing the matrix.
- The $p(H) = 10$ partition is a second, separable claim. Even if a 50 already
  exists, a 2-partition beating $p(H_{KR}) = 11$ may not.
- If any box turns up a prior $\ell_2(10,2) \le 50$: update `NOTE.md` §1 and §9,
  demote this to a re-verification with an independent witness and a smaller
  2-partition, and say so in the first paragraph rather than a footnote.
