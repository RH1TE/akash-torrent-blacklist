# Accepted case record format

A case is an approved, reviewable explanation of why an Akash tenant wallet was added. The file name must match its ID, for example `AKT-2026-001.json`.

**Do not publish unreviewed allegations here.** An issue without an approved case record never enters either feed.

## Version 2

| Field | Type | Requirement |
| --- | --- | --- |
| `schema_version` | Integer | Exactly `2` |
| `id` | String | `AKT-YYYY-NNN` |
| `wallet` | String | Akash Bech32 account address with valid checksum |
| `chain_id` | String | `akashnet-2` |
| `dseqs` | List of strings | At least one verifiable deployment ID |
| `category` | String | `prohibited-p2p` or `attributed-infringement` |
| `provider_region` | String | Region, no private host identifiers |
| `provider_policy` | String | Applicable policy or finding basis, with dates |
| `observed_utc` | ISO UTC | Incident observation |
| `approved_utc` | ISO UTC | Human review approval date |
| `expires_on` | YYYY-MM-DD | Strictly future, maximum 180 days from approval |
| `reviewers` | List | At least two distinct GitHub reviewers |
| `issue` | GitHub issue URL | Existing report from this repository |
| `decision` | String | Concise supported reason for inclusion |
| `risk_notes` | String | Uncertainty and known false-positive limitations |
| `records` | List | Between three and twelve evidence summaries |

Each evidence record has `kind`, `source_id` and `summary`. Source IDs are opaque references to independently retained private originals. They are **not links** to a private log or the private media. Distinct source IDs must identify actual independent records, not copies of one log.

For `prohibited-p2p`: include independent kinds `deployment`, `runtime` and `policy`. For `attributed-infringement`: include `complaint`, `flow` and `deployment`.

A placeholder example is in [examples/case-example.json](../examples/case-example.json). It uses a **synthetic wallet** and is not an approved real entry. The schema checker ignores example files outside `cases/AKT-*.json`.

## Publish an accepted case

```bash
python3 tools/list.py build
python3 tools/list.py verify
python3 tools/list.py stats
python3 -m unittest discover -s tests -v
```

The generated `blacklist.txt` contains only wallet addresses. The generated `approved.json` includes category, expiry and case links. Do not edit either feed manually.

## Corrections

Remove or revise the case, regenerate both feeds and open a reviewed PR referencing the appeal. The history of the decision remains visible in the PR. Never leave a case approved after its supporting evidence or applicable policy has been withdrawn.
