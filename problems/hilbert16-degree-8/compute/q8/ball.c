/* Finite sign neighborhoods. Exact balanced-parenthesis tree keys, no hash
 * collisions. The search topology engine is inherited; proof verification
 * must also use the independent implementations described in CLAIM.md. */
#define TCORE_MAX_CHILDREN 64
#include "../tcore.h"

static uint64_t known[4096], keys[16384], counts[16384], evals;
static int nknown, radius, trace;

static int ucmp(const void *a, const void *b) {
    uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b;
    return (x > y) - (x < y);
}
static uint64_t pack(uint64_t *children, int n) {
    qsort(children, n, sizeof(uint64_t), ucmp);
    uint64_t code = 1;
    for (int i = 0; i < n; ++i) {
        int width = 64 - __builtin_clzll(children[i]);
        if (64 - __builtin_clzll(code) + width + 1 > 63) abort();
        code = (code << width) | children[i];
    }
    return code << 1;
}
static uint64_t code_node(int node) {
    uint64_t children[64]; int n = 0;
    for (int k = tree_head[node]; k >= 0; k = tree_next[k])
        children[n++] = code_node(k);
    return pack(children, n);
}
static void visit(void) {
    int ok; H128 fp;
    int nc = evaluate(cursign, &ok, &fp);
    if (!ok || nc > 22) { fprintf(stderr, "invalid topology\n"); exit(2); }
    uint64_t children[64]; int n = 0;
    for (int c = 0; c < nc; c++)
        if (reg_lift[parent_reg[c]] == 1) children[n++] = code_node(c);
    uint64_t code = pack(children, n);
    evals++;
    unsigned j = (unsigned)mix64(code) & 16383;
    while (keys[j] && keys[j] != code) j = (j + 1) & 16383;
    int first = !keys[j];
    keys[j] = code; counts[j]++;
    if (trace || (first && !bsearch(&code, known, nknown, sizeof(uint64_t), ucmp))) {
        uint64_t bits = 0;
        for (int p = 0; p < npts; p++) if (cursign[p] < 0) bits |= 1ULL << p;
        printf("{\"kind\":\"witness\",\"code\":%" PRIu64 ",\"bits\":%" PRIu64 "}\n", code, bits);
        fflush(stdout);
    }
}
static void dfs(int first, int depth) {
    visit();
    if (depth == radius) return;
    for (int i = first; i < npts; i++) {
        cursign[i] = -cursign[i];
        dfs(i + 1, depth + 1);
        cursign[i] = -cursign[i];
    }
}
int main(int argc, char **argv) {
    if (argc < 3 || argc > 4) return 2;
    radius = atoi(argv[2]); trace = argc == 4 && !strcmp(argv[3], "trace");
    if (radius < 0 || radius > 6) return 2;
    FILE *f = load_task(argv[1]);
    if (npts != 45 || F != 256) return 2;
    int ns; char tag[32];
    if (fscanf(f, "%31s %d", tag, &ns) != 2 || strcmp(tag, "SEEDS") || ns != 1) return 2;
    for (int p = 0; p < npts; p++) {
        int x; need(f, 1, &x); if (x != 1 && x != -1) return 2;
        cursign[p] = x;
    }
    if (fscanf(f, "%31s %d", tag, &nknown) != 2 || strcmp(tag, "KNOWN") || nknown > 4096 || nknown < 0) return 2;
    for (int i = 0; i < nknown; i++) if (fscanf(f, "%" SCNu64, &known[i]) != 1) return 2;
    fclose(f); qsort(known, nknown, sizeof(uint64_t), ucmp);
    dfs(0, 0);
    printf("{\"kind\":\"summary\",\"complete\":true,\"evals\":%" PRIu64 ",\"counts\":[", evals);
    int sep = 0;
    for (int j = 0; j < 16384; j++) if (keys[j]) {
        printf("%s[%" PRIu64 ",%" PRIu64 "]", sep ? "," : "", keys[j], counts[j]); sep = 1;
    }
    puts("]}");
    return 0;
}
