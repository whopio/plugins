"""Compose one client's plugin from shared/ plus clients/<client>/ overrides.

Layering, in order:
  1. shared/skills/          -> <out>/skills/
  2. clients/<c>/skills/     -> <out>/skills/   (adds, and overrides file by file)
  3. shared/mcp.json         -> <out>/<mcpConfigPath>   (or client.json:mcpTemplate)
  4. shared/plugin.base.json + clients/<c>/client.json:manifest -> <out>/<manifestPath>
  5. shared/assets/          -> <out>/assets/
  6. shared/README.md        -> <out>/README.md
  7. client.json:extraFiles  -> <out>/<path>      (optional)

Optional client.json keys, all absent for Claude and Grok:
  version           replaces shared/plugin.base.json:version for this client only,
                    in the manifest and in {{PLUGIN_VERSION}}
  mcpTemplate       MCP config template to render instead of shared/mcp.json
  dropManifestKeys  keys removed from the merged manifest
  extraFiles        {"<out path>": "<source path>"}, rendered like shared files
  lineEndings       "lf": write every text file (.md, .json, .svg, .yaml, .yml, .txt,
                    and any other UTF-8 file without NUL bytes) with LF on every
                    platform. Without it, rendered files use the
                    platform's line ending and other files are copied byte for byte,
                    which is what Claude and Grok rely on.

Every {{TOKEN}} in a copied Markdown or JSON file is replaced from
client.json:tokens, plus CLIENT_KEY and PLUGIN_VERSION injected here.
An unresolved token is a hard error: a client that forgets one must not ship.

Markdown may also hold per-client blocks, each marker on its own line:

  {{#if claude}}      kept only for the named client(s), comma-separated
  {{#elif openai}}    optional, repeatable: kept for these if no earlier branch matched
  {{else}}            optional: kept for every client no earlier branch matched
  {{/if}}

Blocks do not nest. An unclosed or stray marker is a hard error.

A client may set "sameBlocksAs" in client.json to a list of other clients. It then
also matches every block written for those clients. The generic client uses this to
take the same text as Grok, which is on the same MCP route.

A client may set "extraManifestPaths" in client.json to a list of further paths. The
manifest is written to each as well, for tools that only read their own path.

A client may set "skills" in client.json to a list of skill names. Only those shared
skills are copied. Without it, every shared skill is copied.

Sources are read as UTF-8 on every platform, so a Windows build matches a macOS one.
"""

import json
import re
import shutil
import sys
from pathlib import Path

TOKEN_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
IF_RE = re.compile(r"^\{\{#if ([a-z0-9_,]+)\}\}$")
ELIF_RE = re.compile(r"^\{\{#elif ([a-z0-9_,]+)\}\}$")


def select_blocks(text: str, clients: set, where: Path) -> str:
    # state: None outside a block, else True/False = keep the current branch.
    # taken: some branch of the current block already matched this client.
    out, state, taken, seen_else = [], None, False, False
    for n, line in enumerate(text.splitlines(keepends=True), 1):
        marker = line.strip()
        m = IF_RE.match(marker)
        e = ELIF_RE.match(marker)
        if m:
            if state is not None:
                raise SystemExit(f"error: {where}:{n}: nested {{{{#if}}}}")
            state = bool(clients & set(m.group(1).split(",")))
            taken, seen_else = state, False
        elif e:
            if state is None:
                raise SystemExit(f"error: {where}:{n}: {{{{#elif}}}} outside a block")
            if seen_else:
                raise SystemExit(f"error: {where}:{n}: {{{{#elif}}}} after {{{{else}}}}")
            state = not taken and bool(clients & set(e.group(1).split(",")))
            taken = taken or state
        elif marker == "{{else}}":
            if state is None:
                raise SystemExit(f"error: {where}:{n}: {{{{else}}}} outside a block")
            if seen_else:
                raise SystemExit(f"error: {where}:{n}: second {{{{else}}}} in a block")
            state, taken, seen_else = not taken, True, True
        elif marker == "{{/if}}":
            if state is None:
                raise SystemExit(f"error: {where}:{n}: stray {{{{/if}}}}")
            state = None
        elif state is not False:
            out.append(line)
    if state is not None:
        raise SystemExit(f"error: {where}: unclosed {{{{#if}}}}")
    return "".join(out)


def render(text: str, tokens: dict, where: Path) -> str:
    def sub(m):
        key = m.group(1)
        if key not in tokens or not isinstance(tokens[key], str):
            raise SystemExit(f"error: {where}: no value for token {{{{{key}}}}}")
        return tokens[key]

    return TOKEN_RE.sub(sub, text)


