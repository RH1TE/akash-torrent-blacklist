# System design

The toolkit has separate stages so a reporting mistake cannot immediately become a production ban.

## Detection

**Inventory scanner:** The operator exports an explicit `kubectl get pods -A -o json` snapshot and runs the local scanner. Rules match named fields and produce review candidates. The scanner never queries a live cluster unless an operator separately runs the optional shell wrapper.

**Traffic screening:** Saved network-flow metadata can be screened for connection fan-out and sustained egress. This produces anomalies rather than findings. No raw peer IPs are published.

**Incident correlation:** A preserved NAT mapping can be compared against a complainant's public source port and timestamp. Records with incomplete destinations remain candidates; multiple possible matches produce an ambiguous result.

## Investigation

The operator follows `docs/INCIDENT_RESPONSE.md`, preserves evidence with `tools/evidence.py`, checks lease and namespace mapping and verifies relevant policy terms. Confidential evidence remains in restricted operator storage.

## Community review

A contributor submits a sanitized GitHub issue. Reviewers can accept it, reject it or request more evidence. Only a reviewed case JSON file in a PR can generate a feed entry. The case validator requires supporting evidence kinds, an expiry date, reviewers and valid wallet addresses.

## Publication

`tools/list.py build` generates both `blacklist.txt` and `approved.json`. CI compares those files to the approved case records, runs the tests and rejects obvious private artefact paths. A code-owner reviews case additions. There is no API, database, account signup or automated ban service.

## Consumption

Operators download a reviewed feed into an atomic cache with optional SHA-256 pinning. They compare the list against their own AUP and local overrides. A local wallet checker defaults to dry-run. Enforced denial is a separate operator choice and uses an explicit flag and distinct exit code.

## Threat model

Consider false reports, impersonated on-chain owners, source NAT ambiguity, timestamp drift, malicious PR modifications to tests, poisoned public feeds, forged reviewer names, and disclosure of personal data. No individual control fully mitigates these threats. Human independent verification, case expiration, code-owner review, restrictions on publication and opt-in consumer integration are all necessary.

All hosted test fixtures use invented traffic data. The project does not ship the RHITE incident archive or its wallet as a public listing.
