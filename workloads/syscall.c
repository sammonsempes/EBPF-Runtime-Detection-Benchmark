#define _GNU_SOURCE
#include "common.h"

#include <arpa/inet.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <unistd.h>

#define READ_BUFFER_SIZE 4096
#define PROBE_PATH "/etc/passwd"

struct benchmark {
    const char *name;
    timed_operation operation;
};

static int zero_device_fd = -1;
static int listener_fd = -1;
static struct sockaddr_in listener_address;

static int64_t elapsed_since(uint64_t start)
{
    return (int64_t)(monotonic_ns() - start);
}

static int64_t timed_getpid(void)
{
    uint64_t start = monotonic_ns();
    long pid = syscall(SYS_getpid);
    int64_t elapsed = elapsed_since(start);
    return pid > 0 ? elapsed : -1;
}

static int64_t timed_openat_close(void)
{
    uint64_t start = monotonic_ns();
    int fd = openat(AT_FDCWD, PROBE_PATH, O_RDONLY | O_CLOEXEC);
    if (fd < 0)
        return -1;
    close(fd);
    return elapsed_since(start);
}

static int64_t timed_read(void)
{
    char buffer[READ_BUFFER_SIZE];
    uint64_t start = monotonic_ns();
    ssize_t received = read(zero_device_fd, buffer, sizeof buffer);
    int64_t elapsed = elapsed_since(start);
    return received == (ssize_t)sizeof buffer ? elapsed : -1;
}

static int64_t timed_stat(void)
{
    struct stat information;
    uint64_t start = monotonic_ns();
    int status = stat(PROBE_PATH, &information);
    int64_t elapsed = elapsed_since(start);
    return status == 0 ? elapsed : -1;
}

static int64_t timed_connect(void)
{
    int client_fd = socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (client_fd < 0)
        return -1;
    struct linger abortive_close = {1, 0};
    setsockopt(client_fd, SOL_SOCKET, SO_LINGER, &abortive_close, sizeof abortive_close);
    uint64_t start = monotonic_ns();
    int status = connect(client_fd, (struct sockaddr *)&listener_address, sizeof listener_address);
    int64_t elapsed = elapsed_since(start);
    int accepted_fd = status == 0 ? accept4(listener_fd, NULL, NULL, SOCK_CLOEXEC) : -1;
    close(client_fd);
    if (accepted_fd >= 0)
        close(accepted_fd);
    return status == 0 ? elapsed : -1;
}

static void open_zero_device(void)
{
    zero_device_fd = open("/dev/zero", O_RDONLY | O_CLOEXEC);
    if (zero_device_fd < 0) {
        perror("open /dev/zero");
        exit(1);
    }
}

static void open_loopback_listener(void)
{
    listener_fd = socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (listener_fd < 0) {
        perror("socket");
        exit(1);
    }
    int enabled = 1;
    setsockopt(listener_fd, SOL_SOCKET, SO_REUSEADDR, &enabled, sizeof enabled);
    memset(&listener_address, 0, sizeof listener_address);
    listener_address.sin_family = AF_INET;
    listener_address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    listener_address.sin_port = 0;
    socklen_t address_length = sizeof listener_address;
    if (bind(listener_fd, (struct sockaddr *)&listener_address, sizeof listener_address) != 0 ||
        listen(listener_fd, 128) != 0 ||
        getsockname(listener_fd, (struct sockaddr *)&listener_address, &address_length) != 0) {
        perror("loopback listener");
        exit(1);
    }
}

int main(int argc, char **argv)
{
    double duration = parse_duration(argc, argv);
    const struct benchmark benchmarks[] = {
        {"getpid", timed_getpid},
        {"openat", timed_openat_close},
        {"read", timed_read},
        {"stat", timed_stat},
        {"connect", timed_connect},
    };
    size_t benchmark_count = sizeof benchmarks / sizeof benchmarks[0];
    double seconds_per_benchmark = duration / (double)benchmark_count;

    open_zero_device();
    open_loopback_listener();

    struct sampler sampler;
    sampler_init(&sampler, SAMPLER_CAPACITY);
    struct metrics_writer writer;
    metrics_begin(&writer, "syscall");
    for (size_t index = 0; index < benchmark_count; index++) {
        struct loop_result result = run_timed_loop(benchmarks[index].operation, seconds_per_benchmark, &sampler);
        metrics_add(&writer, benchmarks[index].name, "p50_ns", sampler_percentile(&sampler, 50.0));
        metrics_add(&writer, benchmarks[index].name, "p99_ns", sampler_percentile(&sampler, 99.0));
        metrics_add(&writer, benchmarks[index].name, "ops_per_sec", rate_per_second(&result));
    }
    metrics_end();

    sampler_free(&sampler);
    close(listener_fd);
    close(zero_device_fd);
    return 0;
}
