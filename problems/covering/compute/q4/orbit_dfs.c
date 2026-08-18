/*
 * q4: exhaustive search for group-invariant 49-column radius-2 coverings
 * of F_2^10.
 *
 * Input: a "group file" listing g generator matrices of a subgroup
 * G <= GL(10,2).  Each generator is one line of 10 integers (decimal or
 * 0x-hex): the images M(e_0), ..., M(e_9) of the basis vectors, encoded
 * as 10-bit integers with bit i = coordinate i.  M(v) is the XOR of the
 * listed images over the set bits of v.
 *
 * The program computes the orbits of G on the 1023 nonzero points,
 * then exhaustively enumerates all G-invariant subsets (unions of
 * orbits) of total size exactly --n (default 49), testing whether the
 * union S satisfies {0} u S u (S+S) = F_2^10.  Coverage bookkeeping is
 * done in orbit-class space: a syndrome is covered iff its whole orbit
 * is, because S is G-invariant and x -> Mx commutes with XOR.
 *
 * Pruning (all provably safe, so "exhausted" means exhausted):
 *   1. budget: exact subset-sum feasibility of the remaining weight
 *      over the item-weight suffix (precomputed DP);
 *   2. counting: an optimistic upper bound on how many still-uncovered
 *      classes the remaining picks could cover;
 *   3. reachability: a class not in the union of every single/pair
 *      mask still available in the suffix (including pairs with the
 *      already-chosen items) can never be covered - prune.
 *
 * Output: every witness found (as 49 column values, decimal), plus a
 * deterministic exhaustion summary with node counts.  A witness is
 * re-verified here by a from-scratch pair enumeration, and must still
 * be checked by the independent Python verifier.
 *
 * Build:
 *   gcc -O3 -std=c11 -Wall -Wextra -fopenmp compute/q4/orbit_dfs.c \
 *       -o compute/q4/orbit_dfs
 *
 * Run:
 *   compute/q4/orbit_dfs --group compute/q4/groups/c7_t1_30.grp
 */

#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef _OPENMP
#include <omp.h>
#endif

enum { R = 10, V = 1 << R, MAX_GENS = 4, MAX_ITEMS = 1024, MAX_W = 16 };

static int target_n = 49;
static int max_witnesses = 16;
static int no_prune = 0;
static const char *group_path = NULL;

static int gen_count = 0;
static int gens[MAX_GENS][R];

static int item_count = 0;          /* number of orbits (= classes) */
static int words = 0;               /* mask words = ceil(item_count/64) */
static int class_of[V];             /* orbit id of each nonzero point */
static int item_size[MAX_ITEMS];    /* orbit sizes */
static int item_min[MAX_ITEMS];     /* smallest point of orbit */
static int *item_points[MAX_ITEMS]; /* orbit member lists */

static uint64_t *single_mask;       /* [item][words]: own + internal-sum classes */
static uint64_t *pair_mask;         /* [i*item_count+j][words]: cross-sum classes */
static uint64_t *pt_suffix;         /* [t][k][words]: union of pair(t,i), i>=k */
static uint64_t *ss_suffix;         /* [k][words]: union of single(i), i>=k */
static uint64_t *sp_suffix;         /* [k][words]: union of pair(i,j), i,j>=k */
static unsigned char *budget_ok;    /* [k*(target_n+1)+w]: subset-sum DP */
static int *max_items_dp;           /* [k*(target_n+1)+w]: max #items summing to w */
static uint64_t full_mask[MAX_W];

static int max_single_pop = 0;
static int max_pair_pop = 0;

static long long witnesses_found = 0;
static long long total_nodes = 0;

static int apply_gen(int g, int v) {
    int out = 0;
    for (int bit = 0; bit < R; ++bit) {
        if (v & (1 << bit)) {
            out ^= gens[g][bit];
        }
    }
    return out;
}

