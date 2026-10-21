# Practical investigation examples

For an actual provider investigation, see [RHITE October 2026 case study](CASE_STUDY_OCTOBER_2026.md). The scenarios below remain fictional test examples.

These examples are fictional. They use documentation network ranges and contain no real customer evidence.

## Case A: A suspicious pod with no infringement attribution

A routine pod inventory export shows a container image called `qbittorrent`, with an Akash owner and DSEQ label. The name scanner flags it.

**What we can say:** the tenant declared a BitTorrent client image, and its pod exists in the inventory. If a runtime record separately confirms execution and the provider's AUP disallows it, the provider may have enough evidence to consider a `prohibited-p2p` case.

**What we cannot say:** that it shared an unlawful file, connected to a particular tracker, or caused a complaint about a public IP. The pod might have legitimate content or might have crashed.

Action: preserve the original PodSpec and runtime evidence privately, verify applicable AUP, seek further information, and leave the public wallet feed unchanged until human review concludes.

## Case B: A complaint about a shared public IP

An upstream provider reports `203.0.113.10:42000` at `2026-01-15T12:00:00Z`. Two tenants were active on the node.

The report identifies the host, but no connection log maps source port 42000 back to either pod at the incident time.

**Result:** not attributable to either wallet. The operator can explain the investigation to the upstream provider, preserve the case and improve future network-flow retention. Neither tenant should be publicly labelled a confirmed infringer from this evidence.

## Case C: A preserved source NAT mapping

The same fictional complaint is accompanied by a precise destination tuple. The operator has a trustworthy flow record captured at the same UTC time that shows a source NAT translation from the public port to `10.42.0.42:53000`. The Kubernetes pod assignment and owner mapping were logged at that time.

Run the offline correlator with the public source IP, port, destination, protocol and timestamp. It returns a unique recorded tuple, subject to integrity and clock verification.

**Result:** a supported connection-level lead. Review the complainant's actual observation, tenant mapping and data provenance before claiming an infringement, and do not infer the identity of the wallet holder.

## Case D: Two possible matches

The source NAT table or flow export includes two records that could match the same reported tuple within the tolerance window. The tool reports `ambiguous_multiple_mappings` rather than choosing one by time proximity.

**Result:** the event remains unresolved. Request a narrower timestamp, destination address, connection ID or authenticated packet detail from the complainant.

## Case E: Behavioural anomaly but legitimate workload

A customer backup system opens many connections and uploads more than a gigabyte during a 15-minute period. The behavioural scanner flags the volume.

**Result:** a reason to review the traffic profile, not a reason to evict or blacklist the tenant. Keep baseline comparisons for content distribution, game services, media streaming, proxies and storage sync.

## Review and appeal

After a reviewer reaches a supported case finding, they open a PR containing a redacted case summary. The case includes source IDs, decision, category, reviewers and an expiry date. The list generator updates the feeds. An appeal can later narrow the finding or remove it entirely.
