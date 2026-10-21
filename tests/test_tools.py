import datetime as dt
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import correlate_flows
import evidence
import list as listing
import provider_check
import scan_pods
import scan_flows
import update_feed


ROOT = Path(__file__).resolve().parents[1]


class TestPodScanner(unittest.TestCase):
    def test_finds_suspicious_image_and_ignores_web(self):
        with (ROOT / "examples/pods.json").open() as f:
            data = json.load(f)
        findings = scan_pods.scan(data, scan_pods.read_rules(ROOT / "rules/indicators.json"))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["pod"], "downloads-6c78d")
        self.assertIn("client-qbittorrent", [s["rule"] for s in findings[0]["signals"]])

    def test_namespace_filter(self):
        data = json.loads((ROOT / "examples/pods.json").read_text())
        findings = scan_pods.scan(data, scan_pods.read_rules(ROOT / "rules/indicators.json"), "tenant-example-other")
        self.assertEqual(findings, [])

    def test_invalid_inventory(self):
        with self.assertRaises(ValueError):
            scan_pods.scan({"kind": "ServiceList", "items": []}, [])


class TestFlowCorrelation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.flows = [json.loads(s) for s in (ROOT / "examples/flows.jsonl").read_text().splitlines()]

    def test_exact_tuple(self):
        r = correlate_flows.correlate(self.flows, "203.0.113.10", 42000, "tcp",
                                     "2026-01-15T12:00:00Z", "198.51.100.40", 51413)
        self.assertEqual(r["status"], "single_tuple_match_requires_source_verification")
        self.assertEqual(r["candidate_count"], 1)

    def test_without_destination_is_only_candidate(self):
        r = correlate_flows.correlate(self.flows, "203.0.113.10", 42000, "tcp", "2026-01-15T12:00:00Z")
        self.assertEqual(r["status"], "single_public_tuple_match_destination_unverified")

    def test_ambiguous_source_nat_reuse(self):
        more = dict(self.flows[0], event_id="flow-0003", private_src_port=62001, pod="other-pod")
        r = correlate_flows.correlate(self.flows + [more], "203.0.113.10", 42000, "tcp", "2026-01-15T12:00:00Z")
        self.assertEqual(r["status"], "ambiguous_multiple_mappings")

    def test_no_retained_mapping(self):
        r = correlate_flows.correlate(self.flows, "203.0.113.10", 61582, "tcp", "2026-01-15T12:00:00Z")
        self.assertEqual(r["status"], "no_retained_mapping")


class TestEvidence(unittest.TestCase):
    def test_file_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "evidence"
            source.mkdir()
            (source / "record.txt").write_text("sample private log")
            report = evidence.make_manifest(source, base / "manifest.json")
            self.assertEqual(report["file_count"], 1)
            self.assertEqual(len(report["files"][0]["sha256"]), 64)

    def test_manifest_cannot_contain_own_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            (source / "log.txt").write_text("x")
            with self.assertRaises(ValueError):
                evidence.make_manifest(source, source / "manifest.json")


class TestProviderChecks(unittest.TestCase):
    def test_override_precedence(self):
        wallet = listing.valid_wallet
        self.assertEqual(provider_check.decide("example", ["example"], ["example"], []), "local-allow")
        self.assertEqual(provider_check.decide("example", ["example"], ["example"], ["example"]), "local-deny")
        self.assertEqual(provider_check.decide("example", [], [], []), "not-listed")

    def test_feed_fetch_is_atomic(self):
        class Response:
            headers = {}
            def __init__(self, content):
                self.content = content
            def __enter__(self):
                return self
            def __exit__(self, *a):
                pass
            def read(self, amount):
                return self.content
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "feed.txt"
            dest.write_text("# previous good list\n")
            r = update_feed.update("https://example.com/feed.txt", dest,
                                   opener=lambda req, timeout: Response(b"# approved wallet feed\n"))
            self.assertEqual(r["wallets"], 0)
            before = dest.read_text()
            with self.assertRaises(ValueError):
                update_feed.update("https://example.com/feed.txt", dest,
                                   opener=lambda req, timeout: Response(b"invalid_wallet\n"))
            self.assertEqual(dest.read_text(), before)


if __name__ == "__main__":
    unittest.main()


class TestBehaviouralScreening(unittest.TestCase):
    def test_fanout_alert_is_anomaly_not_infringement(self):
        t="2026-01-15T12:00:00Z"
        flows=[{"at":t,"namespace":"a","pod":"p","owner":"synthetic",
                "lease_dseq":"1792500000001","dest_ip":f"198.51.100.{i}",
                "bytes_out":100} for i in range(1,6)]
        r=scan_flows.profile(flows,"2026-01-15T12:05:00Z",minutes=15,
                             min_peers=4,min_egress_bytes=100000)
        self.assertEqual(len(r),1)
        self.assertEqual(r[0]["distinct_peer_count"],5)
        self.assertIn("Traffic anomaly only",r[0]["interpretation"])
        self.assertNotIn("dest_ip",r[0])

    def test_normal_traffic_not_flagged(self):
        flows=[{"at":"2026-01-15T12:00:00Z","namespace":"a","pod":"p",
                "dest_ip":"192.0.2.5","bytes_out":10}]
        r=scan_flows.profile(flows,"2026-01-15T12:05:00Z",
                             min_peers=4,min_egress_bytes=100000)
        self.assertEqual(r, [])

    def test_invalid_threshold(self):
        with self.assertRaises(ValueError):
            scan_flows.profile([], "2026-01-15T12:05:00Z", minutes=0)
