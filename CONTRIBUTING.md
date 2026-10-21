# Contributing

We welcome reports from datacentre operators, Akash providers and people who can supply reliable technical evidence.

Please use the [incident report form](../../issues/new/choose) rather than editing the blacklist directly.

A useful report contains the tenant wallet, DSEQ, observation time in UTC, a short description of the activity, the provider's relevant policy and a factual account of how the activity was attributed to that tenant.

Be clear about what you know and what you do not know. For example, an infringement notice and a torrent-labelled deployment starting two minutes earlier are correlated facts, but do not alone prove the file was transferred by that deployment.

**Before publishing anything:** remove personal IP addresses, names, private logs, access tokens, customer account data, media files and full copyright notices. Public GitHub history is difficult to erase. Maintainers can review confidential records separately.

## For maintainers

1. Review the issue and record the reason for acceptance or refusal.
2. For accepted cases, create a JSON file in `cases/` following [cases/FORMAT.md](cases/FORMAT.md).
3. Run `python3 tools/list.py build`.
4. Open a pull request containing the case and regenerated `blacklist.txt`.
5. Check the automated tests, request code-owner review and merge only after approval.

For rejected reports, explain the decision and close the issue. Do not edit the blacklist.

Report an error or request removal through the appeal issue template.

See [REVIEW.md](REVIEW.md) for the decision standard.
