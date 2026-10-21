# Behavioural traffic screening

The name scanner finds obvious client labels. Some workloads use generic container names or install a P2P client after startup. Network patterns can provide another lead, but traffic volume and connection fan-out are not proof of BitTorrent.

## Input

`tools/scan_flows.py` reads a previously captured JSONL file in operator-controlled storage. Each record should have:

- `at`: UTC timestamp
- `namespace` and `pod`: identity recorded at the event time
- `owner` and `lease_dseq`: optional tenant mapping from authenticated lease labels
- `dest_ip`: destination peer address, used only locally for counting unique peers
- `bytes_out`: observed egress bytes in the record, if available

If the data lacks tenant identity or was not collected at the connection time, keep the result as a host-level anomaly. Do not infer owner from an IP address assigned hours later.

## Example

```bash
python3 tools/scan_flows.py \
  --flows /restricted/flows.jsonl \
  --end 2026-01-15T12:15:00Z \
  --minutes 15 \
  --min-peers 60 \
  --min-egress-bytes 1000000000
```

The tool screens a 15-minute window and emits only pods exceeding at least one threshold. It prints counts and pod identity, not the individual peer addresses.

## Practical thresholds

Tune thresholds against actual legitimate tenant traffic. A game server, content distribution job, backup or proxy can exceed hundreds of connections and several gigabytes of traffic. Start with alerting only and compare false positives over a week or longer. Stronger evidence may include protocol-specific logs or a correlation with an external abuse notice.

The scanner does not create flow records, inspect payloads, trigger network changes, evict workloads or add wallets to a public list. It has no dependency on root SSH or Kubernetes administrator access.

For source-port attribution, use [the NAT mapping guide](FLOW_ATTRIBUTION.md) and [correlator](../tools/correlate_flows.py). Do not collapse a traffic-anomaly score into a claim that copyrighted files were shared.
