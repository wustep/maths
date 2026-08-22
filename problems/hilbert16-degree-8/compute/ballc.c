/* ballc -- exhaustive Hamming balls around census sign distributions.
 *
 * The span sweeps (zonec) classify the MAXIMAL T-curves of a triangulation
 * exactly, but the census's 2,367 schemes are mostly non-maximal, and those
 * live outside the Haas affine subspace.  This program walks every sign
 * vector within Hamming distance <= r of each seed on one triangulation and
 * emits one witness per distinct scheme fingerprint; zone_collect-style
 * Python decoding then diffs against the census and hands anything new to
 * the exact Fraction verifier.
 *
 * The triangulation is a census certificate's own, so its integer
 * MIN_WEIGHTS certify regularity for every witness found on it.
 *
 * usage: ballc <task.txt> <radius> <out.jsonl> [maxseconds]
 */
#include "tcore.h"
#include <time.h>

static int radius;
static FILE *out;
static int seedidx;
static uint64_t evals, valid, maxev, logged;
static double deadline;

static double now(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static int stop;

static void visit(void)
{
    int ok; H128 fp;
    int ncomp = evaluate(cursign, &ok, &fp);
    evals++;
    if ((evals & 0xfffff) == 0 && deadline > 0 && now() > deadline) stop = 1;
    if (!ok) return;
    valid++;
    if (ncomp == 22) maxev++;
    if (seen_fp(fp, ncomp)) return;
    logged++;
    fprintf(out, "{\"kind\":\"WITNESS\",\"ncomp\":%d,\"seed\":%d,\"signs\":[",
            ncomp, seedidx);
    for (int j = 0; j < npts; j++)
        fprintf(out, "%s%d", j ? "," : "", cursign[j]);
    fprintf(out, "]}\n");
    fflush(out);
}

static void dfs(int start, int depth)
{
    visit();
    if (depth == radius || stop) return;
    for (int i = start; i < npts; i++) {
        cursign[i] = -cursign[i];
        dfs(i + 1, depth + 1);
        cursign[i] = -cursign[i];
        if (stop) return;
    }
}

int main(int argc, char **argv)
{
    if (argc < 4) { fprintf(stderr, "usage: ballc task radius out [sec]\n"); return 1; }
    FILE *f = load_task(argv[1]);
    radius = atoi(argv[2]);
    out = fopen(argv[3], "w");
    deadline = (argc > 4) ? now() + atof(argv[4]) : 0;

    char tag[32];
    int nseeds = 0;
    if (fscanf(f, "%31s %d", tag, &nseeds) != 2 || strcmp(tag, "SEEDS")) {
        fprintf(stderr, "no SEEDS block\n"); return 1;
    }
    signed char *seeds = malloc((size_t)nseeds * npts);
    for (int s = 0; s < nseeds; s++)
        for (int j = 0; j < npts; j++) {
            int v; need(f, 1, &v);
            seeds[(size_t)s * npts + j] = (signed char)v;
        }
    fclose(f);

    for (int s = 0; s < nseeds && !stop; s++) {
        seedidx = s;
        memcpy(cursign, seeds + (size_t)s * npts, npts);
        dfs(0, 0);
    }
    fprintf(out, "{\"kind\":\"summary\",\"radius\":%d,\"seeds\":%d,"
                 "\"evals\":%llu,\"valid\":%llu,\"maximal\":%llu,"
                 "\"distinct\":%llu,\"complete\":%d}\n",
            radius, nseeds, (unsigned long long)evals,
            (unsigned long long)valid, (unsigned long long)maxev,
            (unsigned long long)logged, stop ? 0 : 1);
    fclose(out);
    fprintf(stderr, "seeds=%d evals=%llu distinct=%llu complete=%d\n",
            nseeds, (unsigned long long)evals,
            (unsigned long long)logged, stop ? 0 : 1);
    return 0;
}
