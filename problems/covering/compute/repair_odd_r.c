/*
 * Local repair around a near-covering: exhaustive 1-swaps, then targeted
 * simulated annealing with periodic kicks.  Discovery only.
 *
 *   gcc -O3 -std=c11 -Wall -Wextra -pthread compute/repair_odd_r.c \
 *       -lm -o compute/repair_odd_r
 *   compute/repair_odd_r --r 11 --n 78 --seconds 120 --threads 4 \
 *       --source compute/odd_r11_n78_16hole.cols \
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

static int redundancy = 11;
static int length = 78;
static int space = 2048;
static int thread_count = 4;
static double time_limit = 120.0;
static uint64_t master_seed = UINT64_C(0x0DD202608200100);
static const char *output_path = "compute/odd_r_repair.json";
static const char *source_path = NULL;
static int source_columns[MAX_N];
static int source_count = 0;
static struct timespec start_clock;
static volatile sig_atomic_t stop_requested = 0;
static pthread_mutex_t best_mutex = PTHREAD_MUTEX_INITIALIZER;
static int global_best = 1 << 30;
static int global_best_columns[MAX_N];
static int found_cover = 0;

typedef struct {
    int *counts;
    int *columns;
    unsigned char *member;
    int *zero_list;
    int *zero_pos;
    int missing;
} State;

static double elapsed_seconds(void) {
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    return (double)(now.tv_sec - start_clock.tv_sec) +
           1e-9 * (double)(now.tv_nsec - start_clock.tv_nsec);
}

static void handle_signal(int sig) {
    (void)sig;
    stop_requested = 1;
}

static uint64_t splitmix64(uint64_t *state) {
    uint64_t z = (*state += UINT64_C(0x9E3779B97F4A7C15));
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
    int basis[MAX_R] = {0};
    int rank = 0;
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

static int read_source(const char *path) {
    FILE *file = fopen(path, "r");
    char line[65536];
    unsigned char seen[1 << MAX_R];
    if (file == NULL) {
        fprintf(stderr, "cannot open %s: %s\n", path, strerror(errno));
        return 0;
    }
    memset(seen, 0, sizeof(seen));
    source_count = 0;
    while (fgets(line, sizeof(line), file) != NULL) {
        char *cursor = line;
        if (line[0] == '#' || line[0] == '\n') {
            continue;
        }
        while (*cursor) {
            char *end;
            long value;
            while (*cursor == ' ' || *cursor == ',' || *cursor == '\t' ||
                   *cursor == '\n') {
                ++cursor;
            }
            if (*cursor == '\0' || *cursor == '#') {
                break;
            }
            value = strtol(cursor, &end, 0);
            if (end == cursor || value <= 0 || value >= space) {
                fclose(file);
                fprintf(stderr, "bad column in %s\n", path);
                return 0;
            }
            if (seen[value] || source_count >= MAX_N) {
                fclose(file);
                fprintf(stderr, "repeated or too many columns\n");
                return 0;
            }
            seen[value] = 1;
            source_columns[source_count++] = (int)value;
            cursor = end;
        }
    }
    fclose(file);
    return source_count == length;
}

static void state_alloc(State *state) {
    state->counts = calloc((size_t)space, sizeof(int));
    state->columns = calloc((size_t)length, sizeof(int));
    state->member = calloc((size_t)space, 1);
    state->zero_list = calloc((size_t)space, sizeof(int));
    state->zero_pos = calloc((size_t)space, sizeof(int));
    if (!state->counts || !state->columns || !state->member ||
        !state->zero_list || !state->zero_pos) {
        fprintf(stderr, "out of memory\n");
        exit(1);
    }
}

static void state_free(State *state) {
    free(state->counts);
    free(state->columns);
    free(state->member);
    free(state->zero_list);
    free(state->zero_pos);
}

static void zero_add(State *state, int syndrome) {
    state->zero_pos[syndrome] = state->missing;
    state->zero_list[state->missing++] = syndrome;
}

static void zero_remove(State *state, int syndrome) {
    int position = state->zero_pos[syndrome];
    int tail = state->zero_list[--state->missing];
    state->zero_list[position] = tail;
    state->zero_pos[tail] = position;
    state->zero_pos[syndrome] = -1;
}

static void change_count(State *state, int syndrome, int delta) {
    int before = state->counts[syndrome];
    int after = before + delta;
    if (before == 0 && after == 1) {
        zero_remove(state, syndrome);
    } else if (before == 1 && after == 0) {
        zero_add(state, syndrome);
    }
    state->counts[syndrome] = after;
}

static void initialize_state(State *state, const int *columns) {
    memset(state->counts, 0, (size_t)space * sizeof(int));
    memset(state->member, 0, (size_t)space);
    memcpy(state->columns, columns, (size_t)length * sizeof(int));
    state->missing = 0;
    for (int s = 0; s < space; ++s) {
        state->zero_pos[s] = -1;
    }
    state->counts[0] = 1;
    for (int i = 0; i < length; ++i) {
        int column = columns[i];
        state->member[column] = 1;
        ++state->counts[column];
        for (int j = 0; j < i; ++j) {
            ++state->counts[column ^ columns[j]];
        }
    }
    for (int s = 0; s < space; ++s) {
        if (state->counts[s] == 0) {
            zero_add(state, s);
        }
    }
}

static void apply_swap(State *state, int slot, int added) {
    int removed = state->columns[slot];
    change_count(state, removed, -1);
    for (int i = 0; i < length; ++i) {
        if (i != slot) {
            change_count(state, removed ^ state->columns[i], -1);
        }
    }
    change_count(state, added, +1);
    for (int i = 0; i < length; ++i) {
        if (i != slot) {
            change_count(state, added ^ state->columns[i], +1);
        }
    }
    state->member[removed] = 0;
    state->member[added] = 1;
    state->columns[slot] = added;
}

static void write_checkpoint(void) {
    char temporary[4096];
    FILE *file;
    int columns[MAX_N];
    snprintf(temporary, sizeof(temporary), "%s.tmp", output_path);
    memcpy(columns, global_best_columns, (size_t)length * sizeof(int));
    qsort(columns, length, sizeof(int), compare_ints);
    file = fopen(temporary, "w");
    if (file == NULL) {
        return;
    }
    fprintf(file,
            "{\n  \"format\": \"odd-r-repair-checkpoint-v1\",\n"
            "  \"status\": \"%s\",\n  \"redundancy\": %d,\n  \"length\": %d,\n"
            "  \"best_uncovered\": %d,\n  \"rank\": %d,\n"
            "  \"elapsed_seconds\": %.6f,\n  \"columns_decimal\": [",
            global_best == 0 ? "candidate witness" : "search residue",
            redundancy, length, global_best,
            binary_rank(columns, length, redundancy), elapsed_seconds());
    for (int i = 0; i < length; ++i) {
        fprintf(file, "%s%d", i == 0 ? "" : ", ", columns[i]);
    }
    fprintf(file, "]\n}\n");
    fclose(file);
    rename(temporary, output_path);
}

static void publish(const int *columns, int missing) {
    pthread_mutex_lock(&best_mutex);
    if (missing < global_best) {
        global_best = missing;
        memcpy(global_best_columns, columns, (size_t)length * sizeof(int));
        write_checkpoint();
        fprintf(stdout, "best uncovered=%d elapsed=%.3f\n",
                missing, elapsed_seconds());
        fflush(stdout);
        if (missing == 0) {
            found_cover = 1;
            stop_requested = 1;
        }
    }
    pthread_mutex_unlock(&best_mutex);
}

static int exhaustive_one_swap(State *state) {
    int improved = 0;
    int best_missing = state->missing;
    int best_slot = -1;
    int best_add = -1;
    for (int slot = 0; slot < length; ++slot) {
        int removed = state->columns[slot];
        for (int proposal = 1; proposal < space; ++proposal) {
            if (state->member[proposal]) {
                continue;
            }
            apply_swap(state, slot, proposal);
            if (state->missing < best_missing) {
                best_missing = state->missing;
                best_slot = slot;
                best_add = proposal;
            }
            apply_swap(state, slot, removed);
        }
    }
    if (best_slot >= 0) {
        apply_swap(state, best_slot, best_add);
        improved = 1;
    }
    return improved;
}

static int random_available(State *state, uint64_t *rng) {
    int proposal;
    do {
        proposal = 1 + (int)(rng_next(rng) % (uint64_t)(space - 1));
    } while (state->member[proposal]);
    return proposal;
}

static int targeted(State *state, uint64_t *rng) {
    int target;
    int proposal;
    if (state->missing <= 0) {
        return random_available(state, rng);
    }
    target = state->zero_list[rng_next(rng) % (uint64_t)state->missing];
    for (int attempt = 0; attempt < 100; ++attempt) {
        if ((rng_next(rng) & 31U) == 0U) {
            proposal = target;
        } else {
            proposal = target ^ state->columns[rng_next(rng) % (uint64_t)length];
        }
        if (proposal > 0 && proposal < space && !state->member[proposal]) {
            return proposal;
        }
    }
    return random_available(state, rng);
}

typedef struct {
    int worker_id;
    uint64_t seed;
} Worker;

static void *worker_main(void *arg) {
    Worker *worker = (Worker *)arg;
    State state;
    uint64_t rng = worker->seed;
    int kick = 4 + (worker->worker_id % 9);
    state_alloc(&state);
    initialize_state(&state, source_columns);
    for (int step = 0; step < kick; ++step) {
        apply_swap(&state, (int)(rng_next(&rng) % (uint64_t)length),
                   random_available(&state, &rng));
    }
    publish(state.columns, state.missing);

    while (!stop_requested && elapsed_seconds() < time_limit) {
        int old = state.missing;
        int slot;
        int proposal;
        int removed;
        double temperature = 2.5 * pow(0.02 / 2.5,
            (elapsed_seconds() / time_limit));
        if (state.missing > 0 && state.missing <= 24 &&
            (rng_next(&rng) & 31U) == 0U) {
            exhaustive_one_swap(&state);
            publish(state.columns, state.missing);
            continue;
        }
        proposal = ((rng_next(&rng) & 255U) < 240U)
                       ? targeted(&state, &rng)
                       : random_available(&state, &rng);
        if (state.missing <= 40) {
            int best_slot = 0;
            int best_miss = old + 8;
            int saved[MAX_N];
            memcpy(saved, state.columns, (size_t)length * sizeof(int));
            for (int candidate = 0; candidate < length; ++candidate) {
                int was = state.columns[candidate];
                apply_swap(&state, candidate, proposal);
                if (state.missing < best_miss) {
                    best_miss = state.missing;
                    best_slot = candidate;
                }
                apply_swap(&state, candidate, was);
            }
            slot = best_slot;
            (void)saved;
        } else {
            slot = (int)(rng_next(&rng) % (uint64_t)length);
        }
        removed = state.columns[slot];
        apply_swap(&state, slot, proposal);
        if (state.missing <= old ||
            ((rng_next(&rng) >> 11) * (1.0 / 9007199254740992.0) <
             exp((old - state.missing) / (temperature + 1e-9)))) {
            publish(state.columns, state.missing);
        } else {
            apply_swap(&state, slot, removed);
        }
        if ((rng_next(&rng) & 4095U) == 0U) {
            int blows = 6 + (int)(rng_next(&rng) % 10U);
            for (int step = 0; step < blows; ++step) {
                apply_swap(&state, (int)(rng_next(&rng) % (uint64_t)length),
                           random_available(&state, &rng));
            }
        }
    }
    state_free(&state);
    return NULL;
}

int main(int argc, char **argv) {
    Worker *workers;
    pthread_t *threads;
    State probe;

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--r") == 0) {
            redundancy = (int)strtol(argv[++i], NULL, 10);
        } else if (strcmp(argv[i], "--n") == 0) {
            length = (int)strtol(argv[++i], NULL, 10);
        } else if (strcmp(argv[i], "--seconds") == 0) {
            time_limit = strtod(argv[++i], NULL);
        } else if (strcmp(argv[i], "--threads") == 0) {
            thread_count = (int)strtol(argv[++i], NULL, 10);
        } else if (strcmp(argv[i], "--seed") == 0) {
            master_seed = strtoull(argv[++i], NULL, 0);
        } else if (strcmp(argv[i], "--output") == 0) {
            output_path = argv[++i];
        } else if (strcmp(argv[i], "--source") == 0) {
            source_path = argv[++i];
        }
    }
    if (source_path == NULL || redundancy < 3 || redundancy > MAX_R ||
        length < redundancy || length > MAX_N) {
        fprintf(stderr, "usage: repair_odd_r --r R --n N --source COLS ...\n");
        return 2;
    }
    space = 1 << redundancy;
    if (!read_source(source_path)) {
        return 1;
    }
    clock_gettime(CLOCK_MONOTONIC, &start_clock);
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);

    state_alloc(&probe);
    initialize_state(&probe, source_columns);
    publish(source_columns, probe.missing);
    fprintf(stdout, "start missing=%d r=%d n=%d\n", probe.missing,
            redundancy, length);
    fflush(stdout);
    if (probe.missing <= 20) {
        while (exhaustive_one_swap(&probe)) {
            publish(probe.columns, probe.missing);
        }
        fprintf(stdout, "after exhaustive 1-swap missing=%d\n", probe.missing);
        fflush(stdout);
        memcpy(source_columns, probe.columns, (size_t)length * sizeof(int));
    }
    state_free(&probe);
    if (found_cover) {
        return 0;
    }

    workers = calloc((size_t)thread_count, sizeof(*workers));
    threads = calloc((size_t)thread_count, sizeof(*threads));
    for (int i = 0; i < thread_count; ++i) {
        uint64_t local = master_seed ^ (UINT64_C(0x9E3779B97F4A7C15) * (uint64_t)(i + 3));
        workers[i].worker_id = i;
        workers[i].seed = splitmix64(&local);
        pthread_create(&threads[i], NULL, worker_main, &workers[i]);
    }
    for (int i = 0; i < thread_count; ++i) {
        pthread_join(threads[i], NULL);
    }
    fprintf(stdout, "done best_uncovered=%d cover=%s elapsed=%.3f\n",
            global_best, found_cover ? "yes" : "no", elapsed_seconds());
    free(workers);
    free(threads);
    return found_cover ? 0 : 1;
}
