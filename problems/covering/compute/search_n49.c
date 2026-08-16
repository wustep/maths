/*
 * Focused q2 search for a 49-point 1-saturating set in F_2^10.
 *
 * The input is the certified q1 10 x 50 parity-check matrix.  Each worker
 * deletes one column, then performs fixed-cardinality swaps.  Coverage counts
 * are maintained incrementally: a swap touches one singleton and the 48 pair
 * sums incident with the changed column.  Workers deliberately use several
 * objective functions (plain uncovered count, low-multiplicity penalties,
 * and dynamic weights for persistently uncovered syndromes).
 *
 * This is discovery code, not a verifier.  It writes a JSON checkpoint every
 * time the process-wide best uncovered count improves.  Any zero-residue
 * checkpoint must still be checked independently by Python.
 *
 * Build (from the problem directory):
 *   gcc -O3 -std=c11 -Wall -Wextra -pthread compute/search_n49.c \
 *       -lm -o compute/search_n49
 *
 * Example:
 *   compute/search_n49 --seconds 300 --threads 8 \
 *       --input compute/H_r10_n50.txt \
 *       --output compute/q2_search_checkpoint.json
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

enum { REDUNDANCY = 10, SPACE = 1 << REDUNDANCY, Q1_N = 50, N = 49 };

typedef struct {
    int counts[SPACE];
    int columns[N];
    unsigned char member[SPACE];
    int zero_list[SPACE];
    int zero_pos[SPACE];
    int missing;
    int singletons;
    long weighted_missing;
    int weights[SPACE];
} State;

typedef struct {
    int worker_id;
    int mode;
    uint64_t seed;
    uint64_t iterations;
    uint64_t accepted;
    int best_missing;
    int best_singletons;
    int best_columns[N];
} Worker;

static int q1_columns[Q1_N];
static int thread_count = 1;
static double time_limit = 60.0;
static uint64_t master_seed = UINT64_C(0x243F6A8885A308D3);
static const char *input_path = "compute/H_r10_n50.txt";
static const char *output_path = "compute/q2_search_checkpoint.json";
static struct timespec start_clock;
static volatile sig_atomic_t stop_requested = 0;
static pthread_mutex_t best_mutex = PTHREAD_MUTEX_INITIALIZER;
static int global_best = SPACE;
static int global_best_singletons = SPACE;
static int global_best_columns[N];
static int global_best_worker = -1;
static int global_best_mode = -1;
static uint64_t global_best_iteration = 0;
static uint64_t global_best_seed = 0;

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

static double rng_unit(uint64_t *state) {
    return (double)(rng_next(state) >> 11) * (1.0 / 9007199254740992.0);
}

static int compare_ints(const void *left, const void *right) {
    const int a = *(const int *)left;
    const int b = *(const int *)right;
    return (a > b) - (a < b);
}

static int binary_rank(const int *columns, int length) {
    int basis[REDUNDANCY] = {0};
    int rank = 0;
    for (int index = 0; index < length; ++index) {
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

static int read_q1_matrix(const char *path) {
    FILE *file = fopen(path, "r");
    char line[8192];
    int row = 0;
    if (file == NULL) {
        fprintf(stderr, "cannot open %s: %s\n", path, strerror(errno));
        return 0;
    }
    memset(q1_columns, 0, sizeof(q1_columns));
    while (fgets(line, sizeof(line), file) != NULL) {
        char *token;
        char *save = NULL;
        int column = 0;
        if (line[0] == '#' || line[0] == '\n' || line[0] == '\r') {
            continue;
        }
        token = strtok_r(line, " \t\r\n", &save);
        while (token != NULL) {
            char *end = NULL;
            long bit = strtol(token, &end, 10);
            if (end == token || *end != '\0' || (bit != 0 && bit != 1) ||
                row >= REDUNDANCY || column >= Q1_N) {
                fclose(file);
                fprintf(stderr, "malformed matrix entry in %s\n", path);
                return 0;
            }
            q1_columns[column] |= ((int)bit) << row;
            ++column;
            token = strtok_r(NULL, " \t\r\n", &save);
        }
        if (column != Q1_N) {
            fclose(file);
            fprintf(stderr, "matrix row %d has %d columns, expected %d\n",
                    row + 1, column, Q1_N);
            return 0;
        }
        ++row;
    }
    fclose(file);
    if (row != REDUNDANCY) {
        fprintf(stderr, "matrix has %d rows, expected %d\n", row, REDUNDANCY);
        return 0;
    }
    if (binary_rank(q1_columns, Q1_N) != REDUNDANCY) {
        fprintf(stderr, "q1 matrix does not have rank %d\n", REDUNDANCY);
        return 0;
    }
    for (int i = 0; i < Q1_N; ++i) {
        if (q1_columns[i] <= 0 || q1_columns[i] >= SPACE) {
            fprintf(stderr, "q1 matrix has an invalid column\n");
            return 0;
        }
        for (int j = 0; j < i; ++j) {
            if (q1_columns[i] == q1_columns[j]) {
                fprintf(stderr, "q1 matrix has repeated columns\n");
                return 0;
            }
        }
    }
    return 1;
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
    memset(state, 0, sizeof(*state));
    for (int syndrome = 0; syndrome < SPACE; ++syndrome) {
        state->zero_pos[syndrome] = -1;
        state->weights[syndrome] = 1;
    }
    memcpy(state->columns, columns, sizeof(state->columns));
    state->counts[0] = 1;
    for (int index = 0; index < N; ++index) {
        int column = state->columns[index];
        state->member[column] = 1;
        ++state->counts[column];
        for (int previous = 0; previous < index; ++previous) {
            ++state->counts[column ^ state->columns[previous]];
        }
    }
    state->missing = 0;
    state->singletons = 0;
    state->weighted_missing = 0;
    for (int syndrome = 0; syndrome < SPACE; ++syndrome) {
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
    for (int index = 0; index < N; ++index) {
        if (index != slot) {
            change_count(state, removed ^ state->columns[index], -1);
        }
    }
}

static void add_slot(State *state, int slot, int added) {
    change_count(state, added, +1);
    for (int index = 0; index < N; ++index) {
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

static void undo_swap(State *state, int slot, int removed) {
    int added = state->columns[slot];
    remove_slot(state, slot);
    add_slot(state, slot, removed);
    state->member[added] = 0;
    state->member[removed] = 1;
    state->columns[slot] = removed;
}

static long objective(const State *state, int mode) {
    switch (mode) {
        case 0:
        case 5:
            return state->missing;
        case 1:
            return 24L * state->missing + state->singletons;
        case 2:
        case 6:
            return state->weighted_missing;
        case 3:
            return 96L * state->missing + state->singletons;
        case 4:
        default:
            return 8L * state->missing + state->singletons;
    }
}

static int random_available(State *state, uint64_t *rng) {
    int proposal;
    do {
        proposal = 1 + (int)(rng_next(rng) % (SPACE - 1));
    } while (state->member[proposal]);
    return proposal;
}

static int targeted_available(State *state, uint64_t *rng, int mode) {
    int target;
    int proposal = 0;
    if (state->missing <= 0) {
        return random_available(state, rng);
    }
    target = state->zero_list[rng_next(rng) % (uint64_t)state->missing];
    if (mode == 2 || mode == 6) {
        /* Bias toward a persistently missed syndrome without an O(1024) scan. */
        for (int sample = 0; sample < 7; ++sample) {
            int candidate = state->zero_list[rng_next(rng) % (uint64_t)state->missing];
            if (state->weights[candidate] > state->weights[target]) {
                target = candidate;
            }
        }
    }
    for (int attempt = 0; attempt < 64; ++attempt) {
        if ((rng_next(rng) & 31U) == 0U) {
            proposal = target;
        } else {
            proposal = target ^ state->columns[rng_next(rng) % N];
        }
        if (proposal != 0 && !state->member[proposal]) {
            return proposal;
        }
    }
    return random_available(state, rng);
}

