/*
 * q4: exhaustive k-swap prover / LNS searcher for 49-column radius-2
 * coverings of F_2^10.
 *
 * Input: a 49-column configuration (text file, 49 integers in 1..1023,
 * whitespace separated; lines starting with '#' ignored).
 *
 * --prove K: exhaustively decide whether some swap of at most K columns
 *   (remove j <= K, add j new distinct nonzero columns) reaches zero
 *   uncovered syndromes.  For each removal set, the re-add search
 *   branches on the first live hole h; any full cover must cover h by a
 *   fresh column c with c = h, c ^ h kept, c ^ h an earlier fresh
 *   column, or by a pair of two later fresh columns.  The last case is
 *   handled by an explicit defer branch: deferred holes (at most
 *   C(j,2) of them) are resolved in an exact endgame that enumerates
 *   anchored fresh columns (values forced by pairing with kept/placed
 *   columns, closed under hole-XOR chains up to the slot budget) and
 *   recognizes fully floating pair components, which are always
 *   placeable by translation in a space this empty.  If the program
 *   prints NO-KSWAP, no such swap exists (a replayable certificate for
 *   the given input configuration).
 *
 * Build:
 *   gcc -O3 -std=c11 -Wall -Wextra compute/q4/kswap.c -lm \
 *       -o compute/q4/kswap
 */

#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifndef N_COLS
#define N_COLS 49
#endif

enum { R = 10, V = 1 << R, N = N_COLS };

static int columns[N];
static int counts[V];          /* representation multiplicities */
static unsigned char member[V];
static int prove_k = 0;
static const char *input_path = NULL;
static const char *emit_path = NULL;
static long long readd_nodes = 0;

static int read_columns(const char *path) {
    FILE *file = fopen(path, "r");
    char line[8192];
    int got = 0;
    if (file == NULL) {
        fprintf(stderr, "cannot open %s: %s\n", path, strerror(errno));
        return 0;
    }
    while (fgets(line, sizeof(line), file) != NULL) {
        char *cursor = line;
        if (line[0] == '#') {
            continue;
        }
        while (got <= N) {
            char *end = NULL;
            long value = strtol(cursor, &end, 0);
            if (end == cursor) {
                break;
            }
            if (value < 1 || value >= V || got >= N) {
                fprintf(stderr, "bad column list in %s\n", path);
                fclose(file);
                return 0;
            }
            columns[got++] = (int)value;
            cursor = end;
        }
    }
    fclose(file);
    if (got != N) {
        fprintf(stderr, "expected %d columns, got %d\n", N, got);
        return 0;
    }
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < i; ++j) {
            if (columns[i] == columns[j]) {
                fprintf(stderr, "repeated column %d\n", columns[i]);
                return 0;
            }
        }
    }
    return 1;
}

static void rebuild_counts(void) {
    memset(counts, 0, sizeof(counts));
    memset(member, 0, sizeof(member));
    counts[0] = 1;
    for (int i = 0; i < N; ++i) {
        member[columns[i]] = 1;
        ++counts[columns[i]];
        for (int j = 0; j < i; ++j) {
            ++counts[columns[i] ^ columns[j]];
        }
    }
}

static int hole_count(void) {
    int holes = 0;
    for (int v = 0; v < V; ++v) {
        if (counts[v] == 0) {
            ++holes;
        }
    }
    return holes;
}

/* ---- exact re-add search ---------------------------------------- */

/* kept[] has nk columns; we may place up to slots new columns; holes[]
 * lists syndromes currently uncovered by kept (and by already-placed
 * new columns).  Returns 1 and fills added[] if full cover possible. */

static int kept[N];
static int nk;
static unsigned char kept_member[V];
static int added[8];
static int n_added;
static int slots_total;

static int hole_covered_by_added(int h) {
    for (int a = 0; a < n_added; ++a) {
        if (added[a] == h) {
            return 1;
        }
        for (int b = 0; b < a; ++b) {
            if ((added[a] ^ added[b]) == h) {
                return 1;
            }
        }
        if (kept_member[added[a] ^ h]) {
            return 1;
        }
    }
    return 0;
}

