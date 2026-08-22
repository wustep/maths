/* q11 -- exact search for the fibered "graph plus kernel" family.
 *
 * F_2^r = V (+) W, dim V = F (the fiber), dim W = M (the base), r = F+M.
 * The candidate column set is
 *
 *     S = { (v,0) : v in A }  u  { (g(u),u) : u in W\{0} },   A subset of V\{0},
 *
 * so n = |A| + 2^M - 1.  Radius 2 is equivalent to
 *
 *   fiber 0 : {0} u A u (A+A) = V                       (A is 1-saturating in V)
 *   fiber u : B + g(u) subset of D_u  for every u != 0,
 *
 * where B = V \ (A u {0}) and D_u = { g(w)+g(w+u) : w in W\{0,u} }.
 *
 * D_u has at most 2^{M-1}-1 elements, so the whole family is decided by a DFS
 * over g with a per-fiber slack budget.  A shear (v,u) -> (v+K(u),u) with K
 * linear preserves the family and fixes A, so g may be normalised to vanish on
 * a basis of W; that is done here (g[2^i] = 0).
 *
 * Exit status / output: prints SOLUTION lines for every g found (or the first
 * one with --first), and a final EXHAUSTED or FOUND summary.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int F, M, NV, NW, PAIRS;
static uint32_t Bmask, Amask;
static uint32_t Bshift[64];      /* Bshift[v] = { b^v : b in B } as a bitmask */
static int g[64];
static uint32_t cov[64];
static int remp[64];
static uint32_t target[64];
static int strong = 0, firstonly = 0, quiet = 0, Bsize = 0, restarts = 1;
static long long nodes = 0, solutions = 0;
static long long nodecap = 0;
static int vorder[64][64]; static int randomize = 0; static unsigned long long rstate = 88172645463325252ULL;
static int capped = 0;

static inline int pc(uint32_t x){ return __builtin_popcount(x); }

static inline unsigned long long xs(void){
    rstate ^= rstate << 13; rstate ^= rstate >> 7; rstate ^= rstate << 17; return rstate;
}
static void shuffle_orders(void){
    for (int x = 0; x < NW; x++){
        for (int v = 0; v < NV; v++) vorder[x][v] = v;
        if (!randomize) continue;
        for (int v = NV-1; v > 0; v--){
            int j = (int)(xs() % (unsigned)(v+1));
            int t = vorder[x][v]; vorder[x][v] = vorder[x][j]; vorder[x][j] = t;
        }
    }
}

static int is_pow2(int x){ return (x & (x-1)) == 0; }

/* minimal number of still-needed targets over all possible values of g(u) */
static inline int min_needed(uint32_t c){
    int best = 64;
    for (int v = 0; v < NV; v++){
        int k = pc(Bshift[v] & ~c);
        if (k < best) best = k;
    }
    return best;
}

static void emit(void){
    solutions++;
    printf("SOLUTION A=%08x g=", Amask);
    for (int x = 1; x < NW; x++) printf("%s%d", x>1?",":"", g[x]);
    printf("\n");
    fflush(stdout);
}

static void dfs(int x){
    if (nodecap && nodes > nodecap){ capped = 1; return; }
    if (x == NW){ emit(); return; }
    nodes++;
    int lo = 0, hi = NV;
    if (is_pow2(x)) hi = 1;                 /* shear normalisation: g[2^i]=0 */
    for (int vi = lo; vi < hi; vi++){
        int v = vorder[x][vi];
        g[x] = v;
        target[x] = Bshift[v];
        int ok = 1;
        int touched[64], nt = 0;
        uint32_t oldcov[64];
        for (int w = 1; w < x; w++){
            int u = x ^ w;
            int s = v ^ g[w];
            oldcov[nt] = cov[u];
            cov[u] |= (uint32_t)1 << s;
            remp[u]--;
            touched[nt++] = u;
        }
        /* fiber x itself */
        if (pc(target[x] & ~cov[x]) > remp[x]) ok = 0;
        if (ok) for (int i = 0; i < nt && ok; i++){
            int u = touched[i];
            if (u < x){ if (pc(target[u] & ~cov[u]) > remp[u]) ok = 0; }
            else if (u > x && strong && remp[u] < Bsize){ if (min_needed(cov[u]) > remp[u]) ok = 0; }
        }
        if (ok) dfs(x+1);
        for (int i = nt-1; i >= 0; i--){ int u = touched[i]; remp[u]++; cov[u] = oldcov[i]; }
        if (firstonly && solutions) return;
        if (capped) return;
    }
    g[x] = -1;
}

/* A is 1-saturating in V ? */
static int sat_ok(uint32_t A){
    uint32_t c = 1u | A;
    for (int a = 1; a < NV; a++) if (A >> a & 1)
        for (int b = a+1; b < NV; b++) if (A >> b & 1) c |= (uint32_t)1 << (a^b);
    uint32_t full = (NV == 32) ? 0xffffffffu : (((uint32_t)1 << NV) - 1);
    return c == full;
}

