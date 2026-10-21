# Incident response for copyright and P2P complaints

Use this procedure when an upstream datacentre reports BitTorrent traffic from an Akash worker. The clock starts when the notice is received, not when the investigation is convenient.

## 1. Register and preserve

Log the datacentre ticket reference, receiving mailbox, response deadline, reported public IP and port, UTC observation time, transport, reported file or infohash and complainant case identifier. Keep the **original notice privately**, including full headers, without reposting the notice or media title on GitHub.

Create a case directory with restricted permissions. Record who accessed evidence and the acquisition time. Collect a file hash inventory with `tools/evidence.py`. Avoid writing sensitive records to a shared knowledge index or public issue.

Acknowledge the notice within the datacentre's required timeframe, including what is confirmed, what remains unknown and what you have changed. An acknowledgement does not imply guilt.

## 2. Identify the public IP owner

Use the datacentre account to map the reported public IP to a dedicated server, cloud VM, assigned routed subnet and observation time. Note any services sharing the address, including tenant pods, game VMs, proxies and NAT.

Take a snapshot of current firewall/NAT and conntrack configuration read-only. A **current** connection list cannot prove the historical connection existed. If the operator did not retain old flow logs, record that gap explicitly.

## 3. Reconstruct the tenant window

Use the UTC observation time and a narrow margin for log clock drift. Search targeted K3s journals on the suspected worker and control-plane nodes for:

- Namespace create/update/delete events.
- Pod start and stop timestamps, UID and internal IP assignment.
- Service ports and container image or command metadata.
- DSEQ/owner namespace labels and on-chain Akash lease creation/closure.

Verify the deterministic namespace-to-lease mapping rather than assuming a client IP belongs to a tenant. Make a timeline with independent clocks and source references.

**Never restore the live etcd database to inspect an old tenant.** Inspect offline snapshots only after evaluating recoverability and operational risk.

## 4. Match the network event

A convincing packet/flow association needs the complainant's public observed five-tuple (public source IP:port, destination IP:port and protocol) at time T, plus a preserved source NAT record identifying private pre-NAT source IP:port and pod identity at T. Match time zones, clock error margins, protocol and port reuse.

Run `tools/correlate_flows.py` on a validated local flow export. It rejects ambiguous multiple matches rather than selecting the nearest at random. **No NAT records** means **no source-port attribution**. A pod name, 51413 service or a close timestamp does not fill that gap.

Ask the reporter for missing peer/destination and BitTorrent handshake data through the datacentre. They may not hold it. Avoid speculative statements about a tenant's residential IP.

## 5. Determine a justified response

A provider may find a P2P workload that violates its own terms without establishing that the reported content was shared. Conversely, a complaint may be incorrectly attributed to a different tenant or service.

Document the narrower supported finding first. Preserve workloads when possible, but act promptly on verified abuse consistent with contractual terms and lawful obligations. Avoid broad firewall rules that impact Wings, other games, or unrelated paying customers.

If a wallet is locally denied, record the evidence, scope, expiration and rollback. A **local** provider ban does not automatically justify a **public** community listing.

## 6. Notify Hetzner or other upstream

Respond through the specified authenticated channel before the deadline. Include the host/server reference, distinct incident times and ports, verified lease ownership if established, steps completed, and outstanding evidence requests. Never claim a firewall rule was enforced if it was only staged, or a bid denial is effective if the pricing script mount is stale.

Ask what the datacentre needs to keep the service operational. A report in this public repository does not count as a response to the datacentre.

## 7. Close out

Secure evidence, add an incident runbook, record control improvements and review whether flow metadata retention would have shortened attribution. Use a human review path for any proposed public wallet listing. Reassess the retained case after 30, 90 and 180 days.

## Response checklist

- [ ] Verify deadline and acknowledge receipt
- [ ] Map public IP to machine and NAT domains
- [ ] Preserve original complaint and relevant targeted logs
- [ ] Build UTC tenant lease and pod timeline
- [ ] Look for a recorded source NAT translation
- [ ] Keep confirmed facts distinct from complainant claims
- [ ] Verify impact of any mitigation and its rollback
- [ ] Submit the upstream statement before the deadline
- [ ] Consider public submission only after review and redaction
