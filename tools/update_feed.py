#!/usr/bin/env python3
"""Fetch a reviewed wallet feed into an atomic local cache. No provider writes."""
import argparse
import hashlib
import os
from pathlib import Path
import tempfile
import urllib.parse
import urllib.request
import sys

from list import check_feed


DEFAULT_URL = "https://raw.githubusercontent.com/RH1TE/akash-torrent-blacklist/main/blacklist.txt"


def update(url, dest, expected_sha256=None, opener=None):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("Only HTTPS feed URLs are supported")
    if expected_sha256 and (len(expected_sha256) != 64 or any(x not in "0123456789abcdef" for x in expected_sha256)):
        raise ValueError("SHA-256 must be 64 lowercase hex characters")
    req = urllib.request.Request(url, headers={"User-Agent": "akash-torrent-blacklist-feed/1"})
    open_url = opener or urllib.request.urlopen
    with open_url(req, timeout=12) as response:
        length = response.headers.get("Content-Length") if getattr(response, "headers", None) else None
        if length and int(length) > 2_000_000:
            raise ValueError("Remote feed exceeds size limit")
        content = response.read(2_000_001)
    if len(content) > 2_000_000 or not content.strip():
        raise ValueError("Empty or oversized feed; keeping previous cache")
    digest = hashlib.sha256(content).hexdigest()
    if expected_sha256 and digest != expected_sha256:
        raise ValueError("Feed SHA-256 mismatch; keeping previous cache")
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False, mode="wb", prefix=".registry-") as temp:
            tmp_path = Path(temp.name)
            os.chmod(tmp_path, 0o640)
            temp.write(content)
            temp.flush()
            os.fsync(temp.fileno())
        wallets = check_feed(tmp_path)
        os.replace(tmp_path, dest)
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)
    return {"wallets": len(wallets), "sha256": digest, "path": str(dest)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--dest", required=True)
    parser.add_argument("--sha256", help="Expected SHA-256 hex of exact approved feed")
    args = parser.parse_args()
    try:
        item = update(args.url, Path(args.dest), args.sha256)
        print(f'Updated {item["path"]}: {item["wallets"]} reviewed wallets; sha256={item["sha256"]}')
        return 0
    except (OSError, ValueError, urllib.error.URLError) as exc:
        print(f"Feed update failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
