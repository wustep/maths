# Constants

| quantity | value | source |
| --- | --- | --- |
| conjectured out-degree threshold | $1/3$ | Caccetta–Häggkvist 1978 |
| published unrestricted threshold (refereed) | $0.3465$ | Hladký–Král'–Norin, *Combinatorica* 37 (2017) |
| claimed F₆ threshold | $0.3388$ | de Joannis de Verclos–Sereni–Volec, Mar 2014, **personal communication** |
| two-sided threshold | $0.343545$ | Lichiardopol 2010 (both $\delta^+$ and $\delta^-$) |
| Shen elementary | $3-\sqrt{7}\approx 0.354249$ | Shen, JCTB 74 (1998) |
| HHK | $0.3532$ | Hamburger–Haxell–Kostochka, *Electron. J. Combin.* 2007 |
| tonight, same F₄ system | $0.34645$ | `certs/f4_certificate.json`, worst $F=-0.12343$ |
| tonight, F₄ plus CKLS 2015 fork | $0.34640$ | `q4/certs/keep/f4_or_new_certificate.json`, worst $F=-0.41903$ |
| F₄ SDP saturation (this system) | $\approx 0.346439$ | `certs/sdp_bound.json` |

Cyclic construction: out-set $\{1,\ldots,\lfloor(n-1)/3\rfloor\}$ on $\mathbb{Z}/n$, C₃-free.

Exact finite statement: every $n$-vertex oriented graph with $\delta^+\ge\lceil n/3\rceil$ has a directed triangle.

First $n$ not implied by Hoàng–Reed ($r\le 5$) plus HKN $0.3465$ was $n=18$. That order, and the later holes $n=21,24,26,27,29,30,32,33,35,36$, now have stored in-degree-cube DRATs.

Exact orders with stored in-degree-cube DRATs now include every leftover hole through $n=139$.

First remaining hole: **$n=140$, $\delta^+=47$**.
