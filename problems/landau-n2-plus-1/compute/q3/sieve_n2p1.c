/*
 * Residue factor-sieve for n^2+1: primes and Iwaniec P2 composites.
 *
 * Same algorithm as compute/sieve_n2p1.py. Even n (and n=1) only.
 * For every prime q ≡ 1 (mod 4), q <= n_max, divide n^2+1 on the two
 * progressions n ≡ ±sqrt(-1) (mod q). Leftovers have all prime factors
 * > n_max, so each leftover is 1, a prime, or a product of two primes.
 *
 * Deterministic Miller–Rabin bases 2,3,5,7,11,13,17,19,23 (OEIS A014233),
 * sufficient for n^2+1 with n <= 10^9.
 *
 * Build: gcc -O3 -std=c11 -Wall -Wextra sieve_n2p1.c -o sieve_n2p1
 * Run:   ./sieve_n2p1 --self-test
 *        ./sieve_n2p1 10000000 /path/to/outdir
 *
 * RAM: segmented leftover arrays (default 5e6 even n per strip:
 * about 50 MB) plus the prime list and precomputed sqrt(-1) values
 * (~50 MB at n_max=1e8). One-shot leftover storage at n_max=1e8
 * would be ~500 MB; strips keep the resident set well under 200 MB.
 */
#define _POSIX_C_SOURCE 200809L

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static const uint64_t MR_WITNESSES[] = {2, 3, 5, 7, 11, 13, 17, 19, 23};
static const int N_MR = 9;
static const uint64_t MR_BOUND = UINT64_C(3825123056546413051);
/* Even-n leftover strip. 5e6 * 10 bytes = 50 MB plus two uint8 counters. */
#ifndef SEG_EVENS
#define SEG_EVENS 5000000u
#endif

static double now_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_nsec * 1e-9 + (double)ts.tv_sec;
}

static long rss_kb(void) {
    FILE *f = fopen("/proc/self/status", "r");
    if (!f)
        return -1;
    char line[256];
    long kb = -1;
    while (fgets(line, sizeof line, f)) {
        if (sscanf(line, "VmRSS: %ld kB", &kb) == 1)
            break;
    }
    fclose(f);
    return kb;
}

static uint64_t mulmod(uint64_t a, uint64_t b, uint64_t m) {
    return (uint64_t)((__uint128_t)a * b % m);
}

static uint64_t modpow(uint64_t a, uint64_t e, uint64_t m) {
    uint64_t r = 1;
    a %= m;
    while (e) {
        if (e & 1)
            r = mulmod(r, a, m);
        a = mulmod(a, a, m);
        e >>= 1;
    }
    return r;
}

static uint64_t gcd_u64(uint64_t a, uint64_t b) {
    while (b) {
        uint64_t t = a % b;
        a = b;
        b = t;
    }
    return a;
}

static int miller_rabin(uint64_t n) {
    if (n < 2)
        return 0;
    static const uint64_t small[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31};
    for (size_t i = 0; i < sizeof small / sizeof small[0]; i++) {
        if (n == small[i])
            return 1;
        if (n % small[i] == 0)
            return 0;
    }
    if (n >= MR_BOUND) {
        fprintf(stderr, "n=%" PRIu64 " exceeds deterministic MR bound\n", n);
        exit(2);
    }
    uint64_t d = n - 1;
    int s = 0;
    while ((d & 1) == 0) {
        d >>= 1;
        s++;
    }
    for (int i = 0; i < N_MR; i++) {
        uint64_t a = MR_WITNESSES[i];
        if (a % n == 0)
            continue;
        uint64_t x = modpow(a, d, n);
        if (x == 1 || x == n - 1)
            continue;
        int ok = 0;
        for (int r = 0; r < s - 1; r++) {
            x = mulmod(x, x, n);
            if (x == n - 1) {
                ok = 1;
                break;
            }
        }
        if (!ok)
            return 0;
    }
    return 1;
}

static uint64_t sqrt_minus_one(uint64_t p) {
    uint64_t exp = (p - 1) / 4;
    for (uint64_t a = 2; a < p; a++) {
        uint64_t r = modpow(a, exp, p);
        if (mulmod(r, r, p) == p - 1)
            return r;
    }
    fprintf(stderr, "sqrt(-1) failed mod %" PRIu64 "\n", p);
    exit(1);
}

