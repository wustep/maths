/* Exact one-merge test for q13's 34-block (3,0) partition.
 * Build from the problem folder: cc -O3 -std=c11 search_merges.c -o /tmp/search_merges
 * At most ~300 MiB RAM. No SAT or incomplete cutoffs.
 */
#define main q13_original_main
#include "../q13/verify_q13.c"
#undef main

static uint16_t *total, *bad;
static uint8_t *short_cover;
static uint32_t *touched;
static uint32_t col[SEED_N];
static int label[SEED_N], members[COARSE_P][SEED_N], sizes[COARSE_P];

static void add_total(uint32_t syndrome)
{
    if (total[syndrome] == UINT16_MAX - 1)
        fail("three-sum multiplicity overflow at %u", syndrome);
    ++total[syndrome];
}

int main(int argc, char **argv)
{
    if (argc != 3)
        fail("usage: search_merges seed_matrix partition");
    uint64_t *raw = read_matrix(argv[1], SEED_R, SEED_N);
    int *raw_labels = read_partition(argv[2], SEED_N);
    count_blocks(raw_labels, SEED_N, COARSE_P);
    verify_columns(raw, SEED_N, SEED_R, "seed");
    const uint32_t space = UINT32_C(1) << SEED_R;
    total = calloc(space, sizeof(*total));
    bad = calloc(space, sizeof(*bad));
    short_cover = calloc(space, sizeof(*short_cover));
    touched = malloc((size_t)space * sizeof(*touched));
    if (!total || !bad || !short_cover || !touched)
        fail("allocation failed");
    short_cover[0] = 1;
    for (int i = 0; i < SEED_N; ++i) {
        col[i] = (uint32_t)raw[i];
        label[i] = raw_labels[i];
        members[label[i]][sizes[label[i]]++] = i;
        short_cover[col[i]] = 1;
        for (int j = 0; j < i; ++j)
            if (label[i] != label[j])
                short_cover[col[i] ^ col[j]] = 1;
    }
    free(raw);
    free(raw_labels);

    uint64_t triples = 0;
    for (int a = 0; a < COARSE_P; ++a)
        for (int b = a + 1; b < COARSE_P; ++b)
            for (int c = b + 1; c < COARSE_P; ++c)
                for (int ia = 0; ia < sizes[a]; ++ia)
                    for (int ib = 0; ib < sizes[b]; ++ib)
                        for (int ic = 0; ic < sizes[c]; ++ic) {
                            add_total(col[members[a][ia]] ^ col[members[b][ib]] ^
                                      col[members[c][ic]]);
                            ++triples;
                        }
    uint32_t uncovered = 0;
    for (uint32_t s = 0; s < space; ++s)
        if (!short_cover[s] && !total[s]) ++uncovered;
    printf("seed triples=%" PRIu64 " uncovered=%u\n", triples, uncovered);
    if (uncovered) fail("input partition is not (3,0)");

    int viable = 0, rejected = 0;
    uint64_t min_lost = UINT64_MAX;
    int best_a = -1, best_b = -1;
    for (int a = 0; a < COARSE_P; ++a)
        for (int b = a + 1; b < COARSE_P; ++b) {
            size_t ntouched = 0;
            for (int c = 0; c < COARSE_P; ++c) {
                if (c == a || c == b) continue;
                for (int ia = 0; ia < sizes[a]; ++ia)
                    for (int ib = 0; ib < sizes[b]; ++ib)
                        for (int ic = 0; ic < sizes[c]; ++ic) {
                            uint32_t s = col[members[a][ia]] ^
                                col[members[b][ib]] ^ col[members[c][ic]];
                            if (bad[s] == 0) touched[ntouched++] = s;
                            if (bad[s] == UINT16_MAX - 1)
                                fail("bad multiplicity overflow at %u", s);
                            ++bad[s];
                        }
            }
            uint64_t lost = 0;
            for (size_t i = 0; i < ntouched; ++i) {
                uint32_t s = touched[i];
                if (!short_cover[s] && total[s] == bad[s]) ++lost;
                bad[s] = 0;
            }
            if (lost < min_lost) min_lost = lost, best_a = a, best_b = b;
            if (lost == 0) {
                ++viable;
                printf("VALID merge %d %d sizes %d %d\n", a, b, sizes[a], sizes[b]);
            } else ++rejected;
        }
    printf("merges=%d viable=%d rejected=%d best=%d,%d lost=%" PRIu64 "\n",
           viable + rejected, viable, rejected, best_a, best_b, min_lost);
    free(total); free(bad); free(short_cover); free(touched);
    return 0;
}
