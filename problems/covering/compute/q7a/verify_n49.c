/*
 * Independent verifier for an ell_2(10,2) <= 49 candidate.
 *
 * This file deliberately shares no search bookkeeping.  It reparses either
 * 49 integer columns or a 10 x 49 binary matrix, checks the basic matrix
 * conditions, computes rank over F_2, and enumerates all singletons and
 * unordered pair XORs from scratch.
 *
 * Build:
 *   gcc -O2 -std=c11 -Wall -Wextra compute/q7a/verify_n49.c \
 *       -o compute/q7a/verify_n49
 *
 * Run:
 *   compute/q7a/verify_n49 --columns candidate.cols
 *   compute/q7a/verify_n49 --matrix compute/H_r10_n49.txt
 */

#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { R = 10, N = 49, SPACE = 1 << R };

static int columns[N];

static int parse_columns(const char *path) {
    FILE *file = fopen(path, "r");
    char line[16384];
    int count = 0;
    if (file == NULL) {
        fprintf(stderr, "cannot open %s: %s\n", path, strerror(errno));
        return 0;
    }
    while (fgets(line, sizeof(line), file) != NULL) {
        char *cursor = line;
        if (line[0] == '#') {
            continue;
        }
        while (1) {
            char *end = NULL;
            long value = strtol(cursor, &end, 0);
            if (end == cursor) {
                break;
            }
            if (count >= N || value < 1 || value >= SPACE) {
                fprintf(stderr, "%s is not a list of 49 columns in 1..1023\n",
                        path);
                fclose(file);
                return 0;
            }
            columns[count++] = (int)value;
            cursor = end;
        }
    }
    if (ferror(file) || fclose(file) != 0 || count != N) {
        fprintf(stderr, "%s contains %d columns, expected %d\n", path, count, N);
        return 0;
    }
    return 1;
}

static int parse_matrix(const char *path) {
    FILE *file = fopen(path, "r");
    char line[16384];
    int row = 0;
    memset(columns, 0, sizeof(columns));
    if (file == NULL) {
        fprintf(stderr, "cannot open %s: %s\n", path, strerror(errno));
        return 0;
    }
    while (fgets(line, sizeof(line), file) != NULL) {
        char *cursor = line;
        int column = 0;
        if (line[0] == '#' || line[0] == '\n' || line[0] == '\r') {
            continue;
        }
        while (1) {
            char *end = NULL;
            long bit = strtol(cursor, &end, 10);
            if (end == cursor) {
                break;
            }
            if (row >= R || column >= N || (bit != 0 && bit != 1)) {
                fprintf(stderr, "%s is not a 10 x 49 binary matrix\n", path);
                fclose(file);
                return 0;
            }
            columns[column++] |= (int)bit << row;
            cursor = end;
        }
        if (column != N) {
            fprintf(stderr, "%s row %d has %d entries, expected %d\n",
                    path, row + 1, column, N);
            fclose(file);
            return 0;
        }
        ++row;
    }
    if (ferror(file) || fclose(file) != 0 || row != R) {
        fprintf(stderr, "%s has %d data rows, expected %d\n", path, row, R);
        return 0;
    }
    return 1;
}

static int rank_binary(void) {
    int basis[R] = {0};
    int rank = 0;
    for (int index = 0; index < N; ++index) {
        int value = columns[index];
        while (value != 0) {
            int pivot = 31 - __builtin_clz((unsigned)value);
            if (basis[pivot] != 0) {
                value ^= basis[pivot];
            } else {
                basis[pivot] = value;
                ++rank;
                break;
            }
        }
    }
    return rank;
}

int main(int argc, char **argv) {
    const char *path;
    int matrix_mode;
    unsigned char covered[SPACE] = {0};
    int distinct = 1;
    int nonzero = 1;
    int covered_count = 0;
    int holes = 0;
    int rank;

    if (argc != 3 ||
        (strcmp(argv[1], "--columns") != 0 &&
         strcmp(argv[1], "--matrix") != 0)) {
        fprintf(stderr, "usage: %s (--columns|--matrix) FILE\n", argv[0]);
        return 2;
    }
    matrix_mode = strcmp(argv[1], "--matrix") == 0;
    path = argv[2];
    if (!(matrix_mode ? parse_matrix(path) : parse_columns(path))) {
        return 2;
    }

    for (int left = 0; left < N; ++left) {
        if (columns[left] <= 0 || columns[left] >= SPACE) {
            nonzero = 0;
        }
        for (int right = 0; right < left; ++right) {
            if (columns[left] == columns[right]) {
                distinct = 0;
            }
        }
    }
    rank = rank_binary();

    covered[0] = 1;
    for (int left = 0; left < N; ++left) {
        covered[columns[left]] = 1;
        for (int right = 0; right < left; ++right) {
            covered[columns[left] ^ columns[right]] = 1;
        }
    }
    for (int syndrome = 0; syndrome < SPACE; ++syndrome) {
        if (covered[syndrome]) {
            ++covered_count;
        } else {
            ++holes;
        }
    }

    printf("n=%d distinct=%s nonzero=%s rank=%d covered=%d/%d holes=%d\n",
           N, distinct ? "yes" : "no", nonzero ? "yes" : "no", rank,
           covered_count, SPACE, holes);
    if (holes != 0) {
        printf("uncovered:");
        for (int syndrome = 0; syndrome < SPACE; ++syndrome) {
            if (!covered[syndrome]) {
                printf(" %d", syndrome);
            }
        }
        printf("\n");
    }
    return distinct && nonzero && rank == R && covered_count == SPACE ? 0 : 1;
}
