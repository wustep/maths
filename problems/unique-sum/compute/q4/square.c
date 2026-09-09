/* Enumerate normalized seeds C with |C| <= MAX_SEED and test A=C+C.
 * This is a construction search in a restricted family, not a lower search
 * for arbitrary A. Adding seed elements cannot shrink the sumset.
 * gcc -O3 -std=c11 -Wall -Wextra -Werror square.c -o square
 * Usage: square PRIME MAX_SEED MAX_SUMSET
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
typedef __uint128_t mask_t;
static int p, max_seed, cap, seed[64], best[128], best_n, best_seed[64], best_c;
static uint64_t nodes, tested;
static int pop(mask_t x) { return __builtin_popcountll((uint64_t)x) + __builtin_popcountll((uint64_t)(x >> 64)); }
static int values(mask_t mask, int *out) {
    int count=0;
    for(int i=0;i<p;++i) if(mask & ((mask_t)1 << i)) out[count++]=i;
    return count;
}
static int valid(mask_t mask) {
    int a[128], count[128]={0}, n=values(mask,a);
    for(int i=0;i<n;++i) for(int j=i;j<n;++j) ++count[(a[i]+a[j])%p];
    for(int s=0;s<p;++s) if(count[s]==1) return 0;
    return 1;
}
static void search(int n, int next, mask_t sums) {
    ++nodes;
    int size=pop(sums);
    if(size>cap) return;
    ++tested;
    if(valid(sums)) {
        best_n=values(sums,best); best_c=n;
        for(int i=0;i<n;++i) best_seed[i]=seed[i];
        fprintf(stderr,"found cardinality=%d seed_size=%d nodes=%llu\n",best_n,n,(unsigned long long)nodes);
        cap=best_n-1;
        return;
    }
    if(n==max_seed) return;
    for(int x=next;x<p;++x) {
        mask_t expanded=sums | ((mask_t)1 << ((2*x)%p));
        for(int i=0;i<n;++i) expanded |= (mask_t)1 << ((seed[i]+x)%p);
        seed[n]=x; search(n+1,x+1,expanded);
    }
}
int main(int argc,char **argv) {
    if(argc!=4) { fprintf(stderr,"usage: %s PRIME MAX_SEED MAX_SUMSET\n",argv[0]); return 2; }
    p=atoi(argv[1]);max_seed=atoi(argv[2]);cap=atoi(argv[3]);int initial_cap=cap;
    if(p<3 || p>=128 || max_seed<2 || max_seed>p || max_seed>64 || cap<2) return 2;
    for(int d=2;d*d<=p;++d) if(p%d==0) return 2;
    seed[0]=0;seed[1]=1;clock_t started=clock();search(2,2,7);
    printf("{\"status\":\"%s\",\"scope\":\"normalized symmetric-square seeds only\",\"p\":%d,\"max_seed\":%d,\"initial_sumset_cap\":%d,\"nodes\":%llu,\"tested\":%llu,\"cpu_seconds\":%.6f,\"witness\":[",best_n?"SAT":"UNSAT",p,max_seed,initial_cap,(unsigned long long)nodes,(unsigned long long)tested,(double)(clock()-started)/CLOCKS_PER_SEC);
    for(int i=0;i<best_n;++i) printf("%s%d",i?",":"",best[i]);
    printf("],\"seed\":[");for(int i=0;i<best_c;++i)printf("%s%d",i?",":"",best_seed[i]);puts("]}");
    return 0;
}
