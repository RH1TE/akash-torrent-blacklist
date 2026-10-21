# Case record format

One file per accepted report, named `AKT-YYYY-NNN.json`. Do not create a case record for an allegation still under investigation.

Expected fields:

| Field | Description |
| --- | --- |
| `id` | Case identifier matching the filename |
| `wallet` | Valid Akash tenant wallet |
| `category` | `prohibited-p2p` or `attributed-infringement` |
| `observed_utc` | Timestamp of the relevant observation |
| `approved_utc` | Timestamp of the review decision |
| `expires_on` | Last day the approval is valid |
| `reviewer` | GitHub reviewer username |
| `issue` | Public GitHub report issue URL |
| `summary` | Short, non-accusatory finding |
| `records` | Two or more independent, sanitised evidence summaries |

Example structure (placeholder only, not a real entry):

```json
{
  "id": "AKT-2026-001",
  "wallet": "<valid Akash tenant wallet>",
  "category": "prohibited-p2p",
  "observed_utc": "2026-10-20T16:00:00Z",
  "approved_utc": "2026-10-21T10:00:00Z",
  "expires_on": "2027-01-01",
  "reviewer": "github-reviewer",
  "issue": "https://github.com/RH1TE/akash-torrent-blacklist/issues/1",
  "summary": "Observed workload breached the reporting provider's published P2P policy.",
  "records": [
    {"kind": "deployment", "summary": "Lease ownership verified from chain records."},
    {"kind": "runtime", "summary": "Workload activity verified from restricted host records."}
  ]
}
```

The checker verifies the JSON format, timestamps, wallet checksum, evidence categories and that the blacklist matches approved cases. It does not replace human fact checking.
