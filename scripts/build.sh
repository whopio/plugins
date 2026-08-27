#!/usr/bin/env bash
# Compose each client's plugin from shared/ + clients/<client>/ into dist/<client>/whop.
#
#   ./scripts/build.sh            # rebuild every client
#   ./scripts/build.sh claude     # rebuild one
#   ./scripts/build.sh --check    # fail if dist/ is stale (CI)
#
# dist/ is COMMITTED, not ignored: marketplaces read a path in this repo at a pinned
# commit and never run this script.
set -euo pipefail
cd "$(dirname "$0")/.."

check=false
targets=()
for arg in "$@"; do
  case "$arg" in
    --check) check=true ;;
    -*) echo "unknown flag: $arg" >&2; exit 2 ;;
    *) targets+=("$arg") ;;
  esac
done
if [ ${#targets[@]} -eq 0 ]; then
  for d in clients/*/client.json; do targets+=("$(basename "$(dirname "$d")")"); done
fi

outroot="dist"
[ "$check" = true ] && outroot="$(mktemp -d)/dist"

for client in "${targets[@]}"; do
  cfg="clients/$client/client.json"
  [ -f "$cfg" ] || { echo "no such client: $client (missing $cfg)" >&2; exit 1; }
  out="$outroot/$client/whop"
  rm -rf "$out"; mkdir -p "$out"

  python3 scripts/compose.py "$client" "$out"
  echo "  built $client -> dist/$client/whop"
done

if [ "$check" = true ]; then
  if diff -r -q "$outroot" dist >/dev/null 2>&1; then
    echo "dist/ is up to date."
  else
    echo "ERROR: dist/ is stale — run ./scripts/build.sh and commit the result." >&2
    diff -r "$outroot" dist | head -20 >&2
    exit 1
  fi
fi