static int value_in_added(int c) {
    for (int a = 0; a < n_added; ++a) {
        if (added[a] == c) {
            return 1;
        }
    }
    return 0;
}

static int value_usable(int c) {
    return c > 0 && c < V && !kept_member[c] && !value_in_added(c);
}

/* --- endgame: every remaining deferred hole must be the XOR of two
 * fresh columns (possibly one of them already placed).  Fresh columns
 * come in two kinds: anchored (value forced by pairing with a placed
 * column, or by a chain of hole-XORs from an anchored value) and
 * floating (a whole pair component whose absolute position is free).
 * Floating components of total size s cover exactly the pairwise XORs
 * of an offset set {0, l_1, ..., l_{s-1}}; the absolute position can
 * always be chosen because at most 53 + 4 of the 1024 points are in
 * use, and a component of size s <= 4 excludes at most s * 58 + s
 * positions.  So a floating component is feasible iff the offset
 * multiset exists; no concrete placement is needed for the proof. */

static int float_holes_ref[16];
static int float_nh_ref;

static int float_rec(int cn, int *offs, int slots) {
    int all = 1;
    for (int i = 0; i < float_nh_ref; ++i) {
        int cov = 0;
        for (int a = 0; a < cn && !cov; ++a) {
            for (int b = 0; b < a; ++b) {
                if ((offs[a] ^ offs[b]) == float_holes_ref[i]) {
                    cov = 1;
                    break;
                }
            }
        }
        if (!cov) {
            all = 0;
            break;
        }
    }
    if (all) {
        return 1;
    }
    if (cn >= slots) {
        return 0;
    }
    /* a useful next offset must equal hole ^ existing-offset */
    for (int i = 0; i < float_nh_ref; ++i) {
        for (int a = 0; a < cn; ++a) {
            int cand = float_holes_ref[i] ^ offs[a];
            int dup = (cand == 0);
            for (int t = 0; t < cn && !dup; ++t) {
                dup = (offs[t] == cand);
            }
            if (dup) {
                continue;
            }
            offs[cn] = cand;
            if (float_rec(cn + 1, offs, slots)) {
                return 1;
            }
        }
    }
    return 0;
}

static int float_embeds(const int *holes, int nh, int slots) {
    /* Can nh holes be covered by pairwise XORs of `slots` fresh columns
     * whose absolute position is otherwise free?  WLOG offsets start
     * {0, holes[0]} (translate the component so one endpoint of the
     * pair covering holes[0] sits at offset 0).  A multi-component
     * solution merges into one offset pool without loss.  Concrete
     * placement always exists: at most 4 * 54 of the 1024 translates
     * collide with used values. */
    int offs[8];
    if (nh <= 0) {
        return 1;
    }
    if (slots < 2 || nh > 6) {
        return 0;
    }
    memcpy(float_holes_ref, holes, (size_t)(nh > 16 ? 16 : nh) * sizeof(int));
    float_nh_ref = nh;
    offs[0] = 0;
    offs[1] = holes[0];
    return float_rec(2, offs, slots);
}

