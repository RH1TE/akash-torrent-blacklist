#!/usr/bin/env python3
"""Correlate a complainant's public tuple to saved source-NAT flow metadata.

This is a local-only, read-only tool. It does not create or retrieve NAT logs.
"""
import argparse
import datetime as dt
import ipaddress
import json
from pathlib import Path
import sys


def utc(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("Timestamp must be UTC ISO 8601 ending in Z")
    return dt.datetime.fromisoformat(value[:-1] + "+00:00")


def valid_port(p):
    return isinstance(p, int) and not isinstance(p, bool) and 1 <= p <= 65535


def correlate(records, public_ip, public_port, protocol, at, dest_ip=None, dest_port=None, tolerance=5):
    if protocol not in ("tcp", "udp") or not valid_port(public_port) or not 0 <= tolerance <= 600:
        raise ValueError("Invalid protocol, port or tolerance")
    ipaddress.ip_address(public_ip)
    if dest_ip:
        ipaddress.ip_address(dest_ip)
    target = utc(at)
    candidates = []
    for record in records:
        if not isinstance(record, dict):
            continue
        required = {"at", "protocol", "public_src_ip", "public_src_port",
                    "dest_ip", "dest_port", "private_src_ip", "private_src_port",
                    "namespace", "pod", "lease_dseq", "observed_by", "event_id"}
        if not required.issubset(record):
            continue
        try:
            observed = utc(record["at"])
        except (ValueError, TypeError):
            continue
        if abs((observed - target).total_seconds()) > tolerance:
            continue
        if (record["protocol"] != protocol or record["public_src_ip"] != public_ip
                or record["public_src_port"] != public_port):
            continue
        if dest_ip and record["dest_ip"] != dest_ip:
            continue
        if dest_port is not None and record["dest_port"] != dest_port:
            continue
        candidates.append(record)
    unique = {(r["event_id"], r["private_src_ip"], r["private_src_port"],
               r["dest_ip"], r["dest_port"], r["lease_dseq"]) for r in candidates}
    if not candidates:
        status = "no_retained_mapping"
    elif len(unique) > 1:
        status = "ambiguous_multiple_mappings"
    elif dest_ip and dest_port is not None:
        status = "single_tuple_match_requires_source_verification"
    else:
        status = "single_public_tuple_match_destination_unverified"
    return {
        "status": status,
        "candidate_count": len(unique),
        "matches": sorted(candidates, key=lambda x: (x["at"], x["event_id"])),
        "tolerance_seconds": tolerance,
        "note": "These are supplied historic flow records, not independent verification of a copyrighted transfer."
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flows", required=True, type=Path)
    parser.add_argument("--public-ip", required=True)
    parser.add_argument("--public-port", required=True, type=int)
    parser.add_argument("--protocol", required=True, choices=("tcp", "udp"))
    parser.add_argument("--at", required=True)
    parser.add_argument("--dest-ip")
    parser.add_argument("--dest-port", type=int)
    parser.add_argument("--tolerance", type=int, default=5)
    args = parser.parse_args()
    try:
        if args.flows.stat().st_size > 100 * 1024 * 1024:
            raise ValueError("Flow file too large")
        with args.flows.open(encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]
        if not all(isinstance(x, dict) for x in records):
            raise ValueError("Each JSONL row must be an object")
        result = correlate(records, args.public_ip, args.public_port, args.protocol,
                           args.at, args.dest_ip, args.dest_port, args.tolerance)
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"Could not correlate saved flows: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
