/* Unrestricted weighted min-conflicts search for a 7-coloring of [1697].

   The search starts from Rowley's independently verified coloring of [1696]
   plus one new color, but it imposes no reflection or template constraints.
   A zero-conflict output still has to pass ../verify_coloring.py.

   Build: gcc -O3 -march=native -std=c11 -Wall -Wextra -o search_unrestricted search_unrestricted.c
*/

#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

enum { N = 1697, COLORS = 7, MAX_CANDIDATES = 18 };

typedef struct {
    uint16_t vertex[3];
    uint8_t size;
} Edge;

typedef struct {
    int vertex;
    int color;
    int unweighted_delta;
    int64_t weighted_delta;
} Candidate;

static uint64_t rng_state;

static uint64_t rng_next(void) {
    uint64_t x = rng_state;
    x ^= x >> 12;
    x ^= x << 25;
    x ^= x >> 27;
    rng_state = x;
    return x * UINT64_C(2685821657736338717);
}

static double now_seconds(void) {
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) {
        perror("clock_gettime");
        exit(2);
    }
    return (double)ts.tv_sec + 1e-9 * (double)ts.tv_nsec;
}

static void *checked_calloc(size_t count, size_t size) {
    void *pointer = calloc(count, size);
    if (pointer == NULL) {
        perror("calloc");
        exit(2);
    }
    return pointer;
}

static void *checked_malloc(size_t size) {
    void *pointer = malloc(size);
    if (pointer == NULL) {
        perror("malloc");
        exit(2);
    }
    return pointer;
}

static int read_seed(const char *path, uint8_t colors[N]) {
    FILE *input = fopen(path, "r");
    if (input == NULL) {
        perror(path);
        return 0;
    }
    int count = 0;
    for (; count < N; ++count) {
        int color;
        int status = fscanf(input, "%d", &color);
        if (status == EOF) break;
        if (status != 1 || color < 0 || color >= COLORS) {
            fprintf(stderr, "malformed seed at position %d\n", count + 1);
            fclose(input);
            return 0;
        }
        colors[count] = (uint8_t)color;
    }
    int extra;
    if (fscanf(input, "%d", &extra) == 1) {
        fprintf(stderr, "seed has more than 1697 entries\n");
        fclose(input);
        return 0;
    }
    fclose(input);
    if (count == N - 1) {
        colors[N - 1] = 4;
    } else if (count != N) {
        fprintf(stderr, "seed has %d entries; expected 1696 or 1697\n", count);
        return 0;
    }
    return count;
}

static int write_coloring(const char *path, const uint8_t colors[N]) {
    FILE *output = fopen(path, "w");
    if (output == NULL) {
        perror(path);
        return 0;
    }
    for (int vertex = 0; vertex < N; ++vertex) {
        if (fprintf(output, "%s%u", vertex ? " " : "", colors[vertex]) < 0) {
            perror(path);
            fclose(output);
            return 0;
        }
    }
    if (fputc('\n', output) == EOF || fclose(output) != 0) {
        perror(path);
        return 0;
    }
    return 1;
}

static int edge_bad(const Edge *edge, const uint8_t colors[N]) {
    uint8_t color = colors[edge->vertex[0]];
    if (colors[edge->vertex[1]] != color) return 0;
    return edge->size == 2 || colors[edge->vertex[2]] == color;
}

static int edge_bad_after(
    const Edge *edge, const uint8_t colors[N], int changed, int new_color
) {
    int first = edge->vertex[0];
    int second = edge->vertex[1];
    int first_color = first == changed ? new_color : colors[first];
    int second_color = second == changed ? new_color : colors[second];
    if (first_color != second_color) return 0;
    if (edge->size == 2) return 1;
    int third = edge->vertex[2];
    int third_color = third == changed ? new_color : colors[third];
    return first_color == third_color;
}

static void remove_bad(int edge_id, int *bad_ids, int *bad_position, int *bad_count) {
    int position = bad_position[edge_id];
    int last_id = bad_ids[--*bad_count];
    bad_ids[position] = last_id;
    bad_position[last_id] = position;
    bad_position[edge_id] = -1;
}