static int read_group(const char *path) {
    FILE *file = fopen(path, "r");
    char line[4096];
    if (file == NULL) {
        fprintf(stderr, "cannot open %s: %s\n", path, strerror(errno));
        return 0;
    }
    gen_count = 0;
    while (fgets(line, sizeof(line), file) != NULL) {
        char *cursor = line;
        int images[R];
        int got = 0;
        if (line[0] == '#' || line[0] == '\n' || line[0] == '\r') {
            continue;
        }
        while (got < R) {
            char *end = NULL;
            long value = strtol(cursor, &end, 0);
            if (end == cursor) {
                break;
            }
            if (value < 0 || value >= V) {
                fprintf(stderr, "generator entry out of range in %s\n", path);
                fclose(file);
                return 0;
            }
            images[got++] = (int)value;
            cursor = end;
        }
        if (got == 0) {
            continue;
        }
        if (got != R || gen_count >= MAX_GENS) {
            fprintf(stderr, "malformed generator line in %s\n", path);
            fclose(file);
            return 0;
        }
        memcpy(gens[gen_count], images, sizeof(images));
        ++gen_count;
    }
    fclose(file);
    if (gen_count == 0) {
        fprintf(stderr, "no generators in %s\n", path);
        return 0;
    }
    /* each generator must be invertible: check rank 10 */
    for (int g = 0; g < gen_count; ++g) {
        int basis[R] = {0};
        int rank = 0;
        for (int i = 0; i < R; ++i) {
            int value = gens[g][i];
            while (value != 0) {
                int pivot = 31 - __builtin_clz((unsigned)value);
                if (basis[pivot]) {
                    value ^= basis[pivot];
                } else {
                    basis[pivot] = value;
                    ++rank;
                    break;
                }
            }
        }
        if (rank != R) {
            fprintf(stderr, "generator %d is singular\n", g);
            return 0;
        }
    }
    return 1;
}

static int cmp_item_order(const void *a, const void *b) {
    int i = *(const int *)a;
    int j = *(const int *)b;
    if (item_size[i] != item_size[j]) {
        return item_size[j] - item_size[i]; /* big orbits first */
    }
    return item_min[i] - item_min[j];
}

static void build_orbits(void) {
    static int orbit_of[V];
    static int queue[V];
    int raw_count = 0;
    for (int v = 0; v < V; ++v) {
        orbit_of[v] = -1;
    }
    for (int v = 1; v < V; ++v) {
        if (orbit_of[v] >= 0) {
            continue;
        }
        int head = 0;
        int tail = 0;
        queue[tail++] = v;
        orbit_of[v] = raw_count;
        while (head < tail) {
            int u = queue[head++];
            for (int g = 0; g < gen_count; ++g) {
                int w = apply_gen(g, u);
                if (orbit_of[w] < 0) {
                    orbit_of[w] = raw_count;
                    queue[tail++] = w;
                }
            }
        }
        ++raw_count;
    }
    /* gather members per raw orbit */
    static int raw_size[MAX_ITEMS];
    static int raw_min[MAX_ITEMS];
    memset(raw_size, 0, sizeof(raw_size));
    for (int i = 0; i < raw_count; ++i) {
        raw_min[i] = V;
    }
    for (int v = 1; v < V; ++v) {
        int o = orbit_of[v];
        ++raw_size[o];
        if (v < raw_min[o]) {
            raw_min[o] = v;
        }
    }
    /* order items: big orbits first, then by min element */
    static int order[MAX_ITEMS];
    for (int i = 0; i < raw_count; ++i) {
        order[i] = i;
        item_size[i] = raw_size[i];
        item_min[i] = raw_min[i];
    }
    qsort(order, (size_t)raw_count, sizeof(order[0]), cmp_item_order);
    static int new_id[MAX_ITEMS];
    static int sorted_size[MAX_ITEMS];
    static int sorted_min[MAX_ITEMS];
    for (int pos = 0; pos < raw_count; ++pos) {
        new_id[order[pos]] = pos;
        sorted_size[pos] = raw_size[order[pos]];
        sorted_min[pos] = raw_min[order[pos]];
    }
    for (int i = 0; i < raw_count; ++i) {
        item_size[i] = sorted_size[i];
        item_min[i] = sorted_min[i];
        item_points[i] = malloc((size_t)item_size[i] * sizeof(int));
        if (item_points[i] == NULL) {
            fprintf(stderr, "out of memory\n");
            exit(2);
        }
    }
    static int fill[MAX_ITEMS];
    memset(fill, 0, sizeof(fill));
    for (int v = 1; v < V; ++v) {
        int o = new_id[orbit_of[v]];
        class_of[v] = o;
        item_points[o][fill[o]++] = v;
    }
    item_count = raw_count;
    words = (item_count + 63) / 64;
    if (words > MAX_W) {
        fprintf(stderr, "too many classes\n");
        exit(2);
    }
    memset(full_mask, 0, sizeof(full_mask));
    for (int c = 0; c < item_count; ++c) {
        full_mask[c >> 6] |= (uint64_t)1 << (c & 63);
    }
}

