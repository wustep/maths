/*
 * Matrix-only verifier for binary radius-2 covering codes.
 *
 * This file shares no code with build_qm3.py.  It parses a text matrix,
 * derives its columns, checks full binary rank and distinct nonzero columns,
 * and exhaustively marks {0}, every singleton, and every unordered pair XOR.
 *
 * Build and run from problems/covering/:
 *
 *   gcc -O3 -std=c11 -Wall -Wextra compute/verify_radius2_matrix.c \
 *       -o compute/verify_radius2_matrix
 *   compute/verify_radius2_matrix compute/H_r22_n3325.txt 22 3325
 *
 * Optionally append a partition-label file and its expected block count.  The
 * verifier then independently marks only pairs drawn from distinct blocks:
 *
 *   compute/verify_radius2_matrix MATRIX R N PARTITION_LABELS EXPECTED_BLOCKS
 */

#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef struct {
    int redundancy;
    size_t length;
    uint32_t *columns;
} Matrix;

static void die(const char *message) {
    fprintf(stderr, "FAIL: %s\n", message);
    exit(1);
}

static void die_path(const char *message, const char *path) {
    fprintf(stderr, "FAIL: %s %s: %s\n", message, path, strerror(errno));
    exit(1);
}

static double seconds_since(const struct timespec *start) {
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    return (double)(now.tv_sec - start->tv_sec) +
           1e-9 * (double)(now.tv_nsec - start->tv_nsec);
}

static size_t parse_row(char *line, unsigned char **bits, size_t *capacity) {
    char *cursor = line;
    size_t count = 0;
    while (*cursor != '\0') {
        while (*cursor == ' ' || *cursor == '\t' ||
               *cursor == '\r' || *cursor == '\n') {
            ++cursor;
        }
        if (*cursor == '\0' || *cursor == '#') {
            break;
        }
        if ((*cursor != '0' && *cursor != '1') ||
            (cursor[1] != '\0' && cursor[1] != '#' &&
             cursor[1] != ' ' && cursor[1] != '\t' &&
             cursor[1] != '\r' && cursor[1] != '\n')) {
            die("matrix contains a token other than 0 or 1");
        }
        if (count == *capacity) {
            size_t next = *capacity == 0 ? 1024 : 2 * *capacity;
            unsigned char *grown = realloc(*bits, next * sizeof(**bits));
            if (grown == NULL) {
                die("out of memory while parsing a matrix row");
            }
            *bits = grown;
            *capacity = next;
        }
        (*bits)[count++] = (unsigned char)(*cursor - '0');
        ++cursor;
    }
    return count;
}

static Matrix read_matrix(const char *path) {
    FILE *file = fopen(path, "r");
    char *line = NULL;
    size_t line_capacity = 0;
    ssize_t got;
    unsigned char *row_bits = NULL;
    size_t row_capacity = 0;
    Matrix matrix = {0, 0, NULL};
    if (file == NULL) {
        die_path("cannot open", path);
    }
    while ((got = getline(&line, &line_capacity, file)) >= 0) {
        size_t row_length;
        char *cursor = line;
        (void)got;
        while (*cursor == ' ' || *cursor == '\t' ||
               *cursor == '\r' || *cursor == '\n') {
            ++cursor;
        }
        if (*cursor == '\0' || *cursor == '#') {
            continue;
        }
        if (matrix.redundancy >= 31) {
            die("this verifier supports at most 30 matrix rows");
        }
        row_length = parse_row(cursor, &row_bits, &row_capacity);
        if (row_length == 0) {
            continue;
        }
        if (matrix.length == 0) {
            matrix.length = row_length;
            matrix.columns = calloc(matrix.length, sizeof(*matrix.columns));
            if (matrix.columns == NULL) {
                die("out of memory allocating columns");
            }
        } else if (row_length != matrix.length) {
            die("matrix is ragged");
        }
        for (size_t column = 0; column < matrix.length; ++column) {
            matrix.columns[column] |=
                (uint32_t)row_bits[column] << matrix.redundancy;
        }
        ++matrix.redundancy;
    }
    if (ferror(file)) {
        die_path("error reading", path);
    }
    free(line);
    free(row_bits);
    fclose(file);
    if (matrix.redundancy == 0 || matrix.length == 0) {
        die("matrix has no data rows");
    }
    return matrix;
}

