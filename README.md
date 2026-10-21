# Akash Torrent Blacklist

A community-maintained list of Akash tenant wallets linked to torrent-related abuse reports.

This project is run by RHITE LTD. It gives hosting providers a place to share evidence, compare incidents and make informed decisions about their own customers. It does not decide whether someone has broken the law.

**A report is not a blacklist entry.** Every submission is reviewed before a wallet is added. Maintainers can accept a report, request more information or decline it.

## What is in the repository?

- [blacklist.txt](blacklist.txt): approved Akash tenant wallets, one per line
- [cases](cases): public summaries explaining each approved entry
- [Report an incident](../../issues/new/choose): submit an evidence-backed report
- [Review guidelines](REVIEW.md): how reports are checked and decisions made
- [Appeals](../../issues/new/choose): request a correction or removal

The list starts empty. We are not publishing wallet addresses from an unresolved incident simply because they appeared in a complaint.

## Reporting an incident

Open an issue using the report form. Include the Akash tenant wallet, the deployment ID, the UTC incident window, the behaviour observed and the evidence that links the activity to the wallet.

Useful evidence includes deployment records, container logs, traffic records and abuse notices. A complaint about an IP address shared by several tenants is not enough to identify a particular wallet without supporting technical evidence.

Do not upload raw access logs, personal IP addresses, keys, copyrighted files or unredacted complaints. Describe sensitive evidence in the issue and arrange a private review where necessary.

## How entries are approved

1. A maintainer checks the wallet and deployment history.
2. The evidence is assessed against the [review guidelines](REVIEW.md).
3. The report is accepted, declined or left open pending evidence.
4. For accepted reports, the maintainer adds a case summary through a reviewed pull request.
5. Automated checks verify the data and rebuild the plain-text list.

The issue remains available for discussion, corrections and appeals. Removal requests are considered on their merits.

## Using the list

Providers can read or download [blacklist.txt](blacklist.txt). There is also a simple [validation tool](tools/list.py).

```bash
curl -fsSL https://raw.githubusercontent.com/RH1TE/akash-torrent-blacklist/main/blacklist.txt -o blacklist.txt
python3 tools/list.py verify
```

**Always review entries before enforcing them.** A wallet may have been restricted under one provider's terms while remaining acceptable under another's. Keep a local override and a way to reverse a block.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a report.

Maintained by RHITE LTD. Not affiliated with Akash Network or any upstream hosting provider.
