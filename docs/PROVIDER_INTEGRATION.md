# Using this registry in an Akash provider

The public list is a **reviewed reference**, not a mandatory policy. Start with a local copy and inspect case records before enforcing a block.

## 1. Fetch outside the bid hot path

```bash
mkdir -p /var/lib/akash-provider/abuse
python3 tools/update_feed.py \
  --url https://raw.githubusercontent.com/RH1TE/akash-torrent-blacklist/main/blacklist.txt \
  --dest /var/lib/akash-provider/abuse/community-wallets.txt
```

The downloader validates syntax, size and uniqueness, saves atomically, and retains the previous cache if validation fails. For higher assurance, pin the URL to an approved Git commit and set `--sha256` to the expected content hash. Review GitHub releases and case records before updating the pinned version.

Never `curl | bash` a remote file. Never fetch GitHub during a pricing script invocation.

## 2. Local provider choices

Keep your operator-specific `allow.txt` and `deny.txt` separate. They take precedence over the community feed. Use the checker interactively first:

```bash
python3 tools/provider_check.py \
  --wallet "$AKASH_OWNER" \
  --feed /var/lib/akash-provider/abuse/community-wallets.txt \
  --allow /etc/akash-provider/allow.txt \
  --deny /etc/akash-provider/deny.txt
```

Without `--enforce`, it always reports a decision but returns success for a valid request. After reviewing the list, adding case-specific local overrides and testing with an ordinary wallet, use `--enforce`. A matching denied wallet returns exit code 10, explicitly distinct from an invalid/missing feed (exit code 20). A production wrapper should map the *known* denial exit code to the provider's expected reject status and treat other errors as operational faults.

Allowlist overrides exist to correct a false positive quickly. A local explicit deny always takes precedence unless the local operator deliberately changes it. Neither script changes Kubernetes or a Helm release.

## 3. Existing pricing scripts

```bash
if python3 /opt/registry/tools/provider_check.py \
    --wallet "${AKASH_OWNER:-}" --feed /var/lib/akash-provider/abuse/community-wallets.txt \
    --deny /etc/akash-provider/deny.txt --allow /etc/akash-provider/allow.txt \
    --enforce --quiet; then
  : # continue pricing calculation
else
  code=$?
  if [ "$code" -eq 10 ]; then
    echo "wallet denied by locally approved provider policy" >&2
    exit 1
  fi
  echo "feed or policy check failed, review provider health" >&2
  # Choose your failure behaviour deliberately, rather than guessing.
fi
```

The code above is a pattern for **operator review**, not a ready-to-paste replacement for every Akash Helm chart. Check how your provider supplies `AKASH_OWNER`, refreshes projected ConfigMap volumes and restarts a bid price process. Test the effective mounted script after rollout. A ConfigMap update is not proof the running provider refreshed its copy.

## 4. Firewall and runtime security

Blocking ports 6881 to 6999, 51413 or 6969 catches only a fraction of BitTorrent traffic, and could affect unrelated services. Validate actual tenant traffic, rule order, CNI policy interaction, Wings/game ingress, routed IPs and rollback before activating a global rule.

A Kubernetes admission policy can prevent a known image or command from being started; it cannot ensure the same process is not downloaded or renamed later. Add privacy-aware flow logging and tenant-scoped monitoring if a stronger abuse response is needed.

## 5. Rolling back

Remove the relevant local deny entry or temporarily allow a wallet under your documented review procedure. Restore the last known-good cached feed. Use a provider-specific tested deployment method for updating running script mounts. Do not trigger a broad cluster upgrade merely because a public list changed.

The registry does not execute lease closures, remove namespaces, restart a pod or modify a host firewall.
