#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"

data_dir="/srv/bench-data-$marker"
archive="/backup/data-$marker.tar.gz"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$data_dir/reports" "$data_dir/uploads" /backup || exit 1
file_index=1
while [ "$file_index" -le 10 ]; do
    printf 'report %d for %s\n' "$file_index" "$marker" > "$data_dir/reports/report-$file_index.txt"
    printf 'upload %d\n' "$file_index" > "$data_dir/uploads/upload-$file_index.csv"
    file_index=$((file_index + 1))
done

echo "BENCH_ACTION $(date +%s.%N)"
tar -czf "$archive" -C /srv "bench-data-$marker" || exit 1
tar -tzf "$archive" | head -n 5
