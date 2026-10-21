# Detection guide

The aim is to identify workloads requiring investigation without treating every torrent-related string as an infringement finding.

## Detection vectors

| Signal | How it is collected | Strength | Common failure |
| --- | --- | --- | --- |
| Name/image indicator | Kubernetes PodSpec | Low to medium | A legitimate tool or misleading name |
| Explicit executable and args | Kubernetes PodSpec | Medium | The process may not start, or may be renamed |
| Runtime process from tenant cgroup | Container runtime | Medium to high | Process names may be altered |
| Well-known peer port | Service or socket snapshot | Low | Other protocols can share the port |
| Tracker or peer negotiation | Consent-authorised network sensor | Medium | Encryption and NAT hide detail |
| High connection fan-out | Aggregated flow metadata | Medium | CDN or game workloads may resemble it |
| Completed egress NAT tuple | Flow/conntrack records with owner at time | High for session attribution | Clocks, NAT reuse, missing logs |
| Copyright notice | Provider's abuse inbox | Evidence of allegation | Source IP may be NAT shared |

A detector should produce a *lead*, not an automatic public accusation. Avoid generic keywords such as `seed`, `download` or `peer` without more context. An image called `transmission` is worth checking; it is not proof that an unlawful copy was shared.

## Pattern scanner

`tools/scan_pods.py` reads `kubectl get pods -A -o json` from a file or standard input.

It examines pod, container and init-container names, image references and declared commands. It checks only fields needed for classification. It does not read secrets, mounted disks, kubeconfigs or the rest of the host.

A result contains: namespace, pod, node, wallet label when present, DSEQ when present, image, matched indicator, configured severity and an explanation. Missing labels are reported as missing rather than inferred from an unrelated IP.

The scanner's `--fail-on-signal` option is useful in a local CI audit but does not implement blocking. The normal exit code is zero when input is valid, even if indicators are found.

### Tuning

Curated indicators live in `rules/indicators.json` with a unique ID, case-insensitive regular expression, severity, description and allowed fields. A new rule must include a false-positive explanation and tests.

Run scanners against known legitimate deployments before modifying your admission controls. Store raw pod exports locally, not in public GitHub issues. Short output windows and explicit namespace selection reduce unnecessary collection.

## Behavioural signals

The companion `tools/scan_flows.py` can inspect saved per-pod flow summaries for unusual egress or peer fan-out. See [behavioural screening](BEHAVIOURAL_SCREENING.md). Relevant signals include: concurrent peers, sustained upload rate, outbound connection fan-out, and DNS or SNI metadata where appropriate and lawful. Each signal needs thresholds calibrated to a provider's customer mix. Persistent traffic alone can be legitimate, especially for VPN, backup, streaming or gaming applications.

Do not claim that a high port count or traffic volume proves BitTorrent. There should be a documented process for someone to correct the attribution.

## What the scripts deliberately do not do

- No automatic namespace deletion, lease closure, wallet ban or DNS blocking.
- No deep packet capture, copyrighted payload storage or intrusive content inspection.
- No scanning of unrelated host files.
- No guessed public client identity from cloud addresses seen at a provider gateway.
- No universal assumption that P2P software breaches an AUP.

For enforcement, follow [incident response](INCIDENT_RESPONSE.md), verify the local AUP and obtain human approval before disrupting a tenant.