static void make_seed_columns(int *columns, int deletion) {
    int position = 0;
    for (int index = 0; index < Q1_N; ++index) {
        if (index != deletion) {
            columns[position++] = q1_columns[index];
        }
    }
}

static int count_missing_independently(const int *columns, int *missing_values) {
    unsigned char covered[SPACE] = {0};
    int missing = 0;
    covered[0] = 1;
    for (int left = 0; left < N; ++left) {
        covered[columns[left]] = 1;
        for (int right = 0; right < left; ++right) {
            covered[columns[left] ^ columns[right]] = 1;
        }
    }
    for (int syndrome = 0; syndrome < SPACE; ++syndrome) {
        if (!covered[syndrome]) {
            if (missing_values != NULL) {
                missing_values[missing] = syndrome;
            }
            ++missing;
        }
    }
    return missing;
}

static void write_checkpoint_locked(void) {
    char temporary[4096];
    FILE *file;
    int columns[N];
    int missing_values[SPACE];
    int independently_missing;
    int histogram[N + 2];
    int counts[SPACE] = {0};
    if (snprintf(temporary, sizeof(temporary), "%s.tmp", output_path) >=
        (int)sizeof(temporary)) {
        fprintf(stderr, "output path is too long\n");
        return;
    }
    memcpy(columns, global_best_columns, sizeof(columns));
    qsort(columns, N, sizeof(columns[0]), compare_ints);
    independently_missing = count_missing_independently(columns, missing_values);
    if (independently_missing != global_best) {
        fprintf(stderr, "internal checkpoint verification disagrees: %d versus %d\n",
                independently_missing, global_best);
        abort();
    }
    memset(histogram, 0, sizeof(histogram));
    counts[0] = 1;
    for (int left = 0; left < N; ++left) {
        ++counts[columns[left]];
        for (int right = 0; right < left; ++right) {
            ++counts[columns[left] ^ columns[right]];
        }
    }
    for (int syndrome = 0; syndrome < SPACE; ++syndrome) {
        int value = counts[syndrome];
        if (value >= 0 && value < N + 2) {
            ++histogram[value];
        }
    }
    file = fopen(temporary, "w");
    if (file == NULL) {
        fprintf(stderr, "cannot write %s: %s\n", temporary, strerror(errno));
        return;
    }
    fprintf(file, "{\n");
    fprintf(file, "  \"format\": \"q2-n49-search-checkpoint-v1\",\n");
    fprintf(file, "  \"status\": \"%s\",\n", global_best == 0 ? "candidate witness" : "search residue");
    fprintf(file, "  \"redundancy\": 10,\n  \"length\": 49,\n");
    fprintf(file, "  \"best_uncovered\": %d,\n", global_best);
    fprintf(file, "  \"rank\": %d,\n", binary_rank(columns, N));
    fprintf(file, "  \"elapsed_seconds\": %.6f,\n", elapsed_seconds());
    fprintf(file, "  \"worker\": %d,\n  \"mode\": %d,\n", global_best_worker, global_best_mode);
    fprintf(file, "  \"worker_seed\": \"%016llx\",\n",
            (unsigned long long)global_best_seed);
    fprintf(file, "  \"iteration\": %llu,\n",
            (unsigned long long)global_best_iteration);
    fprintf(file, "  \"columns_decimal\": [");
    for (int index = 0; index < N; ++index) {
        fprintf(file, "%s%d", index == 0 ? "" : ", ", columns[index]);
    }
    fprintf(file, "],\n  \"columns_hex\": [");
    for (int index = 0; index < N; ++index) {
        fprintf(file, "%s\"%03X\"", index == 0 ? "" : ", ", columns[index]);
    }
    fprintf(file, "],\n  \"uncovered_syndromes_decimal\": [");
    for (int index = 0; index < independently_missing; ++index) {
        fprintf(file, "%s%d", index == 0 ? "" : ", ", missing_values[index]);
    }
    fprintf(file, "],\n  \"uncovered_syndromes_hex\": [");
    for (int index = 0; index < independently_missing; ++index) {
        fprintf(file, "%s\"%03X\"", index == 0 ? "" : ", ", missing_values[index]);
    }
    fprintf(file, "],\n  \"representation_multiplicities\": {");
    int first = 1;
    for (int count = 0; count < N + 2; ++count) {
        if (histogram[count] != 0) {
            fprintf(file, "%s\"%d\": %d", first ? "" : ", ", count, histogram[count]);
            first = 0;
        }
    }
    fprintf(file, "},\n");
    fprintf(file, "  \"source_matrix\": \"%s\",\n", input_path);
    fprintf(file, "  \"warning\": \"A zero residue is only a candidate until independently verified.\"\n");
    fprintf(file, "}\n");
    if (fclose(file) != 0 || rename(temporary, output_path) != 0) {
        fprintf(stderr, "cannot finalize checkpoint %s: %s\n", output_path, strerror(errno));
    }
}

