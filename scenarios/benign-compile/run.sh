#!/bin/sh
set -u
marker="${BENCH_MARKER:-manual}"
work="/tmp/bench-$marker"

workspace="/root/workspace/bench-$marker"

sh "$(dirname "$0")/cleanup.sh"
mkdir -p "$workspace" "$work" || exit 1
cat > "$workspace/checksum.c" <<'EOF'
#include <stdio.h>
#include <string.h>

static unsigned long checksum(const char *text)
{
    unsigned long hash = 5381;
    for (size_t index = 0; index < strlen(text); index++)
        hash = hash * 33 + (unsigned char)text[index];
    return hash;
}

int main(int argc, char **argv)
{
    const char *input = argc > 1 ? argv[1] : "bench";
    printf("checksum(%s) = %lu\n", input, checksum(input));
    return 0;
}
EOF
echo "BENCH_ACTION $(date +%s.%N)"
gcc -O2 -Wall -o "$workspace/checksum" "$workspace/checksum.c" || exit 1
"$workspace/checksum" "bench-$marker" > "$work/checksum.out" || exit 1
cat "$work/checksum.out"
