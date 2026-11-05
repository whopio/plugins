#!/usr/bin/env python3
"""Offline pre-flight check for a public ChatGPT/Codex plugin package (With MCP path).

    python3 scripts/check_openai_plugin.py <plugin.zip | plugin-dir>
        [--expect-origin https://mcp.whop.com] [--expect-url https://mcp.whop.com/chatgpt/mcp]
        [--surface clients/openai/surface.json]
        [--draft]

Rule IDs (Z, M, L, I, R, P, C, S, Y, F, W) are this script's own labels; each
message says what it checks. Sources: developers.openai.com/plugins/build/plugins,
/plugins/deploy/submission and /plugins/plugin-guidelines. This is NOT an OpenAI
tool: the upload at platform.openai.com/plugins is the real validator, and OpenAI's
server-side checks are out of reach here.

--surface   JSON object with `tools` (group -> operations), `meta`, and
            `excludedGroups` (every Whop tool group with no tool on the route;
            required, because a live tools/list cannot produce it). Every
            tools_triggered name, and every Whop tool name the skills mention, must
            be on it (R5 / SURF).
--draft     Submission-only gates become warnings: the placeholder demo URL (R7) and
            TODO markers (TODO). Without it they are errors.

Exit code 0 = no errors (warnings may remain), 1 = errors, 2 = usage.
SKILL.md front matter and agents/openai.yaml need PyYAML.
"""
import json
import os
import re
import struct
import sys
import unicodedata
import zipfile
from urllib.parse import urlsplit
from xml.etree import ElementTree

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
ROOT_KEYS = {"$schema", "name", "version", "description", "author", "homepage",
             "repository", "license", "keywords", "extensions"}
OPENAI_KEYS = {"interface", "onboardingSkill", "review", "publication"}
INTERFACE_KEYS = {"displayName", "shortDescription", "longDescription", "developerName",
                  "category", "capabilities", "websiteURL", "supportURL", "privacyPolicyURL",
                  "termsOfServiceURL", "defaultPrompt", "brandColor", "brandColorDark",
                  "composerIcon", "composerIconDark", "logo", "logoDark", "screenshots"}
CATEGORIES = {"Productivity", "Creativity", "Developer Tools", "Business & Operations",
              "Data & Analytics", "Communication", "Education & Research", "Security",
              "Finance", "Healthcare", "Travel", "Entertainment", "Other"}
POS_KEYS = {"description", "prompt", "tools_triggered", "expected_behavior",
            "file_attachment_urls", "expected_output_url"}
NEG_KEYS = {"description", "prompt", "file_attachment_urls", "expected_output_url"}
SKILL_FM_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
BANNED_MANIFEST_KEYS = {"apps", "hooks", "test_credentials", "reviewer_instructions",
                        "clientSecret", "client_secret", "skills", "mcpServers"}
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
                    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$")
PLUGIN_NAME = re.compile(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
INVISIBLE = re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2064\u2066-\u2069\u061c\ufeff\u2028\u2029]")
OTHER_MANIFESTS = (".codex-plugin/", ".claude-plugin/", ".agent-plugin/")
CLAUDE_ONLY = ("commands/", "agents/", ".claude/", "output-styles/")
JUNK = re.compile(r"(^|/)(\.DS_Store|Thumbs\.db|desktop\.ini|__MACOSX/.*|\.git/.*|\.env.*)$")
TEXT_EXT = (".md", ".json", ".yaml", ".yml", ".txt", ".svg")
TOOLISH = re.compile(r"(?<![\w./-])([a-z][a-z0-9-]*)_([a-z0-9][a-z0-9_-]*\*?|\*)(?![\w-])")


class Report:
    def __init__(self, draft):
        self.draft = draft
        self.errors, self.warnings, self.passes = [], [], []

    def err(self, rid, msg):
        self.errors.append(f"[{rid}] {msg}")

    def warn(self, rid, msg):
        self.warnings.append(f"[{rid}] {msg}")

    def ok(self, rid, msg):
        self.passes.append(f"[{rid}] {msg}")

    def gate(self, rid, msg):
        """A submission-only gate: an error, or a warning in --draft mode."""
        (self.warn if self.draft else self.err)(rid, msg)


def supported_text(s, multiline=False):
    if not isinstance(s, str) or not s.strip():
        return False
    if INVISIBLE.search(s):
        return False
    for ch in s:
        if ch == "\n" and multiline:
            continue
        if unicodedata.category(ch) == "Cc":
            return False
    return True


def one_line(s):
    return isinstance(s, str) and "\n" not in s and "\r" not in s


def https_ok(u, maxlen):
    if not isinstance(u, str) or not u or len(u) > maxlen:
        return False
    p = urlsplit(u)
    return p.scheme == "https" and bool(p.hostname) and p.username is None and p.password is None and not p.fragment


def contrast(hex1, hex2):
    def lum(h):
        h = h.lstrip("#")
        c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    a, b = sorted([lum(hex1), lum(hex2)], reverse=True)
    return (a + 0.05) / (b + 0.05)


