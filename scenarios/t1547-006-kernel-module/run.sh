#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

module_file="/tmp/bench-module-$marker.ko"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$work" || exit 1
printf 'bench dummy kernel module %s\n' "$marker" > "$module_file" || exit 1
echo "BENCH_ACTION $(date +%s.%N)"
insmod_output=$(insmod "$module_file" 2>&1)
insmod_status=$?
printf '%s\n' "$insmod_output" > "$work/insmod.out"
echo "$insmod_status" > "$work/insmod.status"
printf '%s\n' "$insmod_output"

if [ "$insmod_status" -eq 0 ]; then
    exit 0
fi
case "$insmod_output" in
    *"could not insert module"*) exit 0 ;;
    *) exit 1 ;;
esac
