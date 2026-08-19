/*
 * Guided add-then-delete search for 49 points covering F_2^10 at radius 2.
 *
 * Unlike search_n49.c, a move is not a random (slot, new column) pair.  Pick
 * an uncovered syndrome t, enumerate all 50 columns a that would represent t
 * after insertion (a=t or a=t^x for x in S), temporarily form S union {a},
 * and score every possible deletion from the old 49-set.  Uncovered-syndrome
 * weights are increased on plateaus (breakout / guided local search).
 *
 * This is discovery code.  Even a zero checkpoint must be checked with the
 * separate verify_radius2_matrix.c program.
 *
 * Build and example (from problems/covering/):
 *
 *   gcc -O3 -std=c11 -Wall -Wextra -pthread \
 *       compute/search_n49_guided.c -o compute/search_n49_guided
 *   compute/search_n49_guided --seconds 1200 --threads 4 \
 *       --input compute/q2_direct_20260819_a.json \
 *       --output compute/q2_guided_checkpoint.json
 */

#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <pthread.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

enum { R = 10, V = 1 << R, N = 49, AUGMENTED = 50 };

typedef struct {
    int columns[N];
    unsigned char member[V];
    unsigned char counts[V];
    int weights[V];
    int missing;
    int ones;
    long weighted_missing;
} State;

typedef struct {
    int id;
    int mode;
    uint64_t seed;
    uint64_t iterations;
    uint64_t moves;
    int best_missing;
    int best_ones;
    int best_columns[N];
} Worker;

typedef struct {
    int added;
    int deleted_slot;
    int resulting_missing;
    int resulting_ones;
    long resulting_weighted;
} Move;

static int input_columns[N];
static int thread_count = 4;
static double time_limit = 60.0;
static uint64_t master_seed = UINT64_C(0xA4093822299F31D0);
static const char *input_path = "compute/q2_direct_20260819_a.json";
static const char *output_path = "compute/q2_guided_checkpoint.json";
static struct timespec start_clock;
static volatile sig_atomic_t stop_requested = 0;
static pthread_mutex_t best_mutex = PTHREAD_MUTEX_INITIALIZER;
static int global_best = V;
static int global_ones = V;
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
    uint64_t value = *state;
    value ^= value << 13;
    value ^= value >> 7;
    value ^= value << 17;
    *state = value;
    return value;
}

static int compare_ints(const void *left, const void *right) {
    int a = *(const int *)left;
    int b = *(const int *)right;
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

static int read_checkpoint(const char *path) {
    FILE *file = fopen(path, "r");
    char *blob;
    char *cursor;
    long size;
    if (file == NULL) {
        fprintf(stderr, "cannot open %s: %s\n", path, strerror(errno));
        return 0;
    }
    if (fseek(file, 0, SEEK_END) != 0 || (size = ftell(file)) < 0 ||
        fseek(file, 0, SEEK_SET) != 0) {
        fclose(file);
        fprintf(stderr, "cannot seek in %s\n", path);
        return 0;
    }
    blob = malloc((size_t)size + 1U);
    if (blob == NULL || fread(blob, 1, (size_t)size, file) != (size_t)size) {
        free(blob);
        fclose(file);
        fprintf(stderr, "cannot read %s\n", path);
        return 0;
    }
    fclose(file);
    blob[size] = '\0';
    cursor = strstr(blob, "\"columns_decimal\"");
    if (cursor != NULL) {
        cursor = strchr(cursor, '[');
    }
    if (cursor == NULL) {
        free(blob);
        fprintf(stderr, "%s has no columns_decimal array\n", path);
        return 0;
    }
    ++cursor;
    for (int index = 0; index < N; ++index) {
        char *end;
        long value;
        while (*cursor == ' ' || *cursor == '\t' || *cursor == '\r' ||
               *cursor == '\n' || *cursor == ',') {
            ++cursor;
        }
        value = strtol(cursor, &end, 10);
        if (end == cursor || value <= 0 || value >= V) {
            free(blob);
            fprintf(stderr, "invalid column %d in %s\n", index, path);
            return 0;
        }
        input_columns[index] = (int)value;
        cursor = end;
    }
    while (*cursor == ' ' || *cursor == '\t' || *cursor == '\r' ||
           *cursor == '\n') {
        ++cursor;
    }
    if (*cursor != ']') {
        free(blob);
        fprintf(stderr, "%s columns_decimal does not have exactly 49 values\n", path);
        return 0;
    }
    free(blob);
    if (binary_rank(input_columns, N) != R) {
        fprintf(stderr, "input columns do not have rank 10\n");
        return 0;
    }
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < i; ++j) {
            if (input_columns[i] == input_columns[j]) {
                fprintf(stderr, "input columns are repeated\n");
                return 0;
            }
        }
    }
    return 1;
}

