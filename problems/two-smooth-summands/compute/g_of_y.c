/* Exact G(y) bitset cover. Independent of the Python path.
 *
 *   cc -O3 -std=c11 -o g_of_y_c g_of_y.c
 *   ./g_of_y_c 73 131486759
 *
 * Prints first uncovered n in 2..limit and whether `limit` itself
 * is a sum of two y-smooth numbers. A hole-free prefix is residue.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void die(const char *msg) {
    fprintf(stderr, "%s\n", msg);
    exit(1);
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "usage: %s y limit [small_bound]\n", argv[0]);
        return 2;
    }
    const int y = atoi(argv[1]);
    const uint64_t limit = strtoull(argv[2], NULL, 10);
    uint64_t small_bound = (argc >= 4) ? strtoull(argv[3], NULL, 10)
                                       : (limit / 20);
    if (small_bound < 10000) small_bound = 10000;
    if (small_bound > limit) small_bound = limit;

    /* primes <= y */
    int *isprime = calloc((size_t)y + 1, sizeof(int));
    if (!isprime) die("oom primes");
    int nprimes = 0;
    for (int i = 2; i <= y; i++) isprime[i] = 1;
    for (int i = 2; i * i <= y; i++)
        if (isprime[i])
            for (int j = i * i; j <= y; j += i) isprime[j] = 0;
    for (int i = 2; i <= y; i++)
        if (isprime[i]) nprimes++;
    int *primes = malloc((size_t)nprimes * sizeof(int));
    if (!primes) die("oom plist");
    nprimes = 0;
    for (int i = 2; i <= y; i++)
        if (isprime[i]) primes[nprimes++] = i;
    free(isprime);

    const uint64_t nwords = (limit >> 6) + 1;
    uint64_t *src = calloc(nwords, sizeof(uint64_t));
    uint64_t *dst = calloc(nwords, sizeof(uint64_t));
    if (!src || !dst) die("oom bitset");

    /* DFS generate y-smooth numbers, set bits, collect small list. */
    uint64_t *small = malloc((size_t)(small_bound + 1) * sizeof(uint64_t));
    if (!small) die("oom small");
    uint64_t nsmall = 0;
    uint64_t nsmooth = 0;

    typedef struct {
        int pi;
        uint64_t v;
    } Fr;
    size_t cap = 1 << 20;
    Fr *st = malloc(cap * sizeof(Fr));
    if (!st) die("oom stack");
    size_t sp = 0;
    st[sp++] = (Fr){0, 1};
    while (sp) {
        Fr cur = st[--sp];
        /* record cur.v */
        nsmooth++;
        src[cur.v >> 6] |= 1ull << (cur.v & 63);
        if (cur.v >= 1 && cur.v <= small_bound) small[nsmall++] = cur.v;
        for (int j = cur.pi; j < nprimes; j++) {
            uint64_t p = (uint64_t)primes[j];
            if (cur.v > limit / p) break;
            uint64_t nv = cur.v * p;
            while (nv <= limit) {
                if (sp >= cap) {
                    cap *= 2;
                    st = realloc(st, cap * sizeof(Fr));
                    if (!st) die("oom stack grow");
                }
                st[sp++] = (Fr){j + 1, nv};
                if (nv > limit / p) break;
                nv *= p;
            }
        }
    }
    free(st);
    free(primes);

    /* Shift-OR by each small summand. */
    for (uint64_t t = 0; t < nsmall; t++) {
        uint64_t a = small[t];
        uint64_t aw = a >> 6, ab = a & 63;
        if (ab == 0) {
            for (uint64_t i = 0; i + aw < nwords; i++) dst[i + aw] |= src[i];
        } else {
            for (uint64_t i = 0; i + aw < nwords; i++) {
                dst[i + aw] |= (src[i] << ab);
                if (i + aw + 1 < nwords) dst[i + aw + 1] |= (src[i] >> (64 - ab));
            }
        }
    }
    /* mask bits > limit */
    {
        int extra = (int)((nwords << 6) - 1 - limit);
        if (extra > 0) dst[nwords - 1] &= (~0ull) >> extra;
    }

    uint64_t first = 0;
    for (uint64_t n = 2; n <= limit; n++) {
        if (((dst[n >> 6] >> (n & 63)) & 1ull) == 0) {
            first = n;
            break;
        }
    }

    /* two-pointer on all smooth <= limit against `limit` itself */
    /* Rebuild sorted smooth list from src bits. */
    uint64_t *S = malloc((size_t)nsmooth * sizeof(uint64_t));
    if (!S) die("oom S");
    uint64_t ns = 0;
    for (uint64_t n = 1; n <= limit; n++) {
        if ((src[n >> 6] >> (n & 63)) & 1ull) S[ns++] = n;
    }
    int limit_is_sum = 0;
    uint64_t i = 0, j = ns ? ns - 1 : 0;
    while (ns && i <= j) {
        uint64_t s = S[i] + S[j];
        if (s == limit) {
            limit_is_sum = 1;
            break;
        }
        if (s < limit) i++;
        else j--;
    }

    printf("y=%d limit=%llu small_bound=%llu nsmooth=%llu nsmall=%llu\n",
           y, (unsigned long long)limit, (unsigned long long)small_bound,
           (unsigned long long)nsmooth, (unsigned long long)nsmall);
    printf("first_uncovered=%llu\n", (unsigned long long)first);
    printf("limit_is_sum=%d\n", limit_is_sum);
    printf("G_equals_limit=%d\n", first == limit && !limit_is_sum);

    free(small);
    free(S);
    free(src);
    free(dst);
    return 0;
}
