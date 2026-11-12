#!/usr/bin/env python3
"""Zip dist/openai/whop into the ChatGPT/Codex submission package, then check it.

    python3 scripts/package-openai.py <out.zip> [--draft]

Run ./scripts/build.sh first: the script stops if dist/openai/whop differs from a
fresh build. The ZIP holds one top-level folder, whop/, with nothing beside it.
Entries use '/' paths, deflate, a fixed order and a fixed timestamp, so the same
dist/ gives the same bytes with the same zlib. Text files are written with LF line
endings: dist/openai is already LF (client.json lineEndings, .gitattributes
eol=lf), and the stale check rejects hand edits, so the rewrite only guards against
compose.py itself emitting CRLF. OpenAI's front matter parsing expects '---\\n'.

The ZIP is then run through scripts/check_openai_plugin.py against the planned
ChatGPT surface (clients/openai/surface.json). Without --draft, submission-only gates
(placeholder demo URL, TODO markers) fail the run; the ZIP is still written so it can
be inspected.
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "dist" / "openai" / "whop"
TOP = "whop"
TEXT_EXT = {".md", ".json", ".yaml", ".yml", ".txt", ".svg"}
SKIP = {".DS_Store", "Thumbs.db", "desktop.ini"}
STAMP = (2026, 1, 1, 0, 0, 0)


def is_text(data: bytes) -> bool:
    if b"\0" in data:
        return False
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def tree(base: Path) -> dict:
    return {p.relative_to(base).as_posix(): p.read_bytes() for p in base.rglob("*")
            if p.is_file() and p.name not in SKIP
            and not any(part.startswith(".git") for part in p.relative_to(base).parts)}


def check_fresh() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / TOP
        subprocess.run([sys.executable, str(ROOT / "scripts" / "compose.py"), "openai", str(fresh)],
                       cwd=ROOT, check=True)
        if tree(fresh) != tree(SRC):
            raise SystemExit("error: dist/openai/whop is stale: run ./scripts/build.sh openai and commit dist/")


def build_zip(out: Path) -> int:
    if not (SRC / "plugin.json").is_file():
        raise SystemExit(f"error: {SRC} has no plugin.json; run ./scripts/build.sh openai first")
    check_fresh()
    files = sorted((p for p in SRC.rglob("*") if p.is_file() and p.name not in SKIP),
                   key=lambda p: p.relative_to(SRC).parts)
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            rel = p.relative_to(SRC).as_posix()
            if any(part.startswith(".git") for part in rel.split("/")):
                continue
            data = p.read_bytes()
            if p.suffix.lower() in TEXT_EXT or is_text(data):
                data = data.replace(b"\r\n", b"\n")
            info = zipfile.ZipInfo(f"{TOP}/{rel}", date_time=STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3  # unix, so the mode bits below are read
            info.external_attr = (0o100644 & 0xFFFF) << 16
            z.writestr(info, data, compresslevel=9)
    return len(files)


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    out = Path(args[0]).resolve()
    n = build_zip(out)
    print(f"wrote {out} ({n} files, {os.path.getsize(out)} bytes)\n")

    sys.dont_write_bytecode = True  # no scripts/__pycache__ in the repo
    spec = importlib.util.spec_from_file_location("check_openai_plugin", ROOT / "scripts" / "check_openai_plugin.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    check_args = ["check", str(out), "--expect-origin", "https://mcp.whop.com",
                  "--expect-url", "https://mcp.whop.com/chatgpt/mcp",
                  "--surface", str(ROOT / "clients" / "openai" / "surface.json")]
    if "--draft" in argv:
        check_args.append("--draft")
    return checker.main(check_args)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
