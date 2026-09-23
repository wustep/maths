/* Exact existence search for all 3-delete/2-add switches of the 50-set.
 * For each first insertion x, the second y must cover the first remaining
 * syndrome h, so y belongs to {h, h^x} union {h^b: b in base}.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int col[50];
static unsigned char seen[1024], base_present[1024], covered[1024];

static void read_matrix(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) { perror(path); exit(2); }
    char line[4096]; int row = 0;
    while (fgets(line, sizeof line, f)) {
        if (line[0] == '#') continue;
        char *p = line;
        for (int j = 0; j < 50; j++) {
            char *end; long bit = strtol(p, &end, 10);
            if (end == p || (bit != 0 && bit != 1)) { fprintf(stderr, "bad matrix\n"); exit(2); }
            col[j] |= (int)bit << row; p = end;
        }
        while (*p == ' ' || *p == '\t' || *p == '\r' || *p == '\n') p++;
        if (*p || ++row > 10) { fprintf(stderr, "bad matrix shape\n"); exit(2); }
    }
    fclose(f);
    if (row != 10) { fprintf(stderr, "expected 10 rows\n"); exit(2); }
    for (int j = 0; j < 50; j++) {
        if (!col[j] || seen[col[j]]) { fprintf(stderr, "duplicate or zero column\n"); exit(2); }
        seen[col[j]] = 1;
    }
}

int main(int argc, char **argv) {
    if (argc != 2) { fprintf(stderr, "usage: %s H_r10_n50.txt\n", argv[0]); return 2; }
    read_matrix(argv[1]);
    long long triples = 0, first_insertions = 0, second_candidates = 0;
    int min_base_holes = 1024, min_after_first = 1024;
    for (int a = 0; a < 50; a++) for (int b = a + 1; b < 50; b++)
    for (int c = b + 1; c < 50; c++) {
        triples++;
        int base[47], n = 0;
        memset(base_present, 0, sizeof base_present);
        for (int j = 0; j < 50; j++) if (j != a && j != b && j != c) {
            base[n++] = col[j]; base_present[col[j]] = 1;
        }
        memset(covered, 0, sizeof covered); covered[0] = 1;
        for (int j = 0; j < 47; j++) {
            covered[base[j]] = 1;
            for (int k = 0; k < j; k++) covered[base[j] ^ base[k]] = 1;
        }
        int holes[1024], nh = 0;
        for (int s = 0; s < 1024; s++) if (!covered[s]) holes[nh++] = s;
        if (nh < min_base_holes) min_base_holes = nh;
        for (int x = 1; x < 1024; x++) {
            if (base_present[x]) continue;
            first_insertions++;
            int remaining[1024], nr = 0;
            for (int k = 0; k < nh; k++) {
                int h = holes[k];
                if (h != x && !base_present[h ^ x]) remaining[nr++] = h;
            }
            if (nr < min_after_first) min_after_first = nr;
            if (!nr) { fprintf(stderr, "unexpected 48-cover: delete %d %d %d, insert %d\n", a,b,c,x); return 3; }
            int h = remaining[0];
            int candidates[49], nc = 0;
            candidates[nc++] = h;
            candidates[nc++] = h ^ x;
            for (int j = 0; j < 47; j++) candidates[nc++] = h ^ base[j];
            for (int k = 0; k < nc; k++) {
                int y = candidates[k];
                if (!y || y == x || base_present[y]) continue;
                second_candidates++;
                int t;
                for (t = 1; t < nr; t++) {
                    int s = remaining[t];
                    if (s != y && s != (x ^ y) && !base_present[s ^ y]) break;
                }
                if (t == nr) {
                    printf("FOUND delete_indices_0based=%d,%d,%d insert=%d,%d\n",a,b,c,x,y);
                    return 0;
                }
            }
        }
    }
    printf("NO_COVER triples=%lld first_insertions=%lld second_candidates=%lld min_base_holes=%d min_after_first=%d\n", triples, first_insertions, second_candidates, min_base_holes, min_after_first);
    return 0;
}
