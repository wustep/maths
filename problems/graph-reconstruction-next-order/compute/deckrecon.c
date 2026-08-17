/* deckrecon.c
 *
 * Independent reconstruction tester in the style of McKay, arXiv:2102.01942.
 *
 * Read graph6 graphs (or generate them via geng -DOUTPROC) and decide whether
 * any two non-isomorphic graphs share a deck or a reduced deck.
 *
 * A graph is identified with its nauty graph6 string. Cards are canonicalised
 * with densenauty; the multiset (full deck) and the set (reduced deck) of
 * those strings are SHA-256 hashed. Two graphs with the same hash are then
 * compared exactly.
 *
 * Membership of a degree-window class is reduced-deck-recognisable
 * (McKay Lemma 2.2 / Manvel), so uniqueness inside the class implies
 * reconstructibility from the reduced deck.
 */

#define MAXN 64
#include "gtools.h"
#include "nauty.h"

#include <openssl/sha.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>

#ifndef WORDSIZE
#error "WORDSIZE undefined"
#endif

#if WORDSIZE < 64
#error "Need WORDSIZE >= 64 so that m=1 for n<=64"
#endif

#define G6MAX 128
#define CARDMAX 32

static DEFAULTOPTIONS_GRAPH(options);
static statsblk stats;
static int options_ready = 0;

static unsigned long long n_read = 0;
static unsigned long long n_kept = 0;
static unsigned long long n_unique_full = 0;
static unsigned long long n_unique_set = 0;
static unsigned long long n_full_collisions = 0;
static unsigned long long n_set_collisions = 0;
static unsigned long long n_hash_tie_full = 0;
static unsigned long long n_hash_tie_set = 0;

static int require_minmax = 0;
static int min_deg_bound = -1;
static int max_deg_bound = -1;
static int emit_mode = 0;
static int unique_mode = 0;
static int sample_every = 0;
static FILE *sample_fp = NULL;
static FILE *coll_fp = NULL;
static const char *sample_path = NULL;
static const char *coll_path = NULL;

/* ---- SHA-256 of a list of C strings (already sorted) ---- */

static void sha_strings(char *const *ss, int k, unsigned char out[32])
{
    SHA256_CTX ctx;
    SHA256_Init(&ctx);
    for (int i = 0; i < k; i++) {
        SHA256_Update(&ctx, ss[i], strlen(ss[i]));
        SHA256_Update(&ctx, "\n", 1);
    }
    SHA256_Final(out, &ctx);
}

static void hex32(const unsigned char h[32], char *out)
{
    static const char *hexd = "0123456789abcdef";
    for (int i = 0; i < 32; i++) {
        out[2 * i] = hexd[h[i] >> 4];
        out[2 * i + 1] = hexd[h[i] & 15];
    }
    out[64] = 0;
}

static int cmp_strptr(const void *a, const void *b)
{
    return strcmp(*(char *const *)a, *(char *const *)b);
}

/* Delete vertex v from n-vertex dense graph g (m=1). Write n-1 vertex graph h.
 * nauty packs vertex 0 at the high bit of the word; do not shift as if LSB=0. */
static void delete_vertex(const graph *g, int n, int v, graph *h)
{
    EMPTYGRAPH(h, 1, n - 1);
    for (int i = 0; i < n; i++) {
        if (i == v)
            continue;
        int ni = (i < v) ? i : i - 1;
        for (int j = i + 1; j < n; j++) {
            if (j == v)
                continue;
            if (ISELEMENT(GRAPHROW(g, i, 1), j)) {
                int nj = (j < v) ? j : j - 1;
                ADDONEEDGE(h, ni, nj, 1);
            }
        }
    }
}

static void ensure_options(void)
{
    if (options_ready)
        return;
    options.getcanon = TRUE;
    options.defaultptn = TRUE;
    options_ready = 1;
}

/* Canonical graph6 of an n-vertex m=1 graph. Writes into out (size G6MAX). */
static void canon_g6(graph *g, int n, char *out)
{
    graph canon[MAXN];
    int lab[MAXN], ptn[MAXN], orbits[MAXN];
    ensure_options();
    densenauty(g, lab, ptn, orbits, &options, &stats, 1, n, canon);
    char *s = ntog6(canon, 1, n);
    strncpy(out, s, G6MAX - 1);
    out[G6MAX - 1] = 0;
    /* ntog6 includes a trailing newline; hash the graph6 token only */
    size_t L = strlen(out);
    while (L && (out[L - 1] == '\n' || out[L - 1] == '\r'))
        out[--L] = 0;
}