static inline void mask_set(uint64_t *mask, int c) {
    mask[c >> 6] |= (uint64_t)1 << (c & 63);
}

static void build_masks(void) {
    size_t stride = (size_t)words;
    single_mask = calloc((size_t)item_count * stride, sizeof(uint64_t));
    pair_mask = calloc((size_t)item_count * item_count * stride, sizeof(uint64_t));
    if (single_mask == NULL || pair_mask == NULL) {
        fprintf(stderr, "out of memory for masks\n");
        exit(2);
    }
    for (int i = 0; i < item_count; ++i) {
        uint64_t *mask = single_mask + (size_t)i * stride;
        for (int a = 0; a < item_size[i]; ++a) {
            mask_set(mask, class_of[item_points[i][a]]);
            for (int b = 0; b < a; ++b) {
                int sum = item_points[i][a] ^ item_points[i][b];
                mask_set(mask, class_of[sum]);
            }
        }
    }
    for (int i = 0; i < item_count; ++i) {
        for (int j = 0; j < i; ++j) {
            uint64_t *mask = pair_mask + ((size_t)i * item_count + j) * stride;
            for (int a = 0; a < item_size[i]; ++a) {
                for (int b = 0; b < item_size[j]; ++b) {
                    int sum = item_points[i][a] ^ item_points[j][b];
                    mask_set(mask, class_of[sum]);
                }
            }
            memcpy(pair_mask + ((size_t)j * item_count + i) * stride, mask,
                   stride * sizeof(uint64_t));
        }
    }
    for (int i = 0; i < item_count; ++i) {
        int pop = 0;
        for (int w = 0; w < words; ++w) {
            pop += __builtin_popcountll(single_mask[(size_t)i * stride + w]);
        }
        if (pop > max_single_pop) {
            max_single_pop = pop;
        }
        for (int j = 0; j < i; ++j) {
            int ppop = 0;
            for (int w = 0; w < words; ++w) {
                ppop += __builtin_popcountll(
                    pair_mask[((size_t)i * item_count + j) * stride + w]);
            }
            if (ppop > max_pair_pop) {
                max_pair_pop = ppop;
            }
        }
    }
}

static void build_suffixes(void) {
    size_t stride = (size_t)words;
    ss_suffix = calloc((size_t)(item_count + 1) * stride, sizeof(uint64_t));
    sp_suffix = calloc((size_t)(item_count + 1) * stride, sizeof(uint64_t));
    pt_suffix = calloc((size_t)item_count * (item_count + 1) * stride,
                       sizeof(uint64_t));
    budget_ok = calloc((size_t)(item_count + 1) * (target_n + 1), 1);
    max_items_dp = malloc((size_t)(item_count + 1) * (target_n + 1) * sizeof(int));
    if (ss_suffix == NULL || sp_suffix == NULL || pt_suffix == NULL ||
        budget_ok == NULL || max_items_dp == NULL) {
        fprintf(stderr, "out of memory for suffixes\n");
        exit(2);
    }
    for (int k = item_count - 1; k >= 0; --k) {
        for (int w = 0; w < words; ++w) {
            ss_suffix[(size_t)k * stride + w] =
                ss_suffix[(size_t)(k + 1) * stride + w] |
                single_mask[(size_t)k * stride + w];
        }
    }
    /* sp_suffix[k] = union of pair(i,j) with i>j>=k */
    for (int k = item_count - 1; k >= 0; --k) {
        for (int w = 0; w < words; ++w) {
            uint64_t acc = sp_suffix[(size_t)(k + 1) * stride + w];
            for (int j = k + 1; j < item_count; ++j) {
                acc |= pair_mask[((size_t)j * item_count + k) * stride + w];
            }
            sp_suffix[(size_t)k * stride + w] = acc;
        }
    }
    for (int t = 0; t < item_count; ++t) {
        for (int k = item_count - 1; k >= 0; --k) {
            for (int w = 0; w < words; ++w) {
                uint64_t acc =
                    pt_suffix[((size_t)t * (item_count + 1) + k + 1) * stride + w];
                if (k != t) {
                    acc |= pair_mask[((size_t)t * item_count + k) * stride + w];
                }
                pt_suffix[((size_t)t * (item_count + 1) + k) * stride + w] = acc;
            }
        }
    }
    /* budget DP over item suffixes */
    for (int w = 0; w <= target_n; ++w) {
        budget_ok[(size_t)item_count * (target_n + 1) + w] = (w == 0);
        max_items_dp[(size_t)item_count * (target_n + 1) + w] = (w == 0) ? 0 : -1;
    }
    for (int k = item_count - 1; k >= 0; --k) {
        for (int w = 0; w <= target_n; ++w) {
            unsigned char ok = budget_ok[(size_t)(k + 1) * (target_n + 1) + w];
            int best = max_items_dp[(size_t)(k + 1) * (target_n + 1) + w];
            if (item_size[k] <= w) {
                unsigned char take =
                    budget_ok[(size_t)(k + 1) * (target_n + 1) + w - item_size[k]];
                int take_cnt =
                    max_items_dp[(size_t)(k + 1) * (target_n + 1) + w - item_size[k]];
                if (take) {
                    ok = 1;
                    if (take_cnt + 1 > best) {
                        best = take_cnt + 1;
                    }
                }
            }
            budget_ok[(size_t)k * (target_n + 1) + w] = ok;
            max_items_dp[(size_t)k * (target_n + 1) + w] = best;
        }
    }
}

