/* Exhaust the 2-delete/1-add neighborhood of the published 50-set.
 * Build: cc -O3 -Wall -Wextra -o /tmp/q14_switch switch_2to1.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int col[50];
static unsigned char covered[1024], present[1024];

static void read_matrix(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) { perror(path); exit(2); }
    char line[4096];
    int row = 0;
    while (fgets(line, sizeof line, f)) {
        if (line[0] == '#') continue;
        char *p = line;
        for (int j = 0; j < 50; j++) {
            char *end;
            long bit = strtol(p, &end, 10);
            if (end == p || (bit != 0 && bit != 1)) { fprintf(stderr, "bad row %d column %d\n", row, j); exit(2); }
            col[j] |= (int)bit << row;
            p = end;
        }
        while (*p == ' ' || *p == '\t' || *p == '\r' || *p == '\n') p++;
        if (*p || ++row > 10) { fprintf(stderr, "bad matrix shape\n"); exit(2); }
    }
    fclose(f);
    if (row != 10) { fprintf(stderr, "expected 10 rows\n"); exit(2); }
    memset(present, 0, sizeof present);
    for (int j = 0; j < 50; j++) {
        if (!col[j] || present[col[j]]) { fprintf(stderr, "duplicate or zero column\n"); exit(2); }
        present[col[j]] = 1;
    }
}

static int rank49(int a, int b, int x) {
    int basis[10] = {0}, rank = 0;
    for (int j = 0; j <= 50; j++) {
        if (j == a || j == b) continue;
        int v = j == 50 ? x : col[j];
        while (v) {
            int k = 31 - __builtin_clz((unsigned)v);
            if (basis[k]) v ^= basis[k];
            else { basis[k] = v; rank++; break; }
        }
    }
    return rank;
}

int main(int argc, char **argv) {
    if (argc != 2) { fprintf(stderr, "usage: %s H_r10_n50.txt\n", argv[0]); return 2; }
    read_matrix(argv[1]);
    long long tested = 0;
    int best = -1, best_a = -1, best_b = -1, best_x = -1;
    int base_holes_min = 1024, rank_bad = 0;
    for (int a = 0; a < 50; a++) for (int b = a + 1; b < 50; b++) {
        int base[48], n = 0;
        for (int j = 0; j < 50; j++) if (j != a && j != b) base[n++] = col[j];
        memset(covered, 0, sizeof covered);
        covered[0] = 1;
        for (int j = 0; j < 48; j++) {
            covered[base[j]] = 1;
            for (int k = 0; k < j; k++) covered[base[j] ^ base[k]] = 1;
        }
        int holes[1024], nh = 0;
        for (int s = 0; s < 1024; s++) if (!covered[s]) holes[nh++] = s;
        if (nh < base_holes_min) base_holes_min = nh;
        for (int x = 1; x < 1024; x++) {
            if (present[x] && x != col[a] && x != col[b]) continue;
            int fixed = 0;
            for (int h = 0; h < nh; h++) {
                int s = holes[h];
                if (s == x) { fixed++; continue; }
                for (int j = 0; j < 48; j++) if ((x ^ base[j]) == s) { fixed++; break; }
            }
            int remaining = nh - fixed;
            tested++;
            if (best < 0 || remaining < best) {
                best = remaining; best_a = a; best_b = b; best_x = x;
            }
            if (remaining == 0 && rank49(a, b, x) != 10) rank_bad++;
        }
    }
    printf("pairs=1225 candidates=%lld base_holes_min=%d best_holes=%d rank_bad_zero_hole=%d\n", tested, base_holes_min, best, rank_bad);
    printf("best_delete_indices_0based=%d,%d best_insert=%d\n", best_a, best_b, best_x);
    return 0;
}
