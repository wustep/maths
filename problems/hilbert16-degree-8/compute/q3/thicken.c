/* thicken -- Haas maximal stratum of one triangulation, Hamming ball
 * of radius R around EVERY point of eta + span{delta_S}.
 *
 * R=1 is the leftover whole-stratum thicken (parent thickc.c): every
 * sign vector at distance <= 1 from the complete maximal stratum, not
 * from the one published representative per scheme.
 * R=2 adds every pair of coordinate flips (used on low-rank tris).
 *
 * usage: thicken <task.txt> <shard> <nshards> <out.jsonl> <radius> [maxseconds]
 */
#include "../tcore.h"
#include <time.h>

static double now(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static void emit(FILE *out, int ncomp, unsigned long long m, int f, int g)
{
    fprintf(out, "{\"kind\":\"WITNESS\",\"ncomp\":%d,"
                 "\"sweep_index\":%llu,\"flip\":%d,\"flip2\":%d,\"signs\":[",
            ncomp, m, f, g);
    for (int j = 0; j < npts; j++)
        fprintf(out, "%s%d", j ? "," : "", cursign[j]);
    fprintf(out, "]}\n");
    fflush(out);
}

int main(int argc, char **argv)
{
    if (argc < 6) {
        fprintf(stderr, "usage: thicken task shard nshards out radius [sec]\n");
        return 1;
    }
    fclose(load_task(argv[1]));
    long shard = atol(argv[2]), nsh = atol(argv[3]);
    FILE *out = fopen(argv[4], "w");
    int radius = atoi(argv[5]);
    if (radius < 0 || radius > 2) {
        fprintf(stderr, "radius must be 0, 1 or 2\n");
        return 1;
    }
    double deadline = (argc > 6) ? now() + atof(argv[6]) : 0;

    uint64_t total = (rnk >= 63) ? 0 : (1ULL << rnk);
    uint64_t lo = total * shard / nsh, hi = total * (shard + 1) / nsh;

    for (int i = 0; i < npts; i++) cursign[i] = eta_s[i];
    uint64_t g0 = lo ^ (lo >> 1), acc = 0;
    for (int i = 0; i < rnk; i++) if (g0 >> i & 1) acc ^= basis[i];
    for (int j = 0; j < npts; j++) if (acc >> j & 1) cursign[j] = -cursign[j];

    uint64_t prev = g0, evals = 0, valid = 0, maxev = 0, logged = 0;
    int stop = 0;
    for (uint64_t m = lo; m < hi && !stop; m++) {
        uint64_t gcode = m ^ (m >> 1), diff = gcode ^ prev;
        while (diff) {
            uint64_t low = diff & (~diff + 1);
            uint64_t b = basis[__builtin_ctzll(low)];
            for (int j = 0; j < npts; j++) if (b >> j & 1) cursign[j] = -cursign[j];
            diff ^= low;
        }
        prev = gcode;
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
                    emit(out, ncomp, (unsigned long long)m, f, -1);
                }
            }
            if (radius >= 2 && f >= 0) {
                for (int g = f + 1; g < npts; g++) {
                    cursign[g] = -cursign[g];
                    ncomp = evaluate(cursign, &ok, &fp);
                    evals++;
                    if (ok) {
                        valid++;
                        if (ncomp == 22) maxev++;
                        if (!seen_fp(fp, ncomp)) {
                            logged++;
                            emit(out, ncomp, (unsigned long long)m, f, g);
                        }
                    }
                    cursign[g] = -cursign[g];
                }
            }
            if (f >= 0) cursign[f] = -cursign[f];
            if (radius == 0) break;
        }
        if ((m & 0xffff) == 0) {
            char ppath[512];
            snprintf(ppath, sizeof(ppath), "%s.progress", argv[4]);
            FILE *pf = fopen(ppath, "w");
            if (pf) {
                fprintf(pf,
                        "{\"m\":%llu,\"lo\":%llu,\"hi\":%llu,\"evals\":%llu,"
                        "\"rank\":%d,\"radius\":%d}\n",
                        (unsigned long long)m, (unsigned long long)lo,
                        (unsigned long long)hi, (unsigned long long)evals,
                        rnk, radius);
                fclose(pf);
            }
            if (deadline > 0 && now() > deadline) stop = 1;
        }
    }
    fprintf(out, "{\"kind\":\"summary\",\"rank\":%d,\"radius\":%d,"
                 "\"span_points\":%llu,\"evals\":%llu,\"valid\":%llu,"
                 "\"maximal\":%llu,\"distinct\":%llu,\"complete\":%d}\n",
            rnk, radius, (unsigned long long)(hi - lo),
            (unsigned long long)evals, (unsigned long long)valid,
            (unsigned long long)maxev, (unsigned long long)logged,
            stop ? 0 : 1);
    fclose(out);
    fprintf(stderr, "rank=%d radius=%d evals=%llu distinct=%llu complete=%d\n",
            rnk, radius, (unsigned long long)evals,
            (unsigned long long)logged, !stop);
    return 0;
}