static int endgame(const int *deferred, int nd) {
    ++readd_nodes;
    /* refilter deferred against current placements */
    int live[16];
    int m = 0;
    for (int i = 0; i < nd; ++i) {
        if (!hole_covered_by_added(deferred[i])) {
            if (m >= 16) {
                return 0;
            }
            live[m++] = deferred[i];
        }
    }
    if (m == 0) {
        return 1;
    }
    int slots = slots_total - n_added;
    if (slots <= 0) {
        return 0;
    }
    int h = live[0];
    /* case 1: fresh column pairing with an already-placed column */
    for (int a = 0; a < n_added; ++a) {
        int c = h ^ added[a];
        if (value_usable(c)) {
            added[n_added++] = c;
            if (endgame(live, m)) {
                return 1;
            }
            --n_added;
        }
    }
    /* case 2: anchored fresh pair (f1 anchored, f2 = h ^ f1).
     * Anchors: f1 covers some live hole h' directly (f1 = h', f1 =
     * h' ^ kept, f1 = h' ^ placed) or via a chain f1 = h' ^ f3 with f3
     * anchored - chains are captured by closing the anchor set with
     * hole-XORs as long as slots allow. */
    if (slots >= 2) {
        /* local: recursive endgame calls below must not clobber it */
        int anchors[65536];
        int na = 0;
        for (int i = 0; i < m; ++i) {
            int hp = live[i];
            anchors[na++] = hp;
            for (int t = 0; t < nk; ++t) {
                anchors[na++] = hp ^ kept[t];
            }
            for (int a = 0; a < n_added; ++a) {
                anchors[na++] = hp ^ added[a];
            }
        }
        int level1_end = na;
        if (slots >= 3) {
            /* chain level 1: h' ^ anchor */
            for (int i = 0; i < m; ++i) {
                for (int t = 0; t < level1_end && na < 65000; ++t) {
                    anchors[na++] = live[i] ^ anchors[t];
                }
            }
        }
        if (slots >= 4) {
            /* chain level 2: h'' ^ (h' ^ anchor); enough for any
             * anchored component of at most 4 fresh columns */
            int level2_start = level1_end;
            int level2_end = na;
            for (int i = 0; i < m; ++i) {
                for (int t = level2_start; t < level2_end && na < 65000; ++t) {
                    anchors[na++] = live[i] ^ anchors[t];
                }
            }
        }
        for (int t = 0; t < na; ++t) {
            int f1 = anchors[t];
            int f2 = h ^ f1;
            if (f1 == f2 || !value_usable(f1)) {
                continue;
            }
            added[n_added++] = f1;
            if (!value_usable(f2)) {
                --n_added;
                continue;
            }
            added[n_added++] = f2;
            if (endgame(live, m)) {
                return 1;
            }
            n_added -= 2;
        }
    }
    /* case 3: everything left is floating: all remaining live holes
     * covered by pairwise XORs of the remaining free columns. */
    return float_embeds(live, m, slots);
}

static int readd_dfs(const int *holes, int nh, const int *deferred, int nd) {
    ++readd_nodes;
    /* drop holes now covered by placed columns */
    int live[V];
    int defer_live[16] = {0};
    int m = 0;
    int dm = 0;
    for (int i = 0; i < nd; ++i) {
        if (!hole_covered_by_added(deferred[i])) {
            if (dm >= 16) {
                return 0;
            }
            defer_live[dm++] = deferred[i];
        }
    }
    for (int i = 0; i < nh; ++i) {
        if (!hole_covered_by_added(holes[i])) {
            live[m++] = holes[i];
        }
    }
    if (m == 0) {
        return endgame(defer_live, dm);
    }
    if (n_added == slots_total) {
        return 0;
    }
    int h = live[0];
    int cand[N + 12];
    int nc = 0;
    if (!kept_member[h]) {
        cand[nc++] = h;
    }
    for (int i = 0; i < nk; ++i) {
        int c = h ^ kept[i];
        if (c != 0 && !kept_member[c]) {
            cand[nc++] = c;
        }
    }
    for (int a = 0; a < n_added; ++a) {
        int c = h ^ added[a];
        if (c != 0 && !kept_member[c]) {
            cand[nc++] = c;
        }
    }
    for (int i = 0; i < nc; ++i) {
        int c = cand[i];
        if (!value_usable(c)) {
            continue;
        }
        added[n_added++] = c;
        if (readd_dfs(live + 1, m - 1, defer_live, dm)) {
            return 1;
        }
        --n_added;
    }
    /* defer h: it will be covered by a pair of two later fresh columns.
     * At most C(slots_total,2) holes can be deferred in total. */
    if (dm + 1 <= slots_total * (slots_total - 1) / 2) {
        defer_live[dm] = h;
        if (readd_dfs(live + 1, m - 1, defer_live, dm + 1)) {
            return 1;
        }
    }
    return 0;
}

