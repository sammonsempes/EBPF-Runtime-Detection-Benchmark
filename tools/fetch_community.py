from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "ebpf-bench-community-fetch"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def sync(list_file: Path) -> bool:
    ok = True
    base = list_file.parent
    for number, line in enumerate(list_file.read_text().splitlines(), start=1):
        fields = line.split()
        if not fields or fields[0].startswith("#"):
            continue
        if len(fields) != 3:
            print(f"INVALID {list_file}:{number}", file=sys.stderr)
            ok = False
            continue
        expected, url, dest = fields
        target = (base / dest).resolve()
        if base.resolve() not in target.parents:
            print(f"OUTSIDE {list_file}:{number} {dest}", file=sys.stderr)
            ok = False
            continue
        try:
            data = fetch(url)
        except OSError as error:
            print(f"FAILED {url}: {error}", file=sys.stderr)
            ok = False
            continue
        actual = hashlib.sha256(data).hexdigest()
        if expected != "-" and expected != actual:
            print(f"MISMATCH {dest} expected {expected} got {actual}", file=sys.stderr)
            ok = False
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        print(f"OK {actual} {url} {dest}")
    return ok


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path("/bench/tools")
    lists = sorted(root.glob("*/community/sources.txt"))
    results = [sync(path) for path in lists]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