static void initialize(State *state, const int *columns) {
    memset(state, 0, sizeof(*state));
    memcpy(state->columns, columns, sizeof(state->columns));
    for (int syndrome = 0; syndrome < V; ++syndrome) {
        state->weights[syndrome] = 1;
    }
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
            ++state->missing;
            state->weighted_missing += state->weights[syndrome];
        } else if (state->counts[syndrome] == 1) {
            ++state->ones;
        }
    }
}

static void change_count(State *state, int syndrome, int delta) {
    int before = state->counts[syndrome];
    int after = before + delta;
    if (after < 0 || after > AUGMENTED + 1) {
        fprintf(stderr, "internal count error\n");
        abort();
    }
    if (before == 0 && after == 1) {
        --state->missing;
        ++state->ones;
        state->weighted_missing -= state->weights[syndrome];
    } else if (before == 1 && after == 0) {
        ++state->missing;
        --state->ones;
        state->weighted_missing += state->weights[syndrome];
    } else if (before == 1 && after == 2) {
        --state->ones;
    } else if (before == 2 && after == 1) {
        ++state->ones;
    }
    state->counts[syndrome] = (unsigned char)after;
}

static void add_temporary(State *state, int added) {
    change_count(state, added, +1);
    for (int index = 0; index < N; ++index) {
        change_count(state, added ^ state->columns[index], +1);
    }
}

static void remove_temporary(State *state, int added) {
    change_count(state, added, -1);
    for (int index = 0; index < N; ++index) {
        change_count(state, added ^ state->columns[index], -1);
    }
}

