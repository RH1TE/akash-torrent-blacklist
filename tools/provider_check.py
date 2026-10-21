#!/usr/bin/env python3
"""Opt-in policy check. Dry-run by default; never changes Akash resources."""
import argparse
from pathlib import Path
import sys

from list import check_feed, valid_wallet


def decide(wallet, community, allow=(), deny=()):
    if wallet in set(deny):
        return "local-deny"
    if wallet in set(allow):
        return "local-allow"
    if wallet in set(community):
        return "reviewed-community-feed"
    return "not-listed"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wallet", required=True)
    parser.add_argument("--feed", required=True, type=Path)
    parser.add_argument("--allow", type=Path)
    parser.add_argument("--deny", type=Path)
    parser.add_argument("--enforce", action="store_true", help="Return 10 for a denied wallet")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    try:
        if not valid_wallet(args.wallet):
            raise ValueError("Invalid Akash tenant wallet")
        community = check_feed(args.feed)
        allow = check_feed(args.allow) if args.allow and args.allow.exists() else []
        deny = check_feed(args.deny) if args.deny and args.deny.exists() else []
        decision = decide(args.wallet, community, allow, deny)
        if not args.quiet:
            print(f"{decision}: {args.wallet} (enforcement={'on' if args.enforce else 'dry-run'})")
        if args.enforce and decision in ("local-deny", "reviewed-community-feed"):
            return 10
        return 0
    except (OSError, ValueError) as exc:
        print(f"Policy check error: {exc}", file=sys.stderr)
        return 20


if __name__ == "__main__":
    sys.exit(main())
