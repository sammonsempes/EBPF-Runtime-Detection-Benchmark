#define _GNU_SOURCE
#include "common.h"

#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#define TRUE_BINARY "/bin/true"

extern char **environ;

static int64_t timed_fork_exec_true(void)
{
    char *const arguments[] = {TRUE_BINARY, NULL};
    uint64_t start = monotonic_ns();
    pid_t child = fork();
    if (child < 0)
        return -1;
    if (child == 0) {
        execve(TRUE_BINARY, arguments, environ);
        _exit(127);
    }
    int status = 0;
    if (waitpid(child, &status, 0) != child)
        return -1;
    int64_t elapsed = (int64_t)(monotonic_ns() - start);
    return WIFEXITED(status) && WEXITSTATUS(status) == 0 ? elapsed : -1;
}

int main(int argc, char **argv)
{
    double duration = parse_duration(argc, argv);
    struct sampler sampler;
    sampler_init(&sampler, SAMPLER_CAPACITY);
    struct loop_result result = run_timed_loop(timed_fork_exec_true, duration, &sampler);

    struct metrics_writer writer;
    metrics_begin(&writer, "exec");
    metrics_add(&writer, NULL, "execs_per_sec", rate_per_second(&result));
    metrics_add(&writer, NULL, "p50_us", sampler_percentile(&sampler, 50.0) / 1000.0);
    metrics_add(&writer, NULL, "p99_us", sampler_percentile(&sampler, 99.0) / 1000.0);
    metrics_end();

    sampler_free(&sampler);
    return 0;
}
