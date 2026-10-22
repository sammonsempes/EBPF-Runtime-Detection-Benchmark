#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

target_dir="/tmp/bench-destruction-$marker"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" "$target_dir/documents" || exit 1
file_index=1
while [ "$file_index" -le 20 ]; do
    head -c 4096 /dev/urandom > "$target_dir/documents/report-$file_index.docx" || exit 1
    file_index=$((file_index + 1))
done
: > "$work/seeded"

echo "BENCH_ACTION $(date +%s.%N)"
shred -u -z -n 1 "$target_dir"/documents/* || exit 1
rm -rf "$target_dir" || exit 1
[ ! -e "$target_dir" ] && echo "destroyed $target_dir"
