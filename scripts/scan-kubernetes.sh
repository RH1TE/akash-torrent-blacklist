#!/usr/bin/env bash
# Operator-scheduled, read-only scan. No namespace eviction or wallet ban.
set -euo pipefail
: "${KUBECTL:=kubectl}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/.." && pwd)"
OUT="${1:-./local-reports}"
mkdir -p "$OUT"
chmod 700 "$OUT"
DATE="$(date -u +%Y%m%dT%H%M%SZ)"
PODS="$OUT/pods-$DATE.json"
REPORT="$OUT/pod-signals-$DATE.json"
umask 077
"$KUBECTL" get pods -A -o json > "$PODS"
python3 "$REPO/tools/scan_pods.py" --input "$PODS" --format json > "$REPORT"
python3 - "$REPORT" <<'PY'
import json,sys
p=sys.argv[1]
report=json.load(open(p))
print(f'Read-only scan complete: {report["finding_count"]} pods with indicators. Review {p}')
PY
# Neither file is automatically published. Restrict operator storage.
