#!/usr/bin/env python3
"""Read-only inspection of a saved Kubernetes PodList.

This is a candidate scanner, not proof of misconduct or a policy enforcer.
"""
import argparse
import json
from pathlib import Path
import re
import sys


def read_rules(path):
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if obj.get("schema") != 1 or not isinstance(obj.get("indicators"), list):
        raise ValueError("Unrecognised indicator rules format")
    result = []
    ids = set()
    for item in obj["indicators"]:
        if set(item) != {"id", "pattern", "fields", "severity", "reason", "false_positive"}:
            raise ValueError("Indicator fields do not match schema")
        if item["id"] in ids or item["severity"] not in {"low", "medium", "high"}:
            raise ValueError("Duplicate ID or unknown indicator severity")
        if not item["fields"] or any(f not in {"pod", "image", "container", "command", "args"} for f in item["fields"]):
            raise ValueError("Invalid indicator field")
        if len(item["pattern"]) > 250:
            raise ValueError("Pattern too large")
        result.append((item, re.compile(item["pattern"], re.IGNORECASE)))
        ids.add(item["id"])
    return result


def scan(data, rules, namespace=None):
    if not isinstance(data, dict) or data.get("kind") not in ("PodList", "List") or not isinstance(data.get("items"), list):
        raise ValueError("Expected kubectl get pods -A -o json PodList")
    findings = []
    for pod in data["items"]:
        if not isinstance(pod, dict):
            continue
        meta = pod.get("metadata", {})
        spec = pod.get("spec", {})
        ns = meta.get("namespace", "")
        if namespace and ns != namespace:
            continue
        labels = meta.get("labels") or {}
        fields = [("pod", meta.get("name", ""))]
        for ctr in (spec.get("initContainers") or []) + (spec.get("containers") or []):
            fields += [("container", ctr.get("name", "")), ("image", ctr.get("image", ""))]
            fields += [("command", str(x)) for x in (ctr.get("command") or []) if isinstance(x, str) and len(x) <= 1024]
            fields += [("args", str(x)) for x in (ctr.get("args") or []) if isinstance(x, str) and len(x) <= 1024]
        hits = []
        for rule, expr in rules:
            sources = sorted({field for field, value in fields if field in rule["fields"] and value and expr.search(value)})
            if sources:
                hits.append({"rule": rule["id"], "severity": rule["severity"],
                             "matched_fields": sources, "reason": rule["reason"]})
        if hits:
            findings.append({"namespace": ns, "pod": meta.get("name"), "pod_uid": meta.get("uid"),
                             "node": spec.get("nodeName"), "owner": labels.get("akash.network/lease.id.owner"),
                             "dseq": labels.get("akash.network/lease.id.dseq"),
                             "status": (pod.get("status") or {}).get("phase"),
                             "signals": hits})
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="PodList JSON path, or - for stdin")
    parser.add_argument("--rules", default=str(Path(__file__).resolve().parents[1] / "rules/indicators.json"))
    parser.add_argument("--namespace", help="Only inspect a known namespace")
    parser.add_argument("--format", choices=("table", "json"), default="table")
    parser.add_argument("--fail-on-signal", action="store_true", help="For tests only, not automatic punishment")
    args = parser.parse_args()
    try:
        if args.input == "-":
            data = json.load(sys.stdin)
        else:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
        findings = scan(data, read_rules(args.rules), args.namespace)
    except (OSError, ValueError, TypeError, re.error) as exc:
        print(f"Cannot scan inventory: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps({"finding_count": len(findings), "findings": findings,
                          "finding_type": "investigative_lead_not_attribution"}, indent=2))
    else:
        print("SCANNER IS READ ONLY. INDICATORS ARE NOT FINDINGS OF INFRINGEMENT.")
        for row in findings:
            names = ",".join(s["rule"] for s in row["signals"])
            print(f'{row["namespace"]}\t{row["pod"]}\towner={row["owner"] or "unknown"}\t{names}')
        print(f"Indicators on {len(findings)} pods")
    return 3 if args.fail_on_signal and findings else 0


if __name__ == "__main__":
    sys.exit(main())
