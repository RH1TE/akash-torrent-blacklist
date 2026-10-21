# Security

Please report vulnerabilities in the registry code using GitHub's private vulnerability reporting feature, if enabled, rather than an ordinary public issue. Do not include credentials, private customer logs or traffic payloads in an issue.

## Trust boundaries

Unreviewed GitHub issues are untrusted input. They never automatically populate `blacklist.txt`. The registry cannot establish the person controlling a wallet. It cannot establish illegality solely from a process name, image, port or traffic graph.

The working tools are designed to operate offline or read a specific provided JSON file. No detector closes leases, evicts pods, runs privileged host commands or posts evidence anywhere. Sensitive inputs should remain inside restricted operator storage.

## Consumer safety

`tools/update_feed.py` performs bounded downloads and validates the checksum or wallet data before atomically replacing the cache. Operators should pin a trusted Git commit and sha256 digest when using data for denial. `tools/provider_check.py` has a dry-run mode and explicit enforcement switch.

No public report should contain a residential IP address, private NAT records, usernames, download filenames, media content, confidential cloud diagrams, key material or full raw third-party notices. Public Git history may retain removed data, so reviewers must inspect a diff **before** merging.

## Limits

A valid wallet checksum and passing unit tests do not prove a case is true. Maintainers need direct evidence review and a reasoned finding. Review protection on GitHub is not a substitute for careful review of claims and personal data.