static void add_bad(int edge_id, int *bad_ids, int *bad_position, int *bad_count) {
    bad_position[edge_id] = *bad_count;
    bad_ids[(*bad_count)++] = edge_id;
}

static void initialize_bad(
    const Edge *edges,
    int edge_count,
    const uint8_t colors[N],
    int *bad_ids,
    int *bad_position,
    int *bad_count
) {
    *bad_count = 0;
    for (int edge_id = 0; edge_id < edge_count; ++edge_id) {
        bad_position[edge_id] = -1;
        if (edge_bad(&edges[edge_id], colors)) {
            add_bad(edge_id, bad_ids, bad_position, bad_count);
        }
    }
}

static void print_result(
    const char *result,
    uint64_t seed,
    int restarts,
    int64_t moves,
    int best_bad,
    double elapsed,
    const Edge *edges,
    int edge_count,
    const uint8_t best_colors[N]
) {
    printf(
        "{\"result\":\"%s\",\"seed\":%" PRIu64
        ",\"restarts\":%d,\"moves\":%" PRId64
        ",\"best_violations\":%d,\"elapsed_seconds\":%.6f,\"violations\":[",
        result, seed, restarts, moves, best_bad, elapsed
    );
    int printed = 0;
    for (int edge_id = 0; edge_id < edge_count && printed < 20; ++edge_id) {
        const Edge *edge = &edges[edge_id];
        if (!edge_bad(edge, best_colors)) continue;
        int x = edge->vertex[0] + 1;
        int y = edge->size == 2 ? x : edge->vertex[1] + 1;
        int z = edge->vertex[edge->size - 1] + 1;
        printf(
            "%s[%d,%d,%d,%u]",
            printed ? "," : "", x, y, z, best_colors[edge->vertex[0]]
        );
        ++printed;
    }
    printf("]}\n");
    fflush(stdout);
}

