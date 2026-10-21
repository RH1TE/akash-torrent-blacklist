# Akash Torrent Blacklist

Community-maintained intelligence for Akash providers dealing with unwanted BitTorrent workloads, peer-to-peer traffic and copyright complaints.

Maintained by RHITE LTD. This project is independent of Akash Network, Hetzner, other infrastructure providers and rights holders.

**This is not a list of people accused of piracy.** It is a record of reviewed observations tied to Akash tenant wallets. A BitTorrent client can have legitimate uses. Each provider sets its own acceptable use policy, investigates its own traffic and decides whether an entry is relevant.

## Why this exists

A copyright complaint will normally identify a public IP, a timestamp and an observed source port. An Akash worker can have several unrelated workloads behind that IP. A tenant can also terminate a lease before the operator receives the notice. The address in the notice identifies the host, not necessarily the workload.

Operators need to answer four questions before acting:

1. Which leases and pods were running on the worker at the reported time?
2. Can the reported network connection be traced through source NAT to a particular pod?
3. What does the evidence establish about the workload, as distinct from the complainant's claim?
4. What action is justified under the provider's own terms, and what should be shared with other operators?

This repository provides a common reporting standard and practical scripts for the first stages of that process. The [mining blacklist maintained by jjozzietech](https://github.com/jjozzietech/akash-miner-blacklist) is a useful example of community reporting with honest provenance. Torrent cases require a different standard because identifying a client or port does not establish infringement.

## Contents

| Path | Purpose |
| --- | --- |
| [blacklist.txt](blacklist.txt) | Approved tenant wallets, one per line |
| [approved.json](approved.json) | Same approvals with category and case references |
| [cases](cases) | Public reviewed case records, with source summaries |
| [rules/indicators.json](rules/indicators.json) | Maintained workload indicators and rationale |
| [tools/scan_pods.py](tools/scan_pods.py) | Read-only scanner for Kubernetes pod inventory |
| [tools/correlate_flows.py](tools/correlate_flows.py) | Offline public-to-private NAT flow correlation |
| [tools/scan_flows.py](tools/scan_flows.py) | Behavioural screening of flow metadata for unusual fan-out or egress |
| [scripts/scan-kubernetes.sh](scripts/scan-kubernetes.sh) | Read-only local cluster collection and indicator report |
| [tools/evidence.py](tools/evidence.py) | SHA-256 manifest for a local, private evidence folder |
| [tools/list.py](tools/list.py) | Strict case validator and feed generator |
| [tools/update_feed.py](tools/update_feed.py) | Download and validate a reviewed feed into an atomic local cache |
| [tools/provider_check.py](tools/provider_check.py) | Opt-in wallet check for provider bid scripts |
| [docs/DETECTION.md](docs/DETECTION.md) | What indicators mean, how to tune them and when not to block |
| [docs/BEHAVIOURAL_SCREENING.md](docs/BEHAVIOURAL_SCREENING.md) | Traffic analysis thresholds and false positive controls |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System components, trust boundaries and workflow |
| [docs/INCIDENT_RESPONSE.md](docs/INCIDENT_RESPONSE.md) | Copyright complaint investigation and response procedure |
| [docs/FLOW_ATTRIBUTION.md](docs/FLOW_ATTRIBUTION.md) | SNAT, pod identity, clock accuracy and evidence limitations |
| [docs/PROVIDER_INTEGRATION.md](docs/PROVIDER_INTEGRATION.md) | Deployment patterns, logging, rollback and examples |
| [docs/OPERATIONS.md](docs/OPERATIONS.md) | Monitoring, schedules, retention and maintenance |
| [REVIEW.md](REVIEW.md) | The evidence threshold for publication |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to submit or review reports |
| [SECURITY.md](SECURITY.md) | Privacy, threat model and vulnerability handling |

## The two categories

**prohibited-p2p** means a provider can substantiate that a P2P workload ran under a particular tenant lease and breached a specific policy that applied at the time. It does not mean that copyright infringement was proven.

**attributed-infringement** requires an external infringement observation **and** reliable technical attribution of the observed session to that lease. A public IP, a similarly timed deployment and an image named `torrent-worker` are not enough on their own.

Reports that do not reach either standard stay in triage. The reviewer records missing evidence and can reject the report. We do not add wallets because another list contains them or because a report is popular.

## Operator quick start

The tools use Python 3.11 or later and its standard library. No agent, cluster administrator role or new Python package is needed for offline checks.

```bash
git clone https://github.com/RH1TE/akash-torrent-blacklist.git
cd akash-torrent-blacklist

python3 -m unittest discover -s tests -v
python3 tools/list.py verify

# Read-only: inspect a pod-list JSON file already exported from your cluster.
python3 tools/scan_pods.py --input examples/pods.json --format table

# Match a reported network tuple against preserved NAT events.
python3 tools/correlate_flows.py \
  --flows examples/flows.jsonl \
  --public-ip 203.0.113.10 --public-port 42000 \
  --protocol tcp --at 2026-01-15T12:00:00Z

# Build a private integrity record. Do not commit its output or source files.
python3 tools/evidence.py manifest --dir /path/to/incident-folder \
  --out /path/to/restricted-storage/manifest.json
```

For your own cluster, collect the **necessary metadata only**, for example:

```bash
kubectl get pods -A -o json > /restricted/pods-snapshot.json
python3 tools/scan_pods.py --input /restricted/pods-snapshot.json
```

The scanner does not contact a cluster or inspect file contents. It raises candidates for review. It does not evict tenants, change firewalls, close leases or update the public feed. See [detection limitations](docs/DETECTION.md).

## How the public list works

1. [Open a report](https://github.com/RH1TE/akash-torrent-blacklist/issues/new/choose) describing the Akash wallet, lease, time window and observed behaviour.
2. Maintainers review the evidence, ask for missing records where necessary, and check the relevant provider policy.
3. An accepted report is represented by a case JSON file in `cases/`. Rejected reports are closed with an explanation. They do not enter the list.
4. The reviewer regenerates both feeds using `python3 tools/list.py build`, then opens a PR.
5. Automated checks validate the case and compare the checked-in feeds to the approved case records. Code-owner review is required before merge.
6. The listing expires unless reviewed again. Anyone can [appeal or request a correction](https://github.com/RH1TE/akash-torrent-blacklist/issues/new/choose).

The list starts empty. No private RHITE incident material or unreviewed wallet has been published here.

## Using the feed at a provider

There are two reasonable approaches.

**Reference only:** download the public list, read its case records and decide whether each entry applies to your AUP. This is the recommended starting point.

**Opt-in local denial:** cache an approved feed, keep explicit local overrides, run a dry-run check, then call the local wallet checker from the bid script only after testing it. Never fetch a remote list during bid pricing. The scripts provided here deliberately require a conscious `--enforce` flag before returning a denial.

See [provider integration](docs/PROVIDER_INTEGRATION.md) for a working example. This repository is not a substitute for host firewall isolation, session mapping, operational monitoring or legal advice.

## Evidence quality

| Evidence available | Reasonable conclusion |
| --- | --- |
| Torrent keyword in pod/image | Lead worth investigating |
| Torrent client process confirmed in pod | P2P workload operated |
| On-chain DSEQ linked to that pod | Tenant wallet identified for the workload |
| Notice identifying shared node IPv4 and source port | Complaint about node, not necessarily tenant |
| Preserved SNAT translation matching source port, timestamp and peer | Network session attributed to pod, subject to clock and log integrity |
| Infringement notice and attributable peer session | May justify reviewed `attributed-infringement` finding |
| No session data, but strong workload and AUP evidence | May justify only `prohibited-p2p` |

Read [the review policy](REVIEW.md) for the precise acceptance requirements and [the incident playbook](docs/INCIDENT_RESPONSE.md) for source preservation.

## Project status

The reporting format, validators and inspection tools are available. There are currently no public approved cases. The examples use documentation-only network addresses and synthetic data. Nothing in this repository automatically modifies production Akash infrastructure.

Contributions, corrections and review requests are welcome. RHITE LTD maintains the list and records the reason for each decision.

Licensed under MIT. See [LICENSE](LICENSE).
