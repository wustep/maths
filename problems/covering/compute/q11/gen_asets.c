/* Complete GL(F,2)-reduced list of A-masks for the q11 graph family.
 *
 * The family depends on A only through B = V \ (A u {0}), and GL(V) acts on
 * the whole family, so one A per GL(F,2)-orbit of B suffices.  Reduction
 * (rigorous; possibly more than one representative per orbit):
 *   rank(B) = F  ->  B may be assumed to contain e_1..e_F, and to be
 *                    lexicographically minimal under the coordinate
 *                    permutations S_F (which stabilise {e_1..e_F});
 *   rank(B) = d < F -> B may be assumed to lie in <e_1..e_d>.
 * Prints hex A-masks, one per line.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int F, NV, b;
static int perm[128][32], nperm;

static void gen_perms(void){
    int idx[8]; for (int i=0;i<F;i++) idx[i]=i;
    int c[8]; for (int i=0;i<F;i++) c[i]=0;
    nperm = 0;
    /* Heap's algorithm */
    int p[8]; memcpy(p, idx, sizeof p);
    for (int v=0; v<NV; v++){ int w=0; for(int i=0;i<F;i++) if(v>>i&1) w|=1<<p[i]; perm[nperm][v]=w; }
    nperm++;
    int i = 0;
    while (i < F){
        if (c[i] < i){
            int j = (i % 2 == 0) ? 0 : c[i];
            int t = p[j]; p[j] = p[i]; p[i] = t;
            for (int v=0; v<NV; v++){ int w=0; for(int k=0;k<F;k++) if(v>>k&1) w|=1<<p[k]; perm[nperm][v]=w; }
            nperm++;
            c[i]++; i = 0;
        } else { c[i] = 0; i++; }
    }
}

static int rankof(int *vs, int k){
    int bs[8], nb = 0;
    for (int i = 0; i < k; i++){
        int c = vs[i];
        for (int j = 0; j < nb; j++) if ((c ^ bs[j]) < c) c ^= bs[j];
        if (c){ bs[nb++] = c; for (int j=nb-1;j>0 && bs[j]>bs[j-1];j--){int t=bs[j];bs[j]=bs[j-1];bs[j-1]=t;} }
    }
    return nb;
}

int main(int argc, char **argv){
    F = atoi(argv[1]); int a = atoi(argv[2]);
    NV = 1 << F; b = NV - 1 - a;
    gen_perms();
    uint32_t full = (NV==32)? 0xfffffffeu : ((((uint32_t)1<<NV)-1) & ~1u);
    int rest[64], nrest = 0;
    for (int v = 1; v < NV; v++){ int isb=0; for(int i=0;i<F;i++) if(v==(1<<i)) isb=1; if(!isb) rest[nrest++]=v; }
    long count = 0;
    if (b >= F){
        int k = b - F;
        int idx[64];
        for (int i = 0; i < k; i++) idx[i] = i;
        while (1){
            int B[64]; int nb = 0;
            for (int i = 0; i < F; i++) B[nb++] = 1 << i;
            for (int i = 0; i < k; i++) B[nb++] = rest[idx[i]];
            uint32_t m = 0; for (int i=0;i<nb;i++) m |= (uint32_t)1 << B[i];
            uint32_t best = m;
            for (int pi = 1; pi < nperm; pi++){
                uint32_t mm = 0;
                for (int i = 0; i < nb; i++) mm |= (uint32_t)1 << perm[pi][B[i]];
                if (mm < best) best = mm;
            }
            if (best == m){ printf("%08x\n", full & ~m); count++; }
            if (k == 0) break;
            int i = k - 1;
            while (i >= 0 && idx[i] == nrest - k + i) i--;
            if (i < 0) break;
            idx[i]++;
            for (int j = i + 1; j < k; j++) idx[j] = idx[j-1] + 1;
        }
    }
    for (int d = 1; d < F; d++){
        int np = (1 << d) - 1;
        if (b > np) continue;
        int idx[64];
        for (int i = 0; i < b; i++) idx[i] = i;
        while (1){
            int B[64];
            for (int i = 0; i < b; i++) B[i] = idx[i] + 1;
            if (rankof(B, b) == d){
                uint32_t m = 0; for (int i=0;i<b;i++) m |= (uint32_t)1 << B[i];
                printf("%08x\n", full & ~m); count++;
            }
            int i = b - 1;
            while (i >= 0 && idx[i] == np - b + i) i--;
            if (i < 0) break;
            idx[i]++;
            for (int j = i + 1; j < b; j++) idx[j] = idx[j-1] + 1;
        }
    }
    fprintf(stderr, "generated %ld A-masks (F=%d a=%d |B|=%d)\n", count, F, a, b);
    return 0;
}
