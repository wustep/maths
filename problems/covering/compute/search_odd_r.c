/*
 * Fixed-cardinality targeted search for binary radius-2 coverings.
 *
 * Discovers an r x n set of distinct nonzero columns in F_2^r whose
 * {0} u S u (S+S) covers the whole space.  Incremental coverage counts
 * make a swap O(n).  This is discovery code, not a certificate: any
 * zero-residue checkpoint must still be checked by verify_radius2_matrix.c
 * (and the companion Python checker) from the emitted matrix text.
 *
 * Built for the odd-r Table 5.1 holes r=11 (paper 79) and r=13 (paper 159).
 * Also usable for a constructed seed of size n+1 that is then shortened.
 *
 * Build from problems/covering/:
 *   gcc -O3 -std=c11 -Wall -Wextra -pthread compute/search_odd_r.c \
 *       -lm -o compute/search_odd_r
 *
 * Example:
 *   compute/search_odd_r --r 11 --n 78 --seconds 180 --threads 4 \
 *       --seed 0x0DD202608200001 \
 *       --output compute/odd_r11_n78_checkpoint.json
 */

#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <math.h>
#include <pthread.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

enum { MAX_R = 16, MAX_N = 320 };

typedef struct {
    int *counts;
    int *columns;
    unsigned char *member;
    int *zero_list;
    int *zero_pos;
    int *weights;
    int missing;
    int singletons;
    long weighted_missing;
} State;

typedef struct {
    int worker_id;
    int mode;
    uint64_t seed;
    uint64_t iterations;
    uint64_t accepted;
    int best_missing;
    int best_singletons;
    int *best_columns;
} Worker;

static int redundancy = 11;
static int length = 78;
static int space = 2048;
static int thread_count = 1;
static double time_limit = 60.0;
static uint64_t master_seed = UINT64_C(0x0DD202608200001);
static const char *output_path = "compute/odd_r_checkpoint.json";
static const char *source_path = NULL;
static int source_columns[MAX_N + 8];
static int source_count = 0;
static struct timespec start_clock;
static volatile sig_atomic_t stop_requested = 0;
static pthread_mutex_t best_mutex = PTHREAD_MUTEX_INITIALIZER;
static int global_best = 1 << 30;
static int global_best_singletons = 1 << 30;
static int global_best_columns[MAX_N];
static int global_best_worker = -1;
static int global_best_mode = -1;
static uint64_t global_best_iteration = 0;
static uint64_t global_best_seed = 0;
static int found_cover = 0;

static double elapsed_seconds(void) {
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    return (double)(now.tv_sec - start_clock.tv_sec) +
           1e-9 * (double)(now.tv_nsec - start_clock.tv_nsec);
}

static void handle_signal(int signal_number) {
    (void)signal_number;
    stop_requested = 1;
}

static uint64_t splitmix64(uint64_t *state) {
    uint64_t z;
    *state += UINT64_C(0x9E3779B97F4A7C15);
    z = *state;
    z = (z ^ (z >> 30)) * UINT64_C(0xBF58476D1CE4E5B9);
    z = (z ^ (z >> 27)) * UINT64_C(0x94D049BB133111EB);
    return z ^ (z >> 31);
}

static uint64_t rng_next(uint64_t *state) {
    uint64_t x = *state;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    *state = x;
    return x;
}

static int compare_ints(const void *left, const void *right) {
    const int a = *(const int *)left;
    const int b = *(const int *)right;
    return (a > b) - (a < b);
}

