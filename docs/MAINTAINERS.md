# Maintainer procedure

## Intake

Check that the report is about a tenant wallet, not the provider's treasury or the public node IP. Verify the chain and DSEQ, place the issue in triage, and request removal of sensitive content immediately if necessary.

Use `needs-evidence` until evidence supports an actual workload finding. Do not label a complainant's file hash as the pod's content hash without independent verification.

## Verification

A reviewer should inspect at least one primary technical record and at least one independently generated corroborating record. Confirm source clock offsets and the specific owner-to-namespace or owner-to-pod relationship. Record the original source custody privately and a sanitized summary in the case.

For an infringement claim, confirm historical flow mapping. Do not assume a containerPort matches a reported outbound ephemeral source port.

Check that the provider's policy applied at the observation time, especially if you are publishing a `prohibited-p2p` record.

## Approval or rejection

Record the decision in the issue. A rejection does not create an entry. For approval, ask a second reviewer, create a case JSON in a PR and regenerate feeds. Check the diff for sensitive data and verify the expiry. Passing CI is necessary but not enough.

Repository branch protection requires a passing `check` workflow and at least one code-owner approval. The case schema also requires two distinct named reviewers. This is an additional human process, not an assertion that the GitHub API has confirmed both approvals.

## Appeals and urgent corrections

When an appellant provides plausible contrary facts, review promptly. Suspend or remove a case if the evidence no longer supports the category. Record the review in the appeal issue and issue a reviewed PR. A new wallet should not be added solely because an old wallet was removed.

## Release and consumer guidance

The default community feed may be fetched from GitHub, but production operators should pin a known reviewed commit or release hash. Publish a changelog with substantial additions, removals or schema changes. Never direct users to run a remote PR script inside a provider container.

## Security checklist

- [ ] No identifying user or client IPs in public issue or diff
- [ ] No private screenshots, raw access logs, notices or key material
- [ ] Two genuinely independent pieces of technical evidence where possible
- [ ] Source and limitations accurately described
- [ ] No unreviewed wallet in public feed
- [ ] Expiry and appeal path present
- [ ] Rollback for consumer operators documented
