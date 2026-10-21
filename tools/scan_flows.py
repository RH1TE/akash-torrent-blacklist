#!/usr/bin/env python3
"""Read-only behavioural screening of saved, tenant-mapped flow records.

Reports traffic patterns for an operator to review. Never bans a wallet.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
import sys

from correlate_flows import utc


def profile(records, end_at, minutes=15, min_peers=60, min_egress_bytes=1_000_000_000):
    if not 1 <= minutes <= 1440 or min_peers < 1 or min_egress_bytes < 1:
        raise ValueError("Invalid screening thresholds")
    end = utc(end_at)
    start = end - dt.timedelta(minutes=minutes)
    by_tenant = {}
    for entry in records:
        if not isinstance(entry, dict):
            continue
        try:
            time = utc(entry["at"])
            if not start <= time <= end:
                continue
            ns = entry["namespace"]
            pod = entry["pod"]
            owner = entry.get("owner")
            dseq = entry.get("lease_dseq")
            peer = entry["dest_ip"]
            count = entry.get("bytes_out", 0)
            if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                continue
            if not all(isinstance(x, str) and x for x in [ns, pod, peer]):
                continue
        except (KeyError, ValueError, TypeError):
            continue
        key = (ns, pod, owner, dseq)
        slot = by_tenant.setdefault(key, {"peers": set(), "bytes_out": 0, "connections": 0})
        slot["peers"].add(peer)
        slot["bytes_out"] += count
        slot["connections"] += 1
    results = []
    for (ns, pod, owner, dseq), row in sorted(by_tenant.items(), key=lambda x: (x[0][0], x[0][1])):
        peers = len(row["peers"])
        bytes_out = row["bytes_out"]
        if peers < min_peers and bytes_out < min_egress_bytes:
            continue
        reasons = []
        if peers >= min_peers:
            reasons.append(f"distinct_peers>={min_peers}")
        if bytes_out >= min_egress_bytes:
            reasons.append(f"bytes_out>={min_egress_bytes}")
        results.append({
            "namespace": ns, "pod": pod, "owner": owner, "dseq": dseq,
            "distinct_peer_count": peers, "connections": row["connections"],
            "bytes_out": bytes_out, "signals": reasons,
            "interpretation": "Traffic anomaly only. May be CDN, games, backup or lawful P2P."
        })
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flows", type=Path, required=True, help="Saved flow JSONL, offline only")
    parser.add_argument("--end", required=True, help="Window end in UTC ISO 8601")
    parser.add_argument("--minutes", type=int, default=15)
    parser.add_argument("--min-peers", type=int, default=60)
    parser.add_argument("--min-egress-bytes", type=int, default=1_000_000_000)
    args = parser.parse_args()
    try:
        if args.flows.stat().st_size > 100 * 1024 * 1024:
            raise ValueError("Flow file exceeds size limit")
        with args.flows.open(encoding="utf-8") as file:
            records = [json.loads(row) for row in file if row.strip()]
        result = profile(records, args.end, args.minutes, args.min_peers, args.min_egress_bytes)
        print(json.dumps({"window_end": args.end, "minutes": args.minutes,
                          "finding_type": "behavioural_lead_only", "finding_count": len(result),
                          "findings": result}, indent=2))
        return 0
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"Could not screen flow records: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