static int binary_rank(const int *columns, int n, int r) {
    int basis[MAX_R];
    int rank = 0;
    memset(basis, 0, sizeof(basis));
    for (int index = 0; index < n; ++index) {
        int value = columns[index];
        while (value != 0) {
            int pivot = 31 - __builtin_clz((unsigned)value);
            if (pivot >= r) {
                break;
            }
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

static int parse_hex_or_dec(const char *text, uint64_t *out) {
    char *end = NULL;
    unsigned long long value;
    if (text[0] == '0' && (text[1] == 'x' || text[1] == 'X')) {
        value = strtoull(text, &end, 16);
    } else {
        value = strtoull(text, &end, 0);
    }
    if (end == text || *end != '\0') {
        return 0;
    }
    *out = (uint64_t)value;
    return 1;
}

static int read_source_columns(const char *path) {
    FILE *file = fopen(path, "r");
    char line[65536];
    unsigned char seen[1 << MAX_R];
    if (file == NULL) {
        fprintf(stderr, "cannot open source %s: %s\n", path, strerror(errno));
        return 0;
    }
    memset(seen, 0, sizeof(seen));
    source_count = 0;
    while (fgets(line, sizeof(line), file) != NULL) {
        char *cursor = line;
        if (line[0] == '#' || line[0] == '\n' || line[0] == '\r') {
            continue;
        }
        while (*cursor != '\0') {
            char *end;
            long value;
            while (*cursor == ' ' || *cursor == '\t' || *cursor == ',' ||
                   *cursor == '\r' || *cursor == '\n') {
                ++cursor;
            }
            if (*cursor == '\0' || *cursor == '#') {
                break;
            }
            value = strtol(cursor, &end, 0);
            if (end == cursor || value <= 0 || value >= space) {
                fclose(file);
                fprintf(stderr, "invalid source column in %s\n", path);
                return 0;
            }
            if (seen[value]) {
                fclose(file);
                fprintf(stderr, "repeated source column %ld\n", value);
                return 0;
            }
            if (source_count >= MAX_N + 4) {
                fclose(file);
                fprintf(stderr, "too many source columns\n");
                return 0;
            }
            seen[value] = 1;
            source_columns[source_count++] = (int)value;
            cursor = end;
        }
    }
    fclose(file);
    if (source_count < length) {
        fprintf(stderr, "source has %d columns, need at least %d\n",
                source_count, length);
        return 0;
    }
    return 1;
}

static void state_alloc(State *state) {
    state->counts = calloc((size_t)space, sizeof(int));
    state->columns = calloc((size_t)length, sizeof(int));
    state->member = calloc((size_t)space, 1);
    state->zero_list = calloc((size_t)space, sizeof(int));
    state->zero_pos = calloc((size_t)space, sizeof(int));
    state->weights = calloc((size_t)space, sizeof(int));
    if (state->counts == NULL || state->columns == NULL ||
        state->member == NULL || state->zero_list == NULL ||
        state->zero_pos == NULL || state->weights == NULL) {
        fprintf(stderr, "out of memory allocating search state\n");
        exit(1);
    }
}

static void state_free(State *state) {
    free(state->counts);
    free(state->columns);
    free(state->member);
    free(state->zero_list);
    free(state->zero_pos);
    free(state->weights);
}

static void zero_add(State *state, int syndrome) {
    state->zero_pos[syndrome] = state->missing;
    state->zero_list[state->missing] = syndrome;
    ++state->missing;
}

static void zero_remove(State *state, int syndrome) {
    int position = state->zero_pos[syndrome];
    int tail = state->zero_list[state->missing - 1];
    state->zero_list[position] = tail;
    state->zero_pos[tail] = position;
    --state->missing;
    state->zero_pos[syndrome] = -1;
}

static void change_count(State *state, int syndrome, int delta) {
    int before = state->counts[syndrome];
    int after = before + delta;
    if (after < 0) {
        fprintf(stderr, "internal error: negative coverage count\n");
        abort();
    }
    if (before == 0 && after == 1) {
        zero_remove(state, syndrome);
        ++state->singletons;
        state->weighted_missing -= state->weights[syndrome];
    } else if (before == 1 && after == 0) {
        zero_add(state, syndrome);
        --state->singletons;
        state->weighted_missing += state->weights[syndrome];
    } else if (before == 1 && after == 2) {
        --state->singletons;
    } else if (before == 2 && after == 1) {
        ++state->singletons;
    }
    state->counts[syndrome] = after;
}

static void initialize_state(State *state, const int *columns) {
    memset(state->counts, 0, (size_t)space * sizeof(int));
    memset(state->member, 0, (size_t)space);
    memcpy(state->columns, columns, (size_t)length * sizeof(int));
    state->missing = 0;
    state->singletons = 0;
    state->weighted_missing = 0;
    for (int syndrome = 0; syndrome < space; ++syndrome) {
        state->zero_pos[syndrome] = -1;
        state->weights[syndrome] = 1;
    }
    state->counts[0] = 1;
    for (int index = 0; index < length; ++index) {
        int column = state->columns[index];
        state->member[column] = 1;
        ++state->counts[column];
        for (int previous = 0; previous < index; ++previous) {
            ++state->counts[column ^ state->columns[previous]];
        }
    }
    for (int syndrome = 0; syndrome < space; ++syndrome) {
        if (state->counts[syndrome] == 0) {
            zero_add(state, syndrome);
            state->weighted_missing += state->weights[syndrome];
        } else if (state->counts[syndrome] == 1) {
            ++state->singletons;
        }
    }
}

static void remove_slot(State *state, int slot) {
    int removed = state->columns[slot];
    change_count(state, removed, -1);
    for (int index = 0; index < length; ++index) {
        if (index != slot) {
            change_count(state, removed ^ state->columns[index], -1);
        }
    }
}

static void add_slot(State *state, int slot, int added) {
    change_count(state, added, +1);
    for (int index = 0; index < length; ++index) {
        if (index != slot) {
            change_count(state, added ^ state->columns[index], +1);
        }
    }
}

static void apply_swap(State *state, int slot, int added) {
    int removed = state->columns[slot];
    remove_slot(state, slot);
    add_slot(state, slot, added);
    state->member[removed] = 0;
    state->member[added] = 1;
    state->columns[slot] = added;
}

static long objective(const State *state, int mode) {
    switch (mode) {
        case 0:
        case 3:
            return state->missing;
        case 1:
        case 4:
            return 16L * state->missing + state->singletons;
        case 2:
        case 5:
        default:
            return 64L * state->missing + state->singletons;
    }
}

static int random_available(State *state, uint64_t *rng) {
    int proposal;
    do {
        proposal = 1 + (int)(rng_next(rng) % (uint64_t)(space - 1));
    } while (state->member[proposal]);
    return proposal;
}

static int targeted_available(State *state, uint64_t *rng) {
    int target;
    int proposal = 0;
    if (state->missing <= 0) {
        return random_available(state, rng);
    }
    target = state->zero_list[rng_next(rng) % (uint64_t)state->missing];
    for (int attempt = 0; attempt < 80; ++attempt) {
        if ((rng_next(rng) & 63U) == 0U) {
            proposal = target;
        } else {
            proposal = target ^ state->columns[rng_next(rng) % (uint64_t)length];
        }
        if (proposal != 0 && proposal < space && !state->member[proposal]) {
            return proposal;
        }
    }
    return random_available(state, rng);
}

static int count_missing_independently(const int *columns, int *missing_values) {
    unsigned char *covered = calloc((size_t)space, 1);
    int missing = 0;
    if (covered == NULL) {
        fprintf(stderr, "out of memory in independent recount\n");
        exit(1);
    }
    covered[0] = 1;
    for (int left = 0; left < length; ++left) {
        covered[columns[left]] = 1;
        for (int right = 0; right < left; ++right) {
            covered[columns[left] ^ columns[right]] = 1;
        }
    }
    for (int syndrome = 0; syndrome < space; ++syndrome) {
        if (!covered[syndrome]) {
            if (missing_values != NULL) {
                missing_values[missing] = syndrome;
            }
            ++missing;
        }
    }
    free(covered);
    return missing;
}

static void write_checkpoint_locked(void) {
    char temporary[4096];
    FILE *file;
    int columns[MAX_N];
    int *missing_values;
    int independently_missing;
    if (snprintf(temporary, sizeof(temporary), "%s.tmp", output_path) >=
        (int)sizeof(temporary)) {
        fprintf(stderr, "output path is too long\n");
        return;
    }
    memcpy(columns, global_best_columns, (size_t)length * sizeof(int));
    qsort(columns, length, sizeof(columns[0]), compare_ints);
    missing_values = calloc((size_t)space, sizeof(int));
    if (missing_values == NULL) {
        fprintf(stderr, "out of memory writing checkpoint\n");
        return;
    }
    independently_missing = count_missing_independently(columns, missing_values);
    if (independently_missing != global_best) {
        fprintf(stderr, "internal checkpoint verification disagrees: %d versus %d\n",
                independently_missing, global_best);
        abort();
    }
    file = fopen(temporary, "w");
    if (file == NULL) {
        fprintf(stderr, "cannot write %s: %s\n", temporary, strerror(errno));
        free(missing_values);
        return;
    }
    fprintf(file, "{\n");
    fprintf(file, "  \"format\": \"odd-r-radius2-search-checkpoint-v1\",\n");
    fprintf(file, "  \"status\": \"%s\",\n",
            global_best == 0 ? "candidate witness" : "search residue");
    fprintf(file, "  \"redundancy\": %d,\n  \"length\": %d,\n", redundancy, length);
    fprintf(file, "  \"paper_length\": %d,\n",
            redundancy == 11 ? 79 : (redundancy == 13 ? 159 : -1));
    fprintf(file, "  \"best_uncovered\": %d,\n", global_best);
    fprintf(file, "  \"rank\": %d,\n", binary_rank(columns, length, redundancy));
    fprintf(file, "  \"elapsed_seconds\": %.6f,\n", elapsed_seconds());
    fprintf(file, "  \"worker\": %d,\n  \"mode\": %d,\n",
            global_best_worker, global_best_mode);
    fprintf(file, "  \"worker_seed\": \"%016llx\",\n",
            (unsigned long long)global_best_seed);
    fprintf(file, "  \"iteration\": %llu,\n",
            (unsigned long long)global_best_iteration);
    fprintf(file, "  \"columns_decimal\": [");
    for (int index = 0; index < length; ++index) {
        fprintf(file, "%s%d", index == 0 ? "" : ", ", columns[index]);
    }
    fprintf(file, "],\n  \"uncovered_syndromes_decimal\": [");
    for (int index = 0; index < independently_missing; ++index) {
        fprintf(file, "%s%d", index == 0 ? "" : ", ", missing_values[index]);
    }
    fprintf(file, "],\n");
    fprintf(file, "  \"warning\": \"A zero residue is only a candidate until independently verified.\"\n");
    fprintf(file, "}\n");
    if (fclose(file) != 0 || rename(temporary, output_path) != 0) {
        fprintf(stderr, "cannot finalize checkpoint %s: %s\n",
                output_path, strerror(errno));
    }
    free(missing_values);
}

static void publish_if_better(Worker *worker, const State *state) {
    int should_print = 0;
    pthread_mutex_lock(&best_mutex);
    if (state->missing < global_best ||
        (state->missing == global_best &&
         state->singletons < global_best_singletons)) {
        global_best = state->missing;
        global_best_singletons = state->singletons;
        memcpy(global_best_columns, state->columns, (size_t)length * sizeof(int));
        global_best_worker = worker->worker_id;
        global_best_mode = worker->mode;
        global_best_iteration = worker->iterations;
        global_best_seed = worker->seed;
        write_checkpoint_locked();
        should_print = 1;
        if (state->missing == 0) {
            found_cover = 1;
            stop_requested = 1;
        }
    }
    pthread_mutex_unlock(&best_mutex);
    if (should_print) {
        fprintf(stdout,
                "best uncovered=%d fragile=%d worker=%d mode=%d iteration=%llu elapsed=%.3f\n",
                state->missing, state->singletons, worker->worker_id, worker->mode,
                (unsigned long long)worker->iterations, elapsed_seconds());
        fflush(stdout);
    }
}

static void kick_state(State *state, uint64_t *rng, int swaps) {
    for (int step = 0; step < swaps; ++step) {
        int slot = (int)(rng_next(rng) % (uint64_t)length);
        int proposal = random_available(state, rng);
        apply_swap(state, slot, proposal);
    }
}

static void make_start_columns(int *columns, int worker_id, uint64_t *rng) {
    unsigned char used[1 << MAX_R];
    memset(used, 0, sizeof(used));
    if (source_count == length) {
        memcpy(columns, source_columns, (size_t)length * sizeof(int));
        return;
    }
    if (source_count == length + 1) {
        int deletion = worker_id % source_count;
        int position = 0;
        for (int index = 0; index < source_count; ++index) {
            if (index != deletion) {
                columns[position++] = source_columns[index];
            }
        }
        return;
    }
    if (source_count > length + 1) {
        int chosen = 0;
        while (chosen < length) {
            int index = (int)(rng_next(rng) % (uint64_t)source_count);
            int column = source_columns[index];
            if (!used[column]) {
                used[column] = 1;
                columns[chosen++] = column;
            }
        }
        return;
    }
    for (int index = 0; index < length; ++index) {
        int column;
        do {
            column = 1 + (int)(rng_next(rng) % (uint64_t)(space - 1));
        } while (used[column]);
        used[column] = 1;
        columns[index] = column;
    }
}

static void *search_worker(void *argument) {
    Worker *worker = (Worker *)argument;
    State state;
    int *start_columns;
    int *local_best_columns;
    uint64_t rng_seed = worker->seed;
    uint64_t rng = splitmix64(&rng_seed);
    uint64_t cycle_length = 160000U + 10000U * (uint64_t)(worker->worker_id % 7);

    state_alloc(&state);
    start_columns = calloc((size_t)length, sizeof(int));
    local_best_columns = calloc((size_t)length, sizeof(int));
    if (start_columns == NULL || local_best_columns == NULL) {
        fprintf(stderr, "out of memory in worker %d\n", worker->worker_id);
        exit(1);
    }
    make_start_columns(start_columns, worker->worker_id, &rng);
    initialize_state(&state, start_columns);
    if (source_count == 0 && worker->worker_id >= 2) {
        kick_state(&state, &rng, 8 + 3 * worker->worker_id);
    } else if (source_count == length + 1 && worker->worker_id >= source_count) {
        kick_state(&state, &rng, 6 + worker->worker_id);
    }
    memcpy(local_best_columns, state.columns, (size_t)length * sizeof(int));
    worker->best_missing = state.missing;
    worker->best_singletons = state.singletons;
    memcpy(worker->best_columns, state.columns, (size_t)length * sizeof(int));
    publish_if_better(worker, &state);

    while (!stop_requested && elapsed_seconds() < time_limit) {
        uint64_t phase_index = worker->iterations % cycle_length;
        double phase = (double)phase_index / (double)(cycle_length - 1U);
        double high_temperature = (worker->mode == 0 || worker->mode == 3) ? 4.0 : 90.0;
        double low_temperature = (worker->mode == 0 || worker->mode == 3) ? 0.012 : 0.08;
        double temperature = high_temperature *
                             pow(low_temperature / high_temperature, phase);
        long old_objective = objective(&state, worker->mode);
        int proposal;
        int slot = -1;
        int removed;
        long new_objective;
        double uniform;

        if ((rng_next(&rng) & 255U) < 238U) {
            proposal = targeted_available(&state, &rng);
        } else {
            proposal = random_available(&state, &rng);
        }

        if (state.missing > 0 && state.missing < 80) {
            long best_trial = (1L << 60);
            int best_slot = 0;
            for (int candidate = 0; candidate < length; ++candidate) {
                int was = state.columns[candidate];
                long trial;
                apply_swap(&state, candidate, proposal);
                trial = objective(&state, worker->mode);
                if (trial < best_trial ||
                    (trial == best_trial && (rng_next(&rng) & 1U))) {
                    best_trial = trial;
                    best_slot = candidate;
                }
                apply_swap(&state, candidate, was);
            }
            slot = best_slot;
        } else {
            slot = (int)(rng_next(&rng) % (uint64_t)length);
        }

        removed = state.columns[slot];
        apply_swap(&state, slot, proposal);
        new_objective = objective(&state, worker->mode);
        uniform = (double)(rng_next(&rng) >> 11) * (1.0 / 9007199254740992.0);
        if (new_objective <= old_objective ||
            (temperature > 1e-12 &&
             uniform < exp((double)(old_objective - new_objective) / temperature))) {
            ++worker->accepted;
            if (state.missing < worker->best_missing ||
                (state.missing == worker->best_missing &&
                 state.singletons < worker->best_singletons)) {
                worker->best_missing = state.missing;
                worker->best_singletons = state.singletons;
                memcpy(worker->best_columns, state.columns,
                       (size_t)length * sizeof(int));
                publish_if_better(worker, &state);
            }
        } else {
            apply_swap(&state, slot, removed);
        }

        ++worker->iterations;
        if (phase_index == cycle_length - 1U) {
            initialize_state(&state, worker->best_columns);
            if ((rng_next(&rng) & 7U) == 0U) {
                kick_state(&state, &rng, 3 + (int)(rng_next(&rng) % 5U));
            }
        }
        (void)local_best_columns;
    }

    free(start_columns);
    free(local_best_columns);
    state_free(&state);
    return NULL;
}

static void usage(const char *argv0) {
    fprintf(stderr,
            "usage: %s --r R --n N [--seconds S] [--threads T] [--seed HEX]\n"
            "          [--output PATH] [--source COLUMNS]\n",
            argv0);
}

int main(int argc, char **argv) {
    Worker *workers;
    pthread_t *threads;
    int have_r = 0;
    int have_n = 0;

    for (int index = 1; index < argc; ++index) {
        if (strcmp(argv[index], "--r") == 0 && index + 1 < argc) {
            redundancy = (int)strtol(argv[++index], NULL, 10);
            have_r = 1;
        } else if (strcmp(argv[index], "--n") == 0 && index + 1 < argc) {
            length = (int)strtol(argv[++index], NULL, 10);
            have_n = 1;
        } else if (strcmp(argv[index], "--seconds") == 0 && index + 1 < argc) {
            time_limit = strtod(argv[++index], NULL);
        } else if (strcmp(argv[index], "--threads") == 0 && index + 1 < argc) {
            thread_count = (int)strtol(argv[++index], NULL, 10);
        } else if (strcmp(argv[index], "--seed") == 0 && index + 1 < argc) {
            if (!parse_hex_or_dec(argv[++index], &master_seed)) {
                fprintf(stderr, "invalid seed\n");
                return 2;
            }
        } else if (strcmp(argv[index], "--output") == 0 && index + 1 < argc) {
            output_path = argv[++index];
        } else if (strcmp(argv[index], "--source") == 0 && index + 1 < argc) {
            source_path = argv[++index];
        } else {
            usage(argv[0]);
            return 2;
        }
    }
    if (!have_r || !have_n || redundancy < 3 || redundancy > MAX_R ||
        length < redundancy || length > MAX_N || thread_count < 1 ||
        thread_count > 64 || time_limit <= 0.0) {
        usage(argv[0]);
        return 2;
    }
    space = 1 << redundancy;
    if (source_path != NULL && !read_source_columns(source_path)) {
        return 1;
    }

    clock_gettime(CLOCK_MONOTONIC, &start_clock);
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);

    workers = calloc((size_t)thread_count, sizeof(*workers));
    threads = calloc((size_t)thread_count, sizeof(*threads));
    if (workers == NULL || threads == NULL) {
        fprintf(stderr, "out of memory allocating workers\n");
        return 1;
    }
    fprintf(stdout,
            "search r=%d n=%d space=%d threads=%d seconds=%.1f seed=0x%llx source=%s\n",
            redundancy, length, space, thread_count, time_limit,
            (unsigned long long)master_seed,
            source_path == NULL ? "(random)" : source_path);
    fflush(stdout);

    for (int index = 0; index < thread_count; ++index) {
        uint64_t local = master_seed ^ (UINT64_C(0x9E3779B97F4A7C15) *
                                        (uint64_t)(index + 1));
        workers[index].worker_id = index;
        workers[index].mode = index % 6;
        workers[index].seed = splitmix64(&local);
        workers[index].best_columns = calloc((size_t)length, sizeof(int));
        if (workers[index].best_columns == NULL) {
            fprintf(stderr, "out of memory allocating worker columns\n");
            return 1;
        }
        if (pthread_create(&threads[index], NULL, search_worker, &workers[index]) != 0) {
            fprintf(stderr, "cannot start worker %d\n", index);
            return 1;
        }
    }
    for (int index = 0; index < thread_count; ++index) {
        pthread_join(threads[index], NULL);
    }

    fprintf(stdout,
            "done best_uncovered=%d fragile=%d rank=%d cover=%s elapsed=%.3f output=%s\n",
            global_best, global_best_singletons,
            binary_rank(global_best_columns, length, redundancy),
            found_cover ? "yes" : "no", elapsed_seconds(), output_path);
    for (int index = 0; index < thread_count; ++index) {
        free(workers[index].best_columns);
    }
    free(workers);
    free(threads);
    return found_cover ? 0 : 1;
}
