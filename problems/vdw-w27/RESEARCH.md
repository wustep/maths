# Research log — W(2,7)

URLs actually opened.

- [OEIS A005346, text format](https://oeis.org/search?q=id:A005346&fmt=text) — exact values \(1,3,9,35,178,1132\). \(W(2,7)\) is not listed. Sequence last edited 2026-06-28.
- [OEIS A005346 /list](https://oeis.org/A005346/list) — Cloudflare interstitial; no extra terms.
- [Wikipedia, Van der Waerden number](https://en.wikipedia.org/wiki/Van_der_Waerden_number) — table still has \(W(2,7)>3703\), citing Rabung–Lotts.
- [Leaps in Bounds, \(W(2,7)\)](https://leapsinbounds.org/constants/van-der-waerden-2-7/) — lower bound recorded as \(3704\) (i.e. a coloring of \(3703\)), update 2012-06-06.
- [Herwig, Heule, van Lambalgen, van Maaren, E-JC 14 (2007) #R6](https://doi.org/10.37236/925) — cyclic zipper; \(W(2,7)\) from prime \(617\), \(0\) zips, bound \(>3703\).
- [Heule PDF copy of the same paper](https://www.cs.utexas.edu/~marijn/publications/waerden.pdf)
- [Rabung and Lotts, E-JC 19(2) (2012) #P35](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v19i2p35) — faster zip check; primes to \(10^7\); \(W(2,7)\) not improved.
- [Rabung–Lotts PDF](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v19i2p35/pdf)
- [DOI 10.37236/2363](https://doi.org/10.37236/2363) — same paper via DOI.
- [marijnheule/vdWaerden](https://github.com/marijnheule/vdWaerden) — SAT encoder and published certificates, including `certificates/W_2_7_617.cert` (3703 bytes). Used as a format/length check, not copied as a dent.
- [Heule README](https://raw.githubusercontent.com/marijnheule/vdWaerden/master/README.md)
- [Heule `vdW-encode.c`](https://raw.githubusercontent.com/marijnheule/vdWaerden/d18a9106ba9b720b18fd8d92946cf8b67746eab6/vdW-encode.c)
- [Heule `check-cert.c`](https://raw.githubusercontent.com/marijnheule/vdWaerden/d18a9106ba9b720b18fd8d92946cf8b67746eab6/check-cert.c)
- [Heule `W_2_7_617.cert`](https://raw.githubusercontent.com/marijnheule/vdWaerden/d18a9106ba9b720b18fd8d92946cf8b67746eab6/certificates/W_2_7_617.cert)
- [Erdős problems #138](https://www.erdosproblems.com/138) — fetch timed out.
- [Dransfield–Liu–Marek–Truszczyński SAT paper](https://cs.uky.edu/~marek/papers.dir/vdw.pdf) — early SAT lower bounds, not a \(W(2,7)\) coloring of length \(\ge 3704\).
- [Kouril–Paul, \(W(2,6)=1132\)](https://www.cs.umd.edu/~gasarch/TOPICS/vdw/1132.pdf) — notes that the same preprocessing does not shrink \(W(2,7)\).

No later accepted improvement of the \(3703\) coloring was found in these sources.