def render_file(path: Path, tokens: dict) -> str:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".md":
        text = select_blocks(text, tokens["BLOCK_CLIENTS"], path)
    return render(text, tokens, path)


# Copied (not rendered) files that lineEndings: "lf" also normalizes. Any other
# file that looks like text (UTF-8, no NUL bytes) is normalized too.
LF_COPY_EXT = (".svg", ".yaml", ".yml", ".txt")


def is_text(data: bytes) -> bool:
    if b"\0" in data:
        return False
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def write_text(target: Path, text: str, nl: "str | None") -> None:
    # Same bytes as Path.write_text(text, encoding="utf-8") when nl is None;
    # open() takes newline on every Python 3, Path.write_text only from 3.10.
    with target.open("w", encoding="utf-8", newline=nl) as f:
        f.write(text)


def copy_file(path: Path, target: Path, tokens: dict, nl: "str | None" = None) -> None:
    # nl None keeps the original behavior: platform line endings for rendered
    # files, byte-for-byte copies for the rest. nl "\n" writes LF everywhere.
    target.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in (".md", ".json"):
        write_text(target, render_file(path, tokens), nl)
    elif nl == "\n" and (path.suffix.lower() in LF_COPY_EXT or is_text(path.read_bytes())):
        target.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
    else:
        shutil.copy2(path, target)


def copy_tree(src: Path, dst: Path, tokens: dict, nl: "str | None" = None) -> None:
    for path in sorted(src.rglob("*")):
        if not path.is_file():
            continue
        copy_file(path, dst / path.relative_to(src), tokens, nl)


def main() -> None:
    client, out = sys.argv[1], Path(sys.argv[2])
    cfg = json.loads(Path(f"clients/{client}/client.json").read_text(encoding="utf-8"))
    base = json.loads(Path("shared/plugin.base.json").read_text(encoding="utf-8"))
    version = cfg.get("version", base.get("version", "0.0.0"))
    tokens = {
        "CLIENT_KEY": client,
        "PLUGIN_VERSION": version,
        "DISPLAY_NAME": cfg["displayName"],
        **cfg.get("tokens", {}),
    }
    # Not a text token: the set of client names this build's {{#if}} blocks match.
    tokens["BLOCK_CLIENTS"] = {client, *cfg.get("sameBlocksAs", [])}
    endings = cfg.get("lineEndings")
    if endings not in (None, "lf"):
        raise SystemExit(f'error: clients/{client}/client.json: lineEndings must be "lf" (got {endings!r})')
    nl = "\n" if endings == "lf" else None

    only = cfg.get("skills")
    for skill in sorted(Path("shared/skills").iterdir()):
        if skill.is_dir() and (only is None or skill.name in only):
            copy_tree(skill, out / "skills" / skill.name, tokens, nl)

    client_skills = Path(f"clients/{client}/skills")
    if client_skills.is_dir():
        copy_tree(client_skills, out / "skills", tokens, nl)

    mcp_src = Path(cfg.get("mcpTemplate", "shared/mcp.json"))
    mcp_dst = out / cfg["mcpConfigPath"]
    mcp_dst.parent.mkdir(parents=True, exist_ok=True)
    write_text(mcp_dst, render(mcp_src.read_text(encoding="utf-8"), tokens, mcp_src), nl)

    manifest = dict(base)
    manifest.update(cfg.get("manifest", {}))
    if "version" in cfg:
        manifest["version"] = version
    for key in cfg.get("dropManifestKeys", []):
        manifest.pop(key, None)
    # $schema, when present, is conventionally first
    ordered = {k: manifest[k] for k in ("$schema",) if k in manifest}
    ordered.update({k: v for k, v in manifest.items() if k != "$schema"})

    for rel in [cfg["manifestPath"], *cfg.get("extraManifestPaths", [])]:
        man_dst = out / rel
        man_dst.parent.mkdir(parents=True, exist_ok=True)
        with man_dst.open("w", encoding="utf-8", newline=nl) as f:
            json.dump(ordered, f, indent=2, ensure_ascii=False)
            f.write("\n")

    copy_tree(Path("shared/assets"), out / "assets", tokens, nl)

    readme_src = Path("shared/README.md")
    write_text(out / "README.md", render_file(readme_src, tokens), nl)

    for dst, src in cfg.get("extraFiles", {}).items():
        copy_file(Path(src), out / dst, tokens, nl)



if __name__ == "__main__":
    main()
