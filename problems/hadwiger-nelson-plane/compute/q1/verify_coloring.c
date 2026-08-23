#include <stdio.h>
#include <stdlib.h>

static void fail(const char *message) {
    fprintf(stderr, "error: %s\n", message);
    exit(1);
}

int main(int argc, char **argv) {
    if (argc != 5) {
        fprintf(stderr, "usage: %s graph.edge coloring.txt expected_n expected_m\n", argv[0]);
        return 2;
    }
    const int expected_n = atoi(argv[3]);
    const int expected_m = atoi(argv[4]);
    FILE *edge_file = fopen(argv[1], "r");
    FILE *color_file = fopen(argv[2], "r");
    if (edge_file == NULL || color_file == NULL) fail("cannot open input");

    char p = 0;
    char word[16] = {0};
    int n = 0, m = 0;
    if (fscanf(edge_file, " %c %15s %d %d", &p, word, &n, &m) != 4 ||
        p != 'p' || n != expected_n || m != expected_m) {
        fail("bad or unexpected edge header");
    }
    int *colors = malloc((size_t)n * sizeof(*colors));
    if (colors == NULL) fail("allocation failed");
    int counts[5] = {0, 0, 0, 0, 0};
    for (int i = 0; i < n; ++i) {
        if (fscanf(color_file, "%d", &colors[i]) != 1) fail("too few colors");
        if (colors[i] < 0 || colors[i] >= 5) fail("color outside 0..4");
        ++counts[colors[i]];
    }
    int extra = 0;
    if (fscanf(color_file, "%d", &extra) == 1) fail("too many colors");

    int seen = 0;
    for (;;) {
        char e = 0;
        int left = 0, right = 0;
        int got = fscanf(edge_file, " %c %d %d", &e, &left, &right);
        if (got == EOF) break;
        if (got != 3 || e != 'e') fail("malformed edge line");
        if (left < 1 || left > n || right < 1 || right > n || left >= right) {
            fail("invalid edge endpoints");
        }
        if (colors[left - 1] == colors[right - 1]) fail("monochromatic edge");
        ++seen;
    }
    if (seen != m) fail("edge count differs from header");
    printf("%s: C checker verified n=%d m=%d counts=%d,%d,%d,%d,%d\n",
           argv[1], n, m, counts[0], counts[1], counts[2], counts[3], counts[4]);
    free(colors);
    fclose(edge_file);
    fclose(color_file);
    return 0;
}
