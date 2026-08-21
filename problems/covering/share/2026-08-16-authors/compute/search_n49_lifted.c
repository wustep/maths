/*
 * Lifted q2 search: optimize 50 columns by the best 49-column deletion.
 *
 * For a 50-set S, let m be its number of uncovered syndromes.  Deleting a
 * column x additionally uncovers exactly those singleton/pair representations
 * incident with x whose multiplicity in S is one.  Hence
 *
 *   score(S) = m + min_x unique_incident_S(x)
 *
 * is exactly the smallest uncovered count among all 49-subsets of S.  A
 * 50-column swap can change which point is regarded as the spare, making this
 * a genuine large neighborhood on 49-sets.  Score zero is an n=49 witness.
 *
 * This is discovery code; the JSON checkpoint independently re-enumerates its
 * selected 49-set, but a candidate must also pass the Python verifier.
 *
 * Build:
 *   gcc -O3 -std=c11 -Wall -Wextra -pthread \
 *       compute/search_n49_lifted.c -lm -o compute/search_n49_lifted
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

enum { R = 10, V = 1 << R, N = 50, TARGET_N = 49, MAX_TRIALS = 6 };

typedef struct {
    int columns[N];
    int counts[V];
    unsigned char member[V];
    int uncovered;
    int ones;
} State;

typedef struct {
    int id;
    int mode;
    uint64_t seed;
    uint64_t iterations;
    uint64_t accepted;
    int best_score;
    int best_ones;
    int best_deleted_slot;
    int best_columns[N];
} Worker;

static int q1_columns[N];
static int thread_count = 8;
static double time_limit = 60.0;
static uint64_t master_seed = UINT64_C(0x3BD39E10CB0EF593);
static const char *input_path = "compute/H_r10_n50.txt";
static const char *output_path = "compute/q2_lifted_checkpoint.json";
static struct timespec start_clock;
static volatile sig_atomic_t stop_requested = 0;
static pthread_mutex_t best_mutex = PTHREAD_MUTEX_INITIALIZER;
static int global_score = V;
static int global_ones = V;
static int global_deleted_slot = -1;
static int global_columns[N];
static int global_worker = -1;
static int global_mode = -1;
static uint64_t global_iteration = 0;
static uint64_t global_seed = 0;

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
    int basis[R] = {0};
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

static int read_matrix(const char *path) {
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
                row >= R || column >= N) {
                fclose(file);
                fprintf(stderr, "malformed matrix entry in %s\n", path);
                return 0;
            }
            q1_columns[column] |= ((int)bit) << row;
            ++column;
            token = strtok_r(NULL, " \t\r\n", &save);
        }
        if (column != N) {
            fclose(file);
            fprintf(stderr, "matrix row %d has %d columns, expected %d\n",
                    row + 1, column, N);
            return 0;
        }
        ++row;
    }
    fclose(file);
    if (row != R || binary_rank(q1_columns, N) != R) {
        fprintf(stderr, "input is not a rank-10 10 x 50 matrix\n");
        return 0;
    }
    for (int i = 0; i < N; ++i) {
        if (q1_columns[i] <= 0 || q1_columns[i] >= V) {
            fprintf(stderr, "input has a zero or out-of-range column\n");
            return 0;
        }
        for (int j = 0; j < i; ++j) {
            if (q1_columns[i] == q1_columns[j]) {
                fprintf(stderr, "input has a repeated column\n");
                return 0;
            }
        }
    }
    return 1;
}

static void initialize(State *state, const int *columns) {
    memset(state, 0, sizeof(*state));
    memcpy(state->columns, columns, sizeof(state->columns));
    state->counts[0] = 1;
    for (int left = 0; left < N; ++left) {
        int column = state->columns[left];
        state->member[column] = 1;
        ++state->counts[column];
        for (int right = 0; right < left; ++right) {
            ++state->counts[column ^ state->columns[right]];
        }
    }
    for (int syndrome = 0; syndrome < V; ++syndrome) {
        if (state->counts[syndrome] == 0) {
            ++state->uncovered;
        } else if (state->counts[syndrome] == 1) {
            ++state->ones;
        }
    }
}

static void change_count(State *state, int syndrome, int delta) {
    int before = state->counts[syndrome];
    int after = before + delta;
    if (after < 0) {
        fprintf(stderr, "internal error: negative count\n");
        abort();
    }
    if (before == 0 && after == 1) {
        --state->uncovered;
        ++state->ones;
    } else if (before == 1 && after == 0) {
        ++state->uncovered;
        --state->ones;
    } else if (before == 1 && after == 2) {
        --state->ones;
    } else if (before == 2 && after == 1) {
        ++state->ones;
    }
    state->counts[syndrome] = after;
}

static void swap_column(State *state, int slot, int added) {
    int removed = state->columns[slot];
    change_count(state, removed, -1);
    for (int index = 0; index < N; ++index) {
        if (index != slot) {
            change_count(state, removed ^ state->columns[index], -1);
        }
    }
    change_count(state, added, +1);
    for (int index = 0; index < N; ++index) {
        if (index != slot) {
            change_count(state, added ^ state->columns[index], +1);
        }
    }
    state->member[removed] = 0;
    state->member[added] = 1;
    state->columns[slot] = added;
}

static int evaluate(const State *state, int *deleted_slot) {
    int best_damage = V;
    int best_slot = -1;
    for (int slot = 0; slot < N; ++slot) {
        int column = state->columns[slot];
        int damage = state->counts[column] == 1;
        for (int index = 0; index < N; ++index) {
            if (index != slot &&
                state->counts[column ^ state->columns[index]] == 1) {
                ++damage;
            }
        }
        if (damage < best_damage) {
            best_damage = damage;
            best_slot = slot;
        }
    }
    *deleted_slot = best_slot;
    return state->uncovered + best_damage;
}

static int collect_deletion_holes(const State *state, int deleted_slot,
                                  int *holes) {
    unsigned char listed[V] = {0};
    int count = 0;
    int deleted = state->columns[deleted_slot];
    for (int syndrome = 0; syndrome < V; ++syndrome) {
        if (state->counts[syndrome] == 0) {
            listed[syndrome] = 1;
            holes[count++] = syndrome;
        }
    }
    if (state->counts[deleted] == 1 && !listed[deleted]) {
        listed[deleted] = 1;
        holes[count++] = deleted;
    }
    for (int index = 0; index < N; ++index) {
        int syndrome;
        if (index == deleted_slot) {
            continue;
        }
        syndrome = deleted ^ state->columns[index];
        if (state->counts[syndrome] == 1 && !listed[syndrome]) {
            listed[syndrome] = 1;
            holes[count++] = syndrome;
        }
    }
    return count;
}

static int random_available(const State *state, uint64_t *rng) {
    int value;
    do {
        value = 1 + (int)(rng_next(rng) % (V - 1));
    } while (state->member[value]);
    return value;
}

static int independent_missing(const int *columns, int length,
                               int *missing_values, int *histogram) {
    int counts[V] = {0};
    int missing = 0;
    counts[0] = 1;
    for (int left = 0; left < length; ++left) {
        ++counts[columns[left]];
        for (int right = 0; right < left; ++right) {
            ++counts[columns[left] ^ columns[right]];
        }
    }
    if (histogram != NULL) {
        memset(histogram, 0, (N + 2) * sizeof(histogram[0]));
    }
    for (int syndrome = 0; syndrome < V; ++syndrome) {
        if (counts[syndrome] == 0) {
            if (missing_values != NULL) {
                missing_values[missing] = syndrome;
            }
            ++missing;
        }
        if (histogram != NULL && counts[syndrome] < N + 2) {
            ++histogram[counts[syndrome]];
        }
    }
    return missing;
}

static void write_checkpoint_locked(void) {
    char temporary[4096];
    int columns[TARGET_N];
    int missing_values[V];
    int histogram[N + 2];
    int position = 0;
    int missing;
    FILE *file;
    for (int index = 0; index < N; ++index) {
        if (index != global_deleted_slot) {
            columns[position++] = global_columns[index];
        }
    }
    qsort(columns, TARGET_N, sizeof(columns[0]), compare_ints);
    missing = independent_missing(columns, TARGET_N, missing_values, histogram);
    if (position != TARGET_N || missing != global_score) {
        fprintf(stderr, "internal lifted-score verification failed\n");
        abort();
    }
    if (snprintf(temporary, sizeof(temporary), "%s.tmp", output_path) >=
        (int)sizeof(temporary)) {
        fprintf(stderr, "output path too long\n");
        return;
    }
    file = fopen(temporary, "w");
    if (file == NULL) {
        fprintf(stderr, "cannot write %s: %s\n", temporary, strerror(errno));
        return;
    }
    fprintf(file, "{\n  \"format\": \"q2-n49-lifted-checkpoint-v1\",\n");
    fprintf(file, "  \"status\": \"%s\",\n",
            missing == 0 ? "candidate witness" : "search residue");
    fprintf(file, "  \"redundancy\": 10,\n  \"length\": 49,\n");
    fprintf(file, "  \"best_uncovered\": %d,\n", missing);
    fprintf(file, "  \"rank\": %d,\n", binary_rank(columns, TARGET_N));
    fprintf(file, "  \"elapsed_seconds\": %.6f,\n", elapsed_seconds());
    fprintf(file, "  \"worker\": %d,\n  \"mode\": %d,\n",
            global_worker, global_mode);
    fprintf(file, "  \"worker_seed\": \"%016llx\",\n",
            (unsigned long long)global_seed);
    fprintf(file, "  \"iteration\": %llu,\n",
            (unsigned long long)global_iteration);
    fprintf(file, "  \"deleted_column_decimal\": %d,\n",
            global_columns[global_deleted_slot]);
    fprintf(file, "  \"columns_decimal\": [");
    for (int index = 0; index < TARGET_N; ++index) {
        fprintf(file, "%s%d", index == 0 ? "" : ", ", columns[index]);
    }
    fprintf(file, "],\n  \"columns_hex\": [");
    for (int index = 0; index < TARGET_N; ++index) {
        fprintf(file, "%s\"%03X\"", index == 0 ? "" : ", ", columns[index]);
    }
    fprintf(file, "],\n  \"uncovered_syndromes_decimal\": [");
    for (int index = 0; index < missing; ++index) {
        fprintf(file, "%s%d", index == 0 ? "" : ", ", missing_values[index]);
    }
    fprintf(file, "],\n  \"uncovered_syndromes_hex\": [");
    for (int index = 0; index < missing; ++index) {
        fprintf(file, "%s\"%03X\"", index == 0 ? "" : ", ", missing_values[index]);
    }
    fprintf(file, "],\n  \"representation_multiplicities\": {");
    int first = 1;
    for (int value = 0; value < N + 2; ++value) {
        if (histogram[value] != 0) {
            fprintf(file, "%s\"%d\": %d", first ? "" : ", ",
                    value, histogram[value]);
            first = 0;
        }
    }
    fprintf(file, "},\n  \"source_matrix\": \"%s\",\n", input_path);
    fprintf(file, "  \"method\": \"50-column lifted search scored by its cheapest deletion\",\n");
    fprintf(file, "  \"warning\": \"A zero residue is only a candidate until independently verified.\"\n}\n");
    if (fclose(file) != 0 || rename(temporary, output_path) != 0) {
        fprintf(stderr, "cannot finalize %s: %s\n", output_path, strerror(errno));
    }
}

static void publish_if_better(Worker *worker, const State *state,
                              int score, int deleted_slot) {
    int changed = 0;
    pthread_mutex_lock(&best_mutex);
    if (score < global_score || (score == global_score && state->ones < global_ones)) {
        global_score = score;
        global_ones = state->ones;
        global_deleted_slot = deleted_slot;
        memcpy(global_columns, state->columns, sizeof(global_columns));
        global_worker = worker->id;
        global_mode = worker->mode;
        global_iteration = worker->iterations;
        global_seed = worker->seed;
        write_checkpoint_locked();
        changed = 1;
    }
    pthread_mutex_unlock(&best_mutex);
    if (changed) {
        fprintf(stdout,
                "best deletion residue=%d full_missing=%d ones=%d worker=%d mode=%d iteration=%llu elapsed=%.3f\n",
                score, state->uncovered, state->ones, worker->id, worker->mode,
                (unsigned long long)worker->iterations, elapsed_seconds());
        fflush(stdout);
    }
}

static void kick(State *state, uint64_t *rng, int number) {
    for (int step = 0; step < number; ++step) {
        int slot = (int)(rng_next(rng) % N);
        int added = random_available(state, rng);
        swap_column(state, slot, added);
    }
}

static void *run_worker(void *argument) {
    Worker *worker = argument;
    State state;
    int local_best_columns[N];
    int local_best_score;
    int local_best_ones;
    int local_best_deleted;
    uint64_t rng_seed = worker->seed;
    uint64_t rng = splitmix64(&rng_seed);
    uint64_t cycle = 90000U + 10000U * (uint64_t)(worker->id % 5);
    uint64_t stagnant_cycles = 0;

    initialize(&state, q1_columns);
    if (worker->id != 0) {
        kick(&state, &rng, 3 + worker->id);
    }
    local_best_score = evaluate(&state, &local_best_deleted);
    local_best_ones = state.ones;
    memcpy(local_best_columns, state.columns, sizeof(local_best_columns));
    worker->best_score = local_best_score;
    worker->best_ones = local_best_ones;
    worker->best_deleted_slot = local_best_deleted;
    memcpy(worker->best_columns, state.columns, sizeof(worker->best_columns));
    publish_if_better(worker, &state, local_best_score, local_best_deleted);

    while (!stop_requested && elapsed_seconds() < time_limit) {
        uint64_t phase_index = worker->iterations % cycle;
        double phase = (double)phase_index / (double)(cycle - 1U);
        double high = worker->mode == 0 ? 4.5 :
                      (worker->mode == 1 ? 2.8 :
                       (worker->mode == 2 ? 7.0 : 3.6));
        double low = worker->mode == 2 ? 0.03 : 0.008;
        double temperature = high * pow(low / high, phase);
        int trials = worker->mode == 0 ? 1 :
                     (worker->mode == 1 ? 3 :
                      (worker->mode == 2 ? 2 : 5));
        int old_deleted;
        int old_score = evaluate(&state, &old_deleted);
        int holes[V];
        int hole_count = collect_deletion_holes(&state, old_deleted, holes);
        int selected_slot = -1;
        int selected_added = -1;
        int selected_score = V;
        int selected_ones = V;

        for (int trial = 0; trial < trials; ++trial) {
            int slot;
            int added = 0;
            int removed;
            int trial_deleted;
            int trial_score;
            if (hole_count > 0 && (rng_next(&rng) & 255U) < 232U) {
                int target = holes[rng_next(&rng) % (uint64_t)hole_count];
                for (int attempt = 0; attempt < 64; ++attempt) {
                    if ((rng_next(&rng) & 31U) == 0U) {
                        added = target;
                    } else {
                        int partner_slot = (int)(rng_next(&rng) % N);
                        if (partner_slot == old_deleted) {
                            continue;
                        }
                        added = target ^ state.columns[partner_slot];
                    }
                    if (added > 0 && !state.member[added]) {
                        break;
                    }
                }
            }
            if (added <= 0 || state.member[added]) {
                added = random_available(&state, &rng);
            }
            slot = (int)(rng_next(&rng) % N);
            removed = state.columns[slot];
            swap_column(&state, slot, added);
            trial_score = evaluate(&state, &trial_deleted);
            if (selected_slot < 0 || trial_score < selected_score ||
                (trial_score == selected_score && state.ones < selected_ones) ||
                (trial_score == selected_score && state.ones == selected_ones &&
                 (rng_next(&rng) & 1U))) {
                selected_slot = slot;
                selected_added = added;
                selected_score = trial_score;
                selected_ones = state.ones;
            }
            swap_column(&state, slot, removed);
        }

        {
            int removed = state.columns[selected_slot];
            int new_deleted;
            int new_score;
            int delta;
            int accept;
            swap_column(&state, selected_slot, selected_added);
            new_score = evaluate(&state, &new_deleted);
            delta = new_score - old_score;
            accept = delta <= 0 || rng_unit(&rng) < exp(-(double)delta / temperature);
            if (accept) {
                ++worker->accepted;
            } else {
                swap_column(&state, selected_slot, removed);
            }
        }
        ++worker->iterations;

        {
            int current_deleted;
            int current_score = evaluate(&state, &current_deleted);
            if (current_score < local_best_score ||
                (current_score == local_best_score && state.ones < local_best_ones)) {
                local_best_score = current_score;
                local_best_ones = state.ones;
                local_best_deleted = current_deleted;
                memcpy(local_best_columns, state.columns, sizeof(local_best_columns));
                stagnant_cycles = 0;
                if (current_score < worker->best_score ||
                    (current_score == worker->best_score && state.ones < worker->best_ones)) {
                    worker->best_score = current_score;
                    worker->best_ones = state.ones;
                    worker->best_deleted_slot = current_deleted;
                    memcpy(worker->best_columns, state.columns, sizeof(worker->best_columns));
                    publish_if_better(worker, &state, current_score, current_deleted);
                }
                if (current_score == 0) {
                    stop_requested = 1;
                    break;
                }
            }
        }

        if (phase_index + 1U == cycle) {
            ++stagnant_cycles;
            initialize(&state, local_best_columns);
            kick(&state, &rng, 1 + (int)(stagnant_cycles % 8U));
            if (stagnant_cycles % 20U == 0U) {
                initialize(&state, q1_columns);
                kick(&state, &rng, 10 + (int)(rng_next(&rng) % 31U));
                local_best_score = evaluate(&state, &local_best_deleted);
                local_best_ones = state.ones;
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
            "[--input PATH] [--output PATH]\n", program);
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
    if (!read_matrix(input_path)) {
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
            "q2 lifted search: threads=%d seconds=%.3f master_seed=0x%016llx\n",
            thread_count, time_limit, (unsigned long long)master_seed);
    fflush(stdout);
    for (int index = 0; index < thread_count; ++index) {
        uint64_t seed_state = master_seed + (uint64_t)index;
        workers[index].id = index;
        workers[index].mode = index % 4;
        workers[index].seed = splitmix64(&seed_state);
        workers[index].best_score = V;
        if (pthread_create(&threads[index], NULL, run_worker, &workers[index]) != 0) {
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
            elapsed_seconds(), global_score);
    for (int index = 0; index < created; ++index) {
        fprintf(stdout,
                "worker=%d mode=%d iterations=%llu accepted=%llu best=%d ones=%d\n",
                workers[index].id, workers[index].mode,
                (unsigned long long)workers[index].iterations,
                (unsigned long long)workers[index].accepted,
                workers[index].best_score, workers[index].best_ones);
    }
    free(threads);
    free(workers);
    return global_score == 0 ? 0 : 1;
}
