#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1

echo "BENCH_ACTION $(date +%s.%N)"
python3 - "$marker" "$work" <<'EOF'
import os
import sys

marker = sys.argv[1]
work_dir = sys.argv[2]
memory_name = "bench-memfd-" + marker
memory_fd = os.memfd_create(memory_name, 0)
with open("/bin/sh", "rb") as shell_binary:
    content = shell_binary.read()
written = 0
while written < len(content):
    written += os.write(memory_fd, content[written:])
script = "echo fileless execution \"$1\"; readlink /proc/$$/exe > \"$2/fileless.proof\"; id"
os.execve(memory_fd, [memory_name, "-c", script, memory_name, marker, work_dir], dict(os.environ))
EOF