/* Degrees of g. Returns min,max via pointers. */
static void degrees_of(const graph *g, int n, int *deg, int *dmin, int *dmax)
{
    int mn = n, mx = 0;
    for (int i = 0; i < n; i++) {
        int d = (int)POPCOUNT(g[i]);
        deg[i] = d;
        if (d < mn)
            mn = d;
        if (d > mx)
            mx = d;
    }
    if (dmin)
        *dmin = mn;
    if (dmax)
        *dmax = mx;
}

/* Compute full-deck and reduced-deck SHA-256. */
static void decks_of(graph *g, int n, unsigned char full[32], unsigned char red[32],
                     int *n_red)
{
    char cards[MAXN][CARDMAX];
    char *ptrs[MAXN];
    graph h[MAXN];
    for (int v = 0; v < n; v++) {
        delete_vertex(g, n, v, h);
        canon_g6(h, n - 1, cards[v]);
        ptrs[v] = cards[v];
    }
    qsort(ptrs, (size_t)n, sizeof(char *), cmp_strptr);
    sha_strings(ptrs, n, full);

    int k = 0;
    char *uniq[MAXN];
    for (int i = 0; i < n; i++) {
        if (k == 0 || strcmp(uniq[k - 1], ptrs[i]) != 0)
            uniq[k++] = ptrs[i];
    }
    sha_strings(uniq, k, red);
    if (n_red)
        *n_red = k;
}

/* ---------- open-addressing table: SHA-256 -> first graph6 ---------- */

typedef struct {
    unsigned char key[32];
    char g6[G6MAX];
    unsigned int count;
    unsigned char used;
} slot_t;

typedef struct {
    slot_t *s;
    size_t cap;
    size_t fill;
    const char *name;
    unsigned long long *n_unique;
    unsigned long long *n_coll;
    unsigned long long *n_tie;
} table_t;

static size_t key_index(const unsigned char key[32], size_t cap)
{
    uint64_t h;
    memcpy(&h, key, 8);
    return (size_t)(h % cap);
}

static void table_init(table_t *t, size_t cap, const char *name,
                       unsigned long long *nu, unsigned long long *nc,
                       unsigned long long *nt)
{
    /* cap must be a power of two-ish; we just take the given size. */
    t->s = calloc(cap, sizeof(slot_t));
    if (!t->s) {
        fprintf(stderr, "deckrecon: out of memory allocating %s table (%zu slots)\n",
                name, cap);
        exit(2);
    }
    t->cap = cap;
    t->fill = 0;
    t->name = name;
    t->n_unique = nu;
    t->n_coll = nc;
    t->n_tie = nt;
}

static void table_free(table_t *t)
{
    free(t->s);
    t->s = NULL;
}

static slot_t *table_find(table_t *t, const unsigned char key[32], int for_insert)
{
    size_t i = key_index(key, t->cap);
    for (size_t step = 0; step < t->cap; step++) {
        slot_t *sl = &t->s[i];
        if (!sl->used)
            return for_insert ? sl : NULL;
        if (memcmp(sl->key, key, 32) == 0)
            return sl;
        i++;
        if (i == t->cap)
            i = 0;
    }
    return NULL;
}

static void report_collision(const char *kind, const char *g1, const char *g2,
                             const unsigned char key[32])
{
    char hex[65];
    hex32(key, hex);
    fprintf(stderr, "COLLISION %s sha256=%s\n  A %s\n  B %s\n", kind, hex, g1, g2);
    if (coll_fp) {
        fprintf(coll_fp, "%s %s %s %s\n", kind, hex, g1, g2);
        fflush(coll_fp);
    }
}

/* Exact deck comparison of two graph6 strings (independent of the hash). */
static int same_decks(const char *g6a, const char *g6b, int want_set)
{
    graph ga[MAXN], gb[MAXN];
    int na, nb, ma, mb;
    stringtograph((char *)g6a, ga, 1);
    stringtograph((char *)g6b, gb, 1);
    na = graphsize((char *)g6a);
    nb = graphsize((char *)g6b);
    (void)ma;
    (void)mb;
    if (na != nb)
        return 0;
    unsigned char fa[32], ra[32], fb[32], rb[32];
    decks_of(ga, na, fa, ra, NULL);
    decks_of(gb, nb, fb, rb, NULL);
    if (want_set)
        return memcmp(ra, rb, 32) == 0;
    return memcmp(fa, fb, 32) == 0;
}

