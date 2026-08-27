#!/usr/bin/env bash
# Validate marketplace and plugin structure. Run before every release.
set -euo pipefail

cd "$(dirname "$0")/.."
fail=0
err() { echo "  ✗ $1"; fail=1; }

echo "Validating JSON…"
while IFS= read -r f; do
  if python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$f" 2>/dev/null; then
    echo "  ✓ $f"
  else
    err "$f is not valid JSON"
  fi
done < <(find . -name '*.json' -not -path './node_modules/*' -not -path './.git/*' | sort)

echo "Validating marketplace…"
if python3 - <<'PY'
import json, os, sys

mp = json.load(open(".claude-plugin/marketplace.json"))
problems = []

for field in ("name", "owner", "plugins"):
    if field not in mp:
        problems.append(f"marketplace.json missing required field: {field}")

for entry in mp.get("plugins", []):
    name, src = entry.get("name"), entry.get("source")
    if not name or not src:
        problems.append(f"plugin entry missing name or source: {entry}")
        continue
    root = os.path.normpath(src)
    if not os.path.isdir(root):
        problems.append(f"{name}: source directory not found: {root}")
        continue

    manifest = os.path.join(root, ".claude-plugin", "plugin.json")
    if not os.path.isfile(manifest):
        problems.append(f"{name}: missing {manifest}")
    else:
        pj = json.load(open(manifest))
        if pj.get("name") != name:
            problems.append(
                f"{name}: plugin.json name is {pj.get('name')!r}, "
                f"marketplace says {name!r}"
            )
        if pj.get("version") != entry.get("version"):
            problems.append(
                f"{name}: version mismatch — plugin.json {pj.get('version')!r} "
                f"vs marketplace {entry.get('version')!r}"
            )

    # Components must sit at the plugin root, never inside .claude-plugin/
    for comp in ("skills", "commands", "agents", "hooks", ".mcp.json"):
        stray = os.path.join(root, ".claude-plugin", comp)
        if os.path.exists(stray):
            problems.append(f"{name}: {comp} must be at the plugin root, not in .claude-plugin/")

    skills = os.path.join(root, "skills")
    if os.path.isdir(skills):
        for d in sorted(os.listdir(skills)):
            sd = os.path.join(skills, d)
            if os.path.isdir(sd) and not os.path.isfile(os.path.join(sd, "SKILL.md")):
                problems.append(f"{name}: skills/{d}/ has no SKILL.md")

for p in problems:
    print(f"  ✗ {p}")
sys.exit(1 if problems else 0)
PY
then :; else fail=1; fi

echo "Validating dist/ is in sync with shared/ + clients/…"
if ./scripts/build.sh --check >/dev/null 2>&1; then
  echo "  ✓ dist/ up to date"
else
  err "dist/ is stale — run ./scripts/build.sh and commit the result"
fi

echo "Validating skill frontmatter…"
while IFS= read -r f; do
  if [ "$(head -1 "$f")" != "---" ]; then
    err "$f does not start with YAML frontmatter"
  elif ! sed -n '2,20p' "$f" | grep -q '^description:'; then
    err "$f has no description: in its frontmatter"
  else
    echo "  ✓ $f"
  fi
done < <(find shared clients -name 'SKILL.md' | sort)

if [ "$fail" -ne 0 ]; then
  echo
  echo "FAILED"
  exit 1
fi
echo
echo "All checks passed."
