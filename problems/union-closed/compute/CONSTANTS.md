# Independently recomputed constants

All logs base 2.  Replay: `python solve_published.py`, `python verify.py`, `q1/run_all.sh`, and `q2/run_all.sh`.

| symbol | value | source |
| --- | ---: | --- |
| φ = (3−√5)/2 | 0.3819660112501051518 | Gilmer / AHS / Chase–Lovett, sharp for iid |
| c* | 0.3823455333667027211 | Yu–Cambie / Sawin mix; larger root of h(b)(2−h(b))=h((1−b)²), a=1−h(b)/h((1−b)²), c*=a+(1−a)b |
| b* | 0.32945473850303697 | that larger root |
| a* | 0.07887729270592317 | |
| c₅ (Liu) | 0.38270908791873503 | Example 5 2-point; x²+x²(1+x̄²)=1, p=h(x)/h(x²), c=1−px |
| x* | 0.690787593924988 | |
| p* | 0.8936045139054655 | |
| c₄^{ray}(β=1/5) | 0.38289680852720065 | 2026-08-17: first mean on {b,1} with iid+Example-4 ratio < 1 |
| claimed c (2026-08-17) | 0.38285 | below the β=1/5 mesh crossing, min ratio 1.000077 on 5.1M cells |
| c₄^{ray}(β=1) | 0.38305135658682558 | 2026-08-27: unique critical point of 1−(1−b)h(b); h(b)=(1−b)log₂((1−b)/b) |
| claimed c | **0.38304** | 2026-08-27: below the analytic crossing, min ratio 1.000021687 on 5.1M cells (Python and C) |
| 2-sample ceiling on {b,1} | 0.38305135658682558 | q2: any bit protocol, product coupling; `h(Π_{b,b})≤1` |
| 2-mixture witness ratio | 0.9091371378730101 | q2: `{b*,1}` at mean 0.45 mixed with `δ_{0.01}`; not a ray dent |
| q3 claimed c | **0.38305** | 2026-08-27: 9,000×7,000 mesh; min ratio 1.0000049143029008 on 20,440,358 retained cells; Python and C agree |

Deltas versus the published quotes are < 10⁻¹⁴ (Liu, Cambie). q2 left
the printed constant unchanged; q3 moves it from 0.38304 to 0.38305.
