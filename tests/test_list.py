import datetime as dt
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
        "schema_version": 2,
        "id": "AKT-2026-001",
        "wallet": test_wallet(),
        "chain_id": "akashnet-2",
        "dseqs": ["1792500000001"],
        "category": "prohibited-p2p",
        "provider_region": "eu-test",
        "provider_policy": "Example contract explicitly prohibited P2P activity on this fictional provider.",
        "observed_utc": "2026-10-20T10:00:00Z",
        "approved_utc": "2026-10-21T10:00:00Z",
        "expires_on": "2027-01-15",
        "reviewers": ["first-reviewer", "second-reviewer"],
        "issue": "https://github.com/RH1TE/akash-torrent-blacklist/issues/123",
        "decision": "The fictional operator confirmed a running P2P workload under the fictional terms.",
        "risk_notes": "This synthetic observation does not establish any actual file distribution.",
        "records": [
            {"kind": "deployment", "source_id": "chain-record-01", "summary": "On-chain owner and lease metadata were verified."},
            {"kind": "runtime", "source_id": "runtime-record-01", "summary": "Host runtime independently observed a running process."},
            {"kind": "policy", "source_id": "policy-record-01", "summary": "The sample policy prohibited P2P workloads at this timestamp."}
        ]
    }


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.date = dt.date(2026, 10, 22)

    def test_wallet_checksum(self):
        self.assertTrue(listing.valid_wallet(test_wallet()))
        self.assertFalse(listing.valid_wallet(test_wallet()[:-1] + ("x" if test_wallet()[-1] != "x" else "q")))

    def test_case_valid(self):
        listing.check_case(sample_case(), "AKT-2026-001.json", self.date)

    def test_two_reviewers(self):
        c = sample_case()
        c["reviewers"] = ["first-reviewer", "first-reviewer"]
        with self.assertRaises(listing.InvalidRecord):
            listing.check_case(c, "AKT-2026-001.json", self.date)

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
            listing.check_case(sample_case(), "AKT-2026-001.json", dt.date(2027, 3, 1))

    def test_private_extra_field_rejected(self):
        c = sample_case()
        c["client_ip"] = "no public disclosure"
        with self.assertRaises(listing.InvalidRecord):
            listing.check_case(c, "AKT-2026-001.json", self.date)

    def test_feed_generated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "cases").mkdir()
            (root / "cases/AKT-2026-001.json").write_text(json.dumps(sample_case()))
            txt, machine = listing.render_feeds(root, self.date)
            self.assertIn(test_wallet(), txt)
            record = json.loads(machine)["wallets"][0]
            self.assertEqual(record["cases"][0]["category"], "prohibited-p2p")

    def test_invalid_feed_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "blacklist.txt"
            p.write_text(test_wallet() + " extra\n")
            with self.assertRaises(listing.InvalidRecord):
                listing.check_feed(p)

    def test_duplicate_feed_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "blacklist.txt"
            p.write_text(test_wallet() + "\n" + test_wallet() + "\n")
            with self.assertRaises(listing.InvalidRecord):
                listing.check_feed(p)

    def test_invalid_evidence_duplicate(self):
        c = sample_case()
        c["records"][2]["source_id"] = c["records"][0]["source_id"]
        with self.assertRaises(listing.InvalidRecord):
            listing.check_case(c, "AKT-2026-001.json", self.date)


if __name__ == "__main__":
    unittest.main()