static int binary_rank(const uint32_t *columns, size_t length) {
    uint32_t basis[31] = {0};
    int rank = 0;
    for (size_t index = 0; index < length; ++index) {
        uint32_t value = columns[index];
        while (value != 0) {
            int pivot = 31 - __builtin_clz(value);
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

static long parse_expected(const char *text, const char *name) {
    char *end = NULL;
    long value = strtol(text, &end, 10);
    if (end == text || *end != '\0' || value <= 0) {
        fprintf(stderr, "FAIL: invalid expected %s: %s\n", name, text);
        exit(1);
    }
    return value;
}

static int *read_partition(const char *path, size_t length, int *block_count) {
    FILE *file = fopen(path, "r");
    char *line = NULL;
    size_t line_capacity = 0;
    ssize_t got;
    int *labels;
    size_t count = 0;
    int maximum = -1;
    unsigned char *used;
    if (file == NULL) {
        die_path("cannot open", path);
    }
    labels = malloc(length * sizeof(*labels));
    if (labels == NULL) {
        die("out of memory allocating partition labels");
    }
    while ((got = getline(&line, &line_capacity, file)) >= 0) {
        char *cursor = line;
        (void)got;
        while (*cursor != '\0') {
            char *end;
            long value;
            while (*cursor == ' ' || *cursor == '\t' ||
                   *cursor == '\r' || *cursor == '\n') {
                ++cursor;
            }
            if (*cursor == '\0' || *cursor == '#') {
                break;
            }
            value = strtol(cursor, &end, 10);
            if (end == cursor || value < 0 || value > 1000000) {
                die("partition file contains an invalid block label");
            }
            if (count >= length) {
                die("partition file has more labels than matrix columns");
            }
            labels[count++] = (int)value;
            if (value > maximum) {
                maximum = (int)value;
            }
            cursor = end;
        }
    }
    if (ferror(file)) {
        die_path("error reading", path);
    }
    free(line);
    fclose(file);
    if (count != length) {
        die("partition label count does not equal matrix length");
    }
    used = calloc((size_t)maximum + 1U, 1);
    if (used == NULL) {
        die("out of memory checking partition block labels");
    }
    for (size_t index = 0; index < length; ++index) {
        used[labels[index]] = 1;
    }
    for (int block = 0; block <= maximum; ++block) {
        if (!used[block]) {
            die("partition block labels are not contiguous from zero");
        }
    }
    free(used);
    *block_count = maximum + 1;
    return labels;
}

int main(int argc, char **argv) {
    Matrix matrix;
    uint64_t space;
    unsigned char *seen;
    unsigned char *covered;
    unsigned char *partition_covered = NULL;
    int *partition_labels = NULL;
    int partition_blocks = 0;
    uint64_t covered_count = 0;
    uint64_t pair_count = 0;
    int rank;
    struct timespec started;

    if (argc != 4 && argc != 6) {
        fprintf(stderr,
                "usage: %s MATRIX EXPECTED_R EXPECTED_N "
                "[PARTITION_LABELS EXPECTED_BLOCKS]\n", argv[0]);
        return 2;
    }
    clock_gettime(CLOCK_MONOTONIC, &started);
    matrix = read_matrix(argv[1]);
    if (matrix.redundancy != parse_expected(argv[2], "redundancy") ||
        matrix.length != (size_t)parse_expected(argv[3], "length")) {
        fprintf(stderr,
                "FAIL: shape is %d x %zu, expected %s x %s\n",
                matrix.redundancy, matrix.length, argv[2], argv[3]);
        free(matrix.columns);
        return 1;
    }
    space = UINT64_C(1) << matrix.redundancy;
    seen = calloc((size_t)space, 1);
    covered = calloc((size_t)space, 1);
    if (seen == NULL || covered == NULL) {
        die("out of memory allocating syndrome arrays");
    }
    for (size_t index = 0; index < matrix.length; ++index) {
        uint32_t column = matrix.columns[index];
        if (column == 0 || (uint64_t)column >= space) {
            die("matrix has a zero or out-of-range column");
        }
        if (seen[column]) {
            die("matrix has a repeated column");
        }
        seen[column] = 1;
    }
    rank = binary_rank(matrix.columns, matrix.length);
    if (rank != matrix.redundancy) {
        die("matrix does not have full binary rank");
    }

    if (argc == 6) {
        partition_labels = read_partition(argv[4], matrix.length,
                                           &partition_blocks);
        if (partition_blocks != parse_expected(argv[5], "partition blocks")) {
            die("partition block count differs from expected value");
        }
    }

    covered[0] = 1;
    for (size_t left = 0; left < matrix.length; ++left) {
        covered[matrix.columns[left]] = 1;
        for (size_t right = 0; right < left; ++right) {
            covered[matrix.columns[left] ^ matrix.columns[right]] = 1;
            ++pair_count;
        }
    }
    for (uint64_t syndrome = 0; syndrome < space; ++syndrome) {
        covered_count += covered[syndrome] != 0;
    }
    if (covered_count != space) {
        fprintf(stderr,
                "FAIL: covered=%" PRIu64 "/%" PRIu64
                " missing=%" PRIu64 " rank=%d distinct_nonzero=%zu\n",
                covered_count, space, space - covered_count,
                rank, matrix.length);
        free(seen);
        free(covered);
        free(matrix.columns);
        return 1;
    }
    if (partition_labels != NULL) {
        uint64_t cross_covered_count = 0;
        partition_covered = calloc((size_t)space, 1);
        if (partition_covered == NULL) {
            die("out of memory allocating partition coverage array");
        }
        partition_covered[0] = 1;
        for (size_t left = 0; left < matrix.length; ++left) {
            partition_covered[matrix.columns[left]] = 1;
            for (size_t right = 0; right < left; ++right) {
                if (partition_labels[left] != partition_labels[right]) {
                    partition_covered[matrix.columns[left] ^
                                      matrix.columns[right]] = 1;
                }
            }
        }
        for (uint64_t syndrome = 0; syndrome < space; ++syndrome) {
            cross_covered_count += partition_covered[syndrome] != 0;
        }
        if (cross_covered_count != space) {
            fprintf(stderr,
                    "FAIL: partition cross-block covered=%" PRIu64
                    "/%" PRIu64 " missing=%" PRIu64 " blocks=%d\n",
                    cross_covered_count, space,
                    space - cross_covered_count, partition_blocks);
            free(partition_covered);
            free(partition_labels);
            free(seen);
            free(covered);
            free(matrix.columns);
            return 1;
        }
        printf("PASS partition=%s blocks=%d cross_block_covered=%" PRIu64
               "/%" PRIu64 "\n",
               argv[4], partition_blocks, cross_covered_count, space);
    }
    printf("PASS matrix=%s r=%d n=%zu rank=%d distinct_nonzero=%zu "
           "pairs=%" PRIu64 " covered=%" PRIu64 "/%" PRIu64
           " elapsed_seconds=%.3f\n",
           argv[1], matrix.redundancy, matrix.length, rank, matrix.length,
           pair_count, covered_count, space, seconds_since(&started));
    free(seen);
    free(covered);
    free(partition_covered);
    free(partition_labels);
    free(matrix.columns);
    return 0;
}
