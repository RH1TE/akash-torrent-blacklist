# Case study: two short-lived P2P workloads behind one provider IP

**Incident period:** October 2026  
**Prepared by:** RHITE LTD, infrastructure operations  
**Status:** Investigated, no public wallet listing approved  
**Scope:** Evidence handling, tenant attribution and prevention  
**Identification:** Tenant wallet, deployment IDs, node IP and complaint identifiers deliberately withheld from this public account

This is a real RHITE Akash provider incident. It is not a simulated detection case. We have changed or withheld identifying data that is not needed to explain the methods. The technical conclusions reflect retained host records and reported complaints, while the specific copyright allegations remain unverified by our own connection evidence.

## Incident summary

An upstream datacentre forwarded two copyright-related BitTorrent reports concerning one public IPv4 address on our Akash worker. The reports referred to different alleged content files, different outbound source ports and separate observation times within roughly half an hour.

That public IP also provided internet access for independent tenant workloads and a separate virtual machine. We could not identify the source of either connection from the public IP alone.

During a targeted review of retained K3s journals, we found two short-lived deployments with the service name `torrent-worker`. Both were associated with the same Akash tenant wallet. Each began running shortly before one of the datacentre's observations.

The association was significant enough to warrant containment and further investigation. It did not, by itself, demonstrate that either reported copyrighted file was present in the workloads or transferred by them.

## What the records showed

| Evidence | First deployment | Second deployment |
| --- | --- | --- |
| Pod/service label | `torrent-worker` | `torrent-worker` |
| Lease ownership | Same on-chain tenant wallet | Same on-chain tenant wallet |
| Startup relative to complaint | About 2 minutes before | About 2.5 minutes before |
| Runtime status at time of complaint | Pod running | Pod running |
| Lease status when investigated | Already closed | Already closed |
| Closure source | Tenant owner | Tenant owner |
| Public source-port mapping | Not retained | Not retained |
| Alleged media file confirmed on host | No | No |

The names and service metadata indicated a torrent-related workload. Kubernetes networking logs also showed the first deployment exposing TCP services on common torrent client ports, including **9091** and **51413**, and associated Kubernetes NodePorts. These were *service* ports and did not match or prove the datacentre's claimed outbound NAT source ports.

## How we linked the leases

We used three independent areas of evidence.

**Kubernetes journals:** retained worker-node messages showed the pod startup times, namespace references and declared workload names.

**Akash lease history:** the public chain supplied tenant ownership, deployment sequence numbers and creation and closure events. We matched the namespace identifiers to the same Akash owner using the provider's deterministic namespace mapping. We did not infer ownership from a public gateway visitor's address.

**CNI and control-plane logs:** Calico and separate control-plane journals independently recorded private pod IP allocations and service creation. These records supported the runtime timeline rather than merely showing a scheduled deployment.

The original timestamps, raw logs, on-chain proofs and checksums remain in restricted internal storage. None were uploaded to this repository.

## What we tried to establish

The critical missing evidence was the historical source NAT translation. To conclusively connect the reported BitTorrent session with one of the pods, we needed a record linking:

- The public source IP and source port described by the complainant.
- The remote destination IP and destination port.
- The protocol and observation time, allowing for known clock drift.
- The private pre-NAT pod IP and source port.
- The pod UID, namespace and the lease owner at that time.

Our host did not retain that historical mapping. A current conntrack snapshot could not recover it after both deployments closed. The external notices did not supply a complete destination tuple or packet capture for our own independent verification.

We also reviewed available Ceph metadata and Kubernetes control-plane snapshots. The suspect deployments had requested default short-lived storage, and no matching retained persistent volume or overlapping etcd snapshot was found. There was no recovered copy of either alleged media file.

These limitations prevent us from claiming a specific copyrighted transfer as proven.

## Attribution assessment

| Claim | Assessment |
| --- | --- |
| Two torrent-labelled tenant workloads ran | Supported by retained Kubernetes and network records |
| Both workloads belonged to the same tenant wallet | Supported by deterministic namespace matching and chain records |
| Each startup was closely followed by a separate complaint | Supported by independently recorded timestamps |
| The workloads used recognised torrent-related service ports | Supported by Kubernetes service and networking configuration |
| The complaint's outbound source ports belonged to these pods | Unresolved, no historical NAT record |
| The complained-of media files were stored or distributed by the pods | Unresolved, no file or session proof |
| The tenant's real-world identity or residential IP is known | Not established |

A repeated temporal association is stronger than one suspicious label, but does not repair a missing network attribution record.

## Local response

Our immediate response separated tenant containment from public publication.

The implicated leases had already closed. We added a **local Kubernetes namespace admission block** for the identified tenant wallet, with a server-side test confirming rejection of that wallet and acceptance of an unrelated tenant. We also deployed a tenant-scoped admission policy that rejects selected high-confidence torrent client image and startup identifiers. Tests confirmed that a matching torrent-labelled pod was denied and an ordinary web pod was allowed.

An additional wallet denial was staged in our bid pricing configuration. At the time of the incident response, the running provider had not refreshed that projected script, so we did not describe bid-layer enforcement as fully verified. We did not apply an untested blanket egress firewall rule, and no customer pods were evicted for this investigation.

These local operational actions are not evidence that a copyright allegation was proven.

## Public blacklist decision

**Not listed at this stage.** We know the wallet linked to the two workloads, but we have not independently confirmed that a relevant RHITE acceptable use policy prohibited the specific P2P workload at the time of the incident. We also lack the source NAT and peer-session evidence required for an `attributed-infringement` classification.

A verified policy and contemporaneous runtime evidence could support a narrower `prohibited-p2p` case after review. A definitive infringement listing would need stronger session attribution. Neither decision is automatic, and the affected party can appeal any future public entry.

The wallet itself and the exact deployment IDs are held in the private case file. We do not publish an unreviewed wallet merely to populate the community blacklist.

## Lessons for other providers

**Retain short-lived mappings.** A 7 to 14 day, access-controlled record of source NAT mappings and pod identity would materially improve an investigation that arrives hours later. Capture public and private tuples at connection time, not after receiving a complaint.

**Keep clocks aligned.** Record timestamps in UTC and monitor NTP drift. The difference between a pod startup and an observed peer connection may be only a few minutes.

**Preserve before cleaning up.** Targeted K3s, CNI and control-plane logs can outlive a tenant lease. Hash originals, avoid altering production storage, and record what is missing.

**Do not confuse client metadata with a specific transfer.** A torrent-labelled container image, TCP 51413, a peer-style process and a datacentre complaint each establish different things. Record those limits.

**Separate local enforcement from publication.** A provider can restrict a tenant under its own risk policy while still withholding the wallet from a public shared list pending impartial review.

## Related guidance

See [Incident response](INCIDENT_RESPONSE.md), [Flow attribution](FLOW_ATTRIBUTION.md), [Detection](DETECTION.md), [Public review standard](../REVIEW.md) and [Evidence handling](../tools/evidence.py).

*This case study describes investigated infrastructure activity, not a legal conclusion about any person or the content they accessed.*