static uint64_t pollard_rho(uint64_t n) {
    if ((n & 1) == 0)
        return 2;
    if (n % 3 == 0)
        return 3;
    for (uint64_t c = 1; c < 96; c++) {
        uint64_t y = 2, d = 1, r = 1, q = 1, ys = y, x = 0;
        while (d == 1) {
            x = y;
            for (uint64_t i = 0; i < r; i++)
                y = (mulmod(y, y, n) + c) % n;
            uint64_t k = 0;
            while (k < r && d == 1) {
                ys = y;
                uint64_t mstep = r - k;
                if (mstep > 128)
                    mstep = 128;
                for (uint64_t i = 0; i < mstep; i++) {
                    y = (mulmod(y, y, n) + c) % n;
                    uint64_t diff = x > y ? x - y : y - x;
                    q = mulmod(q, diff, n);
                }
                d = gcd_u64(q, n);
                k += mstep;
            }
            r *= 2;
        }
        if (d != n)
            return d;
        y = ys;
        for (;;) {
            y = (mulmod(y, y, n) + c) % n;
            uint64_t diff = x > y ? x - y : y - x;
            d = gcd_u64(diff, n);
            if (d > 1) {
                if (d != n)
                    return d;
                break;
            }
        }
    }
    fprintf(stderr, "pollard rho failed on %" PRIu64 "\n", n);
    exit(1);
}

static void factor_rec(uint64_t m, uint64_t *out, int *nout) {
    if (m == 1)
        return;
    if (miller_rabin(m)) {
        out[(*nout)++] = m;
        return;
    }
    uint64_t d = pollard_rho(m);
    factor_rec(d, out, nout);
    factor_rec(m / d, out, nout);
}

static int cmp_u64(const void *a, const void *b) {
    uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b;
    return (x > y) - (x < y);
}

static uint64_t *primes_upto(uint64_t limit, uint64_t *nprimes) {
    if (limit < 2) {
        *nprimes = 0;
        return NULL;
    }
    uint64_t n = limit + 1;
    uint8_t *sieve = malloc(n);
    if (!sieve) {
        fprintf(stderr, "prime sieve malloc failed\n");
        exit(1);
    }
    memset(sieve, 1, n);
    sieve[0] = sieve[1] = 0;
    for (uint64_t p = 2; p * p < n; p++) {
        if (!sieve[p])
            continue;
        for (uint64_t k = p * p; k < n; k += p)
            sieve[k] = 0;
    }
    uint64_t cnt = 0;
    for (uint64_t i = 2; i < n; i++)
        if (sieve[i])
            cnt++;
    uint64_t *primes = malloc(cnt * sizeof *primes);
    if (!primes) {
        fprintf(stderr, "prime list malloc failed\n");
        exit(1);
    }
    uint64_t j = 0;
    for (uint64_t i = 2; i < n; i++)
        if (sieve[i])
            primes[j++] = i;
    free(sieve);
    *nprimes = cnt;
    return primes;
}

static void self_test(void) {
    if (mulmod(sqrt_minus_one(5), sqrt_minus_one(5), 5) != 4)
        exit(1);
    if (mulmod(sqrt_minus_one(13), sqrt_minus_one(13), 13) != 12)
        exit(1);
    if (mulmod(sqrt_minus_one(17), sqrt_minus_one(17), 17) != 16)
        exit(1);
    if (mulmod(sqrt_minus_one(29), sqrt_minus_one(29), 29) != 28)
        exit(1);
    if (!miller_rabin(2) || !miller_rabin(5) || miller_rabin(65))
        exit(1);
    if (!miller_rabin(UINT64_C(999900002501))) /* 999950^2+1, inside N=10^6 */
        exit(1);
    uint64_t fs[8];
    int n = 0;
    factor_rec(325, fs, &n);
    qsort(fs, (size_t)n, sizeof *fs, cmp_u64);
    if (n != 3 || fs[0] != 5 || fs[1] != 5 || fs[2] != 13)
        exit(1);
    n = 0;
    factor_rec(65, fs, &n);
    qsort(fs, (size_t)n, sizeof *fs, cmp_u64);
    if (n != 2 || fs[0] != 5 || fs[1] != 13)
        exit(1);
    printf("self-test OK\n");
}

