/* q11 -- local search for the best member of the fibered graph family.
 *
 * The family is  S = A x {0}  u  { (g(u),u) : u in W\{0} }  inside V (+) W,
 * dim V = F, dim W = M.  Writing tau(l) = g(a)+g(b)+g(a+b) for a line
 * l = {a,b,a+b} of PG(M-1,2) and C_u = { tau(l) : l ni u }, radius 2 is
 *
 *     A 1-saturating in V,   and   B := V \ (A u {0})  contained in  C_u
 *     for every point u of PG(M-1,2).
 *
 * So the family's best length at (F,M) is  n = 2^F-1-|B| + 2^M-1  with |B| the
 * largest k such that some g admits k nonzero colours common to every C_u.
 * This program maximises that directly: pick the k colours with the largest
 * point-count, cost = sum over them of (#points missing the colour), and
 * anneal over g.  Cost 0 is a covering (subject to A being 1-saturating,
 * which is checked and reported).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

static int F, M, NV, NW, P;
static int g[128];
static uint32_t Cu[128];
static int cnt[64];
static unsigned long long rs = 12345;
static inline unsigned long long xs(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }

static void recompute(void){
    for (int u = 1; u < NW; u++) Cu[u] = 0;
    for (int a = 1; a < NW; a++)
        for (int b = a+1; b < NW; b++){
            int c = a ^ b;
            if (c < b) continue;
            int t = g[a] ^ g[b] ^ g[c];
            Cu[a] |= 1u << t; Cu[b] |= 1u << t; Cu[c] |= 1u << t;
        }
    for (int v = 0; v < NV; v++) cnt[v] = 0;
    for (int u = 1; u < NW; u++)
        for (int v = 0; v < NV; v++) if (Cu[u] >> v & 1) cnt[v]++;
}

static uint32_t fixedB = 0; static int haveB = 0;

/* cost against a prescribed B (fiber-0 set A = V \ (B u {0}) fixed) */
static int costB(void){
    int c = 0;
    for (int v = 1; v < NV; v++) if (fixedB >> v & 1) c += P - cnt[v];
    return c;
}

static int cost(int k, int *chosen){
    int idx[64], m = 0;
    for (int v = 1; v < NV; v++) idx[m++] = v;
    for (int i = 0; i < m; i++)
        for (int j = i+1; j < m; j++)
            if (cnt[idx[j]] > cnt[idx[i]]){ int t=idx[i]; idx[i]=idx[j]; idx[j]=t; }
    int c = 0;
    for (int i = 0; i < k && i < m; i++){ c += P - cnt[idx[i]]; if (chosen) chosen[i] = idx[i]; }
    return c;
}

static int sat_ok(uint32_t A){
    uint32_t c = 1u | A;
    for (int a = 1; a < NV; a++) if (A >> a & 1)
        for (int b = a+1; b < NV; b++) if (A >> b & 1) c |= 1u << (a^b);
    uint32_t full = (NV==32)? 0xffffffffu : ((1u << NV) - 1);
    return c == full;
}

int main(int argc, char **argv){
    int k = 0; long long iters = 20000000; int tries = 1; unsigned long long seed = 1; uint32_t fixedA = 0;
    for (int i = 1; i < argc; i++){
        if (!strcmp(argv[i],"-F")) F = atoi(argv[++i]);
        else if (!strcmp(argv[i],"-M")) M = atoi(argv[++i]);
        else if (!strcmp(argv[i],"-k")) k = atoi(argv[++i]);
        else if (!strcmp(argv[i],"--iters")) iters = atoll(argv[++i]);
        else if (!strcmp(argv[i],"--tries")) tries = atoi(argv[++i]);
        else if (!strcmp(argv[i],"--seed")) seed = strtoull(argv[++i],0,10);
        else if (!strcmp(argv[i],"-A")) { uint32_t Am = (uint32_t)strtoul(argv[++i],0,16); haveB = 1; fixedA = Am; }
        else { fprintf(stderr,"bad arg %s\n", argv[i]); return 2; }
    }
    NV = 1 << F; NW = 1 << M; P = NW - 1;
    if (haveB){
        uint32_t full = (NV==32)? 0xfffffffeu : (((1u<<NV)-1) & ~1u);
        fixedB = full & ~fixedA;
        k = __builtin_popcount(fixedB);
        if (!sat_ok(fixedA)){ printf("BADA A=%08x not 1-saturating\n", fixedA); return 2; }
    }
    rs = seed * 6364136223846793005ULL + 1442695040888963407ULL;
    int best_overall = 1 << 30;
    for (int t = 0; t < tries; t++){
        for (int x = 1; x < NW; x++) g[x] = (int)(xs() % (unsigned)NV);
        recompute();
        int cur = haveB ? costB() : cost(k, NULL);
        int best = cur;
        double T0 = 3.0;
        for (long long it = 0; it < iters && cur > 0; it++){
            double T = T0 * (1.0 - (double)it / (double)iters) + 0.02;
            int x = 1 + (int)(xs() % (unsigned)(NW-1));
            int old = g[x];
            int nv = (int)(xs() % (unsigned)NV);
            if (nv == old) continue;
            g[x] = nv;
            recompute();
            int c = haveB ? costB() : cost(k, NULL);
            int d = c - cur;
            if (d <= 0 || (double)(xs() % 1000000ULL)/1000000.0 < exp(-d / T)) {
                cur = c;
                if (c < best) best = c;
            } else { g[x] = old; recompute(); }
        }
        if (cur < best_overall) best_overall = cur;
        if (cur == 0){
            int chosen[64];
            recompute();
            uint32_t full = (NV==32)? 0xfffffffeu : (((1u<<NV)-1) & ~1u);
            uint32_t Am;
            if (haveB) Am = fixedA;
            else {
                /* colours seen at every point; pick a k-subset whose complement
                   is 1-saturating, so that fibre 0 is covered too */
                int fl[64], nf = 0;
                for (int v = 1; v < NV; v++) if (cnt[v] == P) fl[nf++] = v;
                uint32_t Bm = 0; int got = 0;
                for (uint32_t sub = 0; sub < (1u << nf) && !got; sub++){
                    if (__builtin_popcount(sub) != k) continue;
                    uint32_t bb = 0;
                    for (int i = 0; i < nf; i++) if (sub >> i & 1) bb |= 1u << fl[i];
                    if (sat_ok(full & ~bb)){ Bm = bb; got = 1; }
                }
                if (!got){ uint32_t fm = 0; for (int i = 0; i < nf; i++) fm |= 1u << fl[i];
                    fprintf(stderr, "FULLSET %08x nf=%d (no k-subset has 1-saturating complement)\n", fm, nf); continue; }
                Am = full & ~Bm;
            }
            printf("SOLUTION A=%08x g=", Am);
            for (int x = 1; x < NW; x++) printf("%s%d", x>1?",":"", g[x]);
            printf("\n");
            printf("# k=%d |A|=%d n=%d saturating=%d\n", k, __builtin_popcount(Am),
                   __builtin_popcount(Am) + NW - 1, sat_ok(Am));
            fflush(stdout);
            if (sat_ok(Am)) return 0;
            continue;
        }
        fprintf(stderr, "try %d: best cost %d (k=%d)\n", t, best, k);
    }
    printf("NOSOLUTION F=%d M=%d k=%d bestcost=%d\n", F, M, k, best_overall);
    return 1;
}
