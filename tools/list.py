#!/usr/bin/env python3
"""Validate approved cases and generate the operator wallet feed.

Format version 2. Syntax validation is not evidence verification.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import re
import sys

BASE = Path(__file__).resolve().parent.parent
CHARS = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
CATEGORIES = {"prohibited-p2p", "attributed-infringement"}
FIELDS = {
    "schema_version", "id", "wallet", "chain_id", "dseqs", "category",
    "provider_region", "provider_policy", "observed_utc", "approved_utc",
    "expires_on", "reviewers", "issue", "decision", "risk_notes", "records"
}
CASE_NAME = re.compile(r"AKT-20[0-9]{2}-[0-9]{3}")
REVIEWER_NAME = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?")
ISSUE_URL = re.compile(r"https://github.com/RH1TE/akash-torrent-blacklist/issues/[1-9][0-9]*")
DECIMAL = re.compile(r"[1-9][0-9]{8,15}")
RECORD_KINDS = {"deployment", "runtime", "policy", "complaint", "flow", "other"}


class InvalidRecord(ValueError):
    pass


def polymod(values):
    acc = 1
    generators = (0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3)
    for value in values:
        top = acc >> 25
        acc = ((acc & 0x1ffffff) << 5) ^ value
        for index, generator in enumerate(generators):
            if (top >> index) & 1:
                acc ^= generator
    return acc


def valid_wallet(wallet):
    if not isinstance(wallet, str) or len(wallet) != 44 or not wallet.startswith("akash1"):
        return False
    try:
        data = [CHARS.index(x) for x in wallet[6:]]
    except ValueError:
        return False
    hrp = [ord(x) >> 5 for x in "akash"] + [0] + [ord(x) & 31 for x in "akash"]
    return polymod(hrp + data) == 1


def parse_utc(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise InvalidRecord("Use UTC timestamps ending in Z")
    try:
        result = dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise InvalidRecord("Invalid timestamp") from exc
    if result.utcoffset() != dt.timedelta():
        raise InvalidRecord("Timestamp must be UTC")
    return result


def public_text(value, min_length=16, max_length=600):
    if not isinstance(value, str) or not min_length <= len(value.strip()) <= max_length:
        return False
    if "\n" in value or "\x00" in value:
        return False
    if re.search(r"(?i)BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY|password\s*[:=]|api[_-]?key\s*[:=]", value):
        return False
    return True


def check_case(case, filename, today=None):
    today = today or dt.datetime.now(dt.timezone.utc).date()
    if not isinstance(case, dict) or set(case) != FIELDS:
        raise InvalidRecord("Missing or unexpected case fields")
    name = case["id"]
    if not isinstance(name, str) or not CASE_NAME.fullmatch(name) or name + ".json" != filename:
        raise InvalidRecord("Case ID and filename do not match")
    if case["schema_version"] != 2 or not valid_wallet(case["wallet"]) or case["chain_id"] != "akashnet-2":
        raise InvalidRecord("Invalid schema, chain or wallet checksum")
    dseqs = case["dseqs"]
    if not isinstance(dseqs, list) or not 1 <= len(dseqs) <= 10 or not all(
            isinstance(s, str) and DECIMAL.fullmatch(s) for s in dseqs) or len(dseqs) != len(set(dseqs)):
        raise InvalidRecord("DSEQ references must be unique numeric strings")
    if case["category"] not in CATEGORIES:
        raise InvalidRecord("Unknown report category")
    observed = parse_utc(case["observed_utc"])
    approved = parse_utc(case["approved_utc"])
    if observed > approved or approved.date() > today:
        raise InvalidRecord("Observation and approval times inconsistent")
    try:
        expiry = dt.date.fromisoformat(case["expires_on"])
    except (TypeError, ValueError) as exc:
        raise InvalidRecord("Invalid expiry date") from exc
    if not (today < expiry <= approved.date() + dt.timedelta(days=180)):
        raise InvalidRecord("Entry expired or outside 180-day review window")
    if not isinstance(case["provider_region"], str) or not re.fullmatch(r"[A-Za-z0-9-]{2,40}", case["provider_region"]):
        raise InvalidRecord("Invalid provider region")
    if not isinstance(case["issue"], str) or not ISSUE_URL.fullmatch(case["issue"]):
        raise InvalidRecord("Public report issue must be from this repository")
    for key in ("provider_policy", "decision", "risk_notes"):
        if not public_text(case[key]):
            raise InvalidRecord(f"Invalid public summary: {key}")
    reviewers = case["reviewers"]
    if (not isinstance(reviewers, list) or len(reviewers) < 2 or len(reviewers) != len(set(reviewers))
            or any(not isinstance(x, str) or not REVIEWER_NAME.fullmatch(x) for x in reviewers)):
        raise InvalidRecord("Two or more distinct reviewer usernames are required")
    records = case["records"]
    if not isinstance(records, list) or len(records) < 3 or len(records) > 12:
        raise InvalidRecord("Three to twelve reviewed evidence records required")
    kinds = set()
    source_ids = set()
    for entry in records:
        if not isinstance(entry, dict) or set(entry) != {"kind", "source_id", "summary"}:
            raise InvalidRecord("Record needs kind, source_id, summary")
        if entry["kind"] not in RECORD_KINDS:
            raise InvalidRecord("Unknown evidence kind")
        if not isinstance(entry["source_id"], str) or not re.fullmatch(r"[A-Za-z0-9_-]{5,60}", entry["source_id"]):
            raise InvalidRecord("Source ID must be an opaque private evidence reference")
        if entry["source_id"] in source_ids:
            raise InvalidRecord("Duplicate evidence source ID")
        if not public_text(entry["summary"]):
            raise InvalidRecord("Invalid evidence summary")
        source_ids.add(entry["source_id"])
        kinds.add(entry["kind"])
    required = ({"deployment", "runtime", "policy"} if case["category"] == "prohibited-p2p"
                else {"complaint", "flow", "deployment"})
    if not required.issubset(kinds):
        raise InvalidRecord(f"Missing required evidence types: {sorted(required - kinds)}")


def cases(base=BASE, today=None):
    result = []
    ids = set()
    for path in sorted((base / "cases").glob("AKT-*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            check_case(record, path.name, today)
        except (ValueError, TypeError, KeyError) as exc:
            raise InvalidRecord(f"{path.name}: {exc}") from exc
        if record["id"] in ids:
            raise InvalidRecord("Duplicate case ID")
        ids.add(record["id"])
        result.append(record)
    return result


def render_feeds(base=BASE, today=None):
    records = cases(base, today)
    wallets = sorted({item["wallet"] for item in records})
    txt = ("# Approved Akash tenant wallets only\n"
           + ("# No reports have been accepted yet.\n" if not wallets else "")
           + "".join(x + "\n" for x in wallets))
    machine = {"schema_version": 2,
               "purpose": "operator-reviewed advisory intelligence",
               "wallets": [
                   {"wallet": wallet,
                    "cases": [{"id": c["id"], "category": c["category"], "expires_on": c["expires_on"],
                               "issue": c["issue"]} for c in records if c["wallet"] == wallet]}
                   for wallet in wallets]}
    return txt, json.dumps(machine, indent=2) + "\n"


def expected_list(base=BASE, today=None):
    return render_feeds(base, today)[0]


def check_feed(path):
    result = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        item = line.strip()
        if not item or item.startswith("#"):
            continue
        if not valid_wallet(item):
            raise InvalidRecord(f"Invalid wallet on line {number}")
        result.append(item)
    if len(set(result)) != len(result):
        raise InvalidRecord("Duplicate wallet")
    if len(result) > 100000:
        raise InvalidRecord("Unreasonable list size")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "build", "check", "stats"))
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--wallet")
    parser.add_argument("--feed", type=Path)
    options = parser.parse_args()
    try:
        output = options.base / "blacklist.txt"
        machine_path = options.base / "approved.json"
        if options.command == "build":
            txt, machine = render_feeds(options.base)
            output.write_text(txt, encoding="utf-8")
            machine_path.write_text(machine, encoding="utf-8")
            print(f"Generated {len(check_feed(output))} reviewed wallets")
        elif options.command == "verify":
            txt, machine = render_feeds(options.base)
            if output.read_text(encoding="utf-8") != txt:
                raise InvalidRecord("Text list differs from approved cases. Run build.")
            if machine_path.read_text(encoding="utf-8") != machine:
                raise InvalidRecord("Machine feed differs from approved cases. Run build.")
            print(f"Verified {len(check_feed(output))} approved wallets and both feeds")
        elif options.command == "stats":
            records = cases(options.base)
            print(json.dumps({"approved_cases": len(records), "distinct_wallets": len(set(x["wallet"] for x in records)),
                              "categories": {x: sum(r["category"] == x for r in records) for x in sorted(CATEGORIES)}}, indent=2))
        else:
            if not valid_wallet(options.wallet):
                raise InvalidRecord("Use --wallet with a valid Akash address")
            print("LISTED" if options.wallet in check_feed(options.feed or output) else "NOT LISTED")
        return 0
    except (InvalidRecord, OSError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