static void write_json_meta(
    const char *path,
    uint64_t n_max,
    uint64_t nprime,
    uint64_t np2,
    uint64_t w_le2,
    uint64_t unsplit,
    const uint64_t *omega_hist,
    int hist_max,
    double t_sieve,
    double t_cls,
    long rss
) {
    FILE *f = fopen(path, "w");
    if (!f) {
        perror(path);
        exit(1);
    }
    fprintf(f, "{\n");
    fprintf(f, "  \"n_max\": %" PRIu64 ",\n", n_max);
    fprintf(f, "  \"count_prime\": %" PRIu64 ",\n", nprime);
    fprintf(f, "  \"count_p2_omega_eq_2_composite\": %" PRIu64 ",\n", np2);
    fprintf(f, "  \"count_iwaniec_p2\": %" PRIu64 ",\n", nprime + np2);
    fprintf(f, "  \"count_omega_le2_composite_diagnostic\": %" PRIu64 ",\n", w_le2);
    fprintf(f, "  \"unsplit\": %" PRIu64 ",\n", unsplit);
    fprintf(f, "  \"omega_hist\": {\n");
    int first = 1;
    for (int k = 1; k <= hist_max; k++) {
        if (!omega_hist[k])
            continue;
        if (!first)
            fprintf(f, ",\n");
        first = 0;
        fprintf(f, "    \"%d\": %" PRIu64, k, omega_hist[k]);
    }
    fprintf(f, "\n  },\n");
    fprintf(f, "  \"seconds_sieve\": %.9f,\n", t_sieve);
    fprintf(f, "  \"seconds_classify\": %.9f,\n", t_cls);
    fprintf(f, "  \"rss_kb\": %ld,\n", rss);
    fprintf(f, "  \"producer\": \"sieve_n2p1.c\"\n");
    fprintf(f, "}\n");
    fclose(f);
}

static void classify_one(
    uint64_t n,
    uint64_t rem,
    unsigned om,
    unsigned w,
    FILE *fp,
    FILE *f2,
    uint64_t *nprime,
    uint64_t *np2,
    uint64_t *w_le2,
    uint64_t *unsplit,
    uint64_t *omega_hist,
    int *hist_max
) {
    uint64_t leftover[8];
    int nleft = 0;
    if (rem > 1) {
        if (miller_rabin(rem)) {
            leftover[nleft++] = rem;
            om += 1;
            w += 1;
        } else {
            uint64_t d = pollard_rho(rem);
            uint64_t a = d, b = rem / d;
            if (a > b) {
                uint64_t tmp = a;
                a = b;
                b = tmp;
            }
            if (miller_rabin(a) && miller_rabin(b) && a * b == rem) {
                leftover[nleft++] = a;
                leftover[nleft++] = b;
            } else {
                factor_rec(rem, leftover, &nleft);
                (*unsplit)++;
            }
            om += (unsigned)nleft;
            qsort(leftover, (size_t)nleft, sizeof *leftover, cmp_u64);
            unsigned distinct = 0;
            for (int k = 0; k < nleft; k++)
                if (k == 0 || leftover[k] != leftover[k - 1])
                    distinct++;
            w += distinct;
        }
    }
    if (om > 31)
        om = 31;
    omega_hist[om]++;
    if ((int)om > *hist_max)
        *hist_max = (int)om;
    if (om == 1) {
        fprintf(fp, "%" PRIu64 "\n", n);
        (*nprime)++;
        return;
    }
    if (w <= 2)
        (*w_le2)++;
    if (om != 2)
        return;
    uint64_t m = n * n + 1;
    uint64_t fs[8];
    int nfs = 0;
    if (rem > 1 && nleft > 0) {
        uint64_t prod = 1;
        for (int k = 0; k < nleft; k++)
            prod *= leftover[k];
        if (prod == rem) {
            uint64_t other = m / rem;
            if (other == 1) {
                memcpy(fs, leftover, (size_t)nleft * sizeof *fs);
                nfs = nleft;
            } else {
                memcpy(fs, leftover, (size_t)nleft * sizeof *fs);
                fs[nleft] = other;
                nfs = nleft + 1;
            }
        }
    }
    if (nfs != 2) {
        nfs = 0;
        factor_rec(m, fs, &nfs);
    }
    qsort(fs, (size_t)nfs, sizeof *fs, cmp_u64);
    {
        uint64_t prod = 1;
        for (int k = 0; k < nfs; k++)
            prod *= fs[k];
        if (nfs != 2 || prod != m) {
            (*unsplit)++;
            fprintf(f2, "%" PRIu64, n);
            for (int k = 0; k < nfs; k++)
                fprintf(f2, " %" PRIu64, fs[k]);
            fputc('\n', f2);
        } else {
            fprintf(f2, "%" PRIu64 " %" PRIu64 " %" PRIu64 "\n", n, fs[0], fs[1]);
        }
    }
    (*np2)++;
}

