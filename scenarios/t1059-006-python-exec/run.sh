#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1

echo "BENCH_ACTION $(date +%s.%N)"
python3 -c 'import subprocess, sys; sys.exit(subprocess.call(["/bin/sh", "-c", "id; uname -a; echo \"$0\" > \"$1/python-exec.proof\"", sys.argv[1], sys.argv[2]]))' "bench-python-exec-$marker" "$work"
