/*
 * Census of Filaseta–Kalogirou Conjecture 1 (arXiv:2508.12242 §5).
 *
 * A runs over subsets of {0,1,...,n} containing 0 (2^n of them).
 * phi(A) is the difference *multiset* A-A, equivalently the histogram
 *   r[k] = #(A ∩ (A-k)) = popcount( bits & (bits >> k) ), k=1..n.
 * The conjecture: #im(phi) = 2^{n-1} + o(2^n).
 *
 * Reflection A |-> max(A)-A preserves r, and after translating to
 * contain 0 it stays inside the family. If every fibre is exactly
 * {A, A'} we would have #im = 2^{n-1} + (1/2)#symmetric.
 *
 * We count:
 *   images           = number of distinct histograms
 *   expected_pair    = 2^{n-1} + (number of A with A = A')/2
 *   extra_loss       = expected_pair - images
 *                    = how many extra identifications beyond reflection
 *
 * Hash table: 128-bit fingerprint of the histogram (splitmix of the
 * r[k] bytes) with linear probing. Collision of fingerprints is
 * rechecked only if we ever see a suspicious count; with 2^28 keys
 * and 128-bit hashes the expected number of hash collisions is ~2^{-72}.
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static inline uint64_t splitmix64(uint64_t x) {
    x += 0x9e3779b97f4a7c15ULL;
    x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
    x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}

static inline int pop64(uint64_t x) { return __builtin_popcountll(x); }

static inline uint64_t bit_reverse_low(uint64_t x, int width) {
    /* reverse the lowest `width` bits */
    uint64_t r = 0;
    for (int i = 0; i < width; i++) {
        if (x & (1ULL << i)) r |= 1ULL << (width - 1 - i);
    }
    return r;
}

typedef struct {
    uint64_t h0, h1;
    uint32_t count; /* number of A mapping here; 0 = empty slot */
} Slot;

static void fingerprint(const uint8_t *r, int n, uint64_t *h0, uint64_t *h1) {
    uint64_t a = 0x243f6a8885a308d3ULL, b = 0x13198a2e03707344ULL;
    for (int k = 1; k <= n; k++) {
        a ^= (uint64_t)r[k] + 0x9e3779b97f4a7c15ULL * (uint64_t)k;
        a = splitmix64(a);
        b ^= (uint64_t)r[k] * 0x100000001b3ULL + (uint64_t)k;
        b = splitmix64(b);
    }
    *h0 = a;
    *h1 = b;
}

static int insert(Slot *tab, uint64_t mask, int nslots, const uint8_t *r, int n) {
    uint64_t h0, h1;
    fingerprint(r, n, &h0, &h1);
    uint64_t i = h0 & (mask);
    for (;;) {
        if (tab[i].count == 0) {
            tab[i].h0 = h0;
            tab[i].h1 = h1;
            tab[i].count = 1;
            return 1; /* new image */
        }
        if (tab[i].h0 == h0 && tab[i].h1 == h1) {
            tab[i].count++;
            return 0; /* existing image */
        }
        i = (i + 1) & mask;
    }
}

int main(int argc, char **argv) {
    int nmin = 1, nmax = 24;
    if (argc >= 2) nmin = atoi(argv[1]);
    if (argc >= 3) nmax = atoi(argv[2]);
    if (nmin < 1) nmin = 1;
    if (nmax > 30) {
        fprintf(stderr, "nmax<=30 (bitmask in uint64)\n");
        return 1;
    }

    printf("# n  total  images  symmetric  expected_if_only_reflection  extra_loss  extra_frac\n");
    fflush(stdout);

    for (int n = nmin; n <= nmax; n++) {
        clock_t t0 = clock();
        uint64_t total = 1ULL << n; /* free bits 1..n; bit 0 fixed on */
        /* table size: power of two, ~ 2 * total */
        int logtab = n + 2;
        if (logtab < 10) logtab = 10;
        uint64_t nslots = 1ULL << logtab;
        uint64_t mask = nslots - 1;
        Slot *tab = calloc(nslots, sizeof(Slot));
        if (!tab) {
            fprintf(stderr, "alloc failed at n=%d (%llu slots)\n", n,
                    (unsigned long long)nslots);
            return 1;
        }

        uint64_t images = 0;
        uint64_t symmetric = 0;

        /* A is encoded in the low (n+1) bits, bit 0 always 1. */
        uint64_t nA = 1ULL << n;
        for (uint64_t free = 0; free < nA; free++) {
            uint64_t bits = 1ULL | (free << 1); /* bits 0..n */
            uint8_t r[32];
            for (int k = 1; k <= n; k++) {
                r[k] = (uint8_t)pop64(bits & (bits >> k));
            }
            images += (uint64_t)insert(tab, mask, (int)nslots, r, n);

            /* reflection through max(A) */
            int m = 63 - __builtin_clzll(bits); /* max element */
            uint64_t rev = bit_reverse_low(bits, m + 1);
            if (rev == bits) symmetric++;
        }

        /* expected images if fibres are exactly {A, A'} */
        /* #images_pair = symmetric + (total - symmetric)/2
         *              = total/2 + symmetric/2 */
        double expected = 0.5 * (double)total + 0.5 * (double)symmetric;
        double extra = expected - (double)images;
        double extra_frac = extra / (double)total;

        clock_t t1 = clock();
        double sec = (double)(t1 - t0) / (double)CLOCKS_PER_SEC;
        printf("%d  %llu  %llu  %llu  %.1f  %.1f  %.8g   (%.2fs)\n", n,
               (unsigned long long)total, (unsigned long long)images,
               (unsigned long long)symmetric, expected, extra, extra_frac,
               sec);
        fflush(stdout);
        free(tab);
    }
    return 0;
}
