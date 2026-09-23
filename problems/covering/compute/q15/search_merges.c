/* Search all single merges of the certified q13 34-block partition.
 * Compile from problems/covering with: cc -O3 compute/q15/search_merges.c -o /tmp/q15-merges
 */
#define main q13_verifier_main
#include "../q13/verify_q13.c"
#undef main

int main(int argc, char **argv)
{
    if (argc != 4) {
        fprintf(stderr, "usage: %s SEED PARTITION first_block\n", argv[0]);
        return 2;
    }
    uint64_t *columns = read_matrix(argv[1], SEED_R, SEED_N);
    int *original = read_partition(argv[2], SEED_N);
    verify_columns(columns, SEED_N, SEED_R, "seed");
    count_blocks(original, SEED_N, COARSE_P);
    int first = atoi(argv[3]);
    if (first < 0 || first >= COARSE_P) return 2;
    uint64_t *bits = calloc((size_t)1 << (SEED_R - 6), sizeof(*bits));
    if (!bits) fail("cannot allocate syndrome bitmap");
    for (int second = first + 1; second < COARSE_P; ++second) {
        memset(bits, 0, (size_t)1 << (SEED_R - 3));
        mark(bits, 0);
        for (int i = 0; i < SEED_N; ++i) {
            int bi = original[i] == second ? first : original[i];
            mark(bits, (uint32_t)columns[i]);
            for (int j = 0; j < i; ++j) {
                int bj = original[j] == second ? first : original[j];
                if (bi == bj) continue;
                uint32_t pair = (uint32_t)(columns[i] ^ columns[j]);
                mark(bits, pair);
                for (int k = 0; k < j; ++k) {
                    int bk = original[k] == second ? first : original[k];
                    if (bk != bi && bk != bj)
                        mark(bits, pair ^ (uint32_t)columns[k]);
                }
            }
        }
        uint64_t covered = count_marked(bits, (size_t)1 << (SEED_R - 6));
        printf("merge %d %d covered=%" PRIu64 "/%u\n",
               first, second, covered, 1U << SEED_R);
        fflush(stdout);
    }
    free(bits);
    free(original);
    free(columns);
    return 0;
}
