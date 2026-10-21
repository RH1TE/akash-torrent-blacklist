# Contributions

This repository is built around operator evidence rather than screenshots circulating between servers.

## Submit a report

Use the [report form](https://github.com/RH1TE/akash-torrent-blacklist/issues/new/choose). Describe the incident in UTC, include the tenant wallet and DSEQ, explain the behaviour observed and provide a policy reference when one is relevant.

If you have evidence from your own worker, explain the source and observation time. Suitable sources include on-chain lease records, saved Kubernetes pod and CNI logs, a preserved process record or retained network flow mapping. An upstream copyright notice is a report of an observation, not proof of source pod attribution.

Do not upload a full `kubectl get pods -A -o json` output, raw nft/conntrack logs, private public-to-pod IP mappings, personally identifying information, media titles and hashes, keyrings, access tokens or the entire infringement notice. Keep originals in controlled storage. Public issue comments should contain only sanitised summaries.

Reporters must state the gaps. If you only know that a torrent-labelled container appeared just before an infringement complaint, record it as a lead for investigation.

## Review process

1. The report is triaged and checked for private information.
2. Reviewers verify ownership, DSEQ, timestamps, runtime evidence and the provider's AUP.
3. The report is accepted, declined or held for more evidence. Reasons are recorded.
4. Only accepted reports become case JSON records. Use [the format guide](cases/FORMAT.md).
5. Run `python3 tools/list.py build`, then `python3 tools/list.py verify` and the full test suite.
6. Open a PR linked to the original issue and have another reviewer check it.
7. Publish the decision by merging the reviewed PR. Unaccepted reports do not appear in the feed.

## Update detection indicators

The [indicator rules](rules/indicators.json) are a human-review scanner configuration, not a ban policy. A new rule needs a descriptive ID, exact matching pattern, severity, rationale, fields to inspect and a realistic false-positive example.

Include a positive fixture that detects the intended case and a negative fixture that proves a legitimate name will not be flagged. Changes should not introduce generic word matching that incorrectly identifies every media server, downloader, seed database or networking tool.

## Fix a mistake

Use the [appeal template](https://github.com/RH1TE/akash-torrent-blacklist/issues/new/choose) or a correction PR referencing the existing case. Give concrete new information and request a remedy. The public feed is regenerated after an approved removal or reclassification.

## General expectations

Make a claim no stronger than the evidence supports. Be civil and specific. Avoid personal identification, threats, guesses about geography and statements that BitTorrent use is automatically illegal.

Maintainers may reject unreliable or privacy-invasive contributions. All public code changes need CI and code-owner review. RHITE LTD keeps authority over the published registry but will record decisions and corrections.