static void apply_swap(State *state, int slot, int added) {
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

static int independently_missing(const int *columns, int *holes, int *histogram) {
    unsigned char counts[V] = {0};
    int missing = 0;
    counts[0] = 1;
    for (int left = 0; left < N; ++left) {
        ++counts[columns[left]];
        for (int right = 0; right < left; ++right) {
            ++counts[columns[left] ^ columns[right]];
        }
    }
    if (histogram != NULL) {
        memset(histogram, 0, (N + 2) * sizeof(*histogram));
    }
    for (int syndrome = 0; syndrome < V; ++syndrome) {
        if (counts[syndrome] == 0) {
            if (holes != NULL) {
                holes[missing] = syndrome;
            }
            ++missing;
        }
        if (histogram != NULL) {
            ++histogram[counts[syndrome]];
        }
    }
    return missing;
}

static void write_checkpoint_locked(void) {
    char temporary[4096];
    int columns[N];
    int holes[V];
    int histogram[N + 2];
    int missing;
    FILE *file;
    memcpy(columns, global_columns, sizeof(columns));
    qsort(columns, N, sizeof(columns[0]), compare_ints);
    missing = independently_missing(columns, holes, histogram);
    if (missing != global_best) {
        fprintf(stderr, "independent checkpoint check disagrees\n");
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
    fprintf(file, "{\n  \"format\": \"q2-n49-guided-checkpoint-v1\",\n");
    fprintf(file, "  \"status\": \"%s\",\n",
            missing == 0 ? "candidate witness" : "search residue");
    fprintf(file, "  \"redundancy\": 10,\n  \"length\": 49,\n");
    fprintf(file, "  \"best_uncovered\": %d,\n", missing);
    fprintf(file, "  \"rank\": %d,\n", binary_rank(columns, N));
    fprintf(file, "  \"elapsed_seconds\": %.6f,\n", elapsed_seconds());
    fprintf(file, "  \"worker\": %d,\n  \"mode\": %d,\n",
            global_worker, global_mode);
    fprintf(file, "  \"worker_seed\": \"%016llx\",\n",
            (unsigned long long)global_seed);
    fprintf(file, "  \"iteration\": %llu,\n",
            (unsigned long long)global_iteration);
    fprintf(file, "  \"columns_decimal\": [");
    for (int index = 0; index < N; ++index) {
        fprintf(file, "%s%d", index == 0 ? "" : ", ", columns[index]);
    }
    fprintf(file, "],\n  \"uncovered_syndromes_decimal\": [");
    for (int index = 0; index < missing; ++index) {
        fprintf(file, "%s%d", index == 0 ? "" : ", ", holes[index]);
    }
    fprintf(file, "],\n  \"representation_multiplicities\": {");
    int first = 1;
    for (int count = 0; count < N + 2; ++count) {
        if (histogram[count] != 0) {
            fprintf(file, "%s\"%d\": %d", first ? "" : ", ",
                    count, histogram[count]);
            first = 0;
        }
    }
    fprintf(file, "},\n  \"source_checkpoint\": \"%s\",\n", input_path);
    fprintf(file, "  \"warning\": \"A zero is only a candidate until independently verified.\"\n}\n");
    if (fclose(file) != 0 || rename(temporary, output_path) != 0) {
        fprintf(stderr, "cannot finalize %s: %s\n", output_path, strerror(errno));
    }
}

static void publish(Worker *worker, const State *state) {
    int changed = 0;
    pthread_mutex_lock(&best_mutex);
    if (state->missing < global_best ||
        (state->missing == global_best && state->ones < global_ones)) {
        global_best = state->missing;
        global_ones = state->ones;
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
        printf("best uncovered=%d ones=%d worker=%d mode=%d iteration=%llu elapsed=%.3f\n",
               state->missing, state->ones, worker->id, worker->mode,
               (unsigned long long)worker->iterations, elapsed_seconds());
        fflush(stdout);
    }
}

static int select_target(const State *state, uint64_t *rng, int mode) {
    int selected = -1;
    int seen = 0;
    int best_weight = -1;
    for (int syndrome = 1; syndrome < V; ++syndrome) {
        if (state->counts[syndrome] != 0) {
            continue;
        }
        if (mode == 1 || mode == 3) {
            if (state->weights[syndrome] > best_weight ||
                (state->weights[syndrome] == best_weight &&
                 (rng_next(rng) % (uint64_t)(seen + 1)) == 0)) {
                best_weight = state->weights[syndrome];
                selected = syndrome;
            }
        } else {
            ++seen;
            if ((rng_next(rng) % (uint64_t)seen) == 0) {
                selected = syndrome;
            }
        }
    }
    return selected;
}

static int move_is_better(const Move *candidate, const Move *best,
                          int mode, uint64_t *rng) {
    if (best->added < 0 || candidate->resulting_weighted < best->resulting_weighted) {
        return 1;
    }
    if (candidate->resulting_weighted > best->resulting_weighted) {
        return 0;
    }
    if (candidate->resulting_missing != best->resulting_missing) {
        return candidate->resulting_missing < best->resulting_missing;
    }
    if (candidate->resulting_ones != best->resulting_ones) {
        if (mode == 2 || mode == 3) {
            return candidate->resulting_ones > best->resulting_ones;
        }
        return candidate->resulting_ones < best->resulting_ones;
    }
    return (rng_next(rng) & 1U) != 0;
}

static Move best_guided_move(State *state, int target, int mode,
                             uint64_t *rng, const uint64_t *tabu_until,
                             uint64_t iteration, int aspiration_missing) {
    int candidates[AUGMENTED];
    int candidate_count = 0;
    Move best = {-1, -1, V, V, 0};
    candidates[candidate_count++] = target;
    for (int index = 0; index < N; ++index) {
        candidates[candidate_count++] = target ^ state->columns[index];
    }
    for (int ci = 0; ci < candidate_count; ++ci) {
        int added = candidates[ci];
        int augmented[AUGMENTED];
        int damage_missing[AUGMENTED] = {0};
        int delta_ones[AUGMENTED] = {0};
        long damage_weight[AUGMENTED] = {0};
        if (added <= 0 || added >= V || state->member[added]) {
            continue;
        }
        if (tabu_until[added] > iteration && mode != 3) {
            continue;
        }
        memcpy(augmented, state->columns, sizeof(state->columns));
        augmented[N] = added;
        add_temporary(state, added);

        for (int index = 0; index < AUGMENTED; ++index) {
            int syndrome = augmented[index];
            int count = state->counts[syndrome];
            if (count == 1) {
                ++damage_missing[index];
                damage_weight[index] += state->weights[syndrome];
                --delta_ones[index];
            } else if (count == 2) {
                ++delta_ones[index];
            }
        }
        for (int left = 0; left < AUGMENTED; ++left) {
            for (int right = 0; right < left; ++right) {
                int syndrome = augmented[left] ^ augmented[right];
                int count = state->counts[syndrome];
                if (count == 1) {
                    ++damage_missing[left];
                    ++damage_missing[right];
                    damage_weight[left] += state->weights[syndrome];
                    damage_weight[right] += state->weights[syndrome];
                    --delta_ones[left];
                    --delta_ones[right];
                } else if (count == 2) {
                    ++delta_ones[left];
                    ++delta_ones[right];
                }
            }
        }
        for (int slot = 0; slot < N; ++slot) {
            Move candidate;
            candidate.added = added;
            candidate.deleted_slot = slot;
            candidate.resulting_missing = state->missing + damage_missing[slot];
            candidate.resulting_ones = state->ones + delta_ones[slot];
            candidate.resulting_weighted =
                state->weighted_missing + damage_weight[slot];
            if (tabu_until[state->columns[slot]] > iteration &&
                candidate.resulting_missing >= aspiration_missing) {
                continue;
            }
            if (move_is_better(&candidate, &best, mode, rng)) {
                best = candidate;
            }
        }
        remove_temporary(state, added);
    }
    return best;
}

static void bump_weights(State *state, int amount) {
    for (int syndrome = 1; syndrome < V; ++syndrome) {
        if (state->counts[syndrome] == 0) {
            state->weights[syndrome] += amount;
            state->weighted_missing += amount;
        }
    }
}

static void rescale_weights(State *state) {
    state->weighted_missing = 0;
    for (int syndrome = 0; syndrome < V; ++syndrome) {
        state->weights[syndrome] = (state->weights[syndrome] + 1) / 2;
        if (state->weights[syndrome] < 1) {
            state->weights[syndrome] = 1;
        }
        if (state->counts[syndrome] == 0) {
            state->weighted_missing += state->weights[syndrome];
        }
    }
}

static int random_available(const State *state, uint64_t *rng) {
    int value;
    do {
        value = 1 + (int)(rng_next(rng) % (V - 1));
    } while (state->member[value]);
    return value;
}

static void kick(State *state, uint64_t *rng, int swaps) {
    for (int step = 0; step < swaps; ++step) {
        int slot = (int)(rng_next(rng) % N);
        int added = random_available(state, rng);
        apply_swap(state, slot, added);
    }
}

static void *run_worker(void *argument) {
    Worker *worker = argument;
    State state;
    int local_best_columns[N];
    int local_best_missing;
    int local_best_ones;
    uint64_t tabu_until[V] = {0};
    uint64_t rng_state = worker->seed;
    uint64_t rng = splitmix64(&rng_state);
    uint64_t since_improvement = 0;
    initialize(&state, input_columns);
    if (worker->id > 0) {
        kick(&state, &rng, worker->id + (worker->mode == 3 ? 5 : 0));
    }
    local_best_missing = state.missing;
    local_best_ones = state.ones;
    memcpy(local_best_columns, state.columns, sizeof(local_best_columns));
    worker->best_missing = state.missing;
    worker->best_ones = state.ones;
    memcpy(worker->best_columns, state.columns, sizeof(worker->best_columns));
    publish(worker, &state);

    while (!stop_requested && elapsed_seconds() < time_limit) {
        int target = select_target(&state, &rng, worker->mode);
        Move move;
        int removed;
        if (target < 0) {
            stop_requested = 1;
            break;
        }
        move = best_guided_move(&state, target, worker->mode, &rng,
                                tabu_until, worker->iterations,
                                local_best_missing);
        if (move.added < 0) {
            bump_weights(&state, 1);
            memset(tabu_until, 0, sizeof(tabu_until));
            ++worker->iterations;
            continue;
        }
        removed = state.columns[move.deleted_slot];
        apply_swap(&state, move.deleted_slot, move.added);
        tabu_until[removed] = worker->iterations + 5U + (rng_next(&rng) % 7U);
        tabu_until[move.added] = worker->iterations + 2U;
        ++worker->moves;
        ++worker->iterations;
        ++since_improvement;

        if (state.missing < local_best_missing ||
            (state.missing == local_best_missing && state.ones < local_best_ones)) {
            local_best_missing = state.missing;
            local_best_ones = state.ones;
            memcpy(local_best_columns, state.columns, sizeof(local_best_columns));
            since_improvement = 0;
            if (state.missing < worker->best_missing ||
                (state.missing == worker->best_missing &&
                 state.ones < worker->best_ones)) {
                worker->best_missing = state.missing;
                worker->best_ones = state.ones;
                memcpy(worker->best_columns, state.columns,
                       sizeof(worker->best_columns));
                publish(worker, &state);
            }
            if (state.missing == 0) {
                stop_requested = 1;
                break;
            }
        }
        if (since_improvement != 0 && since_improvement % 40U == 0U) {
            bump_weights(&state, worker->mode == 1 ? 2 : 1);
        }
        if (worker->iterations % 2000U == 0U) {
            rescale_weights(&state);
        }
        if (since_improvement >= 4000U) {
            initialize(&state, local_best_columns);
            kick(&state, &rng, 2 + (int)(rng_next(&rng) % 7U));
            memset(tabu_until, 0, sizeof(tabu_until));
            since_improvement = 0;
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
            "[--input CHECKPOINT.json] [--output PATH]\n", program);
}

int main(int argc, char **argv) {
    pthread_t *threads;
    Worker *workers;
    int created = 0;
    for (int index = 1; index < argc; ++index) {
        if (strcmp(argv[index], "--seconds") == 0 && index + 1 < argc) {
            time_limit = parse_double(argv[++index], 0.01, 86400.0, "seconds");
        } else if (strcmp(argv[index], "--threads") == 0 && index + 1 < argc) {
            thread_count = parse_int(argv[++index], 1, 64, "threads");
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
    if (!read_checkpoint(input_path)) {
        return 2;
    }
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);
    clock_gettime(CLOCK_MONOTONIC, &start_clock);
    threads = calloc((size_t)thread_count, sizeof(*threads));
    workers = calloc((size_t)thread_count, sizeof(*workers));
    if (threads == NULL || workers == NULL) {
        fprintf(stderr, "out of memory\n");
        return 2;
    }
    printf("q2 guided n=49 search: threads=%d seconds=%.3f master_seed=0x%016llx\n",
           thread_count, time_limit, (unsigned long long)master_seed);
    fflush(stdout);
    for (int index = 0; index < thread_count; ++index) {
        uint64_t seed_state = master_seed + (uint64_t)index;
        workers[index].id = index;
        workers[index].mode = index % 4;
        workers[index].seed = splitmix64(&seed_state);
        workers[index].best_missing = V;
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
    printf("finished: elapsed=%.3f best_uncovered=%d\n",
           elapsed_seconds(), global_best);
    for (int index = 0; index < created; ++index) {
        printf("worker=%d mode=%d iterations=%llu moves=%llu best=%d ones=%d\n",
               workers[index].id, workers[index].mode,
               (unsigned long long)workers[index].iterations,
               (unsigned long long)workers[index].moves,
               workers[index].best_missing, workers[index].best_ones);
    }
    free(threads);
    free(workers);
    return global_best == 0 ? 0 : 1;
}