class Pkg:
    """Uniform read access to a ZIP or a directory, rooted at the plugin root."""

    def __init__(self, path, rep):
        self.rep = rep
        self.files = {}
        self.is_zip = path.lower().endswith(".zip")
        if self.is_zip:
            self._load_zip(path)
        else:
            self._load_dir(path)

    def _load_dir(self, path):
        base = os.path.abspath(path)
        if not os.path.isdir(base):
            self.rep.err("Z1", f"not a directory or .zip: {path}")
            return
        for dp, dn, fn in os.walk(base):
            for f in fn:
                full = os.path.join(dp, f)
                rel = os.path.relpath(full, base).replace(os.sep, "/")
                if os.path.islink(full):
                    self.rep.err("Z8", f"symlink not allowed: {rel}")
                    continue
                if JUNK.search(rel):
                    self.rep.err("Z14", f"junk/secret-looking file: {rel}")
                with open(full, "rb") as fh:
                    self.files[rel] = fh.read()
        self.rep.warn("Z0", "directory given: archive-level rules (Z1-Z13, W3) not checked")

    def _load_zip(self, path):
        size = os.path.getsize(path)
        if size > 100 * 1000 * 1000:
            self.rep.err("Z2", f"compressed ZIP is {size} bytes (> 100 MB)")
        try:
            z = zipfile.ZipFile(path)
        except zipfile.BadZipFile:
            self.rep.err("Z1", "not a valid ZIP")
            return
        infos = z.infolist()
        if not infos:
            self.rep.err("Z1", "archive is empty")
        if z.testzip() is not None:
            self.rep.err("Z1", f"corrupt entry: {z.testzip()}")
        if len(infos) > 5000:
            self.rep.err("Z3", f"{len(infos)} entries (> 5000)")
        total, seen_norm, names = 0, {}, [i.filename for i in infos]
        for i in infos:
            n = i.filename
            if "\\" in n:
                self.rep.err("Z5", f"backslash in path: {n}")
            if n != n.strip():
                self.rep.err("Z5", f"outer whitespace in path: {n!r}")
            if n.startswith("/") or re.match(r"^[A-Za-z]:", n):
                self.rep.err("Z5", f"absolute path: {n}")
            segs = n.rstrip("/").split("/")
            if any(s == "" for s in segs):
                self.rep.err("Z5", f"empty segment: {n}")
            if any(s == ".." for s in segs):
                self.rep.err("Z5", f"'..' segment: {n}")
            if any(s != s.strip() for s in segs):
                self.rep.err("Z5", f"segment with outer whitespace: {n!r}")
            if len(segs) > 20:
                self.rep.err("Z6", f"path deeper than 20 segments: {n}")
            key = unicodedata.normalize("NFC", n.rstrip("/")).casefold()
            if key in seen_norm:
                self.rep.err("Z7", f"duplicate or case/Unicode collision: {n} vs {seen_norm[key]}")
            seen_norm[key] = n
            mode = (i.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                self.rep.err("Z8", f"symlink entry: {n}")
            if i.flag_bits & 0x1:
                self.rep.err("Z9", f"encrypted entry: {n}")
            if i.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                self.rep.err("Z9", f"unsupported compression {i.compress_type}: {n}")
            if i.file_size > 100 * 1024 * 1024:
                self.rep.err("Z4", f"entry > 100 MiB: {n}")
            total += i.file_size
            if JUNK.search(n):
                self.rep.err("Z14", f"junk/secret-looking file: {n}")
        if total > 512 * 1024 * 1024:
            self.rep.err("Z3", f"extracted size {total} > 512 MiB")
        files = [i for i in infos if not i.is_dir()]
        for f in files:
            if any(o.filename.startswith(f.filename + "/") for o in infos):
                self.rep.err("Z7", f"file path also used as directory: {f.filename}")
        manifests = ("plugin.json", ".codex-plugin/plugin.json", ".agent-plugin/plugin.json",
                     ".claude-plugin/plugin.json")
        top = {n.split("/")[0] for n in names}
        prefix = ""
        if any(n in manifests for n in names):
            prefix = ""
        elif len(top) == 1:
            prefix = next(iter(top)) + "/"
            siblings = [n for n in names if "/" not in n]
            if siblings:
                self.rep.err("Z11", f"sibling files next to the top-level plugin folder: {siblings}")
        else:
            self.rep.err("Z10", f"ambiguous plugin root; top-level entries: {sorted(top)}")
        self.rep.ok("Z10", f"plugin root = '{prefix or '<archive root>'}', {len(files)} files, {size} bytes")
        for f in files:
            if f.filename.startswith(prefix):
                data = z.read(f)
                rel = f.filename[len(prefix):]
                self.files[rel] = data
                if rel.lower().endswith(TEXT_EXT) and b"\r\n" in data:
                    self.rep.err("W3", f"CRLF line endings in {rel} (front matter parsers expect '---\\n')")


def load_json(pkg, rep, path, rid):
    raw = pkg.files.get(path)
    if raw is None:
        rep.err(rid, f"{path} missing")
        return None
    try:
        data = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError:
        rep.err(rid, f"{path} is not UTF-8")
        return None
    except json.JSONDecodeError as e:
        rep.err(rid, f"{path} malformed JSON: {e}")
        return None
    if not isinstance(data, dict):
        rep.err(rid, f"{path} top level is not an object")
        return None
    return data


def walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k, v, f"{path}.{k}"
            yield from walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield None, v, f"{path}[{i}]"
            yield from walk(v, f"{path}[{i}]")


def check_image(pkg, rep, field, p):
    if not isinstance(p, str) or not p:
        rep.err("I1", f"{field} must be a non-empty path string")
        return
    if p != p.strip() or any(ord(c) < 32 or ord(c) == 127 for c in p):
        rep.err("I1", f"{field} has whitespace/control chars")
    if not p.startswith("./"):
        rep.err("M11", f"{field} must start with ./ ({p})")
    rel = p[2:] if p.startswith("./") else p
    if ".." in rel.split("/") or rel.startswith("/") or re.match(r"^[A-Za-z]:", rel):
        rep.err("M11", f"{field} path leaves the plugin root: {p}")
        return
    data = pkg.files.get(rel)
    if data is None:
        rep.err("I1", f"{field} file not in package: {p}")
        return
    if len(data) > 5 * 1024 * 1024:
        rep.err("I2", f"{field} > 5 MiB")
    ext = rel.rsplit(".", 1)[-1].lower()
    if ext not in ("png", "jpg", "jpeg", "webp", "svg"):
        rep.err("I2", f"{field} extension .{ext} not in png/jpg/jpeg/webp/svg")
        return
    w = h = None
    if ext == "svg":
        if b"<!DOCTYPE" in data or b"<!ENTITY" in data:
            rep.err("I4", f"{field} SVG contains DOCTYPE/ENTITY declarations; remove them")
            return
        try:
            root = ElementTree.fromstring(data.decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            rep.err("I4", f"{field} SVG not valid UTF-8 XML: {e}")
            return
        if not root.tag.endswith("svg"):
            rep.err("I4", f"{field} root element is not <svg>")
            return
        num = r"^[+-]?(\d+(\.\d*)?|\.\d+)$"
        vb = root.get("viewBox")
        if vb:
            parts = re.split(r"[\s,]+", vb.strip())
            if len(parts) == 4 and all(re.match(num, x) for x in parts):
                w, h = float(parts[2]), float(parts[3])
        ws, hs = root.get("width"), root.get("height")
        if w is None and ws and hs and re.match(num, ws) and re.match(num, hs):
            w, h = float(ws), float(hs)
        for v in (ws, hs):
            if v and not re.match(num, v):
                rep.err("I4", f"{field} SVG width/height must be unitless numbers ({v})")
        if w is None:
            rep.err("I4", f"{field} SVG lacks a numeric viewBox or numeric width/height")
            return
    else:
        kind = None
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            kind = "png"
            w, h = struct.unpack(">II", data[16:24])
        elif data[:3] == b"\xff\xd8\xff":
            kind = "jpeg"
            i = 2
            while i < len(data) - 9:
                if data[i] != 0xFF:
                    i += 1
                    continue
                marker = data[i + 1]
                if marker in (0xC0, 0xC1, 0xC2):
                    h, w = struct.unpack(">HH", data[i + 5:i + 9])
                    break
                i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
        elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            kind = "webp"
            chunk = data[12:16]
            if chunk == b"VP8X":
                w = 1 + int.from_bytes(data[24:27], "little")
                h = 1 + int.from_bytes(data[27:30], "little")
            elif chunk == b"VP8 ":
                w, h = struct.unpack("<HH", data[26:30])
                w, h = w & 0x3FFF, h & 0x3FFF
            elif chunk == b"VP8L":
                b = int.from_bytes(data[21:25], "little")
                w, h = (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
        else:
            rep.err("I3", f"{field} raster cannot be decoded as PNG/JPEG/WebP")
            return
        if {"jpg": "jpeg"}.get(ext, ext) != kind:
            rep.err("I3", f"{field} extension .{ext} does not match content ({kind})")
        if w and (w > 4096 or h > 4096):
            rep.err("I3", f"{field} larger than 4096 px ({w}x{h})")
    if w is None or h is None:
        rep.err("I3", f"{field} dimensions unreadable")
        return
    if w <= 0 or h <= 0:
        rep.err("I4", f"{field} non-positive dimensions")
    if abs(w - h) > 1e-9:
        rep.err("I3", f"{field} not square ({w:g}x{h:g})")
    if min(w, h) < 48:
        rep.err("I3", f"{field} smaller than 48x48 ({w:g}x{h:g})")
    rep.ok("I1", f"{field} {p} ok ({w:g}x{h:g})")


def check_layout(pkg, rep):
    names = set(pkg.files)
    for n in sorted(names):
        if n.startswith(OTHER_MANIFESTS):
            rep.err("M2", f"second manifest folder in the package: {n}")
        if n == ".app.json" or n.endswith("/.app.json"):
            rep.err("F1", f"apps mapping not allowed in a public ZIP: {n}")
        if n.startswith("hooks/") or n == "hooks.json":
            rep.err("F2", f"lifecycle hooks are not allowed in a public ZIP: {n}")
        if n.startswith(CLAUDE_ONLY) or n in ("CLAUDE.md",) or n.endswith(".mcpb"):
            rep.err("F5", f"Claude-only component; convert to a skill or drop: {n}")
    if ".mcp.json" in names:
        rep.err("W1", ".mcp.json next to mcp.json: ship one MCP config only")


def check_manifest(pkg, rep):
    m = load_json(pkg, rep, "plugin.json", "M1")
    if m is None:
        return None
    extra = set(m) - ROOT_KEYS
    if extra:
        rep.err("M3", f"plugin.json top-level keys outside the closed portable schema: {sorted(extra)}")
    if m.get("$schema") != PLUGIN_SCHEMA:
        rep.err("M4", f"$schema must be {PLUGIN_SCHEMA}")
    name = m.get("name")
    if not isinstance(name, str) or not PLUGIN_NAME.match(name or "") or len(name) > 64:
        rep.err("M5", f"name {name!r} must be 1-64 chars, lowercase/digits/single hyphens, alnum ends")
    else:
        rep.ok("M5", f"name = {name}")
    v = m.get("version")
    if not isinstance(v, str) or not SEMVER.match(v or "") or len(v) > 64:
        rep.err("M6", f"version {v!r} must be a semver string <= 64 chars")
    else:
        rep.ok("M6", f"version = {v} (must differ from the last upload)")
    d = m.get("description")
    if not supported_text(d, multiline=True):
        rep.err("M7", "description required, non-empty, supported text")
    elif len(d) > 1024:
        rep.err("M7", f"description is {len(d)} chars (> 1024, plugin_description_too_long)")
    else:
        rep.ok("M7", f"description {len(d)}/1024")
    a = m.get("author")
    if not isinstance(a, dict) or not supported_text(a.get("name", "")):
        rep.err("M8", "author.name required")
    else:
        if set(a) - {"name", "email", "url"}:
            rep.err("M8", f"author has extra keys {sorted(set(a) - {'name', 'email', 'url'})}")
        if len(a["name"]) > 120:
            rep.err("M8", "author.name > 120")
        if "email" in a and (not supported_text(a["email"]) or len(a["email"]) > 320):
            rep.err("M8", "author.email invalid")
        if "url" in a and not https_ok(a["url"], 2048):
            rep.err("M8", "author.url must be HTTPS <= 2048, no credentials")
    if "homepage" in m and not https_ok(m["homepage"], 2048):
        rep.err("M9", "homepage must be HTTPS <= 2048")
    if "keywords" in m and (not isinstance(m["keywords"], list) or not all(isinstance(k, str) for k in m["keywords"])):
        rep.err("M9", "keywords must be an array of strings")
    for k, _, where in walk(m):
        if k in BANNED_MANIFEST_KEYS:
            rep.err("R9", f"key not allowed in a public plugin.json: {where}")
    ext = m.get("extensions")
    if not isinstance(ext, dict) or not isinstance(ext.get("com.openai"), dict):
        rep.err("M10", "extensions.com.openai object missing")
        return m
    for ns, val in ext.items():
        if not isinstance(val, dict):
            rep.err("M10", f"extensions.{ns} must be an object")
    o = ext["com.openai"]
    if "id" in o:
        rep.err("M10", "do not set extensions.com.openai.id: ZIP uploads use the dashboard identity")
    if set(o) - OPENAI_KEYS - {"id"}:
        rep.warn("M10", f"unexpected extensions.com.openai keys: {sorted(set(o) - OPENAI_KEYS - {'id'})}")
    check_interface(pkg, rep, o.get("interface"))
    ob = o.get("onboardingSkill")
    if ob is not None:
        mm = re.match(r"^\./skills/([^/]+)/SKILL\.md$", ob or "")
        if not mm or ob[2:] not in pkg.files:
            rep.err("M12", f"onboardingSkill {ob!r} must be ./skills/<skill>/SKILL.md of an included skill")
        else:
            rep.ok("M12", f"onboardingSkill -> {ob}")
    check_review(rep, o.get("review"))
    check_publication(rep, o.get("publication"))
    return m


def check_interface(pkg, rep, i):
    if not isinstance(i, dict):
        rep.err("L1", "extensions.com.openai.interface missing")
        return
    if set(i) - INTERFACE_KEYS:
        rep.warn("L0", f"unknown interface keys: {sorted(set(i) - INTERFACE_KEYS)}")
    for key, lim, rid in (("displayName", 30, "L1"), ("shortDescription", 30, "L2"),
                          ("developerName", 80, "L4")):
        s = i.get(key)
        if not supported_text(s) or not one_line(s):
            rep.err(rid, f"{key} required, one line, supported text")
        elif len(s) > lim:
            rep.err(rid, f"{key} is {len(s)} chars (> {lim})")
        else:
            rep.ok(rid, f"{key} = {s!r} ({len(s)}/{lim})")
    if re.search(r"\b(plugin|mcp|mcp server)\s*$", (i.get("displayName") or "").strip(), re.I):
        rep.err("L1b", "displayName must not append 'Plugin', 'MCP' or 'MCP Server'")
    ld = i.get("longDescription")
    if not supported_text(ld, multiline=True):
        rep.err("L3", "longDescription required")
    elif len(ld) > 4000:
        rep.err("L3", f"longDescription {len(ld)} chars (> 4000)")
    else:
        rep.ok("L3", f"longDescription {len(ld)}/4000")
    for k in ("shortDescription", "longDescription", "displayName"):
        s = i.get(k) or ""
        hit = re.search(r"(\$\s?\d|\bprice|\bpricing|free trial|\bdiscount|\bpromo|\bupgrade|\bsubscribe\b|% off|\bbetter than\b|\bbest\b|\bprefer\b)", s, re.I)
        if hit:
            rep.warn("L13", f"{k} may advertise pricing/promotion or steer: {hit.group(0)!r}")
    cat = i.get("category")
    if cat not in CATEGORIES:
        rep.err("L5", f"category {cat!r} not in {sorted(CATEGORIES)}")
    else:
        rep.ok("L5", f"category = {cat}")
    caps = i.get("capabilities")
    if caps is not None:
        if not isinstance(caps, list) or len(caps) > 20:
            rep.err("L6", "capabilities must be a list of <= 20")
        else:
            for c in caps:
                if not supported_text(c) or not one_line(c) or len(c) > 120:
                    rep.err("L6", f"capability invalid: {c!r}")
    for key in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
        if not https_ok(i.get(key), 1024):
            rep.err("L7", f"{key} required for MCP review: HTTPS, <= 1024, no credentials")
        else:
            rep.ok("L7", f"{key} = {i[key]}")
    dp = i.get("defaultPrompt")
    if dp is not None:
        lst = [dp] if isinstance(dp, str) else dp
        if not isinstance(lst, list) or len(lst) > 3:
            rep.err("L8", "defaultPrompt must be a string or a list of <= 3")
        else:
            seen = set()
            for p in lst:
                if not supported_text(p) or not one_line(p) or len(p) > 128:
                    rep.err("L8", f"starter prompt invalid or > 128: {p!r}")
                if isinstance(p, str) and "@" in p:
                    rep.err("L8", f"starter prompt has an @mention: {p!r}")
                k = " ".join(unicodedata.normalize("NFKC", str(p)).split()).casefold()
                if k in seen:
                    rep.err("L8", f"duplicate starter prompt: {p!r}")
                seen.add(k)
            rep.ok("L8", f"{len(lst)} starter prompts")
    for key, against in (("brandColor", "#FFFFFF"), ("brandColorDark", "#212121")):
        bc = i.get(key)
        if bc is None:
            continue
        if not isinstance(bc, str) or not HEX.match(bc):
            rep.err("L9", f"{key} must be #RRGGBB")
        elif contrast(bc, against) < 2:
            rep.err("L9", f"{key} contrast vs {against} {contrast(bc, against):.2f} < 2")
        else:
            rep.ok("L9", f"{key} {bc} contrast vs {against} {contrast(bc, against):.2f}")
    for key in ("logo", "composerIcon"):
        if key not in i:
            rep.err("L10", f"interface.{key} required")
        else:
            check_image(pkg, rep, key, i[key])
    for key in ("logoDark", "composerIconDark"):
        if key in i:
            check_image(pkg, rep, key, i[key])
    if "screenshots" in i:
        rep.err("L11", "omit screenshots: allowed only when the MCP server has a UI output template")
    for k, v, where in walk(i):
        if isinstance(v, str) and (INVISIBLE.search(v) or any(unicodedata.category(c) == "Cc" and c != "\n" for c in v)):
            rep.err("L12", f"unsupported characters in interface{where}")


def check_review(rep, r):
    if not isinstance(r, dict):
        rep.warn("R1", "review block absent: test cases and demo URL must then be entered in the portal")
        return
    tc = r.get("test_cases")
    if tc is not None and not isinstance(tc, dict):
        rep.err("R1", "review.test_cases must be an object with positive and negative lists")
    elif isinstance(tc, dict) and not all(isinstance(tc.get(k, []), list) for k in ("positive", "negative")):
        rep.err("R1", "review.test_cases.positive and .negative must be lists")
    elif isinstance(tc, dict):
        pos, neg = tc.get("positive") or [], tc.get("negative") or []
        if len(pos) != 5:
            rep.err("R1", f"exactly 5 positive test cases required, found {len(pos)}")
        if len(neg) != 3:
            rep.err("R2", f"exactly 3 negative test cases required, found {len(neg)}")
        for idx, c in enumerate(pos):
            if not isinstance(c, dict):
                rep.err("R3", f"positive[{idx}] not an object")
                continue
            for k in ("description", "prompt", "tools_triggered", "expected_behavior"):
                if not isinstance(c.get(k), str) or not c.get(k, "").strip():
                    rep.err("R3", f"positive[{idx}].{k} required (non-empty string)")
            if len(c.get("description") or "") > 4000:
                rep.err("R3", f"positive[{idx}].description > 4000")
            if set(c) - POS_KEYS:
                rep.err("R3", f"positive[{idx}] unknown keys {sorted(set(c) - POS_KEYS)} (the documented field is 'prompt')")
        for idx, c in enumerate(neg):
            if not isinstance(c, dict):
                rep.err("R4", f"negative[{idx}] not an object")
                continue
            for k in ("description", "prompt"):
                if not isinstance(c.get(k), str) or not c.get(k, "").strip():
                    rep.err("R4", f"negative[{idx}].{k} required (non-empty string)")
            if set(c) - NEG_KEYS:
                rep.err("R4", f"negative[{idx}] unknown keys {sorted(set(c) - NEG_KEYS)}")
        for c in pos + neg:
            if isinstance(c, dict):
                urls = c.get("file_attachment_urls")
                if urls is not None and (not isinstance(urls, list) or not all(https_ok(u, 2048) for u in urls)):
                    rep.err("R3", "file_attachment_urls must be a list of HTTPS URLs")
                if "expected_output_url" in c and not https_ok(c["expected_output_url"], 2048):
                    rep.err("R3", "expected_output_url must be an HTTPS URL")
        if len(pos) == 5 and len(neg) == 3:
            rep.ok("R1", "5 positive / 3 negative test cases")
    elif tc is None:
        rep.warn("R1", "review.test_cases absent: enter 5 + 3 cases in the portal before submitting")
    demo = r.get("demo_recording_url")
    host = (urlsplit(demo).hostname or "") if isinstance(demo, str) else ""
    if not https_ok(demo, 2048) or host.endswith(".invalid") or "todo" in host.lower():
        rep.gate("R7", f"demo_recording_url must be a real, reviewer-accessible HTTPS URL ({demo!r})")
    if not isinstance(r.get("commerce"), bool):
        rep.err("R8", "review.commerce must be a boolean")
    if "commerce_description" in r and not isinstance(r["commerce_description"], str):
        rep.err("R8", "review.commerce_description must be a string")


def check_publication(rep, p):
    if not isinstance(p, dict):
        rep.err("P1", "publication.release_notes required for MCP final submission")
        return
    if "commerce" in p or "commerce_description" in p:
        rep.err("R8", "commerce fields belong in review, not publication")
    if not supported_text(p.get("release_notes"), multiline=True):
        rep.err("P1", "publication.release_notes required, non-empty")
    c = p.get("countries")
    if c is not None:
        if not isinstance(c, list) or not all(isinstance(x, str) and re.match(r"^[A-Z]{2}$", x) for x in c):
            rep.err("P2", "publication.countries must be uppercase ISO 3166-1 alpha-2 codes ([] = no restriction)")
    else:
        rep.warn("P2", "publication.countries omitted: targeting comes from the portal (decide before submitting)")
    t = p.get("translations")
    if isinstance(t, dict):
        for loc, v in t.items():
            if not loc.strip() or not isinstance(v, (dict, type(None))):
                rep.err("P3", f"translation {loc!r} invalid")
                continue
            v = v or {}
            s = v.get("subtitle")
            if s is not None and (not supported_text(s) or not one_line(s) or len(s) > 30 or "\t" in s):
                rep.err("P3", f"translations.{loc}.subtitle must be one line <= 30")
            d = v.get("description")
            if d is not None and (not supported_text(d, True) or len(d) > 4000 or "\t" in d):
                rep.err("P3", f"translations.{loc}.description must be <= 4000, no tabs")


def check_mcp(pkg, rep, expect_origin, expect_url=None):
    mc = load_json(pkg, rep, "mcp.json", "C1")
    if mc is None:
        return None
    if set(mc) != {"$schema", "mcpServers"}:
        rep.err("C2", f"mcp.json must have exactly $schema and mcpServers (has {sorted(mc)})")
    if mc.get("$schema") != MCP_SCHEMA:
        rep.err("C2", f"mcp.json $schema must be {MCP_SCHEMA}")
    servers = mc.get("mcpServers")
    if not isinstance(servers, dict) or len(servers) != 1:
        rep.err("C3", "mcpServers must contain exactly one server (R11: plugin-level test cases need exactly one)")
        return None
    sname, s = next(iter(servers.items()))
    if not sname.strip() or not isinstance(s, dict):
        rep.err("C3", "server entry invalid")
        return None
    if set(s) - {"type", "url", "headers", "extensions"}:
        rep.err("C4", f"server has unknown keys {sorted(set(s) - {'type', 'url', 'headers', 'extensions'})}")
    if s.get("type") != "streamable-http":
        rep.err("C4", f"server type must be 'streamable-http' (got {s.get('type')!r}); F4 forbids local servers")
    url = s.get("url")
    if not https_ok(url, 2048):
        rep.err("C5", "server url must be absolute HTTPS, no userinfo/fragment")
    else:
        u = urlsplit(url)
        origin = f"{u.scheme}://{u.netloc}"
        if expect_origin and origin != expect_origin:
            rep.err("C5", f"MCP origin {origin} != expected {expect_origin} (the origin can never change)")
        if expect_url and url != expect_url:
            rep.err("C5", f"MCP url {url} != expected {expect_url}: other routes serve tools this plugin says it leaves out")
        host = u.hostname or ""
        if host in ("localhost", "127.0.0.1", "::1") or any(t in host for t in ("ngrok", "trycloudflare", "loca.lt")):
            rep.err("C5", "local or tunnel endpoints are not allowed for public submission")
        rep.ok("C5", f"MCP server '{sname}' -> {url}")
    if "headers" in s:
        rep.err("C6", "drop 'headers': public submission rejects non-empty server headers (Whop rule: no key at all)")
    else:
        rep.ok("C6", "no server headers")
    if "extensions" not in s:
        rep.err("C7", "declare extensions.com.openai.auth with client.mode 'dcr': ChatGPT's default CIMD fails on Whop's server")
    else:
        rep.warn("C7", "server-level 'extensions' (auth) is documented by OpenAI but violates the closed agent-plugins.org server schema; only a real portal upload settles it")
        auth = ((s.get("extensions") or {}).get("com.openai") or {}).get("auth") if isinstance(s.get("extensions"), dict) else None
        if not isinstance(auth, dict):
            rep.err("C7", "extensions.com.openai.auth is missing: declare type 'oauth' and client.mode 'dcr'")
        else:
            if auth.get("type") != "oauth":
                rep.err("C7", f"auth.type {auth.get('type')!r}: Whop's server needs 'oauth'")
            cl = auth.get("client")
            mode = cl.get("mode") if isinstance(cl, dict) else None
            if mode != "dcr":
                rep.err("C7", f"client.mode {mode!r}: ChatGPT's default CIMD fails on Whop's server, so declare 'dcr'")
            if isinstance(cl, dict) and {"clientId", "tokenEndpointAuthMethod"} & set(cl):
                rep.err("C7", "a dcr client must not include clientId or credentials")
    for k, v, where in walk(mc):
        if k in ("clientSecret", "client_secret", "Authorization", "authorization", "token", "apiKey"):
            rep.err("C9", f"secret-like key in mcp.json: {where}")
    return url


def front_matter(raw):
    text = raw.decode("utf-8").lstrip("\ufeff")
    return re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.S)


def check_skills(pkg, rep, plugin_name):
    if yaml is None:
        rep.err("S0", "PyYAML not available; cannot check skills (pip install pyyaml)")
        return
    skill_dirs = {}
    for n in pkg.files:
        if not n.startswith("skills/"):
            continue
        parts = n.split("/")
        if len(parts) == 2:
            rep.warn("S1", f"file directly under skills/ is ignored: {n}")
            continue
        skill_dirs.setdefault(parts[1], set()).add("/".join(parts[2:]))
    if not skill_dirs:
        rep.err("S1", "at least one valid skill required (skills/<name>/SKILL.md); Z12")
        return
    names = set()
    for d, files in sorted(skill_dirs.items()):
        if d.startswith("."):
            rep.err("S2", f"hidden skill dir: {d}")
        if "SKILL.md" not in files:
            nested = [f for f in files if f.endswith("/SKILL.md")]
            rep.err("S1", f"skills/{d} has no SKILL.md" + (f" (nested, not discovered: {nested})" if nested else ""))
            continue
        try:
            mm = front_matter(pkg.files[f"skills/{d}/SKILL.md"])
        except UnicodeDecodeError:
            rep.err("S3", f"skills/{d}/SKILL.md not UTF-8")
            continue
        if not mm:
            rep.err("S3", f"skills/{d}/SKILL.md must start with YAML front matter between --- lines")
            continue
        try:
            fm = yaml.safe_load(mm.group(1))
        except yaml.YAMLError as e:
            rep.err("S3", f"skills/{d} front matter YAML malformed: {e}")
            continue
        if not isinstance(fm, dict):
            rep.err("S3", f"skills/{d} front matter must be a mapping")
            continue
        nm, desc, body = fm.get("name"), fm.get("description"), mm.group(2)
        if not isinstance(nm, str) or not nm.strip():
            rep.err("S4", f"skills/{d} name missing")
        else:
            if not SKILL_NAME.match(nm) or len(nm) > 64:
                rep.err("S4", f"skill name {nm!r} must be lowercase hyphen-case <= 64")
            if nm != d:
                rep.err("S4", f"skill name {nm!r} must match its directory {d!r}")
            if nm in names:
                rep.err("S4", f"duplicate skill name {nm}")
            names.add(nm)
            if len(f"{plugin_name}:{nm}") > 64:
                rep.err("S6", f"{plugin_name}:{nm} > 64 chars")
        if not isinstance(desc, str) or not desc.strip():
            rep.err("S5", f"skills/{d} description missing")
        else:
            if len(desc) > 1024:
                rep.err("S5", f"skills/{d} description {len(desc)} > 1024")
            if "<" in desc or ">" in desc:
                rep.err("S5", f"skills/{d} description has angle brackets (quick_validate rejects them)")
            if not supported_text(desc, True):
                rep.err("S5", f"skills/{d} description has unsupported characters")
            else:
                rep.ok("S5", f"skills/{d} description {len(desc)}/1024")
        extra = set(fm) - SKILL_FM_KEYS
        if extra:
            rep.err("S7", f"skills/{d} front matter keys outside the Agent Skills/OpenAI set: {sorted(extra)}")
        if not body.strip():
            rep.err("S8", f"skills/{d} body is empty")
        if body.count("\n") > 500:
            rep.warn("S8", f"skills/{d}/SKILL.md body {body.count(chr(10))} lines (> 500 recommended)")
        for f in sorted(files):
            if not f.endswith((".md", ".txt", ".yaml", ".yml", ".json")):
                continue
            t = pkg.files[f"skills/{d}/{f}"].decode("utf-8", "replace")
            for pat, rid, msg in (
                (r"\bClaude\b|Claude Code|/plugin\b|/mcp\b|\$\{CLAUDE_PLUGIN_ROOT\}|\$ARGUMENTS|claude\.ai|live artifact", "S9", "Claude-specific wording"),
                (r"\bSSN\b|social security|date of birth|\bDOB\b|passport|\bpassword|\bAPI key|card number|\bCVV\b|\bCVC\b", "S10", "restricted-data wording: confirm it forbids collection rather than asking for it"),
                (r"\bwhop\.app\b", "WH1", "stale *.whop.app domain (now whop.site)"),
                (r"\bfree trial\b|\bupgrade (?:to|your plan)\b|\bsubscribe now\b", "WH3", "upsell wording"),
            ):
                hits = sorted({h if isinstance(h, str) else h[0] for h in re.findall(pat, t, re.I)})
                if hits:
                    rep.warn(rid, f"skills/{d}/{f}: {msg}: {hits[:6]}")
            if f.endswith(".md"):
                for link in re.findall(r"\]\(([^)\s]+)\)", t):
                    if re.match(r"^[a-z]+:", link) or link.startswith("#"):
                        continue
                    target = os.path.normpath(os.path.join(f"skills/{d}", os.path.dirname(f), link.split("#")[0])).replace(os.sep, "/")
                    if target not in pkg.files:
                        rep.err("S12", f"skills/{d}/{f} links to a missing file: {link}")
        if "agents/openai.yaml" in files:
            check_openai_yaml(pkg, rep, d, files)
    rep.ok("S1", f"{len(names)} skills: {sorted(names)}")


def check_openai_yaml(pkg, rep, d, files):
    p = f"skills/{d}/agents/openai.yaml"
    try:
        y = yaml.safe_load(pkg.files[p].decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        rep.err("Y1", f"{p} invalid YAML/UTF-8: {e}")
        return
    if not isinstance(y, dict):
        rep.err("Y1", f"{p} top level must be a mapping")
        return
    if set(y) - {"interface", "policy", "dependencies"}:
        rep.warn("Y1", f"{p} unknown top-level keys {sorted(set(y) - {'interface', 'policy', 'dependencies'})}")
    i = y.get("interface")
    if not isinstance(i, dict):
        rep.err("Y2", f"{p} interface mapping required")
    else:
        for k in ("display_name", "short_description"):
            if not isinstance(i.get(k), str) or not i[k].strip():
                rep.err("Y2", f"{p} interface.{k} required")
        sd = i.get("short_description") or ""
        if isinstance(sd, str) and not 25 <= len(sd) <= 64:
            rep.warn("Y3", f"{p} short_description is {len(sd)} chars (guidance: 25-64)")
        for k in ("icon_small", "icon_large"):
            if k in i:
                v = i[k]
                rel = v[2:] if isinstance(v, str) and v.startswith("./") else v
                if not isinstance(v, str) or not v.strip() or rel not in files:
                    rep.err("Y3", f"{p} interface.{k} must be a relative path to a file in the skill dir: {v!r}")
        if "brand_color" in i and not (isinstance(i["brand_color"], str) and HEX.match(i["brand_color"])):
            rep.err("Y3", f"{p} brand_color must be #RRGGBB")
        if "default_prompt" in i and (not isinstance(i["default_prompt"], str) or not i["default_prompt"].strip()):
            rep.err("Y3", f"{p} default_prompt must be a non-empty string")
    pol = y.get("policy")
    if pol is not None:
        if not isinstance(pol, dict) or set(pol) - {"products", "allow_implicit_invocation"}:
            rep.err("Y4", f"{p} policy may contain only products and allow_implicit_invocation")
        else:
            if "allow_implicit_invocation" in pol and not isinstance(pol["allow_implicit_invocation"], bool):
                rep.err("Y4", f"{p} allow_implicit_invocation must be true/false")
            if "products" in pol:
                pr = pol["products"]
                if not isinstance(pr, list) or not pr or set(pr) - {"CHAT", "CODEX"}:
                    rep.err("Y4", f"{p} products must be a non-empty list of CHAT/CODEX")
    dep = y.get("dependencies")
    if dep is not None and (not isinstance(dep, dict) or set(dep) - {"tools"}):
        rep.err("Y5", f"{p} dependencies supports only tools")
    rep.ok("Y1", f"{p} checked")


def load_surface(path):
    with open(path, encoding="utf-8") as f:
        s = json.load(f)
    if not s.get("excludedGroups"):
        raise SystemExit(f"error: {path} needs a non-empty excludedGroups list (see --surface)")
    allowed = {f"{g}_{op}" for g, ops in s["tools"].items() for op in ops}
    return {
        "meta": set(s.get("meta", [])),
        "allowed": allowed,
        "groups": set(s["tools"]),
        "known_groups": set(s["tools"]) | set(s.get("excludedGroups", [])),
    }


def surface_ok(group, op, surf):
    if op.endswith("*"):
        prefix = f"{group}_{op[:-1]}"
        return any(t.startswith(prefix) for t in surf["allowed"]) if op != "*" else group in surf["groups"]
    return f"{group}_{op}" in surf["allowed"]


def check_surface(pkg, rep, manifest, surf):
    """R5 (against an inferred surface) and SURF: skills route only to served tools."""
    if surf is None:
        return
    def obj(v):
        return v if isinstance(v, dict) else {}

    review = obj(obj(obj(obj(manifest).get("extensions")).get("com.openai")).get("review"))
    positives = obj(review.get("test_cases")).get("positive")
    for idx, c in enumerate(positives if isinstance(positives, list) else []):
        tools = obj(c).get("tools_triggered")
        for name in re.split(r"[,\s]+", tools.strip() if isinstance(tools, str) else ""):
            if name and name not in surf["meta"] and name not in surf["allowed"]:
                rep.err("R5", f"positive[{idx}] tools_triggered {name!r} is not on the surface")
    bad = {}
    for path, raw in pkg.files.items():
        if not path.startswith("skills/") or not path.endswith((".md", ".yaml", ".yml")):
            continue
        for g, op in TOOLISH.findall(raw.decode("utf-8", "replace")):
            if g not in surf["known_groups"]:
                continue
            if not surface_ok(g, op, surf):
                bad.setdefault(path, set()).add(f"{g}_{op}")
    for path, names in sorted(bad.items()):
        rep.err("SURF", f"{path} names tools that are not on the surface: {sorted(names)}")
    if not bad:
        rep.ok("SURF", "every Whop tool named in the skills is on the surface")


def check_todo(pkg, rep):
    for path, raw in sorted(pkg.files.items()):
        if not path.lower().endswith(TEXT_EXT):
            continue
        n = len(re.findall(r"\bTODO\b", raw.decode("utf-8", "replace")))
        if n:
            rep.gate("TODO", f"{path} still has {n} TODO marker(s)")


def secret_scan(pkg, rep):
    pats = (r"sk_(live|test)_[0-9A-Za-z]{10,}", r"apik_[0-9A-Za-z]{10,}", r"-----BEGIN [A-Z ]*PRIVATE KEY",
            r"\bBearer\s+[A-Za-z0-9._-]{20,}", r"\bghp_[0-9A-Za-z]{20,}", r"\bAKIA[0-9A-Z]{16}\b")
    for path, raw in pkg.files.items():
        t = raw.decode("utf-8", "replace")
        for p in pats:
            if re.search(p, t):
                rep.err("F7", f"secret-looking value in {path} ({p})")


def main(argv):
    args = argv[1:]
    if not args or args[0].startswith("-"):
        print(__doc__)
        return 2
    path, expect_origin, expect_url, surface, draft = args[0], None, None, None, "--draft" in args
    if "--expect-origin" in args:
        expect_origin = args[args.index("--expect-origin") + 1]
    if "--expect-url" in args:
        expect_url = args[args.index("--expect-url") + 1]
    if "--surface" in args:
        surface = load_surface(args[args.index("--surface") + 1])
    rep = Report(draft)
    pkg = Pkg(path, rep)
    if pkg.files:
        check_layout(pkg, rep)
        m = check_manifest(pkg, rep)
        check_mcp(pkg, rep, expect_origin, expect_url)
        check_skills(pkg, rep, (m or {}).get("name", "plugin"))
        check_surface(pkg, rep, m, surface)
        check_todo(pkg, rep)
        secret_scan(pkg, rep)
    elif not rep.errors:
        rep.err("Z1", "package has no files")
    for title, items in (("PASS", rep.passes), ("WARN", rep.warnings), ("ERROR", rep.errors)):
        for it in items:
            print(f"{title:5} {it}")
    mode = "draft" if draft else "submission"
    print(f"\n{len(rep.errors)} error(s), {len(rep.warnings)} warning(s) [{mode} mode]")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
