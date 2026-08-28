"""Compose one client's plugin from shared/ plus clients/<client>/ overrides.

Layering, in order:
  1. shared/skills/          -> <out>/skills/
  2. clients/<c>/skills/     -> <out>/skills/   (adds, and overrides by skill name)
  3. shared/mcp.json         -> <out>/<mcpConfigPath>
  4. shared/plugin.base.json + clients/<c>/client.json:manifest -> <out>/<manifestPath>

Every {{TOKEN}} in a copied Markdown or JSON file is replaced from
client.json:tokens, plus CLIENT_KEY and PLUGIN_VERSION injected here.
An unresolved token is a hard error: a client that forgets one must not ship.
"""

import json
import re
import shutil
import sys
from pathlib import Path

TOKEN_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def render(text: str, tokens: dict, where: Path) -> str:
    def sub(m):
        key = m.group(1)
        if key not in tokens:
            raise SystemExit(f"error: {where}: no value for token {{{{{key}}}}}")
        return tokens[key]

    return TOKEN_RE.sub(sub, text)


def copy_tree(src: Path, dst: Path, tokens: dict) -> None:
    for path in sorted(src.rglob("*")):
        if not path.is_file():
            continue
        target = dst / path.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix.lower() in (".md", ".json"):
            target.write_text(render(path.read_text(), tokens, path), encoding="utf-8")
        else:
            shutil.copy2(path, target)


def main() -> None:
    client, out = sys.argv[1], Path(sys.argv[2])
    cfg = json.loads(Path(f"clients/{client}/client.json").read_text())
    base = json.loads(Path("shared/plugin.base.json").read_text())
    tokens = {
        "CLIENT_KEY": client,
        "PLUGIN_VERSION": base.get("version", "0.0.0"),
        **cfg.get("tokens", {}),
    }

    copy_tree(Path("shared/skills"), out / "skills", tokens)

    client_skills = Path(f"clients/{client}/skills")
    if client_skills.is_dir():
        copy_tree(client_skills, out / "skills", tokens)

    mcp_src = Path("shared/mcp.json")
    mcp_dst = out / cfg["mcpConfigPath"]
    mcp_dst.parent.mkdir(parents=True, exist_ok=True)
    mcp_dst.write_text(render(mcp_src.read_text(), tokens, mcp_src), encoding="utf-8")

    manifest = dict(base)
    manifest.update(cfg.get("manifest", {}))
    # $schema, when present, is conventionally first
    ordered = {k: manifest[k] for k in ("$schema",) if k in manifest}
    ordered.update({k: v for k, v in manifest.items() if k != "$schema"})

    man_dst = out / cfg["manifestPath"]
    man_dst.parent.mkdir(parents=True, exist_ok=True)
    with man_dst.open("w", encoding="utf-8") as f:
        json.dump(ordered, f, indent=2, ensure_ascii=False)
        f.write("\n")

    (out / "README.md").write_text(
        f"# Whop plugin for {cfg['displayName']}\n\n"
        "**Generated — do not edit.** Source lives in `shared/` and "
        f"`clients/{client}/`; rebuild with `./scripts/build.sh {client}`.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