static int try_removal(const int *remove_idx, int j, int *witness_out) {
    static unsigned char removed_mark[N];
    memset(removed_mark, 0, sizeof(removed_mark));
    for (int i = 0; i < j; ++i) {
        removed_mark[remove_idx[i]] = 1;
    }
    nk = 0;
    memset(kept_member, 0, sizeof(kept_member));
    for (int i = 0; i < N; ++i) {
        if (!removed_mark[i]) {
            kept[nk++] = columns[i];
            kept_member[columns[i]] = 1;
        }
    }
    /* holes of the kept set, from scratch */
    static unsigned char covered[V];
    memset(covered, 0, sizeof(covered));
    covered[0] = 1;
    for (int i = 0; i < nk; ++i) {
        covered[kept[i]] = 1;
        for (int t = 0; t < i; ++t) {
            covered[kept[i] ^ kept[t]] = 1;
        }
    }
    int holes[V];
    int nh = 0;
    for (int v = 0; v < V; ++v) {
        if (!covered[v]) {
            holes[nh++] = v;
        }
    }
    n_added = 0;
    slots_total = j;
    if (readd_dfs(holes, nh, NULL, 0)) {
        /* pad with unused columns if fewer than j were needed */
        int next = 1;
        while (n_added < j) {
            while (next < V) {
                int used = kept_member[next];
                for (int a = 0; a < n_added && !used; ++a) {
                    used = (added[a] == next);
                }
                if (!used) {
                    break;
                }
                ++next;
            }
            added[n_added++] = next++;
        }
        int w = 0;
        for (int i = 0; i < nk; ++i) {
            witness_out[w++] = kept[i];
        }
        for (int a = 0; a < j; ++a) {
            witness_out[w++] = added[a];
        }
        return 1;
    }
    return 0;
}

static void emit_witness(const int *witness) {
    printf("WITNESS columns:");
    for (int i = 0; i < N; ++i) {
        printf(" %d", witness[i]);
    }
    printf("\n");
    if (emit_path != NULL) {
        FILE *f = fopen(emit_path, "w");
        if (f != NULL) {
            fprintf(f, "# q4 kswap witness candidate (verify independently)\n");
            for (int i = 0; i < N; ++i) {
                fprintf(f, "%d\n", witness[i]);
            }
            fclose(f);
        }
    }
}

static int prove(void) {
    int witness[N];
    for (int j = 1; j <= prove_k; ++j) {
        long long sets = 0;
        int idx[8];
        for (int i = 0; i < j; ++i) {
            idx[i] = i;
        }
        for (;;) {
            ++sets;
            if (try_removal(idx, j, witness)) {
                printf("KSWAP-FOUND j=%d after %lld removal sets\n", j, sets);
                emit_witness(witness);
                return 1;
            }
            int p = j - 1;
            while (p >= 0 && idx[p] == N - j + p) {
                --p;
            }
            if (p < 0) {
                break;
            }
            ++idx[p];
            for (int t = p + 1; t < j; ++t) {
                idx[t] = idx[t - 1] + 1;
            }
        }
        printf("NO-KSWAP j=%d removal_sets=%lld readd_nodes=%lld\n", j, sets,
               readd_nodes);
        fflush(stdout);
    }
    return 0;
}

int main(int argc, char **argv) {
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--input") == 0 && i + 1 < argc) {
            input_path = argv[++i];
        } else if (strcmp(argv[i], "--prove") == 0 && i + 1 < argc) {
            prove_k = (int)strtol(argv[++i], NULL, 0);
        } else if (strcmp(argv[i], "--emit") == 0 && i + 1 < argc) {
            emit_path = argv[++i];
        } else {
            fprintf(stderr,
                    "usage: %s --input COLS --prove K [--emit PATH]\n",
                    argv[0]);
            return 2;
        }
    }
    if (input_path == NULL || !read_columns(input_path)) {
        return 2;
    }
    rebuild_counts();
    printf("loaded %s holes=%d\n", input_path, hole_count());
    if (prove_k > 0) {
        return prove() ? 0 : 1;
    }
    fprintf(stderr, "nothing to do\n");
    return 2;
}
