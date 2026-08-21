/* thickc -- the Haas maximal stratum of one triangulation, thickened.
 *
 * zonec sweeps eta + span{delta_S}, which is every MAXIMAL sign distribution
 * the triangulation carries.  The schemes missing from the published census
 * are all non-maximal and all sit a short Hamming distance from a maximal
 * one -- but the ball searches only ever centred on the ONE representative
 * sign vector the paper published per scheme, while a triangulation of twist
 * rank r carries 2^r maximal vectors.
 *
 * This program walks the whole span and, at every point of it, also evaluates
 * all 45 single-coordinate flips.  So it covers every sign vector within
 * Hamming distance 1 of the entire maximal stratum, not of one point of it.
 *
 * usage: thickc <task.txt> <shard> <nshards> <out.jsonl> [maxseconds]
 */
#include "tcore.h"
#include <time.h>

static double now(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

int main(int argc, char **argv)
{
    if (argc < 5) { fprintf(stderr, "usage: thickc task shard nshards out [sec]\n"); return 1; }
    fclose(load_task(argv[1]));
    long shard = atol(argv[2]), nsh = atol(argv[3]);
    FILE *out = fopen(argv[4], "w");
    double deadline = (argc > 5) ? now() + atof(argv[5]) : 0;

    uint64_t total = (rnk >= 63) ? 0 : (1ULL << rnk);
    uint64_t lo = total * shard / nsh, hi = total * (shard + 1) / nsh;

    for (int i = 0; i < npts; i++) cursign[i] = eta_s[i];
    uint64_t g0 = lo ^ (lo >> 1), acc = 0;
    for (int i = 0; i < rnk; i++) if (g0 >> i & 1) acc ^= basis[i];
    for (int j = 0; j < npts; j++) if (acc >> j & 1) cursign[j] = -cursign[j];

    uint64_t prev = g0, evals = 0, valid = 0, maxev = 0, logged = 0;
    int stop = 0;
    for (uint64_t m = lo; m < hi && !stop; m++) {
        uint64_t g = m ^ (m >> 1), diff = g ^ prev;
        while (diff) {
            uint64_t low = diff & (~diff + 1);
            uint64_t b = basis[__builtin_ctzll(low)];
            for (int j = 0; j < npts; j++) if (b >> j & 1) cursign[j] = -cursign[j];
            diff ^= low;
        }
        prev = g;
        for (int f = -1; f < npts; f++) {
            if (f >= 0) cursign[f] = -cursign[f];
            int ok; H128 fp;
            int ncomp = evaluate(cursign, &ok, &fp);
            evals++;
            if (ok) {
                valid++;
                if (ncomp == 22) maxev++;
                if (!seen_fp(fp, ncomp)) {
                    logged++;
                    fprintf(out, "{\"kind\":\"WITNESS\",\"ncomp\":%d,"
                                 "\"sweep_index\":%llu,\"flip\":%d,\"signs\":[",
                            ncomp, (unsigned long long)m, f);
                    for (int j = 0; j < npts; j++)
                        fprintf(out, "%s%d", j ? "," : "", cursign[j]);
                    fprintf(out, "]}\n");
                    fflush(out);
                }
            }
            if (f >= 0) cursign[f] = -cursign[f];
        }
        if ((m & 0xffff) == 0 && deadline > 0 && now() > deadline) stop = 1;
    }
    fprintf(out, "{\"kind\":\"summary\",\"rank\":%d,\"span_points\":%llu,"
                 "\"evals\":%llu,\"valid\":%llu,\"maximal\":%llu,"
                 "\"distinct\":%llu,\"complete\":%d}\n",
            rnk, (unsigned long long)(hi - lo), (unsigned long long)evals,
            (unsigned long long)valid, (unsigned long long)maxev,
            (unsigned long long)logged, stop ? 0 : 1);
    fclose(out);
    fprintf(stderr, "rank=%d evals=%llu distinct=%llu complete=%d\n",
            rnk, (unsigned long long)evals, (unsigned long long)logged, !stop);
    return 0;
}
