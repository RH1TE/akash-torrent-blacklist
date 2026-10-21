#!/usr/bin/env python3
"""Check reviewed case records and build the plain text Akash wallet list."""
import argparse
import datetime as datetime
import json
from pathlib import Path
import re
import sys

BASE = Path(__file__).resolve().parent.parent
CHARS = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
CATEGORIES = {"prohibited-p2p", "attributed-infringement"}
FIELDS = {"id", "wallet", "category", "observed_utc", "approved_utc",
          "expires_on", "reviewer", "issue", "summary", "records"}
CASE_NAME = re.compile(r"AKT-20[0-9]{2}-[0-9]{3}")
REVIEWER_NAME = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?")
ISSUE_URL = re.compile(r"https://github.com/RH1TE/akash-torrent-blacklist/issues/[1-9][0-9]*")


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
        result = datetime.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise InvalidRecord("Invalid timestamp") from exc
    if result.utcoffset() != datetime.timedelta():
        raise InvalidRecord("Timestamp must be UTC")
    return result


def public_text(value):
    if not isinstance(value, str) or not 16 <= len(value.strip()) <= 350:
        return False
    if "\n" in value or "\x00" in value:
        return False
    if re.search(r"(?i)BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY|password\\s*[:=]|api[_-]?key\\s*[:=]", value):
        return False
    return True


def check_case(case, filename, today=None):
    today = today or datetime.datetime.now(datetime.timezone.utc).date()
    if not isinstance(case, dict) or set(case) != FIELDS:
        raise InvalidRecord("Missing or unexpected fields")
    name = case["id"]
    if not isinstance(name, str) or not CASE_NAME.fullmatch(name) or name + ".json" != filename:
        raise InvalidRecord("Case ID and file name do not match")
    if not valid_wallet(case["wallet"]):
        raise InvalidRecord("Invalid Akash wallet")
    if case["category"] not in CATEGORIES:
        raise InvalidRecord("Unknown report category")
    observation = parse_utc(case["observed_utc"])
    approval = parse_utc(case["approved_utc"])
    if observation > approval or approval.date() > today:
        raise InvalidRecord("Invalid observation or approval date")
    try:
        expiry = datetime.date.fromisoformat(case["expires_on"])
    except (TypeError, ValueError) as exc:
        raise InvalidRecord("Invalid expiry date") from exc
    if expiry <= today or expiry > approval.date() + datetime.timedelta(days=180):
        raise InvalidRecord("Case is expired or exceeds 180-day review period")
    if not isinstance(case["reviewer"], str) or not REVIEWER_NAME.fullmatch(case["reviewer"]):
        raise InvalidRecord("Invalid reviewer")
    if not isinstance(case["issue"], str) or not ISSUE_URL.fullmatch(case["issue"]):
        raise InvalidRecord("Issue must be from this repository")
    if not public_text(case["summary"]):
        raise InvalidRecord("Case summary invalid or possibly sensitive")
    evidence = case["records"]
    if not isinstance(evidence, list) or len(evidence) < 2:
        raise InvalidRecord("At least two records required")
    kinds = set()
    for item in evidence:
        if not isinstance(item, dict) or set(item) != {"kind", "summary"}:
            raise InvalidRecord("Invalid evidence record")
        if not public_text(item["summary"]) or not isinstance(item["kind"], str):
            raise InvalidRecord("Invalid evidence summary")
        kinds.add(item["kind"])
    if case["category"] == "prohibited-p2p":
        if not {"deployment", "runtime"}.issubset(kinds):
            raise InvalidRecord("P2P case requires deployment and runtime evidence")
    else:
        if not {"complaint", "connection"}.issubset(kinds):
            raise InvalidRecord("Infringement attribution requires complaint and connection records")


def cases(base=BASE, today=None):
    result = []
    ids = set()
    for item in sorted((base / "cases").glob("AKT-*.json")):
        try:
            record = json.loads(item.read_text(encoding="utf-8"))
            check_case(record, item.name, today)
        except (ValueError, TypeError, KeyError) as exc:
            raise InvalidRecord(f"{item.name}: {exc}") from exc
        if record["id"] in ids:
            raise InvalidRecord("Duplicate case ID")
        ids.add(record["id"])
        result.append(record)
    return result


def expected_list(base=BASE, today=None):
    wallets = sorted({item["wallet"] for item in cases(base, today)})
    return ("# Approved Akash tenant wallets only\n"
            + ("# No reports have been accepted yet.\n" if not wallets else "")
            + "".join(w + "\n" for w in wallets))


def check_feed(path):
    result = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        item = line.strip()
        if not item or item.startswith("#"):
            continue
        if not valid_wallet(item):
            raise InvalidRecord(f"Invalid wallet on line {number}")
        result.append(item)
    if len(set(result)) != len(result):
        raise InvalidRecord("Duplicate wallet")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "build", "check"))
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--wallet")
    parser.add_argument("--feed", type=Path)
    opts = parser.parse_args()
    try:
        output = opts.base / "blacklist.txt"
        if opts.command == "build":
            output.write_text(expected_list(opts.base), encoding="utf-8")
            print("Updated blacklist.txt")
        elif opts.command == "verify":
            if output.read_text(encoding="utf-8") != expected_list(opts.base):
                raise InvalidRecord("List differs from reviewed cases. Run build.")
            print(f"Verified {len(check_feed(output))} approved wallets")
        else:
            if not valid_wallet(opts.wallet):
                raise InvalidRecord("Use --wallet with a valid Akash address")
            if opts.wallet in check_feed(opts.feed or output):
                print("LISTED")
                return 1
            print("NOT LISTED")
        return 0
    except (InvalidRecord, OSError) as exc:
        print("Error:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