static void publish_if_better(Worker *worker, const State *state) {
    int should_print = 0;
    pthread_mutex_lock(&best_mutex);
    if (state->missing < global_best ||
        (state->missing == global_best && state->singletons < global_best_singletons)) {
        global_best = state->missing;
        global_best_singletons = state->singletons;
        memcpy(global_best_columns, state->columns, sizeof(global_best_columns));
        global_best_worker = worker->worker_id;
        global_best_mode = worker->mode;
        global_best_iteration = worker->iterations;
        global_best_seed = worker->seed;
        write_checkpoint_locked();
        should_print = 1;
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
        int slot = (int)(rng_next(rng) % N);
        int proposal = random_available(state, rng);
        apply_swap(state, slot, proposal);
    }
}

static void reset_weights(State *state) {
    state->weighted_missing = 0;
    for (int syndrome = 0; syndrome < SPACE; ++syndrome) {
        state->weights[syndrome] = 1;
        if (state->counts[syndrome] == 0) {
            ++state->weighted_missing;
        }
    }
}

static void bump_missing_weights(State *state) {
    for (int index = 0; index < state->missing; ++index) {
        int syndrome = state->zero_list[index];
        if (state->weights[syndrome] < 10000) {
            ++state->weights[syndrome];
            ++state->weighted_missing;
        }
    }
}

