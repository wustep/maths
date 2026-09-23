/* Exact necessary screen for deleting a seed column while retaining the
 * 33-block (3,0) partition. A syndrome with one admissible representation
 * makes every column in that representation essential. */
#define main q13_original_main
#include "../q13/verify_q13.c"
#undef main

int main(int argc, char **argv)
{
    if (argc != 3 && argc != 4)
        fail("usage: delete_screen seed partition [plain]");
    uint64_t *col = read_matrix(argv[1], SEED_R, SEED_N);
    int *lab = read_partition(argv[2], SEED_N);
    if (argc == 4) {
        if (strcmp(argv[3], "plain") != 0) fail("unknown mode");
        for (int i = 0; i < SEED_N; ++i) lab[i] = i;
    } else count_blocks(lab, SEED_N, 33);
    const uint32_t space = UINT32_C(1) << SEED_R;
    uint16_t *count = calloc(space, sizeof(*count));
    uint8_t *essential = calloc(SEED_N, 1);
    if (!count || !essential) fail("allocation failure");
    ++count[0];
    for (int i = 0; i < SEED_N; ++i) {
        ++count[col[i]];
        for (int j = 0; j < i; ++j)
            if (lab[i] != lab[j]) ++count[col[i] ^ col[j]];
    }
    for (int i = 0; i < SEED_N; ++i)
        for (int j = 0; j < i; ++j) {
            if (lab[i] == lab[j]) continue;
            uint32_t pair = (uint32_t)(col[i] ^ col[j]);
            for (int k = 0; k < j; ++k) {
                if (lab[i] == lab[k] || lab[j] == lab[k]) continue;
                uint32_t s = pair ^ (uint32_t)col[k];
                if (count[s] == UINT16_MAX) fail("multiplicity overflow");
                ++count[s];
            }
        }
    uint32_t holes = 0, unique = 0;
    for (uint32_t s = 0; s < space; ++s) {
        holes += count[s] == 0;
        unique += count[s] == 1;
    }
    if (holes) fail("input partition has %u holes", holes);
    for (int i = 0; i < SEED_N; ++i) {
        if (count[col[i]] == 1) essential[i] = 1;
        for (int j = 0; j < i; ++j)
            if (lab[i] != lab[j] && count[col[i] ^ col[j]] == 1)
                essential[i] = essential[j] = 1;
    }
    for (int i = 0; i < SEED_N; ++i)
        for (int j = 0; j < i; ++j) {
            if (lab[i] == lab[j]) continue;
            uint32_t pair = (uint32_t)(col[i] ^ col[j]);
            for (int k = 0; k < j; ++k) {
                if (lab[i] == lab[k] || lab[j] == lab[k]) continue;
                if (count[pair ^ col[k]] == 1)
                    essential[i] = essential[j] = essential[k] = 1;
            }
        }
    int candidates = 0;
    printf("partition holes=%u unique_syndromes=%u\n", holes, unique);
    for (int i = 0; i < SEED_N; ++i)
        if (!essential[i]) {
            ++candidates;
            printf("candidate index=%d block=%d value=%" PRIu64 "\n", i, lab[i], col[i]);
        }
    printf("essential_by_unique=%d candidates=%d\n", SEED_N - candidates, candidates);
    if (candidates) fail("%d deletion candidates remain undecided", candidates);
    free(col); free(lab); free(count); free(essential);
    return 0;
}