static void table_insert(table_t *t, const unsigned char key[32], const char *g6,
                         int want_set)
{
    if (t->fill * 10 >= t->cap * 6) {
        fprintf(stderr, "deckrecon: %s table load > 0.6 (%zu / %zu); abort\n",
                t->name, t->fill, t->cap);
        exit(3);
    }
    slot_t *sl = table_find(t, key, 1);
    if (!sl) {
        fprintf(stderr, "deckrecon: %s table full\n", t->name);
        exit(3);
    }
    if (!sl->used) {
        sl->used = 1;
        memcpy(sl->key, key, 32);
        strncpy(sl->g6, g6, G6MAX - 1);
        sl->count = 1;
        t->fill++;
        (*t->n_unique)++;
        return;
    }
    sl->count++;
    if (strcmp(sl->g6, g6) == 0)
        return; /* same isomorph generated twice; should not happen */
    /* Hash collision or genuine deck collision. Compare exactly. */
    if (same_decks(sl->g6, g6, want_set)) {
        (*t->n_coll)++;
        report_collision(t->name, sl->g6, g6, key);
    } else {
        (*t->n_tie)++;
        fprintf(stderr, "deckrecon: SHA-256 tie on %s (graphs differ); treating as unique\n",
                t->name);
    }
}

static table_t tab_full, tab_set;

static void process_one(graph *g, int n, const char *g6_in)
{
    int deg[MAXN], dmin, dmax;
    degrees_of(g, n, deg, &dmin, &dmax);
    n_read++;
    if (require_minmax) {
        if (min_deg_bound >= 0 && dmin != min_deg_bound)
            return;
        if (max_deg_bound >= 0 && dmax != max_deg_bound)
            return;
    }
    n_kept++;

    unsigned char full[32], red[32];
    int nred;
    decks_of(g, n, full, red, &nred);

    char g6buf[G6MAX];
    const char *g6 = g6_in;
    if (!g6) {
        char *s = ntog6(g, 1, n);
        strncpy(g6buf, s, G6MAX - 1);
        g6buf[G6MAX - 1] = 0;
        g6 = g6buf;
    }

    if (emit_mode) {
        char hf[65], hs[65];
        hex32(full, hf);
        hex32(red, hs);
        printf("%s %s %d %d %d %s\n", hf, hs, dmin, dmax, nred, g6);
    }
    if (unique_mode) {
        table_insert(&tab_full, full, g6, 0);
        table_insert(&tab_set, red, g6, 1);
    }
    if (sample_fp && sample_every > 0 && (n_kept % (unsigned long long)sample_every) == 0) {
        char hf[65], hs[65];
        hex32(full, hf);
        hex32(red, hs);
        fprintf(sample_fp, "%s %s %s\n", hf, hs, g6);
    }
    if ((n_kept & 0xFFFFF) == 0 && n_kept) {
        fprintf(stderr, "deckrecon: kept=%llu read=%llu full_coll=%llu set_coll=%llu\n",
                n_kept, n_read, n_full_collisions, n_set_collisions);
    }
}

/* geng OUTPROC hook (used when this file is compiled with -DOUTPROC). */
#ifdef OUTPROC
void OUTPROC(FILE *f, graph *g, int n)
{
    (void)f;
    process_one(g, n, NULL);
}
#endif

#ifdef SUMMARY
void SUMMARY(nauty_counter nout, double cpu)
{
    fprintf(stderr, "SUMMARY nout=%llu cpu=%.3f kept=%llu full_coll=%llu set_coll=%llu\n",
            (unsigned long long)nout, cpu, n_kept, n_full_collisions, n_set_collisions);
}
#endif