int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "--self-test") == 0) {
        self_test();
        return 0;
    }
    if (argc != 3) {
        fprintf(stderr, "usage: %s --self-test | %s NMAX OUTDIR\n", argv[0], argv[0]);
        return 2;
    }
    uint64_t n_max = strtoull(argv[1], NULL, 10);
    const char *outdir = argv[2];
    if (n_max < 1) {
        fprintf(stderr, "n_max must be >= 1\n");
        return 2;
    }
    if (n_max > UINT64_C(4294967295)) {
        fprintf(stderr, "n_max too large for uint64 n^2+1\n");
        return 2;
    }
    uint64_t size = n_max / 2;
    uint64_t seg = SEG_EVENS;
    if (seg > size)
        seg = size;
    if (seg < 1)
        seg = 1;

    setvbuf(stderr, NULL, _IONBF, 0);

    double t0 = now_sec();
    uint64_t nprimes = 0;
    uint64_t *primes = primes_upto(n_max, &nprimes);
    uint64_t n_q = 0;
    for (uint64_t pi = 0; pi < nprimes; pi++) {
        uint64_t q = primes[pi];
        if (q != 2 && q % 4 == 1)
            n_q++;
    }
    uint64_t *qs = malloc(n_q * sizeof *qs);
    uint64_t *rs = malloc(n_q * sizeof *rs);
    if (!qs || !rs) {
        fprintf(stderr, "q/r malloc failed\n");
        return 1;
    }
    uint64_t qi = 0;
    for (uint64_t pi = 0; pi < nprimes; pi++) {
        uint64_t q = primes[pi];
        if (q == 2 || q % 4 != 1)
            continue;
        uint64_t r = sqrt_minus_one(q);
        if (mulmod(r, r, q) != q - 1) {
            fprintf(stderr, "bad sqrt(-1) mod %" PRIu64 "\n", q);
            return 1;
        }
        qs[qi] = q;
        rs[qi] = r;
        qi++;
        if (qi % 20000 == 0)
            fprintf(stderr, "  sqrt(-1) q=%" PRIu64 " (%.1fs) rss=%ld kB\n",
                    q, now_sec() - t0, rss_kb());
    }
    free(primes);
    primes = NULL;
    double t_roots = now_sec();
    fprintf(stderr, "precomputed %" PRIu64 " roots in %.2fs rss=%ld kB; segmented sieve\n",
            n_q, t_roots - t0, rss_kb());

    uint64_t *remaining = malloc(seg * sizeof *remaining);
    uint8_t *big_omega = malloc(seg);
    uint8_t *little_omega = malloc(seg);
    if (!remaining || !big_omega || !little_omega) {
        fprintf(stderr, "strip malloc failed (seg=%" PRIu64 ")\n", seg);
        return 1;
    }

    char path_p[4096], path_p2[4096], path_meta[4096];
    snprintf(path_p, sizeof path_p, "%s/prime_n.txt", outdir);
    snprintf(path_p2, sizeof path_p2, "%s/p2_omega2.txt", outdir);
    snprintf(path_meta, sizeof path_meta, "%s/sieve_meta.json", outdir);
    FILE *fp = fopen(path_p, "w");
    FILE *f2 = fopen(path_p2, "w");
    if (!fp || !f2) {
        perror("open lists");
        return 1;
    }
    fputs("# n such that n^2+1 is prime, n <= n_max, including n=1\n", fp);
    fputs("# Iwaniec P2 composites: n  p  q   with n^2+1 = p*q, Ω=2, p<=q\n", f2);

    uint64_t omega_hist[32] = {0};
    int hist_max = 0;
    uint64_t nprime = 0, np2 = 0, w_le2 = 0, unsplit = 0;
    if (n_max >= 1 && miller_rabin(2)) {
        fputs("1\n", fp);
        nprime++;
        omega_hist[1]++;
        hist_max = 1;
    }

    uint64_t nseg = (size + seg - 1) / seg;
    for (uint64_t s = 0; s < nseg; s++) {
        uint64_t i0 = s * seg;
        uint64_t slen = size - i0;
        if (slen > seg)
            slen = seg;
        uint64_t n_lo = 2 * (i0 + 1);
        uint64_t n_hi = 2 * (i0 + slen);
        for (uint64_t j = 0; j < slen; j++) {
            uint64_t n = 2 * (i0 + j + 1);
            remaining[j] = n * n + 1;
        }
        memset(big_omega, 0, slen);
        memset(little_omega, 0, slen);

        for (uint64_t k = 0; k < n_q; k++) {
            uint64_t q = qs[k];
            uint64_t r = rs[k];
            uint64_t residues[2] = {r, q - r};
            uint64_t step = 2 * q;
            for (int t = 0; t < 2; t++) {
                uint64_t start = residues[t];
                if (start & 1)
                    start += q;
                if (start == 0)
                    start = 2 * q;
                if (start < 2)
                    start += 2 * q;
                if (start < n_lo) {
                    uint64_t diff = n_lo - start;
                    uint64_t kk = (diff + step - 1) / step;
                    start += kk * step;
                }
                for (uint64_t n = start; n <= n_hi; n += step) {
                    uint64_t j = n / 2 - 1 - i0;
                    uint64_t m = remaining[j];
                    if (m % q)
                        continue;
                    int e = 0;
                    while (m % q == 0) {
                        m /= q;
                        e++;
                    }
                    remaining[j] = m;
                    unsigned om = (unsigned)big_omega[j] + (unsigned)e;
                    big_omega[j] = (uint8_t)(om > 255 ? 255 : om);
                    if (little_omega[j] < 255)
                        little_omega[j]++;
                }
            }
        }

        for (uint64_t j = 0; j < slen; j++) {
            uint64_t n = 2 * (i0 + j + 1);
            classify_one(
                n, remaining[j], big_omega[j], little_omega[j],
                fp, f2, &nprime, &np2, &w_le2, &unsplit, omega_hist, &hist_max
            );
        }
        fprintf(stderr,
                "  strip %" PRIu64 "/%" PRIu64 " n=%" PRIu64 "..%" PRIu64
                " primes=%" PRIu64 " p2=%" PRIu64 " %.1fs rss=%ld kB\n",
                s + 1, nseg, n_lo, n_hi, nprime, np2, now_sec() - t0, rss_kb());
    }

    fclose(fp);
    fclose(f2);
    double t2 = now_sec();
    long rss = rss_kb();
    /* seconds_sieve = root precompute; seconds_classify = segmented sieve+classify. */
    write_json_meta(path_meta, n_max, nprime, np2, w_le2, unsplit, omega_hist, hist_max,
                    t_roots - t0, t2 - t_roots, rss);
    printf("n_max=%" PRIu64 " primes=%" PRIu64 " p2_Omega2=%" PRIu64 " iwaniec_P2=%" PRIu64
           " w<=2_comp=%" PRIu64 " unsplit=%" PRIu64 "\n",
           n_max, nprime, np2, nprime + np2, w_le2, unsplit);
    printf("roots %.2fs sieve+classify %.2fs rss %ld kB strips=%" PRIu64 " seg=%" PRIu64 "\n",
           t_roots - t0, t2 - t_roots, rss, nseg, seg);
    printf("wrote %s %s %s\n", path_p, path_p2, path_meta);
    free(remaining);
    free(big_omega);
    free(little_omega);
    free(qs);
    free(rs);
    return unsplit ? 1 : 0;
}
