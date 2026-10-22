#define _GNU_SOURCE
#include "common.h"

#include <fcntl.h>
#include <limits.h>
#include <unistd.h>

#define FILE_SIZE 4096

static char work_directory[] = "/tmp/bench-fileio-XXXXXX";
static char payload[FILE_SIZE];
static uint64_t file_counter;

static int64_t timed_create_write_fsync_unlink(void)
{
    char path[PATH_MAX];
    snprintf(path, sizeof path, "%s/file-%llu", work_directory, (unsigned long long)file_counter++);
    uint64_t start = monotonic_ns();
    int fd = open(path, O_CREAT | O_WRONLY | O_TRUNC | O_CLOEXEC, 0600);
    if (fd < 0)
        return -1;
    ssize_t written = write(fd, payload, sizeof payload);
    int synced = fsync(fd);
    close(fd);
    int removed = unlink(path);
    int64_t elapsed = (int64_t)(monotonic_ns() - start);
    return written == (ssize_t)sizeof payload && synced == 0 && removed == 0 ? elapsed : -1;
}

int main(int argc, char **argv)
{
    double duration = parse_duration(argc, argv);
    if (mkdtemp(work_directory) == NULL) {
        perror("mkdtemp");
        return 1;
    }
    memset(payload, 'b', sizeof payload);

    struct sampler sampler;
    sampler_init(&sampler, SAMPLER_CAPACITY);
    struct loop_result result = run_timed_loop(timed_create_write_fsync_unlink, duration, &sampler);
    rmdir(work_directory);

    struct metrics_writer writer;
    metrics_begin(&writer, "fileio");
    metrics_add(&writer, NULL, "ops_per_sec", rate_per_second(&result));
    metrics_add(&writer, NULL, "p50_us", sampler_percentile(&sampler, 50.0) / 1000.0);
    metrics_add(&writer, NULL, "p99_us", sampler_percentile(&sampler, 99.0) / 1000.0);
    metrics_end();

    sampler_free(&sampler);
    return 0;
}
