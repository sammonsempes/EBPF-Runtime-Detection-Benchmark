#ifndef BENCH_WORKLOAD_COMMON_H
#define BENCH_WORKLOAD_COMMON_H

#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define SAMPLER_CAPACITY 100000

struct sampler {
    double *values;
    size_t capacity;
    size_t stored;
    uint64_t seen;
    uint64_t random_state;
};

struct loop_result {
    uint64_t completed;
    uint64_t failed;
    double wall_seconds;
};

typedef int64_t (*timed_operation)(void);

static inline uint64_t monotonic_ns(void)
{
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    return (uint64_t)now.tv_sec * 1000000000ull + (uint64_t)now.tv_nsec;
}

static inline void sampler_init(struct sampler *sampler, size_t capacity)
{
    sampler->values = malloc(capacity * sizeof(double));
    if (sampler->values == NULL) {
        perror("malloc");
        exit(1);
    }
    sampler->capacity = capacity;
    sampler->stored = 0;
    sampler->seen = 0;
    sampler->random_state = 0x9E3779B97F4A7C15ull;
}

static inline void sampler_reset(struct sampler *sampler)
{
    sampler->stored = 0;
    sampler->seen = 0;
}

static inline void sampler_free(struct sampler *sampler)
{
    free(sampler->values);
    sampler->values = NULL;
}

static inline uint64_t sampler_next_random(struct sampler *sampler)
{
    uint64_t state = sampler->random_state;
    state ^= state << 13;
    state ^= state >> 7;
    state ^= state << 17;
    sampler->random_state = state;
    return state;
}

static inline void sampler_add(struct sampler *sampler, double value)
{
    sampler->seen++;
    if (sampler->stored < sampler->capacity) {
        sampler->values[sampler->stored++] = value;
        return;
    }
    uint64_t slot = sampler_next_random(sampler) % sampler->seen;
    if (slot < sampler->capacity)
        sampler->values[slot] = value;
}

static inline int compare_doubles(const void *left, const void *right)
{
    double a = *(const double *)left;
    double b = *(const double *)right;
    return (a > b) - (a < b);
}

static inline void sampler_sort(struct sampler *sampler)
{
    qsort(sampler->values, sampler->stored, sizeof(double), compare_doubles);
}

static inline double sampler_percentile(const struct sampler *sampler, double percentile)
{
    if (sampler->stored == 0)
        return 0.0;
    size_t rank = (size_t)(percentile / 100.0 * (double)(sampler->stored - 1) + 0.5);
    return sampler->values[rank];
}

static inline struct loop_result run_timed_loop(timed_operation operation, double seconds, struct sampler *sampler)
{
    struct loop_result result = {0, 0, 0.0};
    sampler_reset(sampler);
    uint64_t start = monotonic_ns();
    uint64_t deadline = start + (uint64_t)(seconds * 1e9);
    uint64_t now = start;
    while (now < deadline) {
        int64_t elapsed_ns = operation();
        if (elapsed_ns < 0) {
            result.failed++;
        } else {
            sampler_add(sampler, (double)elapsed_ns);
            result.completed++;
        }
        now = monotonic_ns();
    }
    result.wall_seconds = (double)(now - start) / 1e9;
    sampler_sort(sampler);
    return result;
}

static inline double rate_per_second(const struct loop_result *result)
{
    return result->wall_seconds > 0.0 ? (double)result->completed / result->wall_seconds : 0.0;
}

static inline double parse_duration(int argc, char **argv)
{
    for (int index = 1; index + 1 < argc; index++) {
        if (strcmp(argv[index], "--duration") == 0) {
            char *end = NULL;
            double seconds = strtod(argv[index + 1], &end);
            if (end != argv[index + 1] && *end == '\0' && seconds > 0.0)
                return seconds;
        }
    }
    fprintf(stderr, "usage: %s --duration <seconds>\n", argv[0]);
    exit(2);
}

struct metrics_writer {
    int written;
};

static inline void metrics_begin(struct metrics_writer *writer, const char *name)
{
    writer->written = 0;
    printf("{\"name\": \"%s\", \"metrics\": {", name);
}

static inline void metrics_add(struct metrics_writer *writer, const char *prefix, const char *key, double value)
{
    if (!isfinite(value))
        value = 0.0;
    printf("%s\"%s%s%s\": %.3f", writer->written ? ", " : "", prefix ? prefix : "", prefix ? "_" : "", key, value);
    writer->written++;
}

static inline void metrics_end(void)
{
    printf("}}\n");
    fflush(stdout);
}

#endif
