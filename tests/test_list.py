import datetime as datetime
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import list as listing


def test_wallet():
    payload = [0] * 32
    hrp = [ord(x) >> 5 for x in "akash"] + [0] + [ord(x) & 31 for x in "akash"]
    v = listing.polymod(hrp + payload + [0] * 6) ^ 1
    check = [(v >> (5 * (5 - i))) & 31 for i in range(6)]
    return "akash1" + "".join(listing.CHARS[c] for c in payload + check)


def sample_case():
    return {
        "id": "AKT-2026-001",
        "wallet": test_wallet(),
        "category": "prohibited-p2p",
        "observed_utc": "2026-10-20T10:00:00Z",
        "approved_utc": "2026-10-21T10:00:00Z",
        "expires_on": "2027-01-15",
        "reviewer": "reviewer-one",
        "issue": "https://github.com/RH1TE/akash-torrent-blacklist/issues/123",
        "summary": "Provider confirmed a P2P workload against published and applicable terms.",
        "records": [
            {"kind": "deployment", "summary": "On-chain owner and lease were verified independently."},
            {"kind": "runtime", "summary": "Host runtime recorded the active workload during the lease."},
        ],
    }


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.date = datetime.date(2026, 10, 22)

    def test_wallet_checksum(self):
        self.assertTrue(listing.valid_wallet(test_wallet()))
        self.assertFalse(listing.valid_wallet(test_wallet()[:-1] + "x"))

    def test_case_valid(self):
        listing.check_case(sample_case(), "AKT-2026-001.json", self.date)

    def test_requires_actual_runtime_record(self):
        c = sample_case()
        c["records"][1]["kind"] = "complaint"
        with self.assertRaises(listing.InvalidRecord):
            listing.check_case(c, "AKT-2026-001.json", self.date)

    def test_infringement_requires_flow_attribution(self):
        c = sample_case()
        c["category"] = "attributed-infringement"
        c["records"][0]["kind"] = "complaint"
        with self.assertRaises(listing.InvalidRecord):
            listing.check_case(c, "AKT-2026-001.json", self.date)

    def test_expired_case_rejected(self):
        with self.assertRaises(listing.InvalidRecord):
            listing.check_case(sample_case(), "AKT-2026-001.json", datetime.date(2027, 3, 1))

    def test_private_extra_field_rejected(self):
        c = sample_case()
        c["client_ip"] = "secret"
        with self.assertRaises(listing.InvalidRecord):
            listing.check_case(c, "AKT-2026-001.json", self.date)

    def test_feed_generated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "cases").mkdir()
            (root / "cases/AKT-2026-001.json").write_text(json.dumps(sample_case()))
            self.assertIn(test_wallet(), listing.expected_list(root, self.date))

    def test_invalid_feed_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "blacklist.txt"
            p.write_text(test_wallet() + " extra\n")
            with self.assertRaises(listing.InvalidRecord):
                listing.check_feed(p)


if __name__ == "__main__":
    unittest.main()