int main(int argc, char **argv){
    int a = -1; uint32_t Afix = 0; int haveA = 0;
    const char *alist = NULL;
    for (int i = 1; i < argc; i++){
        if (!strcmp(argv[i],"-F")) F = atoi(argv[++i]);
        else if (!strcmp(argv[i],"-M")) M = atoi(argv[++i]);
        else if (!strcmp(argv[i],"-a")) a = atoi(argv[++i]);
        else if (!strcmp(argv[i],"-A")) { Afix = (uint32_t)strtoul(argv[++i],0,16); haveA = 1; }
        else if (!strcmp(argv[i],"--alist")) alist = argv[++i];
        else if (!strcmp(argv[i],"--strong")) strong = 1;
        else if (!strcmp(argv[i],"--first")) firstonly = 1;
        else if (!strcmp(argv[i],"--quiet")) quiet = 1;
        else if (!strcmp(argv[i],"--nodes")) nodecap = atoll(argv[++i]);
        else if (!strcmp(argv[i],"--rand")) { randomize = 1; rstate = strtoull(argv[++i],0,10) * 2862933555777941757ULL + 3037000493ULL; }
        else if (!strcmp(argv[i],"--restarts")) restarts = atoi(argv[++i]);
        else { fprintf(stderr,"bad arg %s\n", argv[i]); return 2; }
    }
    if (F <= 0 || M <= 0){ fprintf(stderr,"need -F and -M\n"); return 2; }
    NV = 1 << F; NW = 1 << M; PAIRS = (NW - 2) / 2;

    uint32_t *As = NULL; long nA = 0, capA = 0;
    if (haveA){ As = malloc(sizeof(uint32_t)); As[0] = Afix; nA = 1; }
    else if (alist){
        FILE *f = fopen(alist,"r"); if(!f){perror(alist);return 2;}
        char line[256];
        while (fgets(line,sizeof line,f)){
            if (line[0]=='#'||line[0]=='\n') continue;
            if (nA == capA){ capA = capA? capA*2 : 1024; As = realloc(As, capA*sizeof(uint32_t)); }
            As[nA++] = (uint32_t)strtoul(line,0,16);
        }
        fclose(f);
    } else {
        if (a < 0){ fprintf(stderr,"need -a or -A or --alist\n"); return 2; }
        /* all a-subsets of V\{0} */
        uint32_t full = (NV==32)? 0xfffffffeu : ((((uint32_t)1<<NV)-1) & ~1u);
        for (uint32_t s = 0; s < (uint32_t)(1u<<NV) ; s++){
            if (s & 1) continue;
            if (pc(s) != a) continue;
            if ((s & ~full)) continue;
            if (nA == capA){ capA = capA? capA*2 : 1024; As = realloc(As, capA*sizeof(uint32_t)); }
            As[nA++] = s;
            if (NV > 24) break; /* guard: never enumerate blindly at F=5 */
        }
    }

    long long tot_nodes = 0; long long tot_sol = 0; long nsat = 0;
    long ndecided = 0, ncapped = 0;
    for (long ai = 0; ai < nA; ai++){
        Amask = As[ai];
        if (pc(Amask) == 0) continue;
        if (!sat_ok(Amask)) continue;
        nsat++;
        uint32_t full = (NV == 32) ? 0xffffffffu : (((uint32_t)1 << NV) - 1);
        Bmask = full & ~Amask & ~1u; Bsize = pc(Bmask);
        for (int v = 0; v < NV; v++){
            uint32_t t = 0;
            for (int b = 0; b < NV; b++) if (Bmask >> b & 1) t |= (uint32_t)1 << (b ^ v);
            Bshift[v] = t;
        }
        for (int u = 0; u < NW; u++){ cov[u] = 0; remp[u] = PAIRS; target[u] = 0; }
        for (int x = 0; x < NW; x++) g[x] = -1;
        nodes = 0; solutions = 0; capped = 0;
        for (int rr = 0; rr < restarts; rr++){
            shuffle_orders();
            nodes = 0; capped = 0;
            dfs(1);
            if (solutions) break;
            if (!capped) break;   /* exhausted this A with the current order */
        }
        tot_nodes += nodes; tot_sol += solutions;
        if (capped) ncapped++; else ndecided++;
        if (!quiet) fprintf(stderr,"A=%08x |A|=%d nodes=%lld sol=%lld%s\n",
                            Amask, pc(Amask), nodes, solutions, capped?" CAPPED":"");
        if (firstonly && tot_sol) break;
    }
    printf("SUMMARY F=%d M=%d Asets=%ld saturating=%ld decided=%ld capped=%ld nodes=%lld solutions=%lld %s\n",
           F, M, nA, nsat, ndecided, ncapped, tot_nodes, tot_sol,
           tot_sol? "FOUND" : (ncapped? "PARTIAL" : "EXHAUSTED"));
    return 0;
}