int main(int argc, char **argv) {
    if (argc != 6) {
        fprintf(
            stderr,
            "usage: %s ROWLEY_1696 OUTPUT SECONDS SEED RESTART_MOVES\n",
            argv[0]
        );
        return 2;
    }
    const char *seed_path = argv[1];
    const char *output_path = argv[2];
    char *end = NULL;
    double seconds = strtod(argv[3], &end);
    if (*argv[3] == '\0' || *end != '\0' || seconds <= 0) {
        fprintf(stderr, "SECONDS must be positive\n");
        return 2;
    }
    errno = 0;
    uint64_t original_seed = strtoull(argv[4], &end, 10);
    if (errno || *argv[4] == '\0' || *end != '\0' || original_seed == 0) {
        fprintf(stderr, "SEED must be a positive uint64\n");
        return 2;
    }
    int restart_moves = (int)strtol(argv[5], &end, 10);
    if (*argv[5] == '\0' || *end != '\0' || restart_moves <= 0) {
        fprintf(stderr, "RESTART_MOVES must be positive\n");
        return 2;
    }
    rng_state = original_seed;

    int edge_count = 0;
    int incidence_count = 0;
    int *degree = checked_calloc(N, sizeof(*degree));
    for (int x = 1; x <= N; ++x) {
        for (int y = x; x + y <= N; ++y) {
            ++edge_count;
            incidence_count += x == y ? 2 : 3;
            ++degree[x - 1];
            if (x != y) ++degree[y - 1];
            ++degree[x + y - 1];
        }
    }

    Edge *edges = checked_malloc((size_t)edge_count * sizeof(*edges));
    int *starts = checked_malloc((N + 1) * sizeof(*starts));
    int *cursor = checked_malloc(N * sizeof(*cursor));
    int *incident = checked_malloc((size_t)incidence_count * sizeof(*incident));
    starts[0] = 0;
    for (int vertex = 0; vertex < N; ++vertex) {
        starts[vertex + 1] = starts[vertex] + degree[vertex];
        cursor[vertex] = starts[vertex];
    }
    int edge_id = 0;
    for (int x = 1; x <= N; ++x) {
        for (int y = x; x + y <= N; ++y) {
            Edge *edge = &edges[edge_id];
            edge->vertex[0] = (uint16_t)(x - 1);
            if (x == y) {
                edge->vertex[1] = (uint16_t)(x + y - 1);
                edge->vertex[2] = 0;
                edge->size = 2;
                incident[cursor[x - 1]++] = edge_id;
            } else {
                edge->vertex[1] = (uint16_t)(y - 1);
                edge->vertex[2] = (uint16_t)(x + y - 1);
                edge->size = 3;
                incident[cursor[x - 1]++] = edge_id;
                incident[cursor[y - 1]++] = edge_id;
            }
            incident[cursor[x + y - 1]++] = edge_id;
            ++edge_id;
        }
    }
    free(cursor);
    free(degree);
    if (edge_id != edge_count || starts[N] != incidence_count) {
        fprintf(stderr, "internal hypergraph size mismatch\n");
        return 2;
    }

    uint8_t initial[N], colors[N], best_colors[N];
    int seed_length = read_seed(seed_path, initial);
    if (!seed_length) return 2;
    memcpy(best_colors, initial, sizeof(best_colors));

    int *bad_ids = checked_malloc((size_t)edge_count * sizeof(*bad_ids));
    int *bad_position = checked_malloc((size_t)edge_count * sizeof(*bad_position));
    uint32_t *weights = checked_malloc((size_t)edge_count * sizeof(*weights));
    int64_t *tabu_until = checked_calloc((size_t)N * COLORS, sizeof(*tabu_until));

    int global_best = edge_count + 1;
    int restarts = 0;
    int64_t total_moves = 0;
    double started = now_seconds();
    double deadline = started + seconds;

    while (now_seconds() < deadline) {
        ++restarts;
        memcpy(colors, initial, sizeof(colors));
        if (seed_length == N - 1) {
            colors[N - 1] = (uint8_t)((4 + restarts - 1) % COLORS);
        }
        for (int index = 0; index < edge_count; ++index) weights[index] = 1;
        memset(tabu_until, 0, (size_t)N * COLORS * sizeof(*tabu_until));

        int bad_count;
        initialize_bad(edges, edge_count, colors, bad_ids, bad_position, &bad_count);
        int restart_best = bad_count;
        int plateau = 0;
        if (bad_count < global_best) {
            global_best = bad_count;
            memcpy(best_colors, colors, sizeof(best_colors));
            write_coloring(output_path, best_colors);
            print_result(
                "improvement", original_seed, restarts, total_moves, global_best,
                now_seconds() - started, edges, edge_count, best_colors
            );
        }

        for (int local_move = 1; local_move <= restart_moves; ++local_move) {
            if ((local_move & 4095) == 0 && now_seconds() >= deadline) break;
            if (bad_count == 0) {
                write_coloring(output_path, colors);
                print_result(
                    "sat", original_seed, restarts, total_moves, 0,
                    now_seconds() - started, edges, edge_count, colors
                );
                return 0;
            }

            int chosen_bad = bad_ids[rng_next() % (uint64_t)bad_count];
            const Edge *focus = &edges[chosen_bad];
            Candidate candidates[MAX_CANDIDATES];
            int allowed_count = 0;
            int64_t best_delta = INT64_MAX;

            for (int slot = 0; slot < focus->size; ++slot) {
                int vertex = focus->vertex[slot];
                int old_color = colors[vertex];
                for (int new_color = 0; new_color < COLORS; ++new_color) {
                    if (new_color == old_color) continue;
                    Candidate candidate = {vertex, new_color, 0, 0};
                    for (int at = starts[vertex]; at < starts[vertex + 1]; ++at) {
                        int affected = incident[at];
                        int was_bad = bad_position[affected] >= 0;
                        int will_be_bad = edge_bad_after(
                            &edges[affected], colors, vertex, new_color
                        );
                        if (was_bad && !will_be_bad) {
                            --candidate.unweighted_delta;
                            candidate.weighted_delta -= weights[affected];
                        } else if (!was_bad && will_be_bad) {
                            ++candidate.unweighted_delta;
                            candidate.weighted_delta += weights[affected];
                        }
                    }
                    int tabu = tabu_until[vertex * COLORS + new_color] > total_moves;
                    int aspiration = bad_count + candidate.unweighted_delta < restart_best;
                    if (!tabu || aspiration) {
                        candidates[allowed_count++] = candidate;
                        if (candidate.weighted_delta < best_delta) {
                            best_delta = candidate.weighted_delta;
                        }
                    }
                }
            }
            if (allowed_count == 0) {
                allowed_count = 0;
                best_delta = INT64_MAX;
                for (int slot = 0; slot < focus->size; ++slot) {
                    int vertex = focus->vertex[slot];
                    int old_color = colors[vertex];
                    for (int new_color = 0; new_color < COLORS; ++new_color) {
                        if (new_color == old_color) continue;
                        Candidate candidate = {vertex, new_color, 0, 0};
                        for (int at = starts[vertex]; at < starts[vertex + 1]; ++at) {
                            int affected = incident[at];
                            int was_bad = bad_position[affected] >= 0;
                            int will_be_bad = edge_bad_after(
                                &edges[affected], colors, vertex, new_color
                            );
                            if (was_bad && !will_be_bad) {
                                --candidate.unweighted_delta;
                                candidate.weighted_delta -= weights[affected];
                            } else if (!was_bad && will_be_bad) {
                                ++candidate.unweighted_delta;
                                candidate.weighted_delta += weights[affected];
                            }
                        }
                        candidates[allowed_count++] = candidate;
                        if (candidate.weighted_delta < best_delta) {
                            best_delta = candidate.weighted_delta;
                        }
                    }
                }
            }

            int choice;
            if (rng_next() % 1000 < 15) {
                choice = (int)(rng_next() % (uint64_t)allowed_count);
            } else {
                int ties[MAX_CANDIDATES], tie_count = 0;
                for (int index = 0; index < allowed_count; ++index) {
                    if (candidates[index].weighted_delta == best_delta) {
                        ties[tie_count++] = index;
                    }
                }
                choice = ties[rng_next() % (uint64_t)tie_count];
            }
            Candidate move = candidates[choice];
            int old_color = colors[move.vertex];

            for (int at = starts[move.vertex]; at < starts[move.vertex + 1]; ++at) {
                int affected = incident[at];
                int was_bad = bad_position[affected] >= 0;
                int will_be_bad = edge_bad_after(
                    &edges[affected], colors, move.vertex, move.color
                );
                if (was_bad && !will_be_bad) {
                    remove_bad(affected, bad_ids, bad_position, &bad_count);
                } else if (!was_bad && will_be_bad) {
                    add_bad(affected, bad_ids, bad_position, &bad_count);
                }
            }
            colors[move.vertex] = (uint8_t)move.color;
            ++total_moves;
            tabu_until[move.vertex * COLORS + old_color] =
                total_moves + 5 + (int64_t)(rng_next() % 11);

            if (bad_count < restart_best) {
                restart_best = bad_count;
                plateau = 0;
            } else {
                ++plateau;
            }
            if (bad_count < global_best) {
                global_best = bad_count;
                memcpy(best_colors, colors, sizeof(best_colors));
                write_coloring(output_path, best_colors);
                print_result(
                    "improvement", original_seed, restarts, total_moves, global_best,
                    now_seconds() - started, edges, edge_count, best_colors
                );
            }
            if (plateau >= 10000) {
                for (int index = 0; index < bad_count; ++index) {
                    ++weights[bad_ids[index]];
                }
                plateau = 0;
            }
        }
    }

    write_coloring(output_path, best_colors);
    print_result(
        "timeout", original_seed, restarts, total_moves, global_best,
        now_seconds() - started, edges, edge_count, best_colors
    );
    return 1;
}
