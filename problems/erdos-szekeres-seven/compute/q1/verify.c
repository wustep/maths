#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

enum { N = 32, K = 7 };

typedef struct {
    int id;
    int64_t x;
    int64_t y;
} Point;

static __int128 cross(Point a, Point b, Point c) {
    return (__int128)(b.x - a.x) * (c.y - a.y)
         - (__int128)(b.y - a.y) * (c.x - a.x);
}

static int compare_points(const void *left, const void *right) {
    const Point *a = left;
    const Point *b = right;
    if (a->x < b->x) return -1;
    if (a->x > b->x) return 1;
    if (a->y < b->y) return -1;
    if (a->y > b->y) return 1;
    return 0;
}

static int hull_size(const Point input[K]) {
    Point sorted[K];
    Point hull[2 * K];
    for (int i = 0; i < K; ++i) sorted[i] = input[i];
    qsort(sorted, K, sizeof(Point), compare_points);

    int size = 0;
    for (int i = 0; i < K; ++i) {
        while (size >= 2 && cross(hull[size - 2], hull[size - 1], sorted[i]) <= 0)
            --size;
        hull[size++] = sorted[i];
    }
    int lower = size;
    for (int i = K - 2; i >= 0; --i) {
        while (size > lower && cross(hull[size - 2], hull[size - 1], sorted[i]) <= 0)
            --size;
        hull[size++] = sorted[i];
    }
    return size - 1;
}

static int next_combination(int indices[K]) {
    int i = K - 1;
    while (i >= 0 && indices[i] == N - K + i) --i;
    if (i < 0) return 0;
    ++indices[i];
    for (int j = i + 1; j < K; ++j) indices[j] = indices[j - 1] + 1;
    return 1;
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "usage: %s points.csv\n", argv[0]);
        return 2;
    }
    FILE *file = fopen(argv[1], "r");
    if (!file) {
        perror(argv[1]);
        return 2;
    }

    char header[64];
    assert(fgets(header, sizeof header, file));
    Point points[N];
    for (int i = 0; i < N; ++i) {
        long long x, y;
        int id;
        assert(fscanf(file, "%d,%lld,%lld", &id, &x, &y) == 3);
        assert(id == i);
        points[i] = (Point){id, (int64_t)x, (int64_t)y};
    }
    int trailing;
    while ((trailing = fgetc(file)) != EOF)
        assert(trailing == ' ' || trailing == '\t' || trailing == '\r' || trailing == '\n');
    fclose(file);

    uint64_t triples = 0;
    for (int i = 0; i < N; ++i)
        for (int j = i + 1; j < N; ++j)
            for (int k = j + 1; k < N; ++k) {
                assert(cross(points[i], points[j], points[k]) != 0);
                ++triples;
            }

    uint64_t histogram[K + 1] = {0};
    uint64_t seven_sets = 0;
    int indices[K] = {0, 1, 2, 3, 4, 5, 6};
    do {
        Point subset[K];
        for (int i = 0; i < K; ++i) subset[i] = points[indices[i]];
        int size = hull_size(subset);
        assert(size >= 3 && size <= 6);
        ++histogram[size];
        ++seven_sets;
    } while (next_combination(indices));

    assert(triples == 4960);
    assert(seven_sets == 3365856);
    assert(histogram[3] == 49204);
    assert(histogram[4] == 1125664);
    assert(histogram[5] == 1793716);
    assert(histogram[6] == 397272);

    printf("C verifier: 4960 noncollinear triples; 3365856 seven-sets; ");
    printf("hull histogram 3:%llu 4:%llu 5:%llu 6:%llu\n",
           (unsigned long long)histogram[3],
           (unsigned long long)histogram[4],
           (unsigned long long)histogram[5],
           (unsigned long long)histogram[6]);
    return 0;
}
