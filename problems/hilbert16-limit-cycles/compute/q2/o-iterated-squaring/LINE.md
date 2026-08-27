# Line O — iterated non-separable pullback

Status: imagined, then work backwards.

Imagined certificate. k-fold pullback by the complex-squaring map
Φ(u,v) = (u² − v², 2uv) of the radial cubic of q1 line D
produces more than a quadratic number of hyperbolic cycles in the
final degree, beating Theorem 2 of arXiv:2604.12883 and answering
Remark 4.

Expected drop. Bézout caps each degree-2 step at 4 regular
sheets. After k steps, N = (n+1)2^k − 1 and the sheet count is
at most 4^k = ((N+1)/(n+1))², still quadratic. One-step
Chebyshev of degree 2^k matches that count.

Fork to keep. The factor m² remains optimal under iteration of
degree-2 maps, separable or not. Check: adj(DΦ) pullback
identity, degree bound, regular-sheet count for k = 1,2,3 on the
radial cubic (or a linear center), and the arithmetic
4^k vs ((N+1)/(n+1))². Not a new H(n). Do not cite
252/1080/1380/2012 as found here.

Replay: `./run.sh`