/* Independent flat re-check of a selection of items (no class logic). */
static int flat_check(const int *sel, int sel_count) {
    static unsigned char covered[V];
    int columns[128];
    int n = 0;
    memset(covered, 0, sizeof(covered));
    covered[0] = 1;
    for (int s = 0; s < sel_count; ++s) {
        for (int a = 0; a < item_size[sel[s]]; ++a) {
            if (n >= 128) {
                return 0;
            }
            columns[n++] = item_points[sel[s]][a];
        }
    }
    for (int i = 0; i < n; ++i) {
        covered[columns[i]] = 1;
        for (int j = 0; j < i; ++j) {
            covered[columns[i] ^ columns[j]] = 1;
        }
    }
    for (int v = 0; v < V; ++v) {
        if (!covered[v]) {
            return 0;
        }
    }
    return 1;
}

static void report_witness(const int *sel, int sel_count) {
    #pragma omp critical
    {
        int ok = flat_check(sel, sel_count);
        ++witnesses_found;
        printf("WITNESS %s: items", ok ? "flat-check-ok" : "FLAT-CHECK-FAILED");
        for (int s = 0; s < sel_count; ++s) {
            printf(" %d(size%d)", sel[s], item_size[sel[s]]);
        }
        printf("\n  columns:");
        for (int s = 0; s < sel_count; ++s) {
            for (int a = 0; a < item_size[sel[s]]; ++a) {
                printf(" %d", item_points[sel[s]][a]);
            }
        }
        printf("\n");
        fflush(stdout);
    }
}

typedef struct {
    uint64_t covered[MAX_W];
    int sel[128];
    int depth;
    int budget;
    long long nodes;
} Ctx;

static void dfs(Ctx *ctx, int start) {
    size_t stride = (size_t)words;
    int done = 1;
    for (int w = 0; w < words; ++w) {
        if ((ctx->covered[w] & full_mask[w]) != full_mask[w]) {
            done = 0;
            break;
        }
    }
    if (done && ctx->budget == 0) {
        report_witness(ctx->sel, ctx->depth);
        return;
    }
    if (done) {
        /* covered with columns to spare: any budget-feasible completion
         * is also a witness (adding columns never uncovers).  Complete
         * greedily via the DP. */
        int k = start;
        int w = ctx->budget;
        int extra_depth = ctx->depth;
        while (w > 0 && k < item_count) {
            if (item_size[k] <= w &&
                budget_ok[(size_t)(k + 1) * (target_n + 1) + w - item_size[k]]) {
                ctx->sel[extra_depth++] = k;
                w -= item_size[k];
            }
            ++k;
        }
        if (w == 0) {
            report_witness(ctx->sel, extra_depth);
        }
        return;
    }
    if (ctx->budget == 0 || start >= item_count) {
        return;
    }
    /* counting bound */
    if (!no_prune) {
        int uncovered = 0;
        for (int w = 0; w < words; ++w) {
            uncovered += __builtin_popcountll(full_mask[w] & ~ctx->covered[w]);
        }
        int q = max_items_dp[(size_t)start * (target_n + 1) + ctx->budget];
        if (q < 0) {
            return; /* budget infeasible */
        }
        long bound = (long)q * max_single_pop +
                     ((long)q * (q - 1) / 2 + (long)q * ctx->depth) *
                         (long)max_pair_pop;
        if (uncovered > bound) {
            return;
        }
        /* reachability */
        for (int w = 0; w < words; ++w) {
            uint64_t reach = ss_suffix[(size_t)start * stride + w] |
                             sp_suffix[(size_t)start * stride + w];
            for (int d = 0; d < ctx->depth; ++d) {
                reach |= pt_suffix[((size_t)ctx->sel[d] * (item_count + 1) + start) *
                                       stride + w];
            }
            if ((full_mask[w] & ~ctx->covered[w]) & ~reach) {
                return;
            }
        }
    }
    for (int i = start; i < item_count; ++i) {
        if (item_size[i] > ctx->budget) {
            continue;
        }
        if (!budget_ok[(size_t)(i + 1) * (target_n + 1) + ctx->budget - item_size[i]]) {
            continue;
        }
        uint64_t saved[MAX_W];
        memcpy(saved, ctx->covered, sizeof(saved));
        for (int w = 0; w < words; ++w) {
            ctx->covered[w] |= single_mask[(size_t)i * stride + w];
        }
        for (int d = 0; d < ctx->depth; ++d) {
            const uint64_t *pm =
                pair_mask + ((size_t)i * item_count + ctx->sel[d]) * stride;
            for (int w = 0; w < words; ++w) {
                ctx->covered[w] |= pm[w];
            }
        }
        ctx->sel[ctx->depth] = i;
        ++ctx->depth;
        ctx->budget -= item_size[i];
        ++ctx->nodes;
        dfs(ctx, i + 1);
        --ctx->depth;
        ctx->budget += item_size[i];
        memcpy(ctx->covered, saved, sizeof(saved));
    }
}

