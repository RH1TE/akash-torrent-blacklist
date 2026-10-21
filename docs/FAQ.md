# Frequently asked questions

## Is BitTorrent illegal?

No. BitTorrent is a protocol. It has lawful uses, including software distribution. An infringement finding depends on what happened, the relevant rights and credible evidence. A provider can also prohibit particular traffic under its contract without claiming criminal activity.

## Why is a copyright complaint not enough?

A complaint commonly reports the datacentre's public IP. Behind that IP may be several customers and different NAT domains. Accurate tenant attribution needs contemporaneous technical records.

## Can the operator just block common ports?

That may reduce some traffic but will not reliably identify or stop all BitTorrent use. Clients can use random ports and encrypted tunnels. A broad firewall change can also disrupt legitimate game, VPN or backup services. Scope and test network controls separately.

## Why publish a wallet rather than an IP address?

Akash tenants are associated with on-chain wallet addresses and leases. Those are the relevant public identifiers. A node IP usually belongs to the hosting provider, while a gateway connection IP might belong to an intermediary service. Neither proves a person's identity.

## What if a wallet changes?

The registry has no identity graph and makes no attempt to link people across wallets based on speculation. A new wallet needs its own evidence.

## What does the approved list do by itself?

Nothing to production systems. Providers may download it and use it as a reference. Enforcement is a separate, optional local decision with overrides and rollback.

## Who accepts or declines a report?

RHITE LTD maintains the repository and records decisions. The case format asks for two distinct reviewers for acceptance. Public issue labels alone do not change the list.

## How long does a listing last?

Up to 180 days after approval. It must be re-reviewed or removed. New contradictory evidence can justify earlier correction.

## How do I appeal?

Use the GitHub appeal form and identify the case. Do not submit private information publicly. Explain the factual error or new evidence and the remedy requested.

## Are these detection scripts safe?

The Python tools read operator-supplied pod or flow files, or create a local hash manifest. The optional Kubernetes shell wrapper performs a pod export with the user's existing `kubectl` credentials. None of them closes leases, restarts nodes, writes firewall rules or bans a wallet.

## Why not copy the mining project's automatic eviction logic?

Torrent-related evidence has distinct attribution and rights questions. Automated disruption on keyword matches can punish legitimate workloads. This repository deliberately separates detection, investigation, review and enforcement.