static void usage(void)
{
    fprintf(stderr,
            "Usage: deckrecon [options] hash|unique\n"
            "  Read graph6 on stdin.\n"
            "  hash    write: full_sha set_sha dmin dmax n_reduced g6\n"
            "  unique  insert decks into a table; report collisions\n"
            "Options:\n"
            "  --require-minmax   keep only graphs attaining both --dmin and --dmax\n"
            "  --dmin K --dmax K  degree bounds for the filter\n"
            "  --table N          hash-table capacity (default 4000003)\n"
            "  --sample K FILE    write every K-th kept graph+hash to FILE\n"
            "  --collisions FILE  write collision pairs to FILE\n");
}

int main(int argc, char **argv)
{
    size_t table_cap = 4000003; /* prime */
    int argi = 1;
    const char *cmd = NULL;

    while (argi < argc) {
        if (strcmp(argv[argi], "--require-minmax") == 0) {
            require_minmax = 1;
            argi++;
        } else if (strcmp(argv[argi], "--dmin") == 0 && argi + 1 < argc) {
            min_deg_bound = atoi(argv[++argi]);
            argi++;
        } else if (strcmp(argv[argi], "--dmax") == 0 && argi + 1 < argc) {
            max_deg_bound = atoi(argv[++argi]);
            argi++;
        } else if (strcmp(argv[argi], "--table") == 0 && argi + 1 < argc) {
            table_cap = (size_t)strtoull(argv[++argi], NULL, 10);
            argi++;
        } else if (strcmp(argv[argi], "--sample") == 0 && argi + 2 < argc) {
            sample_every = atoi(argv[++argi]);
            sample_path = argv[++argi];
            argi++;
        } else if (strcmp(argv[argi], "--collisions") == 0 && argi + 1 < argc) {
            coll_path = argv[++argi];
            argi++;
        } else if (strcmp(argv[argi], "-h") == 0 || strcmp(argv[argi], "--help") == 0) {
            usage();
            return 0;
        } else if (argv[argi][0] == '-') {
            fprintf(stderr, "unknown option %s\n", argv[argi]);
            usage();
            return 1;
        } else if (!cmd) {
            cmd = argv[argi++];
        } else {
            fprintf(stderr, "unexpected argument %s\n", argv[argi]);
            usage();
            return 1;
        }
    }
    if (!cmd) {
        usage();
        return 1;
    }
    if (strcmp(cmd, "hash") == 0)
        emit_mode = 1;
    else if (strcmp(cmd, "unique") == 0)
        unique_mode = 1;
    else {
        fprintf(stderr, "unknown command %s\n", cmd);
        usage();
        return 1;
    }

    if (sample_path) {
        sample_fp = fopen(sample_path, "w");
        if (!sample_fp) {
            perror(sample_path);
            return 1;
        }
    }
    if (coll_path) {
        coll_fp = fopen(coll_path, "w");
        if (!coll_fp) {
            perror(coll_path);
            return 1;
        }
    }

    if (unique_mode) {
        table_init(&tab_full, table_cap, "full-deck", &n_unique_full,
                   &n_full_collisions, &n_hash_tie_full);
        table_init(&tab_set, table_cap, "reduced-deck", &n_unique_set,
                   &n_set_collisions, &n_hash_tie_set);
    }

    graph g[MAXN];
    int m, n;
    char *line;
    while ((line = gtools_getline(stdin)) != NULL) {
        if (line[0] == '>' || line[0] == 0)
            continue;
        n = graphsize(line);
        if (n < 2 || n > 64) {
            fprintf(stderr, "deckrecon: skip n=%d\n", n);
            continue;
        }
        stringtograph(line, g, 1);
        (void)m;
        /* strip trailing newline for stored g6 */
        size_t L = strlen(line);
        while (L && (line[L - 1] == '\n' || line[L - 1] == '\r'))
            line[--L] = 0;
        process_one(g, n, line);
    }

    printf("read=%llu kept=%llu\n", n_read, n_kept);
    if (unique_mode) {
        printf("full_unique=%llu full_collisions=%llu full_sha_ties=%llu\n",
               n_unique_full, n_full_collisions, n_hash_tie_full);
        printf("set_unique=%llu set_collisions=%llu set_sha_ties=%llu\n",
               n_unique_set, n_set_collisions, n_hash_tie_set);
        table_free(&tab_full);
        table_free(&tab_set);
    }
    if (sample_fp)
        fclose(sample_fp);
    if (coll_fp)
        fclose(coll_fp);
    return (n_full_collisions || n_set_collisions) ? 10 : 0;
}
