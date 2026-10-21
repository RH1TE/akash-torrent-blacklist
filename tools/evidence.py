#!/usr/bin/env python3
"""Create a private, reproducible integrity manifest for targeted incident files."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys


def make_manifest(directory, output):
    directory = Path(directory).resolve(strict=True)
    output = Path(output).resolve()
    if not directory.is_dir():
        raise ValueError("Evidence source must be a directory")
    if output.is_relative_to(directory):
        raise ValueError("Store the integrity manifest outside the evidence input directory")
    contents = []
    total = 0
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlink rejected: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(directory).as_posix()
        if path.stat().st_size > 2 * 1024 * 1024 * 1024:
            raise ValueError(f"File too large for this safe utility: {relative}")
        sha = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                sha.update(chunk)
        size = path.stat().st_size
        total += size
        contents.append({"path": relative, "size": size, "sha256": sha.hexdigest()})
    if not contents:
        raise ValueError("No evidence files found")
    return {"schema": 1, "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "source": "operator-selected local evidence directory",
            "files": contents, "file_count": len(contents), "total_bytes": total,
            "handling": "Private evidence only. Do not commit or upload this manifest to the public registry."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["manifest"])
    parser.add_argument("--dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        data = make_manifest(args.dir, args.out)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        if args.out.exists():
            raise FileExistsError("Will not overwrite an existing evidence manifest")
        with args.out.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(data, indent=2) + "\n")
        args.out.chmod(0o600)
        print(f'Hashed {data["file_count"]} local files. Manifest saved privately at {args.out}')
        return 0
    except (OSError, ValueError) as exc:
        print(f"Evidence manifest failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
