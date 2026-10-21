# Case review standard

The public list is useful only when operators can explain why an entry was added. An unsupported wallet address is a liability for everyone using the feed.

## Intake is not publication

Any operator can open a report. A maintainer checks the evidence before accepting it. The issue may be labelled `needs-review`, `needs-evidence`, `accepted`, `declined` or `appeal`. These labels record the process; they do not change the public list.

Only case records in `cases/AKT-YYYY-NNN.json` generate entries in `blacklist.txt` and `approved.json`. A reviewer records the decision, references an actual issue, documents the reason and obtains independent review before the PR is merged.

## Evidence requirements by category

### prohibited-p2p

This category requires:

1. **Deployment attribution:** a verifiable tenant wallet and lease, including DSEQ, observation timestamp and namespace/pod relationship.
2. **Runtime observation:** evidence that the P2P workload ran, rather than an image tag that was merely proposed or never started. A process record, relevant runtime log or independently verified CNI/service activity may help, but record precisely what was observed.
3. **Provider policy:** an applicable, date-valid AUP clause that prohibited the observed workload on that provider. A provider with no such clause cannot borrow another provider's policy to claim a breach.

It does **not** mean copyright infringement has been established. A running torrent client may distribute licensed, public domain or otherwise lawful material.

### attributed-infringement

This category requires:

1. An infringement **complaint** with a date, source public IP:port and enough detail to distinguish the incident.
2. An authenticated historic **flow or session record** matching the reported connection to a private workload and lease at the stated time, including protocol and NAT details where applicable.
3. Independent **deployment attribution** linking that workload to the on-chain tenant wallet.

If the reporter's notice omits the destination tuple, or only the node's source IP is known, reviewers must describe the limitation. A matching time and a torrent-labelled image are insufficient for this category.

## Minimum provenance for public approval

Every accepted case must contain the on-chain DSEQ, UTC observation and approval times, a valid Akash wallet checksum, two distinct human reviewer usernames, provider region, the provider's relevant policy or basis for the finding, a short decision and risk note, and at least three independent evidence records. Record source IDs in the private evidence register. The public record contains only opaque IDs and summaries.

For `prohibited-p2p`, the required kinds are `deployment`, `runtime` and `policy`. For `attributed-infringement`, they are `complaint`, `flow` and `deployment`. Repeated copies of the same single log are not independent observations.

The validator checks record structure, wallet checksum, allowed kinds and expiry. **It cannot validate the truth of the evidence or confirm that named reviewers actually approved the PR.** The maintainer must check that manually against the GitHub audit trail.

## Cases to decline or keep open

- The only evidence is a third-party blocklist or an unverified Discord message.
- The reported IP is shared but there is no tenant mapping.
- The wallet was guessed from a public provider gateway client address.
- A service exposes a familiar P2P port but there is no evidence the protocol ran.
- The image name contains the word `torrent` but the process never executed.
- The provider terms are missing, do not apply to the lease or allow the activity.
- The public summary reveals identifiable details or confidential infrastructure.
- The issue does not record uncertainties or alternative explanations.

Ask for additional evidence where it might become available. Otherwise decline with a concise explanation. Do not leave a disputed allegation on the list because removing it is inconvenient.

## Publication and expiry

A case may remain listed for no more than 180 days after acceptance without another review. The CI check rejects expired entries so they cannot remain silently in the generated feed. Corrections and renewed reviews must identify the case and use a PR.

A second independent reviewer should approve each accepted case. A technical reviewer and a provider policy reviewer can be different people, but reviewers should recuse themselves when they have a material conflict.

## Appeals

A tenant, provider or other affected party can submit an appeal. The reviewer checks new information, gives a reasoned outcome and prepares a correction or delisting PR if necessary. A credible urgent false positive can be removed immediately through a reviewed correction. Cases should be referred to another reviewer where there is a conflict of interest.

The project is not a dispute-resolution court. No public case record should disclose a subscriber's identity, residential IP, media download history or private credentials.
