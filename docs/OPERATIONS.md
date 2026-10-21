# Operations and maintenance

## Responsibilities

Public triage, evidence review, code changes and infrastructure enforcement are separate jobs. Maintainers moderate reports and publish only supported cases. Individual datacentre operators investigate their own hosts and control their own customer services.

## Routine work

**Daily:** look at new reports, urgent abuse deadlines, evidence requests and active appeals. Do not leave a datacentre notice unanswered while a public review is pending.

**Weekly:** check proposed indicator changes against legitimate pods, review open PRs, recent corrections and expiry warnings. Confirm GitHub Actions checks are passing.

**Monthly:** check that accepted case evidence remains available to the reviewers, inspect false positive trends, check pinned feed consumer versions and assess the impact of any changes in Akash deployment labels or provider chart behaviour.

**At expiry:** remove or reassess the listing. The validator fails on expired case records, so maintainers cannot silently ship a stale approved feed.

## Evidence handling

Keep original complaints and flow traces private, with controlled read access. Record an evidence acquisition manifest and keep public case summaries minimal. A code repository is not a durable forensic evidence store. Do not include secret environment values or complete pod YAML exports in GitHub issues.

## Provider change control

Before enforcing new wallet policy or network restrictions, preserve the current rules, identify rollback commands, run synthetic allow and deny tests, check current customer workloads and assign the person who will approve production changes. Monitor live bid and customer acceptance after deployment.

A failed script download or unresponsive GitHub should not silently replace a valid cache with an empty file. If there is no valid feed, the checker returns an operational error rather than claiming every wallet is safe or unsafe.

## Review outcomes

An approved report creates an auditable case record and changes the public feed through a reviewed PR. A declined or unresolved report does not. An appeal can lead to correction, a narrower category, or full removal. Document why, and notify providers relying on the earlier case when reasonable.

## Maintenance checklist

- [ ] Reports have timestamps, DSEQ, owner and evidence references
- [ ] Two independent sources have been considered
- [ ] Claim category is not stronger than the evidence
- [ ] No sensitive information appears in public diffs
- [ ] CI checks and tests pass
- [ ] Review and expiry dates are current
- [ ] A rollback exists for consumer operators

## Read-only scheduled capture

The optional `scripts/scan-kubernetes.sh` wrapper exports a Kubernetes pod inventory into a restricted local directory and produces an indicators report. It does not evict pods or deny wallets. Schedule it only after reviewing the required cluster RBAC and available storage.

For behavioural screening, supply saved flow metadata to `tools/scan_flows.py` with explicit thresholds. Tune alerts against legitimate customer traffic before using any findings for investigation.
