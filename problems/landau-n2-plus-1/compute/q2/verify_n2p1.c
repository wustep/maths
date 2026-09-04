/*
 * Independent check of the prime and P2 lists. Does not use the residue sieve.
 *
 *   * Miller–Rabin every even n (and n=1)
 *   * multiply every claimed P2 factorization back
 *   * trial (primes <= 2003) + Pollard of every even n^2+1, and require
 *     the P2 file to be exactly the Ω=2 composites
 *
 * Build: gcc -O3 -std=c11 -Wall -Wextra verify_n2p1.c -o verify_n2p1
 * Run:   ./verify_n2p1 OUTDIR
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
static const int TRIAL_BOUND = 2003;

static double now_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_nsec * 1e-9 + (double)ts.tv_sec;
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

static uint64_t *trial_primes(int bound, int *nprimes) {
    uint8_t *s = malloc((size_t)bound + 1);
    memset(s, 1, (size_t)bound + 1);
    s[0] = s[1] = 0;
    for (int p = 2; p * p <= bound; p++)
        if (s[p])
            for (int k = p * p; k <= bound; k += p)
                s[k] = 0;
    int cnt = 0;
    for (int i = 2; i <= bound; i++)
        if (s[i])
            cnt++;
    uint64_t *pr = malloc((size_t)cnt * sizeof *pr);
    int j = 0;
    for (int i = 2; i <= bound; i++)
        if (s[i])
            pr[j++] = (uint64_t)i;
    free(s);
    *nprimes = cnt;
    return pr;
}

static int factor_omega(uint64_t m, const uint64_t *pr, int npr) {
    int om = 0;
    for (int i = 0; i < npr; i++) {
        uint64_t p = pr[i];
        if (p * p > m)
            break;
        while (m % p == 0) {
            om++;
            m /= p;
        }
    }
    if (m == 1)
        return om;
    uint64_t fs[16];
    int nfs = 0;
    factor_rec(m, fs, &nfs);
    return om + nfs;
}

static uint64_t parse_nmax(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) {
        perror(path);
        exit(1);
    }
    char line[256];
    uint64_t n = 0;
    while (fgets(line, sizeof line, f)) {
        if (sscanf(line, "  \"n_max\": %" SCNu64, &n) == 1) {
            fclose(f);
            return n;
        }
    }
    fclose(f);
    fprintf(stderr, "n_max not found in %s\n", path);
    exit(1);
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "usage: %s OUTDIR\n", argv[0]);
        return 2;
    }
    const char *dir = argv[1];
    char path[4096];
    snprintf(path, sizeof path, "%s/n2p1.json", dir);
    uint64_t n_max = parse_nmax(path);
    uint64_t size = n_max / 2;
    uint8_t *is_prime = calloc(size, 1);
    uint8_t *is_p2 = calloc(size, 1);
    if (!is_prime || !is_p2) {
        fprintf(stderr, "calloc failed\n");
        return 1;
    }

    double t0 = now_sec();
    snprintf(path, sizeof path, "%s/prime_n.txt", dir);
    FILE *fp = fopen(path, "r");
    if (!fp) {
        perror(path);
        return 1;
    }
    char *line = NULL;
    size_t cap = 0;
    uint64_t nclaimed = 0, has1 = 0;
    while (getline(&line, &cap, fp) != -1) {
        if (line[0] == '#' || line[0] == '\n')
            continue;
        uint64_t n = strtoull(line, NULL, 10);
        if (n == 1) {
            has1 = 1;
            nclaimed++;
            continue;
        }
        if (n < 2 || n > n_max || (n & 1)) {
            fprintf(stderr, "bad prime n=%" PRIu64 "\n", n);
            return 1;
        }
        is_prime[n / 2 - 1] = 1;
        nclaimed++;
    }
    fclose(fp);

    snprintf(path, sizeof path, "%s/p2_omega2.txt", dir);
    FILE *f2 = fopen(path, "r");
    if (!f2) {
        perror(path);
        return 1;
    }
    uint64_t np2 = 0, bad = 0;
    while (getline(&line, &cap, f2) != -1) {
        if (line[0] == '#' || line[0] == '\n')
            continue;
        uint64_t n = 0, p = 0, q = 0, extra = 0;
        int got = sscanf(line, "%" SCNu64 " %" SCNu64 " %" SCNu64 " %" SCNu64, &n, &p, &q, &extra);
        if (got != 3) {
            bad++;
            if (bad <= 5)
                fprintf(stderr, "p2 parse fail: %s", line);
            continue;
        }
        if (n < 2 || n > n_max || (n & 1) || p > q ||
            (__uint128_t)p * q != (__uint128_t)n * n + 1 ||
            !miller_rabin(p) || !miller_rabin(q) || miller_rabin(n * n + 1)) {
            bad++;
            if (bad <= 5)
                fprintf(stderr, "p2 fail n=%" PRIu64 " p=%" PRIu64 " q=%" PRIu64 "\n", n, p, q);
            continue;
        }
        is_p2[n / 2 - 1] = 1;
        np2++;
    }
    fclose(f2);
    if (bad) {
        fprintf(stderr, "P2 factorization failures: %" PRIu64 "\n", bad);
        return 1;
    }
    printf("P2 factorizations OK (%" PRIu64 " rows) %.1fs\n", np2, now_sec() - t0);

    uint64_t nfound = has1 && miller_rabin(2) ? 1 : 0;
    uint64_t extra = 0, missing = 0;
    for (uint64_t n = 2; n <= n_max; n += 2) {
        if ((n & ((1u << 18) - 1)) == 0)
            fprintf(stderr, "  prime scan n=%" PRIu64 " found=%" PRIu64 "\n", n, nfound);
        int pr = miller_rabin(n * n + 1);
        uint64_t i = n / 2 - 1;
        if (pr)
            nfound++;
        if (pr && !is_prime[i])
            missing++;
        if (!pr && is_prime[i])
            extra++;
    }
    printf("primes n_max=%" PRIu64 " claimed=%" PRIu64 " found=%" PRIu64 " extra=%" PRIu64 " missing=%" PRIu64 "\n",
           n_max, nclaimed, nfound, extra, missing);
    if (extra || missing || nclaimed != nfound)
        return 1;
    printf("primes OK %.1fs\n", now_sec() - t0);

    int npr = 0;
    uint64_t *pr = trial_primes(TRIAL_BOUND, &npr);
    uint64_t miss_p2 = 0, extra_p2 = 0, scanned = 0;
    for (uint64_t n = 2; n <= n_max; n += 2) {
        scanned++;
        if (scanned % 200000 == 0)
            fprintf(stderr, "  completeness scanned %" PRIu64 " even n\n", scanned);
        uint64_t i = n / 2 - 1;
        if (is_prime[i])
            continue;
        int om = factor_omega(n * n + 1, pr, npr);
        if (om == 2) {
            if (!is_p2[i]) {
                miss_p2++;
                if (miss_p2 <= 5)
                    fprintf(stderr, "missing P2 n=%" PRIu64 "\n", n);
            }
        } else if (is_p2[i]) {
            extra_p2++;
            if (extra_p2 <= 5)
                fprintf(stderr, "extra P2 n=%" PRIu64 " omega=%d\n", n, om);
        }
    }
    printf("complete P2 scan miss=%" PRIu64 " extra=%" PRIu64 " %.1fs\n", miss_p2, extra_p2, now_sec() - t0);
    if (miss_p2 || extra_p2)
        return 1;
    printf("P2 completeness OK\n");
    printf("OK\n");
    free(line);
    free(is_prime);
    free(is_p2);
    free(pr);
    return 0;
}