static void *search_worker(void *argument) {
    Worker *worker = (Worker *)argument;
    State state;
    int seed_columns[N];
    int local_best_columns[N];
    int local_best_missing;
    int local_best_singletons;
    uint64_t rng_seed = worker->seed;
    uint64_t rng = splitmix64(&rng_seed);
    const int preferred_deletions[] = {21, 26, 46, 17, 11, 15, 27, 33, 37};
    int deletion = preferred_deletions[worker->worker_id %
                                       (int)(sizeof(preferred_deletions) /
                                             sizeof(preferred_deletions[0]))];
    uint64_t cycle_length = 120000U + 10000U * (uint64_t)(worker->worker_id % 7);
    uint64_t stagnant_cycles = 0;

    make_seed_columns(seed_columns, deletion);
    initialize_state(&state, seed_columns);
    if (worker->worker_id >= (int)(sizeof(preferred_deletions) /
                                   sizeof(preferred_deletions[0]))) {
        kick_state(&state, &rng, 20 + worker->worker_id);
    }
    local_best_missing = state.missing;
    local_best_singletons = state.singletons;
    memcpy(local_best_columns, state.columns, sizeof(local_best_columns));
    worker->best_missing = state.missing;
    worker->best_singletons = state.singletons;
    memcpy(worker->best_columns, state.columns, sizeof(worker->best_columns));
    publish_if_better(worker, &state);

    while (!stop_requested && elapsed_seconds() < time_limit) {
        uint64_t phase_index = worker->iterations % cycle_length;
        double phase = (double)phase_index / (double)(cycle_length - 1U);
        double high_temperature;
        double low_temperature;
        int trials;
        long old_objective = objective(&state, worker->mode);
        long selected_objective = 0;
        int selected_slot = -1;
        int selected_proposal = -1;

        if (worker->mode == 0 || worker->mode == 5) {
            high_temperature = worker->mode == 0 ? 3.8 : 2.2;
            low_temperature = 0.012;
            trials = worker->mode == 0 ? 1 : 3;
        } else if (worker->mode == 2 || worker->mode == 6) {
            high_temperature = worker->mode == 2 ? 5.0 : 2.5;
            low_temperature = 0.02;
            trials = worker->mode == 2 ? 2 : 5;
        } else {
            high_temperature = worker->mode == 1 ? 75.0 :
                               (worker->mode == 3 ? 180.0 : 35.0);
            low_temperature = 0.08;
            trials = worker->mode == 3 ? 4 : 3;
        }

        for (int trial = 0; trial < trials; ++trial) {
            int proposal;
            int slot;
            int removed;
            long trial_objective;
            if ((rng_next(&rng) & 255U) < (worker->mode == 4 ? 205U : 232U)) {
                proposal = targeted_available(&state, &rng, worker->mode);
            } else {
                proposal = random_available(&state, &rng);
            }
            slot = (int)(rng_next(&rng) % N);
            removed = state.columns[slot];
            apply_swap(&state, slot, proposal);
            trial_objective = objective(&state, worker->mode);
            if (selected_slot < 0 || trial_objective < selected_objective ||
                (trial_objective == selected_objective && (rng_next(&rng) & 1U))) {
                selected_objective = trial_objective;
                selected_slot = slot;
                selected_proposal = proposal;
            }
            undo_swap(&state, slot, removed);
        }

        {
            int removed = state.columns[selected_slot];
            long delta;
            double temperature = high_temperature *
                pow(low_temperature / high_temperature, phase);
            int accept;
            apply_swap(&state, selected_slot, selected_proposal);
            selected_objective = objective(&state, worker->mode);
            delta = selected_objective - old_objective;
            accept = delta <= 0 || rng_unit(&rng) < exp(-(double)delta / temperature);
            if (accept) {
                ++worker->accepted;
            } else {
                undo_swap(&state, selected_slot, removed);
            }
        }
        ++worker->iterations;

        if (state.missing < local_best_missing ||
            (state.missing == local_best_missing && state.singletons < local_best_singletons)) {
            local_best_missing = state.missing;
            local_best_singletons = state.singletons;
            memcpy(local_best_columns, state.columns, sizeof(local_best_columns));
            stagnant_cycles = 0;
            if (state.missing < worker->best_missing ||
                (state.missing == worker->best_missing &&
                 state.singletons < worker->best_singletons)) {
                worker->best_missing = state.missing;
                worker->best_singletons = state.singletons;
                memcpy(worker->best_columns, state.columns, sizeof(worker->best_columns));
                publish_if_better(worker, &state);
            }
            if (state.missing == 0) {
                stop_requested = 1;
                break;
            }
        }

        if (phase_index + 1U == cycle_length) {
            ++stagnant_cycles;
            if (worker->mode == 2 || worker->mode == 6) {
                bump_missing_weights(&state);
                if (stagnant_cycles % 12U == 0U) {
                    reset_weights(&state);
                }
            } else {
                initialize_state(&state, local_best_columns);
                kick_state(&state, &rng, 2 + (int)(stagnant_cycles % 9U));
            }
            if (stagnant_cycles % 25U == 0U) {
                int new_deletion = preferred_deletions[
                    rng_next(&rng) % (sizeof(preferred_deletions) /
                                      sizeof(preferred_deletions[0]))];
                make_seed_columns(seed_columns, new_deletion);
                initialize_state(&state, seed_columns);
                kick_state(&state, &rng, 10 + (int)(rng_next(&rng) % 31U));
                local_best_missing = state.missing;
                local_best_singletons = state.singletons;
                memcpy(local_best_columns, state.columns, sizeof(local_best_columns));
                stagnant_cycles = 0;
            }
        }
    }
    return NULL;
}