int main(int argc, char **argv) {
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--group") == 0 && i + 1 < argc) {
            group_path = argv[++i];
        } else if (strcmp(argv[i], "--n") == 0 && i + 1 < argc) {
            target_n = (int)strtol(argv[++i], NULL, 0);
        } else if (strcmp(argv[i], "--max-witnesses") == 0 && i + 1 < argc) {
            max_witnesses = (int)strtol(argv[++i], NULL, 0);
        } else if (strcmp(argv[i], "--no-prune") == 0) {
            no_prune = 1;
        } else {
            fprintf(stderr,
                    "usage: %s --group FILE [--n 49] [--max-witnesses K]\n",
                    argv[0]);
            return 2;
        }
    }
    if (group_path == NULL || target_n < 1 || target_n > 120) {
        fprintf(stderr, "need --group FILE and 1<=n<=120\n");
        return 2;
    }
    if (!read_group(group_path)) {
        return 2;
    }
    build_orbits();
    build_masks();
    build_suffixes();
    {
        int size_hist[64] = {0};
        for (int i = 0; i < item_count; ++i) {
            if (item_size[i] < 64) {
                ++size_hist[item_size[i]];
            }
        }
        printf("group=%s generators=%d orbits=%d classes=%d\n", group_path,
               gen_count, item_count, item_count);
        printf("orbit sizes:");
        for (int s = 63; s >= 1; --s) {
            if (size_hist[s]) {
                printf(" %d^%d", s, size_hist[s]);
            }
        }
        printf("\nmax_single_classes=%d max_pair_classes=%d target_n=%d\n",
               max_single_pop, max_pair_pop, target_n);
        if (!budget_ok[0 * (target_n + 1) + target_n]) {
            printf("RESULT group=%s n=%d witnesses=0 nodes=0 "
                   "(budget infeasible: no orbit multiset sums to %d)\n",
                   group_path, target_n, target_n);
            return 0;
        }
        fflush(stdout);
    }
    #pragma omp parallel for schedule(dynamic, 1) num_threads(4)
    for (int first = 0; first < item_count; ++first) {
        Ctx ctx;
        memset(&ctx, 0, sizeof(ctx));
        ctx.budget = target_n;
        if (item_size[first] > ctx.budget) {
            continue;
        }
        if (!budget_ok[(size_t)(first + 1) * (target_n + 1) + ctx.budget -
                       item_size[first]]) {
            continue;
        }
        size_t stride = (size_t)words;
        for (int w = 0; w < words; ++w) {
            ctx.covered[w] = single_mask[(size_t)first * stride + w];
        }
        ctx.sel[0] = first;
        ctx.depth = 1;
        ctx.budget -= item_size[first];
        ctx.nodes = 1;
        dfs(&ctx, first + 1);
        #pragma omp atomic
        total_nodes += ctx.nodes;
    }
    printf("RESULT group=%s n=%d witnesses=%lld nodes=%lld%s\n", group_path,
           target_n, witnesses_found, total_nodes,
           witnesses_found == 0 ? " (exhausted: no invariant covering)" : "");
    return 0;
}
