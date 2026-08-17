# Independently recomputed constants

All logs base 2.  Replay: `python solve_published.py` and `python verify.py`.

| symbol | value | source |
| --- | ---: | --- |
| φ = (3−√5)/2 | 0.3819660112501051518 | Gilmer / AHS / Chase–Lovett, sharp for iid |
| c* | 0.3823455333667027211 | Yu–Cambie / Sawin mix; larger root of h(b)(2−h(b))=h((1−b)²), a=1−h(b)/h((1−b)²), c*=a+(1−a)b |
| b* | 0.32945473850303697 | that larger root |
| a* | 0.07887729270592317 | |
| c₅ (Liu) | 0.38270908791873503 | Example 5 2-point; x²+x²(1+x̄²)=1, p=h(x)/h(x²), c=1−px |
| x* | 0.690787593924988 | |
| p* | 0.8936045139054655 | |
| c₄^{ray}(β=1/5) | 0.38289680852720065 | tonight: first mean on {b,1} with iid+Example-4 ratio < 1 |
| claimed c | **0.38285** | tonight: below the mesh crossing, min ratio 1.000077 on 5.1M cells |

Deltas versus the published quotes are < 10⁻¹⁴ (Liu, Cambie).
