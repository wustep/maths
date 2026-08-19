/*
 * Exhaustively search for two safe, disjoint merges of partition blocks.
 *
 * For every non-singleton syndrome, record up to three distinct unordered
 * pairs of input block labels that represent it.  Merging two disjoint block
 * pairs e and f can destroy only representations using e or f.  It is safe
 * exactly when no syndrome has its complete representation-edge set equal to
 * {e}, {f}, or {e,f}.  The program checks those conditions exhaustively over
 * all syndromes and writes a relabelled partition with two fewer blocks.
 *
 * The state array uses four bytes per syndrome.  At r=28 it needs 1 GiB.
 *
 * Build and run from problems/covering/:
 *
 *   gcc -O3 -std=c11 -Wall -Wextra compute/search_partition_merges.c \
 *       -o compute/search_partition_merges
 *   compute/search_partition_merges compute/H_r28_n26111.txt 28 26111 \
 *       compute/partition_r28_n26111.txt 66 \
 *       compute/partition_r28_n26111_p64.txt
 */

#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define EDGE_MASK UINT32_C(0xFFF)
#define MANY_EDGES UINT32_C(1) << 24

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

static long parse_expected(const char *text, const char *name) {
    char *end = NULL;
    long value = strtol(text, &end, 10);
    if (end == text || *end != '\0' || value <= 0) {
        fprintf(stderr, "FAIL: invalid expected %s: %s\n", name, text);
        exit(1);
    }
    return value;
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
        char *cursor = line;
        size_t row_length;
        (void)got;
        while (*cursor == ' ' || *cursor == '\t' ||
               *cursor == '\r' || *cursor == '\n') {
            ++cursor;
        }
        if (*cursor == '\0' || *cursor == '#') {
            continue;
        }
        if (matrix.redundancy >= 31) {
            die("this search supports at most 30 matrix rows");
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
            if (end == cursor || value < 0 || value >= 90) {
                die("partition contains an invalid block label");
            }
            if (count >= length) {
                die("partition has more labels than matrix columns");
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
        die("out of memory checking labels");
    }
    for (size_t index = 0; index < length; ++index) {
        used[labels[index]] = 1;
    }
    for (int block = 0; block <= maximum; ++block) {
        if (!used[block]) {
            die("partition labels are not contiguous from zero");
        }
    }
    free(used);
    *block_count = maximum + 1;
    return labels;
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

static void add_edge(uint32_t *state, uint16_t edge_plus_one) {
    uint32_t value = *state;
    uint16_t first;
    uint16_t second;
    if (value & MANY_EDGES) {
        return;
    }
    first = (uint16_t)(value & EDGE_MASK);
    second = (uint16_t)((value >> 12) & EDGE_MASK);
    if (edge_plus_one == first || edge_plus_one == second) {
        return;
    }
    if (first == 0) {
        *state = edge_plus_one;
    } else if (second == 0) {
        *state = value | ((uint32_t)edge_plus_one << 12);
    } else {
        *state = MANY_EDGES;
    }
}

static int find_root(int *parent, int value) {
    while (parent[value] != value) {
        parent[value] = parent[parent[value]];
        value = parent[value];
    }
    return value;
}

static void join(int *parent, int left, int right) {
    left = find_root(parent, left);
    right = find_root(parent, right);
    if (left != right) {
        parent[right] = left;
    }
}

static void write_partition(const char *path, const int *labels, size_t length,
                            int blocks, const int merge[4]) {
    FILE *file = fopen(path, "w");
    if (file == NULL) {
        die_path("cannot create", path);
    }
    fprintf(file, "# Exhaustive coarsening of partition_r28_n26111.txt.\n");
    fprintf(file, "# Merged original blocks %d+%d and %d+%d; %d blocks.\n",
            merge[0], merge[1], merge[2], merge[3], blocks);
    fprintf(file, "# Generated by compute/search_partition_merges.c.\n");
    for (size_t index = 0; index < length; ++index) {
        fprintf(file, "%d%c", labels[index],
                index + 1 == length ? '\n' : ' ');
    }
    if (fclose(file) != 0) {
        die_path("cannot close", path);
    }
}

int main(int argc, char **argv) {
    Matrix matrix;
    int *labels;
    int blocks;
    int edge_ids[90][90];
    int edge_left[4095];
    int edge_right[4095];
    int edge_count = 0;
    uint64_t space;
    uint32_t *states;
    unsigned char *unsafe_single;
    unsigned char *forbidden_pair;
    uint64_t state_counts[4] = {0, 0, 0, 0};
    uint64_t cross_pairs = 0;
    int chosen_first = -1;
    int chosen_second = -1;
    int safe_edges = 0;
    int rank;
    struct timespec started;

    if (argc != 7) {
        fprintf(stderr,
                "usage: %s MATRIX EXPECTED_R EXPECTED_N PARTITION "
                "EXPECTED_BLOCKS OUTPUT_PARTITION\n", argv[0]);
        return 2;
    }
    clock_gettime(CLOCK_MONOTONIC, &started);
    matrix = read_matrix(argv[1]);
    if (matrix.redundancy != parse_expected(argv[2], "redundancy") ||
        matrix.length != (size_t)parse_expected(argv[3], "length")) {
        die("matrix shape differs from expected shape");
    }
    labels = read_partition(argv[4], matrix.length, &blocks);
    if (blocks != parse_expected(argv[5], "partition blocks")) {
        die("partition block count differs from expected value");
    }
    if (blocks < 4 || blocks > 90) {
        die("block count must lie between 4 and 90");
    }
    rank = binary_rank(matrix.columns, matrix.length);
    if (rank != matrix.redundancy) {
        die("matrix does not have full binary rank");
    }
    space = UINT64_C(1) << matrix.redundancy;
    states = calloc((size_t)space, sizeof(*states));
    if (states == NULL) {
        die("out of memory allocating four bytes per syndrome");
    }
    states[0] = MANY_EDGES;
    for (size_t index = 0; index < matrix.length; ++index) {
        uint32_t column = matrix.columns[index];
        if (column == 0 || (uint64_t)column >= space) {
            die("matrix has a zero or out-of-range column");
        }
        if (states[column] == MANY_EDGES) {
            die("matrix has a repeated column");
        }
        states[column] = MANY_EDGES;
    }

    for (int left = 0; left < blocks; ++left) {
        for (int right = left + 1; right < blocks; ++right) {
            edge_ids[left][right] = edge_count;
            edge_ids[right][left] = edge_count;
            edge_left[edge_count] = left;
            edge_right[edge_count] = right;
            ++edge_count;
        }
    }
    if (edge_count >= 4095) {
        die("too many block-pair edges for packed state");
    }

    for (size_t left = 0; left < matrix.length; ++left) {
        int left_block = labels[left];
        uint32_t left_column = matrix.columns[left];
        for (size_t right = 0; right < left; ++right) {
            int right_block = labels[right];
            int edge;
            if (left_block == right_block) {
                continue;
            }
            edge = edge_ids[left_block][right_block];
            add_edge(&states[left_column ^ matrix.columns[right]],
                     (uint16_t)(edge + 1));
            ++cross_pairs;
        }
    }

    unsafe_single = calloc((size_t)edge_count, 1);
    forbidden_pair = calloc((size_t)edge_count * (size_t)edge_count, 1);
    if (unsafe_single == NULL || forbidden_pair == NULL) {
        die("out of memory allocating merge constraints");
    }
    for (uint64_t syndrome = 0; syndrome < space; ++syndrome) {
        uint32_t state = states[syndrome];
        uint16_t first;
        uint16_t second;
        if (state & MANY_EDGES) {
            ++state_counts[3];
            continue;
        }
        first = (uint16_t)(state & EDGE_MASK);
        second = (uint16_t)((state >> 12) & EDGE_MASK);
        if (first == 0) {
            fprintf(stderr, "FAIL: original partition misses syndrome %" PRIu64
                    "\n", syndrome);
            free(states);
            free(forbidden_pair);
            free(unsafe_single);
            free(labels);
            free(matrix.columns);
            return 1;
        }
        if (second == 0) {
            int edge = first - 1;
            unsafe_single[edge] = 1;
            ++state_counts[1];
        } else {
            int edge1 = first - 1;
            int edge2 = second - 1;
            forbidden_pair[(size_t)edge1 * (size_t)edge_count + edge2] = 1;
            forbidden_pair[(size_t)edge2 * (size_t)edge_count + edge1] = 1;
            ++state_counts[2];
        }
    }
    free(states);
    for (int edge = 0; edge < edge_count; ++edge) {
        safe_edges += !unsafe_single[edge];
    }

    for (int first = 0; first < edge_count && chosen_first < 0; ++first) {
        if (unsafe_single[first]) {
            continue;
        }
        for (int second = first + 1; second < edge_count; ++second) {
            if (unsafe_single[second] ||
                forbidden_pair[(size_t)first * (size_t)edge_count + second]) {
                continue;
            }
            if (edge_left[first] == edge_left[second] ||
                edge_left[first] == edge_right[second] ||
                edge_right[first] == edge_left[second] ||
                edge_right[first] == edge_right[second]) {
                continue;
            }
            chosen_first = first;
            chosen_second = second;
            break;
        }
    }
    if (chosen_first < 0) {
        fprintf(stderr,
                "FAIL: no safe pair of disjoint merges; safe_edges=%d/%d\n",
                safe_edges, edge_count);
        free(forbidden_pair);
        free(unsafe_single);
        free(labels);
        free(matrix.columns);
        return 1;
    }

    {
        int parent[90];
        int root_label[90];
        int output_blocks = 0;
        int merge[4] = {
            edge_left[chosen_first], edge_right[chosen_first],
            edge_left[chosen_second], edge_right[chosen_second]
        };
        for (int block = 0; block < blocks; ++block) {
            parent[block] = block;
            root_label[block] = -1;
        }
        join(parent, merge[0], merge[1]);
        join(parent, merge[2], merge[3]);
        for (int block = 0; block < blocks; ++block) {
            int root = find_root(parent, block);
            if (root_label[root] < 0) {
                root_label[root] = output_blocks++;
            }
        }
        if (output_blocks != blocks - 2) {
            die("internal error: output does not have two fewer blocks");
        }
        for (size_t index = 0; index < matrix.length; ++index) {
            labels[index] = root_label[find_root(parent, labels[index])];
        }
        write_partition(argv[6], labels, matrix.length, output_blocks, merge);
        printf("PASS input_blocks=%d output_blocks=%d safe_edges=%d/%d "
               "merged=%d+%d,%d+%d cross_pairs=%" PRIu64
               " protected_or_ge3=%" PRIu64 " exactly1=%" PRIu64
               " exactly2=%" PRIu64 " output=%s elapsed_seconds=%.3f\n",
               blocks, output_blocks, safe_edges, edge_count,
               merge[0], merge[1], merge[2], merge[3], cross_pairs,
               state_counts[3], state_counts[1], state_counts[2], argv[6],
               seconds_since(&started));
    }

    free(forbidden_pair);
    free(unsafe_single);
    free(labels);
    free(matrix.columns);
    return 0;
}
