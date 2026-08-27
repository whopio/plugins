#!/usr/bin/env bash
# Print the xAI marketplace catalog entry for this plugin, pinned to a commit SHA.
#
#   ./scripts/grok-entry.sh              # pin to local HEAD
#   ./scripts/grok-entry.sh <sha>        # pin to an explicit commit
#
# Paste the output into the `plugins` array of .grok-plugin/marketplace.json in a
# fork of xai-org/plugin-marketplace, then regenerate their component index.
set -euo pipefail

cd "$(dirname "$0")/.."
entry="clients/grok/marketplace-entry.json"
[ -f "$entry" ] || { echo "missing $entry" >&2; exit 1; }

sha="${1:-$(git rev-parse --verify HEAD 2>/dev/null || true)}"

if [ -z "$sha" ]; then
  echo "error: no commit to pin — this repo has no commits yet." >&2
  echo "       Commit and push to a public whopio/ repo first, or pass a SHA." >&2
  exit 1
fi

if ! printf '%s' "$sha" | grep -Eq '^[0-9a-f]{40}$'; then
  echo "error: '$sha' is not a full 40-character lowercase commit SHA." >&2
  echo "       xAI's validator rejects branches, tags, and abbreviated SHAs." >&2
  exit 1
fi

# Warn when the pinned commit is not on a public remote — their CI clones it.
if ! git branch -r --contains "$sha" 2>/dev/null | grep -q .; then
  echo "warning: $sha is not on any remote-tracking branch." >&2
  echo "         Push it before submitting, or their CI cannot fetch it." >&2
fi

python3 - "$entry" "$sha" <<'PY'
import json, sys, collections
entry_path, sha = sys.argv[1], sys.argv[2]
d = json.load(open(entry_path), object_pairs_hook=collections.OrderedDict)
d["source"]["sha"] = sha
print(json.dumps(d, indent=2, ensure_ascii=False))
PY
