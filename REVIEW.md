# Reviewing reports

We publish observations that another provider can evaluate, not accusations about the person controlling a wallet.

## Evidence

An accepted report must identify:

- An Akash tenant wallet and deployment ID that can be checked against network records.
- A clear UTC observation window.
- The behaviour reported, with enough technical detail for another operator to understand it.
- At least two relevant supporting records, with the limits of each explained.
- The provider policy involved, when the issue is a breach of hosting terms.

An abuse notice is useful evidence that a complaint was made. It does not by itself prove which workload produced the traffic. Pod names, torrent-related ports and timestamps can support an investigation, but do not establish a specific copyright infringement on their own.

## Categories

**prohibited-p2p**: a hosted P2P workload is supported by deployment or runtime evidence and conflicts with the reporting provider's applicable terms. This category is not a finding of copyright infringement.

**attributed-infringement**: a copyright complaint is supported by technical records tying the reported network session to the specific Akash tenant. A shared host IP and nearby deployment time are not sufficient.

Using BitTorrent is not inherently unlawful. We do not publish claims about a wallet holder's identity, home address or geographic location.

## Decision process

Each report receives one of these outcomes:

- **Needs evidence**: relevant records are missing or attribution is uncertain.
- **Accepted**: a maintainer has reviewed the evidence and documented the finding.
- **Declined**: the claim is unsupported, out of scope or does not meet the standard.

Accepted entries are added through pull requests. We require an approving code-owner review and a passing data check before merging. A contributor cannot add a wallet to the published list by opening an issue.

Cases have a review expiry date, no later than 180 days after acceptance. Entries are removed unless reviewed again with current evidence.

## Corrections and appeals

Anyone can challenge a case using the appeal form. We review new evidence and correct or remove unsupported listings. The reason for each decision is recorded in the issue or pull request.

Do not post identifying or confidential material in public GitHub comments. Contact the maintainers through an appropriate private channel if evidence needs restricted handling.
