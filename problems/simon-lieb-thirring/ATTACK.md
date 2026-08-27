# Attack log — simon-lieb-thirring

Chronological attempts, newest last.

## 2026-08-27 — mint and record

Opened Simon's 2000 reprint (Caltech r40.pdf; OCR of all seven pages)
and took #15 as printed: the Lieb–Thirring conjecture on L(γ,1) for
1/2 < γ < 3/2. Wikipedia's table was used only as a map.

Fetched the three papers named as the record:

- Frank–Hundertmark–Jex–Nam, arXiv:1808.09017, published as
  *J. Eur. Math. Soc.* 23 (2021), 2583–2600. Theorem 1:
  L(1,d)/Lcl(1,d) ≤ 1.456 for every d ≥ 1. The text also gives
  1.455786 from K1/Kcl ≥ 0.471851.
- Schimmer, arXiv:2203.06051. This id is Schimmer's Lieb
  90th-birthday survey, not a Frank paper. It still marks
  1/2 < γ < 3/2 in dimension 1 as open and still quotes 1.456
  for 1 ≤ γ < 3/2.
- Frank, arXiv:2007.09326. Same 1.456, same open interval.

Independently recomputed the classical Gamma formula
(Lcl(1,1) = 2/(3π), Lcl(3/2,1) = 3/16) and the one-bound-state
ratio 2/√3 ≈ 1.1547005. Evaluated the Pöschl–Teller sech² family
as a lower-bound witness: the ratios sit below 1.456, as they
must. That is a replay, not a new upper bound.

No attempt on the conjecture. The folder exists so a later run
has a cited number to beat.

Replay: `cd problems/simon-lieb-thirring/compute && sh run_all.sh`