static int parse_int(const char *text, int minimum, int maximum, const char *name) {
    char *end = NULL;
    long value = strtol(text, &end, 10);
    if (end == text || *end != '\0' || value < minimum || value > maximum) {
        fprintf(stderr, "invalid %s: %s\n", name, text);
        exit(2);
    }
    return (int)value;
}

static double parse_double(const char *text, double minimum, double maximum,
                           const char *name) {
    char *end = NULL;
    double value = strtod(text, &end);
    if (end == text || *end != '\0' || value < minimum || value > maximum) {
        fprintf(stderr, "invalid %s: %s\n", name, text);
        exit(2);
    }
    return value;
}

static uint64_t parse_seed(const char *text) {
    char *end = NULL;
    unsigned long long value = strtoull(text, &end, 0);
    if (end == text || *end != '\0' || value == 0) {
        fprintf(stderr, "invalid seed: %s\n", text);
        exit(2);
    }
    return (uint64_t)value;
}

static void usage(const char *program) {
    fprintf(stderr,
            "usage: %s [--seconds N] [--threads N] [--seed N] "
            "[--input PATH] [--output PATH]\n",
            program);
}

int main(int argc, char **argv) {
    pthread_t *threads;
    Worker *workers;
    int created = 0;
    for (int index = 1; index < argc; ++index) {
        if (strcmp(argv[index], "--seconds") == 0 && index + 1 < argc) {
            time_limit = parse_double(argv[++index], 0.01, 86400.0, "seconds");
        } else if (strcmp(argv[index], "--threads") == 0 && index + 1 < argc) {
            thread_count = parse_int(argv[++index], 1, 256, "threads");
        } else if (strcmp(argv[index], "--seed") == 0 && index + 1 < argc) {
            master_seed = parse_seed(argv[++index]);
        } else if (strcmp(argv[index], "--input") == 0 && index + 1 < argc) {
            input_path = argv[++index];
        } else if (strcmp(argv[index], "--output") == 0 && index + 1 < argc) {
            output_path = argv[++index];
        } else {
            usage(argv[0]);
            return 2;
        }
    }
    if (!read_q1_matrix(input_path)) {
        return 2;
    }
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);
    clock_gettime(CLOCK_MONOTONIC, &start_clock);
    threads = calloc((size_t)thread_count, sizeof(*threads));
    workers = calloc((size_t)thread_count, sizeof(*workers));
    if (threads == NULL || workers == NULL) {
        fprintf(stderr, "out of memory\n");
        free(threads);
        free(workers);
        return 2;
    }
    fprintf(stdout,
            "q2 n=49 search: threads=%d seconds=%.3f master_seed=0x%016llx\n",
            thread_count, time_limit, (unsigned long long)master_seed);
    fflush(stdout);
    for (int index = 0; index < thread_count; ++index) {
        uint64_t seed_state = master_seed + (uint64_t)index;
        workers[index].worker_id = index;
        workers[index].mode = index % 7;
        workers[index].seed = splitmix64(&seed_state);
        workers[index].best_missing = SPACE;
        if (pthread_create(&threads[index], NULL, search_worker, &workers[index]) != 0) {
            fprintf(stderr, "failed to create worker %d\n", index);
            stop_requested = 1;
            break;
        }
        ++created;
    }
    for (int index = 0; index < created; ++index) {
        pthread_join(threads[index], NULL);
    }
    pthread_mutex_lock(&best_mutex);
    write_checkpoint_locked();
    pthread_mutex_unlock(&best_mutex);
    fprintf(stdout, "finished: elapsed=%.3f best_uncovered=%d\n",
            elapsed_seconds(), global_best);
    for (int index = 0; index < created; ++index) {
        fprintf(stdout,
                "worker=%d mode=%d iterations=%llu accepted=%llu best=%d fragile=%d\n",
                workers[index].worker_id, workers[index].mode,
                (unsigned long long)workers[index].iterations,
                (unsigned long long)workers[index].accepted,
                workers[index].best_missing, workers[index].best_singletons);
    }
    free(threads);
    free(workers);
    return global_best == 0 ? 0 : 1;
}
