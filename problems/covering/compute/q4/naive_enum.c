/*
 * q4 cross-check: naive enumerator of group-invariant n-column coverings.
 *
 * Same input format as orbit_dfs.c, but written independently and kept
 * deliberately dumb: enumerate every union of orbits with total size n
 * (only budget feasibility, no coverage pruning), and test coverage by
 * a from-scratch flat pair enumeration over all 1024 syndromes.  Used
 * to validate orbit_dfs on small cases: witness counts must agree.
 *
 * Build:
 *   gcc -O2 -std=c11 -Wall -Wextra compute/q4/naive_enum.c \
 *       -o compute/q4/naive_enum
 */

#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { R = 10, V = 1 << R, MAX_GENS = 4 };

static int target_n = 49;
static int gen_count = 0;
static int gens[MAX_GENS][R];
static int orbit_id[V];
static int orbit_count = 0;
static int orbit_size[V];
static int *orbit_members[V];
static long long leaves = 0;
static long long witnesses = 0;

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
    while (fgets(line, sizeof(line), file) != NULL) {
        char *cursor = line;
        int images[R];
        int got = 0;
        if (line[0] == '#' || line[0] == '\n') {
            continue;
        }
        while (got < R) {
            char *end = NULL;
            long value = strtol(cursor, &end, 0);
            if (end == cursor) {
                break;
            }
            images[got++] = (int)value;
            cursor = end;
        }
        if (got == 0) {
            continue;
        }
        if (got != R || gen_count >= MAX_GENS) {
            fclose(file);
            return 0;
        }
        memcpy(gens[gen_count++], images, sizeof(images));
    }
    fclose(file);
    return gen_count > 0;
}

static void build_orbits(void) {
    static int queue[V];
    for (int v = 0; v < V; ++v) {
        orbit_id[v] = -1;
    }
    for (int v = 1; v < V; ++v) {
        if (orbit_id[v] >= 0) {
            continue;
        }
        int head = 0;
        int tail = 0;
        queue[tail++] = v;
        orbit_id[v] = orbit_count;
        while (head < tail) {
            int u = queue[head++];
            for (int g = 0; g < gen_count; ++g) {
                int w = apply_gen(g, u);
                if (orbit_id[w] < 0) {
                    orbit_id[w] = orbit_count;
                    queue[tail++] = w;
                }
            }
        }
        ++orbit_count;
    }
    for (int o = 0; o < orbit_count; ++o) {
        orbit_size[o] = 0;
    }
    for (int v = 1; v < V; ++v) {
        ++orbit_size[orbit_id[v]];
    }
    for (int o = 0; o < orbit_count; ++o) {
        orbit_members[o] = malloc((size_t)orbit_size[o] * sizeof(int));
        orbit_size[o] = 0;
    }
    for (int v = 1; v < V; ++v) {
        int o = orbit_id[v];
        orbit_members[o][orbit_size[o]++] = v;
    }
}

static int chosen[V];

static void check_leaf(int depth) {
    static unsigned char covered[V];
    int columns[128];
    int n = 0;
    ++leaves;
    memset(covered, 0, sizeof(covered));
    covered[0] = 1;
    for (int d = 0; d < depth; ++d) {
        int o = chosen[d];
        for (int a = 0; a < orbit_size[o]; ++a) {
            columns[n++] = orbit_members[o][a];
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
            return;
        }
    }
    ++witnesses;
    printf("NAIVE-WITNESS orbits");
    for (int d = 0; d < depth; ++d) {
        printf(" %d", chosen[d]);
    }
    printf(" columns");
    for (int i = 0; i < n; ++i) {
        printf(" %d", columns[i]);
    }
    printf("\n");
}

static void rec(int start, int depth, int budget) {
    if (budget == 0) {
        check_leaf(depth);
        return;
    }
    for (int o = start; o < orbit_count; ++o) {
        if (orbit_size[o] > budget) {
            continue;
        }
        chosen[depth] = o;
        rec(o + 1, depth + 1, budget - orbit_size[o]);
    }
}

int main(int argc, char **argv) {
    const char *path = NULL;
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--group") == 0 && i + 1 < argc) {
            path = argv[++i];
        } else if (strcmp(argv[i], "--n") == 0 && i + 1 < argc) {
            target_n = (int)strtol(argv[++i], NULL, 0);
        } else {
            fprintf(stderr, "usage: %s --group FILE [--n 49]\n", argv[0]);
            return 2;
        }
    }
    if (path == NULL || !read_group(path)) {
        return 2;
    }
    build_orbits();
    printf("naive: group=%s orbits=%d n=%d\n", path, orbit_count, target_n);
    rec(0, 0, target_n);
    printf("NAIVE-RESULT group=%s n=%d witnesses=%lld leaves=%lld\n", path,
           target_n, witnesses, leaves);
    return 0;
}
